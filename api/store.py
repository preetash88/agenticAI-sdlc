"""In-memory run state shared by the replay and live runners.

A Run is the single source of truth the dashboard polls. It also records
every step it emits, so a live run can be saved and replayed later.
"""
from __future__ import annotations

import asyncio
import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

TERMINAL = {"completed", "blocked", "rejected", "failed"}
MAX_RECORDED_DELAY = 6.0  # seconds; keeps a replayed LLM call from feeling endless


def plain(obj: Any) -> Any:
    """Force anything (enums, pydantic dumps, datetimes) into plain JSON types."""
    if obj is None:
        return None
    return json.loads(json.dumps(obj, default=str))


@dataclass
class Run:
    mode: str
    prompt: str
    user_id: str
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:10])
    status: str = "running"
    stages: list[dict] = field(default_factory=list)
    stage_state: dict[str, str] = field(default_factory=dict)
    events: list[dict] = field(default_factory=list)
    results: dict[str, Any] = field(default_factory=dict)
    review: dict | None = None
    error: str | None = None
    created_at: float = field(default_factory=time.time)
    finished_at: float | None = None

    _steps: list[dict] = field(default_factory=list, repr=False)
    _last_step: float = field(default_factory=time.monotonic, repr=False)
    _gate: asyncio.Event = field(default_factory=asyncio.Event, repr=False)
    _decision: dict | None = field(default=None, repr=False)

    # ------------------------------------------------------------------ events
    def _log(self, stage: str, state: str, title: str, detail: Any = None) -> None:
        self.stage_state[stage] = state
        self.events.append(
            {
                "t": round(time.time() - self.created_at, 2),
                "stage": stage,
                "state": state,
                "title": title,
                "detail": plain(detail),
            }
        )

    def _delay(self) -> float:
        now = time.monotonic()
        delay = min(now - self._last_step, MAX_RECORDED_DELAY)
        self._last_step = now
        return round(delay, 2)

    def emit(
        self,
        stage: str,
        state: str,
        title: str,
        detail: Any = None,
        results: dict[str, Any] | None = None,
    ) -> None:
        """state: active | done | waiting | blocked | failed | skipped"""
        results = plain(results)
        if results:
            self.results.update(results)
        self._log(stage, state, title, detail)
        self._steps.append(
            {
                "kind": "event",
                "delay": self._delay(),
                "stage": stage,
                "state": state,
                "title": title,
                "detail": plain(detail),
                "results": results,
            }
        )

    # ------------------------------------------------------------- human gate
    async def wait_for_review(self, payload: dict, timeout: float = 1800) -> dict:
        payload = plain(payload)
        self.review = payload
        self.status = "awaiting_review"
        self._log("review", "waiting", "Waiting for human review")
        self._steps.append(
            {"kind": "gate", "delay": self._delay(), "stage": "review", "review": payload}
        )
        self._gate.clear()
        self._decision = None
        try:
            await asyncio.wait_for(self._gate.wait(), timeout)
        except asyncio.TimeoutError:
            self._decision = {"approved": False, "feedback": "Review timed out."}
        self.status = "running"
        self.review = None
        self._last_step = time.monotonic()
        return self._decision or {"approved": False, "feedback": ""}

    def submit_review(self, approved: bool, feedback: str) -> None:
        self._decision = {"approved": approved, "feedback": feedback.strip()}
        self._gate.set()

    # ---------------------------------------------------------------- finish
    def finish(self, status: str, error: str | None = None) -> None:
        self.status = status
        self.error = error
        self.finished_at = time.time()

    def public(self) -> dict:
        end = self.finished_at or time.time()
        return {
            "id": self.id,
            "mode": self.mode,
            "prompt": self.prompt,
            "status": self.status,
            "stages": self.stages,
            "stage_state": self.stage_state,
            "events": self.events,
            "results": self.results,
            "review": self.review,
            "error": self.error,
            "elapsed": round(end - self.created_at, 1),
        }

    def to_replay(self) -> dict:
        """Everything except the guardrail stage, which always runs for real."""
        return {
            "_note": "Recorded from a live run. Copy to demo_data/replay_run.json to replay it.",
            "prompt": self.prompt,
            "stages": self.stages,
            "steps": [s for s in self._steps if s.get("stage") != "guardrail"],
        }


class RunStore:
    def __init__(self) -> None:
        self._runs: dict[str, Run] = {}

    def create(self, **kwargs: Any) -> Run:
        run = Run(**kwargs)
        self._runs[run.id] = run
        return run

    def get(self, run_id: str) -> Run | None:
        return self._runs.get(run_id)

    def recent(self, n: int = 10) -> list[Run]:
        return sorted(self._runs.values(), key=lambda r: r.created_at, reverse=True)[:n]
