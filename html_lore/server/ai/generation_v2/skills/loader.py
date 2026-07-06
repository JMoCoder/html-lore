from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from importlib import resources
from pathlib import PurePosixPath
from typing import Any


class SkillLoaderError(ValueError):
    pass


@dataclass(frozen=True)
class LoadedSkill:
    id: str
    title: str
    description: str
    version: str
    license: str
    source: str
    path: str
    content: str


@dataclass(frozen=True)
class SkillRegistryItem:
    id: str
    title: str
    description: str
    applies_to_agents: tuple[str, ...]
    default_enabled: bool
    planner_selectable: bool
    trigger_keywords: tuple[str, ...]
    version: str
    license: str
    source: str
    path: str


@lru_cache(maxsize=1)
def load_skill_registry() -> dict[str, Any]:
    package = "html_lore.server.ai.generation_v2.skills"
    raw = resources.files(package).joinpath("registry.json").read_text(encoding="utf-8")
    decoded = json.loads(raw)
    if not isinstance(decoded, dict) or not isinstance(decoded.get("skills"), list):
        raise SkillLoaderError("Skill registry must contain a skills list.")
    return decoded


def load_default_skills_for_agent(agent_name: str) -> tuple[LoadedSkill, ...]:
    result: list[LoadedSkill] = []
    for item in iter_skill_registry_items():
        if not item.default_enabled:
            continue
        if agent_name not in item.applies_to_agents:
            continue
        result.append(load_skill_by_id(item.id))
    return tuple(result)


def iter_skill_registry_items() -> tuple[SkillRegistryItem, ...]:
    registry = load_skill_registry()
    result: list[SkillRegistryItem] = []
    for item in registry["skills"]:
        if not isinstance(item, dict):
            continue
        path = str(item.get("path") or "")
        metadata, content = load_skill_document(path)
        applies = item.get("applies_to_agents") if isinstance(item.get("applies_to_agents"), list) else []
        triggers = item.get("trigger_keywords") if isinstance(item.get("trigger_keywords"), list) else []
        skill_id = str(item.get("id") or metadata.get("name") or "").strip()
        result.append(
            SkillRegistryItem(
                id=skill_id,
                title=str(metadata.get("title") or first_markdown_heading(content) or skill_id),
                description=str(metadata.get("description") or ""),
                applies_to_agents=tuple(str(value or "") for value in applies if str(value or "")),
                default_enabled=bool(item.get("default_enabled", False)),
                planner_selectable=bool(item.get("planner_selectable", not bool(item.get("default_enabled", False)))),
                trigger_keywords=tuple(str(value or "") for value in triggers if str(value or "")),
                version=str(metadata.get("version") or ""),
                license=str(metadata.get("license") or ""),
                source=str(item.get("source") or "local"),
                path=path,
            )
        )
    return tuple(result)


def load_skill_by_id(skill_id: str) -> LoadedSkill:
    normalized = str(skill_id or "").strip()
    for item in iter_skill_registry_items():
        if item.id == normalized:
            return load_skill(item)
    raise SkillLoaderError(f"Unknown skill id: {normalized}")


def load_skill(item: SkillRegistryItem) -> LoadedSkill:
    metadata, content = load_skill_document(item.path)
    skill_id = str(metadata.get("name") or item.id).strip()
    title = str(metadata.get("title") or item.title or first_markdown_heading(content) or skill_id).strip()
    return LoadedSkill(
        id=skill_id,
        title=title,
        description=str(metadata.get("description") or item.description or ""),
        version=str(metadata.get("version") or item.version or ""),
        license=str(metadata.get("license") or item.license or ""),
        source=item.source,
        path=item.path,
        content=content,
    )


def load_skill_document(skill_path: str) -> tuple[dict[str, Any], str]:
    if not skill_path or PurePosixPath(skill_path).is_absolute() or ".." in PurePosixPath(skill_path).parts:
        raise SkillLoaderError(f"Invalid skill path: {skill_path}")
    package = "html_lore.server.ai.generation_v2.skills"
    raw = resources.files(package).joinpath(skill_path).read_text(encoding="utf-8")
    metadata, content = split_frontmatter(raw)
    return metadata, content


def split_frontmatter(raw: str) -> tuple[dict[str, Any], str]:
    text = str(raw or "")
    if not text.startswith("---\n"):
        return {}, text
    marker = "\n---\n"
    end = text.find(marker, 4)
    if end < 0:
        raise SkillLoaderError("Skill frontmatter is not closed.")
    frontmatter = text[4:end]
    content = text[end + len(marker) :]
    return parse_simple_frontmatter(frontmatter), content.lstrip()


def parse_simple_frontmatter(frontmatter: str) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    for line in frontmatter.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith(" ") or line.startswith("\t"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if not key:
            continue
        metadata[key] = parse_frontmatter_value(value.strip())
    return metadata


def parse_frontmatter_value(value: str) -> Any:
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [part.strip().strip("\"'") for part in inner.split(",") if part.strip()]
    return value.strip("\"'")


def first_markdown_heading(content: str) -> str:
    for line in str(content or "").splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return ""
