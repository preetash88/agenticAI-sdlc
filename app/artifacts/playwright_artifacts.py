from pathlib import Path


class PlaywrightArtifactStore:
    def __init__(self, root: str = "playwright"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def write_test_plan(self, content: str) -> Path:
        path = self.root / "test_plan.md"

        path.write_text(
            content,
            encoding="utf-8",
        )

        return path
