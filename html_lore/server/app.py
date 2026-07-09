from __future__ import annotations

import asyncio
import json
import re
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Annotated

try:
    from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, Query, Request, Response, UploadFile
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
except ModuleNotFoundError as exc:  # pragma: no cover - import guard for static-only installs
    raise RuntimeError(
        "The backend server requires the agent extra: pip install 'html-lore[agent]'",
    ) from exc

from html_lore import __version__

from .ai.api import (
    AIContextError,
    AIConversationService,
    AIJobError,
    AIProviderConfigError,
    AIProviderConfigStore,
    AIService,
    AIRunError,
    AIRunStore,
    ConversationError,
    ConversationStore,
    GuardrailError,
    HtmlGenerationError,
    MaterialGenerationError,
    VectorMaintenanceError,
)
from .ai.vector_maintenance import clear_vector_index_for_items
from .auth import current_user, login, logout, read_session, require_session, session_status
from .config import ServerSettings, load_settings
from .ai.rate_limit import AIRateLimitError, ai_rate_limiter
from .items import ItemContentError, ItemContentUpdateError, ItemDeleteError, ItemMetadataError, ItemService, ItemStateError, normalize_query
from .jobs import JobError, JobService
from .navigation import NavigationConfigError, NavigationConfigService
from .shares import ShareError, ShareSafetyError, ShareService, scan_share_content, settings_for_share_token
from .uploads import UploadError, UploadService, ensure_within


@lru_cache
def get_settings() -> ServerSettings:
    return load_settings()


def get_request_settings(
    settings: Annotated[ServerSettings, Depends(get_settings)],
    request: Request,
) -> ServerSettings:
    user = read_session(settings, request) if settings.auth_enabled else None
    return settings.for_user(user.data_id) if user else settings


def get_item_service(settings: Annotated[ServerSettings, Depends(get_request_settings)]) -> ItemService:
    return ItemService(settings)


def get_upload_service(settings: Annotated[ServerSettings, Depends(get_request_settings)]) -> UploadService:
    return UploadService(settings)


def get_navigation_service(settings: Annotated[ServerSettings, Depends(get_request_settings)]) -> NavigationConfigService:
    return NavigationConfigService(settings)


def get_job_service(settings: Annotated[ServerSettings, Depends(get_request_settings)]) -> JobService:
    return JobService(settings)


def get_share_service(
    settings: Annotated[ServerSettings, Depends(get_request_settings)],
    root_settings: Annotated[ServerSettings, Depends(get_settings)],
) -> ShareService:
    return ShareService(settings, root_settings)


def get_ai_service(settings: Annotated[ServerSettings, Depends(get_request_settings)]) -> AIService:
    return AIService(AIProviderConfigStore(settings), settings)


def get_ai_conversation_service(
    settings: Annotated[ServerSettings, Depends(get_request_settings)],
    item_service: Annotated[ItemService, Depends(get_item_service)],
) -> AIConversationService:
    return AIConversationService(
        settings,
        ConversationStore(settings, item_service),
        item_service,
        AIProviderConfigStore(settings),
        AIRunStore(settings),
    )


def verify_api_token(
    settings: Annotated[ServerSettings, Depends(get_settings)],
    request: Request,
    authorization: Annotated[str, Header()] = "",
    access_token: str = "",
) -> None:
    if settings.api_token:
        scheme, _, token = authorization.partition(" ")
        if (scheme.lower() == "bearer" and token == settings.api_token) or access_token == settings.api_token:
            return
    if settings.auth_enabled:
        require_session(settings, request)
        return
    if not settings.api_token:
        return
    raise HTTPException(status_code=401, detail="API token or login session required.")


ApiAuth = Annotated[None, Depends(verify_api_token)]


def verify_ai_rate_limit(
    settings: Annotated[ServerSettings, Depends(get_settings)],
    request: Request,
) -> None:
    user = read_session(settings, request) if settings.auth_enabled else None
    client_host = request.client.host if request.client else "unknown"
    key = f"user:{user.data_id}" if user else f"ip:{client_host}"
    try:
        ai_rate_limiter.check(
            key,
            max_requests=settings.ai_rate_limit_requests,
            window_seconds=settings.ai_rate_limit_window_seconds,
        )
    except AIRateLimitError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc


AiRateLimit = Annotated[None, Depends(verify_ai_rate_limit)]


@dataclass(frozen=True)
class UploadedMaterial:
    filename: str
    content: bytes
    content_type: str = ""


MATERIAL_UPLOAD_ID_PATTERN = re.compile(r"^mat_upl_[A-Za-z0-9]+$")


async def read_style_reference_metadata(
    reference_file: UploadFile | None,
    reference_file_name: str,
    reference_file_type: str,
    reference_file_size: int,
    max_upload_bytes: int,
) -> dict[str, object]:
    if reference_file is None:
        return {
            "reference_file_name": reference_file_name,
            "reference_file_type": reference_file_type,
            "reference_file_size": reference_file_size,
            "reference_file_content": b"",
        }
    content = await read_limited_upload(reference_file, max_upload_bytes)
    return {
        "reference_file_name": reference_file.filename or reference_file_name,
        "reference_file_type": reference_file.content_type or reference_file_type,
        "reference_file_size": len(content) or reference_file_size,
        "reference_file_content": content,
    }


async def read_generation_materials(files: list[UploadFile], instruction: str, max_upload_bytes: int, max_upload_total_bytes: int) -> list[UploadedMaterial]:
    materials: list[UploadedMaterial] = []
    total = 0
    for index, file in enumerate(files):
        if file is None:
            continue
        content = await read_limited_upload(file, max_upload_bytes)
        total += len(content)
        if total > max(1, int(max_upload_total_bytes or 1)):
            raise HTTPException(status_code=413, detail=f"Uploaded files exceed the configured total size limit of {max_upload_total_bytes} bytes.")
        materials.append(
            UploadedMaterial(
                filename=file.filename or f"material-{index + 1}.txt",
                content=content,
                content_type=file.content_type or "",
            ),
        )
    if materials:
        return materials
    prompt = instruction.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Provide a file or describe what you want to generate.")
    return [UploadedMaterial(filename="prompt.txt", content=prompt.encode("utf-8"), content_type="text/plain")]


def material_uploads_root(settings: ServerSettings) -> Path:
    root = settings.meta_dir or (settings.content_dir.parent / ".html-lore-meta")
    return root / "ai" / "material_uploads"


def material_upload_paths(settings: ServerSettings, upload_id: str) -> tuple[Path, Path]:
    if not MATERIAL_UPLOAD_ID_PATTERN.match(upload_id):
        raise HTTPException(status_code=400, detail="Invalid upload id.")
    root = material_uploads_root(settings)
    metadata_path = root / f"{upload_id}.json"
    content_path = root / f"{upload_id}.bin"
    ensure_within(metadata_path, root)
    ensure_within(content_path, root)
    return metadata_path, content_path


def public_material_upload(metadata: dict[str, object]) -> dict[str, object]:
    return {
        "upload_id": str(metadata.get("upload_id") or ""),
        "filename": str(metadata.get("filename") or ""),
        "content_type": str(metadata.get("content_type") or ""),
        "size": int(metadata.get("size") or 0),
        "created_at": str(metadata.get("created_at") or ""),
    }


async def store_material_upload(file: UploadFile, settings: ServerSettings) -> dict[str, object]:
    content = await read_limited_upload(file, settings.max_upload_bytes)
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    upload_id = f"mat_upl_{uuid.uuid4().hex}"
    metadata_path, content_path = material_upload_paths(settings, upload_id)
    metadata = {
        "upload_id": upload_id,
        "filename": file.filename or "material.txt",
        "content_type": file.content_type or "",
        "size": len(content),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    content_path.write_bytes(content)
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return public_material_upload(metadata)


def load_material_upload(settings: ServerSettings, upload_id: str) -> UploadedMaterial:
    metadata_path, content_path = material_upload_paths(settings, upload_id)
    if not metadata_path.exists() or not content_path.exists():
        raise HTTPException(status_code=404, detail="Uploaded material not found.")
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Uploaded material metadata is invalid.") from exc
    if not isinstance(metadata, dict):
        raise HTTPException(status_code=400, detail="Uploaded material metadata is invalid.")
    content = content_path.read_bytes()
    return UploadedMaterial(
        filename=str(metadata.get("filename") or "material.txt"),
        content=content,
        content_type=str(metadata.get("content_type") or ""),
    )


def delete_material_upload(settings: ServerSettings, upload_id: str) -> None:
    metadata_path, content_path = material_upload_paths(settings, upload_id)
    for path in (metadata_path, content_path):
        try:
            path.unlink()
        except FileNotFoundError:
            pass


def read_uploaded_generation_materials(settings: ServerSettings, upload_ids: list[str] | None) -> list[UploadedMaterial]:
    ids = [str(upload_id or "").strip() for upload_id in (upload_ids or []) if str(upload_id or "").strip()]
    if not ids:
        return []
    materials = [load_material_upload(settings, upload_id) for upload_id in ids]
    total = sum(len(material.content) for material in materials)
    ensure_upload_total_within_limit(total, settings.max_upload_total_bytes)
    return materials


def uploaded_payload_size(materials: list[UploadedMaterial], reference: dict[str, object]) -> int:
    reference_content = reference.get("reference_file_content")
    reference_size = len(reference_content) if isinstance(reference_content, bytes) else 0
    return sum(len(material.content) for material in materials) + reference_size


def ensure_upload_total_within_limit(total: int, max_upload_total_bytes: int) -> None:
    limit = max(1, int(max_upload_total_bytes or 1))
    if total > limit:
        raise HTTPException(status_code=413, detail=f"Uploaded files exceed the configured total size limit of {limit} bytes.")


async def read_limited_upload(file: UploadFile, max_upload_bytes: int) -> bytes:
    chunks: list[bytes] = []
    total = 0
    limit = max(1, int(max_upload_bytes or 1))
    while True:
        chunk = await file.read(1024 * 1024)
        if not chunk:
            break
        total += len(chunk)
        if total > limit:
            raise HTTPException(status_code=413, detail=f"Uploaded file exceeds the configured size limit of {limit} bytes.")
        chunks.append(chunk)
    return b"".join(chunks)


def create_app() -> FastAPI:
    settings = get_settings()
    if settings.auth_enabled:
        from .users import UserStore

        UserStore(settings).ensure_bootstrap_admin()
    app = FastAPI(title="HTMlore API Server", version=__version__)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/auth/status")
    def auth_status(request: Request) -> dict:
        return session_status(settings, request)

    @app.post("/api/auth/login")
    def auth_login(values: dict, response: Response) -> dict:
        username = str(values.get("username", ""))
        password = str(values.get("password", ""))
        return login(settings, response, username=username, password=password)

    @app.post("/api/auth/logout")
    def auth_logout(response: Response) -> dict:
        return logout(settings, response)

    @app.get("/api/manifest")
    def manifest(_: ApiAuth, service: Annotated[ItemService, Depends(get_item_service)]) -> dict:
        return service.manifest()

    @app.get("/api/version")
    def version(_: ApiAuth) -> dict[str, str]:
        return {
            "version": __version__,
            "brand": "HTMlore",
            "repository": "JMoCoder/html_lore",
            "release_url": "https://github.com/JMoCoder/html_lore/releases",
        }

    @app.get("/api/ai/providers")
    def ai_provider(_: ApiAuth, service: Annotated[AIService, Depends(get_ai_service)]) -> dict:
        try:
            return service.provider()
        except AIProviderConfigError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.put("/api/ai/providers")
    def update_ai_provider(values: dict, _: ApiAuth, service: Annotated[AIService, Depends(get_ai_service)]) -> dict:
        try:
            return service.update_provider(values)
        except AIProviderConfigError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/ai/status")
    def ai_status(_: ApiAuth, service: Annotated[AIService, Depends(get_ai_service)]) -> dict:
        try:
            return service.status()
        except AIProviderConfigError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/api/ai/test-provider")
    def ai_test_provider(_: ApiAuth, __: AiRateLimit, service: Annotated[AIService, Depends(get_ai_service)]) -> dict:
        try:
            return service.test_provider()
        except AIProviderConfigError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/ai/vector-index")
    def ai_vector_index(_: ApiAuth, service: Annotated[AIService, Depends(get_ai_service)]) -> dict:
        try:
            return service.vector_index_stats()
        except VectorMaintenanceError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/api/ai/vector-index/prune")
    def prune_ai_vector_index(_: ApiAuth, service: Annotated[AIService, Depends(get_ai_service)]) -> dict:
        try:
            return service.prune_vector_index()
        except VectorMaintenanceError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/api/ai/vector-index/clear")
    def clear_ai_vector_index(_: ApiAuth, service: Annotated[AIService, Depends(get_ai_service)]) -> dict:
        try:
            return service.clear_vector_index()
        except VectorMaintenanceError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/api/ai/vector-index/rebuild")
    def rebuild_ai_vector_index(_: ApiAuth, __: AiRateLimit, service: Annotated[AIService, Depends(get_ai_service)]) -> dict:
        try:
            return service.rebuild_vector_index()
        except VectorMaintenanceError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/api/ai/vector-index/smoke-test")
    def smoke_test_ai_embedding(_: ApiAuth, __: AiRateLimit, service: Annotated[AIService, Depends(get_ai_service)]) -> dict:
        try:
            return service.smoke_test_embedding()
        except (AIProviderConfigError, VectorMaintenanceError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/api/ai/context/resolve")
    def ai_resolve_context(values: dict, _: ApiAuth, service: Annotated[AIConversationService, Depends(get_ai_conversation_service)]) -> dict:
        try:
            return service.resolve_context(values)
        except AIContextError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/api/ai/conversations")
    def create_ai_conversation(values: dict, _: ApiAuth, service: Annotated[AIConversationService, Depends(get_ai_conversation_service)]) -> dict:
        try:
            return service.create(values)
        except (AIContextError, ConversationError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/ai/conversations")
    def ai_conversations(_: ApiAuth, service: Annotated[AIConversationService, Depends(get_ai_conversation_service)], context_key: str = "", limit: int = 100) -> dict:
        try:
            return service.list(context_key=context_key, limit=limit)
        except ConversationError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/ai/conversations/latest")
    def ai_latest_conversation(context_key: str, _: ApiAuth, service: Annotated[AIConversationService, Depends(get_ai_conversation_service)]) -> dict:
        try:
            return service.latest(context_key)
        except ConversationError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/ai/conversations/{conversation_id}")
    def ai_conversation(conversation_id: str, _: ApiAuth, service: Annotated[AIConversationService, Depends(get_ai_conversation_service)]) -> dict:
        try:
            return service.get(conversation_id)
        except ConversationError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.delete("/api/ai/conversations/{conversation_id}")
    def delete_ai_conversation(conversation_id: str, _: ApiAuth, service: Annotated[AIConversationService, Depends(get_ai_conversation_service)]) -> dict:
        try:
            return service.delete(conversation_id)
        except ConversationError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/api/ai/conversations/{conversation_id}/messages")
    def ai_conversation_messages(conversation_id: str, _: ApiAuth, service: Annotated[AIConversationService, Depends(get_ai_conversation_service)]) -> dict:
        try:
            return service.messages(conversation_id)
        except ConversationError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/api/ai/conversations/{conversation_id}/messages")
    def create_ai_conversation_message(conversation_id: str, values: dict, _: ApiAuth, __: AiRateLimit, service: Annotated[AIConversationService, Depends(get_ai_conversation_service)]) -> dict:
        try:
            return service.add_message(conversation_id, values)
        except GuardrailError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except ConversationError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/api/ai/conversations/{conversation_id}/generate-note")
    def generate_ai_note(conversation_id: str, values: dict, _: ApiAuth, __: AiRateLimit, service: Annotated[AIConversationService, Depends(get_ai_conversation_service)]) -> dict:
        try:
            return service.generate_note(conversation_id, values)
        except ConversationError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except (HtmlGenerationError, AIRunError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/api/ai/conversations/{conversation_id}/generate-note/jobs")
    def enqueue_ai_note(conversation_id: str, values: dict, _: ApiAuth, __: AiRateLimit, service: Annotated[AIConversationService, Depends(get_ai_conversation_service)]) -> dict:
        try:
            return service.enqueue_generate_note(conversation_id, values)
        except ConversationError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except (HtmlGenerationError, AIJobError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/api/ai/material-runs")
    async def generate_ai_note_from_material(
        _: ApiAuth,
        __: AiRateLimit,
        service: Annotated[AIConversationService, Depends(get_ai_conversation_service)],
        file: Annotated[list[UploadFile] | None, File()] = None,
        upload_id: Annotated[list[str] | None, Form()] = None,
        instruction: Annotated[str, Form()] = "",
        theme: Annotated[str, Form()] = "default",
        target_use: Annotated[str, Form()] = "default",
        reference_style: Annotated[str, Form()] = "default",
        reference_note_id: Annotated[str, Form()] = "",
        reference_file: Annotated[UploadFile | None, File()] = None,
        reference_file_name: Annotated[str, Form()] = "",
        reference_file_type: Annotated[str, Form()] = "",
        reference_file_size: Annotated[int, Form()] = 0,
        style_preference: Annotated[str, Form()] = "default",
        audience: Annotated[str, Form()] = "default",
    ) -> dict:
        uploaded_materials = read_uploaded_generation_materials(service.settings, upload_id)
        materials = uploaded_materials or await read_generation_materials(file or [], instruction, service.settings.max_upload_bytes, service.settings.max_upload_total_bytes)
        uploaded_reference = await read_style_reference_metadata(reference_file, reference_file_name, reference_file_type, reference_file_size, service.settings.max_upload_bytes)
        ensure_upload_total_within_limit(uploaded_payload_size(materials, uploaded_reference), service.settings.max_upload_total_bytes)
        try:
            result = service.generate_note_from_material(
                materials=[asdict(material) for material in materials],
                instruction=instruction,
                values={
                    "theme": theme,
                    "target_use": target_use,
                    "reference_style": reference_style,
                    "reference_note_id": reference_note_id,
                    **uploaded_reference,
                    "style_preference": style_preference,
                    "audience": audience,
                },
            )
            for uploaded_id in upload_id or []:
                delete_material_upload(service.settings, uploaded_id)
            return result
        except (HtmlGenerationError, MaterialGenerationError, AIRunError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/api/ai/material-uploads")
    async def upload_ai_material(
        _: ApiAuth,
        __: AiRateLimit,
        settings: Annotated[ServerSettings, Depends(get_request_settings)],
        file: Annotated[list[UploadFile] | None, File()] = None,
    ) -> dict:
        files = [item for item in (file or []) if item is not None]
        if not files:
            raise HTTPException(status_code=400, detail="Choose at least one file to upload.")
        uploads: list[dict[str, object]] = []
        total = 0
        try:
            for item in files:
                upload = await store_material_upload(item, settings)
                total += int(upload.get("size") or 0)
                uploads.append(upload)
            ensure_upload_total_within_limit(total, settings.max_upload_total_bytes)
        except HTTPException:
            for upload in uploads:
                delete_material_upload(settings, str(upload.get("upload_id") or ""))
            raise
        return {"uploads": uploads, "count": len(uploads), "total_size": total}

    @app.delete("/api/ai/material-uploads/{upload_id}")
    def delete_ai_material_upload(upload_id: str, _: ApiAuth, settings: Annotated[ServerSettings, Depends(get_request_settings)]) -> dict:
        delete_material_upload(settings, upload_id)
        return {"ok": True}

    @app.post("/api/ai/material-jobs")
    async def enqueue_ai_note_from_material(
        _: ApiAuth,
        __: AiRateLimit,
        service: Annotated[AIConversationService, Depends(get_ai_conversation_service)],
        file: Annotated[list[UploadFile] | None, File()] = None,
        upload_id: Annotated[list[str] | None, Form()] = None,
        instruction: Annotated[str, Form()] = "",
        theme: Annotated[str, Form()] = "default",
        target_use: Annotated[str, Form()] = "default",
        reference_style: Annotated[str, Form()] = "default",
        reference_note_id: Annotated[str, Form()] = "",
        reference_file: Annotated[UploadFile | None, File()] = None,
        reference_file_name: Annotated[str, Form()] = "",
        reference_file_type: Annotated[str, Form()] = "",
        reference_file_size: Annotated[int, Form()] = 0,
        style_preference: Annotated[str, Form()] = "default",
        audience: Annotated[str, Form()] = "default",
    ) -> dict:
        uploaded_materials = read_uploaded_generation_materials(service.settings, upload_id)
        materials = uploaded_materials or await read_generation_materials(file or [], instruction, service.settings.max_upload_bytes, service.settings.max_upload_total_bytes)
        uploaded_reference = await read_style_reference_metadata(reference_file, reference_file_name, reference_file_type, reference_file_size, service.settings.max_upload_bytes)
        ensure_upload_total_within_limit(uploaded_payload_size(materials, uploaded_reference), service.settings.max_upload_total_bytes)
        try:
            result = service.enqueue_generate_note_from_material(
                materials=[asdict(material) for material in materials],
                instruction=instruction,
                values={
                    "theme": theme,
                    "target_use": target_use,
                    "reference_style": reference_style,
                    "reference_note_id": reference_note_id,
                    **uploaded_reference,
                    "style_preference": style_preference,
                    "audience": audience,
                },
            )
            for uploaded_id in upload_id or []:
                delete_material_upload(service.settings, uploaded_id)
            return result
        except (HtmlGenerationError, MaterialGenerationError, AIJobError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/ai/runs")
    def ai_runs(_: ApiAuth, service: Annotated[AIConversationService, Depends(get_ai_conversation_service)], limit: int = 20) -> dict:
        try:
            return service.runs(limit=limit)
        except AIRunError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/ai/runs/{run_id}")
    def ai_run(run_id: str, _: ApiAuth, service: Annotated[AIConversationService, Depends(get_ai_conversation_service)]) -> dict:
        try:
            return service.run(run_id)
        except AIRunError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/api/ai/eval/qa-runtime-comparison")
    def compare_ai_qa_runtimes(values: dict, _: ApiAuth, __: AiRateLimit, service: Annotated[AIConversationService, Depends(get_ai_conversation_service)]) -> dict:
        try:
            return service.compare_qa_runtimes(values)
        except (AIContextError, ConversationError, AIProviderConfigError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/api/ai/eval/agent-qa-run")
    def run_ai_agent_qa_once(values: dict, _: ApiAuth, __: AiRateLimit, service: Annotated[AIConversationService, Depends(get_ai_conversation_service)]) -> dict:
        try:
            return service.run_agent_qa_once(values)
        except (AIContextError, ConversationError, AIProviderConfigError, AIRunError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/ai/jobs")
    def ai_jobs(_: ApiAuth, service: Annotated[AIConversationService, Depends(get_ai_conversation_service)], limit: int = 20) -> dict:
        try:
            return service.jobs(limit=limit)
        except AIJobError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/ai/jobs/{job_id}")
    def ai_job(job_id: str, _: ApiAuth, service: Annotated[AIConversationService, Depends(get_ai_conversation_service)]) -> dict:
        try:
            return service.job(job_id)
        except AIJobError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/api/ai/jobs/{job_id}/events")
    async def ai_job_events(job_id: str, _: ApiAuth, service: Annotated[AIConversationService, Depends(get_ai_conversation_service)]) -> StreamingResponse:
        async def stream():
            last_payload = ""
            while True:
                try:
                    payload = service.job(job_id)
                    data = json.dumps(payload, ensure_ascii=False)
                    if data != last_payload:
                        last_payload = data
                        yield f"event: job\ndata: {data}\n\n"
                    status = str(payload.get("job", {}).get("status") or "").lower()
                    if status in {"completed", "failed", "cancelled"}:
                        break
                except AIJobError as exc:
                    error_data = json.dumps({"detail": str(exc)}, ensure_ascii=False)
                    yield f"event: error\ndata: {error_data}\n\n"
                    break
                await asyncio.sleep(1.0)

        return StreamingResponse(
            stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    @app.post("/api/ai/jobs/{job_id}/retry")
    def retry_ai_job(job_id: str, _: ApiAuth, __: AiRateLimit, service: Annotated[AIConversationService, Depends(get_ai_conversation_service)]) -> dict:
        try:
            return service.retry_job(job_id)
        except AIJobError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.delete("/api/ai/jobs/{job_id}")
    def cancel_ai_job(job_id: str, _: ApiAuth, service: Annotated[AIConversationService, Depends(get_ai_conversation_service)]) -> dict:
        try:
            return service.cancel_job(job_id)
        except AIJobError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/api/rebuild")
    def rebuild(_: ApiAuth, service: Annotated[JobService, Depends(get_job_service)]) -> dict:
        try:
            return service.rebuild()
        except JobError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @app.get("/api/rebuild/{job_id}")
    def rebuild_job(job_id: str, _: ApiAuth, service: Annotated[JobService, Depends(get_job_service)]) -> dict:
        try:
            job = service.get_job(job_id)
        except JobError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        if job.get("kind") != "rebuild":
            raise HTTPException(status_code=404, detail="Rebuild job not found.")
        return job

    @app.get("/api/items")
    def items(
        _: ApiAuth,
        service: Annotated[ItemService, Depends(get_item_service)],
        q: str = "",
        library: str = "all",
        collection: str = "",
        tags: str = "",
        tag_match: str = "any",
        favorite: bool | None = None,
        archived: bool | None = None,
        sort: str = "newest",
        limit: Annotated[int | None, Query(gt=0, le=500)] = None,
    ) -> dict:
        query = normalize_query(
            q=q,
            library=library,
            collection=collection,
            tags=tags,
            tag_match=tag_match,
            favorite=favorite,
            archived=archived,
            sort=sort,
            limit=limit,
        )
        result = service.list_items(query)
        return {"items": result, "count": len(result)}

    @app.get("/api/search")
    def search(
        _: ApiAuth,
        service: Annotated[ItemService, Depends(get_item_service)],
        q: str = "",
        library: str = "all",
        collection: str = "",
        tags: str = "",
        tag_match: str = "any",
        favorite: bool | None = None,
        archived: bool | None = None,
        sort: str = "newest",
        limit: Annotated[int | None, Query(gt=0, le=500)] = None,
    ) -> dict:
        query = normalize_query(
            q=q,
            library=library,
            collection=collection,
            tags=tags,
            tag_match=tag_match,
            favorite=favorite,
            archived=archived,
            sort=sort,
            limit=limit,
        )
        return service.search_items(query)

    @app.get("/api/items/{item_id:path}/content", response_class=HTMLResponse)
    def item_content(item_id: str, _: ApiAuth, service: Annotated[ItemService, Depends(get_item_service)]) -> HTMLResponse:
        try:
            return HTMLResponse(service.read_item_content(item_id))
        except ItemContentError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/api/items/{item_id:path}/raw", response_class=HTMLResponse)
    def item_raw(item_id: str, _: ApiAuth, service: Annotated[ItemService, Depends(get_item_service)]) -> HTMLResponse:
        try:
            return HTMLResponse(service.read_item_content(item_id))
        except ItemContentError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.put("/api/items/{item_id:path}/content")
    def update_item_content(item_id: str, values: dict, _: ApiAuth, service: Annotated[ItemService, Depends(get_item_service)]) -> dict:
        try:
            result = service.update_item_content(item_id, values.get("content"))
            clear_vector_index_for_items(service, {item_id})
            return result
        except ItemContentUpdateError as exc:
            message = str(exc)
            status = 404 if message == "Item not found." else 400
            raise HTTPException(status_code=status, detail=message) from exc

    @app.post("/api/items/{item_id:path}/content/share-safety")
    def check_item_content_share_safety(item_id: str, values: dict, _: ApiAuth, service: Annotated[ItemService, Depends(get_item_service)]) -> dict:
        if not service.get_item(item_id):
            raise HTTPException(status_code=404, detail="Item not found.")
        content = values.get("content")
        if not isinstance(content, str):
            raise HTTPException(status_code=400, detail="Content must be a string.")
        return scan_share_content(content)

    @app.get("/api/navigation")
    def navigation(_: ApiAuth, service: Annotated[NavigationConfigService, Depends(get_navigation_service)]) -> dict:
        try:
            return service.get_config()
        except NavigationConfigError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.put("/api/navigation")
    def update_navigation(values: dict, _: ApiAuth, service: Annotated[NavigationConfigService, Depends(get_navigation_service)]) -> dict:
        try:
            return service.update_config(values)
        except NavigationConfigError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.patch("/api/items/{item_id:path}/metadata")
    def update_item_metadata(item_id: str, values: dict, _: ApiAuth, service: Annotated[ItemService, Depends(get_item_service)]) -> dict:
        try:
            result = service.update_item_metadata(item_id, values)
            clear_vector_index_for_items(service, {item_id})
            return result
        except ItemMetadataError as exc:
            message = str(exc)
            status = 404 if message == "Item not found." else 400
            raise HTTPException(status_code=status, detail=message) from exc

    @app.patch("/api/items/{item_id:path}/state")
    def update_item_state(item_id: str, values: dict, _: ApiAuth, service: Annotated[ItemService, Depends(get_item_service)]) -> dict:
        try:
            result = service.update_item_state(item_id, values)
            if "archived" in values:
                clear_vector_index_for_items(service, {item_id})
            return result
        except ItemStateError as exc:
            message = str(exc)
            status = 404 if message == "Item not found." else 400
            raise HTTPException(status_code=status, detail=message) from exc

    @app.get("/api/items/{item_id:path}")
    def item(item_id: str, _: ApiAuth, service: Annotated[ItemService, Depends(get_item_service)]) -> dict:
        found = service.get_item(item_id)
        if not found:
            raise HTTPException(status_code=404, detail="Item not found")
        return found

    @app.delete("/api/items/{item_id:path}")
    def delete_item(item_id: str, _: ApiAuth, service: Annotated[ItemService, Depends(get_item_service)]) -> dict:
        try:
            result = service.delete_item(item_id)
            clear_vector_index_for_items(service, {item_id})
            return result
        except ItemDeleteError as exc:
            message = str(exc)
            status = 404 if message == "Item not found." else 400
            raise HTTPException(status_code=status, detail=message) from exc

    @app.get("/api/uploads/{upload_id}")
    def upload_status(upload_id: str, _: ApiAuth, service: Annotated[JobService, Depends(get_job_service)]) -> dict:
        try:
            return service.get_upload(upload_id)
        except JobError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/api/shares")
    def shares(_: ApiAuth, service: Annotated[ShareService, Depends(get_share_service)]) -> dict:
        items = service.list_shares()
        return {"shares": items, "count": len(items)}

    @app.post("/api/shares")
    def create_share(values: dict, _: ApiAuth, service: Annotated[ShareService, Depends(get_share_service)]) -> dict:
        try:
            result = service.create_share(
                item_id=str(values.get("item_id") or ""),
                duration=str(values.get("duration") or "1d"),
            )
        except ShareSafetyError as exc:
            raise HTTPException(status_code=400, detail={"message": str(exc), "safety": exc.scan}) from exc
        except ShareError as exc:
            message = str(exc)
            status = 404 if message == "Item not found." else 400
            raise HTTPException(status_code=status, detail=message) from exc
        return {
            "share": result.share,
            "token": result.token,
            "url_path": result.url_path,
        }

    @app.patch("/api/shares/{share_id}")
    def update_share(share_id: str, values: dict, _: ApiAuth, service: Annotated[ShareService, Depends(get_share_service)]) -> dict:
        try:
            return service.update_share(share_id, values)
        except ShareError as exc:
            message = str(exc)
            status = 404 if message == "Share not found." else 400
            raise HTTPException(status_code=status, detail=message) from exc

    @app.delete("/api/shares/{share_id}")
    def revoke_share(share_id: str, _: ApiAuth, service: Annotated[ShareService, Depends(get_share_service)]) -> dict:
        try:
            return service.revoke_share(share_id)
        except ShareError as exc:
            message = str(exc)
            status = 404 if message == "Share not found." else 400
            raise HTTPException(status_code=status, detail=message) from exc

    @app.get("/api/public/shares/{token}")
    def public_share(token: str) -> dict:
        public_settings = settings_for_share_token(settings, token)
        try:
            return ShareService(public_settings, settings).public_read_by_token(token)
        except ShareError as exc:
            raise HTTPException(status_code=404, detail="Share not found.") from exc

    @app.get("/share/{token}", response_class=HTMLResponse)
    @app.get("/share/{token}/", response_class=HTMLResponse)
    def public_share_page(token: str) -> HTMLResponse:
        public_settings = settings_for_share_token(settings, token)
        try:
            data = ShareService(public_settings, settings).public_read_by_token(token)
        except ShareError as exc:
            raise HTTPException(status_code=404, detail="Share not found.") from exc
        return HTMLResponse(render_share_page(data))

    @app.post("/api/uploads/html")
    async def upload_html(
        _: ApiAuth,
        service: Annotated[UploadService, Depends(get_upload_service)],
        jobs: Annotated[JobService, Depends(get_job_service)],
        file: Annotated[UploadFile, File()],
        title: Annotated[str, Form()] = "",
        summary: Annotated[str, Form()] = "",
        collection: Annotated[str, Form()] = "",
        tags: Annotated[str, Form()] = "",
    ) -> dict:
        content = await file.read()
        try:
            result = service.import_html(
                filename=file.filename or "imported-note.html",
                content=content,
                title=title,
                summary=summary,
                collection=collection,
                tags=tags,
            )
        except UploadError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        job = jobs.record_upload(upload_id=result.upload_id, item_id=result.item_id, status=result.status)
        return {
            "upload_id": result.upload_id,
            "job_id": job["job_id"],
            "item_id": result.item_id,
            "status": result.status,
            "item": result.item,
        }

    if settings.public_dir.exists():
        @app.get("/{path:path}")
        def static_file(path: str, request: Request) -> FileResponse:
            return serve_static(settings, request, path)

    return app


app = create_app()


def serve_static(settings: ServerSettings, request: Request, path: str) -> FileResponse:
    relative_path = Path(path or "index.html")
    if static_requires_auth(relative_path):
        user = read_session(settings, request) if settings.auth_enabled else None
        active_settings = settings.for_user(user.data_id) if user else settings
    else:
        active_settings = settings
    public_dir = active_settings.public_dir.resolve()
    requested = (public_dir / relative_path).resolve()
    if requested.is_dir():
        requested = (requested / "index.html").resolve()
    if public_dir not in requested.parents and requested != public_dir:
        raise HTTPException(status_code=404, detail="File not found.")
    if not requested.exists() or not requested.is_file():
        raise HTTPException(status_code=404, detail="File not found.")
    if static_requires_auth(requested.relative_to(public_dir)):
        require_session(settings, request)
    return FileResponse(requested)


def static_requires_auth(path: Path) -> bool:
    parts = path.parts
    if not parts:
        return False
    if parts[0] == "content":
        return True
    if path.name == "manifest.json":
        return True
    return False


def render_share_page(data: dict) -> str:
    item = data.get("item") or {}
    title = escape_html(item.get("title") or "Shared note")
    summary = escape_html(item.get("summary") or "")
    srcdoc = escape_html(render_share_srcdoc(data))
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex, nofollow">
  <title>{title} - HTMlore Share</title>
  <style>
    :root {{ color-scheme: light dark; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    body {{ margin: 0; background: #f8fafc; color: #172033; }}
    .share-shell {{ padding: 18px 20px 56px; }}
    .share-banner {{ max-width: 1100px; margin: 0 auto 18px; border-bottom: 1px solid #d9e2ec; padding-bottom: 14px; }}
    .share-banner-top {{ display: flex; align-items: center; justify-content: space-between; gap: 14px; }}
    .share-brand {{ color: #0f766e; font-size: 0.8rem; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; }}
    .share-download-button {{
      width: 36px;
      height: 36px;
      border: 1px solid rgba(15, 118, 110, 0.24);
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.56);
      color: #0f766e;
      opacity: 0.22;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: opacity 160ms ease, background 160ms ease, border-color 160ms ease, transform 160ms ease;
      backdrop-filter: blur(12px);
    }}
    .share-download-button:hover,
    .share-download-button:focus-visible {{
      opacity: 0.9;
      background: rgba(255, 255, 255, 0.82);
      border-color: rgba(15, 118, 110, 0.42);
      transform: translateY(-1px);
      outline: none;
    }}
    .share-download-button svg {{ width: 18px; height: 18px; fill: none; stroke: currentColor; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }}
    .share-title {{ margin: 8px 0; font-size: clamp(1.45rem, 3vw, 2.25rem); line-height: 1.15; }}
    .share-summary {{ color: #607086; font-size: 0.95rem; line-height: 1.55; }}
    .share-frame {{ display: block; width: min(1100px, 100%); min-height: 70vh; margin: 0 auto; border: 0; border-radius: 12px; background: white; }}
    @media (prefers-color-scheme: dark) {{
      body {{ background: #101820; color: #e6edf3; }}
      .share-banner {{ border-color: #334155; }}
      .share-summary {{ color: #a9b6c6; }}
      .share-download-button {{ background: rgba(15, 23, 42, 0.48); border-color: rgba(148, 163, 184, 0.22); color: #99f6e4; }}
      .share-download-button:hover,
      .share-download-button:focus-visible {{ background: rgba(15, 23, 42, 0.74); border-color: rgba(153, 246, 228, 0.42); }}
      .share-frame {{ background: #111827; }}
    }}
  </style>
</head>
<body>
  <div class="share-shell">
    <div class="share-banner">
      <div class="share-banner-top">
        <div class="share-brand">HTMlore shared note</div>
        <button type="button" class="share-download-button" aria-label="Download shared HTML" title="Download shared HTML">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M12 3v12"></path>
            <path d="m7 10 5 5 5-5"></path>
            <path d="M5 21h14"></path>
          </svg>
        </button>
      </div>
      <h1 class="share-title">{title}</h1>
      <p class="share-summary">{summary}</p>
    </div>
    <iframe class="share-frame" title="{title}" sandbox="allow-scripts" srcdoc="{srcdoc}"></iframe>
  </div>
  <script>
    const frame = document.querySelector(".share-frame");
    const downloadButton = document.querySelector(".share-download-button");
    function shareDownloadFilename() {{
      const title = (document.querySelector(".share-title")?.textContent || "html-lore-shared-note").trim();
      let filename = title.replace(/[\\\\/:*?"<>|\\u0000-\\u001f]+/g, "-").replace(/\\s+/g, " ").trim().replace(/[. ]+$/g, "").slice(0, 120);
      if (!filename) filename = "html-lore-shared-note";
      if (!/\\.html?$/i.test(filename)) filename = `${{filename}}.html`;
      return filename;
    }}
    function downloadSharedHtml() {{
      if (!frame) return;
      const source = frame.getAttribute("srcdoc") || frame.srcdoc || "";
      const blob = new Blob([source], {{ type: "text/html;charset=utf-8" }});
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = shareDownloadFilename();
      document.body.append(link);
      link.click();
      link.remove();
      window.setTimeout(() => URL.revokeObjectURL(url), 0);
    }}
    downloadButton?.addEventListener("click", downloadSharedHtml);
    window.addEventListener("message", (event) => {{
      if (!frame || event.source !== frame.contentWindow || !event.data) return;
      if (event.data.type === "html-lore-share-height") {{
        const height = Number(event.data.height);
        if (Number.isFinite(height) && height > 0) {{
          frame.style.height = `${{Math.min(Math.max(height, 420), 16000)}}px`;
        }}
      }}
      if (event.data.type === "html-lore-share-anchor") {{
        const top = Number(event.data.top);
        if (Number.isFinite(top)) {{
          const frameTop = frame.getBoundingClientRect().top + window.scrollY;
          window.scrollTo({{ top: Math.max(frameTop + top - 12, 0), behavior: "smooth" }});
        }}
      }}
    }});
  </script>
</body>
</html>"""


def render_share_srcdoc(data: dict) -> str:
    body = data.get("html") or ""
    styles = data.get("styles") or ""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root {{ color-scheme: light dark; }}
    html {{ min-height: 100%; }}
    body {{ margin: 0; overflow-wrap: anywhere; }}
    a:not([href]) {{ color: inherit; text-decoration: none; pointer-events: none; }}
    a[href^="#"] {{ pointer-events: auto; }}
    img, video, svg, canvas {{ max-width: 100%; height: auto; }}
  </style>
  {styles}
</head>
<body>
  {body}
  <script>
    function reportHeight() {{
      const doc = document.documentElement;
      const height = Math.max(doc.scrollHeight, document.body ? document.body.scrollHeight : 0);
      parent.postMessage({{ type: "html-lore-share-height", height }}, "*");
    }}
    function scrollToFragment(hash) {{
      if (!hash || hash === "#") return;
      const id = decodeURIComponent(hash.slice(1));
      const target = document.getElementById(id);
      if (!target) return;
      const top = target.getBoundingClientRect().top;
      parent.postMessage({{ type: "html-lore-share-anchor", top }}, "*");
      target.scrollIntoView({{ block: "start", behavior: "smooth" }});
      reportHeight();
    }}
    document.addEventListener("click", (event) => {{
      const anchor = event.target.closest('a[href^="#"]');
      if (anchor) {{
        event.preventDefault();
        scrollToFragment(anchor.getAttribute("href"));
        return;
      }}
      const trigger = event.target.closest("[data-share-toggle]");
      if (!trigger) return;
      const target = document.getElementById(trigger.getAttribute("data-share-toggle"));
      if (target) {{
        target.classList.toggle("open");
        reportHeight();
      }}
    }});
    window.addEventListener("load", reportHeight);
    if ("ResizeObserver" in window) new ResizeObserver(reportHeight).observe(document.documentElement);
    reportHeight();
  </script>
</body>
</html>"""


def escape_html(value: object) -> str:
    return (
        str(value or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
