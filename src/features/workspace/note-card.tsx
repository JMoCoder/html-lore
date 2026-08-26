"use client";

import { useRouter } from "next/navigation";
import { Icon } from "@/components/ui/icons";
import { IconButton } from "@/components/ui/icon-button";
import { formatDate, noteReadingTime, shareUrl } from "@/features/workspace/note-meta";
import type { Note } from "@/fixtures/notes";

export function NoteCard({ note }: { note: Note }) {
  const router = useRouter();
  const open = () => router.push(`/read/${note.slug}`);
  const stop = (e: { stopPropagation: () => void }) => e.stopPropagation();

  return (
    <article
      onClick={open}
      onKeyDown={(e) => e.key === "Enter" && open()}
      tabIndex={0}
      role="link"
      className="group relative flex cursor-pointer flex-col rounded-[var(--radius-card)] border border-line bg-panel p-4 shadow-[var(--shadow-sm)] transition duration-150 hover:border-accent/35 hover:shadow-[var(--shadow-card)] focus-visible:outline-2 focus-visible:outline-accent"
    >
      <div className="flex items-start justify-between gap-2">
        <p className="min-w-0 truncate text-[11px] font-medium tracking-[0.06em] text-ink-faint">
          {note.collection}
        </p>
        {note.favorite ? <span className="shrink-0 text-accent"><Icon.star filled /></span> : null}
      </div>

      <h2 className="mt-2 line-clamp-2 text-[15px] font-semibold leading-snug tracking-tight text-ink">
        {note.title}
      </h2>
      <p className="mt-1.5 line-clamp-2 flex-1 text-[13px] leading-relaxed text-ink-soft">
        {note.summary}
      </p>

      <div className="mt-3 flex items-center justify-between gap-2">
        <p className="flex min-w-0 flex-wrap gap-x-2 text-[11px] text-ink-faint">
          {note.tags.slice(0, 3).map((tag) => (
            <span key={tag}>#{tag}</span>
          ))}
        </p>
        <span className="shrink-0 text-[11px] tabular-nums text-ink-faint">
          {formatDate(note.updated)} · {noteReadingTime(note)}
        </span>
      </div>

      <div
        className="pointer-events-none absolute inset-x-3 bottom-2.5 flex items-center justify-end gap-0.5 opacity-0 transition-opacity duration-150 group-hover:pointer-events-auto group-hover:opacity-100 group-focus-within:pointer-events-auto group-focus-within:opacity-100"
        onClick={stop}
      >
        <div className="flex items-center gap-0.5 rounded-full border border-line bg-panel-raised px-1 py-0.5 shadow-[var(--shadow-sm)]">
          <IconButton label={note.favorite ? "取消收藏" : "收藏"} tone={note.favorite ? "active" : "default"} onClick={(e) => { stop(e); alert("原型"); }}>
            <Icon.star filled={note.favorite} />
          </IconButton>
          <IconButton label={note.archived ? "取消归档" : "归档"} onClick={(e) => { stop(e); alert("原型"); }}>
            {note.archived ? <Icon.restore /> : <Icon.archive />}
          </IconButton>
          {note.archived ? (
            <IconButton label="永久删除" tone="danger" onClick={(e) => { stop(e); alert("原型"); }}>
              <Icon.trash />
            </IconButton>
          ) : (
            <>
              <IconButton label="编辑" onClick={(e) => { stop(e); router.push(`/read/${note.slug}?edit=1`); }}>
                <Icon.edit />
              </IconButton>
              <IconButton
                label="分享"
                tone={note.shareToken ? "active" : "default"}
                onClick={(e) => { stop(e); alert("原型：分享对话框"); }}
              >
                <Icon.share />
              </IconButton>
              <IconButton label="打开原文" onClick={(e) => { stop(e); router.push(`/read/${note.slug}?raw=1`); }}>
                <Icon.external />
              </IconButton>
            </>
          )}
        </div>
      </div>

      {note.shareToken ? (
        <a
          href={shareUrl(note.shareToken)}
          target="_blank"
          rel="noreferrer"
          onClick={stop}
          className="absolute top-3 right-3 hidden rounded-md px-1.5 py-0.5 text-[10px] font-medium tracking-wide text-accent-strong bg-accent-soft"
        >
          已分享
        </a>
      ) : null}
    </article>
  );
}
