"use client";

import { useEffect, useRef, useState } from "react";
import { Icon } from "@/components/ui/icons";
import { IconButton } from "@/components/ui/icon-button";
import { ClientOnly } from "@/components/ui/client-only";
import type { SortMode } from "@/fixtures/notes";
import type { TagMatchMode } from "@/features/workspace/workspace-view";
import { useI18n } from "@/i18n/locale-provider";

type Props = {
  onOpenNav: () => void;
  navOpen?: boolean;
  query: string;
  onQuery: (value: string) => void;
  sort: SortMode;
  onSort: (value: SortMode) => void;
  favoritesOnly: boolean;
  onToggleFavorites: () => void;
  filterOpen: boolean;
  onFilterOpen: (open: boolean) => void;
  tags: string[];
  availableTags: { name: string; count: number }[];
  tagMatch: TagMatchMode;
  onTagMatch: (mode: TagMatchMode) => void;
  onToggleTag: (tag: string) => void;
  onClearFilters: () => void;
  resultCount: number;
  onImport: () => void;
};

export function Topbar(props: Props) {
  const { messages: t } = useI18n();
  const [sortOpen, setSortOpen] = useState(false);
  const filterRef = useRef<HTMLDivElement>(null);
  const sortRef = useRef<HTMLDivElement>(null);

  const sorts: { id: SortMode; label: string }[] = [
    { id: "created-newest", label: t.topbar.sortCreatedNewest },
    { id: "created-oldest", label: t.topbar.sortCreatedOldest },
    { id: "newest", label: t.topbar.sortNewest },
    { id: "oldest", label: t.topbar.sortOldest },
    { id: "title-az", label: t.topbar.sortTitleAz },
    { id: "title-za", label: t.topbar.sortTitleZa },
  ];

  useEffect(() => {
    if (!props.filterOpen && !sortOpen) return;
    function onPointerDown(event: MouseEvent) {
      const target = event.target as Node;
      if (filterRef.current?.contains(target) || sortRef.current?.contains(target)) return;
      props.onFilterOpen(false);
      setSortOpen(false);
    }
    document.addEventListener("mousedown", onPointerDown);
    return () => document.removeEventListener("mousedown", onPointerDown);
  }, [props.filterOpen, props.onFilterOpen, sortOpen]);

  function openFilter() {
    const next = !props.filterOpen;
    setSortOpen(false);
    props.onFilterOpen(next);
  }

  function openSort() {
    const next = !sortOpen;
    props.onFilterOpen(false);
    setSortOpen(next);
  }

  return (
    <header className="relative z-50 h-14 border-b border-line bg-bg">
      <div className="flex h-full items-center gap-1.5 px-3 md:gap-2 md:px-4">
        <button
          type="button"
          className="mobile-only inline-flex size-10 items-center justify-center rounded-[var(--radius-control)] text-ink-faint"
          aria-label={t.topbar.openNav}
          aria-expanded={Boolean(props.navOpen)}
          onClick={props.onOpenNav}
        >
          <Icon.menu />
        </button>
        <label className="relative min-w-0 flex-1 md:max-w-[360px] md:flex-none">
          <span className="pointer-events-none absolute top-1/2 left-3 -translate-y-1/2 text-ink-faint">
            <Icon.search />
          </span>
          <input
            value={props.query}
            onChange={(e) => props.onQuery(e.target.value)}
            placeholder={t.topbar.searchPlaceholder}
            suppressHydrationWarning
            className="h-9 w-full rounded-[var(--radius-control)] border border-line bg-panel pr-3 pl-9 text-[13px] outline-none placeholder:text-ink-faint focus:border-accent/60 max-md:h-10"
          />
        </label>

        <div className="ml-auto flex h-full items-center gap-1">
          <IconButton label={t.topbar.importHtml} onClick={props.onImport}>
            <Icon.plus />
          </IconButton>
          <div ref={filterRef} className="relative flex h-full items-center">
            <IconButton
              label={t.topbar.filter}
              tone={props.filterOpen || props.tags.length ? "active" : "default"}
              onClick={openFilter}
            >
              <Icon.filter />
            </IconButton>
            {props.filterOpen ? (
              <div className="absolute top-full right-0 z-30 mt-1.5 w-[260px] rounded-[var(--radius-card)] border border-line bg-panel-raised p-3 shadow-[var(--shadow-card)] max-md:fixed max-md:top-[calc(env(safe-area-inset-top,0px)+3.5rem)] max-md:right-3 max-md:left-3 max-md:mt-0 max-md:w-auto">
                <div className="flex items-center justify-between gap-2">
                  <p className="text-xs font-medium text-ink-soft">{t.topbar.selectedTags}</p>
                  <div className="flex items-center rounded-lg bg-sidebar p-0.5">
                    {(["any", "all"] as const).map((mode) => (
                      <button
                        key={mode}
                        type="button"
                        onClick={() => props.onTagMatch(mode)}
                        className={`h-6 rounded-md px-2 text-[11px] ${
                          props.tagMatch === mode ? "bg-panel-raised text-ink shadow-[var(--shadow-sm)]" : "text-ink-faint"
                        }`}
                      >
                        {mode === "any" ? t.topbar.tagMatchAny : t.topbar.tagMatchAll}
                      </button>
                    ))}
                  </div>
                </div>
                <div className="mt-2 flex min-h-[30px] flex-wrap gap-1.5">
                  {props.availableTags.length === 0 ? (
                    <span className="text-xs text-ink-faint">{t.topbar.pickTagsHint}</span>
                  ) : (
                    props.availableTags.map((entry) => {
                      const selected = props.tags.includes(entry.name);
                      return (
                        <button
                          key={entry.name}
                          type="button"
                          onClick={() => props.onToggleTag(entry.name)}
                          className={`inline-flex h-6 items-center gap-1 rounded-md px-2 text-[11px] ${
                            selected
                              ? "bg-accent-soft text-accent-strong"
                              : "bg-sidebar text-ink-soft hover:text-ink"
                          }`}
                        >
                          #{entry.name}
                          <span className="tabular-nums text-[10px] text-ink-faint">{entry.count}</span>
                        </button>
                      );
                    })
                  )}
                </div>
                <div className="mt-2 flex justify-end">
                  <button
                    type="button"
                    onClick={props.onClearFilters}
                    className="text-[11px] text-ink-faint hover:text-ink"
                  >
                    {t.topbar.clearFilters}
                  </button>
                </div>
              </div>
            ) : null}
          </div>
          <IconButton
            label={t.topbar.favoritesOnly}
            tone={props.favoritesOnly ? "active" : "default"}
            onClick={props.onToggleFavorites}
          >
            <Icon.star filled={props.favoritesOnly} />
          </IconButton>

          <div ref={sortRef} className="relative flex h-full items-center">
            <IconButton
              label={t.topbar.sort}
              tone={sortOpen || props.sort !== "created-newest" ? "active" : "default"}
              onClick={openSort}
            >
              <Icon.sort />
            </IconButton>
            {sortOpen ? (
              <div className="absolute top-full right-0 z-30 mt-1.5 w-max min-w-[7.5rem] rounded-[var(--radius-card)] border border-line bg-panel-raised p-1.5 shadow-[var(--shadow-card)] max-md:fixed max-md:top-[calc(env(safe-area-inset-top,0px)+3.5rem)] max-md:right-3 max-md:left-auto max-md:mt-0">
                {sorts.map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => {
                      props.onSort(item.id);
                      setSortOpen(false);
                    }}
                    className={`mb-0.5 flex h-8 w-full items-center whitespace-nowrap rounded-lg px-2.5 text-left text-[13px] last:mb-0 max-md:h-11 ${
                      props.sort === item.id
                        ? "bg-panel font-medium text-ink shadow-[var(--shadow-sm)]"
                        : "text-ink-soft hover:bg-panel hover:text-ink"
                    }`}
                  >
                    {item.label}
                  </button>
                ))}
              </div>
            ) : null}
          </div>

          <ClientOnly fallback={<span className="ml-3 hidden text-xs text-ink-faint tabular-nums md:block">—</span>}>
            <span className="ml-3 hidden text-xs text-ink-faint tabular-nums md:block">
              {t.topbar.resultCount(props.resultCount)}
            </span>
          </ClientOnly>
        </div>
      </div>
    </header>
  );
}
