from __future__ import annotations

from typing import Any


MECHANICAL_MARKERS = ("笔记提到", "笔记强调", "原文提到", "原文强调")
STOPWORDS = {
    "about",
    "and",
    "are",
    "answer",
    "available",
    "base",
    "beginner",
    "compare",
    "current",
    "does",
    "explain",
    "for",
    "from",
    "group",
    "in",
    "knowledge",
    "list",
    "mentioned",
    "note",
    "notes",
    "practical",
    "question",
    "say",
    "summarize",
    "summary",
    "the",
    "this",
    "to",
    "topic",
    "topics",
    "what",
    "with",
    "write",
    "这个",
    "当前",
    "总结",
    "概括",
    "笔记",
    "知识库",
}


def evaluate_qa_result(result: dict[str, Any], *, question: str = "") -> dict[str, Any]:
    answer = str(result.get("answer") or "")
    sources = result.get("sources") if isinstance(result.get("sources"), list) else []
    citation = result.get("citation") if isinstance(result.get("citation"), dict) else {}
    error = result.get("error") if isinstance(result.get("error"), dict) else {}
    duplicate_report = duplicate_source_report(sources)
    relevance = source_relevance_report(question, sources)
    mechanical_count = sum(answer.count(marker) for marker in MECHANICAL_MARKERS)
    flags: list[str] = []
    if str(result.get("status") or "") != "completed":
        flags.append("not_completed")
    if error:
        flags.append("has_error")
    if not answer.strip():
        flags.append("empty_answer")
    if mechanical_count:
        flags.append("mechanical_phrasing")
    if duplicate_report["duplicate_count"]:
        flags.append("duplicate_sources")
    if relevance["evaluated"] and relevance["status"] == "weak":
        flags.append("weak_relevance")
    citation_status = str(citation.get("status") or citation.get("reason") or "")
    if citation_status in {"missing_citation", "invalid_reference", "invalid_citation"}:
        flags.append(citation_status)
    if citation.get("invalid_citations"):
        flags.append("invalid_citation")
    flags = list(dict.fromkeys(flags))
    return {
        "status": "needs_attention" if flags else "ok",
        "requires_attention": bool(flags),
        "flags": flags,
        "answer_chars": len(answer.strip()),
        "source_count": len(sources),
        "duplicate_sources": duplicate_report,
        "source_relevance": relevance,
        "mechanical_marker_count": mechanical_count,
        "citation_status": citation_status,
    }


def duplicate_source_report(sources: list[dict[str, Any]]) -> dict[str, Any]:
    seen: dict[str, int] = {}
    duplicates: list[str] = []
    for source in sources:
        key = source_identity(source)
        if not key:
            continue
        seen[key] = seen.get(key, 0) + 1
    for key, count in seen.items():
        if count > 1:
            duplicates.append(key)
    return {"duplicate_count": len(duplicates), "duplicates": duplicates}


def source_identity(source: dict[str, Any]) -> str:
    kind = str(source.get("kind") or "local")
    if kind == "external":
        value = str(source.get("url") or source.get("title") or "").strip().lower()
        return f"external:{value}" if value else ""
    value = str(source.get("item_id") or source.get("title") or "").strip().lower()
    return f"local:{value}" if value else ""


def source_relevance_report(question: str, sources: list[dict[str, Any]]) -> dict[str, Any]:
    if is_generic_overview_question(question):
        return {"evaluated": False, "status": "overview", "overlap": [], "query_terms": []}
    query_tokens = meaningful_tokens(question)
    if not question.strip() or not sources or not query_tokens:
        return {"evaluated": False, "status": "unknown", "overlap": [], "query_terms": sorted(query_tokens)}
    source_tokens: set[str] = set()
    for source in sources:
        source_tokens.update(meaningful_tokens(" ".join([str(source.get("title") or ""), str(source.get("item_id") or ""), str(source.get("url") or "")])))
    overlap = sorted(query_tokens & source_tokens)
    status = "ok" if overlap else "weak"
    return {
        "evaluated": True,
        "status": status,
        "overlap": overlap,
        "query_terms": sorted(query_tokens),
    }


def meaningful_tokens(value: str) -> set[str]:
    import re

    tokens = {token.lower() for token in re.findall(r"[A-Za-z0-9]+|[\u4e00-\u9fff]{2,}", str(value or ""))}
    return {token for token in tokens if len(token) >= 2 and token not in STOPWORDS and not contains_stopword(token)}


def is_generic_overview_question(value: str) -> bool:
    text = str(value or "").lower()
    if any(marker in text for marker in ("summarize the current knowledge base", "current knowledge base", "group the answer by topic")):
        return True
    if any(marker in text for marker in ("总结当前知识库", "概括当前知识库", "按主题")):
        return True
    return False


def contains_stopword(token: str) -> bool:
    return any(stopword in token for stopword in STOPWORDS if len(stopword) >= 2)
