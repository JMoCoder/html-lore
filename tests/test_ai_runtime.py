import json

import pytest

from html_lore.server.ai.agents import KnowledgeQATaskAgent, KnowledgeQAVerifier, KnowledgeQAReviewer
from html_lore.server.ai.context import AIContextError
from html_lore.server.ai.model_client import ModelClient
from html_lore.server.ai.prompts import build_qa_answer_messages
from html_lore.server.ai.providers import AIProviderConfig
from html_lore.server.ai.research import ResearchWorkflow, research_limits_for_plan
from html_lore.server.ai.route_planner import plan_ai_route, plan_qa_route
from html_lore.server.ai.conversation_resolution import resolve_conversation_turn
from html_lore.server.ai.retrieval import is_low_trust_generated_item, retrieve_keyword_evidence
from html_lore.server.ai.search_agent import SearchPlannerAgent
from html_lore.server.ai.search_planner import SearchPlan
from html_lore.server.ai.runtime import (
    AgentPlan,
    AgentRequest,
    AgentRuntime,
    BasicVerifier,
    CallableTool,
    AgentDraft,
    TaskAgent,
    ToolCall,
    ToolPermissionError,
    ToolRegistry,
    ToolResult,
    ReviewResult,
    VerificationResult,
)
from html_lore.server.ai.langgraph_qa import LangGraphKnowledgeQARuntime, langgraph_available
from html_lore.server.ai.runtime_eval import build_selected_qa_runtime, compare_qa_runtimes, evaluate_qa_result
from html_lore.server.ai.tools import ContextTool, EvidenceAssessmentTool, EvidenceGateTool, EvidenceTool, ExpansionPolicyTool, ExternalResearchTool, InputGuardrailTool, LLMChatTool, SearchPlanTool, SourceEvaluatorTool, build_evidence_pack, evidence_chunks_overlap_query, external_evidence_assessment
from html_lore.server.ai.qa_search_plan import build_qa_search_plan
from html_lore.server.ai.eval import InMemoryEvalConversationStore
from html_lore.server.ai.external_search import ExternalSearchResult
from html_lore.server.ai.knowledge_qa_graph import EXTERNAL_NO_RESULTS_ANSWER, EXTERNAL_UNAVAILABLE_ANSWER, build_retrieval_query
from html_lore.server.config import ServerSettings
from html_lore.server.items import ItemService


def make_dirs(tmp_path):
    content_dir = tmp_path / "content"
    meta_dir = tmp_path / "meta"
    public_dir = tmp_path / "public"
    content_dir.mkdir()
    (meta_dir / "items").mkdir(parents=True)
    public_dir.mkdir()
    return content_dir, meta_dir, public_dir


def make_note(content_dir, meta_dir, item_id: str, *, title: str, collection: str, tags: list[str], archived: bool = False) -> None:
    content_path = content_dir / item_id
    content_path.parent.mkdir(parents=True, exist_ok=True)
    content_path.write_text(
        f"<!doctype html><html><body><h1>{title}</h1><p>{title} explains MCP Docker context and runtime evidence.</p></body></html>",
        encoding="utf-8",
    )
    metadata_path = meta_dir / "items" / f"{item_id.removesuffix('.html')}.yml"
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(
        "\n".join(
            [
                f"title: {title}",
                "summary: Test summary",
                "source_type: imported",
                f"collection: {collection}",
                "tags:",
                *[f"  - {tag}" for tag in tags],
                f"archived: {'true' if archived else 'false'}",
                "",
            ],
        ),
        encoding="utf-8",
    )


def make_generated_note(
    content_dir,
    meta_dir,
    item_id: str,
    *,
    title: str,
    summary: str,
    body: str,
    tags: list[str],
) -> None:
    content_path = content_dir / item_id
    content_path.parent.mkdir(parents=True, exist_ok=True)
    content_path.write_text(
        f"<!doctype html><html><body><h1>{title}</h1><p>{body}</p></body></html>",
        encoding="utf-8",
    )
    metadata_path = meta_dir / "items" / f"{item_id.removesuffix('.html')}.yml"
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(
        "\n".join(
            [
                f"title: {title}",
                f"summary: \"{summary}\"",
                "source_type: topic",
                "collection: Inbox",
                "tags:",
                *[f"  - {tag}" for tag in tags],
                "agent:",
                "  generated: true",
                "",
            ],
        ),
        encoding="utf-8",
    )


def item_service(tmp_path) -> ItemService:
    content_dir, meta_dir, public_dir = make_dirs(tmp_path)
    make_note(content_dir, meta_dir, "a.html", title="Alpha MCP", collection="AI", tags=["MCP", "Docker"])
    make_note(content_dir, meta_dir, "b.html", title="Beta Docker", collection="Dev", tags=["Docker"])
    make_note(content_dir, meta_dir, "archived.html", title="Archived MCP", collection="AI", tags=["MCP"], archived=True)
    return ItemService(
        ServerSettings(
            content_dir=content_dir,
            meta_dir=meta_dir,
            public_dir=public_dir,
            site_title="Runtime Test",
            max_upload_bytes=10 * 1024 * 1024,
        ),
    )


def test_selected_qa_runtime_auto_prefers_langgraph_when_available(tmp_path) -> None:
    service = item_service(tmp_path)
    settings = service.settings
    model_client = ModelClient(AIProviderConfig(provider="fake", enabled=True, model="fake-model"))

    runtime, engine = build_selected_qa_runtime(
        item_service=service,
        model_client=model_client,
        settings=settings,
        use_model=False,
    )

    if langgraph_available():
        assert isinstance(runtime, LangGraphKnowledgeQARuntime)
        assert engine == "LangGraphKnowledgeQA.v1"
    else:
        assert isinstance(runtime, AgentRuntime)
        assert engine == "AgentRuntime.qa.v1"


def test_selected_qa_runtime_auto_falls_back_when_langgraph_unavailable(monkeypatch, tmp_path) -> None:
    import html_lore.server.ai.langgraph_qa as langgraph_qa

    monkeypatch.setattr(langgraph_qa, "StateGraph", None)
    service = item_service(tmp_path)
    model_client = ModelClient(AIProviderConfig(provider="fake", enabled=True, model="fake-model"))

    runtime, engine = build_selected_qa_runtime(
        item_service=service,
        model_client=model_client,
        settings=service.settings,
        use_model=False,
    )

    assert isinstance(runtime, AgentRuntime)
    assert engine == "AgentRuntime.qa.v1"

    explicit_langgraph_settings = ServerSettings(
        content_dir=service.settings.content_dir,
        meta_dir=service.settings.meta_dir,
        public_dir=service.settings.public_dir,
        site_title="Runtime Test",
        max_upload_bytes=10 * 1024 * 1024,
        ai_qa_engine="langgraph",
    )
    with pytest.raises(Exception, match="LangGraph is not installed"):
        build_selected_qa_runtime(
            item_service=service,
            model_client=model_client,
            settings=explicit_langgraph_settings,
            use_model=False,
        )


class EchoAgent:
    id = "agent.qa"
    task_type = "qa"
    allowed_tools = ("context.read",)

    def __init__(self) -> None:
        self.attempts: list[int] = []

    def plan(self, request: AgentRequest, state: dict, *, attempt: int) -> AgentPlan:
        self.attempts.append(attempt)
        return AgentPlan(
            task_type="qa",
            steps=(ToolCall("context.read", {"topic": request.content}, reason="load context"),),
            response_strategy="answer_from_context",
            attempt=attempt,
        )

    def draft(self, request: AgentRequest, plan: AgentPlan, tool_results: tuple, state: dict) -> AgentDraft:
        return AgentDraft(f"Answer: {tool_results[0].output['title']}")


class WriterAgent:
    id = "agent.writer"
    task_type = "writer"
    allowed_tools = ("note.draft",)

    def plan(self, request: AgentRequest, state: dict, *, attempt: int) -> AgentPlan:
        return AgentPlan(task_type="writer", steps=(ToolCall("note.draft", {"instruction": request.content}),), attempt=attempt)

    def draft(self, request: AgentRequest, plan: AgentPlan, tool_results: tuple, state: dict) -> AgentDraft:
        return AgentDraft(tool_results[0].output["html"])


class RetryVerifier:
    id = "verifier.retry_once"

    def __init__(self) -> None:
        self.calls = 0

    def verify(self, request: AgentRequest, plan: AgentPlan, tool_results: tuple, answer: str, state: dict) -> VerificationResult:
        self.calls += 1
        if self.calls == 1:
            return VerificationResult(False, checks={"naturalness": "mechanical"}, reason="mechanical_answer", retryable=True)
        return VerificationResult(True, checks={"naturalness": "ok"}, reason="ok")


class AlwaysFailVerifier:
    id = "verifier.always_fail"

    def verify(self, request: AgentRequest, plan: AgentPlan, tool_results: tuple, answer: str, state: dict) -> VerificationResult:
        return VerificationResult(False, checks={"quality": "bad"}, reason="quality_failed", retryable=True)


class RetryReviewer:
    id = "reviewer.retry_once"

    def __init__(self) -> None:
        self.calls = 0

    def review(self, request: AgentRequest, plan: AgentPlan, tool_results: tuple, draft: AgentDraft, verification: VerificationResult, state: dict) -> ReviewResult:
        self.calls += 1
        if self.calls == 1:
            return ReviewResult(False, checks={"final_check": "too_mechanical"}, reason="review_failed", retryable=True)
        return ReviewResult(True, checks={"final_check": "ok"}, reason="ok")


def runtime_with_tools(*agents: TaskAgent, verifier=None) -> AgentRuntime:
    tools = ToolRegistry()
    tools.register(CallableTool("context.read", lambda arguments, state: {"title": f"Context for {arguments['topic']}"}))
    tools.register(CallableTool("note.draft", lambda arguments, state: {"html": f"<html>{arguments['instruction']}</html>"}))
    return AgentRuntime(agents=agents, tools=tools, verifier=verifier or BasicVerifier(), max_attempts=2)


def qa_tools(service: ItemService, *, model_client: ModelClient | None = None, use_model: bool = False) -> ToolRegistry:
    tools = ToolRegistry()
    tools.register(InputGuardrailTool(max_message_chars=4000))
    tools.register(ContextTool(service, max_context_items=5))
    tools.register(EvidenceTool(service, model_client=model_client, retrieval_mode="keyword", max_results=5))
    tools.register(ExpansionPolicyTool())
    tools.register(SearchPlanTool())
    tools.register(ExternalResearchTool())
    tools.register(SourceEvaluatorTool(model_client if use_model else None))
    tools.register(EvidenceGateTool(max_prompt_chars=12000))
    tools.register(EvidenceAssessmentTool())
    if use_model and model_client is not None:
        tools.register(
            LLMChatTool(
                model_client,
                prompt_builders={"qa.answer.v1": build_qa_answer_messages},
            ),
        )
    return tools


def test_agent_runtime_routes_explicit_qa_task_and_executes_allowed_tool() -> None:
    agent = EchoAgent()
    runtime = runtime_with_tools(agent)

    result = runtime.run(AgentRequest(content="总结这篇笔记", requested_task="qa"))

    assert result.status == "completed"
    assert result.task_type == "qa"
    assert result.answer == "Answer: Context for 总结这篇笔记"
    assert [tool.tool_id for tool in result.tool_results] == ["context.read"]
    assert [event["node"] for event in result.trace] == [
        "TaskRouter",
        "Planner",
        "ToolExecutor",
        "DraftBuilder",
        "Verifier",
        "Reviewer",
        "Finalizer",
        "OrchestratorReview",
    ]


def test_agent_runtime_auto_routes_generation_to_writer_agent() -> None:
    runtime = runtime_with_tools(EchoAgent(), WriterAgent())

    result = runtime.run(AgentRequest(content="生成一篇 HTML 笔记"))

    assert result.status == "completed"
    assert result.task_type == "writer"
    assert result.answer == "<html>生成一篇 HTML 笔记</html>"


def test_agent_runtime_replans_once_when_verifier_returns_retryable_failure() -> None:
    agent = EchoAgent()
    verifier = RetryVerifier()
    runtime = runtime_with_tools(agent, verifier=verifier)

    result = runtime.run(AgentRequest(content="总结"))

    assert result.status == "completed"
    assert agent.attempts == [1, 2]
    assert verifier.calls == 2
    assert [event["status"] for event in result.trace if event["node"] == "OrchestratorReview"] == ["retry", "completed"]


def test_agent_runtime_replans_once_when_reviewer_returns_retryable_failure() -> None:
    agent = EchoAgent()
    reviewer = RetryReviewer()
    tools = ToolRegistry()
    tools.register(CallableTool("context.read", lambda arguments, state: {"title": "Context"}))
    runtime = AgentRuntime(agents=(agent,), tools=tools, verifier=BasicVerifier(), reviewer=reviewer, max_attempts=2)

    result = runtime.run(AgentRequest(content="总结"))

    assert result.status == "completed"
    assert agent.attempts == [1, 2]
    assert reviewer.calls == 2
    assert result.review is not None
    assert result.review.reason == "ok"


def test_agent_runtime_stops_after_max_attempts_with_needs_attention() -> None:
    runtime = runtime_with_tools(EchoAgent(), verifier=AlwaysFailVerifier())

    result = runtime.run(AgentRequest(content="总结"))

    assert result.status == "needs_attention"
    assert result.verification is not None
    assert result.verification.reason == "quality_failed"
    assert result.trace[-1]["node"] == "OrchestratorReview"
    assert result.trace[-1]["status"] == "needs_attention"


def test_agent_runtime_blocks_unauthorized_tool_call() -> None:
    class BadAgent(EchoAgent):
        def plan(self, request: AgentRequest, state: dict, *, attempt: int) -> AgentPlan:
            return AgentPlan(task_type="qa", steps=(ToolCall("note.draft", {"instruction": "write"}),), attempt=attempt)

    runtime = runtime_with_tools(BadAgent())

    with pytest.raises(ToolPermissionError):
        runtime.run(AgentRequest(content="总结"))


def test_low_trust_generated_item_detector_flags_decline_artifact() -> None:
    item = {
        "title": "zzzz_unrelated_quantum_banana",
        "summary": "Based on 1 context note(s): 当前上下文没有足够资料回答这个问题。请调整上下文、选择相关笔记，或开启内容拓展后再试。",
        "source_type": "topic",
        "agent": {"generated": True},
    }

    assert is_low_trust_generated_item(
        item,
        "Question zzzz_unrelated_quantum_banana Answer 当前上下文没有足够资料回答这个问题。请调整上下文、选择相关笔记，或开启内容拓展后再试。 Referenced Context SNEC 2026",
    ) is True


def test_low_trust_generated_item_detector_keeps_normal_generated_note() -> None:
    item = {
        "title": "EPC 是什么",
        "summary": "EPC 是工程、采购、施工总承包模式。",
        "source_type": "topic",
        "agent": {"generated": True},
    }

    assert is_low_trust_generated_item(
        item,
        "EPC 可以简单理解为一种工程总包模式，涵盖设计、采购与施工。",
    ) is False


def test_global_keyword_retrieval_skips_low_trust_generated_artifact(tmp_path) -> None:
    content_dir, meta_dir, public_dir = make_dirs(tmp_path)
    make_note(content_dir, meta_dir, "imported/snec.html", title="SNEC 2026", collection="Expo", tags=["SNEC"])
    make_generated_note(
        content_dir,
        meta_dir,
        "generated/2026/06/zzzz_unrelated_quantum_banana.html",
        title="zzzz_unrelated_quantum_banana",
        summary="Based on 1 context note(s): 当前上下文没有足够资料回答这个问题。请调整上下文、选择相关笔记，或开启内容拓展后再试。",
        body="Question zzzz_unrelated_quantum_banana Answer 当前上下文没有足够资料回答这个问题。请调整上下文、选择相关笔记，或开启内容拓展后再试。 Referenced Context SNEC 2026",
        tags=["zzzz", "unrelated", "quantum", "banana", "SNEC"],
    )
    service = ItemService(
        ServerSettings(
            content_dir=content_dir,
            meta_dir=meta_dir,
            public_dir=public_dir,
            site_title="Runtime Test",
            max_upload_bytes=10 * 1024 * 1024,
        ),
    )

    evidence = retrieve_keyword_evidence(
        service,
        {
            "scope": "workspace",
            "item_ids": ["imported/snec.html", "generated/2026/06/zzzz_unrelated_quantum_banana.html"],
            "source_mode": "local_only",
        },
        "unrelated quantum banana",
        max_results=5,
    )

    assert evidence == []


def test_reader_keyword_retrieval_keeps_selected_generated_note(tmp_path) -> None:
    content_dir, meta_dir, public_dir = make_dirs(tmp_path)
    make_generated_note(
        content_dir,
        meta_dir,
        "generated/2026/06/zzzz_unrelated_quantum_banana.html",
        title="zzzz_unrelated_quantum_banana",
        summary="Based on 1 context note(s): 当前上下文没有足够资料回答这个问题。请调整上下文、选择相关笔记，或开启内容拓展后再试。",
        body="Question zzzz_unrelated_quantum_banana Answer 当前上下文没有足够资料回答这个问题。请调整上下文、选择相关笔记，或开启内容拓展后再试。 Referenced Context SNEC 2026",
        tags=["zzzz", "unrelated", "quantum", "banana", "SNEC"],
    )
    service = ItemService(
        ServerSettings(
            content_dir=content_dir,
            meta_dir=meta_dir,
            public_dir=public_dir,
            site_title="Runtime Test",
            max_upload_bytes=10 * 1024 * 1024,
        ),
    )

    evidence = retrieve_keyword_evidence(
        service,
        {
            "scope": "reader",
            "item_ids": ["generated/2026/06/zzzz_unrelated_quantum_banana.html"],
            "source_mode": "local_only",
        },
        "总结这篇笔记",
        max_results=5,
    )

    assert len(evidence) == 1
    assert evidence[0]["item_id"] == "generated/2026/06/zzzz_unrelated_quantum_banana.html"


def test_context_tool_resolves_reader_context(tmp_path) -> None:
    tool = ContextTool(item_service(tmp_path), max_context_items=5)

    result = tool.run({"context": {"item_id": "a.html"}, "source_mode": "local_plus_external"}, {})

    assert result["scope"] == "reader"
    assert result["context_key"] == 'reader:{"item_id":"a.html"}'
    assert result["context_title"] == "Alpha MCP"
    assert result["item_ids"] == ["a.html"]
    assert result["context"]["source_mode"] == "local_plus_external"


def test_context_tool_resolves_collection_and_excludes_archived(tmp_path) -> None:
    tool = ContextTool(item_service(tmp_path), max_context_items=5)

    result = tool.run({"context": {"scope": "collection", "collection": "AI"}}, {})

    assert result["scope"] == "collection"
    assert result["context_title"] == "Collection: AI"
    assert result["item_ids"] == ["a.html"]


def test_context_tool_manual_context_excludes_archived_by_default(tmp_path) -> None:
    tool = ContextTool(item_service(tmp_path), max_context_items=5)

    result = tool.run({"context": {"manual_item_ids": ["b.html", "archived.html"]}}, {})

    assert result["scope"] == "manual"
    assert result["context_title"] == "Selected notes (1)"
    assert result["item_ids"] == ["b.html"]


def test_context_tool_enforces_context_item_limit(tmp_path) -> None:
    tool = ContextTool(item_service(tmp_path), max_context_items=1)

    with pytest.raises(AIContextError):
        tool.run({"context": {"scope": "global"}}, {})


def test_agent_runtime_can_execute_context_tool(tmp_path) -> None:
    class ContextAgent:
        id = "agent.qa"
        task_type = "qa"
        allowed_tools = ("context.resolve",)

        def plan(self, request: AgentRequest, state: dict, *, attempt: int) -> AgentPlan:
            return AgentPlan(task_type="qa", steps=(ToolCall("context.resolve", {"context": {"item_id": "a.html"}}),), attempt=attempt)

        def draft(self, request: AgentRequest, plan: AgentPlan, tool_results: tuple, state: dict) -> AgentDraft:
            return AgentDraft(f"Context: {tool_results[0].output['context_title']}")

    tools = ToolRegistry()
    tools.register(ContextTool(item_service(tmp_path), max_context_items=5))
    runtime = AgentRuntime(agents=(ContextAgent(),), tools=tools, verifier=BasicVerifier())

    result = runtime.run(AgentRequest(content="总结"))

    assert result.status == "completed"
    assert result.answer == "Context: Alpha MCP"
    assert result.tool_results[0].output["item_ids"] == ["a.html"]


def test_evidence_pack_separates_chunks_sources_and_citations() -> None:
    pack = build_evidence_pack(
        query="MCP",
        chunks=[
            {"item_id": "a.html", "title": "Alpha", "snippet": "first", "score": 10},
            {"item_id": "a.html", "title": "Alpha", "snippet": "second", "score": 8},
            {"item_id": "b.html", "title": "Beta", "snippet": "third", "score": 6},
        ],
        status={"effective_mode": "keyword"},
    )

    assert len(pack["chunks"]) == 3
    assert len(pack["sources"]) == 2
    assert [source["source_index"] for source in pack["sources"]] == [1, 2]
    assert [chunk["source_index"] for chunk in pack["chunks"]] == [1, 1, 2]
    assert pack["citation_map"] == {"chunk-1": 1, "chunk-2": 1, "chunk-3": 2}
    assert pack["status"]["chunk_count"] == 3
    assert pack["status"]["source_count"] == 2


def test_evidence_tool_builds_pack_from_resolved_context(tmp_path) -> None:
    service = item_service(tmp_path)
    context = ContextTool(service, max_context_items=5).run({"context": {"item_id": "a.html"}}, {})["context"]
    tool = EvidenceTool(service, retrieval_mode="keyword", max_results=5)

    pack = tool.run({"context": context, "query": "MCP Docker"}, {})

    assert pack["query"] == "MCP Docker"
    assert pack["chunks"]
    assert pack["sources"] == [{"kind": "local", "source_index": 1, "title": "Alpha MCP", "item_id": "a.html"}]
    assert all(chunk["source_index"] == 1 for chunk in pack["chunks"])
    assert pack["status"]["effective_mode"] == "keyword"


def test_agent_runtime_can_execute_context_then_evidence_tools(tmp_path) -> None:
    class EvidenceAgent:
        id = "agent.qa"
        task_type = "qa"
        allowed_tools = ("context.resolve", "evidence.build")

        def plan(self, request: AgentRequest, state: dict, *, attempt: int) -> AgentPlan:
            return AgentPlan(
                task_type="qa",
                steps=(
                    ToolCall("context.resolve", {"context": {"item_id": "a.html"}}),
                    ToolCall("evidence.build", {"context": {"item_ids": ["a.html"], "scope": "reader"}, "query": request.content}),
                ),
                attempt=attempt,
            )

        def draft(self, request: AgentRequest, plan: AgentPlan, tool_results: tuple, state: dict) -> AgentDraft:
            evidence_pack = tool_results[1].output
            return AgentDraft(f"Sources: {len(evidence_pack['sources'])}; Chunks: {len(evidence_pack['chunks'])}")

    service = item_service(tmp_path)
    tools = ToolRegistry()
    tools.register(ContextTool(service, max_context_items=5))
    tools.register(EvidenceTool(service, retrieval_mode="keyword", max_results=5))
    runtime = AgentRuntime(agents=(EvidenceAgent(),), tools=tools, verifier=BasicVerifier())

    result = runtime.run(AgentRequest(content="MCP Docker"))

    assert result.status == "completed"
    assert result.answer.startswith("Sources: 1; Chunks:")
    assert [tool.tool_id for tool in result.tool_results] == ["context.resolve", "evidence.build"]


def test_knowledge_qa_agent_happy_path_uses_context_and_evidence_tools(tmp_path) -> None:
    service = item_service(tmp_path)
    runtime = AgentRuntime(
        agents=(KnowledgeQATaskAgent(),),
        tools=qa_tools(service),
        verifier=KnowledgeQAVerifier(),
        reviewer=KnowledgeQAReviewer(),
    )

    result = runtime.run(AgentRequest(content="总结这篇笔记", context={"item_id": "a.html"}, requested_task="qa"))

    assert result.status == "completed"
    assert result.task_type == "qa"
    assert "Alpha MCP 的核心内容可以先这样理解" in result.answer
    assert "来源：[1] Alpha MCP" in result.answer
    assert "笔记提到" not in result.answer
    assert [tool.tool_id for tool in result.tool_results] == [
        "guardrail.input",
        "context.resolve",
        "evidence.build",
        "expansion.policy",
        "search.plan",
        "external.research",
        "source.evaluate",
        "evidence.gate",
        "evidence.assess",
    ]
    assert result.verification is not None
    assert result.verification.reason == "ok"
    assert result.review is not None
    assert result.review.reason == "ok"


def test_llm_chat_tool_uses_registered_prompt_builder() -> None:
    tool = LLMChatTool(
        ModelClient(AIProviderConfig(provider="fake", enabled=True, model="fake-model")),
        prompt_builders={
            "test.prompt": lambda arguments, state: [
                {"role": "system", "content": "test"},
                {"role": "user", "content": f"Question: {arguments['question']}"},
            ],
        },
    )

    result = tool.run({"prompt_id": "test.prompt", "question": "MCP"}, {})

    assert result["model"] == "fake-model"
    assert result["prompt_id"] == "test.prompt"
    assert result["message_count"] == 2
    assert "Question: MCP" in result["content"]


def test_knowledge_qa_agent_can_call_model_tool_after_evidence_build(tmp_path) -> None:
    service = item_service(tmp_path)
    model_client = ModelClient(AIProviderConfig(provider="fake", enabled=True, model="fake-model"))
    runtime = AgentRuntime(
        agents=(KnowledgeQATaskAgent(use_model=True),),
        tools=qa_tools(service, model_client=model_client, use_model=True),
        verifier=KnowledgeQAVerifier(),
        reviewer=KnowledgeQAReviewer(),
    )

    result = runtime.run(AgentRequest(content="总结这篇笔记", context={"item_id": "a.html"}, requested_task="qa"))

    assert result.status == "completed"
    assert [tool.tool_id for tool in result.tool_results][-2:] == ["evidence.assess", "llm.chat"]
    assert result.answer.startswith("Fake AI response for:")
    assert "来源：" in result.answer
    assert result.final_output is not None
    assert result.verification is not None
    assert result.verification.checks["invalid_citations"] == []


def test_knowledge_qa_agent_declines_weak_relevance_before_model_call(tmp_path) -> None:
    service = item_service(tmp_path)
    model_client = ModelClient(AIProviderConfig(provider="fake", enabled=True, model="fake-model"))
    runtime = AgentRuntime(
        agents=(KnowledgeQATaskAgent(use_model=True),),
        tools=qa_tools(service, model_client=model_client, use_model=True),
        verifier=KnowledgeQAVerifier(),
        reviewer=KnowledgeQAReviewer(),
    )

    result = runtime.run(AgentRequest(content="What does runtime evidence say about Kyoto travel?", context={"scope": "global"}, requested_task="qa"))

    assert result.status == "completed"
    assert "关联不足" in result.answer
    llm_result = next(tool for tool in result.tool_results if tool.tool_id == "llm.chat")
    assert llm_result.output["skipped"] is True
    assert llm_result.output["skip_reason"] == "weak_relevance"
    assessment = next(tool.output for tool in result.tool_results if tool.tool_id == "evidence.assess")
    assert assessment["decision"] == {
        "action": "decline",
        "reason": "weak_relevance",
        "confidence": 0.86,
        "requires_attention": True,
    }
    assert result.review is not None
    assert result.review.checks["declined"] == "weak_relevance"


def test_knowledge_qa_agent_accepts_reader_question_when_chunk_matches_query(tmp_path) -> None:
    content_dir, meta_dir, public_dir = make_dirs(tmp_path)
    make_note(
        content_dir,
        meta_dir,
        "octopus.html",
        title="章鱼能源小白入门版深度分析报告",
        collection="Energy",
        tags=["Octopus"],
    )
    (content_dir / "octopus.html").write_text(
        "<!doctype html><html><body><p>Kraken 像公用事业公司的操作系统，把客户、账单、电表、客服、交易、设备调度放在同一套系统里运行。</p></body></html>",
        encoding="utf-8",
    )
    service = ItemService(
        ServerSettings(
            content_dir=content_dir,
            meta_dir=meta_dir,
            public_dir=public_dir,
            site_title="Runtime Test",
            max_upload_bytes=10 * 1024 * 1024,
        ),
    )
    model_client = ModelClient(AIProviderConfig(provider="fake", enabled=True, model="fake-model"))
    runtime = AgentRuntime(
        agents=(KnowledgeQATaskAgent(use_model=True),),
        tools=qa_tools(service, model_client=model_client, use_model=True),
        verifier=KnowledgeQAVerifier(),
        reviewer=KnowledgeQAReviewer(),
    )

    result = runtime.run(AgentRequest(content="解释 Kraken 平台是什么", context={"item_id": "octopus.html"}, requested_task="qa"))

    assert result.status == "completed"
    assert result.answer.startswith("Fake AI response")
    assessment = next(tool.output for tool in result.tool_results if tool.tool_id == "evidence.assess")
    assert assessment["weak_relevance"] is False
    assert assessment["decision"]["action"] == "answer"


def test_knowledge_qa_agent_declines_insufficient_evidence_before_model_call(tmp_path) -> None:
    service = item_service(tmp_path)
    model_client = ModelClient(AIProviderConfig(provider="fake", enabled=True, model="fake-model"))
    runtime = AgentRuntime(
        agents=(KnowledgeQATaskAgent(use_model=True),),
        tools=qa_tools(service, model_client=model_client, use_model=True),
        verifier=KnowledgeQAVerifier(),
        reviewer=KnowledgeQAReviewer(),
    )

    result = runtime.run(AgentRequest(content="Write a travel plan for Kyoto.", context={"scope": "global"}, requested_task="qa"))

    assert result.status == "completed"
    assert "没有找到足够资料" in result.answer
    llm_result = next(tool for tool in result.tool_results if tool.tool_id == "llm.chat")
    assert llm_result.output["skipped"] is True
    assert llm_result.output["skip_reason"] == "insufficient_evidence"
    assessment = next(tool.output for tool in result.tool_results if tool.tool_id == "evidence.assess")
    assert assessment["decision"]["reason"] == "insufficient_evidence"
    assert result.review is not None
    assert result.review.checks["declined"] == "insufficient_evidence"


def test_external_evidence_assessment_rejects_results_without_attribute_terms() -> None:
    assessment = external_evidence_assessment(
        chunks=[
            {
                "kind": "external",
                "title": "风泉资本走进德化共探产业投资新机遇",
                "snippet": "介绍风泉资本的产业投资布局和背景。",
                "url": "https://example.test/profile",
            },
        ],
        query="风泉资本的股权结构如何",
        search_plan={
            "search": {
                "required_terms": ["风泉资本"],
                "evidence_terms": ["股东", "持股", "股权", "实控"],
            },
        },
    )

    assert assessment["weak_relevance"] is True
    assert assessment["insufficient_evidence"] is False
    assert assessment["decision"]["action"] == "decline"
    assert assessment["decision"]["reason"] == "weak_external_evidence"
    assert assessment["matched_evidence_terms"] == []


def test_external_evidence_assessment_accepts_results_with_attribute_terms() -> None:
    assessment = external_evidence_assessment(
        chunks=[
            {
                "kind": "external",
                "title": "风泉资本股东及持股信息",
                "snippet": "披露股东、持股比例和股权结构。",
                "url": "https://example.test/shareholders",
            },
        ],
        query="风泉资本的股权结构如何",
        search_plan={
            "search": {
                "required_terms": ["风泉资本"],
                "evidence_terms": ["股东", "持股", "股权", "实控"],
            },
        },
    )

    assert assessment["weak_relevance"] is False
    assert assessment["insufficient_evidence"] is False
    assert assessment["decision"]["action"] == "answer"
    assert "股东" in assessment["matched_evidence_terms"]


def test_build_retrieval_query_uses_recent_user_messages_only() -> None:
    query = build_retrieval_query(
        "联网搜索",
        [
            {"role": "user", "content": "先解释一下这篇笔记里的电力市场交易和协同增效。"},
            {"role": "assistant", "content": "这是上一轮回答，不应该进入检索词。"},
        ],
    )

    assert "电力市场交易" in query
    assert "上一轮回答" not in query


def test_build_retrieval_query_prefers_recent_entity_focus_for_pronoun_followup() -> None:
    query = build_retrieval_query(
        "他的股权结构是怎样的？",
        [
            {"role": "user", "content": "风泉资本是什么背景"},
            {"role": "assistant", "content": "我先给你查风泉资本的背景。"},
        ],
    )

    assert query.startswith("风泉资本")
    assert "他的股权结构" in query


def test_build_retrieval_query_handles_cross_domain_named_topic_followup() -> None:
    query = build_retrieval_query(
        "它和 Logic Pro 有什么区别？",
        [
            {"role": "user", "content": "Ableton Live 的 warping 是什么？"},
            {"role": "assistant", "content": "Warping 是 Ableton Live 的时间拉伸机制。"},
        ],
    )

    assert query.startswith("Ableton Live")
    assert "Logic Pro" in query


def test_build_retrieval_query_does_not_carry_previous_focus_into_explicit_new_topic() -> None:
    query = build_retrieval_query(
        "什么是 Lydian mode？",
        [
            {"role": "user", "content": "风泉资本是什么背景？"},
            {"role": "assistant", "content": "我先给你查风泉资本的背景。"},
        ],
    )

    assert query == "什么是 Lydian mode？"


def test_expansion_policy_uses_model_knowledge_for_concept_question_without_local_definition() -> None:
    state = {
        "query": "什么是微电网",
        "source_mode": "local_plus_external",
        "tool_outputs": {
            "context.resolve": {"context": {"scope": "reader", "source_mode": "local_plus_external"}},
            "evidence.build": {
                "chunks": [
                    {
                        "item_id": "microgrid.html",
                        "title": "工商业光储+微电网+虚拟电厂协同增效方案",
                        "snippet": "方案讨论工商业光储、微电网、虚拟电厂协同增效，但没有直接给出微电网定义。",
                        "score": 34,
                    },
                ],
            },
        },
    }

    result = ExpansionPolicyTool().run({"query": "什么是微电网"}, state)

    assert result["mode"] == "model_knowledge"
    assert result["reason"] == "concept_explanation_fallback"


def test_expansion_policy_prefers_local_evidence_when_concept_is_defined_locally() -> None:
    state = {
        "query": "什么是微电网",
        "source_mode": "local_plus_external",
        "tool_outputs": {
            "context.resolve": {"context": {"scope": "reader", "source_mode": "local_plus_external"}},
            "evidence.build": {
                "chunks": [
                    {
                        "item_id": "microgrid.html",
                        "title": "微电网学习指南",
                        "snippet": "微电网是指由分布式电源、储能、负荷和控制系统组成的小型电力系统。",
                        "score": 34,
                    },
                ],
            },
        },
    }

    result = ExpansionPolicyTool().run({"query": "什么是微电网"}, state)

    assert result["mode"] == "local_evidence"
    assert result["reason"] == "local_evidence_available"


def test_expansion_policy_keeps_concept_question_local_only_when_expansion_is_disabled() -> None:
    state = {
        "query": "什么是微电网",
        "source_mode": "local_only",
        "tool_outputs": {
            "context.resolve": {"context": {"scope": "reader", "source_mode": "local_only"}},
            "evidence.build": {"chunks": []},
        },
    }

    result = ExpansionPolicyTool().run({"query": "什么是微电网"}, state)

    assert result["mode"] == "local_only"
    assert result["reason"] == "content_expansion_disabled"


def test_evidence_overlap_uses_chinese_concept_term_instead_of_bigram_noise() -> None:
    assert evidence_chunks_overlap_query(
        "什么是微电网",
        [
            {
                "title": "工商业光储+微电网+虚拟电厂协同增效方案",
                "snippet": "方案讨论工商业光储、微电网和虚拟电厂协同增效。",
            },
        ],
    )


def test_knowledge_qa_fallback_answer_varies_by_intent() -> None:
    agent = KnowledgeQATaskAgent(use_model=False)
    chunks = [{"snippet": "微电网负责园区内资源协同和本地自治控制。", "title": "微电网说明"}]
    sources = [{"source_index": 1, "title": "微电网说明"}]
    tool_results = (
        ToolResult(tool_id="context.resolve", status="completed", output={"context_title": "微电网说明"}),
        ToolResult(tool_id="evidence.gate", status="completed", output={"chunks": chunks, "sources": sources}),
        ToolResult(tool_id="evidence.assess", status="completed", output={}),
    )

    concept = agent.draft(
        AgentRequest(content="什么是微电网"),
        AgentPlan(task_type="qa", metadata={"planner": {"intent": "concept_clarify"}}),
        tool_results,
        {},
    )
    deeper = agent.draft(
        AgentRequest(content="详细介绍下微电网"),
        AgentPlan(task_type="qa", metadata={"planner": {"intent": "explain_deeper"}}),
        tool_results,
        {},
    )

    assert concept.content.startswith("如果只抓住核心定义")
    assert deeper.content.startswith("围绕这个主题，可以先从核心机制讲起")


def test_knowledge_qa_reviewer_accepts_concept_answer_with_explanatory_markers() -> None:
    reviewer = KnowledgeQAReviewer()
    draft = AgentDraft("微电网可以理解为园区内部资源协同运行的局部能源系统。它通常把分布式电源、储能和负荷放在同一个局部范围内统一调度，用来提升供电可靠性和能源利用效率。\n\n来源：[1] 微电网说明", metadata={"chunk_count": 1})
    result = reviewer.review(
        AgentRequest(content="什么是微电网"),
        AgentPlan(task_type="qa", metadata={"planner": {"intent": "concept_clarify"}}),
        (),
        draft,
        VerificationResult(True, checks={}, reason="ok"),
        {},
    )

    assert result.passed is True
    assert result.checks["intent"] == "concept_clarify"


def test_knowledge_qa_verifier_can_use_model_decision() -> None:
    class VerifierModel:
        last_messages = None

        def chat(self, *, messages, temperature=0.0, max_tokens=256):
            self.last_messages = messages
            return {"content": '{"passed":false,"reason":"answer_not_grounded","retryable":true,"checks":{"grounded":false}}'}

    model = VerifierModel()
    verifier = KnowledgeQAVerifier(use_model=True, model_client=model)
    result = verifier.verify(
        AgentRequest(content="总结"),
        AgentPlan(task_type="qa"),
        (
            ToolResult(
                tool_id="evidence.build",
                status="completed",
                output={
                    "chunks": [{"chunk_id": "chunk-1", "snippet": "x", "source_index": 1}],
                    "sources": [{"source_index": 1, "title": "A"}],
                    "citation_map": {"chunk-1": 1},
                },
            ),
        ),
        "这是一个回答。\n\n来源：[1] A",
        {},
    )

    assert result.passed is False
    assert result.reason == "answer_not_grounded"
    assert result.retryable is True
    assert result.checks["verifier_mode"] == "llm"
    assert result.checks["grounded"] is False
    payload = json.loads(model.last_messages[-1]["content"])
    assert payload["evidence_review_context"]["source_count"] == 1
    assert "tool_results" not in payload


def test_knowledge_qa_verifier_falls_back_when_model_decision_is_invalid() -> None:
    class BrokenVerifierModel:
        def chat(self, *, messages, temperature=0.0, max_tokens=256):
            return {"content": "not json"}

    verifier = KnowledgeQAVerifier(use_model=True, model_client=BrokenVerifierModel())
    result = verifier.verify(
        AgentRequest(content="总结"),
        AgentPlan(task_type="qa"),
        (
            ToolResult(
                tool_id="evidence.build",
                status="completed",
                output={
                    "chunks": [{"chunk_id": "chunk-1", "snippet": "x", "source_index": 1}],
                    "sources": [{"source_index": 1, "title": "A"}],
                    "citation_map": {"chunk-1": 1},
                },
            ),
        ),
        "这是一个回答。\n\n来源：[1] A",
        {},
    )

    assert result.passed is True
    assert result.reason == "ok"
    assert "verifier_mode" not in result.checks


def test_knowledge_qa_reviewer_can_use_model_decision() -> None:
    class ReviewerModel:
        last_messages = None

        def chat(self, *, messages, temperature=0.0, max_tokens=256):
            self.last_messages = messages
            return {"content": '{"passed":false,"reason":"too_fragmented","retryable":true,"checks":{"readability":"poor"}}'}

    model = ReviewerModel()
    reviewer = KnowledgeQAReviewer(use_model=True, model_client=model)
    result = reviewer.review(
        AgentRequest(content="详细解释"),
        AgentPlan(task_type="qa", metadata={"planner": {"intent": "explain_deeper"}}),
        (),
        AgentDraft("这是一个回答。\n\n来源：[1] A", metadata={"chunk_count": 1}),
        VerificationResult(True, checks={}, reason="ok"),
        {},
    )

    assert result.passed is False
    assert result.reason == "too_fragmented"
    assert result.retryable is True
    assert result.checks["reviewer_mode"] == "llm"
    assert result.checks["readability"] == "poor"
    payload = json.loads(model.last_messages[-1]["content"])
    assert "evidence_review_context" in payload
    assert "tool_results" not in payload


def test_build_qa_answer_messages_includes_task_intent_and_search_plan() -> None:
    messages = build_qa_answer_messages(
        {"question": "详细介绍下微电网"},
        {
            "query": "详细介绍下微电网",
            "plan_metadata": {"planner": {"intent": "explain_deeper"}},
            "tool_outputs": {
                "context.resolve": {"context_title": "微电网"},
                "evidence.build": {"chunks": [{"source_index": 1, "chunk_index": 1, "title": "微电网说明", "snippet": "微电网是一种局部能源系统。"}], "sources": [{"source_index": 1, "title": "微电网说明"}]},
                "external.research": {"search_plan": {"should_search": False, "locality_hint": "global", "language_hint": "zh", "reason": "planner_default"}},
            },
        },
    )

    joined = "\n".join(message["content"] for message in messages)
    assert "TASK_INTENT:\nexplain_deeper" in joined
    assert "SEARCH_PLAN:" in joined
    assert "3-5 coherent points" in joined


def test_evidence_gate_distinguishes_external_no_results_from_unavailable() -> None:
    tool = EvidenceGateTool(max_prompt_chars=12000)
    base_state = {
        "tool_outputs": {
            "context.resolve": {"context": {"scope": "reader", "source_mode": "local_plus_external"}},
            "evidence.build": {"query": "联网搜索基金案例", "chunks": [], "sources": []},
            "expansion.policy": {"mode": "web_research"},
        },
    }

    no_results = tool.run(
        {"query": "联网搜索基金案例"},
        {
            **base_state,
            "tool_outputs": {
                **base_state["tool_outputs"],
                "external.research": {"sources": [], "status": {"provider": "tavily", "available": True, "queried": True, "count": 0}},
            },
        },
    )
    unavailable = tool.run(
        {"query": "联网搜索基金案例"},
        {
            **base_state,
            "tool_outputs": {
                **base_state["tool_outputs"],
                "external.research": {"sources": [], "status": {"provider": "tavily", "available": False, "message": "External content expansion is not configured."}},
            },
        },
    )

    assert no_results["answer"] == EXTERNAL_NO_RESULTS_ANSWER
    assert unavailable["answer"] == EXTERNAL_UNAVAILABLE_ANSWER


def test_evidence_gate_keeps_local_context_when_external_search_has_no_usable_sources() -> None:
    tool = EvidenceGateTool(max_prompt_chars=12000)
    result = tool.run(
        {"query": "风泉和晶科有什么关系"},
        {
            "tool_outputs": {
                "context.resolve": {"context": {"scope": "reader", "source_mode": "local_plus_external", "item_ids": ["note.html"]}},
                "evidence.build": {
                    "query": "风泉和晶科有什么关系",
                    "chunks": [
                        {
                            "kind": "local",
                            "item_id": "note.html",
                            "title": "储能基金结构方案",
                            "snippet": "笔记说明基金方案中涉及风泉资本、晶科以及储能项目公司安排。",
                            "score": 24,
                        },
                    ],
                    "sources": [],
                },
                "expansion.policy": {"mode": "web_research", "requires_citation": True},
                "external.research": {"sources": [], "status": {"provider": "tavily", "available": True, "queried": True, "count": 0}},
                "source.evaluate": {"sources": [], "mode": "llm", "kept_count": 0, "dropped_count": 3},
            },
        },
    )

    assert result["answer"] == ""
    assert result["skipped_model_call"] is False
    assert result["chunks"][0]["title"] == "储能基金结构方案"
    assert result["sources"][0]["kind"] == "local"
    assert "external_evidence_count=0" in "\n".join(message["content"] for message in result["messages"])


def test_external_research_uses_independent_search_plan_query() -> None:
    class RecordingSearch:
        name = "recording"
        max_results = 5

        def __init__(self) -> None:
            self.queries: list[str] = []

        @property
        def available(self) -> bool:
            return True

        def search(self, query: str, *, max_results: int = 5):
            self.queries.append(query)
            return [
                ExternalSearchResult(
                    title="基金案例",
                    url="https://example.test/fund-case",
                    snippet="基金/SPV 项目公司 优先 劣后 案例",
                    accessed_at="2026-06-16T00:00:00+00:00",
                ),
            ]

    search = RecordingSearch()
    tool = ExternalResearchTool(search)
    state = {
        "query": "联网搜索更多利用这种结构的基金案例",
        "retrieval_query": "基金/SPV下面再设项目公司，并在项目公司层面做优先/劣后股权分层安排。联网搜索更多基金案例",
        "tool_outputs": {
            "context.resolve": {"context": {"scope": "reader", "source_mode": "local_plus_external", "items": [{"title": "储能基金结构方案"}]}},
            "expansion.policy": {"mode": "web_research"},
            "search.plan": {
                "should_search": True,
                "effective_should_search": True,
                "queries": ["基金 SPV 项目公司 优先 劣后 案例 中国 中文"],
                "search": {"search_intent": "case_search"},
            },
        },
    }

    result = tool.run({"query": "联网搜索更多利用这种结构的基金案例", "planner": {"should_search": True}}, state)

    assert search.queries == ["基金 SPV 项目公司 优先 劣后 案例 中国 中文"]
    assert result["queried"] is True
    assert result["search_plan"]["search"]["search_intent"] == "case_search"


def test_research_limits_scale_by_search_intent_with_total_cap() -> None:
    plan = SearchPlan(
        original_query="A B",
        intent="entity_relationship",
        queries=["A B relation", "A B ownership", "A B announcement", "A B registry"],
        required_terms=["A", "B"],
        preferred_domains=[],
        authoritative_required=False,
        query_expansions=[],
        evidence_terms=[],
    )

    limits = research_limits_for_plan(plan, base_max_results=5, total_candidate_limit=24)

    assert limits["base_max_results"] == 5
    assert limits["intent_max_results"] == 8
    assert limits["max_results"] == 6
    assert limits["total_candidate_limit"] == 24


def test_research_workflow_uses_dynamic_per_query_limit() -> None:
    class RecordingSearch:
        name = "recording"
        max_results = 5

        def __init__(self) -> None:
            self.calls: list[tuple[str, int]] = []

        @property
        def available(self) -> bool:
            return True

        def search(self, query: str, *, max_results: int = 5):
            self.calls.append((query, max_results))
            return [
                ExternalSearchResult(
                    title=f"{query} result {index}",
                    url=f"https://example.test/{query.replace(' ', '-')}/{index}",
                    snippet=f"{query} relation investment ownership",
                    accessed_at="2026-06-16T00:00:00+00:00",
                )
                for index in range(max_results)
            ]

    plan = SearchPlan(
        original_query="风泉资本 晶科",
        intent="entity_relationship",
        queries=["风泉资本 晶科 关系", "风泉资本 晶科 股权", "风泉资本 晶科 公告", "风泉资本 晶科 工商"],
        required_terms=["风泉资本", "晶科"],
        preferred_domains=[],
        authoritative_required=False,
        query_expansions=[],
        evidence_terms=["关系", "投资", "股权"],
    )
    search = RecordingSearch()

    result = ResearchWorkflow(search).run_plan(plan)

    assert search.calls
    assert {limit for _, limit in search.calls} == {6}
    assert result.status["base_max_results"] == 5
    assert result.status["intent_max_results"] == 8
    assert result.status["max_results"] == 6
    assert result.status["total_candidate_limit"] == 24


def test_search_planner_agent_uses_model_search_plan() -> None:
    class PlannerModel:
        def chat(self, *, messages, temperature=0.0, max_tokens=700):
            return {
                "content": json.dumps(
                    {
                        "should_search": True,
                        "search_intent": "entity_relationship",
                        "queries": [
                            "风泉资本 晶科 关系 投资 基金",
                            "风泉资本 晶科 股东 合作 公告",
                        ],
                        "required_terms": ["风泉资本", "晶科"],
                        "preferred_domains": ["amac.org.cn"],
                        "authoritative_required": False,
                        "evidence_terms": ["关系", "投资", "基金"],
                        "locality_hint": "china",
                        "language_hint": "zh",
                        "reason": "model_planned_relationship_search",
                    },
                    ensure_ascii=False,
                ),
                "model": "planner-test",
                "usage": {"total_tokens": 12},
            }

    planner = SearchPlannerAgent(PlannerModel())
    result = planner.plan(
        question="风泉资本什么背景，和晶科有什么关系",
        planner={"should_search": True, "search_intent": "entity_relationship"},
        policy={"mode": "web_research"},
        context={"scope": "reader", "source_mode": "local_plus_external", "items": [{"title": "储能基金结构方案"}]},
        local_evidence={},
    )

    assert result["planner_mode"] == "llm"
    assert result["should_search"] is True
    assert result["effective_should_search"] is True
    assert result["search"]["search_intent"] == "entity_relationship"
    assert result["search"]["required_terms"] == ["风泉资本", "晶科"]
    assert result["queries"] == ["风泉资本 晶科 关系 投资 基金", "风泉资本 晶科 股东 合作 公告"]


def test_search_plan_tool_falls_back_without_model() -> None:
    tool = SearchPlanTool()
    state = {
        "query": "风泉资本什么背景，和晶科有什么关系",
        "tool_outputs": {
            "context.resolve": {"context": {"scope": "reader", "source_mode": "local_plus_external", "items": [{"title": "储能基金结构方案"}]}},
            "expansion.policy": {"mode": "web_research"},
            "evidence.build": {},
        },
    }

    result = tool.run({"query": "风泉资本什么背景，和晶科有什么关系", "planner": {"should_search": True, "search_intent": "entity_relationship"}}, state)

    assert result["planner_mode"] == "heuristic_fallback"
    assert result["should_search"] is True
    assert result["effective_should_search"] is True
    assert result["search"]["required_terms"] == ["风泉资本", "晶科"]


def test_source_evaluator_drops_unrelated_external_candidates() -> None:
    class EvaluatorModel:
        def chat(self, *, messages, temperature=0.0, max_tokens=700):
            return {
                "content": json.dumps(
                    {
                        "sources": [
                            {"index": 1, "keep": False, "confidence": 0.96, "reason": "literary source, not business relationship"},
                            {"index": 2, "keep": False, "confidence": 0.9, "reason": "mentions only one entity"},
                            {"index": 3, "keep": True, "confidence": 0.88, "reason": "directly discusses both entities and fund participation"},
                        ],
                        "overall": {"usable_count": 1, "reason": "one direct source"},
                    },
                    ensure_ascii=False,
                ),
                "model": "source-evaluator-test",
                "usage": {},
            }

    tool = SourceEvaluatorTool(EvaluatorModel())
    state = {
        "retrieval_query": "风泉和晶科有什么关系",
        "tool_outputs": {
            "expansion.policy": {"mode": "web_research"},
            "external.research": {
                "search_plan": {
                    "search": {
                        "search_intent": "entity_relationship",
                        "required_terms": ["风泉", "晶科"],
                        "evidence_terms": ["关系", "合作", "投资", "基金"],
                    },
                },
                "sources": [
                    {"kind": "external", "title": "《将进酒》的风泉是个怎样的人？", "url": "https://example.test/novel", "snippet": "文学角色讨论。"},
                    {"kind": "external", "title": "晶科年度报告", "url": "https://example.test/jinko", "snippet": "晶科业务介绍。"},
                    {"kind": "external", "title": "风泉资本与晶科共同参与设立基金", "url": "https://example.test/relation", "snippet": "风泉和晶科围绕基金设立、投资关系开展合作。"},
                ],
            },
        },
    }

    result = tool.run({"query": "风泉和晶科有什么关系"}, state)

    assert result["mode"] == "llm"
    assert result["kept_count"] == 1
    assert result["dropped_count"] == 2
    assert [source["title"] for source in result["sources"]] == ["风泉资本与晶科共同参与设立基金"]
    assert result["decisions"][0]["keep"] is False


def test_build_qa_answer_messages_prefers_gated_evidence_over_raw_evidence() -> None:
    messages = build_qa_answer_messages(
        {"question": "详细介绍下微电网"},
        {
            "query": "详细介绍下微电网",
            "plan_metadata": {"planner": {"intent": "explain_deeper"}},
            "tool_outputs": {
                "context.resolve": {"context_title": "微电网"},
                "evidence.build": {
                    "chunks": [{"source_index": 1, "chunk_index": 1, "title": "原始证据", "snippet": "raw evidence should not be used"}],
                    "sources": [{"source_index": 1, "title": "原始证据"}],
                },
                "evidence.gate": {
                    "chunks": [{"source_index": 1, "chunk_index": 1, "title": "过滤后证据", "snippet": "gated evidence should be used"}],
                    "sources": [{"source_index": 1, "title": "过滤后证据"}],
                },
                "external.research": {"search_plan": {"should_search": False, "locality_hint": "global", "language_hint": "zh", "reason": "planner_default"}},
            },
        },
    )

    joined = "\n".join(message["content"] for message in messages)
    assert "过滤后证据" in joined
    assert "gated evidence should be used" in joined
    assert "raw evidence should not be used" not in joined


def test_heuristic_planner_routes_logic_relationship_questions_to_explain_deeper() -> None:
    agent = KnowledgeQATaskAgent(use_model=False)
    plan = agent._heuristic_plan("详细分析储能和光伏场景的逻辑关系", {}, {})

    assert plan["intent"] == "explain_deeper"
    assert plan["retrieval_mode"] == "model_knowledge"
    assert plan["should_search"] is False


def test_heuristic_planner_routes_detailed_domain_explanation_to_model_knowledge_not_web() -> None:
    agent = KnowledgeQATaskAgent(use_model=False)
    plan = agent._heuristic_plan("详细介绍一下虚拟电厂为什么能参与电力市场交易", {}, {})

    assert plan["intent"] == "explain_deeper"
    assert plan["retrieval_mode"] == "model_knowledge"
    assert plan["should_expand"] is True
    assert plan["should_search"] is False
    assert plan["locality"] == "local_context_first"


def test_heuristic_planner_routes_latest_policy_to_web_research() -> None:
    agent = KnowledgeQATaskAgent(use_model=False)
    plan = agent._heuristic_plan("最近国内虚拟电厂政策有哪些变化", {}, {})

    assert plan["intent"] == "current_info"
    assert plan["retrieval_mode"] == "web_research"
    assert plan["should_search"] is True
    assert plan["search_intent"] == "policy_lookup"


def test_heuristic_planner_routes_official_version_to_web_research() -> None:
    agent = KnowledgeQATaskAgent(use_model=False)
    plan = agent._heuristic_plan("MCP 官方规范最新版本是什么", {}, {})

    assert plan["intent"] == "current_info"
    assert plan["retrieval_mode"] == "web_research"
    assert plan["should_search"] is True
    assert plan["search_intent"] == "version_lookup"


def test_heuristic_planner_routes_entity_background_questions_to_web_research() -> None:
    agent = KnowledgeQATaskAgent(use_model=False)
    plan = agent._heuristic_plan("风泉资本是什么背景", {}, {})

    assert plan["intent"] == "current_info"
    assert plan["retrieval_mode"] == "web_research"
    assert plan["should_search"] is True
    assert plan["search_intent"] == "entity_lookup"
    assert plan["reason"] == "entity_background_lookup"


def test_qa_planner_agent_uses_model_json_when_valid() -> None:
    class PlannerModel:
        def chat(self, *, messages, temperature=0.0, max_tokens=320):
            return {
                "content": '{"intent":"current_info","retrieval_mode":"web_research","should_expand":true,"should_search":true,"search_intent":"general","locality":"local_context_first","reason":"model_planned_case_search"}',
                "model": "planner-test",
                "usage": {},
            }

    agent = KnowledgeQATaskAgent(use_model=True, model_client=PlannerModel())
    plan = agent.plan(
        AgentRequest(content="联网搜索更多利用这种结构的基金案例", context={"source_mode": "local_plus_external"}),
        {},
        attempt=1,
    )

    assert plan.metadata["planner"]["planner_mode"] == "llm"
    assert plan.metadata["planner"]["retrieval_mode"] == "web_research"
    assert plan.metadata["planner"]["reason"] == "model_planned_case_search"


def test_qa_planner_agent_keeps_specific_search_intent_from_model() -> None:
    class PlannerModel:
        def chat(self, *, messages, temperature=0.0, max_tokens=320):
            return {
                "content": '{"intent":"current_info","retrieval_mode":"web_research","should_expand":true,"should_search":true,"search_intent":"entity_relationship","locality":"local_context_first","reason":"relationship_lookup"}',
                "model": "planner-test",
                "usage": {},
            }

    agent = KnowledgeQATaskAgent(use_model=True, model_client=PlannerModel())
    plan = agent.plan(
        AgentRequest(content="A 公司和 B 基金有什么关系", context={"source_mode": "local_plus_external"}),
        {},
        attempt=1,
    )

    assert plan.metadata["planner"]["planner_mode"] == "llm"
    assert plan.metadata["planner"]["search_intent"] == "entity_relationship"


def test_qa_planner_agent_falls_back_when_model_json_is_invalid() -> None:
    class BrokenPlannerModel:
        def chat(self, *, messages, temperature=0.0, max_tokens=320):
            return {"content": "not json", "model": "planner-test", "usage": {}}

    agent = KnowledgeQATaskAgent(use_model=True, model_client=BrokenPlannerModel())
    plan = agent.plan(
        AgentRequest(content="风泉资本是什么背景", context={"source_mode": "local_plus_external"}),
        {},
        attempt=1,
    )

    assert plan.metadata["planner"]["planner_mode"] == "heuristic_fallback"
    assert plan.metadata["planner"]["retrieval_mode"] == "web_research"


def test_heuristic_planner_routes_entity_ownership_questions_to_web_research() -> None:
    agent = KnowledgeQATaskAgent(use_model=False)
    plan = agent._heuristic_plan("风泉资本的股权结构如何", {}, {})

    assert plan["intent"] == "current_info"
    assert plan["retrieval_mode"] == "web_research"
    assert plan["should_search"] is True
    assert plan["search_intent"] == "entity_lookup"
    assert plan["reason"] == "entity_ownership_lookup"


def test_heuristic_planner_routes_entity_followup_questions_to_web_research() -> None:
    agent = KnowledgeQATaskAgent(use_model=False)
    plan = agent._heuristic_plan(
        "他的股权结构是怎样的",
        {},
        {
            "conversation_messages": [
                {"role": "user", "content": "风泉资本是什么背景"},
                {"role": "assistant", "content": "我先给你查风泉资本的背景。"},
            ],
        },
    )

    assert plan["intent"] == "current_info"
    assert plan["retrieval_mode"] == "web_research"
    assert plan["should_search"] is True
    assert plan["search_intent"] == "entity_lookup"
    assert plan["reason"] == "entity_ownership_followup"


def test_route_planner_keeps_explicit_new_topic_out_of_old_followup_context() -> None:
    plan = plan_ai_route(
        "什么是 Lydian mode？",
        state={
            "conversation_messages": [
                {"role": "user", "content": "风泉资本是什么背景？"},
                {"role": "assistant", "content": "我先给你查风泉资本的背景。"},
            ]
        },
    )

    assert plan["intent"] == "concept_clarify"
    assert plan["conversation_resolution"]["is_followup"] is False
    assert plan["conversation_resolution"]["topic_shift"] is True


def test_route_planner_handles_cross_domain_named_product_followup() -> None:
    plan = plan_ai_route(
        "它和 Logic Pro 有什么区别？",
        state={
            "conversation_messages": [
                {"role": "user", "content": "Ableton Live 的 warping 是什么？"},
                {"role": "assistant", "content": "Warping 是 Ableton Live 的时间拉伸机制。"},
            ]
        },
    )

    assert plan["conversation_resolution"]["is_followup"] is True
    assert plan["conversation_resolution"]["focus_type"] in {"named_topic", "topic"}
    assert "Ableton Live" in plan["conversation_resolution"]["resolved_query"]


def test_conversation_resolution_infers_alias_based_entity_followup() -> None:
    resolution = resolve_conversation_turn(
        "风泉的股权结构如何",
        [
            {"role": "user", "content": "风泉资本是什么背景"},
            {"role": "assistant", "content": "我先给你查风泉资本的背景。"},
        ],
    )

    assert resolution["is_followup"] is True
    assert resolution["topic_shift"] is False
    assert resolution["focus_type"] == "entity"
    assert resolution["resolved_focus"] == "风泉资本"
    assert resolution["resolved_query"].startswith("风泉资本")


def test_conversation_resolution_infers_alias_based_named_topic_followup() -> None:
    resolution = resolve_conversation_turn(
        "Ableton 和 Logic Pro 的区别是什么",
        [
            {"role": "user", "content": "Ableton Live 的 warping 是什么？"},
            {"role": "assistant", "content": "Warping 是 Ableton Live 的时间拉伸机制。"},
        ],
    )

    assert resolution["is_followup"] is True
    assert resolution["topic_shift"] is False
    assert resolution["resolved_query"].startswith("Ableton Live")


def test_conversation_resolution_uses_assistant_structure_summary_for_generic_case_search() -> None:
    resolution = resolve_conversation_turn(
        "联网搜索更多利用这种结构的基金案例",
        [
            {"role": "user", "content": "什么是两层结构"},
            {"role": "assistant", "content": "两层结构指基金/SPV下面再设项目公司，并在项目公司层面做优先/劣后股权分层安排。"},
        ],
    )

    assert resolution["is_followup"] is True
    assert resolution["focus_type"] == "structure"
    assert "基金/SPV" in resolution["resolved_query"]
    assert "优先/劣后" in resolution["resolved_query"]
    assert "基金案例" in resolution["resolved_query"]


def test_ai_route_planner_returns_unified_workflow_envelope() -> None:
    plan = plan_ai_route("总结这篇笔记")

    assert plan["route_version"] == "ai-route.v1"
    assert plan["workflow"] == "knowledge_qa"
    assert plan["task_family"] == "qa"
    assert plan["operation"] == "answer_question"
    assert plan["entrypoint"] == "knowledge_qa"
    assert plan["execution_mode"] == "sync"
    assert plan["future_workflows"] == {
        "generate": "note_generation",
        "modify": "note_modification",
        "manage": "knowledge_management",
    }


def test_legacy_qa_route_planner_keeps_backward_compatible_shape() -> None:
    plan = plan_qa_route("总结这篇笔记")

    assert "route_version" not in plan
    assert plan["intent"] == "summary"
    assert plan["retrieval_mode"] == "local_evidence"


def test_qa_search_plan_prefers_chinese_context_for_policy_questions() -> None:
    plan = build_qa_search_plan(
        "请联网查一下最近虚拟电厂政策有什么变化",
        planner={"should_search": True, "intent": "current_info"},
        context={"items": [{"title": "工商业光储+微电网+虚拟电厂协同增效方案"}]},
    )

    assert plan.should_search is True
    assert plan.locality_hint == "china"
    assert plan.language_hint == "zh"
    assert "中国" in plan.plan.original_query


def test_qa_search_plan_does_not_force_search_for_concept_questions() -> None:
    plan = build_qa_search_plan(
        "什么是微电网",
        planner={"should_search": False, "intent": "concept_clarify"},
        context={"items": [{"title": "工商业光储+微电网+虚拟电厂协同增效方案"}]},
    )

    assert plan.should_search is False
    assert plan.plan is None
    assert plan.reason == "planner_default"


def test_qa_search_plan_keeps_english_version_lookup_global() -> None:
    plan = build_qa_search_plan(
        "What is the latest MCP version today?",
        planner={"should_search": True, "intent": "current_info"},
        context={"items": [{"title": "MCP Security"}]},
    )

    assert plan.should_search is True
    assert plan.language_hint == "en"
    assert plan.locality_hint == "global"
    assert "中文" not in plan.plan.original_query
    assert "中国" not in plan.plan.original_query


def test_qa_search_plan_builds_entity_background_queries() -> None:
    plan = build_qa_search_plan(
        "风泉资本是什么背景",
        planner={"should_search": True, "intent": "current_info"},
        context={"items": [{"title": "储能基金两层结构方案"}]},
    )

    assert plan.should_search is True
    assert plan.language_hint == "zh"
    assert plan.plan is not None
    assert plan.plan.intent == "entity_background"
    assert "风泉资本" in plan.plan.required_terms
    assert any("工商" in query or "备案" in query for query in plan.plan.queries)


def test_qa_search_plan_builds_entity_relationship_queries() -> None:
    plan = build_qa_search_plan(
        "风泉和晶科有什么关系",
        planner={"should_search": True, "intent": "current_info", "search_intent": "entity_lookup"},
        context={"items": [{"title": "储能基金两层结构方案"}]},
    )

    assert plan.should_search is True
    assert plan.plan is not None
    assert plan.plan.intent == "entity_relationship"
    assert plan.plan.required_terms == ["风泉", "晶科"]
    assert any("风泉" in query and "晶科" in query for query in plan.plan.queries)


def test_qa_search_plan_cleans_mixed_background_relationship_question() -> None:
    plan = build_qa_search_plan(
        "风泉资本什么背景，和晶科有什么关系",
        planner={"should_search": True, "intent": "current_info", "search_intent": "entity_relationship"},
        context={"items": [{"title": "储能基金两层结构方案"}]},
    )

    assert plan.should_search is True
    assert plan.plan is not None
    assert plan.plan.intent == "entity_relationship"
    assert plan.plan.required_terms == ["风泉资本", "晶科"]
    assert plan.plan.queries[0].startswith("风泉资本 晶科")


def test_qa_search_plan_respects_specific_planner_search_intent() -> None:
    plan = build_qa_search_plan(
        "风泉和晶科有什么关系",
        planner={"should_search": True, "intent": "current_info", "search_intent": "entity_relationship"},
        context={"items": [{"title": "储能基金两层结构方案"}]},
    )

    assert plan.should_search is True
    assert plan.plan is not None
    assert plan.plan.intent == "entity_relationship"


def test_knowledge_qa_verifier_rejects_mechanical_answer() -> None:
    verifier = KnowledgeQAVerifier()

    result = verifier.verify(
        AgentRequest(content="总结"),
        AgentPlan(task_type="qa"),
        (
            ToolResult(tool_id="evidence.build", status="completed", output={"chunks": [{"snippet": "x"}], "sources": [{"title": "A"}]}),
        ),
        "笔记提到这里有很多内容。",
        {},
    )

    assert result.passed is False
    assert result.retryable is True
    assert result.reason == "mechanical_answer"


def test_knowledge_qa_verifier_rejects_invalid_citation_number() -> None:
    verifier = KnowledgeQAVerifier()

    result = verifier.verify(
        AgentRequest(content="总结"),
        AgentPlan(task_type="qa"),
        (
            ToolResult(
                tool_id="evidence.build",
                status="completed",
                output={
                    "chunks": [{"chunk_id": "chunk-1", "snippet": "x", "source_index": 1}],
                    "sources": [{"source_index": 1, "title": "A"}],
                    "citation_map": {"chunk-1": 1},
                },
            ),
        ),
        "答案引用了不存在的来源 [2]。",
        {},
    )

    assert result.passed is False
    assert result.retryable is True
    assert result.reason == "invalid_citation"


def test_knowledge_qa_verifier_ignores_bracket_numbers_inside_urls() -> None:
    verifier = KnowledgeQAVerifier()

    result = verifier.verify(
        AgentRequest(content="联网搜索"),
        AgentPlan(task_type="qa"),
        (
            ToolResult(
                tool_id="evidence.build",
                status="completed",
                output={
                    "chunks": [{"chunk_id": "chunk-1", "snippet": "x", "source_index": 1}],
                    "sources": [{"source_index": 1, "title": "A"}],
                    "citation_map": {"chunk-1": 1},
                },
            ),
        ),
        "来源 URL https://example.test/search?q=issue[2852]，答案引用来源 [1]。",
        {},
    )

    assert result.passed is True
    assert result.checks["invalid_citations"] == []


def test_knowledge_qa_verifier_rejects_inconsistent_evidence_pack() -> None:
    verifier = KnowledgeQAVerifier()

    result = verifier.verify(
        AgentRequest(content="总结"),
        AgentPlan(task_type="qa"),
        (
            ToolResult(
                tool_id="evidence.build",
                status="completed",
                output={
                    "chunks": [{"chunk_id": "bad-chunk", "snippet": "x", "source_index": 2}],
                    "sources": [{"source_index": 1, "title": "A"}],
                    "citation_map": {"bad-chunk": 2},
                },
            ),
        ),
        "这是一个回答。\n\n来源：[1] A",
        {},
    )

    assert result.passed is False
    assert result.retryable is True
    assert result.reason == "evidence_inconsistent"
    assert result.checks["evidence_consistency"]["valid"] is False


def test_qa_runtime_comparison_can_run_agent_side_without_legacy(tmp_path) -> None:
    service = item_service(tmp_path)
    settings = service.settings
    model_client = ModelClient(AIProviderConfig(provider="fake", enabled=True, model="fake-model"))
    conversation_store = InMemoryEvalConversationStore(service, max_context_items=5)

    report = compare_qa_runtimes(
        question="总结这篇笔记",
        context={"item_id": "a.html"},
        item_service=service,
        conversation_store=conversation_store,
        model_client=model_client,
        settings=settings,
        run_legacy=False,
        run_agent=True,
        agent_uses_model=False,
    )

    assert report["kind"] == "qa_runtime_comparison"
    assert set(report["results"]) == {"agent"}
    assert report["results"]["agent"]["engine"] == "AgentRuntime.qa.v1"
    assert report["results"]["agent"]["status"] == "completed"
    assert report["results"]["agent"]["source_count"] == 1
    assert report["results"]["agent"]["sources"][0]["title"] == "Alpha MCP"
    assert report["metrics"]["agent"]["status"] == "ok"


def test_qa_runtime_comparison_langgraph_engine_is_explicit(tmp_path) -> None:
    service = item_service(tmp_path)
    settings = service.settings
    model_client = ModelClient(AIProviderConfig(provider="fake", enabled=True, model="fake-model"))
    conversation_store = InMemoryEvalConversationStore(service, max_context_items=5)

    if not langgraph_available():
        with pytest.raises(Exception, match="LangGraph is not installed"):
            compare_qa_runtimes(
                question="总结这篇笔记",
                context={"item_id": "a.html"},
                item_service=service,
                conversation_store=conversation_store,
                model_client=model_client,
                settings=settings,
                run_legacy=False,
                run_agent=False,
                run_langgraph=True,
                agent_uses_model=False,
            )
        return

    report = compare_qa_runtimes(
        question="总结这篇笔记",
        context={"item_id": "a.html"},
        item_service=service,
        conversation_store=conversation_store,
        model_client=model_client,
        settings=settings,
        run_legacy=False,
        run_agent=False,
        run_langgraph=True,
        agent_uses_model=False,
    )

    assert set(report["results"]) == {"langgraph"}
    assert report["results"]["langgraph"]["engine"] == "LangGraphKnowledgeQA.v1"
    assert report["results"]["langgraph"]["status"] == "completed"
    assert report["results"]["langgraph"]["source_count"] == 1


def test_qa_eval_metrics_flag_duplicate_sources_and_mechanical_phrasing() -> None:
    metrics = evaluate_qa_result(
        {
            "status": "completed",
            "answer": "笔记提到这里有内容。",
            "sources": [
                {"kind": "local", "item_id": "a.html", "title": "Alpha"},
                {"kind": "local", "item_id": "a.html", "title": "Alpha"},
            ],
            "citation": {"status": "valid"},
        },
    )

    assert metrics["status"] == "needs_attention"
    assert metrics["requires_attention"] is True
    assert "mechanical_phrasing" in metrics["flags"]
    assert "duplicate_sources" in metrics["flags"]
    assert metrics["duplicate_sources"]["duplicate_count"] == 1


def test_qa_eval_metrics_flag_weak_source_relevance() -> None:
    metrics = evaluate_qa_result(
        {
            "status": "completed",
            "answer": "这里给出一个弱相关回答。",
            "sources": [{"kind": "local", "item_id": "docker.html", "title": "Docker Network Quick Notes"}],
            "citation": {"status": "valid"},
        },
        question="Write a travel plan for Kyoto.",
    )

    assert metrics["status"] == "needs_attention"
    assert "weak_relevance" in metrics["flags"]
    assert metrics["source_relevance"]["status"] == "weak"


def test_qa_eval_metrics_accept_related_source_title_overlap() -> None:
    metrics = evaluate_qa_result(
        {
            "status": "completed",
            "answer": "Docker networking uses bridge networks.",
            "sources": [{"kind": "local", "item_id": "docker.html", "title": "Docker Network Quick Notes"}],
            "citation": {"status": "valid"},
        },
        question="Explain Docker networking.",
    )

    assert metrics["status"] == "ok"
    assert "weak_relevance" not in metrics["flags"]
    assert metrics["source_relevance"]["overlap"] == ["docker"]


def test_qa_eval_metrics_skip_generic_summary_relevance() -> None:
    metrics = evaluate_qa_result(
        {
            "status": "completed",
            "answer": "这是摘要。",
            "sources": [{"kind": "local", "item_id": "a.html", "title": "Alpha MCP"}],
            "citation": {"status": "valid"},
        },
        question="总结这篇笔记",
    )

    assert metrics["status"] == "ok"
    assert metrics["source_relevance"]["evaluated"] is False


def test_qa_eval_metrics_skip_global_overview_relevance() -> None:
    metrics = evaluate_qa_result(
        {
            "status": "completed",
            "answer": "This is a global overview.",
            "sources": [{"kind": "local", "item_id": "workspace.html", "title": "Knowledge Workspace Design Notes"}],
            "citation": {"status": "valid"},
        },
        question="Summarize the current knowledge base and group the answer by topic.",
    )

    assert metrics["status"] == "ok"
    assert metrics["source_relevance"]["status"] == "overview"
