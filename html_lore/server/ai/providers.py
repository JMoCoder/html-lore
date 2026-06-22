from __future__ import annotations

import json
import socket
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from html_lore.server.config import ServerSettings


SUPPORTED_PROVIDERS = {"fake", "openai-compatible"}


class AIProviderConfigError(ValueError):
    pass


class ProviderCallError(RuntimeError):
    pass


@dataclass(frozen=True)
class AIProviderConfig:
    provider: str = ""
    base_url: str = ""
    model: str = "gpt-5.5"
    embedding_model: str = ""
    enabled: bool = False
    secret_ref: str = "env:HTML_LORE_AI_API_KEY"
    api_key: str = ""

    @property
    def configured(self) -> bool:
        if not self.enabled or not self.provider:
            return False
        if self.provider == "fake":
            return True
        return bool(self.base_url and self.model and self.api_key)

    def public_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "base_url": self.base_url,
            "model": self.model,
            "embedding_model": self.embedding_model,
            "enabled": self.enabled,
            "configured": self.configured,
            "secret_ref": self.secret_ref,
            "has_api_key": bool(self.api_key),
        }


class AIProviderConfigStore:
    def __init__(self, settings: ServerSettings) -> None:
        self.settings = settings
        self.path = provider_config_path(settings)

    def get(self) -> AIProviderConfig:
        stored = read_provider_config(self.path)
        provider = str(stored.get("provider") or "").strip()
        base_url = str(stored.get("base_url") or "").strip()
        model = str(stored.get("model") or "").strip()
        embedding_model = str(stored.get("embedding_model") or "").strip()
        enabled = bool(stored.get("enabled", False))

        if self.settings.ai_provider:
            provider = self.settings.ai_provider
        if self.settings.ai_base_url:
            base_url = self.settings.ai_base_url
        if self.settings.ai_model:
            model = self.settings.ai_model
        if self.settings.ai_embedding_model:
            embedding_model = self.settings.ai_embedding_model
        if self.settings.ai_enabled:
            enabled = True

        return AIProviderConfig(
            provider=provider,
            base_url=base_url,
            model=model or "gpt-5.5",
            embedding_model=embedding_model,
            enabled=enabled,
            api_key=self.settings.ai_api_key,
        )

    def update(self, values: dict[str, Any]) -> AIProviderConfig:
        if self.path is None:
            raise AIProviderConfigError("Metadata directory is not configured.")
        current = self.get()
        provider = normalize_provider(values.get("provider", current.provider))
        base_url = normalize_text(values.get("base_url", current.base_url))
        model = normalize_text(values.get("model", current.model)) or "gpt-5.5"
        embedding_model = normalize_text(values.get("embedding_model", current.embedding_model))
        enabled = bool(values.get("enabled", current.enabled))
        if "api_key" in values:
            raise AIProviderConfigError("API key must be configured on the server, not through this endpoint.")
        config = {
            "provider": provider,
            "base_url": base_url,
            "model": model,
            "embedding_model": embedding_model,
            "enabled": enabled,
            "secret_ref": "env:HTML_LORE_AI_API_KEY",
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(config, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return self.get()


class ProviderAdapter:
    def chat(self, *, messages: list[dict[str, str]], temperature: float = 0.2, max_tokens: int = 1024) -> dict[str, Any]:
        raise NotImplementedError

    def embed(self, *, text: str) -> list[float]:
        raise NotImplementedError


class FakeProviderAdapter(ProviderAdapter):
    def __init__(self, config: AIProviderConfig) -> None:
        self.config = config

    def chat(self, *, messages: list[dict[str, str]], temperature: float = 0.2, max_tokens: int = 1024) -> dict[str, Any]:
        last_user = next((message.get("content", "") for message in reversed(messages) if message.get("role") == "user"), "")
        return {
            "model": self.config.model,
            "content": build_fake_chat_content(last_user),
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            "raw_provider": "fake",
        }

    def embed(self, *, text: str) -> list[float]:
        if not self.config.embedding_model:
            raise NotImplementedError("Embedding model is not configured.")
        normalized = str(text or "").lower()
        vector = [0.0] * 32
        for index, char in enumerate(normalized):
            vector[(ord(char) + index) % len(vector)] += 1.0
        return normalize_vector(vector)


class OpenAICompatibleHttpAdapter(ProviderAdapter):
    def __init__(self, config: AIProviderConfig) -> None:
        self.config = config

    def chat(self, *, messages: list[dict[str, str]], temperature: float = 0.2, max_tokens: int = 1024) -> dict[str, Any]:
        if not self.config.api_key:
            raise ProviderCallError("AI API key is not configured.")
        if not self.config.base_url:
            raise ProviderCallError("AI base URL is not configured.")
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            chat_completions_url(self.config.base_url),
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "Content-Length": str(len(body)),
                "User-Agent": "HTMlore/1.0.3 curl-compatible",
                "Accept": "application/json, text/event-stream",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                raw_response = response.read().decode("utf-8")
                data = parse_provider_response(raw_response)
        except urllib.error.HTTPError as exc:
            detail = provider_error_detail(exc)
            raise ProviderCallError(f"AI provider returned HTTP {exc.code}{detail}.") from exc
        except (TimeoutError, socket.timeout, urllib.error.URLError, OSError) as exc:
            raise ProviderCallError("AI provider is unreachable.") from exc
        except json.JSONDecodeError as exc:
            raise ProviderCallError("AI provider returned invalid JSON.") from exc
        response = normalize_chat_completion(data, self.config.model)
        if not response["content"].strip():
            raise ProviderCallError("AI provider returned an empty response.")
        return response

    def embed(self, *, text: str) -> list[float]:
        if not self.config.api_key:
            raise ProviderCallError("AI API key is not configured.")
        if not self.config.base_url:
            raise ProviderCallError("AI base URL is not configured.")
        if not self.config.embedding_model:
            raise ProviderCallError("AI embedding model is not configured.")
        payload = {"model": self.config.embedding_model, "input": str(text or "")}
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            embeddings_url(self.config.base_url),
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "Content-Length": str(len(body)),
                "User-Agent": "HTMlore/1.0.3 curl-compatible",
                "Accept": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = provider_error_detail(exc)
            raise ProviderCallError(f"AI embedding provider returned HTTP {exc.code}{detail}.") from exc
        except (TimeoutError, socket.timeout, urllib.error.URLError, OSError) as exc:
            raise ProviderCallError("AI embedding provider is unreachable.") from exc
        except json.JSONDecodeError as exc:
            raise ProviderCallError("AI embedding provider returned invalid JSON.") from exc
        return normalize_embedding_response(data)


def provider_config_path(settings: ServerSettings) -> Path | None:
    if settings.meta_dir is None:
        return None
    return settings.meta_dir / "config" / "ai_provider.json"


def read_provider_config(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AIProviderConfigError("AI provider config is not valid JSON.") from exc
    if not isinstance(data, dict):
        raise AIProviderConfigError("AI provider config must be a JSON object.")
    return data


def normalize_provider(value: Any) -> str:
    provider = normalize_text(value)
    if provider not in SUPPORTED_PROVIDERS:
        raise AIProviderConfigError("Unsupported AI provider.")
    return provider


def normalize_text(value: Any) -> str:
    return str(value or "").strip()


def build_adapter(config: AIProviderConfig) -> ProviderAdapter:
    if config.provider == "fake":
        return FakeProviderAdapter(config)
    if config.provider == "openai-compatible":
        return OpenAICompatibleHttpAdapter(config)
    raise AIProviderConfigError("Unsupported AI provider.")


def chat_completions_url(base_url: str) -> str:
    base = base_url.rstrip("/")
    if base.endswith("/v1"):
        return f"{base}/chat/completions"
    return f"{base}/v1/chat/completions"


def embeddings_url(base_url: str) -> str:
    base = base_url.rstrip("/")
    if base.endswith("/v1"):
        return f"{base}/embeddings"
    return f"{base}/v1/embeddings"


def parse_provider_response(raw_response: str) -> dict[str, Any]:
    text = raw_response.strip()
    if not text:
        raise ProviderCallError("AI provider returned an empty response.")
    if not text.startswith("data:"):
        return json.loads(text)
    return parse_sse_chat_completion(text)


def parse_sse_chat_completion(text: str) -> dict[str, Any]:
    model = ""
    usage: dict[str, Any] = {}
    content_parts: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("data:"):
            continue
        payload = stripped.removeprefix("data:").strip()
        if not payload or payload == "[DONE]":
            continue
        chunk = json.loads(payload)
        if isinstance(chunk.get("model"), str) and chunk["model"]:
            model = chunk["model"]
        if isinstance(chunk.get("usage"), dict):
            usage = chunk["usage"]
        choices = chunk.get("choices")
        if not isinstance(choices, list):
            continue
        for choice in choices:
            if not isinstance(choice, dict):
                continue
            delta = choice.get("delta") if isinstance(choice.get("delta"), dict) else {}
            message = choice.get("message") if isinstance(choice.get("message"), dict) else {}
            content = delta.get("content") if "content" in delta else message.get("content")
            if content:
                content_parts.append(str(content))
    return {
        "model": model,
        "choices": [{"message": {"content": "".join(content_parts)}}],
        "usage": usage,
    }


def normalize_chat_completion(data: dict[str, Any], fallback_model: str) -> dict[str, Any]:
    choices = data.get("choices") if isinstance(data, dict) else None
    choice = choices[0] if isinstance(choices, list) and choices else {}
    message = choice.get("message") if isinstance(choice, dict) else {}
    content = str(message.get("content") or "") if isinstance(message, dict) else ""
    usage = data.get("usage") if isinstance(data.get("usage"), dict) else {}
    return {
        "model": str(data.get("model") or fallback_model),
        "content": content,
        "usage": usage,
        "raw_provider": "openai-compatible",
    }


def normalize_embedding_response(data: dict[str, Any]) -> list[float]:
    rows = data.get("data") if isinstance(data, dict) else None
    first = rows[0] if isinstance(rows, list) and rows else {}
    embedding = first.get("embedding") if isinstance(first, dict) else None
    if not isinstance(embedding, list) or not embedding:
        raise ProviderCallError("AI embedding provider returned no embedding.")
    vector: list[float] = []
    for value in embedding:
        try:
            vector.append(float(value))
        except (TypeError, ValueError) as exc:
            raise ProviderCallError("AI embedding provider returned a non-numeric embedding.") from exc
    return normalize_vector(vector)


def normalize_vector(vector: list[float]) -> list[float]:
    norm = sum(value * value for value in vector) ** 0.5
    if norm <= 0:
        return vector
    return [value / norm for value in vector]


def build_fake_chat_content(last_user: str) -> str:
    question = extract_fake_prompt_field(last_user, "USER_QUESTION") or last_user.strip()
    intent = extract_fake_prompt_field(last_user, "TASK_INTENT").lower()
    context_title = extract_fake_prompt_field(last_user, "CURRENT_CONTEXT") or "当前上下文"
    prefix = f"Fake AI response for: {question[:120]}"
    if intent == "concept_clarify":
        body = (
            f"可以理解为，{question.strip('？?')}首先是一个需要先抓住定义、再看应用边界的概念。"
            f" 在当前上下文「{context_title}」里，它更重要的作用是帮助读懂整篇笔记的主题结构。"
        )
    elif intent == "explain_deeper":
        body = (
            f"围绕这个问题，可以从三个层面展开：第一，先明确核心对象和边界；第二，梳理它们之间的作用链与协同关系；"
            f"第三，再回到「{context_title}」判断这些关系为什么重要。这样会比一句定义更接近用户真正想问的内容。"
        )
    elif intent == "current_info":
        body = (
            "先给出当前可核验的结论，再补充必要背景。"
            f" 如果「{context_title}」只提供了部分线索，就应该明确哪些是已核验事实，哪些只是背景解释。"
        )
    elif intent == "compare_validate":
        body = (
            f"这个问题适合先并列关键对象，再比较它们的定义、边界和用途，最后回到「{context_title}」说明差异为什么重要。"
        )
    else:
        body = f"这部分内容可以先概括为：围绕「{context_title}」，先抓住与问题直接相关的核心信息，再展开解释。"
    return f"{prefix}\n\n{body}".strip()


def extract_fake_prompt_field(content: str, field_name: str) -> str:
    marker = f"{field_name}:"
    text = str(content or "")
    start = text.find(marker)
    if start < 0:
        return ""
    tail = text[start + len(marker):]
    return tail.split("\n\n", 1)[0].strip()


def provider_error_detail(exc: urllib.error.HTTPError) -> str:
    try:
        raw = exc.read().decode("utf-8", errors="replace")
    except Exception:
        return ""
    if not raw:
        return ""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return f": {raw[:180]}"
    for key in ("message", "detail", "error_name", "title"):
        value = data.get(key)
        if isinstance(value, str) and value:
            return f": {value[:180]}"
    return ""
