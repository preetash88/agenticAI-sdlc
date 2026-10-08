import re

from app.graph.state2 import QAWorkflowState
from app.mcp.client import MCPClient, mcp_config


def extract_issue_key(jira_input: str) -> str:
    """
    Extract Jira issue key from either:

    DEMO-101

    or:

    https://jira.example.com/browse/DEMO-101
    """
    match = re.search(
        r"\b([A-Z][A-Z0-9]+-\d+)\b",
        jira_input,
    )

    if not match:
        raise ValueError(
            f"Could not extract Jira issue key from: {jira_input}"
        )

    return match.group(1)

async def jira_node(state: QAWorkflowState) -> dict:
    issue_key = extract_issue_key(state["jira_input"])

    client = MCPClient(mcp_config())

    try:
        tools = await client.connect()

        get_issue_tool = next(
            tool
            for tool in tools
            if tool.name == "jira_get_issue"
        )

        result = await get_issue_tool.ainvoke(
            {
                "issue_key": issue_key
            }
        )

        if isinstance(result, dict) and result.get("success") is False:
            raise ValueError(
                result.get("error", "Jira issue lookup failed")
            )

        return {
            "jira_issue": result
        }

    finally:
        await client.close()