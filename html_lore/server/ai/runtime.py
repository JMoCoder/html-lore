from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Protocol
import uuid


class AgentRuntimeError(ValueError):
    pass


class ToolPermissionError(AgentRuntimeError):
    pass


class ToolNotFoundError(AgentRuntimeError):
    pass


@dataclass(frozen=True)
class AgentRequest:
    content: str
    context: dict[str, Any] = field(default_factory=dict)
    requested_task: str = ""
    user_id: str = ""


@dataclass(frozen=True)
class ToolCall:
    tool_id: str
    arguments: dict[str, Any] = field(default_factory=dict)
    reason: str = ""


@dataclass(frozen=True)
class AgentPlan:
    task_type: str
    steps: tuple[ToolCall, ...] = ()
    response_strategy: str = ""
    attempt: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ToolResult:
    tool_id: str
    status: str
    output: dict[str, Any] = field(default_factory=dict)
    error: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class VerificationResult:
    passed: bool
    checks: dict[str, Any] = field(default_factory=dict)
    reason: str = ""
    retryable: bool = False


@dataclass(frozen=True)
class ReviewResult:
    passed: bool
    checks: dict[str, Any] = field(default_factory=dict)
    reason: str = ""
    retryable: bool = False


@dataclass(frozen=True)
class AgentDraft:
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class FinalOutput:
    content: str
    write_payload: dict[str, Any] = field(default_factory=dict)
    requires_confirmation: bool = False


@dataclass(frozen=True)
class AgentRunResult:
    run_id: str
    task_type: str
    status: str
    answer: str = ""
    plan: AgentPlan | None = None
    tool_results: tuple[ToolResult, ...] = ()
    verification: VerificationResult | None = None
    review: ReviewResult | None = None
    final_output: FinalOutput | None = None
    trace: tuple[dict[str, Any], ...] = ()


class AgentTool(Protocol):
    id: str

    def run(self, arguments: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
        pass


class TaskAgent(Protocol):
    id: str
    task_type: str
    allowed_tools: tuple[str, ...]

    def plan(self, request: AgentRequest, state: dict[str, Any], *, attempt: int) -> AgentPlan:
        pass

    def draft(self, request: AgentRequest, plan: AgentPlan, tool_results: tuple[ToolResult, ...], state: dict[str, Any]) -> AgentDraft:
        pass


class AgentVerifier(Protocol):
    id: str

    def verify(
        self,
        request: AgentRequest,
        plan: AgentPlan,
        tool_results: tuple[ToolResult, ...],
        answer: str,
        state: dict[str, Any],
    ) -> VerificationResult:
        pass


class AgentReviewer(Protocol):
    id: str

    def review(
        self,
        request: AgentRequest,
        plan: AgentPlan,
        tool_results: tuple[ToolResult, ...],
        draft: AgentDraft,
        verification: VerificationResult,
        state: dict[str, Any],
    ) -> ReviewResult:
        pass


class AgentFinalizer(Protocol):
    id: str

    def finalize(
        self,
        request: AgentRequest,
        plan: AgentPlan,
        tool_results: tuple[ToolResult, ...],
        draft: AgentDraft,
        verification: VerificationResult,
        review: ReviewResult,
        state: dict[str, Any],
    ) -> FinalOutput:
        pass


class CallableTool:
    def __init__(self, tool_id: str, handler: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]) -> None:
        self.id = normalize_id(tool_id, label="tool_id")
        self._handler = handler

    def run(self, arguments: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
        return self._handler(arguments, state)


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, AgentTool] = {}

    def register(self, tool: AgentTool) -> None:
        tool_id = normalize_id(tool.id, label="tool_id")
        self._tools[tool_id] = tool

    def get(self, tool_id: str) -> AgentTool:
        normalized = normalize_id(tool_id, label="tool_id")
        try:
            return self._tools[normalized]
        except KeyError as exc:
            raise ToolNotFoundError(f"Agent tool is not registered: {normalized}.") from exc

    def public_tools(self) -> list[str]:
        return sorted(self._tools)


class AgentRuntime:
    def __init__(
        self,
        *,
        agents: tuple[TaskAgent, ...],
        tools: ToolRegistry,
        verifier: AgentVerifier,
        reviewer: AgentReviewer | None = None,
        finalizer: AgentFinalizer | None = None,
        max_attempts: int = 2,
    ) -> None:
        if not agents:
            raise AgentRuntimeError("Agent runtime requires at least one task agent.")
        self.agents = {normalize_id(agent.task_type, label="task_type"): agent for agent in agents}
        self.tools = tools
        self.verifier = verifier
        self.reviewer = reviewer or BasicReviewer()
        self.finalizer = finalizer or BasicFinalizer()
        self.max_attempts = max(1, int(max_attempts or 1))

    def run(self, request: AgentRequest) -> AgentRunResult:
        run_id = f"agent_{uuid.uuid4().hex}"
        trace: list[dict[str, Any]] = []
        state: dict[str, Any] = {
            "run_id": run_id,
            "started_at": utc_now(),
            "request_context": dict(request.context or {}),
        }
        if isinstance(request.context.get("_conversation_messages"), list):
            state["conversation_messages"] = list(request.context.get("_conversation_messages") or [])
        task_type = self.route(request)
        agent = self.agents[task_type]
        last_plan: AgentPlan | None = None
        last_results: tuple[ToolResult, ...] = ()
        last_draft = AgentDraft("")
        last_verification: VerificationResult | None = None
        last_review: ReviewResult | None = None

        for attempt in range(1, self.max_attempts + 1):
            trace.append(trace_event("TaskRouter", "completed", {"task_type": task_type, "attempt": attempt}))
            plan = agent.plan(request, state, attempt=attempt)
            if normalize_id(plan.task_type, label="task_type") != task_type:
                raise AgentRuntimeError("Task agent returned a plan for a different task type.")
            state["plan_metadata"] = dict(plan.metadata or {})
            trace.append(trace_event("Planner", "completed", {"task_type": task_type, "step_count": len(plan.steps), "attempt": attempt}))
            results = self.execute_plan(agent, plan, state, trace)
            draft = agent.draft(request, plan, results, state)
            trace.append(trace_event("DraftBuilder", "completed", {"draft_chars": len(draft.content), "attempt": attempt}))
            verification = self.verifier.verify(request, plan, results, draft.content, state)
            trace.append(
                trace_event(
                    "Verifier",
                    "completed",
                    {"passed": verification.passed, "retryable": verification.retryable, "reason": verification.reason, "attempt": attempt},
                ),
            )
            review = self.reviewer.review(request, plan, results, draft, verification, state)
            trace.append(
                trace_event(
                    "Reviewer",
                    "completed",
                    {"passed": review.passed, "retryable": review.retryable, "reason": review.reason, "attempt": attempt},
                ),
            )
            last_plan = plan
            last_results = results
            last_draft = draft
            last_verification = verification
            last_review = review
            if verification.passed and review.passed:
                final_output = self.finalizer.finalize(request, plan, results, draft, verification, review, state)
                trace.append(
                    trace_event(
                        "Finalizer",
                        "completed",
                        {
                            "output_chars": len(final_output.content),
                            "requires_confirmation": final_output.requires_confirmation,
                            "attempt": attempt,
                        },
                    ),
                )
                trace.append(trace_event("OrchestratorReview", "completed", {"decision": "pass", "attempt": attempt}))
                return AgentRunResult(
                    run_id=run_id,
                    task_type=task_type,
                    status="completed",
                    answer=final_output.content,
                    plan=plan,
                    tool_results=results,
                    verification=verification,
                    review=review,
                    final_output=final_output,
                    trace=tuple(trace),
                )
            retryable = verification.retryable or review.retryable
            if not retryable or attempt >= self.max_attempts:
                break
            trace.append(trace_event("OrchestratorReview", "retry", {"decision": "replan", "attempt": attempt}))

        trace.append(trace_event("OrchestratorReview", "needs_attention", {"decision": "stop"}))
        return AgentRunResult(
            run_id=run_id,
            task_type=task_type,
            status="needs_attention",
            answer=last_draft.content,
            plan=last_plan,
            tool_results=last_results,
            verification=last_verification,
            review=last_review,
            trace=tuple(trace),
        )

    def route(self, request: AgentRequest) -> str:
        explicit = normalize_optional_id(request.requested_task)
        if explicit:
            if explicit not in self.agents:
                raise AgentRuntimeError(f"Unsupported agent task type: {explicit}.")
            return explicit
        content = str(request.content or "").lower()
        if any(marker in content for marker in ("生成", "create", "generate")) and "writer" in self.agents:
            return "writer"
        if any(marker in content for marker in ("修改", "编辑", "edit", "rewrite")) and "editor" in self.agents:
            return "editor"
        if any(marker in content for marker in ("标签", "集合", "整理", "tag", "collection")) and "librarian" in self.agents:
            return "librarian"
        if "qa" in self.agents:
            return "qa"
        return next(iter(self.agents))

    def execute_plan(self, agent: TaskAgent, plan: AgentPlan, state: dict[str, Any], trace: list[dict[str, Any]]) -> tuple[ToolResult, ...]:
        from .guardrails import GuardrailError
        from .providers import AIProviderConfigError, ProviderCallError

        allowed = set(agent.allowed_tools)
        results: list[ToolResult] = []
        for call in plan.steps:
            tool_id = normalize_id(call.tool_id, label="tool_id")
            if tool_id not in allowed:
                raise ToolPermissionError(f"Task agent {agent.id} is not allowed to call tool: {tool_id}.")
            started_at = utc_now()
            try:
                output = self.tools.get(tool_id).run(dict(call.arguments), state)
                result = ToolResult(tool_id=tool_id, status="completed", output=output)
                state.setdefault("tool_outputs", {})[tool_id] = output
            except (AgentRuntimeError, GuardrailError, AIProviderConfigError, ProviderCallError):
                raise
            except Exception as exc:
                result = ToolResult(tool_id=tool_id, status="failed", error={"type": exc.__class__.__name__, "message": str(exc)})
            trace.append(
                trace_event(
                    "ToolExecutor",
                    result.status,
                    {"tool_id": tool_id, "started_at": started_at, "completed_at": utc_now()},
                ),
            )
            results.append(result)
        return tuple(results)


class BasicVerifier:
    id = "verifier.basic"

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
        if not str(answer or "").strip():
            return VerificationResult(False, checks={"answer_chars": 0}, reason="empty_answer", retryable=True)
        return VerificationResult(True, checks={"answer_chars": len(answer)}, reason="ok", retryable=False)


class BasicReviewer:
    id = "reviewer.basic"

    def review(
        self,
        request: AgentRequest,
        plan: AgentPlan,
        tool_results: tuple[ToolResult, ...],
        draft: AgentDraft,
        verification: VerificationResult,
        state: dict[str, Any],
    ) -> ReviewResult:
        if not verification.passed:
            return ReviewResult(False, checks={"verification_reason": verification.reason}, reason="verification_failed", retryable=verification.retryable)
        return ReviewResult(True, checks={"draft_chars": len(draft.content)}, reason="ok", retryable=False)


class BasicFinalizer:
    id = "finalizer.basic"

    def finalize(
        self,
        request: AgentRequest,
        plan: AgentPlan,
        tool_results: tuple[ToolResult, ...],
        draft: AgentDraft,
        verification: VerificationResult,
        review: ReviewResult,
        state: dict[str, Any],
    ) -> FinalOutput:
        return FinalOutput(content=draft.content)


def normalize_id(value: str, *, label: str) -> str:
    normalized = str(value or "").strip().lower()
    if not normalized:
        raise AgentRuntimeError(f"{label} is required.")
    return normalized


def normalize_optional_id(value: str) -> str:
    return str(value or "").strip().lower()


def trace_event(node: str, status: str, detail: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"node": node, "status": status, "at": utc_now(), "detail": dict(detail or {})}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
