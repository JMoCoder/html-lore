import { jsonOk, mapDomainError, requireApiAuth } from "@/app/api/_lib/http";
import { NavigationConfigService } from "@/server/navigation";

export async function GET(request: Request) {
  try {
    const ctx = await requireApiAuth(request);
    return jsonOk(new NavigationConfigService(ctx.settings).getConfig());
  } catch (error) {
    return mapDomainError(error);
  }
}

export async function PUT(request: Request) {
  try {
    const ctx = await requireApiAuth(request);
    const body = (await request.json()) as Record<string, unknown>;
    return jsonOk(new NavigationConfigService(ctx.settings).updateConfig(body));
  } catch (error) {
    return mapDomainError(error);
  }
}
