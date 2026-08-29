import { ExportService, contentDispositionAttachment } from "@/server";
import { mapDomainError, requireApiAuth } from "@/app/api/_lib/http";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  try {
    const auth = await requireApiAuth(request);
    const file = new ExportService(auth.settings).manifestJson();
    return new Response(new Uint8Array(file.body), {
      headers: {
        "Content-Type": file.mime,
        "Content-Disposition": contentDispositionAttachment(file.filename),
        "Cache-Control": "no-store",
      },
    });
  } catch (error) {
    return mapDomainError(error);
  }
}
