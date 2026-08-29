import path from "node:path";
import { ItemService, contentDispositionAttachment, scanShareContent } from "@/server";
import { jsonError, jsonOk, mapDomainError, requireApiAuth } from "@/app/api/_lib/http";

export const dynamic = "force-dynamic";

const HTML_HEADERS = {
  "Content-Type": "text/html; charset=utf-8",
  "Cache-Control": "no-store, no-cache, must-revalidate",
  Pragma: "no-cache",
};

type Action = "get" | "content" | "raw" | "metadata" | "state" | "share-safety";

function parsePath(segments: string[]): { itemId: string; action: Action } {
  if (segments.length >= 2 && segments.at(-1) === "share-safety" && segments.at(-2) === "content") {
    return { itemId: segments.slice(0, -2).join("/"), action: "share-safety" };
  }
  const last = segments.at(-1);
  if (last === "content" || last === "raw" || last === "metadata" || last === "state") {
    return { itemId: segments.slice(0, -1).join("/"), action: last };
  }
  return { itemId: segments.join("/"), action: "get" };
}

export async function GET(request: Request, ctx: RouteContext<"/api/items/[...path]">) {
  try {
    const auth = await requireApiAuth(request);
    const { itemId, action } = parsePath((await ctx.params).path);
    const items = new ItemService(auth.settings);
    if (action === "content" || action === "raw") {
      const html = items.readItemContent(itemId);
      const headers: Record<string, string> = { ...HTML_HEADERS };
      const download = new URL(request.url).searchParams.get("download");
      if (download === "1" || download === "true") {
        headers["Content-Disposition"] = contentDispositionAttachment(path.basename(itemId) || "note.html");
      }
      return new Response(html, { headers });
    }
    if (action !== "get") return jsonError("Method not allowed.", 405);
    const item = items.getItem(itemId);
    if (!item) return jsonError("Item not found", 404);
    return jsonOk(item);
  } catch (error) {
    return mapDomainError(error);
  }
}

export async function PUT(request: Request, ctx: RouteContext<"/api/items/[...path]">) {
  try {
    const auth = await requireApiAuth(request);
    const { itemId, action } = parsePath((await ctx.params).path);
    if (action !== "content") return jsonError("Method not allowed.", 405);
    const body = (await request.json()) as { content?: unknown };
    return jsonOk(new ItemService(auth.settings).updateItemContent(itemId, body.content));
  } catch (error) {
    return mapDomainError(error);
  }
}

export async function PATCH(request: Request, ctx: RouteContext<"/api/items/[...path]">) {
  try {
    const auth = await requireApiAuth(request);
    const { itemId, action } = parsePath((await ctx.params).path);
    const body = (await request.json()) as Record<string, unknown>;
    const items = new ItemService(auth.settings);
    if (action === "metadata") return jsonOk(items.updateItemMetadata(itemId, body));
    if (action === "state") return jsonOk(items.updateItemState(itemId, body));
    return jsonError("Method not allowed.", 405);
  } catch (error) {
    return mapDomainError(error);
  }
}

export async function DELETE(request: Request, ctx: RouteContext<"/api/items/[...path]">) {
  try {
    const auth = await requireApiAuth(request);
    const { itemId, action } = parsePath((await ctx.params).path);
    if (action !== "get") return jsonError("Method not allowed.", 405);
    return jsonOk(new ItemService(auth.settings).deleteItem(itemId));
  } catch (error) {
    return mapDomainError(error);
  }
}

export async function POST(request: Request, ctx: RouteContext<"/api/items/[...path]">) {
  try {
    const auth = await requireApiAuth(request);
    const { itemId, action } = parsePath((await ctx.params).path);
    if (action !== "share-safety") return jsonError("Method not allowed.", 405);
    const body = (await request.json().catch(() => ({}))) as { content?: string; mode?: string };
    const items = new ItemService(auth.settings);
    const content = typeof body.content === "string" ? body.content : items.readItemContent(itemId);
    return jsonOk(scanShareContent(content));
  } catch (error) {
    return mapDomainError(error);
  }
}
