import asyncio

from app.caching.prompt_cache import PromptCache
from app.orchestrators.agent_orchestrator import AgentOrchestrator


async def main():

    cache = PromptCache()

    agent = AgentOrchestrator(
        agent_name="cache_test_agent",
        custom_tools=[],
        mcp_tools=[],
        system_prompt="""
You are a QA assistant.
Answer the user's question concisely.
Do not use tools.
""",
        model="qwen3:8b",
        temperature=0,
        prompt_cache=cache,
        enable_cache=True,
    )

    prompt = """
Explain what a smoke test is in software testing.
"""

    print("\n========== FIRST CALL ==========\n")

    result_1 = await agent.run(prompt)

    print("\nResponse:")
    print(result_1.response)

    print("\n========== SECOND CALL ==========\n")

    result_2 = await agent.run(prompt)

    print("\nResponse:")
    print(result_2.response)

    await cache.close()


if __name__ == "__main__":
    asyncio.run(main())