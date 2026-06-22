from __future__ import annotations

from dataclasses import dataclass

from .schemas import GenerationState


@dataclass(frozen=True)
class OrchestratorDecision:
    next_node: str
    reason: str = ""


class GenerationOrchestrator:
    name = "GenerationOrchestrator.v2"
    max_revision_rounds = 2

    def decide_next(self, state: GenerationState) -> OrchestratorDecision:
        if state.parsed_document is None:
            return OrchestratorDecision(next_node="ingest", reason="Document has not been parsed.")
        if state.requirement_brief is None:
            return OrchestratorDecision(next_node="requirement_analyst", reason="Requirement brief is missing.")
        if state.plan_draft is None:
            return OrchestratorDecision(next_node="planner", reason="Plan draft is missing.")
        if state.content_draft is None:
            return OrchestratorDecision(next_node="content_writer", reason="Content draft is missing.")
        if state.style_brief is None:
            return OrchestratorDecision(next_node="style_designer", reason="Style brief is missing.")
        if state.html_draft is None:
            return OrchestratorDecision(next_node="html_coder", reason="HTML draft is missing.")
        if state.validation_report is None or not state.validation_report.ok:
            if state.validation_report and state.revision_round >= self.max_revision_rounds:
                return OrchestratorDecision(next_node="max_revision_rounds", reason="Validation did not converge within the revision limit.")
            return OrchestratorDecision(next_node=state.validation_report.route_back_to if state.validation_report else "verifier", reason="Validation is not complete.")
        if state.safety_report is None or not state.safety_report.ok:
            if state.safety_report and state.revision_round >= self.max_revision_rounds:
                return OrchestratorDecision(next_node="max_revision_rounds", reason="Safety review did not converge within the revision limit.")
            return OrchestratorDecision(next_node=state.safety_report.route_back_to if state.safety_report else "safety_reviewer", reason="Safety review is not complete.")
        if state.create_note_proposal is None:
            return OrchestratorDecision(next_node="finalizer", reason="Create note proposal is missing.")
        return OrchestratorDecision(next_node="write_gateway", reason="Ready to write.")
