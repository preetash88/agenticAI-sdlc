# Agentic QA control room

FastAPI + Streamlit layer on top of this repo. It wraps your existing agents, guardrails and registry; it does not change them.

```
api/        FastAPI: runs, human-review gate, guardrails, registry
dashboard/  Streamlit UI (app.py, theme.py)
demo_data/  replay_run.json (saved run), generated: last_live_run.json, demo_registry.json
.streamlit/ theme
```

## Run it

From the repo root:

```bash
uv add fastapi "uvicorn[standard]" streamlit requests httpx     # or: pip install -r requirements-dashboard.txt
uv run uvicorn api.server:app --port 8000                       # terminal 1  (no --reload on Windows in live mode)
uv run streamlit run dashboard/app.py                           # terminal 2
```

Optional but recommended: `redis-server` (enables the five-strikes lockout). Without it the guardrail still works and the UI says the lockout is off.

## Two modes

| | Replay (default) | Live |
|---|---|---|
| Guardrail | real | real |
| Human approval gate | real | real |
| Jira / analysis / strategy / test plan | saved run in `demo_data/replay_run.json` | your agents via Ollama `qwen3:8b` + Jira MCP |
| Needs | nothing | Ollama running, Node/uv for the MCP servers |

`replay_run.json` is **hand-authored sample output**, validated against your Pydantic schemas. To replace it with a real one: do a live run, then copy `demo_data/last_live_run.json` over `demo_data/replay_run.json`. Every successful live run is saved automatically.

Live mode runs `jira_node -> analysis_node -> [human gate] -> strategy_node` directly. It does not yet go through `WorkflowOrchestrator` (router + LangGraph `interrupt`), and the Playwright explorer/planner is not wired in. The request must contain a Jira key such as `DEMO-101`.

Env vars: `REPLAY_SPEED` (default 1.0, higher is faster), `REPLAY_FILE`, `REDIS_URL`, `OLLAMA_URL`, `QA_API_URL`.

## Pitch run-sheet (about 4 minutes)

1. **Pipeline run, replay mode.** Start the default request. Point at the rail: the square node is the human gate.
2. When it pauses, read the analysis: risks, the "needs a person" question about MFA. Type a feedback line, approve. Strategy and the test case appear.
3. **Guardrail lab.** Click "Prompt injection", Check. Then "Run evaluation suite" (6 of 6).
4. Back on **Pipeline run**, type an injection as the request and start: it stops at the first node, no agent runs.
5. **Test registry.** Register the same scenario twice: created, then "already exists".

Closing line: same shape as the social-media agent in the reel (agents work, a human approves), applied to QA.

## Fixes worth making before you show the repo

1. **promptfoo eval is broken.** `app/scripts/promptfoo_guardrail.py` returns `"DENIED"` but `promptfooconfig.yaml` asserts `"BLOCKED"`, and the provider path should be `file://app/scripts/promptfoo_guardrail.py`. Change `"DENIED"` to `"BLOCKED"` and fix the path.
2. **Registry reports duplicates as CREATED.** In `app/testing/test_registry.py`, `register_test`, the duplicate branch sets `test.status = TestStatus.CREATED`. It should be `TestStatus.EXISTING`. (The API works around it by checking existence first.)
3. **`GuardrailService` has no abuse detector.** Only the legacy `InputGuardrail` does. The dashboard adds that check on top so "You are stupid" is blocked; better to move it into the service as a detector.
4. **Verify MCP tool names in live mode.** `jira_node` looks for `jira_get_issue` and the Playwright explorer for `playwright_browser_navigate`. If those names don't match what `MCPAdapter` returns, live mode fails at the Jira stage. Print `[t.name for t in tools]` once to check.
5. **Repo hygiene (it's public):** empty README, committed `.idea/`, `test.html`, and `agentic-qa-phase1.zip`. `main.py` is hardcoded to a "bomb" prompt for the guardrail test.
6. Add to `.gitignore`: `demo_data/last_live_run.json`, `demo_data/demo_registry.json`.