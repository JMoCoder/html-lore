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
const DEFAULT_STRIP_TAGS = ["AI生成"];

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
  const mergeUsers = Boolean(options.mergeUsers);
  const stripTags = mergeUsers ? normalizeStripTags(options.stripTags) : [];

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
  const claimed = new Map();
  const state = { dryRun, mergeUsers, stripTags, copied, skipped, claimed };

  copyNotebookTree(source, dest, state);
  if (mergeUsers) {
    mergeUserLibraries(source, dest, state);
    rewriteShareIndexToRoot(dest, state);
    if (!dryRun && stripTags.length) stripTagsInYamlTree(path.join(dest, "meta", "items"), stripTags);
  }

  const countedRoot = dryRun ? source : dest;
  return {
    source,
    dest,
    dryRun,
    mergeUsers,
    htmlCount: mergeUsers && dryRun
      ? countClaimed(claimed, "content/", ".html")
      : countFiles(path.join(countedRoot, "content"), ".html"),
    ymlCount: mergeUsers && dryRun
      ? countClaimed(claimed, "meta/items/", ".yml")
      : countFiles(path.join(countedRoot, "meta", "items"), ".yml"),
    copied,
    skipped,
  };
}

function copyNotebookTree(source, dest, state) {
  copyDirFiltered(path.join(source, "content"), path.join(dest, "content"), state, new Set(), "content");
  copyMeta(path.join(source, "meta"), path.join(dest, "meta"), state);

  const usersFile = path.join(source, "users.json");
  if (state.mergeUsers) {
    state.skipped.push("users.json (merge-users: single-library dest)");
  } else if (fs.existsSync(usersFile) && fs.statSync(usersFile).isFile()) {
    copyFile(usersFile, path.join(dest, "users.json"), state);
  } else {
    state.skipped.push("users.json (missing)");
  }

  const usersDir = path.join(source, "users");
  if (fs.existsSync(usersDir) && fs.statSync(usersDir).isDirectory()) {
    if (state.mergeUsers) state.skipped.push("users/ (merged into root)");
    else copyUsers(usersDir, path.join(dest, "users"), state);
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
  if (fs.existsSync(items)) copyDirFiltered(items, path.join(destMeta, "items"), state, new Set(), "meta/items");

  const config = path.join(sourceMeta, "config");
  if (fs.existsSync(config) && fs.statSync(config).isDirectory()) {
    if (!state.dryRun) fs.mkdirSync(path.join(destMeta, "config"), { recursive: true });
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

function mergeUserLibraries(source, dest, state) {
  const usersDir = path.join(source, "users");
  if (!fs.existsSync(usersDir) || !fs.statSync(usersDir).isDirectory()) return;
  for (const entry of fs.readdirSync(usersDir, { withFileTypes: true })) {
    if (!entry.isDirectory()) continue;
    const owner = `users/${entry.name}`;
    const from = path.join(usersDir, entry.name);
    copyDirFiltered(path.join(from, "content"), path.join(dest, "content"), state, new Set(), "content", owner);
    const userMeta = path.join(from, "meta");
    if (fs.existsSync(userMeta) && fs.statSync(userMeta).isDirectory()) {
      copyDirFiltered(path.join(userMeta, "items"), path.join(dest, "meta", "items"), state, new Set(), "meta/items", owner);
      mergeUserConfig(path.join(userMeta, "config"), path.join(dest, "meta", "config"), owner, state);
      if (fs.existsSync(path.join(userMeta, "ai"))) state.skipped.push(`${owner}/meta/ai/`);
    }
    if (fs.existsSync(path.join(from, "public"))) state.skipped.push(`${owner}/public/`);
  }
}

function mergeUserConfig(sourceConfig, destConfig, owner, state) {
  if (!fs.existsSync(sourceConfig) || !fs.statSync(sourceConfig).isDirectory()) return;
  if (!state.dryRun) fs.mkdirSync(destConfig, { recursive: true });
  for (const entry of fs.readdirSync(sourceConfig, { withFileTypes: true })) {
    const relative = `${owner}/meta/config/${entry.name}`;
    if (!entry.isFile()) {
      state.skipped.push(`${relative}/`);
      continue;
    }
    if (SKIP_CONFIG_FILES.has(entry.name) || entry.name === "ai_provider.json") {
      state.skipped.push(relative);
      continue;
    }
    const from = path.join(sourceConfig, entry.name);
    const to = path.join(destConfig, entry.name);
    if (entry.name === "shares.json") {
      mergeShareStore(from, to, state);
      continue;
    }
    if (entry.name === "share-index.json") {
      mergeShareIndex(from, to, state);
      continue;
    }
    if (fs.existsSync(to) || (state.dryRun && state.copied.includes(to))) {
      state.skipped.push(`${relative} (root already has meta/config/${entry.name})`);
      continue;
    }
    copyFile(from, to, state);
  }
}

function mergeShareStore(from, to, state) {
  if (!fs.existsSync(to)) {
    copyFile(from, to, state);
    return;
  }
  if (state.dryRun) {
    state.copied.push(to);
    return;
  }
  const incoming = readJson(from, { shares: [] });
  const dest = readJson(to, { shares: [] });
  if (!Array.isArray(dest.shares)) dest.shares = [];
  const ids = new Set(dest.shares.map((row) => String(row?.id || "")));
  for (const record of incoming.shares || []) {
    const id = String(record?.id || "");
    if (id && ids.has(id)) {
      state.skipped.push(`meta/config/shares.json#${id}`);
      continue;
    }
    dest.shares.push(record);
    if (id) ids.add(id);
  }
  fs.writeFileSync(to, `${JSON.stringify(dest, null, 2)}\n`);
  state.copied.push(to);
}

function mergeShareIndex(from, to, state) {
  if (!fs.existsSync(to)) {
    copyFile(from, to, state);
    return;
  }
  if (state.dryRun) {
    state.copied.push(to);
    return;
  }
  const incoming = readJson(from, { tokens: {} });
  const dest = readJson(to, { tokens: {} });
  dest.tokens = { ...(dest.tokens || {}), ...(incoming.tokens || {}) };
  fs.writeFileSync(to, `${JSON.stringify(dest, null, 2)}\n`);
  state.copied.push(to);
}

function rewriteShareIndexToRoot(dest, state) {
  const indexPath = path.join(dest, "meta", "config", "share-index.json");
  if (state.dryRun || !fs.existsSync(indexPath)) return;
  try {
    const data = readJson(indexPath, { tokens: {} });
    if (!data.tokens || typeof data.tokens !== "object") return;
    for (const key of Object.keys(data.tokens)) data.tokens[key] = "default";
    fs.writeFileSync(indexPath, `${JSON.stringify(data, null, 2)}\n`);
  } catch {
    /* keep the copied file */
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

function copyDirFiltered(source, dest, state, skipNames, claimPrefix, owner) {
  if (!fs.existsSync(source) || !fs.statSync(source).isDirectory()) return;
  if (!state.dryRun) fs.mkdirSync(dest, { recursive: true });
  for (const entry of fs.readdirSync(source, { withFileTypes: true })) {
    if (skipNames.has(entry.name)) {
      state.skipped.push(path.relative(path.dirname(dest), path.join(dest, entry.name)) + (entry.isDirectory() ? "/" : ""));
      continue;
    }
    const from = path.join(source, entry.name);
    const to = path.join(dest, entry.name);
    const claimKey = claimPrefix ? path.posix.join(claimPrefix, entry.name) : "";
    if (entry.isDirectory()) copyDirFiltered(from, to, state, skipNames, claimKey, owner);
    else if (entry.isFile()) {
      if (claimKey && state.claimed) {
        const previous = state.claimed.get(claimKey);
        if (previous) {
          throw new MigrateError(`Path collision: ${claimKey} (${previous} and ${owner || "root"})`);
        }
        state.claimed.set(claimKey, owner || "root");
      }
      copyFile(from, to, state);
    }
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

function stripTagsInYamlTree(root, tags) {
  if (!fs.existsSync(root) || !fs.statSync(root).isDirectory()) return;
  const stack = [root];
  while (stack.length) {
    const current = stack.pop();
    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      const full = path.join(current, entry.name);
      if (entry.isDirectory()) stack.push(full);
      else if (entry.isFile() && entry.name.endsWith(".yml")) {
        const next = stripYamlTags(fs.readFileSync(full, "utf8"), tags);
        fs.writeFileSync(full, next);
      }
    }
  }
}

function stripYamlTags(text, tags) {
  const strip = new Set(tags);
  const lines = text.split(/\r?\n/);
  const out = [];
  let inTags = false;
  for (const line of lines) {
    if (/^tags:\s*$/.test(line)) {
      inTags = true;
      out.push(line);
      continue;
    }
    if (inTags) {
      const item = line.match(/^\s+-\s+(.+?)\s*$/);
      if (item) {
        const value = unwrapYamlScalar(item[1]);
        if (strip.has(value)) continue;
        out.push(line);
        continue;
      }
      inTags = false;
    }
    out.push(line);
  }
  return out.join("\n");
}

function unwrapYamlScalar(value) {
  const text = value.trim();
  if (
    (text.startsWith('"') && text.endsWith('"')) ||
    (text.startsWith("'") && text.endsWith("'"))
  ) {
    return text.slice(1, -1);
  }
  return text;
}

function normalizeStripTags(value) {
  if (value == null) return [...DEFAULT_STRIP_TAGS];
  if (Array.isArray(value)) return value.map((item) => String(item).trim()).filter(Boolean);
  return String(value)
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function countClaimed(claimed, prefix, suffix) {
  let count = 0;
  for (const key of claimed.keys()) {
    if (key.startsWith(prefix) && key.endsWith(suffix)) count += 1;
  }
  return count;
}

function readJson(filePath, fallback) {
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf8"));
  } catch {
    return fallback;
  }
}

function printUsage() {
  process.stderr.write(`Copy a 1.x HTMlore data directory into a 2.0 data directory.

Usage:
  node scripts/migrate-from-1x.mjs [--dry-run] [--force] [--merge-users] [--strip-tags=a,b] <source-data> <dest-data>

Example:
  node scripts/migrate-from-1x.mjs /srv/html-lore/data /srv/html-lore-v2/data
  node scripts/migrate-from-1x.mjs --merge-users /srv/html-lore/data /srv/html-lore-v2/data

Copied: content/, meta/items/, meta/config/{shares,share-index,navigation}.json
Default also copies users.json and users/<id>/{content,meta}.
--merge-users flattens users/<id>/{content,meta} into the dest root (no-login single library),
skips users.json, merges shares.json, rewrites share-index tokens to default,
and strips 1.x AI tags (default: AI生成). Path collisions abort the run.

Skipped: public/, meta/ai/, meta/config/jobs.json, meta/config/ai_provider.json, users/<id>/public/
`);
}

function parseArgs(argv) {
  const flags = { dryRun: false, force: false, mergeUsers: false };
  const positional = [];
  for (const arg of argv) {
    if (arg === "--dry-run") flags.dryRun = true;
    else if (arg === "--force") flags.force = true;
    else if (arg === "--merge-users") flags.mergeUsers = true;
    else if (arg === "--strip-tags" || arg.startsWith("--strip-tags=")) {
      flags.stripTags = arg.includes("=") ? arg.slice(arg.indexOf("=") + 1) : "";
    } else if (arg === "--help" || arg === "-h") flags.help = true;
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
          mergeUsers: result.mergeUsers,
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
