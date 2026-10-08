import re


class PIIDetector:

    PATTERNS = {
        "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",

        "PHONE": r"\b(?:\+91[-\s]?)?[6-9]\d{9}\b",

        "CREDIT_CARD": r"\b(?:\d[ -]*?){13,19}\b",

        "AWS_ACCESS_KEY": r"\bAKIA[0-9A-Z]{16}\b",

        "API_KEY": r"\b(?:api[_-]?key|token|secret)\s*[:=]\s*[A-Za-z0-9_\-]{16,}\b",
    }

    def detect(self, text: str):

        findings = []

        for category, pattern in self.PATTERNS.items():

            matches = re.findall(
                pattern,
                text,
                flags=re.IGNORECASE,
            )

            if matches:
                findings.append(category)

        return findings