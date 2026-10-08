from pydantic import BaseModel, Field


class TestingTypeStrategy(BaseModel):
    type: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    priority: str = Field(min_length=1)


class TestStrategy(BaseModel):
    strategy_summary: str = Field(min_length=1)

    testing_types: list[TestingTypeStrategy] = Field(
        default_factory=list
    )

    functional_scope: list[str] = Field(
        default_factory=list
    )

    automation_scope: list[str] = Field(
        default_factory=list
    )

    manual_scope: list[str] = Field(
        default_factory=list
    )

    environment_requirements: list[str] = Field(
        default_factory=list
    )

    test_data_requirements: list[str] = Field(
        default_factory=list
    )

    dependencies: list[str] = Field(
        default_factory=list
    )

    risks: list[str] = Field(
        default_factory=list
    )

    automation_approach: str = Field(min_length=1)

    assumptions: list[str] = Field(
        default_factory=list
    )

    open_questions: list[str] = Field(
        default_factory=list
    )