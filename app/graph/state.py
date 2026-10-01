from typing import TypedDict, Any

from app.schemas.agent import AgentResult
from app.schemas.routing import RoutingDecision


class QAState(TypedDict, total=False):
    # Original user request
    user_prompt: str

    # Routing
    current_agent: str
    next_agent: str | None
    routing_decision: RoutingDecision

    # JIRA
    jira_project: str
    jira_issue_key: str
    jira_status: str
    jira_description: str
    jira_summary: str
    jira_url: str
    jira_preview_html: str
    jira_raw_response: dict[str, Any]

    # Agent Execution
    agent_response: str
    agent_result: AgentResult
    agent_tool_results: list[dict[str, Any]]

    # Workflow
    visited_agents: list[str]

    # HITL
    human_approved: bool
    human_feedback: str

    # Errors
    errors: list[str]
