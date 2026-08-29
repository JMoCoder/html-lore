import { ItemService, normalizeQuery } from "@/server";
import { jsonOk, mapDomainError, parseBoolQuery, requireApiAuth } from "@/app/api/_lib/http";

export async function GET(request: Request) {
  try {
    const ctx = await requireApiAuth(request);
    const url = new URL(request.url);
    const query = normalizeQuery({
      q: url.searchParams.get("q") ?? "",
      library: url.searchParams.get("library") ?? "all",
      collection: url.searchParams.get("collection") ?? "",
      tags: url.searchParams.get("tags") ?? "",
      tag_match: url.searchParams.get("tag_match") ?? "any",
      favorite: parseBoolQuery(url.searchParams.get("favorite")),
      archived: parseBoolQuery(url.searchParams.get("archived")),
      sort: url.searchParams.get("sort") ?? "created-newest",
    });
    return jsonOk(new ItemService(ctx.settings).searchItems(query));
  } catch (error) {
    return mapDomainError(error);
  }
}
