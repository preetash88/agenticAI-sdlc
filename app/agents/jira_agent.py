from typing import Any

from app.orchestrators.agent_orchestrator import AgentOrchestrator
from app.schemas.agent import AgentResult

JIRA_SYSTEM_PROMPT = """
                    You are a Jira automation agent.

                You have access to two types of capabilities:

                1. Custom application tools.
                2. Jira tools exposed through MCP.

                Choose the appropriate tool based on the user's request.

                Jira issue creation rules:
                - The project must come from the user's request.
                - If the user provides a feature name but no explicit summary,
                  use the feature name as the Jira summary.
                - The description must come from the user's request.
                - Do not invent a Jira issue key.
                - Do not claim an operation succeeded unless the tool returned success.

                General rules:
                - Use tools when an action is required.
                - Ask for information only when it genuinely cannot be determined
                  from the user's request.
                - Keep the final response concise.

"""


class JiraAgent:
    name = "jira_agent"

    def __init__(self, *, custom_tools, mcp_tools):
        self.orchestrator = AgentOrchestrator(
            agent_name=self.name,
            system_prompt=JIRA_SYSTEM_PROMPT,
            custom_tools=custom_tools,
            mcp_tools=mcp_tools,
        )

    async def run(
            self,
            user_prompt: str,
    ) -> AgentResult:
        result = await self.orchestrator.run(
            user_prompt=user_prompt
        )

        print(
            "\n🔎 JiraAgent returning:"
        )

        print(
            f"   Tool results: "
            f"{len(result.tool_results)}"
        )

        return result
