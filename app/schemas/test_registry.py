from enum import Enum

from pydantic import BaseModel, Field


class TestStatus(str, Enum):
    CREATED = "CREATED"
    EXISTING = "EXISTING"


class TestScenario(BaseModel):
    application: str
    feature: str
    scenario: str
    expected: str


class TestRecord(BaseModel):
    test_id: str
    test_case_id: str
    scenario: TestScenario
    status: TestStatus


class TestRegistryStore(BaseModel):
    tests: list[TestRecord] = Field(default_factory=list)
    next_case_number: int = 1
