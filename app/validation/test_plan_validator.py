from app.schemas.test_plan import TestPlan


class TestPlanValidator:

    @staticmethod
    def validate(plan: TestPlan) -> list[str]:
        errors = []

        if not plan.test_case_id:
            errors.append("Test case ID is missing.")

        if not plan.title:
            errors.append("Test case title is missing.")

        if not plan.steps:
            errors.append("Test plan must contain at least one step.")

        for index, step in enumerate(plan.steps, start=1):
            if step.step_number != index:
                errors.append(
                    f"Step numbering is invalid. Expected {index}, "
                    f"got {step.step_number}."
                )
            if not step.action.strip():
                errors.append(
                    f"Step {step.step_number} has no action."
                )
            if not step.expected_result.strip():
                errors.append(
                    f"Step {step.step_number} has no expected result."
                )
        if not plan.preconditions:
            errors.append("At least one precondition is required.")

        if not plan.suites:
            errors.append("At least one test suite is required.")

        if not plan.automation:
            errors.append("This test case must be marked for automation.")

        return errors
