import hashlib
import json
from pathlib import Path
from typing import Any

from app.schemas.cache import CacheKeyInput, PromptCacheStore, CacheEntry


class PromptCache:
    """
    Persistent application-level cache for deterministic LLM responses.
    """

    def __init__(self, cache_path: str = "app/cache/prompt_cache.json"):
        self.cache_path = Path(cache_path)
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.cache_path.exists():
            self._write(PromptCacheStore())

    def _read(self) -> PromptCacheStore:
        try:
            data = json.loads(
                self.cache_path.read_text(encoding="utf-8")
            )
            return PromptCacheStore.model_validate(data)

        except (json.JSONDecodeError, FileNotFoundError):
            return PromptCacheStore()

    def _write(self, store: PromptCacheStore) -> None:
        temp_path = self.cache_path.with_suffix(".tmp")

        temp_path.write_text(
            json.dumps(store.model_dump(), indent=2),
            encoding="utf-8",
        )

        temp_path.replace(self.cache_path)

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

    def get(self, cache_key: str) -> CacheEntry | None:
        store = self._read()

        return store.entries.get(cache_key)

    def set(
            self,
            *,
            cache_key: str,
            response: str,
            metadata: dict[str, Any] | None = None,
    ) -> CacheEntry:
        store: PromptCacheStore = self._read()

        entry = CacheEntry(
            cache_key=cache_key,
            response=response,
            metadata=metadata or {},
        )

        store.entries[cache_key] = entry

        self._write(store)

        return entry


if __name__ == "__main__":
    cache = PromptCache()

    model = "qwen3:8b"

    system_prompt = """
    You are a QA test planner.
    """

    user_prompt = """
    Create a test plan for SauceDemo login.
    """

    cache_key = cache.create_cache_key(
        cache_input=CacheKeyInput(
            model=model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.0
        )
    )

    print("\n🧠 PROMPT CACHE TEST\n")

    cached = cache.get(cache_key)

    if cached is None:
        print("❌ Cache MISS")

        fake_llm_response = """
        Test Plan:
        1. Open SauceDemo.
        2. Enter valid username.
        3. Enter valid password.
        4. Click Login.
        5. Verify Products page.
        """

        cache.set(
            cache_key=cache_key,
            response=fake_llm_response,
            metadata={
                "agent": "planner",
                "model": model,
            },
        )

        print("💾 Response stored in cache.")

    else:
        print("✅ Cache HIT")
        print("\nCached response:")
        print(cached)

    print(f"\nCache key: {cache_key}")
