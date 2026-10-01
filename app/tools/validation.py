from langchain_core.tools import tool


@tool
def validate_project_key(project_key: str) -> dict:
    """
       Validate a project key used by the QA automation platform.
       """
    if not project_key:
        return {
            "valid": False,
            "error": "Project key is required"
        }

    if not project_key.isupper():
        return {
            "valid": False,
            "error": "Project key must use uppercase letters."
        }

    if not project_key.isalnum():
        return {
            "valid": False,
            "error": "Project key must contain only letters and numbers."
        }

    return {
        "valid": True,
        "project_key": project_key
    }
