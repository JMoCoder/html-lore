"use client";

import { toggleTheme } from "@/components/ui/theme";
import type { SortMode } from "@/fixtures/notes";

const sorts: { id: SortMode; label: string }[] = [
  { id: "newest", label: "最新" },
  { id: "oldest", label: "最早" },
  { id: "title-az", label: "标题 A–Z" },
  { id: "title-za", label: "标题 Z–A" },
];

type Props = {
  query: string;
  onQuery: (value: string) => void;
  sort: SortMode;
  onSort: (value: SortMode) => void;
  resultCount: number;
};

export function Topbar({ query, onQuery, sort, onSort, resultCount }: Props) {
  return (
    <header className="sticky top-0 z-10 flex h-14 items-center gap-3 border-b border-line bg-paper/80 px-5 backdrop-blur-md">
      <label className="relative min-w-0 flex-1">
        <span className="sr-only">搜索笔记</span>
        <input
          value={query}
          onChange={(event) => onQuery(event.target.value)}
          placeholder="搜索标题、摘要、标签"
          className="h-9 w-full max-w-md rounded-full border border-transparent bg-paper-dim px-4 text-sm text-ink outline-none transition-colors placeholder:text-ink-faint focus:border-line focus:bg-card"
        />
      </label>
      <p className="hidden text-xs text-ink-faint sm:block">{resultCount} 篇</p>
      <select
        value={sort}
        onChange={(event) => onSort(event.target.value as SortMode)}
        aria-label="排序"
        className="h-9 rounded-full border border-line bg-transparent px-3 text-xs text-ink-soft outline-none"
      >
        {sorts.map((item) => (
          <option key={item.id} value={item.id}>
            {item.label}
          </option>
        ))}
      </select>
      <button
        type="button"
        onClick={toggleTheme}
        className="h-9 rounded-full px-3 text-xs text-ink-soft transition-colors hover:bg-accent-soft hover:text-ink"
      >
        亮 / 暗
      </button>
    </header>
  );
}
