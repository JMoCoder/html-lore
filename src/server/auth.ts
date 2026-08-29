import crypto from "node:crypto";
import { authEnabled, type ServerSettings } from "@/server/settings";
import type { AuthenticatedUser } from "@/server/types";
import { UserStore, userFromRecord } from "@/server/users";

export class AuthError extends Error {
  status: number;
  constructor(message: string, status = 401) {
    super(message);
    this.name = "AuthError";
    this.status = status;
  }
}

export function sessionStatus(settings: ServerSettings, cookieValue: string | undefined) {
  if (!authEnabled(settings)) {
    return { enabled: false, authenticated: true, user: null, data_id: null };
  }
  const user = verifySessionToken(settings, cookieValue ?? "");
  return {
    enabled: true,
    authenticated: Boolean(user),
    user: user?.username ?? null,
    data_id: user?.dataId ?? null,
  };
}

export function login(
  settings: ServerSettings,
  username: string,
  password: string,
): { body: Record<string, unknown>; token: string | null } {
  if (!authEnabled(settings)) {
    return { body: { enabled: false, authenticated: true, user: null, data_id: null }, token: null };
  }
  const store = new UserStore(settings);
  store.ensureBootstrapAdmin();
  const user = store.authenticate(username, password);
  if (!user) throw new AuthError("Invalid username or password.");
  return {
    body: { enabled: true, authenticated: true, user: user.username, data_id: user.dataId },
    token: makeSessionToken(settings, user.username),
  };
}

export function logoutBody(settings: ServerSettings) {
  return { enabled: authEnabled(settings), authenticated: false, user: null };
}

export function makeSessionToken(settings: ServerSettings, username: string): string {
  const expiresAt = Math.floor(Date.now() / 1000) + settings.sessionMaxAgeSeconds;
  const payload = encodeJson({ sub: username, exp: expiresAt });
  return `${payload}.${sign(settings, payload)}`;
}

export function verifySessionToken(settings: ServerSettings, token: string): AuthenticatedUser | null {
  if (!token) return null;
  const index = token.indexOf(".");
  if (index < 0) return null;
  const payload = token.slice(0, index);
  const signature = token.slice(index + 1);
  if (!payload || !signature) return null;
  if (!constantTimeEqual(signature, sign(settings, payload))) return null;
  try {
    const data = JSON.parse(Buffer.from(padBase64(payload), "base64url").toString("utf8")) as {
      sub?: string;
      exp?: number;
    };
    const username = String(data.sub ?? "");
    if (Number(data.exp ?? 0) < Math.floor(Date.now() / 1000)) return null;
    const store = new UserStore(settings);
    store.ensureBootstrapAdmin();
    const record = store.findUser(username);
    if (!record || record.enabled === false) return null;
    return userFromRecord(record);
  } catch {
    return null;
  }
}

function sign(settings: ServerSettings, payload: string): string {
  const digest = crypto.createHmac("sha256", settings.sessionSecret).update(payload).digest();
  return digest.toString("base64url");
}

function encodeJson(value: Record<string, unknown>): string {
  return Buffer.from(JSON.stringify(value), "utf8").toString("base64url");
}

function padBase64(value: string): string {
  return value + "=".repeat((4 - (value.length % 4)) % 4);
}

function constantTimeEqual(left: string, right: string): boolean {
  const leftBuf = Buffer.from(left);
  const rightBuf = Buffer.from(right);
  if (leftBuf.length !== rightBuf.length) return false;
  return crypto.timingSafeEqual(leftBuf, rightBuf);
}

export function matchesApiToken(settings: ServerSettings, header: string | null, queryToken: string | null): boolean {
  if (!settings.apiToken) return false;
  const bearer = header?.startsWith("Bearer ") ? header.slice(7).trim() : "";
  return bearer === settings.apiToken || queryToken === settings.apiToken;
}
