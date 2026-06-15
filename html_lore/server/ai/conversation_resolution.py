from __future__ import annotations

import re
from typing import Any


def recent_conversation_messages(messages: Any, *, limit: int = 6) -> list[dict[str, str]]:
    if not isinstance(messages, list):
        return []
    normalized: list[dict[str, str]] = []
    for message in messages:
        if not isinstance(message, dict):
            continue
        role = str(message.get("role") or "").strip().lower()
        content = str(message.get("content") or "").strip()
        if role not in {"user", "assistant"} or not content:
            continue
        normalized.append({"role": role, "content": content[:900]})
    return normalized[-max(1, int(limit or 6)) :]


def resolve_conversation_turn(content: str, recent_messages: list[dict[str, str]]) -> dict[str, Any]:
    question = str(content or "").strip()
    if not question:
        return {
            "original_query": "",
            "resolved_query": "",
            "resolved_focus": "",
            "focus_type": "none",
            "is_followup": False,
            "topic_shift": False,
            "confidence": 0.0,
            "reason": "empty_query",
        }
    if not recent_messages:
        return {
            "original_query": question,
            "resolved_query": question,
            "resolved_focus": "",
            "focus_type": "none",
            "is_followup": False,
            "topic_shift": False,
            "confidence": 0.45,
            "reason": "no_recent_messages",
        }

    aliased_focus = resolve_recent_alias_focus(question, recent_messages)
    is_followup = is_followup_question(question) or aliased_focus is not None
    if not is_followup:
        return {
            "original_query": question,
            "resolved_query": question,
            "resolved_focus": "",
            "focus_type": "none",
            "is_followup": False,
            "topic_shift": True,
            "confidence": 0.7,
            "reason": "explicit_new_turn",
        }

    if aliased_focus is not None:
        return {
            "original_query": question,
            "resolved_query": f"{aliased_focus['text']} {question}".strip(),
            "resolved_focus": aliased_focus["text"],
            "focus_type": aliased_focus["type"],
            "is_followup": True,
            "topic_shift": False,
            "confidence": aliased_focus["confidence"],
            "reason": f"followup_alias_{aliased_focus['type']}",
        }

    focus = resolve_recent_conversation_focus(recent_messages)
    if focus:
        return {
            "original_query": question,
            "resolved_query": f"{focus['text']} {question}".strip(),
            "resolved_focus": focus["text"],
            "focus_type": focus["type"],
            "is_followup": True,
            "topic_shift": False,
            "confidence": focus["confidence"],
            "reason": f"followup_{focus['type']}",
        }

    user_history = [message["content"] for message in recent_messages if message.get("role") == "user"]
    if not user_history:
        return {
            "original_query": question,
            "resolved_query": question,
            "resolved_focus": "",
            "focus_type": "none",
            "is_followup": True,
            "topic_shift": False,
            "confidence": 0.4,
            "reason": "followup_without_user_history",
        }
    history = " ".join(user_history[-3:])[:1600].strip()
    resolved = f"{history} {question}".strip()
    return {
        "original_query": question,
        "resolved_query": resolved,
        "resolved_focus": history,
        "focus_type": "history",
        "is_followup": True,
        "topic_shift": False,
        "confidence": 0.45,
        "reason": "followup_history_fallback",
    }


def build_retrieval_query(content: str, recent_messages: list[dict[str, str]]) -> str:
    return str(resolve_conversation_turn(content, recent_messages).get("resolved_query") or str(content or "").strip())


def resolve_recent_conversation_focus(recent_messages: list[dict[str, str]]) -> dict[str, Any] | None:
    user_messages = [
        str(message.get("content") or "").strip()
        for message in recent_messages
        if str(message.get("role") or "").strip().lower() == "user" and str(message.get("content") or "").strip()
    ]
    if not user_messages:
        return None

    for message in reversed(user_messages):
        explicit = extract_explicit_focus(message)
        if explicit:
            return explicit

    for message in reversed(user_messages):
        if is_generic_followup_prompt(message):
            continue
        return {"text": message[:400], "type": "topic", "confidence": 0.5}
    return None


def resolve_recent_alias_focus(question: str, recent_messages: list[dict[str, str]]) -> dict[str, Any] | None:
    question_text = " ".join(str(question or "").split())
    if not question_text:
        return None
    focus = resolve_recent_conversation_focus(recent_messages)
    if focus is None:
        return None
    aliases = focus_aliases(focus["text"])
    if not aliases:
        return None
    normalized_question = question_text.lower()
    for alias in aliases:
        alias_normalized = alias.lower()
        if len(alias_normalized) < 2:
            continue
        if alias_normalized in normalized_question and alias_normalized != normalized_question:
            return dict(focus)
    return None


def extract_explicit_focus(content: str) -> dict[str, Any] | None:
    text = " ".join(str(content or "").split())
    if not text:
        return None
    from .search_planner import extract_entity_terms

    entity_terms = extract_entity_terms(text)
    if entity_terms:
        joined = " ".join(entity_terms[:2]).strip()
        if joined:
            return {"text": joined, "type": "entity", "confidence": 0.92}

    for phrase in extract_quoted_phrases(text):
        return {"text": phrase, "type": "quoted_topic", "confidence": 0.88}

    for phrase in extract_named_phrases(text):
        return {"text": phrase, "type": "named_topic", "confidence": 0.8}

    for phrase in extract_question_focus_phrases(text):
        return {"text": phrase, "type": "topic", "confidence": 0.72}
    return None


def focus_aliases(text: str) -> list[str]:
    cleaned = clean_focus_text(text)
    if not cleaned:
        return []
    aliases = [cleaned]
    try:
        from .search_planner import EN_ENTITY_SUFFIXES, ZH_ENTITY_SUFFIXES, extract_entity_terms
    except Exception:
        EN_ENTITY_SUFFIXES = ()
        ZH_ENTITY_SUFFIXES = ()
        extract_entity_terms = None

    entity_terms = extract_entity_terms(cleaned) if extract_entity_terms else []
    for entity in entity_terms or [cleaned]:
        value = clean_focus_text(entity)
        if not value:
            continue
        aliases.append(value)
        tokens = [token for token in value.split() if token]
        if len(tokens) >= 2:
            aliases.append(tokens[0])
            aliases.append(" ".join(tokens[:2]))
        for suffix in ZH_ENTITY_SUFFIXES:
            if value.endswith(suffix) and len(value) > len(suffix) + 1:
                aliases.append(value[: -len(suffix)])
        lowered = value.lower()
        for suffix in EN_ENTITY_SUFFIXES:
            suffix_text = f" {suffix}"
            if lowered.endswith(suffix_text) and len(value) > len(suffix_text) + 1:
                aliases.append(value[: -len(suffix_text)])
    return dedupe_focus_values([alias for alias in aliases if alias])


def extract_quoted_phrases(text: str) -> list[str]:
    matches = re.findall(r"[\"“”'‘’《》〈〉「」『』]([^\"“”'‘’《》〈〉「」『』]{2,80})[\"“”'‘’《》〈〉「」『』]", text)
    return [clean_focus_text(match) for match in matches if clean_focus_text(match)]


def extract_named_phrases(text: str) -> list[str]:
    matches: list[str] = []
    patterns = [
        r"\b([A-Z]{2,12})\b",
        r"\b([A-Z][A-Za-z0-9&+._/-]*(?:\s+[A-Z][A-Za-z0-9&+._/-]*){0,4})\b",
        r"\b([A-Za-z0-9][A-Za-z0-9+._/-]{2,40})\b",
    ]
    for pattern in patterns:
        for match in re.findall(pattern, text):
            cleaned = clean_focus_text(match)
            if cleaned and not looks_like_noise_token(cleaned):
                matches.append(cleaned)
    return dedupe_focus_values(matches)


def extract_question_focus_phrases(text: str) -> list[str]:
    patterns = [
        r"(?:什么是|解释一下|介绍一下|讲一下|说一下|分析一下|总结一下|详细介绍|详细分析|关于)([^。！？!?]{2,48})",
        r"([^。！？!?]{2,48})(?:是什么|是什么意思|的概念|的背景|的逻辑|的作用|的区别|的结构)",
        r"(?:how does|what is|tell me about|explain|summarize)\s+(.{2,48})",
    ]
    matches: list[str] = []
    for pattern in patterns:
        for match in re.findall(pattern, text, flags=re.IGNORECASE):
            cleaned = clean_focus_text(match)
            if cleaned and not is_generic_followup_prompt(cleaned):
                matches.append(cleaned)
    return dedupe_focus_values(matches)


def dedupe_focus_values(values: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        key = value.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(value)
    return result


def clean_focus_text(value: str) -> str:
    cleaned = " ".join(str(value or "").split()).strip(".,;:!?，。；：！？()（）[]【】<>《》\"'“”‘’")
    return cleaned[:120]


def looks_like_noise_token(value: str) -> bool:
    lowered = str(value or "").strip().lower()
    if not lowered:
        return True
    if lowered in {"the", "this", "that", "what", "how", "and", "for"}:
        return True
    return len(lowered) <= 1


def is_followup_question(content: str) -> bool:
    normalized = str(content or "").strip().lower()
    if not normalized:
        return False
    if len(normalized) > 120:
        return False
    if looks_like_under_specified_question(normalized):
        return True
    followup_markers = [
        "continue",
        "tell me more",
        "what about",
        "how about",
        "that",
        "this",
        "it",
        "they",
        "them",
        "those",
        "继续",
        "展开",
        "详细",
        "再说",
        "这个",
        "这些",
        "它",
        "他的",
        "她的",
        "它的",
        "该",
        "其",
        "他们",
        "上述",
        "前面",
        "刚才",
        "还有",
        "搜索",
        "联网",
        "查一下",
        "网上查",
        "官网查",
        "呢",
        "続け",
        "詳しく",
        "それ",
        "これ",
        "検索",
        "調べ",
    ]
    return any(marker in normalized for marker in followup_markers)


def looks_like_under_specified_question(normalized: str) -> bool:
    question_markers = ("?", "？", "吗", "呢", "么", "什么", "为何", "为什么", "怎么", "怎样", "多少", "谁", "哪里", "哪家")
    pronoun_markers = ("它", "他的", "她的", "它的", "这个", "这些", "该", "其", "they", "them", "that", "this", "it")
    if not any(marker in normalized for marker in question_markers):
        return False
    return any(marker in normalized for marker in pronoun_markers)


def is_generic_followup_prompt(content: str) -> bool:
    normalized = " ".join(str(content or "").strip().lower().split())
    if not normalized:
        return True
    generic_markers = {
        "继续",
        "展开",
        "详细",
        "再说",
        "联网",
        "联网搜索",
        "查一下",
        "网上查",
        "官网查",
        "继续说",
        "详细说说",
        "展开说说",
        "continue",
        "tell me more",
        "search",
        "search online",
        "web search",
    }
    return normalized in generic_markers


__all__ = [
    "build_retrieval_query",
    "extract_explicit_focus",
    "is_followup_question",
    "recent_conversation_messages",
    "resolve_conversation_turn",
]
