import type { LibraryFilter, Note, SortMode } from "@/fixtures/notes";

export function filterNotes(
  notes: Note[],
  options: {
    library: LibraryFilter;
    collection: string;
    tags: string[];
    sort: SortMode;
    query: string;
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
    if (options.library === "recent") {
      const stamp = Date.parse(note.updated);
      if (Number.isNaN(stamp) || Date.now() - stamp > 1000 * 60 * 60 * 24 * 90) return false;
    }
    if (options.collection && note.collection !== options.collection) return false;
    if (options.tags.length && !options.tags.every((tag) => note.tags.includes(tag))) return false;
    if (!query) return true;
    return `${note.title} ${note.summary} ${note.collection} ${note.tags.join(" ")}`
      .toLowerCase()
      .includes(query);
  });

  return filtered.sort((a, b) => {
    if (options.sort === "title-az") return a.title.localeCompare(b.title, "zh");
    if (options.sort === "title-za") return b.title.localeCompare(a.title, "zh");
    if (options.sort === "oldest") return a.updated.localeCompare(b.updated);
    return b.updated.localeCompare(a.updated);
  });
}
