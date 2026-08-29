import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { ExportService, ItemService, ShareSafetyConfirmationError, ShareService, UploadService } from "@/server";
import { normalizeQuery, sortItems } from "@/server/items";
import type { Item } from "@/server/types";
import { readZipStoreEntries } from "@/server/zip";

function tempWorkspace() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "html-lore-"));
  const contentDir = path.join(root, "content");
  const metaDir = path.join(root, "meta");
  fs.mkdirSync(contentDir, { recursive: true });
  fs.mkdirSync(path.join(metaDir, "items"), { recursive: true });
  fs.mkdirSync(path.join(metaDir, "config"), { recursive: true });
  const examples = path.join(process.cwd(), "examples");
  copyDir(path.join(examples, "content"), contentDir);
  copyDir(path.join(examples, "meta"), metaDir);
  return {
    contentDir,
    metaDir,
    publicDir: path.join(root, "public"),
    siteTitle: "HTMlore",
    maxUploadBytes: 1024 * 1024,
    apiToken: "",
    authUsername: "",
    authPassword: "",
    usersFile: null,
    userDataDir: null,
    sessionSecret: "",
    sessionCookieName: "html_lore_session",
    sessionMaxAgeSeconds: 604800,
    sessionSecure: false,
    shareInteractiveEnabled: true,
  };
}

function itemStub(overrides: Partial<Item>): Item {
  return {
    id: "note.html",
    title: "Note",
    summary: "",
    path: "content/note.html",
    source_type: "html",
    source_url: null,
    collection: "Inbox",
    tags: [],
    status: "ready",
    review_status: "reviewed",
    favorite: false,
    archived: false,
    pinned: false,
    created: "2026-01-01T00:00:00.000Z",
    updated: "2026-01-01T00:00:00.000Z",
    cover: null,
    open_mode: "iframe",
    agent: {},
    text: "",
    ...overrides,
  };
}

function copyDir(src: string, dest: string) {
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const from = path.join(src, entry.name);
    const to = path.join(dest, entry.name);
    if (entry.isDirectory()) {
      fs.mkdirSync(to, { recursive: true });
      copyDir(from, to);
    } else fs.copyFileSync(from, to);
  }
}

describe("examples fixtures", () => {
  it("lists imported and generated items with tag filters", () => {
    const settings = tempWorkspace();
    const items = new ItemService(settings);
    expect(items.listItems({ q: "", library: "all", collection: "", tags: [], tagMatch: "any", favorite: null, archived: null, sort: "newest", limit: null }).length).toBe(10);
    const filtered = items.listItems({
      q: "",
      library: "all",
      collection: "",
      tags: ["MCP", "Docker"],
      tagMatch: "all",
      favorite: null,
      archived: null,
      sort: "newest",
      limit: null,
    });
    expect(filtered.some((item) => item.id.includes("mcp-docker-agent"))).toBe(true);
  });

  it("sorts by created time with the same fallback as updated time", () => {
    const items = [
      itemStub({ id: "old-created-new-updated", title: "B", created: "2026-01-01T00:00:00.000Z", updated: "2026-08-01T00:00:00.000Z" }),
      itemStub({ id: "new-created-old-updated", title: "A", created: "2026-07-01T00:00:00.000Z", updated: "2026-02-01T00:00:00.000Z" }),
      itemStub({ id: "mid", title: "C", created: "2026-03-01T00:00:00.000Z", updated: "2026-03-01T00:00:00.000Z" }),
    ];
    expect(sortItems(items, "created-newest").map((item) => item.id)).toEqual([
      "new-created-old-updated",
      "mid",
      "old-created-new-updated",
    ]);
    expect(sortItems(items, "created-oldest").map((item) => item.id)).toEqual([
      "old-created-new-updated",
      "mid",
      "new-created-old-updated",
    ]);
    expect(sortItems(items, "newest").map((item) => item.id)).toEqual([
      "old-created-new-updated",
      "mid",
      "new-created-old-updated",
    ]);
    expect(normalizeQuery({}).sort).toBe("created-newest");
  });

  it("writes html content and reads the same bytes back", () => {
    const settings = tempWorkspace();
    const items = new ItemService(settings);
    const id = items
      .listItems({ q: "", library: "all", collection: "", tags: [], tagMatch: "any", favorite: null, archived: null, sort: "newest", limit: null })
      .find((item) => item.id.includes("mcp-docker-agent"))?.id;
    expect(id).toBeTruthy();
    const next = "<!doctype html>\n<html><body><p>saved-roundtrip</p></body></html>\n";
    items.updateItemContent(id!, next);
    expect(items.readItemContent(id!)).toBe(next);
  });

  it("exports manifest json and a zip of original html files", () => {
    const settings = tempWorkspace();
    const exported = new ExportService(settings);
    const manifest = JSON.parse(exported.manifestJson().body.toString("utf8")) as { items: { id: string }[] };
    expect(manifest.items.length).toBe(10);
    const archive = exported.htmlArchive();
    const entries = readZipStoreEntries(archive.body);
    expect(entries.some((entry) => entry.name.includes("mcp-docker-agent"))).toBe(true);
    const sample = entries.find((entry) => entry.name.endsWith(".html"));
    expect(sample?.data.includes(Buffer.from("<"))).toBe(true);
  });

  it("imports html and creates share token", () => {
    const settings = tempWorkspace();
    const upload = new UploadService(settings).importHtml({
      filename: "note.html",
      content: Buffer.from("<!doctype html><html><head><title>Imported</title></head><body><p>Hello</p></body></html>", "utf8"),
      collection: "Ops",
      tags: "Demo",
    });
    expect(upload.item_id.startsWith("imported/")).toBe(true);
    const share = new ShareService(settings).createShare({ itemId: upload.item_id, duration: "1d", mode: "safe" });
    expect(share.token.length).toBeGreaterThan(10);
    const payload = new ShareService(settings).publicReadByToken(share.token);
    expect(payload.item.title).toContain("Imported");
  });

  it("revokes a share so the public token no longer works", () => {
    const settings = tempWorkspace();
    const upload = new UploadService(settings).importHtml({
      filename: "share-revoke.html",
      content: Buffer.from("<!doctype html><html><head><title>Revoke me</title></head><body><p>Hello</p></body></html>", "utf8"),
      collection: "Ops",
      tags: "Demo",
    });
    const shares = new ShareService(settings);
    const created = shares.createShare({ itemId: upload.item_id, duration: "1d", mode: "safe" });
    const shareId = String(created.share.id);
    expect(shares.listShares().some((row) => String(row.id) === shareId && row.active)).toBe(true);
    expect(shares.publicReadByToken(created.token).item.title).toContain("Revoke me");
    shares.revokeShare(shareId);
    const listed = shares.listShares().find((row) => String(row.id) === shareId);
    expect(listed?.revoked).toBe(true);
    expect(listed?.active).toBe(false);
    expect(() => shares.publicReadByToken(created.token)).toThrow(/Share not found/);
  });

  it("updates share duration without rotating the public token", () => {
    const settings = tempWorkspace();
    const upload = new UploadService(settings).importHtml({
      filename: "share-update.html",
      content: Buffer.from("<!doctype html><html><head><title>Keep token</title></head><body><p>Hello</p></body></html>", "utf8"),
      collection: "Ops",
      tags: "Demo",
    });
    const shares = new ShareService(settings);
    const created = shares.createShare({ itemId: upload.item_id, duration: "1h", mode: "safe" });
    const before = Date.parse(String(created.share.expires_at));
    const updated = shares.updateShare(String(created.share.id), { duration: "7d" });
    expect(updated.duration).toBe("7d");
    expect(Date.parse(String(updated.expires_at))).toBeGreaterThan(before);
    expect(shares.publicReadByToken(created.token).item.title).toContain("Keep token");
  });

  it("creates an interactive share without confirmation when content is clean", () => {
    const settings = tempWorkspace();
    const upload = new UploadService(settings).importHtml({
      filename: "share-interactive-clean.html",
      content: Buffer.from("<!doctype html><html><head><title>Clean</title></head><body><p>Hello</p></body></html>", "utf8"),
      collection: "Ops",
      tags: "Demo",
    });
    const created = new ShareService(settings).createShare({ itemId: upload.item_id, duration: "1d", mode: "interactive" });
    expect(created.share.mode).toBe("interactive");
    expect(created.token.length).toBeGreaterThan(10);
  });

  it("requires confirmation for interactive shares that mention private hosts", () => {
    const settings = tempWorkspace();
    const upload = new UploadService(settings).importHtml({
      filename: "share-interactive-local.html",
      content: Buffer.from(
        "<!doctype html><html><head><title>Local</title></head><body><p>See http://127.0.0.1:8080</p></body></html>",
        "utf8",
      ),
      collection: "Ops",
      tags: "Demo",
    });
    const shares = new ShareService(settings);
    expect(() => shares.createShare({ itemId: upload.item_id, duration: "1d", mode: "interactive" })).toThrow(
      ShareSafetyConfirmationError,
    );
    const created = shares.createShare({
      itemId: upload.item_id,
      duration: "1d",
      mode: "interactive",
      confirmPrivateReferences: true,
    });
    expect(created.share.mode).toBe("interactive");
  });

  it("renames a collection and a tag across notes", () => {
    const settings = tempWorkspace();
    const items = new ItemService(settings);
    const renamed = items.renameCollection("Dev", "Ops");
    expect(renamed.updated).toBeGreaterThan(0);
    expect(items.listItems({ q: "", library: "all", collection: "Ops", tags: [], tagMatch: "any", favorite: null, archived: null, sort: "newest", limit: null }).length).toBeGreaterThan(0);
    expect(items.listItems({ q: "", library: "all", collection: "Dev", tags: [], tagMatch: "any", favorite: null, archived: null, sort: "newest", limit: null }).length).toBe(0);
    const tagged = items.listItems({ q: "", library: "all", collection: "", tags: ["Docker"], tagMatch: "any", favorite: null, archived: null, sort: "newest", limit: null });
    expect(tagged.length).toBeGreaterThan(0);
    items.renameTag("Docker", "Containers");
    expect(items.listItems({ q: "", library: "all", collection: "", tags: ["Containers"], tagMatch: "any", favorite: null, archived: null, sort: "newest", limit: null }).length).toBe(tagged.length);
    expect(items.listItems({ q: "", library: "all", collection: "", tags: ["Docker"], tagMatch: "any", favorite: null, archived: null, sort: "newest", limit: null }).length).toBe(0);
  });

  it("pins a note and searches HTML body text", () => {
    const settings = tempWorkspace();
    const items = new ItemService(settings);
    const upload = new UploadService(settings).importHtml({
      filename: "body-search.html",
      content: Buffer.from("<!doctype html><html><head><title>Visible title</title></head><body><p>unique-body-token-zxqv</p></body></html>", "utf8"),
      collection: "Inbox",
    });
    expect(items.listItems({ q: "unique-body-token-zxqv", library: "all", collection: "", tags: [], tagMatch: "any", favorite: null, archived: null, sort: "newest", limit: null }).some((item) => item.id === upload.item_id)).toBe(true);
    const pinned = items.updateItemState(upload.item_id, { pinned: true });
    expect(pinned.pinned).toBe(true);
  });

  it("imports up to five html files and rejects a sixth", () => {
    const settings = tempWorkspace();
    const upload = new UploadService(settings);
    const files = Array.from({ length: 5 }, (_, index) => ({
      filename: `batch-${index}.html`,
      content: Buffer.from(`<!doctype html><html><head><title>N${index}</title></head><body><p>Hi</p></body></html>`, "utf8"),
    }));
    expect(upload.importHtmlFiles(files).length).toBe(5);
    expect(() => upload.importHtmlFiles([...files, { filename: "batch-6.html", content: Buffer.from("<p>x</p>") }])).toThrow(/at most 5/);
  });
});
