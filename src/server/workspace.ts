import fs from "node:fs";
import path from "node:path";
import { ensureUserDirs, type ServerSettings } from "@/server/settings";

export function ensureWorkspace(settings: ServerSettings, projectRoot = process.cwd()): void {
  ensureUserDirs(settings);
  if (hasHtml(settings.contentDir)) return;
  const examplesContent = path.join(projectRoot, "examples", "content");
  const examplesMeta = path.join(projectRoot, "examples", "meta");
  if (!fs.existsSync(examplesContent)) return;
  copyDir(examplesContent, settings.contentDir);
  if (settings.metaDir && fs.existsSync(examplesMeta)) copyDir(examplesMeta, settings.metaDir);
}

function hasHtml(root: string): boolean {
  if (!fs.existsSync(root)) return false;
  const stack = [root];
  while (stack.length) {
    const current = stack.pop()!;
    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      const full = path.join(current, entry.name);
      if (entry.isDirectory()) stack.push(full);
      else if (entry.isFile() && entry.name.endsWith(".html")) return true;
    }
  }
  return false;
}

function copyDir(src: string, dest: string): void {
  fs.mkdirSync(dest, { recursive: true });
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const from = path.join(src, entry.name);
    const to = path.join(dest, entry.name);
    if (entry.isDirectory()) copyDir(from, to);
    else fs.copyFileSync(from, to);
  }
}
