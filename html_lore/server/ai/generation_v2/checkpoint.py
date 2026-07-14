from __future__ import annotations

import json
from dataclasses import asdict, fields, is_dataclass, replace
from enum import Enum
from pathlib import Path
from types import UnionType
from typing import Any, Union, get_args, get_origin, get_type_hints
from uuid import uuid4

from html_lore.server.config import ServerSettings

from .material_bundle import ensure_within, internal_meta_relative_path, job_workspace_dir, job_workspace_root
from .schemas import GenerationState, SpreadsheetWorkbook, StageTraceEvent, normalize_for_json


MANUAL_CHECKPOINT_RETRY_LIMIT = 2
TECHNICAL_RETRY_ERROR_TYPES = {"ProviderCallError", "AgentOutputSchemaError"}
TECHNICAL_RETRY_ERROR_CODES = {"provider_failed"}


def write_state_checkpoint(settings: ServerSettings, state: GenerationState, *, job_id: str) -> str:
    if settings.meta_dir is None or not job_id:
        return ""
    workspace = job_workspace_dir(settings, job_id)
    ensure_within(workspace, job_workspace_root(settings))
    persist_checkpoint_workbooks(workspace, state)
    checkpoint_path = workspace / "checkpoints" / "latest.json"
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_path.write_text(
        json.dumps(checkpoint_state_payload(state, omit_workbooks=True), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return internal_meta_relative_path(settings, checkpoint_path)


def read_state_checkpoint(settings: ServerSettings, checkpoint_path: str) -> GenerationState:
    if settings.meta_dir is None:
        raise ValueError("Metadata directory is not configured.")
    path = settings.meta_dir / checkpoint_path
    ensure_within(path, settings.meta_dir)
    if not path.is_file():
        raise ValueError("Generation checkpoint is missing.")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError("Generation checkpoint is not valid JSON.") from exc
    if not isinstance(data, dict):
        raise ValueError("Generation checkpoint must be a JSON object.")
    state = dataclass_from_dict(GenerationState, data)
    return restore_checkpoint_workbooks(path.parent.parent, state)


def checkpoint_state_payload(state: GenerationState, *, omit_workbooks: bool = False) -> dict[str, Any]:
    payload = state.as_dict()
    input_data = payload.get("input") if isinstance(payload.get("input"), dict) else {}
    input_data["content"] = ""
    input_data["reference_content"] = ""
    materials = []
    for item in input_data.get("materials") if isinstance(input_data.get("materials"), list) else []:
        if not isinstance(item, dict):
            continue
        materials.append(
            {
                "filename": str(item.get("filename") or ""),
                "content_type": str(item.get("content_type") or ""),
                "size": len(item.get("content")) if isinstance(item.get("content"), (bytes, bytearray)) else int(item.get("size") or 0),
            }
        )
    input_data["materials"] = materials
    payload["input"] = input_data
    if omit_workbooks:
        parsed = payload.get("parsed_document") if isinstance(payload.get("parsed_document"), dict) else None
        if parsed is not None:
            parsed["workbooks"] = []
    return normalize_for_json(payload)


def persist_checkpoint_workbooks(workspace: Path, state: GenerationState) -> None:
    parsed = state.parsed_document
    if parsed is None or not parsed.workbooks:
        return
    target = workspace / "materials" / "workbooks.json"
    ensure_within(target, workspace)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_file():
        return
    target.write_text(json.dumps(normalize_for_json([asdict(item) for item in parsed.workbooks]), ensure_ascii=False, indent=2), encoding="utf-8")


def restore_checkpoint_workbooks(workspace: Path, state: GenerationState) -> GenerationState:
    if state.parsed_document is None or state.parsed_document.workbooks:
        return state
    source = workspace / "materials" / "workbooks.json"
    ensure_within(source, workspace)
    if not source.is_file():
        return state
    try:
        decoded = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return state
    if not isinstance(decoded, list):
        return state
    workbooks = [dataclass_from_dict(SpreadsheetWorkbook, item) for item in decoded if isinstance(item, dict)]
    return replace(state, parsed_document=replace(state.parsed_document, workbooks=workbooks))


def prepare_state_for_manual_retry(state: GenerationState) -> GenerationState:
    failed_agent = last_failed_agent(state.stage_trace)
    retries = dict(state.same_node_retries)
    if failed_agent:
        retries[failed_agent] = 0
    return replace(state, run_id=uuid4().hex, failed_steps=[], same_node_retries=retries)


def generation_v2_retry_metadata(run: dict[str, Any], state: GenerationState) -> dict[str, Any]:
    if str(run.get("status") or "") != "failed":
        return retry_metadata(
            retryable=False,
            layer="",
            code="",
            reason="",
            limit=0,
        )
    code = str((run.get("error") if isinstance(run.get("error"), dict) else {}).get("code") or "")
    if code in TECHNICAL_RETRY_ERROR_CODES:
        return retry_metadata(
            retryable=True,
            layer="checkpoint_resume",
            code="provider_failed",
            reason="Provider or model call failed after node-level retries.",
        )
    if code == "provider_config_failed":
        return retry_metadata(
            retryable=False,
            layer="not_retryable",
            code="config_error",
            reason="AI provider configuration is invalid. Fix provider settings before creating a new task.",
        )
    if code == "write_gateway_failed":
        return retry_metadata(
            retryable=False,
            layer="not_retryable",
            code="write_failed",
            reason="Writing the generated note failed. Retry is disabled until write idempotency is confirmed.",
        )
    error_type = last_failed_error_type(state.stage_trace)
    if error_type in TECHNICAL_RETRY_ERROR_TYPES:
        return retry_metadata(
            retryable=True,
            layer="checkpoint_resume",
            code="schema_failed" if error_type == "AgentOutputSchemaError" else "provider_failed",
            reason=f"{error_type} failed after node-level retries.",
        )
    failed_steps = {str(step or "") for step in state.failed_steps}
    current_stage = str(state.current_step or "")
    if "parse_failed" in failed_steps or current_stage == "parse_failed":
        return retry_metadata(
            retryable=False,
            layer="not_retryable",
            code="parse_failed",
            reason="Uploaded material could not be parsed into usable content. Re-upload or change the source file.",
        )
    if "max_revision_rounds" in failed_steps:
        return retry_metadata(
            retryable=False,
            layer="not_retryable",
            code="revision_limit_reached",
            reason="Workflow revisions reached the configured limit. This needs workflow, prompt, or content-quality review.",
        )
    if "max_graph_steps" in failed_steps:
        return retry_metadata(
            retryable=False,
            layer="not_retryable",
            code="graph_step_limit_reached",
            reason="Workflow step limit was reached. This indicates a routing or convergence issue.",
        )
    if failed_steps.intersection({"verifier_blocked", "verifier_invalid_output"}):
        return retry_metadata(
            retryable=False,
            layer="not_retryable",
            code="workflow_blocked",
            reason="The workflow reached a blocked or unroutable decision. This needs system-level review, not manual retry.",
        )
    return retry_metadata(
        retryable=False,
        layer="not_retryable",
        code="unknown_failure",
        reason="The failure is not classified as a resumable technical interruption.",
    )


def retry_metadata(*, retryable: bool, layer: str, code: str, reason: str, limit: int = MANUAL_CHECKPOINT_RETRY_LIMIT) -> dict[str, Any]:
    return {
        "retryable": bool(retryable),
        "retry_layer": layer,
        "retry_mode": "resume_from_checkpoint" if layer == "checkpoint_resume" else "",
        "retry_reason_code": code,
        "retry_reason": reason,
        "retry_limit": int(limit or 0),
    }


def last_failed_error_type(stage_trace: list[StageTraceEvent]) -> str:
    for event in reversed(stage_trace):
        if str(event.status or "").lower() != "failed":
            continue
        metadata = event.metadata if isinstance(event.metadata, dict) else {}
        error_type = str(metadata.get("error_type") or "").strip()
        if error_type:
            return error_type
    return ""


def last_failed_agent(stage_trace: list[StageTraceEvent]) -> str:
    for event in reversed(stage_trace):
        if str(event.status or "").lower() == "failed" and event.agent:
            return event.agent
    return ""


def dataclass_from_dict(cls: type[Any], value: Any) -> Any:
    if not is_dataclass(cls):
        return value
    if not isinstance(value, dict):
        return cls()
    hints = get_type_hints(cls)
    kwargs: dict[str, Any] = {}
    for field in fields(cls):
        if field.name not in value:
            continue
        field_type = hints.get(field.name, field.type)
        kwargs[field.name] = typed_value_from_json(field_type, value[field.name])
    return cls(**kwargs)


def typed_value_from_json(expected_type: Any, value: Any) -> Any:
    if expected_type is Any:
        return value
    origin = get_origin(expected_type)
    args = get_args(expected_type)
    if origin in {list, tuple}:
        item_type = args[0] if args else Any
        if not isinstance(value, list):
            return []
        return [typed_value_from_json(item_type, item) for item in value]
    if origin is dict:
        value_type = args[1] if len(args) > 1 else Any
        if not isinstance(value, dict):
            return {}
        return {str(key): typed_value_from_json(value_type, item) for key, item in value.items()}
    if origin in {UnionType, Union}:
        non_none = [arg for arg in args if arg is not type(None)]
        if value is None:
            return None
        for option in non_none:
            try:
                return typed_value_from_json(option, value)
            except Exception:
                continue
        return value
    if isinstance(expected_type, type):
        if is_dataclass(expected_type):
            return dataclass_from_dict(expected_type, value)
        if issubclass_safe(expected_type, Enum):
            try:
                return expected_type(value)
            except ValueError:
                return expected_type(next(iter(expected_type)).value)
        if expected_type is bytes:
            return b""
        if expected_type in {str, int, float, bool}:
            try:
                return expected_type(value)
            except (TypeError, ValueError):
                return expected_type()
    return value


def issubclass_safe(value: type[Any], parent: type[Any]) -> bool:
    try:
        return issubclass(value, parent)
    except TypeError:
        return False
