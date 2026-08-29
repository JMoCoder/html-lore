import fs from "node:fs";
import path from "node:path";

export class PathEscapeError extends Error {
  constructor(message = "Path escapes the allowed directory.") {
    super(message);
    this.name = "PathEscapeError";
  }
}

export function ensureWithin(target: string, root: string): void {
  const resolvedTarget = path.resolve(target);
  const resolvedRoot = path.resolve(root);
  const relative = path.relative(resolvedRoot, resolvedTarget);
  if (relative.startsWith("..") || path.isAbsolute(relative)) {
    throw new PathEscapeError();
  }
}

export function metadataPathForItem(metaDir: string | null, itemId: string): string | null {
  if (!metaDir) return null;
  const relative = itemId.replace(/\.html?$/i, ".yml");
  return path.join(metaDir, "items", relative);
}

export function removeEmptyParents(start: string, stopAt: string): void {
  const stop = path.resolve(stopAt);
  let current = path.resolve(start);
  while (current !== stop && current.startsWith(stop + path.sep)) {
    try {
      fs.rmdirSync(current);
    } catch {
      return;
    }
    current = path.dirname(current);
  }
}

export function posixJoin(...parts: string[]): string {
  return parts.join("/").replace(/\\/g, "/");
}

export function writeFileDurable(filePath: string, content: string, root: string): void {
  const tempPath = `${filePath}.${process.pid}.tmp`;
  ensureWithin(filePath, root);
  ensureWithin(tempPath, root);
  fs.writeFileSync(tempPath, content, "utf8");
  const fd = fs.openSync(tempPath, "r+");
  try {
    fs.fsyncSync(fd);
  } finally {
    fs.closeSync(fd);
  }
  fs.renameSync(tempPath, filePath);
}
