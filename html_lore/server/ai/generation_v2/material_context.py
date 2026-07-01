from __future__ import annotations

import math
import re
from dataclasses import replace

from .schemas import MaterialChunk, MaterialFileBrief, MaterialIndex, MaterialQuery, MaterialRecallResult, ParsedDocument, TemporaryMaterialContext


MAX_FILE_PREVIEW_CHARS = 900
MAX_CHUNK_CHARS = 1400
MAX_SELECTED_CHARS = 14000
MAX_CHUNKS_PER_FILE = 6
MAX_TOTAL_CHUNKS = 18
DEFAULT_RECALL_TOP_K = 3
DEFAULT_RECALL_MAX_CHARS = 7000


def build_temporary_material_context(parsed: ParsedDocument | None, *, instruction: str = "") -> TemporaryMaterialContext:
    index = build_material_index(parsed, instruction=instruction)
    selected = select_chunks(index.chunks, index.files)
    selected_chars = sum(item.char_count for item in selected)
    warnings = list(index.warnings)
    if len(index.files) > 1:
        warnings.append("Temporary material context was selected from multiple uploaded files with per-file coverage.")
    return TemporaryMaterialContext(files=index.files, selected_chunks=selected, warnings=warnings, total_chars=index.total_chars, selected_chars=selected_chars)


def build_material_index(parsed: ParsedDocument | None, *, instruction: str = "") -> MaterialIndex:
    if parsed is None:
        return MaterialIndex(warnings=["No parsed material was available."])
    file_sections = split_parsed_document_by_file(parsed)
    query_tokens = tokenize(instruction)
    files: list[MaterialFileBrief] = []
    all_chunks: list[MaterialChunk] = []
    warnings: list[str] = []
    total_chars = 0
    for index, (filename, text) in enumerate(file_sections, start=1):
        source = next((item for item in parsed.source_files if item.filename == filename), None)
        file_warnings = [warning.message for warning in parsed.warnings if warning.message and filename in warning.message]
        file_chunks = chunk_file_text(index, filename, text, query_tokens)
        total_chars += len(text)
        files.append(
            MaterialFileBrief(
                file_index=index,
                filename=filename,
                content_type=source.content_type if source else "",
                size=source.size if source else 0,
                char_count=len(text),
                chunk_count=len(file_chunks),
                headings=file_headings(text)[:12],
                preview=trim_text(text, MAX_FILE_PREVIEW_CHARS),
                warnings=file_warnings,
            )
        )
        all_chunks.extend(file_chunks)
    if not files and parsed.plain_text:
        chunks = chunk_file_text(1, "uploaded-material", parsed.plain_text, query_tokens)
        total_chars = len(parsed.plain_text)
        files.append(
            MaterialFileBrief(
                file_index=1,
                filename="uploaded-material",
                char_count=len(parsed.plain_text),
                chunk_count=len(chunks),
                headings=file_headings(parsed.plain_text)[:12],
                preview=trim_text(parsed.plain_text, MAX_FILE_PREVIEW_CHARS),
            )
        )
        all_chunks.extend(chunks)
    return MaterialIndex(files=files, chunks=all_chunks, warnings=warnings, total_chars=total_chars)


def recall_material(
    index: MaterialIndex | None,
    queries: list[MaterialQuery],
    *,
    agent: str,
    max_queries: int = 4,
    top_k: int = DEFAULT_RECALL_TOP_K,
    max_chars: int = DEFAULT_RECALL_MAX_CHARS,
) -> list[MaterialRecallResult]:
    if index is None or not index.chunks:
        return []
    results: list[MaterialRecallResult] = []
    used_chars = 0
    seen: set[tuple[str, str]] = set()
    for raw_query in queries[: max(0, max_queries)]:
        query = normalize_query(raw_query)
        if not query.query:
            continue
        query_tokens = tokenize(" ".join([query.query, query.purpose, query.expected_evidence]))
        target_files = {item.lower() for item in query.target_files if item}
        ranked = sorted(
            index.chunks,
            key=lambda chunk: recall_score(chunk, query_tokens, target_files),
            reverse=True,
        )
        selected: list[MaterialChunk] = []
        warnings: list[str] = []
        for chunk in ranked:
            if len(selected) >= max(1, top_k):
                break
            if recall_score(chunk, query_tokens, target_files) <= 0 and selected:
                break
            key = (query.id or query.query, chunk.id)
            if key in seen:
                continue
            if used_chars + chunk.char_count > max_chars and selected:
                warnings.append("Recall result was limited by the agent evidence budget.")
                break
            selected.append(chunk)
            seen.add(key)
            used_chars += chunk.char_count
        results.append(
            MaterialRecallResult(
                agent=agent,
                query_id=query.id,
                query=query.query,
                purpose=query.purpose,
                chunks=selected,
                total_chars=sum(chunk.char_count for chunk in selected),
                warnings=warnings,
            )
        )
        if used_chars >= max_chars:
            break
    return results


def normalize_query(query: MaterialQuery) -> MaterialQuery:
    if isinstance(query, MaterialQuery):
        return query
    return MaterialQuery()


def recall_score(chunk: MaterialChunk, query_tokens: set[str], target_files: set[str]) -> float:
    tokens = tokenize(" ".join([chunk.heading, chunk.text]))
    overlap = len(tokens & query_tokens)
    score = overlap / math.sqrt(max(len(tokens), 1)) if query_tokens else 0.0
    if target_files and any(target in chunk.filename.lower() for target in target_files):
        score += 0.45
    if "table_like" in chunk.token_hints:
        score += 0.18
    if "numeric_dense" in chunk.token_hints:
        score += 0.12
    if "structured_heading" in chunk.token_hints:
        score += 0.08
    return score


def split_parsed_document_by_file(parsed: ParsedDocument) -> list[tuple[str, str]]:
    text = parsed.plain_text or ""
    if not text:
        return []
    matches = list(re.finditer(r"(?:^|\n)Source file:\s*(.+?)\n", text))
    if not matches:
        name = parsed.source_files[0].filename if parsed.source_files else "uploaded-material"
        return [(name, text.strip())]
    sections: list[tuple[str, str]] = []
    for idx, match in enumerate(matches):
        filename = match.group(1).strip() or f"material-{idx + 1}"
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        sections.append((filename, text[start:end].strip()))
    return sections


def chunk_file_text(file_index: int, filename: str, text: str, query_tokens: set[str]) -> list[MaterialChunk]:
    blocks = split_blocks(text)
    chunks: list[MaterialChunk] = []
    current: list[str] = []
    current_heading = ""
    current_locator = ""
    for block in blocks:
        heading = block_heading(block)
        if heading:
            current_heading = heading
        locator = block_locator(block)
        if locator:
            current_locator = locator
        if current and sum(len(part) for part in current) + len(block) > MAX_CHUNK_CHARS:
            chunks.append(make_chunk(file_index, filename, len(chunks) + 1, current, current_heading, current_locator, query_tokens))
            current = []
        if len(block) > MAX_CHUNK_CHARS:
            if current:
                chunks.append(make_chunk(file_index, filename, len(chunks) + 1, current, current_heading, current_locator, query_tokens))
                current = []
            for part in split_long_block(block, MAX_CHUNK_CHARS):
                chunks.append(make_chunk(file_index, filename, len(chunks) + 1, [part], current_heading, current_locator, query_tokens))
            continue
        current.append(block)
    if current:
        chunks.append(make_chunk(file_index, filename, len(chunks) + 1, current, current_heading, current_locator, query_tokens))
    return chunks


def split_blocks(text: str) -> list[str]:
    normalized = str(text or "").replace("\r\n", "\n")
    raw_blocks = re.split(r"\n\s*\n+", normalized)
    blocks = [block.strip() for block in raw_blocks if block.strip()]
    if len(blocks) <= 1:
        lines = [line.strip() for line in normalized.splitlines() if line.strip()]
        blocks = []
        current: list[str] = []
        for line in lines:
            if current and sum(len(part) for part in current) + len(line) > 900:
                blocks.append("\n".join(current))
                current = []
            current.append(line)
        if current:
            blocks.append("\n".join(current))
    return blocks


def split_long_block(block: str, limit: int) -> list[str]:
    parts: list[str] = []
    text = block.strip()
    while text:
        if len(text) <= limit:
            parts.append(text)
            break
        cut = text.rfind("\n", 0, limit)
        if cut < limit // 2:
            cut = text.rfind("。", 0, limit)
        if cut < limit // 2:
            cut = limit
        parts.append(text[:cut].strip())
        text = text[cut:].strip()
    return [part for part in parts if part]


def make_chunk(
    file_index: int,
    filename: str,
    chunk_index: int,
    parts: list[str],
    heading: str,
    locator: str,
    query_tokens: set[str],
) -> MaterialChunk:
    text = "\n\n".join(parts).strip()
    hints = token_hints(text)
    score = score_chunk(text, query_tokens, chunk_index, hints)
    return MaterialChunk(
        id=f"f{file_index}-c{chunk_index}",
        file_index=file_index,
        filename=filename,
        locator=locator,
        heading=heading,
        text=trim_text(text, MAX_CHUNK_CHARS),
        char_count=len(trim_text(text, MAX_CHUNK_CHARS)),
        token_hints=hints,
        score=round(score, 4),
    )


def select_chunks(chunks: list[MaterialChunk], files: list[MaterialFileBrief]) -> list[MaterialChunk]:
    selected: list[MaterialChunk] = []
    seen: set[str] = set()

    def add(chunk: MaterialChunk) -> None:
        if chunk.id in seen or len(selected) >= MAX_TOTAL_CHUNKS:
            return
        if sum(item.char_count for item in selected) + chunk.char_count > MAX_SELECTED_CHARS and selected:
            return
        selected.append(chunk)
        seen.add(chunk.id)

    for file in files:
        file_chunks = [item for item in chunks if item.file_index == file.file_index]
        for chunk in file_chunks[:2]:
            add(replace(chunk, score=max(chunk.score, 0.05)))
        table_like = [item for item in file_chunks if "table_like" in item.token_hints]
        numeric_dense = [item for item in file_chunks if "numeric_dense" in item.token_hints]
        for chunk in sorted([*table_like, *numeric_dense], key=lambda item: item.score, reverse=True)[:2]:
            add(chunk)
        ranked = sorted(file_chunks, key=lambda item: item.score, reverse=True)
        file_added = sum(1 for item in selected if item.file_index == file.file_index)
        for chunk in ranked:
            if file_added >= MAX_CHUNKS_PER_FILE:
                break
            before = len(selected)
            add(chunk)
            if len(selected) > before:
                file_added += 1
    return sorted(selected, key=lambda item: (item.file_index, natural_chunk_number(item.id)))


def token_hints(text: str) -> list[str]:
    hints: list[str] = []
    lines = [line for line in text.splitlines() if line.strip()]
    pipe_lines = [line for line in lines if line.count("|") >= 2]
    number_count = len(re.findall(r"\d+(?:\.\d+)?", text))
    if pipe_lines or looks_like_markdown_table(text):
        hints.append("table_like")
    if number_count >= max(4, len(text) // 180):
        hints.append("numeric_dense")
    if re.search(r"(?:^|\n)\s*(?:#{1,6}\s+|<!--\s*Slide number:)", text):
        hints.append("structured_heading")
    if len(text) <= 360:
        hints.append("short_context")
    return hints


def score_chunk(text: str, query_tokens: set[str], chunk_index: int, hints: list[str]) -> float:
    tokens = tokenize(text)
    overlap = len(tokens & query_tokens)
    score = overlap / math.sqrt(max(len(tokens), 1)) if query_tokens else 0.0
    if "table_like" in hints:
        score += 0.35
    if "numeric_dense" in hints:
        score += 0.2
    if "structured_heading" in hints:
        score += 0.1
    if chunk_index <= 2:
        score += 0.12
    return score


def tokenize(text: str) -> set[str]:
    value = str(text or "").lower()
    ascii_tokens = re.findall(r"[a-z0-9][a-z0-9_\-]{1,}", value)
    cjk_tokens = re.findall(r"[\u4e00-\u9fff]{2,}", value)
    pieces: set[str] = set(ascii_tokens)
    for token in cjk_tokens:
        pieces.add(token)
        if len(token) > 4:
            for size in (2, 3, 4):
                for index in range(0, max(0, len(token) - size + 1)):
                    pieces.add(token[index : index + size])
    return pieces


def file_headings(text: str) -> list[str]:
    headings: list[str] = []
    for line in str(text or "").splitlines():
        cleaned = line.strip().strip("#").strip()
        if not cleaned:
            continue
        if line.strip().startswith("<!-- Slide number:"):
            headings.append(cleaned)
        elif line.strip().startswith("#") and len(cleaned) <= 90:
            headings.append(cleaned)
        elif re.match(r"^\d+(?:\.\d+)*\s+\S+", cleaned) and len(cleaned) <= 90:
            headings.append(cleaned)
        elif re.match(r"^(?:第[一二三四五六七八九十百\d]+[章节部分]|[一二三四五六七八九十]+[、.．])\s*\S+", cleaned) and len(cleaned) <= 90:
            headings.append(cleaned)
        if len(headings) >= 16:
            break
    return headings


def block_heading(block: str) -> str:
    for line in block.splitlines()[:4]:
        cleaned = line.strip().strip("#").strip()
        if cleaned.startswith("<!-- Slide number:"):
            return cleaned
        if cleaned and len(cleaned) <= 90 and (re.match(r"^\d+(?:\.\d+)*\s+\S+", cleaned) or line.strip().startswith("#")):
            return cleaned
    return ""


def block_locator(block: str) -> str:
    match = re.search(r"<!--\s*Slide number:\s*(\d+)\s*-->", block)
    if match:
        return f"slide {match.group(1)}"
    return ""


def looks_like_markdown_table(text: str) -> bool:
    return bool(re.search(r"\|.+\|\s*\n\s*\|?\s*:?-{3,}:?\s*\|", text))


def natural_chunk_number(chunk_id: str) -> int:
    match = re.search(r"-c(\d+)$", chunk_id)
    return int(match.group(1)) if match else 0


def trim_text(value: str, limit: int) -> str:
    text = re.sub(r"\n{3,}", "\n\n", str(value or "").strip())
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 20)].rstrip() + "\n...[truncated]"
