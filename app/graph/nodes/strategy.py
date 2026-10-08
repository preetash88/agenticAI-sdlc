from app.agents.runtime import AgentDefinitionLoader, AgentRuntime
from app.graph.state2 import QAWorkflowState
from app.schemas.test_strategy import TestStrategy


async def strategy_node(state: QAWorkflowState) -> dict:
    loader = AgentDefinitionLoader()

    definition = loader.load("strategy")

    agent = AgentRuntime(
        definition=definition,
        output_schema=TestStrategy,
        model="qwen3:8b",
    )

    analysis = state["analysis"]

    strategy = await agent.run(
        user_input=f"""
    Create a test strategy from the following validated
    FeatureAnalysis.

    FeatureAnalysis:

    {analysis.model_dump_json(indent=2)}
    """
    )

    return {
        "strategy": strategy
    }
