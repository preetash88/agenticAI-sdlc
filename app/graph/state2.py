from typing import TypedDict

from app.schemas.feature_analysis import FeatureAnalysis
from app.schemas.test_strategy import TestStrategy


class QAWorkflowState(TypedDict, total=False):
    jira_input: str
    jira_issue: dict

    analysis: FeatureAnalysis
    analysis_errors: list[str]

    strategy: TestStrategy
