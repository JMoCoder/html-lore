import fs from "node:fs";
import path from "node:path";
import { buildItem, buildManifest } from "@/server/manifest";
import { cachedManifest, invalidateManifestCache, manifestCacheKey } from "@/server/manifest-cache";
import { MetadataStore } from "@/server/metadata";
import { dumpSimpleYaml } from "@/server/yaml";
import { ensureWithin, metadataPathForItem, removeEmptyParents, writeFileDurable } from "@/server/paths";
import { NavigationConfigService } from "@/server/navigation";
import type { ServerSettings } from "@/server/settings";
import type { Item, ItemQuery } from "@/server/types";
import type { NavConfig } from "@/lib/navigation";

export const VALID_LIBRARY_FILTERS = new Set(["all", "inbox", "recent", "favorites", "generated", "imported", "archived"]);
export const VALID_SORT_MODES = new Set(["created-newest", "created-oldest", "newest", "oldest", "title-az", "title-za"]);
export const VALID_TAG_MATCH_MODES = new Set(["any", "all"]);

export class ItemContentError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ItemContentError";
  }
}
export class ItemContentUpdateError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ItemContentUpdateError";
  }
}
export class ItemMetadataError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ItemMetadataError";
  }
}
export class ItemStateError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ItemStateError";
  }
}
export class ItemDeleteError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ItemDeleteError";
  }
}
export class TaxonomyError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "TaxonomyError";
  }
}

export class ItemService {
  constructor(readonly settings: ServerSettings) {}

  manifest() {
    return cachedManifest(manifestCacheKey(this.settings.contentDir, this.settings.metaDir, this.settings.siteTitle), () =>
      buildManifest(this.settings.contentDir, this.settings.metaDir, this.settings.siteTitle),
    );
  }

  listItems(query: ItemQuery): Item[] {
    let items = [...this.manifest().items];
    items = applyLibraryFilter(items, query.library);
    items = applyCollectionFilter(items, query.collection);
    items = applyTagFilter(items, query.tags, query.tagMatch);
    items = applyBooleanFilter(items, "favorite", query.favorite);
    items = applyArchiveFilter(items, query.library, query.archived);
    items = applySearchFilter(items, query.q);
    items = sortItems(items, query.sort);
    if (query.limit != null) items = items.slice(0, query.limit);
    return items;
  }

  searchItems(query: ItemQuery) {
    const items = this.listItems(query);
    return {
      query: query.q,
      count: items.length,
      items: items.map((item) => buildSearchResult(item, query.q)),
    };
  }

  getItem(itemId: string): Item | null {
    const contentPath = this.resolveExistingContentPath(itemId);
    if (contentPath) {
      return buildItem(contentPath, this.settings.contentDir, MetadataStore.loadForItem(this.settings.metaDir, itemId), {
        includeText: false,
      });
    }
    return this.manifest().items.find((item) => item.id === itemId) ?? null;
  }

  getItemContentPath(itemId: string): string {
    const direct = this.resolveExistingContentPath(itemId);
    if (direct) return direct;
    const item = this.manifest().items.find((row) => row.id === itemId);
    if (!item) throw new ItemContentError("Item not found.");
    const fromManifest = path.join(this.settings.contentDir, item.path.replace(/^content\//, ""));
    ensureWithin(fromManifest, this.settings.contentDir);
    if (!fs.existsSync(fromManifest) || !fs.statSync(fromManifest).isFile()) {
      throw new ItemContentError("Item content not found.");
    }
    return fromManifest;
  }

  statItemContent(itemId: string): { path: string; size: number; mtimeMs: number } {
    const contentPath = this.getItemContentPath(itemId);
    const stat = fs.statSync(contentPath);
    return { path: contentPath, size: stat.size, mtimeMs: stat.mtimeMs };
  }

  readItemContent(itemId: string): string {
    return fs.readFileSync(this.getItemContentPath(itemId), "utf8");
  }

  private resolveExistingContentPath(itemId: string): string | null {
    const contentPath = path.join(this.settings.contentDir, itemId);
    try {
      ensureWithin(contentPath, this.settings.contentDir);
    } catch {
      return null;
    }
    if (!fs.existsSync(contentPath) || !fs.statSync(contentPath).isFile()) return null;
    return contentPath;
  }

  updateItemContent(itemId: string, content: unknown): Item {
    const item = this.getItem(itemId);
    if (!item) throw new ItemContentUpdateError("Item not found.");
    if (item.archived) throw new ItemContentUpdateError("Archived items cannot be edited.");
    if (typeof content !== "string") throw new ItemContentUpdateError("Content must be a string.");
    if (!content.trim()) throw new ItemContentUpdateError("Content cannot be empty.");
    if (content.includes("\0")) throw new ItemContentUpdateError("Content cannot contain null bytes.");
    if (Buffer.byteLength(content, "utf8") > this.settings.maxUploadBytes) {
      throw new ItemContentUpdateError("Content exceeds the configured upload size limit.");
    }
    const contentPath = this.getItemContentPath(itemId);
    this.preserveItemDatesForContentEdit(itemId, item);
    writeFileDurable(contentPath, content, this.settings.contentDir);
    invalidateManifestCache();
    const stored = fs.readFileSync(contentPath, "utf8");
    if (stored !== content) throw new ItemContentUpdateError("Content was not persisted.");
    const updated = this.getItem(itemId);
    if (!updated) throw new ItemContentUpdateError("Updated item not found.");
    return updated;
  }

  preserveItemDatesForContentEdit(itemId: string, item: Item): void {
    if (!this.settings.metaDir) return;
    const metadataPath = metadataPathForItem(this.settings.metaDir, itemId);
    if (!metadataPath) return;
    ensureWithin(metadataPath, this.settings.metaDir);
    fs.mkdirSync(path.dirname(metadataPath), { recursive: true });
    const existing = MetadataStore.load(this.settings.metaDir).forItem(itemId);
    const values = Object.fromEntries(
      Object.entries({
        ...existing,
        id: itemId,
        created: existing.created || item.created,
        updated: existing.updated || item.updated || item.created,
      }).filter(([, value]) => value != null),
    );
    fs.writeFileSync(metadataPath, dumpSimpleYaml(values), "utf8");
  }

  updateItemMetadata(itemId: string, values: Record<string, unknown>): Item {
    const item = this.getItem(itemId);
    if (!item) throw new ItemMetadataError("Item not found.");
    if (item.archived) throw new ItemMetadataError("Archived items cannot be edited.");
    return this.writeItemMetadata(itemId, item, {
      title: normalizeMetadataText(values.title) || item.title || "Untitled",
      summary: normalizeMetadataText(values.summary),
      collection: normalizeMetadataText(values.collection) || item.collection || "Inbox",
      tags: normalizeTags(
        Array.isArray(values.tags) ? values.tags : typeof values.tags === "string" ? values.tags : [],
      ),
    });
  }

  updateItemState(itemId: string, values: Record<string, unknown>): Item {
    const item = this.getItem(itemId);
    if (!item) throw new ItemStateError("Item not found.");
    const state: Record<string, boolean> = {};
    for (const key of ["favorite", "archived", "pinned"] as const) {
      if (key in values) {
        if (typeof values[key] !== "boolean") throw new ItemStateError(`${key} must be a boolean.`);
        state[key] = values[key];
      }
    }
    if (!Object.keys(state).length) throw new ItemStateError("No state fields provided.");
    return this.writeItemMetadata(itemId, item, state);
  }

  writeItemMetadata(itemId: string, item: Item, values: Record<string, unknown>): Item {
    if (!this.settings.metaDir) throw new ItemMetadataError("Metadata directory is not configured.");
    const metadataPath = metadataPathForItem(this.settings.metaDir, itemId);
    if (!metadataPath) throw new ItemMetadataError("Metadata directory is not configured.");
    ensureWithin(metadataPath, this.settings.metaDir);
    fs.mkdirSync(path.dirname(metadataPath), { recursive: true });
    const existing = MetadataStore.load(this.settings.metaDir).forItem(itemId);
    const metadata: Record<string, unknown> = {
      ...item,
      ...existing,
      ...values,
      id: itemId,
      updated: new Date().toISOString(),
    };
    delete metadata.path;
    delete metadata.text;
    if (metadata.source_url == null) delete metadata.source_url;
    fs.writeFileSync(metadataPath, dumpSimpleYaml(metadata), "utf8");
    invalidateManifestCache();
    const updated = this.getItem(itemId);
    if (!updated) throw new ItemMetadataError("Updated item not found.");
    return updated;
  }

  deleteItem(itemId: string): { id: string; deleted: true } {
    const item = this.getItem(itemId);
    if (!item) throw new ItemDeleteError("Item not found.");
    if (!item.archived) throw new ItemDeleteError("Only archived items can be permanently deleted.");
    const contentPath = path.join(this.settings.contentDir, itemId);
    ensureWithin(contentPath, this.settings.contentDir);
    if (fs.existsSync(contentPath)) fs.unlinkSync(contentPath);
    const metadataPath = metadataPathForItem(this.settings.metaDir, itemId);
    if (metadataPath && fs.existsSync(metadataPath)) {
      fs.unlinkSync(metadataPath);
      if (this.settings.metaDir) {
        removeEmptyParents(path.dirname(metadataPath), path.join(this.settings.metaDir, "items"));
      }
    }
    invalidateManifestCache();
    return { id: itemId, deleted: true };
  }

  renameCollection(from: string, to: string): { from: string; to: string; updated: number } {
    const source = normalizeMetadataText(from);
    const target = normalizeMetadataText(to);
    if (!source) throw new TaxonomyError("Current collection name is required.");
    if (!target) throw new TaxonomyError("New collection name cannot be empty.");
    if (source === target) return { from: source, to: target, updated: 0 };
    const items = this.manifest().items.filter((item) => item.collection === source);
    for (const item of items) {
      this.writeItemMetadata(item.id, item, { collection: target });
    }
    this.relabelNav("collections", source, target);
    return { from: source, to: target, updated: items.length };
  }

  renameTag(from: string, to: string): { from: string; to: string; updated: number } {
    const source = normalizeTags([from])[0];
    const target = normalizeTags([to])[0];
    if (!source) throw new TaxonomyError("Current tag name is required.");
    if (!target) throw new TaxonomyError("New tag name cannot be empty.");
    if (source === target) return { from: source, to: target, updated: 0 };
    const items = this.manifest().items.filter((item) => item.tags.includes(source));
    for (const item of items) {
      const tags = [...new Set(item.tags.map((tag) => (tag === source ? target : tag)))];
      this.writeItemMetadata(item.id, item, { tags });
    }
    this.relabelNav("tags", source, target);
    return { from: source, to: target, updated: items.length };
  }

  private relabelNav(section: keyof NavConfig, from: string, to: string): void {
    const nav = new NavigationConfigService(this.settings);
    const config = nav.getConfig();
    const current = config[section][from];
    if (!current && !config[section][to]) return;
    const nextSection = { ...config[section] };
    if (current) {
      nextSection[to] = { ...current, ...nextSection[to] };
      delete nextSection[from];
    }
    nav.updateConfig({ ...config, [section]: nextSection });
  }
}

export function normalizeQuery(input: {
  q?: string;
  library?: string;
  collection?: string;
  tags?: string | string[] | Iterable<string>;
  tag_match?: string;
  favorite?: boolean | null;
  archived?: boolean | null;
  sort?: string;
  limit?: number | null;
}): ItemQuery {
  const library = VALID_LIBRARY_FILTERS.has(input.library ?? "") ? input.library! : "all";
  const tagMatch = VALID_TAG_MATCH_MODES.has(input.tag_match ?? "") ? input.tag_match! : "any";
  const sort = VALID_SORT_MODES.has(input.sort ?? "") ? input.sort! : "created-newest";
  const limit = input.limit == null || input.limit > 0 ? (input.limit ?? null) : null;
  return {
    q: (input.q ?? "").trim(),
    library,
    collection: (input.collection ?? "").trim(),
    tags: normalizeTags(input.tags ?? ""),
    tagMatch,
    favorite: input.favorite ?? null,
    archived: input.archived ?? null,
    sort,
    limit,
  };
}

export function normalizeTags(tags: string | Iterable<unknown>): string[] {
  const values = typeof tags === "string" ? tags.split(",") : [...tags];
  return values
    .map((value) => String(value).trim().replace(/^#+/, ""))
    .filter(Boolean);
}

export function normalizeMetadataText(value: unknown): string {
  return String(value ?? "").trim();
}

export function applyLibraryFilter(items: Item[], library: string): Item[] {
  if (library === "all" || library === "recent") return items;
  if (library === "inbox") return items.filter((item) => (item.collection || "Inbox") === "Inbox");
  if (library === "favorites") return items.filter((item) => item.favorite);
  if (library === "generated") {
    return items.filter((item) => Boolean(item.agent?.generated) || item.source_type === "topic");
  }
  if (library === "imported") return items.filter((item) => item.source_type === "imported" || item.source_type === "html");
  if (library === "archived") return items.filter((item) => item.archived);
  return items;
}

export function applyCollectionFilter(items: Item[], collection: string): Item[] {
  if (!collection) return items;
  return items.filter((item) => item.collection === collection);
}

export function applyTagFilter(items: Item[], tags: string[], tagMatch: string): Item[] {
  if (!tags.length) return items;
  const selected = new Set(tags);
  if (tagMatch === "all") {
    return items.filter((item) => tags.every((tag) => item.tags.includes(tag)));
  }
  return items.filter((item) => item.tags.some((tag) => selected.has(tag)));
}

export function applyBooleanFilter(items: Item[], field: "favorite" | "archived", value: boolean | null): Item[] {
  if (value == null) return items;
  return items.filter((item) => Boolean(item[field]) === value);
}

export function applyArchiveFilter(items: Item[], library: string, archived: boolean | null): Item[] {
  if (archived != null) return items.filter((item) => item.archived === archived);
  if (library === "archived") return items;
  return items.filter((item) => !item.archived);
}

export function applySearchFilter(items: Item[], query: string): Item[] {
  if (!query) return items;
  const needle = query.toLowerCase();
  return items.filter((item) => searchableText(item).includes(needle));
}

function searchableText(item: Item): string {
  return [item.title, item.summary, item.path, item.collection, item.source_type, item.text, ...item.tags]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();
}

function buildSearchResult(item: Item, query: string) {
  return {
    item,
    score: scoreSearchResult(item, query),
    matches: searchMatches(item, query),
    snippet: searchSnippet(item, query),
  };
}

export function scoreSearchResult(item: Item, query: string): number {
  if (!query) return 0;
  const needle = query.toLowerCase();
  let score = 0;
  if ((item.title || "").toLowerCase().includes(needle)) score += 30;
  if ((item.summary || "").toLowerCase().includes(needle)) score += 20;
  if ((item.collection || "").toLowerCase().includes(needle)) score += 10;
  if (item.tags.join(" ").toLowerCase().includes(needle)) score += 10;
  if ((item.path || "").toLowerCase().includes(needle)) score += 5;
  if ((item.text || "").toLowerCase().includes(needle)) score += 8;
  return score;
}

export function searchMatches(item: Item, query: string): string[] {
  if (!query) return [];
  const needle = query.toLowerCase();
  const fields: Record<string, string> = {
    title: item.title,
    summary: item.summary,
    collection: item.collection,
    tags: item.tags.join(" "),
    path: item.path,
    text: item.text,
  };
  return Object.entries(fields)
    .filter(([, value]) => String(value || "").toLowerCase().includes(needle))
    .map(([field]) => field);
}

export function searchSnippet(item: Item, query: string): string {
  const source = item.summary || item.text || item.title || "";
  if (!query) return source.slice(0, 180);
  const index = source.toLowerCase().indexOf(query.toLowerCase());
  if (index < 0) return source.slice(0, 180);
  const start = Math.max(0, index - 60);
  const end = Math.min(source.length, index + query.length + 120);
  return `${start > 0 ? "..." : ""}${source.slice(start, end).trim()}${end < source.length ? "..." : ""}`;
}

export function sortItems(items: Item[], sort: string): Item[] {
  return [...items].sort((a, b) => {
    const titleOrder = compareText(a.title, b.title);
    const titleDescOrder = compareText(b.title, a.title);
    const newestUpdated = compareText(b.updated, a.updated);
    const oldestUpdated = compareText(a.updated, b.updated);
    const newestCreated = compareText(b.created, a.created);
    const oldestCreated = compareText(a.created, b.created);
    if (sort === "created-oldest") return oldestCreated || titleOrder;
    if (sort === "oldest") return oldestUpdated || titleOrder;
    if (sort === "newest") return newestUpdated || titleOrder;
    if (sort === "title-az") return titleOrder || newestUpdated;
    if (sort === "title-za") return titleDescOrder || newestUpdated;
    return newestCreated || titleOrder;
  });
}

function compareText(left: unknown, right: unknown): number {
  const leftValue = String(left ?? "").toLowerCase();
  const rightValue = String(right ?? "").toLowerCase();
  if (leftValue < rightValue) return -1;
  if (leftValue > rightValue) return 1;
  return 0;
}
