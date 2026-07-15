from __future__ import annotations

import hashlib
import html
import json
import re
import secrets
import shutil
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Protocol
from urllib.parse import urlsplit

from html_lore.builder import build_site
from html_lore.manifest import build_item
from html_lore.metadata import MetadataStore, dump_simple_yaml

from .config import ServerSettings
from .items import ItemContentError, ItemService, ensure_within, metadata_path_for_item

PROJECT_ROOT = Path(__file__).resolve().parents[2]
APP_INDEX = PROJECT_ROOT / "app_static" / "index.html"

SHARE_DURATIONS = {
    "1h": timedelta(hours=1),
    "1d": timedelta(days=1),
    "7d": timedelta(days=7),
    "30d": timedelta(days=30),
    "forever": None,
}

SAFE_SHARE_MODE = "safe"
INTERACTIVE_SHARE_MODE = "interactive"
SHARE_MODES = {SAFE_SHARE_MODE, INTERACTIVE_SHARE_MODE}

DANGEROUS_TAGS = {"iframe", "object", "embed", "form", "input", "button", "textarea", "select", "base"}
SANITIZER_BLOCK_TAGS = DANGEROUS_TAGS | {"script", "meta", "link"}
SANITIZER_SKIP_CONTENT_TAGS = {"script", "iframe", "object", "embed", "form", "textarea", "select", "button"}
DANGEROUS_EXTENSIONS = {".exe", ".dmg", ".apk", ".msi", ".bat", ".cmd", ".sh", ".ps1", ".scr", ".jar"}
SAFE_TOGGLE_HANDLER = re.compile(r"^toggleGroup\(\s*['\"]([A-Za-z][A-Za-z0-9_-]{0,63})['\"]\s*\)\s*;?\s*$")
SAFE_FRAGMENT_HREF = re.compile(r"^#[A-Za-z][A-Za-z0-9_.:-]{0,127}$")
CHART_SCRIPT_PATTERN = re.compile(r"\bchart(?:\.umd)?(?:\.min)?\.js\b|new\s+Chart\s*\(|<canvas\b", re.I)
CSS_UNSAFE_PATTERNS = [
    ("css-import", re.compile(r"@import\b", re.I)),
    ("css-expression", re.compile(r"\bexpression\s*\(", re.I)),
    ("css-behavior", re.compile(r"(?<![-\w])behavior\s*:", re.I)),
    ("css-binding", re.compile(r"-moz-binding\s*:", re.I)),
    ("css-dangerous-scheme", re.compile(r"(?:javascript|vbscript|file|data\s*:\s*text/html)\s*:", re.I)),
]
CSS_URL_PATTERN = re.compile(r"\burl\s*\(\s*(['\"]?)(.*?)\1\s*\)", re.I | re.S)
SECRET_PATTERNS = [
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\b[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\b(?:api[_-]?key|secret|token|password|passwd|pwd)\b\s*[:=]\s*['\"]?[^'\"\s<]{8,}", re.I),
    re.compile(r"\b(?:sk|pk|rk|ghp|github_pat|xox[baprs])-[-A-Za-z0-9_]{16,}\b", re.I),
    re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    re.compile(r"\b(?:mongodb|postgres|postgresql|mysql|redis)://[^\s<]+", re.I),
]
LOCAL_PATTERNS = [
    re.compile(r"\b(?:10|127|172\.(?:1[6-9]|2\d|3[0-1])|192\.168)\.\d{1,3}\.\d{1,3}\b"),
    re.compile(r"\bfile://[^\s<]+", re.I),
    re.compile(r"(?:^|[\s\"'>])(?:/[A-Za-z0-9_.-]+){2,}"),
    re.compile(r"[A-Za-z]:\\(?:[^\\/:*?\"<>|\r\n]+\\?)+"),
]


@dataclass(frozen=True)
class ShareCreateResult:
    share: dict[str, Any]
    token: str
    url_path: str


class ShareRepairer(Protocol):
    """Extension point for a future offline or AI-assisted safety-copy repairer."""

    name: str

    def repair(self, content: str) -> str: ...


class DeterministicShareRepairer:
    name = "deterministic"

    def repair(self, content: str) -> str:
        return build_safe_share_copy(content)


class ShareService:
    def __init__(
        self,
        settings: ServerSettings,
        root_settings: ServerSettings | None = None,
        repairer: ShareRepairer | None = None,
    ) -> None:
        self.settings = settings
        self.root_settings = root_settings or settings
        self.item_service = ItemService(settings)
        self.repairer = repairer or DeterministicShareRepairer()

    def list_shares(self) -> list[dict[str, Any]]:
        data = self._read_store()
        self._ensure_static_share_shells(data)
        return [public_share(record) for record in data.get("shares", []) if not record.get("deleted")]

    def create_share(
        self,
        item_id: str,
        duration: str,
        mode: str = SAFE_SHARE_MODE,
        confirm_private_references: bool = False,
    ) -> ShareCreateResult:
        if duration not in SHARE_DURATIONS:
            raise ShareError("Invalid share duration.")
        mode = normalize_share_mode(mode)
        item = self.item_service.get_item(item_id)
        if not item:
            raise ShareError("Item not found.")
        if bool(item.get("archived")):
            raise ShareError("Archived items cannot be shared.")
        try:
            content = self.item_service.read_item_content(item_id)
        except ItemContentError as exc:
            raise ShareError(str(exc)) from exc

        content_item_id = item_id
        repair: dict[str, Any] = {}
        if mode == SAFE_SHARE_MODE:
            original_scan = scan_share_content(content)
            if original_scan["shareable"]:
                scan = original_scan
            else:
                repaired = self._create_safe_share_copy(item, content, original_scan)
                content_item_id = repaired["item_id"]
                scan = repaired["safety"]
                repair = repaired["repair"]
        else:
            if not self.settings.share_interactive_enabled:
                raise ShareError("Interactive sharing is disabled by this deployment.")
            scan = scan_interactive_share_content(content)
            if not scan["shareable"]:
                raise ShareSafetyError(scan)
            if scan.get("requires_confirmation") and not confirm_private_references:
                raise ShareSafetyConfirmationError(scan)

        token = secrets.token_urlsafe(32)
        token_hash = hash_token(token)
        url_path = f"/share/{token}"
        now = utc_now()
        data = self._read_store()
        existing = active_share_for_item(data, item_id)
        if existing:
            existing["revoked"] = True
            existing["updated_at"] = now
            self._delete_static_share_shell(str(existing.get("url_path") or ""))

        record = {
            "id": f"share_{secrets.token_urlsafe(10)}",
            "token_hash": token_hash,
            "url_path": url_path,
            "item_id": item_id,
            "content_item_id": content_item_id,
            "mode": mode,
            "duration": duration,
            "created_at": now,
            "updated_at": now,
            "expires_at": expires_at_for(duration, now),
            "revoked": False,
            "access_count": 0,
            "last_accessed_at": "",
            "safety": scan,
            "repair": repair,
        }
        data.setdefault("shares", []).append(record)
        self._write_store(data)
        self._index_token(token_hash)
        self._write_static_share_shell(token)
        return ShareCreateResult(share=public_share(record), token=token, url_path=url_path)

    def update_share(self, share_id: str, values: dict[str, Any]) -> dict[str, Any]:
        data = self._read_store()
        record = find_share(data, share_id)
        if not record:
            raise ShareError("Share not found.")
        is_revoking = values.get("revoked") is True
        if "revoked" in values:
            if not isinstance(values["revoked"], bool):
                raise ShareError("revoked must be a boolean.")
            if values["revoked"] is False:
                raise ShareError("Revoked shares cannot be reactivated.")
        if not is_share_active(record) and not is_revoking:
            raise ShareError("Inactive shares cannot be updated.")
        if "duration" in values:
            duration = str(values.get("duration") or "")
            if duration not in SHARE_DURATIONS:
                raise ShareError("Invalid share duration.")
            record["duration"] = duration
            record["expires_at"] = expires_at_for(duration, utc_now())
        if "revoked" in values:
            record["revoked"] = values["revoked"]
            if values["revoked"] is True:
                self._delete_static_share_shell(str(record.get("url_path") or ""))
        record["updated_at"] = utc_now()
        self._write_store(data)
        return public_share(record)

    def revoke_share(self, share_id: str) -> dict[str, Any]:
        return self.update_share(share_id, {"revoked": True})

    def active_share_for_item(self, item_id: str) -> dict[str, Any] | None:
        return active_share_for_item(self._read_store(), item_id)

    def public_read_by_token(self, token: str) -> dict[str, Any]:
        token_hash = hash_token(token)
        record = self._find_by_token_hash(token_hash)
        if not record or not is_share_active(record):
            raise ShareError("Share not found.")
        self._write_static_share_shell(token)
        item = self.item_service.get_item(str(record.get("item_id") or ""))
        if not item:
            raise ShareError("Share not found.")
        if bool(item.get("archived")):
            raise ShareError("Share not found.")
        content_item_id = str(record.get("content_item_id") or record["item_id"])
        mode = share_mode_for_record(record)
        if mode == INTERACTIVE_SHARE_MODE and not self.settings.share_interactive_enabled:
            raise ShareError("Share not found.")
        try:
            content = self.item_service.read_item_content(content_item_id)
        except ItemContentError as exc:
            raise ShareError("Share not found.") from exc
        scan = scan_for_share_mode(content, mode)
        if not scan["shareable"]:
            record["revoked"] = True
            record["updated_at"] = utc_now()
            record["safety"] = scan
            self._update_record(record)
            raise ShareError("Share not found.")
        rendered = sanitize_shared_html(content) if mode == SAFE_SHARE_MODE else {"body_html": content, "styles": ""}
        record["access_count"] = int(record.get("access_count") or 0) + 1
        record["last_accessed_at"] = utc_now()
        self._update_record(record)
        return {
            "share": public_share_read(record),
            "item": {
                "title": item.get("title") or "Untitled",
                "summary": item.get("summary") or "",
                "updated": item.get("updated") or "",
            },
            "html": rendered["body_html"],
            "styles": rendered["styles"],
        }

    def _create_safe_share_copy(self, item: dict[str, Any], content: str, original_scan: dict[str, Any]) -> dict[str, Any]:
        repaired_content = self.repairer.repair(content)
        repaired_scan = scan_share_content(repaired_content)
        if not repaired_scan["shareable"]:
            raise ShareSafetyError(
                {
                    "shareable": False,
                    "reasons": sorted(set([*original_scan.get("reasons", []), *repaired_scan.get("reasons", []), "safe-copy-failed"])),
                },
            )

        source_path = Path(str(item.get("id") or ""))
        if not source_path.name:
            raise ShareError("Item content path is invalid.")
        relative_path = next_safe_share_copy_path(self.settings.content_dir, source_path)
        content_path = self.settings.content_dir / relative_path
        ensure_within(content_path, self.settings.content_dir)
        content_path.parent.mkdir(parents=True, exist_ok=True)
        content_path.write_text(repaired_content, encoding="utf-8")

        now = utc_now()
        source_metadata = MetadataStore.load(self.settings.meta_dir).for_item(str(item.get("id") or ""))
        metadata = {
            **source_metadata,
            "id": relative_path.as_posix(),
            "title": f"{str(item.get('title') or 'Untitled')} - Safe share copy",
            "summary": str(item.get("summary") or ""),
            "source_type": "share-safety-copy",
            "status": "ready",
            "favorite": False,
            "archived": False,
            "pinned": False,
            "open_mode": "iframe",
            "created": now,
            "updated": now,
            "share_safety": {
                "source_item_id": str(item.get("id") or ""),
                "repair_engine": self.repairer.name,
                "original_reasons": list(original_scan.get("reasons") or []),
            },
        }
        metadata.pop("path", None)
        if self.settings.meta_dir is not None:
            metadata_path = metadata_path_for_item(self.settings.meta_dir, relative_path.as_posix())
            if metadata_path is not None:
                ensure_within(metadata_path, self.settings.meta_dir)
                metadata_path.parent.mkdir(parents=True, exist_ok=True)
                metadata_path.write_text(dump_simple_yaml(metadata), encoding="utf-8")
        copied_item = build_item(content_path, self.settings.content_dir, MetadataStore.load(self.settings.meta_dir))
        build_site(
            content_dir=self.settings.content_dir,
            meta_dir=self.settings.meta_dir,
            output_dir=self.settings.public_dir,
            site_title=self.settings.site_title,
        )
        return {
            "item_id": copied_item["id"],
            "safety": repaired_scan,
            "repair": {
                "created": True,
                "engine": self.repairer.name,
                "source_item_id": str(item.get("id") or ""),
                "copy_item_id": copied_item["id"],
                "original_reasons": list(original_scan.get("reasons") or []),
            },
        }

    def _find_by_token_hash(self, token_hash: str) -> dict[str, Any] | None:
        for record in self._read_store().get("shares", []):
            if secrets.compare_digest(str(record.get("token_hash") or ""), token_hash):
                return record
        return None

    def _update_record(self, record: dict[str, Any]) -> None:
        data = self._read_store()
        existing = find_share(data, str(record.get("id") or ""))
        if existing:
            existing.update(record)
            self._write_store(data)

    def _read_store(self) -> dict[str, Any]:
        path = share_store_path(self.settings)
        if not path.exists():
            return {"version": 1, "shares": []}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"version": 1, "shares": []}
        if not isinstance(data, dict):
            return {"version": 1, "shares": []}
        data.setdefault("version", 1)
        data.setdefault("shares", [])
        return data

    def _write_store(self, data: dict[str, Any]) -> None:
        path = share_store_path(self.settings)
        ensure_within(path, self.settings.meta_dir or self.settings.public_dir)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def _index_token(self, token_hash: str) -> None:
        root = share_index_path(self.root_settings)
        root.parent.mkdir(parents=True, exist_ok=True)
        try:
            data = json.loads(root.read_text(encoding="utf-8")) if root.exists() else {"version": 1, "tokens": {}}
        except json.JSONDecodeError:
            data = {"version": 1, "tokens": {}}
        data.setdefault("tokens", {})[token_hash] = data_id_for_settings(self.root_settings, self.settings)
        root.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def _write_static_share_shell(self, token: str) -> None:
        index = self.settings.public_dir / "index.html"
        if not index.exists():
            index = APP_INDEX
        if not index.exists():
            return
        target = (self.settings.public_dir / "share" / token / "index.html").resolve()
        ensure_within(target, self.settings.public_dir)
        shell = index.read_text(encoding="utf-8")
        if "<base " not in shell:
            shell = shell.replace("<head>", '<head>\n  <base href="/">', 1)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(shell, encoding="utf-8")

    def _ensure_static_share_shells(self, data: dict[str, Any]) -> None:
        for record in data.get("shares", []):
            if record.get("deleted") or not is_share_active(record):
                continue
            token = token_from_url_path(str(record.get("url_path") or ""))
            if token:
                self._write_static_share_shell(token)

    def _delete_static_share_shell(self, url_path: str) -> None:
        token = token_from_url_path(url_path)
        if not token:
            return
        share_dir = (self.settings.public_dir / "share" / token).resolve()
        ensure_within(share_dir, self.settings.public_dir)
        if share_dir.exists():
            shutil.rmtree(share_dir)


class ShareError(ValueError):
    pass


class ShareSafetyError(ShareError):
    def __init__(self, scan: dict[str, Any]) -> None:
        super().__init__("Item failed share safety checks.")
        self.scan = scan


class ShareSafetyConfirmationError(ShareSafetyError):
    def __init__(self, scan: dict[str, Any]) -> None:
        super().__init__(scan)
        self.args = ("Interactive share requires confirmation for private or local references.",)


def public_share(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": record.get("id"),
        "item_id": record.get("item_id"),
        "content_item_id": record.get("content_item_id") or record.get("item_id"),
        "mode": share_mode_for_record(record),
        "duration": record.get("duration"),
        "created_at": record.get("created_at"),
        "updated_at": record.get("updated_at"),
        "expires_at": record.get("expires_at"),
        "url_path": record.get("url_path") or "",
        "revoked": bool(record.get("revoked")),
        "active": is_share_active(record),
        "access_count": int(record.get("access_count") or 0),
        "last_accessed_at": record.get("last_accessed_at") or "",
        "safety": record.get("safety") or {"shareable": True, "reasons": []},
        "repair": record.get("repair") or {},
    }


def public_share_read(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "active": is_share_active(record),
        "expires_at": record.get("expires_at") or "",
        "mode": share_mode_for_record(record),
    }


def find_share(data: dict[str, Any], share_id: str) -> dict[str, Any] | None:
    for record in data.get("shares", []):
        if record.get("id") == share_id:
            return record
    return None


def active_share_for_item(data: dict[str, Any], item_id: str) -> dict[str, Any] | None:
    for record in data.get("shares", []):
        if record.get("item_id") == item_id and is_share_active(record):
            return record
    return None


def share_store_path(settings: ServerSettings) -> Path:
    base = settings.meta_dir or settings.public_dir
    return base / "config" / "shares.json"


def share_index_path(settings: ServerSettings) -> Path:
    base = settings.meta_dir or settings.public_dir
    return base / "config" / "share-index.json"


def data_id_for_settings(root: ServerSettings, settings: ServerSettings) -> str:
    if root.user_data_dir:
        try:
            relative = settings.content_dir.relative_to(root.user_data_dir)
            return relative.parts[0] if relative.parts else "default"
        except ValueError:
            return "default"
    return "default"


def token_from_url_path(url_path: str) -> str:
    parts = [part for part in url_path.split("/") if part]
    if len(parts) == 2 and parts[0] == "share":
        return parts[1]
    return ""


def settings_for_share_token(root: ServerSettings, token: str) -> ServerSettings:
    token_hash = hash_token(token)
    index_path = share_index_path(root)
    if index_path.exists():
        try:
            data = json.loads(index_path.read_text(encoding="utf-8"))
            data_id = data.get("tokens", {}).get(token_hash)
            if data_id:
                return root.for_user(str(data_id))
        except json.JSONDecodeError:
            pass
    return root


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_datetime(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def expires_at_for(duration: str, now_value: str) -> str:
    delta = SHARE_DURATIONS[duration]
    if delta is None:
        return ""
    now = parse_datetime(now_value) or datetime.now(timezone.utc)
    return (now + delta).isoformat()


def is_share_active(record: dict[str, Any]) -> bool:
    if bool(record.get("revoked")):
        return False
    expires_at = parse_datetime(str(record.get("expires_at") or ""))
    if not expires_at:
        return True
    return expires_at >= datetime.now(timezone.utc)


def normalize_share_mode(value: Any) -> str:
    mode = str(value or SAFE_SHARE_MODE).strip().lower()
    if mode not in SHARE_MODES:
        raise ShareError("Invalid share mode.")
    return mode


def share_mode_for_record(record: dict[str, Any]) -> str:
    return str(record.get("mode") or SAFE_SHARE_MODE) if str(record.get("mode") or SAFE_SHARE_MODE) in SHARE_MODES else SAFE_SHARE_MODE


def scan_for_share_mode(content: str, mode: str) -> dict[str, Any]:
    normalized = normalize_share_mode(mode)
    return scan_share_content(content) if normalized == SAFE_SHARE_MODE else scan_interactive_share_content(content)


def scan_share_content(content: str) -> dict[str, Any]:
    scanner = SafetyScanner()
    scanner.feed(content)
    reasons = list(scanner.reasons)
    if scanner.saw_script and not scanner.only_safe_toggle_script():
        reasons.append("blocked-tag:script")
    if scanner.requires_static_chart:
        reasons.append("requires-static-export:chart")
    for reason in unsafe_css_reasons("\n".join(scanner.style_parts)):
        reasons.append(reason)
    text = html.unescape(strip_tags(content))
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            reasons.append("sensitive-secret")
            break
    for pattern in LOCAL_PATTERNS:
        if pattern.search(text):
            reasons.append("private-local-reference")
            break
    return {"shareable": not reasons, "reasons": sorted(set(reasons))}


def scan_interactive_share_content(content: str) -> dict[str, Any]:
    """Keep trusted interactive shares permissive while retaining hard isolation gates."""
    scanner = InteractiveSafetyScanner()
    scanner.feed(content)
    reasons = list(scanner.reasons)
    for reason in unsafe_css_reasons("\n".join(scanner.style_parts)):
        if reason not in {"css-import", "css-url"}:
            reasons.append(reason)
    text = html.unescape(strip_tags(content))
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            reasons.append("sensitive-secret")
            break
    warnings: list[str] = []
    for pattern in LOCAL_PATTERNS:
        if pattern.search(content):
            warnings.append("private-local-reference")
            break
    return {
        "shareable": not reasons,
        "reasons": sorted(set(reasons)),
        "warnings": sorted(set(warnings)),
        "requires_confirmation": bool(warnings),
    }


class InteractiveSafetyScanner(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.reasons: list[str] = []
        self.style_stack = 0
        self.style_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        name = tag.lower()
        if name in {"base", "object", "embed"}:
            self.reasons.append(f"blocked-tag:{name}")
        if name == "meta" and is_meta_refresh(attrs):
            self.reasons.append("meta-refresh")
        if name == "style":
            self.style_stack += 1
        for attr_name, attr_value in attrs:
            attr = attr_name.lower()
            if attr not in {"href", "src", "action", "formaction"}:
                continue
            reason = unsafe_url_reason((attr_value or "").strip())
            if reason in {"dangerous-url", "dangerous-download"}:
                self.reasons.append(reason)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "style" and self.style_stack > 0:
            self.style_stack -= 1

    def handle_data(self, data: str) -> None:
        if self.style_stack > 0:
            self.style_parts.append(data)


def build_safe_share_copy(content: str) -> str:
    """Create a static, auditable copy without sending third-party source to a model."""
    redacted = redact_share_sensitive_values(content)
    prepared = replace_removed_interactive_components(redacted)
    rendered = sanitize_shared_html(prepared)
    body = redact_share_private_references(rendered["body_html"])
    styles = rendered["styles"]
    if not strip_tags(body).strip():
        body = '<div class="html-lore-share-notice">No static content could be preserved. The original interactive components were removed for safe public sharing.</div>'
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <style>
    html {{ min-height: 100%; }}
    body {{ margin: 0; overflow-wrap: anywhere; }}
    .html-lore-share-notice {{ margin: 1rem; padding: .75rem 1rem; border: 1px solid #d7b66b; background: #fff8df; color: #5f4612; font: 14px/1.5 system-ui, sans-serif; }}
    img, video, svg {{ max-width: 100%; height: auto; }}
  </style>
  {styles}
</head>
<body>
  {body}
</body>
</html>"""


def redact_share_sensitive_values(content: str) -> str:
    value = content
    for pattern in SECRET_PATTERNS:
        value = pattern.sub("[redacted sensitive value]", value)
    return value


def redact_share_private_references(content: str) -> str:
    value = content
    for pattern in LOCAL_PATTERNS:
        value = pattern.sub("[removed private reference]", value)
    return value


def replace_removed_interactive_components(content: str) -> str:
    notice = '<div class="html-lore-share-notice">Interactive content was removed from this safety copy.</div>'
    value = re.sub(r"<canvas\b[^>]*>.*?</canvas\s*>", notice, content, flags=re.I | re.S)
    value = re.sub(r"<canvas\b[^>]*/?\s*>", notice, value, flags=re.I)
    value = re.sub(r"<(?:iframe|object|embed)\b[^>]*>.*?</(?:iframe|object)\s*>", notice, value, flags=re.I | re.S)
    value = re.sub(r"<(?:iframe|object|embed)\b[^>]*/?\s*>", notice, value, flags=re.I)
    value = re.sub(r"<form\b[^>]*>", '<div class="html-lore-share-form">', value, flags=re.I)
    value = re.sub(r"</form\s*>", "</div>", value, flags=re.I)
    return value


def next_safe_share_copy_path(content_dir: Path, source_path: Path) -> Path:
    suffix = source_path.suffix or ".html"
    stem = source_path.stem or "shared-note"
    candidate = source_path.with_name(f"{stem}--safe-share{suffix}")
    index = 2
    while (content_dir / candidate).exists():
        candidate = source_path.with_name(f"{stem}--safe-share-{index}{suffix}")
        index += 1
    return candidate


class SafetyScanner(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.reasons: list[str] = []
        self.saw_script = False
        self.requires_static_chart = False
        self.script_stack = 0
        self.script_parts: list[str] = []
        self.style_stack = 0
        self.style_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        name = tag.lower()
        if name == "script":
            self.saw_script = True
            values = {attr.lower(): (value or "").strip() for attr, value in attrs}
            if CHART_SCRIPT_PATTERN.search(values.get("src", "")):
                self.requires_static_chart = True
            self.script_stack += 1
            return
        if name == "style":
            self.style_stack += 1
            return
        if name == "canvas":
            self.requires_static_chart = True
        if name in DANGEROUS_TAGS:
            self.reasons.append(f"blocked-tag:{name}")
        if name == "meta" and is_meta_refresh(attrs):
            self.reasons.append("meta-refresh")
        for attr_name, attr_value in attrs:
            attr = attr_name.lower()
            value = (attr_value or "").strip()
            if attr.startswith("on") and not (attr == "onclick" and safe_toggle_target(value)):
                self.reasons.append("inline-event-handler")
            if attr in {"href", "src", "action", "formaction"}:
                reason = unsafe_url_reason(value)
                if reason and reason != "external-link":
                    self.reasons.append(reason)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "script" and self.script_stack > 0:
            self.script_stack -= 1
        if tag.lower() == "style" and self.style_stack > 0:
            self.style_stack -= 1

    def handle_data(self, data: str) -> None:
        if self.script_stack > 0:
            self.script_parts.append(data)
            if CHART_SCRIPT_PATTERN.search(data):
                self.requires_static_chart = True
        if self.style_stack > 0:
            self.style_parts.append(data)

    def only_safe_toggle_script(self) -> bool:
        return is_safe_toggle_script("\n".join(self.script_parts))


def unsafe_url_reason(value: str) -> str:
    if not value:
        return ""
    lowered = value.strip().lower()
    if lowered.startswith(("javascript:", "vbscript:", "data:text/html")):
        return "dangerous-url"
    parsed = urlsplit(value)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return "external-link"
    suffix = Path(parsed.path).suffix.lower()
    if suffix in DANGEROUS_EXTENSIONS:
        return "dangerous-download"
    return ""


def is_meta_refresh(attrs: list[tuple[str, str | None]]) -> bool:
    values = {name.lower(): (value or "").strip().lower() for name, value in attrs}
    return values.get("http-equiv") == "refresh"


def is_safe_fragment_href(value: str) -> bool:
    return bool(SAFE_FRAGMENT_HREF.fullmatch(value.strip()))


def unsafe_css_reasons(value: str) -> list[str]:
    if not value:
        return []
    reasons = [reason for reason, pattern in CSS_UNSAFE_PATTERNS if pattern.search(value)]
    for raw_url in CSS_URL_PATTERN.findall(value):
        url_value = raw_url[1].strip()
        if is_safe_css_data_image(url_value):
            continue
        parsed = urlsplit(url_value)
        if parsed.scheme or url_value.startswith(("//", "/", "\\")):
            reasons.append("css-url")
    return sorted(set(reasons))


def is_safe_css_data_image(value: str) -> bool:
    lowered = value.strip().lower()
    if not lowered.startswith("data:image/svg+xml"):
        return False
    if ";base64" in lowered:
        return False
    decoded = html.unescape(value)
    decoded = re.sub(r"%([0-9a-fA-F]{2})", lambda match: chr(int(match.group(1), 16)), decoded)
    lowered_decoded = decoded.lower()
    return not re.search(r"<\s*script\b|on[a-z]+\s*=|javascript\s*:|data\s*:\s*text/html", lowered_decoded)


def is_safe_image_src(value: str) -> bool:
    return is_safe_css_data_image(value)


def safe_toggle_target(value: str) -> str:
    match = SAFE_TOGGLE_HANDLER.fullmatch(value.strip())
    return match.group(1) if match else ""


def is_safe_toggle_script(value: str) -> bool:
    compact = re.sub(r"\s+", "", value)
    return bool(
        re.fullmatch(
            r"functiontoggleGroup\(id\)\{constel=document\.getElementById\(id\);el\.classList\.toggle\('open'\);\}"
            r"(//Openfirstgroupbydefault\(alreadysetviaclass\))?"
            r"(//Addkeyboardshortcut:press'\?'toexpandall)?"
            r"document\.addEventListener\('keydown',e=>\{"
            r"if\(e\.key==='\?'\)\{document\.querySelectorAll\('\.qgroup'\)\.forEach\(g=>g\.classList\.add\('open'\)\);\}"
            r"if\(e\.key==='/'\)\{document\.querySelectorAll\('\.qgroup'\)\.forEach\(g=>g\.classList\.remove\('open'\)\);document\.getElementById\('g1'\)\.classList\.add\('open'\);\}"
            r"\}\);",
            compact,
        ),
    )


def sanitize_shared_html(content: str) -> dict[str, str]:
    sanitizer = ShareSanitizer()
    sanitizer.feed(content)
    return sanitizer.output()


class ShareSanitizer(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.head_parts: list[str] = []
        self.body_parts: list[str] = []
        self.skip_stack: list[str] = []
        self.style_stack = 0
        self.style_parts: list[str] = []
        self.in_head = False
        self.in_body = False

    @property
    def active_parts(self) -> list[str]:
        if self.in_head:
            return self.head_parts
        if self.in_body:
            return self.body_parts
        return self.parts

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        name = tag.lower()
        if name == "html":
            return
        if name == "head":
            self.in_head = True
            return
        if name == "body":
            self.in_body = True
            return
        if name in SANITIZER_BLOCK_TAGS or (name == "meta" and is_meta_refresh(attrs)):
            if name in SANITIZER_SKIP_CONTENT_TAGS:
                self.skip_stack.append(name)
            return
        if self.skip_stack:
            return
        if name == "style":
            self.style_stack += 1
            self.style_parts = []
            return
        clean_attrs: list[str] = []
        for attr_name, attr_value in attrs:
            attr = attr_name.lower()
            value = attr_value or ""
            if attr == "onclick":
                target = safe_toggle_target(value)
                if target:
                    clean_attrs.append(f'data-share-toggle="{html.escape(target, quote=True)}"')
                continue
            if attr.startswith("on"):
                continue
            if name == "a" and attr == "href":
                if is_safe_fragment_href(value):
                    clean_attrs.append(f'href="{html.escape(value.strip(), quote=True)}"')
                continue
            if attr == "src":
                if name == "img" and is_safe_image_src(value):
                    clean_attrs.append(f'src="{html.escape(value, quote=True)}"')
                continue
            if attr in {"href", "src", "action", "formaction"}:
                if unsafe_url_reason(value):
                    continue
            clean_attrs.append(f'{html.escape(attr, quote=True)}="{html.escape(value, quote=True)}"')
        attr_text = f" {' '.join(clean_attrs)}" if clean_attrs else ""
        self.active_parts.append(f"<{html.escape(name)}{attr_text}>")

    def handle_endtag(self, tag: str) -> None:
        name = tag.lower()
        if name == "html":
            return
        if name == "head":
            self.in_head = False
            return
        if name == "body":
            self.in_body = False
            return
        if name == "style" and self.style_stack > 0:
            self.style_stack -= 1
            if self.style_stack == 0:
                css = "".join(self.style_parts)
                if not unsafe_css_reasons(css):
                    self.head_parts.append(f"<style>{css}</style>")
                self.style_parts = []
            return
        if self.skip_stack:
            if self.skip_stack[-1] == name:
                self.skip_stack.pop()
            return
        if name not in DANGEROUS_TAGS:
            self.active_parts.append(f"</{html.escape(name)}>")

    def handle_data(self, data: str) -> None:
        if self.style_stack > 0:
            self.style_parts.append(data)
            return
        if not self.skip_stack:
            self.active_parts.append(html.escape(data))

    def handle_entityref(self, name: str) -> None:
        if not self.skip_stack:
            self.active_parts.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        if not self.skip_stack:
            self.active_parts.append(f"&#{name};")

    def output(self) -> dict[str, str]:
        body = "".join(self.body_parts).strip()
        if not body:
            body = "".join(self.parts).strip()
        return {
            "body_html": body,
            "styles": "".join(self.head_parts).strip(),
        }


def strip_tags(content: str) -> str:
    stripper = TextStripper()
    stripper.feed(content)
    return " ".join(stripper.parts)


class TextStripper(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)
