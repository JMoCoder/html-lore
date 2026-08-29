import { Parser } from "htmlparser2";
import fs from "node:fs";
import path from "node:path";

export const SHARE_DURATIONS = {
  "1h": 60 * 60 * 1000,
  "1d": 24 * 60 * 60 * 1000,
  "7d": 7 * 24 * 60 * 60 * 1000,
  "30d": 30 * 24 * 60 * 60 * 1000,
  forever: null,
} as const;

export const SAFE_SHARE_MODE = "safe";
export const INTERACTIVE_SHARE_MODE = "interactive";
export const SHARE_MODES = new Set([SAFE_SHARE_MODE, INTERACTIVE_SHARE_MODE]);

const DANGEROUS_TAGS = new Set(["iframe", "object", "embed", "form", "input", "button", "textarea", "select", "base"]);
const SANITIZER_BLOCK_TAGS = new Set([...DANGEROUS_TAGS, "script", "meta", "link"]);
const SANITIZER_SKIP_CONTENT_TAGS = new Set(["script", "iframe", "object", "embed", "form", "textarea", "select", "button"]);
const DANGEROUS_EXTENSIONS = new Set([".exe", ".dmg", ".apk", ".msi", ".bat", ".cmd", ".sh", ".ps1", ".scr", ".jar"]);
const SAFE_TOGGLE_HANDLER = /^toggleGroup\(\s*['"]([A-Za-z][A-Za-z0-9_-]{0,63})['"]\s*\)\s*;?\s*$/;
const SAFE_FRAGMENT_HREF = /^#[A-Za-z][A-Za-z0-9_.:-]{0,127}$/;
const CHART_SCRIPT_PATTERN = /\bchart(?:\.umd)?(?:\.min)?\.js\b|new\s+Chart\s*\(|<canvas\b/i;
const CSS_UNSAFE_PATTERNS: [string, RegExp][] = [
  ["css-import", /@import\b/i],
  ["css-expression", /\bexpression\s*\(/i],
  ["css-behavior", /(?<![-\w])behavior\s*:/i],
  ["css-binding", /-moz-binding\s*:/i],
  ["css-dangerous-scheme", /(?:javascript|vbscript|file|data\s*:\s*text\/html)\s*:/i],
];
const CSS_URL_PATTERN = /\burl\s*\(\s*(['"]?)(.*?)\1\s*\)/gi;
export const SECRET_PATTERNS = [
  /-----BEGIN [A-Z ]*PRIVATE KEY-----/,
  /\b[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\b/,
  /\b(?:api[_-]?key|secret|token|password|passwd|pwd)\b\s*[:=]\s*['"]?[^'"\s<]{8,}/i,
  /\b(?:sk|pk|rk|ghp|github_pat|xox[baprs])-[-A-Za-z0-9_]{16,}\b/i,
  /\b(?:AKIA|ASIA)[A-Z0-9]{16}\b/,
  /\b(?:mongodb|postgres|postgresql|mysql|redis):\/\/[^\s<]+/i,
];
export const LOCAL_PATTERNS = [
  /\b(?:10|127|172\.(?:1[6-9]|2\d|3[0-1])|192\.168)\.\d{1,3}\.\d{1,3}\b/,
  /\bfile:\/\/[^\s<]+/i,
  /(?:^|[\s"'>])(?:\/[A-Za-z0-9_.-]+){2,}/,
  /[A-Za-z]:\\(?:[^\\/:*?"<>|\r\n]+\\?)+/,
];

export class ShareError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ShareError";
  }
}

export class ShareSafetyError extends ShareError {
  safety: Record<string, unknown>;
  constructor(safety: Record<string, unknown>) {
    super("This item cannot be shared in the requested mode.");
    this.name = "ShareSafetyError";
    this.safety = safety;
  }
}

export class ShareSafetyConfirmationError extends ShareSafetyError {
  constructor(safety: Record<string, unknown>) {
    super(safety);
    this.name = "ShareSafetyConfirmationError";
    this.message = "Interactive share requires confirmation for private or local references.";
  }
}

export function scanShareContent(content: string) {
  const reasons: string[] = [];
  let sawScript = false;
  let requiresStaticChart = false;
  let scriptStack = 0;
  const scriptParts: string[] = [];
  let styleStack = 0;
  const styleParts: string[] = [];

  const parser = new Parser(
    {
      onopentag(name, attrs) {
        const tag = name.toLowerCase();
        if (tag === "script") {
          sawScript = true;
          if (CHART_SCRIPT_PATTERN.test(attrs.src || "")) requiresStaticChart = true;
          scriptStack += 1;
          return;
        }
        if (tag === "style") {
          styleStack += 1;
          return;
        }
        if (tag === "canvas") requiresStaticChart = true;
        if (DANGEROUS_TAGS.has(tag)) reasons.push(`blocked-tag:${tag}`);
        if (tag === "meta" && isMetaRefresh(attrs)) reasons.push("meta-refresh");
        for (const [attrName, attrValue] of Object.entries(attrs)) {
          const attr = attrName.toLowerCase();
          const value = (attrValue || "").trim();
          if (attr.startsWith("on") && !(attr === "onclick" && safeToggleTarget(value))) {
            reasons.push("inline-event-handler");
          }
          if (["href", "src", "action", "formaction"].includes(attr)) {
            const reason = unsafeUrlReason(value);
            if (reason && reason !== "external-link") reasons.push(reason);
          }
        }
      },
      onclosetag(name) {
        const tag = name.toLowerCase();
        if (tag === "script" && scriptStack > 0) scriptStack -= 1;
        if (tag === "style" && styleStack > 0) styleStack -= 1;
      },
      ontext(data) {
        if (scriptStack > 0) {
          scriptParts.push(data);
          if (CHART_SCRIPT_PATTERN.test(data)) requiresStaticChart = true;
        }
        if (styleStack > 0) styleParts.push(data);
      },
    },
    { decodeEntities: true },
  );
  parser.write(content);
  parser.end();

  if (sawScript && !isSafeToggleScript(scriptParts.join("\n"))) reasons.push("blocked-tag:script");
  if (requiresStaticChart) reasons.push("requires-static-export:chart");
  reasons.push(...unsafeCssReasons(styleParts.join("\n")));
  const text = stripTags(content);
  if (SECRET_PATTERNS.some((pattern) => pattern.test(text))) reasons.push("sensitive-secret");
  if (LOCAL_PATTERNS.some((pattern) => pattern.test(text))) reasons.push("private-local-reference");
  return { shareable: reasons.length === 0, reasons: [...new Set(reasons)].sort() };
}

export function scanInteractiveShareContent(content: string) {
  const reasons: string[] = [];
  let styleStack = 0;
  const styleParts: string[] = [];
  const parser = new Parser(
    {
      onopentag(name, attrs) {
        const tag = name.toLowerCase();
        if (["base", "object", "embed"].includes(tag)) reasons.push(`blocked-tag:${tag}`);
        if (tag === "meta" && isMetaRefresh(attrs)) reasons.push("meta-refresh");
        if (tag === "style") styleStack += 1;
        for (const [attrName, attrValue] of Object.entries(attrs)) {
          const attr = attrName.toLowerCase();
          if (!["href", "src", "action", "formaction"].includes(attr)) continue;
          const reason = unsafeUrlReason((attrValue || "").trim());
          if (reason === "dangerous-url" || reason === "dangerous-download") reasons.push(reason);
        }
      },
      onclosetag(name) {
        if (name.toLowerCase() === "style" && styleStack > 0) styleStack -= 1;
      },
      ontext(data) {
        if (styleStack > 0) styleParts.push(data);
      },
    },
    { decodeEntities: true },
  );
  parser.write(content);
  parser.end();

  for (const reason of unsafeCssReasons(styleParts.join("\n"))) {
    if (reason !== "css-import" && reason !== "css-url") reasons.push(reason);
  }
  const text = stripTags(content);
  if (SECRET_PATTERNS.some((pattern) => pattern.test(text))) reasons.push("sensitive-secret");
  const warnings: string[] = [];
  if (LOCAL_PATTERNS.some((pattern) => pattern.test(content))) warnings.push("private-local-reference");
  return {
    shareable: reasons.length === 0,
    reasons: [...new Set(reasons)].sort(),
    warnings: [...new Set(warnings)].sort(),
    requires_confirmation: warnings.length > 0,
  };
}

export function sanitizeSharedHtml(content: string): { body_html: string; styles: string } {
  const parts: string[] = [];
  const headParts: string[] = [];
  const bodyParts: string[] = [];
  const skipStack: string[] = [];
  let styleStack = 0;
  let styleParts: string[] = [];
  let inHead = false;
  let inBody = false;

  const active = () => (inHead ? headParts : inBody ? bodyParts : parts);

  const parser = new Parser(
    {
      onopentag(name, attrs) {
        const tag = name.toLowerCase();
        if (tag === "html") return;
        if (tag === "head") {
          inHead = true;
          return;
        }
        if (tag === "body") {
          inBody = true;
          return;
        }
        if (SANITIZER_BLOCK_TAGS.has(tag) || (tag === "meta" && isMetaRefresh(attrs))) {
          if (SANITIZER_SKIP_CONTENT_TAGS.has(tag)) skipStack.push(tag);
          return;
        }
        if (skipStack.length) return;
        if (tag === "style") {
          styleStack += 1;
          styleParts = [];
          return;
        }
        const cleanAttrs: string[] = [];
        for (const [attrName, attrValue] of Object.entries(attrs)) {
          const attr = attrName.toLowerCase();
          const value = attrValue || "";
          if (attr === "onclick") {
            const target = safeToggleTarget(value);
            if (target) cleanAttrs.push(`data-share-toggle="${escapeAttr(target)}"`);
            continue;
          }
          if (attr.startsWith("on")) continue;
          if (tag === "a" && attr === "href") {
            if (isSafeFragmentHref(value)) cleanAttrs.push(`href="${escapeAttr(value.trim())}"`);
            continue;
          }
          if (attr === "src") {
            if (tag === "img" && isSafeCssDataImage(value)) cleanAttrs.push(`src="${escapeAttr(value)}"`);
            continue;
          }
          if (["href", "src", "action", "formaction"].includes(attr)) {
            if (unsafeUrlReason(value)) continue;
          }
          cleanAttrs.push(`${escapeAttr(attr)}="${escapeAttr(value)}"`);
        }
        const attrText = cleanAttrs.length ? ` ${cleanAttrs.join(" ")}` : "";
        active().push(`<${escapeAttr(tag)}${attrText}>`);
      },
      onclosetag(name) {
        const tag = name.toLowerCase();
        if (tag === "html") return;
        if (tag === "head") {
          inHead = false;
          return;
        }
        if (tag === "body") {
          inBody = false;
          return;
        }
        if (tag === "style" && styleStack > 0) {
          styleStack -= 1;
          if (styleStack === 0) {
            const css = styleParts.join("");
            if (!unsafeCssReasons(css).length) headParts.push(`<style>${css}</style>`);
            styleParts = [];
          }
          return;
        }
        if (skipStack.length) {
          if (skipStack[skipStack.length - 1] === tag) skipStack.pop();
          return;
        }
        if (!DANGEROUS_TAGS.has(tag)) active().push(`</${escapeAttr(tag)}>`);
      },
      ontext(data) {
        if (styleStack > 0) {
          styleParts.push(data);
          return;
        }
        if (!skipStack.length) active().push(escapeText(data));
      },
    },
    { decodeEntities: true },
  );
  parser.write(content);
  parser.end();

  const body = bodyParts.join("").trim() || parts.join("").trim();
  return { body_html: body, styles: headParts.join("").trim() };
}

export function buildSafeShareCopy(content: string): string {
  const redacted = redactShareSensitiveValues(content);
  const prepared = replaceRemovedInteractiveComponents(redacted);
  const rendered = sanitizeSharedHtml(prepared);
  let body = redactSharePrivateReferences(rendered.body_html);
  if (!stripTags(body).trim()) {
    body =
      '<div class="html-lore-share-notice">No static content could be preserved. The original interactive components were removed for safe public sharing.</div>';
  }
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    html { min-height: 100%; }
    body { margin: 0; overflow-wrap: anywhere; }
    .html-lore-share-notice { margin: 1rem; padding: .75rem 1rem; border: 1px solid #d7b66b; background: #fff8df; color: #5f4612; font: 14px/1.5 system-ui, sans-serif; }
    img, video, svg { max-width: 100%; height: auto; }
  </style>
  ${rendered.styles}
</head>
<body>
  ${body}
</body>
</html>`;
}

export function nextSafeShareCopyPath(contentDir: string, sourcePath: string): string {
  const parsed = path.parse(sourcePath);
  const suffix = parsed.ext || ".html";
  const stem = parsed.name || "shared-note";
  let candidate = path.join(parsed.dir, `${stem}--safe-share${suffix}`);
  let index = 2;
  while (fs.existsSync(path.join(contentDir, candidate))) {
    candidate = path.join(parsed.dir, `${stem}--safe-share-${index}${suffix}`);
    index += 1;
  }
  return candidate;
}

function redactShareSensitiveValues(content: string): string {
  let value = content;
  for (const pattern of SECRET_PATTERNS) value = value.replace(pattern, "[redacted sensitive value]");
  return value;
}

function redactSharePrivateReferences(content: string): string {
  let value = content;
  for (const pattern of LOCAL_PATTERNS) value = value.replace(pattern, "[removed private reference]");
  return value;
}

function replaceRemovedInteractiveComponents(content: string): string {
  const notice = '<div class="html-lore-share-notice">Interactive content was removed from this safety copy.</div>';
  return content
    .replace(/<canvas\b[^>]*>.*?<\/canvas\s*>/gi, notice)
    .replace(/<canvas\b[^>]*\/?\s*>/gi, notice)
    .replace(/<(?:iframe|object|embed)\b[^>]*>.*?<\/(?:iframe|object|embed)\s*>/gi, notice)
    .replace(/<(?:iframe|object|embed)\b[^>]*\/?\s*>/gi, notice)
    .replace(/<form\b[^>]*>/gi, '<div class="html-lore-share-form">')
    .replace(/<\/form\s*>/gi, "</div>");
}

function unsafeUrlReason(value: string): string {
  if (!value) return "";
  const lowered = value.trim().toLowerCase();
  if (lowered.startsWith("javascript:") || lowered.startsWith("vbscript:") || lowered.startsWith("data:text/html")) {
    return "dangerous-url";
  }
  try {
    const parsed = new URL(value, "https://html-lore.invalid");
    if ((parsed.protocol === "http:" || parsed.protocol === "https:") && parsed.host && /^https?:/i.test(value)) {
      return "external-link";
    }
    const suffix = path.extname(parsed.pathname).toLowerCase();
    if (DANGEROUS_EXTENSIONS.has(suffix)) return "dangerous-download";
  } catch {
    return "";
  }
  return "";
}

function isMetaRefresh(attrs: Record<string, string>): boolean {
  return String(attrs["http-equiv"] || "").trim().toLowerCase() === "refresh";
}

function isSafeFragmentHref(value: string): boolean {
  return SAFE_FRAGMENT_HREF.test(value.trim());
}

function unsafeCssReasons(value: string): string[] {
  if (!value) return [];
  const reasons = CSS_UNSAFE_PATTERNS.filter(([, pattern]) => pattern.test(value)).map(([reason]) => reason);
  for (const match of value.matchAll(CSS_URL_PATTERN)) {
    const urlValue = (match[2] || "").trim();
    if (isSafeCssDataImage(urlValue)) continue;
    if (/^[a-z][a-z0-9+.-]*:/i.test(urlValue) || urlValue.startsWith("//") || urlValue.startsWith("/") || urlValue.startsWith("\\")) {
      reasons.push("css-url");
    }
  }
  return [...new Set(reasons)].sort();
}

function isSafeCssDataImage(value: string): boolean {
  const lowered = value.trim().toLowerCase();
  if (!lowered.startsWith("data:image/svg+xml")) return false;
  if (lowered.includes(";base64")) return false;
  const decoded = decodeURIComponentSafe(value);
  return !/<\s*script\b|on[a-z]+\s*=|javascript\s*:|data\s*:\s*text\/html/i.test(decoded);
}

function safeToggleTarget(value: string): string {
  const match = SAFE_TOGGLE_HANDLER.exec(value.trim());
  return match?.[1] ?? "";
}

function isSafeToggleScript(value: string): boolean {
  const compact = value.replace(/\s+/g, "");
  return /^functiontoggleGroup\(id\)\{constel=document\.getElementById\(id\);el\.classList\.toggle\('open'\);\}(\/\/Openfirstgroupbydefault\(alreadysetviaclass\))?(\/\/Addkeyboardshortcut:press'\?'toexpandall)?document\.addEventListener\('keydown',e=>\{if\(e\.key==='\?'\)\{document\.querySelectorAll\('\.qgroup'\)\.forEach\(g=>g\.classList\.add\('open'\)\);\}if\(e\.key==='\/'\)\{document\.querySelectorAll\('\.qgroup'\)\.forEach\(g=>g\.classList\.remove\('open'\)\);document\.getElementById\('g1'\)\.classList\.add\('open'\);\}\}\);$/.test(
    compact,
  );
}

export function stripTags(content: string): string {
  const parts: string[] = [];
  const parser = new Parser(
    {
      ontext(data) {
        parts.push(data);
      },
    },
    { decodeEntities: true },
  );
  parser.write(content);
  parser.end();
  return parts.join(" ");
}

function escapeAttr(value: string): string {
  return value.replaceAll("&", "&amp;").replaceAll('"', "&quot;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
}

function escapeText(value: string): string {
  return value.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
}

function decodeURIComponentSafe(value: string): string {
  return value.replace(/%([0-9a-fA-F]{2})/g, (_, hex: string) => String.fromCharCode(Number.parseInt(hex, 16)));
}
