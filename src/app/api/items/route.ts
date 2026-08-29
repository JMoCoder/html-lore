import { ItemService, normalizeQuery } from "@/server";
import { jsonError, jsonOk, mapDomainError, parseBoolQuery, requireApiAuth } from "@/app/api/_lib/http";

export async function GET(request: Request) {
  try {
    const ctx = await requireApiAuth(request);
    const url = new URL(request.url);
    const limitRaw = url.searchParams.get("limit");
    const limit = limitRaw ? Number.parseInt(limitRaw, 10) : null;
    if (limitRaw && (Number.isNaN(limit) || limit! < 1 || limit! > 500)) {
      return jsonError("limit must be between 1 and 500", 400);
    }
    const query = normalizeQuery({
      q: url.searchParams.get("q") ?? "",
      library: url.searchParams.get("library") ?? "all",
      collection: url.searchParams.get("collection") ?? "",
      tags: url.searchParams.get("tags") ?? "",
      tag_match: url.searchParams.get("tag_match") ?? "any",
      favorite: parseBoolQuery(url.searchParams.get("favorite")),
      archived: parseBoolQuery(url.searchParams.get("archived")),
      sort: url.searchParams.get("sort") ?? "created-newest",
      limit,
    });
    const items = new ItemService(ctx.settings).listItems(query);
    return jsonOk({ items, count: items.length });
  } catch (error) {
    return mapDomainError(error);
  }
}
