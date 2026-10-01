from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

from app.schemas.agent import AgentResult
from app.schemas.tools import ToolCallResult
from app.utils.agent_console import AgentConsole


class AgentOrchestrator:
    """
        Executes an individual agent.

        Responsibilities:
        - Initialize the LLM
        - Bind custom + MCP tools
        - Execute the LLM/tool loop
        - Return normalized results

        This class knows nothing about:
        - LangGraph workflow
        - HITL
        - Jira
        - Strategy
        - TestRail
        """

    def __init__(
            self,
            *,
            agent_name: str,
            custom_tools: list[Any],
            mcp_tools: list[Any],
            system_prompt: str,
            model: str = "qwen3:8b",
            temperature: float = 0,
            console: AgentConsole | None = None,
    ):
        self.agent_name = agent_name
        self.custom_tools = custom_tools
        self.mcp_tools = mcp_tools
        self.tools = [*self.custom_tools, *self.mcp_tools]
        self.mcp_tool_names = {tool.name for tool in self.mcp_tools}
        self.tool_map = {tool.name: tool for tool in self.tools}
        self.llm = ChatOllama(model=model, temperature=temperature)
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.system_prompt = system_prompt
        self.console = console or AgentConsole()

    async def run(self, user_prompt: str) -> AgentResult:
        messages = [
            # ("system", self.system_prompt),
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_prompt),
        ]

        tool_results: list[ToolCallResult] = []

        while True:
            self.console.llm(message=f"\n\n Calling Qwen3:8b...")

            response = await self.llm_with_tools.ainvoke(messages)

            self.console.log(message="✓ LLM response received")

            # ----------------------------------------------------
            # Agent finished reasoning.
            # ----------------------------------------------------
            if not response.tool_calls:
                self.console.log(
                    "\n🔎 AgentOrchestrator returning:"
                )

                self.console.log(
                    f"   Tool results: {len(tool_results)}"
                )

                return AgentResult(
                    agent_name=self.agent_name,
                    response=response.content,
                    tool_results=tool_results,
                    success=True,
                )

            # ----------------------------------------------------
            # Preserve assistant message containing
            # tool calls.
            # ----------------------------------------------------
            messages.append(response)

            # ----------------------------------------------------
            # Execute requested tools.
            # ----------------------------------------------------
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_call_id = tool_call["id"]

                selected_tool = self.tool_map.get(tool_name)

                if selected_tool is None:
                    raise ValueError(f"Tool {tool_name} not found")

                tool_type = (
                    "MCP"
                    if tool_name in self.mcp_tool_names
                    else "CUSTOM"
                )

                self.console.tool_call(tool_name=tool_name, args=tool_args, tool_type=tool_type)

                result = await selected_tool.ainvoke(tool_args)

                self.console.tool_result(tool_name=tool_name, result=result, tool_type=tool_type)

                normalized_result = ToolCallResult(
                    tool_name=tool_name,
                    tool_type=tool_type,
                    args=tool_args,
                    result=result,
                )

                tool_results.append(normalized_result)

                messages.append(
                    {
                        "role": "tool",
                        "content": str(result),
                        "tool_call_id": tool_call_id,
                    }
                )
