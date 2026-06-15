from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from typing import Any

from html_lore.server.items import ItemService, normalize_query


VALID_SOURCE_MODES = {"local_only", "local_plus_external"}
DEFAULT_MAX_CONTEXT_ITEMS = 50


class AIContextError(ValueError):
    pass


@dataclass(frozen=True)
class ResolvedContext:
    source_mode: str
    scope: str
    requested: dict[str, Any]
    items: list[dict[str, Any]]
    created_at: str

    def as_dict(self) -> dict[str, Any]:
        payload = {
            "source_mode": self.source_mode,
            "scope": self.scope,
            "requested": self.requested,
            "item_ids": [str(item.get("id") or "") for item in self.items],
            "item_count": len(self.items),
            "items": [context_item(item) for item in self.items],
            "created_at": self.created_at,
        }
        payload["context_key"] = context_key(payload)
        return payload


class ContextResolver:
    def __init__(self, item_service: ItemService, *, max_context_items: int = DEFAULT_MAX_CONTEXT_ITEMS) -> None:
        self.item_service = item_service
        self.max_context_items = max(1, int(max_context_items or DEFAULT_MAX_CONTEXT_ITEMS))

    def resolve(self, values: dict[str, Any]) -> dict[str, Any]:
        source_mode = normalize_source_mode(values.get("source_mode", "local_only"))
        context = values.get("context") if isinstance(values.get("context"), dict) else values
        include_archived = bool(context.get("include_archived", False))
        manual_ids = normalize_id_list(context.get("manual_item_ids") or context.get("manualItemIds") or [])
        item_id = str(context.get("item_id") or context.get("itemId") or "").strip()

        if manual_ids:
            items = self._items_by_ids(manual_ids, include_archived=include_archived)
            scope = "manual"
            requested = {"manual_item_ids": manual_ids, "include_archived": include_archived}
        elif item_id:
            items = self._items_by_ids([item_id], include_archived=include_archived)
            scope = "reader"
            requested = {"item_id": item_id, "include_archived": include_archived}
        else:
            scope = normalize_scope(context)
            query = normalize_query(
                q=str(context.get("q") or context.get("query") or ""),
                library=str(context.get("library") or ("all" if scope == "global" else "")),
                collection=str(context.get("collection") or ""),
                tags=context.get("tags") or [],
                tag_match=str(context.get("tag_match") or context.get("tagMatch") or "any"),
                favorite=parse_optional_bool(context.get("favorite")),
                archived=True if include_archived else False,
                sort=str(context.get("sort") or "newest"),
                limit=parse_optional_int(context.get("limit")),
            )
            items = self.item_service.list_items(query)
            requested = {
                "scope": scope,
                "q": query.q,
                "library": query.library,
                "collection": query.collection,
                "tags": list(query.tags),
                "tag_match": query.tag_match,
                "favorite": query.favorite,
                "include_archived": include_archived,
                "sort": query.sort,
                "limit": query.limit,
            }
        self._validate_item_limit(items)

        return ResolvedContext(
            source_mode=source_mode,
            scope=scope,
            requested=requested,
            items=items,
            created_at=utc_now(),
        ).as_dict()

    def _validate_item_limit(self, items: list[dict[str, Any]]) -> None:
        if len(items) <= self.max_context_items:
            return
        raise AIContextError(
            f"AI context contains {len(items)} notes, exceeding the limit of {self.max_context_items}. "
            "Narrow the context or select fewer notes.",
        )

    def _items_by_ids(self, ids: list[str], *, include_archived: bool) -> list[dict[str, Any]]:
        items_by_id = {str(item.get("id") or ""): item for item in self.item_service.manifest().get("items", [])}
        items: list[dict[str, Any]] = []
        for item_id in ids:
            item = items_by_id.get(item_id)
            if not item:
                continue
            if bool(item.get("archived")) and not include_archived:
                continue
            items.append(item)
        return items


def normalize_source_mode(value: Any) -> str:
    mode = str(value or "local_only").strip()
    if mode not in VALID_SOURCE_MODES:
        raise AIContextError("Unsupported AI source mode.")
    return mode


def normalize_scope(context: dict[str, Any]) -> str:
    scope = str(context.get("scope") or "").strip()
    if scope in {"global", "library", "collection", "tag", "search", "favorites"}:
        return scope
    if context.get("collection"):
        return "collection"
    if context.get("tags"):
        return "tag"
    if context.get("q") or context.get("query"):
        return "search"
    if context.get("favorite") is True:
        return "favorites"
    if context.get("library"):
        return "library"
    return "global"


def normalize_id_list(value: Any) -> list[str]:
    if isinstance(value, str):
        raw_values = value.split(",")
    elif isinstance(value, list):
        raw_values = value
    else:
        raw_values = []
    seen: set[str] = set()
    ids: list[str] = []
    for raw in raw_values:
        item_id = str(raw or "").strip()
        if item_id and item_id not in seen:
            ids.append(item_id)
            seen.add(item_id)
    return ids


def parse_optional_bool(value: Any) -> bool | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def parse_optional_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def context_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(item.get("id") or ""),
        "title": str(item.get("title") or ""),
        "summary": str(item.get("summary") or ""),
        "collection": str(item.get("collection") or ""),
        "tags": list(item.get("tags") or []),
        "source_type": str(item.get("source_type") or ""),
        "favorite": bool(item.get("favorite")),
        "archived": bool(item.get("archived")),
        "updated": str(item.get("updated") or ""),
    }


def context_key(snapshot: dict[str, Any]) -> str:
    scope = str(snapshot.get("scope") or "global").strip() or "global"
    item_ids = [str(item_id) for item_id in snapshot.get("item_ids") or [] if str(item_id)]
    requested = snapshot.get("requested") if isinstance(snapshot.get("requested"), dict) else {}

    if scope == "manual":
        parts = {"item_ids": sorted(item_ids)}
    elif scope == "reader":
        parts = {"item_id": item_ids[0] if item_ids else str(requested.get("item_id") or "")}
    else:
        parts = {
            "scope": scope,
            "q": str(requested.get("q") or ""),
            "library": str(requested.get("library") or ""),
            "collection": str(requested.get("collection") or ""),
            "tags": sorted(str(tag) for tag in requested.get("tags") or []),
            "tag_match": str(requested.get("tag_match") or "any"),
            "favorite": requested.get("favorite"),
            "include_archived": bool(requested.get("include_archived", False)),
            "sort": str(requested.get("sort") or "newest"),
        }
    return f"{scope}:{json.dumps(parts, ensure_ascii=False, sort_keys=True, separators=(',', ':'))}"


def canonical_context_key(value: Any) -> str:
    key = str(value or "").strip()
    for source_mode in VALID_SOURCE_MODES:
        prefix = f"{source_mode}:"
        if key.startswith(prefix):
            return key[len(prefix) :]
    return key


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
