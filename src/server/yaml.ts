export function parseSimpleYaml(text: string): Record<string, unknown> {
  const result: Record<string, unknown> = {};
  let currentKey: string | null = null;

  for (const rawLine of text.split(/\r?\n/)) {
    if (!rawLine.trim() || rawLine.trimStart().startsWith("#")) continue;

    const indent = rawLine.length - rawLine.trimStart().length;
    const line = rawLine.trim();

    if (indent === 0) {
      currentKey = null;
      if (!line.includes(":")) continue;
      const index = line.indexOf(":");
      const key = line.slice(0, index).trim();
      const value = line.slice(index + 1).trim();
      currentKey = key;
      if (value === "") {
        result[key] = [];
      } else {
        result[key] = parseScalar(value);
      }
    } else if (currentKey && line.startsWith("- ")) {
      if (!Array.isArray(result[currentKey])) result[currentKey] = [];
      (result[currentKey] as unknown[]).push(parseScalar(line.slice(2).trim()));
    } else if (currentKey && line.includes(":")) {
      if (!isPlainObject(result[currentKey])) result[currentKey] = {};
      const index = line.indexOf(":");
      const key = line.slice(0, index).trim();
      const value = line.slice(index + 1).trim();
      (result[currentKey] as Record<string, unknown>)[key] = parseScalar(value);
    }
  }

  return result;
}

export function dumpSimpleYaml(data: Record<string, unknown>): string {
  const lines: string[] = [];
  for (const [key, value] of Object.entries(data)) {
    if (Array.isArray(value)) {
      lines.push(`${key}:`);
      for (const item of value) {
        lines.push(`  - ${escapeYamlScalar(item)}`);
      }
    } else if (isPlainObject(value)) {
      lines.push(`${key}:`);
      for (const [childKey, childValue] of Object.entries(value)) {
        lines.push(`  ${childKey}: ${escapeYamlScalar(childValue)}`);
      }
    } else {
      lines.push(`${key}: ${escapeYamlScalar(value)}`);
    }
  }
  return `${lines.join("\n")}\n`;
}

function parseScalar(value: string): unknown {
  if (value === "") return null;
  if (value === "[]") return [];
  if (value === "{}") return {};
  const lowered = value.toLowerCase();
  if (lowered === "true") return true;
  if (lowered === "false") return false;
  if (lowered === "null" || lowered === "none" || lowered === "~") return null;
  if (
    (value.startsWith('"') && value.endsWith('"')) ||
    (value.startsWith("'") && value.endsWith("'"))
  ) {
    return value.slice(1, -1);
  }
  return value;
}

function escapeYamlScalar(value: unknown): string {
  if (typeof value === "boolean") return value ? "true" : "false";
  if (value == null) return "null";
  const text = String(value);
  if (
    text === "" ||
    text.startsWith("-") ||
    text.startsWith("@") ||
    text.startsWith("`") ||
    /[:#\n"]/.test(text)
  ) {
    return `"${text.replace(/\\/g, "\\\\").replace(/"/g, '\\"')}"`;
  }
  return text;
}

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}
