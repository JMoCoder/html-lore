---
name: architecture_explainer_design
title: Architecture explainer design
description: Use when the HTML should explain a system, agent workflow, runtime boundary, process, integration architecture, or technical operating model. Helps StyleDesigner and HTMLCoder present nodes, edges, layers, loops, responsibilities, and runtime-vs-agent boundaries clearly.
version: 0.1.0
author: HTMlore
license: project-internal
metadata:
  hermes:
    tags: [html, architecture, workflow, system, process, diagram]
    related_skills: [html_page_design, safe_static_html, content_quality_review]
---

# Architecture Explainer Design Skill

Turn complex systems and workflows into readable static HTML explanations.

## Role

Use this skill when the generated page needs to explain architecture, runtime behavior, agent workflows, pipelines, state machines, process logic, tools, integrations, or loops.

This skill is project-internal original guidance. It does not copy external project prompts, templates, or code.

## Explanation Strategy

- Start with the simplest mental model before listing components.
- Separate "who decides" from "who executes".
- Show boundaries explicitly: user input, runtime/state control, model/agent judgment, tools, storage, output.
- Use consistent names for nodes and edges. Do not rename code concepts for decoration.
- Explain loops with trigger, route-back target, stop condition, and max attempts.
- Keep diagrams honest: no missing nodes, fake services, or invented edges.
- Expose control ownership: user-controlled inputs, code/runtime-controlled state and safety gates, model-controlled judgment, and tool-controlled deterministic execution.
- If the workflow is fixed by code, explain what Planner still decides inside that fixed topology.

## Layout Patterns

- `system_map`: grouped components with labels for runtime, agents, tools, data, and output.
- `pipeline`: ordered nodes with inputs and outputs.
- `state_machine`: decisions, loops, retry paths, and terminal states.
- `boundary_table`: code-controlled vs model-controlled vs user-controlled parameters.
- `node_cards`: each agent/node with responsibility, inputs, outputs, and failure modes.
- `trace_panel`: example run showing stage order and artifacts.
- `edge_list`: compact table of edge conditions, route-back targets, retry caps, and terminal states.

Use cards only when the relationship is "many similar nodes". Use tables for boundaries and responsibilities. Use flows for edges, loops, and ordering. A grid of cards is not a substitute for an architecture map when the user needs to understand control flow.

## HTML Implementation Guidance

- Prefer semantic HTML boxes, CSS grid, and simple connector lines.
- Inline SVG is acceptable for compact diagrams, but every diagram needs nearby text explanation.
- Use tables for parameter boundaries and edge conditions.
- Make diagrams responsive by stacking nodes vertically on mobile.
- Use small labels, badges, and arrows sparingly; text must remain readable.
- Keep connector lines behind nodes and away from text. If nodes are translucent, either remove background lines beneath them or make the node surface opaque.
- Place loop labels such as "retry", "capability loop", or "route back" outside the title collision zone.
- When a stage card has little content, make it compact or group it with related stages rather than stretching it across a wide column.
- Give every diagram label a protected area. Labels should sit in a badge row, side gutter, or dedicated edge label, not on top of headings.
- Use solid or high-opacity node surfaces when connectors or background grids pass behind them.
- When the diagram becomes too dense, split it into overview flow plus a boundary table instead of forcing every edge into one graphic.

## Review Checklist

- Can a new reader identify the main flow within 30 seconds?
- Are runtime, agent, and tool responsibilities distinct?
- Are loop conditions and stop conditions explicit?
- Are code-controlled and model-controlled parameters separated?
- Does the page explain what is fixed workflow topology versus what the model decides dynamically?
- Are flows, tables, and cards used for the right relationships?
- Are diagram labels, badges, and connector lines free of text collisions?
- Do node surfaces protect text from background lines or patterns?
- Does the page avoid exposing raw prompts, secrets, local paths, or private operational data?
