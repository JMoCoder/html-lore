from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .external_search import ExternalSearchAdapter, ExternalSearchResult, ExternalSearchUnavailable, sanitize_external_results
from .search_planner import SearchPlan, plan_external_search, verify_planned_sources


INTENT_MAX_RESULTS = {
    "official_version": 3,
    "version_lookup": 3,
    "official_docs": 4,
    "general": 5,
    "entity_background": 6,
    "entity_team": 6,
    "entity_registry": 6,
    "entity_ownership": 8,
    "entity_relationship": 8,
    "policy_lookup": 8,
    "case_search": 10,
    "research": 10,
}
DEFAULT_TOTAL_CANDIDATE_LIMIT = 24


@dataclass(frozen=True)
class ResearchResult:
    sources: list[dict[str, Any]]
    status: dict[str, Any]
    trace: list[dict[str, Any]]


class ResearchWorkflow:
    name = "ResearchQAWorkflow.beta"

    def __init__(self, external_search: ExternalSearchAdapter) -> None:
        self.external_search = external_search

    def run(self, query: str) -> ResearchResult:
        return self.run_plan(plan_research_query(query))

    def run_plan(self, plan: SearchPlan) -> ResearchResult:
        status: dict[str, Any] = {"provider": self.external_search.name, "available": self.external_search.available}
        trace: list[dict[str, Any]] = []
        if not self.external_search.available:
            status["message"] = "External content expansion is not configured."
            trace.append({"node": "ExternalSearchAvailabilityNode", "status": "unavailable"})
            return ResearchResult(sources=[], status=status, trace=trace)

        status.update(plan.public_report())
        trace.append({"node": "ResearchQueryPlannerNode", "status": "completed", "query_count": len(plan.queries), "intent": plan.intent})
        if not plan.queries:
            status["message"] = "External search query is empty after safety filtering."
            return ResearchResult(sources=[], status=status, trace=trace)

        limits = research_limits_for_plan(plan, base_max_results=max(1, int(getattr(self.external_search, "max_results", 5) or 5)))
        max_results = limits["per_query_max_results"]
        status.update(limits)
        raw_results: list[ExternalSearchResult] = []
        for query_index, search_query in enumerate(plan.queries, start=1):
            try:
                query_results = self.external_search.search(search_query, max_results=max_results)
            except ExternalSearchUnavailable as exc:
                status.update({"available": False, "message": str(exc)})
                trace.append({"node": "ExternalSearchProviderNode", "status": "unavailable", "query_index": query_index})
                return ResearchResult(sources=[], status=status, trace=trace)
            raw_results.extend(query_results)
            trace.append({"node": "ExternalSearchProviderNode", "status": "completed", "query_index": query_index, "result_count": len(query_results)})
            if enough_authoritative_results(raw_results, plan, target_count=max_results):
                break
            if len(raw_results) >= limits["total_candidate_limit"]:
                trace.append({"node": "ResearchCandidateLimitNode", "status": "completed", "candidate_count": len(raw_results), "limit": limits["total_candidate_limit"]})
                break

        sources, dropped = verify_research_sources(raw_results)
        trace.append({"node": "ResearchSourceVerifierNode", "status": "completed", "selected_count": len(sources), "dropped_count": dropped})
        planned_sources, plan_verify_report = verify_planned_sources(sources, plan)
        trace.append({"node": "ResearchPlanVerifierNode", "status": "completed", **plan_verify_report})
        merged_sources, merge_report = merge_research_evidence(planned_sources, max_results=max_results)
        trace.append({"node": "ResearchEvidenceMergerNode", "status": "completed", **merge_report})
        status.update({
            "available": True,
            "count": len(merged_sources),
            "dropped": dropped + plan_verify_report["dropped_count"],
            "queried": True,
            "workflow": self.name,
            **merge_report,
        })
        return ResearchResult(sources=merged_sources, status=status, trace=trace)


def plan_research_query(query: Any) -> SearchPlan:
    return plan_external_search(query)


def research_limits_for_plan(plan: SearchPlan, *, base_max_results: int, total_candidate_limit: int = DEFAULT_TOTAL_CANDIDATE_LIMIT) -> dict[str, int]:
    base = max(1, min(int(base_max_results or 5), 20))
    query_count = max(1, len(plan.queries))
    intent_limit = max(1, min(int(INTENT_MAX_RESULTS.get(plan.intent, base)), 20))
    plus_cap = max(base, min(10, 20))
    total_limit = max(base, min(int(total_candidate_limit or DEFAULT_TOTAL_CANDIDATE_LIMIT), 40))
    distributed_limit = max(1, (total_limit + query_count - 1) // query_count)
    per_query = min(intent_limit, plus_cap, distributed_limit)
    return {
        "max_results": per_query,
        "per_query_max_results": per_query,
        "base_max_results": base,
        "intent_max_results": intent_limit,
        "total_candidate_limit": total_limit,
    }


def verify_research_sources(results: list[ExternalSearchResult]) -> tuple[list[dict[str, Any]], int]:
    return sanitize_external_results(results)


def merge_research_evidence(sources: list[dict[str, Any]], *, max_results: int = 5) -> tuple[list[dict[str, Any]], dict[str, int]]:
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for source in sources:
        key = str(source.get("url") or source.get("title") or "").strip().lower()
        if not key or key in seen:
            continue
        deduped.append(source)
        seen.add(key)
        if len(deduped) >= max(1, int(max_results or 5)):
            break
    return deduped, {"external_evidence_count": len(deduped)}


def enough_authoritative_results(results: list[ExternalSearchResult], plan: SearchPlan, *, target_count: int) -> bool:
    safe, _ = verify_research_sources(results)
    verified, _ = verify_planned_sources(safe, plan)
    if plan.authoritative_required:
        return len(verified) >= max(1, min(2, target_count))
    return len(verified) >= target_count
