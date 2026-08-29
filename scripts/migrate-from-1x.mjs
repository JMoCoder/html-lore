#!/usr/bin/env node
/**
 * Copy a 1.x file-backed notebook into a 2.0 data directory.
 * There is no SQL database: notes are HTML + YAML sidecars.
 *
 * Kept as plain Node so operators can run it without a TypeScript toolchain.
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const SKIP_TOP_LEVEL = new Set(["public"]);
const SKIP_META_DIRS = new Set(["ai"]);
const SKIP_CONFIG_FILES = new Set(["jobs.json", "ai_provider.json"]);
const USER_SKIP_DIRS = new Set(["public"]);

export class MigrateError extends Error {
  constructor(message) {
    super(message);
    this.name = "MigrateError";
  }
}

export function migrateFrom1x(sourceRoot, destRoot, options = {}) {
  const source = path.resolve(sourceRoot);
  const dest = path.resolve(destRoot);
  const dryRun = Boolean(options.dryRun);
  const force = Boolean(options.force);

  if (!fs.existsSync(source) || !fs.statSync(source).isDirectory()) {
    throw new MigrateError(`Source is not a directory: ${source}`);
  }
  if (samePath(source, dest) || isInside(dest, source) || isInside(source, dest)) {
    throw new MigrateError("Source and destination must be distinct directories.");
  }

  const destContent = path.join(dest, "content");
  if (!force && hasHtml(destContent)) {
    throw new MigrateError(`Destination already has HTML notes (${destContent}). Pass force: true to overwrite.`);
  }

  const copied = [];
  const skipped = [];

  copyNotebookTree(source, dest, { dryRun, copied, skipped });

  const countedRoot = dryRun ? source : dest;
  return {
    source,
    dest,
    dryRun,
    htmlCount: countFiles(path.join(countedRoot, "content"), ".html"),
    ymlCount: countFiles(path.join(countedRoot, "meta", "items"), ".yml"),
    copied,
    skipped,
  };
}

function copyNotebookTree(source, dest, state) {
  copyDirFiltered(path.join(source, "content"), path.join(dest, "content"), state, new Set());
  copyMeta(path.join(source, "meta"), path.join(dest, "meta"), state);

  const usersFile = path.join(source, "users.json");
  if (fs.existsSync(usersFile) && fs.statSync(usersFile).isFile()) {
    copyFile(usersFile, path.join(dest, "users.json"), state);
  } else {
    state.skipped.push("users.json (missing)");
  }

  const usersDir = path.join(source, "users");
  if (fs.existsSync(usersDir) && fs.statSync(usersDir).isDirectory()) {
    copyUsers(usersDir, path.join(dest, "users"), state);
  }

  for (const name of fs.existsSync(source) ? fs.readdirSync(source) : []) {
    if (SKIP_TOP_LEVEL.has(name)) state.skipped.push(`${name}/`);
  }
}

function copyMeta(sourceMeta, destMeta, state) {
  if (!fs.existsSync(sourceMeta) || !fs.statSync(sourceMeta).isDirectory()) {
    state.skipped.push("meta/ (missing)");
    return;
  }
  const items = path.join(sourceMeta, "items");
  if (fs.existsSync(items)) copyDirFiltered(items, path.join(destMeta, "items"), state, new Set());

  const config = path.join(sourceMeta, "config");
  if (fs.existsSync(config) && fs.statSync(config).isDirectory()) {
    fs.mkdirSync(path.join(destMeta, "config"), { recursive: true });
    for (const entry of fs.readdirSync(config, { withFileTypes: true })) {
      const relative = path.posix.join("meta/config", entry.name);
      if (!entry.isFile()) {
        state.skipped.push(`${relative}/`);
        continue;
      }
      if (SKIP_CONFIG_FILES.has(entry.name)) {
        state.skipped.push(relative);
        continue;
      }
      copyFile(path.join(config, entry.name), path.join(destMeta, "config", entry.name), state);
    }
  }

  for (const name of fs.readdirSync(sourceMeta)) {
    if (SKIP_META_DIRS.has(name)) state.skipped.push(`meta/${name}/`);
  }
}

function copyUsers(sourceUsers, destUsers, state) {
  for (const entry of fs.readdirSync(sourceUsers, { withFileTypes: true })) {
    const from = path.join(sourceUsers, entry.name);
    const to = path.join(destUsers, entry.name);
    if (entry.isFile()) {
      copyFile(from, to, state);
      continue;
    }
    if (!entry.isDirectory()) continue;
    for (const child of fs.readdirSync(from, { withFileTypes: true })) {
      if (child.isDirectory() && USER_SKIP_DIRS.has(child.name)) {
        state.skipped.push(`users/${entry.name}/${child.name}/`);
        continue;
      }
      const childFrom = path.join(from, child.name);
      const childTo = path.join(to, child.name);
      if (child.isDirectory()) copyDirFiltered(childFrom, childTo, state, new Set());
      else if (child.isFile()) copyFile(childFrom, childTo, state);
    }
  }
}

function copyDirFiltered(source, dest, state, skipNames) {
  if (!fs.existsSync(source) || !fs.statSync(source).isDirectory()) return;
  if (!state.dryRun) fs.mkdirSync(dest, { recursive: true });
  for (const entry of fs.readdirSync(source, { withFileTypes: true })) {
    if (skipNames.has(entry.name)) {
      state.skipped.push(path.relative(path.dirname(dest), path.join(dest, entry.name)) + (entry.isDirectory() ? "/" : ""));
      continue;
    }
    const from = path.join(source, entry.name);
    const to = path.join(dest, entry.name);
    if (entry.isDirectory()) copyDirFiltered(from, to, state, skipNames);
    else if (entry.isFile()) copyFile(from, to, state);
  }
}

function copyFile(from, to, state) {
  state.copied.push(to);
  if (state.dryRun) return;
  fs.mkdirSync(path.dirname(to), { recursive: true });
  fs.copyFileSync(from, to);
}

function hasHtml(root) {
  return countFiles(root, ".html") > 0;
}

function countFiles(root, suffix) {
  if (!fs.existsSync(root) || !fs.statSync(root).isDirectory()) return 0;
  let count = 0;
  const stack = [root];
  while (stack.length) {
    const current = stack.pop();
    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      const full = path.join(current, entry.name);
      if (entry.isDirectory()) stack.push(full);
      else if (entry.isFile() && entry.name.endsWith(suffix)) count += 1;
    }
  }
  return count;
}

function samePath(a, b) {
  return path.resolve(a) === path.resolve(b);
}

function isInside(inner, outer) {
  const relative = path.relative(path.resolve(outer), path.resolve(inner));
  return relative === "" || (!relative.startsWith("..") && !path.isAbsolute(relative));
}

function printUsage() {
  process.stderr.write(`Copy a 1.x HTMlore data directory into a 2.0 data directory.

Usage:
  node scripts/migrate-from-1x.mjs [--dry-run] [--force] <source-data> <dest-data>

Example:
  node scripts/migrate-from-1x.mjs /srv/html-lore/data /srv/html-lore-v2/data

Copied: content/, meta/items/, meta/config/{shares,share-index,navigation}.json, users.json, users/<id>/{content,meta}
Skipped: public/, meta/ai/, meta/config/jobs.json, meta/config/ai_provider.json, users/<id>/public/
`);
}

function parseArgs(argv) {
  const flags = { dryRun: false, force: false };
  const positional = [];
  for (const arg of argv) {
    if (arg === "--dry-run") flags.dryRun = true;
    else if (arg === "--force") flags.force = true;
    else if (arg === "--help" || arg === "-h") flags.help = true;
    else if (arg.startsWith("-")) throw new MigrateError(`Unknown flag: ${arg}`);
    else positional.push(arg);
  }
  return { flags, positional };
}

function main() {
  try {
    const { flags, positional } = parseArgs(process.argv.slice(2));
    if (flags.help || positional.length !== 2) {
      printUsage();
      process.exit(flags.help ? 0 : 2);
    }
    const result = migrateFrom1x(positional[0], positional[1], flags);
    process.stdout.write(
      `${JSON.stringify(
        {
          ok: true,
          dryRun: result.dryRun,
          source: result.source,
          dest: result.dest,
          htmlCount: result.htmlCount,
          ymlCount: result.ymlCount,
          copied: result.copied.length,
          skipped: result.skipped,
        },
        null,
        2,
      )}\n`,
    );
  } catch (error) {
    process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
    process.exit(1);
  }
}

const invokedDirectly = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (invokedDirectly) main();
