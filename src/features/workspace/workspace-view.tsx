"use client";

import { useMemo, useState } from "react";
import type { LibraryFilter, Note, SortMode } from "@/fixtures/notes";
import { filterNotes } from "@/features/workspace/filter-notes";
import { Sidebar } from "@/features/workspace/sidebar";
import { Topbar } from "@/features/workspace/topbar";
import { NoteGrid } from "@/features/workspace/note-grid";

export function WorkspaceView({ notes }: { notes: Note[] }) {
  const [library, setLibrary] = useState<LibraryFilter>("all");
  const [collection, setCollection] = useState("");
  const [tags, setTags] = useState<string[]>([]);
  const [sort, setSort] = useState<SortMode>("newest");
  const [query, setQuery] = useState("");
  const [collapsed, setCollapsed] = useState(false);

  const visible = useMemo(
    () => filterNotes(notes, { library, collection, tags, sort, query }),
    [notes, library, collection, tags, sort, query],
  );

  const collections = [...new Set(notes.filter((note) => !note.archived).map((note) => note.collection))];
  const allTags = [...new Set(notes.flatMap((note) => note.tags))].sort();

  return (
    <div className="flex min-h-full bg-paper">
      <Sidebar
        collapsed={collapsed}
        onToggle={() => setCollapsed((value) => !value)}
        library={library}
        onLibrary={setLibrary}
        collection={collection}
        onCollection={setCollection}
        tags={tags}
        onToggleTag={(tag) =>
          setTags((current) =>
            current.includes(tag) ? current.filter((item) => item !== tag) : [...current, tag],
          )
        }
        collections={collections}
        allTags={allTags}
        counts={{
          all: notes.filter((note) => !note.archived).length,
          favorites: notes.filter((note) => note.favorite && !note.archived).length,
          imported: notes.filter((note) => note.imported && !note.archived).length,
          archived: notes.filter((note) => note.archived).length,
        }}
      />
      <main className="flex min-w-0 flex-1 flex-col">
        <Topbar
          query={query}
          onQuery={setQuery}
          sort={sort}
          onSort={setSort}
          resultCount={visible.length}
        />
        <NoteGrid notes={visible} />
      </main>
    </div>
  );
}
