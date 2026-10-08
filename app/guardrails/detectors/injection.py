import re


class PromptInjectionDetector:
    PATTERNS = [
        r"\bignore\s+(all\s+)?previous\s+instructions\b",
        r"\bignore\s+(all\s+)?prior\s+instructions\b",
        r"\bdisregard\s+(all\s+)?previous\s+instructions\b",
        r"\bforget\s+(all\s+)?previous\s+instructions\b",

        r"\breveal\s+(your\s+)?system\s+prompt\b",
        r"\bshow\s+(me\s+)?your\s+system\s+prompt\b",
        r"\breveal\s+(your\s+)?instructions\b",

        r"\bdeveloper\s+message\b",
        r"\bsystem\s+message\b",

        r"\bpretend\s+you\s+are\b",
        r"\bact\s+as\s+if\s+you\s+are\b",

        r"\bbypass\s+(the\s+)?safety\b",
        r"\bdisable\s+(the\s+)?guardrails?\b",
    ]

    def detect(self, text: str) -> tuple[bool, float, str | None]:
        normalized = text.lower()

        for pattern in self.PATTERNS:
            if re.search(pattern, normalized):
                return (True, 0.95, pattern)

        return (False, 0.0, None)
