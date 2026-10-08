from enum import Enum

from pydantic import BaseModel, Field


class GuardrailAction(str, Enum):
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    WARN = "WARN"
    RATE_LIMIT = "RATE_LIMIT"


class GuardrailCategory(str, Enum):
    NONE = "NONE"
    DANGEROUS_CONTENT = "DANGEROUS_CONTENT"
    PROMPT_INJECTION = "PROMPT_INJECTION"
    PII = "PII"
    ABUSIVE_CONTENT = "ABUSIVE_CONTENT"
    SPAM = "SPAM"
    RATE_LIMIT = "RATE_LIMIT"
    REPEATED_VIOLATIONS = "REPEATED_VIOLATIONS"
    INVALID_INPUT = "INVALID_INPUT"


class GuardrailResult(BaseModel):
    allowed: bool
    action: GuardrailAction
    category: GuardrailCategory
    reason: str

    confidence: float = Field(default=1.0, ge=0, le=1.0)

    detector: str = "unknown"

    violation_count: int = 0
    metadata: dict = Field(default_factory=dict)
