from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from html_lore.server.config import ServerSettings


class VectorStoreUnavailable(RuntimeError):
    pass


class LocalVectorStore:
    version = 1
    min_similarity = 0.28

    def __init__(self, settings: ServerSettings) -> None:
        if settings.meta_dir is None:
            raise VectorStoreUnavailable("Metadata directory is not configured.")
        self.path = settings.meta_dir / "ai" / "vector_index.json"

    def search(self, *, query_vector: list[float], item_ids: set[str], model: str, limit: int = 5) -> list[dict[str, Any]]:
        data = self._read()
        rows = [
            row
            for row in data.get("vectors", [])
            if isinstance(row, dict)
            and row.get("model") == model
            and str(row.get("item_id") or "") in item_ids
            and isinstance(row.get("vector"), list)
        ]
        scored = []
        for row in rows:
            score = cosine_similarity(query_vector, [float(value) for value in row.get("vector") or []])
            scored.append((score, row))
        ranked = sorted(scored, key=lambda pair: (-pair[0], str(pair[1].get("title") or ""), str(pair[1].get("chunk_id") or "")))
        evidence: list[dict[str, Any]] = []
        for score, row in ranked[: max(1, int(limit or 5))]:
            if score < self.min_similarity:
                continue
            evidence.append(
                {
                    "item_id": str(row.get("item_id") or ""),
                    "title": str(row.get("title") or row.get("item_id") or ""),
                    "snippet": str(row.get("snippet") or ""),
                    "score": max(1, int(score * 100)),
                    "retrieval_sources": ["vector"],
                    "vector_score": round(score, 6),
                },
            )
        return evidence

    def upsert_chunks(self, chunks: list[dict[str, Any]]) -> dict[str, int]:
        data = self._read()
        existing = {
            (str(row.get("item_id") or ""), str(row.get("chunk_id") or ""), str(row.get("model") or "")): row
            for row in data.get("vectors", [])
            if isinstance(row, dict)
        }
        upserted = 0
        for chunk in chunks:
            key = (str(chunk.get("item_id") or ""), str(chunk.get("chunk_id") or ""), str(chunk.get("model") or ""))
            previous = existing.get(key)
            if previous and previous.get("content_hash") == chunk.get("content_hash"):
                continue
            existing[key] = dict(chunk)
            upserted += 1
        data = {"version": self.version, "vectors": list(existing.values())}
        self._write(data)
        return {"upserted": upserted, "total": len(data["vectors"])}

    def existing_hashes(self, *, model: str, item_ids: set[str] | None = None) -> set[tuple[str, str, str]]:
        data = self._read()
        result: set[tuple[str, str, str]] = set()
        for row in data.get("vectors", []):
            if not isinstance(row, dict):
                continue
            item_id = str(row.get("item_id") or "")
            if item_ids is not None and item_id not in item_ids:
                continue
            if row.get("model") != model or not isinstance(row.get("vector"), list):
                continue
            result.add((item_id, str(row.get("chunk_id") or ""), str(row.get("content_hash") or "")))
        return result

    def has_current_chunk(self, *, item_id: str, chunk_id: str, model: str, content_hash_value: str) -> bool:
        data = self._read()
        for row in data.get("vectors", []):
            if not isinstance(row, dict):
                continue
            if (
                row.get("item_id") == item_id
                and row.get("chunk_id") == chunk_id
                and row.get("model") == model
                and row.get("content_hash") == content_hash_value
                and isinstance(row.get("vector"), list)
            ):
                return True
        return False

    def remove_items(self, item_ids: set[str]) -> dict[str, int]:
        if not item_ids:
            return self.stats()
        data = self._read()
        before = len(data.get("vectors", []))
        vectors = [
            row
            for row in data.get("vectors", [])
            if not isinstance(row, dict) or str(row.get("item_id") or "") not in item_ids
        ]
        self._write({"version": self.version, "vectors": vectors})
        return {"removed": before - len(vectors), "total": len(vectors)}

    def prune_to_items(self, valid_item_ids: set[str]) -> dict[str, int]:
        data = self._read()
        before = len(data.get("vectors", []))
        vectors = [
            row
            for row in data.get("vectors", [])
            if isinstance(row, dict) and str(row.get("item_id") or "") in valid_item_ids
        ]
        self._write({"version": self.version, "vectors": vectors})
        return {"removed": before - len(vectors), "total": len(vectors)}

    def clear(self) -> dict[str, int]:
        data = self._read()
        removed = len(data.get("vectors", []))
        self._write({"version": self.version, "vectors": []})
        return {"removed": removed, "total": 0}

    def stats(self) -> dict[str, int]:
        data = self._read()
        vectors = [row for row in data.get("vectors", []) if isinstance(row, dict)]
        item_ids = {str(row.get("item_id") or "") for row in vectors if row.get("item_id")}
        models = {str(row.get("model") or "") for row in vectors if row.get("model")}
        return {"total": len(vectors), "item_count": len(item_ids), "model_count": len(models)}

    def indexed_item_ids(self) -> set[str]:
        data = self._read()
        return {
            str(row.get("item_id") or "")
            for row in data.get("vectors", [])
            if isinstance(row, dict) and row.get("item_id")
        }

    def _read(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"version": self.version, "vectors": []}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise VectorStoreUnavailable("Vector index is not valid JSON.") from exc
        if not isinstance(data, dict):
            raise VectorStoreUnavailable("Vector index must be a JSON object.")
        vectors = data.get("vectors")
        if not isinstance(vectors, list):
            raise VectorStoreUnavailable("Vector index vectors must be a list.")
        return {"version": int(data.get("version") or self.version), "vectors": vectors}

    def _write(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


def vector_chunk_id(item_id: str, index: int) -> str:
    return f"{item_id}#{index}"


def content_hash(text: str) -> str:
    return hashlib.sha256(str(text or "").encode("utf-8")).hexdigest()


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = sum(a * a for a in left) ** 0.5
    right_norm = sum(b * b for b in right) ** 0.5
    if left_norm <= 0 or right_norm <= 0:
        return 0.0
    return dot / (left_norm * right_norm)
