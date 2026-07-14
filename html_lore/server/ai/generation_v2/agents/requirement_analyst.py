from dataclasses import replace

from ..schemas import GenerationStage, RequirementBrief
from .base import GenerationAgent, first_non_empty, short_text


class RequirementAnalystAgent(GenerationAgent):
    name = "RequirementAnalyst"
    stage = GenerationStage.ANALYZING_REQUIREMENTS
    output_schema = RequirementBrief

    def fake_payload(self, state):
        source = material_context_text(state) or (state.parsed_document.plain_text if state.parsed_document else "")
        recall_source = material_recall_text(state)
        if recall_source:
            source = recall_source
        style_preferences = []
        if state.input.theme != "default":
            style_preferences.append(f"theme: {state.input.theme}")
        if state.input.style_preference != "default":
            style_preferences.append(f"style preference: {state.input.style_preference}")
        if state.input.reference_style != "default":
            style_preferences.append(f"reference style: {state.input.reference_style}")
        if state.input.reference_file_name:
            style_preferences.append(f"reference file: {state.input.reference_file_name}")
        constraints = ["Generate a self-contained static HTML note."]
        if state.input.target_use != "default":
            constraints.append(f"Target use: {state.input.target_use}.")
        if state.input.audience != "default":
            constraints.append(f"Audience: {state.input.audience}.")
        return {
            "user_goal": first_non_empty(state.input.instruction, "Create an HTML note from the uploaded material."),
            "target_use": state.input.target_use,
            "audience": state.input.audience if state.input.audience != "default" else "general reader",
            "output_type": "html_note",
            "source_handling_mode": infer_source_handling_mode(state.input.instruction),
            "source_summary": short_text(source, 320),
            "must_include": [item.title for item in (state.parsed_document.outline if state.parsed_document else [])[:5]],
            "constraints": constraints,
            "style_preferences": style_preferences,
            "reference_style_files": [state.input.reference_file_name] if state.input.reference_file_name else [],
            "success_criteria": ["Preserve source intent.", "Produce readable static HTML.", "Avoid unsupported claims."],
            "material_queries": [] if state.material_recall_results else [{"id": "source_overview", "query": first_non_empty(state.input.instruction, state.input.filename, "uploaded material overview"), "purpose": "Confirm the most relevant uploaded material evidence before finalizing requirements."}],
            "material_read_requests": [],
            "workbook_inspect_requests": [],
            "decision": "continue",
            "decision_reason": "Uploaded material provides enough capability for the requested output.",
            "capability_gaps": [],
            "accepted_degradations": [],
        }

    def apply_output(self, state, output):
        return replace(state, requirement_brief=output)


def material_context_text(state) -> str:
    context = state.temporary_material_context
    if not context:
        return ""
    parts: list[str] = []
    for file in context.files:
        parts.append(f"File: {file.filename}\nPreview: {file.preview}")
    for chunk in context.selected_chunks:
        parts.append(f"Chunk {chunk.id} from {chunk.filename}\n{chunk.text}")
    return "\n\n".join(parts)


def material_recall_text(state) -> str:
    parts = []
    for result in state.material_recall_results:
        if result.agent != "RequirementAnalyst":
            continue
        for chunk in result.chunks:
            parts.append(f"{chunk.filename}: {chunk.text}")
    return "\n\n".join(parts)


def infer_source_handling_mode(instruction: str) -> str:
    text = str(instruction or "").lower()
    if any(marker in text for marker in ("禁止增加", "禁止添加", "禁止修改", "准确完整", "完整与准确", "原文", "verbatim", "exact", "do not add", "do not modify")):
        return "extractive_conversion"
    if any(marker in text for marker in ("忠实", "faithful", "preserve", "保留", "仅做视觉", "只做视觉")):
        return "faithful_adaptation"
    if any(marker in text for marker in ("创作", "扩写", "brainstorm", "inspired by", "自由", "new")):
        return "free_synthesis"
    return "source_grounded_rewrite"
