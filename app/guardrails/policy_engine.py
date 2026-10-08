from app.guardrails.models import GuardrailResult, GuardrailAction, GuardrailCategory


class GuardrailPolicyEngine:
    def evaluate(
            self,
            injection_detected: bool,
            injection_confidence: float,
            dangerous_detected: bool,
            dangerous_confidence: float,
            pii_findings: list[str]
    ) -> GuardrailResult:
        # Highest priority: dangerous content.
        if dangerous_detected:
            return GuardrailResult(
                allowed=False,
                action=GuardrailAction.BLOCK,
                category=GuardrailCategory.DANGEROUS_CONTENT,
                reason="Request content potentially dangerous content.",
                confidence=dangerous_confidence,
                detector="dangerous_content",
            )

        # Prompt injection.
        if injection_detected:
            return GuardrailResult(
                allowed=False,
                action=GuardrailAction.BLOCK,
                category=GuardrailCategory.PROMPT_INJECTION,
                reason="Potential prompt injection detected.",
                confidence=injection_confidence,
                detector="prompt_injection",
            )

        # PII is detected but not blocked in Phase 1.
        if pii_findings:
            return GuardrailResult(
                allowed=True,
                action=GuardrailAction.WARN,
                category=GuardrailCategory.PII,
                reason="Potential PII detected in the request.",
                confidence=0.90,
                detector="pii",
                metadata={
                    "pii_types": pii_findings,
                },
            )

        return GuardrailResult(
            allowed=True,
            action=GuardrailAction.ALLOW,
            category=GuardrailCategory.NONE,
            reason="Input passed guardrail checks.",
            confidence=1.0,
            detector="policy_engine",
        )
