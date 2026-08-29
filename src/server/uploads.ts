import fs from "node:fs";
import path from "node:path";
import { buildItem } from "@/server/manifest";
import { MetadataStore } from "@/server/metadata";
import { dumpSimpleYaml } from "@/server/yaml";
import { normalizeTags } from "@/server/items";
import { ensureWithin } from "@/server/paths";
import type { ServerSettings } from "@/server/settings";
import type { Item } from "@/server/types";

export const MAX_IMPORT_FILES = 5;

export class UploadError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "UploadError";
  }
}

export type UploadResult = {
  upload_id: string;
  item_id: string;
  status: string;
  item: Item;
};

export class UploadService {
  constructor(readonly settings: ServerSettings) {}

  importHtml(input: {
    filename: string;
    content: Buffer;
    title?: string;
    summary?: string;
    collection?: string;
    tags?: string | string[];
  }): UploadResult {
    validateHtmlUpload(input.filename, input.content, this.settings.maxUploadBytes);
    const now = new Date();
    const relativePath = this.nextImportPath(input.filename, now);
    const contentPath = path.join(this.settings.contentDir, relativePath);
    ensureWithin(contentPath, this.settings.contentDir);
    fs.mkdirSync(path.dirname(contentPath), { recursive: true });
    fs.writeFileSync(contentPath, input.content);

    const itemId = relativePath.replace(/\\/g, "/");
    const metadata = buildUploadMetadata({
      itemId,
      title: input.title ?? "",
      summary: input.summary ?? "",
      collection: input.collection ?? "",
      tags: input.tags ?? "",
      now,
    });
    this.writeMetadata(relativePath, metadata);
    const item = buildItem(contentPath, this.settings.contentDir, MetadataStore.load(this.settings.metaDir));
    const stamp = formatStamp(now);
    return {
      upload_id: `upl_${stamp}_${path.parse(contentPath).name}`,
      item_id: item.id,
      status: "indexed",
      item,
    };
  }

  importHtmlFiles(files: { filename: string; content: Buffer; title?: string; summary?: string; collection?: string; tags?: string | string[] }[]): UploadResult[] {
    if (!files.length) throw new UploadError("HTML file is required.");
    if (files.length > MAX_IMPORT_FILES) throw new UploadError(`You can import at most ${MAX_IMPORT_FILES} files at once.`);
    return files.map((file) => this.importHtml(file));
  }

  private nextImportPath(filename: string, now: Date): string {
    const stem = slugifyFilename(path.parse(filename).name);
    const relativeDir = path.join("imported", String(now.getUTCFullYear()), pad(now.getUTCMonth() + 1));
    let candidate = path.join(relativeDir, `${stem}.html`);
    let index = 2;
    while (fs.existsSync(path.join(this.settings.contentDir, candidate))) {
      candidate = path.join(relativeDir, `${stem}-${index}.html`);
      index += 1;
    }
    return candidate;
  }

  private writeMetadata(relativePath: string, metadata: Record<string, unknown>): void {
    if (!this.settings.metaDir) return;
    const target = path.join(this.settings.metaDir, "items", relativePath.replace(/\.html?$/i, ".yml"));
    ensureWithin(target, this.settings.metaDir);
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.writeFileSync(target, dumpSimpleYaml(metadata), "utf8");
  }
}

export function validateHtmlUpload(filename: string, content: Buffer, maxUploadBytes: number): void {
  if (!/\.html?$/i.test(filename)) throw new UploadError("Only .html and .htm files can be imported.");
  if (!content.length) throw new UploadError("Uploaded HTML file is empty.");
  if (content.length > maxUploadBytes) throw new UploadError("Uploaded HTML file exceeds the configured size limit.");
  if (content.subarray(0, 1024).includes(0)) throw new UploadError("Uploaded file does not look like HTML text.");
}

export function buildUploadMetadata(input: {
  itemId: string;
  title: string;
  summary: string;
  collection: string;
  tags: string | string[];
  now: Date;
}): Record<string, unknown> {
  const metadata: Record<string, unknown> = {
    id: input.itemId,
    source_type: "imported",
    collection: input.collection.trim() || "Inbox",
    tags: normalizeTags(input.tags),
    status: "ready",
    favorite: false,
    archived: false,
    pinned: false,
    open_mode: "iframe",
    created: input.now.toISOString(),
    updated: input.now.toISOString(),
  };
  if (input.title.trim()) metadata.title = input.title.trim();
  if (input.summary.trim()) metadata.summary = input.summary.trim();
  return metadata;
}

export function slugifyFilename(value: string): string {
  const normalized = value.trim().replace(/[^A-Za-z0-9._-]+/g, "-").replace(/^[-._]+|[-._]+$/g, "").toLowerCase();
  return normalized || "imported-note";
}

function pad(value: number): string {
  return String(value).padStart(2, "0");
}

function formatStamp(now: Date): string {
  return [
    now.getUTCFullYear(),
    pad(now.getUTCMonth() + 1),
    pad(now.getUTCDate()),
    pad(now.getUTCHours()),
    pad(now.getUTCMinutes()),
    pad(now.getUTCSeconds()),
  ].join("");
}
