import fs from "node:fs";
import { StringDecoder } from "node:string_decoder";
import { Parser } from "htmlparser2";

export const SEARCH_TEXT_MAX = 20_000;
const READ_CHUNK = 64 * 1024;
const SKIP_TAGS = new Set(["script", "style", "noscript"]);

export type HtmlScanResult = {
  title: string;
  summary: string;
  text: string;
};

export type HtmlScanOptions = {
  includeText?: boolean;
  includeMeta?: boolean;
  maxText?: number;
};

export function extractPlainText(html: string, max = SEARCH_TEXT_MAX): string {
  return scanHtmlString(html, "", { includeMeta: false, includeText: true, maxText: max }).text;
}

export function extractHtmlMetadata(html: string, fallbackTitle: string): { title: string; summary: string } {
  const scanned = scanHtmlString(html, fallbackTitle, { includeMeta: true, includeText: false });
  return { title: scanned.title, summary: scanned.summary };
}

export function scanHtmlFile(filePath: string, fallbackTitle: string, options: HtmlScanOptions = {}): HtmlScanResult {
  const collector = createHtmlCollector(fallbackTitle, options);
  const fd = fs.openSync(filePath, "r");
  const decoder = new StringDecoder("utf8");
  const buf = Buffer.allocUnsafe(READ_CHUNK);
  try {
    while (!collector.done) {
      const bytes = fs.readSync(fd, buf, 0, buf.length, null);
      if (bytes === 0) break;
      collector.write(decoder.write(buf.subarray(0, bytes)));
    }
    collector.write(decoder.end());
    collector.end();
  } finally {
    fs.closeSync(fd);
  }
  return collector.result();
}

export function scanHtmlString(html: string, fallbackTitle: string, options: HtmlScanOptions = {}): HtmlScanResult {
  const collector = createHtmlCollector(fallbackTitle, options);
  let offset = 0;
  while (offset < html.length && !collector.done) {
    const next = Math.min(html.length, offset + READ_CHUNK);
    collector.write(html.slice(offset, next));
    offset = next;
  }
  collector.end();
  return collector.result();
}

function createHtmlCollector(fallbackTitle: string, options: HtmlScanOptions) {
  const includeText = options.includeText !== false;
  const includeMeta = options.includeMeta !== false;
  const maxText = options.maxText ?? SEARCH_TEXT_MAX;

  let skip = 0;
  const textParts: string[] = [];
  let rawTextLen = 0;
  let textDone = !includeText;

  let title = "";
  let h1 = "";
  let description = "";
  let firstParagraph = "";
  let capture: "title" | "h1" | "p" | null = null;
  let buffer: string[] = [];
  let headClosed = false;

  const parser = new Parser(
    {
      onopentag(name, attrs) {
        const tag = name.toLowerCase();
        if (SKIP_TAGS.has(tag)) skip += 1;
        if (!includeMeta) return;
        if (tag === "meta" && String(attrs.name || "").toLowerCase() === "description") {
          description = String(attrs.content || "").trim();
        }
        if (tag === "title" && title) return;
        if (tag === "h1" && h1) return;
        if (tag === "p" && firstParagraph) return;
        if (tag === "title" || tag === "h1" || tag === "p") {
          capture = tag;
          buffer = [];
        }
      },
      ontext(data) {
        if (capture) buffer.push(data);
        if (skip || textDone) return;
        textParts.push(data);
        rawTextLen += data.length;
        if (rawTextLen >= maxText) textDone = true;
      },
      onclosetag(name) {
        const tag = name.toLowerCase();
        if (SKIP_TAGS.has(tag)) skip = Math.max(0, skip - 1);
        if (tag === "head") headClosed = true;
        if (!includeMeta || tag !== capture) return;
        const text = buffer.join("").replace(/\s+/g, " ").trim();
        if (tag === "title" && !title) title = text;
        else if (tag === "h1" && !h1) h1 = text;
        else if (tag === "p" && !firstParagraph) firstParagraph = text;
        capture = null;
        buffer = [];
      },
    },
    { decodeEntities: true },
  );

  function metaDone() {
    if (!includeMeta) return true;
    const heading = Boolean(title || h1);
    return heading && Boolean(description || firstParagraph || headClosed);
  }

  return {
    get done() {
      return textDone && metaDone();
    },
    write(chunk: string) {
      if (chunk) parser.write(chunk);
    },
    end() {
      parser.end();
    },
    result(): HtmlScanResult {
      let summary = description || firstParagraph;
      if (summary.length > 220) summary = `${summary.slice(0, 217).replace(/\s+$/, "")}...`;
      const text = textParts.join(" ").replace(/\s+/g, " ").trim();
      return {
        title: title || h1 || fallbackTitle,
        summary,
        text: text.length > maxText ? text.slice(0, maxText) : text,
      };
    },
  };
}

export function filenameToTitle(value: string): string {
  return value
    .replaceAll("_", "-")
    .split("-")
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export function slugify(value: string): string {
  let slug = Array.from(value, (char) => (/[a-z0-9]/i.test(char) ? char.toLowerCase() : "-")).join("").replace(/^-+|-+$/g, "");
  while (slug.includes("--")) slug = slug.replaceAll("--", "-");
  return slug || "collection";
}
