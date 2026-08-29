import { ShareService } from "@/server";
import { jsonOk, mapDomainError, requireApiAuth } from "@/app/api/_lib/http";

export async function GET(request: Request) {
  try {
    const ctx = await requireApiAuth(request);
    const shares = new ShareService(ctx.settings, ctx.root).listShares();
    return jsonOk({
      shares,
      count: shares.length,
      interactive_enabled: ctx.settings.shareInteractiveEnabled,
    });
  } catch (error) {
    return mapDomainError(error);
  }
}

export async function POST(request: Request) {
  try {
    const ctx = await requireApiAuth(request);
    const body = (await request.json()) as {
      item_id?: string;
      duration?: string;
      mode?: string;
      confirm_private_references?: boolean;
    };
    const result = new ShareService(ctx.settings, ctx.root).createShare({
      itemId: String(body.item_id || ""),
      duration: String(body.duration || "1d"),
      mode: body.mode,
      confirmPrivateReferences: Boolean(body.confirm_private_references),
    });
    return jsonOk(result);
  } catch (error) {
    return mapDomainError(error);
  }
}
