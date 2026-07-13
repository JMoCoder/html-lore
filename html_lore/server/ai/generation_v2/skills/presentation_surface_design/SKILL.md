---
name: presentation_surface_design
title: Presentation surface design
description: Use when the generated HTML should feel like a PPT, slide deck, pitch deck, executive briefing, keynote-like story, roadshow, product launch, tech sharing, or presentation-like artifact while remaining safe static HTML. Helps StyleDesigner build slide-like narrative rhythm, audience-facing visual hierarchy, talk-track sections, and deck-quality layout contracts without introducing a deck runtime.
version: 0.3.2
author: HTMlore
license: project-internal
metadata:
  hermes:
    tags: [html, design, presentation, pitch, briefing, showcase]
    related_skills: [html_page_design, safe_static_html]
---

# Presentation Surface Design Skill

Design a static HTML artifact that reads like a focused PPT or executive briefing, not a generic article, report, or marketing webpage.

## Role

Use this skill in StyleDesigner when `target_use` is `ppt` or when Planner asks for `presentation`, `slides`, `deck`, `pitch`, `roadshow`, `executive briefing`, `keynote`, `tech sharing`, `product launch`, `showcase`, or similar presentation-oriented output.

This skill is a surface-design enhancer. It should not decide the business conclusion, narrative truth, slide count, speaker script, product claims, metrics, or visual evidence. RequirementAnalyst, Planner, and ContentWriter decide what the presentation should say. StyleDesigner decides how that content should read as a credible slide-like HTML artifact.

This skill is project-internal original guidance. It may be informed by common presentation and HTML design practices, but it does not copy external project prompts, templates, runtime code, or theme assets.

## Boundary

Do not force every PPT-like artifact into a sales pitch deck.

Avoid instructions such as:

- every deck must follow problem / solution / market / traction / roadmap,
- every presentation must have a dramatic hero slide and closing CTA,
- every slide must use the same card grid,
- every technical sharing page must look like a neon developer keynote,
- every business presentation must invent metrics, customers, timelines, or value claims,
- every presentation must include speaker notes, keyboard navigation, JavaScript controls, or a slide runtime.

The current delivery target is safe static HTML. Design slide-like sections and presentation rhythm, but do not assume a real deck runtime unless the implementation layer explicitly provides one. Static in-page anchor navigation is acceptable when it helps shared reading.

## Presentation Surface Types

Choose the surface type from the user's goal, source material, audience, and target context:

- `executive_briefing`: leadership update, board briefing, decision memo, strategy share.
- `pitch_deck`: investor, customer, sales, partnership, or proposal presentation.
- `tech_sharing`: architecture, engineering, research, method, or knowledge sharing.
- `product_launch`: product capability, launch story, feature release, or public showcase.
- `training_module`: course, onboarding, tutorial, or workshop-style presentation.
- `roadshow_story`: external roadshow, campaign narrative, event talk, or keynote-like story.
- `visual_summary`: compressed visual explanation of a report, article, note, or plan.

If the user only selects `ppt` and provides no narrower intent, infer the least misleading surface from the content. Thin source material should become a concise visual summary, not a fake full deck.

## Narrative Strategy

- Treat each major section as a slide-like scene with one clear message.
- Build a talk-track rhythm: setup, context, insight, evidence, implication, next action. Use only the parts supported by the material.
- Make the opening scene identify subject, audience, and point of view quickly.
- Prefer short section titles, strong but supported claims, and visually grouped supporting points.
- Keep one primary idea per slide-like section. If a section has two independent ideas, split or clearly segment them.
- For business presentations, surface the decision, conclusion, or practical ask early when supported.
- For technical presentations, make architecture, workflow, constraints, or trade-offs visible before adding visual drama.
- For educational presentations, use progressive disclosure: concept, example, implication, check.
- Avoid turning every paragraph into a card. Use cards for repeated proof points, capabilities, milestones, stakeholder views, or learning points.

## Slide Canvas Contract

The output is HTML, but each major presentation section should behave like a stable slide canvas:

- Use strong section boundaries so the reader can mentally page through the artifact.
- Treat a slide canvas as a browser-native scene, not as a mandatory centered card or exported PPT frame. A scene may be full-bleed, banded, framed, split, or content-wide depending on the material and audience.
- Keep a consistent canvas rhythm across slide-like sections. On desktop, comparable slides should usually share a similar minimum height, inner padding, title zone, content zone, and footer/page-number zone so the artifact feels like a deck rather than a mixed webpage.
- Use browser width deliberately. Prefer responsive full-width or content-wide slide scenes that can use the available viewport, especially for tables, architecture maps, timelines, dense comparisons, or multi-column evidence. Use a narrow centered frame only when it improves focus or the content is intentionally sparse.
- Keep titles, section labels, slide numbers, decorative marks, and diagrams in predictable collision-safe zones. They do not need identical styling, but their placement should feel deliberate from slide to slide.
- Use viewport-aware sizing. A slide-like section may be near full-screen, slightly shorter, or taller when content requires it, but avoid arbitrary height changes that make adjacent slides feel unrelated.
- Height may create the feeling of page turns, but width should remain content- and viewport-aware. Do not shrink every slide into the same boxed rectangle if the browser can present the material more clearly.
- Keep text blocks short enough for presentation reading. Move supporting detail into compact notes, appendix-like sections, or lower-emphasis blocks.
- Let presentation density follow the user's request and material complexity. A keynote-style deck may emphasize one idea with generous space; an internal briefing, technical sharing, or investor appendix may use denser grids, tables, or maps while preserving slide rhythm.
- Avoid tiny dense paragraphs inside large hero scenes.
- Preserve content hierarchy when the viewport shrinks. Mobile should become a clean stacked talk track, not a broken slide.
- Do not add visible presenter-only instructions. If speaker notes are generated later, they belong in hidden or clearly separated metadata, not on the audience-facing surface.

## Static Navigation

For shareable HTML presentations, consider a lightweight global navigation aid:

- Use script-free anchor links to slide sections. A top or side section index can help readers jump across chapters, but it is separate from page-turn controls.
- Page-turn controls should use three compact controls: previous / directory / next. Use clear symbols or short labels such as `‹`, `☰`, `›` with accessible labels `上一页`, `目录`, `下一页`.
- The previous and next controls must link to the immediately previous and immediately next slide-like scene. The directory control may link to the top chapter index or a dedicated deck directory anchor.
- Prefer bottom-right page-turn controls inside each slide-like scene when the artifact has multiple scenes. This keeps previous/next targets correct without JavaScript: each scene owns its own adjacent anchor targets.
- Do not replace this three-control page-turn group with shortcut links such as `首页`, `目录`, `提示`, `末页`, section dots, or a compact slide index. Those may exist as a separate overview navigation if useful, but the bottom-right control should remain previous / directory / next.
- Keep the control elegant and unobtrusive: semi-transparent surface, readable contrast, small footprint, and enough safe-area spacing so it does not cover slide titles or key content.
- Do not rely on JavaScript, keyboard handlers, forms, inputs, or hidden runtime state.
- On mobile, collapse the three controls to a compact bottom or top rail that remains readable without blocking content.
- The control should support sharing and reading, not simulate a full presentation app.

## Visual Patterns

Choose patterns that support presentation use:

- `hero_brief`: headline, subheadline, audience cue, and 3-4 value chips.
- `value_grid`: business outcomes or benefits in repeated cards.
- `capability_map`: modules or services arranged by layer, domain, or workflow.
- `roadmap`: phased rollout without inventing dates or metrics.
- `comparison_panel`: before/after, current/future, or option trade-offs.
- `talk_track_band`: full-width section with a single takeaway and supporting bullets.
- `executive_summary`: compact conclusion and decision points near the top.
- `evidence_table`: compact matrix for proof, constraints, scope, or responsibilities when tabular comparison is clearer than cards.
- `architecture_scene`: node/edge or layer diagram for technical presentations.
- `case_story`: situation, action, result, lesson, only when source supports it.
- `teaching_sequence`: concept, example, contrast, takeaway.
- `appendix_strip`: compact source notes, caveats, assumptions, or definitions.

## Representation Rules

Choose presentation components from the content relationship:

- one central claim with supporting context -> hero or talk-track scene,
- several benefits, capabilities, or proof points -> value grid,
- sequence, rollout, maturity, or adoption path -> roadmap or timeline,
- architecture, runtime, module, or dependency explanation -> architecture scene,
- alternatives, trade-offs, current/future, before/after -> comparison panel,
- responsibilities, evidence categories, scope, or decision criteria -> evidence table,
- risk, caveat, constraint, or assumption -> warning band or appendix strip,
- training or knowledge transfer -> teaching sequence,
- detailed source material -> appendix-like compact section, not dense slide copy.

Cards are useful for repeated points, but they are not a substitute for comparison tables, diagrams, timelines, or concise narrative scenes.

## Slide-Like Layout Guardrails

- A presentation-like section still needs a strong content grid. Do not rely on large empty areas to create drama.
- Do not make every slide a separate rounded card floating on a page background. Framed slide cards are one valid treatment, but full-bleed scenes, wide bands, split canvases, and edge-to-edge content zones may be more appropriate.
- Pair short claims with compact supporting blocks, not oversized cards that leave half the component blank.
- When placing a badge or label near a headline, keep it above or beside the title in normal flow unless there is clear reserved space.
- Reserve repeatable zones for title, main content, and footer/page metadata when the artifact has multiple slide-like sections. Use those zones flexibly, but avoid moving page numbers and titles to arbitrary positions on each slide.
- Keep repeated slide zones consistent without forcing identical widths. The title, content, navigation, and footer zones should feel related, while the content area can expand for dense evidence or contract for focused claims.
- If a section uses connector lines, loops, or diagram backgrounds, keep text panels opaque enough to hide visual noise.
- Keep companion panels visually aligned. A summary panel and a key insight panel should share the same design language unless the contrast is the message.
- Avoid split layouts where one side is dense and the other is mostly empty. Use asymmetric grids only when the sparse side carries a deliberate hero claim or visual anchor.
- Keep section rhythm varied: combine hero, summary band, matrix/table, roadmap, and capability map instead of repeating the same card grid.
- Keep slide-like scenes visually connected through consistent tokens, but vary composition enough to avoid monotony.
- Avoid placing dense tables inside tiny slide panels. Use a compact matrix, scroll-safe table, or appendix section.
- Do not put translucent cards over strong connector lines, charts, or image details unless the surface is opaque enough to keep text readable.
- Do not make decorative gradients, animation-like effects, or fake UI chrome carry the message.

## Style Rules

- Use stronger contrast and rhythm than a normal knowledge note, but keep it readable.
- Keep decorative effects subordinate to the message.
- Do not invent KPI numbers, customer logos, dates, budgets, or market claims for visual impact.
- When user selected a style preference, express it through hierarchy, spacing, palette, and component shape, not through unsupported content.
- For dark or technology-oriented presentation pages, keep body text contrast high and avoid dense neon effects.
- For light business or technical pages, avoid pale translucent cards over colored lines; it often looks accidental and reduces readability.
- Keep the tone audience-aware:
  - executive audiences need conclusion, impact, risk, and action clarity,
  - technical audiences need mechanism, boundary, trade-off, and evidence clarity,
  - public audiences need plain language, visual story, and low cognitive load,
  - internal self-use presentations can be denser but still need slide rhythm.
- If a reference style file is provided, use it for palette, typography rhythm, spacing, and component shape. Do not copy unrelated branding or proprietary content.

## Output Expectations

StyleBrief should include:

- the presentation surface type and audience reading mode,
- recommended scene rhythm and talk-track order,
- the slide canvas rhythm: width strategy, typical minimum height, title zone, content zone, footer/page-number zone, and when a slide may intentionally break that rhythm,
- density mode for the artifact: highlight-led, balanced briefing, or high-density evidence, with guidance on when to use wide browser space versus focused text measures,
- whether to include script-free three-part page-turn controls, and if so their bottom-right placement, opacity, previous/directory/next anchor behavior, and mobile fallback,
- opening scene strategy and whether it should be a hero, executive summary, or title scene,
- component patterns for value, capability, roadmap, architecture, comparison, evidence, and summary blocks,
- section-level contracts describing scene -> representation -> layout constraint -> visual risk,
- responsive behavior for slide-like sections,
- layout guardrails for density, badge placement, panel pairing, collision-safe zones, and background layering,
- table or matrix guidance when presentation content has responsibilities, options, phases, or decision criteria,
- appendix or caveat handling when source material is detailed, uncertain, or too dense for audience-facing slides,
- avoid styles that would make the artifact look like a fake marketing page, broken slide export, or generic article.

## Review Checklist

- Does the artifact feel like a coherent PPT-style presentation rather than a webpage, report, or styled Markdown?
- Does each slide-like section have one main message and a clear support structure?
- Do slide-like sections share a coherent canvas rhythm, with predictable title and page-number placement, without unnecessarily boxing every scene into the same narrow frame?
- If navigation is present, is it script-free, semi-transparent, unobtrusive, and useful for sharing?
- Is the opening scene appropriate for the audience and source material?
- Are claims, metrics, customers, dates, and roadmaps supported by the uploaded material or user instruction?
- Are tables, diagrams, timelines, cards, and comparison panels used for the right relationships?
- Are titles, badges, numbers, arrows, and decorative marks free from collision?
- Does mobile degrade into a readable talk track instead of broken slides?
- Is the page visually strong without requiring unsupported runtime, controls, or animation?
