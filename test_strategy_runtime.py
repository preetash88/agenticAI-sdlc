import asyncio

from app.agents.runtime import AgentDefinitionLoader, AgentRuntime
from app.schemas.feature_analysis import FeatureAnalysis
from app.schemas.test_strategy import TestStrategy


async def main():

    loader = AgentDefinitionLoader()

    # -------------------------
    # 1. Load Analysis Agent
    # -------------------------
    analysis_definition = loader.load("analysis")

    analysis_agent = AgentRuntime(
        definition=analysis_definition,
        output_schema=FeatureAnalysis,
        model="qwen3:8b",
    )

    analysis = await analysis_agent.run(
        user_input="""
        Jira Issue:

        Key: DEMO-101
        URL: https://jira.example.com/browse/DEMO-101

        Title:
        Add successful login functionality

        Description:
        Users should be able to log into the web application
        using valid credentials.

        Acceptance Criteria:
        1. User can enter username.
        2. User can enter password.
        3. User can click Login.
        4. Successful authentication displays the Products page.

        Priority:
        High

        Issue Type:
        Story
        """
    )

    print("\n==============================")
    print("ANALYSIS AGENT OUTPUT")
    print("==============================")

    print(analysis.model_dump_json(indent=2))

    # -------------------------
    # 2. Load Strategy Agent
    # -------------------------
    strategy_definition = loader.load("strategy")

    strategy_agent = AgentRuntime(
        definition=strategy_definition,
        output_schema=TestStrategy,
        model="qwen3:8b",
    )

    # -------------------------
    # 3. Agent-to-Agent handoff
    # -------------------------
    strategy = await strategy_agent.run(
        user_input=f"""
        Create a test strategy from the following validated
        FeatureAnalysis. Keep the strategy to maximum 100 words.

        FeatureAnalysis:
        {analysis.model_dump_json(indent=2)}
        """
    )

    print("\n==============================")
    print("STRATEGY AGENT OUTPUT")
    print("==============================")

    print(strategy.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())