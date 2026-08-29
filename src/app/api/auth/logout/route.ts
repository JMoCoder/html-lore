import { cookies } from "next/headers";
import { getRootSettings, jsonOk } from "@/app/api/_lib/http";
import { logoutBody } from "@/server";

export async function POST() {
  const settings = await getRootSettings();
  const store = await cookies();
  store.delete(settings.sessionCookieName);
  return jsonOk(logoutBody(settings));
}
