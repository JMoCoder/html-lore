---
name: safe_static_html
title: Safe static HTML
description: Use when implementing a complete self-contained static HTML document for HTMlore. Guides HTMLCoder to preserve approved content and style while avoiding scripts, unsafe attributes, uncontrolled remote dependencies, hidden metadata, and malformed HTML.
version: 0.2.0
author: HTMlore
license: project-internal
metadata:
  hermes:
    tags: [html, static, safety, implementation, iframe-safe]
    related_skills: [html_page_design, content_quality_review]
---

# Safe Static HTML Skill

Generate one complete, self-contained, safe static HTML document for HTMlore.

## Role

Use this skill when implementing the approved ContentDraft and StyleBrief as HTML.

HTMLCoder should focus on faithful implementation, readable structure, polished visual hierarchy, and safety. Do not redesign the content strategy unless a reviewer explicitly asked for a revision.

## Required Document Shape

- Return one full document only.
- Start with `<!doctype html>`.
- Include `<html>`, `<head>`, UTF-8 charset, viewport, `<title>`, and `<body>`.
- Put CSS in one `<style>` block.
- Use semantic structure: `header`, `main`, `section`, `article`, `aside`, `footer` where useful.
- Preserve the ContentDraft's title, summary, section order, key points, tables, quotes, and references unless a reviewer asked for changes.

## Safety Rules

Do not include:

- `<script>` tags.
- event handler attributes such as `onclick`, `onload`, `onerror`, `onmouseover`.
- `javascript:` URLs.
- `data:text/html` URLs.
- `iframe`, `embed`, `object`, `form`, `input`, or uncontrolled external dependencies.
- remote CSS or JavaScript.
- tracking pixels, analytics, beacons, or hidden network calls.
- raw prompts, API keys, local filesystem paths, provider names, hidden state, or private metadata.

If a requested visual effect would require unsafe scripting, replace it with static HTML/CSS.

## Implementation Quality

- Use CSS custom properties for the page's design tokens.
- Keep CSS scoped to the document and avoid global reset tricks that can break embedded reading.
- Make the page render well in an iframe reader and as a standalone file.
- Keep line length readable and spacing stable.
- Use responsive layout primitives: `max-width`, `grid`, `flex`, `minmax`, `clamp` for containers, not viewport-scaled font sizes.
- Use tables only for tabular data. Use lists, grids, or cards for conceptual grouping.
- For diagrams, prefer semantic HTML boxes and CSS connectors. Inline SVG is acceptable for compact diagrams, but keep it simple and accessible.
- Use icons only if they can be represented safely with text, CSS, or inline SVG. Do not fetch icon libraries.

## Visual Restraint

- Do not overuse gradients, shadows, blur, glass effects, or decorative backgrounds.
- Do not make everything a card.
- Do not nest cards inside cards.
- Do not add instructions or feature explanations that are not part of the artifact content.
- Do not include fake screenshots, fake charts, or fake metrics.
- Do not hide important content behind interaction.

## Accessibility

- Use a logical heading order.
- Keep contrast high enough for body text and UI labels.
- Add `aria-label` only when the visible text is insufficient.
- Images or diagram elements need text equivalents when they carry meaning.
- Avoid tiny text in dense panels; compact does not mean unreadable.

## Revision Behavior

If `validation_report` or `safety_report` is present and not ok:

- Treat `retry_instruction`, `issues`, `missing_parts`, `style_mismatch`, `structure_mismatch`, and blocked safety items as high priority.
- Make a concrete change. Do not return the same HTML unchanged.
- Preserve approved content while fixing the reported problem.
- If safety feedback conflicts with visual ambition, safety wins.

## Output Budget

- Keep the document complete and production-readable.
- A normal note or report should be concise. A complex architecture/report page may be longer, but avoid repeated prose and decorative CSS bulk.
- The final HTML should be understandable when inspected by a human maintainer.
