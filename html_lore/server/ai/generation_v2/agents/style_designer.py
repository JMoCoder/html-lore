from dataclasses import replace

from ..schemas import DesignMode, GenerationStage, StyleBrief
from .base import GenerationAgent


class StyleDesignerAgent(GenerationAgent):
    name = "StyleDesigner"
    stage = GenerationStage.DESIGNING_STYLE
    output_schema = StyleBrief

    def fake_payload(self, state):
        mode = "reference_guided_design" if state.parsed_style_reference else "default_free_design"
        style_hints = state.parsed_style_reference.style_hints if state.parsed_style_reference else []
        color_values = [hint.value for hint in style_hints if hint.kind.endswith(":color")][:3]
        palette = [
            {"name": "ink", "value": "#172033", "usage": "body text"},
            {"name": "accent", "value": "#2563eb", "usage": "section accents"},
            {"name": "surface", "value": "#f7fafc", "usage": "page background"},
        ]
        if color_values:
            palette = [{"name": f"reference-{index + 1}", "value": value, "usage": "reference style hint"} for index, value in enumerate(color_values)]
        return {
            "style_goal": "Readable knowledge note with restrained visual hierarchy.",
            "design_mode": mode,
            "reference_sources": [state.input.reference_file_name] if state.parsed_style_reference else [],
            "color_palette": palette,
            "typography": {"font_family": "system-ui, sans-serif", "heading_style": "bold", "body_style": "regular", "scale": "comfortable"},
            "layout_system": "single-column responsive article",
            "component_style": "simple sections",
            "density": "medium",
            "visual_hierarchy": "title, summary, sections, takeaways",
            "responsive_rules": ["Keep content width readable.", "Stack sections on narrow screens."],
            "avoid_styles": ["remote assets", "complex scripts"],
            "implementation_notes": [f"{hint.kind}: {hint.value}" for hint in style_hints[:8]],
        }

    def apply_output(self, state, output: StyleBrief):
        return replace(
            state,
            style_brief=output if isinstance(output.design_mode, DesignMode) else output,
            html_draft=None,
            visual_check_report=None,
            validation_report=None,
            safety_report=None,
            create_note_proposal=None,
            revision_round=state.revision_round + 1 if state.validation_report or state.safety_report else state.revision_round,
        )
