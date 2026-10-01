import html
import json

from pathlib import Path
from typing import Any

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.types import interrupt, Command

from app.agents.router_agent import RouterAgent
from app.graph.state import QAState
from app.schemas.routing import RoutingDecision


class WorkflowOrchestrator:
    """
        Owns the complete multi-agent workflow.

        Responsibilities:
        - Build LangGraph StateGraph
        - Register workflow nodes
        - Connect edges
        - Handle conditional routing
        - Handle Human-in-the-Loop interruptions
        - Maintain workflow state
        - Persist state through a checkpointer
        - Start and resume workflow execution

        It does NOT:
        - Decide which Jira/MCP/custom tool the LLM should call
        - Run the LLM tool-calling loop
        - Contain Jira-specific reasoning

        Those responsibilities belong to AgentOrchestrator/JiraAgent.
        """

    def __init__(self, *, agents: dict[str, Any], router: RouterAgent, checkpointer=None, review_dir: str = "review"):
        self.agents = agents
        self.router = router

        self.review_dir = Path(review_dir)
        self.review_dir.mkdir(parents=True, exist_ok=True)
        self.checkpointer = checkpointer or InMemorySaver()
        self.graph = self._build_graph()

    # ============================================================
    # GRAPH
    # ============================================================
    def _build_graph(self):
        print("   START → router")
        print("   router → selected agent")
        print("   selected agent → router")
        print("   router → END")

        workflow = StateGraph(QAState)

        # --------------------------------------------------------
        # Agent nodes
        # --------------------------------------------------------
        workflow.add_node("router", self._router_node)
        for agent_name in self.agents:
            workflow.add_node(agent_name, self._create_agent_node(agent_name))
        workflow.add_node("jira_preview", self._jira_preview_node)
        workflow.add_node("human_review", self._human_review_node)

        # Edges
        workflow.add_edge(START, "router")
        workflow.add_conditional_edges("router", self._route_from_router,
                                       {
                                           **{
                                               agent_name: agent_name
                                               for agent_name in self.agents
                                           },
                                           "end": END
                                       })
        for agent_name in self.agents:
            if agent_name == "jira_agent":
                workflow.add_edge(agent_name, "jira_preview")
            else:
                workflow.add_edge(agent_name, "router")

        workflow.add_edge("jira_preview", "human_review")
        workflow.add_conditional_edges("human_review", self._route_after_review, {
            "approved": "router",
            "rejected": END
        })

        return workflow.compile(checkpointer=self.checkpointer)

    async def _router_node(self, state: QAState) -> dict[str, Any]:
        decision: RoutingDecision = await self.router.route(
            user_prompt=state["user_prompt"],
            current_agent=state.get("current_agent"),
            previous_results=state.get("visited_agents", []),
        )

        return {
            "routing_decision": decision.model_dump(),
            "next_agent": decision.next_agent
        }

    def _route_from_router(self, state: QAState) -> str:
        decision: RoutingDecision = RoutingDecision.model_validate(state["routing_decision"])

        if decision.done:
            return "end"

        if not decision.next_agent:
            return "end"

        if decision.next_agent not in self.agents:
            raise ValueError(
                f"Router selected unknown agent: "
                f"{decision.next_agent}"
            )

        return decision.next_agent

    def _create_agent_node(self, agent_name: str):
        async def agent_node(state: QAState) -> dict[str, Any]:
            agent = self.agents[agent_name]

            result = await agent.run(state["user_prompt"])

            visited_agents = [
                *state.get("visited_agents", []),
                agent_name
            ]

            result_state = {
                "current_agent": agent_name,
                "agent_result": result.model_dump(),
                "agent_response": result.response,
                "agent_tool_results": [tool.model_dump() for tool in result.tool_results],
                "visited_agents": visited_agents,
            }

            # ---------------------------------------
            # Jira-specific state extraction
            # ---------------------------------------
            if agent_name == "jira_agent":
                jira_issue = self._extract_jira_issue(result.tool_results)

                if jira_issue:
                    result_state.update({
                        "jira_project": jira_issue.get("project", ""),
                        "jira_issue_key": jira_issue.get("key", ""),
                        "jira_summary": jira_issue.get("summary", ""),
                        "jira_description": jira_issue.get("description", ""),
                        "jira_status": jira_issue.get("status", ""),
                        "jira_raw_result": jira_issue,
                    })

                return result_state

        return agent_node

    # ============================================================
    # PREVIEW NODE
    # ============================================================
    def _jira_preview_node(self, state: QAState) -> dict[str, Any]:
        print("\n📄 Jira Preview node started")
        issue_key = state.get("jira_issue_key")
        print(f"   Issue key: {issue_key}")

        if not issue_key:
            print("❌ No Jira issue key found")
            return {
                "errors": [
                    *state.get("errors", []),
                    "Cannot create Jira preview without an issue key"
                ],

            }

        # --------------------------------------------------------
        # This is explicitly a LOCAL MOCK URL.
        #
        # Later this comes from the real Jira MCP/API response.
        # --------------------------------------------------------
        jira_url = f"http://localhost:8000/jira/browse/{issue_key}"
        print(f"   Jira URL: {jira_url}")

        html_content = self._build_jira_preview_html(state, jira_url)

        html_path = self.review_dir / f"{issue_key}.html"

        html_path.write_text(html_content, encoding="utf-8")

        print(f"   ✓ Preview written to: {html_path.resolve()}")

        result = {
            "jira_url": jira_url,
            "jira_preview_html": html_content,
        }

        print("📄 Jira Preview node completed")

        return result

    # ============================================================
    # JIRA RESULT NORMALIZATION
    # ============================================================
    @staticmethod
    def _extract_jira_issue(tool_results: list[Any]) -> dict[str, Any] | None:
        for tool_result in tool_results:
            if tool_result.tool_name != "create_issue":
                continue

            raw_result = tool_result.result

            if not isinstance(raw_result, list):
                continue

            for item in raw_result:
                if not isinstance(item, dict):
                    continue

                if item.get("type") != "text":
                    continue

                text = item.get("text")

                if not text:
                    continue

                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    continue
        return None

    # ============================================================
    # HITL
    # ============================================================
    def _human_review_node(self, state: QAState) -> dict[str, Any]:
        review_request = {
            "type": "agent_review",
            "agent": state.get("current_agent"),
            "message": "Review the agent response before continuing.",
            "agent_response": state.get("agent_response"),
            "artifact": {
                "type": "jira_issue",
                "key": state.get("jira_issue_key"),
                "project": state.get("jira_project"),
                "summary": state.get("jira_summary"),
                "description": state.get("jira_description"),
                "status": state.get("jira_status"),
                "url": state.get("jira_url"),
            },
            "instruction": (
                "Approve to continue to the "
                "next agent or reject to stop."
            ),
        }

        # --------------------------------------------------------
        # LangGraph pauses here.
        # --------------------------------------------------------
        decision = interrupt(review_request)

        print("\n▶️ Human decision received")

        if not isinstance(decision, dict):
            raise ValueError("Invalid human review decision.")

        approved = bool(decision.get("approved", False))

        feedback = str(decision.get("feedback", ""))

        return {
            "human_approved": approved,
            "human_review": feedback,
        }

    def _route_after_review(self, state: QAState) -> str:
        if state.get("human_approved", False):
            return "approved"

        return "rejected"

    async def resume(
            self,
            *,
            thread_id: str,
            approved: bool,
            feedback: str = "",
    ):
        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        return await self.graph.ainvoke(
            Command(
                resume={
                    "approved": approved,
                    "feedback": feedback,
                }
            ),
            config=config,
        )

    # ============================================================
    # HTML
    # ============================================================
    @staticmethod
    def _build_jira_preview_html(state: QAState, jira_url: str) -> str:
        issue_key = html.escape(
            str(
                state.get(
                    "jira_issue_key",
                    "",
                )
            )
        )

        project = html.escape(
            str(
                state.get(
                    "jira_project",
                    "",
                )
            )
        )

        summary = html.escape(
            str(
                state.get(
                    "jira_summary",
                    "",
                )
            )
        )

        description = html.escape(
            str(
                state.get(
                    "jira_description",
                    "",
                )
            )
        )

        status = html.escape(
            str(
                state.get(
                    "jira_status",
                    "",
                )
            )
        )

        raw_json = html.escape(
            json.dumps(
                state.get(
                    "jira_raw_response",
                    {},
                ),
                indent=2,
                ensure_ascii=False,
            )
        )

        return f"""
                <!DOCTYPE html>

        <html lang="en">

        <head>

        <meta charset="UTF-8">

        <title>
        Jira Review - {issue_key}
        </title>

        <style>

        body {{
            font-family:
                Arial,
                Helvetica,
                sans-serif;

            max-width: 1000px;
            margin: 40px auto;
            padding: 0 20px;

            line-height: 1.6;
        }}

        .card {{
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }}

        .label {{
            font-weight: bold;
        }}

        pre {{
            background: #f5f5f5;
            padding: 20px;
            overflow-x: auto;
            border-radius: 6px;
        }}

        </style>

        </head>

        <body>

        <h1>Jira Review</h1>

        <div class="card">

        <p>
        <span class="label">Issue:</span>
        {issue_key}
        </p>

        <p>
        <span class="label">Project:</span>
        {project}
        </p>

        <p>
        <span class="label">Summary:</span>
        {summary}
        </p>

        <p>
        <span class="label">Status:</span>
        {status}
        </p>

        <p>
        <span class="label">Jira URL:</span>
        <a href="{html.escape(jira_url)}">
        {html.escape(jira_url)}
        </a>
        </p>

        </div>

        <div class="card">

        <h2>Description</h2>

        <p>
        {description}
        </p>

        </div>

        <div class="card">

        <h2>Raw Jira JSON</h2>

        <pre>{raw_json}</pre>

        </div>

        </body>

        </html>
        """

    # ============================================================
    # RUN
    # ============================================================
    async def run(self, *, user_prompt: str, thread_id: str):
        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        initial_state: QAState = {
            "user_prompt": user_prompt,
            "errors": [],
        }

        return await self.graph.ainvoke(
            input=initial_state,
            config=config,
        )
