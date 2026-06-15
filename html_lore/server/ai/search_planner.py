from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse


MAX_EXTERNAL_QUERY_CHARS = 240


@dataclass(frozen=True)
class SearchPlan:
    original_query: str
    intent: str
    queries: list[str]
    required_terms: list[str]
    preferred_domains: list[str]
    authoritative_required: bool
    query_expansions: list[str]

    def public_report(self) -> dict[str, Any]:
        return {
            "search_intent": self.intent,
            "planned_query_count": len(self.queries),
            "required_terms": self.required_terms,
            "preferred_domains": self.preferred_domains,
            "authoritative_required": self.authoritative_required,
            "query_expansions": self.query_expansions,
        }


def plan_external_search(query: Any, *, max_chars: int = MAX_EXTERNAL_QUERY_CHARS) -> SearchPlan:
    prepared, report = prepare_external_search_query(query, max_chars=max_chars)
    intent = classify_search_intent(prepared)
    required_terms = required_entity_terms(prepared)
    preferred_domains = preferred_source_domains(prepared, intent)
    authoritative_required = intent in {"official_version", "official_docs"}
    queries = planned_queries(prepared, intent, preferred_domains, max_chars=max_chars)
    return SearchPlan(
        original_query=prepared,
        intent=intent,
        queries=queries,
        required_terms=required_terms,
        preferred_domains=preferred_domains,
        authoritative_required=authoritative_required,
        query_expansions=list(report.get("query_expansions") or []),
    )


def prepare_external_search_query(query: Any, *, max_chars: int = MAX_EXTERNAL_QUERY_CHARS) -> tuple[str, dict[str, Any]]:
    raw = " ".join(str(query or "").split())
    without_internal = drop_internal_url_tokens(raw)
    expanded, expansion_report = expand_search_query_terms(without_internal)
    truncated = len(expanded) > max_chars
    prepared = expanded[:max_chars].strip()
    return prepared, {
        "query_chars": len(prepared),
        "query_truncated": truncated,
        "blocked_internal_url_tokens": prepared != raw[: len(prepared)].strip(),
        **expansion_report,
    }


def expand_search_query_terms(query: str) -> tuple[str, dict[str, Any]]:
    expanded = str(query or "")
    expansions: list[str] = []
    if re.search(r"(?<![A-Za-z0-9])MCP(?![A-Za-z0-9])", expanded) and "Model Context Protocol" not in expanded:
        expanded = f"Model Context Protocol MCP {expanded}"
        expansions.append("mcp_model_context_protocol")
    return expanded, {"query_expansions": expansions}


def drop_internal_url_tokens(value: str) -> str:
    kept: list[str] = []
    for token in str(value or "").split():
        if "://" in token and not is_safe_query_url_token(token):
            continue
        kept.append(token)
    return " ".join(kept)


def is_safe_query_url_token(value: Any) -> bool:
    parsed = urlparse(str(value or "").strip())
    if not parsed.scheme:
        return True
    if parsed.scheme not in {"http", "https"}:
        return False
    host = (parsed.hostname or "").lower()
    if not host:
        return False
    if host in {"localhost", "127.0.0.1", "0.0.0.0"} or host.endswith(".localhost"):
        return False
    if host.startswith(("10.", "192.168.", "169.254.")):
        return False
    return True


def classify_search_intent(query: str) -> str:
    lowered = str(query or "").lower()
    official = any(marker in lowered for marker in ("official", "官网", "官方", "公式"))
    versionish = any(marker in lowered for marker in ("version", "release", "changelog", "发布", "版本", "リリース", "バージョン"))
    docish = any(marker in lowered for marker in ("spec", "specification", "docs", "documentation", "规范", "文档", "ドキュメント"))
    if official and versionish:
        return "official_version"
    if official and docish:
        return "official_docs"
    if versionish:
        return "version_lookup"
    if any(marker in lowered for marker in ("deep research", "深入研究", "深度研究", "多来源", "compare sources")):
        return "research"
    return "general"


def required_entity_terms(query: str) -> list[str]:
    lowered = str(query or "").lower()
    if "model context protocol" in lowered or re.search(r"(?<![a-z0-9])mcp(?![a-z0-9])", lowered):
        return ["model context protocol", "mcp"]
    return []


def preferred_source_domains(query: str, intent: str) -> list[str]:
    lowered = str(query or "").lower()
    if "model context protocol" in lowered or re.search(r"(?<![a-z0-9])mcp(?![a-z0-9])", lowered):
        return ["modelcontextprotocol.io", "github.com/modelcontextprotocol"]
    return []


def planned_queries(query: str, intent: str, preferred_domains: list[str], *, max_chars: int) -> list[str]:
    base = str(query or "").strip()
    candidates = [base]
    if preferred_domains and intent in {"official_version", "official_docs", "version_lookup"}:
        candidates = [
            "Model Context Protocol specification latest version release date site:modelcontextprotocol.io",
            "Model Context Protocol specification changelog release notes site:github.com/modelcontextprotocol",
            "Model Context Protocol official specification version date",
            base,
        ]
    result: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        cleaned = " ".join(str(candidate or "").split())[:max_chars].strip()
        if cleaned and cleaned.lower() not in seen:
            result.append(cleaned)
            seen.add(cleaned.lower())
    return result or [base[:max_chars].strip()]


def verify_planned_sources(sources: list[dict[str, Any]], plan: SearchPlan) -> tuple[list[dict[str, Any]], dict[str, int]]:
    if not sources:
        return [], {"verified_count": 0, "dropped_count": 0}
    kept: list[dict[str, Any]] = []
    dropped = 0
    for source in sources:
        if source_matches_plan(source, plan):
            scored = dict(source)
            score, tier = source_authority_score(scored, plan)
            scored["authority_score"] = score
            scored["authority_tier"] = tier
            kept.append(scored)
        else:
            dropped += 1
    kept = sort_planned_sources(kept)
    return kept, {"verified_count": len(kept), "dropped_count": dropped}


def source_matches_plan(source: dict[str, Any], plan: SearchPlan) -> bool:
    if not plan.required_terms and not plan.authoritative_required:
        return True
    text = " ".join(
        str(source.get(key) or "")
        for key in ("title", "url", "snippet")
    ).lower()
    entity_match = not plan.required_terms or any(term in text for term in plan.required_terms)
    if not entity_match:
        return False
    if not plan.authoritative_required:
        return True
    url = str(source.get("url") or "").lower()
    preferred = any(domain in url for domain in plan.preferred_domains)
    if preferred:
        return True
    authority_markers = ("official", "specification", "release", "changelog", "version", "docs", "documentation")
    return any(marker in text for marker in authority_markers)


def sort_planned_sources(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        sources,
        key=lambda source: (
            -safe_int(source.get("authority_score"), 0),
            str(source.get("title") or "").lower(),
            str(source.get("url") or "").lower(),
        ),
    )


def source_authority_score(source: dict[str, Any], plan: SearchPlan) -> tuple[int, str]:
    text = " ".join(str(source.get(key) or "") for key in ("title", "url", "snippet")).lower()
    url = str(source.get("url") or "").lower()
    parsed = urlparse(url)
    host = parsed.hostname or ""
    path = parsed.path or ""
    score = 0
    tier = "related"
    if any(domain in url for domain in plan.preferred_domains):
        score += 70
        tier = "preferred"
    if host.endswith("modelcontextprotocol.io"):
        score += 30
        tier = "official"
    if any(marker in path for marker in ("/specification", "/docs", "/changelog", "/posts", "/blog", "/release")):
        score += 18
    if any(marker in text for marker in ("specification", "release candidate", "release notes", "changelog", "version", "official")):
        score += 18
    if "/issues/" in path or "/pull/" in path or "/discussions/" in path:
        score -= 28
        if tier == "preferred":
            tier = "community"
    if any(marker in host for marker in ("medium.com", "reddit.com", "news.ycombinator.com")):
        score -= 20
    if plan.required_terms and any(term in text for term in plan.required_terms):
        score += 12
    return max(score, 0), tier


def safe_int(value: Any, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback
