from dataclasses import replace

from ..schemas import ChecklistStatus, GenerationStage, RiskLevel, SafetyReport
from .base import GenerationAgent


class SafetyReviewerAgent(GenerationAgent):
    name = "SafetyReviewer"
    stage = GenerationStage.SAFETY_CHECKING
    output_schema = SafetyReport

    def fake_payload(self, state):
        html = state.html_draft.html if state.html_draft else ""
        blocked = any(token in html.lower() for token in ("<script", "javascript:", "onerror=", "onload="))
        return {
            "ok": not blocked,
            "risk_level": "blocked" if blocked else "low",
            "issues": [{"code": "unsafe_html", "message": "Potential unsafe HTML detected.", "severity": "error"}] if blocked else [],
            "blocked_items": ["unsafe_html"] if blocked else [],
            "warnings": [],
            "route_back_to": "html_coder" if blocked else "",
            "requires_user_confirmation": False,
        }

    def apply_output(self, state, output):
        return replace(state, safety_report=output, create_note_proposal=None)

    def update_execution_checklist(self, state, status, *, notes: str = ""):
        report = state.safety_report
        if report and report.risk_level == RiskLevel.BLOCKED:
            return super().update_execution_checklist(state, ChecklistStatus.FAILED, notes="; ".join(report.blocked_items[:2]) or "Safety review blocked output.")
        if report and (report.issues or report.warnings):
            summary = "; ".join([*(issue.message for issue in report.issues[:2]), *report.warnings[:2]])
            return super().update_execution_checklist(state, ChecklistStatus.WARNING, notes=summary)
        return super().update_execution_checklist(state, status, notes=notes)
