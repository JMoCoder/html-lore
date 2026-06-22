from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from html_lore.builder import build_site
from html_lore.manifest import build_item
from html_lore.metadata import MetadataStore, dump_simple_yaml
from html_lore.server.config import ServerSettings
from html_lore.server.uploads import ensure_within

from .schemas import CreateNoteProposal
from .tools.html_safety import scan_html_safety


class WriteGatewayError(ValueError):
    pass


@dataclass(frozen=True)
class WriteGatewayResult:
    item_id: str = ""
    title: str = ""
    audit_summary: str = ""
    metadata_path: str = ""
    content_path: str = ""


class WriteGateway:
    name = "WriteGateway.v2"

    def __init__(self, settings: ServerSettings, *, build_fn: Callable[..., object] = build_site) -> None:
        self.settings = settings
        self.build_fn = build_fn

    def write(self, proposal: CreateNoteProposal) -> WriteGatewayResult:
        if not proposal.html.strip():
            raise WriteGatewayError("CreateNoteProposal.html is required.")
        if not proposal.title.strip():
            raise WriteGatewayError("CreateNoteProposal.title is required.")
        if len(proposal.html.encode("utf-8")) > self.settings.max_upload_bytes:
            raise WriteGatewayError("Generated HTML exceeds the configured size limit.")
        safety = scan_html_safety(proposal.html)
        if not safety["ok"]:
            reasons = ", ".join(safety["reasons"])
            raise WriteGatewayError(f"Generated HTML failed safety checks: {reasons}")

        now = datetime.now(timezone.utc)
        relative_path = next_generated_path(self.settings.content_dir, proposal.title, now)
        content_path = self.settings.content_dir / relative_path
        metadata_path = self.metadata_path(relative_path)
        wrote_html = False
        try:
            ensure_within(content_path, self.settings.content_dir)
            content_path.parent.mkdir(parents=True, exist_ok=True)
            content_path.write_text(proposal.html, encoding="utf-8")
            wrote_html = True

            metadata = self.build_metadata(proposal, item_id=relative_path.as_posix(), now=now)
            if metadata_path is not None:
                ensure_within(metadata_path, self.settings.meta_dir)  # type: ignore[arg-type]
                metadata_path.parent.mkdir(parents=True, exist_ok=True)
                metadata_path.write_text(dump_simple_yaml(metadata), encoding="utf-8")

            item = build_item(content_path, self.settings.content_dir, MetadataStore.load(self.settings.meta_dir))
            self.build_fn(
                content_dir=self.settings.content_dir,
                meta_dir=self.settings.meta_dir,
                output_dir=self.settings.public_dir,
                site_title=self.settings.site_title,
            )
        except Exception as exc:
            if wrote_html and content_path.exists():
                content_path.unlink()
            if metadata_path is not None and metadata_path.exists():
                metadata_path.unlink()
            raise WriteGatewayError(str(exc)) from exc

        return WriteGatewayResult(
            item_id=str(item.get("id") or relative_path.as_posix()),
            title=proposal.title,
            audit_summary="Generated HTML written and site manifest rebuilt.",
            metadata_path=metadata_path.as_posix() if metadata_path else "",
            content_path=content_path.as_posix(),
        )

    def metadata_path(self, relative_path: Path) -> Path | None:
        if self.settings.meta_dir is None:
            return None
        return self.settings.meta_dir / "items" / relative_path.with_suffix(".yml")

    def build_metadata(self, proposal: CreateNoteProposal, *, item_id: str, now: datetime) -> dict[str, object]:
        metadata = proposal.metadata
        return {
            "id": item_id,
            "title": metadata.title or proposal.title,
            "summary": metadata.summary,
            "source_type": metadata.source_type or "ai_generated",
            "collection": metadata.collection or proposal.target_collection or "inbox",
            "tags": metadata.tags or proposal.tags,
            "status": "ready",
            "favorite": False,
            "archived": False,
            "pinned": False,
            "open_mode": "iframe",
            "created": now.isoformat(),
            "updated": now.isoformat(),
            "agent": {
                "generated": True,
                "run_id": proposal.generation_trace_id,
                "graph": "HtmlGenerationV2.alpha",
            },
        }


def next_generated_path(content_dir: Path, title: str, now: datetime) -> Path:
    relative_dir = Path("generated") / now.strftime("%Y") / now.strftime("%m")
    stem = slugify(title)
    candidate = relative_dir / f"{stem}.html"
    index = 2
    while (content_dir / candidate).exists():
        candidate = relative_dir / f"{stem}-{index}.html"
        index += 1
    return candidate


def slugify(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-._").lower()
    return normalized[:72].strip("-._") or "generated-note"
