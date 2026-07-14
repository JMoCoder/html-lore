from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from html_lore.server.config import ServerSettings

from .schemas import ParsedDocument, normalize_for_json


@dataclass(frozen=True)
class MaterialBundle:
    bundle_id: str = ""
    merged_text: str = ""
    manifest: dict[str, Any] = field(default_factory=dict)
    workbooks: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class MaterialBundleReference:
    bundle_id: str = ""
    job_id: str = ""
    workspace_path: str = ""
    merged_path: str = ""
    manifest_path: str = ""
    workbooks_path: str = ""


def build_material_bundle(parsed: ParsedDocument | None, *, run_id: str = "") -> MaterialBundle | None:
    if parsed is None or not parsed.plain_text:
        return None
    bundle_id = safe_bundle_id(run_id or hashlib.sha256(parsed.plain_text.encode("utf-8")).hexdigest()[:16])
    materials = []
    for material in parsed.materials:
        content = parsed.plain_text[max(0, material.content_start_char) : min(len(parsed.plain_text), material.content_end_char)]
        materials.append(
            {
                **normalize_for_json(asdict(material)),
                "content_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
            }
        )
    manifest = {
        "schema_version": 1,
        "bundle_id": bundle_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "merged_sha256": hashlib.sha256(parsed.plain_text.encode("utf-8")).hexdigest(),
        "merged_char_count": len(parsed.plain_text),
        "materials": materials,
        "source_files": normalize_for_json(asdict(parsed).get("source_files", [])),
        "warnings": normalize_for_json(asdict(parsed).get("warnings", [])),
        "capabilities": normalize_for_json(asdict(parsed).get("capabilities", [])),
        "workbook_count": len(parsed.workbooks),
    }
    return MaterialBundle(bundle_id=bundle_id, merged_text=parsed.plain_text, manifest=manifest, workbooks=normalize_for_json(asdict(parsed).get("workbooks", [])))


def write_job_material_bundle(settings: ServerSettings, bundle: MaterialBundle, *, job_id: str) -> MaterialBundleReference:
    if settings.meta_dir is None:
        return MaterialBundleReference()
    workspace = job_workspace_dir(settings, job_id)
    bundle_dir = workspace / "materials"
    ensure_within(bundle_dir, job_workspace_root(settings))
    bundle_dir.mkdir(parents=True, exist_ok=True)
    merged_path = bundle_dir / "merged.md"
    manifest_path = bundle_dir / "manifest.json"
    workbooks_path = bundle_dir / "workbooks.json"
    merged_path.write_text(bundle.merged_text, encoding="utf-8")
    manifest = {**bundle.manifest, "job_id": job_id}
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    if bundle.workbooks:
        workbooks_path.write_text(json.dumps(bundle.workbooks, ensure_ascii=False, indent=2), encoding="utf-8")
    return MaterialBundleReference(
        bundle_id=bundle.bundle_id,
        job_id=job_id,
        workspace_path=internal_meta_relative_path(settings, workspace),
        merged_path=internal_meta_relative_path(settings, merged_path),
        manifest_path=internal_meta_relative_path(settings, manifest_path),
        workbooks_path=internal_meta_relative_path(settings, workbooks_path) if bundle.workbooks else "",
    )


def read_material_bundle_reference(settings: ServerSettings, reference: MaterialBundleReference | None) -> MaterialBundle | None:
    if settings.meta_dir is None or reference is None or not reference.merged_path or not reference.manifest_path:
        return None
    merged_path = settings.meta_dir / reference.merged_path
    manifest_path = settings.meta_dir / reference.manifest_path
    ensure_within(merged_path, settings.meta_dir)
    ensure_within(manifest_path, settings.meta_dir)
    if not merged_path.is_file() or not manifest_path.is_file():
        return None
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        manifest = {}
    workbooks: list[dict[str, Any]] = []
    if reference.workbooks_path:
        workbooks_path = settings.meta_dir / reference.workbooks_path
        ensure_within(workbooks_path, settings.meta_dir)
        if workbooks_path.is_file():
            try:
                decoded = json.loads(workbooks_path.read_text(encoding="utf-8"))
                workbooks = decoded if isinstance(decoded, list) else []
            except json.JSONDecodeError:
                workbooks = []
    return MaterialBundle(bundle_id=reference.bundle_id or str(manifest.get("bundle_id") or ""), merged_text=merged_path.read_text(encoding="utf-8"), manifest=manifest if isinstance(manifest, dict) else {}, workbooks=workbooks)


def write_job_workspace_jsonl(settings: ServerSettings, job_id: str, relative_path: str, records: list[Any]) -> str:
    if settings.meta_dir is None or not job_id or not records:
        return ""
    workspace = job_workspace_dir(settings, job_id)
    ensure_within(workspace, job_workspace_root(settings))
    target = workspace / relative_path
    ensure_within(target, workspace)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as file:
        for record in records:
            value = asdict(record) if is_dataclass(record) else record
            file.write(json.dumps(normalize_for_json(value), ensure_ascii=False, sort_keys=True) + "\n")
    return internal_meta_relative_path(settings, target)


def write_job_workspace_text(settings: ServerSettings, job_id: str, relative_path: str, content: str) -> str:
    if settings.meta_dir is None or not job_id:
        return ""
    workspace = job_workspace_dir(settings, job_id)
    ensure_within(workspace, job_workspace_root(settings))
    target = workspace / relative_path
    ensure_within(target, workspace)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return internal_meta_relative_path(settings, target)


def write_job_workspace_json(settings: ServerSettings, job_id: str, relative_path: str, value: Any) -> str:
    data = asdict(value) if is_dataclass(value) else value
    return write_job_workspace_text(settings, job_id, relative_path, json.dumps(normalize_for_json(data), ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def delete_job_workspace(settings: ServerSettings, job_id: str) -> None:
    if settings.meta_dir is None or not job_id:
        return
    workspace = job_workspace_dir(settings, job_id)
    root = job_workspace_root(settings)
    ensure_within(workspace, root)
    if workspace.exists():
        shutil.rmtree(workspace)


def cleanup_expired_failed_job_workspaces(settings: ServerSettings, *, keep_days: int = 7) -> int:
    if settings.meta_dir is None:
        return 0
    root = job_workspace_root(settings)
    if not root.exists():
        return 0
    cutoff = datetime.now(timezone.utc) - timedelta(days=max(1, int(keep_days or 7)))
    removed = 0
    for workspace in root.glob("*/workspace"):
        if not workspace.is_dir():
            continue
        try:
            modified = datetime.fromtimestamp(workspace.stat().st_mtime, tz=timezone.utc)
        except OSError:
            continue
        if modified >= cutoff:
            continue
        shutil.rmtree(workspace)
        removed += 1
    return removed


def job_material_bundle_root(settings: ServerSettings) -> Path:
    return settings.meta_dir / "ai" / "generation-jobs"  # type: ignore[operator]


def job_workspace_root(settings: ServerSettings) -> Path:
    return settings.meta_dir / "ai" / "generation-jobs"  # type: ignore[operator]


def job_material_bundle_dir(settings: ServerSettings, job_id: str) -> Path:
    return job_workspace_dir(settings, job_id) / "materials"


def job_workspace_dir(settings: ServerSettings, job_id: str) -> Path:
    return job_material_bundle_root(settings) / safe_bundle_id(job_id) / "workspace"


def internal_meta_relative_path(settings: ServerSettings, path: Path) -> str:
    if settings.meta_dir is None:
        return ""
    return path.relative_to(settings.meta_dir).as_posix()


def safe_bundle_id(value: str) -> str:
    cleaned = "".join(ch for ch in value if ch.isalnum() or ch in {"-", "_"})
    return cleaned[:64] or "material-bundle"


def ensure_within(path: Path, root: Path) -> None:
    path.resolve().relative_to(root.resolve())
