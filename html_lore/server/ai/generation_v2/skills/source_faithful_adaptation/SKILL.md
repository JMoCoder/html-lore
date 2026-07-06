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

## Agent Guidance

- Planner: plan source-order-preserving sections and identify fidelity targets.
- ContentWriter: adapt source material carefully; prefer source wording for key statements and data.
- HTMLCoder: make visual improvements without adding new claims.
- StyleDesigner: improve visual organization without encouraging source-section compression.
- Verifier: check source fidelity and visible section identity before approving; use material read when completeness is uncertain.
