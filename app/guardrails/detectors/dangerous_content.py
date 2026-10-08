import re


class DangerousContentDetector:
    PATTERNS = [
        r"\bhow\s+to\s+make\s+(?:a\s+)?(?:\w+\s+)*bomb\b",
        r"\bhow\s+to\s+create\s+(?:a\s+)?(?:\w+\s+)*bomb\b",
        r"\bhow\s+to\s+build\s+(?:a\s+)?(?:\w+\s+)*weapon\b",
        r"\bhow\s+to\s+make\s+(?:an\s+)?(?:\w+\s+)*explosive\b",
        r"\bhow\s+to\s+kill\s+someone\b",
        r"\bhow\s+to\s+poison\s+someone\b",
    ]

    def detect(self, text: str) -> tuple[bool, float, str | None]:

        normalized = text.lower()

        for pattern in self.PATTERNS:

            if re.search(pattern, normalized):
                return (
                    True,
                    0.99,
                    pattern,
                )

        return False, 0.0, None