from __future__ import annotations

from dataclasses import dataclass

from .schemas import GenerationState, VerifierAction


@dataclass(frozen=True)
class OrchestratorDecision:
    next_node: str
    reason: str = ""


class GenerationOrchestrator:
    name = "GenerationOrchestrator.v2"
    max_revision_rounds = 2
    validation_route_targets = {"verifier", "content_writer", "style_designer", "html_coder"}
    safety_route_targets = {"html_coder"}
    max_verifier_protocol_retries = 1

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
            validation_route = self.validation_route_back_to(state)
            if validation_route in {"verifier_invalid_output", "verifier_blocked"}:
                return OrchestratorDecision(next_node=validation_route, reason="Verifier did not produce a routable validation decision.")
            if validation_route == "verifier_protocol_retry":
                return OrchestratorDecision(next_node=validation_route, reason="Verifier decision was incomplete; retry verifier once.")
            if state.validation_report and state.revision_round >= self.max_revision_rounds:
                return OrchestratorDecision(next_node="max_revision_rounds", reason="Validation did not converge within the revision limit.")
            return OrchestratorDecision(next_node=validation_route, reason="Validation is not complete.")
        if state.safety_report is None or not state.safety_report.ok:
            if state.safety_report and state.revision_round >= self.max_revision_rounds:
                return OrchestratorDecision(next_node="max_revision_rounds", reason="Safety review did not converge within the revision limit.")
            return OrchestratorDecision(next_node=self.safety_route_back_to(state), reason="Safety review is not complete.")
        if state.create_note_proposal is None:
            return OrchestratorDecision(next_node="finalizer", reason="Create note proposal is missing.")
        return OrchestratorDecision(next_node="write_gateway", reason="Ready to write.")

    def validation_route_back_to(self, state: GenerationState) -> str:
        report = state.validation_report
        if report is None:
            return "verifier"
        action = verifier_action(report)
        if action == VerifierAction.PASS:
            return "verifier"
        if action == VerifierAction.REQUEST_EVIDENCE:
            return "verifier"
        if action == VerifierAction.BLOCKED:
            return "verifier_blocked"
        if action != VerifierAction.REQUEST_REVISION:
            return "verifier_invalid_output"
        route = str(report.route_back_to or "").strip()
        if route in self.validation_route_targets:
            return route
        if state.same_node_retries.get("VerifierProtocol", 0) < self.max_verifier_protocol_retries:
            return "verifier_protocol_retry"
        return "verifier_invalid_output"

    def safety_route_back_to(self, state: GenerationState) -> str:
        report = state.safety_report
        if report is None:
            return "safety_reviewer"
        route = str(report.route_back_to or "").strip()
        if route in self.safety_route_targets:
            return route
        return "html_coder"


def verifier_action(report) -> VerifierAction:
    action = getattr(report, "verifier_action", "")
    try:
        action = VerifierAction(str(action or ""))
    except ValueError:
        action = None
    has_evidence_request = bool(getattr(report, "material_queries", None) or getattr(report, "material_read_requests", None))
    if action is None:
        if report.ok:
            return VerifierAction.PASS
        if has_evidence_request:
            return VerifierAction.REQUEST_EVIDENCE
        if str(getattr(report, "route_back_to", "") or "").strip():
            return VerifierAction.REQUEST_REVISION
        return VerifierAction.REQUEST_REVISION
    if report.ok:
        return VerifierAction.PASS
    if has_evidence_request:
        return VerifierAction.REQUEST_EVIDENCE
    return action
