import { ShareService } from "@/server";
import { jsonOk, mapDomainError, requireApiAuth } from "@/app/api/_lib/http";

export async function PATCH(request: Request, ctx: RouteContext<"/api/shares/[shareId]">) {
  try {
    const auth = await requireApiAuth(request);
    const { shareId } = await ctx.params;
    const body = (await request.json()) as { duration?: string; revoked?: boolean };
    return jsonOk(new ShareService(auth.settings, auth.root).updateShare(shareId, body));
  } catch (error) {
    return mapDomainError(error);
  }
}

export async function DELETE(request: Request, ctx: RouteContext<"/api/shares/[shareId]">) {
  try {
    const auth = await requireApiAuth(request);
    const { shareId } = await ctx.params;
    return jsonOk(new ShareService(auth.settings, auth.root).revokeShare(shareId));
  } catch (error) {
    return mapDomainError(error);
  }
}
