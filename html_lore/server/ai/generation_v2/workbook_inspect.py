from __future__ import annotations

import re
from typing import Any

from .schemas import ParsedDocument, SpreadsheetCell, SpreadsheetWorkbook, WorkbookInspectRequest, WorkbookInspectResult


VALID_ACTIONS = {"list_sheets", "read_range", "find_formulas", "trace_references"}
MAX_RESULT_RECORDS = 500
CELL_RE = re.compile(r"^\$?([A-Z]{1,3})\$?([1-9][0-9]*)$", re.IGNORECASE)
FORMULA_REF_RE = re.compile(r"(?:(?:'([^']+)'|([A-Za-z0-9_ .-]+))!)?\$?([A-Z]{1,3})\$?([1-9][0-9]*)", re.IGNORECASE)


def inspect_workbook(
    parsed: ParsedDocument | None,
    requests: list[WorkbookInspectRequest],
    *,
    agent: str,
    max_requests: int = 3,
    max_records: int = MAX_RESULT_RECORDS,
) -> list[WorkbookInspectResult]:
    if parsed is None or not parsed.workbooks:
        return []
    results: list[WorkbookInspectResult] = []
    remaining = max(1, min(int(max_records or MAX_RESULT_RECORDS), MAX_RESULT_RECORDS))
    for request in requests[: max(0, int(max_requests or 0))]:
        workbook = find_workbook(parsed, request)
        if workbook is None:
            results.append(empty_result(request, agent=agent, warning="Requested workbook was not found."))
            continue
        result = inspect_one(workbook, request, agent=agent, record_limit=min(max(1, request.limit), remaining))
        remaining -= len(result.records)
        results.append(result)
        if remaining <= 0:
            break
    return results


def find_workbook(parsed: ParsedDocument, request: WorkbookInspectRequest) -> SpreadsheetWorkbook | None:
    if request.file_id:
        for workbook in parsed.workbooks:
            if workbook.file_id == request.file_id:
                return workbook
    if request.filename:
        target = request.filename.lower()
        for workbook in parsed.workbooks:
            name = workbook.filename.lower()
            if name == target or target in name:
                return workbook
    return parsed.workbooks[0] if len(parsed.workbooks) == 1 else None


def inspect_one(workbook: SpreadsheetWorkbook, request: WorkbookInspectRequest, *, agent: str, record_limit: int) -> WorkbookInspectResult:
    action = request.action if request.action in VALID_ACTIONS else "list_sheets"
    warnings: list[str] = []
    records: list[dict[str, Any]] = []
    possible_count = 0
    if action == "list_sheets":
        possible_count = len(workbook.sheets)
        records = [
            {
                "title": sheet.title,
                "state": sheet.state,
                "max_row": sheet.max_row,
                "max_column": sheet.max_column,
                "cell_count": len(sheet.cells),
                "formula_count": sum(1 for cell in sheet.cells if cell.formula),
                "merged_ranges": sheet.merged_ranges,
                "hidden_row_count": len(sheet.hidden_rows),
                "hidden_column_count": len(sheet.hidden_columns),
                "truncated": sheet.truncated,
            }
            for sheet in workbook.sheets[:record_limit]
        ]
    elif action == "read_range":
        sheet = find_sheet(workbook, request.sheet)
        if sheet is None:
            warnings.append("Requested worksheet was not found.")
        else:
            bounds = parse_range(request.cell_range)
            if bounds is None:
                warnings.append("A valid cell_range such as A1:F20 is required.")
            else:
                matching_cells = [cell for cell in sheet.cells if coordinate_in_bounds(cell.coordinate, bounds)]
                possible_count = len(matching_cells)
                records = [cell_record(cell) for cell in matching_cells[:record_limit]]
    elif action == "find_formulas":
        query = request.query.lower().strip()
        matching_formulas = []
        for sheet in workbook.sheets:
            if request.sheet and sheet.title.lower() != request.sheet.lower():
                continue
            for cell in sheet.cells:
                if cell.formula and (not query or query in cell.formula.lower() or query in cell.coordinate.lower()):
                    matching_formulas.append({"sheet": sheet.title, **cell_record(cell)})
        possible_count = len(matching_formulas)
        records = matching_formulas[:record_limit]
    else:
        records = trace_references(workbook, request, record_limit=record_limit, warnings=warnings)
        possible_count = len(records)
    return WorkbookInspectResult(
        agent=agent,
        request_id=request.id,
        action=action,
        file_id=workbook.file_id,
        filename=workbook.filename,
        sheet=request.sheet,
        records=records,
        truncated=len(records) >= record_limit and possible_count > record_limit,
        warnings=warnings,
    )


def trace_references(workbook: SpreadsheetWorkbook, request: WorkbookInspectRequest, *, record_limit: int, warnings: list[str]) -> list[dict[str, Any]]:
    target = request.coordinate.upper().replace("$", "")
    target_sheet = find_sheet(workbook, request.sheet)
    if not target or not CELL_RE.match(target):
        warnings.append("A valid coordinate such as C12 is required.")
        return []
    if target_sheet is None:
        warnings.append("Requested worksheet was not found.")
        return []
    records: list[dict[str, Any]] = []
    source = next((cell for cell in target_sheet.cells if cell.coordinate.upper() == target), None)
    if source is not None:
        records.append({"relation": "target", "sheet": target_sheet.title, **cell_record(source)})
        if source.formula:
            for reference_sheet, coordinate in formula_references(source.formula, default_sheet=target_sheet.title):
                records.append(
                    {
                        "relation": "references",
                        "sheet": reference_sheet,
                        "coordinate": coordinate,
                    }
                )
    for sheet in workbook.sheets:
        for cell in sheet.cells:
            references = formula_references(cell.formula, default_sheet=sheet.title) if cell.formula else []
            if any(reference_sheet.lower() == target_sheet.title.lower() and coordinate == target for reference_sheet, coordinate in references):
                records.append({"relation": "referenced_by", "sheet": sheet.title, **cell_record(cell)})
                if len(records) >= record_limit:
                    return records[:record_limit]
    return records[:record_limit]


def formula_references(formula: str, *, default_sheet: str) -> list[tuple[str, str]]:
    references: list[tuple[str, str]] = []
    for sheet_name_a, sheet_name_b, column, row in FORMULA_REF_RE.findall(str(formula or "")):
        references.append((sheet_name_a or sheet_name_b.strip() or default_sheet, f"{column.upper()}{row}"))
    return references


def find_sheet(workbook: SpreadsheetWorkbook, title: str):
    if not title and len(workbook.sheets) == 1:
        return workbook.sheets[0]
    target = title.lower().strip()
    return next((sheet for sheet in workbook.sheets if sheet.title.lower() == target), None)


def parse_range(value: str) -> tuple[int, int, int, int] | None:
    parts = str(value or "").upper().replace("$", "").split(":", 1)
    if len(parts) == 1:
        parts.append(parts[0])
    first = parse_coordinate(parts[0])
    last = parse_coordinate(parts[1])
    if first is None or last is None:
        return None
    return min(first[0], last[0]), min(first[1], last[1]), max(first[0], last[0]), max(first[1], last[1])


def parse_coordinate(value: str) -> tuple[int, int] | None:
    match = CELL_RE.match(value.strip())
    if not match:
        return None
    column = 0
    for char in match.group(1).upper():
        column = column * 26 + ord(char) - 64
    return column, int(match.group(2))


def coordinate_in_bounds(coordinate: str, bounds: tuple[int, int, int, int]) -> bool:
    parsed = parse_coordinate(coordinate)
    return bool(parsed and bounds[0] <= parsed[0] <= bounds[2] and bounds[1] <= parsed[1] <= bounds[3])


def cell_record(cell: SpreadsheetCell) -> dict[str, Any]:
    return {
        "coordinate": cell.coordinate,
        "value": cell.value,
        "formula": cell.formula,
        "cached_value": cell.cached_value,
        "data_type": cell.data_type,
        "number_format": cell.number_format,
    }


def empty_result(request: WorkbookInspectRequest, *, agent: str, warning: str) -> WorkbookInspectResult:
    return WorkbookInspectResult(agent=agent, request_id=request.id, action=request.action, file_id=request.file_id, filename=request.filename, sheet=request.sheet, warnings=[warning])
