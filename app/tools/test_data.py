import uuid

from langchain_core.tools import tool


@tool
def generate_test_data(data_type: str) -> dict:
    """
    Generate unique test data for automated testing.

    Supported types:
    - user
    - email
    - username
    :param data_type: str
    :return: dict
    """
    unique_id = uuid.uuid4().hex[:8]

    if data_type == "user":
        return {
            "username": f"test_user_{unique_id}",
            "email": f"test_{unique_id}@example.com",
            "password": "unique_id",
        }

    if data_type == "email":
        return {
            "email": f"test_{unique_id}@example.com"
        }

    if data_type == "username":
        return {
            "username": f"test_user_{unique_id}"
        }

    return {
        "success": False,
        "error": f"Unsupported data type: {data_type}"
    }
