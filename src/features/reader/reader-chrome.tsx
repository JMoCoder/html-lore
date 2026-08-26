"use client";

import Link from "next/link";
import type { Note } from "@/fixtures/notes";
import { BrandMark } from "@/components/ui/brand-mark";
import { toggleTheme } from "@/components/ui/theme";

export function ReaderChrome({ note }: { note: Note }) {
  return (
    <div className="flex h-dvh flex-col bg-paper">
      <header className="flex h-12 shrink-0 items-center gap-4 border-b border-line px-4">
        <Link
          href="/"
          className="text-[13px] text-ink-soft transition-colors hover:text-ink"
        >
          ← 工作台
        </Link>
        <div className="min-w-0 flex-1">
          <p className="truncate font-serif text-[15px] tracking-tight">{note.title}</p>
        </div>
        <p className="hidden text-[11px] tracking-wide text-ink-faint sm:block">
          {note.collection}
          {note.tags.map((tag) => ` · #${tag}`).join("")}
        </p>
        {note.shareToken ? (
          <Link
            href={`/share/${note.shareToken}`}
            className="text-[12px] text-accent hover:underline"
          >
            分享预览
          </Link>
        ) : null}
        <ThemeButton />
      </header>
      <iframe
        title={note.title}
        sandbox="allow-same-origin"
        srcDoc={note.html}
        className="min-h-0 w-full flex-1 border-0 bg-card"
      />
    </div>
  );
}

function ThemeButton() {
  return (
    <button
      type="button"
      onClick={toggleTheme}
      className="text-[12px] text-ink-faint hover:text-ink"
    >
      亮 / 暗
    </button>
  );
}
