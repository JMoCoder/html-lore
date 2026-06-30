---
name: content_quality_review
title: Content quality review
description: Use when verifying whether generated HTML satisfies the user request, source material, plan, content draft, and style brief. Guides Verifier to pass useful complete artifacts, identify unsupported claims or missing sections, and route revisions to the right upstream agent.
version: 0.2.0
author: HTMlore
license: project-internal
metadata:
  hermes:
    tags: [verification, quality, source-fidelity, html, review]
    related_skills: [html_page_design, safe_static_html]
---

# Content Quality Review Skill

Review whether the generated HTML artifact satisfies the user's request, source material, plan, content draft, and style brief.

## Role

Use this skill in Verifier. The goal is not to demand perfection; it is to decide whether the artifact is useful, faithful, complete enough, and ready for safety review.

Safety scanning is handled elsewhere. Do not fail an artifact only because it lacks decorative polish.

## Review Inputs

Check the final HTML against:

- user instruction and explicit options,
- RequirementBrief,
- PlanDraft and execution checklist,
- ContentDraft,
- StyleBrief,
- parsed source summary and references,
- previous validation report when this is a revision pass.

## Core Questions

Ask these in order:

1. Does the artifact answer the user's actual request?
2. Does it preserve source meaning without inventing unsupported facts?
3. Are all important sections from the plan represented?
4. Is the content useful for the target audience?
5. Is the page structure understandable at a glance?
6. Did HTMLCoder implement the StyleBrief in a visible way?
7. Does the visual representation match the content relationship: table for matrices, flow for sequence/loops, cards for repeated independent items, prose/callout for narrative emphasis?
8. Are layout basics sound: no obvious text overlap, no crowded labels, no stretched short-content cards, no large accidental blank areas, and no distracting background lines behind readable text?
9. Are grouped or paired components visually coherent?
10. For architecture/workflow pages, are nodes, edges, loops, ownership boundaries, and stop conditions represented clearly enough?
11. For business/report pages, are conclusions, risks, recommendations, and responsibility/parameter matrices represented with suitable density?
12. Are omissions honest and acceptable for the available material?
13. Is the artifact complete enough to write into the knowledge base?

## Pass Criteria

Pass when:

- the main user goal is satisfied,
- serious source claims are supported by the provided material,
- important planned sections are present,
- the HTML is complete enough to read and navigate,
- visual treatment improves comprehension or at least does not harm it,
- layout choices are readable and do not introduce obvious collisions, empty-card imbalance, or background interference,
- remaining issues are minor and can be edited later.

Do not block for:

- a different but reasonable visual taste,
- minor copyediting,
- lack of advanced animations,
- not using a layout pattern you personally prefer,
- missing facts that were not present in the source material.

## Fail Criteria

Fail and route back when:

- required content is missing,
- the page contradicts the source material,
- the artifact invents important facts, metrics, citations, or claims,
- the structure does not match the requested purpose,
- the layout pattern harms comprehension, such as using generic cards for a process that needs a flow or a matrix that needs a table,
- visible text overlaps labels, badges, connector lines, or decorative backgrounds,
- short-content cards or paired panels create major empty-space imbalance or inconsistent component language,
- architecture or workflow pages hide edge conditions, loop stop conditions, or control ownership that the user explicitly asked to understand,
- business/report pages turn responsibility matrices, assumptions, or option comparisons into vague prose or decorative cards,
- the page is malformed or not a complete HTML document,
- the style brief was substantially ignored,
- reviewer feedback from a prior pass was not addressed.

## Routing Guidance

Use the most specific `route_back_to`:

- `content_writer`: missing sections, unsupported claims, weak source fidelity, wrong audience, or bad content strategy.
- `style_designer`: visual strategy is wrong, style mode is mismatched, reference style was misunderstood.
- `html_coder`: HTML is incomplete, malformed, unreadable, responsive behavior is broken, or style was planned but not implemented.

Use an empty `route_back_to` when the artifact passes.

## Scoring

Use a 0 to 1 score:

- `0.90-1.00`: strong, ready for safety review.
- `0.75-0.89`: acceptable, minor issues only.
- `0.55-0.74`: useful but needs a targeted revision.
- `<0.55`: major mismatch or incomplete artifact.

Scores should reflect usefulness and fidelity, not decorative preference.

## Review Style

- Be concrete and actionable.
- Keep `retry_instruction` short enough for the next agent to use.
- Mention exact missing parts or mismatches.
- Avoid vague feedback like "make it better".
- If the source is thin, say what cannot be verified instead of demanding impossible detail.

## Output

Return a ValidationReport:

- `ok`
- `score`
- `checked_items`
- `issues`
- `missing_parts`
- `unsupported_claims`
- `style_mismatch`
- `structure_mismatch`
- `route_back_to`
- `retry_instruction`
