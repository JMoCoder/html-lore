from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Protocol
from urllib.parse import urlparse

from html_lore.server.config import ServerSettings
from .search_planner import MAX_EXTERNAL_QUERY_CHARS, drop_internal_url_tokens, expand_search_query_terms, prepare_external_search_query


class ExternalSearchError(RuntimeError):
    pass


class ExternalSearchUnavailable(ExternalSearchError):
    pass


class ExternalSearchProviderError(ExternalSearchError):
    pass


TAVILY_SEARCH_URL = "https://api.tavily.com/search"
BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"
TAVILY_DEPTHS = {"basic", "fast", "ultra-fast", "advanced"}
TAVILY_TOPICS = {"general", "news", "finance"}
TAVILY_TIME_RANGES = {"day", "week", "month", "year", "d", "w", "m", "y"}


@dataclass(frozen=True)
class ExternalSearchResult:
    title: str
    url: str
    snippet: str
    accessed_at: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": "external",
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "accessed_at": self.accessed_at,
        }


class ExternalSearchAdapter(Protocol):
    name: str

    @property
    def available(self) -> bool:
        pass

    def search(self, query: str, *, max_results: int = 5) -> list[ExternalSearchResult]:
        pass


class DisabledExternalSearchAdapter:
    name = "disabled"

    @property
    def available(self) -> bool:
        return False

    def search(self, query: str, *, max_results: int = 5) -> list[ExternalSearchResult]:
        raise ExternalSearchUnavailable("External content expansion is not configured.")


class FakeExternalSearchAdapter:
    name = "fake"

    def __init__(self, *, max_results: int = 5) -> None:
        self.max_results = max(1, min(int(max_results or 5), 10))

    @property
    def available(self) -> bool:
        return True

    def search(self, query: str, *, max_results: int = 5) -> list[ExternalSearchResult]:
        safe_limit = max(1, min(int(max_results or self.max_results), self.max_results))
        cleaned = " ".join(str(query or "").split()) or "HTMlore"
        return [
            ExternalSearchResult(
                title=f"External reference for {cleaned[:48]}",
                url=f"https://example.test/search?q={cleaned.replace(' ', '+')}",
                snippet=f"Fake external source related to: {cleaned[:160]}",
                accessed_at=utc_now(),
            ),
        ][:safe_limit]


class TavilyExternalSearchAdapter:
    name = "tavily"

    def __init__(
        self,
        *,
        api_key: str,
        max_results: int = 5,
        search_depth: str = "basic",
        auto_parameters: bool = False,
        topic: str = "general",
        time_range: str = "",
        include_raw_content: bool = False,
    ) -> None:
        self.api_key = str(api_key or "")
        self.max_results = max(1, min(int(max_results or 5), 20))
        self.search_depth = normalize_choice(search_depth, TAVILY_DEPTHS, "basic")
        self.auto_parameters = bool(auto_parameters)
        self.topic = normalize_choice(topic, TAVILY_TOPICS, "general")
        self.time_range = normalize_choice(time_range, TAVILY_TIME_RANGES | {""}, "")
        self.include_raw_content = bool(include_raw_content)

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    def search(self, query: str, *, max_results: int = 5) -> list[ExternalSearchResult]:
        if not self.available:
            raise ExternalSearchUnavailable("Tavily external search API key is not configured.")
        safe_limit = max(1, min(int(max_results or self.max_results), self.max_results, 20))
        payload = build_tavily_payload(
            query,
            max_results=safe_limit,
            search_depth=self.search_depth,
            auto_parameters=self.auto_parameters,
            topic=self.topic,
            time_range=self.time_range,
            include_raw_content=self.include_raw_content,
        )
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            TAVILY_SEARCH_URL,
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Content-Length": str(len(body)),
                "User-Agent": "HTMlore/1.0.4 tavily-search",
                "Accept": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise ExternalSearchProviderError(f"Tavily returned HTTP {exc.code}.") from exc
        except urllib.error.URLError as exc:
            raise ExternalSearchProviderError("Tavily external search is unreachable.") from exc
        except json.JSONDecodeError as exc:
            raise ExternalSearchProviderError("Tavily returned invalid JSON.") from exc
        return parse_tavily_results(data)


class BraveExternalSearchAdapter:
    name = "brave"

    def __init__(self, *, api_key: str, max_results: int = 5, search_lang: str = "", country: str = "", freshness: str = "") -> None:
        self.api_key = str(api_key or "")
        self.max_results = max(1, min(int(max_results or 5), 20))
        self.search_lang = normalize_choice(search_lang, {"", "en", "zh", "ja", "de", "fr", "es", "pt", "it", "nl", "ru", "sv", "no", "da", "fi", "pl", "tr", "ko", "cs", "hu", "vi", "th", "id"}, "")
        self.country = str(country or "").strip().lower()
        self.freshness = normalize_choice(freshness, {"", "pd", "pw", "pm", "py"}, "")

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    def search(self, query: str, *, max_results: int = 5) -> list[ExternalSearchResult]:
        if not self.available:
            raise ExternalSearchUnavailable("Brave Search API key is not configured.")
        safe_limit = max(1, min(int(max_results or self.max_results), self.max_results, 20))
        prepared, _ = prepare_external_search_query(query)
        payload = {
            "q": prepared,
            "count": safe_limit,
            "search_lang": self.search_lang or select_brave_search_lang(prepared),
        }
        country = self.country or extract_country_hint(prepared)
        if country:
            payload["country"] = country
        freshness = self.freshness or select_brave_freshness(prepared)
        if freshness:
            payload["freshness"] = freshness
        url = f"{BRAVE_SEARCH_URL}?{urllib.parse.urlencode(payload)}"
        request = urllib.request.Request(
            url,
            method="GET",
            headers={
                "X-Subscription-Token": self.api_key,
                "Accept": "application/json",
                "User-Agent": "HTMlore/1.0.4 brave-search",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise ExternalSearchProviderError(f"Brave returned HTTP {exc.code}.") from exc
        except urllib.error.URLError as exc:
            raise ExternalSearchProviderError("Brave external search is unreachable.") from exc
        except json.JSONDecodeError as exc:
            raise ExternalSearchProviderError("Brave returned invalid JSON.") from exc
        return parse_brave_results(data)


def build_external_search_adapter(settings: ServerSettings) -> ExternalSearchAdapter:
    provider = settings.ai_external_search.strip().lower()
    brave_adapter = BraveExternalSearchAdapter(
        api_key=settings.ai_external_search_brave_api_key,
        max_results=settings.ai_external_search_max_results,
        search_lang="",
        country="",
        freshness="",
    )
    tavily_adapter = TavilyExternalSearchAdapter(
        api_key=settings.ai_external_search_api_key,
        max_results=settings.ai_external_search_max_results,
        search_depth=settings.ai_external_search_depth,
        auto_parameters=settings.ai_external_search_auto_parameters,
        topic=settings.ai_external_search_topic,
        time_range=settings.ai_external_search_time_range,
        include_raw_content=settings.ai_external_search_include_raw_content,
    )
    if provider == "fake":
        return FakeExternalSearchAdapter(max_results=settings.ai_external_search_max_results)
    if provider == "tavily":
        if brave_adapter.available:
            return ChainedExternalSearchAdapter([tavily_adapter, brave_adapter], max_results=settings.ai_external_search_max_results)
        return tavily_adapter
    if provider == "brave":
        return brave_adapter if brave_adapter.available else DisabledExternalSearchAdapter()
    if provider == "tavily+brave" or provider == "brave+tavily":
        return ChainedExternalSearchAdapter([tavily_adapter, brave_adapter], max_results=settings.ai_external_search_max_results)
    if brave_adapter.available and tavily_adapter.available:
        return ChainedExternalSearchAdapter([tavily_adapter, brave_adapter], max_results=settings.ai_external_search_max_results)
    if tavily_adapter.available:
        return tavily_adapter
    if brave_adapter.available:
        return brave_adapter
    return DisabledExternalSearchAdapter()


class ChainedExternalSearchAdapter:
    def __init__(self, adapters: list[ExternalSearchAdapter], *, max_results: int = 5) -> None:
        self.adapters = [adapter for adapter in adapters if adapter is not None and adapter.available]
        self.max_results = max(1, int(max_results or 5))
        self.name = "+".join(adapter.name for adapter in self.adapters) if self.adapters else "disabled"

    @property
    def available(self) -> bool:
        return any(adapter.available for adapter in self.adapters)

    def search(self, query: str, *, max_results: int = 5) -> list[ExternalSearchResult]:
        last_error: Exception | None = None
        for adapter in self.adapters:
            if not adapter.available:
                continue
            try:
                return adapter.search(query, max_results=max_results)
            except ExternalSearchUnavailable as exc:
                last_error = exc
                continue
            except ExternalSearchProviderError as exc:
                last_error = exc
                continue
        if last_error is not None:
            raise ExternalSearchUnavailable(str(last_error))
        raise ExternalSearchUnavailable("External content expansion is not configured.")


def sanitize_external_results(results: list[ExternalSearchResult]) -> tuple[list[dict[str, Any]], int]:
    safe: list[dict[str, Any]] = []
    dropped = 0
    for result in results:
        data = result.as_dict()
        if is_safe_external_url(data.get("url")):
            safe.append(data)
        else:
            dropped += 1
    return safe, dropped


def is_safe_external_url(value: Any) -> bool:
    parsed = urlparse(str(value or "").strip())
    if parsed.scheme not in {"http", "https"}:
        return False
    host = (parsed.hostname or "").lower()
    if not host:
        return False
    if host in {"localhost", "127.0.0.1", "0.0.0.0"} or host.endswith(".localhost"):
        return False
    if host.startswith("10.") or host.startswith("192.168.") or host.startswith("169.254."):
        return False
    if parsed.path.startswith(("/api/", "/content/", "/share/", "/public/")):
        return False
    return True


def build_tavily_payload(
    query: Any,
    *,
    max_results: int,
    search_depth: str,
    auto_parameters: bool,
    topic: str,
    time_range: str,
    include_raw_content: bool,
) -> dict[str, Any]:
    prepared, _ = prepare_external_search_query(query)
    selected_topic = select_tavily_topic(prepared, topic)
    payload: dict[str, Any] = {
        "query": prepared,
        "max_results": max(1, min(int(max_results or 5), 20)),
        "search_depth": select_tavily_search_depth(prepared, search_depth),
        "topic": selected_topic,
        "include_answer": False,
        "include_raw_content": bool(include_raw_content),
    }
    selected_time_range = select_tavily_time_range(prepared, time_range, selected_topic)
    if selected_time_range:
        payload["time_range"] = selected_time_range
    country = extract_country_hint(prepared)
    if country:
        payload["country"] = country
    if auto_parameters:
        payload["auto_parameters"] = True
    return payload


def select_tavily_search_depth(query: str, configured: str) -> str:
    configured = normalize_choice(configured, TAVILY_DEPTHS, "basic")
    if configured == "advanced":
        return "advanced"
    if asks_for_deep_research(query):
        return "advanced"
    return configured


def select_tavily_topic(query: str, configured: str) -> str:
    configured = normalize_choice(configured, TAVILY_TOPICS, "general")
    if configured != "general":
        return configured
    lowered = str(query or "").lower()
    if any(marker in lowered for marker in ("stock", "earnings", "revenue", "market cap", "sec filing", "finance", "股票", "财报", "营收", "市值", "金融", "決算", "株価")):
        return "finance"
    if is_time_sensitive_search_query(query):
        return "news"
    return "general"


def select_tavily_time_range(query: str, configured: str, topic: str) -> str:
    configured = normalize_choice(configured, TAVILY_TIME_RANGES | {""}, "")
    if configured:
        return configured
    lowered = str(query or "").lower()
    if any(marker in lowered for marker in ("today", "24h", "今日", "今天")):
        return "day"
    if any(marker in lowered for marker in ("this week", "weekly", "本周", "今週")):
        return "week"
    if topic == "news" or is_time_sensitive_search_query(query):
        return "month"
    return ""


def extract_country_hint(query: str) -> str:
    lowered = str(query or "").lower()
    mapping = {
        "us": (" in us", " in the us", "united states", "美国", "美國", "アメリカ", "米国"),
        "china": (" in china", "china ", "中国", "中國"),
        "japan": (" in japan", "japan ", "日本"),
        "germany": (" in germany", "germany ", "德国", "德國", "ドイツ"),
        "uk": (" in uk", " in the uk", "united kingdom", "英国", "英國", "イギリス"),
    }
    for country, markers in mapping.items():
        if any(marker in lowered for marker in markers):
            return country
    explicit = re.search(r"\bcountry\s*[:=]\s*([a-z][a-z -]{1,32})\b", lowered)
    if explicit:
        return explicit.group(1).strip().replace(" ", "-")
    return ""


def asks_for_deep_research(query: str) -> bool:
    lowered = str(query or "").lower()
    markers = [
        "deep research",
        "comprehensive",
        "compare sources",
        "multiple sources",
        "full report",
        "深入研究",
        "深度研究",
        "全面梳理",
        "多来源",
        "複数ソース",
        "詳しく調査",
    ]
    return any(marker in lowered for marker in markers)


def is_time_sensitive_search_query(query: str) -> bool:
    lowered = str(query or "").lower()
    markers = [
        "latest",
        "current",
        "today",
        "yesterday",
        "recent",
        "now",
        "news",
        "release",
        "version",
        "price",
        "policy",
        "law",
        "最新",
        "当前",
        "现在",
        "今天",
        "昨天",
        "最近",
        "新闻",
        "发布",
        "版本",
        "价格",
        "政策",
        "法律",
        "現在",
        "今日",
        "昨日",
        "最近",
        "ニュース",
        "リリース",
        "価格",
    ]
    if any(marker in lowered for marker in markers):
        return True
    year = datetime.now(timezone.utc).year
    return str(year) in lowered or str(year - 1) in lowered or str(year + 1) in lowered


def parse_tavily_results(data: dict[str, Any]) -> list[ExternalSearchResult]:
    raw_results = data.get("results") if isinstance(data, dict) else []
    if not isinstance(raw_results, list):
        return []
    results: list[ExternalSearchResult] = []
    for item in raw_results:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or item.get("url") or "External source").strip()
        url = str(item.get("url") or "").strip()
        snippet = str(item.get("content") or item.get("raw_content") or "").strip()
        if not url or not snippet:
            continue
        results.append(ExternalSearchResult(title=title[:180], url=url, snippet=snippet[:1200], accessed_at=utc_now()))
    return results


def parse_brave_results(data: dict[str, Any]) -> list[ExternalSearchResult]:
    web = data.get("web") if isinstance(data, dict) else {}
    results = web.get("results") if isinstance(web, dict) else []
    if not isinstance(results, list):
        return []
    parsed: list[ExternalSearchResult] = []
    for item in results:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or item.get("url") or "External source").strip()
        url = str(item.get("url") or "").strip()
        snippet = str(item.get("description") or item.get("snippet") or "").strip()
        if not url or not snippet:
            continue
        parsed.append(ExternalSearchResult(title=title[:180], url=url, snippet=snippet[:1200], accessed_at=utc_now()))
    return parsed


def select_brave_search_lang(query: str) -> str:
    text = str(query or "")
    if any("\u4e00" <= char <= "\u9fff" for char in text):
        return "zh"
    if any("\u3040" <= char <= "\u30ff" for char in text):
        return "ja"
    return "en"


def select_brave_freshness(query: str) -> str:
    lowered = str(query or "").lower()
    if any(marker in lowered for marker in ("today", "24h", "今日", "今天")):
        return "pd"
    if any(marker in lowered for marker in ("this week", "weekly", "本周", "今週")):
        return "pw"
    if is_time_sensitive_search_query(query):
        return "pm"
    return ""


def normalize_choice(value: str, choices: set[str], default: str) -> str:
    normalized = str(value or "").strip().lower()
    return normalized if normalized in choices else default


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
