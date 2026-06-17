from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import uuid

try:  # pragma: no cover - dependency availability is environment-specific
    from langgraph.graph import END, StateGraph
except Exception:  # pragma: no cover
    END = "__end__"
    StateGraph = None

from .runtime import (
    AgentDraft,
    AgentPlan,
    AgentRequest,
    AgentRunResult,
    AgentRuntimeError,
    AgentVerifier,
    FinalOutput,
    ReviewResult,
    TaskAgent,
    ToolPermissionError,
    ToolRegistry,
    ToolResult,
    VerificationResult,
    normalize_id,
    trace_event,
    utc_now,
)


class LangGraphQAError(AgentRuntimeError):
    pass


@dataclass
class LangGraphQAState:
    request: AgentRequest
    run_id: str
    task_type: str = ""
    attempt: int = 1
    plan: AgentPlan | None = None
    tool_results: list[ToolResult] = field(default_factory=list)
    draft: AgentDraft = field(default_factory=lambda: AgentDraft(""))
    verification: VerificationResult | None = None
    review: ReviewResult | None = None
    final_output: FinalOutput | None = None
    status: str = "running"
    trace: list[dict[str, Any]] = field(default_factory=list)
    shared: dict[str, Any] = field(default_factory=dict)


class LangGraphKnowledgeQARuntime:
    name = "LangGraphKnowledgeQA.v1"

    def __init__(
        self,
        *,
        agent: TaskAgent,
        tools: ToolRegistry,
        verifier: AgentVerifier,
        reviewer: Any,
        finalizer: Any,
        max_attempts: int = 2,
    ) -> None:
        if StateGraph is None:
            raise LangGraphQAError("LangGraph is not installed. Install the agent extra or set HTML_LORE_AI_QA_ENGINE=agent_runtime.")
        if normalize_id(agent.task_type, label="task_type") != "qa":
            raise LangGraphQAError("LangGraphKnowledgeQARuntime only accepts the QA task agent.")
        self.agent = agent
        self.tools = tools
        self.verifier = verifier
        self.reviewer = reviewer
        self.finalizer = finalizer
        self.max_attempts = max(1, int(max_attempts or 1))
        self._graph = self._compile_graph()

    def run(self, request: AgentRequest) -> AgentRunResult:
        run_id = f"langgraph_qa_{uuid.uuid4().hex}"
        shared: dict[str, Any] = {
            "run_id": run_id,
            "started_at": utc_now(),
            "request_context": dict(request.context or {}),
        }
        if isinstance(request.context.get("_conversation_messages"), list):
            shared["conversation_messages"] = list(request.context.get("_conversation_messages") or [])
        initial = LangGraphQAState(request=request, run_id=run_id, shared=shared)
        state = self._graph.invoke(initial)
        if isinstance(state, dict):
            state = LangGraphQAState(**state)
        return AgentRunResult(
            run_id=state.run_id,
            task_type=state.task_type or "qa",
            status=state.status,
            answer=state.final_output.content if state.final_output else state.draft.content,
            plan=state.plan,
            tool_results=tuple(state.tool_results),
            verification=state.verification,
            review=state.review,
            final_output=state.final_output,
            trace=tuple(state.trace),
        )

    def _compile_graph(self) -> Any:
        graph = StateGraph(LangGraphQAState)
        graph.add_node("task_router", self._task_router)
        graph.add_node("planner", self._planner)
        graph.add_node("tool_executor", self._tool_executor)
        graph.add_node("draft_builder", self._draft_builder)
        graph.add_node("verifier", self._verifier)
        graph.add_node("reviewer", self._reviewer)
        graph.add_node("prepare_retry", self._prepare_retry)
        graph.add_node("finalizer", self._finalizer)
        graph.add_node("needs_attention", self._needs_attention)
        graph.set_entry_point("task_router")
        graph.add_edge("task_router", "planner")
        graph.add_edge("planner", "tool_executor")
        graph.add_edge("tool_executor", "draft_builder")
        graph.add_edge("draft_builder", "verifier")
        graph.add_edge("verifier", "reviewer")
        graph.add_conditional_edges("reviewer", self._review_route, {"finalize": "finalizer", "retry": "prepare_retry", "stop": "needs_attention"})
        graph.add_edge("prepare_retry", "planner")
        graph.add_edge("finalizer", END)
        graph.add_edge("needs_attention", END)
        return graph.compile()

    def _task_router(self, state: LangGraphQAState) -> LangGraphQAState:
        state.task_type = "qa"
        state.trace.append(trace_event("TaskRouter", "completed", {"task_type": "qa", "attempt": state.attempt, "engine": self.name}))
        return state

    def _planner(self, state: LangGraphQAState) -> LangGraphQAState:
        state.tool_results = []
        state.plan = self.agent.plan(state.request, state.shared, attempt=state.attempt)
        if normalize_id(state.plan.task_type, label="task_type") != "qa":
            raise LangGraphQAError("QA planner returned a plan for a different task type.")
        state.shared["plan_metadata"] = dict(state.plan.metadata or {})
        state.trace.append(trace_event("Planner", "completed", {"task_type": "qa", "step_count": len(state.plan.steps), "attempt": state.attempt, "engine": self.name}))
        return state

    def _tool_executor(self, state: LangGraphQAState) -> LangGraphQAState:
        if state.plan is None:
            raise LangGraphQAError("Cannot execute tools before planning.")
        allowed = set(self.agent.allowed_tools)
        results: list[ToolResult] = []
        for call in state.plan.steps:
            tool_id = normalize_id(call.tool_id, label="tool_id")
            if tool_id not in allowed:
                raise ToolPermissionError(f"Task agent {self.agent.id} is not allowed to call tool: {tool_id}.")
            started_at = utc_now()
            output = self.tools.get(tool_id).run(dict(call.arguments), state.shared)
            result = ToolResult(tool_id=tool_id, status="completed", output=output)
            state.shared.setdefault("tool_outputs", {})[tool_id] = output
            state.trace.append(trace_event("ToolExecutor", result.status, {"tool_id": tool_id, "started_at": started_at, "completed_at": utc_now(), "engine": self.name}))
            results.append(result)
        state.tool_results = results
        return state

    def _draft_builder(self, state: LangGraphQAState) -> LangGraphQAState:
        if state.plan is None:
            raise LangGraphQAError("Cannot draft before planning.")
        state.draft = self.agent.draft(state.request, state.plan, tuple(state.tool_results), state.shared)
        state.trace.append(trace_event("DraftBuilder", "completed", {"draft_chars": len(state.draft.content), "attempt": state.attempt, "engine": self.name}))
        return state

    def _verifier(self, state: LangGraphQAState) -> LangGraphQAState:
        if state.plan is None:
            raise LangGraphQAError("Cannot verify before planning.")
        state.verification = self.verifier.verify(state.request, state.plan, tuple(state.tool_results), state.draft.content, state.shared)
        state.trace.append(
            trace_event(
                "Verifier",
                "completed",
                {
                    "passed": state.verification.passed,
                    "retryable": state.verification.retryable,
                    "reason": state.verification.reason,
                    "attempt": state.attempt,
                    "engine": self.name,
                },
            ),
        )
        return state

    def _reviewer(self, state: LangGraphQAState) -> LangGraphQAState:
        if state.plan is None or state.verification is None:
            raise LangGraphQAError("Cannot review before planning and verification.")
        state.review = self.reviewer.review(state.request, state.plan, tuple(state.tool_results), state.draft, state.verification, state.shared)
        state.trace.append(
            trace_event(
                "Reviewer",
                "completed",
                {
                    "passed": state.review.passed,
                    "retryable": state.review.retryable,
                    "reason": state.review.reason,
                    "attempt": state.attempt,
                    "engine": self.name,
                },
            ),
        )
        return state

    def _review_route(self, state: LangGraphQAState) -> str:
        if state.verification and state.review and state.verification.passed and state.review.passed:
            return "finalize"
        retryable = bool((state.verification and state.verification.retryable) or (state.review and state.review.retryable))
        if retryable and state.attempt < self.max_attempts:
            return "retry"
        return "stop"

    def _prepare_retry(self, state: LangGraphQAState) -> LangGraphQAState:
        state.trace.append(trace_event("OrchestratorReview", "retry", {"decision": "replan", "attempt": state.attempt, "engine": self.name}))
        state.attempt += 1
        return state

    def _finalizer(self, state: LangGraphQAState) -> LangGraphQAState:
        if state.plan is None or state.verification is None or state.review is None:
            raise LangGraphQAError("Cannot finalize before plan, verification, and review.")
        state.final_output = self.finalizer.finalize(state.request, state.plan, tuple(state.tool_results), state.draft, state.verification, state.review, state.shared)
        state.status = "completed"
        state.trace.append(
            trace_event(
                "Finalizer",
                "completed",
                {
                    "output_chars": len(state.final_output.content),
                    "requires_confirmation": state.final_output.requires_confirmation,
                    "attempt": state.attempt,
                    "engine": self.name,
                },
            ),
        )
        state.trace.append(trace_event("OrchestratorReview", "completed", {"decision": "pass", "attempt": state.attempt, "engine": self.name}))
        return state

    def _needs_attention(self, state: LangGraphQAState) -> LangGraphQAState:
        state.status = "needs_attention"
        state.trace.append(trace_event("OrchestratorReview", "needs_attention", {"decision": "stop", "attempt": state.attempt, "engine": self.name}))
        return state


def langgraph_available() -> bool:
    return StateGraph is not None


def build_langgraph_qa_runtime(
    *,
    agent: TaskAgent,
    tools: ToolRegistry,
    verifier: AgentVerifier,
    reviewer: Any,
    finalizer: Any,
    max_attempts: int = 2,
) -> LangGraphKnowledgeQARuntime:
    return LangGraphKnowledgeQARuntime(
        agent=agent,
        tools=tools,
        verifier=verifier,
        reviewer=reviewer,
        finalizer=finalizer,
        max_attempts=max_attempts,
    )


__all__ = ["LangGraphQAError", "LangGraphKnowledgeQARuntime", "build_langgraph_qa_runtime", "langgraph_available"]
