from pydantic import BaseModel


class RoutingDecision(BaseModel):
    next_agent: str | None = None
    reason: str = ""
    done: bool = False
