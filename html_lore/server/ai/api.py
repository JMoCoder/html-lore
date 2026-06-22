from __future__ import annotations

from typing import Any

from html_lore.server.config import ServerSettings
from html_lore.server.items import ItemService

from .context import AIContextError, ContextResolver, normalize_source_mode
from .conversations import ConversationError, ConversationStore
from .external_search import build_external_search_adapter
from .guardrails import GuardrailError
from .html_generation import GenerationSpec, HtmlGenerationError, generate_note_from_conversation
from .jobs import AIJobError, AIJobStore, ai_job_queue
from .material_generation import MaterialGenerationError, generate_note_from_material
from .generation_v2.fake_model import FakeGenerationModelClient
from .generation_v2.material_runner import generate_note_from_material_v2
from .generation_v2.model_client import build_provider_generation_client
from .model_client import ModelClient, test_provider
from .providers import AIProviderConfigError, AIProviderConfigStore, ProviderCallError
from .runs import AIRunError, AIRunStore
from .runtime import AgentRequest, AgentRuntimeError
from .langgraph_qa import LangGraphKnowledgeQARuntime, langgraph_available
from .runtime_eval import build_selected_qa_runtime, build_qa_agent_runtime, compare_qa_runtimes, public_agent_run
from .vector_maintenance import VectorMaintenanceError, vector_maintenance_for_config


class AIService:
    def __init__(self, store: AIProviderConfigStore, settings: ServerSettings) -> None:
        self.store = store
        self.settings = settings

    def provider(self) -> dict[str, Any]:
        return {"provider": self.store.get().public_dict()}

    def update_provider(self, values: dict[str, Any]) -> dict[str, Any]:
        config = self.store.update(values)
        return {"provider": config.public_dict()}

    def status(self) -> dict[str, Any]:
        config = self.store.get()
        client_status = ModelClient(config).status()
        external_search = build_external_search_adapter(self.settings)
        external_status = {
            "provider": external_search.name,
            "available": bool(external_search.available),
            "max_results": max(1, int(getattr(external_search, "max_results", self.settings.ai_external_search_max_results) or 5)),
        }
        if hasattr(external_search, "adapters"):
            external_status["chain"] = [str(getattr(adapter, "name", "") or "") for adapter in getattr(external_search, "adapters") if getattr(adapter, "name", "")]
        return {
            "configured": config.configured,
            "available": bool(client_status["available"]),
            "message": client_status["message"],
            "provider": config.public_dict(),
            "qa_engine": qa_engine_status(self.settings.ai_qa_engine),
            "external_search_available": external_status["available"],
            "external_search": external_status,
        }

    def test_provider(self) -> dict[str, Any]:
        config = self.store.get()
        return test_provider(config)

    def vector_index_stats(self) -> dict[str, Any]:
        return vector_maintenance_for_config(ItemService(self.settings), self.store.get()).stats()

    def prune_vector_index(self) -> dict[str, Any]:
        return vector_maintenance_for_config(ItemService(self.settings), self.store.get()).prune()

    def clear_vector_index(self) -> dict[str, Any]:
        return vector_maintenance_for_config(ItemService(self.settings), self.store.get()).clear()

    def rebuild_vector_index(self) -> dict[str, Any]:
        return vector_maintenance_for_config(ItemService(self.settings), self.store.get()).rebuild()

    def smoke_test_embedding(self) -> dict[str, Any]:
        return vector_maintenance_for_config(ItemService(self.settings), self.store.get()).smoke_test_embedding()


class AIConversationService:
    def __init__(
        self,
        settings: ServerSettings,
        store: ConversationStore,
        item_service: ItemService,
        provider_store: AIProviderConfigStore,
        run_store: AIRunStore,
    ) -> None:
        self.settings = settings
        self.store = store
        self.item_service = item_service
        self.provider_store = provider_store
        self.run_store = run_store

    def resolve_context(self, values: dict[str, Any]) -> dict[str, Any]:
        return {"context": ContextResolver(self.item_service, max_context_items=self.settings.ai_max_context_items).resolve(values)}

    def create(self, values: dict[str, Any]) -> dict[str, Any]:
        return {"conversation": self.store.create(values)}

    def list(self, *, context_key: str = "", limit: int = 100) -> dict[str, Any]:
        conversations = self.store.list(context_key=context_key, limit=limit)
        return {"conversations": conversations, "count": len(conversations)}

    def latest(self, context_key: str) -> dict[str, Any]:
        return {"conversation": self.store.latest_for_context(context_key)}

    def get(self, conversation_id: str) -> dict[str, Any]:
        return {"conversation": self.store.get(conversation_id)}

    def delete(self, conversation_id: str) -> dict[str, Any]:
        return self.store.delete(conversation_id)

    def messages(self, conversation_id: str) -> dict[str, Any]:
        messages = self.store.list_messages(conversation_id)
        return {"messages": messages, "count": len(messages)}

    def add_message(self, conversation_id: str, values: dict[str, Any]) -> dict[str, Any]:
        content = str(values.get("content") or values.get("message") or "").strip()
        conversation = self.store.get(conversation_id)
        if "source_mode" in values:
            snapshot = dict(conversation.get("context_snapshot") if isinstance(conversation.get("context_snapshot"), dict) else {})
            snapshot["source_mode"] = normalize_source_mode(values.get("source_mode"))
            conversation = dict(conversation)
            conversation["source_mode"] = snapshot["source_mode"]
            conversation["context_snapshot"] = snapshot
        engine = configured_qa_engine_name(self.settings.ai_qa_engine)
        try:
            runtime, engine = build_selected_qa_runtime(
                item_service=self.item_service,
                model_client=ModelClient(self.provider_store.get()),
                settings=self.settings,
                use_model=True,
            )
            result = runtime.run(AgentRequest(content=content, context=agent_request_context(conversation), requested_task="qa"))
        except GuardrailError as exc:
            self.run_store.add(
                failed_agent_qa_run(
                    conversation_id=conversation_id,
                    code="guardrail_failed",
                    message=str(exc),
                    budget=budget_from_error(str(exc)),
                    engine=engine,
                ),
            )
            raise
        except (AIProviderConfigError, ProviderCallError) as exc:
            self.run_store.add(failed_agent_qa_run(conversation_id=conversation_id, code="provider_failed", message=str(exc), engine=engine))
            raise ConversationError(str(exc)) from exc
        except AgentRuntimeError as exc:
            self.run_store.add(failed_agent_qa_run(conversation_id=conversation_id, code="runtime_failed", message=str(exc), engine=engine))
            raise ConversationError(str(exc)) from exc
        run = public_agent_run(result, conversation_id=conversation_id, engine=engine)
        self.run_store.add(run)
        sources = run["qa_report"].get("sources") if isinstance(run["qa_report"].get("sources"), list) else []
        stored_conversation = self.store.append_messages(
            conversation_id,
            [
                {"role": "user", "content": content, "sources": []},
                {"role": "assistant", "content": result.answer, "sources": sources},
            ],
        )
        return {
            "conversation": stored_conversation,
            "message": stored_conversation["messages"][-1],
            "sources": sources,
            "usage": run["usage"],
            "graph": engine,
            "node_trace": run["node_trace"],
            "external_status": run["qa_report"].get("external_status") or {},
            "retrieval_status": run["qa_report"].get("retrieval") or {},
            "qa_status": qa_status_from_report(run["qa_report"]),
            "qa_report": run["qa_report"],
        }

    def generate_note(self, conversation_id: str, values: dict[str, Any]) -> dict[str, Any]:
        conversation = self.store.get(conversation_id)
        spec = GenerationSpec.from_values(values)
        try:
            result = generate_note_from_conversation(settings=self.settings, conversation=conversation, spec=spec)
        except HtmlGenerationError as exc:
            self._store_failed_run(exc)
            raise
        run = self.run_store.add(result["run"])
        return {"run": run, "item": result["item"]}

    def enqueue_generate_note(self, conversation_id: str, values: dict[str, Any]) -> dict[str, Any]:
        conversation = self.store.get(conversation_id)
        spec = GenerationSpec.from_values(values)
        store = AIJobStore(self.settings)
        job = store.create(
            kind="html_generation",
            label=f"Generate note from conversation {conversation_id[:12]}",
            payload={"type": "conversation_html_generation", "conversation_id": conversation_id, "spec": spec.as_dict()},
        )
        ai_job_queue.enqueue(settings=self.settings, job=job, task=self._conversation_generation_task(conversation_id, spec.as_dict()))
        return {"job": job, "job_id": job["job_id"]}

    def generate_note_from_material(self, *, filename: str, content: bytes, instruction: str, values: dict[str, Any]) -> dict[str, Any]:
        spec = GenerationSpec.from_values(values)
        try:
            if self.settings.ai_generation_engine == "v2":
                result = generate_note_from_material_v2(
                    settings=self.settings,
                    filename=filename,
                    content=content,
                    instruction=instruction,
                    spec=spec,
                    reference_content=values.get("reference_file_content") if isinstance(values.get("reference_file_content"), bytes) else b"",
                    model_client=self._generation_v2_model_client(),
                )
            else:
                result = generate_note_from_material(
                    settings=self.settings,
                    filename=filename,
                    content=content,
                    instruction=instruction,
                    spec=spec,
                )
        except (HtmlGenerationError, MaterialGenerationError) as exc:
            self._store_failed_run(exc)
            raise
        run = self.run_store.add(result["run"])
        return {"run": run, "item": result["item"]}

    def enqueue_generate_note_from_material(self, *, filename: str, content: bytes, instruction: str, values: dict[str, Any]) -> dict[str, Any]:
        spec = GenerationSpec.from_values(values)
        store = AIJobStore(self.settings)
        payload = {
            "type": "material_html_generation",
            "filename": filename,
            "spec": spec.as_dict(),
            "engine": self.settings.ai_generation_engine,
        }
        if self.settings.ai_generation_engine == "v2":
            from .generation_v2.schemas import GenerationEngine, GenerationStage

            from .generation_v2.store import GenerationStore

            job = GenerationStore(self.settings).create_job(kind="material_html_generation", label=filename or "Uploaded material", payload=payload, current_stage=GenerationStage.QUEUED)
        else:
            job = store.create(kind="material_html_generation", label=filename or "Uploaded material", payload=payload)

        def task() -> dict[str, Any]:
            try:
                if self.settings.ai_generation_engine == "v2":
                    generation_store = GenerationStore(self.settings)

                    def sync_v2_state(state) -> None:
                        generation_store.jobs.update(str(job["job_id"]), generation_store.public_state_summary(state))

                    result = generate_note_from_material_v2(
                        settings=self.settings,
                        filename=filename,
                        content=content,
                        instruction=instruction,
                        spec=spec,
                        reference_content=values.get("reference_file_content") if isinstance(values.get("reference_file_content"), bytes) else b"",
                        model_client=self._generation_v2_model_client(),
                        job_id=str(job["job_id"]),
                        on_state=sync_v2_state,
                    )
                else:
                    result = generate_note_from_material(
                        settings=self.settings,
                        filename=filename,
                        content=content,
                        instruction=instruction,
                        spec=spec,
                    )
            except (HtmlGenerationError, MaterialGenerationError) as exc:
                self._store_failed_run(exc)
                raise
            run = self.run_store.add(result["run"])
            return {"run": run, "item": result["item"]}

        ai_job_queue.enqueue(settings=self.settings, job=job, task=task)
        return {"job": job, "job_id": job["job_id"]}

    def runs(self, limit: int = 20) -> dict[str, Any]:
        runs = self.run_store.list(limit=limit)
        return {"runs": runs, "count": len(runs)}

    def run(self, run_id: str) -> dict[str, Any]:
        return {"run": self.run_store.get(run_id)}

    def compare_qa_runtimes(self, values: dict[str, Any]) -> dict[str, Any]:
        if values.get("enabled") is not True:
            raise ConversationError("Runtime comparison is a development tool. Pass enabled=true to run it.")
        question = str(values.get("question") or values.get("content") or "").strip()
        if not question:
            raise ConversationError("Question is required.")
        context = values.get("context") if isinstance(values.get("context"), dict) else {}
        return compare_qa_runtimes(
            question=question,
            context=context,
            item_service=self.item_service,
            conversation_store=self.store,
            model_client=ModelClient(self.provider_store.get()),
            settings=self.settings,
            run_legacy=bool(values.get("run_legacy", values.get("runLegacy", True))),
            run_agent=bool(values.get("run_agent", values.get("runAgent", True))),
            run_langgraph=bool(values.get("run_langgraph", values.get("runLanggraph", False))),
            agent_uses_model=bool(values.get("agent_uses_model", values.get("agentUsesModel", True))),
        )

    def run_agent_qa_once(self, values: dict[str, Any]) -> dict[str, Any]:
        if values.get("enabled") is not True:
            raise ConversationError("Agent QA run is a development tool. Pass enabled=true to run it.")
        question = str(values.get("question") or values.get("content") or "").strip()
        if not question:
            raise ConversationError("Question is required.")
        context = values.get("context") if isinstance(values.get("context"), dict) else {}
        runtime = build_qa_agent_runtime(
            item_service=self.item_service,
            model_client=ModelClient(self.provider_store.get()),
            settings=self.settings,
            use_model=bool(values.get("use_model", values.get("useModel", True))),
        )
        result = runtime.run(AgentRequest(content=question, context=context, requested_task="qa"))
        run = self.run_store.add(public_agent_run(result))
        return {"run": run, "answer": result.answer}

    def jobs(self, limit: int = 20) -> dict[str, Any]:
        jobs = AIJobStore(self.settings).list(limit=limit)
        return {"jobs": jobs, "count": len(jobs)}

    def job(self, job_id: str) -> dict[str, Any]:
        return {"job": AIJobStore(self.settings).get(job_id)}

    def cancel_job(self, job_id: str) -> dict[str, Any]:
        return {"job": AIJobStore(self.settings).cancel(job_id)}

    def retry_job(self, job_id: str) -> dict[str, Any]:
        store = AIJobStore(self.settings)
        job = store.get(job_id, include_private=True)
        if job.get("status") != "failed":
            raise AIJobError("Only failed AI jobs can be retried.")
        payload = job.get("payload") if isinstance(job.get("payload"), dict) else {}
        if str(payload.get("type") or "") != "conversation_html_generation":
            raise AIJobError("This AI job cannot be retried.")
        conversation_id = str(payload.get("conversation_id") or "").strip()
        spec_values = payload.get("spec") if isinstance(payload.get("spec"), dict) else {}
        spec = GenerationSpec.from_values(spec_values)
        self.store.get(conversation_id)
        retried = store.update(
            job_id,
            {
                "status": "pending",
                "started_at": "",
                "completed_at": "",
                "message": "AI job queued for retry.",
                "run_id": "",
                "item_id": "",
                "error": {},
                "cancel_requested": False,
                "attempts": int(job.get("attempts") or 0) + 1,
            },
        )
        ai_job_queue.enqueue(settings=self.settings, job=retried, task=self._conversation_generation_task(conversation_id, spec.as_dict()))
        return {"job": retried, "job_id": retried["job_id"]}

    def _conversation_generation_task(self, conversation_id: str, spec_values: dict[str, Any]):
        def task() -> dict[str, Any]:
            conversation = self.store.get(conversation_id)
            spec = GenerationSpec.from_values(spec_values)
            try:
                result = generate_note_from_conversation(settings=self.settings, conversation=conversation, spec=spec)
            except HtmlGenerationError as exc:
                self._store_failed_run(exc)
                raise
            run = self.run_store.add(result["run"])
            return {"run": run, "item": result["item"]}

        return task

    def _store_failed_run(self, exc: Exception) -> None:
        run = getattr(exc, "run", None)
        if isinstance(run, dict) and run:
            self.run_store.add(run)

    def _generation_v2_model_client(self):
        from dataclasses import replace

        base_config = self.provider_store.get()
        config = replace(base_config, model=self.settings.ai_generation_model or base_config.model)
        if config.provider == "fake":
            return FakeGenerationModelClient()
        return build_provider_generation_client(
            ModelClient(config),
            max_prompt_chars=self.settings.ai_max_prompt_chars,
            max_tokens=max(self.settings.ai_max_response_tokens, 4096),
        )


def qa_status_from_report(report: dict[str, Any]) -> dict[str, Any]:
    citation = report.get("citation") if isinstance(report.get("citation"), dict) else {}
    quality = report.get("answer_quality") if isinstance(report.get("answer_quality"), dict) else {}
    external = report.get("external_status") if isinstance(report.get("external_status"), dict) else {}
    coverage = report.get("evidence_coverage") if isinstance(report.get("evidence_coverage"), dict) else {}
    flags = [str(flag) for flag in quality.get("flags") or [] if str(flag)]
    external_unavailable = bool(external.get("message") and not external.get("queried"))
    if external_unavailable:
        flags.append("external_unavailable")
    if not external_unavailable and str(coverage.get("status") or "") in {"partial", "no_local_evidence"}:
        flags.append("partial_context_coverage")
    flags = list(dict.fromkeys(flags))
    return {
        "status": str(quality.get("status") or "unknown"),
        "requires_attention": bool(quality.get("requires_attention") or flags),
        "flags": flags,
        "citation_status": str(citation.get("status") or citation.get("reason") or ""),
        "source_count": int(report.get("source_count") or 0),
    }


def configured_qa_engine_name(value: str) -> str:
    engine = str(value or "").strip().lower()
    if engine in {"auto", "langgraph"}:
        return LangGraphKnowledgeQARuntime.name
    return "AgentRuntime.qa.v1"


def qa_engine_status(value: str) -> dict[str, Any]:
    configured = str(value or "auto").strip().lower() or "auto"
    available = langgraph_available()
    if configured == "agent_runtime":
        effective = "AgentRuntime.qa.v1"
    elif configured == "auto" and not available:
        effective = "AgentRuntime.qa.v1"
    else:
        effective = LangGraphKnowledgeQARuntime.name
    return {
        "configured": configured,
        "effective": effective,
        "langgraph_available": available,
        "fallback": configured == "auto" and effective == "AgentRuntime.qa.v1",
    }


def agent_request_context(conversation: dict[str, Any]) -> dict[str, Any]:
    snapshot = conversation.get("context_snapshot") if isinstance(conversation.get("context_snapshot"), dict) else {}
    requested = snapshot.get("requested") if isinstance(snapshot.get("requested"), dict) else {}
    scope = str(snapshot.get("scope") or requested.get("scope") or "global")
    item_ids = [str(item_id) for item_id in snapshot.get("item_ids") or [] if str(item_id)]
    context: dict[str, Any] = {"scope": scope}
    if scope == "reader":
        context["item_id"] = str(requested.get("item_id") or (item_ids[0] if item_ids else ""))
    elif scope == "manual":
        context["manual_item_ids"] = list(requested.get("manual_item_ids") or item_ids)
    else:
        for key in ("q", "library", "collection", "tags", "tag_match", "favorite", "include_archived", "sort", "limit"):
            if key in requested:
                context[key] = requested[key]
    if snapshot.get("source_mode"):
        context["source_mode"] = snapshot["source_mode"]
    if isinstance(conversation.get("messages"), list):
        context["_conversation_messages"] = list(conversation.get("messages") or [])
    return context


def failed_agent_qa_run(*, conversation_id: str, code: str, message: str, budget: dict[str, int] | None = None, engine: str = "AgentRuntime.qa.v1") -> dict[str, Any]:
    from datetime import datetime, timezone
    import uuid

    now = datetime.now(timezone.utc).isoformat()
    return {
        "id": f"qa_agent_{uuid.uuid4().hex}",
        "kind": "knowledge_qa",
        "status": "failed",
        "started_at": now,
        "completed_at": now,
        "duration_ms": 0,
        "conversation_id": conversation_id,
        "spec": {"engine": engine},
        "graph": engine,
        "generation_intent": {},
        "qa_report": {
            "source_count": 0,
            "local_source_count": 0,
            "external_source_count": 0,
            "skipped_model_call": True,
            "retrieval": {},
            "external_status": {},
            "research_trace": [],
            "expansion_policy": {},
            "evidence_scope": {},
            "evidence_ranking": {},
            "evidence_rerank": {},
            "evidence_budget": {},
            "evidence_coverage": {},
            "evidence_sufficiency": {},
            "citation": {},
            "answer_quality": {"status": "needs_attention", "requires_attention": True, "flags": [code]},
            "sources": [],
        },
        "review_decision": {},
        "node_trace": [],
        "agent_trace": [],
        "prompt_trace": [],
        "skill_trace": [],
        "usage": {},
        "budget": budget or {},
        "error": {"code": code, "message": message},
        "material": {},
        "item_id": "",
        "retryable": code == "provider_failed",
        "cancellable": False,
    }


def budget_from_error(message: str) -> dict[str, int]:
    import re

    match = re.search(r"\((\d+) characters, limit (\d+)\)", str(message or ""))
    if not match:
        return {}
    return {"prompt_chars": int(match.group(1)), "max_prompt_chars": int(match.group(2))}


__all__ = [
    "AIContextError",
    "AIConversationService",
    "AIProviderConfigError",
    "AIProviderConfigStore",
    "AIService",
    "ConversationError",
    "ConversationStore",
    "GuardrailError",
    "HtmlGenerationError",
    "MaterialGenerationError",
    "AIRunError",
    "AIRunStore",
    "AIJobError",
    "VectorMaintenanceError",
]
