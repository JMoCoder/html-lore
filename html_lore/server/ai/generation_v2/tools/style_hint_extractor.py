from __future__ import annotations

import re

from ..schemas import ParsedDocument, StyleHint


HEX_COLOR_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b")
FONT_RE = re.compile(r"font-family\s*:\s*([^;}{]+)", re.IGNORECASE)


def extract_style_hints(parsed: ParsedDocument, *, role: str = "material") -> list[StyleHint]:
    text = parsed.plain_text or ""
    hints: list[StyleHint] = list(parsed.style_hints)
    hints.extend(color_hints(text, role=role))
    hints.extend(font_hints(text, role=role))
    hints.extend(layout_hints(text, role=role))
    hints.extend(image_metadata_hints(text, role=role))
    return dedupe_hints(hints)


def color_hints(text: str, *, role: str) -> list[StyleHint]:
    result: list[StyleHint] = []
    for value in HEX_COLOR_RE.findall(text)[:12]:
        result.append(StyleHint(kind=f"{role}:color", value=value.lower(), confidence=0.75))
    lower = text.lower()
    for name in ("dark", "blue", "green", "red", "gold", "black", "white"):
        if name in lower:
            result.append(StyleHint(kind=f"{role}:color_keyword", value=name, confidence=0.35))
    return result


def font_hints(text: str, *, role: str) -> list[StyleHint]:
    result: list[StyleHint] = []
    for match in FONT_RE.finditer(text):
        value = " ".join(match.group(1).strip().strip("\"'").split())
        if value:
            result.append(StyleHint(kind=f"{role}:font", value=value[:120], confidence=0.65))
    return result[:8]


def layout_hints(text: str, *, role: str) -> list[StyleHint]:
    lower = text.lower()
    hints: list[StyleHint] = []
    for keyword, value in (
        ("grid", "grid"),
        ("flex", "flex"),
        ("card", "card"),
        ("dashboard", "dashboard"),
        ("table", "table"),
        ("hero", "hero"),
        ("sidebar", "sidebar"),
        ("two-column", "two_column"),
        ("columns", "columns"),
    ):
        if keyword in lower:
            hints.append(StyleHint(kind=f"{role}:layout", value=value, confidence=0.45))
    return hints[:10]


def image_metadata_hints(text: str, *, role: str) -> list[StyleHint]:
    hints: list[StyleHint] = []
    match = re.search(r"ImageSize\s*:\s*([0-9]+x[0-9]+)", text, flags=re.IGNORECASE)
    if match:
        hints.append(StyleHint(kind=f"{role}:image_size", value=match.group(1), confidence=0.6))
    return hints


def dedupe_hints(hints: list[StyleHint]) -> list[StyleHint]:
    seen: set[tuple[str, str]] = set()
    result: list[StyleHint] = []
    for hint in hints:
        key = (hint.kind, hint.value)
        if key in seen:
            continue
        seen.add(key)
        result.append(hint)
    return result
