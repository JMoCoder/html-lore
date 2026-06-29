from __future__ import annotations

from .schemas import GenerationState, ToolNeed
from .skills.loader import LoadedSkill, iter_skill_registry_items, load_default_skills_for_agent, load_skill_by_id


def resolve_skills_for_agent(agent_name: str, state: GenerationState) -> tuple[LoadedSkill, ...]:
    selected = list(load_default_skills_for_agent(agent_name))
    seen = {skill.id for skill in selected}
    for skill_id in planned_skill_ids_for_agent(agent_name, state):
        if skill_id in seen:
            continue
        selected.append(load_skill_by_id(skill_id))
        seen.add(skill_id)
    return tuple(selected)


def planned_skill_ids_for_agent(agent_name: str, state: GenerationState) -> tuple[str, ...]:
    if state.plan_draft is None:
        return ()
    needs = tuple(state.plan_draft.tool_needs or ())
    if not needs:
        return ()
    result: list[str] = []
    for item in iter_skill_registry_items():
        if item.default_enabled:
            continue
        if agent_name not in item.applies_to_agents:
            continue
        if any(tool_need_matches_skill(need, item.id, item.trigger_keywords) for need in needs):
            result.append(item.id)
    return tuple(result)


def tool_need_matches_skill(need: ToolNeed, skill_id: str, trigger_keywords: tuple[str, ...]) -> bool:
    haystack = " ".join(
        [
            str(need.tool_name or ""),
            str(need.reason or ""),
            str(need.priority or ""),
        ]
    ).lower()
    normalized_skill = normalize_token(skill_id)
    if normalized_skill and normalized_skill in normalize_token(haystack):
        return True
    for keyword in trigger_keywords:
        normalized_keyword = normalize_token(keyword)
        if normalized_keyword and normalized_keyword in normalize_token(haystack):
            return True
    return False


def normalize_token(value: str) -> str:
    return "".join(str(value or "").lower().replace("_", " ").replace("-", " ").split())
