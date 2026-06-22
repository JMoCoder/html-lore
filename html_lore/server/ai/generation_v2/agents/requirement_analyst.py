from dataclasses import replace

from ..schemas import GenerationStage, RequirementBrief
from .base import GenerationAgent, first_non_empty, short_text


class RequirementAnalystAgent(GenerationAgent):
    name = "RequirementAnalyst"
    stage = GenerationStage.ANALYZING_REQUIREMENTS
    output_schema = RequirementBrief

    def fake_payload(self, state):
        source = state.parsed_document.plain_text if state.parsed_document else ""
        return {
            "user_goal": first_non_empty(state.input.instruction, "Create an HTML note from the uploaded material."),
            "target_use": state.input.target_use,
            "audience": state.input.audience if state.input.audience != "default" else "general reader",
            "output_type": "html_note",
            "source_summary": short_text(source, 320),
            "must_include": [item.title for item in (state.parsed_document.outline if state.parsed_document else [])[:5]],
            "constraints": ["Generate a self-contained static HTML note."],
            "style_preferences": [state.input.style_preference] if state.input.style_preference != "default" else [],
            "reference_style_files": [state.input.reference_file_name] if state.input.reference_file_name else [],
            "success_criteria": ["Preserve source intent.", "Produce readable static HTML.", "Avoid unsupported claims."],
        }

    def apply_output(self, state, output):
        return replace(state, requirement_brief=output)
