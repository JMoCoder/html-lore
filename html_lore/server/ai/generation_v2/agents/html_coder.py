from dataclasses import replace
from html import escape

from ..model_client import agent_payload
from ..schema_loader import AgentOutputSchemaError
from ..schemas import GenerationStage, HtmlDraft
from .base import GenerationAgent


class HTMLCoderAgent(GenerationAgent):
    name = "HTMLCoder"
    stage = GenerationStage.CODING_HTML
    output_schema = HtmlDraft

    def invoke_structured(self, state) -> HtmlDraft:
        html = self.model_client.complete_text(
            node=self.name,
            payload=agent_payload(node=self.name, schema=self.output_schema, state=state, fallback=self.fake_payload(state), skills=self.skills),
            attempt=state.same_node_retries.get(self.name, 0),
        )
        if not is_complete_html_document(html):
            raise AgentOutputSchemaError("HTMLCoder output must be a complete HTML document.")
        return HtmlDraft(
            html=html,
            css_notes=["Generated as direct HTML artifact."],
            render_assumptions=["Self-contained static HTML document."],
            accessibility_notes=["Reviewed by downstream verifier."],
            responsive_notes=["Reviewed by downstream verifier."],
        )

    def fake_payload(self, state):
        draft = state.content_draft
        title = escape(draft.title if draft else "Generated HTML Note")
        sections = []
        for section in (draft.sections if draft else []):
            bullets = "".join(f"<li>{escape(item)}</li>" for item in section.bullets)
            bullet_html = f"<ul>{bullets}</ul>" if bullets else ""
            sections.append(f"<section><h2>{escape(section.title)}</h2><p>{escape(section.body)}</p>{bullet_html}</section>")
        html = (
            "<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
            f"<title>{title}</title>"
            "<style>body{margin:0;font-family:system-ui,sans-serif;background:#f7fafc;color:#172033;line-height:1.65}"
            "main{max-width:880px;margin:0 auto;padding:48px 24px}section{margin:28px 0;padding-top:18px;border-top:1px solid #dbe4ef}"
            "h1{font-size:2rem;margin:0 0 12px}h2{font-size:1.25rem;margin:0 0 10px;color:#1d4ed8}p{margin:0 0 12px}</style>"
            f"</head><body><main><h1>{title}</h1><p>{escape(draft.summary if draft else '')}</p>{''.join(sections)}</main></body></html>"
        )
        return {
            "html": html,
            "css_notes": ["Inline CSS for first fake path."],
            "render_assumptions": ["No external assets."],
            "accessibility_notes": ["Uses semantic headings."],
            "responsive_notes": ["Fluid content width."],
        }

    def apply_output(self, state, output):
        return replace(
            state,
            html_draft=output,
            validation_report=None,
            safety_report=None,
            create_note_proposal=None,
            revision_round=state.revision_round + 1 if state.html_draft is not None else state.revision_round,
        )


def is_complete_html_document(value: str) -> bool:
    text = str(value or "").strip().lower()
    return ("<!doctype html" in text or text.startswith("<html")) and "</html>" in text
