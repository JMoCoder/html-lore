from __future__ import annotations

from dataclasses import asdict
from typing import Any

from html_lore.server.ai.jobs import AIJobStore
from html_lore.server.ai.runs import AIRunStore
from html_lore.server.config import ServerSettings

from .schemas import ChecklistItem, GenerationEngine, GenerationJobStatus, GenerationStage, GenerationState, StageTraceEvent, normalize_for_json


class GenerationStore:
    def __init__(self, settings: ServerSettings) -> None:
        self.settings = settings
        self.jobs = AIJobStore(settings)
        self.runs = AIRunStore(settings)

    def create_job(
        self,
        *,
        kind: str,
        label: str,
        payload: dict[str, Any] | None = None,
        current_stage: GenerationStage = GenerationStage.QUEUED,
    ) -> dict[str, Any]:
        job = self.jobs.create(kind=kind, label=label, payload=payload)
        return self.jobs.update(
            str(job["job_id"]),
            {
                "generation_engine": GenerationEngine.V2.value,
                "current_stage": current_stage.value,
                "stage_trace": [],
                "execution_checklist": [],
                "agent_artifacts": [],
            },
        )

    def update_job_status(
        self,
        job_id: str,
        *,
        status: GenerationJobStatus | str | None = None,
        stage: GenerationStage | str | None = None,
        message: str = "",
        error: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        values: dict[str, Any] = {}
        if status is not None:
            values["status"] = status.value if isinstance(status, GenerationJobStatus) else str(status)
        if stage is not None:
            values["current_stage"] = stage.value if isinstance(stage, GenerationStage) else str(stage)
        if message:
            values["message"] = message
        if error is not None:
            values["error"] = error
        return self.jobs.update(job_id, values)

    def append_stage_trace(self, job_id: str, event: StageTraceEvent) -> dict[str, Any]:
        job = self.jobs.get(job_id, include_private=True)
        trace = job.get("stage_trace") if isinstance(job.get("stage_trace"), list) else []
        trace = [*trace, normalize_for_json(asdict(event))]
        return self.jobs.update(job_id, {"current_stage": event.stage.value, "stage_trace": trace})

    def update_execution_checklist(self, job_id: str, checklist: list[ChecklistItem]) -> dict[str, Any]:
        return self.jobs.update(job_id, {"execution_checklist": public_execution_checklist(checklist)})

    def save_run(self, run: dict[str, Any]) -> dict[str, Any]:
        data = {**run, "generation_engine": GenerationEngine.V2.value}
        if isinstance(data.get("execution_checklist"), list):
            data["execution_checklist"] = public_execution_checklist(data["execution_checklist"])
        return self.runs.add(data)

    def public_state_summary(self, state: GenerationState) -> dict[str, Any]:
        stage_trace = normalize_for_json([asdict(event) for event in state.stage_trace])
        return {
            "job_id": state.job_id,
            "run_id": state.run_id,
            "generation_engine": GenerationEngine.V2.value,
            "current_stage": state.current_step,
            "stage_trace": stage_trace,
            "skill_trace": public_skill_trace(state),
            "agent_artifacts": normalize_for_json([asdict(event) for event in state.agent_artifacts]),
            "execution_checklist": public_execution_checklist(state.execution_checklist, stage_trace=stage_trace),
        }


def public_skill_trace(state: GenerationState) -> list[dict[str, Any]]:
    trace = normalize_for_json([asdict(event) for event in state.skill_trace])
    needs = state.plan_draft.tool_needs if state.plan_draft else []
    for entry in trace:
        if not isinstance(entry, dict):
            continue
        if not entry.get("kind"):
            entry["kind"] = "default" if str(entry.get("id") or "") in {"html_page_design", "safe_static_html", "content_quality_review"} else "enhanced"
        reason = skill_trigger_reason(str(entry.get("id") or ""), needs)
        if reason:
            entry["trigger_reason"] = reason
    return trace


def skill_trigger_reason(skill_id: str, needs: list[Any]) -> str:
    if not skill_id or not needs:
        return ""
    keywords_by_skill = {
        "presentation_surface_design": ("presentation", "pitch", "deck", "roadshow", "briefing", "showcase", "launch", "ppt"),
        "architecture_explainer_design": ("architecture", "workflow", "system", "process", "pipeline", "state machine", "runtime", "agent", "edge", "loop", "diagram"),
        "component_pattern_html": ("component", "cards", "grid", "timeline", "process flow", "comparison", "callout", "responsive table", "pattern"),
    }
    keywords = keywords_by_skill.get(skill_id, ())
    for need in needs:
        tool_name = str(getattr(need, "tool_name", "") or "").lower()
        reason = str(getattr(need, "reason", "") or "").strip()
        haystack = f"{tool_name} {reason.lower()}"
        if any(keyword in haystack for keyword in keywords):
            return reason or str(getattr(need, "tool_name", "") or "")
    return ""


def public_execution_checklist(checklist: list[ChecklistItem] | list[dict[str, Any]], *, stage_trace: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    inferred_status = checklist_status_from_trace(stage_trace or [])
    result: list[dict[str, Any]] = []
    for item in checklist:
        data = normalize_for_json(asdict(item)) if isinstance(item, ChecklistItem) else normalize_for_json(item)
        if not isinstance(data, dict):
            continue
        if data.get("status") == "done":
            data["status"] = "completed"
        owner = str(data.get("owner") or "")
        status = str(data.get("status") or "")
        if status in {"", "pending", "running"}:
            inferred = inferred_checklist_status(owner, inferred_status)
            if inferred:
                data["status"] = inferred
        result.append(data)
    return result


def checklist_status_from_trace(stage_trace: list[dict[str, Any]]) -> dict[str, str]:
    result: dict[str, str] = {}
    for event in stage_trace:
        if not isinstance(event, dict):
            continue
        agent = str(event.get("agent") or "").strip()
        status = str(event.get("status") or "").strip().lower()
        if not agent or status not in {"completed", "failed", "warning", "started", "running", "retrying"}:
            continue
        result[normalize_owner(agent)] = "running" if status == "started" else status
    return result


def inferred_checklist_status(owner: str, trace_status: dict[str, str]) -> str:
    normalized = normalize_owner(owner)
    if not normalized:
        return ""
    if normalized in trace_status:
        return trace_status[normalized]
    if normalized == "writer":
        return trace_status.get("contentwriter", "")
    if normalized == "designer":
        return trace_status.get("styledesigner", "")
    if normalized == "coder":
        return trace_status.get("htmlcoder", "")
    return ""


def normalize_owner(value: str) -> str:
    return "".join(ch for ch in str(value or "").lower() if ch.isalnum())
