import redis.asyncio as redis


class ViolationTracker:
    def __init__(
            self,
            redis_url: str = "redis://localhost:6379/0",
            window_seconds: int = 3600,
            max_violations: int = 5,
    ):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.window_seconds = window_seconds
        self.max_violations = max_violations

    def _key(self, user_id: str) -> str:
        return f"guardrails:violations:{user_id}"

    async def record_violation(self, user_id: str) -> int:
        key = self._key(user_id)

        # INCR is atomic in Redis.
        count = await self.redis.incr(key)

        # Set the window only when the key is first created.
        if count == 1:
            await self.redis.expire(key, self.window_seconds)

        return count

    async def get_violation_count(self, user_id: str) -> int:
        key = self._key(user_id)
        count = await self.redis.get(key)
        return int(count) if count is not None else 0

    async def is_blocked(self, user_id: str) -> bool:
        count = await self.get_violation_count(user_id)

        return count >= self.max_violations

    async def close(self) -> None:
        await self.redis.aclose()
