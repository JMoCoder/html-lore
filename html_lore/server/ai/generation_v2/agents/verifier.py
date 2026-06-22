from dataclasses import replace

from ..schemas import ChecklistStatus, GenerationStage, ValidationReport
from .base import GenerationAgent


class VerifierAgent(GenerationAgent):
    name = "Verifier"
    stage = GenerationStage.VERIFYING
    output_schema = ValidationReport

    def fake_payload(self, state):
        ok = bool(state.html_draft and state.html_draft.html.strip() and state.content_draft and state.content_draft.title.strip())
        return {
            "ok": ok,
            "score": 0.82 if ok else 0.0,
            "checked_items": [
                {"id": "html", "title": "HTML draft exists", "passed": bool(state.html_draft and state.html_draft.html.strip())},
                {"id": "content", "title": "Content draft exists", "passed": bool(state.content_draft and state.content_draft.title.strip())},
            ],
            "issues": [] if ok else [{"code": "missing_output", "message": "HTML or content draft is missing.", "severity": "error"}],
            "route_back_to": "" if ok else "html_coder",
            "retry_instruction": "" if ok else "Regenerate missing draft fields.",
        }

    def apply_output(self, state, output):
        return replace(state, validation_report=output)

    def update_execution_checklist(self, state, status, *, notes: str = ""):
        report = state.validation_report
        if report and report.ok and report.issues:
            return super().update_execution_checklist(state, ChecklistStatus.WARNING, notes="; ".join(issue.message for issue in report.issues[:2]))
        if report and not report.ok:
            return super().update_execution_checklist(state, ChecklistStatus.FAILED, notes=report.retry_instruction or "; ".join(issue.message for issue in report.issues[:2]))
        return super().update_execution_checklist(state, status, notes=notes)
