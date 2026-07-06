from __future__ import annotations

import json
from dataclasses import asdict, fields, is_dataclass
from enum import Enum
from importlib import resources
from typing import Any, Protocol, get_args, get_origin, get_type_hints

from html_lore.server.ai.model_client import ModelClient

from .capability_registry import planner_capability_catalog
from .schemas import GenerationState, normalize_for_json
from .skills.loader import LoadedSkill
from .tools.registry import get_tool_registry_item


class GenerationJsonModelClient(Protocol):
    def complete_json(self, *, node: str, schema_name: str, payload: dict[str, Any], attempt: int = 0) -> str:
        ...

    def complete_text(self, *, node: str, payload: dict[str, Any], attempt: int = 0) -> str:
        ...


class ProviderGenerationModelClient:
    def __init__(
        self,
        model_client: ModelClient,
        *,
        max_prompt_chars: int = 48000,
        max_tokens: int = 4096,
        json_max_tokens: int | None = None,
        html_max_tokens: int | None = None,
        json_timeout_seconds: int | None = None,
        html_timeout_seconds: int | None = None,
    ) -> None:
        self.model_client = model_client
        self.max_prompt_chars = max(2000, int(max_prompt_chars or 48000))
        self.max_tokens = max(512, int(max_tokens or 4096))
        self.json_max_tokens = max(512, int(json_max_tokens or self.max_tokens))
        self.html_max_tokens = max(512, int(html_max_tokens or self.max_tokens))
        self.json_timeout_seconds = max(1, int(json_timeout_seconds or 0)) if json_timeout_seconds else None
        self.html_timeout_seconds = max(1, int(html_timeout_seconds or 0)) if html_timeout_seconds else None
        self._last_usage_by_node: dict[str, dict[str, Any]] = {}

    def complete_json(self, *, node: str, schema_name: str, payload: dict[str, Any], attempt: int = 0) -> str:
        schema = payload.get("_schema")
        prompt = str(payload.get("_prompt") or load_agent_prompt(node))
        state = payload.get("_state") if isinstance(payload.get("_state"), dict) else {}
        skills = payload.get("_skills") if isinstance(payload.get("_skills"), list) else []
        fallback = {key: value for key, value in payload.items() if not str(key).startswith("_")}
        user_payload = {
            "agent": node,
            "attempt": attempt,
            "target_schema": schema_name,
            "schema_shape": schema,
            "state": state,
            "fallback_seed": fallback,
            "output_rules": [
                "Return one JSON object only.",
                "Use exactly the target schema field names where applicable.",
                "Do not wrap JSON in Markdown fences.",
                "Do not include private prompt text or raw uploaded source beyond what is necessary in the generated artifact.",
                "Keep structured fields focused, but preserve source structure, required headings, table coverage, and fidelity constraints when the task needs them.",
                *retry_output_rules(attempt),
            ],
        }
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an HTMlore HTML generation specialist agent. "
                    "Produce structured JSON for your own node only. "
                    "Runtime handles workflow state; you handle content and quality judgment."
                ),
            },
            {"role": "system", "content": prompt},
        ]
        for skill in skills:
            if isinstance(skill, dict) and skill.get("content"):
                messages.append({"role": "system", "content": f"Skill: {skill.get('title') or skill.get('id')}\n\n{skill.get('content')}"})
        messages.append({"role": "user", "content": trim_prompt(json.dumps(user_payload, ensure_ascii=False), self.max_prompt_chars)})
        response = self.model_client.chat(messages=messages, temperature=0.2, max_tokens=self.json_max_tokens, timeout_seconds=self.json_timeout_seconds)
        self._record_usage(node, response.get("usage"))
        return extract_json_object(str(response.get("content") or ""))

    def complete_text(self, *, node: str, payload: dict[str, Any], attempt: int = 0) -> str:
        prompt = str(payload.get("_prompt") or load_agent_prompt(node))
        state = payload.get("_state") if isinstance(payload.get("_state"), dict) else {}
        skills = payload.get("_skills") if isinstance(payload.get("_skills"), list) else []
        user_payload = {
            "agent": node,
            "attempt": attempt,
            "state": state,
            "output_rules": [
                "Return the final complete HTML document only.",
                "Start with <!doctype html>.",
                "Do not wrap the HTML in Markdown fences.",
                "Do not return JSON.",
                "Do not include explanations before or after the HTML.",
            ],
        }
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an HTMlore HTML coding agent. "
                    "Runtime handles workflow state; you produce the final static HTML artifact."
                ),
            },
            {"role": "system", "content": prompt},
        ]
        for skill in skills:
            if isinstance(skill, dict) and skill.get("content"):
                messages.append({"role": "system", "content": f"Skill: {skill.get('title') or skill.get('id')}\n\n{skill.get('content')}"})
        messages.append({"role": "user", "content": trim_prompt(json.dumps(user_payload, ensure_ascii=False), self.max_prompt_chars)})
        response = self.model_client.chat(messages=messages, temperature=0.2, max_tokens=self.html_max_tokens, timeout_seconds=self.html_timeout_seconds)
        self._record_usage(node, response.get("usage"))
        return extract_html_document(str(response.get("content") or ""))

    def consume_last_usage(self, node: str) -> dict[str, Any]:
        return dict(self._last_usage_by_node.pop(str(node or ""), {}))

    def _record_usage(self, node: str, usage: Any) -> None:
        normalized = normalize_provider_usage(usage)
        if normalized:
            self._last_usage_by_node[str(node or "")] = normalized


def build_provider_generation_client(
    model_client: ModelClient,
    *,
    max_prompt_chars: int,
    max_tokens: int,
    json_max_tokens: int | None = None,
    html_max_tokens: int | None = None,
    json_timeout_seconds: int | None = None,
    html_timeout_seconds: int | None = None,
) -> ProviderGenerationModelClient:
    return ProviderGenerationModelClient(
        model_client,
        max_prompt_chars=max_prompt_chars,
        max_tokens=max_tokens,
        json_max_tokens=json_max_tokens,
        html_max_tokens=html_max_tokens,
        json_timeout_seconds=json_timeout_seconds,
        html_timeout_seconds=html_timeout_seconds,
    )


def normalize_provider_usage(usage: Any) -> dict[str, int]:
    if not isinstance(usage, dict):
        return {}
    mapping = {
        "prompt_tokens": "input_tokens",
        "completion_tokens": "output_tokens",
        "input_tokens": "input_tokens",
        "output_tokens": "output_tokens",
        "total_tokens": "total_tokens",
    }
    normalized: dict[str, int] = {}
    for source_key, target_key in mapping.items():
        raw = usage.get(source_key)
        if isinstance(raw, bool):
            continue
        if isinstance(raw, (int, float)):
            normalized[target_key] = int(raw)
    return normalized


def retry_output_rules(attempt: int) -> list[str]:
    if int(attempt or 0) <= 0:
        return []
    return [
        "This is a retry after the previous output failed validation.",
        "Return a smaller strict JSON object that exactly matches the schema.",
        "Use [] for empty lists and {} for empty objects; do not use null for list/object fields.",
    ]


def agent_payload(
    *,
    node: str,
    schema: type[Any],
    state: GenerationState,
    fallback: dict[str, Any],
    skills: tuple[LoadedSkill, ...],
    material_recall_phase: str = "",
) -> dict[str, Any]:
    return normalize_for_json(
        {
            **fallback,
            "_prompt": load_agent_prompt(node),
            "_schema": dataclass_shape(schema),
            "_state": public_generation_state_for_agent(state, node=node),
            "_skills": [public_skill(skill) for skill in skills],
            "_material_recall_phase": material_recall_phase or "query_or_direct",
            "_available_material_tools": available_material_tools(node),
            "_available_capabilities": available_capabilities(node),
            "_source_handling_modes": source_handling_modes(node),
        }
    )


def load_agent_prompt(node: str) -> str:
    prompt_name = {
        "RequirementAnalyst": "requirement_analyst.md",
        "Planner": "planner.md",
        "ContentWriter": "content_writer.md",
        "StyleDesigner": "style_designer.md",
        "HTMLCoder": "html_coder.md",
        "Verifier": "verifier.md",
        "SafetyReviewer": "safety_reviewer.md",
        "Finalizer": "orchestrator.md",
    }.get(node, "orchestrator.md")
    return resources.files("html_lore.server.ai.generation_v2.prompts").joinpath(prompt_name).read_text(encoding="utf-8")


def public_skill(skill: LoadedSkill) -> dict[str, str]:
    return {
        "id": skill.id,
        "title": skill.title,
        "description": skill.description,
        "version": skill.version,
        "source": skill.source,
        "content": skill.content,
    }


def available_capabilities(node: str) -> dict[str, Any]:
    if node != "Planner":
        return {}
    return planner_capability_catalog()


def source_handling_modes(node: str) -> list[dict[str, str]]:
    if node not in {"RequirementAnalyst", "Planner", "ContentWriter", "Verifier", "HTMLCoder"}:
        return []
    return [
        {
            "id": "free_synthesis",
            "description": "Use when the user asks for a new artifact inspired by the material and allows added explanation or synthesis.",
        },
        {
            "id": "source_grounded_rewrite",
            "description": "Use when the output should be grounded in uploaded material but may reorganize, clarify, and rewrite content.",
        },
        {
            "id": "faithful_adaptation",
            "description": "Use when the output should stay faithful to source content while improving structure, readability, and visual presentation.",
        },
        {
            "id": "extractive_conversion",
            "description": "Use when the user asks to preserve source facts/content nearly exactly, forbids additions, or wants conversion rather than rewriting.",
        },
    ]


def public_generation_state_for_agent(state: GenerationState, *, node: str = "") -> dict[str, Any]:
    parsed = state.parsed_document
    style_ref = state.parsed_style_reference
    material_context = state.temporary_material_context
    material_status = public_material_status(state)
    material_recall_results = compact_material_recall_results(state.material_recall_results, node=node)
    material_read_results = compact_material_read_results(state.material_read_results, node=node)
    common_input = {
        "instruction": state.input.instruction,
        "filename": state.input.filename,
        "materials": public_material_inputs(state.input.materials),
        "content_type": state.input.content_type,
        "theme": state.input.theme,
        "target_use": state.input.target_use,
        "style_preference": state.input.style_preference,
        "audience": state.input.audience,
        "reference_style": state.input.reference_style,
        "reference_file_name": state.input.reference_file_name,
        "target_collection": state.input.target_collection,
    }
    if node in {"Verifier", "SafetyReviewer", "Finalizer"}:
        state_view = {
            "input": common_input,
            "html_draft": compact_html_draft(state.html_draft),
            "visual_check_report": public_value(state.visual_check_report),
            "validation_report": public_value(state.validation_report),
            "safety_report": public_value(state.safety_report),
            "content_draft": compact_content_draft(state.content_draft),
            "style_brief": compact_style_brief(state.style_brief),
            "requirement_brief": public_value(state.requirement_brief),
            "plan_draft": compact_plan_draft(state.plan_draft),
            "parsed_document": compact_parsed_document(parsed),
            "material_status": material_status,
            "temporary_material_context": compact_temporary_material_context(material_context),
            "material_recall_results": material_recall_results,
            "material_read_results": material_read_results,
            "execution_checklist": public_value(state.execution_checklist),
            "revision_round": state.revision_round,
        }
    elif node == "HTMLCoder":
        state_view = {
            "input": common_input,
            "validation_report": public_value(state.validation_report),
            "safety_report": public_value(state.safety_report),
            "visual_check_report": public_value(state.visual_check_report),
            "content_draft": public_value(state.content_draft),
            "style_brief": public_value(state.style_brief),
            "requirement_brief": public_value(state.requirement_brief),
            "plan_draft": compact_plan_draft(state.plan_draft),
            "html_draft": compact_html_draft(state.html_draft),
            "parsed_document": compact_parsed_document(parsed),
            "material_status": material_status,
            "temporary_material_context": compact_temporary_material_context(material_context),
            "material_recall_results": material_recall_results,
            "material_read_results": material_read_results,
            "parsed_style_reference": compact_parsed_document(style_ref),
            "revision_round": state.revision_round,
        }
    else:
        task_material_context = public_value(material_context) if node in {"RequirementAnalyst", "Planner", "ContentWriter"} else compact_temporary_material_context(material_context)
        state_view = {
            "input": common_input,
            "parsed_document": compact_parsed_document(parsed),
            "material_status": material_status,
            "temporary_material_context": task_material_context,
            "material_recall_results": material_recall_results,
            "material_read_results": material_read_results,
            "parsed_style_reference": public_parsed_document(style_ref),
            "requirement_brief": public_value(state.requirement_brief),
            "plan_draft": public_value(state.plan_draft),
            "content_draft": public_value(state.content_draft),
            "style_brief": public_value(state.style_brief),
            "html_draft": trim_html_draft(state.html_draft),
            "visual_check_report": public_value(state.visual_check_report),
            "validation_report": public_value(state.validation_report),
            "safety_report": public_value(state.safety_report),
            "execution_checklist": public_value(state.execution_checklist),
            "revision_round": state.revision_round,
        }
    return normalize_for_json(state_view)


def public_material_status(state: GenerationState) -> dict[str, Any]:
    parsed = state.parsed_document
    context = state.temporary_material_context
    total_chars = int(getattr(context, "total_chars", 0) or 0)
    selected_chars = int(getattr(context, "selected_chars", 0) or 0)
    parsed_chars = len(str(getattr(parsed, "plain_text", "") or ""))
    total_chars = total_chars or parsed_chars
    selected_chunk_count = len(getattr(context, "selected_chunks", []) or [])
    file_count = len(getattr(context, "files", []) or getattr(parsed, "materials", []) or [])
    parse_warnings = []
    if parsed is not None:
        parse_warnings = [
            {
                "code": str(getattr(warning, "code", "") or ""),
                "message": str(getattr(warning, "message", "") or ""),
                "severity": str(getattr(warning, "severity", "") or ""),
            }
            for warning in getattr(parsed, "warnings", [])[:12]
        ]
    selected_covers_full_text = material_selection_covers_full_text(total_chars=total_chars, selected_chars=selected_chars)
    return {
        "file_count": file_count,
        "parsed_chars": parsed_chars,
        "total_chars": total_chars,
        "selected_chars": selected_chars,
        "selected_chunk_count": selected_chunk_count,
        "selected_covers_full_text": selected_covers_full_text,
        "parsed_document_is_preview": True,
        "parsed_text_preview_limit": 1200,
        "parsed_text_preview_truncated": parsed_chars > 1200,
        "full_text_available_via_material_read": parsed is not None and parsed_chars > 0,
        "parse_warnings": parse_warnings,
        "coverage_note": material_coverage_note(
            total_chars=total_chars,
            selected_chars=selected_chars,
            selected_covers_full_text=selected_covers_full_text,
        ),
    }


def material_coverage_note(*, total_chars: int, selected_chars: int, selected_covers_full_text: bool) -> str:
    if total_chars <= 0:
        return "No parsed material text is available."
    if selected_covers_full_text:
        return "temporary_material_context selected_chunks cover the full parsed text; parsed_document.plain_text is only a preview."
    return "temporary_material_context is a partial selection; use MaterialReadTool when full source fidelity or completeness matters."


def material_selection_covers_full_text(*, total_chars: int, selected_chars: int) -> bool:
    if total_chars <= 0:
        return False
    if selected_chars >= total_chars:
        return True
    return (total_chars - selected_chars) <= max(64, int(total_chars * 0.01))


def public_material_inputs(materials: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for item in materials:
        if not isinstance(item, dict):
            continue
        content = item.get("content")
        result.append(
            {
                "filename": str(item.get("filename") or ""),
                "content_type": str(item.get("content_type") or ""),
                "size": len(content) if isinstance(content, bytes) else int(item.get("size") or 0),
            },
        )
    return result


def available_material_tools(node: str) -> list[dict[str, Any]]:
    limits = {
        "RequirementAnalyst": {"max_requests": 2, "max_chars": 48000},
        "ContentWriter": {"max_requests": 4, "max_chars": 96000},
        "Verifier": {"max_requests": 3, "max_chars": 96000},
    }.get(node)
    if not limits:
        return []
    tool = get_tool_registry_item("material_read")
    description = tool.description if tool else "Read task-local uploaded material from the normalized merged source using file_id or filename."
    return [
        {
            "name": "MaterialReadTool",
            "id": "material_read",
            "description": f"{description} Use only when startup chunks and recall results are insufficient.",
            "request_field": tool.request_field if tool else "material_read_requests",
            "actions": ["read_outline", "read_span", "read_file"],
            "limits": limits,
            "offset_units": "characters relative to the selected file content span",
        }
    ]


def public_value(value: Any) -> Any:
    if is_dataclass(value):
        return normalize_for_json(asdict(value))
    if isinstance(value, list):
        return [public_value(item) for item in value]
    return normalize_for_json(value)


def public_parsed_document(parsed: Any) -> dict[str, Any]:
    if parsed is None:
        return {}
    data = public_value(parsed)
    data["plain_text"] = trim_text(str(data.get("plain_text") or ""), 9000)
    data["materials"] = compact_parsed_materials(data, text_limit=1800)
    return data


def compact_parsed_document(parsed: Any) -> dict[str, Any]:
    if parsed is None:
        return {}
    data = public_value(parsed)
    data["plain_text"] = trim_text(str(data.get("plain_text") or ""), 1200)
    data["materials"] = compact_parsed_materials(public_value(parsed), text_limit=500)
    return data


def compact_parsed_materials(parsed_data: Any, *, text_limit: int) -> list[dict[str, Any]]:
    if not isinstance(parsed_data, dict):
        return []
    materials = parsed_data.get("materials")
    if not isinstance(materials, list):
        return []
    plain_text = str(parsed_data.get("plain_text") or "")
    compact: list[dict[str, Any]] = []
    for item in materials[:8]:
        if not isinstance(item, dict):
            continue
        content_start = int(item.get("content_start_char") or 0)
        content_end = int(item.get("content_end_char") or 0)
        preview = plain_text[max(0, content_start) : min(len(plain_text), content_end)] if content_end >= content_start else ""
        file_id = str(item.get("file_id") or "")
        filename = str(item.get("filename") or "")
        outline = [
            entry
            for entry in parsed_data.get("outline", [])[:80]
            if isinstance(entry, dict) and (entry.get("file_id") == file_id or entry.get("filename") == filename)
        ][:12]
        compact.append(
            {
                "file_id": file_id,
                "file_index": int(item.get("file_index") or 0),
                "filename": filename,
                "content_type": str(item.get("content_type") or ""),
                "size": int(item.get("size") or 0),
                "start_char": int(item.get("start_char") or 0),
                "end_char": int(item.get("end_char") or 0),
                "content_start_char": content_start,
                "content_end_char": content_end,
                "char_count": int(item.get("char_count") or max(0, content_end - content_start)),
                "preview": trim_text(preview, text_limit),
                "outline": outline,
                "table_count": count_items_for_file(parsed_data.get("tables"), file_id=file_id, filename=filename),
                "image_count": count_items_for_file(parsed_data.get("images"), file_id=file_id, filename=filename),
                "link_count": count_items_for_file(parsed_data.get("links"), file_id=file_id, filename=filename),
            },
        )
    return compact


def count_items_for_file(items: Any, *, file_id: str, filename: str) -> int:
    if not isinstance(items, list):
        return 0
    return sum(1 for item in items if isinstance(item, dict) and (item.get("file_id") == file_id or item.get("filename") == filename))


def compact_temporary_material_context(context: Any) -> dict[str, Any]:
    if context is None:
        return {}
    data = public_value(context)
    if isinstance(data.get("selected_chunks"), list):
        chunks = []
        for chunk in data["selected_chunks"][:8]:
            if not isinstance(chunk, dict):
                continue
            chunks.append({**chunk, "text": trim_text(str(chunk.get("text") or ""), 500)})
        data["selected_chunks"] = chunks
    if isinstance(data.get("files"), list):
        data["files"] = [{**item, "preview": trim_text(str(item.get("preview") or ""), 300)} for item in data["files"][:8] if isinstance(item, dict)]
    return data


def compact_material_recall_results(results: list[Any], *, node: str = "") -> list[dict[str, Any]]:
    if not results:
        return []
    visible_agents = {
        "RequirementAnalyst": {"RequirementAnalyst"},
        "Planner": {"RequirementAnalyst"},
        "ContentWriter": {"RequirementAnalyst", "ContentWriter"},
        "StyleDesigner": {"RequirementAnalyst", "ContentWriter"},
        "HTMLCoder": {"RequirementAnalyst", "ContentWriter"},
        "Verifier": {"RequirementAnalyst", "ContentWriter", "Verifier"},
        "SafetyReviewer": {"RequirementAnalyst", "ContentWriter", "Verifier"},
        "Finalizer": {"RequirementAnalyst", "ContentWriter", "Verifier"},
    }.get(node, {"RequirementAnalyst", "ContentWriter", "Verifier"})
    compact: list[dict[str, Any]] = []
    text_limit = 900 if node in {"RequirementAnalyst", "ContentWriter", "Verifier"} else 360
    for result in results:
        data = public_value(result)
        if not isinstance(data, dict) or str(data.get("agent") or "") not in visible_agents:
            continue
        chunks = []
        for chunk in data.get("chunks", [])[:3] if isinstance(data.get("chunks"), list) else []:
            if not isinstance(chunk, dict):
                continue
            chunks.append({**chunk, "text": trim_text(str(chunk.get("text") or ""), text_limit)})
        data["chunks"] = chunks
        compact.append(data)
    return compact[-10:]


def compact_material_read_results(results: list[Any], *, node: str = "") -> list[dict[str, Any]]:
    if not results:
        return []
    visible_agents = {
        "RequirementAnalyst": {"RequirementAnalyst"},
        "Planner": {"RequirementAnalyst"},
        "ContentWriter": {"RequirementAnalyst", "ContentWriter"},
        "StyleDesigner": {"RequirementAnalyst", "ContentWriter"},
        "HTMLCoder": {"RequirementAnalyst", "ContentWriter"},
        "Verifier": {"RequirementAnalyst", "ContentWriter", "Verifier"},
        "SafetyReviewer": {"RequirementAnalyst", "ContentWriter", "Verifier"},
        "Finalizer": {"RequirementAnalyst", "ContentWriter", "Verifier"},
    }.get(node, {"RequirementAnalyst", "ContentWriter", "Verifier"})
    text_limit = material_read_text_limit(node)
    total_budget = material_read_total_budget(node)
    compact: list[dict[str, Any]] = []
    seen: set[tuple[str, str, int]] = set()
    used_chars = 0
    for result in results:
        data = public_value(result)
        if not isinstance(data, dict) or str(data.get("agent") or "") not in visible_agents:
            continue
        key = (str(data.get("agent") or ""), str(data.get("file_id") or data.get("filename") or ""), int(data.get("offset") or 0))
        if key in seen:
            continue
        seen.add(key)
        remaining = max(0, total_budget - used_chars)
        if remaining <= 0:
            break
        text = trim_text(str(data.get("text") or ""), min(text_limit, remaining))
        data["text"] = text
        used_chars += len(text)
        compact.append(data)
    return compact[-10:]


def material_read_text_limit(node: str) -> int:
    if node == "Verifier":
        return 48000
    if node in {"RequirementAnalyst", "ContentWriter"}:
        return 24000
    return 700


def material_read_total_budget(node: str) -> int:
    if node == "Verifier":
        return 96000
    if node in {"RequirementAnalyst", "ContentWriter"}:
        return 72000
    return 2100


def compact_plan_draft(draft: Any) -> dict[str, Any]:
    if draft is None:
        return {}
    data = public_value(draft)
    if isinstance(data.get("section_plan"), list):
        data["section_plan"] = data["section_plan"][:8]
    if isinstance(data.get("execution_checklist"), list):
        data["execution_checklist"] = data["execution_checklist"][:8]
    return data


def compact_content_draft(draft: Any) -> dict[str, Any]:
    if draft is None:
        return {}
    data = public_value(draft)
    if isinstance(data.get("sections"), list):
        compact_sections = []
        for section in data["sections"][:10]:
            if not isinstance(section, dict):
                continue
            compact_sections.append(
                {
                    **section,
                    "body": trim_text(str(section.get("body") or ""), 900),
                    "bullets": [trim_text(str(item), 240) for item in section.get("bullets", [])[:8]] if isinstance(section.get("bullets"), list) else [],
                }
            )
        data["sections"] = compact_sections
    return data


def compact_style_brief(brief: Any) -> dict[str, Any]:
    if brief is None:
        return {}
    data = public_value(brief)
    if isinstance(data.get("implementation_notes"), list):
        data["implementation_notes"] = data["implementation_notes"][:10]
    return data


def trim_html_draft(draft: Any) -> dict[str, Any]:
    if draft is None:
        return {}
    data = public_value(draft)
    data["html"] = trim_text(str(data.get("html") or ""), 12000)
    return data


def compact_html_draft(draft: Any) -> dict[str, Any]:
    if draft is None:
        return {"html_present": False, "html_length": 0, "html": ""}
    data = public_value(draft)
    html = str(data.get("html") or "")
    data["html_present"] = bool(html.strip())
    data["html_length"] = len(html)
    data["html"] = trim_text(html, 7000)
    data["html_tail"] = html[-1200:] if len(html) > 1200 else ""
    return data


def trim_text(value: str, limit: int) -> str:
    text = str(value or "")
    if len(text) <= limit:
        return text
    return text[:limit] + "\n...[truncated]"


def trim_prompt(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    return value[:limit] + "\n...[truncated]"


def extract_json_object(text: str) -> str:
    stripped = str(text or "").strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`").strip()
        if stripped.lower().startswith("json"):
            stripped = stripped[4:].strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return stripped
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start >= 0 and end > start:
        return stripped[start : end + 1]
    return stripped


def extract_html_document(text: str) -> str:
    stripped = str(text or "").strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`").strip()
        if stripped.lower().startswith("html"):
            stripped = stripped[4:].strip()
    lowered = stripped.lower()
    start = lowered.find("<!doctype html")
    if start < 0:
        start = lowered.find("<html")
    if start >= 0:
        stripped = stripped[start:]
    end = stripped.lower().rfind("</html>")
    if end >= 0:
        stripped = stripped[: end + len("</html>")]
    return stripped


def dataclass_shape(cls: type[Any]) -> Any:
    if not is_dataclass(cls):
        return "object"
    type_hints = get_type_hints(cls)
    return {field.name: type_shape(type_hints.get(field.name, field.type)) for field in fields(cls)}


def type_shape(annotation: Any) -> Any:
    origin = get_origin(annotation)
    args = get_args(annotation)
    if origin is list:
        return [type_shape(args[0] if args else Any)]
    if origin is dict:
        return "object"
    if is_dataclass(annotation):
        return dataclass_shape(annotation)
    if isinstance(annotation, type) and issubclass(annotation, Enum):
        return [item.value for item in annotation]
    if annotation in {str, int, float, bool}:
        return annotation.__name__
    return "value"
