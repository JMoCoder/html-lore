import fs from "node:fs";
import path from "node:path";
import { buildManifest, listHtmlFiles } from "@/server/manifest";
import { ensureWithin } from "@/server/paths";
import type { ServerSettings } from "@/server/settings";
import { buildStoreZip } from "@/server/zip";

export class ExportError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ExportError";
  }
}

export type ExportFile = {
  filename: string;
  mime: string;
  body: Buffer;
};

export class ExportService {
  constructor(readonly settings: ServerSettings) {}

  manifestJson(): ExportFile {
    const manifest = buildManifest(this.settings.contentDir, this.settings.metaDir, this.settings.siteTitle);
    return {
      filename: `html-lore-manifest-${dateStamp()}.json`,
      mime: "application/json; charset=utf-8",
      body: Buffer.from(`${JSON.stringify(manifest, null, 2)}\n`, "utf8"),
    };
  }

  htmlArchive(): ExportFile {
    if (!this.settings.contentDir) throw new ExportError("Content directory is not configured.");
    const files = listHtmlFiles(this.settings.contentDir).sort();
    const entries = files.map((filePath) => {
      ensureWithin(filePath, this.settings.contentDir);
      const relative = path.relative(this.settings.contentDir, filePath).replace(/\\/g, "/");
      return { name: relative, data: fs.readFileSync(filePath) };
    });
    return {
      filename: `html-lore-html-${dateStamp()}.zip`,
      mime: "application/zip",
      body: buildStoreZip(entries),
    };
  }
}

export function contentDispositionAttachment(filename: string): string {
  const ascii = filename.replace(/[^\w.\-]+/g, "_") || "download";
  return `attachment; filename="${ascii}"; filename*=UTF-8''${encodeURIComponent(filename)}`;
}

function dateStamp(): string {
  return new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
}
