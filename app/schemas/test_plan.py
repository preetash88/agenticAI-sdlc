from pydantic import BaseModel, Field


class TestStep(BaseModel):
    step_number: int
    action: str
    expected_result: str


class TestPlan(BaseModel):
    test_case_id: str
    title: str
    priority: str
    test_type: str
    test_level: str
    suites: list[str] = Field(..., min_items=1)

    preconditions: list[str] = Field(..., min_items=1)
    steps: list[TestStep] = Field(..., min_items=1)
    expected_result: str
    automation: bool = True
