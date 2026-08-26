"use client";

import Link from "next/link";
import { BrandMark } from "@/components/ui/brand-mark";
import type { LibraryFilter } from "@/fixtures/notes";

const libraryItems: { id: LibraryFilter; label: string }[] = [
  { id: "all", label: "全部" },
  { id: "recent", label: "最近" },
  { id: "favorites", label: "收藏" },
  { id: "imported", label: "导入" },
  { id: "archived", label: "归档" },
];

type Props = {
  collapsed: boolean;
  onToggle: () => void;
  library: LibraryFilter;
  onLibrary: (value: LibraryFilter) => void;
  collection: string;
  onCollection: (value: string) => void;
  tags: string[];
  onToggleTag: (tag: string) => void;
  collections: string[];
  allTags: string[];
  counts: Record<"all" | "favorites" | "imported" | "archived", number>;
};

export function Sidebar(props: Props) {
  const width = props.collapsed ? "w-[72px]" : "w-[248px]";

  return (
    <aside
      className={`${width} sticky top-0 flex h-dvh shrink-0 flex-col border-r border-line bg-sidebar text-ink transition-[width] duration-200`}
    >
      <div className="flex h-14 items-center justify-between px-3">
        <Link href="/" aria-label="HTMlore 工作台" className="min-w-0 truncate">
          <BrandMark compact={props.collapsed} />
        </Link>
        <button
          type="button"
          onClick={props.onToggle}
          className="size-8 rounded-full text-ink-faint transition-colors hover:bg-accent-soft hover:text-ink"
          aria-label={props.collapsed ? "展开侧栏" : "收起侧栏"}
        >
          {props.collapsed ? "›" : "‹"}
        </button>
      </div>

      <nav className="flex-1 overflow-y-auto px-2 pb-8">
        <NavLabel collapsed={props.collapsed}>资料库</NavLabel>
        {libraryItems.map((item) => (
          <NavButton
            key={item.id}
            collapsed={props.collapsed}
            active={props.library === item.id}
            label={item.label}
            count={item.id === "recent" ? undefined : props.counts[item.id === "all" ? "all" : item.id]}
            onClick={() => {
              props.onLibrary(item.id);
              props.onCollection("");
            }}
          />
        ))}

        <NavLabel collapsed={props.collapsed}>集合</NavLabel>
        {props.collections.map((name) => (
          <NavButton
            key={name}
            collapsed={props.collapsed}
            active={props.collection === name}
            label={name}
            onClick={() => props.onCollection(props.collection === name ? "" : name)}
          />
        ))}

        <NavLabel collapsed={props.collapsed}>标签</NavLabel>
        {props.allTags.map((tag) => (
          <NavButton
            key={tag}
            collapsed={props.collapsed}
            active={props.tags.includes(tag)}
            label={`#${tag}`}
            onClick={() => props.onToggleTag(tag)}
          />
        ))}
      </nav>

      <p className={`px-3 pb-4 text-[11px] tracking-wide text-ink-faint ${props.collapsed ? "hidden" : ""}`}>
        2.0 原型 · 无 AI
        <Link href="/login" className="mt-1 block text-ink-soft hover:text-ink">
          登录页
        </Link>
      </p>
    </aside>
  );
}

function NavLabel({ collapsed, children }: { collapsed: boolean; children: string }) {
  if (collapsed) return <div className="mt-4 mb-1 h-px bg-line" />;
  return (
    <p className="mt-5 mb-1 px-2 text-[11px] font-medium tracking-[0.14em] text-ink-faint uppercase">
      {children}
    </p>
  );
}

function NavButton({
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
      className={`mb-0.5 flex h-8 w-full items-center rounded-lg px-2 text-left text-[13px] transition-colors duration-150 ${
        active ? "bg-accent-soft text-ink" : "text-ink-soft hover:bg-accent-soft/60 hover:text-ink"
      }`}
    >
      <span className={`truncate ${collapsed ? "mx-auto text-center" : ""}`}>
        {collapsed ? label.slice(0, 1) : label}
      </span>
      {collapsed || count == null ? null : (
        <span className="ml-auto text-[11px] text-ink-faint">{count}</span>
      )}
    </button>
  );
}
