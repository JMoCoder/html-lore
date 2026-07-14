from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ToolRegistryItem:
    id: str
    title: str
    description: str
    available_to_agents: tuple[str, ...]
    request_field: str
    trigger_keywords: tuple[str, ...] = ()
    runtime_controlled: bool = True


_TOOL_REGISTRY: tuple[ToolRegistryItem, ...] = (
    ToolRegistryItem(
        id="material_recall",
        title="Material recall",
        description="Search task-local parsed material chunks when an agent outputs material_queries.",
        available_to_agents=("RequirementAnalyst", "ContentWriter", "Verifier"),
        request_field="material_queries",
        trigger_keywords=("source evidence", "exact facts", "tables", "figures", "material evidence", "verification"),
    ),
    ToolRegistryItem(
        id="material_read",
        title="Material read",
        description="Read task-local parsed material by file id, filename, outline, span, or file page when an agent outputs material_read_requests.",
        available_to_agents=("RequirementAnalyst", "ContentWriter", "Verifier"),
        request_field="material_read_requests",
        trigger_keywords=("full source", "faithful conversion", "exact wording", "outline", "span", "source completeness"),
    ),
    ToolRegistryItem(
        id="workbook_inspect",
        title="Workbook inspect",
        description="Inspect task-local workbook sheets, ranges, formulas, cached values, and formula references without executing workbook code or external links.",
        available_to_agents=("RequirementAnalyst", "ContentWriter", "Verifier"),
        request_field="workbook_inspect_requests",
        trigger_keywords=("workbook", "sheet", "cell", "range", "formula", "named range", "spreadsheet evidence"),
    ),
    ToolRegistryItem(
        id="document_parser",
        title="Document parser",
        description="Runtime ingest tool that parses uploaded material with MarkItDown or basic fallback before agents run.",
        available_to_agents=("Ingest",),
        request_field="runtime_ingest",
        trigger_keywords=("pdf", "docx", "pptx", "xlsx", "markdown", "html", "image", "uploaded material"),
    ),
    ToolRegistryItem(
        id="style_reference_parser",
        title="Style reference parser",
        description="Runtime ingest tool that parses an optional uploaded style reference file into style hints.",
        available_to_agents=("Ingest", "StyleDesigner"),
        request_field="runtime_ingest",
        trigger_keywords=("style reference", "reference file", "visual reference", "uploaded style"),
    ),
    ToolRegistryItem(
        id="browser_visual_check",
        title="Browser visual check",
        description="Runtime tool that renders generated HTML in headless browser viewports and reports overflow, clipping, blank viewport, and layout observations.",
        available_to_agents=("VisualCheckTool", "Verifier"),
        request_field="runtime_after_html_coder",
        trigger_keywords=("overflow", "layout", "browser", "viewport", "visual check", "clipping"),
    ),
    ToolRegistryItem(
        id="html_safety_scan",
        title="HTML safety scan",
        description="WriteGateway hard-boundary tool that blocks unsafe static HTML before writing to the library.",
        available_to_agents=("WriteGateway",),
        request_field="runtime_write_gateway",
        trigger_keywords=("script", "iframe", "form", "unsafe url", "secret", "static html safety"),
    ),
)


def iter_tool_registry_items() -> tuple[ToolRegistryItem, ...]:
    return _TOOL_REGISTRY


def get_tool_registry_item(tool_id: str) -> ToolRegistryItem | None:
    normalized = str(tool_id or "").strip()
    return next((item for item in _TOOL_REGISTRY if item.id == normalized), None)
