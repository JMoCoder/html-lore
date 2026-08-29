import { ItemService } from "@/server";
import { jsonError, jsonOk, mapDomainError, requireApiAuth } from "@/app/api/_lib/http";

export async function POST(request: Request) {
  try {
    const ctx = await requireApiAuth(request);
    const body = (await request.json()) as { kind?: string; from?: string; to?: string };
    const items = new ItemService(ctx.settings);
    if (body.kind === "collection") return jsonOk(items.renameCollection(body.from ?? "", body.to ?? ""));
    if (body.kind === "tag") return jsonOk(items.renameTag(body.from ?? "", body.to ?? ""));
    return jsonError("kind must be collection or tag.", 400);
  } catch (error) {
    return mapDomainError(error);
  }
}
