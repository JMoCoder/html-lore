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


@dataclass(frozen=True)
class OutlineItem:
    level: int = 1
    title: str = ""
    text: str = ""


@dataclass(frozen=True)
class DocumentImage:
    alt: str = ""
    description: str = ""
    source: str = ""


@dataclass(frozen=True)
class DocumentLink:
    text: str = ""
    url: str = ""
    source: str = ""


@dataclass(frozen=True)
class DocumentTable:
    title: str = ""
    headers: list[str] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)


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
class ParsedDocument:
    source_files: list[SourceFile] = field(default_factory=list)
    plain_text: str = ""
    outline: list[OutlineItem] = field(default_factory=list)
    images: list[DocumentImage] = field(default_factory=list)
    links: list[DocumentLink] = field(default_factory=list)
    tables: list[DocumentTable] = field(default_factory=list)
    style_hints: list[StyleHint] = field(default_factory=list)
    warnings: list[ParseWarning] = field(default_factory=list)


@dataclass(frozen=True)
class RequirementBrief:
    user_goal: str = ""
    target_use: str = "default"
    audience: str = ""
    output_type: str = "html_note"
    source_summary: str = ""
    must_include: list[str] = field(default_factory=list)
    should_avoid: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    style_preferences: list[str] = field(default_factory=list)
    reference_style_files: list[str] = field(default_factory=list)
    success_criteria: list[str] = field(default_factory=list)
    uncertainty: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SectionPlan:
    id: str = ""
    title: str = ""
    purpose: str = ""
    source_refs: list[str] = field(default_factory=list)
    expected_content: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ToolNeed:
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
    tool_needs: list[ToolNeed] = field(default_factory=list)
    execution_checklist: list[ChecklistItem] = field(default_factory=list)
    risk_points: list[str] = field(default_factory=list)
    verification_targets: list[str] = field(default_factory=list)


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
class ValidationReport:
    ok: bool = False
    score: float = 0.0
    checked_items: list[CheckedItem] = field(default_factory=list)
    issues: list[ValidationIssue] = field(default_factory=list)
    missing_parts: list[str] = field(default_factory=list)
    unsupported_claims: list[str] = field(default_factory=list)
    style_mismatch: list[str] = field(default_factory=list)
    structure_mismatch: list[str] = field(default_factory=list)
    route_back_to: str = ""
    retry_instruction: str = ""


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
    parsed_style_reference: ParsedDocument | None = None
    requirement_brief: RequirementBrief | None = None
    plan_draft: PlanDraft | None = None
    execution_checklist: list[ChecklistItem] = field(default_factory=list)
    content_draft: ContentDraft | None = None
    style_brief: StyleBrief | None = None
    html_draft: HtmlDraft | None = None
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
