import json


class AgentConsole:
    def __init__(self, enabled: bool = True):
        self.enabled = enabled

    def log(self, message: str):
        if self.enabled:
            print(message, flush=True)

    def thinking(self, message: str = "Thinking..."):
        self.log(f"\n🤖 {message}")

    def llm(self, message: str = "Calling LLM..."):
        self.log(f"🧠 {message}")

    def tool_call(self, tool_name: str, args: dict, tool_type: str = "CUSTOM"):
        icon = "🔌" if tool_type == "MCP" else "🔧"
        self.log(f"\n{icon} {tool_type} TOOL")
        self.log(f"   ├─ Tool: {tool_name}")
        self.log(
            f"   └─ Args: {json.dumps(args, indent=2)}"
        )

    def tool_result(self, tool_name: str, result, tool_type: str = "CUSTOM"):
        self.log(
            f"✓ {tool_type} tool completed: {tool_name}"
        )
        self.log(
            f"  └─ Result: {result}"
        )

    def completed(self):
        self.log("\n✓ Agent completed\n")
