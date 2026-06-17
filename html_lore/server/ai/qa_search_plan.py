from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .search_planner import SearchPlan, build_search_plan, prepare_external_search_query


@dataclass(frozen=True)
class QASearchPlan:
    should_search: bool
    plan: SearchPlan | None
    locality_hint: str
    language_hint: str
    reason: str

    def public_report(self) -> dict[str, Any]:
        payload = {
            "should_search": self.should_search,
            "locality_hint": self.locality_hint,
            "language_hint": self.language_hint,
            "reason": self.reason,
        }
        if self.plan is not None:
            payload["search"] = self.plan.public_report()
            payload["queries"] = list(self.plan.queries)
        else:
            payload["search"] = {}
            payload["queries"] = []
        return payload


def build_qa_search_plan(question: str, *, planner: dict[str, Any] | None = None, context: dict[str, Any] | None = None) -> QASearchPlan:
    planner = dict(planner or {})
    context = dict(context or {})
    text = str(question or "").strip()
    lowered = text.lower()
    language_hint = detect_language_hint(text, context)
    locality_hint = detect_locality_hint(text, context, language_hint=language_hint)
    should_search = bool(planner.get("should_search"))
    reason = str(planner.get("reason") or "planner_default")

    if not should_search:
        return QASearchPlan(
            should_search=False,
            plan=None,
            locality_hint=locality_hint,
            language_hint=language_hint,
            reason=reason,
        )

    query = clean_search_operation_terms(text)
    if locality_hint == "china" and not has_country_hint(text):
        query = f"{query} 中国"
    if language_hint == "zh" and not has_language_anchor(query):
        query = f"{query} 中文"
    query_lowered = query.lower()
    if any(marker in lowered or marker in query_lowered for marker in ("政策", "法规", "新规", "监管", "政策变化", "电力市场", "power market", "electricity market", "policy", "regulation")):
        query = f"{query} policy regulation"
    if any(marker in lowered for marker in ("官方", "官网", "official")):
        query = f"{query} official"

    prepared, report = prepare_external_search_query(query)
    plan = build_search_plan(
        prepared,
        report=report,
        intent_override=str(planner.get("search_intent") or ""),
    )
    return QASearchPlan(
        should_search=True,
        plan=plan,
        locality_hint=locality_hint,
        language_hint=language_hint,
        reason=reason,
    )


def search_plan_from_public_report(report: dict[str, Any]) -> SearchPlan | None:
    if not isinstance(report, dict):
        return None
    search = report.get("search") if isinstance(report.get("search"), dict) else {}
    queries = [str(query).strip() for query in report.get("queries") or [] if str(query).strip()]
    if not search or not queries:
        return None
    return SearchPlan(
        original_query=queries[0],
        intent=str(search.get("search_intent") or "general"),
        queries=queries,
        required_terms=[str(term) for term in search.get("required_terms") or [] if str(term).strip()],
        preferred_domains=[str(domain) for domain in search.get("preferred_domains") or [] if str(domain).strip()],
        authoritative_required=bool(search.get("authoritative_required")),
        query_expansions=[str(term) for term in search.get("query_expansions") or [] if str(term).strip()],
        evidence_terms=[str(term) for term in search.get("evidence_terms") or [] if str(term).strip()],
    )


def detect_language_hint(question: str, context: dict[str, Any], *, default: str = "en") -> str:
    text = str(question or "")
    if any("\u4e00" <= char <= "\u9fff" for char in text):
        return "zh"
    title = ""
    items = context.get("items") if isinstance(context.get("items"), list) else []
    if items:
        title = str(items[0].get("title") or "")
    if any("\u4e00" <= char <= "\u9fff" for char in title):
        return "zh"
    return default


def detect_locality_hint(question: str, context: dict[str, Any], *, language_hint: str) -> str:
    question_text = str(question or "").lower()
    context_text = " ".join(str(item.get("title") or "") for item in (context.get("items") or []) if isinstance(item, dict)).lower()
    text = f"{question_text} {context_text}"
    if any(marker in text for marker in ("中国", "china", "国内", "发改", "电力现货", "工商业")):
        return "china"
    if any(marker in text for marker in ("日本", "japan", "日语", "japanese")):
        return "japan"
    if any(marker in text for marker in ("美国", "united states", "usa", "us ")) and language_hint != "zh":
        return "us"
    if language_hint == "zh" and any(marker in question_text for marker in ("政策", "法规", "中国", "国内", "工商业", "电力")):
        return "china"
    return "global"


def has_country_hint(question: str) -> bool:
    lowered = str(question or "").lower()
    return any(marker in lowered for marker in ("中国", "china", "美国", "usa", "united states", "日本", "japan", "英国", "uk"))


def has_language_anchor(question: str) -> bool:
    lowered = str(question or "").lower()
    return any(marker in lowered for marker in ("中文", "english", "英文", "japanese", "日文"))


def clean_search_operation_terms(question: str) -> str:
    cleaned = str(question or "").strip()
    operation_markers = (
        "联网搜索一下",
        "联网查一下",
        "搜索一下",
        "查一下",
        "联网搜索",
        "网上搜索",
        "外部搜索",
        "搜索",
        "search online",
        "web search",
    )
    lowered = cleaned.lower()
    for marker in operation_markers:
        if marker in lowered:
            cleaned = cleaned.replace(marker, " ")
            cleaned = cleaned.replace(marker.title(), " ")
    return " ".join(cleaned.split()) or str(question or "").strip()
