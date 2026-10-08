from pathlib import Path

from app.agents.runtime.definition import AgentDefinition


class AgentDefinitionLoader:
    """
        Loads Markdown-based agent definitions.

        The Markdown file contains the agent's behavioral instructions.
        """

    def __init__(self, definitions_root: str = "agent_definitions"):
        self.definitions_root = Path(definitions_root)

    def load(self, agent_name: str) -> AgentDefinition:
        agent_path = (
                self.definitions_root
                / agent_name
                / "agent.md"
        )

        if not agent_path.exists():
            raise FileNotFoundError(
                f"Agent definition not found: {agent_path}"
            )

        system_prompt = agent_path.read_text(encoding="utf-8").strip()

        if not system_prompt:
            raise ValueError(
                f"Agent definition is empty: {agent_path}"
            )

        return AgentDefinition(
            name=agent_name,
            path=agent_path,
            system_prompt=system_prompt,
        )
