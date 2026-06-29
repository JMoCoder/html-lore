---
name: html_page_design
title: HTML page design
description: Use when designing readable static HTML knowledge notes, reports, explainers, plans, architecture pages, or lightweight presentation-like artifacts. Guides StyleDesigner to choose surface, layout, visual hierarchy, tokens, and responsive rules without locking the model into one theme.
version: 0.2.0
author: HTMlore
license: project-internal
metadata:
  hermes:
    tags: [html, design, style, layout, report, knowledge-note]
    related_skills: [safe_static_html, content_quality_review]
---

# HTML Page Design Skill

Design a self-contained HTML knowledge artifact that feels intentionally made for its content, not like styled Markdown.

## Role

Use this skill when planning the visual direction for a generated HTML note, report, explainer, architecture overview, comparison, plan, or lightweight presentation page.

The model should keep design autonomy. This skill gives professional habits and guardrails, not a fixed theme.

## First Decide The Surface

Before choosing style details, classify the output surface:

- `knowledge_note`: durable reading page for a knowledge base.
- `report`: structured business or technical report.
- `explainer`: beginner-friendly concept explanation.
- `architecture`: system/process explanation that benefits from diagrams or flow sections.
- `plan`: roadmap, implementation plan, checklist, or phased proposal.
- `presentation_like`: shareable deck-like or keynote-like page, but still delivered as safe static HTML unless a deck mode exists.

Let the user's target use, audience, uploaded material, and style preference decide the surface. If fields are `default`, infer from the content.

## Design Strategy

- Start from information architecture, not decoration.
- Make the first viewport immediately communicate the subject, purpose, and reading path.
- Use a small number of strong layout patterns: hero + sections, article + aside, timeline, comparison grid, process flow, metric blocks, or architecture diagram.
- For each major section, choose the representation that matches the content relationship before choosing visual style:
  - narrative explanation -> article/prose,
  - responsibilities, parameters, concepts, or comparisons -> table/comparison,
  - sequence, state, loop, or dependency -> process flow/timeline,
  - bounded system parts -> architecture map,
  - repeated independent facts -> cards.
- Match density to audience:
  - Self-use notes can be compact and scannable.
  - Shared reports need clearer hierarchy and less clutter.
  - Beginner explainers need progressive disclosure and plain section titles.
  - Executive/business reports need conclusions, risks, and next actions visible early.
- Use visual hierarchy to make the answer easier to understand: title, summary, key insight, sections, evidence, takeaways.
- Prefer semantic structure over visual tricks. The page should still read correctly if CSS is simplified.

## Layout Patterns

Choose only patterns that serve the content:

- `article`: long-form explanation with readable line length.
- `report_grid`: summary, findings, risks, recommendations.
- `process_flow`: step-by-step workflow, state machine, pipeline, or loop.
- `comparison`: before/after, options, trade-offs, pros/cons.
- `timeline`: phased plan, history, release sequence.
- `architecture_map`: components, agents, tools, edges, and control boundaries.
- `data_blocks`: metrics, counts, statuses, validation results.
- `callout_stack`: important warnings, assumptions, decisions, or open questions.

For architecture or workflow pages, include a diagram-like section when it helps. Use simple HTML/CSS boxes or inline SVG only when it improves comprehension. Do not make the page prose-heavy if the user's goal is to understand a system quickly.

## Layout Quality Contract

Every StyleBrief should give HTMLCoder a usable layout contract, not only a mood:

- Define the intended representation for each major section.
- Match container width to content amount. Short text should not sit in a wide empty card; use compact cards, split grids, callouts, or prose blocks instead.
- Keep grouped components visually consistent. When two panels explain one idea, share border, radius, padding, background behavior, and type scale unless contrast is intentional.
- Reserve collision-safe space for labels, badges, numbers, arrows, and decorative marks. They must not overlap or crowd headings.
- Keep background layers subordinate to content. Do not put transparent or glass cards over strong connector lines, patterns, or high-contrast decoration unless the card has an opaque enough surface or local mask.
- Use whitespace intentionally. Large blank areas are acceptable only when they support emphasis, not when they reveal a mismatched grid.
- Prefer fewer, better-composed components over many uniformly styled boxes.

## Visual System

- Define a small token set for color, spacing, border, shadow, and radius.
- Use tokens consistently instead of one-off styling.
- Keep color purposeful:
  - neutral text and surfaces for reading,
  - one primary accent for navigation or key states,
  - one supporting accent for warnings, risks, or secondary categories.
- Avoid one-note palettes dominated by a single hue family.
- Avoid oversized decorative backgrounds, irrelevant gradients, and stock-like atmosphere.
- Use typography to clarify hierarchy. Keep body text comfortable and headings proportionate to their containers.
- Use cards only for repeated items, grouped facts, modals, or genuinely framed tools. Do not nest cards inside cards.

## Content-Aware Design

- Preserve the user's material and the ContentDraft structure.
- Do not invent facts for visual symmetry.
- If the material is thin, design an honest lightweight page rather than a fake comprehensive report.
- If there is a reference style file, use it as design evidence: palette hints, typography hints, spacing rhythm, tone, and component shape. Do not copy proprietary branding or unrelated content.
- If the user selected a style preference, treat it as a direction:
  - `minimal`: calm, spacious, restrained.
  - `business`: structured, credible, conclusion-forward.
  - `tech`: precise, layered, diagram-friendly.
  - `retro`: nostalgic details, but still readable and professional.
  - `default`: infer style from content and audience.

## Responsiveness

- Design mobile and desktop from the start.
- Use max-width, grid fallbacks, wrapping, and stable dimensions.
- Avoid text overlap, clipped buttons, and layout shifts.
- Long labels should wrap or truncate gracefully.
- Fixed-format elements such as diagrams, counters, and grids need explicit responsive constraints.
- Diagram, card, and table sections need a mobile fallback that preserves reading order without leaving orphaned connector lines.

## What To Avoid

- Do not force every artifact into a landing-page hero.
- Do not use decorative cards for whole page sections.
- Do not use cards as the universal fallback for every relationship. Tables, prose, timelines, flows, and callouts are often clearer.
- Do not leave large empty right-hand areas in cards or split panels when the content is short.
- Do not allow badges, chips, connector lines, or decorative marks to collide with titles or body text.
- Do not place translucent content panels over visible background lines that reduce readability.
- Do not add visible instructions about how the page works unless the content itself requires it.
- Do not add complex animation as a substitute for structure.
- Do not depend on external CSS/JS frameworks.
- Do not let style erase source fidelity.

## Output For StyleDesigner

When producing a StyleBrief, make it concrete enough for HTMLCoder:

- design mode and surface choice,
- layout system,
- visual hierarchy,
- color tokens with intended usage,
- typography direction,
- component style,
- responsive rules,
- specific avoid styles,
- layout quality notes covering density, collision avoidance, grouped-component consistency, and background/content layering,
- implementation notes for diagrams, tables, timelines, or comparison blocks.
