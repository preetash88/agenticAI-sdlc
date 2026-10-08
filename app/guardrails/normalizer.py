import re

import unicodedata


class InputNormalizer:
    MAX_INPUT_LENGTH = 10_000

    def normalize(self, text: str) -> str:
        if not isinstance(text, str):
            raise TypeError("Input must be of type str")

        text = text.strip()

        if not text:
            raise ValueError("Input must not be empty")

        if len(text) > self.MAX_INPUT_LENGTH:
            raise ValueError(f"Prompt exceeds maximum length of "
                             f"{self.MAX_INPUT_LENGTH} characters.")

        # Unicode normalization
        text = unicodedata.normalize("NFKC", text)

        # Remove control characters
        text = "".join(
            char
            for char in text
            if unicodedata.category(char) != "Cc"
            or char in "\n\t"
        )

        # Collapse excessive whitespace
        text = re.sub(
            r"\s+", " ", text
        )

        return text.strip()
