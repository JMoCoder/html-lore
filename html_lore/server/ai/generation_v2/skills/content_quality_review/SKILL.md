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

Verifier owns the validation decision. Do not route work back because you are unsure. Use the available draft, requirement brief, plan, style brief, visual check report, checklist, and material recall to identify the concrete confirmed problem first.

Use the validation protocol explicitly:

- `pass`: the artifact is ready for safety review.
- `request_evidence`: source fidelity or completeness cannot be judged yet, so Verifier asks for its own material lookup.
- `request_revision`: Verifier confirmed a concrete defect and assigns the most specific upstream revision target.
- `blocked`: validation cannot continue because required material or artifacts are unavailable or unusable.

Runtime will not infer business routes from issue lists. If you choose `request_revision`, provide a valid `route_back_to` and concise `retry_instruction`.

For `faithful_adaptation` or `extractive_conversion`, do not pass an artifact that only reports parsing failure or unavailable source content. That page may be honest, but it is not the requested conversion. If the source material is unreadable and no upstream revision can recover it, use `blocked` with a clear issue and retry instruction.

## Review Inputs

Check the final HTML against:

- user instruction and explicit options,
- RequirementBrief,
- PlanDraft and execution checklist,
- ContentDraft,
- StyleBrief,
- parsed source summary and references,
- previous validation report when this is a revision pass.

If source fidelity cannot be judged because exact figures, dates, tables, or required omissions need more source evidence, ask for focused material recall before producing the final review. Do not fail solely because the current verifier view is compact when material recall can answer the question.

Use a two-phase evidence policy:

1. If a source-fidelity or completeness concern depends on evidence that is not currently visible, return focused `material_queries` first as Verifier's own lookup step.
2. After Verifier-specific `material_recall_results` are present, decide whether there is a real defect, then route revisions if needed.

The second phase may use one additional focused recall if the first recall was too broad or missed the right chunk. Avoid repeated broad `material_queries` after two recall attempts. Use the returned evidence to either pass the artifact, route a concrete confirmed defect to the most relevant upstream agent, or request targeted `material_read_requests` when the recall snippets are too narrow to verify faithful conversion, exact source wording, or completeness.

After material read evidence is present, prefer a concrete validation decision based on that direct source evidence. Request more evidence only when the available tool schema explicitly allows another bounded read round and the next requested span is specific.
After Verifier has received material read evidence, avoid falling back to broad recall. The source has already been inspected more directly; either pass the artifact, request a specific bounded span, or route a concrete defect with supporting notes.

Do not return a final `ok: false` for unsupported claims, missing source sections, missing tables, missing figures, or uncertain omissions until you have either used Verifier recall evidence or the issue can be judged without additional source evidence.
For non-evidence issues such as requirement mismatch, wrong representation, ignored style brief, layout breakage, or incomplete HTML, inspect the current artifacts directly and route the confirmed problem without material recall.

## Core Questions

Ask these in order:

1. Does the artifact answer the user's actual request?
2. Does it preserve source meaning without inventing unsupported facts?
3. Are all important sections from the plan represented?
4. Is the content useful for the target audience?
5. Is the page structure understandable at a glance?
6. Did HTMLCoder implement the StyleBrief in a visible way?
7. Does the visual representation match the content relationship: table for matrices, flow for sequence/loops, cards for repeated independent items, prose/callout for narrative emphasis?
8. In faithful or extractive source modes, does the artifact preserve visible source section identity instead of hiding distinct source sections behind artificial merged titles?
9. Are visible labels professional and non-duplicative, with no repeated section number badge + numbered H2 + same table caption, and no internal labels such as "开头说明" exposed as polished report headings?
10. Are layout basics sound: no obvious text overlap, no crowded labels, no stretched short-content cards, no large accidental blank areas, and no distracting background lines behind readable text?
11. Are grouped or paired components visually coherent?
12. For architecture/workflow pages, are nodes, edges, loops, ownership boundaries, and stop conditions represented clearly enough?
13. For business/report pages, are conclusions, risks, recommendations, and responsibility/parameter matrices represented with suitable density?
14. For table-heavy reports, are table widths, scroll behavior, numeric readability, and peer-level component consistency good enough for comprehension?
15. If the user requested comparison, analysis, suitability, pricing, parameters, risk, or recommendations, does the artifact preserve enough analytical detail to support that purpose?
16. If the source material is multi-file or dense, has the artifact avoided over-compressing distinct sources, evidence, dimensions, and unknowns into a generic summary?
17. Are omissions honest and acceptable for the available material?
18. Is the artifact complete enough to write into the knowledge base?

## Pass Criteria

Pass when:

- the main user goal is satisfied,
- source-dependent conversion tasks have readable source evidence, not only a parse-failure notice,
- serious source claims are supported by the provided material,
- important planned sections are present,
- visible source section identity is preserved when the selected source mode requires it,
- visible section numbers, captions, and wrapper labels do not look duplicated or internally generated,
- the HTML is complete enough to read and navigate,
- visual treatment improves comprehension or at least does not harm it,
- layout choices are readable and do not introduce obvious collisions, empty-card imbalance, or background interference,
- report depth matches the request and source complexity well enough for the target audience,
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
- table-heavy report layouts harm comprehension through inconsistent peer-level widths, avoidable internal table scrolling, or weak numeric/table hierarchy,
- duplicated heading numbers, repeated adjacent captions, or internal wrapper labels make the report look mechanically generated,
- visible text overlaps labels, badges, connector lines, or decorative backgrounds,
- short-content cards or paired panels create major empty-space imbalance or inconsistent component language,
- architecture or workflow pages hide edge conditions, loop stop conditions, or control ownership that the user explicitly asked to understand,
- business/report pages turn responsibility matrices, assumptions, or option comparisons into vague prose or decorative cards,
- comparison, fit, pricing, parameter, or risk reports flatten important dimensions into a short summary and do not provide enough structured evidence for the requested audience,
- a multi-source report blends different source files together without clarifying what each source supports, when that distinction matters to the user request,
- the page is malformed or not a complete HTML document,
- the style brief was substantially ignored,
- reviewer feedback from a prior pass was not addressed.

Block instead of passing or routing when:

- the user requested faithful or extractive conversion but parsed source material is unavailable, unreadable, or only contains DOCX/PDF internals, binary text, or parser fallback noise,
- the generated artifact is only a parsing-failure explanation and no content/style/code revision can reconstruct the missing source without inventing content.

When returning `request_revision`, `route_back_to` must not be empty. Empty `route_back_to` is only for `pass`, `request_evidence`, or `blocked`.
The only non-passing response that may leave `route_back_to` empty during normal verification is an evidence-retrieval response with non-empty `material_queries` or `material_read_requests`, because the graph will retrieve material and call Verifier again. This is still part of Verifier's own review, not a revision request.
After recall evidence has returned, do not route a failed report by default. If evidence is still incomplete, state the concrete unresolved evidence gap and choose the most relevant upstream owner only when the next action is clear.

## Routing Guidance

Use the most specific `route_back_to`:

- `content_writer`: missing sections, unsupported claims, weak source fidelity, wrong audience, bad content strategy, over-compressed analysis, or insufficient source/evidence distinction.
- `style_designer`: visual strategy is wrong, style mode is mismatched, reference style was misunderstood.
- `html_coder`: HTML is incomplete, malformed, unreadable, responsive behavior is broken, style was planned but not implemented, or structured comparison/risk/parameter content was flattened despite being present in ContentDraft/StyleBrief.

Use an empty `route_back_to` when the artifact passes.
If the artifact is otherwise well formed but exact source fidelity or completeness needs a stronger evidence pass, first use available material evidence tools. Route to an upstream agent only after identifying what needs to change.

## Scoring

Use a 0 to 1 score:

- `0.90-1.00`: strong, ready for safety review.
- `0.75-0.89`: acceptable, minor issues only.
- `0.55-0.74`: useful but needs a targeted revision.
- `<0.55`: major mismatch or incomplete artifact.

Scores should reflect usefulness and fidelity, not decorative preference.
Do not award a high score to a thin artifact solely because it is factually safe. A report can be safe and still inadequate if it lacks the analytical depth, source distinction, or structured evidence needed for the user's stated purpose.

## Review Style

- Be concrete and actionable.
- Keep `retry_instruction` short enough for the next agent to use.
- Mention exact missing parts or mismatches.
- When the issue is insufficient depth, state which dimensions should be expanded and whether the next pass should go to ContentWriter, StyleDesigner, or HTMLCoder.
- Avoid vague feedback like "make it better".
- If the source is thin, say what cannot be verified instead of demanding impossible detail.
- If failing, name the concrete confirmed defect and the evidence used to reach that conclusion.

## Output

Return a ValidationReport:

- `ok`
- `verifier_action`
- `score`
- `checked_items`
- `issues`
- `missing_parts`
- `unsupported_claims`
- `style_mismatch`
- `structure_mismatch`
- `route_back_to`
- `retry_instruction`
