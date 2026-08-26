"use client";

import { useRouter } from "next/navigation";
import { Icon } from "@/components/ui/icons";
import { IconButton } from "@/components/ui/icon-button";
import type { SortMode } from "@/fixtures/notes";
import type { TagMatchMode } from "@/features/workspace/workspace-view";

const sorts: { id: SortMode; label: string }[] = [
  { id: "newest", label: "最近更新" },
  { id: "oldest", label: "最早更新" },
  { id: "title-az", label: "标题 A → Z" },
  { id: "title-za", label: "标题 Z → A" },
];

type Props = {
  query: string;
  onQuery: (value: string) => void;
  sort: SortMode;
  onSort: (value: SortMode) => void;
  favoritesOnly: boolean;
  onToggleFavorites: () => void;
  filterOpen: boolean;
  onToggleFilter: () => void;
  tags: string[];
  tagMatch: TagMatchMode;
  onTagMatch: (mode: TagMatchMode) => void;
  onRemoveTag: (tag: string) => void;
  onClearFilters: () => void;
  resultCount: number;
};

export function Topbar(props: Props) {
  const router = useRouter();

  return (
    <header className="relative z-20 border-b border-line bg-bg">
      <div className="flex h-14 items-center gap-2 px-4">
        <label className="relative w-full max-w-[360px]">
          <span className="pointer-events-none absolute top-1/2 left-3 -translate-y-1/2 text-ink-faint">
            <Icon.search />
          </span>
          <input
            value={props.query}
            onChange={(e) => props.onQuery(e.target.value)}
            placeholder="搜索笔记…"
            className="h-9 w-full rounded-[var(--radius-control)] border border-line bg-panel pl-9 pr-3 text-[13px] outline-none placeholder:text-ink-faint focus:border-accent/60"
          />
        </label>

        <div className="ml-auto flex items-center gap-1">
          <IconButton label="导入 HTML" onClick={() => alert("原型：导入将在领域层接线后启用") }>
            <Icon.plus />
          </IconButton>
          <IconButton
            label="筛选"
            tone={props.filterOpen || props.tags.length ? "active" : "default"}
            onClick={props.onToggleFilter}
          >
            <Icon.filter />
          </IconButton>
          <IconButton
            label="只看收藏"
            tone={props.favoritesOnly ? "active" : "default"}
            onClick={props.onToggleFavorites}
          >
            <Icon.star filled={props.favoritesOnly} />
          </IconButton>

          <div className="relative ml-1">
            <select
              value={props.sort}
              onChange={(e) => props.onSort(e.target.value as SortMode)}
              aria-label="排序"
              className="h-9 appearance-none rounded-[var(--radius-control)] border border-line bg-panel pl-3 pr-8 text-[13px] text-ink-soft outline-none focus:border-accent/60"
            >
              {sorts.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.label}
                </option>
              ))}
            </select>
            <span className="pointer-events-none absolute top-1/2 right-2.5 -translate-y-1/2 text-ink-faint">
              <Icon.chevronDown />
            </span>
          </div>

          <span className="ml-3 hidden text-xs text-ink-faint tabular-nums md:block">
            {props.resultCount} 篇
          </span>
        </div>
      </div>

      {props.filterOpen ? (
        <div className="absolute top-full right-4 mt-2 w-[320px] rounded-[var(--radius-card)] border border-line bg-panel-raised p-3 shadow-[var(--shadow-card)]">
          <div className="flex items-center justify-between">
            <p className="text-xs font-medium text-ink-soft">已选标签</p>
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
                  {mode === "any" ? "任一" : "全部"}
                </button>
              ))}
            </div>
          </div>
          <div className="mt-2 flex min-h-[30px] flex-wrap gap-1.5">
            {props.tags.length === 0 ? (
              <span className="text-xs text-ink-faint">在左侧标签区点选</span>
            ) : (
              props.tags.map((tag) => (
                <button
                  key={tag}
                  type="button"
                  onClick={() => props.onRemoveTag(tag)}
                  className="inline-flex h-6 items-center gap-1 rounded-md bg-accent-soft px-2 text-[11px] text-accent-strong"
                >
                  #{tag}
                  <Icon.x />
                </button>
              ))
            )}
          </div>
          <div className="mt-2 flex justify-end">
            <button
              type="button"
              onClick={props.onClearFilters}
              className="text-[11px] text-ink-faint hover:text-ink"
            >
              清空筛选
            </button>
          </div>
        </div>
      ) : null}
    </header>
  );
}
