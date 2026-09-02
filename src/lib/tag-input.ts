const HASH_RE = /[＃#]/g;
const SPACE_RE = /[\s\u3000]+/g;

export function normalizeTagName(value: string): string {
  return value.replace(HASH_RE, "").replace(SPACE_RE, " ").trim();
}

/** Commit `#tag` tokens that are followed by whitespace (half- or full-width). */
export function consumeHashTags(input: string): { tags: string[]; draft: string } {
  const text = input.replace(/＃/g, "#").replace(/\u3000/g, " ");
  const tags: string[] = [];
  let lastIndex = 0;
  let kept = "";
  const re = /#([^\s#]+)\s+/g;
  let match: RegExpExecArray | null;
  while ((match = re.exec(text)) !== null) {
    kept += text.slice(lastIndex, match.index);
    const tag = normalizeTagName(match[1]);
    if (tag) tags.push(tag);
    lastIndex = match.index + match[0].length;
  }
  return { tags, draft: kept + text.slice(lastIndex) };
}

export function commitDraftTag(draft: string): string {
  return normalizeTagName(draft);
}

export function mergeTags(current: string[], incoming: string[]): string[] {
  const next = [...current];
  for (const tag of incoming) {
    if (!next.includes(tag)) next.push(tag);
  }
  return next;
}
