---
name: webpage_surface_design
title: Webpage surface design
description: Use when the generated HTML is explicitly requested as a webpage, website-like page, landing page, documentation page, article page, product page, or lightweight web prototype. Helps StyleDesigner design scrollable webpage surfaces without forcing a marketing landing-page template.
version: 0.1.0
author: HTMlore
license: project-internal
metadata:
  hermes:
    tags: [html, webpage, website, landing-page, docs, prototype, surface-design]
    related_skills: [html_page_design, safe_static_html, content_quality_review, component_pattern_html]
---

# Webpage Surface Design Skill

Design scrollable HTML webpage surfaces for content that has already been interpreted and planned by upstream agents.

## Role

Use this skill in StyleDesigner when `target_use` is `webpage` or when Planner explicitly asks for a webpage, website-like page, landing page, documentation page, article page, product page, campaign page, dashboard-like prototype, or lightweight web prototype.

This skill is a surface-design enhancer. It should not decide product claims, business conclusions, navigation scope, pricing, testimonials, conversion goals, or application behavior. RequirementAnalyst, Planner, and ContentWriter decide what the page should say. StyleDesigner decides how that content should read as a credible static webpage.

## Boundary

Do not force every webpage into a marketing landing-page pattern.

Avoid instructions such as:

- every webpage must have hero / features / pricing / FAQ / CTA,
- every webpage must include a sticky navigation bar,
- every webpage must include buttons, forms, dashboards, or interactive controls,
- every webpage must look like a SaaS product page,
- every webpage must use oversized hero typography or promotional copy.

Instead, preserve the upstream content intent and improve the webpage surface.

## Webpage Surface Types

Choose the surface type from the user's goal, source material, and audience:

- `editorial_page`: article, knowledge page, long-form explanation, or topic page.
- `product_page`: product, service, capability, or offer introduction.
- `docs_page`: documentation, guide, reference, onboarding, or instructional page.
- `campaign_page`: launch, activity, event, announcement, or focused public page.
- `prototype_page`: static mock of a SaaS, dashboard, mobile page, form, or app screen.
- `portfolio_page`: work, case, project, team, profile, or showcase page.

If the user only selects `webpage` and gives no narrower requirement, infer the least misleading surface from the content. A thin source should become a focused page, not a fake full website.

## Webpage Surface Principles

- Make the page purpose clear in the first viewport without over-marketing the content.
- Use browser-native vertical scrolling as the main reading model.
- Keep the page structure understandable as `header`, `main`, `section`, and optional `footer`.
- Use navigation only when it helps the reader move through multiple meaningful sections.
- Use calls to action only when the user's goal supports an action. Do not invent signup, purchase, contact, or booking actions.
- Distinguish source facts from generated framing. Do not invent social proof, metrics, logos, pricing, guarantees, or user counts.
- Keep section rhythm varied enough to feel designed, but consistent enough to feel like one webpage.
- Preserve the user's material. If the content is informational, do not turn it into sales copy.

## Representation Rules

Choose webpage components from the content relationship:

- broad introduction or public-facing offer -> hero or title band,
- feature, value, service, or capability list -> feature grid or compact cards,
- documentation or guide -> table of contents, step sections, code-like blocks only when source contains code,
- comparison, plans, options, or responsibilities -> comparison table or matrix,
- workflow, onboarding, or process -> stepper, timeline, or process flow,
- metrics supplied by source -> metric blocks, never invented counters,
- questions and objections -> FAQ only when questions are real or clearly implied,
- prototype or dashboard content -> static screen-like panels with honest non-functional controls,
- long narrative -> readable article layout with optional aside notes.

Cards are useful for repeated webpage elements, but they are not a universal substitute for prose, tables, timelines, or documentation sections.

## Visual Direction

- Define a stable webpage shell: width strategy, section spacing, first-viewport treatment, and footer behavior.
- Match the surface to the use case:
  - editorial pages need readable line length and calm section anchors,
  - product pages need clear value hierarchy and credible evidence,
  - docs pages need scan-friendly headings and stable navigation,
  - campaign pages can use stronger visual rhythm but still need source fidelity,
  - prototype pages should look like static product UI without pretending features work.
- Keep buttons visually honest. If there is no real action, use labels, chips, or links only when meaningful.
- Avoid empty split layouts where one side is mostly blank.
- Avoid repeating the same full-width card grid for every section.
- Keep decorative backgrounds away from dense text and small UI components.
- Make mobile behavior explicit for nav, hero, grids, tables, and prototype panels.

## StyleBrief Expectations

When this skill is loaded, StyleDesigner should include:

- webpage surface type and intended reading mode,
- first-viewport strategy and whether a hero is appropriate,
- section rhythm and recommended section order from the upstream plan,
- navigation and CTA rules, including when not to use them,
- component guidance for feature grids, documentation blocks, comparison tables, timelines, FAQ, and prototype panels,
- density rules for public-facing copy, long-form content, and UI-like panels,
- mobile handling for navigation, hero, multi-column areas, tables, and dashboard-like panels,
- visual risk notes for fake CTAs, invented metrics, over-marketing, oversized empty hero areas, repeated card grids, and non-functional controls that look active,
- explicit reminder that unsupported product claims, social proof, prices, and metrics must remain absent.

## Review Checklist

- Does the output feel like a real scrollable webpage rather than a generic styled note or slide deck?
- Is the first viewport clear without forcing promotional content?
- Does the chosen webpage type match the user's material and target use?
- Are navigation, CTAs, and controls only present when they are meaningful?
- Are tables, grids, timelines, FAQ, article sections, and prototype panels used for the right content relationships?
- Does the page avoid invented claims, metrics, pricing, testimonials, or fake business actions?
- Is the mobile version readable and free of overflow, cramped nav, or broken section rhythm?
