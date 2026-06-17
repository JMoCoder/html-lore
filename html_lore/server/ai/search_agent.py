from __future__ import annotations

import json
from typing import Any

from .agents import strip_code_fences
from .model_client import ModelClient
from .qa_search_plan import QASearchPlan, build_qa_search_plan
from .registry import load_agent, load_prompt
from .search_planner import MAX_EXTERNAL_QUERY_CHARS, SearchPlan, drop_internal_url_tokens, prepare_external_search_query


ALLOWED_SEARCH_INTENTS = {
    "general",
    "version_lookup",
    "policy_lookup",
    "official_docs",
    "official_version",
    "entity_background",
    "entity_ownership",
    "entity_team",
    "entity_registry",
    "entity_relationship",
    "case_search",
    "research",
}
ALLOWED_LOCALITY_HINTS = {"global", "china", "japan", "us"}
ALLOWED_LANGUAGE_HINTS = {"zh", "en", "ja"}


class SearchPlannerAgent:
    def __init__(self, model_client: ModelClient | None = None, *, max_queries: int = 5) -> None:
        self.model_client = model_client
        self.max_queries = max(1, min(int(max_queries or 5), 8))
        self.agent = load_agent("knowledge_qa.search_planner_agent.v1")
        self.prompt = load_prompt(self.agent.prompt_template)

    def plan(
        self,
        *,
        question: str,
        planner: dict[str, Any],
        policy: dict[str, Any],
        context: dict[str, Any],
        local_evidence: dict[str, Any],
    ) -> dict[str, Any]:
        fallback = build_qa_search_plan(question, planner=planner, context=context).public_report()
        fallback["planner_mode"] = "heuristic_fallback"
        if str(policy.get("mode") or "") != "web_research":
            fallback["enabled_by_policy"] = False
            fallback["effective_should_search"] = False
            return fallback
        if self.model_client is None:
            fallback["enabled_by_policy"] = True
            fallback["effective_should_search"] = bool(fallback.get("should_search"))
            return fallback
        try:
            messages = build_search_planner_messages(
                self.prompt.render({}),
                question=question,
                planner=planner,
                policy=policy,
                context=context,
                local_evidence=local_evidence,
            )
            response = self.model_client.chat(messages=messages, temperature=0.0, max_tokens=700)
            decoded = decode_search_planner_json(str(response.get("content") or ""))
            report = sanitize_search_planner_output(
                decoded,
                fallback=fallback,
                question=question,
                max_queries=self.max_queries,
            )
            report["enabled_by_policy"] = True
            report["effective_should_search"] = bool(report.get("should_search"))
            report["planner_mode"] = "llm"
            report["agent_trace"] = [self.agent.public_dict()]
            report["prompt_trace"] = [self.prompt.public_dict()]
            report["model"] = str(response.get("model") or "")
            report["usage"] = response.get("usage") if isinstance(response.get("usage"), dict) else {}
            return report
        except Exception as exc:
            fallback["enabled_by_policy"] = True
            fallback["effective_should_search"] = bool(fallback.get("should_search"))
            fallback["planner_mode"] = "fallback_model_error"
            fallback["error"] = {"type": exc.__class__.__name__, "message": str(exc)}
            fallback["agent_trace"] = [self.agent.public_dict()]
            fallback["prompt_trace"] = [self.prompt.public_dict()]
            return fallback


def build_search_planner_messages(
    system_prompt: str,
    *,
    question: str,
    planner: dict[str, Any],
    policy: dict[str, Any],
    context: dict[str, Any],
    local_evidence: dict[str, Any],
) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": json.dumps(
                {
                    "question": question,
                    "task_planner": compact_mapping(planner),
                    "expansion_policy": compact_mapping(policy),
                    "context": compact_context(context),
                    "local_evidence_signal": compact_mapping(local_evidence),
                },
                ensure_ascii=False,
            ),
        },
    ]


def decode_search_planner_json(content: str) -> dict[str, Any]:
    text = str(content or "").strip()
    if not text:
        return {}
    if text.startswith("```"):
        text = strip_code_fences(text)
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        text = text[start : end + 1]
    return json.loads(text)


def sanitize_search_planner_output(
    decoded: Any,
    *,
    fallback: dict[str, Any],
    question: str,
    max_queries: int,
) -> dict[str, Any]:
    if not isinstance(decoded, dict):
        return dict(fallback)
    should_search = parse_bool(decoded.get("should_search"), default=bool(fallback.get("should_search")))
    intent = str(decoded.get("search_intent") or nested_search_value(fallback, "search_intent") or "general").strip().lower()
    if intent not in ALLOWED_SEARCH_INTENTS:
        intent = str(nested_search_value(fallback, "search_intent") or "general")
    locality_hint = str(decoded.get("locality_hint") or fallback.get("locality_hint") or "global").strip().lower()
    if locality_hint not in ALLOWED_LOCALITY_HINTS:
        locality_hint = str(fallback.get("locality_hint") or "global")
    language_hint = str(decoded.get("language_hint") or fallback.get("language_hint") or "en").strip().lower()
    if language_hint not in ALLOWED_LANGUAGE_HINTS:
        language_hint = str(fallback.get("language_hint") or "en")
    queries = sanitize_query_list(decoded.get("queries"), fallback.get("queries"), max_queries=max_queries)
    if should_search and not queries:
        prepared, _ = prepare_external_search_query(question)
        queries = [prepared] if prepared else []
    plan = SearchPlan(
        original_query=queries[0] if queries else str(question or "").strip()[:MAX_EXTERNAL_QUERY_CHARS],
        intent=intent,
        queries=queries,
        required_terms=sanitize_short_list(decoded.get("required_terms"), limit=6, max_chars=40),
        preferred_domains=sanitize_domain_list(decoded.get("preferred_domains"), limit=6),
        authoritative_required=parse_bool(decoded.get("authoritative_required"), default=bool(nested_search_value(fallback, "authoritative_required"))),
        query_expansions=[],
        evidence_terms=sanitize_short_list(decoded.get("evidence_terms"), limit=12, max_chars=32),
    )
    return QASearchPlan(
        should_search=bool(should_search and queries),
        plan=plan if should_search and queries else None,
        locality_hint=locality_hint,
        language_hint=language_hint,
        reason=str(decoded.get("reason") or fallback.get("reason") or "search_planner_agent").strip()[:240],
    ).public_report()


def sanitize_query_list(value: Any, fallback: Any, *, max_queries: int) -> list[str]:
    raw_values = value if isinstance(value, list) else fallback
    queries: list[str] = []
    seen: set[str] = set()
    for item in raw_values or []:
        query = drop_internal_url_tokens(" ".join(str(item or "").split()))
        query = query[:MAX_EXTERNAL_QUERY_CHARS].strip()
        key = query.lower()
        if not query or key in seen:
            continue
        queries.append(query)
        seen.add(key)
        if len(queries) >= max_queries:
            break
    return queries


def sanitize_short_list(value: Any, *, limit: int, max_chars: int) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    if not isinstance(value, list):
        return result
    for item in value:
        text = " ".join(str(item or "").split())[:max_chars].strip("：:，,。.;；、()（）[]【】\"' ")
        key = text.lower()
        if not text or key in seen:
            continue
        result.append(text)
        seen.add(key)
        if len(result) >= limit:
            break
    return result


def sanitize_domain_list(value: Any, *, limit: int) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    if not isinstance(value, list):
        return result
    for item in value:
        text = str(item or "").strip().lower()
        text = text.replace("https://", "").replace("http://", "").strip("/")
        if not text or "/" in text or len(text) > 80:
            continue
        if text in seen:
            continue
        result.append(text)
        seen.add(text)
        if len(result) >= limit:
            break
    return result


def nested_search_value(report: dict[str, Any], key: str) -> Any:
    search = report.get("search") if isinstance(report.get("search"), dict) else {}
    return search.get(key)


def parse_bool(value: Any, *, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "yes", "1", "search"}:
            return True
        if normalized in {"false", "no", "0", "none"}:
            return False
    return default


def compact_context(context: dict[str, Any]) -> dict[str, Any]:
    items = context.get("items") if isinstance(context.get("items"), list) else []
    return {
        "scope": context.get("scope"),
        "source_mode": context.get("source_mode"),
        "item_count": context.get("item_count") or len(items),
        "items": [
            {
                "id": item.get("id"),
                "title": item.get("title"),
                "summary": item.get("summary"),
                "tags": item.get("tags") if isinstance(item.get("tags"), list) else [],
                "collection": item.get("collection"),
            }
            for item in items[:8]
            if isinstance(item, dict)
        ],
    }


def compact_mapping(value: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    allowed = {
        "intent",
        "retrieval_mode",
        "should_expand",
        "should_search",
        "search_intent",
        "locality",
        "reason",
        "mode",
        "confidence",
        "planner_intent",
        "local_evidence_signal",
        "source_count",
        "top_score",
        "sufficient",
    }
    return {key: value.get(key) for key in allowed if key in value}
