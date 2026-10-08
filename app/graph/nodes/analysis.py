from app.agents.runtime import AgentDefinitionLoader, definition, AgentRuntime
from app.graph.state2 import QAWorkflowState
from app.schemas.feature_analysis import FeatureAnalysis


async def analysis_node(state: QAWorkflowState) -> dict:
    loader = AgentDefinitionLoader()

    definition = loader.load("analysis")

    agent = AgentRuntime(
        definition=definition,
        output_schema=FeatureAnalysis,
        model="qwen3:8b"
    )

    jira_issue = state["jira_issue"]

    analysis = await agent.run(
        user_input=f"""
Analyze the following Jira issue.

Jira issue retrieved through Jira MCP:

{jira_issue}
"""
    )

    return {
        "analysis": analysis
    }
