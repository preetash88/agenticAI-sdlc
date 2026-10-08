from app.guardrails.input_guardrail import InputGuardrail

guardrail = InputGuardrail()


def call_api(prompt: str, options, context):
    result = guardrail.check(prompt)

    return {
        "output": "ALLOWED" if result.allowed else "DENIED",
        "guardrails": {
            "flagged": not result.allowed,
            "flaggedInput": not result.allowed,
            "flaggedOutput": False,
            "reason": result.reason,
            "category": result.category,
        }
    }
