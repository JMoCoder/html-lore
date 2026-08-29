import fs from "node:fs";
import path from "node:path";

export type ServerSettings = {
  contentDir: string;
  metaDir: string | null;
  publicDir: string;
  siteTitle: string;
  maxUploadBytes: number;
  apiToken: string;
  authUsername: string;
  authPassword: string;
  usersFile: string | null;
  userDataDir: string | null;
  sessionSecret: string;
  sessionCookieName: string;
  sessionMaxAgeSeconds: number;
  sessionSecure: boolean;
  shareInteractiveEnabled: boolean;
};

export function loadSettings(env: NodeJS.ProcessEnv = process.env): ServerSettings {
  const contentDir = path.resolve(getEnv(env, "CONTENT", "content"));
  const metaValue = getEnv(env, "META", "meta");
  const metaDir = metaValue ? path.resolve(metaValue) : null;
  return {
    contentDir,
    metaDir,
    publicDir: path.resolve(getEnv(env, "PUBLIC", "public")),
    siteTitle: getEnv(env, "TITLE", "HTMlore"),
    maxUploadBytes: parsePositiveInt(getEnv(env, "MAX_UPLOAD_BYTES", String(100 * 1024 * 1024)), 100 * 1024 * 1024),
    apiToken: getEnv(env, "API_TOKEN", "").trim(),
    authUsername: getEnv(env, "AUTH_USERNAME", "").trim(),
    authPassword: getEnv(env, "AUTH_PASSWORD", ""),
    usersFile: parseOptionalPath(env[`HTML_LORE_USERS_FILE`], path.join(path.dirname(contentDir), "users.json")),
    userDataDir: parseOptionalPath(env[`HTML_LORE_USER_DATA_DIR`], path.join(path.dirname(contentDir), "users")),
    sessionSecret: getEnv(env, "SESSION_SECRET", "").trim(),
    sessionCookieName: getEnv(env, "SESSION_COOKIE_NAME", "html_lore_session").trim() || "html_lore_session",
    sessionMaxAgeSeconds: parsePositiveInt(getEnv(env, "SESSION_MAX_AGE_SECONDS", String(7 * 24 * 60 * 60)), 7 * 24 * 60 * 60),
    sessionSecure: parseBool(getEnv(env, "SESSION_SECURE", "false")),
    shareInteractiveEnabled: parseBool(getEnv(env, "SHARE_INTERACTIVE_ENABLED", "true")),
  };
}

export function authEnabled(settings: ServerSettings): boolean {
  if (!settings.sessionSecret) return false;
  if (settings.authUsername && settings.authPassword) return true;
  return Boolean(settings.usersFile && fs.existsSync(settings.usersFile));
}

export function forUser(settings: ServerSettings, dataId: string): ServerSettings {
  if (dataId === "default" || !settings.userDataDir) return settings;
  const userRoot = path.join(settings.userDataDir, dataId);
  const scoped: ServerSettings = {
    ...settings,
    contentDir: path.join(userRoot, "content"),
    metaDir: settings.metaDir ? path.join(userRoot, "meta") : null,
    publicDir: path.join(userRoot, "public"),
  };
  ensureUserDirs(scoped);
  return scoped;
}

export function ensureUserDirs(settings: ServerSettings): void {
  fs.mkdirSync(settings.contentDir, { recursive: true });
  if (settings.metaDir) {
    fs.mkdirSync(path.join(settings.metaDir, "items"), { recursive: true });
    fs.mkdirSync(path.join(settings.metaDir, "config"), { recursive: true });
  }
  fs.mkdirSync(settings.publicDir, { recursive: true });
}

function getEnv(env: NodeJS.ProcessEnv, name: string, fallback: string): string {
  const value = env[`HTML_LORE_${name}`];
  return value !== undefined ? value : fallback;
}

function parseBool(value: string): boolean {
  return ["1", "true", "yes", "on"].includes(value.trim().toLowerCase());
}

function parsePositiveInt(value: string, fallback: number): number {
  const parsed = Number.parseInt(value, 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}

function parseOptionalPath(value: string | undefined, fallback: string): string | null {
  if (value === undefined) return fallback;
  const cleaned = value.trim();
  return cleaned ? path.resolve(cleaned) : null;
}
