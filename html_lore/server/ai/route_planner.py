from __future__ import annotations

from typing import Any

from .conversation_resolution import recent_conversation_messages, resolve_conversation_turn
from .tools import asks_for_external_search, is_concept_explanation_question, is_time_sensitive_question
from .search_planner import classify_entity_question_attribute, is_entity_background_question


def plan_ai_route(question: str, *, context: dict[str, Any] | None = None, state: dict[str, Any] | None = None) -> dict[str, Any]:
    qa_plan = plan_qa_route(question, context=context, state=state)
    return {
        "route_version": "ai-route.v1",
        "workflow": "knowledge_qa",
        "task_family": "qa",
        "operation": "answer_question",
        "entrypoint": "knowledge_qa",
        "execution_mode": "sync",
        "context_policy": "resolved_conversation_context",
        "future_workflows": {
            "generate": "note_generation",
            "modify": "note_modification",
            "manage": "knowledge_management",
        },
        **qa_plan,
    }


def plan_qa_route(question: str, *, context: dict[str, Any] | None = None, state: dict[str, Any] | None = None) -> dict[str, Any]:
    text = str(question or "").strip()
    context = dict(context or {})
    state = dict(state or {})
    recent_messages = recent_conversation_messages(state.get("conversation_messages"))
    resolution = resolve_conversation_turn(text, recent_messages)
    routing_text = str(resolution.get("resolved_query") or text).strip()
    lowered = routing_text.lower()

    if asks_for_external_search(routing_text) or is_time_sensitive_question(routing_text):
        search_intent = "general"
        if any(marker in lowered for marker in ("政策", "法规", "监管", "policy", "regulation", "发改", "能源局")):
            search_intent = "policy_lookup"
        elif any(marker in lowered for marker in ("version", "release", "changelog", "版本", "发布")):
            search_intent = "version_lookup"
        elif any(marker in lowered for marker in ("official", "官网", "官方")):
            search_intent = "official_lookup"
        return route_payload(
            intent="current_info",
            retrieval_mode="web_research",
            should_expand=True,
            should_search=True,
            search_intent=search_intent,
            locality="local_context_first",
            reason="time_sensitive_or_search_requested",
            conversation_resolution=resolution,
        )

    entity_attribute = classify_entity_question_attribute(routing_text)
    if is_entity_background_question(routing_text):
        return route_payload(
            intent="current_info",
            retrieval_mode="web_research",
            should_expand=True,
            should_search=True,
            search_intent="entity_lookup",
            locality="local_context_first",
            reason=entity_route_reason(entity_attribute, routing_text != text),
            conversation_resolution=resolution,
        )

    if is_concept_explanation_question(routing_text):
        return route_payload(
            intent="concept_clarify",
            retrieval_mode="model_knowledge",
            should_expand=True,
            should_search=False,
            search_intent="none",
            locality="local_context_first",
            reason="concept_clarification",
            conversation_resolution=resolution,
        )

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
        return route_payload(
            intent="explain_deeper",
            retrieval_mode="model_knowledge",
            should_expand=True,
            should_search=False,
            search_intent="none",
            locality="local_context_first",
            reason="deeper_explanation",
            conversation_resolution=resolution,
        )

    if any(marker in lowered for marker in ("总结", "概括", "summary", "summarize")):
        return route_payload(
            intent="summary",
            retrieval_mode="local_evidence",
            should_expand=False,
            should_search=False,
            search_intent="none",
            locality="local_only",
            reason="summary_request",
            conversation_resolution=resolution,
        )

    if any(marker in lowered for marker in ("对比", "比较", "区别", "联系", "compare", "validate", "验证")):
        return route_payload(
            intent="compare_validate",
            retrieval_mode="local_evidence",
            should_expand=True,
            should_search=False,
            search_intent="none",
            locality="local_context_first",
            reason="comparison_request",
            conversation_resolution=resolution,
        )

    return route_payload(
        intent="summary",
        retrieval_mode="local_evidence",
        should_expand=True,
        should_search=False,
        search_intent="none",
        locality="local_context_first",
        reason="default_local_context",
        conversation_resolution=resolution,
    )


def route_payload(
    *,
    intent: str,
    retrieval_mode: str,
    should_expand: bool,
    should_search: bool,
    search_intent: str,
    locality: str,
    reason: str,
    conversation_resolution: dict[str, Any],
) -> dict[str, Any]:
    return {
        "intent": intent,
        "retrieval_mode": retrieval_mode,
        "should_expand": bool(should_expand),
        "should_search": bool(should_search),
        "search_intent": search_intent,
        "locality": locality,
        "reason": reason,
        "conversation_resolution": dict(conversation_resolution or {}),
    }


__all__ = ["plan_ai_route", "plan_qa_route"]


def entity_route_reason(attribute: str | None, is_followup: bool) -> str:
    suffix = "followup" if is_followup else "lookup"
    if attribute == "ownership":
        return f"entity_ownership_{suffix}"
    if attribute == "team":
        return f"entity_team_{suffix}"
    if attribute == "registry":
        return f"entity_registry_{suffix}"
    return f"entity_background_{suffix}"
