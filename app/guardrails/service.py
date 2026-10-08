from app.guardrails.detectors.dangerous_content import DangerousContentDetector
from app.guardrails.detectors.injection import PromptInjectionDetector
from app.guardrails.detectors.pii import PIIDetector
from app.guardrails.input_guardrail import InputGuardrail
from app.guardrails.models import GuardrailResult, GuardrailAction, GuardrailCategory
from app.guardrails.normalizer import InputNormalizer
from app.guardrails.policy_engine import GuardrailPolicyEngine
from app.guardrails.violation_tracker import ViolationTracker


class GuardrailService:

    def __init__(self):
        self.normalizer = InputNormalizer()
        self.injection_detector = PromptInjectionDetector()
        self.dangerous_detector = DangerousContentDetector()
        self.pii_detector = PIIDetector()
        self.policy_engine = GuardrailPolicyEngine()
        self.tracker = ViolationTracker(max_violations=5, window_seconds=3600)

    async def check(self, user_id: str, prompt: str) -> dict:

        # ---------------------------------------
        # 1. Check existing user block
        # ---------------------------------------
        if await self.tracker.is_blocked(user_id):
            return GuardrailResult(
                allowed=False,
                action=GuardrailAction.BLOCK,
                category=GuardrailCategory.REPEATED_VIOLATIONS,
                reason="User temporarily blocked",
                confidence=1.0,
                detector="violation_tracker"
            ).model_dump()

        # ---------------------------------------
        # 2. Normalize input
        # ---------------------------------------
        try:
            normalized_input = self.normalizer.normalize(prompt)
        except (TypeError, ValueError) as exc:
            return GuardrailResult(
                allowed=False,
                action=GuardrailAction.BLOCK,
                category=GuardrailCategory.INVALID_INPUT,
                reason=str(exc),
                confidence=1.0,
                detector="normalizer",
            ).model_dump()

        # ---------------------------------------
        # 3. Run detectors
        # ---------------------------------------
        (injection_detected, injection_confidence, _) = self.injection_detector.detect(normalized_input)

        (dangerous_detected, dangerous_confidence, _) = self.dangerous_detector.detect(normalized_input)

        pii_findings = self.pii_detector.detect(normalized_input)

        # ---------------------------------------
        # 4. Apply policy
        # ---------------------------------------
        result = self.policy_engine.evaluate(
            injection_detected=injection_detected,
            injection_confidence=injection_confidence,
            dangerous_detected=dangerous_detected,
            dangerous_confidence=dangerous_confidence,
            pii_findings=pii_findings,
        )

        # ---------------------------------------
        # 5. Track blocking violations
        # ---------------------------------------
        if result.action == GuardrailAction.BLOCK:
            count = await self.tracker.record_violation(user_id=user_id)

            result.violation_count = count

        return result.model_dump()
