import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import type { ServerSettings } from "@/server/settings";
import type { AuthenticatedUser } from "@/server/types";

const PBKDF2_ITERATIONS = 200_000;

export class UserStoreError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "UserStoreError";
  }
}

export class UserStore {
  constructor(readonly settings: ServerSettings) {}

  get path(): string | null {
    return this.settings.usersFile;
  }

  authenticate(username: string, password: string): AuthenticatedUser | null {
    const record = this.findUser(username);
    if (!record || record.enabled === false) return null;
    if (!verifyPassword(password, String(record.password_hash || ""))) return null;
    this.updateLastLogin(String(record.username));
    return userFromRecord(record);
  }

  findUser(username: string): Record<string, unknown> | null {
    const key = username.toLowerCase();
    for (const record of this.read().users) {
      if (!record || typeof record !== "object") continue;
      if (String(record.username || "").toLowerCase() === key) return record;
    }
    return null;
  }

  addUser(input: {
    username: string;
    password: string;
    role?: string;
    dataId?: string;
    enabled?: boolean;
    replaceExisting?: boolean;
  }): Record<string, unknown> {
    const cleaned = input.username.trim();
    if (!cleaned) throw new UserStoreError("Username is required.");
    if (!input.password) throw new UserStoreError("Password is required.");
    const data = this.read();
    const now = utcNow();
    const existingIndex = data.users.findIndex(
      (record) => String(record.username || "").toLowerCase() === cleaned.toLowerCase(),
    );
    if (existingIndex >= 0 && !input.replaceExisting) throw new UserStoreError("User already exists.");
    const existing = existingIndex >= 0 ? data.users[existingIndex]! : {};
    const record: Record<string, unknown> = {
      ...existing,
      username: cleaned,
      password_hash: hashPassword(input.password),
      role: (input.role ?? "user").trim() || "user",
      enabled: input.enabled ?? true,
      data_id: safeDataId(input.dataId || String(existing.data_id || dataIdForUsername(cleaned))),
      updated_at: now,
    };
    record.created_at = existing.created_at || now;
    if (existingIndex < 0) data.users.push(record);
    else data.users[existingIndex] = record;
    this.write(data);
    return publicUserRecord(record);
  }

  ensureBootstrapAdmin(): void {
    if (!this.path) return;
    const data = this.read();
    if (data.users.length) return;
    if (!this.settings.authUsername || !this.settings.authPassword) return;
    const now = utcNow();
    this.write({
      version: 1,
      users: [
        {
          username: this.settings.authUsername,
          password_hash: hashPassword(this.settings.authPassword),
          role: "admin",
          enabled: true,
          data_id: "default",
          created_at: now,
          updated_at: now,
        },
      ],
    });
  }

  private updateLastLogin(username: string): void {
    if (!this.path) return;
    const data = this.read();
    let changed = false;
    const now = utcNow();
    for (const record of data.users) {
      if (String(record.username || "").toLowerCase() === username.toLowerCase()) {
        record.last_login_at = now;
        changed = true;
        break;
      }
    }
    if (changed) this.write(data);
  }

  private read(): { version: number; users: Record<string, unknown>[] } {
    if (!this.path || !fs.existsSync(this.path)) return { version: 1, users: [] };
    let parsed: unknown;
    try {
      parsed = JSON.parse(fs.readFileSync(this.path, "utf8"));
    } catch {
      throw new UserStoreError("User store is not valid JSON.");
    }
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
      throw new UserStoreError("User store must be a JSON object.");
    }
    const users = (parsed as { users?: unknown }).users ?? [];
    if (!Array.isArray(users)) throw new UserStoreError("User store users must be a list.");
    return {
      version: Number((parsed as { version?: unknown }).version || 1),
      users: users.filter((record) => record && typeof record === "object") as Record<string, unknown>[],
    };
  }

  private write(data: { version: number; users: Record<string, unknown>[] }): void {
    if (!this.path) return;
    fs.mkdirSync(path.dirname(this.path), { recursive: true });
    fs.writeFileSync(this.path, `${JSON.stringify(data, null, 2)}\n`, "utf8");
  }
}

export function userFromRecord(record: Record<string, unknown>): AuthenticatedUser {
  const username = String(record.username || "").trim();
  return {
    username,
    dataId: safeDataId(String(record.data_id || dataIdForUsername(username))),
    role: String(record.role || "user"),
  };
}

export function publicUserRecord(record: Record<string, unknown>) {
  return {
    username: String(record.username || ""),
    role: String(record.role || "user"),
    enabled: record.enabled !== false,
    data_id: safeDataId(String(record.data_id || "")),
  };
}

export function hashPassword(password: string): string {
  const salt = crypto.randomBytes(16);
  const digest = crypto.pbkdf2Sync(password, salt, PBKDF2_ITERATIONS, 32, "sha256");
  return `pbkdf2_sha256$${PBKDF2_ITERATIONS}$${toB64Url(salt)}$${toB64Url(digest)}`;
}

export function verifyPassword(password: string, stored: string): boolean {
  if (!stored.startsWith("pbkdf2_sha256$")) return false;
  try {
    const [, iterationsValue, saltValue, digestValue] = stored.split("$");
    const iterations = Number(iterationsValue);
    const salt = fromB64Url(saltValue ?? "");
    const expected = fromB64Url(digestValue ?? "");
    const actual = crypto.pbkdf2Sync(password, salt, iterations, expected.length, "sha256");
    return crypto.timingSafeEqual(actual, expected);
  } catch {
    return false;
  }
}

export function dataIdForUsername(username: string): string {
  return safeDataId(username.toLowerCase());
}

export function safeDataId(value: string): string {
  const normalized = value.toLowerCase().replace(/[^a-z0-9._-]+/g, "-").replace(/^[-._]+|[-._]+$/g, "");
  return normalized || "user";
}

export function utcNow(): string {
  return new Date().toISOString();
}

function toB64Url(buffer: Buffer): string {
  return buffer.toString("base64url");
}

function fromB64Url(value: string): Buffer {
  return Buffer.from(value + "=".repeat((4 - (value.length % 4)) % 4), "base64url");
}
