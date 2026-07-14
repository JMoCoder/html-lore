from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class TextEnum(str, Enum):
    def __str__(self) -> str:
        return self.value


class GenerationEngine(TextEnum):
    LEGACY = "legacy"
    V2 = "v2"


class GenerationJobStatus(TextEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"
    CANCELING = "canceling"


class GenerationStage(TextEnum):
    QUEUED = "queued"
    PARSING = "parsing"
    PARSE_FAILED = "parse_failed"
    ANALYZING_REQUIREMENTS = "analyzing_requirements"
    PLANNING = "planning"
    WRITING_CONTENT = "writing_content"
    EXECUTING_TOOLS = "executing_tools"
    DESIGNING_STYLE = "designing_style"
    CODING_HTML = "coding_html"
    VERIFYING = "verifying"
    SAFETY_CHECKING = "safety_checking"
    FINALIZING = "finalizing"
    WRITING = "writing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class DesignMode(TextEnum):
    DEFAULT_FREE_DESIGN = "default_free_design"
    CONSTRAINED_DESIGN = "constrained_design"
    REFERENCE_GUIDED_DESIGN = "reference_guided_design"


class RiskLevel(TextEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    BLOCKED = "blocked"


class SourceHandlingMode(TextEnum):
    FREE_SYNTHESIS = "free_synthesis"
    SOURCE_GROUNDED_REWRITE = "source_grounded_rewrite"
    FAITHFUL_ADAPTATION = "faithful_adaptation"
    EXTRACTIVE_CONVERSION = "extractive_conversion"


class VerifierAction(TextEnum):
    PASS = "pass"
    REQUEST_EVIDENCE = "request_evidence"
    REQUEST_REVISION = "request_revision"
    BLOCKED = "blocked"


class RequirementDecision(TextEnum):
    CONTINUE = "continue"
    DEGRADED = "degraded"
    BLOCKED = "blocked"


class ChecklistStatus(TextEnum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    COMPLETED = "completed"
    WARNING = "warning"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class GenerationInput:
    instruction: str = ""
    filename: str = ""
    content: bytes = b""
    content_type: str = ""
    materials: list[dict[str, Any]] = field(default_factory=list)
    theme: str = "default"
    target_use: str = "default"
    style_preference: str = "default"
    audience: str = "default"
    reference_style: str = "default"
    reference_file_name: str = ""
    reference_content: bytes = b""
    reference_file_type: str = ""
    reference_file_size: int = 0
    target_collection: str = "inbox"
    source_type: str = "ai_generated"


@dataclass(frozen=True)
class SourceFile:
    filename: str = ""
    content_type: str = ""
    size: int = 0
    role: str = "material"
    file_id: str = ""
    file_index: int = 0


@dataclass(frozen=True)
class OutlineItem:
    level: int = 1
    title: str = ""
    text: str = ""
    file_id: str = ""
    filename: str = ""
    file_index: int = 0


@dataclass(frozen=True)
class DocumentImage:
    alt: str = ""
    description: str = ""
    source: str = ""
    file_id: str = ""
    filename: str = ""
    file_index: int = 0


@dataclass(frozen=True)
class DocumentLink:
    text: str = ""
    url: str = ""
    source: str = ""
    file_id: str = ""
    filename: str = ""
    file_index: int = 0


@dataclass(frozen=True)
class DocumentTable:
    title: str = ""
    headers: list[str] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)
    file_id: str = ""
    filename: str = ""
    file_index: int = 0


@dataclass(frozen=True)
class StyleHint:
    kind: str = ""
    value: str = ""
    confidence: float = 0.0


@dataclass(frozen=True)
class ParseWarning:
    code: str = ""
    message: str = ""
    severity: str = "warning"


@dataclass(frozen=True)
class ParsedMaterialItem:
    file_id: str = ""
    file_index: int = 0
    filename: str = ""
    content_type: str = ""
    size: int = 0
    start_char: int = 0
    end_char: int = 0
    content_start_char: int = 0
    content_end_char: int = 0
    char_count: int = 0


@dataclass(frozen=True)
class MaterialCapability:
    id: str = ""
    status: str = "unknown"
    count: int = 0
    detail: str = ""
    file_id: str = ""
    filename: str = ""
    file_index: int = 0


@dataclass(frozen=True)
class SpreadsheetCell:
    coordinate: str = ""
    value: Any = None
    formula: str = ""
    cached_value: Any = None
    data_type: str = ""
    number_format: str = ""


@dataclass(frozen=True)
class SpreadsheetSheet:
    title: str = ""
    state: str = "visible"
    max_row: int = 0
    max_column: int = 0
    merged_ranges: list[str] = field(default_factory=list)
    hidden_rows: list[int] = field(default_factory=list)
    hidden_columns: list[str] = field(default_factory=list)
    cells: list[SpreadsheetCell] = field(default_factory=list)
    truncated: bool = False


@dataclass(frozen=True)
class SpreadsheetWorkbook:
    file_id: str = ""
    file_index: int = 0
    filename: str = ""
    sheets: list[SpreadsheetSheet] = field(default_factory=list)
    defined_names: list[dict[str, Any]] = field(default_factory=list)
    external_links: list[str] = field(default_factory=list)
    cell_count: int = 0
    formula_count: int = 0
    truncated: bool = False


@dataclass(frozen=True)
class ParsedDocument:
    source_files: list[SourceFile] = field(default_factory=list)
    plain_text: str = ""
    outline: list[OutlineItem] = field(default_factory=list)
    images: list[DocumentImage] = field(default_factory=list)
    links: list[DocumentLink] = field(default_factory=list)
    tables: list[DocumentTable] = field(default_factory=list)
    style_hints: list[StyleHint] = field(default_factory=list)
    warnings: list[ParseWarning] = field(default_factory=list)
    materials: list[ParsedMaterialItem] = field(default_factory=list)
    capabilities: list[MaterialCapability] = field(default_factory=list)
    workbooks: list[SpreadsheetWorkbook] = field(default_factory=list)


@dataclass(frozen=True)
class MaterialChunk:
    id: str = ""
    file_index: int = 0
    filename: str = ""
    locator: str = ""
    heading: str = ""
    text: str = ""
    char_count: int = 0
    token_hints: list[str] = field(default_factory=list)
    score: float = 0.0


@dataclass(frozen=True)
class MaterialFileBrief:
    file_index: int = 0
    filename: str = ""
    content_type: str = ""
    size: int = 0
    char_count: int = 0
    chunk_count: int = 0
    headings: list[str] = field(default_factory=list)
    preview: str = ""
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class MaterialIndex:
    files: list[MaterialFileBrief] = field(default_factory=list)
    chunks: list[MaterialChunk] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    total_chars: int = 0


@dataclass(frozen=True)
class TemporaryMaterialContext:
    files: list[MaterialFileBrief] = field(default_factory=list)
    selected_chunks: list[MaterialChunk] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    total_chars: int = 0
    selected_chars: int = 0


@dataclass(frozen=True)
class MaterialQuery:
    id: str = ""
    query: str = ""
    purpose: str = ""
    target_files: list[str] = field(default_factory=list)
    expected_evidence: str = ""
    priority: str = "medium"


@dataclass(frozen=True)
class MaterialRecallResult:
    agent: str = ""
    query_id: str = ""
    query: str = ""
    purpose: str = ""
    chunks: list[MaterialChunk] = field(default_factory=list)
    total_chars: int = 0
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class MaterialReadRequest:
    id: str = ""
    action: str = "read_span"
    file_id: str = ""
    filename: str = ""
    offset: int = 0
    limit: int = 24000
    purpose: str = ""


@dataclass(frozen=True)
class MaterialReadResult:
    agent: str = ""
    request_id: str = ""
    action: str = ""
    file_id: str = ""
    filename: str = ""
    offset: int = 0
    end_offset: int = 0
    text: str = ""
    char_count: int = 0
    truncated: bool = False
    next_offset: int = 0
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class WorkbookInspectRequest:
    id: str = ""
    action: str = "list_sheets"
    file_id: str = ""
    filename: str = ""
    sheet: str = ""
    cell_range: str = ""
    coordinate: str = ""
    query: str = ""
    limit: int = 200
    purpose: str = ""


@dataclass(frozen=True)
class WorkbookInspectResult:
    agent: str = ""
    request_id: str = ""
    action: str = ""
    file_id: str = ""
    filename: str = ""
    sheet: str = ""
    records: list[dict[str, Any]] = field(default_factory=list)
    truncated: bool = False
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RequirementBrief:
    user_goal: str = ""
    target_use: str = "default"
    audience: str = ""
    output_type: str = "html_note"
    source_handling_mode: SourceHandlingMode = SourceHandlingMode.SOURCE_GROUNDED_REWRITE
    source_summary: str = ""
    must_include: list[str] = field(default_factory=list)
    should_avoid: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    style_preferences: list[str] = field(default_factory=list)
    reference_style_files: list[str] = field(default_factory=list)
    success_criteria: list[str] = field(default_factory=list)
    uncertainty: list[str] = field(default_factory=list)
    material_queries: list[MaterialQuery] = field(default_factory=list)
    material_read_requests: list[MaterialReadRequest] = field(default_factory=list)
    workbook_inspect_requests: list[WorkbookInspectRequest] = field(default_factory=list)
    decision: RequirementDecision = RequirementDecision.CONTINUE
    decision_reason: str = ""
    capability_gaps: list[str] = field(default_factory=list)
    accepted_degradations: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SectionPlan:
    id: str = ""
    title: str = ""
    purpose: str = ""
    source_refs: list[str] = field(default_factory=list)
    expected_content: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ToolNeed:
    # Legacy field name: in generation v2 this represents a registered
    # downstream skill/capability need, not a runtime tool invocation.
    tool_name: str = ""
    reason: str = ""
    priority: str = "medium"
    optional: bool = True


@dataclass(frozen=True)
class ChecklistItem:
    id: str = ""
    title: str = ""
    owner: str = ""
    status: ChecklistStatus = ChecklistStatus.PENDING
    acceptance: str = ""
    notes: str = ""


@dataclass(frozen=True)
class PlanDraft:
    page_goal: str = ""
    information_architecture: str = ""
    section_plan: list[SectionPlan] = field(default_factory=list)
    content_strategy: str = ""
    visual_strategy: str = ""
    # Kept as tool_needs for backward compatibility with existing jobs/artifacts.
    # Semantically these are Planner-selected skill/capability needs.
    tool_needs: list[ToolNeed] = field(default_factory=list)
    execution_checklist: list[ChecklistItem] = field(default_factory=list)
    risk_points: list[str] = field(default_factory=list)
    verification_targets: list[str] = field(default_factory=list)
    evidence_needs: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ContentSection:
    id: str = ""
    title: str = ""
    body: str = ""
    bullets: list[str] = field(default_factory=list)
    source_refs: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Callout:
    kind: str = "note"
    title: str = ""
    body: str = ""


@dataclass(frozen=True)
class Quote:
    text: str = ""
    source: str = ""


@dataclass(frozen=True)
class ContentDraft:
    title: str = ""
    subtitle: str = ""
    summary: str = ""
    sections: list[ContentSection] = field(default_factory=list)
    key_points: list[str] = field(default_factory=list)
    callouts: list[Callout] = field(default_factory=list)
    tables: list[DocumentTable] = field(default_factory=list)
    quotes: list[Quote] = field(default_factory=list)
    references_used: list[str] = field(default_factory=list)
    omitted_items: list[str] = field(default_factory=list)
    material_queries: list[MaterialQuery] = field(default_factory=list)
    material_read_requests: list[MaterialReadRequest] = field(default_factory=list)
    evidence_used: list[str] = field(default_factory=list)
    workbook_inspect_requests: list[WorkbookInspectRequest] = field(default_factory=list)


@dataclass(frozen=True)
class ColorToken:
    name: str = ""
    value: str = ""
    usage: str = ""


@dataclass(frozen=True)
class TypographySpec:
    font_family: str = ""
    heading_style: str = ""
    body_style: str = ""
    scale: str = ""


@dataclass(frozen=True)
class StyleBrief:
    style_goal: str = ""
    design_mode: DesignMode = DesignMode.DEFAULT_FREE_DESIGN
    reference_sources: list[str] = field(default_factory=list)
    color_palette: list[ColorToken] = field(default_factory=list)
    typography: TypographySpec = field(default_factory=TypographySpec)
    layout_system: str = ""
    component_style: str = ""
    density: str = ""
    visual_hierarchy: str = ""
    interaction_level: str = ""
    responsive_rules: list[str] = field(default_factory=list)
    avoid_styles: list[str] = field(default_factory=list)
    implementation_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class AssetRef:
    kind: str = ""
    src: str = ""
    description: str = ""


@dataclass(frozen=True)
class HtmlDraft:
    html: str = ""
    assets: list[AssetRef] = field(default_factory=list)
    css_notes: list[str] = field(default_factory=list)
    js_notes: list[str] = field(default_factory=list)
    render_assumptions: list[str] = field(default_factory=list)
    accessibility_notes: list[str] = field(default_factory=list)
    responsive_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CheckedItem:
    id: str = ""
    title: str = ""
    passed: bool = False
    notes: str = ""


@dataclass(frozen=True)
class ValidationIssue:
    code: str = ""
    message: str = ""
    severity: str = "warning"


@dataclass(frozen=True)
class VisualViewportReport:
    name: str = ""
    width: int = 0
    height: int = 0
    rendered: bool = False
    body_text_length: int = 0
    document_width: int = 0
    document_height: int = 0
    horizontal_overflow_px: int = 0
    blank_ratio: float = 0.0
    issue_count: int = 0


@dataclass(frozen=True)
class VisualCheckReport:
    mode: str = "off"
    available: bool = False
    ok: bool = True
    skipped: bool = True
    reason: str = ""
    checked_at: str = ""
    duration_ms: int = 0
    viewports: list[VisualViewportReport] = field(default_factory=list)
    issues: list[ValidationIssue] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ValidationReport:
    ok: bool = False
    verifier_action: VerifierAction = VerifierAction.REQUEST_REVISION
    score: float = 0.0
    checked_items: list[CheckedItem] = field(default_factory=list)
    issues: list[ValidationIssue] = field(default_factory=list)
    missing_parts: list[str] = field(default_factory=list)
    unsupported_claims: list[str] = field(default_factory=list)
    style_mismatch: list[str] = field(default_factory=list)
    structure_mismatch: list[str] = field(default_factory=list)
    route_back_to: str = ""
    retry_instruction: str = ""
    material_queries: list[MaterialQuery] = field(default_factory=list)
    material_read_requests: list[MaterialReadRequest] = field(default_factory=list)
    workbook_inspect_requests: list[WorkbookInspectRequest] = field(default_factory=list)


@dataclass(frozen=True)
class SafetyIssue:
    code: str = ""
    message: str = ""
    severity: str = "warning"
    location: str = ""


@dataclass(frozen=True)
class SafetyReport:
    ok: bool = False
    risk_level: RiskLevel = RiskLevel.LOW
    issues: list[SafetyIssue] = field(default_factory=list)
    blocked_items: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    route_back_to: str = ""
    requires_user_confirmation: bool = False


@dataclass(frozen=True)
class NoteMetadataProposal:
    title: str = ""
    summary: str = ""
    collection: str = "inbox"
    tags: list[str] = field(default_factory=list)
    source_type: str = "ai_generated"
    created_by: str = "ai_generation_v2"


@dataclass(frozen=True)
class CreateNoteProposal:
    title: str = ""
    html: str = ""
    metadata: NoteMetadataProposal = field(default_factory=NoteMetadataProposal)
    target_collection: str = "inbox"
    tags: list[str] = field(default_factory=list)
    source_files: list[str] = field(default_factory=list)
    source_links: list[str] = field(default_factory=list)
    safety_summary: str = ""
    generation_trace_id: str = ""


@dataclass(frozen=True)
class StageTraceEvent:
    stage: GenerationStage = GenerationStage.QUEUED
    agent: str = ""
    status: str = "started"
    started_at: str = ""
    completed_at: str = ""
    duration_ms: int = 0
    message: str = ""
    error_summary: str = ""
    retryable: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SkillTraceEntry:
    id: str = ""
    title: str = ""
    agent: str = ""
    version: str = ""
    source: str = "local"
    kind: str = "default"
    trigger_reason: str = ""


@dataclass(frozen=True)
class AgentArtifact:
    agent: str = ""
    stage: GenerationStage = GenerationStage.QUEUED
    title: str = ""
    summary: str = ""
    input_summary: str = ""
    output_summary: str = ""
    quality_score: float = 0.0
    usage: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GenerationState:
    schema_version: int = 1
    job_id: str = ""
    run_id: str = ""
    input: GenerationInput = field(default_factory=GenerationInput)
    parsed_document: ParsedDocument | None = None
    material_index: MaterialIndex | None = None
    temporary_material_context: TemporaryMaterialContext | None = None
    material_recall_results: list[MaterialRecallResult] = field(default_factory=list)
    material_read_results: list[MaterialReadResult] = field(default_factory=list)
    workbook_inspect_results: list[WorkbookInspectResult] = field(default_factory=list)
    parsed_style_reference: ParsedDocument | None = None
    requirement_brief: RequirementBrief | None = None
    plan_draft: PlanDraft | None = None
    execution_checklist: list[ChecklistItem] = field(default_factory=list)
    content_draft: ContentDraft | None = None
    style_brief: StyleBrief | None = None
    html_draft: HtmlDraft | None = None
    visual_check_report: VisualCheckReport | None = None
    validation_report: ValidationReport | None = None
    safety_report: SafetyReport | None = None
    create_note_proposal: CreateNoteProposal | None = None
    stage_trace: list[StageTraceEvent] = field(default_factory=list)
    skill_trace: list[SkillTraceEntry] = field(default_factory=list)
    agent_artifacts: list[AgentArtifact] = field(default_factory=list)
    current_step: str = ""
    completed_steps: list[str] = field(default_factory=list)
    failed_steps: list[str] = field(default_factory=list)
    revision_round: int = 0
    same_node_retries: dict[str, int] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return normalize_for_json(asdict(self))


def normalize_for_json(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, list):
        return [normalize_for_json(item) for item in value]
    if isinstance(value, tuple):
        return [normalize_for_json(item) for item in value]
    if isinstance(value, dict):
        return {str(key): normalize_for_json(item) for key, item in value.items()}
    return value
