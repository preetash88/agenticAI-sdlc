import asyncio

from app.agents.runtime import AgentDefinition, AgentDefinitionLoader, AgentRuntime
from app.schemas.feature_analysis import FeatureAnalysis


async def main():
    loader = AgentDefinitionLoader()
    definition = loader.load("analysis")

    print(f"Loaded agent: {definition.name}")
    print(f"Definition: {definition.path}")

    runtime = AgentRuntime(
        definition=definition,
        output_schema=FeatureAnalysis,
        model="qwen3:8b"
    )

    result = await runtime.run(
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

    print("\n===== FEATURE ANALYSIS =====")
    print(
        result.model_dump_json(indent=2)
    )


if __name__ == "__main__":
    asyncio.run(main())
