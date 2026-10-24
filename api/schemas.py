"""Request models for the control-room API."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class StartRun(BaseModel):
    prompt: str = Field(min_length=1, max_length=10_000)
    mode: Literal["replay", "live"] = "replay"
    user_id: str = "demo-user"


class ReviewDecision(BaseModel):
    approved: bool
    feedback: str = ""


class GuardrailRequest(BaseModel):
    prompt: str = Field(max_length=20_000)
    user_id: str = "demo-user"


class RegistryRequest(BaseModel):
    application: str = Field(min_length=1)
    feature: str = Field(min_length=1)
    scenario: str = Field(min_length=1)
    expected: str = Field(min_length=1)
