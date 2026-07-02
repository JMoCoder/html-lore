from __future__ import annotations

import json
import os
import time
from dataclasses import fields
from pathlib import Path

from html_lore.server.ai.generation_v2.agents.requirement_analyst import RequirementAnalystAgent
from html_lore.server.ai.generation_v2.agents.html_coder import HTMLCoderAgent
from html_lore.server.ai.generation_v2.agents.content_writer import ContentWriterAgent
from html_lore.server.ai.generation_v2.agents.verifier import VerifierAgent
from html_lore.server.ai.generation_v2.graph import HtmlGenerationV2Graph, merge_parsed_documents
from html_lore.server.ai.generation_v2.fake_model import FakeGenerationModelClient
from html_lore.server.ai.generation_v2.material_context import build_material_index, build_temporary_material_context, recall_material
from html_lore.server.ai.generation_v2.material_runner import generate_note_from_material_v2
from html_lore.server.ai.generation_v2.material_bundle import build_material_bundle, cleanup_expired_failed_job_workspaces, write_job_material_bundle, read_material_bundle_reference
from html_lore.server.ai.generation_v2.material_read import read_material
from html_lore.server.ai.generation_v2.model_client import ProviderGenerationModelClient, agent_payload, extract_html_document, extract_json_object, public_generation_state_for_agent, retry_output_rules
from html_lore.server.ai.generation_v2.model_profile import DEFAULT_GENERATION_MODEL, GenerationModelProfile
from html_lore.server.ai.generation_v2.orchestrator import GenerationOrchestrator
from html_lore.server.ai.generation_v2.schema_loader import AgentOutputSchemaError, dataclass_from_dict
from html_lore.server.ai.generation_v2.schemas import ChecklistItem, ChecklistStatus, ContentDraft, ContentSection, CreateNoteProposal, DesignMode, DocumentImage, DocumentLink, DocumentTable, GenerationInput, GenerationJobStatus, GenerationStage, GenerationState, HtmlDraft, MaterialQuery, MaterialReadRequest, NoteMetadataProposal, OutlineItem, ParsedDocument, PlanDraft, RequirementBrief, SourceFile, SkillTraceEntry, StageTraceEvent, StyleBrief, ToolNeed, ValidationReport
from html_lore.server.ai.generation_v2.skill_router import planned_skill_ids_for_agent, resolve_skills_for_agent
from html_lore.server.ai.generation_v2.skills.loader import iter_skill_registry_items, load_default_skills_for_agent, load_skill_by_id
from html_lore.server.ai.generation_v2.state import complete_stage, start_stage
from html_lore.server.ai.generation_v2.store import GenerationStore
from html_lore.server.ai.api import AIConversationService, sync_v2_job_from_run
from html_lore.server.ai.generation_v2.tools import document_parser
from html_lore.server.ai.generation_v2.tools.document_parser import parse_document, parse_document_basic
from html_lore.server.ai.generation_v2.tools.html_safety import scan_html_safety
from html_lore.server.ai.generation_v2.tools.style_hint_extractor import extract_style_hints
from html_lore.server.ai.generation_v2.tools.visual_check import run_visual_check
from html_lore.server.ai.generation_v2.write_gateway import WriteGateway, WriteGatewayError
from html_lore.server.ai.html_generation import GenerationSpec
from html_lore.server.ai.jobs import AIJobStore
from html_lore.server.ai.material_generation import MaterialGenerationError
from html_lore.server.ai.providers import AIProviderConfig
from html_lore.server.ai.runs import AIRunStore
from html_lore.server.config import ServerSettings, load_settings


def test_generation_v2_state_serializes_enums() -> None:
    state = GenerationState(job_id="job-1", input=GenerationInput(instruction="Create a note."))
    state = start_stage(state, GenerationStage.PARSING, agent="Ingest", message="Parsing")
    state = complete_stage(state, GenerationStage.PARSING, message="Parsed")

    data = state.as_dict()

    assert data["job_id"] == "job-1"
    assert data["stage_trace"][0]["stage"] == "parsing"
    assert data["stage_trace"][0]["status"] == "completed"
    assert data["stage_trace"][0]["duration_ms"] >= 0
    assert data["completed_steps"] == ["parsing"]


def test_generation_v2_graph_initial_state_uses_input() -> None:
    generation_input = GenerationInput(filename="source.md", instruction="Create HTML.")
    state = HtmlGenerationV2Graph().initial_state(generation_input, job_id="job-1")

    assert state.job_id == "job-1"
    assert state.run_id
    assert state.input.filename == "source.md"


def test_generation_v2_graph_runs_fake_agent_flow() -> None:
    graph = HtmlGenerationV2Graph(parser_mode="basic")
    state = graph.initial_state(
        GenerationInput(
            filename="source.md",
            content=b"# Microgrid Plan\n\nUse storage and demand response.",
            content_type="text/markdown",
            instruction="Create a concise HTML note.",
        ),
        job_id="job-1",
    )

    result = graph.run(state)

    assert not result.failed_steps
    assert result.parsed_document is not None
    assert result.material_index is not None
    assert result.material_recall_results
    assert {recall.agent for recall in result.material_recall_results} >= {"RequirementAnalyst", "ContentWriter", "Verifier"}
    assert result.requirement_brief is not None
    assert result.requirement_brief.material_queries == []
    assert result.plan_draft is not None
    assert "material_queries" not in {field.name for field in fields(PlanDraft)}
    assert result.content_draft is not None
    assert result.content_draft.material_queries == []
    assert result.style_brief is not None
    assert result.html_draft is not None
    assert result.validation_report is not None and result.validation_report.ok
    assert result.validation_report.material_queries == []
    assert result.safety_report is not None and result.safety_report.ok
    assert result.create_note_proposal is not None
    assert result.create_note_proposal.target_collection == "inbox"
    assert "<!doctype html>" in result.create_note_proposal.html
    assert result.create_note_proposal.html == result.html_draft.html
    assert "finalizing" in result.completed_steps
    assert [artifact.agent for artifact in result.agent_artifacts] == [
        "RequirementAnalyst",
        "Planner",
        "ContentWriter",
        "StyleDesigner",
        "HTMLCoder",
        "Verifier",
        "SafetyReviewer",
        "Finalizer",
    ]
    html_artifact = next(artifact for artifact in result.agent_artifacts if artifact.agent == "HTMLCoder")
    assert html_artifact.data["html_chars"] == len(result.html_draft.html)
    assert "html" not in html_artifact.data
    assert html_artifact.quality_score > 0
    requirement_artifact = next(artifact for artifact in result.agent_artifacts if artifact.agent == "RequirementAnalyst")
    assert requirement_artifact.data["material_status"]["selected_covers_full_text"] is True
    writer_artifact = next(artifact for artifact in result.agent_artifacts if artifact.agent == "ContentWriter")
    assert writer_artifact.data["material_status"]["total_chars"] > 0
    verifier_artifact = next(artifact for artifact in result.agent_artifacts if artifact.agent == "Verifier")
    assert "selected_covers_full_text" in verifier_artifact.data["material_status"]
    planner_artifact = next(artifact for artifact in result.agent_artifacts if artifact.agent == "Planner")
    assert planner_artifact.data["section_plan"]
    assert planner_artifact.quality_score > 0
    html_trace = next(event for event in result.stage_trace if event.agent == "HTMLCoder" and event.status == "completed")
    assert html_trace.duration_ms >= 0
    assert html_trace.metadata["output_kind"] == "html"
    assert html_trace.metadata["output_chars"] == len(result.html_draft.html)
    checklist_status = {item.owner: item.status for item in result.execution_checklist}
    assert checklist_status["ContentWriter"] == ChecklistStatus.COMPLETED
    assert checklist_status["StyleDesigner"] == ChecklistStatus.COMPLETED
    assert checklist_status["HTMLCoder"] == ChecklistStatus.COMPLETED
    assert checklist_status["Verifier"] == ChecklistStatus.COMPLETED
    assert [(item.agent, item.id) for item in result.skill_trace] == [
        ("StyleDesigner", "html_page_design"),
        ("HTMLCoder", "safe_static_html"),
        ("Verifier", "content_quality_review"),
    ]
    assert result.visual_check_report is not None
    assert result.visual_check_report.skipped is True


def test_generation_v2_graph_can_run_optional_visual_check_without_breaking_flow() -> None:
    graph = HtmlGenerationV2Graph(parser_mode="basic", visual_check_mode="basic", visual_check_timeout_seconds=5)
    state = graph.initial_state(
        GenerationInput(
            filename="source.md",
            content=b"# Source\n\nBody.",
            content_type="text/markdown",
            instruction="Create HTML.",
        ),
        job_id="job-visual",
    )

    result = graph.run(state)

    assert not result.failed_steps
    assert result.visual_check_report is not None
    assert result.visual_check_report.mode == "basic"
    visual_artifact = next(artifact for artifact in result.agent_artifacts if artifact.agent == "VisualCheckTool")
    assert visual_artifact.data["mode"] == "basic"
    if result.visual_check_report.skipped:
        assert result.visual_check_report.reason
    else:
        assert result.visual_check_report.viewports


def test_generation_v2_graph_emits_active_stage_before_agent_completes() -> None:
    snapshots: list[GenerationState] = []
    graph = HtmlGenerationV2Graph(parser_mode="basic", on_state=snapshots.append)
    state = graph.initial_state(
        GenerationInput(
            filename="source.md",
            content=b"# Source\n\nBody.",
            content_type="text/markdown",
            instruction="Create HTML.",
        ),
        job_id="job-1",
    )

    graph.run(state)

    assert any(
        snapshot.current_step == GenerationStage.ANALYZING_REQUIREMENTS.value
        and not any(event.agent == "RequirementAnalyst" for event in snapshot.stage_trace)
        for snapshot in snapshots
    )


def test_generation_v2_skill_loader_uses_fixed_default_mapping() -> None:
    assert [skill.id for skill in load_default_skills_for_agent("StyleDesigner")] == ["html_page_design"]
    assert [skill.id for skill in load_default_skills_for_agent("HTMLCoder")] == ["safe_static_html"]
    assert [skill.id for skill in load_default_skills_for_agent("Verifier")] == ["content_quality_review"]
    assert load_default_skills_for_agent("Planner") == ()


def test_generation_v2_skill_loader_uses_frontmatter_metadata_and_strips_it() -> None:
    skill = load_skill_by_id("html_page_design")

    assert skill.title == "HTML page design"
    assert skill.description.startswith("Use when designing readable static HTML")
    assert skill.version == "0.2.0"
    assert skill.license == "project-internal"
    assert skill.content.startswith("# HTML Page Design Skill")
    assert not skill.content.startswith("---")

    registry_items = {item.id: item for item in iter_skill_registry_items()}
    assert registry_items["html_page_design"].version == "0.2.0"
    assert registry_items["safe_static_html"].title == "Safe static HTML"
    assert registry_items["content_quality_review"].description.startswith("Use when verifying")


def test_generation_v2_default_skill_smoke_evals_cover_expected_contracts() -> None:
    design = load_skill_by_id("html_page_design").content
    safe_html = load_skill_by_id("safe_static_html").content
    review = load_skill_by_id("content_quality_review").content
    presentation = load_skill_by_id("presentation_surface_design").content
    architecture = load_skill_by_id("architecture_explainer_design").content
    components = load_skill_by_id("component_pattern_html").content

    assert "First Decide The Surface" in design
    assert "Layout Patterns" in design
    assert "Layout Quality Contract" in design
    assert "Capability Map" in design
    assert "business_report" in design
    assert "plan_roadmap" in design
    assert "section -> representation -> layout constraint" in design
    assert "collision" in design.lower()
    assert "transparent" in design.lower()
    assert "knowledge_note" in design
    assert "architecture" in design

    assert "Required Document Shape" in safe_html
    assert "Do not include:" in safe_html
    assert "<script>" in safe_html
    assert "Revision Behavior" in safe_html
    assert "Follow StyleBrief section contracts" in safe_html

    assert "Pass Criteria" in review
    assert "Fail Criteria" in review
    assert "Routing Guidance" in review
    assert "background lines" in review
    assert "stretched short-content cards" in review
    assert "control ownership" in review
    assert "responsibility matrices" in review
    assert "score" in review.lower()

    assert "Presentation Surface Design Skill" in presentation
    assert "hero_brief" in presentation
    assert "evidence_table" in presentation
    assert "section rhythm varied" in presentation
    assert "roadmap" in presentation
    assert "Slide-Like Layout Guardrails" in presentation
    assert "Slide Canvas Contract" in presentation
    assert "executive_briefing" in presentation
    assert "tech_sharing" in presentation
    assert "architecture_scene" in presentation
    assert "talk-track order" in presentation
    assert "unsupported runtime" in presentation

    report = load_skill_by_id("report_surface_design").content
    assert "Report Surface Design Skill" in report
    assert "surface-design enhancer" in report
    assert "Do not force a universal report template" in report
    assert "comparisons, responsibilities, parameters" in report
    assert "missing data must remain missing" in report
    assert "primary report canvas" in report
    assert "narrow reading measure" in report

    webpage = load_skill_by_id("webpage_surface_design").content
    assert "Webpage Surface Design Skill" in webpage
    assert "surface-design enhancer" in webpage
    assert "Do not force every webpage into a marketing landing-page pattern" in webpage
    assert "browser-native vertical scrolling" in webpage
    assert "unsupported product claims, social proof, prices, and metrics must remain absent" in webpage

    assert "Architecture Explainer Design Skill" in architecture
    assert "runtime" in architecture
    assert "loop" in architecture
    assert "collision zone" in architecture
    assert "edge_list" in architecture
    assert "control ownership" in architecture

    assert "Component Pattern HTML Skill" in components
    assert "process-flow" in components
    assert "responsive-table" in components
    assert "boundary-table" in components
    assert "selected layout system" in components
    assert "compact-fact-row" in components
    assert "Pattern Selection Rules" in components


def test_generation_v2_requirement_analyst_fallback_preserves_generation_options() -> None:
    state = HtmlGenerationV2Graph().initial_state(
        GenerationInput(
            instruction="Create a board report.",
            theme="dark",
            target_use="ppt",
            style_preference="tech",
            audience="share",
            reference_style="uploaded",
            reference_file_name="style.pdf",
        )
    )
    payload = RequirementAnalystAgent().fake_payload(state)

    assert "Target use: ppt." in payload["constraints"]
    assert "Audience: share." in payload["constraints"]
    assert "theme: dark" in payload["style_preferences"]
    assert "style preference: tech" in payload["style_preferences"]
    assert "reference style: uploaded" in payload["style_preferences"]
    assert "reference file: style.pdf" in payload["style_preferences"]


def test_generation_v2_skill_router_uses_planner_tool_needs() -> None:
    state = GenerationState(
        plan_draft=PlanDraft(
            tool_needs=[
                ToolNeed(tool_name="safe static html", reason="Need safe self-contained HTML output.", priority="high"),
                ToolNeed(tool_name="content quality review", reason="Verify requirement coverage.", priority="medium"),
            ],
        ),
    )

    assert planned_skill_ids_for_agent("HTMLCoder", state) == ()
    assert planned_skill_ids_for_agent("Verifier", state) == ()
    assert planned_skill_ids_for_agent("StyleDesigner", state) == ()
    assert [skill.id for skill in resolve_skills_for_agent("HTMLCoder", state)] == ["safe_static_html"]


def test_generation_v2_skill_router_loads_optional_capability_skills() -> None:
    state = GenerationState(
        plan_draft=PlanDraft(
            tool_needs=[
                ToolNeed(tool_name="presentation surface design", reason="External roadshow pitch page.", priority="high"),
                ToolNeed(tool_name="architecture explainer design", reason="Explain runtime nodes, edges, and loops.", priority="high"),
                ToolNeed(tool_name="component pattern html", reason="Use grids, process flow, and comparison cards.", priority="medium"),
            ],
        ),
    )

    assert planned_skill_ids_for_agent("StyleDesigner", state) == ("presentation_surface_design", "architecture_explainer_design")
    assert planned_skill_ids_for_agent("HTMLCoder", state) == ("architecture_explainer_design", "component_pattern_html")
    assert [skill.id for skill in resolve_skills_for_agent("StyleDesigner", state)] == [
        "html_page_design",
        "presentation_surface_design",
        "architecture_explainer_design",
    ]
    assert [skill.id for skill in resolve_skills_for_agent("HTMLCoder", state)] == [
        "safe_static_html",
        "architecture_explainer_design",
        "component_pattern_html",
    ]


def test_generation_v2_skill_router_maps_explicit_generation_options() -> None:
    state = GenerationState(input=GenerationInput(target_use="ppt", style_preference="magazine"))

    assert planned_skill_ids_for_agent("StyleDesigner", state) == ("presentation_surface_design", "magazine_style_design")
    assert planned_skill_ids_for_agent("HTMLCoder", state) == ()
    assert [skill.id for skill in resolve_skills_for_agent("StyleDesigner", state)] == [
        "html_page_design",
        "presentation_surface_design",
    ]

    report_state = GenerationState(input=GenerationInput(target_use="report"))

    assert planned_skill_ids_for_agent("StyleDesigner", report_state) == ("report_surface_design",)
    assert planned_skill_ids_for_agent("HTMLCoder", report_state) == ()
    assert [skill.id for skill in resolve_skills_for_agent("StyleDesigner", report_state)] == [
        "html_page_design",
        "report_surface_design",
    ]

    webpage_state = GenerationState(input=GenerationInput(target_use="webpage"))

    assert planned_skill_ids_for_agent("StyleDesigner", webpage_state) == ("webpage_surface_design",)
    assert planned_skill_ids_for_agent("HTMLCoder", webpage_state) == ()
    assert [skill.id for skill in resolve_skills_for_agent("StyleDesigner", webpage_state)] == [
        "html_page_design",
        "webpage_surface_design",
    ]


def test_generation_v2_public_summary_groups_skills_and_infers_running_checklist(tmp_path) -> None:
    settings = ServerSettings(
        content_dir=tmp_path / "content",
        meta_dir=tmp_path / "meta",
        public_dir=tmp_path / "public",
        site_title="Test",
        max_upload_bytes=1024,
    )
    state = GenerationState(
        current_step=GenerationStage.DESIGNING_STYLE.value,
        plan_draft=PlanDraft(
            tool_needs=[
                ToolNeed(
                    tool_name="architecture explainer design",
                    reason="Explain runtime nodes, edges, and loops.",
                    priority="high",
                ),
            ],
        ),
        execution_checklist=[
            ChecklistItem(id="style", title="Prepare style", owner="StyleDesigner", status=ChecklistStatus.PENDING),
        ],
        stage_trace=[
            StageTraceEvent(stage=GenerationStage.DESIGNING_STYLE, agent="StyleDesigner", status="started"),
        ],
        skill_trace=[
            SkillTraceEntry(id="html_page_design", title="HTML page design", agent="StyleDesigner", kind="default"),
            SkillTraceEntry(id="architecture_explainer_design", title="Architecture explainer", agent="StyleDesigner", kind="enhanced"),
        ],
    )

    summary = GenerationStore(settings).public_state_summary(state)
    skills = {item["id"]: item for item in summary["skill_trace"]}

    assert skills["html_page_design"]["kind"] == "default"
    assert skills["architecture_explainer_design"]["kind"] == "enhanced"
    assert skills["architecture_explainer_design"]["trigger_reason"] == "Explain runtime nodes, edges, and loops."
    assert summary["execution_checklist"][0]["status"] == "running"


def test_generation_v2_style_reference_file_guides_style_hints() -> None:
    graph = HtmlGenerationV2Graph(parser_mode="basic")
    state = graph.initial_state(
        GenerationInput(
            filename="source.md",
            content=b"# Source\n\nCreate from this material.",
            content_type="text/markdown",
            instruction="Create HTML.",
            reference_style="file",
            reference_file_name="style.html",
            reference_content=b"<style>body{color:#123456;font-family:Inter, sans-serif}.cards{display:grid}</style><h1>Reference</h1>",
            reference_file_type="text/html",
            reference_file_size=92,
        ),
        job_id="job-1",
    )

    result = graph.run(state)

    assert result.parsed_style_reference is not None
    assert any(hint.value == "#123456" for hint in result.parsed_style_reference.style_hints)
    assert result.style_brief is not None
    assert result.style_brief.design_mode == DesignMode.REFERENCE_GUIDED_DESIGN
    assert result.style_brief.reference_sources == ["style.html"]
    assert result.style_brief.color_palette[0].value == "#123456"


def test_style_hint_extractor_detects_css_and_layout_hints() -> None:
    parsed = ParsedDocument(plain_text="font-family: Inter, sans-serif; color:#abcdef; display:grid; ImageSize: 1200x800")

    hints = extract_style_hints(parsed, role="style_reference")

    assert any(hint.kind == "style_reference:color" and hint.value == "#abcdef" for hint in hints)
    assert any(hint.kind == "style_reference:font" and "Inter" in hint.value for hint in hints)
    assert any(hint.kind == "style_reference:layout" and hint.value == "grid" for hint in hints)
    assert any(hint.kind == "style_reference:image_size" and hint.value == "1200x800" for hint in hints)


def test_generation_v2_agent_schema_failure_retries_same_node() -> None:
    graph = HtmlGenerationV2Graph(
        model_client=FakeGenerationModelClient(invalid_outputs={"Planner": 1}),
        parser_mode="basic",
    )
    state = graph.initial_state(
        GenerationInput(filename="source.txt", content=b"Source text", content_type="text/plain", instruction="Create HTML."),
        job_id="job-1",
    )

    result = graph.run(state)

    assert not result.failed_steps
    assert result.plan_draft is not None
    assert result.same_node_retries["Planner"] == 1
    retry_events = [event for event in result.stage_trace if event.agent == "Planner" and event.status == "retrying"]
    assert len(retry_events) == 1
    assert retry_events[0].duration_ms >= 0
    assert retry_events[0].metadata["error_type"] == "AgentOutputSchemaError"


def test_generation_v2_agent_schema_failure_stops_after_retry_limit() -> None:
    graph = HtmlGenerationV2Graph(
        model_client=FakeGenerationModelClient(invalid_outputs={"Planner": 3}),
        parser_mode="basic",
    )
    state = graph.initial_state(
        GenerationInput(filename="source.txt", content=b"Source text", content_type="text/plain", instruction="Create HTML."),
        job_id="job-1",
    )

    result = graph.run(state)

    assert "planning" in result.failed_steps
    assert result.same_node_retries["Planner"] == 3
    assert result.plan_draft is None


class RecordingChatClient:
    def __init__(self, content: str, *, usage: dict | None = None) -> None:
        self.content = content
        self.usage = usage or {}
        self.messages = []
        self.max_tokens = 0
        self.timeout_seconds = None

    def chat(self, *, messages, temperature=0.2, max_tokens=1024, timeout_seconds=None):
        self.messages = messages
        self.max_tokens = max_tokens
        self.timeout_seconds = timeout_seconds
        return {"content": self.content, "model": "fake", "usage": self.usage}


class AlwaysReviseVerifierClient(FakeGenerationModelClient):
    def complete_json(self, *, node: str, schema_name: str, payload: dict, attempt: int = 0) -> str:
        if node == "Verifier":
            return (
                '{"ok": false, "score": 0.62, '
                '"checked_items": [{"id": "quality", "title": "Quality", "passed": false}], '
                '"issues": [{"code": "needs_revision", "message": "Revise the HTML.", "severity": "warning"}], '
                '"route_back_to": "html_coder", "retry_instruction": "Improve the page."}'
            )
        return super().complete_json(node=node, schema_name=schema_name, payload=payload, attempt=attempt)


class EmptyRouteVerifierClient(FakeGenerationModelClient):
    def complete_json(self, *, node: str, schema_name: str, payload: dict, attempt: int = 0) -> str:
        if node == "Verifier":
            return (
                '{"ok": false, "score": 0.72, '
                '"checked_items": [{"id": "source", "title": "Source fidelity", "passed": false}], '
                '"missing_parts": ["Need source evidence for exact figures."], '
                '"unsupported_claims": ["Exact value requires verification."], '
                '"issues": [{"code": "evidence_gap", "message": "Need source evidence.", "severity": "major"}], '
                '"route_back_to": "", "retry_instruction": "Check source evidence before final approval."}'
            )
        return super().complete_json(node=node, schema_name=schema_name, payload=payload, attempt=attempt)


def test_generation_v2_stops_when_validation_revisions_do_not_converge() -> None:
    graph = HtmlGenerationV2Graph(model_client=AlwaysReviseVerifierClient(), parser_mode="basic")
    state = graph.initial_state(
        GenerationInput(filename="source.txt", content=b"Source text", content_type="text/plain", instruction="Create HTML."),
        job_id="job-1",
    )

    result = graph.run(state)

    assert "max_revision_rounds" in result.failed_steps
    assert result.revision_round == 2


def test_generation_v2_falls_back_when_verifier_returns_empty_route() -> None:
    graph = HtmlGenerationV2Graph(model_client=EmptyRouteVerifierClient(), parser_mode="basic")
    state = graph.initial_state(
        GenerationInput(filename="source.txt", content=b"Source text", content_type="text/plain", instruction="Create HTML."),
        job_id="job-1",
    )

    result = graph.run(state)

    assert "max_revision_rounds" in result.failed_steps
    assert "" not in result.failed_steps
    assert result.revision_round == 2
    assert any(event.agent == "ContentWriter" and event.status == "completed" for event in result.stage_trace)


def test_generation_v2_orchestrator_routes_verifier_material_queries_back_to_verifier() -> None:
    state = GenerationState(
        parsed_document=ParsedDocument(plain_text="source"),
        requirement_brief=RequirementBrief(user_goal="Convert source"),
        plan_draft=PlanDraft(page_goal="Convert source"),
        content_draft=ContentDraft(title="Source"),
        style_brief=StyleBrief(style_goal="Light report"),
        html_draft=HtmlDraft(html="<!doctype html><html><body>Source</body></html>"),
        validation_report=ValidationReport(
            ok=False,
            material_queries=[MaterialQuery(id="verify-source", query="source table", purpose="Verify source completeness.")],
        ),
    )

    decision = GenerationOrchestrator().decide_next(state)

    assert decision.next_node == "verifier"


def test_generation_v2_verifier_instructions_require_recall_before_source_failure() -> None:
    prompt = Path("html_lore/server/ai/generation_v2/prompts/verifier.md").read_text(encoding="utf-8")
    skill = Path("html_lore/server/ai/generation_v2/skills/content_quality_review/SKILL.md").read_text(encoding="utf-8")

    assert "two-step process" in prompt
    assert "output `material_queries` first instead of failing immediately" in prompt
    assert "Before returning `ok: false` for source fidelity" in prompt
    assert "lock down the concrete problem yourself" in prompt
    assert "two-phase evidence policy" in skill
    assert "return focused `material_queries` first" in skill
    assert "Verifier owns the validation decision" in skill
    assert "concrete confirmed defect" in skill


def test_generation_v2_provider_model_client_extracts_json_and_includes_schema() -> None:
    chat_client = RecordingChatClient(
        '```json\n{"user_goal":"Create a note","target_use":"default"}\n```',
        usage={"prompt_tokens": 12, "completion_tokens": 8, "total_tokens": 20},
    )
    client = ProviderGenerationModelClient(chat_client, max_prompt_chars=4000, max_tokens=512, json_max_tokens=700, json_timeout_seconds=123)

    raw = client.complete_json(
        node="RequirementAnalyst",
        schema_name="RequirementBrief",
        payload={
            "_prompt": "Analyze requirements.",
            "_schema": {"user_goal": "str"},
            "_state": {"input": {"instruction": "Create a note."}},
            "_skills": [],
            "user_goal": "fallback",
        },
    )

    assert raw == '{"user_goal":"Create a note","target_use":"default"}'
    assert "target_schema" in chat_client.messages[-1]["content"]
    assert "RequirementBrief" in chat_client.messages[-1]["content"]
    assert chat_client.max_tokens == 700
    assert chat_client.timeout_seconds == 123
    assert client.consume_last_usage("RequirementAnalyst") == {"input_tokens": 12, "output_tokens": 8, "total_tokens": 20}
    assert client.consume_last_usage("RequirementAnalyst") == {}


def test_generation_v2_provider_model_client_returns_raw_html_text() -> None:
    html = "<!doctype html><html><head><title>Done</title></head><body><main>Done</main></body></html>"
    chat_client = RecordingChatClient(f"```html\n{html}\n```")
    client = ProviderGenerationModelClient(chat_client, max_prompt_chars=4000, max_tokens=512, html_max_tokens=900, html_timeout_seconds=456)

    raw = client.complete_text(
        node="HTMLCoder",
        payload={
            "_prompt": "Code HTML.",
            "_state": {"content_draft": {"title": "Done"}},
            "_skills": [],
        },
    )

    assert raw == html
    assert "Do not return JSON" in chat_client.messages[-1]["content"]
    assert chat_client.max_tokens == 900
    assert chat_client.timeout_seconds == 456
    assert "final complete HTML document only" in chat_client.messages[-1]["content"]


def test_generation_v2_verifier_state_keeps_html_visible_in_compact_view() -> None:
    html = "<!doctype html><html><body><main>" + ("<p>Generated paragraph.</p>" * 600) + "</main></body></html>"
    state = GenerationState(
        input=GenerationInput(instruction="Create HTML.", content=b"Source" * 6000),
        parsed_document=ParsedDocument(plain_text="Source text. " * 2000),
        content_draft=ContentDraft(title="Generated", sections=[ContentSection(id="overview", title="Overview", body="Body")]),
        html_draft=HtmlDraft(html=html),
    )

    view = public_generation_state_for_agent(state, node="Verifier")

    assert view["html_draft"]["html_present"] is True
    assert view["html_draft"]["html_length"] == len(html)
    assert "<!doctype html>" in view["html_draft"]["html"]
    assert "html_tail" in view["html_draft"]
    assert len(view["parsed_document"]["plain_text"]) < 1300


def test_generation_v2_temporary_material_context_keeps_later_file_table_evidence() -> None:
    first_file = "Source file: guoneng.pdf\n" + ("三一方案 设备方案 电耗 换电站。 " * 900)
    second_file = """Source file: saic.pptx
<!-- Slide number: 11 -->
2.3 电动矿卡产品配置价格

| 技术指标 | 纯电动宽体自卸车配置表 |  |  |  |
| --- | --- | --- | --- | --- |
| 参数类别 | HY120E | HY120E | HY135E | HY155E |
| 大客户价格（万元） | 190 | 195 | 210 | 230 |
价格备注：
车辆价格为全款价格。
"""
    parsed = ParsedDocument(
        source_files=[
            SourceFile(filename="guoneng.pdf", content_type="application/pdf", size=2000),
            SourceFile(filename="saic.pptx", content_type="application/vnd.openxmlformats-officedocument.presentationml.presentation", size=3000),
        ],
        plain_text=f"{first_file}\n\n{second_file}",
    )

    context = build_temporary_material_context(parsed, instruction="分析两个方案中的重卡报价对比")
    selected_text = "\n".join(chunk.text for chunk in context.selected_chunks)

    assert [item.filename for item in context.files] == ["guoneng.pdf", "saic.pptx"]
    assert "大客户价格（万元）" in selected_text
    assert "190" in selected_text and "230" in selected_text
    assert any(chunk.filename == "saic.pptx" and "table_like" in chunk.token_hints for chunk in context.selected_chunks)
    assert context.total_chars > 9000


def test_generation_v2_material_recall_tool_uses_agent_query_for_later_file_evidence() -> None:
    first_file = "Source file: first.pdf\n" + ("early context without the target table. " * 500)
    second_file = """Source file: second.pptx
<!-- Slide number: 8 -->
Reference comparison table

| Item | Alpha | Beta | Gamma |
| --- | --- | --- | --- |
| Budget | 120 | 240 | 360 |
| Owner | Team A | Team B | Team C |
"""
    parsed = ParsedDocument(
        source_files=[SourceFile(filename="first.pdf"), SourceFile(filename="second.pptx")],
        plain_text=f"{first_file}\n\n{second_file}",
    )
    index = build_material_index(parsed, instruction="Create a comparison report.")

    results = recall_material(
        index,
        [MaterialQuery(id="budget_table", query="Alpha Beta Gamma Budget 120 240 360", purpose="Find the comparison table.")],
        agent="ContentWriter",
        max_queries=1,
        max_chars=3000,
    )
    recalled = "\n".join(chunk.text for result in results for chunk in result.chunks)

    assert results[0].agent == "ContentWriter"
    assert "Budget" in recalled
    assert "120" in recalled and "360" in recalled
    assert any(chunk.filename == "second.pptx" for chunk in results[0].chunks)


def test_generation_v2_merge_preserves_structured_material_items_and_file_ownership() -> None:
    first = ParsedDocument(
        source_files=[SourceFile(filename="A.docx", content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", size=10)],
        plain_text="Alpha content",
        outline=[OutlineItem(level=1, title="Alpha", text="Alpha")],
        links=[DocumentLink(text="Alpha link", url="https://example.test/a", source="markdown")],
    )
    second = ParsedDocument(
        source_files=[SourceFile(filename="B.pdf", content_type="application/pdf", size=20)],
        plain_text="Beta content",
        images=[DocumentImage(alt="Beta image", description="Chart", source="page-1")],
        tables=[DocumentTable(title="Beta table", headers=["Name", "Value"], rows=[["Beta", "2"]])],
    )

    merged = merge_parsed_documents([first, second])

    assert [item.file_id for item in merged.materials] == ["file-1", "file-2"]
    assert [item.filename for item in merged.materials] == ["A.docx", "B.pdf"]
    assert merged.plain_text[merged.materials[0].content_start_char : merged.materials[0].content_end_char] == "Alpha content"
    assert merged.plain_text[merged.materials[1].content_start_char : merged.materials[1].content_end_char] == "Beta content"
    assert merged.materials[0].start_char == 0
    assert merged.materials[0].char_count == len("Alpha content")
    assert merged.source_files[0].file_id == "file-1"
    assert merged.source_files[1].file_index == 2
    assert merged.outline[0].filename == "A.docx"
    assert merged.links[0].file_id == "file-1"
    assert merged.images[0].filename == "B.pdf"
    assert merged.tables[0].file_index == 2


def test_generation_v2_single_material_has_full_text_span_without_duplicate_document() -> None:
    parsed = ParsedDocument(source_files=[SourceFile(filename="single.md")], plain_text="Only source text")

    merged = merge_parsed_documents([parsed])

    assert merged.plain_text == "Only source text"
    assert len(merged.materials) == 1
    assert merged.materials[0].filename == "single.md"
    assert merged.materials[0].start_char == 0
    assert merged.materials[0].end_char == len("Only source text")
    assert merged.materials[0].content_start_char == 0
    assert merged.materials[0].content_end_char == len("Only source text")
    assert not hasattr(merged.materials[0], "parsed_document")


def test_generation_v2_material_index_prefers_structured_materials_over_body_markers() -> None:
    first = ParsedDocument(
        source_files=[SourceFile(filename="A.md")],
        plain_text="A introduction\nSource file: this is original body text, not a boundary\nA ending",
    )
    second = ParsedDocument(source_files=[SourceFile(filename="B.md")], plain_text="B content")
    merged = merge_parsed_documents([first, second])

    index = build_material_index(merged, instruction="")

    assert [item.filename for item in index.files] == ["A.md", "B.md"]
    assert index.files[0].char_count == len(first.plain_text)
    assert any("not a boundary" in chunk.text and chunk.filename == "A.md" for chunk in index.chunks)


def test_generation_v2_agent_state_exposes_compact_material_file_identity() -> None:
    merged = merge_parsed_documents(
        [
            ParsedDocument(source_files=[SourceFile(filename="A.md")], plain_text="Alpha " * 300),
            ParsedDocument(source_files=[SourceFile(filename="B.md")], plain_text="Beta details"),
        ],
    )
    context = build_temporary_material_context(merged, instruction="Beta")
    state = GenerationState(input=GenerationInput(instruction="Beta"), parsed_document=merged, temporary_material_context=context)

    view = public_generation_state_for_agent(state, node="RequirementAnalyst")

    assert view["parsed_document"]["materials"][0]["file_id"] == "file-1"
    assert view["parsed_document"]["materials"][1]["filename"] == "B.md"
    assert view["parsed_document"]["materials"][0]["char_count"] == len("Alpha " * 300)
    assert "parsed_document" not in view["parsed_document"]["materials"][0]
    assert "content_start_char" in view["parsed_document"]["materials"][0]


def test_generation_v2_material_read_tool_reads_file_spans_and_continuations() -> None:
    merged = merge_parsed_documents(
        [
            ParsedDocument(source_files=[SourceFile(filename="A.md")], plain_text="Alpha " * 300),
            ParsedDocument(source_files=[SourceFile(filename="B.md")], plain_text="Beta source body"),
        ],
    )

    results = read_material(
        merged,
        [MaterialReadRequest(id="read-a", action="read_file", file_id="file-1", limit=120)],
        agent="ContentWriter",
        max_requests=1,
        max_chars=120,
    )

    assert results[0].filename == "A.md"
    assert results[0].text.startswith("Alpha")
    assert results[0].truncated is True
    assert results[0].next_offset == 120

    next_results = read_material(
        merged,
        [MaterialReadRequest(id="read-a-2", action="read_span", file_id="file-1", offset=results[0].next_offset, limit=80)],
        agent="ContentWriter",
        max_requests=1,
        max_chars=80,
    )
    assert next_results[0].offset == 120
    assert next_results[0].char_count == 80


def test_generation_v2_material_read_deduplicates_same_file_reads() -> None:
    merged = merge_parsed_documents([ParsedDocument(source_files=[SourceFile(filename="source.md")], plain_text="Alpha source body")])

    results = read_material(
        merged,
        [
            MaterialReadRequest(id="a", action="read_file", file_id="file-1", limit=200),
            MaterialReadRequest(id="b", action="read_file", file_id="file-1", limit=200),
        ],
        agent="Verifier",
        max_requests=3,
        max_chars=1000,
    )

    assert len(results) == 1
    assert results[0].text == "Alpha source body"


def test_generation_v2_agent_payload_exposes_material_read_tool_schema() -> None:
    state = GenerationState(input=GenerationInput(instruction="Create."))

    payload = agent_payload(node="ContentWriter", schema=ContentDraft, state=state, fallback={}, skills=())

    assert payload["_available_material_tools"][0]["name"] == "MaterialReadTool"
    assert payload["_available_material_tools"][0]["request_field"] == "material_read_requests"
    assert agent_payload(node="Planner", schema=PlanDraft, state=state, fallback={}, skills=())["_available_material_tools"] == []


def test_generation_v2_verifier_payload_keeps_full_material_read_evidence() -> None:
    long_text = "完整原文" + ("0123456789" * 450)
    state = GenerationState(
        input=GenerationInput(instruction="Verify."),
        material_read_results=[
            read_material(
                merge_parsed_documents([ParsedDocument(source_files=[SourceFile(filename="source.md")], plain_text=long_text)]),
                [MaterialReadRequest(id="read", action="read_file", file_id="file-1", limit=6000)],
                agent="Verifier",
                max_requests=1,
                max_chars=6000,
            )[0]
        ],
    )

    payload = agent_payload(node="Verifier", schema=ValidationReport, state=state, fallback={}, skills=())

    assert payload["_state"]["material_read_results"][0]["text"] == long_text


def test_generation_v2_agent_material_read_runs_before_final_output() -> None:
    merged = merge_parsed_documents([ParsedDocument(source_files=[SourceFile(filename="source.md")], plain_text="Complete source evidence for writer.")])
    state = GenerationState(
        input=GenerationInput(instruction="Write from source."),
        parsed_document=merged,
        requirement_brief=RequirementBrief(user_goal="Write from source."),
    )

    class ReadingClient(FakeGenerationModelClient):
        def complete_json(self, *, node: str, schema_name: str, payload: dict, attempt: int = 0) -> str:
            if node == "ContentWriter" and not payload["_state"].get("material_read_results"):
                return json.dumps(
                    {
                        "title": "Need read",
                        "summary": "",
                        "sections": [],
                        "key_points": [],
                        "references_used": [],
                        "material_queries": [],
                        "material_read_requests": [{"id": "source", "action": "read_file", "file_id": "file-1", "limit": 200, "purpose": "Read source."}],
                    },
                    ensure_ascii=False,
                )
            return json.dumps(
                {
                    "title": "Read Done",
                    "summary": payload["_state"]["material_read_results"][0]["text"],
                    "sections": [{"id": "s", "title": "Source", "body": payload["_state"]["material_read_results"][0]["text"], "bullets": []}],
                    "key_points": ["read"],
                    "references_used": ["source.md"],
                    "material_queries": [],
                    "material_read_requests": [],
                    "evidence_used": ["source"],
                },
                ensure_ascii=False,
            )

    result = ContentWriterAgent(model_client=ReadingClient()).run(state).state

    assert result.content_draft is not None
    assert result.content_draft.title == "Read Done"
    assert result.material_read_results[0].text == "Complete source evidence for writer."
    assert result.agent_artifacts[0].usage["material_read_count"] == 1


def test_generation_v2_content_writer_can_read_material_in_multiple_rounds() -> None:
    merged = merge_parsed_documents([ParsedDocument(source_files=[SourceFile(filename="source.md")], plain_text=("Segment " * 400))])
    state = GenerationState(
        input=GenerationInput(instruction="Write from source."),
        parsed_document=merged,
        requirement_brief=RequirementBrief(user_goal="Write from source."),
    )

    class MultiReadClient(FakeGenerationModelClient):
        def complete_json(self, *, node: str, schema_name: str, payload: dict, attempt: int = 0) -> str:
            reads = payload["_state"].get("material_read_results") or []
            if node == "ContentWriter" and len(reads) < 2:
                next_offset = reads[-1]["next_offset"] if reads else 0
                return json.dumps(
                    {
                        "title": "Need more read",
                        "summary": "",
                        "sections": [],
                        "key_points": [],
                        "references_used": [],
                        "material_queries": [],
                        "material_read_requests": [{"id": f"source-{len(reads)}", "action": "read_span", "file_id": "file-1", "offset": next_offset, "limit": 300, "purpose": "Continue reading."}],
                    },
                    ensure_ascii=False,
                )
            return json.dumps(
                {
                    "title": "Read Done",
                    "summary": "done",
                    "sections": [{"id": "s", "title": "Source", "body": "done", "bullets": []}],
                    "key_points": ["read"],
                    "references_used": ["source.md"],
                    "material_queries": [],
                    "material_read_requests": [],
                    "evidence_used": ["source"],
                },
                ensure_ascii=False,
            )

    result = ContentWriterAgent(model_client=MultiReadClient()).run(state).state

    assert result.content_draft is not None
    assert result.content_draft.title == "Read Done"
    assert len(result.material_read_results) == 2
    assert result.material_read_results[1].offset == result.material_read_results[0].next_offset


def test_generation_v2_material_read_results_can_persist_to_job_workspace(tmp_path) -> None:
    settings = ServerSettings(
        content_dir=tmp_path / "content",
        meta_dir=tmp_path / "meta",
        public_dir=tmp_path / "public",
        site_title="Test",
        max_upload_bytes=1024 * 1024,
    )
    merged = merge_parsed_documents([ParsedDocument(source_files=[SourceFile(filename="source.md")], plain_text="Workspace source evidence.")])
    state = GenerationState(
        job_id="ai_job_workspace",
        input=GenerationInput(instruction="Write from source."),
        parsed_document=merged,
        requirement_brief=RequirementBrief(user_goal="Write from source."),
    )

    class ReadingClient(FakeGenerationModelClient):
        def complete_json(self, *, node: str, schema_name: str, payload: dict, attempt: int = 0) -> str:
            if node == "ContentWriter" and not payload["_state"].get("material_read_results"):
                return json.dumps(
                    {
                        "title": "Need read",
                        "summary": "",
                        "sections": [],
                        "key_points": [],
                        "references_used": [],
                        "material_queries": [],
                        "material_read_requests": [{"id": "source", "action": "read_file", "file_id": "file-1", "limit": 200, "purpose": "Read source."}],
                    },
                    ensure_ascii=False,
                )
            return json.dumps(
                {
                    "title": "Read Done",
                    "summary": "done",
                    "sections": [{"id": "s", "title": "Source", "body": "done", "bullets": []}],
                    "key_points": ["read"],
                    "references_used": ["source.md"],
                    "material_queries": [],
                    "material_read_requests": [],
                    "evidence_used": ["source"],
                },
                ensure_ascii=False,
            )

    def writer(next_state, relative_path, value, mode):
        from html_lore.server.ai.generation_v2.material_bundle import write_job_workspace_jsonl

        write_job_workspace_jsonl(settings, next_state.job_id, relative_path, value if isinstance(value, list) else [value])

    ContentWriterAgent(model_client=ReadingClient(), workspace_writer=writer).run(state)

    reads_path = settings.meta_dir / "ai" / "generation-jobs" / "ai_job_workspace" / "workspace" / "evidence" / "material_reads.jsonl"
    assert reads_path.exists()
    assert "Workspace source evidence." in reads_path.read_text(encoding="utf-8")


def test_generation_v2_verifier_recall_final_phase_does_not_loop_on_more_queries() -> None:
    parsed = merge_parsed_documents(
        [
            ParsedDocument(
                source_files=[SourceFile(filename="source.md")],
                plain_text="交易对价 53,600,930.82 元。项目 IRR 8%。报告内容用于验证。",
            )
        ]
    )
    state = GenerationState(
        input=GenerationInput(instruction="忠实转换为 HTML 报告"),
        parsed_document=parsed,
        material_index=build_material_index(parsed, instruction="交易对价 IRR"),
        requirement_brief=RequirementBrief(user_goal="忠实转换为 HTML 报告"),
        plan_draft=PlanDraft(page_goal="忠实转换"),
        content_draft=ContentDraft(title="报告", summary="交易对价 53,600,930.82 元。", sections=[ContentSection(id="s", title="估值", body="项目 IRR 8%。")]),
        style_brief=StyleBrief(style_goal="亮色报告"),
        html_draft=HtmlDraft(html="<!doctype html><html><body>交易对价 53,600,930.82 元。项目 IRR 8%。</body></html>"),
    )

    class RepeatingVerifierQueryClient(FakeGenerationModelClient):
        def complete_json(self, *, node: str, schema_name: str, payload: dict, attempt: int = 0) -> str:
            if node == "Verifier":
                if payload["_state"].get("material_read_results"):
                    return json.dumps(
                        {
                            "ok": False,
                            "score": 0.62,
                            "checked_items": [{"id": "source", "title": "源文档核验", "passed": False}],
                            "issues": [{"code": "confirmed_gap", "message": "已读取原文，但仍需修订内容。", "severity": "major"}],
                            "missing_parts": [],
                            "unsupported_claims": ["需要修订内容"],
                            "style_mismatch": [],
                            "structure_mismatch": [],
                            "route_back_to": "content_writer",
                            "retry_instruction": "根据读取到的原文修订内容。",
                            "material_queries": [],
                            "material_read_requests": [],
                        },
                        ensure_ascii=False,
                    )
                return json.dumps(
                    {
                        "ok": False,
                        "score": 0.0,
                        "checked_items": [{"id": "source", "title": "源文档核验", "passed": False}],
                        "issues": [{"code": "needs_evidence", "message": "仍需核验源文档。", "severity": "blocking"}],
                        "missing_parts": [],
                        "unsupported_claims": [],
                        "style_mismatch": [],
                        "structure_mismatch": [],
                        "route_back_to": "",
                        "retry_instruction": "",
                        "material_queries": [{"id": "q", "query": "交易对价 53,600,930.82 IRR 8%", "purpose": "核验关键数字"}],
                        "material_read_requests": [],
                    },
                    ensure_ascii=False,
                )
            return super().complete_json(node=node, schema_name=schema_name, payload=payload, attempt=attempt)

    result = VerifierAgent(model_client=RepeatingVerifierQueryClient()).run(state).state

    assert len(result.material_recall_results) == 2
    assert len(result.material_read_results) == 1
    assert result.validation_report is not None
    assert result.validation_report.material_queries == []
    assert result.validation_report.material_read_requests == []
    assert result.validation_report.route_back_to == "content_writer"


def test_generation_v2_verifier_can_escalate_from_recall_to_material_read() -> None:
    parsed = merge_parsed_documents(
        [
            ParsedDocument(
                source_files=[SourceFile(filename="source.md")],
                plain_text="完整原文：交易对价 53,600,930.82 元。项目 IRR 8%。结论：内容准确。",
            )
        ]
    )
    state = GenerationState(
        input=GenerationInput(instruction="忠实转换为 HTML 报告"),
        parsed_document=parsed,
        material_index=build_material_index(parsed, instruction="交易对价 IRR"),
        requirement_brief=RequirementBrief(user_goal="忠实转换为 HTML 报告"),
        plan_draft=PlanDraft(page_goal="忠实转换"),
        content_draft=ContentDraft(title="报告", summary="交易对价 53,600,930.82 元。", sections=[ContentSection(id="s", title="估值", body="项目 IRR 8%。")]),
        style_brief=StyleBrief(style_goal="亮色报告"),
        html_draft=HtmlDraft(html="<!doctype html><html><body>交易对价 53,600,930.82 元。项目 IRR 8%。</body></html>"),
    )

    class RecallThenReadVerifierClient(FakeGenerationModelClient):
        def complete_json(self, *, node: str, schema_name: str, payload: dict, attempt: int = 0) -> str:
            if node != "Verifier":
                return super().complete_json(node=node, schema_name=schema_name, payload=payload, attempt=attempt)
            state_view = payload["_state"]
            if not state_view.get("material_recall_results"):
                return json.dumps(
                    {
                        "ok": False,
                        "score": 0.0,
                        "checked_items": [{"id": "source", "title": "源文档核验", "passed": False}],
                        "issues": [],
                        "missing_parts": [],
                        "unsupported_claims": [],
                        "style_mismatch": [],
                        "structure_mismatch": [],
                        "route_back_to": "",
                        "retry_instruction": "",
                        "material_queries": [{"id": "q", "query": "交易对价 53,600,930.82 IRR 8%", "purpose": "核验关键数字"}],
                        "material_read_requests": [],
                    },
                    ensure_ascii=False,
                )
            if not state_view.get("material_read_results"):
                return json.dumps(
                    {
                        "ok": False,
                        "score": 0.0,
                        "checked_items": [{"id": "source", "title": "需要读取原文", "passed": False}],
                        "issues": [],
                        "missing_parts": [],
                        "unsupported_claims": [],
                        "style_mismatch": [],
                        "structure_mismatch": [],
                        "route_back_to": "",
                        "retry_instruction": "",
                        "material_queries": [],
                        "material_read_requests": [{"id": "read-source", "action": "read_file", "file_id": "file-1", "limit": 500, "purpose": "读取完整原文核验"}],
                    },
                    ensure_ascii=False,
                )
            return json.dumps(
                {
                    "ok": True,
                    "score": 0.92,
                    "checked_items": [{"id": "source", "title": "源文档核验", "passed": True}],
                    "issues": [],
                    "missing_parts": [],
                    "unsupported_claims": [],
                    "style_mismatch": [],
                    "structure_mismatch": [],
                    "route_back_to": "",
                    "retry_instruction": "",
                    "material_queries": [],
                    "material_read_requests": [],
                },
                ensure_ascii=False,
            )

    result = VerifierAgent(model_client=RecallThenReadVerifierClient()).run(state).state

    assert len(result.material_recall_results) == 1
    assert len(result.material_read_results) == 1
    assert result.validation_report is not None
    assert result.validation_report.ok is True
    assert result.validation_report.material_queries == []
    assert result.validation_report.material_read_requests == []


def test_generation_v2_agent_state_uses_temporary_material_context_over_raw_prefix() -> None:
    parsed = ParsedDocument(
        source_files=[SourceFile(filename="first.md"), SourceFile(filename="second.md")],
        plain_text="Source file: first.md\n" + ("early filler " * 1000) + "\n\nSource file: second.md\nimportant later table",
    )
    context = build_temporary_material_context(parsed, instruction="find later table")
    state = GenerationState(input=GenerationInput(instruction="find later table"), parsed_document=parsed, temporary_material_context=context)

    view = public_generation_state_for_agent(state, node="RequirementAnalyst")

    assert "temporary_material_context" in view
    assert view["temporary_material_context"]["files"][1]["filename"] == "second.md"
    assert any("important later table" in chunk["text"] for chunk in view["temporary_material_context"]["selected_chunks"])
    assert len(view["parsed_document"]["plain_text"]) < 1300


def test_generation_v2_agent_state_exposes_material_status_for_full_context() -> None:
    full_text = " ".join(["完整材料内容"] * 450)
    parsed = merge_parsed_documents([ParsedDocument(source_files=[SourceFile(filename="source.docx")], plain_text=full_text)])
    context = build_temporary_material_context(parsed, instruction="忠实转换，禁止省略")
    state = GenerationState(input=GenerationInput(instruction="忠实转换，禁止省略"), parsed_document=parsed, temporary_material_context=context)

    view = public_generation_state_for_agent(state, node="RequirementAnalyst")

    assert view["material_status"]["total_chars"] == len(full_text)
    assert view["material_status"]["selected_chars"] >= len(full_text) - 64
    assert view["material_status"]["selected_covers_full_text"] is True
    assert view["material_status"]["parsed_document_is_preview"] is True
    assert view["material_status"]["parsed_text_preview_truncated"] is True
    assert "full parsed text" in view["material_status"]["coverage_note"]


def test_generation_v2_post_agent_state_compacts_temporary_material_context() -> None:
    long_later_text = "important later evidence " * 120
    parsed = ParsedDocument(
        source_files=[SourceFile(filename="first.md"), SourceFile(filename="second.md")],
        plain_text="Source file: first.md\n# Early\nsmall\n\nSource file: second.md\n" + long_later_text,
    )
    context = build_temporary_material_context(parsed, instruction="important later evidence")
    state = GenerationState(input=GenerationInput(instruction="important later evidence"), parsed_document=parsed, temporary_material_context=context)

    front_view = public_generation_state_for_agent(state, node="RequirementAnalyst")
    verifier_view = public_generation_state_for_agent(state, node="Verifier")

    front_text = "\n".join(chunk["text"] for chunk in front_view["temporary_material_context"]["selected_chunks"])
    verifier_text = "\n".join(chunk["text"] for chunk in verifier_view["temporary_material_context"]["selected_chunks"])
    assert len(front_text) > len(verifier_text)
    assert len(verifier_view["temporary_material_context"]["selected_chunks"][0]["text"]) <= 520


def test_generation_v2_extract_json_object_from_plain_text() -> None:
    assert extract_json_object("Here is JSON:\n{\"ok\":true}\nDone.") == '{"ok":true}'


def test_generation_v2_extract_html_document_from_plain_text_and_fence() -> None:
    html = "<!doctype html><html><head><title>Done</title></head><body><main>Done</main></body></html>"

    assert extract_html_document(f"Here is HTML:\n```html\n{html}\n```\nDone.") == html
    assert extract_html_document(f"prefix\n{html}\nsuffix") == html


def test_generation_v2_schema_loader_accepts_normalized_enum_values() -> None:
    item = dataclass_from_dict({"id": "verify", "title": "Verify", "owner": "Verifier", "status": "DONE"}, ChecklistItem)

    assert item.status == ChecklistStatus.DONE


def test_generation_v2_schema_loader_treats_null_collections_as_defaults() -> None:
    draft = dataclass_from_dict(
        {
            "title": "Draft",
            "sections": None,
            "key_points": None,
            "callouts": None,
            "tables": None,
            "quotes": None,
        },
        ContentDraft,
    )

    assert draft.sections == []
    assert draft.key_points == []
    assert draft.callouts == []
    assert draft.tables == []
    assert draft.quotes == []


def test_generation_v2_retry_output_rules_are_only_added_after_first_attempt() -> None:
    assert retry_output_rules(0) == []
    assert any("retry" in rule.lower() for rule in retry_output_rules(1))


def test_generation_v2_html_coder_accepts_raw_complete_html() -> None:
    html = "<!doctype html><html><head><title>Generated</title></head><body><main>Generated</main></body></html>"
    state = GenerationState(
        input=GenerationInput(instruction="Create HTML."),
        content_draft=ContentDraft(title="Generated", summary="Summary", sections=[ContentSection(id="a", title="A", body="Body")]),
    )

    output = HTMLCoderAgent(model_client=FakeGenerationModelClient()).invoke_structured(state)

    assert isinstance(output, HtmlDraft)
    assert output.html.startswith("<!doctype html>")
    assert "</html>" in output.html

    class RawHtmlClient(FakeGenerationModelClient):
        def complete_text(self, *, node: str, payload: dict, attempt: int = 0) -> str:
            return html

    output = HTMLCoderAgent(model_client=RawHtmlClient()).invoke_structured(state)

    assert output.html == html


def test_generation_v2_html_coder_rejects_incomplete_html() -> None:
    state = GenerationState(input=GenerationInput(instruction="Create HTML."))

    class BadHtmlClient(FakeGenerationModelClient):
        def complete_text(self, *, node: str, payload: dict, attempt: int = 0) -> str:
            return "<main>Missing document wrapper</main>"

    try:
        HTMLCoderAgent(model_client=BadHtmlClient()).invoke_structured(state)
    except AgentOutputSchemaError as exc:
        assert "complete HTML document" in str(exc)
    else:
        raise AssertionError("AgentOutputSchemaError was expected.")


def test_generation_model_profile_defaults_to_quality_model(tmp_path) -> None:
    settings = ServerSettings(
        content_dir=tmp_path / "content",
        meta_dir=tmp_path / "meta",
        public_dir=tmp_path / "public",
        site_title="Test",
        max_upload_bytes=1024,
    )
    profile = GenerationModelProfile.from_settings(settings)

    assert profile.default_model == DEFAULT_GENERATION_MODEL
    assert profile.model_for("planner") == DEFAULT_GENERATION_MODEL


def test_generation_config_defaults_to_legacy(monkeypatch) -> None:
    monkeypatch.delenv("HTML_LORE_AI_GENERATION_ENGINE", raising=False)
    monkeypatch.delenv("HTML_LORE_AI_GENERATION_MODEL", raising=False)
    monkeypatch.delenv("HTML_LORE_AI_GENERATION_HTML_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv("HTML_LORE_DOCUMENT_PARSER", raising=False)

    settings = load_settings()

    assert settings.ai_generation_engine == "legacy"
    assert settings.ai_generation_model == DEFAULT_GENERATION_MODEL
    assert settings.ai_generation_html_timeout_seconds == 900
    assert settings.document_parser == "markitdown"


def test_generation_config_accepts_v2(monkeypatch) -> None:
    monkeypatch.setenv("HTML_LORE_AI_GENERATION_ENGINE", "v2")
    monkeypatch.setenv("HTML_LORE_AI_GENERATION_MODEL", "custom-generation-model")
    monkeypatch.setenv("HTML_LORE_AI_GENERATION_MAX_TOKENS", "16000")
    monkeypatch.setenv("HTML_LORE_AI_GENERATION_JSON_MAX_TOKENS", "6000")
    monkeypatch.setenv("HTML_LORE_AI_GENERATION_HTML_MAX_TOKENS", "18000")
    monkeypatch.setenv("HTML_LORE_AI_PROVIDER_TIMEOUT_SECONDS", "240")
    monkeypatch.setenv("HTML_LORE_AI_GENERATION_JSON_TIMEOUT_SECONDS", "260")
    monkeypatch.setenv("HTML_LORE_AI_GENERATION_HTML_TIMEOUT_SECONDS", "720")
    monkeypatch.setenv("HTML_LORE_DOCUMENT_PARSER", "basic")

    settings = load_settings()

    assert settings.ai_generation_engine == "v2"
    assert settings.ai_generation_model == "custom-generation-model"
    assert settings.ai_generation_max_tokens == 16000
    assert settings.ai_generation_json_max_tokens == 6000
    assert settings.ai_generation_html_max_tokens == 18000
    assert settings.ai_provider_timeout_seconds == 240
    assert settings.ai_generation_json_timeout_seconds == 260
    assert settings.ai_generation_html_timeout_seconds == 720
    assert settings.document_parser == "basic"


def test_generation_v2_service_uses_larger_prompt_budget_for_material_evidence(tmp_path: Path) -> None:
    settings = ServerSettings(
        content_dir=tmp_path / "content",
        meta_dir=tmp_path / "meta",
        public_dir=tmp_path / "public",
        site_title="Test",
        max_upload_bytes=1024,
        ai_max_prompt_chars=12000,
        ai_generation_engine="v2",
    )

    class FakeStore:
        def get(self) -> AIProviderConfig:
            return AIProviderConfig(provider="openai-compatible", base_url="https://example.invalid/v1", api_key="test-key", enabled=True, model="fake-model")

    service = AIConversationService(settings, store=None, item_service=None, provider_store=FakeStore(), run_store=None)
    client = service._generation_v2_model_client()

    assert isinstance(client, ProviderGenerationModelClient)
    assert client.max_prompt_chars == 48000


def test_basic_document_parser_handles_markdown() -> None:
    parsed = parse_document_basic(
        filename="material.md",
        content=b"# Title\n\nBody paragraph.",
        content_type="text/markdown",
    )

    assert isinstance(parsed, ParsedDocument)
    assert parsed.plain_text == "# Title Body paragraph."
    assert parsed.outline[0].title == "Title"
    assert parsed.source_files[0].filename == "material.md"


def test_basic_document_parser_handles_html() -> None:
    parsed = parse_document_basic(
        filename="source.html",
        content=b"<!doctype html><h1>Alpha</h1><p>Body</p><a href='https://example.invalid'>Link</a>",
        content_type="text/html",
    )

    assert "Alpha" in parsed.plain_text
    assert parsed.outline[0].title == "Alpha"
    assert parsed.links[0].url == "https://example.invalid"


def test_document_parser_uses_basic_parser_for_markdown() -> None:
    parsed = parse_document(
        filename="brief.md",
        content=b"# Brief\n\nUse this as source material.",
        content_type="text/markdown",
    )

    assert parsed.plain_text == "# Brief Use this as source material."
    assert parsed.outline[0].title == "Brief"
    assert parsed.source_files[0].filename == "brief.md"
    assert parsed.source_files[0].role == "material"
    assert not parsed.warnings


def test_document_parser_falls_back_when_markitdown_is_missing(monkeypatch) -> None:
    monkeypatch.setattr(document_parser, "MarkItDown", None)

    parsed = parse_document(
        filename="deck.pptx",
        content=b"Quarterly strategy deck",
        content_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        reference_role="style_reference",
    )

    assert "Quarterly strategy deck" in parsed.plain_text
    assert parsed.source_files[0].filename == "deck.pptx"
    assert parsed.source_files[0].role == "style_reference"
    assert any(warning.code == "unsupported_basic_parser" for warning in parsed.warnings)
    assert any(warning.code == "markitdown_unavailable_or_failed" for warning in parsed.warnings)


def test_document_parser_can_disable_enhanced_parser(monkeypatch) -> None:
    class UnexpectedMarkItDown:
        def convert(self, _path: str) -> object:
            raise AssertionError("MarkItDown should not be called in basic parser mode.")

    monkeypatch.setattr(document_parser, "MarkItDown", UnexpectedMarkItDown)

    parsed = parse_document(
        filename="proposal.docx",
        content=b"Proposal source text",
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        parser_mode="basic",
    )

    assert "Proposal source text" in parsed.plain_text
    assert any(warning.code == "unsupported_basic_parser" for warning in parsed.warnings)
    assert any(warning.code == "enhanced_parser_disabled" for warning in parsed.warnings)
    assert not any(warning.code == "markitdown_failed" for warning in parsed.warnings)


def test_document_parser_uses_markitdown_for_excel(monkeypatch) -> None:
    class SpreadsheetMarkItDown:
        def convert(self, _path: str) -> object:
            return type("Result", (), {"text_content": "Spreadsheet revenue plan"})()

    monkeypatch.setattr(document_parser, "MarkItDown", SpreadsheetMarkItDown)

    parsed = parse_document(
        filename="budget.xlsx",
        content=b"spreadsheet source",
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    assert parsed.plain_text == "Spreadsheet revenue plan"
    assert parsed.source_files[0].filename == "budget.xlsx"
    assert any(warning.code == "markitdown_used" for warning in parsed.warnings)


def test_document_parser_phase_one_file_type_matrix(monkeypatch) -> None:
    class MatrixMarkItDown:
        def convert(self, path: str) -> object:
            return type("Result", (), {"text_content": f"Converted {Path(path).suffix.lower()} material"})()

    monkeypatch.setattr(document_parser, "MarkItDown", MatrixMarkItDown)

    cases = [
        ("brief.md", b"# Brief\n\nMarkdown body.", "text/markdown", "basic", "# Brief Markdown body.", ""),
        ("page.html", b"<h1>HTML Brief</h1><p>Body.</p>", "text/html", "basic", "HTML Brief Body.", ""),
        ("notes.txt", b"Plain source body.", "text/plain", "basic", "Plain source body.", ""),
        ("report.pdf", b"%PDF fake", "application/pdf", "markitdown", "Converted .pdf material", "markitdown_used"),
        ("proposal.docx", b"docx bytes", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "markitdown", "Converted .docx material", "markitdown_used"),
        ("legacy.doc", b"doc bytes", "application/msword", "markitdown", "Converted .doc material", "markitdown_used"),
        ("deck.pptx", b"pptx bytes", "application/vnd.openxmlformats-officedocument.presentationml.presentation", "markitdown", "Converted .pptx material", "markitdown_used"),
        ("legacy.ppt", b"ppt bytes", "application/vnd.ms-powerpoint", "markitdown", "Converted .ppt material", "markitdown_used"),
        ("budget.xlsx", b"xlsx bytes", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "markitdown", "Converted .xlsx material", "markitdown_used"),
        ("budget.xls", b"xls bytes", "application/vnd.ms-excel", "markitdown", "Converted .xls material", "markitdown_used"),
        ("reference.jpg", b"jpg bytes", "image/jpeg", "markitdown", "Converted .jpg material", "markitdown_used"),
        ("reference.png", b"png bytes", "image/png", "markitdown", "Converted .png material", "markitdown_used"),
    ]

    for filename, content, content_type, expected_parser, expected_text, expected_warning in cases:
        parsed = parse_document(filename=filename, content=content, content_type=content_type)

        assert expected_text in parsed.plain_text
        assert parsed.source_files[0].filename == filename
        if expected_parser == "basic":
            assert not any(warning.code.startswith("markitdown") for warning in parsed.warnings), filename
        else:
            assert any(warning.code == expected_warning for warning in parsed.warnings), filename


def test_document_parser_uses_markitdown_for_local_image(monkeypatch) -> None:
    class ImageMarkItDown:
        def convert(self, _path: str) -> object:
            return type("Result", (), {"text_content": "ImageSize: 1200x800"})()

    monkeypatch.setattr(document_parser, "MarkItDown", ImageMarkItDown)

    parsed = parse_document(
        filename="reference.png",
        content=b"fake image bytes",
        content_type="image/png",
        reference_role="style_reference",
    )

    assert parsed.plain_text == "ImageSize: 1200x800"
    assert parsed.source_files[0].role == "style_reference"
    assert any(warning.code == "markitdown_used" for warning in parsed.warnings)


def test_document_parser_does_not_send_audio_to_markitdown(monkeypatch) -> None:
    class UnexpectedMarkItDown:
        def convert(self, _path: str) -> object:
            raise AssertionError("Audio transcription is not part of the local phase-one parser chain.")

    monkeypatch.setattr(document_parser, "MarkItDown", UnexpectedMarkItDown)

    parsed = parse_document(
        filename="meeting.mp3",
        content=b"audio bytes",
        content_type="audio/mpeg",
    )

    assert "audio bytes" in parsed.plain_text
    assert any(warning.code == "unsupported_basic_parser" for warning in parsed.warnings)
    assert not any(warning.code.startswith("markitdown") for warning in parsed.warnings)


def test_document_parser_keeps_markitdown_failure_warning(monkeypatch) -> None:
    class FailingMarkItDown:
        def convert(self, _path: str) -> object:
            raise RuntimeError("conversion failed")

    monkeypatch.setattr(document_parser, "MarkItDown", FailingMarkItDown)

    parsed = parse_document(
        filename="report.pdf",
        content=b"%PDF-1.4 fake content",
        content_type="application/pdf",
    )

    assert parsed.source_files[0].filename == "report.pdf"
    assert any(warning.code == "markitdown_failed" for warning in parsed.warnings)
    assert any(warning.code == "markitdown_unavailable_or_failed" for warning in parsed.warnings)


def test_generation_store_reuses_ai_jobs_with_v2_fields(tmp_path) -> None:
    settings = ServerSettings(
        content_dir=tmp_path / "content",
        meta_dir=tmp_path / "meta",
        public_dir=tmp_path / "public",
        site_title="Test",
        max_upload_bytes=1024,
    )
    store = GenerationStore(settings)

    job = store.create_job(kind="material_html_generation", label="source.md")
    job_id = job["job_id"]
    store.update_job_status(job_id, status=GenerationJobStatus.RUNNING, stage=GenerationStage.PARSING, message="Parsing")
    store.append_stage_trace(
        job_id,
        StageTraceEvent(stage=GenerationStage.PARSING, agent="Ingest", status="completed", message="Parsed"),
    )
    store.update_execution_checklist(
        job_id,
        [ChecklistItem(id="draft-content", title="Draft content", owner="Content Writer", status=ChecklistStatus.PENDING)],
    )
    store.jobs.update(
        job_id,
        {
            "agent_artifacts": [
                {
                    "agent": "HTMLCoder",
                    "stage": "coding_html",
                    "title": "HTML draft",
                    "summary": "100 chars",
                    "input_summary": "content draft and style brief",
                    "output_summary": "passed: doctype, style, script-free",
                    "quality_score": 0.9,
                    "usage": {"retry_count": 1, "output_chars": 100, "cost": 0.1, "prompt": "private prompt"},
                    "warnings": ["render assumption"],
                    "data": {"html_chars": 100, "html": "<!doctype html><html>secret</html>"},
                },
                {
                    "agent": "RequirementAnalyst",
                    "stage": "analyzing_requirements",
                    "title": "Requirement analysis",
                    "summary": "requirements",
                    "input_summary": "generation request",
                    "output_summary": "requirements parsed",
                    "quality_score": 0.8,
                    "usage": {},
                    "warnings": [],
                    "data": {"user_instruction": "Please preserve this long user request. " * 30, "prompt": "private system prompt"},
                }
            ]
        },
    )

    public_job = AIJobStore(settings).get(job_id)

    assert public_job["generation_engine"] == "v2"
    assert public_job["status"] == "running"
    assert public_job["current_stage"] == "parsing"
    assert public_job["stage_trace"][0]["agent"] == "Ingest"
    assert "duration_ms" in public_job["stage_trace"][0]
    assert "metadata" in public_job["stage_trace"][0]
    assert public_job["execution_checklist"][0]["id"] == "draft-content"
    assert public_job["agent_artifacts"][0]["agent"] == "HTMLCoder"
    assert public_job["agent_artifacts"][0]["input_summary"] == "content draft and style brief"
    assert public_job["agent_artifacts"][0]["output_summary"] == "passed: doctype, style, script-free"
    assert public_job["agent_artifacts"][0]["quality_score"] == 0.9
    assert public_job["agent_artifacts"][0]["usage"]["retry_count"] == 1
    assert "cost" not in public_job["agent_artifacts"][0]["usage"]
    assert "prompt" not in public_job["agent_artifacts"][0]["usage"]
    assert public_job["agent_artifacts"][0]["warnings"] == ["render assumption"]
    assert public_job["agent_artifacts"][0]["data"]["html_chars"] == 100
    assert "html" not in public_job["agent_artifacts"][0]["data"]
    assert public_job["agent_artifacts"][1]["data"]["user_instruction"].startswith("Please preserve this long user request.")
    assert len(public_job["agent_artifacts"][1]["data"]["user_instruction"]) > 360
    assert "prompt" not in public_job["agent_artifacts"][1]["data"]


def test_generation_job_workspace_hides_private_paths_by_default(tmp_path) -> None:
    settings = ServerSettings(
        content_dir=tmp_path / "content",
        meta_dir=tmp_path / "meta",
        public_dir=tmp_path / "public",
        site_title="Test",
        max_upload_bytes=1024 * 1024,
    )
    store = AIJobStore(settings)
    job = store.create(kind="material_html_generation", label="Material")
    store.update(
        str(job["job_id"]),
        {
            "workspace": {
                "status": "ready",
                "bundle_id": "bundle-1",
                "workspace_path": "ai/generation-jobs/job/workspace",
                "merged_path": "ai/generation-jobs/job/workspace/materials/merged.md",
                "manifest_path": "ai/generation-jobs/job/workspace/materials/manifest.json",
            }
        },
    )

    public_job = store.get(str(job["job_id"]))
    private_job = store.get(str(job["job_id"]), include_private=True)

    assert public_job["workspace"] == {"status": "ready", "bundle_id": "bundle-1"}
    assert private_job["workspace"]["workspace_path"].endswith("/workspace")
    assert private_job["workspace"]["merged_path"].endswith("merged.md")


def test_generation_store_saves_v2_run_fields(tmp_path) -> None:
    settings = ServerSettings(
        content_dir=tmp_path / "content",
        meta_dir=tmp_path / "meta",
        public_dir=tmp_path / "public",
        site_title="Test",
        max_upload_bytes=1024,
    )
    store = GenerationStore(settings)

    run = store.save_run(
        {
            "id": "run-1",
            "kind": "material_html_generation",
            "status": "completed",
            "current_stage": "completed",
            "stage_trace": [
                {"stage": "verifying", "agent": "Verifier", "status": "started"},
                {"stage": "completed", "agent": "Write Gateway", "status": "completed"},
            ],
            "execution_checklist": [
                {"id": "verify", "title": "Verify", "owner": "Verifier", "status": "pending"},
                {"id": "write", "title": "Write file", "owner": "Write Gateway", "status": "done"},
            ],
            "skill_trace": [
                {
                    "id": "component_pattern_html",
                    "title": "Component pattern HTML",
                    "agent": "HTMLCoder",
                    "kind": "enhanced",
                    "trigger_reason": "Use grids and comparison cards.",
                },
            ],
            "agent_artifacts": [
                {
                    "agent": "ContentWriter",
                    "stage": "writing_content",
                    "title": "Draft",
                    "summary": "Safe summary",
                    "data": {"summary": "Safe summary", "content": "private raw content"},
                }
            ],
        },
    )
    fetched = AIRunStore(settings).get("run-1")

    assert run["generation_engine"] == "v2"
    assert fetched["generation_engine"] == "v2"
    assert fetched["stage_trace"][0]["stage"] == "verifying"
    assert fetched["execution_checklist"][0]["status"] == "running"
    assert fetched["execution_checklist"][1]["status"] == "completed"
    assert fetched["skill_trace"][0]["kind"] == "enhanced"
    assert fetched["skill_trace"][0]["trigger_reason"] == "Use grids and comparison cards."
    assert fetched["agent_artifacts"][0]["agent"] == "ContentWriter"
    assert "content" not in fetched["agent_artifacts"][0]["data"]


def test_ai_job_checklist_status_can_be_inferred_from_stage_trace(tmp_path) -> None:
    settings = ServerSettings(
        content_dir=tmp_path / "content",
        meta_dir=tmp_path / "meta",
        public_dir=tmp_path / "public",
        site_title="Test",
        max_upload_bytes=1024,
    )
    store = GenerationStore(settings)
    job = store.create_job(kind="material_html_generation", label="source.md")
    job_id = job["job_id"]
    store.jobs.update(
        job_id,
        {
            "stage_trace": [
                {"stage": "writing_content", "agent": "ContentWriter", "status": "completed"},
                {"stage": "designing_style", "agent": "StyleDesigner", "status": "completed"},
                {"stage": "coding_html", "agent": "HTMLCoder", "status": "started"},
            ],
            "execution_checklist": [
                {"id": "content", "title": "Draft content", "owner": "ContentWriter", "status": "pending"},
                {"id": "style", "title": "Prepare style", "owner": "Designer", "status": "pending"},
                {"id": "code", "title": "Write HTML", "owner": "Coder", "status": "pending"},
                {"id": "verify", "title": "Verify quality", "owner": "Verifier", "status": "pending"},
            ],
        },
    )

    public_job = AIJobStore(settings).get(job_id)
    statuses = {item["id"]: item["status"] for item in public_job["execution_checklist"]}

    assert statuses["content"] == "completed"
    assert statuses["style"] == "completed"
    assert statuses["code"] == "running"
    assert statuses["verify"] == "pending"


def test_v2_material_job_sync_keeps_agent_artifacts_in_job_detail(tmp_path) -> None:
    settings = ServerSettings(
        content_dir=tmp_path / "content",
        meta_dir=tmp_path / "meta",
        public_dir=tmp_path / "public",
        site_title="Test",
        max_upload_bytes=1024,
    )
    store = GenerationStore(settings)
    job = store.create_job(kind="material_html_generation", label="source.md")
    run = {
        "id": "run-sync",
        "status": "completed",
        "current_stage": "completed",
        "stage_trace": [{"stage": "coding_html", "agent": "HTMLCoder", "status": "completed"}],
        "execution_checklist": [{"id": "code", "title": "Code", "owner": "HTMLCoder", "status": "completed"}],
        "skill_trace": [{"id": "html_quality", "title": "HTML quality", "agent": "HTMLCoder"}],
        "agent_artifacts": [
            {
                "agent": "HTMLCoder",
                "stage": "coding_html",
                "title": "HTML draft",
                "summary": "100 chars",
                "input_summary": "content draft and style brief",
                "output_summary": "passed: doctype, style, script-free",
                "quality_score": 0.9,
                "usage": {"retry_count": 0, "output_chars": 100},
                "warnings": [],
                "data": {"html_chars": 100},
            }
        ],
        "item_id": "generated/source.html",
        "retryable": False,
        "cancellable": False,
    }

    sync_v2_job_from_run(settings, str(job["job_id"]), run, status="completed")

    public_job = store.jobs.get(str(job["job_id"]))

    assert public_job["status"] == "completed"
    assert public_job["item_id"] == "generated/source.html"
    assert public_job["agent_artifacts"][0]["agent"] == "HTMLCoder"
    assert public_job["agent_artifacts"][0]["input_summary"] == "content draft and style brief"
    assert public_job["agent_artifacts"][0]["usage"]["output_chars"] == 100


def test_v2_material_job_sync_marks_failed_run_terminal(tmp_path) -> None:
    settings = ServerSettings(
        content_dir=tmp_path / "content",
        meta_dir=tmp_path / "meta",
        public_dir=tmp_path / "public",
        site_title="Test",
        max_upload_bytes=1024,
    )
    store = GenerationStore(settings)
    job = store.create_job(kind="material_html_generation", label="source.pdf")
    run = {
        "id": "run-failed",
        "status": "failed",
        "completed_at": "2026-07-02T01:02:03+00:00",
        "current_stage": "verifying",
        "stage_trace": [
            {"stage": "coding_html", "agent": "HTMLCoder", "status": "completed"},
            {"stage": "verifying", "agent": "Verifier", "status": "completed"},
        ],
        "execution_checklist": [{"id": "verify", "title": "Verify", "owner": "Verifier", "status": "failed"}],
        "skill_trace": [{"id": "content_quality_review", "title": "Content quality review", "agent": "Verifier"}],
        "agent_artifacts": [
            {
                "agent": "Verifier",
                "stage": "verifying",
                "title": "Verification",
                "summary": "score 0.72",
                "data": {"ok": False, "retry_instruction": "Check source evidence."},
            }
        ],
        "error": {"code": "generation_v2_failed", "message": "Generation v2 did not produce a note proposal."},
        "retryable": True,
        "cancellable": False,
    }

    sync_v2_job_from_run(settings, str(job["job_id"]), run, status="failed")

    public_job = store.jobs.get(str(job["job_id"]))

    assert public_job["status"] == "failed"
    assert public_job["completed_at"] == "2026-07-02T01:02:03+00:00"
    assert public_job["cancellable"] is False
    assert public_job["current_stage"] == "verifying"
    assert public_job["error"]["message"] == "Generation v2 did not produce a note proposal."
    assert public_job["execution_checklist"][0]["status"] == "failed"
    assert public_job["agent_artifacts"][0]["agent"] == "Verifier"


def test_write_gateway_writes_generated_note_and_rebuilds(tmp_path) -> None:
    calls: list[dict[str, object]] = []
    settings = ServerSettings(
        content_dir=tmp_path / "content",
        meta_dir=tmp_path / "meta",
        public_dir=tmp_path / "public",
        site_title="Test",
        max_upload_bytes=1024 * 1024,
    )
    settings.content_dir.mkdir(parents=True)
    settings.public_dir.mkdir(parents=True)

    def build_fn(**kwargs: object) -> dict[str, object]:
        calls.append(kwargs)
        return {}

    proposal = CreateNoteProposal(
        title="My Generated Note",
        html="<!doctype html><html><head><title>My Generated Note</title></head><body><h1>Done</h1></body></html>",
        metadata=NoteMetadataProposal(title="My Generated Note", summary="Summary", collection="inbox", tags=["AI"]),
        generation_trace_id="run-1",
    )

    result = WriteGateway(settings, build_fn=build_fn).write(proposal)

    assert result.item_id.startswith("generated/")
    assert Path(result.content_path).exists()
    assert Path(result.metadata_path).exists()
    assert "title: My Generated Note" in Path(result.metadata_path).read_text(encoding="utf-8")
    assert calls and calls[0]["site_title"] == "Test"


def test_write_gateway_links_note_to_private_job_workspace(tmp_path) -> None:
    calls: list[dict[str, object]] = []
    settings = ServerSettings(
        content_dir=tmp_path / "content",
        meta_dir=tmp_path / "meta",
        public_dir=tmp_path / "public",
        site_title="Test",
        max_upload_bytes=1024 * 1024,
    )
    settings.content_dir.mkdir(parents=True)
    settings.public_dir.mkdir(parents=True)

    parsed = merge_parsed_documents(
        [
            ParsedDocument(source_files=[SourceFile(filename="A.md")], plain_text="Alpha source"),
            ParsedDocument(source_files=[SourceFile(filename="B.md")], plain_text="Beta source"),
        ],
    )
    bundle = build_material_bundle(parsed, run_id="run-bundle")
    reference = write_job_material_bundle(settings, bundle, job_id="ai_job_write")
    proposal = CreateNoteProposal(
        title="Bundle Note",
        html="<!doctype html><html><head><title>Bundle Note</title></head><body><h1>Done</h1></body></html>",
        metadata=NoteMetadataProposal(title="Bundle Note"),
        generation_trace_id="run-bundle",
    )

    result = WriteGateway(settings, build_fn=lambda **kwargs: calls.append(kwargs)).write(proposal, workspace_reference=reference)

    metadata_text = Path(result.metadata_path).read_text(encoding="utf-8")
    assert "workspace:" in metadata_text
    assert "job_id: ai_job_write" in metadata_text
    workspace_dir = settings.meta_dir / "ai" / "generation-jobs" / "ai_job_write" / "workspace"
    merged_path = workspace_dir / "materials" / "merged.md"
    manifest_path = workspace_dir / "materials" / "manifest.json"
    assert merged_path.read_text(encoding="utf-8").startswith("Source file: A.md")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["job_id"] == "ai_job_write"
    assert [item["filename"] for item in manifest["materials"]] == ["A.md", "B.md"]
    assert manifest["materials"][0]["content_sha256"]
    assert not (settings.public_dir / "ai" / "generation-jobs").exists()
    assert calls


def test_generation_v2_job_material_bundle_round_trips_from_reference(tmp_path) -> None:
    settings = ServerSettings(
        content_dir=tmp_path / "content",
        meta_dir=tmp_path / "meta",
        public_dir=tmp_path / "public",
        site_title="Test",
        max_upload_bytes=1024 * 1024,
    )
    parsed = merge_parsed_documents([ParsedDocument(source_files=[SourceFile(filename="source.md")], plain_text="Job source body")])
    bundle = build_material_bundle(parsed, run_id="run-job")
    assert bundle is not None

    reference = write_job_material_bundle(settings, bundle, job_id="ai_job_test")
    restored = read_material_bundle_reference(settings, reference)

    assert reference.workspace_path == "ai/generation-jobs/ai_job_test/workspace"
    assert reference.merged_path == "ai/generation-jobs/ai_job_test/workspace/materials/merged.md"
    assert restored is not None
    assert restored.merged_text == bundle.merged_text
    assert restored.manifest["job_id"] == "ai_job_test"


def test_generation_v2_expired_job_workspace_cleanup_keeps_recent_failures(tmp_path) -> None:
    settings = ServerSettings(
        content_dir=tmp_path / "content",
        meta_dir=tmp_path / "meta",
        public_dir=tmp_path / "public",
        site_title="Test",
        max_upload_bytes=1024 * 1024,
    )
    recent = settings.meta_dir / "ai" / "generation-jobs" / "recent" / "workspace"
    old = settings.meta_dir / "ai" / "generation-jobs" / "old" / "workspace"
    recent.mkdir(parents=True)
    old.mkdir(parents=True)
    old_time = time.time() - 8 * 24 * 60 * 60
    os.utime(old, (old_time, old_time))

    removed = cleanup_expired_failed_job_workspaces(settings, keep_days=7)

    assert removed == 1
    assert recent.exists()
    assert not old.exists()


def test_write_gateway_rolls_back_html_when_build_fails(tmp_path) -> None:
    settings = ServerSettings(
        content_dir=tmp_path / "content",
        meta_dir=tmp_path / "meta",
        public_dir=tmp_path / "public",
        site_title="Test",
        max_upload_bytes=1024 * 1024,
    )
    settings.content_dir.mkdir(parents=True)
    settings.public_dir.mkdir(parents=True)

    def build_fn(**_kwargs: object) -> None:
        raise RuntimeError("build failed")

    proposal = CreateNoteProposal(
        title="Rollback Note",
        html="<!doctype html><html><head><title>Rollback Note</title></head><body><h1>Rollback</h1></body></html>",
        metadata=NoteMetadataProposal(title="Rollback Note", collection="inbox"),
        generation_trace_id="run-rollback",
    )

    try:
        WriteGateway(settings, build_fn=build_fn).write(proposal)
    except WriteGatewayError:
        pass
    else:
        raise AssertionError("WriteGatewayError was expected.")

    assert not list(settings.content_dir.rglob("*.html"))
    assert settings.meta_dir is not None
    assert not list(settings.meta_dir.rglob("*.yml"))


def test_generation_v2_html_safety_blocks_scripts_handlers_css_and_secrets() -> None:
    assert scan_html_safety("<!doctype html><html><body><h1>Safe</h1><a href=\"#a\">Jump</a></body></html>")["ok"] is True
    script = scan_html_safety("<html><body><script>alert(1)</script></body></html>")
    handler = scan_html_safety("<html><body><div onclick=\"steal()\">Bad</div></body></html>")
    css = scan_html_safety("<html><head><style>@import url(https://example.test/a.css)</style></head><body></body></html>")
    secret = scan_html_safety("<html><body>sk-test-secret-value-123456</body></html>")

    assert "blocked-tag:script" in script["reasons"]
    assert "inline-event-handler" in handler["reasons"]
    assert "css-import" in css["reasons"]
    assert "sensitive-secret" in secret["reasons"]


def test_generation_v2_visual_check_disabled_and_empty_html_paths() -> None:
    disabled = run_visual_check("<!doctype html><html><body><p>Ok</p></body></html>", mode="off")
    assert disabled.skipped is True
    assert disabled.ok is True

    empty = run_visual_check("", mode="basic")
    assert empty.skipped is False
    assert empty.ok is False
    assert empty.issues[0].code == "empty_html"


def test_generation_v2_visual_check_reports_layout_observations_without_hard_fail() -> None:
    html = """<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  body{margin:0;font-family:sans-serif}.page{max-width:1120px;margin:0 auto;padding:24px}
  section{margin:18px 0;padding:18px;border:1px solid #ddd}.wide{width:100%}.narrow{max-width:620px}
</style></head><body><main class="page">
<section class="wide"><h1>Wide section</h1><p>This report section uses the primary canvas with enough body text to be measured.</p></section>
<section class="narrow"><h2>Narrow section</h2><p>This peer section is much narrower than the main canvas and should be observed.</p></section>
<section class="wide"><h2>Another wide section</h2><p>This report section returns to the primary canvas with more visible text.</p></section>
<section class="narrow"><h2>Second narrow section</h2><p>This second narrow peer section makes the layout system drift observable.</p></section>
<section class="wide"><h2>Final wide section</h2><p>This report section uses the full canvas again for comparison.</p></section>
</main></body></html>"""

    report = run_visual_check(html, mode="basic", timeout_seconds=5)

    if report.skipped:
        assert report.reason
        return
    assert report.ok is True
    assert any(issue.code == "section_width_inconsistency" for issue in report.issues)


def test_write_gateway_blocks_unsafe_html_without_writing(tmp_path) -> None:
    settings = ServerSettings(
        content_dir=tmp_path / "content",
        meta_dir=tmp_path / "meta",
        public_dir=tmp_path / "public",
        site_title="Test",
        max_upload_bytes=1024 * 1024,
    )
    settings.content_dir.mkdir(parents=True)
    settings.public_dir.mkdir(parents=True)

    proposal = CreateNoteProposal(
        title="Unsafe Generated Note",
        html="<!doctype html><html><body><script>alert(1)</script></body></html>",
        metadata=NoteMetadataProposal(title="Unsafe Generated Note"),
    )

    try:
        WriteGateway(settings).write(proposal)
    except WriteGatewayError as exc:
        assert "failed safety checks" in str(exc)
    else:
        raise AssertionError("WriteGatewayError was expected.")

    assert not list(settings.content_dir.rglob("*.html"))
    assert settings.meta_dir is not None
    assert not list(settings.meta_dir.rglob("*.yml"))


def test_material_generation_v2_runner_writes_note_and_run(tmp_path) -> None:
    settings = ServerSettings(
        content_dir=tmp_path / "content",
        meta_dir=tmp_path / "meta",
        public_dir=tmp_path / "public",
        site_title="Test",
        max_upload_bytes=1024 * 1024,
        ai_generation_engine="v2",
        document_parser="basic",
    )
    settings.content_dir.mkdir(parents=True)
    settings.public_dir.mkdir(parents=True)

    result = generate_note_from_material_v2(
        settings=settings,
        filename="source.md",
        content=b"# Source\n\nGenerated body with private runner evidence.",
        instruction="Create HTML.",
        spec=GenerationSpec(),
    )

    assert result["run"]["generation_engine"] == "v2"
    assert result["run"]["graph"] == "HtmlGenerationV2.alpha"
    assert result["run"]["item_id"].startswith("generated/")
    assert result["item"]["id"] == result["run"]["item_id"]
    assert (settings.content_dir / result["item"]["id"]).exists()
    assert "content" not in result["run"]["spec"]
    raw_run = json.dumps(result["run"], ensure_ascii=False)
    assert "temporary_material_context" not in raw_run
    assert "material_recall_results" not in raw_run
    assert "private runner evidence" not in raw_run
    assert settings.meta_dir is not None
    metadata_path = settings.meta_dir / "items" / Path(result["item"]["id"]).with_suffix(".yml")
    metadata_text = metadata_path.read_text(encoding="utf-8")
    assert "workspace:" in metadata_text
    workspace_root = settings.meta_dir / "ai" / "generation-jobs"
    manifests = list(workspace_root.rglob("workspace/materials/manifest.json"))
    assert len(manifests) == 1
    manifest = json.loads(manifests[0].read_text(encoding="utf-8"))
    assert str(manifest["job_id"]).startswith("run_")
    assert "private runner evidence" in (manifests[0].parent / "merged.md").read_text(encoding="utf-8")

    stored = AIRunStore(settings).add(result["run"])
    assert stored["skill_trace"][0]["id"] == "html_page_design"
    assert stored["skill_trace"][0]["agent"] == "StyleDesigner"


def test_material_generation_v2_runner_writes_job_bundle_before_note_bundle(tmp_path) -> None:
    settings = ServerSettings(
        content_dir=tmp_path / "content",
        meta_dir=tmp_path / "meta",
        public_dir=tmp_path / "public",
        site_title="Test",
        max_upload_bytes=1024 * 1024,
        ai_generation_engine="v2",
        document_parser="basic",
    )
    settings.content_dir.mkdir(parents=True)
    settings.public_dir.mkdir(parents=True)
    references = []

    result = generate_note_from_material_v2(
        settings=settings,
        filename="source.md",
        content=b"# Source\n\nStable job bundle source.",
        instruction="Create HTML.",
        spec=GenerationSpec(),
        job_id="ai_job_bundle",
        on_material_bundle_ready=references.append,
    )

    assert len(references) == 1
    assert references[0].manifest_path == "ai/generation-jobs/ai_job_bundle/workspace/materials/manifest.json"
    job_manifest = json.loads((settings.meta_dir / references[0].manifest_path).read_text(encoding="utf-8"))
    assert job_manifest["job_id"] == "ai_job_bundle"
    workspace_root = settings.meta_dir / "ai" / "generation-jobs" / "ai_job_bundle" / "workspace"
    trace_artifacts = workspace_root / "trace" / "agent_artifacts.jsonl"
    content_artifact = workspace_root / "artifacts" / "content_draft.json"
    html_artifact = workspace_root / "artifacts" / "html_draft.html"
    assert trace_artifacts.exists()
    assert "ContentWriter" in trace_artifacts.read_text(encoding="utf-8")
    assert content_artifact.exists()
    assert json.loads(content_artifact.read_text(encoding="utf-8"))["title"]
    assert html_artifact.exists()
    assert "<!doctype html" in html_artifact.read_text(encoding="utf-8").lower()


def test_material_generation_v2_provider_failure_returns_sanitized_failed_run(tmp_path) -> None:
    settings = ServerSettings(
        content_dir=tmp_path / "content",
        meta_dir=tmp_path / "meta",
        public_dir=tmp_path / "public",
        site_title="Test",
        max_upload_bytes=1024 * 1024,
        ai_generation_engine="v2",
        document_parser="basic",
    )
    settings.content_dir.mkdir(parents=True)
    settings.public_dir.mkdir(parents=True)

    class FailingGenerationModel:
        def complete_json(self, *, node, schema_name, payload, attempt=0):
            raise RuntimeError("provider unavailable")

        def complete_text(self, *, node, payload, attempt=0):
            raise RuntimeError("provider unavailable")

    try:
        generate_note_from_material_v2(
            settings=settings,
            filename="private.md",
            content=b"# Private\n\nSecret source body.",
            instruction="Create HTML.",
            spec=GenerationSpec(),
            model_client=FailingGenerationModel(),
        )
    except MaterialGenerationError as exc:
        run = exc.run
    else:
        raise AssertionError("MaterialGenerationError was expected.")

    assert run["status"] == "failed"
    assert run["generation_engine"] == "v2"
    assert run["error"]["code"] == "generation_v2_failed"
    assert "Secret source body" not in str(run)
    assert not list(settings.content_dir.rglob("*.html"))
