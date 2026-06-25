from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

from html_lore.server.ai.providers import ProviderCallError

from ..fake_model import FakeGenerationModelClient
from ..model_client import GenerationJsonModelClient, agent_payload
from ..schema_loader import AgentOutputSchemaError, parse_dataclass_json
from ..schemas import AgentArtifact, ChecklistStatus, GenerationStage, GenerationState, SkillTraceEntry, normalize_for_json
from ..skills.loader import LoadedSkill, load_default_skills_for_agent
from ..state import complete_stage, fail_stage, retry_stage, start_stage


MAX_SCHEMA_RETRIES = 2
MAX_PROVIDER_RETRIES = 2


@dataclass(frozen=True)
class GenerationAgentResult:
    state: GenerationState
    message: str = ""


class GenerationAgent:
    name = "GenerationAgent"
    stage = GenerationStage.QUEUED
    output_schema: type[Any] | None = None

    def __init__(self, model_client: GenerationJsonModelClient | None = None) -> None:
        self.model_client = model_client or FakeGenerationModelClient()
        self.skills = load_default_skills_for_agent(self.name)

    def run(self, state: GenerationState) -> GenerationAgentResult:
        next_state = start_stage(state, self.stage, agent=self.name, message=f"{self.name} started.")
        try:
            output = self.invoke_structured(next_state)
            next_state = self.apply_output(next_state, output)
            next_state = self.record_agent_artifact(next_state, output)
            next_state = self.record_skill_trace(next_state)
            next_state = self.update_execution_checklist(next_state, ChecklistStatus.COMPLETED)
            next_state = complete_stage(next_state, self.stage, message=f"{self.name} completed.", metadata=self.output_metadata(output, next_state))
            return GenerationAgentResult(state=next_state, message=f"{self.name} completed.")
        except AgentOutputSchemaError as exc:
            next_state = self.record_node_retry(next_state)
            retries = next_state.same_node_retries.get(self.name, 0)
            if retries <= MAX_SCHEMA_RETRIES:
                next_state = retry_stage(next_state, self.stage, message=str(exc), metadata=self.error_metadata(exc, next_state))
                return self.run(next_state)
            next_state = self.update_execution_checklist(next_state, ChecklistStatus.FAILED, notes=str(exc))
            next_state = fail_stage(next_state, self.stage, message=str(exc), retryable=True, metadata=self.error_metadata(exc, next_state))
            return GenerationAgentResult(state=next_state, message=str(exc))
        except ProviderCallError as exc:
            next_state = self.record_node_retry(next_state)
            retries = next_state.same_node_retries.get(self.name, 0)
            if retries <= MAX_PROVIDER_RETRIES:
                next_state = retry_stage(next_state, self.stage, message=str(exc), metadata=self.error_metadata(exc, next_state))
                return self.run(next_state)
            next_state = self.update_execution_checklist(next_state, ChecklistStatus.FAILED, notes=str(exc))
            next_state = fail_stage(next_state, self.stage, message=str(exc), retryable=True, metadata=self.error_metadata(exc, next_state))
            return GenerationAgentResult(state=next_state, message=str(exc))

    def invoke_structured(self, state: GenerationState) -> Any:
        if self.output_schema is None:
            raise AgentOutputSchemaError(f"{self.name} has no output schema.")
        raw = self.model_client.complete_json(
            node=self.name,
            schema_name=self.output_schema.__name__,
            payload=agent_payload(node=self.name, schema=self.output_schema, state=state, fallback=self.fake_payload(state), skills=self.skills),
            attempt=state.same_node_retries.get(self.name, 0),
        )
        return parse_dataclass_json(raw, self.output_schema)

    def fake_payload(self, state: GenerationState) -> dict[str, Any]:
        return {}

    def apply_output(self, state: GenerationState, output: Any) -> GenerationState:
        raise NotImplementedError

    def record_node_retry(self, state: GenerationState) -> GenerationState:
        retries = dict(state.same_node_retries)
        retries[self.name] = retries.get(self.name, 0) + 1
        return replace(state, same_node_retries=retries)

    def record_skill_trace(self, state: GenerationState) -> GenerationState:
        if not self.skills:
            return state
        seen = {(entry.agent, entry.id) for entry in state.skill_trace}
        trace = list(state.skill_trace)
        for skill in self.skills:
            if (self.name, skill.id) in seen:
                continue
            trace.append(skill_trace_entry(self.name, skill))
        return replace(state, skill_trace=trace)

    def update_execution_checklist(self, state: GenerationState, status: ChecklistStatus, *, notes: str = "") -> GenerationState:
        if not state.execution_checklist:
            return state
        checklist = []
        changed = False
        for item in state.execution_checklist:
            if checklist_item_owner_matches_agent(item.owner, self.name):
                checklist.append(replace(item, status=status, notes=notes or item.notes))
                changed = True
            else:
                checklist.append(item)
        return replace(state, execution_checklist=checklist) if changed else state

    def record_agent_artifact(self, state: GenerationState, output: Any) -> GenerationState:
        artifact = self.build_agent_artifact(state, output)
        if artifact is None:
            return state
        return replace(state, agent_artifacts=[*state.agent_artifacts, artifact])

    def build_agent_artifact(self, state: GenerationState, output: Any) -> AgentArtifact | None:
        if output is None:
            return None
        title = self.name
        summary = ""
        output_summary = ""
        quality_score = 0.0
        warnings: list[str] = []
        data: dict[str, Any] = {}
        if self.name == "RequirementAnalyst":
            title = "Requirement analysis"
            summary = short_text(getattr(output, "user_goal", "") or getattr(output, "source_summary", ""), 220)
            output_summary = summarize_list("success criteria", getattr(output, "success_criteria", [])) or summarize_list("must include", getattr(output, "must_include", []))
            warnings = safe_string_list(getattr(output, "uncertainty", []), limit=4)
            data = {
                "target_use": str(getattr(output, "target_use", "") or ""),
                "audience": short_text(getattr(output, "audience", ""), 160),
                "output_type": str(getattr(output, "output_type", "") or ""),
                "must_include": safe_string_list(getattr(output, "must_include", []), limit=8),
                "constraints": safe_string_list(getattr(output, "constraints", []), limit=8),
                "style_preferences": safe_string_list(getattr(output, "style_preferences", []), limit=6),
                "uncertainty": safe_string_list(getattr(output, "uncertainty", []), limit=6),
                "success_criteria": safe_string_list(getattr(output, "success_criteria", []), limit=8),
            }
        elif self.name == "Planner":
            title = "Plan"
            summary = short_text(getattr(output, "page_goal", "") or getattr(output, "information_architecture", ""), 220)
            output_summary = summarize_count("sections", getattr(output, "section_plan", [])) or short_text(getattr(output, "content_strategy", ""), 180)
            warnings = safe_string_list(getattr(output, "risk_points", []), limit=4)
            data = {
                "page_goal": short_text(getattr(output, "page_goal", ""), 260),
                "information_architecture": short_text(getattr(output, "information_architecture", ""), 360),
                "content_strategy": short_text(getattr(output, "content_strategy", ""), 360),
                "visual_strategy": short_text(getattr(output, "visual_strategy", ""), 360),
                "section_plan": public_section_plan(getattr(output, "section_plan", [])),
                "verification_targets": safe_string_list(getattr(output, "verification_targets", []), limit=8),
                "risk_points": safe_string_list(getattr(output, "risk_points", []), limit=8),
            }
        elif self.name == "ContentWriter":
            title = str(getattr(output, "title", "") or "Content draft")
            summary = short_text(getattr(output, "summary", ""), 260)
            output_summary = summarize_count("sections", getattr(output, "sections", [])) or summarize_list("key points", getattr(output, "key_points", []))
            warnings = safe_string_list(getattr(output, "omitted_items", []), limit=4)
            data = {
                "title": short_text(getattr(output, "title", ""), 180),
                "subtitle": short_text(getattr(output, "subtitle", ""), 180),
                "summary": short_text(getattr(output, "summary", ""), 420),
                "sections": public_content_sections(getattr(output, "sections", [])),
                "key_points": safe_string_list(getattr(output, "key_points", []), limit=8),
                "references_used": safe_string_list(getattr(output, "references_used", []), limit=8),
                "omitted_items": safe_string_list(getattr(output, "omitted_items", []), limit=8),
            }
        elif self.name == "StyleDesigner":
            title = "Style brief"
            summary = short_text(getattr(output, "style_goal", ""), 260)
            output_summary = first_non_empty(
                short_text(getattr(output, "layout_system", ""), 160),
                short_text(getattr(output, "visual_hierarchy", ""), 160),
                summarize_count("palette tokens", getattr(output, "color_palette", [])),
            )
            warnings = safe_string_list(getattr(output, "avoid_styles", []), limit=4)
            data = {
                "style_goal": short_text(getattr(output, "style_goal", ""), 360),
                "design_mode": str(getattr(output, "design_mode", "") or ""),
                "reference_sources": safe_string_list(getattr(output, "reference_sources", []), limit=6),
                "color_palette": public_color_palette(getattr(output, "color_palette", [])),
                "layout_system": short_text(getattr(output, "layout_system", ""), 220),
                "component_style": short_text(getattr(output, "component_style", ""), 220),
                "density": short_text(getattr(output, "density", ""), 80),
                "visual_hierarchy": short_text(getattr(output, "visual_hierarchy", ""), 260),
                "responsive_rules": safe_string_list(getattr(output, "responsive_rules", []), limit=8),
                "avoid_styles": safe_string_list(getattr(output, "avoid_styles", []), limit=8),
            }
        elif self.name == "HTMLCoder":
            html = str(getattr(output, "html", "") or "")
            title = "HTML draft"
            summary = f"{len(html)} chars, static HTML"
            output_summary = summarize_bool_checks(
                {
                    "doctype": "<!doctype html" in html.lower(),
                    "style": "<style" in html.lower(),
                    "script-free": "<script" not in html.lower(),
                }
            )
            warnings = safe_string_list(getattr(output, "render_assumptions", []), limit=4)
            data = {
                "html_chars": len(html),
                "has_doctype": "<!doctype html" in html.lower(),
                "has_style": "<style" in html.lower(),
                "has_script": "<script" in html.lower(),
                "css_notes": safe_string_list(getattr(output, "css_notes", []), limit=5),
                "accessibility_notes": safe_string_list(getattr(output, "accessibility_notes", []), limit=5),
                "responsive_notes": safe_string_list(getattr(output, "responsive_notes", []), limit=5),
            }
        elif self.name == "Verifier":
            title = "Verification"
            summary = f"score {getattr(output, 'score', 0)}"
            quality_score = safe_float(getattr(output, "score", 0))
            output_summary = "passed" if bool(getattr(output, "ok", False)) else "needs attention"
            warnings = [
                *safe_string_list(getattr(output, "missing_parts", []), limit=3),
                *safe_string_list(getattr(output, "unsupported_claims", []), limit=3),
            ][:4]
            data = {
                "ok": bool(getattr(output, "ok", False)),
                "score": getattr(output, "score", 0),
                "checked_items": public_checked_items(getattr(output, "checked_items", [])),
                "issues": public_issues(getattr(output, "issues", [])),
                "missing_parts": safe_string_list(getattr(output, "missing_parts", []), limit=8),
                "unsupported_claims": safe_string_list(getattr(output, "unsupported_claims", []), limit=8),
                "route_back_to": str(getattr(output, "route_back_to", "") or ""),
                "retry_instruction": short_text(getattr(output, "retry_instruction", ""), 260),
            }
        elif self.name == "SafetyReviewer":
            title = "Safety review"
            summary = str(getattr(output, "risk_level", "") or "")
            output_summary = "passed" if bool(getattr(output, "ok", False)) else "blocked or warning"
            warnings = safe_string_list(getattr(output, "warnings", []), limit=4)
            data = {
                "ok": bool(getattr(output, "ok", False)),
                "risk_level": str(getattr(output, "risk_level", "") or ""),
                "issues": public_issues(getattr(output, "issues", [])),
                "blocked_items": safe_string_list(getattr(output, "blocked_items", []), limit=8),
                "warnings": safe_string_list(getattr(output, "warnings", []), limit=8),
                "requires_user_confirmation": bool(getattr(output, "requires_user_confirmation", False)),
            }
        elif self.name == "Finalizer":
            title = "Final proposal"
            summary = short_text(getattr(output, "title", ""), 220)
            output_summary = first_non_empty(
                short_text(getattr(output, "safety_summary", ""), 180),
                f"ready for {str(getattr(output, 'target_collection', '') or 'inbox')}",
            )
            data = {
                "title": short_text(getattr(output, "title", ""), 180),
                "target_collection": str(getattr(output, "target_collection", "") or ""),
                "tags": safe_string_list(getattr(output, "tags", []), limit=8),
                "source_files": safe_string_list(getattr(output, "source_files", []), limit=8),
                "source_links": safe_string_list(getattr(output, "source_links", []), limit=8),
                "safety_summary": short_text(getattr(output, "safety_summary", ""), 220),
                "html_chars": len(str(getattr(output, "html", "") or "")),
            }
        else:
            summary = output.__class__.__name__
            data = {"output_kind": output.__class__.__name__}
        quality_score = quality_score_for_agent(self.name, output, default=quality_score)
        usage = build_usage_summary(self.name, state, output)
        usage.update(consume_model_usage(self.model_client, self.name))
        sensitive_phrases = sensitive_phrases_for_state(state)
        return AgentArtifact(
            agent=self.name,
            stage=self.stage,
            title=redact_sensitive_text(short_text(title, 160), sensitive_phrases),
            summary=redact_sensitive_text(summary, sensitive_phrases),
            input_summary=redact_sensitive_text(build_input_summary_for_agent(state, self.name), sensitive_phrases),
            output_summary=redact_sensitive_text(short_text(output_summary, 260), sensitive_phrases),
            quality_score=quality_score,
            usage=usage,
            warnings=safe_string_list(redact_artifact_data(warnings, sensitive_phrases), limit=6, item_limit=180),
            data=normalize_for_json(redact_artifact_data(data, sensitive_phrases)),
        )

    def output_metadata(self, output: Any, state: GenerationState) -> dict[str, Any]:
        metadata: dict[str, Any] = {"retry_count": int(state.same_node_retries.get(self.name, 0))}
        if hasattr(output, "html"):
            metadata["output_kind"] = "html"
            metadata["output_chars"] = len(str(getattr(output, "html") or ""))
        elif hasattr(output, "sections"):
            metadata["output_kind"] = "content"
            metadata["section_count"] = len(getattr(output, "sections") or [])
        elif hasattr(output, "section_plan"):
            metadata["output_kind"] = "plan"
            metadata["section_count"] = len(getattr(output, "section_plan") or [])
        elif hasattr(output, "score"):
            metadata["output_kind"] = "review"
            metadata["score"] = getattr(output, "score")
        elif hasattr(output, "risk_level"):
            metadata["output_kind"] = "safety"
            metadata["risk_level"] = str(getattr(output, "risk_level") or "")
        else:
            metadata["output_kind"] = output.__class__.__name__
        return metadata

    def error_metadata(self, exc: Exception, state: GenerationState) -> dict[str, Any]:
        return {
            "error_type": exc.__class__.__name__,
            "retry_count": int(state.same_node_retries.get(self.name, 0)),
        }


def checklist_item_owner_matches_agent(owner: str, agent_name: str) -> bool:
    normalized_owner = "".join(str(owner or "").lower().split())
    normalized_agent = "".join(str(agent_name or "").lower().split())
    aliases = {
        "writer": "contentwriter",
        "contentwriter": "contentwriter",
        "contentwriteragent": "contentwriter",
        "designer": "styledesigner",
        "styledesigner": "styledesigner",
        "styledesigneragent": "styledesigner",
        "coder": "htmlcoder",
        "htmlcoder": "htmlcoder",
        "htmlcoderagent": "htmlcoder",
        "verifier": "verifier",
        "verifieragent": "verifier",
        "safety": "safetyreviewer",
        "safetyreviewer": "safetyreviewer",
        "safetyrevieweragent": "safetyreviewer",
        "planner": "planner",
        "planneragent": "planner",
        "requirementanalyst": "requirementanalyst",
        "requirementanalystagent": "requirementanalyst",
        "finalizer": "finalizer",
        "finalizeragent": "finalizer",
    }
    return aliases.get(normalized_owner, normalized_owner) == aliases.get(normalized_agent, normalized_agent)


def skill_trace_entry(agent_name: str, skill: LoadedSkill) -> SkillTraceEntry:
    return SkillTraceEntry(id=skill.id, title=skill.title, agent=agent_name, version=skill.version, source=skill.source)


def first_non_empty(*values: str) -> str:
    for value in values:
        if str(value or "").strip():
            return str(value).strip()
    return ""


def short_text(value: str, limit: int = 280) -> str:
    cleaned = " ".join(str(value or "").split())
    return cleaned[:limit]


def safe_float(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def summarize_count(label: str, values: Any) -> str:
    if isinstance(values, list) and values:
        return f"{len(values)} {label}"
    return ""


def summarize_list(label: str, values: Any) -> str:
    items = safe_string_list(values, limit=3, item_limit=60)
    return f"{label}: {', '.join(items)}" if items else ""


def summarize_bool_checks(values: dict[str, bool]) -> str:
    passed = [key for key, value in values.items() if value]
    failed = [key for key, value in values.items() if not value]
    parts = []
    if passed:
        parts.append(f"passed: {', '.join(passed)}")
    if failed:
        parts.append(f"attention: {', '.join(failed)}")
    return "; ".join(parts)


def build_input_summary_for_agent(state: GenerationState, agent_name: str) -> str:
    parsed = state.parsed_document
    style_ref = state.parsed_style_reference
    source_bits: list[str] = []
    if state.input.filename:
        source_bits.append(f"source file {state.input.filename}")
    if parsed and parsed.plain_text:
        source_bits.append(f"{len(parsed.plain_text)} source chars")
    if style_ref and state.input.reference_file_name:
        source_bits.append(f"style reference {state.input.reference_file_name}")
    if state.input.instruction:
        source_bits.append("user instruction")
    if agent_name == "RequirementAnalyst":
        return ", ".join(source_bits) or "generation request"
    if agent_name == "Planner":
        return "requirement brief and parsed document"
    if agent_name == "ContentWriter":
        return "plan draft, requirement brief, parsed document"
    if agent_name == "StyleDesigner":
        return "requirement brief, plan draft, style reference"
    if agent_name == "HTMLCoder":
        return "content draft and style brief"
    if agent_name == "Verifier":
        return "HTML draft, plan, content, and style brief"
    if agent_name == "SafetyReviewer":
        return "HTML draft and validation report"
    if agent_name == "Finalizer":
        return "validated HTML and metadata proposal"
    return "workflow state"


def build_usage_summary(agent_name: str, state: GenerationState, output: Any) -> dict[str, Any]:
    usage: dict[str, Any] = {
        "revision_round": int(state.revision_round or 0),
        "retry_count": int(state.same_node_retries.get(agent_name, 0)),
    }
    if hasattr(output, "html"):
        usage["output_chars"] = len(str(getattr(output, "html") or ""))
    elif hasattr(output, "sections"):
        usage["section_count"] = len(getattr(output, "sections") or [])
    elif hasattr(output, "section_plan"):
        usage["section_count"] = len(getattr(output, "section_plan") or [])
    return usage


def consume_model_usage(model_client: Any, agent_name: str) -> dict[str, Any]:
    consume = getattr(model_client, "consume_last_usage", None)
    if not callable(consume):
        return {}
    usage = consume(agent_name)
    if not isinstance(usage, dict):
        return {}
    result: dict[str, Any] = {}
    for key in ("input_tokens", "output_tokens", "total_tokens"):
        raw = usage.get(key)
        if isinstance(raw, bool):
            continue
        if isinstance(raw, (int, float)):
            result[key] = int(raw)
    return result


def quality_score_for_agent(agent_name: str, output: Any, *, default: float = 0.0) -> float:
    if output is None:
        return 0.0
    if agent_name == "Verifier":
        score = safe_float(getattr(output, "score", default))
        return clamp_score(score / 100 if score > 1 else score)
    if agent_name == "RequirementAnalyst":
        return field_presence_score(
            output,
            [
                "user_goal",
                "source_summary",
                "target_use",
                "output_type",
                "must_include",
                "success_criteria",
                "audience",
                "style_preferences",
            ],
        )
    if agent_name == "Planner":
        return field_presence_score(
            output,
            [
                "page_goal",
                "information_architecture",
                "content_strategy",
                "visual_strategy",
                "section_plan",
                "verification_targets",
                "risk_points",
            ],
        )
    if agent_name == "ContentWriter":
        return field_presence_score(output, ["title", "summary", "sections", "key_points", "references_used"])
    if agent_name == "StyleDesigner":
        return field_presence_score(
            output,
            ["style_goal", "color_palette", "layout_system", "component_style", "visual_hierarchy", "responsive_rules"],
        )
    if agent_name == "HTMLCoder":
        html = str(getattr(output, "html", "") or "")
        checks = [
            bool(html.strip()),
            "<!doctype html" in html.lower(),
            "<html" in html.lower(),
            "<style" in html.lower(),
            "<script" not in html.lower(),
            bool(getattr(output, "accessibility_notes", None)),
            bool(getattr(output, "responsive_notes", None)),
        ]
        return clamp_score(sum(1 for item in checks if item) / len(checks))
    if agent_name == "SafetyReviewer":
        ok = bool(getattr(output, "ok", False))
        risk_level = str(getattr(output, "risk_level", "") or "").lower()
        issues = getattr(output, "issues", []) or []
        blocked = getattr(output, "blocked_items", []) or []
        score = 1.0 if ok else 0.55
        if risk_level in {"high", "critical"}:
            score -= 0.35
        elif risk_level in {"medium"}:
            score -= 0.15
        if issues:
            score -= 0.1
        if blocked:
            score -= 0.25
        return clamp_score(score)
    if agent_name == "Finalizer":
        return field_presence_score(output, ["title", "html", "target_collection", "tags", "source_files", "safety_summary"])
    return clamp_score(default)


def field_presence_score(output: Any, fields: list[str]) -> float:
    if not fields:
        return 0.0
    passed = 0
    for field_name in fields:
        value = getattr(output, field_name, None)
        if isinstance(value, str) and value.strip():
            passed += 1
        elif isinstance(value, (list, tuple, dict)) and value:
            passed += 1
        elif value not in (None, "", [], {}, ()):
            passed += 1
    return clamp_score(passed / len(fields))


def clamp_score(value: float) -> float:
    try:
        score = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, round(score, 2)))


def sensitive_phrases_for_state(state: GenerationState) -> list[str]:
    values = [
        state.input.instruction,
        state.input.filename,
        state.input.reference_file_name,
    ]
    phrases: list[str] = []
    if state.parsed_document:
        values.append(state.parsed_document.plain_text)
    if state.parsed_style_reference:
        values.append(state.parsed_style_reference.plain_text)
        for hint in state.parsed_style_reference.style_hints:
            value = str(hint.value or "").strip()
            if value:
                phrases.append(value)
    if state.parsed_document:
        for hint in state.parsed_document.style_hints:
            value = str(hint.value or "").strip()
            if value:
                phrases.append(value)
    for value in values:
        text = " ".join(str(value or "").split())
        if not text:
            continue
        if len(text) >= 12:
            phrases.append(text)
        parts = [part.strip() for part in text.replace("。", ".").replace("，", ",").replace("\n", ".").split(".")]
        phrases.extend(part for part in parts if len(part) >= 12)
        words = text.split()
        for size in range(4, min(9, len(words) + 1)):
            for index in range(0, len(words) - size + 1):
                phrase = " ".join(words[index : index + size]).strip()
                if len(phrase) >= 12:
                    phrases.append(phrase)
    unique: list[str] = []
    seen: set[str] = set()
    for phrase in phrases:
        key = phrase.lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(phrase)
    return unique[:200]


def redact_artifact_data(value: Any, phrases: list[str]) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            redacted[key] = redact_artifact_data(item, phrases)
        return redacted
    if isinstance(value, list):
        return [redact_artifact_data(item, phrases) for item in value]
    if isinstance(value, str):
        return redact_sensitive_text(value, phrases)
    return value


def redact_sensitive_text(value: str, phrases: list[str]) -> str:
    text = str(value or "")
    for phrase in phrases:
        if not phrase:
            continue
        text = text.replace(phrase, "[redacted]")
    return text


def safe_string_list(values: Any, *, limit: int = 8, item_limit: int = 180) -> list[str]:
    if not isinstance(values, list):
        return []
    return [short_text(str(value), item_limit) for value in values[:limit] if str(value or "").strip()]


def public_section_plan(sections: Any) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    if not isinstance(sections, list):
        return result
    for section in sections[:8]:
        result.append(
            {
                "id": short_text(getattr(section, "id", ""), 80),
                "title": short_text(getattr(section, "title", ""), 160),
                "purpose": short_text(getattr(section, "purpose", ""), 220),
                "expected_content": safe_string_list(getattr(section, "expected_content", []), limit=5),
            }
        )
    return result


def public_content_sections(sections: Any) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    if not isinstance(sections, list):
        return result
    for section in sections[:10]:
        result.append(
            {
                "id": short_text(getattr(section, "id", ""), 80),
                "title": short_text(getattr(section, "title", ""), 160),
                "body_preview": short_text(getattr(section, "body", ""), 220),
            }
        )
    return result


def public_color_palette(colors: Any) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    if not isinstance(colors, list):
        return result
    for color in colors[:8]:
        result.append(
            {
                "name": short_text(getattr(color, "name", ""), 80),
                "value": short_text(getattr(color, "value", ""), 40),
                "usage": short_text(getattr(color, "usage", ""), 120),
            }
        )
    return result


def public_checked_items(items: Any) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    if not isinstance(items, list):
        return result
    for item in items[:10]:
        result.append(
            {
                "id": short_text(getattr(item, "id", ""), 80),
                "title": short_text(getattr(item, "title", ""), 160),
                "passed": bool(getattr(item, "passed", False)),
                "notes": short_text(getattr(item, "notes", ""), 180),
            }
        )
    return result


def public_issues(issues: Any) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    if not isinstance(issues, list):
        return result
    for issue in issues[:10]:
        result.append(
            {
                "code": short_text(getattr(issue, "code", ""), 80),
                "message": short_text(getattr(issue, "message", ""), 220),
                "severity": short_text(getattr(issue, "severity", ""), 40),
            }
        )
    return result


def public_dict(value: Any) -> dict[str, Any]:
    return normalize_for_json(asdict(value))
