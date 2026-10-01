from pydantic import BaseModel, Field

from app.schemas.tools import ToolCallResult


class AgentResult(BaseModel):
    agent_name: str
    response: str = ""
    tool_results: list[ToolCallResult] = Field(default_factory=list)
    success: bool = True
    error: str | None = None
