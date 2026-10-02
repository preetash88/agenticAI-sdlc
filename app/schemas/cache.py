from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

class CacheStatus(str, Enum):
    HIT = "HIT"
    MISS = "MISS"

class CacheKeyInput(BaseModel):
    model: str
    system_prompt: str
    user_prompt: str
    temperature: float = 0.0


class CacheEntry(BaseModel):
    cache_key: str
    response: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class PromptCacheStore(BaseModel):
    entries: dict[str, CacheEntry] = Field(default_factory=dict)
