const { expect, test } = require("@playwright/test");
const fs = require("fs");
const path = require("path");

function appStaticFile(name) {
  return path.join(__dirname, "../../app_static", name);
}

async function routeWorkspace(page) {
  await page.route("**/workspace/", async (route) => {
    await route.fulfill({
      contentType: "text/html",
      body: fs.readFileSync(appStaticFile("index.html"), "utf8"),
    });
  });
  await page.route("**/config.js", async (route) => {
    await route.fulfill({
      contentType: "application/javascript",
      body: 'window.HTML_LORE_AGENT_URL = "http://127.0.0.1:8090";',
    });
  });
  await page.route("**/app.js**", async (route) => {
    await route.fulfill({
      contentType: "application/javascript",
      body: fs.readFileSync(appStaticFile("app.js"), "utf8"),
    });
  });
  await page.route("**/style.css**", async (route) => {
    await route.fulfill({
      contentType: "text/css",
      body: fs.readFileSync(appStaticFile("style.css"), "utf8"),
    });
  });
  await page.route("**/assets/html-lore-logo.svg", async (route) => {
    await route.fulfill({
      contentType: "image/svg+xml",
      body: fs.readFileSync(appStaticFile("assets/html-lore-logo.svg"), "utf8"),
    });
  });
  await page.route("**/manifest.webmanifest", async (route) => {
    await route.fulfill({ contentType: "application/manifest+json", body: "{}" });
  });
}

test("workspace file create mode uploads material to the AI generation endpoint", async ({ page }) => {
  await page.addInitScript(() => localStorage.clear());
  await routeWorkspace(page);

  let materialRequest = null;
  let uploadHtmlCalled = false;
  let legacyJobCalled = false;
  let manifestCalls = 0;
  const generatedRun = {
    id: "run-material-test",
    kind: "material_html_generation",
    status: "completed",
    started_at: "2026-06-07T02:00:00.000Z",
    completed_at: "2026-06-07T02:00:01.250Z",
    duration_ms: 1250,
    retryable: false,
    cancellable: false,
    item_id: "generated/2026/06/material-note.html",
    node_trace: [
      { node: "MaterialParseNode", status: "ok" },
      { node: "ContentBriefNode", status: "ok" },
      { node: "ReviewerNode", status: "ok" },
    ],
    material: { title: "material", material_type: "markdown", text_chars: 36 },
  };
  const refreshedRun = {
    id: "run-qa-refresh-test",
    kind: "knowledge_qa",
    status: "completed",
    started_at: "2026-06-07T02:05:00.000Z",
    completed_at: "2026-06-07T02:05:00.640Z",
    duration_ms: 640,
    retryable: false,
    cancellable: false,
    source_mode: "local_only",
    local_sources: { count: 1 },
    external_sources: { count: 0, enabled: false, status: "skipped" },
    node_trace: [
      { node: "RetrieverNode", status: "ok" },
      { node: "AnswerAgentNode", status: "ok" },
    ],
    spec: { source_mode: "local_only" },
    usage: { input_tokens: 120, output_tokens: 80, total_tokens: 200 },
    budget: { message_chars: 24, max_message_chars: 4000, prompt_chars: 1300, max_prompt_chars: 12000, max_response_tokens: 1024 },
  };
  const manifestBefore = {
    version: 2,
    title: "HTMlore Workspace",
    items: [],
  };
  const manifestAfter = {
    version: 2,
    title: "HTMlore Workspace",
    items: [
      {
        id: "generated/2026/06/material-note.html",
        title: "Generated Material Note",
        summary: "Generated from uploaded material.",
        collection: "Generated",
        tags: ["AI"],
        source: "generated",
        created: "2026-06-07T00:00:00Z",
        updated: "2026-06-07T00:00:00Z",
        path: "content/generated/2026/06/material-note.html",
      },
    ],
  };
  let runsRequested = 0;
  let showRefreshedRun = false;
  let jobsRequested = 0;
  let failedJobRetried = false;

  await page.route("**/api/auth/status", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ enabled: false, authenticated: true, user: null, data_id: null }),
    });
  });
  await page.route("**/api/ai/status", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ available: false, provider: "", model: "", external_search: false }),
    });
  });
  await page.route("**/api/version", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ version: "0.9.0", latest_version: "0.9.0", update_available: false }),
    });
  });
  await page.route("**/api/shares", async (route) => {
    await route.fulfill({ contentType: "application/json", body: JSON.stringify({ shares: [], count: 0 }) });
  });
  await page.route("**/api/ai/runs**", async (route) => {
    const pathname = new URL(route.request().url()).pathname;
    if (pathname.endsWith(`/api/ai/runs/${refreshedRun.id}`)) {
      await route.fulfill({
        contentType: "application/json",
        body: JSON.stringify({
          run: {
            ...refreshedRun,
            unsafe_private_prompt: "Important uploaded source should stay hidden",
          },
        }),
      });
      return;
    }
    runsRequested += 1;
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        runs: showRefreshedRun ? [refreshedRun, generatedRun] : [generatedRun],
        count: showRefreshedRun ? 2 : 1,
      }),
    });
  });
  await page.route("**/api/manifest", async (route) => {
    manifestCalls += 1;
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify(manifestCalls > 1 ? manifestAfter : manifestBefore),
    });
  });
  await page.route("**/api/uploads/html", async (route) => {
    uploadHtmlCalled = true;
    await route.abort();
  });
  await page.route("**/api/jobs", async (route) => {
    legacyJobCalled = true;
    await route.abort();
  });
  await page.route("**/api/ai/jobs**", async (route) => {
    if (route.request().method() === "POST" && route.request().url().includes("/retry")) {
      failedJobRetried = true;
      await route.fulfill({
        contentType: "application/json",
        body: JSON.stringify({
          job_id: "ai-job-failed-retry",
          job: {
            job_id: "ai-job-failed-retry",
            kind: "html_generation",
            status: "pending",
            label: "Failed note",
            cancellable: true,
            retryable: false,
            attempts: 1,
          },
        }),
      });
      return;
    }
    jobsRequested += 1;
    const completed = jobsRequested > 1;
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        jobs: [
          {
            job_id: "ai-job-failed-retry",
            kind: "html_generation",
            status: failedJobRetried ? "pending" : "failed",
            label: "Failed note",
            retryable: !failedJobRetried,
            cancellable: failedJobRetried,
            created_at: "2026-06-07T01:00:00.000Z",
            updated_at: "2026-06-07T01:01:00.000Z",
            error: failedJobRetried ? {} : { message: "Provider failed." },
          },
          {
            job_id: "ai-job-material-test",
            kind: "material_html_generation",
            status: completed ? "completed" : "pending",
            label: "material.md",
            generation_engine: "v2",
            current_stage: completed ? "writing_file" : "designing_style",
            stage_trace: [
              { stage: "parsing", agent: "Ingest", status: "completed", message: "Uploaded material parsed." },
              { stage: "designing_style", agent: "StyleDesigner", status: completed ? "completed" : "running", message: "Style direction prepared." },
            ],
            execution_checklist: [
              { id: "parse", label: "Parse uploaded material", status: "completed" },
              { id: "style", label: "Prepare visual direction", status: completed ? "completed" : "running" },
            ],
            skill_trace: [
              { id: "html_page_design", title: "HTML page design", agent: "StyleDesigner", version: "1" },
            ],
            agent_artifacts: [
              {
                agent: "Planner",
                stage: "planning",
                title: "Plan",
                summary: "Create a concise material note.",
                data: { page_goal: "Study note", section_plan: [{ title: "Overview" }, { title: "Takeaways" }] },
              },
              {
                agent: "HTMLCoder",
                stage: "coding_html",
                title: "HTML draft",
                summary: "2048 chars, static HTML",
                data: { html_chars: 2048, has_doctype: true, has_style: true, has_script: false },
              },
            ],
            run_id: completed ? generatedRun.id : "",
            item_id: completed ? "generated/2026/06/material-note.html" : "",
            cancellable: !completed,
            retryable: false,
            message: completed ? "AI job completed." : "",
            created_at: "2026-06-07T02:00:00.000Z",
            completed_at: completed ? "2026-06-07T02:02:00.000Z" : "",
          },
        ],
        count: 2,
      }),
    });
  });
  await page.route("**/api/ai/material-jobs", async (route) => {
    materialRequest = {
      method: route.request().method(),
      postData: route.request().postData() || "",
    };
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        job_id: "ai-job-material-test",
        job: {
          job_id: "ai-job-material-test",
          kind: "material_html_generation",
          status: "pending",
          label: "material.md",
          cancellable: true,
        },
      }),
    });
  });

  await page.goto("/workspace/", { waitUntil: "domcontentloaded" });
  await page.locator("#new-item-input").fill("Turn this material into a concise study note.");
  await expect(page.locator("#new-generation-options")).toBeHidden();
  await page.locator("#new-generation-toggle").click();
  await expect(page.locator("#new-generation-options")).toBeVisible();
  await page.locator("#new-generate-theme").selectOption("dark");
  await page.locator("#new-generate-target-use").selectOption("ppt");
  await page.locator("#new-generate-style-preference").selectOption("tech");
  await page.locator("#new-generate-audience").selectOption("share");
  const referenceChooserPromise = page.waitForEvent("filechooser");
  await page.locator("#new-reference-trigger").click();
  const referenceChooser = await referenceChooserPromise;
  await referenceChooser.setFiles({
    name: "style-reference.pdf",
    mimeType: "application/pdf",
    buffer: Buffer.from("%PDF-1.4 style reference", "utf8"),
  });
  await expect(page.locator("#new-reference-name")).toContainText("style-reference.pdf");
  await expect(page.locator("#new-reference-trigger")).toHaveClass(/has-file/);

  const fileChooserPromise = page.waitForEvent("filechooser");
  await page.locator("#new-file-trigger").click();
  const fileChooser = await fileChooserPromise;
  await fileChooser.setFiles({
    name: "material.md",
    mimeType: "text/markdown",
    buffer: Buffer.from("# Material\n\nImportant uploaded source.", "utf8"),
  });
  await expect(page.locator("#new-file-name")).toContainText("material.md");
  await expect(page.locator("#new-file-trigger")).toHaveClass(/has-file/);
  await page.locator("#new-item-form button[type='submit']").click();

  await expect(page.locator("#new-feedback")).toContainText("Queued job ai-job-material-test");
  await expect(page.locator(".item-card", { hasText: "Generated Material Note" })).toBeVisible();
  expect(uploadHtmlCalled).toBe(false);
  expect(legacyJobCalled).toBe(false);
  expect(materialRequest).not.toBeNull();
  expect(materialRequest.method).toBe("POST");
  expect(materialRequest.postData).toContain("material.md");
  expect(materialRequest.postData).toContain("Turn this material into a concise study note.");
  expect(materialRequest.postData).toContain("name=\"theme\"");
  expect(materialRequest.postData).toContain("dark");
  expect(materialRequest.postData).toContain("name=\"target_use\"");
  expect(materialRequest.postData).toContain("ppt");
  expect(materialRequest.postData).toContain("name=\"style_preference\"");
  expect(materialRequest.postData).toContain("tech");
  expect(materialRequest.postData).toContain("name=\"audience\"");
  expect(materialRequest.postData).toContain("share");
  expect(materialRequest.postData).toContain("name=\"reference_style\"");
  expect(materialRequest.postData).toContain("file");
  expect(materialRequest.postData).toContain("name=\"reference_file\"");
  expect(materialRequest.postData).toContain("style-reference.pdf");
  expect(materialRequest.postData).toContain("name=\"reference_file_name\"");
  await page.locator("#ai-job-toggle").click();
  await expect(page.locator("#ai-job-list")).toContainText("Generation history");
  await expect(page.locator("#ai-job-list")).toContainText("Failed note");
  await expect(page.locator("#ai-job-list")).toContainText("material.md");
  await expect(page.locator("#ai-job-list")).not.toContainText("Process");
  await expect(page.locator("#ai-job-list")).not.toContainText("Agent outputs");
  await expect(page.locator("#ai-job-list")).not.toContainText("HTML draft");
  await expect(page.locator("#ai-job-list")).not.toContainText("completed");
  await expect(page.locator("#ai-chat-log")).not.toContainText("AI job completed");
  await expect(page.locator("#ai-job-list").getByRole("button", { name: "Retry" })).toBeVisible();
  await page.locator("#ai-job-list").getByRole("button", { name: "Retry" }).click();
  await expect(page.locator("#ai-chat-log")).toContainText("Retrying AI job");
  await page.locator("#ai-job-list .ai-job-row", { hasText: "material.md" }).getByRole("button", { name: "Details" }).click();
  await expect(page.locator("[data-settings-tab='ai-generation-history']")).toHaveClass(/active/);
  await expect(page.locator("[data-settings-section='ai-generation-history']")).toHaveClass(/active/);
  await expect(page.locator("[data-settings-section='ai-generation-history']")).toContainText("AI generation history");
  await expect(page.locator("#ai-generation-list")).toContainText("material.md");
  await expect(page.locator("#ai-generation-list")).toContainText("Failed note");
  await page.locator("#ai-generation-list .ai-generation-row", { hasText: "material.md" }).getByRole("button", { name: "Details" }).click();
  await expect(page.locator("#ai-generation-detail")).toBeVisible();
  await expect(page.locator("#ai-generation-detail")).toContainText("LangGraph workflow");
  await expect(page.locator("#ai-generation-detail")).toContainText("StyleDesigner");
  await page.locator("#ai-generation-detail-close").click();
  await expect(page.locator("#ai-generation-detail")).toBeHidden();
  await page.locator("[data-settings-tab='ai-runs']").click();
  await expect(page.locator("#ai-run-list")).toContainText("Generated from uploaded material");
  await expect(page.locator("#ai-run-list")).toContainText("Completed");
  await expect(page.locator("#ai-run-list")).toContainText("1.3s");
  await expect(page.locator("#ai-run-list")).toContainText("Generated:");
  await expect(page.locator("#ai-run-list")).toContainText("3 steps");
  await expect(page.locator("#ai-run-list")).toContainText("Not cancellable");
  await expect(page.locator("#ai-run-list")).not.toContainText("Important uploaded source should stay hidden");
});

test("workspace material generation failure refreshes AI run history", async ({ page }) => {
  await page.addInitScript(() => localStorage.clear());
  await routeWorkspace(page);

  const failedRun = {
    id: "run-material-failed",
    kind: "material_html_generation",
    status: "failed",
    started_at: "2026-06-07T03:00:00.000Z",
    completed_at: "2026-06-07T03:00:00.080Z",
    duration_ms: 80,
    retryable: true,
    cancellable: false,
    item_id: "",
    node_trace: [{ node: "MaterialParseNode", status: "failed" }],
    error: { code: "material_parse_failed", message: "Only HTML, Markdown, and plain text materials are supported in this beta." },
    material: { title: "private source", material_type: "unknown", text_chars: 0 },
  };
  let runsRequested = 0;

  await page.route("**/api/auth/status", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ enabled: false, authenticated: true, user: null, data_id: null }),
    });
  });
  await page.route("**/api/ai/status", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ available: false, provider: "", model: "", external_search: false }),
    });
  });
  await page.route("**/api/version", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ version: "0.9.0", latest_version: "0.9.0", update_available: false }),
    });
  });
  await page.route("**/api/shares", async (route) => {
    await route.fulfill({ contentType: "application/json", body: JSON.stringify({ shares: [], count: 0 }) });
  });
  await page.route("**/api/manifest", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ version: 2, title: "HTMlore Workspace", items: [] }),
    });
  });
  await page.route("**/api/ai/runs**", async (route) => {
    runsRequested += 1;
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ runs: [failedRun], count: 1 }),
    });
  });
  await page.route("**/api/ai/jobs**", async (route) => {
    await route.fulfill({ contentType: "application/json", body: JSON.stringify({ jobs: [], count: 0 }) });
  });
  await page.route("**/api/ai/material-jobs", async (route) => {
    await route.fulfill({
      status: 400,
      contentType: "application/json",
      body: JSON.stringify({ detail: "Only HTML, Markdown, and plain text materials are supported in this beta." }),
    });
  });

  await page.goto("/workspace/", { waitUntil: "domcontentloaded" });
  await page.locator("#new-item-input").fill("Turn this private source into a note.");

  const fileChooserPromise = page.waitForEvent("filechooser");
  await page.locator("#new-file-trigger").click();
  const fileChooser = await fileChooserPromise;
  await fileChooser.setFiles({
    name: "private-source.pdf",
    mimeType: "application/pdf",
    buffer: Buffer.from("%PDF private uploaded source text", "utf8"),
  });
  await expect(page.locator("#new-file-name")).toContainText("private-source.pdf");
  await page.locator("#new-item-form button[type='submit']").click();

  await expect(page.locator("#new-feedback")).toContainText("Material note generation failed.");

  await page.locator("#settings-open").click();
  await page.locator("[data-settings-tab='ai-generation-history']").click();
  await expect(page.locator("#ai-generation-list")).toContainText("No generation history yet.");
  await page.locator("[data-settings-tab='ai-runs']").click();
  await expect(page.locator("#ai-run-list")).toContainText("Generated from uploaded material");
  await expect(page.locator("#ai-run-list")).toContainText("Failed");
  await expect(page.locator("#ai-run-list")).toContainText("80ms");
  await expect(page.locator("#ai-run-list")).toContainText("Retryable");
  await expect(page.locator("#ai-run-list")).toContainText("Not cancellable");
  await expect(page.locator("#ai-run-list")).not.toContainText("private source");
});

test("workspace text-only create mode uses the AI generation endpoint", async ({ page }) => {
  await page.addInitScript(() => localStorage.clear());
  await routeWorkspace(page);

  let materialRequest = null;
  let legacyJobCalled = false;
  await page.route("**/api/auth/status", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ enabled: false, authenticated: true, user: null, data_id: null }),
    });
  });
  await page.route("**/api/ai/status", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ available: true, provider: "fake", model: "fake", external_search: false }),
    });
  });
  await page.route("**/api/version", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ version: "0.9.0", latest_version: "0.9.0", update_available: false }),
    });
  });
  await page.route("**/api/shares", async (route) => {
    await route.fulfill({ contentType: "application/json", body: JSON.stringify({ shares: [], count: 0 }) });
  });
  await page.route("**/api/manifest", async (route) => {
    await route.fulfill({ contentType: "application/json", body: JSON.stringify({ version: 2, title: "HTMlore Workspace", items: [] }) });
  });
  await page.route("**/api/ai/runs**", async (route) => {
    await route.fulfill({ contentType: "application/json", body: JSON.stringify({ runs: [], count: 0 }) });
  });
  await page.route("**/api/ai/jobs**", async (route) => {
    await route.fulfill({ contentType: "application/json", body: JSON.stringify({ jobs: [], count: 0 }) });
  });
  await page.route("**/api/jobs", async (route) => {
    legacyJobCalled = true;
    await route.abort();
  });
  await page.route("**/api/ai/material-jobs", async (route) => {
    materialRequest = {
      method: route.request().method(),
      postData: route.request().postData() || "",
    };
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        job_id: "ai-job-text-only",
        job: {
          job_id: "ai-job-text-only",
          kind: "material_html_generation",
          status: "pending",
          label: "prompt.txt",
          cancellable: true,
        },
      }),
    });
  });

  await page.goto("/workspace/", { waitUntil: "domcontentloaded" });
  await expect(page.locator("#input-type")).toHaveCount(0);
  await expect(page.locator("#new-item-input")).toHaveAttribute("placeholder", "Describe what you want to generate");
  await page.locator("#new-item-input").fill("Create an HTML page about virtual power plants.");
  await page.locator("#new-item-form button[type='submit']").click();

  await expect(page.locator("#new-feedback")).toContainText("Queued job ai-job-text-only");
  expect(legacyJobCalled).toBe(false);
  expect(materialRequest).not.toBeNull();
  expect(materialRequest.method).toBe("POST");
  expect(materialRequest.postData).toContain("Create an HTML page about virtual power plants.");
  expect(materialRequest.postData).not.toContain('name="file"');
});

test("workspace note generation sends target format and style preference", async ({ page }) => {
  await page.addInitScript(() => localStorage.clear());
  await routeWorkspace(page);

  let conversationRequest = null;
  let generationRequest = null;
  const manifest = {
    version: 2,
    title: "HTMlore Workspace",
    items: [
      {
        id: "mcp.html",
        title: "MCP Security",
        summary: "Context note.",
        collection: "AI",
        tags: ["MCP"],
        source: "imported",
        created: "2026-06-07T00:00:00Z",
        updated: "2026-06-07T00:00:00Z",
        path: "content/mcp.html",
      },
      {
        id: "style.html",
        title: "Style Reference",
        summary: "Reference style note.",
        collection: "Design",
        tags: ["Style"],
        source: "imported",
        created: "2026-06-07T00:00:00Z",
        updated: "2026-06-07T00:00:00Z",
        path: "content/style.html",
      },
      {
        id: "archived-style.html",
        title: "Archived Style",
        summary: "Should not be offered.",
        collection: "Archive",
        tags: ["Style"],
        source: "imported",
        archived: true,
        created: "2026-06-07T00:00:00Z",
        updated: "2026-06-07T00:00:00Z",
        path: "content/archived-style.html",
      },
    ],
  };

  await page.route("**/api/auth/status", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ enabled: false, authenticated: true, user: null, data_id: null }),
    });
  });
  await page.route("**/api/ai/status", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ available: true, provider: "", model: "fake", external_search: false }),
    });
  });
  await page.route("**/api/version", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ version: "0.9.0", latest_version: "0.9.0", update_available: false }),
    });
  });
  await page.route("**/api/shares", async (route) => {
    await route.fulfill({ contentType: "application/json", body: JSON.stringify({ shares: [], count: 0 }) });
  });
  await page.route("**/api/manifest", async (route) => {
    await route.fulfill({ contentType: "application/json", body: JSON.stringify(manifest) });
  });
  await page.route("**/api/ai/runs**", async (route) => {
    await route.fulfill({ contentType: "application/json", body: JSON.stringify({ runs: [], count: 0 }) });
  });
  await page.route("**/api/ai/jobs**", async (route) => {
    await route.fulfill({ contentType: "application/json", body: JSON.stringify({ jobs: [], count: 0 }) });
  });
  await page.route("**/api/ai/conversations/latest**", async (route) => {
    await route.fulfill({ contentType: "application/json", body: JSON.stringify({ conversation: null }) });
  });
  await page.route("**/api/ai/conversations", async (route) => {
    conversationRequest = JSON.parse(route.request().postData() || "{}");
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ conversation: { id: "conversation-reference-test", context_snapshot: conversationRequest.context, messages: [] } }),
    });
  });
  await page.route("**/api/ai/conversations/*/generate-note/jobs", async (route) => {
    generationRequest = JSON.parse(route.request().postData() || "{}");
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        job_id: "ai-job-reference-test",
        job: {
          job_id: "ai-job-reference-test",
          kind: "html_generation",
          status: "pending",
          label: "Generate reference note",
          cancellable: true,
        },
      }),
    });
  });

  await page.goto("/workspace/", { waitUntil: "domcontentloaded" });
  await page.locator("#ai-panel-open").click();
  await page.locator("#ai-generate-note").click();
  await expect(page.locator("#generate-reference-file")).toHaveCount(0);
  await page.locator("#generate-target-use").selectOption("website");
  await page.locator("#generate-audience").selectOption("personal");
  await page.locator("#generate-style-preference").selectOption("business");
  await page.locator("#generate-note-submit").click();

  await expect(page.locator("#generate-note-feedback")).toContainText("AI job queued: ai-job-reference-test");
  await expect(page.locator("#ai-chat-log")).not.toContainText("AI job queued");
  expect(conversationRequest).not.toBeNull();
  expect(generationRequest).toMatchObject({
    target_use: "website",
    audience: "personal",
    style_preference: "business",
  });
  expect(generationRequest.reference_style).toBeUndefined();
  expect(generationRequest.reference_file_name).toBeUndefined();
});

test("workspace AI content expansion controls conversation source mode", async ({ page }) => {
  await page.addInitScript(() => localStorage.clear());
  await routeWorkspace(page);

  const conversationRequests = [];
  const messageRequests = [];
  const manifest = {
    version: 2,
    title: "HTMlore Workspace",
    items: [
      {
        id: "mcp.html",
        title: "MCP Security",
        summary: "Context note.",
        collection: "AI",
        tags: ["MCP"],
        source: "imported",
        created: "2026-06-07T00:00:00Z",
        updated: "2026-06-07T00:00:00Z",
        path: "content/mcp.html",
      },
    ],
  };

  await page.route("**/api/auth/status", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ enabled: false, authenticated: true, user: null, data_id: null }),
    });
  });
  await page.route("**/api/ai/status", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ available: true, provider: "", model: "fake", external_search: true }),
    });
  });
  await page.route("**/api/version", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ version: "0.9.0", latest_version: "0.9.0", update_available: false }),
    });
  });
  await page.route("**/api/shares", async (route) => {
    await route.fulfill({ contentType: "application/json", body: JSON.stringify({ shares: [], count: 0 }) });
  });
  await page.route("**/api/manifest", async (route) => {
    await route.fulfill({ contentType: "application/json", body: JSON.stringify(manifest) });
  });
  await page.route("**/api/ai/runs**", async (route) => {
    await route.fulfill({ contentType: "application/json", body: JSON.stringify({ runs: [], count: 0 }) });
  });
  await page.route("**/api/ai/jobs**", async (route) => {
    await route.fulfill({ contentType: "application/json", body: JSON.stringify({ jobs: [], count: 0 }) });
  });
  await page.route("**/api/ai/conversations/latest**", async (route) => {
    await route.fulfill({ contentType: "application/json", body: JSON.stringify({ conversation: null }) });
  });
  await page.route("**/api/ai/conversations", async (route) => {
    const request = JSON.parse(route.request().postData() || "{}");
    conversationRequests.push(request);
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ conversation: { id: `conversation-${conversationRequests.length}`, context_snapshot: request.context, messages: [] } }),
    });
  });
  await page.route("**/api/ai/conversations/*/messages", async (route) => {
    if (route.request().method() === "POST") {
      messageRequests.push(JSON.parse(route.request().postData() || "{}"));
    }
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        message: { role: "assistant", content: "Answer from selected mode." },
        sources: [
          { kind: "local", title: "MCP Security", item_id: "mcp.html" },
          { kind: "external", title: "External MCP reference", url: "https://example.test/search?q=mcp" },
        ],
        qa_status: {
          status: "needs_attention",
          requires_attention: true,
          flags: ["missing_citation"],
          citation_status: "missing_citation",
          source_count: 2,
        },
        external_status: { provider: "fake", available: true, count: 1 },
      }),
    });
  });

  await page.goto("/workspace/", { waitUntil: "domcontentloaded" });
  await page.locator("#ai-panel-open").click();
  await expect(page.locator("#ai-deep-research")).toBeDisabled();
  await expect(page.locator(".ai-source-toggle-disabled")).toContainText("Research");
  await page.locator("#ai-content-expansion").check();
  await page.locator("#ai-chat-input").fill("Expand this note.");
  await page.locator("#ai-chat-form button[type='submit']").click();
  await expect.poll(() => conversationRequests.length).toBe(1);
  expect(conversationRequests[0].source_mode).toBe("local_plus_external");
  await expect.poll(() => messageRequests.length).toBe(1);
  expect(messageRequests[0].source_mode).toBe("local_plus_external");
  await expect(page.locator(".ai-message-sources")).toContainText("Local");
  await expect(page.locator(".ai-message-sources")).toContainText("External");
  await expect(page.locator(".ai-message-sources")).toContainText("example.test");
  await expect(page.locator(".ai-message-sources a.external")).toHaveAttribute("href", "https://example.test/search?q=mcp");

  await page.locator("#ai-content-expansion").uncheck();
  await page.locator("#ai-chat-input").fill("Answer only from local notes.");
  await page.locator("#ai-chat-form button[type='submit']").click();
  await expect.poll(() => messageRequests.length).toBe(2);
  expect(conversationRequests.length).toBe(1);
  expect(messageRequests[1].source_mode).toBe("local_only");
});

test("workspace AI restores latest context conversation and can start a fresh one", async ({ page }) => {
  await page.addInitScript(() => localStorage.clear());
  await routeWorkspace(page);

  const manifest = {
    version: 2,
    title: "HTMlore Workspace",
    items: [
      {
        id: "notes/mcp.html",
        title: "MCP Security",
        summary: "Security notes for MCP.",
        collection: "AI",
        tags: ["MCP", "Security"],
        source: "imported",
        created: "2026-06-07T00:00:00Z",
        updated: "2026-06-07T00:00:00Z",
        path: "content/notes/mcp.html",
      },
      {
        id: "notes/docker.html",
        title: "Docker Notes",
        summary: "Container notes.",
        collection: "Ops",
        tags: ["Docker"],
        source: "imported",
        created: "2026-06-07T00:00:00Z",
        updated: "2026-06-07T00:00:00Z",
        path: "content/notes/docker.html",
      },
    ],
  };
  const oldConversation = {
    id: "conversation-old",
    title: "MCP Security",
    context_key: 'reader:{"item_id":"notes/mcp.html"}',
    context_snapshot: {
      scope: "reader",
      item_ids: ["notes/mcp.html"],
      items: [{ id: "notes/mcp.html", title: "MCP Security" }],
      requested: { item_id: "notes/mcp.html" },
    },
    message_count: 2,
    created_at: "2026-06-07T01:00:00.000Z",
    updated_at: "2026-06-07T01:05:00.000Z",
  };
  const historyConversation = {
    id: "conversation-history",
    title: "Docker Notes",
    context_key: 'reader:{"item_id":"notes/docker.html"}',
    context_snapshot: {
      scope: "reader",
      item_ids: ["notes/docker.html"],
      items: [{ id: "notes/docker.html", title: "Docker Notes" }],
      requested: { item_id: "notes/docker.html" },
    },
    message_count: 2,
    created_at: "2026-06-07T02:00:00.000Z",
    updated_at: "2026-06-07T02:05:00.000Z",
  };
  const globalContextKey = 'global:{"collection":"","favorite":null,"include_archived":false,"library":"all","q":"","scope":"global","sort":"newest","tag_match":"any","tags":[]}';
  const globalConversation = {
    id: "conversation-global",
    title: "Workspace Overview",
    context_key: globalContextKey,
    context_snapshot: {
      scope: "global",
      item_ids: ["notes/mcp.html", "notes/docker.html"],
      items: [
        { id: "notes/mcp.html", title: "MCP Security" },
        { id: "notes/docker.html", title: "Docker Notes" },
      ],
      requested: { scope: "global", library: "all" },
    },
    message_count: 2,
    created_at: "2026-06-07T00:30:00.000Z",
    updated_at: "2026-06-07T00:35:00.000Z",
  };
  const messagesByConversation = {
    "conversation-old": [
      { role: "user", content: "Summarize this note.", sources: [] },
      { role: "assistant", content: "**MCP** security summary.", sources: [{ kind: "local", title: "MCP Security", item_id: "notes/mcp.html" }] },
    ],
    "conversation-history": [
      { role: "user", content: "Show Docker risks.", sources: [] },
      { role: "assistant", content: "Docker risk summary.", sources: [{ kind: "local", title: "Docker Notes", item_id: "notes/docker.html" }] },
    ],
  };
  const latestRequests = [];
  const conversationCreates = [];
  const conversationListRequests = [];
  const deletedConversationIds = new Set();
  let deletedConversationId = "";

  await page.route("**/api/auth/status", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ enabled: false, authenticated: true, user: null, data_id: null }),
    });
  });
  await page.route("**/api/ai/status", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ available: true, provider: "", model: "fake", external_search: false }),
    });
  });
  await page.route("**/api/version", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ version: "0.9.0", latest_version: "0.9.0", update_available: false }),
    });
  });
  await page.route("**/api/shares", async (route) => {
    await route.fulfill({ contentType: "application/json", body: JSON.stringify({ shares: [], count: 0 }) });
  });
  await page.route("**/api/manifest", async (route) => {
    await route.fulfill({ contentType: "application/json", body: JSON.stringify(manifest) });
  });
  await page.route("**/api/ai/runs**", async (route) => {
    await route.fulfill({ contentType: "application/json", body: JSON.stringify({ runs: [], count: 0 }) });
  });
  await page.route("**/api/ai/jobs**", async (route) => {
    await route.fulfill({ contentType: "application/json", body: JSON.stringify({ jobs: [], count: 0 }) });
  });
  await page.route("**/api/content/**", async (route) => {
    await route.fulfill({ contentType: "text/html", body: "<h1>Reader content</h1>" });
  });
  await page.route("**/api/ai/conversations/latest**", async (route) => {
    const url = new URL(route.request().url());
    const contextKey = url.searchParams.get("context_key") || "";
    latestRequests.push(contextKey);
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ conversation: contextKey === oldConversation.context_key ? oldConversation : null }),
    });
  });
  await page.route("**/api/ai/conversations?*", async (route) => {
    const url = new URL(route.request().url());
    const contextKey = url.searchParams.get("context_key") || "";
    conversationListRequests.push(contextKey);
    const conversations = (
      contextKey === oldConversation.context_key
        ? [oldConversation]
        : contextKey === globalContextKey
          ? [globalConversation]
          : [historyConversation, oldConversation, globalConversation]
    )
      .filter((conversation) => !deletedConversationIds.has(conversation.id));
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ conversations, count: conversations.length }),
    });
  });
  await page.route("**/api/ai/conversations/*", async (route) => {
    if (route.request().method() === "DELETE") {
      deletedConversationId = decodeURIComponent(route.request().url().split("/api/ai/conversations/")[1] || "");
      deletedConversationIds.add(deletedConversationId);
      await route.fulfill({ contentType: "application/json", body: JSON.stringify({ id: deletedConversationId, deleted: true }) });
      return;
    }
    await route.fallback();
  });
  await page.route("**/api/ai/conversations", async (route) => {
    const request = JSON.parse(route.request().postData() || "{}");
    conversationCreates.push(request);
    const created = {
      id: `conversation-new-${conversationCreates.length}`,
      title: "MCP Security",
      context_key: oldConversation.context_key,
      context_snapshot: request.context,
      message_count: 0,
      messages: [],
      created_at: "2026-06-07T03:00:00.000Z",
      updated_at: "2026-06-07T03:00:00.000Z",
    };
    await route.fulfill({ contentType: "application/json", body: JSON.stringify({ conversation: created }) });
  });
  await page.route("**/api/ai/conversations/*/messages", async (route) => {
    const match = route.request().url().match(/\/api\/ai\/conversations\/([^/]+)\/messages/);
    const conversationId = match ? decodeURIComponent(match[1]) : "";
    if (route.request().method() === "GET") {
      await route.fulfill({
        contentType: "application/json",
        body: JSON.stringify({ messages: messagesByConversation[conversationId] || [], count: messagesByConversation[conversationId]?.length || 0 }),
      });
      return;
    }
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        message: { role: "assistant", content: "Fresh answer from new conversation.", sources: [{ kind: "local", title: "MCP Security" }] },
        sources: [{ kind: "local", title: "MCP Security" }],
      }),
    });
  });

  await page.goto("/workspace/", { waitUntil: "domcontentloaded" });
  await page.locator("#ai-panel-open").click();
  await page.locator("#ai-history-toggle").click();
  await expect(page.locator("#ai-history-list")).toContainText("Workspace Overview");
  await expect(page.locator("#ai-history-list")).not.toContainText("MCP Security");
  expect(conversationListRequests.at(-1)).toBe(globalContextKey);
  await page.locator("#ai-history-toggle").click();
  await page.locator("#ai-panel-close").click();

  await page.locator(".item-card", { hasText: "MCP Security" }).getByRole("button", { name: "Read" }).click();
  await page.locator("#ai-panel-open").click();

  await expect(page.locator("#ai-chat-log")).toContainText("Summarize this note.");
  await expect(page.locator("#ai-chat-log")).toContainText("MCP security summary.");
  await expect.poll(() => latestRequests.includes(oldConversation.context_key)).toBe(true);

  await page.locator("#ai-new-chat").click();
  await expect(page.locator("#ai-chat-log .ai-message")).toHaveCount(0);
  await expect(page.locator(".ai-conversation-actions #ai-history-toggle")).toBeVisible();
  await expect.poll(() => conversationListRequests.includes(oldConversation.context_key)).toBe(true);

  await page.locator("#reader-close").click();
  await page.locator(".item-card", { hasText: "MCP Security" }).getByRole("button", { name: "Read" }).click();
  await expect(page.locator("#ai-chat-log .ai-message")).toHaveCount(0);

  await page.locator("#ai-chat-input").fill("Start a fresh summary.");
  await page.locator("#ai-chat-form button[type='submit']").click();
  await expect.poll(() => conversationCreates.length).toBe(1);
  expect(conversationCreates[0]).toMatchObject({ source_mode: "local_only", context: { item_id: "notes/mcp.html" } });
  await expect(page.locator("#ai-chat-log")).toContainText("Fresh answer from new conversation.");

  await page.locator("#ai-history-toggle").click();
  await expect(page.locator("#ai-history-list")).toContainText("MCP Security");
  await expect(page.locator("#ai-history-list")).not.toContainText("Docker Notes");
  expect(conversationListRequests.at(-1)).toBe(oldConversation.context_key);
  page.once("dialog", async (dialog) => dialog.accept());
  await page.locator("#ai-history-list .ai-history-row", { hasText: "MCP Security" }).getByRole("button", { name: "Delete" }).click();
  await expect.poll(() => deletedConversationId).toBe("conversation-old");
  await expect(page.locator("#ai-history-list")).toBeVisible();
  await expect(page.locator("#ai-history-list")).toContainText("No conversation history");

  await page.locator("#settings-open").click();
  await page.locator("[data-settings-tab='ai-conversations']").click();
  await expect(page.locator("#ai-conversation-list")).toContainText("Docker Notes");
  await expect(page.locator("#ai-conversation-list")).not.toContainText("MCP Security");
  await page.locator("#ai-conversation-list .ai-conversation-row", { hasText: "Docker Notes" }).getByRole("button", { name: "Open" }).click();
  await expect(page.locator("#ai-chat-log")).toContainText("Show Docker risks.");
  await expect(page.locator("#ai-chat-log")).toContainText("Docker risk summary.");

  await page.locator("#settings-open").click();
  await page.locator("[data-settings-tab='ai-conversations']").click();
  page.once("dialog", async (dialog) => dialog.accept());
  await page.locator("#ai-conversation-list .ai-conversation-row", { hasText: "Docker Notes" }).getByRole("button", { name: "Delete" }).click();
  await expect.poll(() => deletedConversationId).toBe("conversation-history");
});

test("workspace AI renders markdown hierarchy and aligns the more menu", async ({ page }) => {
  await page.addInitScript(() => localStorage.clear());
  await routeWorkspace(page);

  await page.route("**/api/auth/status", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ enabled: false, authenticated: true, user: null, data_id: null }),
    });
  });
  await page.route("**/api/ai/status", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ available: true, provider: "", model: "fake", external_search: false }),
    });
  });
  await page.route("**/api/version", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ version: "0.9.0", latest_version: "0.9.0", update_available: false }),
    });
  });
  await page.route("**/api/shares", async (route) => {
    await route.fulfill({ contentType: "application/json", body: JSON.stringify({ shares: [], count: 0 }) });
  });
  await page.route("**/api/manifest", async (route) => {
    await route.fulfill({ contentType: "application/json", body: JSON.stringify({ version: 2, title: "HTMlore Workspace", items: [] }) });
  });
  await page.route("**/api/ai/runs**", async (route) => {
    await route.fulfill({ contentType: "application/json", body: JSON.stringify({ runs: [], count: 0 }) });
  });
  await page.route("**/api/ai/jobs**", async (route) => {
    await route.fulfill({ contentType: "application/json", body: JSON.stringify({ jobs: [], count: 0 }) });
  });
  await page.route("**/api/ai/conversations/latest**", async (route) => {
    await route.fulfill({ contentType: "application/json", body: JSON.stringify({ conversation: null }) });
  });
  await page.route("**/api/ai/conversations", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        conversation: {
          id: "markdown-conversation",
          title: "Markdown",
          context_key: "local_only:global:{}",
          context_snapshot: {},
          message_count: 0,
          messages: [],
        },
      }),
    });
  });
  await page.route("**/api/ai/conversations/*/messages", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        message: {
          role: "assistant",
          content: [
            "# 父级标题",
            "",
            "## 子级标题",
            "",
            "1. 储能系统集成商 / EPC总承包商",
            "",
            "目标：寻找能输送优质项目、深度绑定的产业合作方。",
            "",
            "1. 工业园区运营方 / 高耗能用电企业",
            "",
            "目标：寻找工商业储能EMC客户资源。",
          ].join("\n"),
          sources: [{ kind: "local", title: "Long local source title used for markdown rendering" }],
        },
        sources: [{ kind: "local", title: "Long local source title used for markdown rendering" }],
      }),
    });
  });

  await page.goto("/workspace/", { waitUntil: "domcontentloaded" });
  await page.locator("#ai-panel-open").click();
  await page.locator("#ai-chat-input").fill("Render markdown.");
  await page.locator("#ai-chat-form button[type='submit']").click();
  await expect(page.locator("#ai-chat-log .ai-message.assistant").last()).toContainText("父级标题");

  const markdownState = await page.evaluate(() => {
    const container = document.querySelector("#ai-chat-log .ai-message.assistant:last-child .ai-message-body");
    const headings = [...container.querySelectorAll("h3, h4, h5")].map((node) => ({
      tag: node.tagName.toLowerCase(),
      fontSize: Number.parseFloat(getComputedStyle(node).fontSize),
    }));
    return {
      orderedListCount: container.querySelectorAll("ol").length,
      listItemCount: container.querySelectorAll("ol > li").length,
      firstItemText: container.querySelector("ol > li")?.textContent || "",
      headings,
    };
  });
  expect(markdownState.orderedListCount).toBe(1);
  expect(markdownState.listItemCount).toBe(2);
  expect(markdownState.firstItemText).toContain("目标：寻找能输送优质项目");
  expect(markdownState.headings[0]).toMatchObject({ tag: "h3" });
  expect(markdownState.headings[1]).toMatchObject({ tag: "h4" });
  expect(markdownState.headings[0].fontSize).toBeGreaterThan(markdownState.headings[1].fontSize);

  await expect(page.locator("#ai-more-toggle")).toHaveCount(0);
  await expect(page.locator("#ai-new-chat")).toBeVisible();

  await page.locator("#ai-job-toggle").click();
  await expect(page.locator("#ai-job-list")).toBeVisible();
  const jobListMetrics = await page.evaluate(() => {
    const list = document.querySelector("#ai-job-list").getBoundingClientRect();
    const toggle = document.querySelector("#ai-job-toggle").getBoundingClientRect();
    return {
      leftOverflow: Math.round(0 - list.left),
      rightOverflow: Math.round(list.right - window.innerWidth),
      width: Math.round(list.width),
      toggleRightDelta: Math.round(toggle.right - list.right),
      topDelta: Math.round(list.top - toggle.bottom),
    };
  });
  expect(jobListMetrics.leftOverflow).toBeLessThanOrEqual(0);
  expect(jobListMetrics.rightOverflow).toBeLessThanOrEqual(0);
  expect(jobListMetrics.width).toBeLessThanOrEqual(420);
  expect(Math.abs(jobListMetrics.toggleRightDelta)).toBeLessThanOrEqual(60);
  expect(Math.abs(jobListMetrics.topDelta - 8)).toBeLessThanOrEqual(2);
});
