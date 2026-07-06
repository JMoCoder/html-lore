---
name: source_extractive_conversion
title: Source extractive conversion
description: Use when RequirementBrief source_handling_mode is extractive_conversion. Guides agents to convert source material near-verbatim, preserving original content while only changing structure and presentation.
version: 0.1.0
author: HTMlore
license: project-internal
metadata:
  hermes:
    tags: [source-handling, extractive, conversion, fidelity]
    related_skills: []
---

# Source Extractive Conversion Skill

Use this skill when `RequirementBrief.source_handling_mode` is `extractive_conversion`.

## Contract

This is a source conversion task, not a writing task.

- Preserve original facts, numbers, names, dates, units, conclusions, caveats, and table values nearly exactly.
- Prefer source wording for prose. Do not replace source content with a new summary.
- Do not add explanatory claims, recommendations, disclaimers, assumptions, or interpretation.
- Structural labels, containers, table markup, grouping, and responsive presentation are allowed.
- Preserve visible source headings when they exist. Do not merge distinct source sections into artificial range headings or generic grouped titles merely to simplify the page.
- If source text is unavailable or unreadable, the task should block rather than invent content.

## Planner Guidance

- Plan a transcription/extraction workflow, not a rewrite workflow.
- Keep source order unless the user explicitly allows reorganization.
- For each section, state which original source section/table should be transcribed.
- When the source has explicit numbered or titled sections, plan those source sections as visible user-facing sections unless the user asks for a condensed version.
- Adjacent source sections may share a visual group only when the original section identities remain visible inside that group.
- For tables, require all rows and columns to be preserved.
- Verification targets must include no-added-content, no-modified-facts, and complete table/section coverage.
- Do not ask ContentWriter to "write" a replacement narrative when the source already contains the narrative.

## ContentWriter Guidance

ContentWriter acts as a structured transcriber.

- Copy or closely preserve source prose into `sections.body`.
- Convert source tables into `tables` without changing values, row order, columns, or labels.
- Use bullets only when the source already has list-like content or when preserving short source statements.
- Avoid meta sentences such as "this section preserves..." or "the report states..." unless those words are in the source.
- Do not merge distinct source sections into a generic summary if the source contains separate headings.
- Do not shorten the artifact only because another general instruction prefers concise sections; source completeness controls.
- Record unavoidable omissions in `omitted_items`; otherwise keep `omitted_items` empty.

## HTMLCoder Guidance

- Render the approved ContentDraft faithfully.
- Do not create new business copy, metric cards, conclusions, or explanatory sidebars unless the content already exists in ContentDraft/source.
- Visual enhancements are limited to typography, spacing, table readability, hierarchy, navigation, and responsive behavior.

## Verifier Guidance

- Compare the final artifact against source coverage targets.
- Fail if original prose is replaced by high-level summaries.
- Fail if clear source headings are hidden behind artificial merged range titles that make the conversion harder to audit.
- Fail if any table rows, columns, key figures, caveats, or final usage notes are omitted.
- Use material read when coverage cannot be verified from current context.
