from langgraph.constants import START, END
from langgraph.graph import StateGraph

from app.graph.nodes.analysis import analysis_node
from app.graph.nodes.jira import jira_node
from app.graph.nodes.strategy import strategy_node
from app.graph.state2 import QAWorkflowState


def build_workflow():
    graph = StateGraph(QAWorkflowState)

    graph.add_node("jira", jira_node)
    graph.add_node("analysis", analysis_node)
    graph.add_node("strategy", strategy_node)

    graph.add_edge(START, "jira")
    graph.add_edge("jira", "analysis")
    graph.add_edge("analysis", "strategy")
    graph.add_edge("strategy", END)

    return graph.compile()
