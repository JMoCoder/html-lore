from dataclasses import replace

from ..schemas import CreateNoteProposal, GenerationStage
from .base import GenerationAgent


class FinalizerAgent(GenerationAgent):
    name = "Finalizer"
    stage = GenerationStage.FINALIZING
    output_schema = CreateNoteProposal

    def fake_payload(self, state):
        title = state.content_draft.title if state.content_draft else "Generated HTML Note"
        summary = state.content_draft.summary if state.content_draft else ""
        files = [item.filename for item in (state.parsed_document.source_files if state.parsed_document else [])]
        return {
            "title": title,
            "html": state.html_draft.html if state.html_draft else "",
            "metadata": {
                "title": title,
                "summary": summary,
                "collection": state.input.target_collection or "inbox",
                "tags": ["AI生成"],
                "source_type": state.input.source_type,
                "created_by": "ai_generation_v2",
            },
            "target_collection": state.input.target_collection or "inbox",
            "tags": ["AI生成"],
            "source_files": files,
            "source_links": [link.url for link in (state.parsed_document.links if state.parsed_document else [])],
            "safety_summary": "Safety reviewer passed." if state.safety_report and state.safety_report.ok else "Safety review pending.",
            "generation_trace_id": state.run_id,
        }

    def apply_output(self, state, output):
        return replace(state, create_note_proposal=output)
