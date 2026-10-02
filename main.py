import asyncio

from app.agents.entry_agent import EntryAgent
from app.agents.jira_agent import JiraAgent
from app.agents.router_agent import RouterAgent
from app.agents.strategy_agent import StrategyAgent
from app.mcp.client import MCPClient, jira_mcp_config
from app.orchestrators.workflow_orchestrator import WorkflowOrchestrator
from app.tools.test_data import generate_test_data
from app.tools.validation import validate_project_key


async def main():
    entry_agent = EntryAgent()

    mcp_client = MCPClient(
        jira_mcp_config()
    )

    try:

        # ---------------------------------------
        # MCP
        # ---------------------------------------

        mcp_tools = await mcp_client.connect()

        print("\nAvailable MCP tools:\n")

        for tool in mcp_tools:
            print(f"  🔌 {tool.name}")

        # ---------------------------------------
        # Custom tools
        # ---------------------------------------

        custom_tools = [
            generate_test_data,
            validate_project_key,
        ]

        # ---------------------------------------
        # Agent
        # ---------------------------------------

        jira_agent = JiraAgent(
            custom_tools=custom_tools,
            mcp_tools=mcp_tools,
        )
        strategy_agent = StrategyAgent(
            custom_tools=[],
            mcp_tools=[],
        )

        agents = {
            "jira_agent": jira_agent,
            "strategy_agent": strategy_agent,
        }

        # ---------------------------------------
        # User request
        # ---------------------------------------

        # user_prompt = """
        # Create a Jira issue for the Login feature.
        #
        # Project: QA
        #
        # Description:
        # Verify that users can log in successfully using valid credentials.
        #
        # Workflow:
        # 1. Create the Jira issue.
        # 2. Get the Jira issue reviewed.
        # 3. Wait for human approval.
        # 4. After approval, create a QA test strategy for this feature.
        # """

        user_prompt = """
               Who is Doctor Doom?
               """

        thread_id = "qa-run-001"

        # ---------------------------------------
        # RUN WORKFLOW
        # ---------------------------------------

        decision = await entry_agent.classify(
            user_prompt=user_prompt,
        )

        print("\n🧭 ENTRY DECISION")
        print(f"   Requires agents: {decision.require_agents}")
        print(f"   Reason: {decision.reason}")

        if not decision.require_agents:
            print("\n🤖 Direct response:\n")

            response = await entry_agent.answer(
                user_prompt
            )
            print(response)

            return

        # ---------------------------------------
        # Router
        # ---------------------------------------

        router = RouterAgent()

        # ---------------------------------------
        # Workflow
        # ---------------------------------------

        workflow = WorkflowOrchestrator(
            agents=agents,
            router=router,
        )

        result = await workflow.run(
            user_prompt=user_prompt,
            thread_id=thread_id,
        )

        # ---------------------------------------
        # HUMAN-IN-THE-LOOP
        # ---------------------------------------

        interrupts = result.get("__interrupt__")

        if interrupts:
            print("\n⏸️ Waiting for human review...")
            review = interrupts[0].value

            print("\n" + "=" * 60)
            print("🧑 HUMAN REVIEW REQUIRED")
            print("=" * 60)

            print(
                f"\nAgent: {review.get('agent')}"
            )

            print(
                f"\nMessage:\n"
                f"{review.get('message', '')}"
            )

            print(
                "\nAgent response:"
            )

            print(
                review.get(
                    "agent_response",
                    "",
                )
            )

            artifact = review.get(
                "artifact",
                {},
            )

            print("\nArtifact:")

            print(
                f"  Type: {artifact.get('type')}"
            )

            print(
                f"  Issue: {artifact.get('key')}"
            )

            print(
                f"  Project: {artifact.get('project')}"
            )

            print(
                f"  Summary: {artifact.get('summary')}"
            )

            print(
                f"  Status: {artifact.get('status')}"
            )

            print(
                f"  URL: {artifact.get('url')}"
            )

            print("\n" + "=" * 60)

            decision = input(
                "\nApprove? [y/n]: "
            ).strip().lower()

            feedback = input(
                "Feedback (optional): "
            ).strip()

            # ---------------------------------------
            # RESUME WORKFLOW
            # ---------------------------------------

            print("\n▶️ Resuming workflow...\n")

            result = await workflow.resume(
                thread_id=thread_id,
                approved=(decision == "y"),
                feedback=feedback,
            )

        # ---------------------------------------
        # FINAL RESULT
        # ---------------------------------------

        print("\n🔎 Workflow completed")

        # print(result)

    finally:

        await mcp_client.close()


if __name__ == "__main__":
    asyncio.run(main())
