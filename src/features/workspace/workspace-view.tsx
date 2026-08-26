"use client";

import { useMemo, useState } from "react";
import type { LibraryFilter, Note, SortMode } from "@/fixtures/notes";
import { filterNotes } from "@/features/workspace/filter-notes";
import { Sidebar } from "@/features/workspace/sidebar";
import { Topbar } from "@/features/workspace/topbar";
import { NoteGrid } from "@/features/workspace/note-grid";

export type TagMatchMode = "any" | "all";

export function WorkspaceView({ notes }: { notes: Note[] }) {
  const [library, setLibrary] = useState<LibraryFilter>("all");
  const [collection, setCollection] = useState("");
  const [tags, setTags] = useState<string[]>([]);
  const [tagMatch, setTagMatch] = useState<TagMatchMode>("all");
  const [sort, setSort] = useState<SortMode>("newest");
  const [query, setQuery] = useState("");
  const [favoritesOnly, setFavoritesOnly] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  const [filterOpen, setFilterOpen] = useState(false);

  const visible = useMemo(
    () =>
      filterNotes(notes, {
        library,
        collection,
        tags,
        tagMatch,
        sort,
        query,
        favoritesOnly,
      }),
    [notes, library, collection, tags, tagMatch, sort, query, favoritesOnly],
  );

  const active = notes.filter((n) => !n.archived);
  const collections = useMemo(
    () =>
      [...new Set(active.map((n) => n.collection))].map((name) => ({
        name,
        count: active.filter((n) => n.collection === name).length,
      })),
    [active],
  );
  const allTags = useMemo(
    () =>
      [...new Set(active.flatMap((n) => n.tags))].map((name) => ({
        name,
        count: active.filter((n) => n.tags.includes(name)).length,
      })),
    [active],
  );

  return (
    <div className="flex h-dvh bg-bg">
      <Sidebar
        collapsed={collapsed}
        onToggle={() => setCollapsed((v) => !v)}
        library={library}
        onLibrary={(value) => {
          setLibrary(value);
          if (value !== "all") setCollection("");
        }}
        collection={collection}
        onCollection={setCollection}
        tags={tags}
        onToggleTag={(tag) =>
          setTags((current) => (current.includes(tag) ? current.filter((t) => t !== tag) : [...current, tag]))
        }
        collections={collections}
        allTags={allTags}
        counts={{
          all: active.length,
          recent: active.filter((n) => Date.now() - Date.parse(n.updated) < 1000 * 60 * 60 * 24 * 30).length,
          favorites: active.filter((n) => n.favorite).length,
          imported: active.filter((n) => n.imported).length,
          archived: notes.filter((n) => n.archived).length,
        }}
      />
      <main className="flex min-w-0 flex-1 flex-col">
        <Topbar
          query={query}
          onQuery={setQuery}
          sort={sort}
          onSort={setSort}
          favoritesOnly={favoritesOnly}
          onToggleFavorites={() => setFavoritesOnly((v) => !v)}
          filterOpen={filterOpen}
          onToggleFilter={() => setFilterOpen((v) => !v)}
          tags={tags}
          tagMatch={tagMatch}
          onTagMatch={setTagMatch}
          onRemoveTag={(tag) => setTags((current) => current.filter((t) => t !== tag))}
          onClearFilters={() => {
            setTags([]);
            setQuery("");
            setFavoritesOnly(false);
          }}
          resultCount={visible.length}
        />
        <NoteGrid notes={visible} />
      </main>
    </div>
  );
}
