import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { buildItem } from "@/server/manifest";
import { invalidateManifestCache } from "@/server/manifest-cache";
import { MetadataStore } from "@/server/metadata";
import { dumpSimpleYaml } from "@/server/yaml";
import { ItemContentError, ItemService } from "@/server/items";
import { ensureWithin, metadataPathForItem } from "@/server/paths";
import type { ServerSettings } from "@/server/settings";
import { forUser } from "@/server/settings";
import {
  INTERACTIVE_SHARE_MODE,
  SAFE_SHARE_MODE,
  SHARE_DURATIONS,
  SHARE_MODES,
  ShareError,
  ShareSafetyConfirmationError,
  ShareSafetyError,
  buildSafeShareCopy,
  nextSafeShareCopyPath,
  sanitizeSharedHtml,
  scanInteractiveShareContent,
  scanShareContent,
} from "@/server/share-safety";

export { ShareError, ShareSafetyConfirmationError, ShareSafetyError, SAFE_SHARE_MODE, INTERACTIVE_SHARE_MODE };

export type ShareRecord = Record<string, unknown>;

export class ShareService {
  readonly itemService: ItemService;
  readonly rootSettings: ServerSettings;

  constructor(
    readonly settings: ServerSettings,
    rootSettings?: ServerSettings,
  ) {
    this.rootSettings = rootSettings ?? settings;
    this.itemService = new ItemService(settings);
  }

  listShares() {
    return this.readStore()
      .shares.filter((record) => !record.deleted)
      .map(publicShare);
  }

  createShare(input: {
    itemId: string;
    duration: string;
    mode?: string;
    confirmPrivateReferences?: boolean;
  }) {
    if (!(input.duration in SHARE_DURATIONS)) throw new ShareError("Invalid share duration.");
    const mode = normalizeShareMode(input.mode);
    const item = this.itemService.getItem(input.itemId);
    if (!item) throw new ShareError("Item not found.");
    if (item.archived) throw new ShareError("Archived items cannot be shared.");

    let content: string;
    try {
      content = this.itemService.readItemContent(input.itemId);
    } catch (error) {
      if (error instanceof ItemContentError) throw new ShareError(error.message);
      throw error;
    }

    let contentItemId = input.itemId;
    let repair: Record<string, unknown> = {};
    let scan: Record<string, unknown>;
    if (mode === SAFE_SHARE_MODE) {
      const originalScan = scanShareContent(content);
      if (originalScan.shareable) {
        scan = originalScan;
      } else {
        const repaired = this.createSafeShareCopy(item, content, originalScan);
        contentItemId = repaired.item_id;
        scan = repaired.safety;
        repair = repaired.repair;
      }
    } else {
      if (!this.settings.shareInteractiveEnabled) {
        throw new ShareError("Interactive sharing is disabled by this deployment.");
      }
      scan = scanInteractiveShareContent(content);
      if (!scan.shareable) throw new ShareSafetyError(scan);
      if (scan.requires_confirmation && !input.confirmPrivateReferences) {
        throw new ShareSafetyConfirmationError(scan);
      }
    }

    const token = crypto.randomBytes(24).toString("base64url");
    const tokenHash = hashToken(token);
    const urlPath = `/share/${token}`;
    const now = new Date().toISOString();
    const data = this.readStore();
    const existing = activeShareForItem(data, input.itemId);
    if (existing) {
      existing.revoked = true;
      existing.updated_at = now;
      this.deleteStaticShareShell(String(existing.url_path || ""));
    }
    const record: ShareRecord = {
      id: `share_${crypto.randomBytes(8).toString("base64url")}`,
      token_hash: tokenHash,
      url_path: urlPath,
      item_id: input.itemId,
      content_item_id: contentItemId,
      mode,
      duration: input.duration,
      created_at: now,
      updated_at: now,
      expires_at: expiresAtFor(input.duration, now),
      revoked: false,
      access_count: 0,
      last_accessed_at: "",
      safety: scan,
      repair,
    };
    data.shares.push(record);
    this.writeStore(data);
    this.indexToken(tokenHash);
    return { share: publicShare(record), token, url_path: urlPath };
  }

  updateShare(shareId: string, values: Record<string, unknown>) {
    const data = this.readStore();
    const record = findShare(data, shareId);
    if (!record) throw new ShareError("Share not found.");
    const isRevoking = values.revoked === true;
    if ("revoked" in values) {
      if (typeof values.revoked !== "boolean") throw new ShareError("revoked must be a boolean.");
      if (values.revoked === false) throw new ShareError("Revoked shares cannot be reactivated.");
    }
    if (!isShareActive(record) && !isRevoking) throw new ShareError("Inactive shares cannot be updated.");
    if ("duration" in values) {
      const duration = String(values.duration || "");
      if (!(duration in SHARE_DURATIONS)) throw new ShareError("Invalid share duration.");
      record.duration = duration;
      record.expires_at = expiresAtFor(duration, new Date().toISOString());
    }
    if (values.revoked === true) {
      record.revoked = true;
      this.deleteStaticShareShell(String(record.url_path || ""));
    }
    record.updated_at = new Date().toISOString();
    this.writeStore(data);
    return publicShare(record);
  }

  revokeShare(shareId: string) {
    return this.updateShare(shareId, { revoked: true });
  }

  activeShareForItem(itemId: string) {
    return activeShareForItem(this.readStore(), itemId);
  }

  publicReadByToken(token: string) {
    const record = this.findByTokenHash(hashToken(token));
    if (!record || !isShareActive(record)) throw new ShareError("Share not found.");
    const item = this.itemService.getItem(String(record.item_id || ""));
    if (!item || item.archived) throw new ShareError("Share not found.");
    const contentItemId = String(record.content_item_id || record.item_id);
    const mode = shareModeForRecord(record);
    if (mode === INTERACTIVE_SHARE_MODE && !this.settings.shareInteractiveEnabled) {
      throw new ShareError("Share not found.");
    }
    let content: string;
    try {
      content = this.itemService.readItemContent(contentItemId);
    } catch {
      throw new ShareError("Share not found.");
    }
    const scan = mode === SAFE_SHARE_MODE ? scanShareContent(content) : scanInteractiveShareContent(content);
    if (!scan.shareable) {
      record.revoked = true;
      record.updated_at = new Date().toISOString();
      record.safety = scan;
      this.updateRecord(record);
      throw new ShareError("Share not found.");
    }
    const rendered = mode === SAFE_SHARE_MODE ? sanitizeSharedHtml(content) : { body_html: content, styles: "" };
    record.access_count = Number(record.access_count || 0) + 1;
    record.last_accessed_at = new Date().toISOString();
    this.updateRecord(record);
    return {
      share: publicShareRead(record),
      item: {
        title: item.title || "Untitled",
        summary: item.summary || "",
        updated: item.updated || "",
      },
      html: rendered.body_html,
      styles: rendered.styles,
    };
  }

  private createSafeShareCopy(item: { id: string; title: string; summary: string }, content: string, originalScan: { reasons: string[] }) {
    const repairedContent = buildSafeShareCopy(content);
    const repairedScan = scanShareContent(repairedContent);
    if (!repairedScan.shareable) {
      throw new ShareSafetyError({
        shareable: false,
        reasons: [...new Set([...originalScan.reasons, ...repairedScan.reasons, "safe-copy-failed"])].sort(),
      });
    }
    const relativePath = nextSafeShareCopyPath(this.settings.contentDir, item.id).replace(/\\/g, "/");
    const contentPath = path.join(this.settings.contentDir, relativePath);
    ensureWithin(contentPath, this.settings.contentDir);
    fs.mkdirSync(path.dirname(contentPath), { recursive: true });
    fs.writeFileSync(contentPath, repairedContent, "utf8");
    const now = new Date().toISOString();
    const sourceMetadata = MetadataStore.load(this.settings.metaDir).forItem(item.id);
    const metadata: Record<string, unknown> = {
      ...sourceMetadata,
      id: relativePath,
      title: `${item.title || "Untitled"} - Safe share copy`,
      summary: item.summary || "",
      source_type: "share-safety-copy",
      status: "ready",
      favorite: false,
      archived: false,
      pinned: false,
      open_mode: "iframe",
      created: now,
      updated: now,
      share_safety: {
        source_item_id: item.id,
        repair_engine: "deterministic",
        original_reasons: originalScan.reasons,
      },
    };
    delete metadata.path;
    if (this.settings.metaDir) {
      const metadataPath = metadataPathForItem(this.settings.metaDir, relativePath);
      if (metadataPath) {
        ensureWithin(metadataPath, this.settings.metaDir);
        fs.mkdirSync(path.dirname(metadataPath), { recursive: true });
        fs.writeFileSync(metadataPath, dumpSimpleYaml(metadata), "utf8");
      }
    }
    invalidateManifestCache();
    const copiedItem = buildItem(contentPath, this.settings.contentDir, MetadataStore.load(this.settings.metaDir));
    return {
      item_id: copiedItem.id,
      safety: repairedScan,
      repair: {
        created: true,
        engine: "deterministic",
        source_item_id: item.id,
        copy_item_id: copiedItem.id,
        original_reasons: originalScan.reasons,
      },
    };
  }

  private findByTokenHash(tokenHash: string): ShareRecord | null {
    for (const record of this.readStore().shares) {
      if (timingEqual(String(record.token_hash || ""), tokenHash)) return record;
    }
    return null;
  }

  private updateRecord(record: ShareRecord): void {
    const data = this.readStore();
    const existing = findShare(data, String(record.id || ""));
    if (existing) {
      Object.assign(existing, record);
      this.writeStore(data);
    }
  }

  private readStore(): { version: number; shares: ShareRecord[] } {
    const storePath = shareStorePath(this.settings);
    if (!fs.existsSync(storePath)) return { version: 1, shares: [] };
    try {
      const data = JSON.parse(fs.readFileSync(storePath, "utf8")) as { version?: number; shares?: ShareRecord[] };
      if (!data || typeof data !== "object") return { version: 1, shares: [] };
      return { version: data.version ?? 1, shares: data.shares ?? [] };
    } catch {
      return { version: 1, shares: [] };
    }
  }

  private writeStore(data: { version: number; shares: ShareRecord[] }): void {
    const storePath = shareStorePath(this.settings);
    ensureWithin(storePath, this.settings.metaDir || this.settings.publicDir);
    fs.mkdirSync(path.dirname(storePath), { recursive: true });
    fs.writeFileSync(storePath, JSON.stringify(data, null, 2), "utf8");
  }

  private indexToken(tokenHash: string): void {
    const indexPath = shareIndexPath(this.rootSettings);
    fs.mkdirSync(path.dirname(indexPath), { recursive: true });
    let data: { version: number; tokens: Record<string, string> } = { version: 1, tokens: {} };
    if (fs.existsSync(indexPath)) {
      try {
        data = JSON.parse(fs.readFileSync(indexPath, "utf8"));
        data.tokens ??= {};
      } catch {
        data = { version: 1, tokens: {} };
      }
    }
    data.tokens[tokenHash] = dataIdForSettings(this.rootSettings, this.settings);
    fs.writeFileSync(indexPath, JSON.stringify(data, null, 2), "utf8");
  }

  private deleteStaticShareShell(urlPath: string): void {
    const token = tokenFromUrlPath(urlPath);
    if (!token) return;
    const shareDir = path.resolve(this.settings.publicDir, "share", token);
    ensureWithin(shareDir, this.settings.publicDir);
    fs.rmSync(shareDir, { recursive: true, force: true });
  }
}

export function publicShare(record: ShareRecord) {
  return {
    id: record.id,
    item_id: record.item_id,
    content_item_id: record.content_item_id || record.item_id,
    mode: shareModeForRecord(record),
    duration: record.duration,
    created_at: record.created_at,
    updated_at: record.updated_at,
    expires_at: record.expires_at,
    url_path: record.url_path || "",
    revoked: Boolean(record.revoked),
    active: isShareActive(record),
    access_count: Number(record.access_count || 0),
    last_accessed_at: record.last_accessed_at || "",
    safety: record.safety || { shareable: true, reasons: [] },
    repair: record.repair || {},
  };
}

function publicShareRead(record: ShareRecord) {
  return {
    active: isShareActive(record),
    expires_at: record.expires_at || "",
    mode: shareModeForRecord(record),
  };
}

function findShare(data: { shares: ShareRecord[] }, shareId: string) {
  return data.shares.find((record) => record.id === shareId) ?? null;
}

function activeShareForItem(data: { shares: ShareRecord[] }, itemId: string) {
  return data.shares.find((record) => record.item_id === itemId && isShareActive(record)) ?? null;
}

function shareStorePath(settings: ServerSettings): string {
  return path.join(settings.metaDir || settings.publicDir, "config", "shares.json");
}

function shareIndexPath(settings: ServerSettings): string {
  return path.join(settings.metaDir || settings.publicDir, "config", "share-index.json");
}

function dataIdForSettings(root: ServerSettings, settings: ServerSettings): string {
  if (!root.userDataDir) return "default";
  const relative = path.relative(root.userDataDir, settings.contentDir);
  if (relative.startsWith("..") || path.isAbsolute(relative)) return "default";
  return relative.split(path.sep)[0] || "default";
}

function tokenFromUrlPath(urlPath: string): string {
  const parts = urlPath.split("/").filter(Boolean);
  return parts.length === 2 && parts[0] === "share" ? parts[1]! : "";
}

export function settingsForShareToken(root: ServerSettings, token: string): ServerSettings {
  const indexPath = shareIndexPath(root);
  if (!fs.existsSync(indexPath)) return root;
  try {
    const data = JSON.parse(fs.readFileSync(indexPath, "utf8")) as { tokens?: Record<string, string> };
    const dataId = data.tokens?.[hashToken(token)];
    if (dataId) return forUser(root, dataId);
  } catch {
    /* ignore */
  }
  return root;
}

function hashToken(token: string): string {
  return crypto.createHash("sha256").update(token).digest("hex");
}

function expiresAtFor(duration: string, nowValue: string): string {
  const delta = SHARE_DURATIONS[duration as keyof typeof SHARE_DURATIONS];
  if (delta == null) return "";
  const now = Date.parse(nowValue) || Date.now();
  return new Date(now + delta).toISOString();
}

function isShareActive(record: ShareRecord): boolean {
  if (record.revoked) return false;
  const expiresAt = String(record.expires_at || "");
  if (!expiresAt) return true;
  const parsed = Date.parse(expiresAt);
  if (Number.isNaN(parsed)) return true;
  return parsed >= Date.now();
}

function normalizeShareMode(value: unknown): string {
  const mode = String(value || SAFE_SHARE_MODE).trim().toLowerCase();
  if (!SHARE_MODES.has(mode)) throw new ShareError("Invalid share mode.");
  return mode;
}

function shareModeForRecord(record: ShareRecord): string {
  const mode = String(record.mode || SAFE_SHARE_MODE);
  return SHARE_MODES.has(mode) ? mode : SAFE_SHARE_MODE;
}

function timingEqual(left: string, right: string): boolean {
  const a = Buffer.from(left);
  const b = Buffer.from(right);
  if (a.length !== b.length) return false;
  return crypto.timingSafeEqual(a, b);
}
