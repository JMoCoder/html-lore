import { UploadService } from "@/server";
import { jsonError, jsonOk, mapDomainError, requireApiAuth } from "@/app/api/_lib/http";

export async function POST(request: Request) {
  try {
    const ctx = await requireApiAuth(request);
    const form = await request.formData();
    const file = form.get("file");
    if (!(file instanceof File)) return jsonError("HTML file is required.", 400);
    const buffer = Buffer.from(await file.arrayBuffer());
    const result = new UploadService(ctx.settings).importHtml({
      filename: file.name,
      content: buffer,
      title: String(form.get("title") || ""),
      summary: String(form.get("summary") || ""),
      collection: String(form.get("collection") || ""),
      tags: String(form.get("tags") || ""),
    });
    return jsonOk({
      ...result,
      job_id: `upl_job_${result.upload_id}`,
    });
  } catch (error) {
    return mapDomainError(error);
  }
}
