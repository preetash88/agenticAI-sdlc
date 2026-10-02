from typing import Any

from app.orchestrators.agent_orchestrator import AgentOrchestrator

STRATEGY_SYSTEM_PROMPT = """
You are a QA Test Strategy Agent.

Your responsibility is to create a concise test strategy
for the feature described by the user.

Include:
- Testing scope
- Functional testing
- Non-functional testing
- Automation approach
- Key risks

Rules:
- Maximum 100 words.
- Base the strategy only on the information provided.
- Do not invent requirements.
- Keep the strategy practical and concise.
- Do not execute any tools unless required.
- Return only the test strategy.
"""


class StrategyAgent:
    name = "strategy_agent"

    def __init__(self, *, custom_tools: list[Any], mcp_tools: list[Any]):
        self.orchestrator = AgentOrchestrator(
            agent_name=self.name,
            system_prompt=STRATEGY_SYSTEM_PROMPT,
            custom_tools=custom_tools,
            mcp_tools=mcp_tools,
        )

    async def run(self, user_prompt: str):
        result = await self.orchestrator.run(user_prompt=user_prompt)

        print("\n🔎 StrategyAgent returning:")
        print(f"   Tool results: {len(result.tool_results)}")
        return result
