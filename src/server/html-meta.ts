import { Parser } from "htmlparser2";

export function extractPlainText(html: string, max = 20000): string {
  const parts: string[] = [];
  let skip = 0;
  const parser = new Parser(
    {
      onopentag(name) {
        if (name === "script" || name === "style" || name === "noscript") skip += 1;
      },
      onclosetag(name) {
        if (name === "script" || name === "style" || name === "noscript") skip = Math.max(0, skip - 1);
      },
      ontext(data) {
        if (!skip) parts.push(data);
      },
    },
    { decodeEntities: true },
  );
  parser.write(html);
  parser.end();
  const text = parts.join(" ").replace(/\s+/g, " ").trim();
  return text.length > max ? text.slice(0, max) : text;
}

export function extractHtmlMetadata(html: string, fallbackTitle: string): { title: string; summary: string } {
  let title = "";
  let h1 = "";
  let description = "";
  let firstParagraph = "";
  let capture: "title" | "h1" | "p" | null = null;
  let buffer: string[] = [];

  const parser = new Parser(
    {
      onopentag(name, attrs) {
        const tag = name.toLowerCase();
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
      },
      onclosetag(name) {
        const tag = name.toLowerCase();
        if (tag !== capture) return;
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
  parser.write(html);
  parser.end();

  let summary = description || firstParagraph;
  if (summary.length > 220) summary = `${summary.slice(0, 217).replace(/\s+$/, "")}...`;
  return { title: title || h1 || fallbackTitle, summary };
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
