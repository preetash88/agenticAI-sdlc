from enum import Enum

from pydantic import BaseModel, Field, HttpUrl


class AnalysisStatus(str, Enum):
    READY = "READY"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    NOT_AUTOMATABLE = "NOT_AUTOMATABLE"
    BLOCKED = "BLOCKED"


class DependencyType(str, Enum):
    SERVICE = "service"
    API = "api"
    DATABASE = "database"
    UI = "ui"
    EXTERNAL_SYSTEM = "external_system"
    TEST_DATA = "test_data"
    ENVIRONMENT = "environment"
    OTHER = "other"


class RiskSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TestingType(str, Enum):
    FUNCTIONAL = "FUNCTIONAL"
    API = "API"
    UI = "UI"
    INTEGRATION = "INTEGRATION"
    E2E = "E2E"
    REGRESSION = "REGRESSION"
    SMOKE = "SMOKE"
    ACCESSIBILITY = "ACCESSIBILITY"
    SECURITY = "SECURITY"
    PERFORMANCE = "PERFORMANCE"
    DATA_VALIDATION = "DATA_VALIDATION"
    COMPATIBILITY = "COMPATIBILITY"
    MOBILE = "MOBILE"
    NEGATIVE = "NEGATIVE"


class Priority(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class AutomationStatus(str, Enum):
    AUTOMATION_READY = "AUTOMATION_READY"
    PARTIALLY_AUTOMATABLE = "PARTIALLY_AUTOMATABLE"
    NOT_AUTOMATABLE = "NOT_AUTOMATABLE"
    BLOCKED = "BLOCKED"


class AgentType(str, Enum):
    STRATEGY = "strategy"
    API = "api"
    PLAYWRIGHT = "playwright"
    SECURITY = "security"
    PERFORMANCE = "performance"
    ACCESSIBILITY = "accessibility"


class JiraIssue(BaseModel):
    key: str = Field(min_length=1)
    url: str = Field(min_length=1)
    title: str = Field(min_length=1)
    type: str = Field(min_length=1)
    priority: str | None = None


class Requirement(BaseModel):
    id: str = Field(pattern=r"^REQ-[A-Z0-9-]+-\d+$")
    description: str = Field(min_length=1)
    source: str = Field(min_length=1)


class AcceptanceCriterion(BaseModel):
    id: str = Field(pattern=r"^AC-[A-Z0-9-]+-\d+$")
    description: str = Field(min_length=1)
    source: str = Field(min_length=1)


class Dependency(BaseModel):
    name: str = Field(min_length=1)
    type: DependencyType
    description: str = Field(min_length=1)


class Risk(BaseModel):
    description: str = Field(min_length=1)
    severity: RiskSeverity


class Ambiguity(BaseModel):
    description: str = Field(min_length=1)
    impact: str = Field(min_length=1)
    requires_human_input: bool


class TestingScope(BaseModel):
    type: TestingType
    reason: str = Field(min_length=1)
    priority: Priority


class AutomationAssessment(BaseModel):
    status: AutomationStatus
    reason: str = Field(min_length=1)

    automation_candidates: list[str] = Field(
        default_factory=list
    )

    automation_constraints: list[str] = Field(
        default_factory=list
    )


class RequiredAgent(BaseModel):
    agent: AgentType
    reason: str = Field(min_length=1)
    priority: Priority


class Assumption(BaseModel):
    description: str = Field(min_length=1)
    safe_to_use: bool


class FeatureAnalysis(BaseModel):
    status: AnalysisStatus

    issue: JiraIssue

    business_objective: str = Field(min_length=1)

    requirements: list[Requirement] = Field(
        default_factory=list
    )

    acceptance_criteria: list[AcceptanceCriterion] = Field(
        default_factory=list
    )

    dependencies: list[Dependency] = Field(
        default_factory=list
    )

    risks: list[Risk] = Field(
        default_factory=list
    )

    ambiguities: list[Ambiguity] = Field(
        default_factory=list
    )

    testing_scope: list[TestingScope] = Field(
        default_factory=list
    )

    automation_assessment: AutomationAssessment

    required_agents: list[RequiredAgent] = Field(
        default_factory=list
    )

    assumptions: list[Assumption] = Field(
        default_factory=list
    )

    analysis_summary: str = Field(min_length=1)