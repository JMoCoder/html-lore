"use client";

import { useMemo } from "react";
import { HomeLink } from "@/components/ui/logo";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { Icon } from "@/components/ui/icons";
import { IconButton } from "@/components/ui/icon-button";
import type { LibraryFilter } from "@/fixtures/notes";
import { useI18n } from "@/i18n/locale-provider";
import { isNavVisible, type NavConfig } from "@/lib/navigation";

type Entry = { name: string; count: number };

type Props = {
  library: LibraryFilter;
  onLibrary: (value: LibraryFilter) => void;
  collection: string;
  onCollection: (value: string) => void;
  tags: string[];
  onToggleTag: (tag: string) => void;
  collections: Entry[];
  allTags: Entry[];
  counts: Record<LibraryFilter, number>;
  navConfig: NavConfig | null;
  onOpenSettings: () => void;
};

export function Sidebar(props: Props) {
  const { messages: t } = useI18n();

  const libraryItems = useMemo(
    () =>
      (
        [
          { id: "all" as const, label: t.sidebar.all },
          { id: "recent" as const, label: t.sidebar.recent },
          { id: "favorites" as const, label: t.sidebar.favorites },
          { id: "imported" as const, label: t.sidebar.imported },
          { id: "archived" as const, label: t.sidebar.archived },
        ] as const
      ).filter((item) => isNavVisible(props.navConfig, "library", item.id)),
    [props.navConfig, t.sidebar],
  );

  const visibleCollections = props.collections.filter((entry) =>
    isNavVisible(props.navConfig, "collections", entry.name),
  );
  const visibleTags = props.allTags.filter((entry) => isNavVisible(props.navConfig, "tags", entry.name));

  return (
    <aside className="flex h-full w-[252px] shrink-0 flex-col border-r border-line bg-sidebar">
      <div className="flex h-14 items-center justify-between border-b border-line px-3">
        <HomeLink />
        <ThemeToggle />
      </div>

      <nav className="scroll-thin flex-1 overflow-y-auto py-3">
        {libraryItems.length > 0 ? (
          <>
            <Section label={t.sidebar.library} />
            {libraryItems.map((item) => (
              <Row
                key={item.id}
                active={props.library === item.id && !props.collection}
                label={item.label}
                count={props.counts[item.id]}
                onClick={() => props.onLibrary(item.id)}
              />
            ))}
          </>
        ) : null}

        {visibleCollections.length > 0 ? (
          <>
            <Section label={t.sidebar.collections} />
            {visibleCollections.map((entry) => (
              <Row
                key={entry.name}
                active={props.collection === entry.name}
                label={entry.name}
                count={entry.count}
                onClick={() => props.onCollection(props.collection === entry.name ? "" : entry.name)}
              />
            ))}
          </>
        ) : null}

        {visibleTags.length > 0 ? (
          <>
            <Section label={t.sidebar.tags} />
            {visibleTags.map((entry) => (
              <Row
                key={entry.name}
                active={props.tags.includes(entry.name)}
                label={`#${entry.name}`}
                count={entry.count}
                onClick={() => props.onToggleTag(entry.name)}
              />
            ))}
          </>
        ) : null}
      </nav>

      <div className="flex items-center justify-between border-t border-line px-3 py-2.5">
        <a
          href="https://github.com/JMoCoder/html-lore"
          target="_blank"
          rel="noreferrer"
          aria-label={t.sidebar.github}
          title={t.sidebar.github}
          className="inline-flex size-8 items-center justify-center rounded-[var(--radius-control)] text-ink-faint transition-colors hover:bg-panel-raised hover:text-ink"
        >
          <Icon.github />
        </a>
        <IconButton label={t.sidebar.settings} onClick={props.onOpenSettings}>
          <Icon.settings />
        </IconButton>
      </div>
    </aside>
  );
}

function Section({ label }: { label: string }) {
  return (
    <p className="mt-4 mb-1 px-3 text-[11px] font-medium tracking-[0.08em] text-ink-faint first:mt-1">
      {label}
    </p>
  );
}

function Row({
  active,
  label,
  count,
  onClick,
}: {
  active: boolean;
  label: string;
  count?: number;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      title={label}
      onClick={onClick}
      className={`mb-0.5 flex h-8 w-full items-center gap-2 rounded-lg px-3 text-left text-[13px] transition-all ${
        active ? "bg-panel-raised font-medium text-ink shadow-[var(--shadow-sm)]" : "text-ink-soft hover:bg-panel-raised/70 hover:text-ink"
      }`}
    >
      <span className="truncate">{label}</span>
      {count == null ? null : <span className="ml-auto text-[11px] tabular-nums text-ink-faint">{count}</span>}
    </button>
  );
}
