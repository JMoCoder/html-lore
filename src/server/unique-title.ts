/** Return `desired` or `desired 2`, `desired 3`, … so titles stay unique (case-insensitive). */
export function uniqueTitle(desired: string, existing: Iterable<string>): string {
  const base = desired.trim() || "Untitled";
  const taken = new Set([...existing].map((title) => title.trim().toLowerCase()).filter(Boolean));
  if (!taken.has(base.toLowerCase())) return base;
  let index = 2;
  while (taken.has(`${base} ${index}`.toLowerCase())) {
    index += 1;
  }
  return `${base} ${index}`;
}
