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
- If an important source paragraph has no heading, use a professional content-specific wrapper label or no visible label. Do not expose internal workflow labels such as "opening note", "source note", "开头说明", or "前置说明".
- Preserve source-stated handling boundaries. If the source or user frames material as internal, confidential, draft, restricted, non-public, or share-limited, carry that boundary forward as source content without inventing legal language.
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
- Preserve source headings as user-facing headings. For unheaded source introductions or callouts, do not invent mechanical position labels; choose a meaningful label such as "执行摘要", "核心判断", "报告导语", or "前置判断" only when it improves comprehension without changing meaning.
- Preserve source-stated share-scope, confidentiality, draft, restricted-use, or non-public notices as concise user-facing content when present or clearly implied by the user request.
- Use bullets only when the source already has list-like content or when preserving short source statements.
- Avoid meta sentences such as "this section preserves..." or "the report states..." unless those words are in the source.
- Do not merge distinct source sections into a generic summary if the source contains separate headings.
- Do not shorten the artifact only because another general instruction prefers concise sections; source completeness controls.
- Record unavoidable omissions in `omitted_items`; otherwise keep `omitted_items` empty.

## HTMLCoder Guidance

- Render the approved ContentDraft faithfully.
- Do not create new business copy, metric cards, conclusions, or explanatory sidebars unless the content already exists in ContentDraft/source.
- Visual enhancements are limited to typography, spacing, table readability, hierarchy, navigation, and responsive behavior.
- Render source-stated handling notices clearly but calmly when present.
- Avoid duplicate visible labels: if a source heading already includes a number, do not add a separate visible number badge with the same number next to it; if a table sits directly under a same-named section, do not repeat that section title as a visible caption unless the source table has a distinct title.

## Verifier Guidance

- Compare the final artifact against source coverage targets.
- Fail if original prose is replaced by high-level summaries.
- Fail if clear source headings are hidden behind artificial merged range titles that make the conversion harder to audit.
- Fail or request revision when repeated heading numbers/captions make the page look mechanically duplicated, or when an internal label such as "开头说明" is exposed as a polished report heading.
- Fail or request revision when source-stated handling boundaries are omitted, but do not require a notice when the source/user did not imply one.
- Fail if any table rows, columns, key figures, caveats, or final usage notes are omitted.
- Use material read when coverage cannot be verified from current context.
