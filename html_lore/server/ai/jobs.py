from __future__ import annotations

import json
import threading
import uuid
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from html_lore.server.config import ServerSettings


AIJobTask = Callable[[], dict[str, Any]]
AI_JOB_STATUSES = {"pending", "running", "completed", "failed", "cancelled", "canceled", "canceling"}
AI_GENERATION_STAGES = {
    "queued",
    "parsing",
    "parse_failed",
    "analyzing_requirements",
    "planning",
    "writing_content",
    "executing_tools",
    "designing_style",
    "coding_html",
    "verifying",
    "safety_checking",
    "finalizing",
    "writing",
    "completed",
    "failed",
    "canceled",
}


class AIJobError(ValueError):
    pass


@dataclass(frozen=True)
class EnqueuedAIJob:
    settings: ServerSettings
    job_id: str
    task: AIJobTask


class AIJobStore:
    def __init__(self, settings: ServerSettings) -> None:
        self.settings = settings
        self.path = ai_jobs_path(settings)

    def create(self, *, kind: str, label: str = "", payload: dict[str, Any] | None = None) -> dict[str, Any]:
        now = utc_now()
        job = sanitize_ai_job(
            {
                "job_id": f"ai_job_{uuid.uuid4().hex}",
                "kind": kind,
                "status": "pending",
                "label": label,
                "created_at": now,
                "updated_at": now,
                "started_at": "",
                "completed_at": "",
                "message": "",
                "run_id": "",
                "item_id": "",
                "error": {},
                "cancel_requested": False,
                "payload": payload if isinstance(payload, dict) else {},
                "attempts": 0,
            },
            include_private=True,
        )
        data = self._read()
        data.setdefault("jobs", []).append(job)
        self._write(data)
        return sanitize_ai_job(job)

    def list(self, limit: int = 20) -> list[dict[str, Any]]:
        safe_limit = max(1, min(int(limit or 20), 100))
        jobs = [sanitize_ai_job(job) for job in self._read().get("jobs", []) if isinstance(job, dict)]
        return sorted(jobs, key=lambda job: str(job.get("created_at") or ""), reverse=True)[:safe_limit]

    def get(self, job_id: str, *, include_private: bool = False) -> dict[str, Any]:
        for job in self._read().get("jobs", []):
            if job.get("job_id") == job_id:
                return sanitize_ai_job(job, include_private=include_private)
        raise AIJobError("AI job not found.")

    def update(self, job_id: str, values: dict[str, Any]) -> dict[str, Any]:
        data = self._read()
        now = utc_now()
        for job in data.get("jobs", []):
            if job.get("job_id") != job_id:
                continue
            job.update(values)
            job["updated_at"] = now
            data["jobs"] = [sanitize_ai_job(item, include_private=True) for item in data.get("jobs", []) if isinstance(item, dict)]
            self._write(data)
            return self.get(job_id)
        raise AIJobError("AI job not found.")

    def cancel(self, job_id: str) -> dict[str, Any]:
        job = self.get(job_id)
        status = str(job.get("status") or "")
        if status == "pending":
            return self.update(job_id, {"status": "cancelled", "cancel_requested": True, "completed_at": utc_now(), "message": "AI job cancelled before it started."})
        if status == "running":
            return self.update(job_id, {"cancel_requested": True, "message": "Cancellation requested. The current provider call may finish first."})
        if status in {"completed", "failed", "cancelled"}:
            return job
        raise AIJobError("AI job cannot be cancelled.")

    def _read(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"version": 1, "jobs": []}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise AIJobError("AI job store is not valid JSON.") from exc
        if not isinstance(data, dict):
            raise AIJobError("AI job store must be a JSON object.")
        jobs = data.get("jobs", [])
        if not isinstance(jobs, list):
            raise AIJobError("AI job store jobs must be a list.")
        return {"version": int(data.get("version") or 1), "jobs": jobs}

    def _write(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class AIJobQueue:
    def __init__(self) -> None:
        self._pending: deque[EnqueuedAIJob] = deque()
        self._condition = threading.Condition()
        self._worker: threading.Thread | None = None

    def enqueue(self, *, settings: ServerSettings, job: dict[str, Any], task: AIJobTask) -> None:
        with self._condition:
            self._pending.append(EnqueuedAIJob(settings=settings, job_id=str(job["job_id"]), task=task))
            if self._worker is None or not self._worker.is_alive():
                self._worker = threading.Thread(target=self._run, name="html-lore-ai-job-worker", daemon=True)
                self._worker.start()
            self._condition.notify()

    def _run(self) -> None:
        while True:
            with self._condition:
                while not self._pending:
                    self._condition.wait(timeout=10)
                    if not self._pending:
                        return
                entry = self._pending.popleft()
            self._execute(entry)

    def _execute(self, entry: EnqueuedAIJob) -> None:
        store = AIJobStore(entry.settings)
        try:
            job = store.get(entry.job_id)
        except AIJobError:
            return
        if job.get("cancel_requested") or job.get("status") == "cancelled":
            store.update(entry.job_id, {"status": "cancelled", "completed_at": utc_now(), "message": "AI job cancelled before it started."})
            return
        store.update(entry.job_id, {"status": "running", "started_at": utc_now(), "message": "AI job is running."})
        try:
            result = entry.task()
        except Exception as exc:  # pragma: no cover - defensive worker boundary
            store.update(
                entry.job_id,
                {
                    "status": "failed",
                    "completed_at": utc_now(),
                    "message": str(exc),
                    "error": {"code": exc.__class__.__name__, "message": str(exc)},
                },
            )
            return
        run = result.get("run") if isinstance(result.get("run"), dict) else {}
        item = result.get("item") if isinstance(result.get("item"), dict) else {}
        updates = {
            "status": "completed",
            "completed_at": utc_now(),
            "message": "AI job completed.",
            "run_id": str(run.get("id") or ""),
            "item_id": str(item.get("id") or ""),
        }
        updates.update(ai_job_updates_from_run(run))
        store.update(entry.job_id, updates)


ai_job_queue = AIJobQueue()


def ai_jobs_path(settings: ServerSettings) -> Path:
    if settings.meta_dir is None:
        return settings.public_dir / ".html-lore-ai-jobs.json"
    return settings.meta_dir / "ai" / "jobs.json"


def sanitize_ai_job(job: dict[str, Any], *, include_private: bool = False) -> dict[str, Any]:
    status = str(job.get("status") or "pending")
    if status not in AI_JOB_STATUSES:
        status = "pending"
    payload = job.get("payload") if isinstance(job.get("payload"), dict) else {}
    sanitized = {
        "job_id": str(job.get("job_id") or ""),
        "kind": str(job.get("kind") or ""),
        "status": status,
        "label": str(job.get("label") or "")[:160],
        "created_at": str(job.get("created_at") or ""),
        "updated_at": str(job.get("updated_at") or ""),
        "started_at": str(job.get("started_at") or ""),
        "completed_at": str(job.get("completed_at") or ""),
        "message": str(job.get("message") or "")[:240],
        "run_id": str(job.get("run_id") or ""),
        "item_id": str(job.get("item_id") or ""),
        "error": sanitize_error(job.get("error")),
        "cancel_requested": bool(job.get("cancel_requested")),
        "cancellable": status in {"pending", "running"},
        "retryable": status == "failed" and is_retryable_payload(payload),
        "attempts": sanitize_int(job.get("attempts")),
    }
    generation_engine = str(job.get("generation_engine") or "").strip()[:40]
    current_stage = sanitize_generation_stage(job.get("current_stage"))
    if generation_engine:
        sanitized["generation_engine"] = generation_engine
    if current_stage:
        sanitized["current_stage"] = current_stage
        sanitized["stage_label"] = current_stage
    stage_trace = sanitize_stage_trace(job.get("stage_trace"))
    if stage_trace:
        sanitized["stage_trace"] = stage_trace
    checklist = sanitize_execution_checklist(job.get("execution_checklist"), stage_trace=stage_trace)
    if checklist:
        sanitized["execution_checklist"] = checklist
    skill_trace = sanitize_skill_trace(job.get("skill_trace"))
    if skill_trace:
        sanitized["skill_trace"] = skill_trace
    agent_artifacts = sanitize_agent_artifacts(job.get("agent_artifacts"))
    if agent_artifacts:
        sanitized["agent_artifacts"] = agent_artifacts
    if include_private:
        sanitized["payload"] = sanitize_private_payload(payload)
    return sanitized


def ai_job_updates_from_run(run: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(run, dict):
        return {}
    updates: dict[str, Any] = {}
    for key in ("generation_engine", "current_stage", "stage_trace", "execution_checklist", "skill_trace", "agent_artifacts"):
        if key in run:
            updates[key] = run[key]
    return updates


def is_retryable_payload(payload: dict[str, Any]) -> bool:
    return str(payload.get("type") or "") == "conversation_html_generation" and bool(str(payload.get("conversation_id") or "").strip())


def sanitize_private_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    payload_type = str(payload.get("type") or "")
    if payload_type != "conversation_html_generation":
        return {}
    spec = payload.get("spec") if isinstance(payload.get("spec"), dict) else {}
    return {
        "type": payload_type,
        "conversation_id": str(payload.get("conversation_id") or "")[:120],
        "spec": {
            "theme": str(spec.get("theme") or "default")[:40],
            "target_use": str(spec.get("target_use") or "default")[:40],
            "reference_style": str(spec.get("reference_style") or "default")[:40],
            "reference_note_id": str(spec.get("reference_note_id") or "")[:240],
            "reference_file_name": str(spec.get("reference_file_name") or "")[:180],
            "reference_file_type": str(spec.get("reference_file_type") or "")[:120],
            "reference_file_size": str(spec.get("reference_file_size") or "0")[:40],
            "style_preference": str(spec.get("style_preference") or "default")[:40],
            "audience": str(spec.get("audience") or "default")[:40],
        },
    }


def sanitize_error(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    result: dict[str, str] = {}
    code = str(value.get("code") or "")[:80]
    message = str(value.get("message") or "")[:240]
    if code:
        result["code"] = code
    if message:
        result["message"] = message
    return result


def sanitize_int(value: Any) -> int:
    try:
        parsed = int(value or 0)
    except (TypeError, ValueError):
        return 0
    return max(0, parsed)


def sanitize_generation_stage(value: Any) -> str:
    stage = str(value or "").strip()
    return stage if stage in AI_GENERATION_STAGES else ""


def sanitize_stage_trace(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    result: list[dict[str, Any]] = []
    for raw in value[-80:]:
        if not isinstance(raw, dict):
            continue
        stage = sanitize_generation_stage(raw.get("stage"))
        status = str(raw.get("status") or "").strip()[:40]
        if not stage or not status:
            continue
        result.append(
            {
                "stage": stage,
                "agent": str(raw.get("agent") or "")[:120],
                "status": status,
                "started_at": str(raw.get("started_at") or "")[:80],
                "completed_at": str(raw.get("completed_at") or "")[:80],
                "duration_ms": sanitize_int(raw.get("duration_ms")),
                "message": str(raw.get("message") or "")[:240],
                "error_summary": str(raw.get("error_summary") or "")[:240],
                "retryable": bool(raw.get("retryable")),
                "metadata": sanitize_stage_metadata(raw.get("metadata")),
            },
        )
    return result


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
                "stage": sanitize_generation_stage(raw.get("stage")),
                "title": title,
                "summary": str(raw.get("summary") or "")[:360],
                "input_summary": str(raw.get("input_summary") or "")[:360],
                "output_summary": str(raw.get("output_summary") or "")[:360],
                "quality_score": sanitize_float(raw.get("quality_score")),
                "usage": sanitize_artifact_usage(raw.get("usage")),
                "warnings": sanitize_string_list(raw.get("warnings"), limit=8, item_limit=180),
                "data": sanitize_artifact_data(raw.get("data")),
            }
        )
    return result


def sanitize_float(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def sanitize_string_list(value: Any, *, limit: int = 8, item_limit: int = 180) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item or "")[:item_limit] for item in value[:limit] if str(item or "").strip()]


def sanitize_artifact_usage(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    result: dict[str, Any] = {}
    for key in ("input_tokens", "output_tokens", "total_tokens", "duration_ms", "retry_count", "revision_round", "output_chars", "section_count"):
        raw = value.get(key)
        if isinstance(raw, bool):
            continue
        if isinstance(raw, (int, float)):
            result[key] = raw
        elif isinstance(raw, str):
            result[key] = raw[:80]
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


def sanitize_execution_checklist(value: Any, *, stage_trace: list[dict[str, Any]] | None = None) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []
    inferred_status = checklist_status_from_trace(stage_trace or [])
    result: list[dict[str, str]] = []
    for raw in value[:80]:
        if not isinstance(raw, dict):
            continue
        item_id = str(raw.get("id") or "")[:80]
        title = str(raw.get("title") or "")[:160]
        if not item_id and not title:
            continue
        status = str(raw.get("status") or "pending")[:40]
        if status == "done":
            status = "completed"
        if status in {"", "pending", "running"}:
            status = inferred_checklist_status(str(raw.get("owner") or ""), inferred_status) or status
        result.append(
            {
                "id": item_id,
                "title": title,
                "owner": str(raw.get("owner") or "")[:80],
                "status": status,
            },
        )
    return result


def checklist_status_from_trace(stage_trace: list[dict[str, Any]]) -> dict[str, str]:
    result: dict[str, str] = {}
    for event in stage_trace:
        if not isinstance(event, dict):
            continue
        agent = str(event.get("agent") or "").strip()
        status = str(event.get("status") or "").strip().lower()
        if agent and status in {"completed", "failed", "warning", "started", "running", "retrying"}:
            result[normalize_checklist_owner(agent)] = "running" if status == "started" else status
    return result


def inferred_checklist_status(owner: str, trace_status: dict[str, str]) -> str:
    normalized = normalize_checklist_owner(owner)
    if not normalized:
        return ""
    aliases = {
        "writer": "contentwriter",
        "designer": "styledesigner",
        "coder": "htmlcoder",
    }
    return trace_status.get(normalized) or trace_status.get(aliases.get(normalized, ""), "")


def normalize_checklist_owner(value: str) -> str:
    return "".join(ch for ch in str(value or "").lower() if ch.isalnum())


def sanitize_skill_trace(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []
    result: list[dict[str, str]] = []
    for raw in value[:40]:
        if not isinstance(raw, dict):
            continue
        skill_id = str(raw.get("id") or "")[:120]
        if not skill_id:
            continue
        result.append(
            {
                "id": skill_id,
                "title": str(raw.get("title") or "")[:160],
                "agent": str(raw.get("agent") or "")[:120],
                "version": str(raw.get("version") or "")[:40],
                "source": str(raw.get("source") or "")[:40],
                "kind": str(raw.get("kind") or "")[:40],
                "trigger_reason": str(raw.get("trigger_reason") or "")[:240],
            },
        )
    return result


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
