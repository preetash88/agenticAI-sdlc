from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AgentDefinition:
    name: str
    path: Path
    system_prompt: str
