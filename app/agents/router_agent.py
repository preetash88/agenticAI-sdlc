from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama

from app.schemas.routing import RoutingDecision

ROUTER_SYSTEM_PROMPT = """
You are the workflow router for a QA automation system.

Your job is to decide which agent should execute next
based on the user's request and the work already completed.

Available agents:

- jira_agent
- testrail_agent
- strategy_agent
- explorer_agent
- code_generator_agent

Rules:

1. Select only an agent from the available agents.
2. If no more work is required, set done=true.
3. Do not perform the requested work yourself.
4. Do not invent agents.
5. Consider previous agent results before deciding.
6. Return only the required structured routing decision.
"""


class RouterAgent:
    def __init__(self, model: str = "qwen3:8b"):
        self.llm = ChatOllama(
            model=model,
            temperature=0
        )
        self.structured_llm = self.llm.with_structured_output(RoutingDecision)

    async def route(
            self,
            user_prompt: str,
            current_agent: str | None,
            previous_results: list[str]
    ) -> RoutingDecision:
        context = f"""
        User request:
        {user_prompt}
        
        Current agent:
        {current_agent}
        
        Previously executed agents:
        {previous_results}
        
        Routing rules:
        - Read the complete user request before deciding.
        - Select the next agent based on the requested workflow.
        - An agent should not be selected again if its required work is already completed.
        - If jira_agent has not run and the user requested Jira creation, select jira_agent.
        - If jira_agent has completed and the user requested a QA strategy, select strategy_agent.
        - If the user requested a strategy directly without Jira, select strategy_agent.
        - Apply the same reasoning to other available agents.
        - Do not perform the requested work yourself.
        - If more requested work remains, select the appropriate next agent and set done=false.
        - Set done=true only when all requested agent work has been completed.

        """

        response = await self.structured_llm.ainvoke([
            SystemMessage(content=ROUTER_SYSTEM_PROMPT),
            HumanMessage(content=context),
        ])
        return RoutingDecision.model_validate(response)
