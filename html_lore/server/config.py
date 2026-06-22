from __future__ import annotations

import os
from dataclasses import dataclass, replace
from pathlib import Path


@dataclass(frozen=True)
class ServerSettings:
    content_dir: Path
    meta_dir: Path | None
    public_dir: Path
    site_title: str
    max_upload_bytes: int
    api_token: str = ""
    auth_username: str = ""
    auth_password: str = ""
    users_file: Path | None = None
    user_data_dir: Path | None = None
    session_secret: str = ""
    session_cookie_name: str = "html_lore_session"
    session_max_age_seconds: int = 7 * 24 * 60 * 60
    session_secure: bool = False
    cors_origins: tuple[str, ...] = ("http://127.0.0.1:8080", "http://localhost:8080")
    ai_provider: str = ""
    ai_base_url: str = ""
    ai_api_key: str = ""
    ai_model: str = ""
    ai_embedding_model: str = ""
    ai_enabled: bool = False
    ai_external_search: str = ""
    ai_external_search_api_key: str = ""
    ai_external_search_brave_api_key: str = ""
    ai_external_search_max_results: int = 5
    ai_external_search_depth: str = "basic"
    ai_external_search_auto_parameters: bool = False
    ai_external_search_topic: str = "general"
    ai_external_search_time_range: str = ""
    ai_external_search_include_raw_content: bool = False
    ai_max_context_items: int = 50
    ai_max_prompt_chars: int = 12000
    ai_max_message_chars: int = 4000
    ai_max_response_tokens: int = 1024
    ai_rate_limit_requests: int = 20
    ai_rate_limit_window_seconds: int = 60
    ai_retrieval_mode: str = "keyword"
    ai_qa_engine: str = "auto"
    ai_generation_engine: str = "legacy"
    ai_generation_model: str = "gpt-5.5"
    document_parser: str = "markitdown"

    @property
    def auth_enabled(self) -> bool:
        if not self.session_secret:
            return False
        if self.auth_username and self.auth_password:
            return True
        return bool(self.users_file and self.users_file.exists())

    def for_user(self, data_id: str) -> "ServerSettings":
        if data_id == "default" or self.user_data_dir is None:
            return self
        user_root = self.user_data_dir / data_id
        user_settings = replace(
            self,
            content_dir=user_root / "content",
            meta_dir=user_root / "meta" if self.meta_dir is not None else None,
            public_dir=user_root / "public",
        )
        ensure_user_dirs(user_settings)
        return user_settings


def load_settings() -> ServerSettings:
    content_dir = Path(get_env("CONTENT", "content"))
    meta_value = get_env("META", "meta")
    meta_dir = Path(meta_value) if meta_value else None
    public_dir = Path(get_env("PUBLIC", "public"))
    site_title = get_env("TITLE", "HTMlore")
    max_upload_bytes = int(get_env("MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))
    api_token = get_env("API_TOKEN", "").strip()
    auth_username = get_env("AUTH_USERNAME", "").strip()
    auth_password = get_env("AUTH_PASSWORD", "")
    users_file = parse_optional_path(get_env("USERS_FILE"), content_dir.parent / "users.json")
    user_data_dir = parse_optional_path(get_env("USER_DATA_DIR"), content_dir.parent / "users")
    session_secret = get_env("SESSION_SECRET", "").strip()
    session_cookie_name = get_env("SESSION_COOKIE_NAME", "html_lore_session").strip() or "html_lore_session"
    session_max_age_seconds = int(get_env("SESSION_MAX_AGE_SECONDS", str(7 * 24 * 60 * 60)))
    session_secure = parse_bool(get_env("SESSION_SECURE", "false"))
    cors_origins = parse_csv(get_env("CORS_ORIGINS", "http://127.0.0.1:8080,http://localhost:8080"))
    ai_provider = get_env("AI_PROVIDER", "").strip()
    ai_base_url = get_env("AI_BASE_URL", "").strip()
    ai_api_key = get_env("AI_API_KEY", "")
    ai_model = get_env("AI_MODEL", "").strip()
    ai_embedding_model = get_env("AI_EMBEDDING_MODEL", "").strip()
    ai_enabled = parse_bool(get_env("AI_ENABLED", "false"))
    ai_external_search = get_env("AI_EXTERNAL_SEARCH", "").strip()
    ai_external_search_api_key = get_env("AI_EXTERNAL_SEARCH_API_KEY", "")
    ai_external_search_brave_api_key = get_env("AI_EXTERNAL_SEARCH_BRAVE_API_KEY", "")
    ai_external_search_max_results = parse_positive_int(get_env("AI_EXTERNAL_SEARCH_MAX_RESULTS", "5"), 5)
    ai_external_search_depth = parse_choice(get_env("AI_EXTERNAL_SEARCH_DEPTH", "basic"), {"basic", "fast", "ultra-fast", "advanced"}, "basic")
    ai_external_search_auto_parameters = parse_bool(get_env("AI_EXTERNAL_SEARCH_AUTO_PARAMETERS", "false"))
    ai_external_search_topic = parse_choice(get_env("AI_EXTERNAL_SEARCH_TOPIC", "general"), {"general", "news", "finance"}, "general")
    ai_external_search_time_range = parse_choice(get_env("AI_EXTERNAL_SEARCH_TIME_RANGE", ""), {"", "day", "week", "month", "year", "d", "w", "m", "y"}, "")
    ai_external_search_include_raw_content = parse_bool(get_env("AI_EXTERNAL_SEARCH_INCLUDE_RAW_CONTENT", "false"))
    ai_max_context_items = parse_positive_int(get_env("AI_MAX_CONTEXT_ITEMS", "50"), 50)
    ai_max_prompt_chars = parse_positive_int(get_env("AI_MAX_PROMPT_CHARS", "12000"), 12000)
    ai_max_message_chars = parse_positive_int(get_env("AI_MAX_MESSAGE_CHARS", "4000"), 4000)
    ai_max_response_tokens = parse_positive_int(get_env("AI_MAX_RESPONSE_TOKENS", "1024"), 1024)
    ai_rate_limit_requests = parse_positive_int(get_env("AI_RATE_LIMIT_REQUESTS", "20"), 20)
    ai_rate_limit_window_seconds = parse_positive_int(get_env("AI_RATE_LIMIT_WINDOW_SECONDS", "60"), 60)
    ai_retrieval_mode = parse_choice(get_env("AI_RETRIEVAL_MODE", "keyword"), {"keyword", "vector", "hybrid"}, "keyword")
    ai_qa_engine = parse_choice(get_env("AI_QA_ENGINE", "auto"), {"auto", "agent_runtime", "langgraph"}, "auto")
    ai_generation_engine = parse_choice(get_env("AI_GENERATION_ENGINE", "legacy"), {"legacy", "v2"}, "legacy")
    ai_generation_model = get_env("AI_GENERATION_MODEL", "gpt-5.5").strip() or "gpt-5.5"
    document_parser = parse_choice(get_env("DOCUMENT_PARSER", "markitdown"), {"markitdown", "basic"}, "markitdown")
    return ServerSettings(
        content_dir=content_dir,
        meta_dir=meta_dir,
        public_dir=public_dir,
        site_title=site_title,
        max_upload_bytes=max_upload_bytes,
        api_token=api_token,
        auth_username=auth_username,
        auth_password=auth_password,
        users_file=users_file,
        user_data_dir=user_data_dir,
        session_secret=session_secret,
        session_cookie_name=session_cookie_name,
        session_max_age_seconds=session_max_age_seconds,
        session_secure=session_secure,
        cors_origins=cors_origins,
        ai_provider=ai_provider,
        ai_base_url=ai_base_url,
        ai_api_key=ai_api_key,
        ai_model=ai_model,
        ai_embedding_model=ai_embedding_model,
        ai_enabled=ai_enabled,
        ai_external_search=ai_external_search,
        ai_external_search_api_key=ai_external_search_api_key,
        ai_external_search_brave_api_key=ai_external_search_brave_api_key,
        ai_external_search_max_results=ai_external_search_max_results,
        ai_external_search_depth=ai_external_search_depth,
        ai_external_search_auto_parameters=ai_external_search_auto_parameters,
        ai_external_search_topic=ai_external_search_topic,
        ai_external_search_time_range=ai_external_search_time_range,
        ai_external_search_include_raw_content=ai_external_search_include_raw_content,
        ai_max_context_items=ai_max_context_items,
        ai_max_prompt_chars=ai_max_prompt_chars,
        ai_max_message_chars=ai_max_message_chars,
        ai_max_response_tokens=ai_max_response_tokens,
        ai_rate_limit_requests=ai_rate_limit_requests,
        ai_rate_limit_window_seconds=ai_rate_limit_window_seconds,
        ai_retrieval_mode=ai_retrieval_mode,
        ai_qa_engine=ai_qa_engine,
        ai_generation_engine=ai_generation_engine,
        ai_generation_model=ai_generation_model,
        document_parser=document_parser,
    )


def get_env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(f"HTML_LORE_{name}")
    if value is not None:
        return value
    return default


def parse_csv(value: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in value.split(",") if part.strip())


def parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def parse_positive_int(value: str | None, default: int) -> int:
    try:
        parsed = int(str(value or "").strip())
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def parse_choice(value: str | None, choices: set[str], default: str) -> str:
    normalized = str(value or "").strip().lower()
    return normalized if normalized in choices else default


def parse_optional_path(value: str | None, default: Path) -> Path | None:
    if value is None:
        return default
    cleaned = value.strip()
    return Path(cleaned) if cleaned else None


def ensure_user_dirs(settings: ServerSettings) -> None:
    settings.content_dir.mkdir(parents=True, exist_ok=True)
    if settings.meta_dir is not None:
        (settings.meta_dir / "items").mkdir(parents=True, exist_ok=True)
        (settings.meta_dir / "config").mkdir(parents=True, exist_ok=True)
    settings.public_dir.mkdir(parents=True, exist_ok=True)
    if not (settings.public_dir / "manifest.json").exists():
        from html_lore.builder import build_site

        build_site(
            content_dir=settings.content_dir,
            meta_dir=settings.meta_dir,
            output_dir=settings.public_dir,
            site_title=settings.site_title,
        )
