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
        return {
            "job_id": state.job_id,
            "run_id": state.run_id,
            "generation_engine": GenerationEngine.V2.value,
            "current_stage": state.current_step,
            "stage_trace": normalize_for_json([asdict(event) for event in state.stage_trace]),
            "skill_trace": normalize_for_json([asdict(event) for event in state.skill_trace]),
            "execution_checklist": public_execution_checklist(state.execution_checklist),
        }


def public_execution_checklist(checklist: list[ChecklistItem] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for item in checklist:
        data = normalize_for_json(asdict(item)) if isinstance(item, ChecklistItem) else normalize_for_json(item)
        if not isinstance(data, dict):
            continue
        if data.get("status") == "done":
            data["status"] = "completed"
        result.append(data)
    return result
