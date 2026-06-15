from __future__ import annotations

import re
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Any

from html_lore.server.items import ItemContentError, ItemService

from .model_client import ModelClient
from .vector_store import LocalVectorStore, VectorStoreUnavailable, content_hash, vector_chunk_id


MAX_CHUNK_CHARS = 1800
MAX_EVIDENCE_CHARS = 5000
RETRIEVAL_MODES = {"keyword", "vector", "hybrid"}
MAX_CHUNKS_PER_ITEM = 2
KEYWORD_MIN_SCORE = 8
KEYWORD_RELATIVE_SCORE_RATIO = 0.34


@dataclass(frozen=True)
class Evidence:
    item_id: str
    title: str
    snippet: str
    score: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "item_id": self.item_id,
            "title": self.title,
            "snippet": self.snippet,
            "score": self.score,
        }


class RetrievalUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class RetrievalResult:
    evidence: list[dict[str, Any]]
    status: dict[str, Any]


class SafeTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.skip_stack: list[str] = []
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {name.lower(): str(value or "") for name, value in attrs}
        if tag.lower() in {"script", "style", "noscript", "template", "iframe", "svg"} or is_hidden(attr_map):
            self.skip_stack.append(tag.lower())
            return
        if tag.lower() in {"p", "div", "section", "article", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if self.skip_stack:
            if self.skip_stack[-1] == tag.lower():
                self.skip_stack.pop()
            return
        if tag.lower() in {"p", "div", "section", "article", "li", "tr"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.skip_stack and data.strip():
            self.parts.append(data)

    def text(self) -> str:
        return normalize_space(" ".join(self.parts))


def extract_safe_text(html: str) -> str:
    parser = SafeTextExtractor()
    parser.feed(html)
    parser.close()
    return parser.text()


def extract_safe_blocks(html: str) -> list[str]:
    parser = SafeTextExtractor()
    parser.feed(html)
    parser.close()
    raw = " ".join(parser.parts)
    blocks = [normalize_space(line) for line in raw.splitlines()]
    return [block for block in blocks if block]


def retrieve_evidence(item_service: ItemService, context_snapshot: dict[str, Any], query: str, *, max_results: int = 5) -> list[dict[str, Any]]:
    return retrieve_keyword_evidence(item_service, context_snapshot, query, max_results=max_results)


def retrieve_evidence_with_status(
    item_service: ItemService,
    context_snapshot: dict[str, Any],
    query: str,
    *,
    mode: str = "keyword",
    model_client: ModelClient | None = None,
    max_results: int = 5,
) -> RetrievalResult:
    requested_mode = normalize_retrieval_mode(mode)
    if requested_mode == "keyword":
        evidence = retrieve_keyword_evidence(item_service, context_snapshot, query, max_results=max_results)
        return RetrievalResult(evidence=evidence, status=keyword_status(requested_mode, evidence, fallback=False))

    if requested_mode == "hybrid":
        keyword_evidence = retrieve_keyword_evidence(item_service, context_snapshot, query, max_results=max_results)
        try:
            vector_evidence = retrieve_vector_evidence(
                item_service,
                context_snapshot,
                query,
                model_client=model_client,
                max_results=max_results,
            )
        except Exception as exc:
            return RetrievalResult(
                evidence=keyword_evidence,
                status={
                    "requested_mode": "hybrid",
                    "effective_mode": "keyword",
                    "fallback": True,
                    "reason": retrieval_error_reason(exc),
                    "keyword_source_count": len(keyword_evidence),
                    "vector_source_count": 0,
                    "source_count": len(keyword_evidence),
                },
            )
        evidence = merge_hybrid_evidence(keyword_evidence, vector_evidence, max_results=max_results)
        return RetrievalResult(
            evidence=evidence,
            status={
                "requested_mode": "hybrid",
                "effective_mode": "hybrid",
                "fallback": False,
                "keyword_source_count": len(keyword_evidence),
                "vector_source_count": len(vector_evidence),
                "source_count": len(evidence),
            },
        )

    try:
        evidence = retrieve_vector_evidence(
            item_service,
            context_snapshot,
            query,
            model_client=model_client,
            max_results=max_results,
        )
        return RetrievalResult(
            evidence=evidence,
            status={
                "requested_mode": requested_mode,
                "effective_mode": "vector",
                "fallback": False,
                "source_count": len(evidence),
            },
        )
    except Exception as exc:
        evidence = retrieve_keyword_evidence(item_service, context_snapshot, query, max_results=max_results)
        return RetrievalResult(evidence=evidence, status=keyword_status(requested_mode, evidence, fallback=True, reason=retrieval_error_reason(exc)))


def keyword_status(requested_mode: str, evidence: list[dict[str, Any]], *, fallback: bool, reason: str = "") -> dict[str, Any]:
    status: dict[str, Any] = {
        "requested_mode": requested_mode,
        "effective_mode": "keyword",
        "fallback": fallback,
        "keyword_source_count": len(evidence),
        "vector_source_count": 0,
        "source_count": len(evidence),
    }
    if reason:
        status["reason"] = reason
    return status


def retrieve_keyword_evidence(item_service: ItemService, context_snapshot: dict[str, Any], query: str, *, max_results: int = 5) -> list[dict[str, Any]]:
    item_ids = [str(item_id) for item_id in context_snapshot.get("item_ids", []) if item_id]
    if not item_ids:
        return []
    manifest_items = {str(item.get("id") or ""): item for item in item_service.manifest().get("items", [])}
    evidences: list[Evidence] = []
    fallback_candidates: list[Evidence] = []
    scope = str(context_snapshot.get("scope") or "")
    generic_question = is_generic_context_question(query)
    allow_generic_fallback = scope in {"reader", "manual"} and generic_question
    overview_scope = scope not in {"reader", "manual"} and is_context_overview_question(query)
    overview_limit = max(max_results, len(item_ids)) if overview_scope else max_results
    for item_id in item_ids:
        item = manifest_items.get(item_id)
        if not item or bool(item.get("archived")):
            continue
        try:
            html = item_service.read_item_content(item_id)
        except ItemContentError:
            continue
        text = evidence_text(item, html)
        blocks = extract_safe_blocks(html)
        chunks = chunk_blocks(blocks) or [text]
        aggressive_stopwords = scope not in {"reader", "manual"}
        item_score = score_item_metadata(query, item, aggressive_stopwords=aggressive_stopwords)
        chunk_evidences: list[Evidence] = []
        if overview_scope:
            score = score_text(query, text, aggressive_stopwords=aggressive_stopwords) + item_score
            fallback_candidates.append(
                Evidence(
                    item_id=item_id,
                    title=str(item.get("title") or item_id),
                    snippet=overview_snippet(item, text),
                    score=max(score, KEYWORD_MIN_SCORE),
                ),
            )
            continue
        for chunk_index, chunk in enumerate(chunks):
            score = score_text(query, chunk, aggressive_stopwords=aggressive_stopwords) + item_score
            if score <= 0:
                continue
            chunk_evidences.append(
                Evidence(
                    item_id=item_id,
                    title=str(item.get("title") or item_id),
                    snippet=snippet_for_query(chunk, query, aggressive_stopwords=aggressive_stopwords),
                    score=score,
                ),
            )
        if not chunk_evidences:
            if allow_generic_fallback:
                fallback_candidates.append(
                    Evidence(
                        item_id=item_id,
                        title=str(item.get("title") or item_id),
                        snippet=reader_summary_snippet(item, text),
                        score=KEYWORD_MIN_SCORE,
                    ),
                )
            continue
        evidences.extend(best_item_chunks(chunk_evidences))
    if overview_scope and fallback_candidates:
        return [
            evidence.as_dict()
            for evidence in sorted(fallback_candidates, key=lambda item: (-item.score, item.title))[:overview_limit]
        ]
    if not evidences and fallback_candidates:
        return [evidence.as_dict() for evidence in fallback_candidates[:max_results]]
    balanced = scope not in {"reader"} and len(item_ids) > 1
    filtered = filter_low_relevance_evidence(evidences, scope=scope)
    return [evidence.as_dict() for evidence in rank_evidence(filtered, max_results=max_results, balanced=balanced)]


def chunk_blocks(blocks: list[str]) -> list[str]:
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for block in blocks:
        text = normalize_space(block)
        if not text:
            continue
        if len(text) > MAX_CHUNK_CHARS:
            if current:
                chunks.append(" ".join(current))
                current = []
                current_len = 0
            chunks.extend(split_long_text(text, MAX_CHUNK_CHARS))
            continue
        next_len = current_len + len(text) + (1 if current else 0)
        if current and next_len > MAX_CHUNK_CHARS:
            chunks.append(" ".join(current))
            current = [text]
            current_len = len(text)
        else:
            current.append(text)
            current_len = next_len
    if current:
        chunks.append(" ".join(current))
    return chunks


def split_long_text(text: str, size: int) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(text):
        chunks.append(text[start : start + size].strip())
        start += size
    return [chunk for chunk in chunks if chunk]


def best_item_chunks(evidences: list[Evidence]) -> list[Evidence]:
    deduped: list[Evidence] = []
    seen: set[str] = set()
    for evidence in sorted(evidences, key=lambda item: (-item.score, item.snippet)):
        key = normalize_space(evidence.snippet).lower()[:240]
        if key in seen:
            continue
        deduped.append(evidence)
        seen.add(key)
        if len(deduped) >= MAX_CHUNKS_PER_ITEM:
            break
    return deduped


def rank_evidence(evidences: list[Evidence], *, max_results: int, balanced: bool = False) -> list[Evidence]:
    limit = max(1, int(max_results or 5))
    sorted_evidence = sorted(evidences, key=lambda item: (-item.score, item.title, item.snippet))
    if not balanced:
        return sorted_evidence[:limit]

    by_item: dict[str, list[Evidence]] = {}
    for evidence in sorted_evidence:
        by_item.setdefault(evidence.item_id, []).append(evidence)

    ranked: list[Evidence] = []
    first_pass = sorted((items[0] for items in by_item.values()), key=lambda item: (-item.score, item.title, item.snippet))
    for evidence in first_pass:
        if len(ranked) >= limit:
            return ranked
        ranked.append(evidence)

    ranked_keys = {(item.item_id, item.snippet) for item in ranked}
    extras = [item for item in sorted_evidence if (item.item_id, item.snippet) not in ranked_keys]
    for evidence in extras:
        if len(ranked) >= limit:
            break
        ranked.append(evidence)
    return ranked


def filter_low_relevance_evidence(evidences: list[Evidence], *, scope: str) -> list[Evidence]:
    if not evidences:
        return []
    if scope in {"reader", "manual"}:
        return [item for item in evidences if item.score >= 1]
    strong = [item for item in evidences if item.score >= KEYWORD_MIN_SCORE]
    if not strong:
        return []
    top_score = max(item.score for item in strong)
    relative_floor = max(KEYWORD_MIN_SCORE, int(top_score * KEYWORD_RELATIVE_SCORE_RATIO))
    return [item for item in strong if item.score >= relative_floor]


def merge_hybrid_evidence(keyword_evidence: list[dict[str, Any]], vector_evidence: list[dict[str, Any]], *, max_results: int) -> list[dict[str, Any]]:
    merged: dict[tuple[str, str], dict[str, Any]] = {}
    for source, boost in ((keyword_evidence, 0), (vector_evidence, 8)):
        for item in source:
            key = (str(item.get("item_id") or item.get("url") or ""), normalize_space(str(item.get("snippet") or ""))[:240])
            if key in merged:
                existing = merged[key]
                existing["score"] = max(safe_score(existing), safe_score(item) + boost)
                existing["retrieval_sources"] = sorted(set(existing.get("retrieval_sources") or []) | {retrieval_source_name(item, boost)})
                continue
            copied = dict(item)
            copied["score"] = safe_score(item) + boost
            copied["retrieval_sources"] = [retrieval_source_name(item, boost)]
            merged[key] = copied
    ranked = sorted(merged.values(), key=lambda item: (-safe_score(item), str(item.get("title") or ""), str(item.get("snippet") or "")))
    return ranked[: max(1, int(max_results or 5))]


def safe_score(item: dict[str, Any]) -> int:
    try:
        return int(item.get("score") or 0)
    except (TypeError, ValueError):
        return 0


def retrieval_source_name(item: dict[str, Any], boost: int) -> str:
    sources = item.get("retrieval_sources")
    if isinstance(sources, list) and sources:
        return str(sources[0])
    return "vector" if boost else "keyword"


def retrieve_vector_evidence(
    item_service: ItemService,
    context_snapshot: dict[str, Any],
    query: str,
    *,
    model_client: ModelClient | None,
    max_results: int = 5,
) -> list[dict[str, Any]]:
    if model_client is None:
        raise RetrievalUnavailable("Embedding model client is not configured.")
    embedding_model = str(model_client.config.embedding_model or "").strip()
    if not embedding_model:
        raise NotImplementedError("Embedding model is not configured.")
    item_ids = {str(item_id) for item_id in context_snapshot.get("item_ids") or [] if str(item_id)}
    if not item_ids:
        return []
    try:
        store = LocalVectorStore(item_service.settings)
    except VectorStoreUnavailable as exc:
        raise RetrievalUnavailable(str(exc)) from exc
    chunks = build_vector_chunks(item_service, context_snapshot, embedding_model, model_client, store)
    store.upsert_chunks(chunks)
    query_vector = model_client.embed(text=query)
    return store.search(query_vector=query_vector, item_ids=item_ids, model=embedding_model, limit=max_results)


def build_vector_chunks(
    item_service: ItemService,
    context_snapshot: dict[str, Any],
    embedding_model: str,
    model_client: ModelClient,
    store: LocalVectorStore,
) -> list[dict[str, Any]]:
    item_ids = [str(item_id) for item_id in context_snapshot.get("item_ids") or [] if str(item_id)]
    item_id_set = set(item_ids)
    indexed_hashes = store.existing_hashes(model=embedding_model, item_ids=item_id_set)
    manifest_items = {str(item.get("id") or ""): item for item in item_service.manifest().get("items", [])}
    chunks: list[dict[str, Any]] = []
    for item_id in item_ids:
        item = manifest_items.get(item_id)
        if not item or bool(item.get("archived")):
            continue
        try:
            html = item_service.read_item_content(item_id)
        except ItemContentError:
            continue
        blocks = extract_safe_blocks(html)
        text_chunks = chunk_blocks(blocks) or [evidence_text(item, html)]
        for index, text in enumerate(text_chunks[:MAX_CHUNKS_PER_ITEM], start=1):
            snippet = normalize_space(text)[:MAX_CHUNK_CHARS]
            if not snippet:
                continue
            chunk_id = vector_chunk_id(item_id, index)
            hash_value = content_hash(snippet)
            if (item_id, chunk_id, hash_value) in indexed_hashes:
                continue
            chunks.append(
                {
                    "item_id": item_id,
                    "chunk_id": chunk_id,
                    "title": str(item.get("title") or item_id),
                    "snippet": snippet,
                    "content_hash": hash_value,
                    "model": embedding_model,
                    "vector": model_client.embed(text=snippet),
                },
            )
    return chunks


def normalize_retrieval_mode(mode: str) -> str:
    normalized = str(mode or "keyword").strip().lower()
    return normalized if normalized in RETRIEVAL_MODES else "keyword"


def retrieval_error_reason(exc: Exception) -> str:
    if isinstance(exc, NotImplementedError):
        return "embedding_not_implemented"
    if isinstance(exc, RetrievalUnavailable):
        return "vector_unavailable"
    return exc.__class__.__name__


def evidence_text(item: dict[str, Any], html: str) -> str:
    fields = [
        str(item.get("title") or ""),
        str(item.get("summary") or ""),
        str(item.get("collection") or ""),
        " ".join(str(tag) for tag in item.get("tags") or []),
        extract_safe_text(html),
    ]
    return normalize_space(" ".join(fields))[:MAX_EVIDENCE_CHARS]


def score_item_metadata(query: str, item: dict[str, Any], *, aggressive_stopwords: bool = True) -> int:
    tokens = query_tokens(normalize_space(query).lower(), aggressive_stopwords=aggressive_stopwords)
    if not tokens:
        return 0
    title = str(item.get("title") or "").lower()
    summary = str(item.get("summary") or "").lower()
    collection = str(item.get("collection") or "").lower()
    tags = " ".join(str(tag) for tag in item.get("tags") or []).lower()
    score = 0
    normalized_query = normalize_space(query).lower()
    if normalized_query and normalized_query in title:
        score += 50
    if normalized_query and normalized_query in summary:
        score += 24
    for token in tokens:
        if token in title:
            score += max(8, min(len(token) * 3, 36))
        if token in tags:
            score += max(6, min(len(token) * 3, 30))
        if token in collection:
            score += max(3, min(len(token) * 2, 16))
        if token in summary:
            score += max(4, min(len(token) * 2, 24))
    return score


def score_text(query: str, text: str, *, aggressive_stopwords: bool = True) -> int:
    normalized_query = normalize_space(query).lower()
    normalized_text = text.lower()
    if not normalized_query:
        return 0
    score = 0
    if normalized_query in normalized_text:
        score += 30
    for token in query_tokens(normalized_query, aggressive_stopwords=aggressive_stopwords):
        if token in normalized_text:
            score += max(2, min(len(token), 20))
    return score


def snippet_for_query(text: str, query: str, *, aggressive_stopwords: bool = True) -> str:
    normalized = normalize_space(text)
    lowered = normalized.lower()
    positions = [lowered.find(token) for token in query_tokens(query.lower(), aggressive_stopwords=aggressive_stopwords) if token and lowered.find(token) >= 0]
    start = max(min(positions) - 180, 0) if positions else 0
    snippet = normalized[start : start + MAX_CHUNK_CHARS]
    return snippet.strip()


def overview_snippet(item: dict[str, Any], text: str) -> str:
    summary = str(item.get("summary") or "").strip()
    title = str(item.get("title") or item.get("id") or "").strip()
    prefix = f"{title}. {summary}".strip()
    if summary:
        return normalize_space(prefix)[:MAX_CHUNK_CHARS]
    return normalize_space(text)[:MAX_CHUNK_CHARS]


def reader_summary_snippet(item: dict[str, Any], text: str) -> str:
    summary = str(item.get("summary") or "").strip()
    safe_text = normalize_space(text)
    if summary:
        combined = f"{overview_snippet(item, text)}\n\n{safe_text}"
        return normalize_space(combined)[:MAX_CHUNK_CHARS]
    return safe_text[:MAX_CHUNK_CHARS]


def query_tokens(query: str, *, aggressive_stopwords: bool = True) -> list[str]:
    ascii_tokens = re.findall(r"[a-z0-9][a-z0-9._-]{1,}", query.lower())
    cjk_tokens: list[str] = []
    for segment in re.findall(r"[\u4e00-\u9fff]{2,}", query):
        stripped = strip_cjk_stopwords(segment, aggressive=aggressive_stopwords)
        if len(stripped) >= 2:
            cjk_tokens.append(stripped)
        cjk_tokens.extend(re.findall(r"(?=([\u4e00-\u9fff]{2}))", stripped))
        cjk_tokens.extend(re.findall(r"(?=([\u4e00-\u9fff]{3}))", stripped))
    return dedupe_tokens([*ascii_tokens, *cjk_tokens])


def is_generic_context_question(query: str) -> bool:
    normalized = normalize_space(query).lower()
    if not normalized:
        return False
    generic_patterns = [
        r"\bsummary\b",
        r"\bsummarize\b",
        r"\boverview\b",
        r"\bwhat (is|does).{0,32}(note|document|article|file).{0,24}(about|cover)",
        r"\bwhat.{0,24}(this|the).{0,16}(note|document|article|file).{0,24}(about|cover)",
        r"总结",
        r"概括",
        r"摘要",
        r"这[篇个份]?(.{0,8})(文章|文档|笔记|文件)?.{0,8}(讲|说|介绍|关于)",
        r"(文章|文档|笔记|文件).{0,8}(讲|说|介绍|关于).{0,8}(什么|啥)",
        r"要約",
        r"概要",
        r"まとめ",
        r"この(.{0,8})(文章|文書|ノート|ファイル).{0,12}(何|内容)",
    ]
    return any(re.search(pattern, normalized) for pattern in generic_patterns)


def is_context_overview_question(query: str) -> bool:
    normalized = normalize_space(query).lower()
    if not normalized:
        return False
    overview_patterns = [
        r"\ball notes\b",
        r"\ball documents\b",
        r"\ball files\b",
        r"\bknowledge base\b",
        r"\bworkspace\b",
        r"\boverview\b",
        r"\bsummarize.{0,24}(all|workspace|knowledge base)",
        r"所有.{0,8}(笔记|文档|文件|内容)",
        r"(笔记|文档|文件|知识库).{0,12}(总览|概览|梳理|总结|主题)",
        r"(梳理|总结|概括).{0,12}(知识库|全部|所有)",
        r"有哪些.{0,6}(主题|内容)",
        r"すべて.{0,8}(ノート|文書|ファイル)",
        r"(ナレッジ|ワークスペース).{0,12}(概要|要約|整理)",
    ]
    return any(re.search(pattern, normalized) for pattern in overview_patterns)


def strip_cjk_stopwords(value: str, *, aggressive: bool = True) -> str:
    stripped = value
    base_words = (
        "这个",
        "这篇",
        "这份",
        "文章",
        "文档",
        "笔记",
        "文件",
        "什么",
        "一下",
        "一下子",
        "请问",
        "可以",
        "帮我",
        "关于",
        "的是",
        "了吗",
    )
    aggressive_words = (
        "解释",
        "说明",
        "总结",
        "概括",
        "小白",
        "入门",
        "基础",
        "基本",
        "原理",
        "概念",
        "通俗",
        "简单",
        "容易懂",
        "能懂",
    )
    words = (*base_words, *aggressive_words) if aggressive else base_words
    for word in words:
        stripped = stripped.replace(word, "")
    return stripped


def dedupe_tokens(tokens: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for token in tokens:
        normalized = token.strip().lower()
        if len(normalized) < 2 or normalized in seen:
            continue
        result.append(normalized)
        seen.add(normalized)
    return result


def is_hidden(attrs: dict[str, str]) -> bool:
    if "hidden" in attrs:
        return True
    if attrs.get("aria-hidden", "").lower() == "true":
        return True
    style = attrs.get("style", "").replace(" ", "").lower()
    return "display:none" in style or "visibility:hidden" in style


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()
