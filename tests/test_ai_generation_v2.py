from __future__ import annotations

from pathlib import Path

from html_lore.server.ai.generation_v2.graph import HtmlGenerationV2Graph
from html_lore.server.ai.generation_v2.fake_model import FakeGenerationModelClient
from html_lore.server.ai.generation_v2.material_runner import generate_note_from_material_v2
from html_lore.server.ai.generation_v2.model_client import ProviderGenerationModelClient, extract_json_object, public_generation_state_for_agent
from html_lore.server.ai.generation_v2.model_profile import DEFAULT_GENERATION_MODEL, GenerationModelProfile
from html_lore.server.ai.generation_v2.schemas import ChecklistItem, ChecklistStatus, ContentDraft, ContentSection, CreateNoteProposal, DesignMode, GenerationInput, GenerationJobStatus, GenerationStage, GenerationState, HtmlDraft, NoteMetadataProposal, ParsedDocument, StageTraceEvent
from html_lore.server.ai.generation_v2.skills.loader import load_default_skills_for_agent
from html_lore.server.ai.generation_v2.state import complete_stage, start_stage
from html_lore.server.ai.generation_v2.store import GenerationStore
from html_lore.server.ai.generation_v2.tools import document_parser
from html_lore.server.ai.generation_v2.tools.document_parser import parse_document, parse_document_basic
from html_lore.server.ai.generation_v2.tools.html_safety import scan_html_safety
from html_lore.server.ai.generation_v2.tools.style_hint_extractor import extract_style_hints
from html_lore.server.ai.generation_v2.write_gateway import WriteGateway, WriteGatewayError
from html_lore.server.ai.html_generation import GenerationSpec
from html_lore.server.ai.jobs import AIJobStore
from html_lore.server.ai.material_generation import MaterialGenerationError
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
    assert result.requirement_brief is not None
    assert result.plan_draft is not None
    assert result.content_draft is not None
    assert result.style_brief is not None
    assert result.html_draft is not None
    assert result.validation_report is not None and result.validation_report.ok
    assert result.safety_report is not None and result.safety_report.ok
    assert result.create_note_proposal is not None
    assert result.create_note_proposal.target_collection == "inbox"
    assert "<!doctype html>" in result.create_note_proposal.html
    assert "finalizing" in result.completed_steps
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


def test_generation_v2_skill_loader_uses_fixed_default_mapping() -> None:
    assert [skill.id for skill in load_default_skills_for_agent("StyleDesigner")] == ["html_page_design"]
    assert [skill.id for skill in load_default_skills_for_agent("HTMLCoder")] == ["safe_static_html"]
    assert [skill.id for skill in load_default_skills_for_agent("Verifier")] == ["content_quality_review"]
    assert load_default_skills_for_agent("Planner") == ()


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
    def __init__(self, content: str) -> None:
        self.content = content
        self.messages = []

    def chat(self, *, messages, temperature=0.2, max_tokens=1024):
        self.messages = messages
        return {"content": self.content, "model": "fake", "usage": {}}


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


def test_generation_v2_stops_when_validation_revisions_do_not_converge() -> None:
    graph = HtmlGenerationV2Graph(model_client=AlwaysReviseVerifierClient(), parser_mode="basic")
    state = graph.initial_state(
        GenerationInput(filename="source.txt", content=b"Source text", content_type="text/plain", instruction="Create HTML."),
        job_id="job-1",
    )

    result = graph.run(state)

    assert "max_revision_rounds" in result.failed_steps
    assert result.revision_round == 2


def test_generation_v2_provider_model_client_extracts_json_and_includes_schema() -> None:
    chat_client = RecordingChatClient('```json\n{"user_goal":"Create a note","target_use":"default"}\n```')
    client = ProviderGenerationModelClient(chat_client, max_prompt_chars=4000, max_tokens=512)

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


def test_generation_v2_extract_json_object_from_plain_text() -> None:
    assert extract_json_object("Here is JSON:\n{\"ok\":true}\nDone.") == '{"ok":true}'


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
    monkeypatch.delenv("HTML_LORE_DOCUMENT_PARSER", raising=False)

    settings = load_settings()

    assert settings.ai_generation_engine == "legacy"
    assert settings.ai_generation_model == DEFAULT_GENERATION_MODEL
    assert settings.document_parser == "markitdown"


def test_generation_config_accepts_v2(monkeypatch) -> None:
    monkeypatch.setenv("HTML_LORE_AI_GENERATION_ENGINE", "v2")
    monkeypatch.setenv("HTML_LORE_AI_GENERATION_MODEL", "custom-generation-model")
    monkeypatch.setenv("HTML_LORE_DOCUMENT_PARSER", "basic")

    settings = load_settings()

    assert settings.ai_generation_engine == "v2"
    assert settings.ai_generation_model == "custom-generation-model"
    assert settings.document_parser == "basic"


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

    public_job = AIJobStore(settings).get(job_id)

    assert public_job["generation_engine"] == "v2"
    assert public_job["status"] == "running"
    assert public_job["current_stage"] == "parsing"
    assert public_job["stage_trace"][0]["agent"] == "Ingest"
    assert public_job["execution_checklist"][0]["id"] == "draft-content"


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
            "stage_trace": [{"stage": "completed", "agent": "Write Gateway", "status": "completed"}],
            "execution_checklist": [{"id": "verify", "title": "Verify", "owner": "Verifier", "status": "done"}],
        },
    )
    fetched = AIRunStore(settings).get("run-1")

    assert run["generation_engine"] == "v2"
    assert fetched["generation_engine"] == "v2"
    assert fetched["stage_trace"][0]["stage"] == "completed"
    assert fetched["execution_checklist"][0]["status"] == "completed"


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
        content=b"# Source\n\nGenerated body.",
        instruction="Create HTML.",
        spec=GenerationSpec(),
    )

    assert result["run"]["generation_engine"] == "v2"
    assert result["run"]["graph"] == "HtmlGenerationV2.alpha"
    assert result["run"]["item_id"].startswith("generated/")
    assert result["item"]["id"] == result["run"]["item_id"]
    assert (settings.content_dir / result["item"]["id"]).exists()
    assert "content" not in result["run"]["spec"]

    stored = AIRunStore(settings).add(result["run"])
    assert stored["skill_trace"][0]["id"] == "html_page_design"
    assert stored["skill_trace"][0]["agent"] == "StyleDesigner"


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
