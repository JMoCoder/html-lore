from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any
from typing import Callable

from html_lore.server.ai.material_generation import MaterialGenerationError
from html_lore.server.ai.providers import AIProviderConfigError, ProviderCallError
from html_lore.server.ai.html_generation import GenerationSpec
from html_lore.server.config import ServerSettings

from .checkpoint import generation_v2_retry_metadata, prepare_state_for_manual_retry, write_state_checkpoint
from .graph import HtmlGenerationV2Graph
from .graph import StateCallback
from .material_bundle import MaterialBundleReference, build_material_bundle, cleanup_expired_failed_job_workspaces, write_job_material_bundle, write_job_workspace_json, write_job_workspace_jsonl, write_job_workspace_text
from .model_client import GenerationJsonModelClient
from .schemas import GenerationInput, GenerationState, normalize_for_json
from .store import public_execution_checklist, public_skill_trace
from .write_gateway import WriteGateway


def generate_note_from_material_v2(
    *,
    settings: ServerSettings,
    filename: str,
    content: bytes,
    materials: list[dict[str, Any]] | None = None,
    instruction: str,
    spec: GenerationSpec,
    reference_content: bytes = b"",
    model_client: GenerationJsonModelClient | None = None,
    job_id: str = "",
    on_state: StateCallback | None = None,
    on_material_bundle_ready: Callable[[MaterialBundleReference], None] | None = None,
    on_checkpoint_ready: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    started_at = datetime.now(timezone.utc)
    def workspace_writer(state: GenerationState, relative_path: str, value: Any, mode: str) -> None:
        if not state.job_id:
            return
        if mode == "jsonl":
            write_job_workspace_jsonl(settings, state.job_id, relative_path, value if isinstance(value, list) else [value])
        elif mode == "json":
            write_job_workspace_json(settings, state.job_id, relative_path, value)
        elif mode == "text":
            write_job_workspace_text(settings, state.job_id, relative_path, str(value or ""))

    graph = HtmlGenerationV2Graph(
        model_client=model_client,
        parser_mode=settings.document_parser,
        on_state=on_state,
        workspace_writer=workspace_writer,
        visual_check_mode=settings.ai_visual_check,
        visual_check_browser_channel=settings.ai_visual_check_browser_channel,
        visual_check_timeout_seconds=settings.ai_visual_check_timeout_seconds,
    )
    generation_input = GenerationInput(
        instruction=instruction,
        filename=filename,
        content=content,
        content_type="",
        materials=normalize_materials_for_generation(materials, filename=filename, content=content),
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
    material_bundle_reference: MaterialBundleReference | None = None

    def sync_state(next_state: GenerationState) -> None:
        nonlocal material_bundle_reference
        if on_state is not None:
            on_state(next_state)
        checkpoint_path = write_state_checkpoint(settings, next_state, job_id=job_id) if job_id else ""
        if checkpoint_path and on_checkpoint_ready is not None:
            on_checkpoint_ready(checkpoint_path)
        if material_bundle_reference is not None or next_state.parsed_document is None or not job_id:
            return
        bundle = build_material_bundle(next_state.parsed_document, run_id=next_state.run_id)
        if bundle is None:
            return
        material_bundle_reference = write_job_material_bundle(settings, bundle, job_id=job_id)
        if on_material_bundle_ready is not None:
            on_material_bundle_ready(material_bundle_reference)

    try:
        graph.on_state = sync_state
        state = graph.run(state)
    except AIProviderConfigError as exc:
        cleanup_expired_failed_job_workspaces(settings, keep_days=7)
        completed_at = datetime.now(timezone.utc)
        run = public_material_v2_run(state, started_at=started_at, completed_at=completed_at, status="failed", error_code="provider_config_failed", error_message=str(exc))
        raise MaterialGenerationError(str(exc), run=run) from exc
    except ProviderCallError as exc:
        cleanup_expired_failed_job_workspaces(settings, keep_days=7)
        completed_at = datetime.now(timezone.utc)
        run = public_material_v2_run(state, started_at=started_at, completed_at=completed_at, status="failed", error_code="provider_failed", error_message=str(exc))
        raise MaterialGenerationError(str(exc), run=run) from exc
    except Exception as exc:
        cleanup_expired_failed_job_workspaces(settings, keep_days=7)
        completed_at = datetime.now(timezone.utc)
        run = public_material_v2_run(state, started_at=started_at, completed_at=completed_at, status="failed", error_code="generation_v2_failed", error_message=str(exc))
        raise MaterialGenerationError(str(exc), run=run) from exc
    if state.failed_steps or state.create_note_proposal is None:
        cleanup_expired_failed_job_workspaces(settings, keep_days=7)
        completed_at = datetime.now(timezone.utc)
        message = ", ".join(state.failed_steps) or "Generation v2 did not produce a note proposal."
        run = public_material_v2_run(state, started_at=started_at, completed_at=completed_at, status="failed", error_code="generation_v2_failed", error_message=message)
        raise MaterialGenerationError(message, run=run)
    try:
        if material_bundle_reference is None:
            fallback_job_id = job_id or f"run_{state.run_id}"
            bundle = build_material_bundle(state.parsed_document, run_id=state.run_id)
            material_bundle_reference = write_job_material_bundle(settings, bundle, job_id=fallback_job_id) if bundle is not None else None
        write_result = WriteGateway(settings).write(state.create_note_proposal, workspace_reference=material_bundle_reference)
    except Exception as exc:
        cleanup_expired_failed_job_workspaces(settings, keep_days=7)
        completed_at = datetime.now(timezone.utc)
        run = public_material_v2_run(state, started_at=started_at, completed_at=completed_at, status="failed", error_code="write_gateway_failed", error_message=str(exc))
        raise MaterialGenerationError(str(exc), run=run) from exc
    completed_at = datetime.now(timezone.utc)
    run = public_material_v2_run(state, started_at=started_at, completed_at=completed_at, status="completed", item_id=write_result.item_id)
    return {"run": run, "item": {"id": write_result.item_id, "title": write_result.title}}


def resume_note_from_material_v2(
    *,
    settings: ServerSettings,
    state: GenerationState,
    model_client: GenerationJsonModelClient | None = None,
    on_state: StateCallback | None = None,
    on_checkpoint_ready: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    retry_state = prepare_state_for_manual_retry(state)
    return run_material_v2_state(
        settings=settings,
        state=retry_state,
        model_client=model_client,
        on_state=on_state,
        on_checkpoint_ready=on_checkpoint_ready,
    )


def run_material_v2_state(
    *,
    settings: ServerSettings,
    state: GenerationState,
    model_client: GenerationJsonModelClient | None = None,
    on_state: StateCallback | None = None,
    on_checkpoint_ready: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    started_at = datetime.now(timezone.utc)

    def workspace_writer(next_state: GenerationState, relative_path: str, value: Any, mode: str) -> None:
        if not next_state.job_id:
            return
        if mode == "jsonl":
            write_job_workspace_jsonl(settings, next_state.job_id, relative_path, value if isinstance(value, list) else [value])
        elif mode == "json":
            write_job_workspace_json(settings, next_state.job_id, relative_path, value)
        elif mode == "text":
            write_job_workspace_text(settings, next_state.job_id, relative_path, str(value or ""))

    graph = HtmlGenerationV2Graph(
        model_client=model_client,
        parser_mode=settings.document_parser,
        on_state=on_state,
        workspace_writer=workspace_writer,
        visual_check_mode=settings.ai_visual_check,
        visual_check_browser_channel=settings.ai_visual_check_browser_channel,
        visual_check_timeout_seconds=settings.ai_visual_check_timeout_seconds,
    )

    def sync_state(next_state: GenerationState) -> None:
        if on_state is not None:
            on_state(next_state)
        checkpoint_path = write_state_checkpoint(settings, next_state, job_id=next_state.job_id) if next_state.job_id else ""
        if checkpoint_path and on_checkpoint_ready is not None:
            on_checkpoint_ready(checkpoint_path)

    material_bundle_reference: MaterialBundleReference | None = None
    try:
        graph.on_state = sync_state
        state = graph.run(state)
    except AIProviderConfigError as exc:
        cleanup_expired_failed_job_workspaces(settings, keep_days=7)
        completed_at = datetime.now(timezone.utc)
        run = public_material_v2_run(state, started_at=started_at, completed_at=completed_at, status="failed", error_code="provider_config_failed", error_message=str(exc))
        raise MaterialGenerationError(str(exc), run=run) from exc
    except ProviderCallError as exc:
        cleanup_expired_failed_job_workspaces(settings, keep_days=7)
        completed_at = datetime.now(timezone.utc)
        run = public_material_v2_run(state, started_at=started_at, completed_at=completed_at, status="failed", error_code="provider_failed", error_message=str(exc))
        raise MaterialGenerationError(str(exc), run=run) from exc
    except Exception as exc:
        cleanup_expired_failed_job_workspaces(settings, keep_days=7)
        completed_at = datetime.now(timezone.utc)
        run = public_material_v2_run(state, started_at=started_at, completed_at=completed_at, status="failed", error_code="generation_v2_failed", error_message=str(exc))
        raise MaterialGenerationError(str(exc), run=run) from exc
    if state.failed_steps or state.create_note_proposal is None:
        cleanup_expired_failed_job_workspaces(settings, keep_days=7)
        completed_at = datetime.now(timezone.utc)
        message = ", ".join(state.failed_steps) or "Generation v2 did not produce a note proposal."
        run = public_material_v2_run(state, started_at=started_at, completed_at=completed_at, status="failed", error_code="generation_v2_failed", error_message=message)
        raise MaterialGenerationError(message, run=run)
    try:
        bundle = build_material_bundle(state.parsed_document, run_id=state.run_id)
        material_bundle_reference = write_job_material_bundle(settings, bundle, job_id=state.job_id) if bundle is not None and state.job_id else None
        write_result = WriteGateway(settings).write(state.create_note_proposal, workspace_reference=material_bundle_reference)
    except Exception as exc:
        cleanup_expired_failed_job_workspaces(settings, keep_days=7)
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
    data = {
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
        "execution_checklist": public_execution_checklist(
            state.execution_checklist,
            stage_trace=normalize_for_json([asdict(event) for event in state.stage_trace]),
        ),
        "skill_trace": public_skill_trace(state),
        "agent_artifacts": normalize_for_json([asdict(item) for item in state.agent_artifacts]),
        "material": {"filename": state.input.filename, "filenames": material_filenames(state), "reference_file_name": state.input.reference_file_name},
        "item_id": item_id,
        "error": {"code": error_code or "generation_v2_failed", "message": error_message or ", ".join(state.failed_steps)} if status == "failed" else {},
        "cancellable": False,
    }
    data.update(generation_v2_retry_metadata(data, state))
    return data


def public_generation_input(state: GenerationState) -> dict[str, Any]:
    data = normalize_for_json(asdict(state.input))
    data.pop("content", None)
    data.pop("reference_content", None)
    data["materials"] = [
        {
            "filename": str(item.get("filename") or ""),
            "content_type": str(item.get("content_type") or ""),
            "size": len(item.get("content")) if isinstance(item.get("content"), bytes) else int(item.get("size") or 0),
        }
        for item in state.input.materials
        if isinstance(item, dict)
    ]
    return data


def normalize_materials_for_generation(materials: list[dict[str, Any]] | None, *, filename: str, content: bytes) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for index, raw in enumerate(materials or []):
        if not isinstance(raw, dict):
            continue
        raw_content = raw.get("content")
        if not isinstance(raw_content, bytes):
            continue
        result.append(
            {
                "filename": str(raw.get("filename") or f"material-{index + 1}.txt"),
                "content": raw_content,
                "content_type": str(raw.get("content_type") or ""),
            },
        )
    if result:
        return result
    return [{"filename": filename or "material.txt", "content": content, "content_type": ""}]


def material_filenames(state: GenerationState) -> list[str]:
    names = [str(item.get("filename") or "") for item in state.input.materials if isinstance(item, dict) and str(item.get("filename") or "")]
    return names or ([state.input.filename] if state.input.filename else [])
