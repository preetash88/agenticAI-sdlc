import json
from pathlib import Path

from fastmcp import FastMCP

from app.schemas.jira import JiraIssue

mcp = FastMCP("Jira MCP")

DATA_FILE = Path("mock_data/jira.json")


def load_data() -> dict:
    if not DATA_FILE.exists():
        return {
            "issues": [],
            "next_issue_number": 1
        }

    return json.loads(DATA_FILE.read_text())


def save_data(data: dict) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


@mcp.tool()
def create_issue(project: str, summary: str, description: str) -> dict:
    """Create a Jira Issue"""
    data = load_data()
    issue_number = data["next_issue_number"]
    issue_key = f"{project}-{issue_number}"
    issue = JiraIssue(
        key=issue_key,
        project=project,
        summary=summary,
        description=description,
        status="OPEN",
    )

    data["issues"].append(issue.model_dump())
    data["next_issue_number"] += 1

    save_data(data)
    return issue.model_dump()


@mcp.tool()
def transition_issue(issue_key: str, status: str) -> dict:
    """Change the status of an existing Jira Issue"""
    data = load_data()

    for issue in data["issues"]:
        if issue["key"] == issue_key:
            issue["status"] = status
            save_data(data)
            return issue
    return {
        "success": False,
        "error": f"Issue:{issue_key} not found"
    }


@mcp.tool()
def get_issue(issue_key: str) -> dict:
    """Get a Jira Issue by issue key"""
    data = load_data()

    for issue in data["issues"]:
        if issue["key"] == issue_key:
            return issue
    return {
        "success": False,
        "error": f"Issue {issue_key} not found"
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
