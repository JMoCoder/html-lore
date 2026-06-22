from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

from .schemas import GenerationStage, GenerationState, StageTraceEvent


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def start_stage(state: GenerationState, stage: GenerationStage, *, agent: str, message: str = "") -> GenerationState:
    event = StageTraceEvent(stage=stage, agent=agent, status="started", started_at=utc_now(), message=message)
    return replace(state, current_step=stage.value, stage_trace=[*state.stage_trace, event])


def complete_stage(state: GenerationState, stage: GenerationStage, *, message: str = "") -> GenerationState:
    trace = list(state.stage_trace)
    for index in range(len(trace) - 1, -1, -1):
        event = trace[index]
        if event.stage == stage and event.status == "started":
            trace[index] = replace(event, status="completed", completed_at=utc_now(), message=message or event.message)
            break
    return replace(state, stage_trace=trace, completed_steps=[*state.completed_steps, stage.value])


def fail_stage(state: GenerationState, stage: GenerationStage, *, message: str, retryable: bool = True) -> GenerationState:
    trace = list(state.stage_trace)
    for index in range(len(trace) - 1, -1, -1):
        event = trace[index]
        if event.stage == stage and event.status == "started":
            trace[index] = replace(event, status="failed", completed_at=utc_now(), error_summary=message, retryable=retryable)
            break
    return replace(state, current_step=stage.value, stage_trace=trace, failed_steps=[*state.failed_steps, stage.value])
