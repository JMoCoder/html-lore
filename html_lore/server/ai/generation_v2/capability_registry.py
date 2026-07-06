from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .skills.loader import iter_skill_registry_items
from .tools.registry import iter_tool_registry_items


@dataclass(frozen=True)
class PlannerCapability:
    id: str
    kind: str
    title: str
    description: str
    applies_to_agents: tuple[str, ...]
    trigger_keywords: tuple[str, ...]
    planner_selectable: bool
    selection_field: str = ""


def planner_capability_catalog() -> dict[str, Any]:
    return {
        "skills": [public_planner_capability(item) for item in planner_skill_capabilities()],
        "tools": [public_planner_capability(item) for item in planner_tool_capabilities()],
        "rules": [
            "Use tool_needs only for planner_selectable skill ids from this catalog.",
            "Tools are registered runtime capabilities for boundary awareness; Planner must not request tools directly.",
            "Do not invent capability, skill, tool, vendor, package, or project names.",
        ],
    }


def planner_skill_capabilities() -> tuple[PlannerCapability, ...]:
    result: list[PlannerCapability] = []
    for item in iter_skill_registry_items():
        if item.default_enabled or not item.planner_selectable:
            continue
        result.append(
            PlannerCapability(
                id=item.id,
                kind="skill",
                title=item.title,
                description=item.description,
                applies_to_agents=item.applies_to_agents,
                trigger_keywords=item.trigger_keywords,
                planner_selectable=True,
                selection_field="tool_needs.tool_name",
            )
        )
    return tuple(result)


def planner_tool_capabilities() -> tuple[PlannerCapability, ...]:
    result: list[PlannerCapability] = []
    for item in iter_tool_registry_items():
        result.append(
            PlannerCapability(
                id=item.id,
                kind="tool",
                title=item.title,
                description=item.description,
                applies_to_agents=item.available_to_agents,
                trigger_keywords=item.trigger_keywords,
                planner_selectable=False,
                selection_field=item.request_field,
            )
        )
    return tuple(result)


def planner_selectable_skill_ids() -> tuple[str, ...]:
    return tuple(item.id for item in planner_skill_capabilities() if item.planner_selectable)


def canonical_planner_skill_id(value: str, *, reason: str = "") -> str:
    haystack = " ".join([str(value or ""), str(reason or "")])
    normalized = normalize_token(haystack)
    for item in planner_skill_capabilities():
        if normalize_token(item.id) and normalize_token(item.id) in normalized:
            return item.id
        if normalize_token(item.title) and normalize_token(item.title) in normalized:
            return item.id
        for keyword in item.trigger_keywords:
            if normalize_token(keyword) and normalize_token(keyword) in normalized:
                return item.id
    return ""


def public_planner_capability(item: PlannerCapability) -> dict[str, Any]:
    return {
        "id": item.id,
        "kind": item.kind,
        "title": item.title,
        "description": item.description,
        "applies_to_agents": list(item.applies_to_agents),
        "trigger_keywords": list(item.trigger_keywords[:12]),
        "planner_selectable": item.planner_selectable,
        "selection_field": item.selection_field,
    }


def normalize_token(value: str) -> str:
    return "".join(str(value or "").lower().replace("_", " ").replace("-", " ").split())
