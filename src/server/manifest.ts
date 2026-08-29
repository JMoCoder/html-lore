import fs from "node:fs";
import path from "node:path";
import { extractHtmlMetadata, extractPlainText, filenameToTitle, slugify } from "@/server/html-meta";
import { MetadataStore } from "@/server/metadata";
import type { Item, Manifest } from "@/server/types";

export function buildManifest(contentDir: string, metaDir: string | null, siteTitle = "HTMlore"): Manifest {
  const metadata = MetadataStore.load(metaDir);
  const items = listHtmlFiles(contentDir).sort().map((filePath) => buildItem(filePath, contentDir, metadata));
  const pinned = items.filter((item) => item.pinned).sort(manifestCompare);
  const unpinned = items.filter((item) => !item.pinned).sort(manifestCompare);

  return {
    version: 2,
    generated_at: new Date().toISOString(),
    site: { title: siteTitle, layout: "cards" },
    items: [...pinned, ...unpinned],
    collections: summarizeCollections(items),
    tags: summarizeTags(items),
  };
}

export function buildItem(filePath: string, contentDir: string, metadata: MetadataStore): Item {
  const relative = path.relative(contentDir, filePath).replace(/\\/g, "/");
  const html = fs.readFileSync(filePath, "utf8");
  const extracted = extractHtmlMetadata(html, filenameToTitle(path.parse(filePath).name));
  const sidecar = metadata.forItem(relative);
  const updated = new Date(fs.statSync(filePath).mtime).toISOString();
  const sourceType = String(sidecar.source_type || inferSourceType(relative));

  return {
    id: String(sidecar.id || relative),
    title: String(sidecar.title || extracted.title),
    summary: String(sidecar.summary || extracted.summary),
    path: `content/${relative}`,
    source_type: sourceType,
    source_url: sidecar.source_url == null ? null : String(sidecar.source_url),
    collection: String(sidecar.collection || inferCollection(relative)),
    tags: Array.isArray(sidecar.tags) ? sidecar.tags.map(String) : [],
    status: String(sidecar.status || "ready"),
    review_status: String(sidecar.review_status || "reviewed"),
    favorite: Boolean(sidecar.favorite),
    archived: Boolean(sidecar.archived),
    pinned: Boolean(sidecar.pinned),
    created: String(sidecar.created || updated),
    updated: String(sidecar.updated || updated),
    cover: sidecar.cover == null ? null : String(sidecar.cover),
    open_mode: String(sidecar.open_mode || "iframe"),
    agent: isPlainObject(sidecar.agent) ? sidecar.agent : { generated: sourceType === "topic" },
    text: extractPlainText(html),
  };
}

export function inferCollection(itemId: string): string {
  const first = itemId.split("/")[0] ?? itemId;
  if (first === itemId) return "Inbox";
  return filenameToTitle(first);
}

export function inferSourceType(itemId: string): string {
  if (itemId.startsWith("generated/")) return "topic";
  if (itemId.startsWith("imported/")) return "imported";
  return "html";
}

export function listHtmlFiles(contentDir: string): string[] {
  if (!fs.existsSync(contentDir)) return [];
  const found: string[] = [];
  const stack = [contentDir];
  while (stack.length) {
    const current = stack.pop()!;
    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      const full = path.join(current, entry.name);
      if (entry.isDirectory()) stack.push(full);
      else if (entry.isFile() && entry.name.endsWith(".html")) found.push(full);
    }
  }
  return found;
}

function summarizeCollections(items: Item[]): Manifest["collections"] {
  const counts = new Map<string, number>();
  for (const item of items) {
    const name = item.collection || "Inbox";
    counts.set(name, (counts.get(name) ?? 0) + 1);
  }
  return [...counts.entries()]
    .sort((a, b) => a[0].toLowerCase().localeCompare(b[0].toLowerCase()))
    .map(([name, count]) => ({ id: slugify(name), name, count }));
}

function summarizeTags(items: Item[]): Manifest["tags"] {
  const counts = new Map<string, number>();
  for (const item of items) {
    for (const tag of item.tags) counts.set(tag, (counts.get(tag) ?? 0) + 1);
  }
  return [...counts.entries()]
    .sort((a, b) => b[1] - a[1] || a[0].toLowerCase().localeCompare(b[0].toLowerCase()))
    .map(([name, count]) => ({ name, count }));
}

function manifestCompare(a: Item, b: Item): number {
  return b.updated.localeCompare(a.updated) || b.title.localeCompare(a.title);
}

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}
