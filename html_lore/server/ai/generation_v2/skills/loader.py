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
    version: str
    source: str
    path: str
    content: str


@lru_cache(maxsize=1)
def load_skill_registry() -> dict[str, Any]:
    package = "html_lore.server.ai.generation_v2.skills"
    raw = resources.files(package).joinpath("registry.json").read_text(encoding="utf-8")
    decoded = json.loads(raw)
    if not isinstance(decoded, dict) or not isinstance(decoded.get("skills"), list):
        raise SkillLoaderError("Skill registry must contain a skills list.")
    return decoded


def load_default_skills_for_agent(agent_name: str) -> tuple[LoadedSkill, ...]:
    registry = load_skill_registry()
    result: list[LoadedSkill] = []
    for item in registry["skills"]:
        if not isinstance(item, dict):
            continue
        if not item.get("default_enabled", False):
            continue
        applies = item.get("applies_to_agents") if isinstance(item.get("applies_to_agents"), list) else []
        if agent_name not in applies:
            continue
        result.append(load_skill(item))
    return tuple(result)


def load_skill(item: dict[str, Any]) -> LoadedSkill:
    skill_path = str(item.get("path") or "")
    if not skill_path or PurePosixPath(skill_path).is_absolute() or ".." in PurePosixPath(skill_path).parts:
        raise SkillLoaderError(f"Invalid skill path: {skill_path}")
    package = "html_lore.server.ai.generation_v2.skills"
    content = resources.files(package).joinpath(skill_path).read_text(encoding="utf-8")
    return LoadedSkill(
        id=str(item.get("id") or ""),
        title=str(item.get("title") or ""),
        version=str(item.get("version") or ""),
        source=str(item.get("source") or "local"),
        path=skill_path,
        content=content,
    )
