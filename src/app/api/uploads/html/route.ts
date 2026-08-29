import { UploadService } from "@/server";
import { jsonError, jsonOk, mapDomainError, requireApiAuth } from "@/app/api/_lib/http";

export async function POST(request: Request) {
  try {
    const ctx = await requireApiAuth(request);
    const form = await request.formData();
    const files = [...form.getAll("file"), ...form.getAll("files")].filter((value): value is File => value instanceof File);
    if (!files.length) return jsonError("HTML file is required.", 400);
    const results = new UploadService(ctx.settings).importHtmlFiles(
      await Promise.all(
        files.map(async (file) => ({
          filename: file.name,
          content: Buffer.from(await file.arrayBuffer()),
          title: String(form.get("title") || ""),
          summary: String(form.get("summary") || ""),
          collection: String(form.get("collection") || ""),
          tags: String(form.get("tags") || ""),
        })),
      ),
    );
    const first = results[0];
    return jsonOk({
      ...first,
      job_id: `upl_job_${first.upload_id}`,
      imported: results.length,
      items: results.map((row) => row.item),
      upload_ids: results.map((row) => row.upload_id),
    });
  } catch (error) {
    return mapDomainError(error);
  }
}
