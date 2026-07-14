---
name: tech_style_design
title: Tech style design
description: Use when the user selects a tech visual preference for an HTML architecture page, technical report, product explanation, or presentation. Helps StyleDesigner make systems, evidence, state, and constraints legible without defaulting to neon decoration or a fictional developer console.
version: 1.0.0
author: HTMlore
license: project-internal
metadata:
  hermes:
    tags: [html, style, tech, architecture, systems, evidence]
    related_skills: [html_page_design, architecture_explainer_design, presentation_surface_design, component_pattern_html]
---

# Tech Style Design Skill

## Role

Use this as a visual-direction layer when the user selects `tech`. It should clarify technical reasoning and controlled complexity on top of the selected surface skill. It does not require a dark theme, code blocks, terminal chrome, or animated effects.

## Design Read

First identify what makes the material technical:

- an architecture, process, integration, or state machine,
- parameters, models, data, or implementation constraints,
- a product capability or engineering trade-off,
- research or operational evidence, or
- a technical story intended for a non-technical audience.

Choose the visual language for comprehension. A technical business report may need a light, precise table-led treatment; an architecture explainer may need a layered map; a product page may need a capability narrative.

## Visual Direction

- Make structure visible: layers, dependencies, inputs, outputs, states, ownership, and constraints should have a clear reading order.
- Use contrast, alignment, labels, and spacing to distinguish primary flow from supporting detail.
- Reserve accent color for system state, priority, grouping, or interaction cues. Keep effects subordinate to evidence.
- Use technical texture only when it reinforces the subject: a grid, mono metadata, code treatment, or linework can support orientation, but none is required.
- Keep node surfaces and evidence panels sufficiently solid when diagrams, lines, or patterns are present behind them.
- Give dense material a broad, responsive canvas. Let tables, architecture maps, and parameter comparisons remain legible instead of compressing them into cards.
- Use diagrams for relationships and nearby prose or tables for interpretation. A diagram alone is not an explanation.

## Composition Choices

- Architecture and workflows: overview flow first, then layer map, node responsibilities, boundaries, and edge conditions as needed.
- Parameter-heavy material: structured tables or comparison matrices with consistent labels and units.
- Technical sharing: sequence concept, mechanism, trade-off, evidence, and practical implication without inventing a product narrative.
- Product capability pages: connect features to supported outcomes and boundaries; do not use fabricated code, metrics, or dashboards as decoration.
- Dark or high-contrast themes: preserve body-text contrast and use saturated color sparingly. Light themes are equally valid for technical work.

## Risks To Avoid

- Defaulting to neon, gradients, terminal framing, pseudo-code, or sci-fi motifs.
- Using connector lines that cross labels or visually compete with content.
- Making diagrams dense enough that they replace explanation with visual noise.
- Treating every technical fact as a card rather than selecting a table, flow, or prose explanation.
- Implying live system status, data, logs, or interactive controls that the static HTML cannot provide.

## StyleBrief Contract

When this skill is active, state:

- the core technical mental model,
- the hierarchy between overview, mechanism, evidence, and detail,
- which relationships need maps, flows, tables, or code-style treatment,
- the meaning of any technical visual texture or accent,
- protected zones for labels, connectors, and state markers, and
- the responsive fallback that keeps the system understandable on narrow screens.

## Review Questions

- Does the chosen visual language make the system easier to understand than prose alone?
- Are technical motifs serving evidence and orientation rather than decoration?
- Can a reader distinguish facts, constraints, model judgment, and runtime behavior where relevant?
