import hashlib
import json
from pathlib import Path
from typing import Any

from app.schemas.test_registry import TestRegistryStore, TestScenario, TestRecord, TestStatus


class TestRegistry:
    """
        Persistent registry used to prevent duplicate test generation.
        """

    def __init__(self, registry_path: str = "app/playwright/test_registry.json"):
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.registry_path.exists():
            self._write(TestRegistryStore())

    def _read(self) -> TestRegistryStore:
        try:
            data = json.loads(
                self.registry_path.read_text(encoding="utf-8")
            )
            return TestRegistryStore.model_validate(data)
        except (json.JSONDecodeError, FileNotFoundError):
            return TestRegistryStore()

    def _write(self, store: TestRegistryStore) -> None:
        temp_path = self.registry_path.with_suffix(".tmp")

        temp_path.write_text(
            json.dumps(store.model_dump(), indent=2),
            encoding="utf-8"
        )

        temp_path.replace(self.registry_path)

    @staticmethod
    def create_test_id(scenario: TestScenario) -> str:
        """
                Create a deterministic ID from the canonical scenario definition.
                """
        canonical = json.dumps(
            scenario.model_dump(),
            sort_keys=True,
            separators=(',', ':')
        )

        return hashlib.sha256(canonical.encode()).hexdigest()

    def find_test(self, test_id: str) -> TestRecord | None:
        store: TestRegistryStore = self._read()

        for test in store.tests:
            if test.test_id == test_id:
                return test
        return None

    def test_exists(self, test_id: str) -> bool:
        return self.find_test(test_id) is not None

    def register_test(self, scenario: TestScenario) -> TestRecord:
        test_id: str = self.create_test_id(scenario)

        existing = self.find_test(test_id)

        if existing:
            existing.status = TestStatus.EXISTING
            return existing

        test_record = TestRecord(
            test_id=test_id,
            status=TestStatus.CREATED,
            scenario=scenario,
        )

        store = self._read()
        store.tests.append(test_record)
        self._write(store)
        return test_record


if __name__ == "__main__":
    registry = TestRegistry()

    scenario_a = TestScenario(
        application="saucedemo",
        feature="login",
        scenario="successful_login",
        expected="products_page_displayed",
    )

    scenario_b = TestScenario(
        application="saucedemo",
        feature="login",
        scenario="invalid_login",
        expected="error_message_displayed",
    )

    result_1 = registry.register_test(scenario_a)
    # Same scenario again
    result_2 = registry.register_test(scenario_a)

    # Different scenario
    result_3 = registry.register_test(scenario_b)

    print("\n🧪 TEST REGISTRY CHECK\n")

    print("Scenario A - First registration:")
    print(f"  test_id: {result_1.test_id}")
    print(f"  status:  {result_1.status.value}")

    print("\nScenario A - Duplicate registration:")
    print(f"  test_id: {result_2.test_id}")
    print(f"  status:  {result_2.status.value}")

    print("\nScenario B - Different scenario:")
    print(f"  test_id: {result_3.test_id}")
    print(f"  status:  {result_3.status.value}")

    print("\n🔍 Duplicate check:")

    if result_1.test_id == result_2.test_id:
        print("  ✅ Same scenario produced the same test_id")
    else:
        print("  ❌ Duplicate detection failed")

    if result_1.test_id != result_3.test_id:
        print("  ✅ Different scenario produced a different test_id")
    else:
        print("  ❌ Different scenarios have the same test_id")
