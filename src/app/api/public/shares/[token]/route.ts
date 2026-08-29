import { ShareService, settingsForShareToken } from "@/server";
import { getRootSettings, jsonOk, mapDomainError } from "@/app/api/_lib/http";

export const dynamic = "force-dynamic";

export async function GET(_request: Request, ctx: RouteContext<"/api/public/shares/[token]">) {
  try {
    const root = await getRootSettings();
    const { token } = await ctx.params;
    const settings = settingsForShareToken(root, token);
    return jsonOk(new ShareService(settings, root).publicReadByToken(token));
  } catch (error) {
    return mapDomainError(error);
  }
}
