from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from html_lore.server.config import ServerSettings


DEFAULT_GENERATION_MODEL = "gpt-5.5"


@dataclass(frozen=True)
class GenerationRetryPolicy:
    allow_model_escalation: bool = False
    escalation_model: str = ""


@dataclass(frozen=True)
class GenerationModelProfile:
    default_model: str = DEFAULT_GENERATION_MODEL
    node_models: dict[str, str] = field(default_factory=dict)
    retry_policy: GenerationRetryPolicy = field(default_factory=GenerationRetryPolicy)

    @classmethod
    def from_settings(cls, settings: ServerSettings) -> "GenerationModelProfile":
        # V2 generation intentionally defaults to the product-level quality model.
        # The configured AI model remains available to other AI features.
        return cls(default_model=getattr(settings, "ai_generation_model", "") or DEFAULT_GENERATION_MODEL)

    def model_for(self, node_name: str) -> str:
        return self.node_models.get(node_name) or self.default_model

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
