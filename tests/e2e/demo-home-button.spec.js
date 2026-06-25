const { expect, test } = require("@playwright/test");

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => localStorage.clear());
  await page.goto("/demo/", { waitUntil: "domcontentloaded" });
});

test("demo defaults to English without a saved language", async ({ page }) => {
  await page.goto("/demo/");

  await expect(page.locator("#language-select")).toHaveValue("en");
  await expect(page.getByRole("button", { name: /All Items/ })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Create with AI" })).toBeVisible();
});

test("demo Home button stays outside the AI panel", async ({ page }) => {
  await page.goto("/demo/?lang=zh-CN");

  const homeButton = page.locator(".demo-home-link");
  await expect(homeButton).toBeVisible();

  await page.locator("#ai-panel-open").click();
  const aiPanel = page.locator("#ai-panel");
  await expect(aiPanel).toBeVisible();
  await expect(page.locator("body")).toHaveClass(/ai-panel-open/);

  await expect
    .poll(async () => {
      const homeBox = await homeButton.boundingBox();
      const panelBox = await aiPanel.boundingBox();
      if (!homeBox || !panelBox) return false;
      return homeBox.x + homeBox.width <= panelBox.x - 12;
    })
    .toBe(true);
});

test("workspace logo returns to the workspace home", async ({ page }) => {
  await page.goto("/demo/?lang=zh-CN");

  await page.locator("#library-nav .nav-item", { hasText: "Imported" }).click();
  await expect(page.getByRole("button", { name: /Imported/ })).toHaveClass(/active/);
  await page.locator("#brand-home").click();
  await expect(page).toHaveURL(/\/demo\/\?lang=zh-CN$/);
  await expect(page.getByRole("button", { name: /All Items/ })).toHaveClass(/active/);
  await expect(page.locator(".cover h1")).toHaveCount(0);
});

test("topbar keeps settings, generation queue, and AI actions grouped on the right", async ({ page }) => {
  await expect(page.locator("#profile-status")).toHaveCount(0);
  await expect(page.locator("#settings-open")).toBeVisible();
  await expect(page.locator("#ai-job-toggle")).toBeVisible();
  await expect(page.locator("#ai-panel-open")).toBeVisible();
  await expect(page.locator(".project-link")).toBeVisible();
  await expect(page.locator(".github-link")).toBeVisible();
  await expect(page.locator(".sidebar-tools #settings-open")).toHaveCount(0);
  await expect(page.locator(".topbar-control-group #settings-open")).toHaveCount(0);
  await expect(page.locator(".topbar-search-group #settings-open")).toHaveCount(1);
  await expect(page.locator(".topbar-search-group #ai-job-toggle")).toHaveCount(1);
  await expect(page.locator(".project-link")).toHaveAttribute("href", /html_lore\/$/);
  await expect(page.locator(".github-link")).toHaveAttribute("href", /github\.com\/JMoCoder\/html_lore/);

  await expect
    .poll(async () => {
      const settings = await page.locator("#settings-open").boundingBox();
      const queue = await page.locator("#ai-job-toggle").boundingBox();
      const ai = await page.locator("#ai-panel-open").boundingBox();
      if (!settings || !queue || !ai) return false;
      return settings.x < queue.x && queue.x < ai.x;
    })
    .toBe(true);
});

test("sidebar footer stays inside a narrow resized sidebar", async ({ page }) => {
  await page.evaluate(() => {
    document.body.style.setProperty("--sidebar-width", "240px");
  });

  const sidebar = page.locator(".sidebar");
  await expect
    .poll(async () => {
      const sidebarBox = await sidebar.boundingBox();
      const footerBox = await page.locator(".sidebar-tools").boundingBox();
      const projectBox = await page.locator(".project-link").boundingBox();
      const githubBox = await page.locator(".github-link").boundingBox();
      if (!sidebarBox || !footerBox || !projectBox || !githubBox) return false;
      return footerBox.x >= sidebarBox.x
        && footerBox.x + footerBox.width <= sidebarBox.x + sidebarBox.width
        && projectBox.x + projectBox.width <= sidebarBox.x + sidebarBox.width
        && githubBox.width <= 44;
    })
    .toBe(true);
});

test("AI panel sends with Enter and keeps Shift Enter for new lines", async ({ page }) => {
  await page.locator("#ai-panel-open").click();
  await expect(page.locator("#ai-content-expansion")).toBeDisabled();
  await expect(page.locator("#ai-deep-research")).toBeDisabled();
  await expect(page.locator("#ai-generate-note")).toBeDisabled();
  await expect(page.locator(".ai-source-options")).toContainText("Expand");
  await expect(page.locator(".ai-source-options")).toContainText("Research");
  await expect(page.locator("#ai-more-toggle")).toHaveCount(0);
  await expect(page.locator("#ai-new-chat")).toBeVisible();
  await expect(page.locator(".ai-conversation-actions #ai-history-toggle")).toBeVisible();
  const newChatButtonMetrics = await page.locator("#ai-new-chat").evaluate((button) => {
    const icon = button.querySelector(".button-icon");
    const buttonBox = button.getBoundingClientRect();
    const iconBox = icon.getBoundingClientRect();
    return {
      dx: Math.abs((buttonBox.left + buttonBox.width / 2) - (iconBox.left + iconBox.width / 2)),
      dy: Math.abs((buttonBox.top + buttonBox.height / 2) - (iconBox.top + iconBox.height / 2)),
    };
  });
  expect(newChatButtonMetrics.dx).toBeLessThan(1);
  expect(newChatButtonMetrics.dy).toBeLessThan(1);
  await page.locator("#ai-chat-input").fill("First line");
  await page.keyboard.press("Shift+Enter");
  await page.keyboard.type("Second line");
  await expect(page.locator("#ai-chat-input")).toHaveValue("First line\nSecond line");

  await page.keyboard.press("Enter");
  await expect(page.locator(".ai-message.user")).toContainText("First line");
  await expect(page.locator(".ai-message.pending")).toContainText("Replying");
  await expect(page.locator("#ai-chat-input")).toHaveValue("");
  await expect(page.locator(".ai-conversation-actions #ai-history-toggle")).toBeVisible();
  await expect(page.locator(".ai-message.pending")).toHaveCount(0);
  await expect(page.locator(".ai-message.assistant").last()).toContainText("AI response placeholder");
});

test("card share action opens the same share dialog", async ({ page }) => {
  await page.goto("/demo/?lang=en");

  const firstCard = page.locator(".item-card").first();
  await expect(firstCard.getByTitle("Share")).toBeVisible();
  await firstCard.getByTitle("Share").click();

  await expect(page.locator("#share-dialog")).toBeVisible();
  await expect(page.locator("#share-duration")).toBeVisible();
  await expect(page.locator("#share-feedback")).toContainText("backend server");
  await page.locator("#share-cancel").click();
  await expect(page.locator("#share-dialog")).toBeHidden();
});

test("share dialog and management show expiry and static status", async ({ page }) => {
  let shares = [];
  const share = {
    id: "share-test",
    item_id: "demo-notes/readme.zh-CN.html",
    token: "token-test",
    url_path: "/share/token-test",
    duration: "7d",
    expires_at: "2026-06-12T09:30:00Z",
    revoked: false,
    active: true,
    access_count: 2,
  };
  await page.route("**/demo/config.js", async (route) => {
    await route.fulfill({
      contentType: "application/javascript",
      body: 'window.HTML_LORE_AGENT_URL = "http://127.0.0.1:8090";',
    });
  });
  await page.route("**/api/auth/status", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ enabled: false, authenticated: true, user: null, data_id: null }),
    });
  });
  await page.route("**/api/shares", async (route) => {
    if (route.request().method() === "POST") {
      shares = [share];
      await route.fulfill({
        contentType: "application/json",
        body: JSON.stringify({ share, token: share.token, url_path: share.url_path }),
      });
      return;
    }
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ shares, count: shares.length }),
    });
  });

  await page.goto("/demo/?lang=en");
  await page
    .locator(".item-card", { hasText: "HTMlore README 完整说明" })
    .locator("[data-item-action='share']")
    .click();
  await page.locator("#share-duration").selectOption("7d");
  await page.locator("#share-create").click();

  await expect(page.locator("#share-link")).toHaveValue(/\/share\/token-test$/);
  await expect(page.locator("#share-expiry")).toContainText("Valid until:");
  await expect(page.locator("#share-expiry")).toContainText("2026");
  await expect(page.locator("#share-expiry .share-status")).toContainText("Active");
  await expect(page.locator("#share-expiry .share-status")).toHaveClass(/is-active/);

  await page.locator("#share-cancel").click();
  await expect(page.locator("#share-dialog")).toBeHidden();
  await page.locator("#settings-open").click();
  await page.locator("[data-settings-tab='shares']").click();
  const row = page.locator("#share-management-list .share-row").first();
  await expect(row.locator(".share-status")).toContainText("Active");
  await expect(row).toContainText("HTMlore README 完整说明");
  await expect(row).toContainText("2026");
  await expect(row).toContainText("2 visits");
  await expect(row.locator(".share-row-title")).toHaveCSS("cursor", "pointer");
  await expect(row.locator("[data-share-open]")).toHaveCSS("cursor", "pointer");
  await expect(row.locator("[data-share-revoke]")).toHaveCSS("cursor", "pointer");
  const shareMetaLayout = await row.evaluate((node) => {
    const title = node.querySelector(".management-name").getBoundingClientRect();
    const detailsNode = node.querySelector(".share-row-details");
    const metaNode = node.querySelector(".share-row-meta");
    const details = detailsNode.getBoundingClientRect();
    const meta = metaNode.getBoundingClientRect();
    const status = node.querySelector(".share-status").getBoundingClientRect();
    return {
      detailsLeft: Math.round(details.left),
      metaLeft: Math.round(meta.left),
      statusLeft: Math.round(status.left),
      detailsText: [...detailsNode.querySelectorAll("span")]
        .map((span) => span.textContent || "")
        .join(" "),
      detailsFits: detailsNode.scrollWidth <= detailsNode.clientWidth + 1,
      metaFits: metaNode.scrollWidth <= metaNode.clientWidth + 1,
      sameRow: Math.abs(details.top - title.top) < 10,
      metaHeight: Math.round(meta.height),
    };
  });
  expect(shareMetaLayout.sameRow).toBe(true);
  expect(Math.abs(shareMetaLayout.metaLeft - shareMetaLayout.detailsLeft)).toBeLessThanOrEqual(2);
  expect(Math.abs(shareMetaLayout.statusLeft - shareMetaLayout.detailsLeft)).toBeLessThanOrEqual(2);
  expect(shareMetaLayout.metaHeight).toBeLessThan(28);
  expect(shareMetaLayout.detailsText).toContain("Active");
  expect(shareMetaLayout.detailsText).toContain("2026");
  expect(shareMetaLayout.detailsText).toContain("2 visits");
  expect(shareMetaLayout.detailsText).not.toContain("...");
  expect(shareMetaLayout.detailsFits).toBe(true);
  expect(shareMetaLayout.metaFits).toBe(true);

  await row.locator(".share-row-title").click();
  await expect(page.locator("#settings-page")).toBeHidden();
  await expect(page.locator("#reader")).toBeVisible();
  await expect(page.locator("#reader-title")).toHaveText("HTMlore README 完整说明");
});

test("share management sorts active links before expired links by note creation time", async ({ page }) => {
  const baseShare = {
    duration: "7d",
    revoked: false,
    access_count: 1,
  };
  const shares = [
    {
      ...baseShare,
      id: "share-expired-older",
      item_id: "demo-notes/readme.zh-CN.html",
      token: "token-expired-older",
      url_path: "/share/token-expired-older",
      expires_at: "2026-06-01T08:30:00Z",
      active: false,
    },
    {
      ...baseShare,
      id: "share-expired-newer",
      item_id: "demo-notes/changelog.zh-CN.html",
      token: "token-expired-newer",
      url_path: "/share/token-expired-newer",
      expires_at: "2026-06-01T09:30:00Z",
      active: false,
      access_count: 3,
    },
    {
      ...baseShare,
      id: "share-active-older",
      item_id: "demo-notes/readme.zh-CN.html",
      token: "token-active-older",
      url_path: "/share/token-active-older",
      expires_at: "2026-06-11T09:30:00Z",
      active: true,
    },
    {
      ...baseShare,
      id: "share-active-newer",
      item_id: "demo-notes/changelog.zh-CN.html",
      token: "token-active-newer",
      url_path: "/share/token-active-newer",
      expires_at: "2026-06-13T09:30:00Z",
      active: true,
      access_count: 5,
    },
  ];
  await page.route("**/demo/config.js", async (route) => {
    await route.fulfill({
      contentType: "application/javascript",
      body: 'window.HTML_LORE_AGENT_URL = "http://127.0.0.1:8090";',
    });
  });
  await page.route("**/api/auth/status", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ enabled: false, authenticated: true, user: null, data_id: null }),
    });
  });
  await page.route("**/api/shares", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ shares, count: shares.length }),
    });
  });

  await page.goto("/demo/?lang=en");
  await page.locator("#settings-open").click();
  await page.locator("[data-settings-tab='shares']").click();

  const rowTitles = await page.locator("#share-management-list .share-row-title").allTextContents();
  expect(rowTitles).toEqual([
    "HTMlore 更新日志",
    "HTMlore README 完整说明",
    "HTMlore 更新日志",
    "HTMlore README 完整说明",
  ]);
  await expect(page.locator("#share-management-list .share-row").nth(0).locator(".share-status")).toContainText("Active");
  await expect(page.locator("#share-management-list .share-row").nth(1).locator(".share-status")).toContainText("Active");
  await expect(page.locator("#share-management-list .share-row").nth(2).locator(".share-status")).toContainText("Expired");
  await expect(page.locator("#share-management-list .share-row").nth(3).locator(".share-status")).toContainText("Expired");
});

test("tag filter counts follow OR and AND selection semantics", async ({ page }) => {
  const items = [
    {
      id: "notes/a.html",
      title: "Alpha",
      summary: "A only",
      collection: "Test",
      tags: ["A"],
      source: "imported",
      updated: "2026-06-04T00:00:00Z",
      path: "content/a.html",
    },
    {
      id: "notes/ab.html",
      title: "Alpha Beta",
      summary: "A and B",
      collection: "Test",
      tags: ["A", "B"],
      source: "imported",
      updated: "2026-06-03T00:00:00Z",
      path: "content/ab.html",
    },
    {
      id: "notes/c.html",
      title: "Gamma",
      summary: "C only",
      collection: "Test",
      tags: ["C"],
      source: "imported",
      updated: "2026-06-02T00:00:00Z",
      path: "content/c.html",
    },
  ];
  await page.route("**/demo/config.js", async (route) => {
    await route.fulfill({
      contentType: "application/javascript",
      body: 'window.HTML_LORE_AGENT_URL = "http://127.0.0.1:8090";',
    });
  });
  await page.route("**/api/auth/status", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ enabled: false, authenticated: true, user: null, data_id: null }),
    });
  });
  await page.route("**/api/manifest", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ version: 2, title: "Filter Test", items }),
    });
  });
  await page.route("**/api/shares", async (route) => {
    await route.fulfill({ contentType: "application/json", body: JSON.stringify({ shares: [], count: 0 }) });
  });

  await page.goto("/demo/?lang=en");
  await page.locator("#multi-filter-toggle").click();
  await expect(page.locator("#multi-filter-result-count")).toHaveText("(Selected: 3)");
  await expect(page.locator("#multi-tag-options .multi-filter-option", { hasText: "#A" }).locator(".multi-filter-count")).toHaveText("2");
  await expect(page.locator("#multi-tag-options .multi-filter-option", { hasText: "#B" }).locator(".multi-filter-count")).toHaveText("1");
  await expect(page.locator("#multi-tag-options .multi-filter-option", { hasText: "#C" }).locator(".multi-filter-count")).toHaveText("1");

  await page.locator("#multi-tag-options .multi-filter-option", { hasText: "#A" }).click();
  await expect(page.locator("#multi-filter-result-count")).toHaveText("(Selected: 2)");
  await expect(page.locator("#multi-tag-options .multi-filter-option", { hasText: "#B" }).locator(".multi-filter-count")).toHaveText("1");
  await expect(page.locator("#multi-tag-options .multi-filter-option", { hasText: "#C" }).locator(".multi-filter-count")).toHaveText("1");

  await page.locator("[data-tag-match-mode='all']").click();
  await expect(page.locator("#multi-filter-result-count")).toHaveText("(Selected: 2)");
  await expect(page.locator("#multi-tag-options .multi-filter-option", { hasText: "#A" }).locator(".multi-filter-count")).toHaveText("2");
  await expect(page.locator("#multi-tag-options .multi-filter-option", { hasText: "#B" }).locator(".multi-filter-count")).toHaveText("1");
  await expect(page.locator("#multi-tag-options .multi-filter-option", { hasText: "#C" }).locator(".multi-filter-count")).toHaveText("0");

  await page.locator("#multi-tag-options .multi-filter-option", { hasText: "#B" }).click();
  await expect(page.locator("#multi-filter-result-count")).toHaveText("(Selected: 1)");
  await expect(page.locator("#multi-tag-options .multi-filter-option", { hasText: "#A" }).locator(".multi-filter-count")).toHaveText("1");
  await expect(page.locator("#multi-tag-options .multi-filter-option", { hasText: "#B" }).locator(".multi-filter-count")).toHaveText("1");
  await expect(page.locator("#multi-tag-options .multi-filter-option", { hasText: "#C" }).locator(".multi-filter-count")).toHaveText("0");
});

test("card date uses the stable created date instead of state update time", async ({ page }) => {
  await page.route("**/demo/config.js", async (route) => {
    await route.fulfill({
      contentType: "application/javascript",
      body: 'window.HTML_LORE_AGENT_URL = "http://127.0.0.1:8090";',
    });
  });
  await page.route("**/api/auth/status", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ enabled: false, authenticated: true, user: null, data_id: null }),
    });
  });
  await page.route("**/api/manifest", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        version: 2,
        title: "Date Test",
        items: [
          {
            id: "notes/stable-date.html",
            title: "Stable Date",
            summary: "Created date should remain visible after state changes.",
            collection: "Test",
            tags: ["Date"],
            source: "imported",
            created: "2026-05-01T08:00:00Z",
            updated: "2026-06-05T08:00:00Z",
            path: "content/stable-date.html",
          },
        ],
      }),
    });
  });
  await page.route("**/api/shares", async (route) => {
    await route.fulfill({ contentType: "application/json", body: JSON.stringify({ shares: [], count: 0 }) });
  });

  await page.goto("/demo/?lang=en");
  const card = page.locator(".item-card", { hasText: "Stable Date" });
  await expect(card.locator(".card-date")).toHaveText("2026-05-01");
});

test("card original links use raw API in same-origin app mode", async ({ page }) => {
  await page.route("**/demo/config.js", async (route) => {
    await route.fulfill({
      contentType: "application/javascript",
      body: 'window.HTML_LORE_AGENT_URL = "http://127.0.0.1:8090";',
    });
  });
  await page.route("**/api/auth/status", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ enabled: false, authenticated: true, user: null, data_id: null }),
    });
  });
  await page.route("**/api/manifest", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        version: 2,
        title: "HTMlore Test",
        items: [
          {
            id: "imported/2026/06/imported-note-6.html",
            title: "Imported Note",
            summary: "Imported note summary",
            collection: "Inbox",
            tags: ["HTML"],
            source: "imported",
            updated: "2026-06-04T00:00:00Z",
            path: "content/imported/2026/06/imported-note-6.html",
          },
        ],
      }),
    });
  });
  await page.goto("/demo/?lang=en");

  const original = page.locator(".item-card .card-links a").first();
  await expect(original).toBeVisible();
  await expect(original).toHaveAttribute("href", /\/api\/items\/.+\/raw$/);
});

test("card original links keep static content paths in demo mode", async ({ page }) => {
  await page.goto("/demo/?lang=en");

  const original = page.locator(".item-card .card-links a").first();
  await expect(original).toBeVisible();
  await expect(original).toHaveAttribute("href", /^content\/.+\.html$/);
});
