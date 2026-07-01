from __future__ import annotations

from typing import Any

from .providers import AIProviderConfig, AIProviderConfigError, ProviderCallError, build_adapter


class ModelClient:
    def __init__(self, config: AIProviderConfig) -> None:
        self.config = config

    def status(self) -> dict[str, Any]:
        if not self.config.enabled:
            return {"available": False, "message": "AI provider is disabled."}
        if not self.config.provider:
            return {"available": False, "message": "AI provider is not configured."}
        if self.config.provider != "fake" and not self.config.api_key:
            return {"available": False, "message": "AI API key is not configured on the server."}
        if self.config.provider != "fake" and not self.config.base_url:
            return {"available": False, "message": "AI base URL is not configured."}
        return {"available": self.config.configured, "message": "AI provider is configured."}

    def chat(self, *, messages: list[dict[str, str]], temperature: float = 0.2, max_tokens: int = 1024, timeout_seconds: int | None = None) -> dict[str, Any]:
        self._ensure_available()
        return build_adapter(self.config).chat(messages=messages, temperature=temperature, max_tokens=max_tokens, timeout_seconds=timeout_seconds)

    def structured_output(self, *, messages: list[dict[str, str]], schema: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("Structured output is not implemented yet.")

    def embed(self, *, text: str) -> list[float]:
        self._ensure_available()
        return build_adapter(self.config).embed(text=text)

    def vision_analyze(self, *, image: bytes, prompt: str) -> dict[str, Any]:
        raise NotImplementedError("Vision analysis is not implemented yet.")

    def _ensure_available(self) -> None:
        status = self.status()
        if not status["available"]:
            raise AIProviderConfigError(str(status["message"]))


def test_provider(config: AIProviderConfig) -> dict[str, Any]:
    client = ModelClient(config)
    try:
        response = client.chat(
            messages=[
                {"role": "system", "content": "You are testing an HTMlore AI provider connection."},
                {"role": "user", "content": "Return a short connection test response."},
            ],
            max_tokens=128,
        )
    except (AIProviderConfigError, ProviderCallError) as exc:
        return {"ok": False, "message": str(exc)}
    return {
        "ok": True,
        "message": "AI provider test succeeded.",
        "model": response.get("model") or config.model,
        "sample": response.get("content") or "",
        "usage": response.get("usage") or {},
    }
