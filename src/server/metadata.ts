import fs from "node:fs";
import path from "node:path";
import { parseSimpleYaml } from "@/server/yaml";

export class MetadataStore {
  constructor(readonly items: Record<string, Record<string, unknown>>) {}

  static load(metaDir: string | null): MetadataStore {
    if (!metaDir || !fs.existsSync(metaDir)) return new MetadataStore({});
    const itemsRoot = path.join(metaDir, "items");
    if (!fs.existsSync(itemsRoot)) return new MetadataStore({});

    const items: Record<string, Record<string, unknown>> = {};
    for (const filePath of walkYaml(itemsRoot).sort()) {
      const data = readYaml(filePath);
      const itemId = String(data.id || metadataPathToItemId(filePath, itemsRoot));
      items[itemId] = normalizeMetadata(data);
    }
    return new MetadataStore(items);
  }

  forItem(itemId: string): Record<string, unknown> {
    return { ...(this.items[itemId] ?? {}) };
  }
}

function walkYaml(root: string): string[] {
  const found: string[] = [];
  const stack = [root];
  while (stack.length) {
    const current = stack.pop()!;
    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      const full = path.join(current, entry.name);
      if (entry.isDirectory()) stack.push(full);
      else if (entry.isFile() && entry.name.endsWith(".yml")) found.push(full);
    }
  }
  return found;
}

function readYaml(filePath: string): Record<string, unknown> {
  const data = parseSimpleYaml(fs.readFileSync(filePath, "utf8"));
  if (!data || typeof data !== "object" || Array.isArray(data)) {
    throw new Error(`Metadata file must contain a mapping: ${filePath}`);
  }
  return data;
}

function metadataPathToItemId(filePath: string, itemsRoot: string): string {
  const relative = path.relative(itemsRoot, filePath).replace(/\\/g, "/");
  return relative.replace(/\.yml$/i, ".html");
}

function normalizeMetadata(data: Record<string, unknown>): Record<string, unknown> {
  const normalized = { ...data };
  if ("tags" in normalized) normalized.tags = normalizeSidecarTags(normalized.tags);
  return normalized;
}

function normalizeSidecarTags(value: unknown): string[] {
  if (value == null) return [];
  if (typeof value === "string") {
    return value.split(",").map((tag) => tag.trim()).filter(Boolean);
  }
  if (Array.isArray(value)) {
    return value.map((tag) => String(tag).trim()).filter(Boolean);
  }
  return [];
}
