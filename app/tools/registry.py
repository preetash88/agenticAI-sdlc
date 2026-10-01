from app.tools.test_data import generate_test_data
from app.tools.validation import validate_project_key

CUSTOM_TOOLS = [
    generate_test_data,
    validate_project_key
]


def get_custom_tools():
    return CUSTOM_TOOLS
