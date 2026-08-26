import Link from "next/link";
import type { Note } from "@/fixtures/notes";

export function NoteCard({ note }: { note: Note }) {
  return (
    <Link
      href={`/read/${note.slug}`}
      className="group relative flex min-h-[220px] flex-col rounded-2xl border border-line bg-card p-5 shadow-none transition duration-200 hover:-translate-y-0.5 hover:border-accent/35 hover:shadow-[var(--shadow)]"
    >
      <p className="text-[11px] font-medium tracking-[0.16em] text-ink-faint uppercase">
        {note.collection}
        {note.favorite ? " · 收藏" : ""}
        {note.archived ? " · 归档" : ""}
      </p>
      <h2 className="mt-3 font-serif text-[1.35rem] leading-snug tracking-tight text-ink">
        {note.title}
      </h2>
      <p className="mt-2 line-clamp-3 flex-1 text-sm leading-relaxed text-ink-soft">
        {note.summary}
      </p>
      <div className="mt-4 flex items-end justify-between gap-3">
        <p className="flex flex-wrap gap-x-2 text-[11px] text-ink-faint">
          {note.tags.map((tag) => (
            <span key={tag}>#{tag}</span>
          ))}
        </p>
        <span className="text-[11px] text-ink-faint">{note.updated}</span>
      </div>
      <span className="pointer-events-none absolute top-4 right-4 text-[11px] tracking-wide text-accent opacity-0 transition-opacity duration-150 group-hover:opacity-100">
        阅读
      </span>
    </Link>
  );
}
