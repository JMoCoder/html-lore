import { ItemService } from "@/server";
import { jsonOk, mapDomainError, requireApiAuth } from "@/app/api/_lib/http";

export async function GET(request: Request) {
  try {
    const ctx = await requireApiAuth(request);
    return jsonOk(new ItemService(ctx.settings).manifest());
  } catch (error) {
    return mapDomainError(error);
  }
}
