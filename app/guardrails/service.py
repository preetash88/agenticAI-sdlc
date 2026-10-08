from app.guardrails.input_guardrail import InputGuardrail
from app.guardrails.violation_tracker import ViolationTracker


class GuardrailService:

    def __init__(self):
        self.guardrail = InputGuardrail()
        self.tracker = ViolationTracker(max_violations=5, window_seconds=3600)

    async def check(self, user_id: str, prompt: str):
        # Check whether user is already blocked
        if await self.tracker.is_blocked(user_id):
            return {
                "allowed": False,
                "reason": "User temporarily blocked.",
                "category": "REPEATED_VIOLATIONS",
            }

        # Inspect current prompt
        result = self.guardrail.check(prompt)

        if not result.allowed:
            count = await self.tracker.record_violation(user_id)
            return {
                "allowed": False,
                "reason": result.reason,
                "category": result.category,
                "violation_count": count,
            }

        return {
            "allowed": True,
            "reason": result.reason,
        }
