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
- Follow StyleBrief section contracts. If a section is specified as a table, flow, timeline, or architecture map, implement that representation instead of flattening it into generic cards.
- Implement the StyleBrief's page canvas and section relationship strategy. Use text measures semantically; do not create unrelated one-off width rules for peer-level sections unless the brief calls for an intentional aside, appendix lane, or expanded evidence area.
- Apply text measures with semantic classes instead of global paragraph rules. For example, an article-like `.article-prose` block may have its own reading rhythm, while `.section-lead`, `.table-note`, `.matrix-intro`, `.module-summary`, and related callouts should align with the section or component group they introduce.
- Keep main section left/right edges, panel widths, and repeated component groups aligned to the selected layout system. Internal grids may vary, but the page should not look like unrelated templates stitched together.
- For opening, summary, and module-entry groups, let component scale follow information density and semantic importance. Do not use a rigid two-column wrapper when it cramps dense material beside a sparse companion.
- Reserve safe space for badges, loop labels, arrows, counters, and connector labels.
- Keep repeated component groups visually coherent through shared classes and tokens.

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
- If feedback is layout-only, such as overflow, clipped labels, table containment, width drift, duplicated visible labels, or style implementation, patch HTML/CSS layout while preserving ContentDraft wording, facts, section coverage, and table data.
- If VisualCheckReport identifies horizontal overflow, first look for fixed-width wrappers, wide tables without scroll containers, unconstrained grids, absolute badges, connector labels, or long unwrapped text. Fix the specific cause rather than simplifying the document.

## Final Self-Check

Before returning HTML, verify that:

- all required ContentDraft sections and tables are still present,
- peer-level section widths follow one intentional canvas,
- tables and grids have responsive containment,
- visible numbers, badges, and captions are not duplicated,
- short panels do not create large accidental blank areas,
- dense and sparse companion panels are not forced into an obviously mismatched width relationship,
- no scripts, event handlers, remote dependencies, local paths, prompts, or credentials were introduced.

## Output Budget

- Keep the document complete and production-readable.
- Match document length to the approved content and source-handling mode. Ordinary notes can be concise; faithful/extractive conversions and complex reports may be longer when completeness requires it.
- Avoid repeated prose and decorative CSS bulk, but do not remove source-required content or weaken layout readability for brevity.
- The final HTML should be understandable when inspected by a human maintainer.
