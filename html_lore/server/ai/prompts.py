from __future__ import annotations

from typing import Any


def build_qa_answer_messages(arguments: dict[str, Any], state: dict[str, Any]) -> list[dict[str, str]]:
    question = str(arguments.get("question") or state.get("query") or "").strip()
    context_output = tool_output(state, "context.resolve")
    evidence_pack = tool_output(state, "evidence.gate") or tool_output(state, "evidence.build")
    planner = state.get("plan_metadata", {}).get("planner") if isinstance(state.get("plan_metadata"), dict) else {}
    context_title = str(context_output.get("context_title") or "Current context")
    chunks = evidence_pack.get("chunks") if isinstance(evidence_pack.get("chunks"), list) else []
    sources = evidence_pack.get("sources") if isinstance(evidence_pack.get("sources"), list) else []
    intent = str(planner.get("intent") or "summary")
    research = tool_output(state, "external.research")
    search_plan = research.get("search_plan") if isinstance(research.get("search_plan"), dict) else {}

    return [
        {
            "role": "system",
            "content": (
                "You are HTMlore's knowledge-base QA agent. Answer as a knowledgeable assistant, "
                "not as a retrieval log. Use the supplied evidence when it is relevant. If the evidence "
                "is insufficient and external expansion is not enabled, say that the current context is "
                "insufficient. Do not invent citations. Put verification sources at the end instead of "
                "interrupting the answer body. Adapt the answer style to the task intent: summary should "
                "be concise, concept clarification should define and explain, explain_deeper should expand "
                "with structure, current_info should separate verified current facts from background context."
            ),
        },
        {
            "role": "user",
            "content": "\n\n".join(
                [
                    f"TASK_INTENT:\n{intent}",
                    f"USER_QUESTION:\n{question}",
                    f"CURRENT_CONTEXT:\n{context_title}",
                    f"SEARCH_PLAN:\n{format_search_plan(search_plan)}",
                    f"EVIDENCE_CHUNKS:\n{format_chunks(chunks)}",
                    f"AVAILABLE_SOURCES:\n{format_sources(sources)}",
                    "OUTPUT_REQUIREMENTS:\n"
                    "- Give a direct, naturally organized answer.\n"
                    "- Follow TASK_INTENT when choosing structure and level of detail.\n"
                    "- If TASK_INTENT is explain_deeper, expand with 3-5 coherent points instead of a short definition.\n"
                    "- If TASK_INTENT is current_info, start with currently verified facts, then add concise context, and clearly say when external evidence is missing or region-limited.\n"
                    "- If TASK_INTENT is concept_clarify, define first, then explain why it matters in the current note context.\n"
                    "- Do not start every sentence with source-oriented phrases.\n"
                    "- If you cite, only use source numbers listed in AVAILABLE_SOURCES.\n"
                    "- End with one compact line starting with `来源：` when sources are available.",
                ],
            ),
        },
    ]


def tool_output(state: dict[str, Any], tool_id: str) -> dict[str, Any]:
    outputs = state.get("tool_outputs") if isinstance(state.get("tool_outputs"), dict) else {}
    value = outputs.get(tool_id)
    return dict(value) if isinstance(value, dict) else {}


def format_chunks(chunks: list[Any], *, limit: int = 8) -> str:
    lines: list[str] = []
    for chunk in chunks[:limit]:
        if not isinstance(chunk, dict):
            continue
        source_index = chunk.get("source_index") or "?"
        chunk_index = chunk.get("chunk_index") or "?"
        title = str(chunk.get("title") or chunk.get("item_id") or "Untitled")
        snippet = compact_text(str(chunk.get("snippet") or ""), limit=900)
        lines.append(f"[source {source_index}, chunk {chunk_index}] {title}\n{snippet}")
    return "\n\n".join(lines) if lines else "(none)"


def format_sources(sources: list[Any], *, limit: int = 12) -> str:
    lines: list[str] = []
    for source in sources[:limit]:
        if not isinstance(source, dict):
            continue
        index = source.get("source_index") or "?"
        title = str(source.get("title") or source.get("item_id") or source.get("url") or "Untitled")
        if source.get("kind") == "external":
            lines.append(f"[{index}] {title} - {source.get('url') or ''}".rstrip())
        else:
            lines.append(f"[{index}] {title}")
    return "\n".join(lines) if lines else "(none)"


def compact_text(value: str, *, limit: int) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "..."


def format_search_plan(value: dict[str, Any]) -> str:
    if not isinstance(value, dict) or not value:
        return "(none)"
    lines = []
    for key in ("should_search", "locality_hint", "language_hint", "reason"):
        if key in value:
            lines.append(f"{key}: {value[key]}")
    search = value.get("search") if isinstance(value.get("search"), dict) else {}
    if search:
        for key in ("search_intent", "preferred_domains", "required_terms", "authoritative_required"):
            if key in search:
                lines.append(f"{key}: {search[key]}")
    return "\n".join(lines) if lines else "(none)"
