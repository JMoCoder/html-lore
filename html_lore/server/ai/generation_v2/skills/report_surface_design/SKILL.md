---
name: report_surface_design
title: Report surface design
description: Use when the generated HTML is explicitly requested as a report or should present already-planned report content with credible hierarchy, scannable findings, matrices, risks, recommendations, and decision-oriented reading flow. Helps StyleDesigner design report-like HTML without imposing a fixed report template.
version: 0.1.0
author: HTMlore
license: project-internal
metadata:
  hermes:
    tags: [html, report, business-report, analysis, decision, surface-design]
    related_skills: [html_page_design, safe_static_html, content_quality_review, component_pattern_html]
---

# Report Surface Design Skill

Design report-like HTML surfaces for content that has already been interpreted and planned by upstream agents.

## Role

Use this skill in StyleDesigner when `target_use` is `report` or when Planner has explicitly requested a report-oriented presentation.

This skill is a surface-design enhancer. It should not decide the report's business logic, required chapters, conclusions, or evidence. RequirementAnalyst, Planner, and ContentWriter decide what the report should say. StyleDesigner decides how that content should read as a credible HTML report.

## Boundary

Do not force a universal report template.

Avoid instructions such as:

- every report must have executive summary / background / findings / risks / recommendations,
- every report must be corporate blue and gray,
- every report must include a table, metric block, roadmap, or chart,
- every report must be conclusion-first when the source material does not support a conclusion.

Instead, preserve the upstream content structure and improve its report surface.

## Report Surface Principles

- Make the subject, purpose, and reading path obvious in the first viewport.
- If the upstream content includes a summary, conclusion, judgment, recommendation, or decision point, make it easy to find early.
- Keep facts, assumptions, risks, recommendations, and open questions visually distinct when those categories exist.
- Use a report density that supports scanning without turning the page into a dashboard.
- Prefer a calm, credible visual system over decorative spectacle.
- Do not invent metrics, dates, budgets, owners, market claims, citations, or confidence levels for visual balance.
- When evidence is thin, use honest lightweight framing instead of fake completeness.
- Match report depth to source complexity and user intent. A short memo can stay short; a multi-source comparison, adaptation analysis, pricing review, technical parameter review, or risk assessment should not be collapsed into a thin summary.
- Preserve the analytical chain when the user asks for comparison, suitability, fit, risk, price, parameters, trade-offs, or recommendations: source fact -> comparison dimension -> interpretation -> risk or next check.
- Separate source facts from model judgment. If the report includes an adaptation view or recommendation, make clear which parts are directly sourced and which parts are cautious analysis.
- When multiple source files or options are involved, make the relationship between sources visible instead of blending them into generic prose.

## Representation Rules

Choose the visual representation from the content relationship:

- comparisons, responsibilities, parameters, options, criteria, or evidence categories -> matrix or table,
- phased work, maturity path, rollout, history, or sequence -> timeline or roadmap,
- risks, constraints, dependencies, or assumptions -> risk list, priority matrix, or callout stack,
- key findings or independent observations -> compact finding cards,
- recommendations or next actions -> prioritized action list,
- narrative analysis -> readable article section with pull quote or side note only when useful,
- source limitations or unknowns -> explicit caveat band or appendix note.

Cards are useful for repeated findings, but they are not a replacement for tables, matrices, timelines, or analysis prose.

For analytical reports, choose the representation by decision need:

- source scope or evidence coverage -> source table or scope band,
- equipment lists, product parameters, prices, quantities, dates, owners, or model variants -> structured table,
- two-source or multi-option comparison -> side-by-side matrix with matching dimensions,
- suitability or fit analysis -> fit matrix that separates matched points, gaps, risks, and evidence source,
- risk discussion -> risk register, caution stack, or verification checklist with explicit follow-up actions,
- management recommendation -> concise decision summary backed by the preceding evidence, not a decorative slogan.

## Visual Direction

- Use a stable layout grid with restrained spacing, readable line length, and clear section dividers.
- Choose one primary report canvas for peer-level sections and keep their left/right edges visually consistent.
- Treat narrow reading lanes, sidebars, appendix notes, or full-bleed bands as intentional variants. If a report section changes width, the StyleBrief should state why and how it relates to the main canvas.
- Tables, matrices, comparison panels, and multi-card finding groups usually belong on the primary report canvas. Avoid mixing a narrow prose measure with full-width report panels at the same hierarchy unless it is an intentional editorial rhythm.
- Give summary or conclusion areas stronger hierarchy, but avoid oversized marketing hero treatment unless the report is meant for external presentation.
- Tables and matrices should be legible on desktop and usable on mobile through horizontal scroll or stacked rows.
- Use visual tokens consistently: surface, border, muted text, primary accent, risk/warning accent, and optional success/next-step accent.
- Keep color functional. Use accent color for hierarchy and status, not decoration.
- Make risk or warning treatments visible but not alarmist.
- Keep charts or diagram-like blocks honest; do not fake data visualization when the source has no data.
- Ensure paired report panels use the same component language unless contrast carries meaning.

## StyleBrief Expectations

When this skill is loaded, StyleDesigner should include:

- report surface type and intended reading mode,
- primary canvas behavior for main report sections, including whether sections are panel-first, article-flow, dashboard-like, or mixed intentionally,
- rules for when a section may use a narrow reading measure, an aside, or a full-width panel, and how those variants should align with the main canvas,
- which upstream sections need summary, finding, matrix, risk, recommendation, roadmap, or appendix treatment,
- table/matrix guidance when the plan contains comparisons, responsibilities, options, parameters, or evidence categories,
- analysis-depth guidance when source material is complex: whether the report should read as a short memo, standard report, deep comparison, technical review, or decision brief, and how much detail should be preserved,
- explicit source-vs-judgment guidance when the page contains suitability, risk, or recommendation language,
- density rules for findings, callouts, and long analysis sections,
- mobile handling for tables, matrices, and multi-column report areas,
- visual risk notes for empty cards, over-wide short content, weak contrast, and decorative elements that reduce credibility,
- explicit reminder that missing data must remain missing, not invented for visual polish.

## Review Checklist

- Does the page look like a readable report rather than styled Markdown or a generic landing page?
- Are the upstream conclusions, findings, risks, recommendations, or open questions easy to scan when present?
- Are tables, matrices, timelines, cards, and prose used for the right content relationships?
- If the source material is complex or multi-source, does the surface preserve enough detail to support decision reading rather than reducing everything to a generic summary?
- Are comparison, fit, pricing, parameter, and risk relationships visually explicit when the upstream content calls for them?
- Is the report credible without inventing metrics or unsupported certainty?
- Are dense sections readable on mobile?
- Is the visual hierarchy strong enough for decision reading, but not so decorative that it weakens trust?
