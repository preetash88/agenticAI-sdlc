import asyncio

from app.graph.workflow import build_workflow


async def main():

    workflow = build_workflow()

    result = await workflow.ainvoke(
        {
            "jira_input": "DEMO-101"
        }
    )

    print("\n==============================")
    print("JIRA MCP OUTPUT")
    print("==============================")

    print(result["jira_issue"])

    print("\n==============================")
    print("ANALYSIS AGENT OUTPUT")
    print("==============================")

    print(
        result["analysis"].model_dump_json(
            indent=2
        )
    )


if __name__ == "__main__":
    asyncio.run(main())