import asyncio

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama

from app.agents.playwright.playwright_explorer import PlaywrightExplorer
from app.mcp.client import MCPClient, mcp_config
from app.schemas.playwright import ExplorationResult

PLAYWRIGHT_EXPLORATION_PROMPT = """
You are a Senior SDET performing browser exploration.

Your job is to analyze the browser snapshot provided by the
Playwright Explorer and produce a structured exploration result.

Rules:

1. Only report elements actually present in the snapshot.
2. Do not invent selectors, elements, or application behavior.
3. Preserve the Playwright element references when available.
4. Identify the page and important elements relevant to the requested scenario.
5. Record useful observations.
6. Do not generate test code.
7. Do not modify the application.

Return only the requested structured output.
"""


class PlaywrightAgent:

    def __init__(
            self,
            mcp_tools,
            model: str = "qwen3:8b"
    ):
        self.explorer = PlaywrightExplorer(mcp_tools)
        self.llm = ChatOllama(
            model=model,
            temperature=0
        )
        self.structured_llm = self.llm.with_structured_output(ExplorationResult)

    async def agent_explore(self, *, url: str, scenario: str) -> ExplorationResult:
        exploration = await self.explorer.explore(url=url)

        snapshot = exploration["snapshot"]

        messages = [
            SystemMessage(content=PLAYWRIGHT_EXPLORATION_PROMPT),
            HumanMessage(content=f"""
            Application URL:
            {url}
                
            Requested scenario:
            {scenario}
                
            Browser snapshot:
            {snapshot}
                """
                         ),
        ]

        print("\n🧠 Playwright Agent: asking Qwen3 to analyze snapshot...", flush=True)

        result = await self.structured_llm.ainvoke(messages)

        print("✅ Playwright Agent: Qwen3 analysis completed.", flush=True)

        result = await self.structured_llm.ainvoke(messages)

        return ExplorationResult.model_validate(result)


async def main():
    client = MCPClient(mcp_config())

    try:
        tools = await client.connect()

        agent = PlaywrightAgent(tools)

        result = await agent.agent_explore(
            url="https://www.saucedemo.com/",
            scenario=f"""
            Successful login with valid credentials
            
            Happy credentials:
            username: "standard_user"
            password: "secret_sauce" 
            """
        )

        print("\n🤖 PLAYWRIGHT AGENT")
        print("=" * 70)

        print(result.model_dump_json(indent=2))

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
