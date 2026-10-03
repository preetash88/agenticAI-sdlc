import asyncio
from typing import Any

from app.mcp.client import MCPClient, mcp_config
from app.schemas.playwright import PlaywrightMCPNavigationResult


class PlaywrightExplorer:

    def __init__(self, mcp_tools: list[Any]):
        self.tools = {tool.name: tool for tool in mcp_tools if tool.name.startswith("playwright_")}

    def _get_tool(self, name: str):
        tool = self.tools.get(name)

        if tool is None:
            raise ValueError(f"Required Playwright MCP tool '{name}' was not found.")

        return tool

    async def navigate(self, url: str):
        tool = self._get_tool("playwright_browser_navigate")

        return await tool.ainvoke({
            "url": url,
        })

    def extract_snapshot(self, navigation_result: list[dict]) -> str:
        parsed = PlaywrightMCPNavigationResult.model_validate(navigation_result)

        snapshot = parsed.get_snapshot()

        if not snapshot:
            raise RuntimeError(
                "Playwright MCP navigation did not return a snapshot."
            )

        return snapshot

    async def screenshot(self):
        tool = self._get_tool("playwright_browser_screenshot")
        return await tool.ainvoke({})

    async def click(self, ref: str):
        tool = self._get_tool("playwright_browser_click")
        return await tool.ainvoke({"ref": ref})

    async def type(self, ref: str, text: str):
        tool = self._get_tool("playwright_browser_type")
        return await tool.ainvoke({"ref": ref, "text": text})

    async def wait_for(self, time: float):
        tool = self._get_tool("playwright_browser_wait_for")
        return await tool.ainvoke({"time": time})

    async def explore(self, url: str) -> dict:
        print("\n🌐 Explorer: starting navigation...", flush=True)

        navigation = await self.navigate(url)

        print("✅ Explorer: navigation completed.", flush=True)

        snapshot = self.extract_snapshot(navigation)

        if not snapshot:
            raise RuntimeError(
                "Playwright MCP navigation did not return a snapshot."
            )

        return {
            "url": url,
            "navigation": navigation,
            "snapshot": snapshot,
        }


async def main():
    client = MCPClient(mcp_config())

    try:
        tools = await client.connect()

        explorer = PlaywrightExplorer(tools)

        result = await explorer.explore(
            "https://www.saucedemo.com/"
        )

        print("\n🔎 EXPLORATION RESULT")
        print("=" * 70)

        print("\nURL:")
        print(result["url"])

        print("\nSNAPSHOT:")
        print(result["snapshot"])

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
