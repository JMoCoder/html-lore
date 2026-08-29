import type { LibraryFilter, Note, SortMode } from "@/fixtures/notes";

export type TagMatchMode = "any" | "all";

export function filterNotes(
  notes: Note[],
  options: {
    library: LibraryFilter;
    collection: string;
    tags: string[];
    tagMatch: TagMatchMode;
    sort: SortMode;
    query: string;
    favoritesOnly: boolean;
  },
): Note[] {
  const query = options.query.trim().toLowerCase();

  const filtered = notes.filter((note) => {
    if (options.library === "archived") {
      if (!note.archived) return false;
    } else if (note.archived) {
      return false;
    }
    if (options.library === "favorites" && !note.favorite) return false;
    if (options.library === "imported" && !note.imported) return false;
    if (options.library === "recent" && Date.now() - Date.parse(note.updated) > 1000 * 60 * 60 * 24 * 30) return false;
    if (options.favoritesOnly && !note.favorite) return false;
    if (options.collection && note.collection !== options.collection) return false;
    if (options.tags.length) {
      const hit = options.tags.some((tag) => note.tags.includes(tag));
      const all = options.tags.every((tag) => note.tags.includes(tag));
      if (options.tagMatch === "all" && !all) return false;
      if (options.tagMatch === "any" && !hit) return false;
    }
    if (!query) return true;
    return `${note.title} ${note.summary} ${note.collection} ${note.tags.join(" ")} ${note.html}`.toLowerCase().includes(query);
  });

  return [...filtered].sort((a, b) => {
    if (a.pinned !== b.pinned) return a.pinned ? -1 : 1;
    const titleOrder = a.title.localeCompare(b.title, "zh");
    const titleDescOrder = b.title.localeCompare(a.title, "zh");
    const newestUpdated = b.updated.localeCompare(a.updated);
    const oldestUpdated = a.updated.localeCompare(b.updated);
    const newestCreated = b.created.localeCompare(a.created);
    const oldestCreated = a.created.localeCompare(b.created);
    if (options.sort === "created-oldest") return oldestCreated || titleOrder;
    if (options.sort === "oldest") return oldestUpdated || titleOrder;
    if (options.sort === "newest") return newestUpdated || titleOrder;
    if (options.sort === "title-az") return titleOrder || newestUpdated;
    if (options.sort === "title-za") return titleDescOrder || newestUpdated;
    return newestCreated || titleOrder;
  });
}
