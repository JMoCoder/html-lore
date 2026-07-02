from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from functools import cmp_to_key
from pathlib import Path
from typing import Any, Iterable

from html_lore.builder import build_site
from html_lore.manifest import build_manifest
from html_lore.metadata import MetadataStore, dump_simple_yaml

from .config import ServerSettings


VALID_LIBRARY_FILTERS = {"all", "inbox", "recent", "favorites", "generated", "imported", "archived"}
VALID_SORT_MODES = {"newest", "oldest", "title-az", "title-za"}
VALID_TAG_MATCH_MODES = {"any", "all"}


@dataclass(frozen=True)
class ItemQuery:
    q: str = ""
    library: str = "all"
    collection: str = ""
    tags: tuple[str, ...] = ()
    tag_match: str = "any"
    favorite: bool | None = None
    archived: bool | None = None
    sort: str = "newest"
    limit: int | None = None


class ItemService:
    def __init__(self, settings: ServerSettings) -> None:
        self.settings = settings

    def manifest(self) -> dict[str, Any]:
        return build_manifest(
            content_dir=self.settings.content_dir,
            meta_dir=self.settings.meta_dir,
            site_title=self.settings.site_title,
        )

    def list_items(self, query: ItemQuery) -> list[dict[str, Any]]:
        items = list(self.manifest().get("items", []))
        items = apply_library_filter(items, query.library)
        items = apply_collection_filter(items, query.collection)
        items = apply_tag_filter(items, query.tags, query.tag_match)
        items = apply_boolean_filter(items, "favorite", query.favorite)
        items = apply_archive_filter(items, query.library, query.archived)
        items = apply_search_filter(items, query.q)
        items = sort_items(items, query.sort)
        if query.limit is not None:
            items = items[: query.limit]
        return items

    def search_items(self, query: ItemQuery) -> dict[str, Any]:
        items = self.list_items(query)
        return {
            "query": query.q,
            "count": len(items),
            "items": [build_search_result(item, query.q) for item in items],
        }

    def get_item(self, item_id: str) -> dict[str, Any] | None:
        for item in self.manifest().get("items", []):
            if item.get("id") == item_id:
                return item
        return None

    def get_item_content_path(self, item_id: str) -> Path:
        item = self.get_item(item_id)
        if not item:
            raise ItemContentError("Item not found.")
        content_path = self.settings.content_dir / item_id
        ensure_within(content_path, self.settings.content_dir)
        if not content_path.is_file():
            raise ItemContentError("Item content not found.")
        return content_path

    def read_item_content(self, item_id: str) -> str:
        return self.get_item_content_path(item_id).read_text(encoding="utf-8", errors="replace")

    def update_item_content(self, item_id: str, content: Any) -> dict[str, Any]:
        item = self.get_item(item_id)
        if not item:
            raise ItemContentUpdateError("Item not found.")
        if bool(item.get("archived")):
            raise ItemContentUpdateError("Archived items cannot be edited.")
        if not isinstance(content, str):
            raise ItemContentUpdateError("Content must be a string.")
        if not content.strip():
            raise ItemContentUpdateError("Content cannot be empty.")
        if "\x00" in content:
            raise ItemContentUpdateError("Content cannot contain null bytes.")
        encoded = content.encode("utf-8")
        if len(encoded) > self.settings.max_upload_bytes:
            raise ItemContentUpdateError("Content exceeds the configured upload size limit.")

        content_path = self.get_item_content_path(item_id)
        self.preserve_item_dates_for_content_edit(item_id, item)
        content_path.write_text(content, encoding="utf-8")
        build_site(
            content_dir=self.settings.content_dir,
            meta_dir=self.settings.meta_dir,
            output_dir=self.settings.public_dir,
            site_title=self.settings.site_title,
        )
        updated = self.get_item(item_id)
        if not updated:
            raise ItemContentUpdateError("Updated item not found.")
        return updated

    def preserve_item_dates_for_content_edit(self, item_id: str, item: dict[str, Any]) -> None:
        if self.settings.meta_dir is None:
            return
        metadata_path = metadata_path_for_item(self.settings.meta_dir, item_id)
        if metadata_path is None:
            return
        ensure_within(metadata_path, self.settings.meta_dir)
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        existing = MetadataStore.load(self.settings.meta_dir).for_item(item_id)
        values = {
            **existing,
            "id": item_id,
            "created": existing.get("created") or item.get("created"),
            "updated": existing.get("updated") or item.get("updated") or item.get("created"),
        }
        values = {key: value for key, value in values.items() if value is not None}
        metadata_path.write_text(dump_simple_yaml(values), encoding="utf-8")

    def update_item_metadata(self, item_id: str, values: dict[str, Any]) -> dict[str, Any]:
        item = self.get_item(item_id)
        if not item:
            raise ItemMetadataError("Item not found.")
        if bool(item.get("archived")):
            raise ItemMetadataError("Archived items cannot be edited.")

        metadata = {
            "title": normalize_metadata_text(values.get("title")) or item.get("title") or "Untitled",
            "summary": normalize_metadata_text(values.get("summary")),
            "collection": normalize_metadata_text(values.get("collection")) or item.get("collection") or "Inbox",
            "tags": normalize_tags(values.get("tags") or []),
        }
        return self.write_item_metadata(item_id, item, metadata, ItemMetadataError)

    def update_item_state(self, item_id: str, values: dict[str, Any]) -> dict[str, Any]:
        item = self.get_item(item_id)
        if not item:
            raise ItemStateError("Item not found.")
        state: dict[str, bool] = {}
        for key in ("favorite", "archived"):
            if key in values:
                if not isinstance(values[key], bool):
                    raise ItemStateError(f"{key} must be a boolean.")
                state[key] = values[key]
        if not state:
            raise ItemStateError("No state fields provided.")
        return self.write_item_metadata(item_id, item, state, ItemStateError)

    def write_item_metadata(
        self,
        item_id: str,
        item: dict[str, Any],
        values: dict[str, Any],
        error_type: type[ValueError],
    ) -> dict[str, Any]:
        if self.settings.meta_dir is None:
            raise error_type("Metadata directory is not configured.")

        metadata_path = metadata_path_for_item(self.settings.meta_dir, item_id)
        if metadata_path is None:
            raise error_type("Metadata directory is not configured.")
        ensure_within(metadata_path, self.settings.meta_dir)
        metadata_path.parent.mkdir(parents=True, exist_ok=True)

        existing = MetadataStore.load(self.settings.meta_dir).for_item(item_id)
        metadata = {
            **item,
            **existing,
            **values,
            "id": item_id,
            "updated": datetime.now(timezone.utc).isoformat(),
        }
        metadata.pop("path", None)
        metadata.pop("source_url", None) if metadata.get("source_url") is None else None
        metadata_path.write_text(dump_simple_yaml(metadata), encoding="utf-8")
        build_site(
            content_dir=self.settings.content_dir,
            meta_dir=self.settings.meta_dir,
            output_dir=self.settings.public_dir,
            site_title=self.settings.site_title,
        )
        updated = self.get_item(item_id)
        if not updated:
            raise ItemMetadataError("Updated item not found.")
        return updated

    def delete_item(self, item_id: str) -> dict[str, Any]:
        item = self.get_item(item_id)
        if not item:
            raise ItemDeleteError("Item not found.")
        if not bool(item.get("archived")):
            raise ItemDeleteError("Only archived items can be permanently deleted.")
        existing_metadata = MetadataStore.load(self.settings.meta_dir).for_item(item_id)

        content_path = self.settings.content_dir / item_id
        ensure_within(content_path, self.settings.content_dir)
        if content_path.exists():
            content_path.unlink()

        metadata_path = metadata_path_for_item(self.settings.meta_dir, item_id)
        if metadata_path and metadata_path.exists():
            metadata_path.unlink()
            remove_empty_parents(metadata_path.parent, self.settings.meta_dir / "items")
        delete_linked_workspace(self.settings, existing_metadata)
        build_site(
            content_dir=self.settings.content_dir,
            meta_dir=self.settings.meta_dir,
            output_dir=self.settings.public_dir,
            site_title=self.settings.site_title,
        )
        return {"id": item_id, "deleted": True}


class ItemDeleteError(ValueError):
    pass


def delete_linked_workspace(settings: ServerSettings, metadata: dict[str, Any]) -> None:
    workspace = metadata.get("workspace") if isinstance(metadata.get("workspace"), dict) else {}
    job_id = str(workspace.get("job_id") or "").strip()
    if not job_id:
        return
    from html_lore.server.ai.generation_v2.material_bundle import delete_job_workspace

    delete_job_workspace(settings, job_id)


class ItemContentError(ValueError):
    pass


class ItemContentUpdateError(ValueError):
    pass


class ItemMetadataError(ValueError):
    pass


class ItemStateError(ValueError):
    pass


def normalize_query(
    q: str = "",
    library: str = "all",
    collection: str = "",
    tags: str | Iterable[str] = "",
    tag_match: str = "any",
    favorite: bool | None = None,
    archived: bool | None = None,
    sort: str = "newest",
    limit: int | None = None,
) -> ItemQuery:
    library_value = library if library in VALID_LIBRARY_FILTERS else "all"
    tag_match_value = tag_match if tag_match in VALID_TAG_MATCH_MODES else "any"
    sort_value = sort if sort in VALID_SORT_MODES else "newest"
    tag_values = normalize_tags(tags)
    limit_value = limit if limit is None or limit > 0 else None
    return ItemQuery(
        q=q.strip(),
        library=library_value,
        collection=collection.strip(),
        tags=tuple(tag_values),
        tag_match=tag_match_value,
        favorite=favorite,
        archived=archived,
        sort=sort_value,
        limit=limit_value,
    )


def normalize_tags(tags: str | Iterable[str]) -> list[str]:
    if isinstance(tags, str):
        values = tags.split(",")
    else:
        values = tags
    return [value.strip().lstrip("#") for value in values if value and value.strip().lstrip("#")]


def normalize_metadata_text(value: Any) -> str:
    return str(value or "").strip()


def apply_library_filter(items: list[dict[str, Any]], library: str) -> list[dict[str, Any]]:
    if library == "all" or library == "recent":
        return items
    if library == "inbox":
        return [item for item in items if (item.get("collection") or "Inbox") == "Inbox"]
    if library == "favorites":
        return [item for item in items if bool(item.get("favorite"))]
    if library == "generated":
        return [
            item for item in items
            if bool((item.get("agent") or {}).get("generated")) or item.get("source_type") == "topic"
        ]
    if library == "imported":
        return [item for item in items if item.get("source_type") in {"imported", "html"}]
    if library == "archived":
        return [item for item in items if bool(item.get("archived"))]
    return items


def apply_collection_filter(items: list[dict[str, Any]], collection: str) -> list[dict[str, Any]]:
    if not collection:
        return items
    return [item for item in items if item.get("collection") == collection]


def apply_tag_filter(items: list[dict[str, Any]], tags: tuple[str, ...], tag_match: str) -> list[dict[str, Any]]:
    if not tags:
        return items
    selected = set(tags)
    if tag_match == "all":
        return [item for item in items if selected.issubset(set(item.get("tags") or []))]
    return [item for item in items if selected.intersection(set(item.get("tags") or []))]


def apply_boolean_filter(
    items: list[dict[str, Any]],
    field: str,
    value: bool | None,
) -> list[dict[str, Any]]:
    if value is None:
        return items
    return [item for item in items if bool(item.get(field)) is value]


def apply_archive_filter(
    items: list[dict[str, Any]],
    library: str,
    archived: bool | None,
) -> list[dict[str, Any]]:
    if archived is not None:
        return [item for item in items if bool(item.get("archived")) is archived]
    if library == "archived":
        return items
    return [item for item in items if not bool(item.get("archived"))]


def apply_search_filter(items: list[dict[str, Any]], query: str) -> list[dict[str, Any]]:
    if not query:
        return items
    needle = query.lower()
    return [item for item in items if needle in searchable_text(item)]


def searchable_text(item: dict[str, Any]) -> str:
    return " ".join(
        str(value)
        for value in [
            item.get("title"),
            item.get("summary"),
            item.get("path"),
            item.get("collection"),
            item.get("source_type"),
            *(item.get("tags") or []),
        ]
        if value
    ).lower()


def build_search_result(item: dict[str, Any], query: str) -> dict[str, Any]:
    return {
        "item": item,
        "score": score_search_result(item, query),
        "matches": search_matches(item, query),
        "snippet": search_snippet(item, query),
    }


def score_search_result(item: dict[str, Any], query: str) -> int:
    if not query:
        return 0
    needle = query.lower()
    score = 0
    if needle in str(item.get("title") or "").lower():
        score += 30
    if needle in str(item.get("summary") or "").lower():
        score += 20
    if needle in str(item.get("collection") or "").lower():
        score += 10
    if needle in " ".join(str(tag) for tag in item.get("tags") or []).lower():
        score += 10
    if needle in str(item.get("path") or "").lower():
        score += 5
    return score


def search_matches(item: dict[str, Any], query: str) -> list[str]:
    if not query:
        return []
    needle = query.lower()
    matches: list[str] = []
    fields = {
        "title": item.get("title"),
        "summary": item.get("summary"),
        "collection": item.get("collection"),
        "tags": " ".join(str(tag) for tag in item.get("tags") or []),
        "path": item.get("path"),
    }
    for field, value in fields.items():
        if needle in str(value or "").lower():
            matches.append(field)
    return matches


def search_snippet(item: dict[str, Any], query: str) -> str:
    source = str(item.get("summary") or item.get("title") or "")
    if not query:
        return source[:180]
    index = source.lower().find(query.lower())
    if index < 0:
        return source[:180]
    start = max(0, index - 60)
    end = min(len(source), index + len(query) + 120)
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(source) else ""
    return f"{prefix}{source[start:end].strip()}{suffix}"


def sort_items(items: list[dict[str, Any]], sort: str) -> list[dict[str, Any]]:
    def compare(a: dict[str, Any], b: dict[str, Any]) -> int:
        title_order = compare_text(a.get("title"), b.get("title"))
        newest_order = compare_text(b.get("updated"), a.get("updated"))
        oldest_order = compare_text(a.get("updated"), b.get("updated"))
        title_desc_order = compare_text(b.get("title"), a.get("title"))

        if sort == "oldest":
            return oldest_order or title_order
        if sort == "title-az":
            return title_order or newest_order
        if sort == "title-za":
            return title_desc_order or newest_order
        return newest_order or title_order

    return sorted(items, key=cmp_to_key(compare))


def compare_text(left: Any, right: Any) -> int:
    left_value = str(left or "").lower()
    right_value = str(right or "").lower()
    if left_value < right_value:
        return -1
    if left_value > right_value:
        return 1
    return 0


def metadata_path_for_item(meta_dir: Path | None, item_id: str) -> Path | None:
    if meta_dir is None:
        return None
    return meta_dir / "items" / Path(item_id).with_suffix(".yml")


def ensure_within(path: Path, root: Path) -> None:
    path.resolve().relative_to(root.resolve())


def remove_empty_parents(path: Path, stop_at: Path) -> None:
    stop = stop_at.resolve()
    current = path.resolve()
    while current != stop and stop in current.parents:
        try:
            current.rmdir()
        except OSError:
            return
        current = current.parent
