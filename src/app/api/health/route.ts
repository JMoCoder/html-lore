import { jsonOk } from "@/app/api/_lib/http";
import { APP_VERSION } from "@/server/version";

export async function GET() {
  return jsonOk({ status: "ok", version: APP_VERSION });
}
