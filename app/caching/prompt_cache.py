import asyncio
import hashlib
import json
from typing import Any

import redis.asyncio as redis_async

from app.schemas.cache import CacheKeyInput, PromptCacheStore, CacheEntry


class PromptCache:
    """
    Redis-backed application-level cache for LLM responses.
    """

    def __init__(
            self,
            redis_url: str = "redis://localhost:6379/0",
            namespace: str = "agentic-qa:prompt",
            default_ttl: int = 86400
    ):
        self.redis = redis_async.Redis.from_url(
            url=redis_url,
            decode_responses=True,
        )
        self.namespace = namespace
        self.default_ttl = default_ttl

    @staticmethod
    def create_cache_key(
            *,
            cache_input: CacheKeyInput
    ) -> str:
        canonical = json.dumps(
            cache_input.model_dump(),
            sort_keys=True,
            separators=(",", ":"),
        )

        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def _build_key(self, cache_key: str) -> str:
        return f"{self.namespace}.{cache_key}"

    async def get(self, cache_key: str) -> CacheEntry | None:
        key = self._build_key(cache_key)

        value = await self.redis.get(key)

        if value is None:
            return None

        return CacheEntry.model_validate_json(value)

    async def set(
            self,
            *,
            cache_key: str,
            response: str,
            metadata: dict[str, Any] | None = None,
            ttl: int | None = None,
    ) -> CacheEntry:

        entry = CacheEntry(
            cache_key=cache_key,
            response=response,
            metadata=metadata or {},
        )

        key = self._build_key(cache_key)

        await self.redis.set(
            key,
            entry.model_dump_json(),
            ex=ttl or self.default_ttl,

        )

        return entry

    async def delete(self, cache_key: str) -> bool:
        key = self._build_key(cache_key)
        deleted = await self.redis.delete(key)
        return deleted > 0

    async def clear(self) -> None:
        """
                Clear only keys belonging to this cache namespace.
                """
        pattern = f"{self.namespace}:*"

        keys = []

        async for key in self.redis.scan_iter(match=pattern):
            keys.append(key)

        if keys:
            await self.redis.delete(*keys)

    async def ping(self) -> bool:
        return await self.redis.ping()

    async def close(self) -> None:
        await self.redis.aclose()


async def main():
    cache = PromptCache()

    print("\n🧠 REDIS PROMPT CACHE TEST\n")

    # Verify Redis connection
    connected = await cache.ping()

    if not connected:
        print("❌ Redis connection failed")
        return

    print("✅ Redis connection successful")

    cache_input = CacheKeyInput(
        cache_version="v1",
        model="qwen3:8b",
        system_prompt="You are a QA test planner.",
        user_prompt="Create a test plan for SauceDemo login.",
        temperature=0,
    )

    cache_key = cache.create_cache_key(cache_input=cache_input)

    print(f"\n🔑 Cache key:")
    print(cache_key)

    cached = await cache.get(cache_key)

    if cached is None:

        print("\n❌ Cache MISS")

        response = """
    Test Plan:
    1. Open SauceDemo.
    2. Enter valid username.
    3. Enter valid password.
    4. Click Login.
    5. Verify Products page.
    """

        await cache.set(
            cache_key=cache_key,
            response=response,
            metadata={
                "agent": "planner",
                "model": "qwen3:8b",
            },
        )

        print("💾 Response stored in Redis")

    else:

        print("\n✅ Cache HIT")
        print("\nCached response:")
        print(cached.response)

    await cache.close()

if __name__ == "__main__":
    asyncio.run(main())