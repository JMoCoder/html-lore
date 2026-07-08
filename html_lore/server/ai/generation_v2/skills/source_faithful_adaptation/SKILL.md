---
name: source_faithful_adaptation
title: Source faithful adaptation
description: Use when RequirementBrief source_handling_mode is faithful_adaptation. Guides agents to keep source content faithful while improving structure and visual presentation.
version: 0.1.0
author: HTMlore
license: project-internal
metadata:
  hermes:
    tags: [source-handling, faithful, adaptation]
    related_skills: []
---

# Source Faithful Adaptation Skill

Use this skill when `RequirementBrief.source_handling_mode` is `faithful_adaptation`.

## Contract

- The output should remain faithful to source claims, figures, entities, order, omissions, and conclusions.
- Structure, readability, grouping, labels, and visual presentation may improve.
- Light paraphrase is allowed only when it does not change meaning or emphasis.
- Do not add conclusions, assumptions, recommendations, or explanations not present in the source.
- Preserve visible source headings and section identity when the source structure matters to user trust or auditability. Do not collapse distinct source sections just to create a shorter plan.
- For source paragraphs without headings, use professional content-specific wrapper labels or no visible label. Do not expose internal labels such as "opening note", "source note", "开头说明", or "前置说明".

## Agent Guidance

- Planner: plan source-order-preserving sections and identify fidelity targets.
- ContentWriter: adapt source material carefully; prefer source wording for key statements and data; preserve real headings and avoid mechanical invented labels for unheaded introductions.
- HTMLCoder: make visual improvements without adding new claims; avoid duplicating section numbers or repeating an immediately preceding section title as a visible table caption.
- StyleDesigner: improve visual organization without encouraging source-section compression.
- Verifier: check source fidelity, visible section identity, duplicate heading/caption labels, and professional wrapper labels before approving; use material read when completeness is uncertain.
