from pydantic import BaseModel, Field, RootModel


class ExploredElement(BaseModel):
    name: str
    role: str
    label: str | None = None
    ref: str | None = None


class ExplorationResult(BaseModel):
    application: str
    page: str
    url: str
    elements: list[ExploredElement] = Field(default_factory=list)
    observations: list[str] = Field(default_factory=list)


class PlaywrightMCPContent(BaseModel):
    type: str
    text: str


class PlaywrightMCPNavigationResult(RootModel[list[PlaywrightMCPContent]]):

    def get_snapshot(self) -> str:
        for item in self.root:
            if item.type != "text":
                continue
            if "### Snapshot" in item.text:
                return item.text.split("### Snapshot",1)[1].strip()

        return ""
