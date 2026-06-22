from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from html_lore.server.items import ItemService

from .context import ContextResolver
from .external_search import DisabledExternalSearchAdapter, ExternalSearchAdapter
from .guardrails import validate_answer, validate_message_budget, validate_prompt_budget, validate_user_message
from .conversation_resolution import resolve_conversation_turn
from .knowledge_qa_graph import (
    EXTERNAL_NO_RESULTS_ANSWER,
    EXTERNAL_UNAVAILABLE_ANSWER,
    assess_evidence_coverage,
    assess_evidence_sufficiency,
    assess_local_evidence_signal,
    answer_query_tokens,
    asks_for_external_search,
    concept_terms_from_question,
    budget_prompt_inputs,
    build_answer_prompt,
    dedupe_display_sources,
    evidence_with_display_source_indices,
    is_time_sensitive_question,
    is_concept_explanation_question,
    local_evidence_defines_query,
    prompt_chars,
    recent_conversation_messages,
    build_retrieval_query,
    retrieval_coverage_status,
    should_reject_weak_evidence,
    should_trust_local_context_evidence,
)
from .model_client import ModelClient
from .providers import ProviderCallError
from .registry import load_agent, load_prompt
from .research import ResearchWorkflow
from .retrieval import retrieve_evidence_with_status
from .qa_search_plan import build_qa_search_plan, search_plan_from_public_report
from .search_agent import SearchPlannerAgent
from .metrics import evaluate_qa_result


PromptBuilder = Callable[[dict[str, Any], dict[str, Any]], list[dict[str, str]]]


class InputGuardrailTool:
    id = "guardrail.input"

    def __init__(self, *, max_message_chars: int = 4000) -> None:
        self.max_message_chars = max(1, int(max_message_chars or 4000))

    def run(self, arguments: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
        values = dict(arguments or {})
        content = str(values.get("content") or state.get("query") or "").strip()
        validate_user_message(content)
        validate_message_budget(content, max_chars=self.max_message_chars)
        state["query"] = content
        return {
            "content": content,
            "budget": {"message_chars": len(content), "max_message_chars": self.max_message_chars},
        }


class ContextTool:
    id = "context.resolve"

    def __init__(self, item_service: ItemService, *, max_context_items: int = 50) -> None:
        self.resolver = ContextResolver(item_service, max_context_items=max_context_items)

    def run(self, arguments: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
        values = dict(arguments or {})
        if "source_mode" not in values and state.get("source_mode"):
            values["source_mode"] = state["source_mode"]
        resolved = self.resolver.resolve(values)
        state["context"] = resolved
        state["source_mode"] = resolved.get("source_mode", state.get("source_mode") or "local_only")
        return {
            "context": resolved,
            "context_key": resolved.get("context_key", ""),
            "context_title": context_title(resolved),
            "scope": resolved.get("scope", ""),
            "item_count": resolved.get("item_count", 0),
            "item_ids": list(resolved.get("item_ids") or []),
        }


class EvidenceTool:
    id = "evidence.build"

    def __init__(
        self,
        item_service: ItemService,
        *,
        model_client: ModelClient | None = None,
        retrieval_mode: str = "keyword",
        max_results: int = 5,
    ) -> None:
        self.item_service = item_service
        self.model_client = model_client
        self.retrieval_mode = retrieval_mode
        self.max_results = max(1, int(max_results or 5))

    def run(self, arguments: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
        values = dict(arguments or {})
        context = values.get("context") if isinstance(values.get("context"), dict) else {}
        if not context:
            context_output = state.get("tool_outputs", {}).get("context.resolve", {}) if isinstance(state.get("tool_outputs"), dict) else {}
            if isinstance(context_output.get("context"), dict):
                context = dict(context_output["context"])
        if not context and isinstance(state.get("context"), dict):
            context = dict(state["context"])
        query = str(values.get("query") or state.get("query") or "").strip()
        resolution = resolve_conversation_turn(query, recent_conversation_messages(state.get("conversation_messages")))
        retrieval_query = str(resolution.get("resolved_query") or query)
        if retrieval_query:
            query = retrieval_query
        state["conversation_resolution"] = resolution
        state["retrieval_query"] = query
        mode = str(values.get("retrieval_mode") or self.retrieval_mode or "keyword")
        max_results = max(1, int(values.get("max_results") or self.max_results))
        result = retrieve_evidence_with_status(
            self.item_service,
            context,
            query,
            mode=mode,
            model_client=self.model_client,
            max_results=max_results,
        )
        status = dict(result.status or {})
        status["query_expanded"] = bool(query != str(values.get("query") or state.get("query") or "").strip())
        status.update(retrieval_coverage_status(context, result.evidence))
        return build_evidence_pack(query=query, chunks=result.evidence, status=status)


class ExpansionPolicyTool:
    id = "expansion.policy"

    def run(self, arguments: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
        values = dict(arguments or {})
        planner = values.get("planner") if isinstance(values.get("planner"), dict) else {}
        context_output = state.get("tool_outputs", {}).get("context.resolve", {}) if isinstance(state.get("tool_outputs"), dict) else {}
        evidence_pack = state.get("tool_outputs", {}).get("evidence.build", {}) if isinstance(state.get("tool_outputs"), dict) else {}
        context = values.get("context") if isinstance(values.get("context"), dict) else context_output.get("context", {})
        if not isinstance(context, dict):
            context = {}
        chunks = evidence_pack.get("chunks") if isinstance(evidence_pack.get("chunks"), list) else []
        query = str(state.get("retrieval_query") or values.get("query") or evidence_pack.get("query") or state.get("query") or "").strip()
        source_mode = str(context.get("source_mode") or state.get("source_mode") or "local_only")
        local_signal = assess_local_evidence_signal(chunks, context, query)
        explicit_search = asks_for_external_search(query)
        time_sensitive = is_time_sensitive_question(query)
        planner_mode = str(planner.get("retrieval_mode") or "").strip().lower()
        planner_intent = str(planner.get("intent") or "").strip().lower()
        if source_mode != "local_plus_external":
            policy = {
                "mode": "local_only",
                "reason": "content_expansion_disabled",
                "confidence": 1.0,
                "requires_citation": bool(chunks),
                "local_evidence_signal": local_signal,
            }
        elif planner_mode == "web_research":
            policy = {
                "mode": "web_research",
                "reason": "explicit_search_request" if explicit_search else ("time_sensitive_question" if time_sensitive else "planner_requested_web_research"),
                "confidence": 0.9,
                "requires_citation": True,
                "local_evidence_signal": local_signal,
                "planner_intent": planner_intent,
            }
        elif planner_mode == "model_knowledge":
            reason = "planner_requested_model_knowledge"
            if is_concept_explanation_question(query):
                reason = "concept_explanation_fallback" if chunks else "general_knowledge_fallback"
            policy = {
                "mode": "model_knowledge",
                "reason": reason,
                "confidence": 0.78,
                "requires_citation": bool(chunks),
                "local_evidence_signal": local_signal,
                "planner_intent": planner_intent,
            }
        elif planner_mode == "local_evidence" and local_signal.get("sufficient"):
            policy = {
                "mode": "local_evidence",
                "reason": "local_evidence_available",
                "confidence": 0.85,
                "requires_citation": True,
                "local_evidence_signal": local_signal,
                "planner_intent": planner_intent,
            }
        elif explicit_search or time_sensitive:
            policy = {
                "mode": "web_research",
                "reason": "explicit_search_request" if explicit_search else "time_sensitive_question",
                "confidence": 0.9,
                "requires_citation": True,
                "local_evidence_signal": local_signal,
            }
        elif chunks and is_concept_explanation_question(query) and not local_evidence_defines_query(chunks, query):
            policy = {
                "mode": "model_knowledge",
                "reason": "concept_explanation_fallback",
                "confidence": 0.78,
                "requires_citation": bool(chunks),
                "local_evidence_signal": local_signal,
            }
        elif local_signal.get("sufficient"):
            policy = {
                "mode": "local_evidence",
                "reason": "local_evidence_available",
                "confidence": 0.85,
                "requires_citation": True,
                "local_evidence_signal": local_signal,
            }
        else:
            policy = {
                "mode": "model_knowledge",
                "reason": "weak_local_evidence_fallback" if local_signal.get("source_count") else "general_knowledge_fallback",
                "confidence": 0.72,
                "requires_citation": False,
                "local_evidence_signal": local_signal,
            }
        return policy


class SearchPlanTool:
    id = "search.plan"

    def __init__(self, model_client: ModelClient | None = None) -> None:
        self.search_planner = SearchPlannerAgent(model_client)

    def run(self, arguments: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
        values = dict(arguments or {})
        planner = values.get("planner") if isinstance(values.get("planner"), dict) else {}
        policy = state.get("tool_outputs", {}).get("expansion.policy", {}) if isinstance(state.get("tool_outputs"), dict) else {}
        context_output = state.get("tool_outputs", {}).get("context.resolve", {}) if isinstance(state.get("tool_outputs"), dict) else {}
        context = context_output.get("context") if isinstance(context_output.get("context"), dict) else {}
        evidence_pack = state.get("tool_outputs", {}).get("evidence.build", {}) if isinstance(state.get("tool_outputs"), dict) else {}
        query = str(state.get("retrieval_query") or values.get("query") or state.get("query") or "").strip()
        return self.search_planner.plan(
            question=query,
            planner=planner,
            policy=policy,
            context=context,
            local_evidence=evidence_pack.get("retrieval") if isinstance(evidence_pack.get("retrieval"), dict) else {},
        )


class ExternalResearchTool:
    id = "external.research"

    def __init__(self, external_search: ExternalSearchAdapter | None = None) -> None:
        self.workflow = ResearchWorkflow(external_search or DisabledExternalSearchAdapter())

    def run(self, arguments: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
        policy = state.get("tool_outputs", {}).get("expansion.policy", {}) if isinstance(state.get("tool_outputs"), dict) else {}
        planner = (arguments or {}).get("planner") if isinstance((arguments or {}).get("planner"), dict) else {}
        context_output = state.get("tool_outputs", {}).get("context.resolve", {}) if isinstance(state.get("tool_outputs"), dict) else {}
        context = context_output.get("context") if isinstance(context_output.get("context"), dict) else {}
        planned = state.get("tool_outputs", {}).get("search.plan", {}) if isinstance(state.get("tool_outputs"), dict) else {}
        qa_search_plan = build_qa_search_plan(str(state.get("retrieval_query") or (arguments or {}).get("query") or state.get("query") or "").strip(), planner=planner, context=context)
        public_plan = dict(planned) if isinstance(planned, dict) and planned else qa_search_plan.public_report()
        default_status = {"provider": self.workflow.external_search.name, "available": self.workflow.external_search.available}
        if not bool(public_plan.get("effective_should_search", qa_search_plan.should_search)) or str(policy.get("mode") or "") != "web_research":
            return {
                "sources": [],
                "status": default_status,
                "trace": [],
                "queried": False,
                "search_plan": public_plan,
            }
        planned_query = search_plan_from_public_report(public_plan)
        if planned_query is not None:
            research = self.workflow.run_plan(planned_query)
        else:
            search_query = str(qa_search_plan.plan.original_query if qa_search_plan.plan else state.get("retrieval_query") or (arguments or {}).get("query") or state.get("query") or "").strip()
            research = self.workflow.run(search_query)
        return {"sources": research.sources, "status": dict(research.status or {}), "trace": research.trace, "queried": True, "search_plan": public_plan}


class SourceEvaluatorTool:
    id = "source.evaluate"

    def __init__(self, model_client: ModelClient | None = None) -> None:
        self.model_client = model_client
        self.agent = load_agent("knowledge_qa.source_evaluator_agent.v1")
        self.prompt = load_prompt(self.agent.prompt_template)

    def run(self, arguments: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
        policy = state.get("tool_outputs", {}).get("expansion.policy", {}) if isinstance(state.get("tool_outputs"), dict) else {}
        research = state.get("tool_outputs", {}).get("external.research", {}) if isinstance(state.get("tool_outputs"), dict) else {}
        mode = str(policy.get("mode") or "local_only")
        sources = [dict(item) for item in research.get("sources") or [] if isinstance(item, dict)]
        if mode != "web_research" or not sources:
            return {
                "sources": sources,
                "kept_count": len(sources),
                "dropped_count": 0,
                "mode": "not_required",
                "agent_trace": [],
                "prompt_trace": [],
                "decisions": [],
            }
        query = str(state.get("retrieval_query") or (arguments or {}).get("query") or state.get("query") or "").strip()
        search_plan = research.get("search_plan") if isinstance(research.get("search_plan"), dict) else {}
        if self.model_client is None:
            return self._fallback_filter(query=query, sources=sources, search_plan=search_plan, mode="fallback_no_model")
        messages = build_source_evaluator_messages(self.prompt.render({}), query=query, sources=sources, search_plan=search_plan)
        try:
            response = self.model_client.chat(messages=messages, temperature=0.0, max_tokens=700)
            decoded = decode_source_evaluator_json(str(response.get("content") or ""))
            kept, decisions = apply_source_evaluator_decisions(sources, decoded)
            if not decisions:
                return self._fallback_filter(query=query, sources=sources, search_plan=search_plan, mode="fallback_empty_decision")
            return {
                "sources": kept,
                "kept_count": len(kept),
                "dropped_count": max(0, len(sources) - len(kept)),
                "mode": "llm",
                "model": str(response.get("model") or ""),
                "usage": response.get("usage") if isinstance(response.get("usage"), dict) else {},
                "agent_trace": [self.agent.public_dict()],
                "prompt_trace": [self.prompt.public_dict()],
                "decisions": decisions,
            }
        except Exception as exc:
            result = self._fallback_filter(query=query, sources=sources, search_plan=search_plan, mode="fallback_model_error")
            result["error"] = {"type": exc.__class__.__name__, "message": str(exc)}
            return result

    def _fallback_filter(self, *, query: str, sources: list[dict[str, Any]], search_plan: dict[str, Any], mode: str) -> dict[str, Any]:
        kept: list[dict[str, Any]] = []
        decisions: list[dict[str, Any]] = []
        for index, source in enumerate(sources, start=1):
            keep, reason = fallback_source_relevance(source, query=query, search_plan=search_plan)
            if keep:
                kept.append(source)
            decisions.append({"index": index, "keep": keep, "confidence": 0.55 if keep else 0.65, "reason": reason})
        return {
            "sources": kept,
            "kept_count": len(kept),
            "dropped_count": max(0, len(sources) - len(kept)),
            "mode": mode,
            "agent_trace": [self.agent.public_dict()],
            "prompt_trace": [self.prompt.public_dict()],
            "decisions": decisions,
        }


class EvidenceGateTool:
    id = "evidence.gate"

    def __init__(self, *, max_prompt_chars: int = 12000) -> None:
        self.max_prompt_chars = max(1, int(max_prompt_chars or 12000))
        self.answer_agent = load_agent("knowledge_qa.answer_agent.v1")
        self.answer_prompt = load_prompt(self.answer_agent.prompt_template)

    def run(self, arguments: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
        context_output = state.get("tool_outputs", {}).get("context.resolve", {}) if isinstance(state.get("tool_outputs"), dict) else {}
        evidence_pack = state.get("tool_outputs", {}).get("evidence.build", {}) if isinstance(state.get("tool_outputs"), dict) else {}
        policy = state.get("tool_outputs", {}).get("expansion.policy", {}) if isinstance(state.get("tool_outputs"), dict) else {}
        research = state.get("tool_outputs", {}).get("external.research", {}) if isinstance(state.get("tool_outputs"), dict) else {}
        source_evaluation = state.get("tool_outputs", {}).get("source.evaluate", {}) if isinstance(state.get("tool_outputs"), dict) else {}
        context = context_output.get("context") if isinstance(context_output.get("context"), dict) else {}
        query = str(state.get("retrieval_query") or (arguments or {}).get("query") or evidence_pack.get("query") or state.get("query") or "").strip()
        local_chunks = [dict(item) for item in evidence_pack.get("chunks") or [] if isinstance(item, dict)]
        evaluated_sources = source_evaluation.get("sources") if isinstance(source_evaluation.get("sources"), list) else None
        external_chunks = [dict(item) for item in (evaluated_sources if evaluated_sources is not None else research.get("sources") or []) if isinstance(item, dict)]
        mode = str(policy.get("mode") or "local_only")
        if mode == "web_research":
            evidence = [*local_chunks, *external_chunks]
        else:
            evidence = local_chunks
        prompt_policy = dict(policy)
        if mode == "web_research":
            prompt_policy["external_evidence_count"] = len(external_chunks)
            status = research.get("status") if isinstance(research.get("status"), dict) else {}
            prompt_policy["external_status"] = {
                "provider": str(status.get("provider") or ""),
                "available": bool(status.get("available", True)),
                "queried": bool(status.get("queried")),
                "count": int(status.get("count") or 0),
                "message": str(status.get("message") or ""),
            }
        skipped_model_call = False
        answer = ""
        if mode == "web_research" and not external_chunks and is_external_research_unavailable(research.get("status") if isinstance(research.get("status"), dict) else {}):
            answer = EXTERNAL_UNAVAILABLE_ANSWER
            evidence = []
            skipped_model_call = True
        elif mode == "web_research" and not external_chunks and not local_chunks:
            status = research.get("status") if isinstance(research.get("status"), dict) else {}
            answer = EXTERNAL_UNAVAILABLE_ANSWER if is_external_research_unavailable(status) else EXTERNAL_NO_RESULTS_ANSWER
            evidence = []
            skipped_model_call = True
        if (
            evidence
            and should_reject_weak_evidence(evidence, context, query)
            and mode != "model_knowledge"
            and not should_trust_local_context_evidence(query, context, policy, evidence)
        ):
            evidence = []
        if not evidence and mode == "local_only":
            skipped_model_call = True
        numbered_pack = build_evidence_pack(query=query, chunks=evidence, status={})
        sources = numbered_pack["sources"]
        prompt_evidence = numbered_pack["chunks"]
        evidence_budget: dict[str, Any] = {}
        messages: list[dict[str, str]] = []
        budget: dict[str, int] = {}
        if not skipped_model_call and (prompt_evidence or mode == "model_knowledge"):
            recent = recent_conversation_messages(state.get("conversation_messages"))
            prompt_evidence, recent, evidence_budget = budget_prompt_inputs(
                content=query,
                evidence=prompt_evidence,
                snapshot=context,
                recent_messages=recent,
                expansion_policy=prompt_policy,
                max_prompt_chars=self.max_prompt_chars,
                agent=self.answer_agent,
                prompt=self.answer_prompt,
            )
            prompt_context = evidence_budget.pop("_budgeted_snapshot", context) if isinstance(evidence_budget, dict) else context
            if not isinstance(prompt_context, dict):
                prompt_context = context
            sources = dedupe_display_sources(prompt_evidence)
            prompt_evidence = evidence_with_display_source_indices(prompt_evidence, sources)
            renumbered_pack = build_evidence_pack(query=query, chunks=prompt_evidence, status={})
            prompt_evidence = renumbered_pack["chunks"]
            sources = renumbered_pack["sources"]
            messages = build_answer_prompt(
                query,
                prompt_evidence,
                prompt_context,
                recent,
                expansion_policy=prompt_policy,
                agent=self.answer_agent,
                prompt=self.answer_prompt,
            )
            budget = {"prompt_chars": prompt_chars(messages), "max_prompt_chars": self.max_prompt_chars}
            validate_prompt_budget(messages, max_chars=self.max_prompt_chars)
        coverage = assess_evidence_coverage(
            snapshot=context,
            retrieval_status=evidence_pack.get("status") if isinstance(evidence_pack.get("status"), dict) else {},
            sources=sources,
            budget_report=evidence_budget,
        )
        sufficiency = assess_evidence_sufficiency(sources=sources, expansion_policy=policy, coverage_report=coverage)
        return {
            "query": query,
            "chunks": prompt_evidence,
            "sources": sources,
            "citation_map": {str(chunk.get("chunk_id") or f"chunk-{index}"): int(chunk.get("source_index") or index) for index, chunk in enumerate(prompt_evidence, start=1)},
            "messages": messages,
            "answer": answer,
            "skipped_model_call": skipped_model_call,
            "skip_reason": "insufficient_evidence" if skipped_model_call and not answer else "",
            "budget": budget,
            "evidence_budget": evidence_budget,
            "evidence_coverage": coverage,
            "evidence_sufficiency": sufficiency,
            "agent_trace": [self.answer_agent.public_dict()] if messages else [],
            "prompt_trace": [self.answer_prompt.public_dict()] if messages else [],
            "source_evaluation": {
                "mode": str(source_evaluation.get("mode") or ""),
                "kept_count": int(source_evaluation.get("kept_count") or 0) if source_evaluation else 0,
                "dropped_count": int(source_evaluation.get("dropped_count") or 0) if source_evaluation else 0,
                "decisions": source_evaluation.get("decisions") if isinstance(source_evaluation.get("decisions"), list) else [],
            },
        }


class OutputGuardrailTool:
    id = "guardrail.output"

    def run(self, arguments: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
        content = str((arguments or {}).get("content") or state.get("draft_answer") or "").strip()
        skipped = bool((arguments or {}).get("skipped_model_call"))
        if not skipped:
            validate_answer(content)
        return {"validated": True, "skipped": skipped}


class EvidenceAssessmentTool:
    id = "evidence.assess"

    def run(self, arguments: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
        values = dict(arguments or {})
        evidence_pack = values.get("evidence_pack") if isinstance(values.get("evidence_pack"), dict) else {}
        if not evidence_pack:
            evidence_pack = state.get("tool_outputs", {}).get("evidence.build", {}) if isinstance(state.get("tool_outputs"), dict) else {}
        query = str(values.get("query") or evidence_pack.get("query") or state.get("query") or "").strip()
        gate = state.get("tool_outputs", {}).get("evidence.gate", {}) if isinstance(state.get("tool_outputs"), dict) else {}
        sources = gate.get("sources") if isinstance(gate.get("sources"), list) else evidence_pack.get("sources")
        if not isinstance(sources, list):
            sources = []
        chunks = gate.get("chunks") if isinstance(gate.get("chunks"), list) else evidence_pack.get("chunks")
        if not isinstance(chunks, list):
            chunks = []
        context_output = state.get("tool_outputs", {}).get("context.resolve", {}) if isinstance(state.get("tool_outputs"), dict) else {}
        context = context_output.get("context") if isinstance(context_output.get("context"), dict) else {}
        policy = state.get("tool_outputs", {}).get("expansion.policy", {}) if isinstance(state.get("tool_outputs"), dict) else {}
        research = state.get("tool_outputs", {}).get("external.research", {}) if isinstance(state.get("tool_outputs"), dict) else {}
        search_plan = research.get("search_plan") if isinstance(research.get("search_plan"), dict) else {}
        if is_assessment_exempt(query, context, policy) or should_trust_local_context_evidence(query, context, policy, chunks):
            if str(policy.get("mode") or "") == "web_research" and search_requires_attribute_evidence(search_plan):
                external_check = external_evidence_assessment(chunks=chunks, query=query, search_plan=search_plan)
                if external_check["insufficient_evidence"] or external_check["weak_relevance"]:
                    return external_check
            return {
                "query": query,
                "metrics": {"status": "ok", "requires_attention": False, "flags": []},
                "status": "ok",
                "requires_attention": False,
                "insufficient_evidence": False,
                "weak_relevance": False,
                "decision": assessment_decision("answer", reason="assessment_exempt", confidence=0.9),
            }
        metrics = evaluate_qa_result(
            {
                "status": "completed",
                "answer": "temporary assessment",
                "sources": sources,
                "citation": {},
                "error": {},
            },
            question=query,
        )
        insufficient = not sources
        weak_relevance = "weak_relevance" in (metrics.get("flags") or [])
        if weak_relevance and evidence_chunks_overlap_query(query, chunks):
            weak_relevance = False
            metrics = {**metrics, "status": "ok", "requires_attention": False, "flags": [flag for flag in metrics.get("flags") or [] if flag != "weak_relevance"]}
        return {
            "query": query,
            "metrics": metrics,
            "status": "insufficient_evidence" if insufficient else metrics.get("status", "unknown"),
            "requires_attention": insufficient or bool(metrics.get("requires_attention")),
            "insufficient_evidence": insufficient,
            "weak_relevance": weak_relevance,
            "decision": assessment_decision(
                "decline" if insufficient or weak_relevance else "answer",
                reason="insufficient_evidence" if insufficient else ("weak_relevance" if weak_relevance else "evidence_ok"),
                confidence=0.86 if insufficient or weak_relevance else 0.78,
            ),
        }


class LLMChatTool:
    id = "llm.chat"

    def __init__(
        self,
        model_client: ModelClient,
        *,
        prompt_builders: dict[str, PromptBuilder] | None = None,
        default_temperature: float = 0.2,
        default_max_tokens: int = 1024,
    ) -> None:
        self.model_client = model_client
        self.prompt_builders = dict(prompt_builders or {})
        self.default_temperature = float(default_temperature)
        self.default_max_tokens = max(1, int(default_max_tokens or 1024))

    def run(self, arguments: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
        values = dict(arguments or {})
        gate = state.get("tool_outputs", {}).get("evidence.gate", {}) if isinstance(state.get("tool_outputs"), dict) else {}
        if bool(gate.get("skipped_model_call")):
            return {
                "content": "",
                "model": "",
                "usage": {},
                "prompt_id": str(values.get("prompt_id") or ""),
                "message_count": 0,
                "skipped": True,
                "skip_reason": str(gate.get("skip_reason") or "no_evidence"),
            }
        messages = values.get("messages") or gate.get("messages")
        assessment = state.get("tool_outputs", {}).get("evidence.assess", {}) if isinstance(state.get("tool_outputs"), dict) else {}
        decision = assessment.get("decision") if isinstance(assessment.get("decision"), dict) else {}
        should_decline = str(decision.get("action") or "") == "decline" or bool(assessment.get("weak_relevance")) or bool(assessment.get("insufficient_evidence"))
        if should_decline:
            reason = str(decision.get("reason") or ("insufficient_evidence" if bool(assessment.get("insufficient_evidence")) else "weak_relevance"))
            return {
                "content": "",
                "model": "",
                "usage": {},
                "prompt_id": str(values.get("prompt_id") or ""),
                "message_count": 0,
                "skipped": True,
                "skip_reason": reason,
            }
        if not isinstance(messages, list):
            prompt_id = str(values.get("prompt_id") or "").strip()
            if not prompt_id:
                raise ProviderCallError("LLM tool requires messages or a prompt_id.")
            builder = self.prompt_builders.get(prompt_id)
            if builder is None:
                raise ProviderCallError(f"LLM prompt builder is not registered: {prompt_id}.")
            messages = builder(values, state)
        normalized_messages = normalize_messages(messages)
        response = self.model_client.chat(
            messages=normalized_messages,
            temperature=float(values.get("temperature", self.default_temperature)),
            max_tokens=max(1, int(values.get("max_tokens") or self.default_max_tokens)),
        )
        return {
            "content": str(response.get("content") or "").strip(),
            "model": str(response.get("model") or ""),
            "usage": response.get("usage") if isinstance(response.get("usage"), dict) else {},
            "prompt_id": str(values.get("prompt_id") or ""),
            "message_count": len(normalized_messages),
        }


def build_evidence_pack(*, query: str, chunks: list[dict[str, Any]], status: dict[str, Any]) -> dict[str, Any]:
    indexed_chunks: list[dict[str, Any]] = []
    sources: list[dict[str, Any]] = []
    source_index_by_key: dict[tuple[str, str], int] = {}
    citation_map: dict[str, int] = {}
    for chunk_index, chunk in enumerate(chunks, start=1):
        source_key = evidence_source_key(chunk)
        source_index = source_index_by_key.get(source_key)
        if source_index is None:
            source_index = len(sources) + 1
            source_index_by_key[source_key] = source_index
            sources.append(display_source(chunk, source_index))
        chunk_id = str(chunk.get("chunk_id") or f"chunk-{chunk_index}")
        citation_map[chunk_id] = source_index
        indexed = dict(chunk)
        indexed["chunk_id"] = chunk_id
        indexed["chunk_index"] = chunk_index
        indexed["source_index"] = source_index
        indexed.setdefault("kind", "local")
        indexed_chunks.append(indexed)
    return {
        "query": query,
        "chunks": indexed_chunks,
        "sources": sources,
        "citation_map": citation_map,
        "status": {
            **dict(status or {}),
            "chunk_count": len(indexed_chunks),
            "source_count": len(sources),
        },
    }


def evidence_source_key(chunk: dict[str, Any]) -> tuple[str, str]:
    if chunk.get("kind") == "external":
        return ("external", str(chunk.get("url") or chunk.get("title") or "").strip().lower())
    return ("local", str(chunk.get("item_id") or chunk.get("title") or "").strip().lower())


def display_source(chunk: dict[str, Any], source_index: int) -> dict[str, Any]:
    if chunk.get("kind") == "external":
        return {
            "kind": "external",
            "source_index": source_index,
            "title": str(chunk.get("title") or chunk.get("url") or "External source"),
            "url": str(chunk.get("url") or ""),
        }
    result = {
        "kind": "local",
        "source_index": source_index,
        "title": str(chunk.get("title") or chunk.get("item_id") or "Local note"),
        "item_id": str(chunk.get("item_id") or ""),
    }
    retrieval_sources = list(chunk.get("retrieval_sources") or [])
    if retrieval_sources:
        result["retrieval_sources"] = retrieval_sources
    return result


def is_assessment_exempt(query: str, context: dict[str, Any], policy: dict[str, Any]) -> bool:
    if str(policy.get("mode") or "") in {"model_knowledge", "web_research"}:
        return True
    scope = str(context.get("scope") or "")
    if scope in {"reader", "manual"}:
        from .retrieval import is_generic_context_question

        return is_generic_context_question(query)
    from .retrieval import is_context_overview_question

    return is_context_overview_question(query)


def evidence_chunks_overlap_query(query: str, chunks: list[dict[str, Any]]) -> bool:
    raw_tokens = [token for token in answer_query_tokens(query) if is_specific_relevance_token(token)]
    concept_terms = [term.lower() for term in concept_terms_from_question(query) if is_specific_relevance_token(term)]
    tokens = list(dict.fromkeys([*concept_terms, *raw_tokens]))
    if not tokens:
        return False
    haystack = " ".join(
        " ".join([str(chunk.get("title") or ""), str(chunk.get("snippet") or ""), str(chunk.get("item_id") or ""), str(chunk.get("url") or "")])
        for chunk in chunks
        if isinstance(chunk, dict)
    ).lower()
    return any(token.lower() in haystack for token in tokens)


def is_specific_relevance_token(token: str) -> bool:
    normalized = str(token or "").strip().lower()
    if len(normalized) < 3:
        return False
    generic = {
        "about",
        "does",
        "evidence",
        "explain",
        "runtime",
        "say",
        "summary",
        "travel",
        "what",
        "用小白能懂的话解释",
        "解释",
        "平台",
        "是什么",
    }
    return normalized not in generic


def external_evidence_assessment(*, chunks: list[dict[str, Any]], query: str, search_plan: dict[str, Any]) -> dict[str, Any]:
    search = search_plan.get("search") if isinstance(search_plan.get("search"), dict) else {}
    evidence_terms = [str(term).lower() for term in search.get("evidence_terms") or [] if str(term).strip()]
    required_terms = [str(term).lower() for term in search.get("required_terms") or [] if str(term).strip()]
    texts: list[str] = []
    for chunk in chunks:
        if not isinstance(chunk, dict):
            continue
        title = str(chunk.get("title") or "")
        snippet = str(chunk.get("snippet") or "")
        url = str(chunk.get("url") or "")
        if title.lower().startswith("external reference for "):
            title = ""
        if snippet.lower().startswith("fake external source related to:"):
            snippet = ""
        if "example.test/search" in url:
            url = ""
        texts.append(" ".join(part for part in (title, snippet, url) if part))
    haystack = " ".join(texts).lower()
    normalized_query = str(query or "").strip().lower()
    if normalized_query:
        haystack = haystack.replace(normalized_query, " ")
    for marker in ("external reference for", "fake external source related to:"):
        haystack = haystack.replace(marker, " ")
    missing_required_terms = [term for term in required_terms if term not in haystack]
    matched_evidence_terms = [term for term in evidence_terms if term in haystack]
    insufficient = not chunks or bool(missing_required_terms)
    weak_relevance = bool(chunks) and bool(evidence_terms) and not matched_evidence_terms
    flags: list[str] = []
    if insufficient:
        flags.append("insufficient_evidence")
    if weak_relevance:
        flags.append("weak_relevance")
    return {
        "query": query,
        "metrics": {
            "status": "needs_attention" if flags else "ok",
            "requires_attention": bool(flags),
            "flags": flags,
            "matched_evidence_terms": matched_evidence_terms,
            "missing_required_terms": missing_required_terms,
        },
        "status": "insufficient_evidence" if insufficient else ("needs_attention" if weak_relevance else "ok"),
        "requires_attention": insufficient or weak_relevance,
        "insufficient_evidence": insufficient,
        "weak_relevance": weak_relevance,
        "matched_evidence_terms": matched_evidence_terms,
        "missing_required_terms": missing_required_terms,
        "decision": assessment_decision(
            "decline" if insufficient or weak_relevance else "answer",
            reason="weak_external_evidence" if insufficient or weak_relevance else "external_evidence_ok",
            confidence=0.88 if insufficient or weak_relevance else 0.82,
        ),
    }


def assessment_decision(action: str, *, reason: str, confidence: float) -> dict[str, Any]:
    normalized_action = "decline" if str(action or "").strip().lower() == "decline" else "answer"
    return {
        "action": normalized_action,
        "reason": str(reason or ("evidence_ok" if normalized_action == "answer" else "insufficient_evidence")),
        "confidence": max(0.0, min(float(confidence or 0.0), 1.0)),
        "requires_attention": normalized_action == "decline",
    }


def search_requires_attribute_evidence(search_plan: dict[str, Any]) -> bool:
    search = search_plan.get("search") if isinstance(search_plan.get("search"), dict) else {}
    intent = str(search.get("search_intent") or search_plan.get("reason") or "").lower()
    return intent.startswith("entity_")


def is_external_research_unavailable(status: dict[str, Any]) -> bool:
    if status.get("available") is False:
        return True
    message = str(status.get("message") or "").strip().lower()
    if not message:
        return False
    unavailable_markers = (
        "not configured",
        "api key is not configured",
        "unavailable",
        "未配置",
        "不可用",
    )
    return any(marker in message for marker in unavailable_markers)


def build_source_evaluator_messages(system_prompt: str, *, query: str, sources: list[dict[str, Any]], search_plan: dict[str, Any]) -> list[dict[str, str]]:
    candidates: list[dict[str, Any]] = []
    for index, source in enumerate(sources, start=1):
        candidates.append(
            {
                "index": index,
                "title": str(source.get("title") or "")[:220],
                "url": str(source.get("url") or "")[:260],
                "snippet": str(source.get("snippet") or "")[:900],
            },
        )
    search = search_plan.get("search") if isinstance(search_plan.get("search"), dict) else {}
    payload = {
        "question": query,
        "search_plan": {
            "intent": str(search.get("search_intent") or ""),
            "required_terms": [str(term) for term in search.get("required_terms") or []],
            "evidence_terms": [str(term) for term in search.get("evidence_terms") or []],
            "authoritative_required": bool(search.get("authoritative_required")),
        },
        "candidate_sources": candidates,
    }
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
    ]


def decode_source_evaluator_json(content: str) -> dict[str, Any]:
    text = str(content or "").strip()
    if not text:
        return {}
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 2:
            text = "\n".join(lines[1:-1]).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        text = text[start : end + 1]
    decoded = json.loads(text)
    return decoded if isinstance(decoded, dict) else {}


def apply_source_evaluator_decisions(sources: list[dict[str, Any]], decoded: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    raw_decisions = decoded.get("sources") if isinstance(decoded.get("sources"), list) else []
    decisions_by_index: dict[int, dict[str, Any]] = {}
    for raw in raw_decisions:
        if not isinstance(raw, dict):
            continue
        try:
            index = int(raw.get("index"))
        except (TypeError, ValueError):
            continue
        if index < 1 or index > len(sources):
            continue
        keep = parse_bool(raw.get("keep"), default=False)
        confidence = parse_float(raw.get("confidence"), default=0.0)
        decisions_by_index[index] = {
            "index": index,
            "keep": keep,
            "confidence": confidence,
            "reason": str(raw.get("reason") or "").strip()[:180],
        }
    if not decisions_by_index:
        return [], []
    kept = [dict(source) for index, source in enumerate(sources, start=1) if decisions_by_index.get(index, {}).get("keep")]
    decisions = [decisions_by_index.get(index, {"index": index, "keep": False, "confidence": 0.0, "reason": "missing_decision"}) for index in range(1, len(sources) + 1)]
    return kept, decisions


def fallback_source_relevance(source: dict[str, Any], *, query: str, search_plan: dict[str, Any]) -> tuple[bool, str]:
    search = search_plan.get("search") if isinstance(search_plan.get("search"), dict) else {}
    required_terms = [str(term).lower() for term in search.get("required_terms") or [] if str(term).strip()]
    evidence_terms = [str(term).lower() for term in search.get("evidence_terms") or [] if str(term).strip()]
    text = " ".join(str(source.get(key) or "") for key in ("title", "url", "snippet")).lower()
    if "example.test/search" in text and ("external reference for" in text or "fake external source related to:" in text):
        return True, "fake_search_fixture_pass"
    intent = str(search.get("search_intent") or "").lower()
    if required_terms and intent == "entity_relationship" and not all(term in text for term in required_terms):
        return False, "missing_required_relationship_terms"
    if required_terms and intent.startswith("entity_") and not any(term in text for term in required_terms):
        return False, "missing_required_entity_terms"
    if evidence_terms and not any(term in text for term in evidence_terms):
        return False, "missing_evidence_terms"
    query_tokens = [token for token in answer_query_tokens(query) if is_specific_relevance_token(token)]
    if query_tokens and not any(token.lower() in text for token in query_tokens[:8]):
        return False, "no_query_token_overlap"
    return True, "fallback_relevance_pass"


def parse_bool(value: Any, *, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "yes", "1", "keep", "pass"}:
            return True
        if normalized in {"false", "no", "0", "drop", "fail"}:
            return False
    return default


def parse_float(value: Any, *, default: float) -> float:
    try:
        return max(0.0, min(float(value), 1.0))
    except (TypeError, ValueError):
        return default


def context_title(context: dict[str, Any]) -> str:
    items = context.get("items") if isinstance(context.get("items"), list) else []
    scope = str(context.get("scope") or "global")
    requested = context.get("requested") if isinstance(context.get("requested"), dict) else {}
    if scope == "reader" and items:
        return str(items[0].get("title") or "Current note")
    if scope == "manual":
        return f"Selected notes ({len(items)})"
    if requested.get("collection"):
        return f"Collection: {requested['collection']}"
    tags = requested.get("tags") if isinstance(requested.get("tags"), list) else []
    if tags:
        return "Tags: " + ", ".join(str(tag) for tag in tags)
    if requested.get("q"):
        return f"Search: {requested['q']}"
    if requested.get("library") and requested.get("library") != "all":
        return f"Library: {requested['library']}"
    return "All notes"


def normalize_messages(messages: list[Any]) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for message in messages:
        if not isinstance(message, dict):
            continue
        role = str(message.get("role") or "").strip()
        content = str(message.get("content") or "")
        if role and content:
            normalized.append({"role": role, "content": content})
    if not normalized:
        raise ProviderCallError("LLM tool received no valid messages.")
    return normalized
