from dataclasses import replace

from ..schemas import ContentDraft, GenerationStage
from .base import GenerationAgent, first_non_empty, short_text


class ContentWriterAgent(GenerationAgent):
    name = "ContentWriter"
    stage = GenerationStage.WRITING_CONTENT
    output_schema = ContentDraft

    def fake_payload(self, state):
        goal = state.requirement_brief.user_goal if state.requirement_brief else state.input.instruction
        source = state.parsed_document.plain_text if state.parsed_document else ""
        title = first_non_empty(goal, state.input.filename, "Generated HTML Note")
        summary = short_text(source, 220) or "Generated from uploaded material."
        return {
            "title": title,
            "subtitle": "AI generated draft",
            "summary": summary,
            "sections": [
                {"id": "overview", "title": "Overview", "body": summary, "bullets": []},
                {"id": "details", "title": "Details", "body": short_text(source, 900), "bullets": ["Source material was parsed.", "Content will be refined by the real model path."]},
                {"id": "takeaways", "title": "Takeaways", "body": "Use this draft as the initial generated note.", "bullets": ["Review the generated page.", "Edit details as needed."]},
            ],
            "key_points": ["Parsed source material", "Structured HTML note", "Static output"],
            "references_used": [item.filename for item in (state.parsed_document.source_files if state.parsed_document else [])],
        }

    def apply_output(self, state, output):
        return replace(
            state,
            content_draft=output,
            html_draft=None,
            validation_report=None,
            safety_report=None,
            create_note_proposal=None,
        )
