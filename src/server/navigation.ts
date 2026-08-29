import fs from "node:fs";
import path from "node:path";
import type { NavConfig } from "@/lib/navigation";
import { ensureWithin } from "@/server/paths";
import type { ServerSettings } from "@/server/settings";

export type { NavConfig } from "@/lib/navigation";
export { isNavVisible } from "@/lib/navigation";

const DEFAULT_NAV_CONFIG: NavConfig = {
  library: {},
  collections: {},
  tags: {},
};

export class NavigationConfigError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "NavigationConfigError";
  }
}

export class NavigationConfigService {
  constructor(readonly settings: ServerSettings) {}

  getConfig(): NavConfig {
    const filePath = this.configPath();
    if (!fs.existsSync(filePath)) return cloneDefaultConfig();
    let data: unknown;
    try {
      data = JSON.parse(fs.readFileSync(filePath, "utf8"));
    } catch {
      throw new NavigationConfigError("Navigation config is not valid JSON.");
    }
    if (!data || typeof data !== "object" || Array.isArray(data)) {
      throw new NavigationConfigError("Navigation config must be an object.");
    }
    return normalizeNavConfig(data as Record<string, unknown>);
  }

  updateConfig(values: Record<string, unknown>): NavConfig {
    const config = normalizeNavConfig(values);
    const filePath = this.configPath();
    fs.mkdirSync(path.dirname(filePath), { recursive: true });
    fs.writeFileSync(filePath, `${JSON.stringify(config, null, 2)}\n`, "utf8");
    return config;
  }

  private configPath(): string {
    if (!this.settings.metaDir) throw new NavigationConfigError("Metadata directory is not configured.");
    const filePath = path.join(this.settings.metaDir, "config", "navigation.json");
    ensureWithin(filePath, this.settings.metaDir);
    return filePath;
  }
}

export function normalizeNavConfig(values: Record<string, unknown>): NavConfig {
  const config = cloneDefaultConfig();
  for (const section of ["library", "collections", "tags"] as const) {
    const rawSection = values[section];
    if (rawSection == null) continue;
    if (!rawSection || typeof rawSection !== "object" || Array.isArray(rawSection)) {
      throw new NavigationConfigError(`${section} must be an object.`);
    }
    for (const [name, rawItem] of Object.entries(rawSection)) {
      if (!String(name).trim()) continue;
      if (!rawItem || typeof rawItem !== "object" || Array.isArray(rawItem)) {
        throw new NavigationConfigError(`${section}.${name} must be an object.`);
      }
      const visible = (rawItem as { visible?: unknown }).visible ?? true;
      if (typeof visible !== "boolean") {
        throw new NavigationConfigError(`${section}.${name}.visible must be a boolean.`);
      }
      config[section][String(name)] = { visible };
    }
  }
  return config;
}

function cloneDefaultConfig(): NavConfig {
  return {
    library: { ...DEFAULT_NAV_CONFIG.library },
    collections: { ...DEFAULT_NAV_CONFIG.collections },
    tags: { ...DEFAULT_NAV_CONFIG.tags },
  };
}

