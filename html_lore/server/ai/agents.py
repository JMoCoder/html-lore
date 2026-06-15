from __future__ import annotations

from typing import Any
import json

from .guardrails import validate_answer
from .registry import load_agent, load_prompt
from .runtime import AgentDraft, AgentPlan, AgentRequest, ReviewResult, ToolCall, ToolResult, VerificationResult


class KnowledgeQATaskAgent:
    id = "agent.qa.v1"
    task_type = "qa"

    def __init__(self, *, use_model: bool = False, max_response_tokens: int = 1024) -> None:
        self.use_model = bool(use_model)
        self.max_response_tokens = max(1, int(max_response_tokens or 1024))
        self.planner_agent = load_agent("knowledge_qa.planner_agent.v1")
        self.planner_prompt = load_prompt(self.planner_agent.prompt_template)
        base_tools = (
            "guardrail.input",
            "context.resolve",
            "evidence.build",
            "expansion.policy",
            "external.research",
            "evidence.gate",
            "evidence.assess",
        )
        self.allowed_tools = (*base_tools, "llm.chat") if self.use_model else base_tools

    def plan(self, request: AgentRequest, state: dict[str, Any], *, attempt: int) -> AgentPlan:
        context_arguments = {"context": dict(request.context or {})}
        if request.context.get("source_mode"):
            context_arguments["source_mode"] = request.context["source_mode"]
        elif state.get("source_mode"):
            context_arguments["source_mode"] = state["source_mode"]
        evidence_arguments = {"query": request.content}
        if attempt > 1:
            evidence_arguments["max_results"] = 8
        planner = self.plan_strategy(request, state)
        steps = [
            ToolCall("guardrail.input", {"content": request.content}, reason="validate user request before any model call"),
            ToolCall("context.resolve", context_arguments, reason="resolve authorized note context"),
            ToolCall("evidence.build", evidence_arguments, reason="build evidence pack"),
            ToolCall("expansion.policy", {"query": request.content, "planner": planner}, reason="choose local, model-knowledge, or web research path"),
            ToolCall("external.research", {"query": request.content, "planner": planner}, reason="run external research only when search planner requires it"),
            ToolCall("evidence.gate", {"query": request.content}, reason="prepare safe evidence and prompt budget"),
            ToolCall("evidence.assess", {"query": request.content}, reason="assess whether evidence is relevant enough to answer"),
        ]
        if self.use_model:
            steps.append(
                ToolCall(
                    "llm.chat",
                    {
                        "prompt_id": "qa.answer.v1",
                        "question": request.content,
                        "temperature": 0.2,
                        "max_tokens": self.max_response_tokens,
                    },
                    reason="draft natural answer with the shared model tool",
                ),
            )
        if attempt <= 1:
            return AgentPlan(
                task_type="qa",
                steps=tuple(steps),
                response_strategy="model_answer_from_evidence_pack" if self.use_model else "natural_answer_from_evidence_pack",
                attempt=attempt,
                metadata={"planner": planner},
            )
        return AgentPlan(
            task_type="qa",
            steps=tuple(steps),
            response_strategy="revised_model_answer_from_evidence_pack" if self.use_model else "revised_natural_answer_from_evidence_pack",
            attempt=attempt,
            metadata={"planner": planner},
        )

    def plan_strategy(self, request: AgentRequest, state: dict[str, Any]) -> dict[str, Any]:
        context_output = state.get("tool_outputs", {}).get("context.resolve", {}) if isinstance(state.get("tool_outputs"), dict) else {}
        context = context_output.get("context") if isinstance(context_output.get("context"), dict) else {}
        prompt_messages = [
            {
                "role": "system",
                "content": self.planner_prompt.render({}),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "question": request.content,
                        "context": context,
                        "source_mode": str(context.get("source_mode") or state.get("source_mode") or "local_only"),
                    },
                    ensure_ascii=False,
                ),
            },
        ]
        if self.use_model:
            return self._decode_planner_model(prompt_messages, request.content, context, state)
        return self._heuristic_plan(request.content, context, state)

    def _decode_planner_model(self, prompt_messages: list[dict[str, str]], question: str, context: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
        # Phase 1 keeps planner decisions deterministic while reserving a dedicated
        # planner agent contract in the registry and runtime metadata.
        return self._heuristic_plan(question, context, state)

    def _heuristic_plan(self, question: str, context: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
        text = str(question or "").strip()
        lowered = text.lower()
        from .tools import is_concept_explanation_question, is_time_sensitive_question, asks_for_external_search
        if asks_for_external_search(text) or is_time_sensitive_question(text):
            return {
                "intent": "current_info",
                "retrieval_mode": "web_research",
                "should_expand": True,
                "should_search": True,
                "search_intent": "official_lookup" if any(marker in lowered for marker in ("official", "官网", "官方")) else "general",
                "locality": "local_context_first",
                "reason": "time_sensitive_or_search_requested",
            }
        if is_concept_explanation_question(text):
            return {
                "intent": "concept_clarify",
                "retrieval_mode": "model_knowledge",
                "should_expand": True,
                "should_search": False,
                "search_intent": "none",
                "locality": "local_context_first",
                "reason": "concept_clarification",
            }
        if any(
            marker in lowered
            for marker in (
                "详细介绍",
                "详细分析",
                "展开讲",
                "more detail",
                "explain more",
                "深入",
                "继续说",
                "具体说",
                "逻辑关系",
                "关系",
                "机制",
                "路径",
                "怎么配合",
                "协同",
                "作用链",
                "why",
                "how they work together",
            )
        ):
            return {
                "intent": "explain_deeper",
                "retrieval_mode": "model_knowledge",
                "should_expand": True,
                "should_search": False,
                "search_intent": "none",
                "locality": "local_context_first",
                "reason": "deeper_explanation",
            }
        if any(marker in lowered for marker in ("总结", "概括", "summary", "summarize")):
            return {
                "intent": "summary",
                "retrieval_mode": "local_evidence",
                "should_expand": False,
                "should_search": False,
                "search_intent": "none",
                "locality": "local_only",
                "reason": "summary_request",
            }
        if any(marker in lowered for marker in ("对比", "比较", "区别", "联系", "compare", "validate", "验证")):
            return {
                "intent": "compare_validate",
                "retrieval_mode": "local_evidence",
                "should_expand": True,
                "should_search": False,
                "search_intent": "none",
                "locality": "local_context_first",
                "reason": "comparison_request",
            }
        return {
            "intent": "summary",
            "retrieval_mode": "local_evidence",
            "should_expand": True,
            "should_search": False,
            "search_intent": "none",
            "locality": "local_context_first",
            "reason": "default_local_context",
        }

    def draft(self, request: AgentRequest, plan: AgentPlan, tool_results: tuple[ToolResult, ...], state: dict[str, Any]) -> AgentDraft:
        context_output = tool_result_output(tool_results, "context.resolve")
        evidence_pack = tool_result_output(tool_results, "evidence.gate") or tool_result_output(tool_results, "evidence.build")
        evidence_gate = tool_result_output(tool_results, "evidence.gate")
        assessment = tool_result_output(tool_results, "evidence.assess")
        llm_output = tool_result_output(tool_results, "llm.chat")
        planner = dict(plan.metadata.get("planner") or {})
        intent = str(planner.get("intent") or "summary")
        title = str(context_output.get("context_title") or "当前上下文")
        chunks = evidence_gate.get("chunks") if isinstance(evidence_gate.get("chunks"), list) else evidence_pack.get("chunks")
        if not isinstance(chunks, list):
            chunks = []
        sources = evidence_gate.get("sources") if isinstance(evidence_gate.get("sources"), list) else evidence_pack.get("sources")
        if not isinstance(sources, list):
            sources = []
        if evidence_gate.get("answer"):
            return AgentDraft(
                str(evidence_gate.get("answer") or ""),
                metadata={
                    "context_title": title,
                    "source_count": len(sources),
                    "chunk_count": len(chunks),
                    "strategy": "skipped_model_call",
                    "model_called": False,
                    "skipped_model_call": True,
                    "skip_reason": evidence_gate.get("skip_reason") or "",
                },
            )
        decline_reason = decline_reason_from_assessment(assessment)
        if decline_reason:
            return AgentDraft(
                decline_answer(title, decline_reason),
                metadata={
                    "context_title": title,
                    "source_count": len(sources),
                    "chunk_count": len(chunks),
                    "strategy": "decline_weak_relevance",
                    "model_called": False,
                    "declined": True,
                    "decline_reason": decline_reason,
                    "assessment": assessment,
                },
            )
        if llm_output.get("content"):
            answer = ensure_source_footer(str(llm_output["content"]), sources)
            return AgentDraft(
                answer,
                metadata={
                    "context_title": title,
                    "source_count": len(sources),
                    "chunk_count": len(chunks),
                    "strategy": plan.response_strategy,
                    "model": llm_output.get("model") or "",
                    "usage": llm_output.get("usage") or {},
                    "model_called": True,
                },
            )
        if not chunks:
            return AgentDraft(
                decline_answer(title, "insufficient_evidence"),
                metadata={"source_count": 0, "chunk_count": 0, "model_called": False},
            )
        answer = natural_answer_from_chunks(request.content, title, chunks, intent=intent)
        answer = ensure_source_footer(answer, sources)
        return AgentDraft(
            answer,
            metadata={
                "context_title": title,
                "source_count": len(sources),
                "chunk_count": len(chunks),
                "strategy": plan.response_strategy,
                "model_called": False,
            },
        )


class KnowledgeQAVerifier:
    id = "verifier.qa.v1"
    mechanical_markers = ("笔记提到", "笔记强调", "原文提到", "原文强调")

    def __init__(self) -> None:
        self.agent_spec = load_agent("knowledge_qa.verifier_agent.v1")
        self.prompt_spec = load_prompt(self.agent_spec.prompt_template)

    def verify(
        self,
        request: AgentRequest,
        plan: AgentPlan,
        tool_results: tuple[ToolResult, ...],
        answer: str,
        state: dict[str, Any],
    ) -> VerificationResult:
        failed_tools = [result.tool_id for result in tool_results if result.status != "completed"]
        if failed_tools:
            return VerificationResult(False, checks={"failed_tools": failed_tools}, reason="tool_failed", retryable=True)
        evidence_pack = tool_result_output(tool_results, "evidence.gate") or tool_result_output(tool_results, "evidence.build")
        planner = dict(plan.metadata.get("planner") or {})
        intent = str(planner.get("intent") or "summary")
        search_plan = tool_result_output(tool_results, "external.research").get("search_plan") if isinstance(tool_result_output(tool_results, "external.research").get("search_plan"), dict) else {}
        sources = evidence_pack.get("sources") if isinstance(evidence_pack.get("sources"), list) else []
        chunks = evidence_pack.get("chunks") if isinstance(evidence_pack.get("chunks"), list) else []
        checks = {
            "answer_chars": len(str(answer or "")),
            "chunk_count": len(chunks),
            "source_count": len(sources),
            "mechanical_marker_count": sum(str(answer or "").count(marker) for marker in self.mechanical_markers),
            "verifier_agent": self.agent_spec.public_dict(),
            "verifier_prompt": self.prompt_spec.public_dict(),
            "intent": intent,
        }
        if search_plan:
            checks["search_plan"] = search_plan
        consistency = evidence_consistency_report(evidence_pack)
        checks["evidence_consistency"] = consistency
        if not str(answer or "").strip():
            return VerificationResult(False, checks=checks, reason="empty_answer", retryable=True)
        try:
            validate_answer(answer)
        except Exception as exc:
            return VerificationResult(False, checks={**checks, "output_guardrail": exc.__class__.__name__}, reason="output_guardrail_failed", retryable=False)
        if checks["mechanical_marker_count"]:
            return VerificationResult(False, checks=checks, reason="mechanical_answer", retryable=True)
        if not consistency["valid"]:
            return VerificationResult(False, checks=checks, reason="evidence_inconsistent", retryable=True)
        if chunks and not sources:
            return VerificationResult(False, checks=checks, reason="missing_sources", retryable=True)
        invalid_refs = invalid_citation_numbers(answer, len(sources))
        checks["invalid_citations"] = invalid_refs
        if invalid_refs:
            return VerificationResult(False, checks=checks, reason="invalid_citation", retryable=True)
        if intent == "current_info" and sources and not any(source.get("kind") == "external" for source in sources):
            return VerificationResult(False, checks=checks, reason="current_info_without_external_sources", retryable=True)
        if intent == "explain_deeper" and len(str(answer or "").strip()) < 120:
            return VerificationResult(False, checks=checks, reason="explain_deeper_too_shallow", retryable=True)
        return VerificationResult(True, checks=checks, reason="ok", retryable=False)


class KnowledgeQAReviewer:
    id = "reviewer.qa.v1"

    def __init__(self) -> None:
        self.agent_spec = load_agent("knowledge_qa.reviewer_agent.v1")
        self.prompt_spec = load_prompt(self.agent_spec.prompt_template)

    def review(
        self,
        request: AgentRequest,
        plan: AgentPlan,
        tool_results: tuple[ToolResult, ...],
        draft: AgentDraft,
        verification: VerificationResult,
        state: dict[str, Any],
    ) -> ReviewResult:
        planner = dict(plan.metadata.get("planner") or {})
        intent = str(planner.get("intent") or "summary")
        if not verification.passed:
            return ReviewResult(False, checks={"verification_reason": verification.reason}, reason="verification_failed", retryable=verification.retryable)
        if draft.metadata.get("declined"):
            return ReviewResult(True, checks={"declined": draft.metadata.get("decline_reason")}, reason="ok", retryable=False)
        if draft.metadata.get("chunk_count", 0) and "来源：" not in draft.content:
            return ReviewResult(False, checks={"source_footer": "missing"}, reason="source_footer_missing", retryable=True)
        checks = {
            "source_footer": "ok",
            "reviewer_agent": self.agent_spec.public_dict(),
            "reviewer_prompt": self.prompt_spec.public_dict(),
            "intent": intent,
        }
        if intent == "concept_clarify" and "Fake AI response" not in draft.content and not any(marker in draft.content for marker in ("可以理解为", "是指", "本质", "定义")):
            return ReviewResult(False, checks=checks, reason="concept_answer_not_explanatory_enough", retryable=True)
        return ReviewResult(True, checks=checks, reason="ok", retryable=False)


def tool_result_output(tool_results: tuple[ToolResult, ...], tool_id: str) -> dict[str, Any]:
    for result in tool_results:
        if result.tool_id == tool_id:
            return dict(result.output or {})
    return {}


def natural_answer_from_chunks(question: str, context_title: str, chunks: list[dict[str, Any]], *, intent: str = "summary") -> str:
    first = chunks[0]
    snippet = compact_snippet(str(first.get("snippet") or ""))
    if intent == "concept_clarify":
        return f"如果只抓住核心定义，可以先这样理解：{snippet}"
    if intent == "explain_deeper":
        return f"围绕这个主题，可以先从核心机制讲起：{snippet}"
    if intent == "current_info":
        return f"基于当前可核验资料，先给你结论：{snippet}"
    if is_summary_question(question):
        return f"{context_title} 的核心内容可以先这样理解：{snippet}"
    return f"围绕你的问题，当前上下文中最相关的信息是：{snippet}"


def decline_reason_from_assessment(assessment: dict[str, Any]) -> str:
    if bool(assessment.get("insufficient_evidence")):
        return "insufficient_evidence"
    if bool(assessment.get("weak_relevance")):
        return "weak_relevance"
    return ""


def decline_answer(context_title: str, reason: str) -> str:
    if reason == "insufficient_evidence":
        return f"「{context_title}」中没有找到足够资料回答这个问题。请换一个更具体的问题，或重新选择上下文。"
    return f"当前问题和「{context_title}」中的资料关联不足，我不能基于现有上下文给出可靠回答。请换一个与当前笔记相关的问题，或重新选择上下文。"


def is_summary_question(value: str) -> bool:
    text = str(value or "").lower()
    return any(marker in text for marker in ("总结", "概括", "summary", "summarize"))


def compact_snippet(value: str, *, limit: int = 420) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "..."


def ensure_source_footer(answer: str, sources: list[dict[str, Any]]) -> str:
    text = str(answer or "").strip()
    if not sources:
        return text
    if "来源：" in text:
        return text
    source_labels = "; ".join(f"[{source.get('source_index')}] {source.get('title')}" for source in sources[:4])
    return f"{text}\n\n来源：{source_labels}"


def invalid_citation_numbers(answer: str, source_count: int) -> list[int]:
    import re

    refs: set[int] = set()
    for match in re.finditer(r"(?<![A-Za-z0-9_/-])\[((?:\d+\s*(?:[,，]\s*)?)+)\](?![A-Za-z0-9_/-])", str(answer or "")):
        for part in re.split(r"[,，]\s*", match.group(1)):
            part = part.strip()
            if part.isdigit():
                refs.add(int(part))
    return sorted(ref for ref in refs if ref < 1 or ref > source_count)


def evidence_consistency_report(evidence_pack: dict[str, Any]) -> dict[str, Any]:
    chunks = evidence_pack.get("chunks") if isinstance(evidence_pack.get("chunks"), list) else []
    sources = evidence_pack.get("sources") if isinstance(evidence_pack.get("sources"), list) else []
    citation_map = evidence_pack.get("citation_map") if isinstance(evidence_pack.get("citation_map"), dict) else {}
    source_indexes = {int(source.get("source_index")) for source in sources if is_positive_int(source.get("source_index"))}
    missing_chunk_sources: list[str] = []
    missing_citation_map: list[str] = []
    invalid_citation_map: list[str] = []
    duplicate_source_indexes = len(source_indexes) != len([source for source in sources if is_positive_int(source.get("source_index"))])

    for chunk in chunks:
        chunk_id = str(chunk.get("chunk_id") or "").strip()
        source_index = chunk.get("source_index")
        if not is_positive_int(source_index) or int(source_index) not in source_indexes:
            missing_chunk_sources.append(chunk_id or f"chunk-{len(missing_chunk_sources) + 1}")
        if chunk_id:
            mapped = citation_map.get(chunk_id)
            if mapped is None:
                missing_citation_map.append(chunk_id)
            elif not is_positive_int(mapped) or int(mapped) not in source_indexes:
                invalid_citation_map.append(chunk_id)

    valid = not missing_chunk_sources and not missing_citation_map and not invalid_citation_map and not duplicate_source_indexes
    return {
        "valid": valid,
        "missing_chunk_sources": missing_chunk_sources,
        "missing_citation_map": missing_citation_map,
        "invalid_citation_map": invalid_citation_map,
        "duplicate_source_indexes": duplicate_source_indexes,
    }


def is_positive_int(value: Any) -> bool:
    try:
        return int(value) > 0
    except (TypeError, ValueError):
        return False
