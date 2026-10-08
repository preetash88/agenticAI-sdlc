import re
from dataclasses import dataclass


@dataclass
class GuardrailResult:
    allowed: bool
    reason: str
    category: str | None = None


class InputGuardrail:
    BLOCKED_PATTERNS = [
        r"\bhow to make a bomb\b",
        r"\bhow to create .*bomb\b",
        r"\bhow to build a weapon\b",
        r"\bkill someone\b",
        r"\bmake an explosive\b",
    ]

    INJECTION_PATTERNS = [
        r"ignore previous instructions",
        r"ignore all previous instructions",
        r"system prompt",
        r"reveal your instructions",
        r"developer message",
    ]

    ABUSE_PATTERNS = [
        r"\bfuck you\b",
        r"\bidiot\b",
        r"\bstupid\b",
    ]

    def check(self, prompt: str) -> GuardrailResult:
        normalized = prompt.lower().strip()

        # Dangerous content
        for pattern in self.BLOCKED_PATTERNS:
            if re.search(pattern, normalized):
                return GuardrailResult(
                    allowed=False,
                    category="DANGEROUS_CONTENT",
                    reason="Request violates safety policy.",
                )

                # Prompt injection
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, normalized):
                return GuardrailResult(
                    allowed=False,
                    category="PROMPT_INJECTION",
                    reason="Potential prompt injection detected.",
                )

            # Abuse
        for pattern in self.ABUSE_PATTERNS:
            if re.search(pattern, normalized):
                return GuardrailResult(
                    allowed=False,
                    category="ABUSIVE_CONTENT",
                    reason="Abusive content detected.",
                )

        return GuardrailResult(
            allowed=True,
            reason="Input passed guardrail.",
        )
