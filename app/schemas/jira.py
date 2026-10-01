from pydantic import BaseModel


class JiraIssue(BaseModel):
    key: str
    project: str
    summary: str
    description: str
    status: str