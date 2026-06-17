from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import uuid

from html_lore.server.config import ServerSettings
from html_lore.server.items import ItemService

from .agents import KnowledgeQATaskAgent, KnowledgeQAReviewer, KnowledgeQAVerifier
from .conversations import ConversationStore
from .external_search import DisabledExternalSearchAdapter, build_external_search_adapter
from .knowledge_qa_graph import KnowledgeQAGraph, KnowledgeQAState, public_qa_run
from .metrics import evaluate_qa_result
from .model_client import ModelClient
from .prompts import build_qa_answer_messages
from .langgraph_qa import LangGraphKnowledgeQARuntime, LangGraphQAError, build_langgraph_qa_runtime
from .runtime import AgentRequest, AgentRunResult, AgentRuntime, BasicFinalizer, ToolRegistry
from .tools import ContextTool, EvidenceAssessmentTool, EvidenceGateTool, EvidenceTool, ExpansionPolicyTool, ExternalResearchTool, InputGuardrailTool, LLMChatTool, SearchPlanTool, SourceEvaluatorTool


DEFAULT_RUNTIME_EVAL_CASES = [
    {"id": "global-summary", "question": "Summarize the current knowledge base.", "context": {"scope": "global"}},
    {"id": "global-mcp", "question": "What does MCP security cover?", "context": {"scope": "global"}},
    {"id": "global-docker", "question": "What Docker topics are mentioned?", "context": {"scope": "global"}},
]


@dataclass(frozen=True)
class QARuntimeEvalSpec:
    content_dir: Path
    meta_dir: Path | None
    public_dir: Path
    cases: list[dict[str, Any]]
    provider: str = "fake"
    base_url: str = ""
    api_key: str = ""
    model: str = "fake-eval-model"
    retrieval_mode: str = "keyword"
    max_context_items: int = 50
    max_prompt_chars: int = 12000
    max_response_tokens: int = 1024
    run_legacy: bool = True
    run_agent: bool = True
    run_langgraph: bool = False
    agent_uses_model: bool = True


def build_qa_tools(
    *,
    item_service: ItemService,
    model_client: ModelClient,
    settings: ServerSettings,
    use_model: bool = True,
) -> ToolRegistry:
    tools = ToolRegistry()
    tools.register(InputGuardrailTool(max_message_chars=settings.ai_max_message_chars))
    tools.register(ContextTool(item_service, max_context_items=settings.ai_max_context_items))
    tools.register(
        EvidenceTool(
            item_service,
            model_client=model_client,
            retrieval_mode=settings.ai_retrieval_mode,
            max_results=5,
        ),
    )
    tools.register(ExpansionPolicyTool())
    tools.register(SearchPlanTool(model_client if use_model else None))
    tools.register(ExternalResearchTool(build_external_search_adapter(settings)))
    tools.register(SourceEvaluatorTool(model_client if use_model else None))
    tools.register(EvidenceGateTool(max_prompt_chars=settings.ai_max_prompt_chars))
    tools.register(EvidenceAssessmentTool())
    if use_model:
        tools.register(
            LLMChatTool(
                model_client,
                prompt_builders={"qa.answer.v1": build_qa_answer_messages},
                default_max_tokens=settings.ai_max_response_tokens,
            ),
        )
    return tools


def build_qa_agent_runtime(
    *,
    item_service: ItemService,
    model_client: ModelClient,
    settings: ServerSettings,
    use_model: bool = True,
) -> AgentRuntime:
    return AgentRuntime(
        agents=(KnowledgeQATaskAgent(use_model=use_model, max_response_tokens=settings.ai_max_response_tokens, model_client=model_client),),
        tools=build_qa_tools(item_service=item_service, model_client=model_client, settings=settings, use_model=use_model),
        verifier=KnowledgeQAVerifier(use_model=use_model, model_client=model_client),
        reviewer=KnowledgeQAReviewer(use_model=use_model, model_client=model_client),
    )


def build_qa_langgraph_runtime(
    *,
    item_service: ItemService,
    model_client: ModelClient,
    settings: ServerSettings,
    use_model: bool = True,
) -> LangGraphKnowledgeQARuntime:
    return build_langgraph_qa_runtime(
        agent=KnowledgeQATaskAgent(use_model=use_model, max_response_tokens=settings.ai_max_response_tokens, model_client=model_client),
        tools=build_qa_tools(item_service=item_service, model_client=model_client, settings=settings, use_model=use_model),
        verifier=KnowledgeQAVerifier(use_model=use_model, model_client=model_client),
        reviewer=KnowledgeQAReviewer(use_model=use_model, model_client=model_client),
        finalizer=BasicFinalizer(),
    )


def build_selected_qa_runtime(
    *,
    item_service: ItemService,
    model_client: ModelClient,
    settings: ServerSettings,
    use_model: bool = True,
) -> tuple[AgentRuntime | LangGraphKnowledgeQARuntime, str]:
    engine = str(settings.ai_qa_engine or "auto").strip().lower()
    if engine in {"auto", "langgraph"}:
        try:
            return (
                build_qa_langgraph_runtime(
                    item_service=item_service,
                    model_client=model_client,
                    settings=settings,
                    use_model=use_model,
                ),
                LangGraphKnowledgeQARuntime.name,
            )
        except LangGraphQAError:
            if engine == "langgraph":
                raise
    return (
        build_qa_agent_runtime(
            item_service=item_service,
            model_client=model_client,
            settings=settings,
            use_model=use_model,
        ),
        "AgentRuntime.qa.v1",
    )


def run_qa_runtime_eval(spec: QARuntimeEvalSpec) -> dict[str, Any]:
    from .eval import InMemoryEvalConversationStore
    from .providers import AIProviderConfig

    settings = ServerSettings(
        content_dir=spec.content_dir,
        meta_dir=spec.meta_dir,
        public_dir=spec.public_dir,
        site_title="HTMlore QA Runtime Eval",
        max_upload_bytes=10 * 1024 * 1024,
        ai_max_context_items=spec.max_context_items,
        ai_max_prompt_chars=spec.max_prompt_chars,
        ai_max_response_tokens=spec.max_response_tokens,
        ai_retrieval_mode=spec.retrieval_mode,
    )
    item_service = ItemService(settings)
    conversation_store = InMemoryEvalConversationStore(item_service, max_context_items=spec.max_context_items)
    model_client = ModelClient(
        AIProviderConfig(
            provider=spec.provider,
            base_url=spec.base_url,
            api_key=spec.api_key,
            model=spec.model,
            enabled=True,
        ),
    )
    cases = normalize_runtime_eval_cases(spec.cases)
    results: list[dict[str, Any]] = []
    for case in cases:
        comparison = compare_qa_runtimes(
            question=case["question"],
            context=case["context"],
            item_service=item_service,
            conversation_store=conversation_store,
            model_client=model_client,
            settings=settings,
            run_legacy=spec.run_legacy,
            run_agent=spec.run_agent,
            run_langgraph=spec.run_langgraph,
            agent_uses_model=spec.agent_uses_model,
        )
        results.append({"id": case["id"], **comparison})
    return {
        "kind": "qa_runtime_batch_eval",
        "provider": spec.provider,
        "model": spec.model,
        "retrieval_mode": spec.retrieval_mode,
        "persistent": False,
        "item_count": len(item_service.manifest().get("items", [])),
        "case_count": len(results),
        "engines": [name for name, enabled in (("legacy", spec.run_legacy), ("agent", spec.run_agent), ("langgraph", spec.run_langgraph)) if enabled],
        "summary": summarize_runtime_eval(results),
        "results": results,
    }


def load_runtime_eval_cases(path: Path | None) -> list[dict[str, Any]]:
    if path is None:
        return [dict(case) for case in DEFAULT_RUNTIME_EVAL_CASES]
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("cases")
    if not isinstance(data, list):
        raise ValueError("Runtime evaluation file must be a JSON list or an object with a cases list.")
    return normalize_runtime_eval_cases(data)


def normalize_runtime_eval_cases(values: list[Any]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for index, raw in enumerate(values, start=1):
        if isinstance(raw, str):
            question = raw.strip()
            context: dict[str, Any] = {"scope": "global"}
            case_id = f"case-{index}"
        elif isinstance(raw, dict):
            question = str(raw.get("question") or raw.get("content") or "").strip()
            context = dict(raw.get("context")) if isinstance(raw.get("context"), dict) else {"scope": "global"}
            case_id = str(raw.get("id") or f"case-{index}").strip()
        else:
            continue
        if question:
            cases.append({"id": case_id or f"case-{index}", "question": question, "context": sanitize_context_for_eval(context)})
    if not cases:
        raise ValueError("Runtime evaluation requires at least one valid case.")
    return cases


def summarize_runtime_eval(results: list[dict[str, Any]]) -> dict[str, Any]:
    engines = sorted({name for result in results for name in result.get("results", {})})
    summary: dict[str, Any] = {}
    for engine in engines:
        engine_results = [result["results"][engine] for result in results if engine in result.get("results", {})]
        metrics = [
            result.get("metrics", {}).get(engine)
            for result in results
            if isinstance(result.get("metrics"), dict) and isinstance(result.get("metrics", {}).get(engine), dict)
        ]
        flag_counts: dict[str, int] = {}
        for metric in metrics:
            for flag in metric.get("flags") or []:
                flag_counts[str(flag)] = flag_counts.get(str(flag), 0) + 1
        summary[engine] = {
            "case_count": len(engine_results),
            "completed_count": len([result for result in engine_results if result.get("status") == "completed"]),
            "needs_attention_count": len([metric for metric in metrics if metric.get("requires_attention")]),
            "flag_counts": dict(sorted(flag_counts.items())),
        }
    return summary


def compare_qa_runtimes(
    *,
    question: str,
    context: dict[str, Any],
    item_service: ItemService,
    conversation_store: ConversationStore,
    model_client: ModelClient,
    settings: ServerSettings,
    run_legacy: bool = True,
    run_agent: bool = True,
    run_langgraph: bool = False,
    agent_uses_model: bool = True,
) -> dict[str, Any]:
    results: dict[str, Any] = {}
    if run_legacy:
        results["legacy"] = run_legacy_qa(
            question=question,
            context=context,
            item_service=item_service,
            conversation_store=conversation_store,
            model_client=model_client,
            settings=settings,
        )
    if run_agent:
        results["agent"] = run_agent_qa(
            question=question,
            context=context,
            item_service=item_service,
            model_client=model_client,
            settings=settings,
            use_model=agent_uses_model,
        )
    if run_langgraph:
        results["langgraph"] = run_langgraph_qa(
            question=question,
            context=context,
            item_service=item_service,
            model_client=model_client,
            settings=settings,
            use_model=agent_uses_model,
        )
    metrics = {
        name: result.get("metrics") if isinstance(result.get("metrics"), dict) and result.get("metrics") else evaluate_qa_result(result, question=question)
        for name, result in results.items()
    }
    return {
        "kind": "qa_runtime_comparison",
        "question": question,
        "context": sanitize_context_for_eval(context),
        "results": results,
        "metrics": metrics,
    }


def run_legacy_qa(
    *,
    question: str,
    context: dict[str, Any],
    item_service: ItemService,
    conversation_store: ConversationStore,
    model_client: ModelClient,
    settings: ServerSettings,
) -> dict[str, Any]:
    conversation = conversation_store.create({"context": context})
    state = KnowledgeQAState(conversation_id=conversation["id"], conversation=conversation, content=question)
    status = "completed"
    error: dict[str, str] = {}
    try:
        state = KnowledgeQAGraph(
            item_service=item_service,
            model_client=model_client,
            conversation_store=conversation_store,
            external_search=DisabledExternalSearchAdapter(),
            max_prompt_chars=settings.ai_max_prompt_chars,
            max_response_tokens=settings.ai_max_response_tokens,
            retrieval_mode=settings.ai_retrieval_mode,
        ).run(state)
    except Exception as exc:  # pragma: no cover - detailed legacy graph failures are covered elsewhere
        status = "failed"
        error = {"code": exc.__class__.__name__, "message": str(exc)}
    run = public_qa_run(state, status=status, error=error)
    result = {
        "engine": KnowledgeQAGraph.name,
        "status": status,
        "answer": state.answer,
        "answer_preview": state.answer[:240],
        "sources": normalize_sources(state.sources),
        "source_count": len(state.sources),
        "usage": state.usage,
        "retrieval": run["qa_report"]["retrieval"],
        "citation": run["qa_report"]["citation"],
        "quality": run["qa_report"]["answer_quality"],
        "trace": state.node_trace,
        "error": error,
    }
    result["metrics"] = evaluate_qa_result(result, question=question)
    return result


def run_agent_qa(
    *,
    question: str,
    context: dict[str, Any],
    item_service: ItemService,
    model_client: ModelClient,
    settings: ServerSettings,
    use_model: bool,
) -> dict[str, Any]:
    runtime = build_qa_agent_runtime(
        item_service=item_service,
        model_client=model_client,
        settings=settings,
        use_model=use_model,
    )
    result = runtime.run(AgentRequest(content=question, context=context, requested_task="qa"))
    return public_agent_eval_result(result)


def run_langgraph_qa(
    *,
    question: str,
    context: dict[str, Any],
    item_service: ItemService,
    model_client: ModelClient,
    settings: ServerSettings,
    use_model: bool,
) -> dict[str, Any]:
    runtime = build_qa_langgraph_runtime(
        item_service=item_service,
        model_client=model_client,
        settings=settings,
        use_model=use_model,
    )
    result = runtime.run(AgentRequest(content=question, context=context, requested_task="qa"))
    return public_agent_eval_result(result, engine=LangGraphKnowledgeQARuntime.name)


def public_agent_run(result: AgentRunResult, *, conversation_id: str = "", engine: str = "AgentRuntime.qa.v1") -> dict[str, Any]:
    evidence = tool_output(result, "evidence.gate") or tool_output(result, "evidence.build")
    llm = tool_output(result, "llm.chat")
    guardrail = tool_output(result, "guardrail.input")
    gate = tool_output(result, "evidence.gate")
    error = runtime_error(result)
    agent_trace = collect_agent_trace(result)
    prompt_trace = collect_prompt_trace(result)
    return {
        "id": f"qa_agent_{uuid.uuid4().hex}",
        "kind": "knowledge_qa",
        "status": result.status,
        "started_at": trace_time(result, first=True),
        "completed_at": trace_time(result, first=False),
        "duration_ms": 0,
        "conversation_id": conversation_id,
        "spec": {"engine": engine},
        "graph": engine,
        "generation_intent": {},
        "qa_report": public_agent_qa_report(result, evidence),
        "review_decision": result.review.checks if result.review else {},
        "node_trace": public_agent_trace(result),
        "agent_trace": agent_trace,
        "prompt_trace": prompt_trace,
        "skill_trace": public_agent_skill_trace(result),
        "usage": llm.get("usage") if isinstance(llm.get("usage"), dict) else {},
        "budget": merge_runtime_budget(
            guardrail.get("budget") if isinstance(guardrail.get("budget"), dict) else {},
            gate.get("budget") if isinstance(gate.get("budget"), dict) else {},
            result=result,
        ),
        "error": error,
        "material": {},
        "item_id": "",
        "retryable": result.status != "completed",
        "cancellable": False,
    }


def public_agent_eval_result(result: AgentRunResult, *, engine: str = "AgentRuntime.qa.v1") -> dict[str, Any]:
    run = public_agent_run(result, engine=engine)
    payload = {
        "engine": engine,
        "status": result.status,
        "answer": result.answer,
        "answer_preview": result.answer[:240],
        "sources": normalize_sources(run["qa_report"]["sources"]),
        "source_count": run["qa_report"]["source_count"],
        "usage": run["usage"],
        "retrieval": run["qa_report"]["retrieval"],
        "citation": run["qa_report"]["citation"],
        "quality": run["qa_report"]["answer_quality"],
        "trace": list(result.trace),
        "error": run["error"],
    }
    report_metrics = run.get("qa_report", {}).get("answer_quality", {}).get("metrics") if isinstance(run.get("qa_report"), dict) else {}
    payload["metrics"] = report_metrics if isinstance(report_metrics, dict) and report_metrics else evaluate_qa_result(payload)
    return payload


def public_agent_qa_report(result: AgentRunResult, evidence: dict[str, Any]) -> dict[str, Any]:
    sources = evidence.get("sources") if isinstance(evidence.get("sources"), list) else []
    verification = dict(result.verification.checks if result.verification else {})
    if result.verification and result.verification.reason:
        verification.setdefault("reason", result.verification.reason)
    review = result.review.checks if result.review else {}
    local_evidence = tool_output(result, "evidence.build")
    policy = tool_output(result, "expansion.policy")
    planner = dict(result.plan.metadata.get("planner") or {}) if getattr(result.plan, "metadata", None) else {}
    resolution = planner.get("conversation_resolution") if isinstance(planner.get("conversation_resolution"), dict) else None
    if resolution is not None:
        planner["conversation_resolution"] = public_conversation_resolution(resolution)
    research = tool_output(result, "external.research")
    source_evaluation = tool_output(result, "source.evaluate")
    external_status = research.get("status") if isinstance(research.get("status"), dict) else {}
    research_trace = research.get("trace") if isinstance(research.get("trace"), list) else []
    planned_search = tool_output(result, "search.plan")
    search_plan = planned_search if planned_search else (research.get("search_plan") if isinstance(research.get("search_plan"), dict) else {})
    evidence_budget = evidence.get("evidence_budget") if isinstance(evidence.get("evidence_budget"), dict) else {}
    evidence_coverage = evidence.get("evidence_coverage") if isinstance(evidence.get("evidence_coverage"), dict) else {}
    evidence_sufficiency = evidence.get("evidence_sufficiency") if isinstance(evidence.get("evidence_sufficiency"), dict) else {}
    assessment = tool_output(result, "evidence.assess")
    assessment_decision = assessment.get("decision") if isinstance(assessment.get("decision"), dict) else {}
    llm = tool_output(result, "llm.chat")
    has_llm_tool = any(tool.tool_id == "llm.chat" for tool in result.tool_results)
    skipped_model_call = bool(evidence.get("skipped_model_call")) or bool(llm.get("skipped")) or not has_llm_tool
    metric_payload = {
        "status": "completed" if result.answer else result.status,
        "answer": result.answer,
        "sources": normalize_sources(sources),
        "citation": verification,
        "error": runtime_error(result),
    }
    metrics = evaluate_qa_result(metric_payload)
    assessment_metrics = assessment.get("metrics") if isinstance(assessment.get("metrics"), dict) else {}
    if assessment_metrics.get("status") == "ok" and "weak_relevance" in (metrics.get("flags") or []):
        metric_flags = [flag for flag in metrics.get("flags") or [] if flag != "weak_relevance"]
        metrics = {
            **metrics,
            "flags": metric_flags,
            "status": "needs_attention" if metric_flags else "ok",
            "requires_attention": bool(metric_flags),
        }
    flags = list(metrics.get("flags") or [])
    if skipped_model_call:
        flags.append("model_call_skipped")
    if result.review and result.review.checks.get("declined"):
        flags.append(str(result.review.checks.get("declined")))
    if result.verification and result.verification.reason in {"current_info_without_external_sources", "explain_deeper_too_shallow"}:
        flags.append(str(result.verification.reason))
    flags = list(dict.fromkeys(str(flag) for flag in flags if str(flag)))
    status = "needs_attention" if flags else "ok"
    return {
        "source_count": len(sources),
        "local_source_count": len([source for source in sources if source.get("kind") != "external"]),
        "external_source_count": len([source for source in sources if source.get("kind") == "external"]),
        "skipped_model_call": skipped_model_call,
        "retrieval": local_evidence.get("status") if isinstance(local_evidence.get("status"), dict) else {},
        "external_status": external_status,
        "source_evaluation": {
            "mode": str(source_evaluation.get("mode") or ""),
            "kept_count": int(source_evaluation.get("kept_count") or 0) if source_evaluation else 0,
            "dropped_count": int(source_evaluation.get("dropped_count") or 0) if source_evaluation else 0,
            "decisions": source_evaluation.get("decisions") if isinstance(source_evaluation.get("decisions"), list) else [],
            "error": source_evaluation.get("error") if isinstance(source_evaluation.get("error"), dict) else {},
        },
        "search_plan": search_plan,
        "research_trace": research_trace,
        "planner": planner,
        "expansion_policy": policy,
        "evidence_scope": {},
        "evidence_ranking": {},
        "evidence_rerank": {},
        "evidence_budget": evidence_budget,
        "evidence_coverage": evidence_coverage,
        "evidence_sufficiency": evidence_sufficiency,
        "evidence_assessment": {
            "status": str(assessment.get("status") or ""),
            "decision": assessment_decision,
        },
        "citation": verification,
        "answer_quality": {
            "status": status,
            "requires_attention": bool(flags),
            "flags": flags,
            "review": {
                **dict(review or {}),
                "intent": planner.get("intent") or "",
                "verification_reason": result.verification.reason if result.verification else "",
                "search_used": bool(external_status.get("queried")),
            },
            "metrics": metrics,
        },
        "sources": normalize_sources(sources),
    }


def public_conversation_resolution(resolution: dict[str, Any]) -> dict[str, Any]:
    return {
        "is_followup": bool(resolution.get("is_followup")),
        "topic_shift": bool(resolution.get("topic_shift")),
        "focus_type": str(resolution.get("focus_type") or "none"),
        "confidence": float(resolution.get("confidence") or 0.0),
        "reason": str(resolution.get("reason") or ""),
    }


def public_agent_trace(result: AgentRunResult) -> list[dict[str, str]]:
    return [{"node": str(event.get("node") or ""), "status": str(event.get("status") or "")} for event in result.trace if isinstance(event, dict)]


def public_agent_skill_trace(result: AgentRunResult) -> list[dict[str, Any]]:
    trace: list[dict[str, Any]] = []
    for tool in result.tool_results:
        trace.append(
            {
                "skill_id": tool.tool_id,
                "version": "runtime.v1",
                "status": tool.status,
                "input_summary": {},
                "output_summary": summarize_tool_output(tool.output),
            },
        )
    return trace


def collect_agent_trace(result: AgentRunResult) -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []
    plan_meta = result.plan.metadata if result.plan and isinstance(result.plan.metadata, dict) else {}
    planner = plan_meta.get("planner")
    if isinstance(planner, dict):
        specs.append({"id": "knowledge_qa.planner_agent", "version": "v1", "role": "HTMlore knowledge-base QA planner"})
    verification = result.verification.checks if result.verification and isinstance(result.verification.checks, dict) else {}
    verifier_spec = verification.get("verifier_agent")
    if isinstance(verifier_spec, dict):
        specs.append(verifier_spec)
    review = result.review.checks if result.review and isinstance(result.review.checks, dict) else {}
    reviewer_spec = review.get("reviewer_agent")
    if isinstance(reviewer_spec, dict):
        specs.append(reviewer_spec)
    return specs


def collect_prompt_trace(result: AgentRunResult) -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []
    verification = result.verification.checks if result.verification and isinstance(result.verification.checks, dict) else {}
    verifier_prompt = verification.get("verifier_prompt")
    if isinstance(verifier_prompt, dict):
        specs.append(verifier_prompt)
    review = result.review.checks if result.review and isinstance(result.review.checks, dict) else {}
    reviewer_prompt = review.get("reviewer_prompt")
    if isinstance(reviewer_prompt, dict):
        specs.append(reviewer_prompt)
    return specs


def summarize_tool_output(output: dict[str, Any]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    status = output.get("status") if isinstance(output.get("status"), dict) else {}
    if "effective_mode" in status:
        summary["effective_mode"] = str(status.get("effective_mode") or "")
    if "fallback" in status:
        summary["fallback"] = bool(status.get("fallback"))
    if "chunk_count" in status:
        summary["evidence_count"] = int(status.get("chunk_count") or 0)
    if "item_count" in output:
        summary["context_item_count"] = int(output.get("item_count") or 0)
    if "mode" in output:
        summary["mode"] = str(output.get("mode") or "")
    if "skipped_model_call" in output:
        summary["skipped_model_call"] = bool(output.get("skipped_model_call"))
    return summary


def trace_time(result: AgentRunResult, *, first: bool) -> str:
    if not result.trace:
        return ""
    event = result.trace[0] if first else result.trace[-1]
    return str(event.get("at") or "")


def tool_output(result: AgentRunResult, tool_id: str) -> dict[str, Any]:
    for tool_result in result.tool_results:
        if tool_result.tool_id == tool_id:
            return dict(tool_result.output or {})
    return {}


def runtime_error(result: AgentRunResult) -> dict[str, str]:
    if result.status == "completed":
        return {}
    reason = ""
    if result.verification and result.verification.reason:
        reason = result.verification.reason
    elif result.review and result.review.reason:
        reason = result.review.reason
    return {"code": "agent_needs_attention", "message": reason or result.status}


def merge_runtime_budget(*values: dict[str, Any], result: AgentRunResult) -> dict[str, int]:
    merged: dict[str, int] = {}
    for value in values:
        if not isinstance(value, dict):
            continue
        for key in ("message_chars", "max_message_chars", "prompt_chars", "max_prompt_chars", "max_response_tokens"):
            try:
                number = int(value.get(key) or 0)
            except (TypeError, ValueError):
                number = 0
            if number > 0:
                merged[key] = number
    if result.plan:
        for call in result.plan.steps:
            if call.tool_id == "llm.chat":
                try:
                    merged["max_response_tokens"] = max(1, int(call.arguments.get("max_tokens") or 0))
                except (TypeError, ValueError):
                    pass
    return merged


def normalize_sources(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for source in sources:
        item = {
            "kind": str(source.get("kind") or "local"),
            "source_index": source.get("source_index"),
            "title": str(source.get("title") or ""),
            "item_id": str(source.get("item_id") or ""),
            "url": str(source.get("url") or ""),
        }
        if isinstance(source.get("retrieval_sources"), list):
            item["retrieval_sources"] = [str(value) for value in source.get("retrieval_sources") or [] if str(value)]
        normalized.append(item)
    return normalized


def sanitize_context_for_eval(context: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in dict(context or {}).items() if key not in {"api_key", "token", "authorization"}}
