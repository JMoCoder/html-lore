from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse


MAX_EXTERNAL_QUERY_CHARS = 240
ZH_ENTITY_SUFFIXES = (
    "资本",
    "公司",
    "基金",
    "集团",
    "能源",
    "投资",
    "控股",
    "管理",
    "资管",
    "证券",
    "银行",
    "科技",
    "合伙企业",
    "事务所",
    "协会",
    "管理人",
)
EN_ENTITY_SUFFIXES = (
    "capital",
    "fund",
    "management",
    "holdings",
    "energy",
    "group",
    "partners",
    "ventures",
    "investment",
    "investments",
    "company",
    "co",
    "inc",
    "corp",
    "llc",
    "ltd",
)


@dataclass(frozen=True)
class SearchPlan:
    original_query: str
    intent: str
    queries: list[str]
    required_terms: list[str]
    preferred_domains: list[str]
    authoritative_required: bool
    query_expansions: list[str]
    evidence_terms: list[str]

    def public_report(self) -> dict[str, Any]:
        return {
            "search_intent": self.intent,
            "planned_query_count": len(self.queries),
            "required_terms": self.required_terms,
            "preferred_domains": self.preferred_domains,
            "authoritative_required": self.authoritative_required,
            "query_expansions": self.query_expansions,
            "evidence_terms": self.evidence_terms,
        }


def plan_external_search(query: Any, *, max_chars: int = MAX_EXTERNAL_QUERY_CHARS) -> SearchPlan:
    prepared, report = prepare_external_search_query(query, max_chars=max_chars)
    intent = classify_search_intent(prepared)
    required_terms = required_entity_terms(prepared)
    preferred_domains = preferred_source_domains(prepared, intent)
    authoritative_required = intent in {"official_version", "official_docs"}
    evidence_terms = search_evidence_terms(intent)
    queries = planned_queries(prepared, intent, preferred_domains, max_chars=max_chars)
    return SearchPlan(
        original_query=prepared,
        intent=intent,
        queries=queries,
        required_terms=required_terms,
        preferred_domains=preferred_domains,
        authoritative_required=authoritative_required,
        query_expansions=list(report.get("query_expansions") or []),
        evidence_terms=evidence_terms,
    )


def prepare_external_search_query(query: Any, *, max_chars: int = MAX_EXTERNAL_QUERY_CHARS) -> tuple[str, dict[str, Any]]:
    raw = " ".join(str(query or "").split())
    without_internal = drop_internal_url_tokens(raw)
    expanded, expansion_report = expand_search_query_terms(without_internal)
    truncated = len(expanded) > max_chars
    prepared = expanded[:max_chars].strip()
    return prepared, {
        "query_chars": len(prepared),
        "query_truncated": truncated,
        "blocked_internal_url_tokens": prepared != raw[: len(prepared)].strip(),
        **expansion_report,
    }


def expand_search_query_terms(query: str) -> tuple[str, dict[str, Any]]:
    expanded = str(query or "")
    expansions: list[str] = []
    if re.search(r"(?<![A-Za-z0-9])MCP(?![A-Za-z0-9])", expanded) and "Model Context Protocol" not in expanded:
        expanded = f"Model Context Protocol MCP {expanded}"
        expansions.append("mcp_model_context_protocol")
    return expanded, {"query_expansions": expansions}


def drop_internal_url_tokens(value: str) -> str:
    kept: list[str] = []
    for token in str(value or "").split():
        if "://" in token and not is_safe_query_url_token(token):
            continue
        kept.append(token)
    return " ".join(kept)


def is_safe_query_url_token(value: Any) -> bool:
    parsed = urlparse(str(value or "").strip())
    if not parsed.scheme:
        return True
    if parsed.scheme not in {"http", "https"}:
        return False
    host = (parsed.hostname or "").lower()
    if not host:
        return False
    if host in {"localhost", "127.0.0.1", "0.0.0.0"} or host.endswith(".localhost"):
        return False
    if host.startswith(("10.", "192.168.", "169.254.")):
        return False
    return True


def classify_search_intent(query: str) -> str:
    lowered = str(query or "").lower()
    official = any(marker in lowered for marker in ("official", "官网", "官方", "公式"))
    versionish = any(marker in lowered for marker in ("version", "release", "changelog", "发布", "版本", "リリース", "バージョン"))
    docish = any(marker in lowered for marker in ("spec", "specification", "docs", "documentation", "规范", "文档", "ドキュメント"))
    policyish = any(marker in lowered for marker in ("policy", "regulation", "政策", "法规", "监管", "发改", "能源局", "电力市场"))
    if is_case_search_question(query):
        return "case_search"
    entity_attribute = classify_entity_question_attribute(query)
    if entity_attribute == "ownership":
        return "entity_ownership"
    if entity_attribute == "team":
        return "entity_team"
    if entity_attribute == "registry":
        return "entity_registry"
    if entity_attribute == "background" or is_entity_lookup_question(query):
        return "entity_background"
    if official and versionish:
        return "official_version"
    if official and docish:
        return "official_docs"
    if versionish:
        return "version_lookup"
    if policyish:
        return "policy_lookup"
    if any(marker in lowered for marker in ("deep research", "深入研究", "深度研究", "多来源", "compare sources")):
        return "research"
    return "general"


def required_entity_terms(query: str) -> list[str]:
    lowered = str(query or "").lower()
    if is_case_search_question(query):
        return []
    extracted = extract_entity_terms(query)
    if extracted:
        return extracted
    if "model context protocol" in lowered or re.search(r"(?<![a-z0-9])mcp(?![a-z0-9])", lowered):
        return ["model context protocol", "mcp"]
    return []


def preferred_source_domains(query: str, intent: str) -> list[str]:
    lowered = str(query or "").lower()
    if intent in {"entity_background", "entity_ownership", "entity_team", "entity_registry"}:
        return ["gsxt.gov.cn", "amac.org.cn", "qcc.com", "tianyancha.com", "企查查", "天眼查"]
    if "model context protocol" in lowered or re.search(r"(?<![a-z0-9])mcp(?![a-z0-9])", lowered):
        return ["modelcontextprotocol.io", "github.com/modelcontextprotocol"]
    return []


def planned_queries(query: str, intent: str, preferred_domains: list[str], *, max_chars: int) -> list[str]:
    base = str(query or "").strip()
    candidates = [base]
    required_terms = required_entity_terms(base)
    primary_entity = required_terms[0] if required_terms else ""
    if intent == "case_search":
        case_terms = extract_case_search_terms(base)
        if case_terms:
            joined = " ".join(case_terms)
            candidates = [
                f"{joined} 案例",
                f"{joined} case study",
                f"{joined} 投资案例 交易结构",
                base,
            ]
    if intent == "entity_background" and primary_entity:
        if any("\u4e00" <= char <= "\u9fff" for char in primary_entity):
            candidates = [
                f"{primary_entity} 官网",
                f"{primary_entity} 工商 股东 备案",
                f"{primary_entity} 私募 管理人 协会",
                f"{primary_entity} 背景 团队 注册地",
                base,
            ]
        else:
            candidates = [
                f"{primary_entity} official website",
                f"{primary_entity} company background shareholders registration",
                f"{primary_entity} management team profile",
                base,
            ]
    if intent == "entity_ownership" and primary_entity:
        if any("\u4e00" <= char <= "\u9fff" for char in primary_entity):
            candidates = [
                f"{primary_entity} 工商 股东 持股比例 备案",
                f"{primary_entity} 股权结构 股东 实控人",
                f"{primary_entity} 天眼查 股权结构",
                f"{primary_entity} 企查查 股东",
                base,
            ]
        else:
            candidates = [
                f"{primary_entity} ownership shareholders cap table",
                f"{primary_entity} shareholder structure registry",
                f"{primary_entity} beneficial owner filing",
                base,
            ]
    if intent == "entity_team" and primary_entity:
        if any("\u4e00" <= char <= "\u9fff" for char in primary_entity):
            candidates = [
                f"{primary_entity} 管理团队 高管 创始人",
                f"{primary_entity} 负责人 董事 总经理",
                f"{primary_entity} 官网 团队",
                base,
            ]
        else:
            candidates = [
                f"{primary_entity} management team founders executives",
                f"{primary_entity} leadership profile official",
                base,
            ]
    if intent == "entity_registry" and primary_entity:
        if any("\u4e00" <= char <= "\u9fff" for char in primary_entity):
            candidates = [
                f"{primary_entity} 工商 登记 注册信息 统一社会信用代码",
                f"{primary_entity} 企业信用 信息公示",
                f"{primary_entity} 管理人 协会 备案",
                base,
            ]
        else:
            candidates = [
                f"{primary_entity} registry incorporation registration",
                f"{primary_entity} legal representative registered address",
                base,
            ]
    if intent == "policy_lookup":
        policy_terms = extract_policy_search_terms(base)
        joined = " ".join(policy_terms) if policy_terms else base
        if any("\u4e00" <= char <= "\u9fff" for char in joined):
            candidates = [
                f"{joined} 政策 监管 最新",
                f"{joined} 国家能源局 发改委 政策",
                f"{joined} site:gov.cn",
                base,
            ]
        else:
            candidates = [
                f"{joined} policy regulation latest",
                f"{joined} official government policy",
                base,
            ]
    if preferred_domains and intent in {"official_version", "official_docs", "version_lookup"}:
        candidates = [
            "Model Context Protocol specification latest version release date site:modelcontextprotocol.io",
            "Model Context Protocol specification changelog release notes site:github.com/modelcontextprotocol",
            "Model Context Protocol official specification version date",
            base,
        ]
    result: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        cleaned = " ".join(str(candidate or "").split())[:max_chars].strip()
        if cleaned and cleaned.lower() not in seen:
            result.append(cleaned)
            seen.add(cleaned.lower())
    return result or [base[:max_chars].strip()]


def verify_planned_sources(sources: list[dict[str, Any]], plan: SearchPlan) -> tuple[list[dict[str, Any]], dict[str, int]]:
    if not sources:
        return [], {"verified_count": 0, "dropped_count": 0}
    kept: list[dict[str, Any]] = []
    dropped = 0
    for source in sources:
        if source_matches_plan(source, plan):
            scored = dict(source)
            score, tier = source_authority_score(scored, plan)
            scored["authority_score"] = score
            scored["authority_tier"] = tier
            kept.append(scored)
        else:
            dropped += 1
    kept = sort_planned_sources(kept)
    return kept, {"verified_count": len(kept), "dropped_count": dropped}


def source_matches_plan(source: dict[str, Any], plan: SearchPlan) -> bool:
    if plan.intent in {"case_search", "research", "general"} and not plan.authoritative_required:
        return True
    if not plan.required_terms and not plan.authoritative_required:
        return True
    text = " ".join(
        str(source.get(key) or "")
        for key in ("title", "url", "snippet")
    ).lower()
    entity_match = not plan.required_terms or any(term in text for term in plan.required_terms)
    if not entity_match:
        return False
    if plan.evidence_terms and not any(term in text for term in plan.evidence_terms):
        return False
    if not plan.authoritative_required:
        return True
    url = str(source.get("url") or "").lower()
    preferred = any(domain in url for domain in plan.preferred_domains)
    if preferred:
        return True
    authority_markers = ("official", "specification", "release", "changelog", "version", "docs", "documentation")
    return any(marker in text for marker in authority_markers)


def sort_planned_sources(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        sources,
        key=lambda source: (
            -safe_int(source.get("authority_score"), 0),
            str(source.get("title") or "").lower(),
            str(source.get("url") or "").lower(),
        ),
    )


def source_authority_score(source: dict[str, Any], plan: SearchPlan) -> tuple[int, str]:
    text = " ".join(str(source.get(key) or "") for key in ("title", "url", "snippet")).lower()
    url = str(source.get("url") or "").lower()
    parsed = urlparse(url)
    host = parsed.hostname or ""
    path = parsed.path or ""
    score = 0
    tier = "related"
    if any(domain in url for domain in plan.preferred_domains):
        score += 70
        tier = "preferred"
    if host.endswith("modelcontextprotocol.io"):
        score += 30
        tier = "official"
    if any(marker in path for marker in ("/specification", "/docs", "/changelog", "/posts", "/blog", "/release")):
        score += 18
    if any(marker in text for marker in ("specification", "release candidate", "release notes", "changelog", "version", "official")):
        score += 18
    if "/issues/" in path or "/pull/" in path or "/discussions/" in path:
        score -= 28
        if tier == "preferred":
            tier = "community"
    if any(marker in host for marker in ("medium.com", "reddit.com", "news.ycombinator.com")):
        score -= 20
    if plan.required_terms and any(term in text for term in plan.required_terms):
        score += 12
    return max(score, 0), tier


def safe_int(value: Any, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def is_entity_lookup_question(query: Any) -> bool:
    text = " ".join(str(query or "").split())
    if not text:
        return False
    return bool(extract_entity_terms(text) and classify_entity_question_attribute(text))


def is_entity_background_question(query: Any) -> bool:
    return is_entity_lookup_question(query)


def classify_entity_question_attribute(query: Any) -> str | None:
    text = " ".join(str(query or "").split())
    lowered = text.lower()
    if not text or not extract_entity_terms(text):
        return None
    ownership_markers = (
        "股权",
        "股权结构",
        "股东",
        "持股",
        "实控",
        "控制人",
        "ownership",
        "shareholder",
        "shareholders",
        "equity",
        "cap table",
        "beneficial owner",
    )
    team_markers = (
        "管理团队",
        "团队",
        "高管",
        "创始人",
        "董事",
        "总经理",
        "ceo",
        "founder",
        "leadership",
        "management team",
        "executive",
    )
    registry_markers = (
        "工商",
        "备案",
        "注册",
        "登记",
        "统一社会信用代码",
        "注册地",
        "legal representative",
        "registered address",
        "registry",
        "registration",
        "incorporation",
    )
    background_markers = (
        "背景",
        "官网",
        "官方",
        "介绍一下",
        "是什么背景",
        "谁在管理",
        "管理人",
        "背景资料",
        "profile",
        "background",
        "official website",
        "about",
    )
    if any(marker in lowered for marker in ownership_markers):
        return "ownership"
    if any(marker in lowered for marker in team_markers):
        return "team"
    if any(marker in lowered for marker in registry_markers):
        return "registry"
    if any(marker in lowered for marker in background_markers):
        return "background"
    return "background"


def search_evidence_terms(intent: str) -> list[str]:
    if intent == "case_search":
        return []
    if intent == "entity_ownership":
        return ["股东", "持股", "股权", "实控", "ownership", "shareholder", "equity"]
    if intent == "entity_team":
        return ["团队", "高管", "创始人", "董事", "ceo", "founder", "management", "leadership", "executive"]
    if intent == "entity_registry":
        return ["工商", "注册", "登记", "备案", "统一社会信用代码", "registry", "registration", "incorporation", "legal representative"]
    if intent == "policy_lookup":
        return ["政策", "监管", "法规", "通知", "意见", "发改委", "能源局", "policy", "regulation"]
    return []


def is_case_search_question(query: Any) -> bool:
    lowered = str(query or "").lower()
    return any(marker in lowered for marker in ("案例", "例子", "样本", "类似", "更多利用", "case", "cases", "case study", "examples", "similar"))


def extract_case_search_terms(query: Any) -> list[str]:
    text = " ".join(str(query or "").split())
    if not text:
        return []
    terms: list[str] = []
    candidates = (
        "两层结构",
        "基金/SPV",
        "基金",
        "SPV",
        "项目公司",
        "优先劣后",
        "优先/劣后",
        "优先级",
        "劣后级",
        "股权分层",
        "风险分层",
        "交易结构",
        "project company",
        "preferred equity",
        "subordinated equity",
        "waterfall",
    )
    lowered = text.lower()
    for candidate in candidates:
        if candidate.lower() in lowered and candidate not in terms:
            terms.append(candidate)
    if not terms:
        for token in re.findall(r"[\u4e00-\u9fffA-Za-z0-9+/.-]{2,30}", text):
            if token in {"联网搜索", "更多利用", "这种结构", "这个结构", "案例", "中文", "中国"}:
                continue
            terms.append(token)
            if len(terms) >= 6:
                break
    return terms[:8]


def extract_policy_search_terms(query: Any) -> list[str]:
    text = " ".join(str(query or "").split())
    if not text:
        return []
    terms: list[str] = []
    candidates = (
        "虚拟电厂",
        "电力市场",
        "电力现货",
        "需求响应",
        "分布式资源",
        "储能",
        "virtual power plant",
        "electricity market",
        "demand response",
        "distributed energy resource",
    )
    lowered = text.lower()
    for candidate in candidates:
        if candidate.lower() in lowered and candidate not in terms:
            terms.append(candidate)
    if not terms:
        for token in re.findall(r"[\u4e00-\u9fffA-Za-z0-9+/.-]{2,30}", text):
            if token in {"最近", "国内", "政策", "变化", "哪些", "中国", "中文", "policy", "regulation", "latest"}:
                continue
            terms.append(token)
            if len(terms) >= 5:
                break
    return terms[:6]


def extract_entity_terms(query: Any) -> list[str]:
    text = " ".join(str(query or "").split())
    if not text:
        return []
    matches: list[str] = []
    zh_suffix_pattern = "|".join(re.escape(suffix) for suffix in ZH_ENTITY_SUFFIXES)
    for value in re.findall(rf"([\u4e00-\u9fffA-Za-z0-9]{{2,30}}(?:{zh_suffix_pattern}))", text):
        cleaned = value.strip("：:，,。.;；、()（）[]【】\"'")
        if cleaned:
            matches.append(cleaned)
    english_pattern = re.compile(
        r"\b([A-Z][A-Za-z0-9&'.-]*(?:\s+[A-Z][A-Za-z0-9&'.-]*){0,4}\s+(?:"
        + "|".join(re.escape(suffix) for suffix in EN_ENTITY_SUFFIXES)
        + r"))\b"
    )
    for value in english_pattern.findall(text):
        cleaned = " ".join(value.split()).strip(".,;:()[]{}\"'")
        if cleaned:
            matches.append(cleaned)
    seen: set[str] = set()
    normalized: list[str] = []
    for value in matches:
        key = value.lower()
        if key in seen:
            continue
        seen.add(key)
        normalized.append(value)
    return normalized
