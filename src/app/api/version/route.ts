import { jsonOk } from "@/app/api/_lib/http";
import { APP_BRAND, APP_RELEASE_URL, APP_REPOSITORY, APP_VERSION } from "@/server/version";

export async function GET() {
  return jsonOk({
    version: APP_VERSION,
    brand: APP_BRAND,
    repository: APP_REPOSITORY,
    release_url: APP_RELEASE_URL,
  });
}
