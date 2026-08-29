import { cookies } from "next/headers";
import { getRootSettings, jsonOk } from "@/app/api/_lib/http";
import { sessionStatus } from "@/server";

export async function GET() {
  const settings = await getRootSettings();
  const store = await cookies();
  return jsonOk(sessionStatus(settings, store.get(settings.sessionCookieName)?.value));
}
