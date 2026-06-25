from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from html_lore.server.config import ServerSettings


class AIRunError(ValueError):
    pass


class AIRunStore:
    def __init__(self, settings: ServerSettings) -> None:
        self.settings = settings
        self.path = runs_path(settings)

    def add(self, run: dict[str, Any]) -> dict[str, Any]:
        if self.path is None:
            raise AIRunError("Metadata directory is not configured.")
        data = self._read()
        public = sanitize_run(run)
        data.setdefault("runs", []).append(public)
        self._write(data)
        return public

    def list(self, limit: int = 20) -> list[dict[str, Any]]:
        safe_limit = max(1, min(int(limit or 20), 100))
        runs = [sanitize_run(run) for run in self._read().get("runs", []) if isinstance(run, dict)]
        return list(reversed(runs))[:safe_limit]

    def get(self, run_id: str) -> dict[str, Any]:
        for run in self._read().get("runs", []):
            if run.get("id") == run_id:
                return sanitize_run(run) if isinstance(run, dict) else {}
        raise AIRunError("AI run not found.")

    def _read(self) -> dict[str, Any]:
        if self.path is None or not self.path.exists():
            return {"version": 1, "runs": []}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise AIRunError("AI run store is not valid JSON.") from exc
        if not isinstance(data, dict):
            raise AIRunError("AI run store must be a JSON object.")
        runs = data.get("runs", [])
        if not isinstance(runs, list):
            raise AIRunError("AI run store runs must be a list.")
        return {"version": int(data.get("version") or 1), "runs": runs}

    def _write(self, data: dict[str, Any]) -> None:
        if self.path is None:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def runs_path(settings: ServerSettings) -> Path | None:
    if settings.meta_dir is None:
        return None
    return settings.meta_dir / "ai" / "runs.json"


def sanitize_run(run: dict[str, Any]) -> dict[str, Any]:
    status = str(run.get("status") or "")
    kind = str(run.get("kind") or "")
    started_at = str(run.get("started_at") or "")
    completed_at = str(run.get("completed_at") or "")
    return {
        "id": str(run.get("id") or ""),
        "kind": kind,
        "operation": run_operation(kind),
        "status": status,
        "started_at": started_at,
        "completed_at": completed_at,
        "duration_ms": sanitize_duration(run.get("duration_ms")) or duration_between(started_at, completed_at),
        "conversation_id": str(run.get("conversation_id") or ""),
        "spec": run.get("spec") if isinstance(run.get("spec"), dict) else {},
        "graph": str(run.get("graph") or ""),
        "generation_intent": run.get("generation_intent") if isinstance(run.get("generation_intent"), dict) else {},
        "qa_report": run.get("qa_report") if isinstance(run.get("qa_report"), dict) else {},
        "review_decision": run.get("review_decision") if isinstance(run.get("review_decision"), dict) else {},
        "node_trace": run.get("node_trace") if isinstance(run.get("node_trace"), list) else [],
        "generation_engine": str(run.get("generation_engine") or "")[:40],
        "current_stage": str(run.get("current_stage") or "")[:80],
        "stage_trace": sanitize_generation_stage_trace(run.get("stage_trace")),
        "execution_checklist": sanitize_execution_checklist(run.get("execution_checklist")),
        "agent_trace": sanitize_trace_list(run.get("agent_trace"), allowed_keys={"id", "version", "role", "prompt_template", "input_schema", "output_schema"}),
        "prompt_trace": sanitize_trace_list(run.get("prompt_trace"), allowed_keys={"id", "version", "path"}),
        "skill_trace": sanitize_skill_trace(run.get("skill_trace")),
        "agent_artifacts": sanitize_agent_artifacts(run.get("agent_artifacts")),
        "usage": sanitize_usage(run.get("usage")),
        "budget": sanitize_budget(run.get("budget")),
        "error": sanitize_error(run.get("error")),
        "material": run.get("material") if isinstance(run.get("material"), dict) else {},
        "item_id": str(run.get("item_id") or ""),
        "retryable": sanitize_bool(run.get("retryable"), default=status == "failed" and kind in {"html_generation", "material_html_generation", "knowledge_qa"}),
        "cancellable": sanitize_bool(run.get("cancellable"), default=status in {"pending", "running"} and False),
    }


def run_operation(kind: str) -> str:
    if kind == "material_html_generation":
        return "material_to_html"
    if kind == "html_generation":
        return "conversation_to_html"
    if kind == "knowledge_qa":
        return "knowledge_qa"
    return "unknown"


def sanitize_bool(value: Any, *, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    return default


def sanitize_trace_list(value: Any, *, allowed_keys: set[str]) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    sanitized: list[dict[str, Any]] = []
    for entry in value:
        if not isinstance(entry, dict):
            continue
        clean = {key: entry[key] for key in allowed_keys if key in entry and isinstance(entry[key], (str, int, float, bool))}
        if clean:
            sanitized.append(clean)
    return sanitized


def sanitize_skill_trace(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    sanitized: list[dict[str, Any]] = []
    for entry in value:
        if not isinstance(entry, dict):
            continue
        if entry.get("id") or entry.get("agent"):
            clean_v2 = {
                "id": str(entry.get("id") or "")[:120],
                "title": str(entry.get("title") or "")[:160],
                "agent": str(entry.get("agent") or "")[:120],
                "version": str(entry.get("version") or "")[:40],
                "source": str(entry.get("source") or "")[:40],
            }
            if clean_v2["id"]:
                sanitized.append(clean_v2)
            continue
        clean = {
            "skill_id": str(entry.get("skill_id") or ""),
            "version": str(entry.get("version") or ""),
            "status": str(entry.get("status") or ""),
            "input_summary": sanitize_summary(entry.get("input_summary")),
            "output_summary": sanitize_summary(entry.get("output_summary")),
        }
        if clean["skill_id"]:
            sanitized.append(clean)
    return sanitized


def sanitize_agent_artifacts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    result: list[dict[str, Any]] = []
    for raw in value[-40:]:
        if not isinstance(raw, dict):
            continue
        agent = str(raw.get("agent") or "")[:120]
        title = str(raw.get("title") or "")[:160]
        if not agent and not title:
            continue
        result.append(
            {
                "agent": agent,
                "stage": str(raw.get("stage") or "")[:80],
                "title": title,
                "summary": str(raw.get("summary") or "")[:360],
                "data": sanitize_artifact_data(raw.get("data")),
            }
        )
    return result


def sanitize_artifact_data(value: Any, *, depth: int = 0) -> Any:
    if depth > 3:
        return ""
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, raw in list(value.items())[:40]:
            clean_key = str(key)[:80]
            if clean_key.lower() in {"html", "content", "reference_content", "prompt", "raw", "raw_output"}:
                continue
            result[clean_key] = sanitize_artifact_data(raw, depth=depth + 1)
        return result
    if isinstance(value, list):
        return [sanitize_artifact_data(item, depth=depth + 1) for item in value[:20]]
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value
    if value is None:
        return ""
    return str(value)[:360]


def sanitize_summary(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    result: dict[str, Any] = {}
    for key, raw in value.items():
        if not isinstance(key, str) or key not in {"query_chars", "context_item_count", "requested_mode", "evidence_count", "effective_mode", "fallback"}:
            continue
        if isinstance(raw, bool):
            result[key] = raw
        elif isinstance(raw, (int, float)):
            result[key] = int(raw)
        elif isinstance(raw, str):
            result[key] = raw[:80]
    return result


def sanitize_duration(value: Any) -> int:
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError):
        return 0


def duration_between(started_at: str, completed_at: str) -> int:
    try:
        start = datetime.fromisoformat(str(started_at or ""))
        end = datetime.fromisoformat(str(completed_at or ""))
    except ValueError:
        return 0
    return max(0, int((end - start).total_seconds() * 1000))


def sanitize_usage(value: Any) -> dict[str, int]:
    if not isinstance(value, dict):
        return {}
    result: dict[str, int] = {}
    key_map = {
        "input_tokens": ("input_tokens", "prompt_tokens"),
        "output_tokens": ("output_tokens", "completion_tokens"),
        "total_tokens": ("total_tokens",),
    }
    for key, aliases in key_map.items():
        raw = 0
        for alias in aliases:
            if value.get(alias) not in (None, ""):
                raw = value.get(alias)
                break
        try:
            number = int(raw or 0)
        except (TypeError, ValueError):
            number = 0
        if number > 0:
            result[key] = number
    return result


def sanitize_budget(value: Any) -> dict[str, int]:
    if not isinstance(value, dict):
        return {}
    result: dict[str, int] = {}
    for key in ("message_chars", "max_message_chars", "prompt_chars", "max_prompt_chars", "max_response_tokens"):
        try:
            number = int(value.get(key) or 0)
        except (TypeError, ValueError):
            number = 0
        if number > 0:
            result[key] = number
    return result


def sanitize_error(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    code = str(value.get("code") or "").strip()[:80]
    message = str(value.get("message") or "").strip()[:240]
    result: dict[str, str] = {}
    if code:
        result["code"] = code
    if message:
        result["message"] = message
    return result


def sanitize_generation_stage_trace(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    sanitized: list[dict[str, Any]] = []
    for entry in value[-120:]:
        if not isinstance(entry, dict):
            continue
        stage = str(entry.get("stage") or "")[:80]
        status = str(entry.get("status") or "")[:40]
        if not stage or not status:
            continue
        sanitized.append(
            {
                "stage": stage,
                "agent": str(entry.get("agent") or "")[:120],
                "status": status,
                "started_at": str(entry.get("started_at") or "")[:80],
                "completed_at": str(entry.get("completed_at") or "")[:80],
                "duration_ms": sanitize_duration(entry.get("duration_ms")),
                "message": str(entry.get("message") or "")[:240],
                "error_summary": str(entry.get("error_summary") or "")[:240],
                "retryable": bool(entry.get("retryable")),
                "metadata": sanitize_stage_metadata(entry.get("metadata")),
            },
        )
    return sanitized


def sanitize_stage_metadata(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    result: dict[str, Any] = {}
    for key in ("output_kind", "output_chars", "section_count", "score", "risk_level", "retry_count", "error_type"):
        raw = value.get(key)
        if isinstance(raw, bool):
            result[key] = raw
        elif isinstance(raw, (int, float)):
            result[key] = raw
        elif isinstance(raw, str):
            result[key] = raw[:80]
    return result


def sanitize_execution_checklist(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []
    sanitized: list[dict[str, str]] = []
    for entry in value[:120]:
        if not isinstance(entry, dict):
            continue
        item_id = str(entry.get("id") or "")[:80]
        title = str(entry.get("title") or "")[:160]
        if not item_id and not title:
            continue
        sanitized.append(
            {
                "id": item_id,
                "title": title,
                "owner": str(entry.get("owner") or "")[:80],
                "status": str(entry.get("status") or "")[:40],
            },
        )
    return sanitized
