import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { extractPlainText, scanHtmlFile, SEARCH_TEXT_MAX } from "@/server/html-meta";

describe("html text extraction", () => {
  it("skips script, style, and noscript", () => {
    const html = `<html><head><style>.a{color:red}</style><script>var hide="nope"</script></head><body><noscript>hidden</noscript><p>visible-token</p></body></html>`;
    const text = extractPlainText(html);
    expect(text).toContain("visible-token");
    expect(text).not.toContain("nope");
    expect(text).not.toContain("color:red");
    expect(text).not.toContain("hidden");
  });

  it("indexes visible text after a 300KiB style/script prefix", () => {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), "html-lore-scan-"));
    const filePath = path.join(dir, "late-body.html");
    const prefix = "x".repeat(300 * 1024);
    const html = `<!doctype html><html><head><style>${prefix}</style><script>window.__hide="script-token-should-not-index";</script><title>Prefixed</title></head><body><p>unique-body-after-css-zzlm</p></body></html>`;
    fs.writeFileSync(filePath, html);
    const scanned = scanHtmlFile(filePath, "Fallback");
    expect(scanned.title).toBe("Prefixed");
    expect(scanned.text).toContain("unique-body-after-css-zzlm");
    expect(scanned.text).not.toContain("script-token-should-not-index");
    expect(scanned.text.includes("xxxx")).toBe(false);
    fs.rmSync(dir, { recursive: true, force: true });
  });

  it("stops after 20,000 visible characters", () => {
    const html = `<html><body><p>${"alpha ".repeat(8000)}TAIL-SHOULD-DROP</p></body></html>`;
    const text = extractPlainText(html);
    expect(text.length).toBe(SEARCH_TEXT_MAX);
    expect(text).not.toContain("TAIL-SHOULD-DROP");
  });
});
