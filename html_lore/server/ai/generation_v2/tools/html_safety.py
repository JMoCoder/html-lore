from __future__ import annotations

import html
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


DANGEROUS_TAGS = {"script", "iframe", "object", "embed", "form", "input", "button", "textarea", "select", "base", "link"}
CSS_UNSAFE_PATTERNS = [
    ("css-dangerous-scheme", re.compile(r"(?:javascript|vbscript|file|data\s*:\s*text/html)\s*:", re.I)),
    ("css-expression", re.compile(r"\bexpression\s*\(", re.I)),
    ("css-import", re.compile(r"@import\b", re.I)),
]
CSS_URL_PATTERN = re.compile(r"url\(([^)]+)\)", re.I)
DANGEROUS_EXTENSIONS = {".js", ".mjs", ".cjs", ".svg", ".html", ".htm", ".xhtml", ".xml"}
SECRET_PATTERNS = [
    re.compile(r"(?<![A-Za-z0-9_-])sk-[A-Za-z0-9_-]{12,}"),
    re.compile(r"HTML_LORE_[A-Z0-9_]*=\S+"),
]


def scan_html_safety(content: str) -> dict[str, Any]:
    scanner = HtmlSafetyScanner()
    scanner.feed(content)
    reasons = list(scanner.reasons)
    if scanner.saw_script and not scanner.only_safe_toggle_script():
        reasons.append("blocked-tag:script")
    if scanner.requires_static_chart:
        reasons.append("requires-static-export:chart")
    for reason in unsafe_css_reasons("\n".join(scanner.style_parts)):
        reasons.append(reason)
    text = html.unescape(strip_tags(content))
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            reasons.append("sensitive-secret")
            break
    return {"ok": not reasons, "reasons": sorted(set(reasons))}


class HtmlSafetyScanner(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.reasons: list[str] = []
        self.saw_script = False
        self.requires_static_chart = False
        self.script_stack = 0
        self.script_parts: list[str] = []
        self.style_stack = 0
        self.style_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        name = tag.lower()
        if name == "script":
            self.saw_script = True
            self.script_stack += 1
            return
        if name == "style":
            self.style_stack += 1
            return
        if name == "canvas":
            self.requires_static_chart = True
        if name in DANGEROUS_TAGS:
            self.reasons.append(f"blocked-tag:{name}")
        if name == "meta" and is_meta_refresh(attrs):
            self.reasons.append("meta-refresh")
        for attr_name, attr_value in attrs:
            attr = attr_name.lower()
            value = (attr_value or "").strip()
            if attr.startswith("on"):
                self.reasons.append("inline-event-handler")
            if attr in {"href", "src", "action", "formaction"}:
                reason = unsafe_url_reason(value)
                if reason and reason != "external-link":
                    self.reasons.append(reason)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "script" and self.script_stack > 0:
            self.script_stack -= 1
        if tag.lower() == "style" and self.style_stack > 0:
            self.style_stack -= 1

    def handle_data(self, data: str) -> None:
        if self.script_stack > 0:
            self.script_parts.append(data)
        if self.style_stack > 0:
            self.style_parts.append(data)

    def only_safe_toggle_script(self) -> bool:
        return False


def unsafe_url_reason(value: str) -> str:
    if not value:
        return ""
    lowered = value.strip().lower()
    if lowered.startswith(("javascript:", "vbscript:", "data:text/html")):
        return "dangerous-url"
    parsed = urlsplit(value)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return "external-link"
    suffix = Path(parsed.path).suffix.lower()
    if suffix in DANGEROUS_EXTENSIONS:
        return "dangerous-download"
    return ""


def is_meta_refresh(attrs: list[tuple[str, str | None]]) -> bool:
    values = {name.lower(): (value or "").strip().lower() for name, value in attrs}
    return values.get("http-equiv") == "refresh"


def unsafe_css_reasons(value: str) -> list[str]:
    if not value:
        return []
    reasons = [reason for reason, pattern in CSS_UNSAFE_PATTERNS if pattern.search(value)]
    for raw_url in CSS_URL_PATTERN.findall(value):
        url_value = raw_url.strip().strip("'\"")
        if is_safe_css_data_image(url_value):
            continue
        parsed = urlsplit(url_value)
        if parsed.scheme or url_value.startswith(("//", "/", "\\")):
            reasons.append("css-url")
    return sorted(set(reasons))


def is_safe_css_data_image(value: str) -> bool:
    lowered = value.strip().lower()
    if not lowered.startswith("data:image/svg+xml"):
        return False
    if ";base64" in lowered:
        return False
    decoded = html.unescape(value)
    decoded = re.sub(r"%([0-9a-fA-F]{2})", lambda match: chr(int(match.group(1), 16)), decoded)
    lowered_decoded = decoded.lower()
    return not re.search(r"<\s*script\b|on[a-z]+\s*=|javascript\s*:|data\s*:\s*text/html", lowered_decoded)


def strip_tags(value: str) -> str:
    class _Stripper(HTMLParser):
        def __init__(self) -> None:
            super().__init__(convert_charrefs=True)
            self.parts: list[str] = []

        def handle_data(self, data: str) -> None:
            self.parts.append(data)

    stripper = _Stripper()
    stripper.feed(value)
    return "".join(stripper.parts)
