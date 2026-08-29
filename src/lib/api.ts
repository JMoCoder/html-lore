import type { Item } from "@/server/types";
import type { Note } from "@/fixtures/notes";

export function itemToNote(item: Item, extras: { html?: string; shareToken?: string } = {}): Note {
  return {
    id: item.id,
    slug: item.id,
    title: item.title,
    summary: item.summary,
    collection: item.collection,
    tags: item.tags,
    favorite: item.favorite,
    archived: item.archived,
    imported: item.source_type === "imported" || item.source_type === "html",
    created: item.created,
    updated: item.updated,
    shareToken: extras.shareToken,
    html: extras.html ?? "",
  };
}

export function readHref(itemId: string): string {
  return `/read/${itemId.split("/").map(encodeURIComponent).join("/")}`;
}

export function itemContentHref(itemId: string): string {
  return `/api/items/${itemId.split("/").map(encodeURIComponent).join("/")}/content`;
}

export function itemContentDownloadHref(itemId: string): string {
  return `${itemContentHref(itemId)}?download=1`;
}

export function triggerDownload(href: string) {
  const link = document.createElement("a");
  link.href = href;
  link.rel = "noopener";
  document.body.append(link);
  link.click();
  link.remove();
}

export function itemApiHref(itemId: string, suffix = ""): string {
  const base = `/api/items/${itemId.split("/").map(encodeURIComponent).join("/")}`;
  return suffix ? `${base}/${suffix}` : base;
}

export class ApiError extends Error {
  readonly status: number;
  readonly detail: unknown;

  constructor(message: string, status: number, detail: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

export function isShareConfirmationRequired(error: unknown): boolean {
  if (!(error instanceof ApiError) || error.status !== 409) return false;
  const detail = error.detail;
  return Boolean(detail && typeof detail === "object" && (detail as { requires_confirmation?: boolean }).requires_confirmation);
}

export async function apiJson<T>(input: RequestInfo, init?: RequestInit): Promise<T> {
  const response = await fetch(input, init);
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = (body as { detail?: unknown }).detail;
    const message = typeof detail === "string" ? detail : (detail as { message?: string } | undefined)?.message || response.statusText;
    throw new ApiError(message, response.status, detail);
  }
  return body as T;
}

export type PublicShare = {
  id: string;
  item_id: string;
  url_path: string;
  active: boolean;
  revoked: boolean;
  duration: string;
  expires_at: string;
  mode: string;
  access_count: number;
};

export async function listShares() {
  return apiJson<{ shares: PublicShare[]; interactive_enabled?: boolean }>("/api/shares");
}

export async function createShareLink(input: {
  itemId: string;
  duration: string;
  mode?: string;
  confirmPrivateReferences?: boolean;
}): Promise<{ urlPath: string; share: PublicShare }> {
  const result = await apiJson<{ share: PublicShare; url_path: string }>("/api/shares", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      item_id: input.itemId,
      duration: input.duration,
      mode: input.mode ?? "safe",
      confirm_private_references: Boolean(input.confirmPrivateReferences),
    }),
  });
  return { urlPath: result.url_path, share: result.share };
}

export async function updateShareLink(shareId: string, duration: string): Promise<PublicShare> {
  return apiJson<PublicShare>(`/api/shares/${encodeURIComponent(shareId)}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ duration }),
  });
}

export async function revokeShareLink(shareId: string): Promise<PublicShare> {
  return apiJson<PublicShare>(`/api/shares/${encodeURIComponent(shareId)}`, { method: "DELETE" });
}

function normalizeNewlines(value: string) {
  return value.replace(/\r\n/g, "\n");
}

export async function saveItemContent(
  itemId: string,
  content: string,
  confirmUnsafe: (reasons: string) => boolean,
): Promise<"saved" | "cancelled"> {
  if (!content.trim()) throw new Error("Content cannot be empty.");
  const scan = await apiJson<{ shareable: boolean; reasons?: string[] }>(itemApiHref(itemId, "content/share-safety"), {
    method: "POST",
    cache: "no-store",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content }),
  }).catch(() => null);
  if (!scan?.shareable) {
    const reasons = scan?.reasons?.length ? scan.reasons.join(", ") : "precheck-failed";
    if (!confirmUnsafe(reasons)) return "cancelled";
  }
  await apiJson(itemApiHref(itemId, "content"), {
    method: "PUT",
    cache: "no-store",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content }),
  });
  const verified = await fetch(`${itemContentHref(itemId)}?verify=${Date.now()}`, {
    cache: "no-store",
    credentials: "same-origin",
  });
  if (!verified.ok) throw new Error(`Verify failed (${verified.status}).`);
  const stored = await verified.text();
  if (normalizeNewlines(stored) !== normalizeNewlines(content)) {
    throw new Error("verify-mismatch");
  }
  return "saved";
}
