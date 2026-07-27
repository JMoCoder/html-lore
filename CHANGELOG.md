# Changelog

Languages: [English](CHANGELOG.md) | [中文](CHANGELOG.zh-CN.md) | [日本語](CHANGELOG.ja.md)

All notable changes to HTMlore will be documented in this file.

The format is based on Keep a Changelog, and this project uses semantic
versioning after the initial public release.

## [1.2.4] - 2026-07-27

### Fixed

- Public share pages now use the available browser width instead of a fixed centered document frame, so generated reports, dashboards, and virtual presentations retain their intended canvas on wide screens.
- Kept server-rendered shares and the static-share fallback visually consistent, while preserving existing share URLs, download behavior, and iframe sandbox isolation.

## [1.2.3] - 2026-07-15

### Added

- Added formula-aware `.xlsx` parsing that preserves workbook structure and exposes bounded read-only workbook inspection to the requirement, content, and verification agents.
- Added two public sharing policies: default safe static sharing with deterministic safety copies, and an explicit sandboxed interactive mode for trusted content.

### Changed

- Requirement analysis now makes an explicit continue, degraded, or blocked decision from generic material capability facts; checkpoints retain structured workbook data once per private workspace and restore it for resumable jobs.
- Tightened Verifier evidence convergence after direct workbook or material reads without relaxing quality requirements.
- Stabilized CI browser checks by using Playwright 1.61.1 and its pinned Chromium instead of the mutable system Chrome channel.
- Safe sharing now creates a traceable same-directory copy when source HTML needs scripts, controls, charts, unsafe resources, or local references removed; original notes remain unchanged.
- Added `HTML_LORE_SHARE_INTERACTIVE_ENABLED` so hosted deployments can disable interactive sharing without changing the safe default.

## [1.2.0] - 2026-07-13

### Added

- Added explicit OpenAI-compatible Chat Completions reasoning-effort configuration for standard AI calls and an independent V2 generation override. Supported values are `none`, `low`, `medium`, `high`, `xhigh`, and `max`.

### Changed

- Refined the V2 Verifier into a lightweight, convergent quality gate: direct material evidence is prioritized, empty evidence requests are rejected, and truncated HTML previews no longer imply that the full artifact is missing.
- Improved virtual-presentation guidance with responsive browser-width scenes and safe three-part previous / directory / next anchor navigation.
- Clarified safety review so static fragment navigation and preserved source confidentiality, non-offer, and risk notices are treated appropriately without replacing approved content.
- Updated AI configuration documentation to recommend `gpt-5.6-sol` with `medium` reasoning as the GPT-5.6 quality-first evaluation baseline.
- Updated package, app, PWA, demo cache, and provider user-agent versions to `1.2.0`.

## [1.1.16] - 2026-07-10

### Changed

- Further refined AI generation layout prompts and skills to prefer content-led proportions, reduce premature text wrapping and empty-space imbalance, and improve report-level component grouping.
- Updated package, app, PWA, demo cache, and provider user-agent versions to `1.1.16`.

## [1.1.15] - 2026-07-09

### Changed

- Refined AI generation layout skills and prompts to reduce concrete-width bias and guide report module summaries, callouts, tables, and related evidence as semantic visual groups.
- Updated package, app, PWA, demo cache, and provider user-agent versions to `1.1.15`.

## [1.1.14] - 2026-07-09

### Fixed

- Fixed AI-generated HTML safety scanning so CSS class names such as `risk-table-mobile` are not misclassified as API-key secrets while real `sk-...` secret patterns are still blocked.

### Changed

- Updated package, app, PWA, demo cache, and provider user-agent versions to `1.1.14`.

## [1.1.13] - 2026-07-09

### Added

- Added a low-profile download action on public share pages and static share fallback pages so viewers can download the shared HTML document.

### Changed

- Updated package, app, PWA, demo cache, and provider user-agent versions to `1.1.13`.

## [1.1.12] - 2026-07-09

### Added

- Added a reader-page action to download the current note's original HTML source.

### Changed

- Improved AI generation surface skills for report and virtual-slide outputs, including more balanced report blocks and consistent slide navigation/layout rhythm.
- Updated package, app, PWA, demo cache, and provider user-agent versions to `1.1.12`.

## [1.1.11] - 2026-07-08

### Changed

- AI generation retry now distinguishes resumable technical interruptions from workflow/content failures. V2 material jobs write private checkpoints and only expose manual retry when a failed job can resume from the saved checkpoint.
- Updated package, app, PWA, demo cache, and provider user-agent versions to `1.1.11`.

## [1.1.10] - 2026-07-08

### Changed

- Improved AI generation workflow details so RequirementAnalyst artifacts show the user's original instruction explicitly.
- Strengthened AI generation v2 style and HTML skills with semantic width guidance for section leads, module summaries, table notes, and component groups.
- Added lightweight source-handling skill guidance so ContentWriter preserves source-stated internal, confidential, draft, restricted, non-public, or share-limited handling boundaries before safety review.
- Updated package, app, PWA, demo cache, and provider user-agent versions to `1.1.10`.

## [1.1.9] - 2026-07-08

### Changed

- Added pre-output self-review guidance to AI generation v2 agent prompts, covering requirement fidelity, source handling mode, section/table/number preservation, skill selection, verifier routing, and safety review.
- Strengthened HTMLCoder and static HTML skills with layout-repair behavior: overflow, width drift, title collisions, duplicated labels, and table-container defects should be fixed in HTML/CSS while preserving approved content.
- Improved the AI generation workflow detail dialog so polling refreshes preserve scroll positions for the stage list, detail panel, checklist, and loaded-skill list.
- Updated package, app, PWA, demo cache, and provider user-agent versions to `1.1.9`.

## [1.1.8] - 2026-07-06

### Added

- AI generation v2 Planner payload now includes a registered capability catalog that separates selectable skills from runtime tools used only for boundary awareness.
- AI generation v2 requirement analysis now outputs `source_handling_mode` to distinguish free synthesis, source-grounded rewrite, faithful adaptation, and extractive conversion, with downstream planning, writing, coding, and verification aligned to that mode.
- AI generation v2 document parsing now has a three-layer parser chain extension point: future specialized parsers, MarkItDown, then local basic parsing, with one retry per active parser layer.
- AI generation v2 source handling modes now route to dedicated skills for planning, writing, coding, and verification, making extractive conversion behave as structured source transcription instead of general rewriting.

### Changed

- AI generation v2 browser visual checking now defaults to `basic`; missing Playwright or Chrome/Chromium still skips the check and records the skip instead of blocking generation.
- AI generation v2 ingest now blocks clearly unreadable enhanced-format uploads before calling LLM agents, returning `parse_failed` instead of generating from DOCX/PDF container noise.
- OpenAI-compatible provider calls now wrap incomplete HTTP reads as retryable provider errors, allowing long generation nodes to retry instead of failing the whole job on a partial response.
- AI generation v2 source fidelity prompts no longer impose artificial section-count, compactness, or byte-size guidance on extractive conversion jobs; StyleDesigner and Verifier now check source section identity, table width consistency, and numeric readability.
- Updated package, app, PWA, demo, and provider user-agent versions to `1.1.8`.

## [1.1.7] - 2026-07-02

### Added

- Added structured material status to AI generation v2 agent payloads and
  workflow artifacts so agents can distinguish parser quality from prompt
  preview truncation.
- Added a bounded task-local MaterialReadTool for RequirementAnalyst,
  ContentWriter, and Verifier to inspect uploaded material when startup chunks
  or recall snippets are insufficient.
- Added private generation job workspaces for normalized material bundles,
  per-agent artifacts, and material evidence logs.

### Changed

- Preserved per-file material identity across merged uploaded documents so
  multi-file jobs can locate source spans without relying on body text markers.
- Improved failed v2 generation job synchronization so terminal runs stay
  failed/completed instead of appearing stuck in progress.
- Improved the generation workflow detail dialog for repeated stages and long
  skill lists.
- Updated package, app, PWA, demo, and provider user-agent versions to
  `1.1.7`.

### Security

- Material workspaces are stored under private metadata paths, sanitized from
  public job payloads, and removed with the associated generated note.

## [1.1.6] - 2026-07-02

### Changed

- Strengthened AI generation v2 verification so evidence gaps trigger
  Verifier-owned material recall before routing revisions back to upstream
  agents.
- Made failed AI generation retry controls consistent between the history list
  and workflow detail dialog when a job is not retryable.
- Preserved a truncated original user instruction in generation workflow
  artifacts to improve local debugging without exposing raw uploaded content.
- Removed local `mark/` working notes from repository tracking and ignored them
  like other local development documents.
- Updated package, app, PWA, demo, and provider user-agent versions to
  `1.1.6`.

### Security

- Local notes, AI provider keys, generated artifacts, and test observations
  remain outside the release commit.

## [1.1.4] - 2026-06-30

### Added

- Added explicit AI generation target-use routing for report and webpage
  surfaces, with project-internal StyleDesigner skills for report-like and
  scrollable webpage artifacts.

### Changed

- Expanded the presentation/PPT target-use skill into a fuller HTML virtual
  presentation contract covering audience-facing scene rhythm, slide canvas
  constraints, talk-track order, presentation surface types, and supported
  representation choices.
- Updated the AI creation target-use option from website to webpage and added
  magazine as a style preference while preserving legacy website compatibility.
- Updated package, app, PWA, demo, and provider user-agent versions to
  `1.1.4`.

### Security

- Local AI provider configuration, API keys, generated notes, and development
  library data remain outside the release commit.

## [1.1.1] - 2026-06-29

### Added

- Added default AI generation v2 skill routing and optional capability skills
  for presentation surfaces, architecture explainers, and static HTML component
  patterns to improve output quality without changing the graph architecture.

### Changed

- Strengthened AI generation v2 design, component, and verification prompts with
  a layout contract for representation choice, card density, title/badge
  spacing, paired-component consistency, and background/content layering.
- Requirement analysis and planning now preserve non-default generation options
  such as theme, target use, style preference, audience, and reference style
  files more explicitly so downstream agents do not drop user choices.
- Updated package, app, PWA, demo, and provider user-agent versions to
  `1.1.1`.

### Security

- Local real-AI test configuration, API keys, development library data, and
  generated notes remain in ignored local directories and are not included in
  the release commit.

## [1.1.0] - 2026-06-26

### Added

- Added `HTML_LORE_AI_GENERATION_MAX_TOKENS` so HTML generation has its own
  output budget instead of inheriting the shorter Q&A response limit.
- Added configurable provider chat and embedding wait times with
  `HTML_LORE_AI_PROVIDER_TIMEOUT_SECONDS` and
  `HTML_LORE_AI_EMBEDDING_TIMEOUT_SECONDS`.

### Changed

- Relaxed provider wait handling for long HTML generation while keeping node
  retries, max graph steps, and reviewer revision limits; no total wall-clock
  cutoff is applied to a generation job.
- Updated README and AI generation closure notes with a real complex-generation
  validation showing the streamed multi-agent path can write a local note.
- Updated package, app, PWA, demo, and provider user-agent versions to
  `1.1.0`.

## [1.0.5] - 2026-06-25

### Added

- Added a large AI generation workflow detail modal for LangGraph stage status,
  agent input/output summaries, token usage, lightweight quality scores,
  warnings, and stage metadata.
- Added an SSE endpoint for generation job updates with polling fallback so
  task details can refresh while background generation is running.

### Changed

- Improved AI generation history and the workspace generation queue: completed
  jobs show an open action, failed jobs show retry, and running/pending jobs show
  queue position and status.
- Improved AI run history layout, removed internal agent ids from list rows, and
  backfilled run duration from historical trace timestamps.
- Synced the live workspace and static demo UI for AI creation, generation
  history, conversation history, and settings pages.
- Updated package, app, PWA, demo, and provider user-agent versions to
  `1.0.5`.

### Security

- Public job and run details continue to expose only redacted summaries, not raw
  prompts, uploaded source text, reference file content, generated HTML bodies,
  API keys, or cost estimates.

## [1.0.4] - 2026-06-24

### Added

- Added the AI generation v2 baseline for text-only prompts, optional material
  files, and optional reference style files.
- Added generation agent artifacts and stage trace metadata so local task
  details can show what each agent produced without storing raw uploads,
  full prompts, reference content, or generated HTML bodies.

### Changed

- Updated the workspace "Create with AI" flow to use natural-language input
  first, with file and reference style uploads as optional controls.
- Kept the generation v2 finalizer as runtime assembly only so the HTML coder's
  output is not rewritten by a final model pass.
- Improved generation v2 schema tolerance, transient provider retries, and
  privacy redaction for task logs.
- Updated package, app, PWA, demo, and provider user-agent versions to
  `1.0.4`.

## [1.0.3] - 2026-06-22

### Fixed

- Fixed knowledge-base Q&A evidence gating so current-note and manually scoped
  expansion questions are not rejected as weakly relevant before the model can
  answer.
- Fixed short follow-up instructions so they can inherit the active topic
  instead of starting from an empty context.
- Fixed GitHub Actions Playwright validation on Ubuntu 26.04 by using the
  system Chrome channel instead of Playwright-managed Chromium.
- Updated the workspace AI upload regression check for the current file-picker
  flow and tightened topbar / reader layout behavior across demo and app
  builds.

### Changed

- Updated package, app, PWA, demo, and provider user-agent versions to
  `1.0.3`.

## [1.0.2] - 2026-06-22

### Changed

- Updated the agent runtime dependency floor to LangGraph 1.2.x, pulling in the
  matching LangChain Core and checkpoint packages.
- Removed the LangChain pending-deprecation warning emitted during LangGraph
  imports in the local development environment.
- Updated package, app, PWA, demo, and provider user-agent versions to
  `1.0.2`.

## [1.0.1] - 2026-06-22

### Added

- Added the beta AI HTML generation v2 workflow for uploaded materials, with
  staged agents, structured model calls, MarkItDown-backed parsing, safe static
  HTML writing, task trace metadata, and checklist status updates.
- Added the workspace "Create with AI" source-file upload flow with optional
  theme, purpose, style, and audience controls.

### Changed

- Improved the create form layout, long-prompt resizing, static demo preview,
  topbar settings/search controls, and narrow workspace behavior when the AI
  sidebar is open.
- Documented MarkItDown parser deployment notes and resource considerations.
- Updated package, app, PWA, demo, and provider user-agent versions to
  `1.0.1`.

## [1.0.0] - 2026-06-17

### Added

- Promoted the knowledge-base Q&A flow to a formal 1.0.0 release with
  LangGraph-first orchestration, context-aware retrieval, recent-conversation
  grounding, Markdown rendering, clickable source pills, and per-context
  history.
- Added the Tavily -> Brave -> disabled external-search fallback chain, with
  both providers optional and the app still usable in local-only mode.
- Added dynamic search planning so result caps can grow with intent while still
  respecting cost limits.

### Changed

- Updated README guidance for 1.0.0 release scope, external-search options,
  and demo/static boundaries.
- Updated package, app, PWA, demo, and provider user-agent versions to
  `1.0.0`.

### Fixed

- External Q&A source pills now open their source URL when a search result
  includes a link.

## [0.9.10] - 2026-06-17

### Changed

- Renamed the AI sidebar source controls to shorter `Expand` and `Research`
  labels.
- Simplified static demo AI behavior so it mirrors the live workspace styling
  while keeping backend and AI actions disabled as preview-only controls.
- Updated README notes for clickable external Q&A sources and static demo
  boundaries.
- Updated package, app, PWA, demo, and provider user-agent versions to
  `0.9.10`.

### Fixed

- External Q&A source pills now open their source URL when a search result
  includes a link.

## [0.9.9] - 2026-06-17

### Added

- Added the LangGraph knowledge-base Q&A engine as the default `auto` runtime,
  with the previous agent runtime kept as a fallback.
- Added reusable conversation resolution, route planning, search planning,
  evidence assessment, verifier, reviewer, and trace metadata for the Q&A
  workflow.
- Added external-search planning support for content expansion, including
  Tavily status wiring and controlled source-mode handling.

### Changed

- Improved Q&A source-mode behavior so content expansion no longer starts a new
  conversation; it now affects the next message while preserving the current
  context.
- Updated static demo AI behavior and e2e coverage to match the live workspace
  conversation flow.
- Updated README deployment notes for AI provider, LangGraph, embedding, and
  Tavily configuration.
- Updated package, app, PWA, demo, and provider user-agent versions to
  `0.9.9`.

### Fixed

- Fixed demo CI failures around AI source-mode switching and restoring the
  latest conversation for the current context.
- Fixed the demo pending-reply assertion to match the animated reply indicator.

## [0.9.8] - 2026-06-16

### Removed

- Removed the former rename migration guide and active documentation links to
  the old project name.
- Removed browser preference migration from the old localStorage prefix and
  dropped imports of the old backup payload type.

### Changed

- Kept environment configuration tests focused on the current `HTML_LORE_*`
  prefix and generic unknown-prefix rejection instead of old-name compatibility.
- Updated package, app, PWA, demo, and provider user-agent versions to
  `0.9.8`.

## [0.9.7] - 2026-06-15

### Added

- Added generic retrieval pollution controls for knowledge-base Q&A so
  low-trust generated artifacts no longer hijack unrelated global questions,
  including matching protection for both keyword and vector retrieval paths.
- Added extracted conversation resolution and route planning modules for the
  live Q&A runtime, keeping follow-up handling and intent routing reusable for
  the broader AI architecture.

### Changed

- Updated the live Q&A prompt builder to use gated evidence instead of raw
  retrieval output, so the answer stage now follows the same filtered evidence
  contract used by verification and review.
- Tightened entity attribute external-evidence assessment and global weak-signal
  refusal behavior without hardcoding business-specific names.
- Updated package, app, PWA, demo, and provider user-agent versions to
  `0.9.7`.

## [0.9.6] - 2026-06-15

### Added

- Added a staged knowledge-base Q&A runtime contract that separates planner,
  search planner, answer agent, verifier, reviewer, agent trace, and prompt
  trace metadata, so the backend can evolve toward the broader multi-agent AI
  architecture without breaking the current notebook workflows.

### Changed

- Refined follow-up retrieval so short prompts such as `联网搜索` inherit only
  recent user questions instead of mixing prior assistant answers into the
  retrieval query.
- Aligned fake-provider QA runs with the newer verifier/reviewer contract so
  development and CI can validate the runtime structure without being rejected
  by production-oriented answer-quality checks.
- Updated package, app, PWA, demo, and provider user-agent versions to
  `0.9.6`.

## [0.9.5] - 2026-06-11

### Added

- Added OpenAI-compatible embedding requests and a lightweight local vector
  index for vector/hybrid knowledge-base retrieval. The index is stored under
  the active user's metadata directory and requires
  `HTML_LORE_AI_EMBEDDING_MODEL` plus `HTML_LORE_AI_RETRIEVAL_MODE=vector` or
  `hybrid` to take effect; otherwise retrieval falls back to keyword mode.
- Added backend-only vector index maintenance APIs and the
  `html-lore ai-vector-index` CLI for stats, prune, clear, rebuild, and
  embedding smoke tests.
- Added Tavily as a controlled external-search adapter for AI content
  expansion, with server-side API key configuration, low-cost defaults, topic
  and time-range inference, country hints from the user query, and advanced
  search only for explicit deep-research requests or operator configuration.
- Added a disabled Deep Research checkbox beside content expansion in the AI
  sidebar as a visible placeholder for the future asynchronous research
  workflow.

### Changed

- Stale local vectors are now cleared when a note is edited, archived, or
  permanently deleted, and vector retrieval avoids repeated index reads while
  preparing chunks for larger contexts.
- Updated package, app, PWA, and provider user-agent versions to `0.9.5`.

## [0.9.4] - 2026-06-10

### Changed

- Improved knowledge-base Q&A prompts with current context summaries and recent
  conversation context, so short follow-up questions can stay grounded in the
  active notebook context.
- Improved retrieval for multi-note contexts by expanding short follow-up
  queries from recent dialogue and balancing evidence across more distinct
  notes before adding duplicate chunks.
- Added retrieval coverage diagnostics for context item count, covered item
  count, coverage ratio, and query expansion state.
- Updated package, app, PWA, demo, and provider user-agent versions to `0.9.4`.

### Fixed

- Fixed AI Markdown rendering so ordered lists keep natural numbering and
  heading hierarchy is visually coherent without constraining model output
  format in the backend prompt.
- Fixed AI sidebar More menu alignment and width.

## [0.9.3] - 2026-06-09

### Fixed

- Improved the visual file editor background color picker so selected inline
  text follows the nearest non-transparent parent background.
- Updated package, app, PWA, demo, and provider user-agent versions to `0.9.3`.

## [0.9.2] - 2026-06-09

### Added

- Added manual HTML source editing for non-archived notes with save, save and
  close, fullscreen, line wrapping, cursor position, and share-safety precheck.
- Added a conservative visual file editor for non-archived notes with text
  editing, color/background controls, inline text styles, undo/redo, element
  reset, resizable/collapsible editor panel, and direct preview editing.

### Changed

- Improved left navigation section headers for Library, Collections, and Tags
  with clearer default accent styling.
- Updated package, app, PWA, demo, and provider user-agent versions to `0.9.2`.

### Fixed

- Fixed visual editor text-area cursor jumps while typing in the side panel.
- Fixed visual editor selection so blank canvas clicks no longer select the
  whole document, while composite text blocks can still be selected as a unit.
- Fixed visual editor color pickers so selected text/background colors stay in
  sync with rendered styles.
- Fixed visual editor undo/redo disabled states and panel collapse behavior.

## [0.9.1] - 2026-06-08

### Changed

- Renamed the AI sidebar queue popover to generation history in English,
  Chinese, and Japanese.
- Display generation jobs in chronological order, with the newest entries at
  the bottom of the popover.
- Updated package, app, PWA, demo, and provider user-agent versions to `0.9.1`.

### Fixed

- Fixed AI More menu item highlighting and icon centering.
- Fixed AI sidebar conversation history so reader-page history is scoped to the
  current note instead of showing global conversations.
- Fixed generation-history rows so completed jobs show completion time, active
  jobs show a live status marker, and failed retryable jobs show a retry action.

### Security

- Added a retry endpoint for failed conversation-to-HTML generation jobs while
  keeping retry metadata private in the backend job store.
- Kept uploaded-material generation jobs non-retryable from history unless their
  source material can be retried without persisting private upload content.

## [0.9.0] - 2026-06-08

### Added

- Added server-side AI provider configuration for OpenAI-compatible endpoints,
  with API keys read only from backend environment variables.
- Added a knowledge-base Q&A beta flow with context resolution, keyword
  retrieval, strict/content-expansion modes, Markdown-rendered assistant
  messages, source pills, and rate limiting.
- Added persistent AI conversations, latest conversation restore per context,
  per-context history in the AI sidebar, and global conversation management in
  Settings.
- Added a lightweight AI job queue, run history, queue popover, and job/run API
  endpoints.
- Added beta HTML note generation from existing conversations using a staged
  PM/UX/Coder/QA/Reviewer graph.
- Added beta material-to-HTML generation from uploaded HTML, Markdown, or plain
  text files.
- Added vector/hybrid retrieval scaffolding with keyword fallback while the
  pluggable vector store is not yet configured.
- Added AI guardrails for prompt budget, unsupported requests, secret-like
  output, and share-target HTML safety checks.
- Added frontend AI panel refinements: compact context header, resizable
  composer area, reply status, context reset, conversation history, queue/more
  menu behavior, and icon-only conversation management actions.

### Changed

- Updated README files in English, Chinese, and Japanese to document current AI
  capabilities, server-side AI configuration, and beta limitations.
- Regenerated the static demo README and CHANGELOG notes from the current
  documentation.
- Updated package, app, PWA, demo, and provider user-agent versions to `0.9.0`.

### Security

- Confirmed AI public provider responses expose only public status fields such
  as `has_api_key`; raw API keys are not accepted by the browser settings API
  and are not returned to the frontend.
- Added tests that assert AI provider secrets are not leaked through status,
  provider config, or generated run payloads.

### Fixed

- Improved global-context Q&A retrieval so overview-style questions can use the
  full selected context instead of over-focusing on a single note.
- Fixed static build copying so `app_static` is not copied into itself.
- Fixed AI sidebar menu state, conversation-history filtering, settings
  sidebar closing behavior, and related Playwright coverage.

## [0.8.4] - 2026-06-06

### Fixed

- Increased the desktop reader header height budget so tags remain visible when
  a two-line title and three-line summary are shown with both sidebars open on
  laptop-width screens.

### Added

- Added Playwright coverage for the laptop-width reader layout with both
  sidebars open.

### Changed

- Updated package, app, PWA, and demo cache versions to `0.8.4`.

## [0.8.3] - 2026-06-06

### Fixed

- Changed the mobile Settings page navigation into a compact horizontal
  scrolling tab bar so long setting section names no longer render as oversized
  blocks or overflow the phone viewport.
- Kept the desktop Settings page on the existing left-navigation layout.

### Added

- Added Playwright coverage for the mobile Settings tab scroller and the
  desktop Settings navigation layout.

### Changed

- Updated package, app, PWA, and demo cache versions to `0.8.3`.

## [0.8.2] - 2026-06-05

### Fixed

- Refined the tag filter count placement so the selected result count appears
  inline beside the "Tag filters" title in accent text, while the redundant
  lower "Tags" label is removed.
- Card dates now prefer the stable item creation date, so archive/unarchive
  and other state updates no longer change the date shown on cards.

### Changed

- Updated package, app, PWA, and demo cache versions to `0.8.2`.

## [0.8.1] - 2026-06-05

### Added

- Added dynamic result counts to the tag filter popover. The title now shows
  the current filtered item count, OR mode keeps per-tag counts independent,
  and AND mode shows co-occurring tag counts within the current intersection.
- Added share expiry/status metadata to the share dialog and share management
  list.

### Fixed

- Kept fragment links inside public shared HTML pages scoped to the shared
  document instead of navigating back to the workspace shell.
- Increased reader header spacing so three-line summaries do not crowd the tag
  row against the header boundary.

### Changed

- Reduced the OR/AND tag match buttons in the filter popover.
- Updated package, app, PWA, and demo cache versions to `0.8.1`.

## [0.8.0] - 2026-06-05

### Removed

- Removed legacy `html_vault` Python compatibility package, the old
  `html-vault` CLI entry point, and `HTML_VAULT_*` runtime environment
  fallback paths. Current runtime configuration now uses `html_lore`,
  `html-lore`, and `HTML_LORE_*` only.

### Changed

- Updated Docker, deployment examples, migration notes, and package discovery
  to use the renamed HTMlore runtime path only.
- Updated package, app, PWA, and demo cache versions to `0.8.0`.

## [0.7.9] - 2026-06-05

### Added

- Added an HTMlore homepage shortcut to the sidebar footer beside the GitHub
  shortcut.
- Added static share shell repair so existing active share entries can regain
  a safe `/share/{token}` entry page after route or cache issues.

### Changed

- The workspace brand logo now returns to the workspace home instead of opening
  the public project homepage.
- Moved the Agent Server connection status into Settings > User profile.
- Removed the sidebar footer user status button; account details stay inside
  settings.
- On mobile reader pages, the reader metadata and action header now scrolls away
  with the note content while the global top bar remains available.

### Fixed

- Hidden zero-count tags after archiving notes, while restoring them when notes
  are unarchived.
- Fixed `/share/{token}/` routing to match `/share/{token}`.
- Updated package, app, PWA, and demo cache versions to `0.7.9`.

## [0.7.8] - 2026-06-05

### Fixed

- Removed the reader Fit width / Original width button introduced in `0.7.7`;
  mobile reader behavior will be redesigned without adding unconfirmed controls.
- Changed the mobile sidebar from a hidden or narrow left rail into a top
  vertical-collapse bar, keeping navigation usable without squeezing the
  workspace.
- Added a static share fallback that renders `/share/{token}` from
  `/api/public/shares/{token}` when deployment routing accidentally returns the
  workspace shell.
- Added per-token static share shells under `public/share/<token>/index.html`
  and removes them when shares are revoked or replaced.
- Added Playwright coverage for mobile sidebar collapse and static share
  fallback rendering.
- Updated package, app, PWA, and demo cache versions to `0.7.8`.

## [0.7.7] - 2026-06-05

### Added

- Added an initial reader-level width-mode experiment for HTML notes.

### Fixed

- Improved mobile reader layout so the left sidebar no longer consumes reading
  width on narrow screens.
- Kept reader action buttons above the iframe content on mobile instead of
  letting note content visually cover them.
- Added Playwright coverage for the mobile reader viewport.
- Updated package, app, PWA, and demo cache versions to `0.7.7`.

## [0.7.6] - 2026-06-04

### Security

- Minimized the public share JSON response so share readers no longer receive
  internal item IDs, collection/tag metadata, share management IDs, access
  counters, or copyable management URL fields.
- Prevented revoked or expired shares from being reactivated or extended through
  the share update API.
- Hardened shared HTML sanitization so resource `src` attributes cannot point
  back to private `/api/` or `/content/` paths, nor to external tracking
  resources; only vetted inline SVG data images remain allowed.
- Added share security tests for private API isolation, public response
  minimization, inactive-share update rejection, and resource-source stripping.
- Updated package, app, PWA, and demo cache versions to `0.7.6`.

## [0.7.5] - 2026-06-04

### Fixed

- Fixed the Caddy deployment route for public share pages by proxying
  `/share/*` to the backend API instead of letting the static app fallback
  return the workspace shell.
- Updated the optional Basic Auth Caddy example so `/share/*` and
  `/api/public/shares/*` remain publicly reachable while the workspace and
  private API routes stay protected.
- Added deployment-config tests covering public share routing.
- Updated package, app, PWA, and demo cache versions to `0.7.5`.

## [0.7.4] - 2026-06-04

### Fixed

- Fixed public share pages so shared note HTML is rendered inside an isolated
  iframe, preventing source-page global styles from breaking the HTMlore share
  shell or showing oversized icon artwork.
- Persisted share `url_path` values so active shared notes can reopen the share
  dialog and copy the existing public link instead of only seeing it at creation
  time.
- Moved revoke-share controls to the left side of the share dialog and share
  management rows.
- Updated the PWA service worker so `/share/`, `/api/`, and `/content/` routes
  are not intercepted by the workspace app-shell cache.
- Updated package, app, PWA, and demo cache versions to `0.7.4`.

## [0.7.3] - 2026-06-04

### Added

- Preserved safe inline CSS and same-page `#anchor` links on public share pages
  while still blocking external CSS resources and dangerous CSS features.
- Added explicit `requires-static-export:chart` share safety feedback for
  Chart.js/canvas notes that need static chart export instead of script
  execution.

### Fixed

- Fixed public share pages so sanitized full HTML documents render as body
  content plus safe head styles instead of nesting `<html>/<head>/<body>` inside
  the share wrapper.
- Increased import feedback spacing and card-summary breathing room to avoid
  cramped upload messages and slight summary/tag overlap.
- Updated package, app, PWA, and demo cache versions to `0.7.3`.

## [0.7.2] - 2026-06-04

### Added

- Added backend-backed public note sharing with expiring token links, share
  management APIs, public sanitized share pages, and revoke support.
- Added share safety checks that block executable HTML, form/embed content,
  dangerous URL schemes, local/private references, and likely secrets before a
  public share can be created.
- Added a narrow safe-share conversion for local `toggleGroup('id')`
  collapsible note interactions while stripping source scripts and external
  font/resource links from the public share page.
- Added workspace share UI on reader pages, share-link management in Settings,
  and removed the internal copy-link reader action.
- Moved the workspace Agent connection status into the sidebar profile popover
  and made the large profile avatar uploadable from that popover.
- Updated package, app, PWA, and demo cache versions to `0.7.2`.

## [0.7.1] - 2026-06-04

### Fixed

- Fixed card-level Original links in deployed workspaces so they use the authenticated raw item API instead of static `content/...` paths that can be intercepted by SPA fallback routing.
- Added same-origin API detection for self-hosted HTTP/HTTPS deployments while keeping GitHub Pages and static demo mode backend-free.
- Blocked service workers during Playwright checks and added coverage for card Original links in API-backed and static demo modes.
- Updated package, app, PWA, and demo cache versions to `0.7.1`.

## [0.7.0] - 2026-06-04

### Changed

- Promoted the HTMlore rename, repository migration, primary `html_lore`
  package namespace, `html-lore` CLI, and `HTML_LORE_*` configuration names to
  the `0.7.0` stable release.
- Added a migration guide for deployments upgrading from the former project
  name to HTMlore.
- Cleaned up remaining sample and static asset references from the former
  project name after the HTMlore rename.
- Updated public homepage, demo README notes, app accessibility labels, and
  logo descriptions to use HTMlore's current library/lore wording.
- Refined the public homepage and workspace wordmark so both use the same
  `HTM` + accented `lore` styling.
- Routed the legacy `html-vault` console script through the compatibility
  wrapper so its help output keeps the legacy command name while using the
  `html_lore` implementation.
- Expanded `.env.example` with the local login/session and self-hosted
  multi-user data settings used by the default Docker deployment.
- Added a Docker image health check for the backend API.
- Added GitHub Actions CI for pytest, Playwright demo checks, and Docker
  Compose validation.
- Updated package, app, PWA, demo, and homepage cache versions to `0.7.0`.

## [0.6.8] - 2026-06-04

### Changed

- Moved the primary Python implementation package to `html_lore`.
- Updated package entry points, tests, API server launch paths, and Docker
  packaging to use the new `html_lore` namespace by default.
- Kept the legacy `html_vault` package as a thin compatibility shim for
  existing imports and old `uvicorn html_vault.server.app:app` launch paths.
- Updated package, app, PWA, demo, and homepage cache versions to `0.6.8`.

### Compatibility

- Existing `html_vault` imports and the legacy `html-vault` CLI remain
  supported during the 0.x compatibility window.

## [0.6.7] - 2026-06-04

### Added

- Added the new `html-lore` CLI entry point while keeping the legacy
  `html-vault` command available during the 0.x compatibility window.
- Added the `html_lore` public Python namespace as a compatibility entry that
  points to the existing implementation package.
- Added `HTML_LORE_*` runtime configuration names with fallback support for
  legacy `HTML_VAULT_*` environment variables.
- Added browser preference migration from `html-vault-*` localStorage keys to
  `html-lore-*` keys, without deleting the legacy keys.

### Changed

- Renamed the public product brand from HTMlore's former name to `HTMlore`
  across the app shell, login screen, PWA manifest, Pages site, static demo,
  README, deployment docs, and version metadata.
- Updated the default repository and release-check URLs to
  `JMoCoder/html_lore`.
- Updated package, app, PWA, demo, and homepage cache versions to `0.6.7`.

### Compatibility

- Existing `html_vault` Python imports, `html-vault` CLI commands,
  `HTML_VAULT_*` env variables, `html-vault-*` browser preferences, and
  `html-vault-backup` imports remain supported.

## [0.6.6] - 2026-06-03

### Changed

- Refined the sidebar profile area: the footer avatar now opens a compact user
  status popover with avatar, username, ID, subscription status, and AI credit
  balance instead of navigating away.
- Moved profile management controls into Settings > User profile, made the
  avatar itself the upload target, and aligned sign out on the same profile row.
- Smoothed collapsed sidebar behavior across the main workspace, reader, and
  settings overlays.
- Updated package, app, PWA, demo, and homepage cache versions to `0.6.6`.

## [0.6.5] - 2026-06-03

### Added

- Added file-backed self-hosted multi-user login support through
  `data/users.json`.
- Added per-user persistent notebook partitions under `data/users/<data_id>/`
  for each user's imported/generated HTML, metadata, runtime config, jobs, and
  generated public output.
- Added `html-lore user-add` for creating or replacing self-hosted users
  without storing plaintext passwords.
- Added backend integration coverage for env bootstrap, case-insensitive
  multi-user login, and cross-user upload isolation.

### Changed

- Default env credentials now bootstrap the first admin user into
  `users.json`; that bootstrap admin keeps the existing root notebook data for
  backwards compatibility.
- Updated package, app, PWA, demo, and homepage cache versions to `0.6.5`.

## [0.6.4] - 2026-06-03

### Changed

- Login usernames are now matched case-insensitively while passwords remain
  case-sensitive.
- Login sessions store and return the configured canonical username.
- Updated package, app, PWA, demo, and homepage cache versions to `0.6.4`.

## [0.6.3] - 2026-06-03

### Changed

- Increased the spacing and line stability of the import/create feedback row so
  messages such as `Imported {title}` no longer sit too close to the interaction
  form.
- Updated package, app, PWA, and demo cache versions to `0.6.3`.

## [0.6.2] - 2026-06-03

### Changed

- Promoted the built-in login flow to the stable `0.6.2` release.
- Default Docker now enables local/test login with `admin` / `test-password`
  and a development session secret so fresh deployments open the login screen.
- README and deployment docs now clearly require changing the default username,
  password, and session secret before public access.
- Updated package, app, PWA, demo, and homepage cache versions to `0.6.2`.

## [0.6.0] - 2026-06-03

### Added

- Added a standard login screen as the first workspace view when server-side
  authentication is configured.
- Added `/api/auth/status`, `/api/auth/login`, and `/api/auth/logout` with
  HttpOnly signed session cookies.
- Added environment-configured test-user credentials via
  `HTML_LORE_AUTH_USERNAME`, `HTML_LORE_AUTH_PASSWORD`, and
  `HTML_LORE_SESSION_SECRET`.
- Protected backend APIs, `manifest.json`, and note content files with either
  a valid API token or browser login session.
- Added backend integration tests for login, failed login, API protection, and
  static content protection.

### Changed

- Updated package, app, PWA, demo, and homepage cache versions to `0.6.0`.

## [0.5.3] - 2026-06-03

### Changed

- Changed the default workspace and static demo language fallback to English
  for first-time deployments, while preserving saved user preferences and
  homepage-to-demo language handoff.
- Updated package, app, PWA, demo, and homepage cache versions to `0.5.3`.

## [0.5.2] - 2026-06-03

### Added

- Added Playwright E2E coverage for the static demo layout and workspace logo
  navigation.
- Added configurable `HTML_LORE_PAGES_URL` support so workspace branding can
  open the public GitHub Pages homepage from the real app.

### Changed

- Demo workspace branding now returns to the static Pages homepage instead of
  staying inside the demo workspace.
- Updated package, app, PWA, demo, and homepage cache versions to `0.5.2`.

## [0.5.1] - 2026-06-02

### Added

- Added the GitHub Pages `docs/` static homepage and read-only demo.
- Added direct English, Chinese, and Japanese language switching for the public
  homepage.
- Added language handoff from the homepage to the demo with
  `demo/?lang=zh-CN`, `demo/?lang=en`, and `demo/?lang=ja`.
- Added language-specific demo manifests and full README/CHANGELOG HTML demo
  notes for each supported language.

### Changed

- Kept the demo explicitly static with backend auto-detection disabled.
- Updated demo cache-busting and service worker cache names so stale demo shells
  do not render outdated controls.
- Updated package, app, and PWA cache versions to `0.5.1`.

## [0.5.0] - 2026-06-02

### Changed

- Promoted the project to the first stable self-hosted notebook release.
- Rebuilt the English, Chinese, and Japanese README files around the full
  project vision, implemented 0.5.0 scope, current limits, deployment paths,
  security model, and roadmap.
- Updated package, app, and PWA cache versions to `0.5.0`.

## [0.4.14] - 2026-06-02

### Changed

- Changed the default Docker Compose path to a single-container self-hosted
  notebook deployment that serves both the frontend and `/api/*`.
- Moved Caddy Basic Auth into an optional public deployment example instead of
  requiring it for the default startup path.
- Simplified default Docker environment variables so local and LAN deployments
  can run without a generated `.env` file.

## [0.4.13] - 2026-06-02

### Added

- Added reusable self-hosted Docker deployment assets: `Dockerfile.api`,
  `compose.prod.yml`, `deploy/Caddyfile`, and a backend container entrypoint.
- Added runtime frontend `config.js` support so deployed sites can use
  same-origin API access without embedding backend tokens in browser code.
- Added `.dockerignore` and expanded deployment docs for self-hosted Docker
  startup, updates, backups, and rollback.

### Changed

- The initial production compose path used `compose.prod.yml`; the default
  compose path was later simplified in `0.4.14`.

## [0.4.12] - 2026-06-02

### Added

- Added `GET /api/version` for backend version and repository metadata.
- Settings > About now shows the running version and checks GitHub
  releases/tags for update availability.
- Update checks only show a hint and never auto-update the server.

## [0.4.11] - 2026-06-02

### Added

- Added persistent lightweight backend job records stored in
  `meta/config/jobs.json`.
- Added `POST /api/rebuild` and `GET /api/rebuild/{job_id}` for explicit
  rebuild execution and status lookup.
- Added `GET /api/uploads/{upload_id}` and upload `job_id` responses so HTML
  imports can be queried after completion.
- Added a full core API smoke test covering upload, list, metadata edit,
  search, content read, favorite, archive, unarchive, and permanent delete.
- Localhost frontends now default to `http://127.0.0.1:8787` for the backend
  API, enabling local notebook mode without inline script configuration.
- README now documents real local notebook startup with `data/content`,
  `data/meta`, the API server, and the static web server.
- Added reusable deployment security baseline docs and backend API token/CORS
  configuration for self-hosted production preparation.

## [0.4.10] - 2026-06-02

### Fixed

- Fixed a startup crash when a stale cached HTML shell loaded the newer import
  button script before the hidden import file input existed.
- The PWA service worker now prefers the network for navigation and asset GET
  requests, while keeping cached fallbacks for offline use.
- Updated app and PWA cache version to `0.4.10` so browsers request the fixed
  shell and script instead of reusing stale `0.4.9` assets.

## [0.4.9] - 2026-06-02

### Changed

- Archived item cards and reader pages no longer show metadata edit actions.
- `PATCH /api/items/{id}/metadata` now rejects archived items until they are
  unarchived.
- Archived items still allow favorite toggles, unarchive, and permanent delete.

## [0.4.8] - 2026-06-01

### Added

- Added `GET /api/search` with the same filtering and sorting parameters as
  `GET /api/items`.
- Search responses now include the matched item, score, matched fields, and a
  snippet, creating a stable interface for future Pagefind, SQLite FTS, or cloud
  search backends.
- Added service and real HTTP integration tests for search query, tag OR/AND,
  favorite filtering, Chinese text search, and result metadata.

## [0.4.7] - 2026-06-01

### Added

- Added `GET /api/navigation` and `PUT /api/navigation` for persisting sidebar
  visibility preferences for library views, collections, and tags.
- Navigation visibility settings are stored in `meta/config/navigation.json`.
- The frontend settings management page loads and saves navigation visibility
  through the backend when an Agent Server URL is configured, with local storage
  fallback in static mode.
- Added service and real HTTP integration tests for navigation configuration.

## [0.4.6] - 2026-06-01

### Added

- Added `PATCH /api/items/{id}/state` to persist `favorite` and `archived`
  state to YAML sidecar metadata.
- Favorite and archive buttons now write through the backend when an Agent
  Server URL is configured, with static-mode local overrides kept as fallback.
- Added service and real HTTP integration tests for archive/favorite state
  persistence and archive-view filtering.

## [0.4.5] - 2026-06-01

### Added

- Added `PATCH /api/items/{id}/metadata` to persist note title, summary,
  collection, and tags to YAML sidecar metadata.
- Metadata edits now rebuild `public/` and return the re-indexed item.
- The frontend metadata editor writes through the backend when an Agent Server
  URL is configured, with static-mode local overrides kept as fallback.
- Added service and real HTTP integration tests for metadata persistence.

## [0.4.4] - 2026-06-01

### Added

- Added backend content access endpoints: `GET /api/items/{id}/content` and
  `GET /api/items/{id}/raw`.
- Reader iframe and original-file links now use the backend content API when an
  Agent Server URL is configured, while static mode keeps using local content
  paths.
- Added real HTTP integration tests for item content and raw HTML access.

## [0.4.3] - 2026-06-01

### Added

- Archived item cards now replace the AI context button with a permanent
  delete action.
- Archived reader pages now replace the right-side AI button with a permanent
  delete action.
- Added `DELETE /api/items/{id}` for permanently deleting archived notes from
  `content/` and `meta/`, followed by a rebuild.

## [0.4.2] - 2026-06-01

### Added

- Added HTML import backend support with `POST /api/uploads/html`.
- Imported HTML files are saved under `content/imported/YYYY/MM/`, sidecar
  metadata is written under `meta/items/`, and the static site is rebuilt after
  a successful import.
- Added upload service tests covering HTML import, metadata generation, rebuild,
  and invalid file rejection.

## [0.4.1] - 2026-06-01

### Added

- Added the first backend development slice: optional Agent Server API skeleton,
  `GET /api/health`, `GET /api/manifest`, `GET /api/items`, and
  `GET /api/items/{id}`.
- `GET /api/items` supports current frontend list behavior for library,
  collection, tag OR/AND, favorite/archive, search, sort, and limit filters.
- Added `html-lore serve-api` and service/API tests for the item query layer.

### Fixed

- Updated the builder test expectation to match the current four-item example
  fixture.

## [0.4.0] - 2026-06-01

### Added

- Promoted the current UI to the first formal frontend release.
- Frontend now includes the card workspace, PWA app shell, trilingual UI,
  light/dark theme switching, resizable sidebars, global AI panel scaffold,
  settings modules, local backup/export scaffolds, item favorite/archive
  actions, and local note metadata editing.

### Changed

- Replaced the light-mode theme switch moon with a clearer filled moon-and-star
  icon and added cache-busting resource URLs for the frontend bundle.
- Package, app, and PWA cache version updated to `0.4.0`.

## [0.3.21] - 2026-05-30

### Added

- Item cards and the reader now include an edit metadata button before the
  favorite action.
- A local metadata editor can update note title, summary, collection, and tags
  with Save and Cancel controls. The overrides are stored in browser state and
  are reflected in cards, reader headers, search, filters, counts, sorting, and
  AI context labels.
- Package, app, and PWA cache version updated to `0.3.21`.

## [0.3.20] - 2026-05-30

### Fixed

- AI panel resizing on the reader page now follows the pointer consistently by
  ignoring the reader iframe during drag and calculating width from the actual
  panel boundary.
- Package, app, and PWA cache version updated to `0.3.20`.

## [0.3.19] - 2026-05-30

### Changed

- Collapsed sidebar is narrower and uses a smaller logo mark.
- Top filter popover now filters tags only; collection filtering remains a
  left-navigation action.
- Light/dark theme toggle moved back beside the sidebar Settings button with
  icon-only switching.
- Basic settings now labels the theme area as Theme settings and reserves it
  for future theme-color controls.
- Package, app, and PWA cache version updated to `0.3.19`.

## [0.3.18] - 2026-05-30

### Changed

- Sidebar branding now always shows `HTMlore` and removes the item-count
  subtitle.
- Sidebar and AI-panel resize rails no longer show hover/drag highlight lines.
- Reader actions now use icon buttons for original/copy, keep the AI button on
  the far right, and let that button toggle the AI panel open/closed.
- Reader headers now clamp title, summary, and tags to keep the header height
  stable as the AI panel width changes.
- Package, app, and PWA cache version updated to `0.3.18`.

## [0.3.17] - 2026-05-30

### Changed

- Sidebar scroll indicator now shares the resize rail so the nav labels no
  longer shift when the sidebar is focused.
- Archive is now confirm-first, hidden from collections/tags by default, and
  counted only inside the archived library view while preserving metadata.
- The top toolbar keeps only favorites in the filter/sort group, and the reader
  action row now uses a share button plus a direct AI-panel entry.
- Package, app, and PWA cache version updated to `0.3.17`.

## [0.3.16] - 2026-05-29

### Added

- Top toolbar now has a dedicated colored `+` import button with an HTML import
  tooltip, and the old sidebar import button was removed.
- Library, Collections, and Tags sidebar sections can be collapsed and expanded.
- Reader actions now include add/remove from AI Q&A context and a share button.

### Changed

- Updated the sidebar brand mark to the redesigned HTMlore icon and refined
  brand/collapse-button alignment for light and dark themes.
- Sidebar and page scrollbars now stay hidden until hover or keyboard focus.
- AI-create source selector now uses an inset custom chevron so the arrow no
  longer touches the right border.
- Package, app, and PWA cache version updated to `0.3.16`.

## [0.3.15] - 2026-05-29

### Changed

- Removed the workspace title from the top toolbar to avoid wrapping on
  smaller screens with side panels open.
- Removed the view-mode toggle and forced the workspace to stay in card view.
- Top toolbar now groups the five control buttons separately from the
  search/AI group, allowing the search/AI group to wrap together when narrow.
- AI panel generation action now reads "Generate note".
- Package, app, and PWA cache version updated to `0.3.15`.

## [0.3.14] - 2026-05-29

### Added

- GitHub sidebar link now includes the GitHub mark.
- Basic settings theme control now offers System, Light, and Dark modes.

### Changed

- Theme preference now stores the selected mode and resolves System from the
  browser color-scheme preference.
- Package, app, and PWA cache version updated to `0.3.14`.

## [0.3.13] - 2026-05-29

### Added

- GitHub repository link in the lower-right side of the sidebar footer.
- Basic settings section for interface theme and language preferences.

### Changed

- Sidebar footer now keeps Settings on the left and removes theme/language
  controls from the persistent navigation.
- User-related settings now appear first: Basic settings, User profile, and
  Account & security.
- Package, app, and PWA cache version updated to `0.3.13`.

## [0.3.12] - 2026-05-29

### Changed

- Top toolbar grouping now pairs filter with sort, and favorite with archive.
- Verified OR/AND tag filtering against MCP and Docker sample notes: OR returns
  any matching tag, while AND requires all selected tags.
- Package, app, and PWA cache version updated to `0.3.12`.

## [0.3.11] - 2026-05-29

### Changed

- Opening the AI panel no longer changes the top toolbar into a wrapped
  multi-row layout.
- The global AI button remains visible to the right of search while the panel
  is open, preserving the search/AI button relationship.
- Package, app, and PWA cache version updated to `0.3.11`.

## [0.3.10] - 2026-05-29

### Changed

- Manual AI context card action now changes from plus to minus when selected
  while keeping the active icon color.
- Filter and sort toolbar controls are separated into independent groups again.
- Tag match controls now use OR/AND wording, matching the underlying any/all
  tag filter logic.
- Package, app, and PWA cache version updated to `0.3.10`.

## [0.3.9] - 2026-05-29

### Changed

- Card metadata now stays in the upper-left top row beside the card action
  icons, while titles start on the next row.
- List view layout separates action icons, read/original buttons, and date to
  prevent overlap.
- The AI panel now slides out from the right edge and uses the same resize
  highlight behavior as the left sidebar.
- Package, app, and PWA cache version updated to `0.3.9`.

## [0.3.8] - 2026-05-29

### Added

- Card actions now include an add-to-Q&A-context button for manually selecting
  multiple files as the AI context.

### Changed

- Manual AI context selections now override the default page, reader, and
  filter-derived context labels.
- The top AI button hides while the AI panel is open, leaving the panel close
  button as the single close control.
- Filter and sort buttons now share one toolbar group.
- Package, app, and PWA cache version updated to `0.3.8`.

## [0.3.7] - 2026-05-29

### Changed

- Sidebar resize handle no longer creates a horizontal scrollbar.
- Multi-filter popover now uses the header area for Any/All tag match controls.
- Card action buttons no longer reserve a top layout row, keeping collection,
  source, and date visually anchored in the lower-left area.
- Package, app, and PWA cache version updated to `0.3.7`.

## [0.3.6] - 2026-05-29

### Added

- User profile and account/security placeholder sections in settings.

### Changed

- Filter and sort toolbar controls are now visually separated.
- Card metadata now shows collection/source and date in the lower-left area,
  while favorite/archive actions stay in the upper-right.
- Source labels are normalized to generated/imported system labels.
- Removed the Needs Review library view; notes are categorized by source
  instead of a review queue.
- Settings title now reads simply as Settings, and data settings appear before
  AI settings.
- Package, app, and PWA cache version updated to `0.3.6`.

## [0.3.5] - 2026-05-29

### Added

- Tag multi-select filters now support Any and All match modes.
- Added an example note with both MCP and Docker tags for combined-tag
  filtering coverage.

### Changed

- Library navigation clears collection/tag multi-select limits, treating
  library views as all collections and all tags within that library.
- The multi-filter "All" action now resets collection/tag limits.
- Package, app, and PWA cache version updated to `0.3.5`.

## [0.3.4] - 2026-05-29

### Added

- Sort menu in the result filter group for newest, oldest, title A-Z, and
  title Z-A ordering of the current view.

### Changed

- Package, app, and PWA cache version updated to `0.3.4`.

## [0.3.3] - 2026-05-29

### Added

- Resizable left sidebar width with local persistence.
- Multi-select collection and tag filter popover in the top toolbar, including
  a clear-all action.
- AI context labels now include library views, favorite-only state, archive
  visibility state, and active multi-select filters.

### Changed

- Clicking a collection or tag while multi-select filters are active now syncs
  the matching multi-select group.
- Package, app, and PWA cache version updated to `0.3.3`.

## [0.3.2] - 2026-05-29

### Added

- Global AI assistant button beside search.
- Resizable right AI sidebar with context labels for all notes, collection,
  tag, search, and reader states.
- Placeholder chat and HTML note generation actions for the future Agent
  Server.

### Changed

- Multi-turn knowledge conversation planning moved out of settings and into
  the global AI sidebar.
- Package, app, and PWA cache version updated to `0.3.2`.

## [0.3.1] - 2026-05-29

### Changed

- Compact list-view rows by moving the read/original actions up to align with the tag row.
- Package, app, and PWA cache version updated to `0.3.1`.

## [0.3.0] - 2026-05-29

### Added

- Favorite-only toolbar filter beside the archive filter.
- Archive filter now starts enabled so archived items are excluded by default.

### Changed

- Archive filter tooltip now reads as an action to show archived items while the filter is active.
- Toolbar filters use icon color for state instead of adding a highlighted frame.
- Package, app, and PWA cache version updated to `0.3.0`.

## [0.1.0] - 2026-05-29

### Added

- Initial static-first HTMlore MVP.
- Manifest v2 builder for HTML knowledge items.
- Sidecar YAML metadata support.
- Karakeep-style card workspace with sidebar filters.
- Static reader pane with iframe and original-open actions.
- New knowledge item entry card with optional Agent API handoff.
- Example content, tests, Docker static image, README, MIT license.

## [0.2.0] - 2026-05-29

### Added

- Extensible frontend i18n dictionary.
- Language selector for Chinese, English, and Japanese system UI labels.
- Persistent language preference via `localStorage`.
- Dark and light theme toggle with a compact icon control.
- Settings page with AI provider configuration, user agreement, about, and
  update documentation sections.
- Collection and tag management sections with sidebar visibility controls and
  disabled structural actions for future metadata writing.
- Library management section for fixed system view visibility.
- AI knowledge assistant placeholder with operation selection, prompt input,
  and a second confirmation before future database-impacting jobs.
- Global AI sidebar placeholder for future multi-turn conversations over
  knowledge base files.
- Magic-wand "I'm feeling lucky" action for opening a random matching item.
- Archived library view for future archive workflows.
- Favorite and archive icon actions on cards and in the reader.
- Card/list workspace view toggle.
- Separate data settings group for local backup and restore, automatic backup
  snapshots, WebDAV settings, and JSON exports.
- PWA manifest and service worker for browser installation and app-shell
  caching.
- Toolbar archive filter for excluding archived items from the current result
  view.

### Changed

- System UI copy is now rendered from translation keys while user-created
  content such as item titles, collections, and tags remains unchanged.
- Language selection now lives at the bottom of the sidebar.
- API keys are explicitly excluded from browser storage; static mode only saves
  non-sensitive AI model preferences.
- Settings header icon buttons are grid-centered for consistent visual
  alignment.
- AI provider settings are visually separated from sidebar management and
  project information sections.
- Sidebar import entry is separated from the AI creation entry.
- Logo and sidebar navigation now consistently return from settings or reader
  overlays to the main workspace.
- Manifest items now include an `archived` metadata flag.
- Card and list layouts now reserve stable areas for title, summary, tags, and
  actions so long summaries truncate instead of hiding controls.
