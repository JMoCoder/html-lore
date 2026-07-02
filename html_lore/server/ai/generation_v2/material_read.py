from __future__ import annotations

from dataclasses import replace

from .schemas import MaterialReadRequest, MaterialReadResult, ParsedDocument


DEFAULT_READ_LIMIT = 24000
MAX_READ_LIMIT = 96000


def read_material(
    parsed: ParsedDocument | None,
    requests: list[MaterialReadRequest],
    *,
    agent: str,
    max_requests: int = 3,
    max_chars: int = 16000,
) -> list[MaterialReadResult]:
    if parsed is None or not parsed.plain_text:
        return []
    results: list[MaterialReadResult] = []
    used_chars = 0
    seen_reads: set[tuple[str, str, int]] = set()
    for raw_request in requests[: max(0, max_requests)]:
        request = normalize_request(raw_request)
        material = find_material(parsed, request)
        if material is None:
            results.append(
                MaterialReadResult(
                    agent=agent,
                    request_id=request.id,
                    action=request.action,
                    file_id=request.file_id,
                    filename=request.filename,
                    warnings=["Requested material file was not found."],
                )
            )
            continue
        read_key = (material.file_id, request.action, 0 if request.action in {"read_file", "read_outline"} else request.offset)
        if read_key in seen_reads:
            continue
        seen_reads.add(read_key)
        available = max(0, max_chars - used_chars)
        if available <= 0:
            results.append(
                MaterialReadResult(
                    agent=agent,
                    request_id=request.id,
                    action=request.action,
                    file_id=material.file_id,
                    filename=material.filename,
                    warnings=["Material read result was limited by the agent evidence budget."],
                )
            )
            break
        limit = min(max(1, int(request.limit or DEFAULT_READ_LIMIT)), MAX_READ_LIMIT, available)
        result = read_one(parsed, request, agent=agent, file_id=material.file_id, filename=material.filename, file_start=material.content_start_char, file_end=material.content_end_char, limit=limit)
        used_chars += result.char_count
        results.append(result)
    return results


def normalize_request(request: MaterialReadRequest) -> MaterialReadRequest:
    if not isinstance(request, MaterialReadRequest):
        return MaterialReadRequest()
    action = request.action if request.action in {"read_file", "read_span", "read_outline"} else "read_span"
    return replace(request, action=action, offset=max(0, int(request.offset or 0)), limit=max(1, int(request.limit or DEFAULT_READ_LIMIT)))


def find_material(parsed: ParsedDocument, request: MaterialReadRequest):
    if not parsed.materials:
        return None
    if request.file_id:
        for material in parsed.materials:
            if material.file_id == request.file_id:
                return material
    if request.filename:
        lowered = request.filename.lower()
        for material in parsed.materials:
            if material.filename.lower() == lowered or lowered in material.filename.lower():
                return material
    return parsed.materials[0] if len(parsed.materials) == 1 else None


def read_one(
    parsed: ParsedDocument,
    request: MaterialReadRequest,
    *,
    agent: str,
    file_id: str,
    filename: str,
    file_start: int,
    file_end: int,
    limit: int,
) -> MaterialReadResult:
    if request.action == "read_outline":
        outline = [item for item in parsed.outline if item.file_id == file_id or item.filename == filename]
        text = "\n".join(f"{item.level}. {item.title}" for item in outline)
        if not text:
            text = material_preview(parsed, file_start, file_end, limit=min(limit, 1600))
        truncated = len(text) > limit
        return MaterialReadResult(
            agent=agent,
            request_id=request.id,
            action=request.action,
            file_id=file_id,
            filename=filename,
            offset=0,
            end_offset=min(len(text), limit),
            text=text[:limit],
            char_count=min(len(text), limit),
            truncated=truncated,
            next_offset=limit if truncated else 0,
        )
    relative_start = 0 if request.action == "read_file" else request.offset
    absolute_start = min(max(file_start, file_start + relative_start), file_end)
    absolute_end = min(file_end, absolute_start + limit)
    text = parsed.plain_text[absolute_start:absolute_end]
    truncated = absolute_end < file_end
    return MaterialReadResult(
        agent=agent,
        request_id=request.id,
        action=request.action,
        file_id=file_id,
        filename=filename,
        offset=max(0, absolute_start - file_start),
        end_offset=max(0, absolute_end - file_start),
        text=text,
        char_count=len(text),
        truncated=truncated,
        next_offset=max(0, absolute_end - file_start) if truncated else 0,
    )


def material_preview(parsed: ParsedDocument, file_start: int, file_end: int, *, limit: int) -> str:
    return parsed.plain_text[file_start : min(file_end, file_start + limit)]
