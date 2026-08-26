"use client";

import { HomeLink } from "@/components/ui/logo";
import type { LibraryFilter } from "@/fixtures/notes";
import { ThemeToggle } from "@/components/ui/theme-toggle";

const libraryItems: { id: LibraryFilter; label: string }[] = [
  { id: "all", label: "全部笔记" },
  { id: "recent", label: "最近" },
  { id: "favorites", label: "收藏" },
  { id: "imported", label: "已导入" },
  { id: "archived", label: "已归档" },
];

type Entry = { name: string; count: number };

type Props = {
  collapsed: boolean;
  onToggle: () => void;
  library: LibraryFilter;
  onLibrary: (value: LibraryFilter) => void;
  collection: string;
  onCollection: (value: string) => void;
  tags: string[];
  onToggleTag: (tag: string) => void;
  collections: Entry[];
  allTags: Entry[];
  counts: Record<LibraryFilter, number>;
};

export function Sidebar(props: Props) {
  return (
    <aside
      className={`flex h-full shrink-0 flex-col border-r border-line bg-sidebar transition-[width] duration-200 ${
        props.collapsed ? "w-[64px]" : "w-[252px]"
      }`}
    >
      <div className="flex h-14 items-center justify-between border-b border-line px-3">
        {props.collapsed ? (
          <button
            type="button"
            onClick={props.onToggle}
            className="mx-auto rounded-lg p-1.5 hover:bg-panel-raised"
            aria-label="展开侧栏"
          >
            <HomeLink />
          </button>
        ) : (
          <>
            <HomeLink />
            <button
              type="button"
              onClick={props.onToggle}
              className="size-7 rounded-lg text-ink-faint hover:bg-panel-raised hover:text-ink"
              aria-label="收起侧栏"
            >
              ‹
            </button>
          </>
        )}
      </div>

      <nav className="scroll-thin flex-1 overflow-y-auto px-2 py-3">
        <Section collapsed={props.collapsed} label="资料库" />
        {libraryItems.map((item) => (
          <Row
            key={item.id}
            collapsed={props.collapsed}
            active={props.library === item.id && !props.collection}
            label={item.label}
            count={props.counts[item.id]}
            onClick={() => props.onLibrary(item.id)}
          />
        ))}

        <Section collapsed={props.collapsed} label="集合" />
        {props.collections.map((entry) => (
          <Row
            key={entry.name}
            collapsed={props.collapsed}
            active={props.collection === entry.name}
            label={entry.name}
            count={entry.count}
            onClick={() => props.onCollection(props.collection === entry.name ? "" : entry.name)}
          />
        ))}

        <Section collapsed={props.collapsed} label="标签" />
        {props.allTags.map((entry) => (
          <Row
            key={entry.name}
            collapsed={props.collapsed}
            active={props.tags.includes(entry.name)}
            label={`#${entry.name}`}
            count={entry.count}
            onClick={() => props.onToggleTag(entry.name)}
          />
        ))}
      </nav>

      <div className="flex items-center justify-between border-t border-line px-3 py-2.5">
        {props.collapsed ? null : (
          <span className="text-[11px] text-ink-faint">2.0 原型 · 无 AI</span>
        )}
        <ThemeToggle />
      </div>
    </aside>
  );
}

function Section({ collapsed, label }: { collapsed: boolean; label: string }) {
  if (collapsed) return <div className="my-3 h-px bg-line" />;
  return (
    <p className="mt-4 mb-1 px-2 text-[11px] font-medium tracking-[0.08em] text-ink-faint first:mt-1">
      {label}
    </p>
  );
}

function Row({
  collapsed,
  active,
  label,
  count,
  onClick,
}: {
  collapsed: boolean;
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
      className={`mb-0.5 flex h-8 w-full items-center gap-2 rounded-lg px-2 text-left text-[13px] transition-colors ${
        active ? "bg-panel-raised font-medium text-ink shadow-[var(--shadow-sm)]" : "text-ink-soft hover:bg-panel-raised/70 hover:text-ink"
      }`}
    >
      <span className={`truncate ${collapsed ? "mx-auto" : ""}`}>
        {collapsed ? label.replace(/^#/, "").slice(0, 2) : label}
      </span>
      {collapsed || count == null ? null : (
        <span className="ml-auto text-[11px] tabular-nums text-ink-faint">{count}</span>
      )}
    </button>
  );
}
