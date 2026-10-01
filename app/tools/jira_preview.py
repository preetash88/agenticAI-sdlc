from langchain_core.tools import tool


@tool
def build_jira_preview(
        issue_key: str,
        project: str,
        summary: str,
        description: str,
        status: str,
) -> dict:
    """
        Build a human-readable preview of a Jira issue for review.
        """

    jira_url = f"http://localhost:8000/jira/browse/{issue_key}"

    html = f"""
            <!DOCTYPE html>
        <html>
        <head>
            <title>{issue_key} - Jira Preview</title>
        </head>
        <body>
            <h1>{summary}</h1>
        
            <p>
                <strong>Issue:</strong> {issue_key}
            </p>
        
            <p>
                <strong>Project:</strong> {project}
            </p>
        
            <p>
                <strong>Status:</strong> {status}
            </p>
        
            <h2>Description</h2>
        
            <p>{description}</p>
        
            <p>
                <strong>URL:</strong>
                <a href="{jira_url}">
                    {jira_url}
                </a>
            </p>
        </body>
        </html>

"""
    return {
        "url": jira_url,
        "html": html,
    }
