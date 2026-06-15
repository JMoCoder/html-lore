from __future__ import annotations

import uuid
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Protocol

from html_lore.server.items import ItemService

from .conversations import ConversationStore
from .external_search import DisabledExternalSearchAdapter, ExternalSearchAdapter
from .guardrails import GuardrailError, validate_answer, validate_message_budget, validate_prompt_budget, validate_user_message
from .model_client import ModelClient
from .registry import AgentSpec, PromptTemplate, load_agent, load_prompt
from .research import ResearchWorkflow
from .retrieval import is_context_overview_question, is_generic_context_question
from .skills import RetrievalSkill


NO_EVIDENCE_ANSWER = "当前上下文没有足够资料回答这个问题。请调整上下文、选择相关笔记，或开启内容拓展后再试。"
EXTERNAL_UNAVAILABLE_ANSWER = "内容拓展尚未配置外部检索服务。当前上下文也没有足够资料回答这个问题。"
ANSWER_AGENT_ID = "knowledge_qa.answer_agent.v1"


class KnowledgeQANode(Protocol):
    name: str

    def run(self, state: "KnowledgeQAState") -> None:
        pass


@dataclass
class KnowledgeQAState:
    conversation_id: str
    conversation: dict[str, Any]
    content: str
    context_snapshot: dict[str, Any] = field(default_factory=dict)
    recent_messages: list[dict[str, str]] = field(default_factory=list)
    retrieval_query: str = ""
    evidence: list[dict[str, Any]] = field(default_factory=list)
    retrieval_status: dict[str, Any] = field(default_factory=dict)
    external_sources: list[dict[str, Any]] = field(default_factory=list)
    external_status: dict[str, Any] = field(default_factory=dict)
    research_trace: list[dict[str, Any]] = field(default_factory=list)
    expansion_policy: dict[str, Any] = field(default_factory=dict)
    evidence_scope_report: dict[str, Any] = field(default_factory=dict)
    evidence_rank_report: dict[str, Any] = field(default_factory=dict)
    evidence_rerank_report: dict[str, Any] = field(default_factory=dict)
    evidence_budget: dict[str, Any] = field(default_factory=dict)
    evidence_coverage_report: dict[str, Any] = field(default_factory=dict)
    evidence_sufficiency_report: dict[str, Any] = field(default_factory=dict)
    prompt_messages: list[dict[str, str]] = field(default_factory=list)
    agent_trace: list[dict[str, Any]] = field(default_factory=list)
    prompt_trace: list[dict[str, str]] = field(default_factory=list)
    skill_trace: list[dict[str, Any]] = field(default_factory=list)
    citation_report: dict[str, Any] = field(default_factory=dict)
    answer_quality_report: dict[str, Any] = field(default_factory=dict)
    answer: str = ""
    sources: list[dict[str, Any]] = field(default_factory=list)
    usage: dict[str, Any] = field(default_factory=dict)
    budget: dict[str, Any] = field(default_factory=dict)
    skipped_model_call: bool = False
    stored_conversation: dict[str, Any] = field(default_factory=dict)
    node_trace: list[dict[str, str]] = field(default_factory=list)
    started_at: str = ""
    completed_at: str = ""
    duration_ms: int = 0

    def mark_completed(self, node_name: str) -> None:
        self.node_trace.append({"node": node_name, "status": "completed"})


class KnowledgeQAGraph:
    name = "KnowledgeQAAndNoteGraph.beta"

    def __init__(
        self,
        *,
        item_service: ItemService,
        model_client: ModelClient,
        conversation_store: ConversationStore,
        external_search: ExternalSearchAdapter | None = None,
        nodes: tuple[KnowledgeQANode, ...] | None = None,
        max_message_chars: int = 4000,
        max_prompt_chars: int = 12000,
        max_response_tokens: int = 1024,
        retrieval_mode: str = "keyword",
    ) -> None:
        external_search = external_search or DisabledExternalSearchAdapter()
        self.nodes = nodes or (
            InputGuardrailNode(max_message_chars=max_message_chars),
            RetrieverNode(item_service, model_client=model_client, retrieval_mode=retrieval_mode),
            ExpansionPolicyNode(),
            ExternalSearchNode(external_search),
            EvidenceScopeGuardNode(),
            EvidenceRankerNode(),
            EvidenceRerankNode(),
            EvidenceGateNode(max_prompt_chars=max_prompt_chars),
            EvidenceCoverageNode(),
            EvidenceSufficiencyNode(),
            AnswerAgentNode(model_client, max_response_tokens=max_response_tokens),
            CitationVerifierNode(),
            AnswerQualityNode(),
            OutputGuardrailNode(),
            ConversationPersistNode(conversation_store),
        )

    def run(self, state: KnowledgeQAState) -> KnowledgeQAState:
        started_at = datetime.now(timezone.utc)
        state.started_at = started_at.isoformat()
        try:
            for node in self.nodes:
                node.run(state)
                state.mark_completed(node.name)
        finally:
            completed_at = datetime.now(timezone.utc)
            state.completed_at = completed_at.isoformat()
            state.duration_ms = int((completed_at - started_at).total_seconds() * 1000)
        return state


class InputGuardrailNode:
    name = "InputGuardrailNode"

    def __init__(self, *, max_message_chars: int = 4000) -> None:
        self.max_message_chars = max(1, int(max_message_chars or 4000))

    def run(self, state: KnowledgeQAState) -> None:
        state.content = state.content.strip()
        validate_user_message(state.content)
        validate_message_budget(state.content, max_chars=self.max_message_chars)
        state.budget["message_chars"] = len(state.content)
        state.budget["max_message_chars"] = self.max_message_chars
        state.context_snapshot = state.conversation.get("context_snapshot") if isinstance(state.conversation.get("context_snapshot"), dict) else {}
        state.recent_messages = recent_conversation_messages(state.conversation.get("messages"))
        state.retrieval_query = build_retrieval_query(state.content, state.recent_messages)


class RetrieverNode:
    name = "RetrieverNode"

    def __init__(self, item_service: ItemService, *, model_client: ModelClient | None = None, retrieval_mode: str = "keyword") -> None:
        self.retrieval_skill = RetrievalSkill(item_service, model_client=model_client, mode=retrieval_mode)

    def run(self, state: KnowledgeQAState) -> None:
        result, trace = self.retrieval_skill.run(state.context_snapshot, state.retrieval_query or state.content)
        state.skill_trace.append(trace)
        state.evidence = result.evidence
        state.retrieval_status = result.status
        state.retrieval_status["query_expanded"] = bool(state.retrieval_query and state.retrieval_query != state.content)
        state.retrieval_status.update(retrieval_coverage_status(state.context_snapshot, state.evidence))


class ExternalSearchNode:
    name = "ExternalSearchNode"

    def __init__(self, external_search: ExternalSearchAdapter) -> None:
        self.research_workflow = ResearchWorkflow(external_search)

    def run(self, state: KnowledgeQAState) -> None:
        source_mode = str(state.context_snapshot.get("source_mode") or "local_only")
        state.external_status = {"provider": self.research_workflow.external_search.name, "available": self.research_workflow.external_search.available}
        if source_mode != "local_plus_external":
            return
        if state.expansion_policy.get("mode") != "web_research":
            return
        research = self.research_workflow.run(state.retrieval_query or state.content)
        state.external_status = research.status
        state.research_trace = research.trace
        state.external_sources = research.sources
        state.evidence = list(state.external_sources)


class ExpansionPolicyNode:
    name = "ExpansionPolicyNode"

    def run(self, state: KnowledgeQAState) -> None:
        source_mode = str(state.context_snapshot.get("source_mode") or "local_only")
        local_signal = assess_local_evidence_signal(state.evidence, state.context_snapshot, state.content)
        has_local_evidence = bool(local_signal["sufficient"])
        explicit_search = asks_for_external_search(state.content)
        time_sensitive = is_time_sensitive_question(state.content)
        if source_mode != "local_plus_external":
            state.expansion_policy = {
                "mode": "local_only",
                "reason": "content_expansion_disabled",
                "confidence": 1.0,
                "requires_citation": bool(state.evidence),
            }
            return
        if explicit_search or time_sensitive:
            state.expansion_policy = {
                "mode": "web_research",
                "reason": "explicit_search_request" if explicit_search else "time_sensitive_question",
                "confidence": 0.9,
                "requires_citation": True,
            }
            return
        if has_local_evidence:
            state.expansion_policy = {
                "mode": "local_evidence",
                "reason": "local_evidence_available",
                "confidence": 0.85,
                "requires_citation": True,
                "local_evidence_signal": local_signal,
            }
            return
        state.expansion_policy = {
            "mode": "model_knowledge",
            "reason": "weak_local_evidence_fallback" if local_signal["source_count"] else "general_knowledge_fallback",
            "confidence": 0.72,
            "requires_citation": False,
            "local_evidence_signal": local_signal,
        }


class EvidenceRankerNode:
    name = "EvidenceRankerNode"

    def run(self, state: KnowledgeQAState) -> None:
        state.evidence, state.evidence_rank_report = rank_answer_evidence(state.evidence)


class EvidenceScopeGuardNode:
    name = "EvidenceScopeGuardNode"

    def run(self, state: KnowledgeQAState) -> None:
        state.evidence, state.evidence_scope_report = filter_evidence_by_context(state.evidence, state.context_snapshot)


class EvidenceRerankNode:
    name = "EvidenceRerankNode"

    def run(self, state: KnowledgeQAState) -> None:
        state.evidence, state.evidence_rerank_report = rerank_answer_evidence(state.evidence, state.retrieval_query or state.content)


class EvidenceGateNode:
    name = "EvidenceGateNode"

    def __init__(self, *, max_prompt_chars: int = 12000) -> None:
        self.max_prompt_chars = max(1, int(max_prompt_chars or 12000))
        self.answer_agent = load_agent(ANSWER_AGENT_ID)
        self.answer_prompt = load_prompt(self.answer_agent.prompt_template)

    def run(self, state: KnowledgeQAState) -> None:
        allow_model_knowledge = state.expansion_policy.get("mode") == "model_knowledge"
        requires_web_research = state.expansion_policy.get("mode") == "web_research"
        has_external_evidence = any(source.get("kind") == "external" for source in state.evidence)
        if state.evidence and should_reject_weak_evidence(state.evidence, state.context_snapshot, state.content):
            state.retrieval_status["weak_evidence_rejected"] = True
            state.retrieval_status["source_count_before_weak_reject"] = len(state.evidence)
            state.evidence = []
        if requires_web_research and not has_external_evidence:
            state.answer = EXTERNAL_UNAVAILABLE_ANSWER
            state.sources = []
            state.skipped_model_call = True
            return
        if state.evidence or allow_model_knowledge:
            budgeted_evidence, budgeted_history, budget_report = budget_prompt_inputs(
                content=state.content,
                evidence=state.evidence,
                snapshot=state.context_snapshot,
                recent_messages=state.recent_messages,
                expansion_policy=state.expansion_policy,
                max_prompt_chars=self.max_prompt_chars,
                agent=self.answer_agent,
                prompt=self.answer_prompt,
            )
            state.evidence = budgeted_evidence
            state.recent_messages = budgeted_history
            state.evidence_budget = budget_report
            state.retrieval_status["budget"] = budget_report
            state.sources = assign_source_indices(dedupe_display_sources(state.evidence))
            prompt_evidence = evidence_with_display_source_indices(state.evidence, state.sources)
            state.prompt_messages = build_answer_prompt(
                state.content,
                prompt_evidence,
                state.context_snapshot,
                budgeted_history,
                expansion_policy=state.expansion_policy,
                agent=self.answer_agent,
                prompt=self.answer_prompt,
            )
            state.agent_trace.append(self.answer_agent.public_dict())
            state.prompt_trace.append(self.answer_prompt.public_dict())
            state.budget["prompt_chars"] = prompt_chars(state.prompt_messages)
            state.budget["max_prompt_chars"] = self.max_prompt_chars
            validate_prompt_budget(state.prompt_messages, max_chars=self.max_prompt_chars)
            return
        if str(state.context_snapshot.get("source_mode") or "local_only") == "local_plus_external":
            if state.expansion_policy.get("mode") == "web_research":
                state.answer = EXTERNAL_UNAVAILABLE_ANSWER
            else:
                state.answer = NO_EVIDENCE_ANSWER
        else:
            state.answer = NO_EVIDENCE_ANSWER
        state.sources = []
        state.skipped_model_call = True


class EvidenceCoverageNode:
    name = "EvidenceCoverageNode"

    def run(self, state: KnowledgeQAState) -> None:
        state.evidence_coverage_report = assess_evidence_coverage(
            snapshot=state.context_snapshot,
            retrieval_status=state.retrieval_status,
            sources=state.sources,
            budget_report=state.evidence_budget,
        )


class EvidenceSufficiencyNode:
    name = "EvidenceSufficiencyNode"

    def run(self, state: KnowledgeQAState) -> None:
        state.evidence_sufficiency_report = assess_evidence_sufficiency(
            sources=state.sources,
            expansion_policy=state.expansion_policy,
            coverage_report=state.evidence_coverage_report,
        )


class AnswerAgentNode:
    name = "AnswerAgentNode"

    def __init__(self, model_client: ModelClient, *, max_response_tokens: int = 1024) -> None:
        self.model_client = model_client
        self.max_response_tokens = max(1, int(max_response_tokens or 1024))

    def run(self, state: KnowledgeQAState) -> None:
        if state.skipped_model_call:
            return
        state.budget["max_response_tokens"] = self.max_response_tokens
        response = self.model_client.chat(messages=state.prompt_messages, max_tokens=self.max_response_tokens)
        state.answer = str(response.get("content") or "").strip()
        state.usage = response.get("usage") if isinstance(response.get("usage"), dict) else {}


class CitationVerifierNode:
    name = "CitationVerifierNode"

    def run(self, state: KnowledgeQAState) -> None:
        state.citation_report = verify_answer_citations(
            state.answer,
            state.sources,
            requires_citation=bool(state.expansion_policy.get("requires_citation")),
        )
        if state.citation_report.get("status") == "invalid_reference":
            invalid_refs = ", ".join(str(ref) for ref in state.citation_report.get("invalid_refs") or [])
            raise GuardrailError(f"AI output cited unavailable sources: {invalid_refs}.")


class AnswerQualityNode:
    name = "AnswerQualityNode"

    def run(self, state: KnowledgeQAState) -> None:
        state.answer_quality_report = assess_answer_quality(
            state.answer,
            sources=state.sources,
            citation_report=state.citation_report,
            skipped_model_call=state.skipped_model_call,
        )


class OutputGuardrailNode:
    name = "OutputGuardrailNode"

    def run(self, state: KnowledgeQAState) -> None:
        if state.skipped_model_call:
            return
        validate_answer(state.answer)


class ConversationPersistNode:
    name = "ConversationPersistNode"

    def __init__(self, conversation_store: ConversationStore) -> None:
        self.conversation_store = conversation_store

    def run(self, state: KnowledgeQAState) -> None:
        state.stored_conversation = self.conversation_store.append_messages(
            state.conversation_id,
            [
                {"role": "user", "content": state.content},
                {"role": "assistant", "content": state.answer, "sources": state.sources},
            ],
        )


def build_answer_prompt(
    content: str,
    evidence: list[dict[str, Any]],
    snapshot: dict[str, Any],
    recent_messages: list[dict[str, str]] | None = None,
    *,
    expansion_policy: dict[str, Any] | None = None,
    agent: AgentSpec | None = None,
    prompt: PromptTemplate | None = None,
) -> list[dict[str, str]]:
    agent = agent or load_agent(ANSWER_AGENT_ID)
    prompt = prompt or load_prompt(agent.prompt_template)
    source_mode = str(snapshot.get("source_mode") or "local_only")
    policy = expansion_policy if isinstance(expansion_policy, dict) else {}
    context_text = format_context_for_prompt(snapshot)
    recent_text = format_recent_conversation_for_prompt(recent_messages or [])
    evidence_text = "\n\n".join(
        format_evidence_for_prompt(index, item)
        for index, item in enumerate(evidence, start=1)
    )
    recent_section = f"RECENT_CONVERSATION:\n{recent_text}\n\n" if recent_text else ""
    return [
        {
            "role": "system",
            "content": prompt.render({}),
        },
        {
            "role": "user",
            "content": (
                f"SOURCE_MODE: {source_mode}\n"
                f"EXPANSION_POLICY: {format_expansion_policy_for_prompt(policy)}\n"
                f"CURRENT_CONTEXT:\n{context_text}\n\n"
                f"{recent_section}"
                f"USER_QUESTION:\n{content}\n\n"
                f"TRUSTED_EVIDENCE:\n{evidence_text}"
            ),
        },
    ]


def budget_prompt_inputs(
    *,
    content: str,
    evidence: list[dict[str, Any]],
    snapshot: dict[str, Any],
    recent_messages: list[dict[str, str]],
    expansion_policy: dict[str, Any],
    max_prompt_chars: int,
    agent: AgentSpec,
    prompt: PromptTemplate,
) -> tuple[list[dict[str, Any]], list[dict[str, str]], dict[str, Any]]:
    original_evidence_count = len(evidence)
    original_history_count = len(recent_messages)
    working_evidence = [dict(item) for item in evidence]
    working_history = list(recent_messages)
    working_snapshot, context_report = budget_context_snapshot(snapshot, max_prompt_chars=max_prompt_chars)
    max_chars = max(1, int(max_prompt_chars or 1))
    trimmed_evidence_chars = False
    dropped_evidence = 0
    dropped_history = 0

    if working_evidence:
        per_snippet_limit = evidence_snippet_limit(max_chars, len(working_evidence))
        trimmed: list[dict[str, Any]] = []
        for item in working_evidence:
            snippet = str(item.get("snippet") or "")
            if len(snippet) > per_snippet_limit:
                item["snippet"] = snippet[:per_snippet_limit].rstrip() + "..."
                trimmed_evidence_chars = True
            trimmed.append(item)
        working_evidence = trimmed

    messages = build_answer_prompt(
        content,
        working_evidence,
        working_snapshot,
        working_history,
        expansion_policy=expansion_policy,
        agent=agent,
        prompt=prompt,
    )
    while prompt_chars(messages) > max_chars and context_report["selected_item_count"] > 0:
        working_snapshot, context_report = shrink_context_snapshot(working_snapshot, context_report, max_prompt_chars=max_prompt_chars)
        messages = build_answer_prompt(
            content,
            working_evidence,
            working_snapshot,
            working_history,
            expansion_policy=expansion_policy,
            agent=agent,
            prompt=prompt,
        )
    while prompt_chars(messages) > max_chars and working_history:
        working_history = working_history[1:]
        dropped_history += 1
        messages = build_answer_prompt(
            content,
            working_evidence,
            working_snapshot,
            working_history,
            expansion_policy=expansion_policy,
            agent=agent,
            prompt=prompt,
        )
    while prompt_chars(messages) > max_chars and len(working_evidence) > 1:
        working_evidence = drop_lowest_priority_evidence(working_evidence)
        dropped_evidence += 1
        messages = build_answer_prompt(
            content,
            working_evidence,
            working_snapshot,
            working_history,
            expansion_policy=expansion_policy,
            agent=agent,
            prompt=prompt,
        )

    report = {
        "max_prompt_chars": max_chars,
        "original_evidence_count": original_evidence_count,
        "selected_evidence_count": len(working_evidence),
        "dropped_evidence_count": dropped_evidence,
        "original_history_count": original_history_count,
        "selected_history_count": len(working_history),
        "dropped_history_count": dropped_history,
        "trimmed_evidence_chars": trimmed_evidence_chars,
        "prompt_chars_after_budget": prompt_chars(messages),
        "context_summary_chars": context_report["summary_chars"],
        "context_items_original": context_report["original_item_count"],
        "context_items_selected": context_report["selected_item_count"],
        "context_items_omitted": context_report["omitted_item_count"],
    }
    return working_evidence, working_history, report


def budget_context_snapshot(snapshot: dict[str, Any], *, max_prompt_chars: int) -> tuple[dict[str, Any], dict[str, int]]:
    items = snapshot.get("items") if isinstance(snapshot.get("items"), list) else []
    max_items = max_context_summary_items(max_prompt_chars)
    selected_items = items[:max_items]
    budgeted = dict(snapshot)
    budgeted["items"] = selected_items
    budgeted["_context_items_original_count"] = len(items)
    report = {
        "summary_chars": len(format_context_for_prompt(budgeted)),
        "original_item_count": len(items),
        "selected_item_count": len(selected_items),
        "omitted_item_count": max(0, len(items) - len(selected_items)),
    }
    return budgeted, report


def shrink_context_snapshot(snapshot: dict[str, Any], report: dict[str, int], *, max_prompt_chars: int) -> tuple[dict[str, Any], dict[str, int]]:
    items = snapshot.get("items") if isinstance(snapshot.get("items"), list) else []
    if not items:
        return snapshot, report
    next_count = max(0, len(items) - 1)
    budgeted = dict(snapshot)
    budgeted["items"] = items[:next_count]
    original_count = int(snapshot.get("_context_items_original_count") or report.get("original_item_count") or len(items))
    budgeted["_context_items_original_count"] = original_count
    next_report = {
        "summary_chars": len(format_context_for_prompt(budgeted)),
        "original_item_count": original_count,
        "selected_item_count": next_count,
        "omitted_item_count": max(0, original_count - next_count),
    }
    return budgeted, next_report


def max_context_summary_items(max_prompt_chars: int) -> int:
    chars = max(1, int(max_prompt_chars or 1))
    if chars < 3000:
        return 8
    if chars < 6000:
        return 16
    if chars < 10000:
        return 24
    return 30


def evidence_snippet_limit(max_prompt_chars: int, evidence_count: int) -> int:
    if evidence_count <= 0:
        return 0
    evidence_budget = max(240, int(max_prompt_chars * 0.42))
    return max(160, min(900, evidence_budget // max(1, evidence_count)))


def drop_lowest_priority_evidence(evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(evidence) <= 1:
        return evidence
    indexed = list(enumerate(evidence))
    drop_index, _ = min(indexed, key=lambda pair: (evidence_priority(pair[1]), -pair[0]))
    return [item for index, item in indexed if index != drop_index]


def evidence_priority(item: dict[str, Any]) -> int:
    if item.get("kind") == "external":
        return safe_int(item.get("score"), 100)
    return safe_int(item.get("score"), 0)


def should_reject_weak_evidence(evidence: list[dict[str, Any]], snapshot: dict[str, Any], query: str) -> bool:
    if any(item.get("kind") == "external" for item in evidence):
        return False
    return not assess_local_evidence_signal(evidence, snapshot, query)["sufficient"]


def assess_local_evidence_signal(evidence: list[dict[str, Any]], snapshot: dict[str, Any], query: str) -> dict[str, Any]:
    scope = str(snapshot.get("scope") or "")
    if scope in {"reader", "manual"} and is_generic_context_question(query):
        local_count = sum(1 for item in evidence if item.get("kind") != "external")
        return {
            "sufficient": bool(local_count),
            "reason": "generic_reader_context",
            "top_score": max_local_score(evidence),
            "source_count": local_count,
        }
    if is_context_overview_question(query):
        local_count = sum(1 for item in evidence if item.get("kind") != "external")
        return {
            "sufficient": bool(local_count),
            "reason": "context_overview",
            "top_score": max_local_score(evidence),
            "source_count": local_count,
        }
    local_scores = [
        safe_int(item.get("score"), 0)
        for item in evidence
        if item.get("kind") != "external"
    ]
    external_count = sum(1 for item in evidence if item.get("kind") == "external")
    if external_count and not local_scores:
        return {
            "sufficient": False,
            "reason": "external_only",
            "top_score": 0,
            "source_count": 0,
        }
    if not local_scores:
        return {
            "sufficient": False,
            "reason": "no_local_evidence",
            "top_score": 0,
            "source_count": 0,
        }
    top_score = max(local_scores)
    if scope in {"reader", "manual"}:
        threshold = 4
    else:
        threshold = 18 if str(snapshot.get("source_mode") or "local_only") == "local_plus_external" else 10
    retrieval_sources = {
        str(source)
        for item in evidence
        if item.get("kind") != "external"
        for source in (item.get("retrieval_sources") if isinstance(item.get("retrieval_sources"), list) else [])
    }
    pure_vector = retrieval_sources == {"vector"}
    if pure_vector and top_score < 62:
        return {
            "sufficient": False,
            "reason": "weak_vector_only_evidence",
            "top_score": top_score,
            "threshold": 62,
            "source_count": len(local_scores),
            "retrieval_sources": sorted(retrieval_sources),
        }
    return {
        "sufficient": top_score >= threshold,
        "reason": "local_score_threshold",
        "top_score": top_score,
        "threshold": threshold,
        "source_count": len(local_scores),
    }


def is_concept_explanation_question(content: str) -> bool:
    normalized = str(content or "").strip().lower()
    if not normalized:
        return False
    markers = (
        "what is",
        "what are",
        "define",
        "definition",
        "concept",
        "explain",
        "是什么",
        "什么是",
        "定义",
        "概念",
        "如何理解",
        "解释一下",
        "解释",
        "とは",
        "定義",
        "概念",
        "説明",
    )
    return any(marker in normalized for marker in markers)


def local_evidence_defines_query(evidence: list[dict[str, Any]], query: str) -> bool:
    if not is_concept_explanation_question(query):
        return False
    terms = concept_terms_from_question(query)
    haystacks = [
        normalize_answer_evidence_text(" ".join([str(item.get("title") or ""), str(item.get("snippet") or "")])).lower()
        for item in evidence
        if item.get("kind") != "external"
    ]
    if not haystacks:
        return False
    definition_markers = (
        " is ",
        " are ",
        " refers to ",
        " means ",
        " defined as ",
        "是一种",
        "是一个",
        "是指",
        "指的是",
        "定义为",
        "とは",
        "を指",
    )
    for haystack in haystacks:
        if not any(marker in haystack for marker in definition_markers):
            continue
        if not terms:
            return True
        if any(term and term.lower() in haystack for term in terms):
            return True
    return False


def concept_terms_from_question(content: str) -> list[str]:
    text = normalize_answer_evidence_text(str(content or "")).strip()
    if not text:
        return []
    patterns = (
        r"什么是\s*([^？?，,。.!；;：:]{2,40})",
        r"([^？?，,。.!；;：:]{2,40})\s*是什么",
        r"解释一下\s*([^？?，,。.!；;：:]{2,40})",
        r"如何理解\s*([^？?，,。.!；;：:]{2,40})",
        r"what\s+(?:is|are)\s+([^?.,;:!]{2,60})",
        r"define\s+([^?.,;:!]{2,60})",
    )
    terms: list[str] = []
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            terms.extend(split_concept_term(match.group(1)))
    if not terms:
        tokens = [token for token in answer_query_tokens(text) if is_concept_token(token)]
        terms.extend(tokens[:3])
    seen: set[str] = set()
    result: list[str] = []
    for term in terms:
        normalized = term.strip().lower()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(term.strip())
    return result


def split_concept_term(value: str) -> list[str]:
    cleaned = re.sub(r"\b(in|for|with|about|as|a|an|the)\b", " ", str(value or ""), flags=re.IGNORECASE)
    cleaned = re.sub(r"(用小白能懂的话|简单|基本原理|概念|定义|一下|请|the concept of)", " ", cleaned, flags=re.IGNORECASE)
    parts = [part.strip(" \t\r\n\"'“”‘’()（）") for part in re.split(r"[/、,，和与]| and | or ", cleaned) if part.strip()]
    return [part for part in parts if len(part) >= 2][:4]


def is_concept_token(token: str) -> bool:
    normalized = str(token or "").strip().lower()
    if len(normalized) < 2:
        return False
    generic = {
        "what",
        "define",
        "definition",
        "concept",
        "explain",
        "什么是",
        "是什么",
        "解释",
        "概念",
        "定义",
        "如何理解",
        "小白",
    }
    return normalized not in generic


def max_local_score(evidence: list[dict[str, Any]]) -> int:
    scores = [safe_int(item.get("score"), 0) for item in evidence if item.get("kind") != "external"]
    return max(scores) if scores else 0


def safe_int(value: Any, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def prompt_chars(messages: list[dict[str, str]]) -> int:
    return sum(len(str(message.get("content") or "")) for message in messages)


def filter_evidence_by_context(evidence: list[dict[str, Any]], snapshot: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    allowed_ids = {str(item_id) for item_id in snapshot.get("item_ids") or [] if str(item_id)}
    kept: list[dict[str, Any]] = []
    dropped: list[str] = []
    external_count = 0
    for item in evidence:
        if item.get("kind") == "external":
            kept.append(dict(item))
            external_count += 1
            continue
        item_id = str(item.get("item_id") or "").strip()
        if item_id and item_id in allowed_ids:
            kept.append(dict(item))
            continue
        dropped.append(item_id or str(item.get("title") or "unknown"))
    report = {
        "original_count": len(evidence),
        "selected_count": len(kept),
        "dropped_count": len(dropped),
        "dropped_local_ids": dropped[:20],
        "external_source_count": external_count,
        "context_item_count": len(allowed_ids),
    }
    return kept, report


def rank_answer_evidence(evidence: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    original_count = len(evidence)
    deduped: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    duplicate_dropped = 0
    for item in sorted(evidence, key=evidence_sort_key):
        normalized = normalize_evidence_item(item)
        key = evidence_dedupe_key(normalized)
        if key in seen:
            duplicate_dropped += 1
            continue
        deduped.append(normalized)
        seen.add(key)
    indexed = assign_source_indices(deduped)
    local_count = sum(1 for item in indexed if item.get("kind") != "external")
    external_count = sum(1 for item in indexed if item.get("kind") == "external")
    report = {
        "original_count": original_count,
        "selected_count": len(indexed),
        "duplicate_dropped_count": duplicate_dropped,
        "local_source_count": local_count,
        "external_source_count": external_count,
        "numbered": bool(indexed),
    }
    return indexed, report


def rerank_answer_evidence(evidence: list[dict[str, Any]], query: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    original_order = [evidence_identity(item) for item in evidence]
    scored: list[dict[str, Any]] = []
    for item in evidence:
        copied = dict(item)
        base_score = safe_int(copied.get("score"), 0)
        query_score = evidence_query_match_score(query, copied)
        source_bonus = 2 if copied.get("kind") != "external" else 0
        rerank_score = base_score + query_score + source_bonus
        copied["rerank_score"] = rerank_score
        copied["rerank_features"] = {
            "base_score": base_score,
            "query_match_score": query_score,
            "source_bonus": source_bonus,
        }
        scored.append(copied)
    reranked = sorted(scored, key=lambda item: (-safe_int(item.get("rerank_score"), 0), str(item.get("title") or ""), str(item.get("item_id") or item.get("url") or "")))
    indexed = assign_source_indices(reranked)
    reranked_order = [evidence_identity(item) for item in indexed]
    report = {
        "strategy": "deterministic_query_score_v1",
        "source_count": len(indexed),
        "order_changed": original_order != reranked_order,
        "top_source": reranked_order[0] if reranked_order else "",
    }
    return indexed, report


def evidence_query_match_score(query: str, item: dict[str, Any]) -> int:
    normalized_query = normalize_answer_evidence_text(query).lower()
    if not normalized_query:
        return 0
    haystack = " ".join(
        [
            str(item.get("title") or ""),
            str(item.get("snippet") or ""),
            str(item.get("item_id") or ""),
            str(item.get("url") or ""),
        ],
    ).lower()
    score = 0
    if normalized_query and normalized_query in haystack:
        score += 24
    for token in answer_query_tokens(normalized_query):
        if token in haystack:
            score += max(2, min(len(token), 16))
    return score


def answer_query_tokens(query: str) -> list[str]:
    tokens = re.findall(r"[a-z0-9][a-z0-9._-]{1,}", query.lower())
    for segment in re.findall(r"[\u4e00-\u9fff]{2,}", query):
        tokens.append(segment)
        tokens.extend(re.findall(r"(?=([\u4e00-\u9fff]{2}))", segment))
    seen: set[str] = set()
    result: list[str] = []
    for token in tokens:
        normalized = token.strip().lower()
        if len(normalized) < 2 or normalized in seen:
            continue
        result.append(normalized)
        seen.add(normalized)
    return result


def evidence_identity(item: dict[str, Any]) -> str:
    return str(item.get("item_id") or item.get("url") or item.get("title") or "").strip()


def normalize_evidence_item(item: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(item)
    normalized["title"] = str(normalized.get("title") or normalized.get("item_id") or normalized.get("url") or "Source").strip()
    normalized["snippet"] = normalize_answer_evidence_text(str(normalized.get("snippet") or ""))
    try:
        normalized["score"] = int(normalized.get("score") or 0)
    except (TypeError, ValueError):
        normalized["score"] = 0
    return normalized


def evidence_sort_key(item: dict[str, Any]) -> tuple[int, str, str, str]:
    kind_priority = 1 if item.get("kind") == "external" else 0
    return (
        -safe_int(item.get("score"), 0),
        str(kind_priority),
        str(item.get("title") or ""),
        str(item.get("item_id") or item.get("url") or ""),
    )


def evidence_dedupe_key(item: dict[str, Any]) -> tuple[str, str]:
    source_id = str(item.get("url") or item.get("item_id") or item.get("title") or "").strip().lower()
    snippet = normalize_answer_evidence_text(str(item.get("snippet") or "")).lower()[:280]
    return (source_id, snippet)


def assign_source_indices(evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    indexed: list[dict[str, Any]] = []
    for index, item in enumerate(evidence, start=1):
        copied = dict(item)
        copied["source_index"] = index
        indexed.append(copied)
    return indexed


def dedupe_display_sources(evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for item in evidence:
        key = display_source_key(item)
        if key in seen:
            continue
        deduped.append(item)
        seen.add(key)
    return deduped


def evidence_with_display_source_indices(evidence: list[dict[str, Any]], display_sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    display_index_by_key = {
        display_source_key(source): int(source.get("source_index") or index)
        for index, source in enumerate(display_sources, start=1)
    }
    indexed: list[dict[str, Any]] = []
    for item in evidence:
        copied = dict(item)
        copied["source_index"] = display_index_by_key.get(display_source_key(item), len(display_index_by_key) + 1)
        indexed.append(copied)
    return indexed


def display_source_key(item: dict[str, Any]) -> tuple[str, str]:
    if item.get("kind") == "external":
        return ("external", str(item.get("url") or item.get("title") or "").strip().lower())
    return ("local", str(item.get("item_id") or item.get("title") or "").strip().lower())


def normalize_answer_evidence_text(value: str) -> str:
    return " ".join(str(value or "").split())


def verify_answer_citations(answer: str, sources: list[dict[str, Any]], *, requires_citation: bool = False) -> dict[str, Any]:
    source_count = len(sources)
    cited_refs = citation_numbers(answer)
    invalid_refs = sorted({number for number in cited_refs if number < 1 or number > source_count})
    missing_required = bool(requires_citation and source_count and not cited_refs)
    if invalid_refs:
        status = "invalid_reference"
    elif missing_required:
        status = "missing_citation"
    elif cited_refs:
        status = "valid"
    else:
        status = "not_required"
    return {
        "status": status,
        "valid": not invalid_refs and not missing_required,
        "requires_citation": bool(requires_citation),
        "source_count": source_count,
        "has_citations": bool(cited_refs),
        "cited_refs": cited_refs,
        "invalid_refs": invalid_refs,
        "missing_required": missing_required,
    }


def citation_numbers(answer: str) -> list[int]:
    refs: list[int] = []
    for match in re.finditer(r"\[((?:\d+\s*(?:[,，]\s*)?)+)\]", str(answer or "")):
        for part in re.split(r"[,，]\s*", match.group(1)):
            part = part.strip()
            if not part:
                continue
            try:
                refs.append(int(part))
            except ValueError:
                continue
    return sorted(set(refs))


def assess_answer_quality(
    answer: str,
    *,
    sources: list[dict[str, Any]],
    citation_report: dict[str, Any],
    skipped_model_call: bool,
) -> dict[str, Any]:
    text = str(answer or "").strip()
    flags: list[str] = []
    if not text:
        flags.append("empty_answer")
    elif len(text) < 24 and not skipped_model_call:
        flags.append("very_short_answer")
    if sources and citation_report.get("status") == "missing_citation":
        flags.append("missing_citation")
    if skipped_model_call:
        flags.append("model_call_skipped")
    status = "needs_attention" if flags else "ok"
    return {
        "status": status,
        "answer_chars": len(text),
        "source_count": len(sources),
        "flags": flags,
        "requires_attention": bool(flags),
    }


def assess_evidence_coverage(
    *,
    snapshot: dict[str, Any],
    retrieval_status: dict[str, Any],
    sources: list[dict[str, Any]],
    budget_report: dict[str, Any],
) -> dict[str, Any]:
    context_ids = [str(item_id) for item_id in snapshot.get("item_ids") or [] if str(item_id)]
    selected_ids = [
        str(source.get("item_id") or "")
        for source in sources
        if source.get("kind") != "external" and str(source.get("item_id") or "")
    ]
    selected_unique_ids = sorted(set(selected_ids))
    context_unique_ids = list(dict.fromkeys(context_ids))
    missing_ids = [item_id for item_id in context_unique_ids if item_id not in set(selected_unique_ids)]
    context_count = len(context_unique_ids)
    selected_count = len(selected_unique_ids)
    retrieved_count = safe_int(retrieval_status.get("covered_item_count"), selected_count)
    dropped_by_budget = max(0, safe_int(budget_report.get("dropped_evidence_count"), 0))
    if context_count == 0:
        status = "empty_context"
    elif selected_count == 0:
        status = "no_local_evidence"
    elif selected_count < context_count:
        status = "partial"
    else:
        status = "full"
    return {
        "status": status,
        "context_item_count": context_count,
        "retrieved_item_count": retrieved_count,
        "selected_item_count": selected_count,
        "coverage_ratio": round(selected_count / context_count, 4) if context_count else 0,
        "missing_item_count": len(missing_ids),
        "missing_item_ids": missing_ids[:20],
        "dropped_evidence_count": dropped_by_budget,
        "trimmed_evidence_chars": bool(budget_report.get("trimmed_evidence_chars")),
    }


def assess_evidence_sufficiency(
    *,
    sources: list[dict[str, Any]],
    expansion_policy: dict[str, Any],
    coverage_report: dict[str, Any],
) -> dict[str, Any]:
    local_sources = [source for source in sources if source.get("kind") != "external"]
    external_sources = [source for source in sources if source.get("kind") == "external"]
    scores = [max(safe_int(source.get("rerank_score"), safe_int(source.get("score"), 0)), safe_int(source.get("score"), 0)) for source in sources]
    top_score = max(scores) if scores else 0
    if not sources:
        level = "none"
    elif top_score >= 24 and coverage_report.get("status") in {"full", "partial"}:
        level = "strong"
    elif top_score >= 8:
        level = "moderate"
    else:
        level = "weak"
    return {
        "level": level,
        "top_score": top_score,
        "source_count": len(sources),
        "local_source_count": len(local_sources),
        "external_source_count": len(external_sources),
        "coverage_status": str(coverage_report.get("status") or ""),
        "policy_mode": str(expansion_policy.get("mode") or "local_only"),
    }


def format_evidence_for_prompt(index: int, item: dict[str, Any]) -> str:
    source_index = safe_int(item.get("source_index"), index)
    if item.get("kind") == "external":
        return f"[{source_index}] EXTERNAL: {item.get('title')} ({item.get('url')})\n{item.get('snippet')}"
    return f"[{source_index}] LOCAL: {item.get('title')} ({item.get('item_id')})\n{item.get('snippet')}"


def format_expansion_policy_for_prompt(policy: dict[str, Any]) -> str:
    if not policy:
        return "mode=local_only, reason=default, general_knowledge_allowed=false, web_research_required=false"
    mode = str(policy.get("mode") or "local_only")
    general_allowed = mode == "model_knowledge"
    web_required = mode == "web_research"
    reason = str(policy.get("reason") or "")
    return (
        f"mode={mode}, reason={reason}, "
        f"general_knowledge_allowed={str(general_allowed).lower()}, "
        f"web_research_required={str(web_required).lower()}"
    )


def format_context_for_prompt(snapshot: dict[str, Any]) -> str:
    scope = str(snapshot.get("scope") or "global")
    requested = snapshot.get("requested") if isinstance(snapshot.get("requested"), dict) else {}
    items = snapshot.get("items") if isinstance(snapshot.get("items"), list) else []
    lines = [
        f"scope: {scope}",
        f"item_count: {snapshot.get('item_count', len(items))}",
    ]
    if requested:
        requested_parts = []
        for key in ("library", "collection", "tags", "tag_match", "favorite", "include_archived", "q"):
            value = requested.get(key)
            if value not in (None, "", []):
                requested_parts.append(f"{key}={value}")
        if requested_parts:
            lines.append(f"requested: {', '.join(str(part) for part in requested_parts)}")
    if items:
        lines.append("items:")
        for index, item in enumerate(items[:30], start=1):
            title = str(item.get("title") or item.get("id") or "").strip()
            item_id = str(item.get("id") or "").strip()
            collection = str(item.get("collection") or "").strip()
            tags = ", ".join(str(tag) for tag in item.get("tags") or [] if str(tag).strip())
            summary = str(item.get("summary") or "").strip()
            meta = " / ".join(part for part in (collection, tags) if part)
            suffix = f" ({meta})" if meta else ""
            summary_part = f" - {summary[:180]}" if summary else ""
            lines.append(f"{index}. {title or item_id}{suffix}{summary_part}")
        if len(items) > 30:
            lines.append(f"... {len(items) - 30} more items omitted from context summary")
    return "\n".join(lines)


def recent_conversation_messages(messages: Any, *, limit: int = 6) -> list[dict[str, str]]:
    if not isinstance(messages, list):
        return []
    normalized: list[dict[str, str]] = []
    for message in messages:
        if not isinstance(message, dict):
            continue
        role = str(message.get("role") or "").strip().lower()
        content = str(message.get("content") or "").strip()
        if role not in {"user", "assistant"} or not content:
            continue
        normalized.append({"role": role, "content": content[:900]})
    return normalized[-max(1, int(limit or 6)) :]


def build_retrieval_query(content: str, recent_messages: list[dict[str, str]]) -> str:
    question = str(content or "").strip()
    if not recent_messages or not is_followup_question(question):
        return question
    user_history = [message["content"] for message in recent_messages if message.get("role") == "user"]
    if not user_history:
        return question
    history = " ".join(user_history[-3:])
    return f"{history[:1600]} {question}".strip()


def is_followup_question(content: str) -> bool:
    normalized = str(content or "").strip().lower()
    if not normalized:
        return False
    if len(normalized) > 120:
        return False
    followup_markers = [
        "continue",
        "tell me more",
        "what about",
        "how about",
        "that",
        "this",
        "it",
        "they",
        "them",
        "those",
        "继续",
        "展开",
        "详细",
        "再说",
        "这个",
        "这些",
        "它",
        "他们",
        "上述",
        "前面",
        "刚才",
        "还有",
        "搜索",
        "联网",
        "查一下",
        "网上查",
        "官网查",
        "呢",
        "続け",
        "詳しく",
        "それ",
        "これ",
        "検索",
        "調べ",
    ]
    return any(marker in normalized for marker in followup_markers)


def asks_for_external_search(content: str) -> bool:
    normalized = str(content or "").strip().lower()
    markers = [
        "search",
        "web",
        "online",
        "source",
        "official",
        "link",
        "citation",
        "查一下",
        "联网",
        "网上",
        "官网",
        "链接",
        "来源",
        "引用",
        "調べ",
        "検索",
        "公式",
        "リンク",
    ]
    return any(marker in normalized for marker in markers)


def is_time_sensitive_question(content: str) -> bool:
    normalized = str(content or "").strip().lower()
    markers = [
        "latest",
        "current",
        "today",
        "yesterday",
        "recent",
        "now",
        "price",
        "pricing",
        "version",
        "release",
        "news",
        "law",
        "policy",
        "ceo",
        "最新",
        "当前",
        "现在",
        "今天",
        "昨天",
        "最近",
        "价格",
        "报价",
        "版本",
        "发布",
        "新闻",
        "政策",
        "法规",
        "法律",
        "最新",
        "現在",
        "今日",
        "昨日",
        "最近",
        "価格",
        "料金",
        "バージョン",
        "リリース",
        "ニュース",
        "法律",
    ]
    if any(marker in normalized for marker in markers):
        return True
    year = datetime.now(timezone.utc).year
    return str(year) in normalized or str(year - 1) in normalized or str(year + 1) in normalized


def format_recent_conversation_for_prompt(messages: list[dict[str, str]]) -> str:
    if not messages:
        return ""
    lines = []
    for index, message in enumerate(messages, start=1):
        role = "USER" if message.get("role") == "user" else "ASSISTANT"
        content = str(message.get("content") or "").replace("\n", " ").strip()
        lines.append(f"{index}. {role}: {content[:600]}")
    return "\n".join(lines)


def retrieval_coverage_status(snapshot: dict[str, Any], evidence: list[dict[str, Any]]) -> dict[str, Any]:
    context_ids = [str(item_id) for item_id in snapshot.get("item_ids") or [] if str(item_id)]
    evidence_ids = {
        str(item.get("item_id") or "")
        for item in evidence
        if item.get("kind") != "external" and str(item.get("item_id") or "")
    }
    context_count = len(context_ids)
    covered_count = len(evidence_ids)
    return {
        "context_item_count": context_count,
        "covered_item_count": covered_count,
        "coverage_ratio": round(covered_count / context_count, 4) if context_count else 0,
    }


def public_qa_run(state: KnowledgeQAState, *, status: str = "completed", error: dict[str, str] | None = None) -> dict[str, Any]:
    local_sources = [source for source in state.sources if source.get("kind") != "external"]
    external_sources = [source for source in state.sources if source.get("kind") == "external"]
    return {
        "id": f"qa_{uuid.uuid4().hex}",
        "kind": "knowledge_qa",
        "status": status,
        "started_at": state.started_at,
        "completed_at": state.completed_at,
        "duration_ms": state.duration_ms,
        "conversation_id": state.conversation_id,
        "spec": {"source_mode": str(state.context_snapshot.get("source_mode") or "local_only")},
        "graph": KnowledgeQAGraph.name,
        "generation_intent": {},
        "qa_report": {
            "source_count": len(state.sources),
            "local_source_count": len(local_sources),
            "external_source_count": len(external_sources),
            "skipped_model_call": bool(state.skipped_model_call),
            "retrieval": state.retrieval_status,
            "external_status": state.external_status,
            "research_trace": state.research_trace,
            "expansion_policy": state.expansion_policy,
            "evidence_scope": state.evidence_scope_report,
            "evidence_ranking": state.evidence_rank_report,
            "evidence_rerank": state.evidence_rerank_report,
            "evidence_budget": state.evidence_budget,
            "evidence_coverage": state.evidence_coverage_report,
            "evidence_sufficiency": state.evidence_sufficiency_report,
            "citation": state.citation_report,
            "answer_quality": state.answer_quality_report,
        },
        "review_decision": {},
        "node_trace": state.node_trace,
        "agent_trace": state.agent_trace,
        "prompt_trace": state.prompt_trace,
        "skill_trace": state.skill_trace,
        "usage": state.usage,
        "budget": state.budget,
        "error": error or {},
        "material": {},
        "item_id": "",
    }
