from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any

from html_lore.server.ai.material_generation import MaterialGenerationError
from html_lore.server.ai.providers import AIProviderConfigError, ProviderCallError
from html_lore.server.ai.html_generation import GenerationSpec
from html_lore.server.config import ServerSettings

from .graph import HtmlGenerationV2Graph
from .graph import StateCallback
from .model_client import GenerationJsonModelClient
from .schemas import GenerationInput, GenerationState, normalize_for_json
from .store import public_execution_checklist
from .write_gateway import WriteGateway


def generate_note_from_material_v2(
    *,
    settings: ServerSettings,
    filename: str,
    content: bytes,
    instruction: str,
    spec: GenerationSpec,
    reference_content: bytes = b"",
    model_client: GenerationJsonModelClient | None = None,
    job_id: str = "",
    on_state: StateCallback | None = None,
) -> dict[str, Any]:
    started_at = datetime.now(timezone.utc)
    graph = HtmlGenerationV2Graph(model_client=model_client, parser_mode=settings.document_parser, on_state=on_state)
    generation_input = GenerationInput(
        instruction=instruction,
        filename=filename,
        content=content,
        content_type="",
        theme=spec.theme,
        target_use=spec.target_use,
        style_preference=spec.style_preference,
        audience=spec.audience,
        reference_style=spec.reference_style,
        reference_file_name=spec.reference_file_name,
        reference_content=reference_content,
        reference_file_type=spec.reference_file_type,
        reference_file_size=spec.reference_file_size,
        target_collection="inbox",
        source_type="ai_generated",
    )
    state = graph.initial_state(generation_input, job_id=job_id)
    try:
        state = graph.run(state)
    except (AIProviderConfigError, ProviderCallError) as exc:
        completed_at = datetime.now(timezone.utc)
        run = public_material_v2_run(state, started_at=started_at, completed_at=completed_at, status="failed", error_code="provider_failed", error_message=str(exc))
        raise MaterialGenerationError(str(exc), run=run) from exc
    except Exception as exc:
        completed_at = datetime.now(timezone.utc)
        run = public_material_v2_run(state, started_at=started_at, completed_at=completed_at, status="failed", error_code="generation_v2_failed", error_message=str(exc))
        raise MaterialGenerationError(str(exc), run=run) from exc
    if state.failed_steps or state.create_note_proposal is None:
        completed_at = datetime.now(timezone.utc)
        message = ", ".join(state.failed_steps) or "Generation v2 did not produce a note proposal."
        run = public_material_v2_run(state, started_at=started_at, completed_at=completed_at, status="failed", error_code="generation_v2_failed", error_message=message)
        raise MaterialGenerationError(message, run=run)
    try:
        write_result = WriteGateway(settings).write(state.create_note_proposal)
    except Exception as exc:
        completed_at = datetime.now(timezone.utc)
        run = public_material_v2_run(state, started_at=started_at, completed_at=completed_at, status="failed", error_code="write_gateway_failed", error_message=str(exc))
        raise MaterialGenerationError(str(exc), run=run) from exc
    completed_at = datetime.now(timezone.utc)
    run = public_material_v2_run(state, started_at=started_at, completed_at=completed_at, status="completed", item_id=write_result.item_id)
    return {"run": run, "item": {"id": write_result.item_id, "title": write_result.title}}


def public_material_v2_run(
    state: GenerationState,
    *,
    started_at: datetime,
    completed_at: datetime,
    status: str,
    item_id: str = "",
    error_code: str = "",
    error_message: str = "",
) -> dict[str, Any]:
    return {
        "id": state.run_id,
        "kind": "material_html_generation",
        "status": status,
        "started_at": started_at.isoformat(),
        "completed_at": completed_at.isoformat(),
        "duration_ms": int((completed_at - started_at).total_seconds() * 1000),
        "conversation_id": "",
        "spec": public_generation_input(state),
        "graph": HtmlGenerationV2Graph.name,
        "generation_engine": "v2",
        "current_stage": state.current_step,
        "stage_trace": normalize_for_json([asdict(event) for event in state.stage_trace]),
        "execution_checklist": public_execution_checklist(state.execution_checklist),
        "skill_trace": normalize_for_json([asdict(item) for item in state.skill_trace]),
        "agent_artifacts": normalize_for_json([asdict(item) for item in state.agent_artifacts]),
        "material": {"filename": state.input.filename, "reference_file_name": state.input.reference_file_name},
        "item_id": item_id,
        "error": {"code": error_code or "generation_v2_failed", "message": error_message or ", ".join(state.failed_steps)} if status == "failed" else {},
        "retryable": status == "failed",
        "cancellable": False,
    }


def public_generation_input(state: GenerationState) -> dict[str, Any]:
    data = normalize_for_json(asdict(state.input))
    data.pop("content", None)
    data.pop("reference_content", None)
    return data
