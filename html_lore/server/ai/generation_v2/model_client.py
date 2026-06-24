from __future__ import annotations

import json
from dataclasses import asdict, fields, is_dataclass
from enum import Enum
from importlib import resources
from typing import Any, Protocol, get_args, get_origin, get_type_hints

from html_lore.server.ai.model_client import ModelClient

from .schemas import GenerationState, normalize_for_json
from .skills.loader import LoadedSkill


class GenerationJsonModelClient(Protocol):
    def complete_json(self, *, node: str, schema_name: str, payload: dict[str, Any], attempt: int = 0) -> str:
        ...

    def complete_text(self, *, node: str, payload: dict[str, Any], attempt: int = 0) -> str:
        ...


class ProviderGenerationModelClient:
    def __init__(self, model_client: ModelClient, *, max_prompt_chars: int = 12000, max_tokens: int = 4096) -> None:
        self.model_client = model_client
        self.max_prompt_chars = max(2000, int(max_prompt_chars or 12000))
        self.max_tokens = max(512, int(max_tokens or 4096))

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
                "Keep structured fields concise; downstream agents will expand only where their role requires it.",
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
        response = self.model_client.chat(messages=messages, temperature=0.2, max_tokens=self.max_tokens)
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
        response = self.model_client.chat(messages=messages, temperature=0.2, max_tokens=self.max_tokens)
        return extract_html_document(str(response.get("content") or ""))


def build_provider_generation_client(model_client: ModelClient, *, max_prompt_chars: int, max_tokens: int) -> ProviderGenerationModelClient:
    return ProviderGenerationModelClient(model_client, max_prompt_chars=max_prompt_chars, max_tokens=max_tokens)


def retry_output_rules(attempt: int) -> list[str]:
    if int(attempt or 0) <= 0:
        return []
    return [
        "This is a retry after the previous output failed validation.",
        "Return a smaller strict JSON object that exactly matches the schema.",
        "Use [] for empty lists and {} for empty objects; do not use null for list/object fields.",
    ]


def agent_payload(*, node: str, schema: type[Any], state: GenerationState, fallback: dict[str, Any], skills: tuple[LoadedSkill, ...]) -> dict[str, Any]:
    return normalize_for_json(
        {
            **fallback,
            "_prompt": load_agent_prompt(node),
            "_schema": dataclass_shape(schema),
            "_state": public_generation_state_for_agent(state, node=node),
            "_skills": [public_skill(skill) for skill in skills],
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
        "version": skill.version,
        "source": skill.source,
        "content": skill.content,
    }


def public_generation_state_for_agent(state: GenerationState, *, node: str = "") -> dict[str, Any]:
    parsed = state.parsed_document
    style_ref = state.parsed_style_reference
    common_input = {
        "instruction": state.input.instruction,
        "filename": state.input.filename,
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
            "validation_report": public_value(state.validation_report),
            "safety_report": public_value(state.safety_report),
            "content_draft": compact_content_draft(state.content_draft),
            "style_brief": compact_style_brief(state.style_brief),
            "requirement_brief": public_value(state.requirement_brief),
            "plan_draft": compact_plan_draft(state.plan_draft),
            "parsed_document": compact_parsed_document(parsed),
            "execution_checklist": public_value(state.execution_checklist),
            "revision_round": state.revision_round,
        }
    elif node == "HTMLCoder":
        state_view = {
            "input": common_input,
            "validation_report": public_value(state.validation_report),
            "safety_report": public_value(state.safety_report),
            "content_draft": public_value(state.content_draft),
            "style_brief": public_value(state.style_brief),
            "requirement_brief": public_value(state.requirement_brief),
            "plan_draft": compact_plan_draft(state.plan_draft),
            "html_draft": compact_html_draft(state.html_draft),
            "parsed_document": compact_parsed_document(parsed),
            "parsed_style_reference": compact_parsed_document(style_ref),
            "revision_round": state.revision_round,
        }
    else:
        state_view = {
            "input": common_input,
            "parsed_document": public_parsed_document(parsed),
            "parsed_style_reference": public_parsed_document(style_ref),
            "requirement_brief": public_value(state.requirement_brief),
            "plan_draft": public_value(state.plan_draft),
            "content_draft": public_value(state.content_draft),
            "style_brief": public_value(state.style_brief),
            "html_draft": trim_html_draft(state.html_draft),
            "validation_report": public_value(state.validation_report),
            "safety_report": public_value(state.safety_report),
            "execution_checklist": public_value(state.execution_checklist),
            "revision_round": state.revision_round,
        }
    return normalize_for_json(state_view)


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
    return data


def compact_parsed_document(parsed: Any) -> dict[str, Any]:
    if parsed is None:
        return {}
    data = public_value(parsed)
    data["plain_text"] = trim_text(str(data.get("plain_text") or ""), 1200)
    return data


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
