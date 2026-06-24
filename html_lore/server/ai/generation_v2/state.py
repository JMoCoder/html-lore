from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from typing import Any

from .schemas import GenerationStage, GenerationState, StageTraceEvent


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def elapsed_ms(started_at: str, completed_at: str) -> int:
    try:
        start = datetime.fromisoformat(str(started_at or ""))
        end = datetime.fromisoformat(str(completed_at or ""))
    except ValueError:
        return 0
    return max(0, int((end - start).total_seconds() * 1000))


def start_stage(state: GenerationState, stage: GenerationStage, *, agent: str, message: str = "") -> GenerationState:
    event = StageTraceEvent(stage=stage, agent=agent, status="started", started_at=utc_now(), message=message)
    return replace(state, current_step=stage.value, stage_trace=[*state.stage_trace, event])


def complete_stage(state: GenerationState, stage: GenerationStage, *, message: str = "", metadata: dict[str, Any] | None = None) -> GenerationState:
    trace = list(state.stage_trace)
    for index in range(len(trace) - 1, -1, -1):
        event = trace[index]
        if event.stage == stage and event.status == "started":
            completed_at = utc_now()
            trace[index] = replace(
                event,
                status="completed",
                completed_at=completed_at,
                duration_ms=elapsed_ms(event.started_at, completed_at),
                message=message or event.message,
                metadata=metadata or event.metadata,
            )
            break
    return replace(state, stage_trace=trace, completed_steps=[*state.completed_steps, stage.value])


def fail_stage(state: GenerationState, stage: GenerationStage, *, message: str, retryable: bool = True, metadata: dict[str, Any] | None = None) -> GenerationState:
    trace = list(state.stage_trace)
    for index in range(len(trace) - 1, -1, -1):
        event = trace[index]
        if event.stage == stage and event.status == "started":
            completed_at = utc_now()
            trace[index] = replace(
                event,
                status="failed",
                completed_at=completed_at,
                duration_ms=elapsed_ms(event.started_at, completed_at),
                error_summary=message,
                retryable=retryable,
                metadata=metadata or event.metadata,
            )
            break
    return replace(state, current_step=stage.value, stage_trace=trace, failed_steps=[*state.failed_steps, stage.value])


def retry_stage(state: GenerationState, stage: GenerationStage, *, message: str, metadata: dict[str, Any] | None = None) -> GenerationState:
    trace = list(state.stage_trace)
    for index in range(len(trace) - 1, -1, -1):
        event = trace[index]
        if event.stage == stage and event.status == "started":
            completed_at = utc_now()
            trace[index] = replace(
                event,
                status="retrying",
                completed_at=completed_at,
                duration_ms=elapsed_ms(event.started_at, completed_at),
                error_summary=message,
                retryable=True,
                metadata=metadata or event.metadata,
            )
            break
    return replace(state, stage_trace=trace)
