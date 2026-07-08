---
name: source_grounded_rewrite
title: Source grounded rewrite
description: Use when RequirementBrief source_handling_mode is source_grounded_rewrite. Guides agents to reorganize and clarify source-backed material while preserving facts.
version: 0.1.0
author: HTMlore
license: project-internal
metadata:
  hermes:
    tags: [source-handling, rewrite, grounded]
    related_skills: []
---

# Source Grounded Rewrite Skill

Use this skill when `RequirementBrief.source_handling_mode` is `source_grounded_rewrite`.

## Contract

- The output should be grounded in uploaded material.
- Reorganization, condensation, clarification, and reader-friendly phrasing are allowed.
- Source facts, figures, names, dates, units, and conclusions must not change.
- Important omissions must be explicit when the source is insufficient.
- Preserve source-stated handling boundaries. If the source or user frames material as internal, confidential, draft, restricted, non-public, or share-limited, carry that boundary forward as a concise notice or caveat without inventing legal language.

## Agent Guidance

- Planner: plan a clearer information architecture while preserving source facts.
- ContentWriter: rewrite for clarity, but keep source-backed facts accurate and traceable; when source material is share-sensitive, include a brief source-faithful share-scope or handling notice in the draft.
- HTMLCoder: improve readability and visual hierarchy without changing content; render source-stated handling notices clearly but calmly when present.
- Verifier: check that rewritten content keeps facts intact and does not invent support; preserve source-stated handling boundaries when present, but do not demand a notice when the source/user did not imply one.
