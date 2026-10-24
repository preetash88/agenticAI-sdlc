"""Run executors: replay (saved run) and live (your real agents)."""
from __future__ import annotations

import asyncio
import json
import re
from pathlib import Path
from typing import Any

from api.guardrail import GuardrailAdapter
from api.store import Run

ROOT = Path(__file__).resolve().parent.parent
LAST_LIVE_RUN = ROOT / "demo_data" / "last_live_run.json"

LIVE_STAGES = [
    {"id": "guardrail", "label": "Input guardrail"},
    {"id": "entry", "label": "Entry decision"},
    {"id": "jira", "label": "Jira (MCP)"},
    {"id": "analysis", "label": "Analysis agent"},
    {"id": "review", "label": "Human review"},
    {"id": "strategy", "label": "Strategy agent"},
]


async def execute(run: Run, guard: GuardrailAdapter, replay: dict, speed: float) -> None:
    try:
        if not await _guardrail_stage(run, guard):
            return
        if run.mode == "live":
            await run_live(run)
        else:
            await run_replay(run, replay, speed)
    except asyncio.CancelledError:
        raise
    except Exception as exc:  # surface the failure in the UI instead of dying silently
        active = next((s for s, v in run.stage_state.items() if v == "active"), None)
        message = f"{type(exc).__name__}: {exc}"
        if active:
            run.emit(active, "failed", message)
        run.finish("failed", message)


async def _guardrail_stage(run: Run, guard: GuardrailAdapter) -> bool:
    """Always real, in both modes, so typing an attack in replay mode still gets blocked."""
    run.emit("guardrail", "active", "Checking the request")
    res = await guard.check(run.user_id, run.prompt)
    run.results["guardrail"] = res
    if not res["allowed"]:
        run.emit("guardrail", "blocked", f"Blocked: {res['category'].replace('_', ' ').lower()}", res)
        run.finish("blocked")
        return False
    title = "Allowed with a warning" if res["action"] == "WARN" else "Request allowed"
    run.emit("guardrail", "done", title, res)
    return True


async def _review_gate(run: Run, payload: dict) -> bool:
    decision = await run.wait_for_review(payload)
    if decision["approved"]:
        run.emit("review", "done", "Approved by reviewer", {"feedback": decision["feedback"]})
        return True
    run.emit("review", "blocked", "Rejected by reviewer", {"feedback": decision["feedback"]})
    run.finish("rejected")
    return False


# --------------------------------------------------------------------- replay
async def run_replay(run: Run, data: dict, speed: float) -> None:
    for step in data["steps"]:
        stage, state = step.get("stage"), step.get("state")
        await asyncio.sleep(step.get("delay", 0.5) / max(speed, 0.1))
        if step.get("kind") == "gate":
            if not await _review_gate(run, step["review"]):
                return
            continue
        if stage == "review" and state == "done":
            continue  # the gate above already emitted the real decision
        run.emit(stage, state, step["title"], step.get("detail"), step.get("results"))
    run.finish("completed")


# ----------------------------------------------------------------------- live
def _coerce_issue(raw: Any) -> dict:
    """The MCP tool can hand back a dict, a JSON string, or a list of content blocks."""
    if isinstance(raw, list) and raw and isinstance(raw[0], dict) and "text" in raw[0]:
        raw = raw[0]["text"]
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            return {"raw": raw}
    return raw if isinstance(raw, dict) else {"raw": str(raw)}


async def run_live(run: Run) -> None:
    # Imported lazily so replay mode works without langgraph/ollama installed.
    from app.agents.entry_agent import EntryAgent
    from app.graph.nodes.analysis import analysis_node
    from app.graph.nodes.jira import jira_node
    from app.graph.nodes.strategy import strategy_node

    entry = EntryAgent()
    run.emit("entry", "active", "Deciding whether agents are needed")
    decision = await entry.classify(user_prompt=run.prompt)
    if not decision.require_agents:
        run.emit("entry", "done", "Answered directly, no agents needed", decision.model_dump())
        run.results["direct_answer"] = await entry.answer(run.prompt)
        run.finish("completed")
        return
    run.emit("entry", "done", "Needs the QA agents", decision.model_dump())

    state: dict[str, Any] = {"jira_input": run.prompt}

    run.emit("jira", "active", "Fetching the issue through the Jira MCP server")
    state.update(await jira_node(state))
    issue = _coerce_issue(state["jira_issue"])
    run.emit("jira", "done", f"Fetched {issue.get('key', 'issue')}", issue, {"jira_issue": issue})

    run.emit("analysis", "active", "Analysing the requirement")
    state.update(await analysis_node(state))
    analysis = state["analysis"].model_dump(mode="json")
    run.emit(
        "analysis",
        "done",
        "Analysis ready",
        {"status": analysis["status"], "requirements": len(analysis["requirements"])},
        {"analysis": analysis},
    )

    approved = await _review_gate(
        run,
        {
            "agent": "analysis_agent",
            "message": "Review the analysis before the strategy agent runs.",
            "summary": {
                "status": analysis["status"],
                "requirements": len(analysis["requirements"]),
                "risks": len(analysis["risks"]),
                "open_ambiguities": sum(a["requires_human_input"] for a in analysis["ambiguities"]),
                "automation": analysis["automation_assessment"]["status"],
            },
        },
    )
    if not approved:
        return

    run.emit("strategy", "active", "Drafting the test strategy")
    state.update(await strategy_node(state))
    strategy = state["strategy"].model_dump(mode="json")
    run.emit("strategy", "done", "Strategy ready", None, {"strategy": strategy})

    LAST_LIVE_RUN.parent.mkdir(parents=True, exist_ok=True)
    LAST_LIVE_RUN.write_text(json.dumps(run.to_replay(), indent=2), encoding="utf-8")
    run.results["recorded_to"] = str(LAST_LIVE_RUN.relative_to(ROOT))
    run.finish("completed")
