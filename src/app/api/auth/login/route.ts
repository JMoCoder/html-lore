import { cookies } from "next/headers";
import { getRootSettings, jsonOk, mapDomainError } from "@/app/api/_lib/http";
import { login } from "@/server";

export async function POST(request: Request) {
  try {
    const settings = await getRootSettings();
    const body = (await request.json().catch(() => ({}))) as { username?: string; password?: string };
    const result = login(settings, String(body.username ?? ""), String(body.password ?? ""));
    if (result.token) {
      const store = await cookies();
      store.set(settings.sessionCookieName, result.token, {
        httpOnly: true,
        path: "/",
        sameSite: "lax",
        secure: settings.sessionSecure,
        maxAge: settings.sessionMaxAgeSeconds,
      });
    }
    return jsonOk(result.body);
  } catch (error) {
    return mapDomainError(error);
  }
}
