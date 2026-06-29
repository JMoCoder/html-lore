---
name: presentation_surface_design
title: Presentation surface design
description: Use when the generated HTML should feel like a pitch deck, executive briefing, launch page, showcase, or presentation-like artifact while remaining safe static HTML. Helps StyleDesigner choose strong first-viewport framing, slide-like sections, value cards, and talk-track hierarchy.
version: 0.1.0
author: HTMlore
license: project-internal
metadata:
  hermes:
    tags: [html, design, presentation, pitch, briefing, showcase]
    related_skills: [html_page_design, safe_static_html]
---

# Presentation Surface Design Skill

Design a static HTML artifact that reads like a focused presentation or executive briefing, not a generic article.

## Role

Use this skill in StyleDesigner when the Planner asks for `presentation`, `pitch`, `deck`, `roadshow`, `executive briefing`, `showcase`, `launch`, or similar presentation-oriented output.

This skill is project-internal original guidance. It may be informed by common presentation and HTML design practices, but it does not copy external project prompts, templates, or code.

## Surface Strategy

- Treat each major section as a slide-like scene with one clear message.
- Make the first viewport identify the subject, audience, and value proposition quickly.
- Prefer short section titles, concise claims, and visually grouped supporting points.
- Use layout to create a talk track: problem, opportunity, solution, capability, roadmap, proof, next action.
- Avoid turning every paragraph into a card. Use cards for repeated proof points, metrics, capabilities, roadmap steps, or stakeholder views.

## Visual Patterns

Choose patterns that support presentation use:

- `hero_brief`: headline, subheadline, audience cue, and 3-4 value chips.
- `value_grid`: business outcomes or benefits in repeated cards.
- `capability_map`: modules or services arranged by layer, domain, or workflow.
- `roadmap`: phased rollout without inventing dates or metrics.
- `comparison_panel`: before/after, current/future, or option trade-offs.
- `talk_track_band`: full-width section with a single takeaway and supporting bullets.
- `executive_summary`: compact conclusion and decision points near the top.

## Slide-Like Layout Guardrails

- A presentation-like section still needs a strong content grid. Do not rely on large empty areas to create drama.
- Pair short claims with compact supporting blocks, not oversized cards that leave half the component blank.
- When placing a badge or label near a headline, keep it above or beside the title in normal flow unless there is clear reserved space.
- If a section uses connector lines, loops, or diagram backgrounds, keep text panels opaque enough to hide visual noise.
- Keep companion panels visually aligned. A summary panel and a key insight panel should share the same design language unless the contrast is the message.

## Style Rules

- Use stronger contrast and rhythm than a normal knowledge note, but keep it readable.
- Keep decorative effects subordinate to the message.
- Do not invent KPI numbers, customer logos, dates, budgets, or market claims for visual impact.
- When user selected a style preference, express it through hierarchy, spacing, palette, and component shape, not through unsupported content.
- For dark or technology-oriented presentation pages, keep body text contrast high and avoid dense neon effects.
- For light business or technical pages, avoid pale translucent cards over colored lines; it often looks accidental and reduces readability.

## Output Expectations

StyleBrief should include:

- the presentation surface type,
- recommended section rhythm,
- component patterns for value, capability, roadmap, and summary blocks,
- responsive behavior for slide-like sections,
- layout guardrails for density, badge placement, panel pairing, and background layering,
- avoid styles that would make the artifact look like a fake marketing page.
