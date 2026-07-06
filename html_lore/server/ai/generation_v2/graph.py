from __future__ import annotations

from dataclasses import asdict, replace
from typing import Any, Callable
from uuid import uuid4

from .agents.content_writer import ContentWriterAgent
from .agents.finalizer import FinalizerAgent
from .agents.html_coder import HTMLCoderAgent
from .agents.planner import PlannerAgent
from .agents.requirement_analyst import RequirementAnalystAgent
from .agents.safety_reviewer import SafetyReviewerAgent
from .agents.style_designer import StyleDesignerAgent
from .agents.verifier import VerifierAgent
from .fake_model import FakeGenerationModelClient
from .material_context import build_material_index, build_temporary_material_context
from .model_client import GenerationJsonModelClient
from .orchestrator import GenerationOrchestrator
from .schemas import AgentArtifact, GenerationInput, GenerationStage, GenerationState, ParsedDocument, ParsedMaterialItem, ParseWarning, SourceFile
from .state import complete_stage, fail_stage, start_stage
from .tools.document_parser import parse_document
from .tools.document_parser import blocking_parse_failure_reason
from .tools.style_hint_extractor import extract_style_hints
from .tools.visual_check import run_visual_check


StateCallback = Callable[[GenerationState], None]
WorkspaceWriter = Callable[[GenerationState, str, Any, str], None]


class HtmlGenerationV2Graph:
    name = "HtmlGenerationV2.alpha"

    def __init__(
        self,
        *,
        model_client: GenerationJsonModelClient | None = None,
        parser_mode: str = "markitdown",
        on_state: StateCallback | None = None,
        workspace_writer: WorkspaceWriter | None = None,
        visual_check_mode: str = "off",
        visual_check_browser_channel: str = "chrome",
        visual_check_timeout_seconds: int = 20,
    ) -> None:
        self.model_client = model_client or FakeGenerationModelClient()
        self.parser_mode = parser_mode
        self.on_state = on_state
        self.workspace_writer = workspace_writer
        self.visual_check_mode = str(visual_check_mode or "off")
        self.visual_check_browser_channel = str(visual_check_browser_channel or "chrome")
        self.visual_check_timeout_seconds = max(1, int(visual_check_timeout_seconds or 20))
        self.orchestrator = GenerationOrchestrator()
        self.agents = {
            "requirement_analyst": RequirementAnalystAgent(self.model_client, workspace_writer=workspace_writer),
            "planner": PlannerAgent(self.model_client, workspace_writer=workspace_writer),
            "content_writer": ContentWriterAgent(self.model_client, workspace_writer=workspace_writer),
            "style_designer": StyleDesignerAgent(self.model_client, workspace_writer=workspace_writer),
            "html_coder": HTMLCoderAgent(self.model_client, workspace_writer=workspace_writer),
            "verifier": VerifierAgent(self.model_client, workspace_writer=workspace_writer),
            "safety_reviewer": SafetyReviewerAgent(self.model_client, workspace_writer=workspace_writer),
            "finalizer": FinalizerAgent(self.model_client, workspace_writer=workspace_writer),
        }

    def initial_state(self, generation_input: GenerationInput, *, job_id: str = "", run_id: str = "") -> GenerationState:
        return GenerationState(job_id=job_id, run_id=run_id or uuid4().hex, input=generation_input)

    def run(self, state: GenerationState) -> GenerationState:
        next_state = state
        for _ in range(32):
            decision = self.orchestrator.decide_next(next_state)
            if decision.next_node == "write_gateway":
                return replace(next_state, current_step=GenerationStage.COMPLETED.value)
            if decision.next_node == "max_revision_rounds":
                return replace(next_state, failed_steps=[*next_state.failed_steps, decision.next_node])
            if decision.next_node == "verifier_protocol_retry":
                retries = dict(next_state.same_node_retries)
                retries["VerifierProtocol"] = retries.get("VerifierProtocol", 0) + 1
                next_state = replace(next_state, validation_report=None, same_node_retries=retries)
                continue
            if decision.next_node in {"verifier_invalid_output", "verifier_blocked"}:
                return replace(next_state, failed_steps=[*next_state.failed_steps, decision.next_node])
            if decision.next_node == "ingest":
                next_state = self.run_ingest(next_state)
                self.emit_state(next_state)
                if next_state.failed_steps:
                    return next_state
                continue
            agent = self.agents.get(decision.next_node)
            if agent is None:
                return replace(next_state, failed_steps=[*next_state.failed_steps, decision.next_node])
            next_state = replace(next_state, current_step=agent.stage.value)
            self.emit_state(next_state)
            result = agent.run(next_state)
            next_state = result.state
            self.emit_state(next_state)
            if next_state.failed_steps:
                return next_state
            if decision.next_node == "html_coder":
                next_state = self.run_visual_check(next_state)
                self.emit_state(next_state)
        return replace(next_state, failed_steps=[*next_state.failed_steps, "max_graph_steps"])

    def emit_state(self, state: GenerationState) -> None:
        if self.on_state is None:
            return
        self.on_state(state)

    def run_ingest(self, state: GenerationState) -> GenerationState:
        next_state = start_stage(state, GenerationStage.PARSING, agent="Ingest", message="Parsing uploaded material.")
        parsed_items = []
        parse_failures = []
        for material in material_inputs(state):
            filename = str(material.get("filename") or "source.txt")
            content_type = str(material.get("content_type") or "")
            parsed = parse_document(
                filename=filename,
                content=material.get("content") if isinstance(material.get("content"), bytes) else b"",
                content_type=content_type,
                parser_mode=self.parser_mode,
            )
            parsed_items.append(parsed)
            reason = blocking_parse_failure_reason(parsed, filename=filename, content_type=content_type)
            if reason:
                parse_failures.append({"filename": filename, "reason": reason})
        parsed = merge_parsed_documents(parsed_items)
        parsed = replace(parsed, style_hints=extract_style_hints(parsed, role="material"))
        material_index = build_material_index(parsed, instruction=state.input.instruction)
        temporary_material_context = build_temporary_material_context(parsed, instruction=state.input.instruction)
        if parse_failures:
            failed_state = replace(
                next_state,
                parsed_document=parsed,
                material_index=material_index,
                temporary_material_context=temporary_material_context,
            )
            metadata = {
                "file_count": len(temporary_material_context.files),
                "total_chars": temporary_material_context.total_chars,
                "selected_chunks": len(temporary_material_context.selected_chunks),
                "selected_chars": temporary_material_context.selected_chars,
                "parse_failures": parse_failures,
            }
            message = "; ".join(item["reason"] for item in parse_failures[:3])
            failed_state = fail_stage(failed_state, GenerationStage.PARSING, message=message, retryable=True, metadata=metadata)
            return replace(failed_state, current_step=GenerationStage.PARSE_FAILED.value, failed_steps=[GenerationStage.PARSE_FAILED.value])
        parsed_style_reference = None
        if state.input.reference_style == "file" and state.input.reference_file_name and state.input.reference_content:
            parsed_style_reference = parse_document(
                filename=state.input.reference_file_name,
                content=state.input.reference_content,
                content_type=state.input.reference_file_type,
                reference_role="style_reference",
                parser_mode=self.parser_mode,
            )
            parsed_style_reference = replace(parsed_style_reference, style_hints=extract_style_hints(parsed_style_reference, role="style_reference"))
        next_state = replace(
            next_state,
            parsed_document=parsed,
            material_index=material_index,
            temporary_material_context=temporary_material_context,
            parsed_style_reference=parsed_style_reference,
        )
        metadata = {
            "file_count": len(temporary_material_context.files),
            "total_chars": temporary_material_context.total_chars,
            "selected_chunks": len(temporary_material_context.selected_chunks),
            "selected_chars": temporary_material_context.selected_chars,
        }
        return complete_stage(next_state, GenerationStage.PARSING, message="Uploaded material parsed.", metadata=metadata)

    def run_visual_check(self, state: GenerationState) -> GenerationState:
        if state.html_draft is None:
            return state
        report = run_visual_check(
            state.html_draft.html,
            mode=self.visual_check_mode,
            browser_channel=self.visual_check_browser_channel,
            timeout_seconds=self.visual_check_timeout_seconds,
        )
        if report.mode == "off":
            return replace(state, visual_check_report=report)
        summary = "skipped"
        if not report.skipped:
            summary = "passed" if report.ok else "issues found"
        artifact = AgentArtifact(
            agent="VisualCheckTool",
            stage=GenerationStage.VERIFYING,
            title="Browser visual check",
            summary=summary,
            input_summary="HTML draft rendered in browser viewports",
            output_summary=visual_check_output_summary(report),
            quality_score=1.0 if report.ok else 0.55,
            warnings=[issue.message for issue in report.issues[:4] if issue.severity != "error"] + report.warnings[:4],
            data={
                "mode": report.mode,
                "available": report.available,
                "skipped": report.skipped,
                "ok": report.ok,
                "reason": report.reason,
                "duration_ms": report.duration_ms,
                "viewports": [asdict(item) for item in report.viewports],
                "issues": [asdict(item) for item in report.issues[:12]],
            },
        )
        return replace(state, visual_check_report=report, agent_artifacts=[*state.agent_artifacts, artifact])


def visual_check_output_summary(report) -> str:
    if report.skipped:
        return report.reason or "Visual check skipped"
    if not report.issues:
        return "passed: rendered, no blocking visual issues"
    return f"{len(report.issues)} visual issue(s): " + "; ".join(issue.code for issue in report.issues[:3])


def material_inputs(state: GenerationState) -> list[dict[str, object]]:
    materials = [item for item in state.input.materials if isinstance(item, dict)]
    if materials:
        return materials
    return [{"filename": state.input.filename or "source.txt", "content": state.input.content, "content_type": state.input.content_type}]


def merge_parsed_documents(items: list[ParsedDocument]) -> ParsedDocument:
    if not items:
        return ParsedDocument(warnings=[ParseWarning(code="no_material", message="No uploaded material was available to parse.", severity="warning")])
    annotated_items = [annotate_parsed_material(item, index) for index, item in enumerate(items, start=1)]
    if len(annotated_items) == 1:
        item = annotated_items[0]
        material = parsed_material_item(item, 1, start_char=0, end_char=len(item.plain_text), content_start_char=0, content_end_char=len(item.plain_text))
        return replace(item, materials=[material])
    text_parts: list[str] = []
    source_files = []
    outline = []
    images = []
    links = []
    tables = []
    style_hints = []
    warnings = []
    materials = []
    cursor = 0
    for index, item in enumerate(annotated_items, start=1):
        source_files.extend(item.source_files)
        label = item.source_files[0].filename if item.source_files else f"material-{index}"
        if item.plain_text:
            if text_parts:
                cursor += 2
            header = f"Source file: {label}\n"
            part = f"{header}{item.plain_text}"
            start_char = cursor
            content_start_char = start_char + len(header)
            content_end_char = content_start_char + len(item.plain_text)
            end_char = start_char + len(part)
            text_parts.append(part)
            materials.append(
                parsed_material_item(
                    item,
                    index,
                    start_char=start_char,
                    end_char=end_char,
                    content_start_char=content_start_char,
                    content_end_char=content_end_char,
                )
            )
            cursor = end_char
        outline.extend(item.outline)
        images.extend(item.images)
        links.extend(item.links)
        tables.extend(item.tables)
        style_hints.extend(item.style_hints)
        warnings.extend(item.warnings)
    warnings.append(ParseWarning(code="multiple_materials", message=f"Parsed {len(items)} uploaded material files.", severity="info"))
    return ParsedDocument(
        source_files=source_files,
        plain_text="\n\n".join(text_parts),
        outline=outline,
        images=images,
        links=links,
        tables=tables,
        style_hints=style_hints,
        warnings=warnings,
        materials=materials,
    )


def annotate_parsed_material(item: ParsedDocument, index: int) -> ParsedDocument:
    source = item.source_files[0] if item.source_files else None
    file_id = source.file_id if source and source.file_id else f"file-{index}"
    filename = source.filename if source and source.filename else f"material-{index}"
    content_type = source.content_type if source else ""
    size = source.size if source else 0
    role = source.role if source else "material"
    source_files = [replace(file, file_id=file.file_id or file_id, file_index=file.file_index or index) for file in item.source_files]
    if not source_files:
        source_files = [SourceFile(filename=filename, content_type=content_type, size=size, role=role, file_id=file_id, file_index=index)]
    return replace(
        item,
        source_files=source_files,
        outline=[replace(entry, file_id=entry.file_id or file_id, filename=entry.filename or filename, file_index=entry.file_index or index) for entry in item.outline],
        images=[replace(entry, file_id=entry.file_id or file_id, filename=entry.filename or filename, file_index=entry.file_index or index) for entry in item.images],
        links=[replace(entry, file_id=entry.file_id or file_id, filename=entry.filename or filename, file_index=entry.file_index or index) for entry in item.links],
        tables=[replace(entry, file_id=entry.file_id or file_id, filename=entry.filename or filename, file_index=entry.file_index or index) for entry in item.tables],
        materials=[],
    )


def parsed_material_item(
    item: ParsedDocument,
    index: int,
    *,
    start_char: int,
    end_char: int,
    content_start_char: int,
    content_end_char: int,
) -> ParsedMaterialItem:
    source = item.source_files[0] if item.source_files else None
    file_id = source.file_id if source and source.file_id else f"file-{index}"
    filename = source.filename if source and source.filename else f"material-{index}"
    return ParsedMaterialItem(
        file_id=file_id,
        file_index=source.file_index if source and source.file_index else index,
        filename=filename,
        content_type=source.content_type if source else "",
        size=source.size if source else 0,
        start_char=start_char,
        end_char=end_char,
        content_start_char=content_start_char,
        content_end_char=content_end_char,
        char_count=max(0, content_end_char - content_start_char),
    )
