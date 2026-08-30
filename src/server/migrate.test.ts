import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { describe, expect, it } from "vitest";
import { ItemService } from "@/server/items";
import { MigrateError, migrateFrom1x } from "../../scripts/migrate-from-1x.mjs";

function make1xNotebook() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "html-lore-1x-"));
  const content = path.join(root, "content");
  const metaItems = path.join(root, "meta", "items");
  const metaConfig = path.join(root, "meta", "config");
  const metaAi = path.join(root, "meta", "ai");
  const publicDir = path.join(root, "public");
  fs.mkdirSync(path.join(content, "imported"), { recursive: true });
  fs.mkdirSync(path.join(metaItems, "imported"), { recursive: true });
  fs.mkdirSync(metaConfig, { recursive: true });
  fs.mkdirSync(metaAi, { recursive: true });
  fs.mkdirSync(publicDir, { recursive: true });
  fs.writeFileSync(
    path.join(content, "imported", "note.html"),
    "<!doctype html><html><head><title>Keep me</title></head><body><p>hello</p></body></html>\n",
  );
  fs.writeFileSync(
    path.join(metaItems, "imported", "note.yml"),
    "id: imported/note.html\ntitle: Keep me\ncollection: Ops\ntags:\n  - Demo\n",
  );
  fs.writeFileSync(path.join(metaConfig, "shares.json"), JSON.stringify({ version: 1, shares: [] }, null, 2));
  fs.writeFileSync(path.join(metaConfig, "share-index.json"), JSON.stringify({ tokens: {} }, null, 2));
  fs.writeFileSync(path.join(metaConfig, "navigation.json"), JSON.stringify({ library: {}, collections: {}, tags: {} }, null, 2));
  fs.writeFileSync(path.join(metaConfig, "jobs.json"), JSON.stringify({ jobs: ["drop-me"] }, null, 2));
  fs.writeFileSync(path.join(metaConfig, "ai_provider.json"), JSON.stringify({ api_key: "secret" }, null, 2));
  fs.writeFileSync(path.join(metaAi, "conversations.json"), JSON.stringify({ conversations: [] }, null, 2));
  fs.writeFileSync(path.join(publicDir, "index.html"), "<html>v1 static</html>\n");
  fs.writeFileSync(
    path.join(root, "users.json"),
    JSON.stringify({ version: 1, users: [{ username: "admin", role: "admin", data_id: "default", enabled: true }] }, null, 2),
  );
  const extraUser = path.join(root, "users", "alice");
  fs.mkdirSync(path.join(extraUser, "content", "imported"), { recursive: true });
  fs.mkdirSync(path.join(extraUser, "meta", "items", "imported"), { recursive: true });
  fs.mkdirSync(path.join(extraUser, "public"), { recursive: true });
  fs.writeFileSync(path.join(extraUser, "content", "imported", "alice.html"), "<!doctype html><title>Alice</title>\n");
  fs.writeFileSync(path.join(extraUser, "meta", "items", "imported", "alice.yml"), "title: Alice\n");
  fs.writeFileSync(path.join(extraUser, "public", "index.html"), "skip\n");
  return root;
}

function settingsFor(dest: string) {
  return {
    contentDir: path.join(dest, "content"),
    metaDir: path.join(dest, "meta"),
    publicDir: path.join(dest, "public"),
    siteTitle: "HTMlore",
    maxUploadBytes: 1024 * 1024,
    apiToken: "",
    authUsername: "",
    authPassword: "",
    usersFile: path.join(dest, "users.json"),
    userDataDir: path.join(dest, "users"),
    sessionSecret: "",
    sessionCookieName: "html_lore_session",
    sessionMaxAgeSeconds: 604800,
    sessionSecure: false,
    shareInteractiveEnabled: true,
  };
}

describe("migrateFrom1x", () => {
  it("copies notebook files and skips 1.x AI/static rebuild artifacts", () => {
    const source = make1xNotebook();
    const dest = fs.mkdtempSync(path.join(os.tmpdir(), "html-lore-2x-"));
    const result = migrateFrom1x(source, dest);
    expect(result.htmlCount).toBe(1);
    expect(fs.existsSync(path.join(dest, "content", "imported", "note.html"))).toBe(true);
    expect(fs.existsSync(path.join(dest, "meta", "items", "imported", "note.yml"))).toBe(true);
    expect(fs.existsSync(path.join(dest, "meta", "config", "shares.json"))).toBe(true);
    expect(fs.existsSync(path.join(dest, "meta", "config", "navigation.json"))).toBe(true);
    expect(fs.existsSync(path.join(dest, "users.json"))).toBe(true);
    expect(fs.existsSync(path.join(dest, "users", "alice", "content", "imported", "alice.html"))).toBe(true);
    expect(fs.existsSync(path.join(dest, "public"))).toBe(false);
    expect(fs.existsSync(path.join(dest, "meta", "ai"))).toBe(false);
    expect(fs.existsSync(path.join(dest, "meta", "config", "jobs.json"))).toBe(false);
    expect(fs.existsSync(path.join(dest, "meta", "config", "ai_provider.json"))).toBe(false);
    expect(fs.existsSync(path.join(dest, "users", "alice", "public"))).toBe(false);
    expect(result.skipped.some((row) => row.includes("meta/ai"))).toBe(true);
    const items = new ItemService(settingsFor(dest)).listItems({
      q: "",
      library: "all",
      collection: "",
      tags: [],
      tagMatch: "any",
      favorite: null,
      archived: null,
      sort: "newest",
      limit: null,
    });
    expect(items.some((item) => item.id === "imported/note.html")).toBe(true);
  });

  it("refuses to overwrite an existing 2.0 notebook unless forced", () => {
    const source = make1xNotebook();
    const dest = fs.mkdtempSync(path.join(os.tmpdir(), "html-lore-2x-"));
    migrateFrom1x(source, dest);
    expect(() => migrateFrom1x(source, dest)).toThrow(MigrateError);
    const again = migrateFrom1x(source, dest, { force: true });
    expect(again.htmlCount).toBe(1);
  });

  it("merges user libraries into the dest root for no-login 2.0", () => {
    const source = make1xNotebook();
    fs.writeFileSync(
      path.join(source, "users", "alice", "meta", "items", "imported", "alice.yml"),
      "title: Alice\ntags:\n  - Demo\n  - AI生成\n",
    );
    fs.mkdirSync(path.join(source, "users", "alice", "meta", "config"), { recursive: true });
    fs.writeFileSync(
      path.join(source, "users", "alice", "meta", "config", "shares.json"),
      JSON.stringify({ version: 1, shares: [{ id: "share_alice", item_id: "imported/alice.html", revoked: false }] }, null, 2),
    );
    fs.writeFileSync(
      path.join(source, "meta", "config", "share-index.json"),
      JSON.stringify({ tokens: { "tok-alice": "alice" } }, null, 2),
    );
    const dest = fs.mkdtempSync(path.join(os.tmpdir(), "html-lore-2x-merge-"));
    const result = migrateFrom1x(source, dest, { mergeUsers: true });
    expect(result.htmlCount).toBe(2);
    expect(fs.existsSync(path.join(dest, "content", "imported", "note.html"))).toBe(true);
    expect(fs.existsSync(path.join(dest, "content", "imported", "alice.html"))).toBe(true);
    expect(fs.existsSync(path.join(dest, "users.json"))).toBe(false);
    expect(fs.existsSync(path.join(dest, "users"))).toBe(false);
    const aliceYml = fs.readFileSync(path.join(dest, "meta", "items", "imported", "alice.yml"), "utf8");
    expect(aliceYml).toContain("Demo");
    expect(aliceYml).not.toContain("AI生成");
    const shares = JSON.parse(fs.readFileSync(path.join(dest, "meta", "config", "shares.json"), "utf8")) as {
      shares: { id: string }[];
    };
    expect(shares.shares.some((row) => row.id === "share_alice")).toBe(true);
    const index = JSON.parse(fs.readFileSync(path.join(dest, "meta", "config", "share-index.json"), "utf8")) as {
      tokens: Record<string, string>;
    };
    expect(Object.values(index.tokens).every((dataId) => dataId === "default")).toBe(true);
    const items = new ItemService(settingsFor(dest)).listItems({
      q: "",
      library: "all",
      collection: "",
      tags: [],
      tagMatch: "any",
      favorite: null,
      archived: null,
      sort: "newest",
      limit: null,
    });
    expect(items.some((item) => item.id === "imported/alice.html")).toBe(true);
    expect(items.some((item) => item.tags.includes("AI生成"))).toBe(false);
  });

  it("aborts --merge-users when two notebooks share the same note path", () => {
    const source = make1xNotebook();
    fs.mkdirSync(path.join(source, "users", "alice", "content", "imported"), { recursive: true });
    fs.writeFileSync(path.join(source, "users", "alice", "content", "imported", "note.html"), "<title>Clash</title>\n");
    const dest = fs.mkdtempSync(path.join(os.tmpdir(), "html-lore-2x-clash-"));
    expect(() => migrateFrom1x(source, dest, { mergeUsers: true })).toThrow(/Path collision/);
  });

  it("runs as a node CLI", () => {
    const source = make1xNotebook();
    const dest = fs.mkdtempSync(path.join(os.tmpdir(), "html-lore-2x-cli-"));
    const output = execFileSync(process.execPath, ["scripts/migrate-from-1x.mjs", source, dest], {
      encoding: "utf8",
      cwd: process.cwd(),
    });
    const parsed = JSON.parse(output) as { ok: boolean; htmlCount: number };
    expect(parsed.ok).toBe(true);
    expect(parsed.htmlCount).toBe(1);
    expect(fs.existsSync(path.join(dest, "content", "imported", "note.html"))).toBe(true);
  });
});
