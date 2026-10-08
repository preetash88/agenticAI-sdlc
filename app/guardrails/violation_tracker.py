import redis


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

    async def record_violation(self, user_id: str) -> int:
        key = f"guardrail:violations:{user_id}"

        count = await self.redis.incr(key)

        if count == 1:
            await self.redis.expire(key, self.window_seconds)

        return count

    async def is_blocked(self, user_id: str) -> bool:
        key = f"guardrail:violations:{user_id}"

        count = await self.redis.get(key)

        return (
                count is not None
                and int(count) >= self.max_violations
        )
