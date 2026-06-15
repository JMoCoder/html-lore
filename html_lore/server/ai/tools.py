from __future__ import annotations

from collections.abc import Callable
from typing import Any

from html_lore.server.items import ItemService

from .context import ContextResolver
from .external_search import DisabledExternalSearchAdapter, ExternalSearchAdapter
from .guardrails import validate_answer, validate_message_budget, validate_prompt_budget, validate_user_message
from .conversation_resolution import resolve_conversation_turn
from .knowledge_qa_graph import (
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
)
from .model_client import ModelClient
from .providers import ProviderCallError
from .registry import load_agent, load_prompt
from .research import ResearchWorkflow
from .retrieval import retrieve_evidence_with_status
from .qa_search_plan import build_qa_search_plan
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


class ExternalResearchTool:
    id = "external.research"

    def __init__(self, external_search: ExternalSearchAdapter | None = None) -> None:
        self.workflow = ResearchWorkflow(external_search or DisabledExternalSearchAdapter())

    def run(self, arguments: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
        policy = state.get("tool_outputs", {}).get("expansion.policy", {}) if isinstance(state.get("tool_outputs"), dict) else {}
        planner = (arguments or {}).get("planner") if isinstance((arguments or {}).get("planner"), dict) else {}
        context_output = state.get("tool_outputs", {}).get("context.resolve", {}) if isinstance(state.get("tool_outputs"), dict) else {}
        context = context_output.get("context") if isinstance(context_output.get("context"), dict) else {}
        qa_search_plan = build_qa_search_plan(str(state.get("retrieval_query") or (arguments or {}).get("query") or state.get("query") or "").strip(), planner=planner, context=context)
        default_status = {"provider": self.workflow.external_search.name, "available": self.workflow.external_search.available}
        if not qa_search_plan.should_search or str(policy.get("mode") or "") != "web_research":
            return {
                "sources": [],
                "status": default_status,
                "trace": [],
                "queried": False,
                "search_plan": qa_search_plan.public_report(),
            }
        research = self.workflow.run(qa_search_plan.plan.original_query if qa_search_plan.plan else str(state.get("retrieval_query") or (arguments or {}).get("query") or state.get("query") or "").strip())
        return {"sources": research.sources, "status": dict(research.status or {}), "trace": research.trace, "queried": True, "search_plan": qa_search_plan.public_report()}


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
        context = context_output.get("context") if isinstance(context_output.get("context"), dict) else {}
        query = str(state.get("retrieval_query") or (arguments or {}).get("query") or evidence_pack.get("query") or state.get("query") or "").strip()
        local_chunks = [dict(item) for item in evidence_pack.get("chunks") or [] if isinstance(item, dict)]
        external_chunks = [dict(item) for item in research.get("sources") or [] if isinstance(item, dict)]
        mode = str(policy.get("mode") or "local_only")
        evidence = external_chunks if mode == "web_research" else local_chunks
        skipped_model_call = False
        answer = ""
        if mode == "web_research" and not external_chunks:
            answer = EXTERNAL_UNAVAILABLE_ANSWER
            evidence = []
            skipped_model_call = True
        if evidence and should_reject_weak_evidence(evidence, context, query) and mode != "model_knowledge":
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
                expansion_policy=policy,
                max_prompt_chars=self.max_prompt_chars,
                agent=self.answer_agent,
                prompt=self.answer_prompt,
            )
            sources = dedupe_display_sources(prompt_evidence)
            prompt_evidence = evidence_with_display_source_indices(prompt_evidence, sources)
            renumbered_pack = build_evidence_pack(query=query, chunks=prompt_evidence, status={})
            prompt_evidence = renumbered_pack["chunks"]
            sources = renumbered_pack["sources"]
            messages = build_answer_prompt(
                query,
                prompt_evidence,
                context,
                recent,
                expansion_policy=policy,
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
        if is_assessment_exempt(query, context, policy):
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
        if bool(assessment.get("weak_relevance")) or bool(assessment.get("insufficient_evidence")):
            return {
                "content": "",
                "model": "",
                "usage": {},
                "prompt_id": str(values.get("prompt_id") or ""),
                "message_count": 0,
                "skipped": True,
                "skip_reason": "insufficient_evidence" if bool(assessment.get("insufficient_evidence")) else "weak_relevance",
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
    }


def search_requires_attribute_evidence(search_plan: dict[str, Any]) -> bool:
    search = search_plan.get("search") if isinstance(search_plan.get("search"), dict) else {}
    intent = str(search.get("search_intent") or search_plan.get("reason") or "").lower()
    return intent.startswith("entity_")


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
