"""FastAPI layer over the agentic QA platform.

Run from the repo root:   uvicorn api.server:app --port 8000
(Do not use --reload with live mode on Windows: MCP stdio subprocesses need the default loop.)
"""
from __future__ import annotations

import asyncio
import importlib.util
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.chdir(ROOT)  # your agents load agent_definitions/ and mock_data/ by relative path

import httpx
import redis.asyncio as aioredis
from fastapi import FastAPI, HTTPException

from api.guardrail import GuardrailAdapter, run_suite
from api.runner import LIVE_STAGES, execute
from api.schemas import GuardrailRequest, RegistryRequest, ReviewDecision, StartRun
from api.store import TERMINAL, RunStore
from app.schemas.test_registry import TestRegistryStore, TestScenario
from app.testing.test_registry import TestRegistry

REPLAY_FILE = Path(os.getenv("REPLAY_FILE", ROOT / "demo_data" / "replay_run.json"))
REPLAY_SPEED = float(os.getenv("REPLAY_SPEED", "1.0"))
DEMO_REGISTRY = ROOT / "demo_data" / "demo_registry.json"
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

app = FastAPI(title="Agentic QA control room API", version="0.1.0")
store = RunStore()
guard = GuardrailAdapter()
_tasks: set[asyncio.Task] = set()


def _load_replay() -> dict:
    if not REPLAY_FILE.exists():
        raise HTTPException(500, f"Replay file not found: {REPLAY_FILE}")
    return json.loads(REPLAY_FILE.read_text(encoding="utf-8"))


def _registry() -> TestRegistry:
    return TestRegistry(registry_path=str(DEMO_REGISTRY))  # never touches the repo's real registry


# --------------------------------------------------------------------- health
@app.get("/health")
async def health() -> dict:
    redis_ok = ollama_ok = False
    try:
        client = aioredis.from_url(REDIS_URL)
        redis_ok = bool(await asyncio.wait_for(client.ping(), 1.0))
        await client.aclose()
    except Exception:
        pass
    try:
        async with httpx.AsyncClient(timeout=1.0) as http:
            ollama_ok = (await http.get(f"{OLLAMA_URL}/api/tags")).status_code == 200
    except Exception:
        pass
    replay_stages = _load_replay()["stages"] if REPLAY_FILE.exists() else []
    live_deps = all(importlib.util.find_spec(m) for m in ("langgraph", "langchain_ollama"))
    return {
        "api": True,
        "redis": redis_ok,
        "ollama": ollama_ok,
        "live_ready": live_deps and ollama_ok,
        "replay_ready": REPLAY_FILE.exists(),
        "stages": {"replay": replay_stages, "live": LIVE_STAGES},
    }


# ------------------------------------------------------------------ guardrails
@app.post("/guardrail/check")
async def guardrail_check(body: GuardrailRequest) -> dict:
    return await guard.check(body.user_id, body.prompt)


@app.get("/guardrail/suite")
async def guardrail_suite() -> dict:
    return await run_suite(guard)


@app.delete("/guardrail/violations/{user_id}")
async def guardrail_reset(user_id: str) -> dict:
    return {"reset": await guard.reset(user_id)}


# ------------------------------------------------------------------------ runs
@app.post("/runs", status_code=202)
async def start_run(body: StartRun) -> dict:
    replay = _load_replay()
    if body.mode == "live" and not importlib.util.find_spec("langgraph"):
        raise HTTPException(400, "Live mode needs your agent dependencies (langgraph, langchain-ollama).")
    stages = replay["stages"] if body.mode == "replay" else LIVE_STAGES
    run = store.create(mode=body.mode, prompt=body.prompt, user_id=body.user_id, stages=stages)
    task = asyncio.create_task(execute(run, guard, replay, REPLAY_SPEED))
    _tasks.add(task)
    task.add_done_callback(_tasks.discard)
    return run.public()


@app.get("/runs")
async def list_runs() -> list[dict]:
    return [
        {"id": r.id, "mode": r.mode, "status": r.status, "prompt": r.prompt[:80]}
        for r in store.recent()
    ]


@app.get("/runs/{run_id}")
async def get_run(run_id: str) -> dict:
    run = store.get(run_id)
    if not run:
        raise HTTPException(404, "Run not found")
    return run.public()


@app.post("/runs/{run_id}/review")
async def review_run(run_id: str, body: ReviewDecision) -> dict:
    run = store.get(run_id)
    if not run:
        raise HTTPException(404, "Run not found")
    if run.status != "awaiting_review":
        raise HTTPException(409, f"Run is {run.status}, not waiting for review")
    run.submit_review(body.approved, body.feedback)
    return {"ok": True}


# -------------------------------------------------------------------- registry
@app.get("/registry")
def registry_list() -> dict:
    return _registry()._read().model_dump(mode="json")


@app.post("/registry/register")
def registry_register(body: RegistryRequest) -> dict:
    reg = _registry()
    scenario = TestScenario(**{k: v.strip() for k, v in body.model_dump().items()})
    test_id = reg.create_test_id(scenario)
    existed = reg.test_exists(test_id)  # checked first: register_test reports duplicates as CREATED
    record = reg.register_test(scenario)
    return {
        "duplicate": existed,
        "status": "EXISTING" if existed else "CREATED",
        "test_id": record.test_id,
        "test_case_id": record.test_case_id,
        "scenario": record.scenario.model_dump(),
    }


@app.delete("/registry")
def registry_reset() -> dict:
    reg = _registry()
    reg._write(TestRegistryStore())
    return {"reset": True}


@app.get("/artifacts/test-plan")
def artifact_test_plan() -> dict:
    path = ROOT / "playwright" / "test_plan.md"
    return {"exists": path.exists(), "markdown": path.read_text(encoding="utf-8") if path.exists() else ""}
