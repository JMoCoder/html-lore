from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter
from typing import Any

from ..schemas import ValidationIssue, VisualCheckReport, VisualViewportReport


DEFAULT_VIEWPORTS = (
    ("desktop", 1366, 900),
    ("mobile", 390, 844),
)


def run_visual_check(
    html: str,
    *,
    mode: str = "off",
    browser_channel: str = "chrome",
    timeout_seconds: int = 20,
) -> VisualCheckReport:
    normalized_mode = str(mode or "off").strip().lower()
    if normalized_mode not in {"basic", "strict"}:
        return VisualCheckReport(mode="off", available=False, ok=True, skipped=True, reason="Visual check is disabled.")
    if not str(html or "").strip():
        return VisualCheckReport(
            mode=normalized_mode,
            available=True,
            ok=False,
            skipped=False,
            reason="HTML is empty.",
            issues=[ValidationIssue(code="empty_html", message="HTML is empty; browser rendering was not attempted.", severity="error")],
        )
    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import sync_playwright
    except Exception:
        return VisualCheckReport(
            mode=normalized_mode,
            available=False,
            ok=True,
            skipped=True,
            reason="Python Playwright is not installed.",
            warnings=["Install optional Python Playwright support and a system Chrome/Chromium browser to enable visual checks."],
        )

    started = perf_counter()
    checked_at = datetime.now(timezone.utc).isoformat()
    issues: list[ValidationIssue] = []
    warnings: list[str] = []
    reports: list[VisualViewportReport] = []
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(channel=str(browser_channel or "chrome"), headless=True)
            try:
                for name, width, height in DEFAULT_VIEWPORTS:
                    page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
                    page.set_content(str(html), wait_until="load", timeout=max(1, int(timeout_seconds or 20)) * 1000)
                    page.wait_for_timeout(100)
                    report_data = page.evaluate(
                        """() => {
                          const doc = document.documentElement;
                          const body = document.body;
                          const visibleText = (body && body.innerText || '').trim();
                          const elements = Array.from(document.body ? document.body.querySelectorAll('body *') : []);
                          const viewportWidth = window.innerWidth;
                          const viewportHeight = window.innerHeight;
                          const elementIssues = [];
                          let visibleArea = 0;
                          let checked = 0;
                          for (const el of elements) {
                            const style = window.getComputedStyle(el);
                            if (style.display === 'none' || style.visibility === 'hidden' || Number(style.opacity || 1) === 0) continue;
                            const rect = el.getBoundingClientRect();
                            if (rect.width <= 1 || rect.height <= 1) continue;
                            checked += 1;
                            if (rect.right > viewportWidth + 2 || rect.left < -2) {
                              elementIssues.push({ code: 'element_horizontal_overflow', tag: el.tagName.toLowerCase(), text: (el.innerText || '').trim().slice(0, 80) });
                            }
                            if (rect.width > viewportWidth * 1.08) {
                              elementIssues.push({ code: 'oversized_element', tag: el.tagName.toLowerCase(), text: (el.innerText || '').trim().slice(0, 80) });
                            }
                            const clipped = (el.scrollWidth - el.clientWidth > 2 || el.scrollHeight - el.clientHeight > 2) && style.overflow === 'hidden';
                            if (clipped) {
                              elementIssues.push({ code: 'clipped_content', tag: el.tagName.toLowerCase(), text: (el.innerText || '').trim().slice(0, 80) });
                            }
                            const clippedWidth = Math.max(0, Math.min(rect.right, viewportWidth) - Math.max(rect.left, 0));
                            const clippedHeight = Math.max(0, Math.min(rect.bottom, viewportHeight) - Math.max(rect.top, 0));
                            visibleArea += Math.min(clippedWidth * clippedHeight, viewportWidth * viewportHeight);
                            if (elementIssues.length >= 24) break;
                          }
                          const blankRatio = visibleText ? Math.max(0, Math.min(1, 1 - (Math.min(visibleArea, viewportWidth * viewportHeight) / (viewportWidth * viewportHeight)))) : 1;
                          return {
                            rendered: Boolean(body),
                            bodyTextLength: visibleText.length,
                            documentWidth: Math.max(doc ? doc.scrollWidth : 0, body ? body.scrollWidth : 0),
                            documentHeight: Math.max(doc ? doc.scrollHeight : 0, body ? body.scrollHeight : 0),
                            horizontalOverflowPx: Math.max(0, Math.max(doc ? doc.scrollWidth : 0, body ? body.scrollWidth : 0) - viewportWidth),
                            blankRatio,
                            checked,
                            elementIssues,
                          };
                        }"""
                    )
                    viewport_issues = visual_issues_for_viewport(name, width, height, report_data)
                    issues.extend(viewport_issues)
                    reports.append(
                        VisualViewportReport(
                            name=name,
                            width=width,
                            height=height,
                            rendered=bool(report_data.get("rendered")),
                            body_text_length=int(report_data.get("bodyTextLength") or 0),
                            document_width=int(report_data.get("documentWidth") or 0),
                            document_height=int(report_data.get("documentHeight") or 0),
                            horizontal_overflow_px=int(report_data.get("horizontalOverflowPx") or 0),
                            blank_ratio=round(float(report_data.get("blankRatio") or 0), 3),
                            issue_count=len(viewport_issues),
                        )
                    )
                    page.close()
            finally:
                browser.close()
    except PlaywrightError as exc:
        return VisualCheckReport(
            mode=normalized_mode,
            available=False,
            ok=True,
            skipped=True,
            checked_at=checked_at,
            duration_ms=int((perf_counter() - started) * 1000),
            reason=f"Browser visual check could not run: {safe_message(str(exc))}",
            warnings=["Visual check was skipped; generation can continue without browser validation."],
        )

    return VisualCheckReport(
        mode=normalized_mode,
        available=True,
        ok=not any(issue.severity == "error" for issue in issues),
        skipped=False,
        checked_at=checked_at,
        duration_ms=int((perf_counter() - started) * 1000),
        viewports=reports,
        issues=issues[:40],
        warnings=warnings,
    )


def visual_issues_for_viewport(name: str, width: int, height: int, data: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not data.get("rendered"):
        issues.append(ValidationIssue(code="not_rendered", message=f"{name} viewport did not render a document body.", severity="error"))
    if int(data.get("bodyTextLength") or 0) < 20:
        issues.append(ValidationIssue(code="too_little_visible_text", message=f"{name} viewport has very little visible text after rendering.", severity="warning"))
    overflow = int(data.get("horizontalOverflowPx") or 0)
    if overflow > 8:
        severity = "error" if overflow > max(24, int(width * 0.08)) else "warning"
        issues.append(ValidationIssue(code="horizontal_overflow", message=f"{name} viewport overflows horizontally by {overflow}px.", severity=severity))
    blank_ratio = float(data.get("blankRatio") or 0)
    if blank_ratio > 0.92:
        issues.append(ValidationIssue(code="mostly_blank_first_viewport", message=f"{name} first viewport appears mostly blank.", severity="warning"))
    for item in data.get("elementIssues") if isinstance(data.get("elementIssues"), list) else []:
        if not isinstance(item, dict):
            continue
        code = str(item.get("code") or "layout_issue")
        tag = str(item.get("tag") or "element")
        text = str(item.get("text") or "").strip()
        suffix = f": {text}" if text else ""
        issues.append(ValidationIssue(code=code, message=f"{name} {tag} has {code.replace('_', ' ')}{suffix}", severity="warning"))
    return issues


def safe_message(value: str, limit: int = 240) -> str:
    return " ".join(str(value or "").split())[:limit]
