from dataclasses import replace

from ..schemas import ContentDraft, GenerationStage
from .base import GenerationAgent, first_non_empty, short_text


class ContentWriterAgent(GenerationAgent):
    name = "ContentWriter"
    stage = GenerationStage.WRITING_CONTENT
    output_schema = ContentDraft

    def fake_payload(self, state):
        goal = state.requirement_brief.user_goal if state.requirement_brief else state.input.instruction
        mode = str(getattr(state.requirement_brief, "source_handling_mode", "") or "source_grounded_rewrite") if state.requirement_brief else "source_grounded_rewrite"
        if mode in {"faithful_adaptation", "extractive_conversion"} and state.parsed_document and not any(result.agent in {"RequirementAnalyst", "ContentWriter"} for result in state.material_read_results):
            material = state.parsed_document.materials[0] if state.parsed_document.materials else None
            if material:
                return faithful_read_request_payload(goal, material, mode)
        source = material_context_text(state) or (state.parsed_document.plain_text if state.parsed_document else "")
        recall_source = material_recall_text(state)
        if recall_source:
            source = recall_source
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
            "material_queries": [] if any(result.agent == "ContentWriter" for result in state.material_recall_results) else [{"id": "content_evidence", "query": first_non_empty(goal, state.input.instruction, "source evidence for planned sections"), "purpose": "Collect evidence needed to write the planned sections."}],
            "material_read_requests": [],
            "evidence_used": [result.query for result in state.material_recall_results if result.agent in {"RequirementAnalyst", "ContentWriter"}],
            "workbook_inspect_requests": [],
        }

    def apply_output(self, state, output):
        return replace(
            state,
            content_draft=output,
            html_draft=None,
            visual_check_report=None,
            validation_report=None,
            safety_report=None,
            create_note_proposal=None,
            revision_round=state.revision_round + 1 if state.validation_report or state.safety_report else state.revision_round,
        )


def material_context_text(state) -> str:
    context = state.temporary_material_context
    if not context:
        return ""
    parts = [f"{chunk.filename}: {chunk.text}" for chunk in context.selected_chunks[:8]]
    return "\n\n".join(parts)


def material_recall_text(state) -> str:
    parts = []
    for result in state.material_recall_results:
        if result.agent not in {"RequirementAnalyst", "ContentWriter"}:
            continue
        for chunk in result.chunks:
            parts.append(f"{chunk.filename}: {chunk.text}")
    return "\n\n".join(parts)


def faithful_read_request_payload(goal: str, material, mode: str) -> dict:
    return {
        "title": first_non_empty(goal, "Generated HTML Note"),
        "subtitle": "Source-faithful draft",
        "summary": "Reading source material before drafting because source fidelity is required.",
        "sections": [],
        "key_points": [],
        "references_used": [],
        "material_queries": [],
        "material_read_requests": [
            {
                "id": "source_fidelity_read",
                "action": "read_file",
                "file_id": material.file_id,
                "filename": material.filename,
                "limit": 96000 if mode == "extractive_conversion" else 48000,
                "purpose": "Read original material before drafting a source-faithful conversion.",
            }
        ],
        "evidence_used": [],
        "workbook_inspect_requests": [],
    }
