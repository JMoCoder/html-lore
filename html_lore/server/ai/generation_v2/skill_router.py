from __future__ import annotations

from .schemas import GenerationState, ToolNeed
from .skills.loader import LoadedSkill, SkillLoaderError, iter_skill_registry_items, load_default_skills_for_agent, load_skill_by_id


TARGET_USE_SKILLS = {
    "report": "report_surface_design",
    "webpage": "webpage_surface_design",
    "ppt": "presentation_surface_design",
}

STYLE_PREFERENCE_SKILLS = {
    "minimal": "minimal_style_design",
    "business": "business_style_design",
    "tech": "tech_style_design",
    "retro": "retro_style_design",
    "magazine": "magazine_style_design",
}


def resolve_skills_for_agent(agent_name: str, state: GenerationState) -> tuple[LoadedSkill, ...]:
    selected = list(load_default_skills_for_agent(agent_name))
    seen = {skill.id for skill in selected}
    for skill_id in planned_skill_ids_for_agent(agent_name, state):
        if skill_id in seen:
            continue
        skill = load_optional_skill_by_id(skill_id)
        if skill is None:
            continue
        selected.append(skill)
        seen.add(skill_id)
    return tuple(selected)


def planned_skill_ids_for_agent(agent_name: str, state: GenerationState) -> tuple[str, ...]:
    result: list[str] = []
    result.extend(explicit_option_skill_ids_for_agent(agent_name, state))
    if state.plan_draft is None:
        return tuple(dict.fromkeys(result))
    needs = tuple(state.plan_draft.tool_needs or ())
    if not needs:
        return tuple(dict.fromkeys(result))
    for item in iter_skill_registry_items():
        if item.default_enabled:
            continue
        if agent_name not in item.applies_to_agents:
            continue
        if any(tool_need_matches_skill(need, item.id, item.trigger_keywords) for need in needs):
            result.append(item.id)
    return tuple(dict.fromkeys(result))


def explicit_option_skill_ids_for_agent(agent_name: str, state: GenerationState) -> tuple[str, ...]:
    if agent_name != "StyleDesigner":
        return ()
    result: list[str] = []
    target_use = str(state.input.target_use or "default").strip().lower()
    style_preference = str(state.input.style_preference or "default").strip().lower()
    if target_use in TARGET_USE_SKILLS:
        result.append(TARGET_USE_SKILLS[target_use])
    if style_preference in STYLE_PREFERENCE_SKILLS:
        result.append(STYLE_PREFERENCE_SKILLS[style_preference])
    return tuple(result)


def load_optional_skill_by_id(skill_id: str) -> LoadedSkill | None:
    try:
        return load_skill_by_id(skill_id)
    except SkillLoaderError:
        return None


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
