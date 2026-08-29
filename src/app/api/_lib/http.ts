import { cookies } from "next/headers";
import {
  authEnabled,
  ensureWorkspace,
  forUser,
  loadSettings,
  matchesApiToken,
  verifySessionToken,
  type AuthenticatedUser,
  type ServerSettings,
} from "@/server";

export type RequestContext = {
  settings: ServerSettings;
  root: ServerSettings;
  user: AuthenticatedUser | null;
};

export async function getRootSettings(): Promise<ServerSettings> {
  const settings = loadSettings();
  ensureWorkspace(settings);
  return settings;
}

export async function getRequestContext(request: Request): Promise<RequestContext> {
  const root = await getRootSettings();
  const user = await resolveUser(root, request);
  const settings = user ? forUser(root, user.dataId) : root;
  return { settings, root, user };
}

export async function requireApiAuth(request: Request): Promise<RequestContext> {
  const root = await getRootSettings();
  const header = request.headers.get("authorization");
  const queryToken = new URL(request.url).searchParams.get("access_token");
  if (matchesApiToken(root, header, queryToken)) {
    return { settings: root, root, user: null };
  }
  if (!authEnabled(root)) {
    return { settings: root, root, user: null };
  }
  const user = await resolveUser(root, request);
  if (!user) {
    throw Object.assign(new Error("Login required."), { status: 401, detail: "Login required." });
  }
  return { settings: forUser(root, user.dataId), root, user };
}

async function resolveUser(settings: ServerSettings, request: Request): Promise<AuthenticatedUser | null> {
  const store = await cookies();
  const fromStore = store.get(settings.sessionCookieName)?.value;
  const fromRequest = request.headers
    .get("cookie")
    ?.split(";")
    .map((part) => part.trim())
    .find((part) => part.startsWith(`${settings.sessionCookieName}=`))
    ?.slice(settings.sessionCookieName.length + 1);
  return verifySessionToken(settings, decodeURIComponent(fromStore || fromRequest || ""));
}

export function jsonOk(body: unknown, init?: ResponseInit) {
  return Response.json(body, init);
}

export function jsonError(detail: unknown, status: number) {
  return Response.json({ detail }, { status });
}

export function mapDomainError(error: unknown): Response {
  const err = error as { name?: string; message?: string; status?: number; detail?: unknown; safety?: unknown };
  if (err.status && err.detail) return jsonError(err.detail, err.status);
  if (err.status && err.message) return jsonError(err.message, err.status);
  const message = err.message || "Unexpected error.";
  switch (err.name) {
    case "AuthError":
      return jsonError(message, 401);
    case "ItemContentError":
      return jsonError(message, message.includes("not found") ? 404 : 400);
    case "ItemDeleteError":
    case "ItemMetadataError":
    case "ItemStateError":
    case "ItemContentUpdateError":
    case "UploadError":
      return jsonError(message, message === "Item not found." || message === "Item not found" ? 404 : 400);
    case "ShareSafetyConfirmationError":
      return jsonError(
        {
          message,
          safety: err.safety,
          requires_confirmation: true,
        },
        409,
      );
    case "ShareSafetyError":
      return jsonError({ message, safety: err.safety }, 400);
    case "ShareError":
      return jsonError(message, message === "Share not found." || message === "Item not found." ? 404 : 400);
    case "TaxonomyError":
    case "NavigationConfigError":
    case "ExportError":
      return jsonError(message, 400);
    default:
      return jsonError(message, 500);
  }
}

export async function getServerContext(): Promise<RequestContext> {
  const root = await getRootSettings();
  const store = await cookies();
  const user = verifySessionToken(root, store.get(root.sessionCookieName)?.value ?? "");
  const settings = user ? forUser(root, user.dataId) : root;
  return { settings, root, user };
}

export function parseBoolQuery(value: string | null): boolean | null {
  if (value == null || value === "") return null;
  if (["1", "true", "yes", "on"].includes(value.toLowerCase())) return true;
  if (["0", "false", "no", "off"].includes(value.toLowerCase())) return false;
  return null;
}
