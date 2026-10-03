from langchain.mcp import MCPAdapter


class MCPClient:
    def __init__(self, config: dict):
        self.config = config
        self.adapter = None
        self.tools = []

    async def connect(self):
        self.adapter = MCPAdapter(self.config)
        await self.adapter.__aenter__()
        self.tools = await self.adapter.list_tools()
        return self.tools

    async def close(self):
        if self.adapter is not None:
            await self.adapter.__aexit__(None, None, None)
            self.adapter = None


def mcp_config():
    return {
        "mcpServers": {
            "jira": {
                "transport": "stdio",
                "command": "uv",
                "args": [
                    "run",
                    "python",
                    "-m",
                    "app.mcp.jira_server"
                ]
            },
            "playwright": {
                "transport": "stdio",
                "command": "npx",
                "args": [
                    "@playwright/mcp"
                ],
            }

        }
    }
