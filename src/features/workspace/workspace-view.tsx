"use client";

import { useCallback, useMemo, useRef, useState } from "react";
import type { LibraryFilter, Note, SortMode } from "@/fixtures/notes";
import { filterNotes } from "@/features/workspace/filter-notes";
import { Sidebar } from "@/features/workspace/sidebar";
import { Topbar } from "@/features/workspace/topbar";
import { NoteGrid } from "@/features/workspace/note-grid";
import { ShareDialog } from "@/features/share/share-dialog";
import { SettingsPage } from "@/features/settings/settings-page";
import { useI18n } from "@/i18n/locale-provider";
import { apiJson, itemApiHref, itemToNote } from "@/lib/api";
import type { NavConfig } from "@/lib/navigation";
import type { Item } from "@/server/types";

export type TagMatchMode = "any" | "all";

type ShareRow = { item_id: string; url_path: string; active: boolean };

const RECENT_MS = 1000 * 60 * 60 * 24 * 30;

type Props = {
  initialItems?: Item[];
  initialShares?: ShareRow[];
  initialNav?: NavConfig | null;
  initialInteractive?: boolean;
};

export function WorkspaceView({
  initialItems = [],
  initialShares = [],
  initialNav = null,
  initialInteractive = true,
}: Props) {
  const { messages: t } = useI18n();
  const [items, setItems] = useState<Item[]>(initialItems);
  const [shares, setShares] = useState<ShareRow[]>(initialShares);
  const [navConfig, setNavConfig] = useState<NavConfig | null>(initialNav);
  const [interactiveEnabled, setInteractiveEnabled] = useState(initialInteractive);
  const [now] = useState(() => Date.now());
  const [shareTarget, setShareTarget] = useState<Note | null>(null);
  const [error, setError] = useState("");
  const [library, setLibrary] = useState<LibraryFilter>("all");
  const [collection, setCollection] = useState("");
  const [tags, setTags] = useState<string[]>([]);
  const [tagMatch, setTagMatch] = useState<TagMatchMode>("all");
  const [sort, setSort] = useState<SortMode>("created-newest");
  const [query, setQuery] = useState("");
  const [favoritesOnly, setFavoritesOnly] = useState(false);
  const [filterOpen, setFilterOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [shareEpoch, setShareEpoch] = useState(0);
  const fileRef = useRef<HTMLInputElement>(null);

  const load = useCallback(async () => {
    const [manifest, shareList, navigation] = await Promise.all([
      apiJson<{ items: Item[] }>("/api/manifest"),
      apiJson<{ shares: ShareRow[]; interactive_enabled?: boolean }>("/api/shares").catch(() => ({ shares: [], interactive_enabled: true })),
      apiJson<NavConfig>("/api/navigation").catch(() => null),
    ]);
    setItems(manifest.items);
    setShares(shareList.shares.filter((row) => row.active));
    setInteractiveEnabled(shareList.interactive_enabled ?? true);
    setNavConfig(navigation);
  }, []);

  const tokenByItem = useMemo(() => {
    const map = new Map<string, string>();
    for (const share of shares) {
      const token = share.url_path.split("/").filter(Boolean)[1];
      if (token) map.set(share.item_id, token);
    }
    return map;
  }, [shares]);

  const notes = useMemo(
    () => items.map((item) => itemToNote(item, { shareToken: tokenByItem.get(item.id) })),
    [items, tokenByItem],
  );

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
  const recentCount = active.filter((n) => now - Date.parse(n.updated) < RECENT_MS).length;

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

  async function patchState(note: Note, values: { favorite?: boolean; archived?: boolean; pinned?: boolean }) {
    await apiJson(itemApiHref(note.id, "state"), {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(values),
    });
    await load();
  }

  async function remove(note: Note) {
    if (!confirm(t.workspace.deleteConfirm(note.title))) return;
    await apiJson(itemApiHref(note.id), { method: "DELETE" });
    await load();
  }

  return (
    <div className="flex h-dvh bg-bg">
      <input
        ref={fileRef}
        type="file"
        accept=".html,.htm"
        multiple
        className="hidden"
        onChange={(event) => {
          const picked = [...(event.target.files ?? [])];
          event.target.value = "";
          if (!picked.length) return;
          if (picked.length > 5) setError(t.workspace.importMax(5));
          const files = picked.slice(0, 5);
          const form = new FormData();
          for (const file of files) form.append("file", file);
          apiJson("/api/uploads/html", { method: "POST", body: form })
            .then(() => load())
            .catch((err: Error) => setError(err.message));
        }}
      />
      <Sidebar
        library={library}
        onLibrary={(value) => {
          setLibrary(value);
          setCollection("");
        }}
        collection={collection}
        onCollection={setCollection}
        tags={tags}
        onToggleTag={(tag) =>
          setTags((current) => (current.includes(tag) ? current.filter((t) => t !== tag) : [...current, tag]))
        }
        collections={collections}
        allTags={allTags}
        navConfig={navConfig}
        counts={{
          all: active.length,
          recent: recentCount,
          favorites: active.filter((n) => n.favorite).length,
          imported: active.filter((n) => n.imported).length,
          archived: notes.filter((n) => n.archived).length,
        }}
        onOpenSettings={() => setSettingsOpen(true)}
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
          onFilterOpen={setFilterOpen}
          tags={tags}
          availableTags={allTags}
          tagMatch={tagMatch}
          onTagMatch={setTagMatch}
          onToggleTag={(tag) =>
            setTags((current) => (current.includes(tag) ? current.filter((t) => t !== tag) : [...current, tag]))
          }
          onClearFilters={() => {
            setTags([]);
            setQuery("");
            setFavoritesOnly(false);
          }}
          resultCount={visible.length}
          onImport={() => fileRef.current?.click()}
        />
        {error ? <p className="px-4 py-2 text-xs text-danger">{error}</p> : null}
        <NoteGrid
          notes={visible}
          onFavorite={(note) => patchState(note, { favorite: !note.favorite }).catch((err: Error) => setError(err.message))}
          onPin={(note) => patchState(note, { pinned: !note.pinned }).catch((err: Error) => setError(err.message))}
          onArchive={(note) => patchState(note, { archived: !note.archived }).catch((err: Error) => setError(err.message))}
          onDelete={(note) => remove(note).catch((err: Error) => setError(err.message))}
          onShare={(note) => setShareTarget(note)}
        />
      </main>
      {shareTarget ? (
        <ShareDialog
          key={shareTarget.id}
          open
          itemId={shareTarget.id}
          title={shareTarget.title}
          interactiveEnabled={interactiveEnabled}
          onClose={() => setShareTarget(null)}
          onChanged={() => {
            setShareEpoch((n) => n + 1);
            load().catch((err: Error) => setError(err.message));
          }}
        />
      ) : null}
      {settingsOpen ? (
        <SettingsPage
          onClose={() => setSettingsOpen(false)}
          navConfig={navConfig}
          onNavConfig={setNavConfig}
          items={items}
          collections={collections}
          allTags={allTags}
          libraryCounts={{
            all: active.length,
            recent: recentCount,
            favorites: active.filter((n) => n.favorite).length,
            imported: active.filter((n) => n.imported).length,
            archived: notes.filter((n) => n.archived).length,
          }}
          onItemsChanged={() => {
            load().catch((err: Error) => setError(err.message));
          }}
          onRenamed={(kind, from, to) => {
            if (kind === "collection" && collection === from) setCollection(to);
            if (kind === "tag") setTags((current) => current.map((tag) => (tag === from ? to : tag)));
          }}
          onSharesChanged={() => {
            setShareEpoch((n) => n + 1);
            load().catch((err: Error) => setError(err.message));
          }}
          shareEpoch={shareEpoch}
          onManageShare={(itemId) => {
            const note = notes.find((row) => row.id === itemId);
            if (note) {
              setShareTarget(note);
              return;
            }
            const item = items.find((row) => row.id === itemId);
            if (item) setShareTarget(itemToNote(item));
          }}
        />
      ) : null}
    </div>
  );
}
