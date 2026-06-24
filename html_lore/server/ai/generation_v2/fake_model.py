from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FakeGenerationModelClient:
    """Deterministic model stand-in used to validate graph state flow."""

    invalid_outputs: dict[str, int] | None = None

    def complete_json(self, *, node: str, schema_name: str, payload: dict[str, Any], attempt: int = 0) -> str:
        if self.invalid_outputs and attempt < int(self.invalid_outputs.get(node, 0)):
            return "{invalid json"
        public_payload = {key: value for key, value in payload.items() if not str(key).startswith("_")}
        return json.dumps(public_payload, ensure_ascii=False)

    def complete_text(self, *, node: str, payload: dict[str, Any], attempt: int = 0) -> str:
        public_payload = {key: value for key, value in payload.items() if not str(key).startswith("_")}
        html = str(public_payload.get("html") or "")
        return html or "<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\"><title>Generated HTML Note</title></head><body></body></html>"
