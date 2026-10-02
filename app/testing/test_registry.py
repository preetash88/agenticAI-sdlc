import hashlib
import json
from pathlib import Path
from typing import Any


class TestRegistry:
    """
        Persistent registry used to prevent duplicate test generation.
        """

    def __init__(self, registry_path: str = "app/playwright/test_registry.json"):
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.registry_path.exists():
            self._write({
                "tests": []
            })

    def _read(self) -> dict[str, Any]:
        try:
            with self.registry_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"tests": []}

    def _write(self, data: dict[str, Any]) -> None:
        temp_path = self.registry_path.with_suffix(".tmp")

        with temp_path.open("w", encoding="utf-8") as f:
            f.write(json.dumps(data, indent=2))

        temp_path.replace(self.registry_path)

    @staticmethod
    def create_test_id(scenario: dict[str, Any]) -> str:
        """
                Create a deterministic ID from the canonical scenario definition.
                """
        canonical = json.dumps(scenario, sort_keys=True, separators=(',', ':'))

        return hashlib.sha256(canonical.encode()).hexdigest()

    def find_test(self, test_id: str) -> dict[str, Any] | None:
        data = self._read()

        for test in data["tests"]:
            if test["test_id"] == test_id:
                return test
        return None

    def text_exists(self, test_id: str) -> bool:
        return self.find_test(test_id) is not None

    def register_test(self, scenario: dict[str, Any]) -> dict[str, Any]:
        test_id = self.create_test_id(scenario)

        existing = self.find_test(test_id)

        if existing:
            return {**existing, "status": "EXISTING"}

        test_record = {
            "test_id": test_id,
            "scenario": scenario,
            "status": "CREATED"
        }

        data = self._read()
        data["tests"].append(test_record)
        self._write(data)
        return test_record


if __name__ == "__main__":
    registry = TestRegistry()

    scenario_a = {
        "application": "saucedemo",
        "feature": "login",
        "scenario": "successful_login",
        "expected": "products_page_displayed",
    }

    scenario_b = {
        "application": "saucedemo",
        "feature": "login",
        "scenario": "invalid_login",
        "expected": "error_message_displayed",
    }

    result_1 = registry.register_test(scenario_a)
    # Same scenario again
    result_2 = registry.register_test(scenario_a)

    # Different scenario
    result_3 = registry.register_test(scenario_b)

    print("\n🧪 TEST REGISTRY CHECK\n")

    print("Scenario A - First registration:")
    print(f"  test_id: {result_1['test_id']}")
    print(f"  status:  {result_1['status']}")

    print("\nScenario A - Duplicate registration:")
    print(f"  test_id: {result_2['test_id']}")
    print(f"  status:  {result_2['status']}")

    print("\nScenario B - Different scenario:")
    print(f"  test_id: {result_3['test_id']}")
    print(f"  status:  {result_3['status']}")

    print("\n🔍 Duplicate check:")

    if result_1["test_id"] == result_2["test_id"]:
        print("  ✅ Same scenario produced the same test_id")
    else:
        print("  ❌ Duplicate detection failed")

    if result_1["test_id"] != result_3["test_id"]:
        print("  ✅ Different scenario produced a different test_id")
    else:
        print("  ❌ Different scenarios have the same test_id")
