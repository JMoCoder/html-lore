from __future__ import annotations

import re
from dataclasses import dataclass, field
from html import escape
from typing import Any, Protocol

from html_lore.server.shares import scan_share_content


class HtmlGenerationNode(Protocol):
    name: str

    def run(self, state: "HtmlGenerationState") -> None:
        pass


@dataclass
class HtmlGenerationState:
    run_id: str
    conversation_id: str
    spec: dict[str, str]
    context_snapshot: dict[str, Any]
    messages: list[dict[str, Any]]
    generation_intent: dict[str, Any] = field(default_factory=dict)
    content_brief: dict[str, Any] = field(default_factory=dict)
    style_spec: dict[str, Any] = field(default_factory=dict)
    html_draft: str = ""
    qa_report: dict[str, Any] = field(default_factory=dict)
    review_decision: dict[str, Any] = field(default_factory=dict)
    node_trace: list[dict[str, str]] = field(default_factory=list)

    def mark_completed(self, node_name: str) -> None:
        self.node_trace.append({"node": node_name, "status": "completed"})

    def as_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "conversation_id": self.conversation_id,
            "spec": self.spec,
            "context_snapshot": self.context_snapshot,
            "messages": self.messages,
            "generation_intent": self.generation_intent,
            "content_brief": self.content_brief,
            "style_spec": self.style_spec,
            "html_draft": self.html_draft,
            "qa_report": self.qa_report,
            "review_decision": self.review_decision,
            "node_trace": self.node_trace,
        }


class HtmlGenerationGraph:
    name = "HtmlGenerationGraph.beta"

    def __init__(self, nodes: tuple[HtmlGenerationNode, ...] | None = None) -> None:
        self.nodes = nodes or (
            GenerationIntentNode(),
            PMAgentNode(),
            UXAgentNode(),
            CoderAgentNode(),
            QANode(),
            ReviewerNode(),
        )

    def run(self, state: HtmlGenerationState) -> HtmlGenerationState:
        for node in self.nodes:
            node.run(state)
            state.mark_completed(node.name)
        return state


class GenerationIntentNode:
    name = "GenerationIntentNode"

    def run(self, state: HtmlGenerationState) -> None:
        spec = state.spec
        state.generation_intent = {
            "theme": controlled_option(spec.get("theme"), "default"),
            "target_use": controlled_option(spec.get("target_use"), "default"),
            "reference_style": controlled_option(spec.get("reference_style"), "default"),
            "reference_note_id": spec.get("reference_note_id") or "",
            "reference_file_name": spec.get("reference_file_name") or "",
            "reference_file_type": spec.get("reference_file_type") or "",
            "reference_file_size": spec.get("reference_file_size") or "0",
            "style_preference": controlled_option(spec.get("style_preference"), "default"),
            "audience": controlled_option(spec.get("audience"), "default"),
            "uses_style_prompt": any(
                controlled_option(spec.get(key), "default") != "default"
                for key in ("theme", "target_use", "reference_style", "style_preference", "audience")
            ),
        }


class PMAgentNode:
    name = "PMAgentNode"

    def run(self, state: HtmlGenerationState) -> None:
        messages = [message for message in state.messages if isinstance(message, dict)]
        last_user = next((str(message.get("content") or "") for message in reversed(messages) if message.get("role") == "user"), "")
        last_assistant = next((str(message.get("content") or "") for message in reversed(messages) if message.get("role") == "assistant"), "")
        titles = context_titles(state.context_snapshot)
        state.content_brief = {
            "title": summarize_title(last_user, titles),
            "summary": summarize_summary(last_user, last_assistant, titles),
            "sections": [
                {"heading": "Question", "body": last_user or "No user question was captured."},
                {"heading": "Answer", "body": last_assistant or "No assistant answer was captured yet."},
                {"heading": "Referenced Context", "body": "\n".join(titles) if titles else "No context notes were selected."},
            ],
            "tags": infer_tags(last_user, titles),
            "collection": infer_collection(state.context_snapshot),
        }


class UXAgentNode:
    name = "UXAgentNode"

    def run(self, state: HtmlGenerationState) -> None:
        intent = state.generation_intent or {}
        theme = str(intent.get("theme") or "default")
        style_preference = str(intent.get("style_preference") or "default")
        dark = theme == "dark"
        state.style_spec = {
            "theme": theme,
            "style_preference": style_preference,
            "background": "#111827" if dark else "#f8fafc",
            "panel": "#172033" if dark else "#ffffff",
            "text": "#e5edf7" if dark else "#172033",
            "accent": "#0f766e",
        }


class CoderAgentNode:
    name = "CoderAgentNode"

    def run(self, state: HtmlGenerationState) -> None:
        brief = state.content_brief
        style = state.style_spec
        title = escape(str(brief.get("title") or "Generated note"))
        summary = escape(str(brief.get("summary") or "Generated from an HTMlore conversation."))
        sections = brief.get("sections") if isinstance(brief.get("sections"), list) else []
        section_html = "\n".join(
            f"<section><h2>{escape(str(section.get('heading') or 'Section'))}</h2><p>{escape(str(section.get('body') or '')).replace(chr(10), '<br>')}</p></section>"
            for section in sections
            if isinstance(section, dict)
        )
        state.html_draft = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{ font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: {style.get('text')}; background: {style.get('background')}; }}
    body {{ margin: 0; background: {style.get('background')}; color: {style.get('text')}; }}
    main {{ max-width: 920px; margin: 0 auto; padding: 42px 22px 64px; }}
    header {{ border-bottom: 1px solid rgba(15, 118, 110, .26); margin-bottom: 26px; padding-bottom: 22px; }}
    h1 {{ margin: 0 0 12px; font-size: clamp(2rem, 5vw, 3.4rem); line-height: 1.05; }}
    h2 {{ margin: 0 0 10px; color: {style.get('accent')}; }}
    p {{ line-height: 1.72; }}
    section {{ background: {style.get('panel')}; border: 1px solid rgba(15, 118, 110, .16); border-radius: 10px; padding: 20px; margin: 16px 0; box-shadow: 0 18px 42px rgba(15, 23, 42, .08); }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>{title}</h1>
      <p>{summary}</p>
    </header>
    {section_html}
  </main>
</body>
</html>"""


class QANode:
    name = "QANode"

    def run(self, state: HtmlGenerationState) -> None:
        state.qa_report = qa_html(state.html_draft)


class ReviewerNode:
    name = "ReviewerNode"

    def run(self, state: HtmlGenerationState) -> None:
        state.review_decision = review_html(state.html_draft, state.spec)


def qa_html(html: str) -> dict[str, Any]:
    lowered = html.lower()
    if "<html" not in lowered or "</html>" not in lowered:
        return {"ok": False, "message": "Generated HTML is incomplete."}
    if "<script" in lowered:
        return {"ok": False, "message": "Generated HTML contains script, which is not allowed in this beta graph."}
    if len(html.encode("utf-8")) > 2 * 1024 * 1024:
        return {"ok": False, "message": "Generated HTML is too large."}
    return {"ok": True, "message": "QA passed."}


def review_html(html: str, spec: dict[str, str]) -> dict[str, Any]:
    lowered = html.lower()
    if "html_lore_ai_api_key" in lowered or re.search(r"(?<![a-z0-9_-])sk-[a-z0-9_-]{12,}", html, re.IGNORECASE):
        return {"ok": False, "message": "Generated HTML contains a likely secret."}
    if spec.get("audience") == "share" or spec.get("target_use") == "share":
        scan = scan_share_content(html)
        if not scan["shareable"]:
            return {
                "ok": False,
                "message": "Share-target generation failed safety review.",
                "safety": scan,
            }
    return {"ok": True, "message": "Review passed."}


def context_titles(context: dict[str, Any]) -> list[str]:
    items = context.get("items") if isinstance(context.get("items"), list) else []
    return [str(item.get("title") or "") for item in items if isinstance(item, dict) and item.get("title")][:6]


def infer_collection(context: dict[str, Any]) -> str:
    requested = context.get("requested") if isinstance(context.get("requested"), dict) else {}
    if requested.get("collection"):
        return str(requested["collection"])
    items = context.get("items") if isinstance(context.get("items"), list) else []
    collections = [str(item.get("collection") or "") for item in items if isinstance(item, dict) and item.get("collection")]
    return collections[0] if len(set(collections)) == 1 and collections else "AI"


def infer_tags(last_user: str, titles: list[str]) -> list[str]:
    text = " ".join([last_user, *titles])
    candidates = []
    for token in re.findall(r"[A-Za-z][A-Za-z0-9+-]{1,24}", text):
        normalized = token.strip()
        if normalized.lower() in {"what", "does", "cover", "from", "note", "notes", "based"}:
            continue
        if normalized not in candidates:
            candidates.append(normalized)
    return candidates[:6] or ["AI"]


def summarize_title(last_user: str, titles: list[str]) -> str:
    cleaned = re.sub(r"\s+", " ", last_user).strip()
    if cleaned:
        return cleaned[:72]
    return (titles[0] if titles else "Generated knowledge note")[:72]


def summarize_summary(last_user: str, last_assistant: str, titles: list[str]) -> str:
    source = last_assistant or last_user or "Generated from selected HTMlore context."
    cleaned = re.sub(r"\s+", " ", source).strip()
    if titles:
        cleaned = f"Based on {len(titles)} context note(s): {cleaned}"
    return cleaned[:240]


def controlled_option(value: Any, fallback: str) -> str:
    return str(value or fallback).strip() or fallback
