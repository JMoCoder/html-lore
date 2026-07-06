---
name: source_free_synthesis
title: Source free synthesis
description: Use when RequirementBrief source_handling_mode is free_synthesis. Guides downstream agents to create a new artifact inspired by supplied material without falsely presenting additions as source facts.
version: 0.1.0
author: HTMlore
license: project-internal
metadata:
  hermes:
    tags: [source-handling, synthesis, content]
    related_skills: []
---

# Source Free Synthesis Skill

Use this skill when `RequirementBrief.source_handling_mode` is `free_synthesis`.

## Contract

- The user allows a new artifact inspired by the source material.
- Added explanation, framing, examples, and synthesis are allowed when useful.
- Do not present new ideas as if they came from the uploaded material.
- Keep source-backed facts distinguishable from general reasoning.

## Agent Guidance

- Planner: plan a coherent artifact around the user's goal, with evidence-aware sections.
- ContentWriter: synthesize naturally, but avoid fake source facts, citations, numbers, or organizations.
- HTMLCoder: implement the approved content without adding claims.
- Verifier: pass useful synthesis when additions are honest; fail unsupported claims presented as source-backed.
