from typing import Any

from pydantic import BaseModel, Field


class ToolCallResult(BaseModel):
    tool_name: str
    tool_type: str
    args: dict[str, Any] = Field(default_factory=dict)
    result: Any = None
