---
name: report_surface_design
title: Report surface design
description: Use when the generated HTML is explicitly requested as a report or should present already-planned report content with credible hierarchy, scannable findings, matrices, risks, recommendations, and decision-oriented reading flow. Helps StyleDesigner design report-like HTML without imposing a fixed report template.
version: 0.1.2
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

This skill should not compress, expand, or reorder report content by itself. It supplies layout and readability options; the agent remains responsible for deciding what structure best satisfies the user's request and source-handling mode.

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
- When the task is faithful or extractive source conversion, preserve source section identity in the visible reading path. Improve the report surface around the source structure instead of replacing it with a generic report template.
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

- Use a stable layout grid with restrained spacing, readable measure for the content role, and clear section dividers.
- Choose one primary report canvas for peer-level sections and keep their left/right edges visually consistent.
- Treat alternate reading lanes, sidebars, appendix notes, or full-bleed bands as intentional semantic variants. If a report section changes canvas relationship, the StyleBrief should state why and how it relates to peer sections.
- Tables, matrices, comparison panels, and multi-card finding groups usually belong on the primary report canvas. Compact notes, sidebars, and expanded evidence areas are acceptable only when their visual weight and semantic relationship match the content.
- Let content weight decide layout weight. A short caveat, one-sentence conclusion, or small note should not become the dominant wide/tall panel merely because it sits near longer evidence. Give short material compact treatment such as a side note, inline fact row, small callout, or balanced companion block.
- Distinguish standalone article prose from report module text. Section introductions, module summaries, table notes, matrix explanations, boundary callouts, and related evidence that belong to the same report module should read as one composed group. Do not mix a detached prose lane with a sibling callout, table, or card group unless the relationship is explicitly intentional.
- When mixing asymmetric blocks, make the asymmetry intentional: the visually larger area should usually carry denser or more important content, while short supporting material should feel compact, anchored, or subordinate.
- Give summary or conclusion areas stronger hierarchy, but avoid oversized marketing hero treatment unless the report is meant for external presentation.
- For opening, summary, or module-entry areas, choose the relationship first: stacked, inline, grouped, side-by-side, table-like, callout, or prose-led. Base that choice on information density, semantic role, and reading priority rather than on a default split-panel habit.
- When metadata, caveats, summaries, evidence, and navigation appear together, do not automatically pair them into two columns. A balanced report entry may be stacked, banded, table-like, or grouped if that better matches the amount of content in each part.
- Avoid solving short-text blankness by squeezing adjacent dense content. If a sparse companion block is useful, keep it visually subordinate or let the dense content carry the main canvas.
- Avoid arbitrary fixed measures in the StyleBrief. Use semantic layout intent, proportional relationships, responsive behavior, and content-density guidance; reserve numeric sizing only for practical containment such as table readability or mobile fallbacks.
- Tables and matrices should be legible on desktop and usable on mobile through horizontal scroll or stacked rows.
- For table-heavy financial or parameter reports, choose table layouts by readability:
  - short parameter tables may be grouped only if they remain readable without avoidable internal scrolling,
  - standard report tables should usually share the primary report canvas,
  - genuinely wide data tables need an explicit scroll container and stronger header/numeric treatment.
- Use visual tokens consistently: surface, border, muted text, primary accent, risk/warning accent, and optional success/next-step accent.
- Keep color functional. Use accent color for hierarchy and status, not decoration.
- Use only one visible numbering system for numbered source sections. A decorative badge and a numbered heading should not repeat the same number side by side.
- Make risk or warning treatments visible but not alarmist.
- Keep charts or diagram-like blocks honest; do not fake data visualization when the source has no data.
- Ensure paired report panels use the same component language unless contrast carries meaning.

## StyleBrief Expectations

When this skill is loaded, StyleDesigner should include:

- report surface type and intended reading mode,
- primary canvas behavior for main report sections, including whether sections are panel-first, article-flow, dashboard-like, or mixed intentionally,
- opening and summary area relationship: whether metadata, caveats, summaries, navigation, and evidence should be stacked, grouped, side-by-side, or table-like, and why that relationship fits their information density,
- rules for matching component scale to content amount and importance, especially when combining short notes with longer evidence, tables, or bullet groups,
- rules for when prose is standalone reading content versus module text, how section leads stay visually connected to related callouts/tables/matrices/card groups, and how compact notes, sidebars, or expanded evidence areas relate to the main canvas,
- which upstream sections need summary, finding, matrix, risk, recommendation, roadmap, or appendix treatment,
- table/matrix guidance when the plan contains comparisons, responsibilities, options, parameters, or evidence categories,
- table-density guidance that distinguishes short parameter tables, standard report tables, and wide data tables,
- explicit horizontal overflow policy for report sections: shared canvas for peer-level sections, scroll containment only for genuinely wide tables, and no accidental full-document overflow,
- analysis-depth guidance when source material is complex: whether the report should read as a short memo, standard report, deep comparison, technical review, or decision brief, and how much detail should be preserved,
- explicit source-vs-judgment guidance when the page contains suitability, risk, or recommendation language,
- density rules for findings, callouts, and long analysis sections,
- mobile handling for tables, matrices, and multi-column report areas,
- visual risk notes for empty cards, over-wide short content, unbalanced split panels, weak contrast, and decorative elements that reduce credibility,
- visual risk notes for high-density content being cramped while low-density companion content dominates the canvas,
- visual risk notes for duplicated section numbers, repeated captions, and internal labels exposed as report headings,
- explicit reminder that missing data must remain missing, not invented for visual polish.

## Review Checklist

- Does the page look like a readable report rather than styled Markdown or a generic landing page?
- Are the upstream conclusions, findings, risks, recommendations, or open questions easy to scan when present?
- Are tables, matrices, timelines, cards, and prose used for the right content relationships?
- If the source material is complex or multi-source, does the surface preserve enough detail to support decision reading rather than reducing everything to a generic summary?
- Are comparison, fit, pricing, parameter, and risk relationships visually explicit when the upstream content calls for them?
- Is the report credible without inventing metrics or unsupported certainty?
- Are dense sections readable on mobile?
- Are peer-level sections aligned on a coherent report canvas, with wide tables contained intentionally rather than causing page-level overflow?
- Does each component's scale feel proportional to its content and importance, especially when a short note sits beside longer evidence?
- Do opening and summary areas let visual weight follow semantic importance and information density rather than a mechanical split layout?
- Is the visual hierarchy strong enough for decision reading, but not so decorative that it weakens trust?
