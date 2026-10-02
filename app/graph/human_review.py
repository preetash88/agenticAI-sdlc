# from langgraph.types import interrupt
#
# from app.graph.state import QAState
#
#
# def jira_review_node(state: QAState):
#     review = interrupt(
#         {
#             "type": "jira_review",
#             "message": "Please review the Jira issue before continuing.",
#             "issue": {
#                 "key": state["jira_issue_key"],
#                 "project": state["jira_project"],
#                 "summary": state["jira_summary"],
#                 "description": state["jira_description"],
#                 "status": state["jira_status"],
#                 "url": state["jira_url"],
#             },
#             "html": state["jira_preview_html"],
#             "instruction": (
#                 "Approve to continue to the next workflow."
#                 "Reject to stop the workflow."
#             )
#         }
#     )
#
#     if review.get("approved") is True:
#         return {
#             "human_approved": True,
#             "human_feedback": review.get("feedback", ""),
#         }
#
#     return {
#         "human_approved": False,
#         "human_feedback": review.get("feedback", ""),
#     }
