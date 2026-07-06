---
name: component_pattern_html
title: Component pattern HTML
description: Use when HTMLCoder needs a compact set of reusable static HTML/CSS component patterns for cards, grids, timelines, comparison blocks, process flows, callouts, and responsive tables. Helps implementation quality without external frameworks or scripts.
version: 0.1.0
author: HTMlore
license: project-internal
metadata:
  hermes:
    tags: [html, components, css, layout, implementation, responsive]
    related_skills: [safe_static_html, html_page_design]
---

# Component Pattern HTML Skill

Implement polished static HTML with a small set of reusable component patterns.

## Role

Use this skill in HTMLCoder when the PlanDraft or StyleBrief calls for component-heavy layouts such as grids, timelines, process flows, architecture maps, comparison blocks, callouts, tables, or presentation cards.

This skill is project-internal original guidance. It does not copy external project prompts, templates, or code.

This skill is an implementation aid, not a page-planning authority. It should help HTMLCoder execute the approved PlanDraft and StyleBrief; it must not replace the agent's judgment with a fixed component recipe.

## Component Principles

- Define CSS custom properties once, then reuse them.
- Prefer a few strong component patterns over many one-off styles.
- Keep HTML semantic before styling it.
- Components must work without JavaScript.
- Components must stack cleanly on mobile.
- Do not use external CSS frameworks, icon libraries, web fonts, or remote assets.
- Components in the same conceptual group must look related: consistent padding, border, radius, type scale, and background opacity.
- Peer-level component groups should share the same outer canvas unless the StyleBrief explicitly creates a narrow lane, aside, or full-bleed variant.
- Component size should follow content density. Do not stretch a short label or one-sentence fact into a wide empty card.
- Visual decoration must never compete with content. Connectors, badges, counters, and background lines need reserved space or reduced contrast.
- The component pattern must follow the relationship in the content: matrix -> table, sequence -> flow/timeline, bounded system -> architecture map, repeated independent facts -> cards.

## Recommended Patterns

- `metric-card`: title, short value or theme label, explanation, optional note. Do not invent numeric values.
- `info-card`: heading, body, bullets, and source-aware caveat.
- `timeline`: ordered phases with labels and plain-text outcomes.
- `process-flow`: steps connected by arrows or borders; stack vertically on mobile.
- `comparison-grid`: options, before/after, pros/cons, or trade-off columns.
- `callout`: decision, risk, assumption, warning, or takeaway.
- `responsive-table`: real tabular data with horizontal overflow fallback.
- `architecture-node`: component name, role, inputs, outputs, and owner.
- `boundary-table`: controlled-by / parameter / source / notes matrix for runtime, model, user, and tool responsibilities.
- `compact-fact-row`: short facts or tags laid out as inline chips or narrow cards when a full card grid would create empty space.
- `fit-matrix`: requirement / option / evidence / fit / gap table for suitability or adaptation analysis.
- `risk-register`: risk / evidence / impact / follow-up action table or compact list for decision review.
- `source-scope-table`: source file / what it provides / what it does not provide / how it is used.
- `price-parameter-table`: model / parameter / price / caveat table for product, equipment, financial, or specification comparisons.

## Pattern Selection Rules

- Use `responsive-table` for matrices, responsibilities, parameter boundaries, node/edge conditions, and concept comparisons.
- Use `price-parameter-table` or `responsive-table` when the source contains prices, product models, equipment quantities, capacities, ranges, operating assumptions, or other structured numbers. Do not hide these relationships inside prose.
- For report conversions with many source tables, prefer consistent table canvas behavior. Do not place tables in a narrow grid if their own minimum readable width will force avoidable horizontal scrolling.
- Use `fit-matrix` when the page evaluates whether one option, product, architecture, or plan fits another requirement. Keep matched evidence, gaps, and unknowns separate.
- Use `risk-register` when risks have causes, impacts, mitigations, or follow-up checks. A plain bullet list is acceptable for a lightweight memo, but complex decision reports usually need a more structured risk component.
- Use `source-scope-table` when more than one source file contributes different kinds of evidence or when some data is missing.
- Use `process-flow` or `timeline` for ordered stages, loops, dependencies, and state transitions.
- Use `architecture-node` inside an architecture map when components have inputs, outputs, and owners.
- Use `info-card` only for repeated independent items. Avoid using a card grid to represent a sequence or a matrix.
- Use `callout` for one important message beside a longer explanation; match its visual language to the companion panel.
- Use `compact-fact-row` for short labels, statuses, options, or one-line facts. Do not stretch these into wide cards.
- Use `boundary-table` when the page must clarify what code, model, user, or tools control.
- Use cards for conclusions, highlights, or independent findings, but do not use cards as the primary vehicle for dense comparison, pricing, parameter, or risk evidence.

## CSS Implementation Rules

- Use `box-sizing: border-box`.
- Use `max-width`, `grid`, `flex`, `minmax`, `gap`, and natural wrapping.
- Define page, section, panel, and grid wrappers deliberately. Avoid one-off wrapper widths that make adjacent report sections appear unrelated.
- Avoid viewport-scaled font sizes.
- Avoid fixed heights for content cards.
- Keep border radius and shadow consistent.
- Use `overflow-wrap: anywhere` for long labels only where needed.
- Tables need `overflow-x: auto` wrappers or mobile card alternatives.
- Table overflow should be intentional. A wide annual/detail table may scroll; a short parameter table should not scroll merely because it was squeezed into an ornamental grid.
- Prefer `align-items: stretch` only when card content lengths are similar; otherwise use natural height or compact max-width.
- Use opaque or nearly opaque surfaces for cards placed over diagrams, connector lines, or textured backgrounds.
- Place badges and section labels in normal document flow where possible. If absolutely positioned, reserve padding so they cannot overlap headings.
- Connector lines should sit behind nodes and stop before content surfaces. They should not cross readable text.
- For side-by-side panels, define shared class names and tokens so left and right panels look intentionally related.
- If a panel sits over a diagram or patterned background, make it opaque enough to hide the layer below. Avoid glass panels over connector lines.
- Use `grid-template-columns: repeat(auto-fit, minmax(...))` for repeated cards, but cap max widths or use natural-height rows when content is short.

## Output Expectations

HTMLCoder should use this skill to make the final HTML more coherent, not more complex.

Before returning final HTML, verify:

- repeated components share class names and tokens,
- mobile layout is readable,
- no text overlaps,
- no avoidable empty columns or stretched short-content cards,
- no translucent panel exposes distracting background lines behind text,
- related left/right or paired panels use a coherent visual system,
- main section widths and edge alignment match the selected layout system unless a deliberate variant is named in the StyleBrief,
- tables, flows, and cards are used for the correct content relationships,
- structured facts from the ContentDraft or PlanDraft remain structured in the HTML instead of being flattened into generic paragraphs,
- comparison, fit, price, parameter, and risk relationships are implemented with a component that preserves their dimensions,
- labels, loop badges, and counters have protected space and do not collide with headings,
- no scripts or unsafe attributes were introduced,
- visual patterns match StyleBrief rather than overriding it.
