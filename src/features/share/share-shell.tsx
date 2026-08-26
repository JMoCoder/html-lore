import Link from "next/link";
import type { Note } from "@/fixtures/notes";

export function ShareShell({ note }: { note: Note }) {
  return (
    <div className="flex min-h-dvh flex-col bg-panel">
      <header className="flex h-9 shrink-0 items-center justify-between border-b border-line px-4 text-[11px] text-ink-faint">
        <Link href="/" className="font-display font-semibold tracking-tight text-ink-soft hover:text-ink">
          HTMlore
        </Link>
        <span className="inline-flex items-center gap-1.5">
          <span className="size-1.5 rounded-full bg-accent" />
          安全分享 · 只读
        </span>
      </header>
      <iframe
        title={note.title}
        sandbox="allow-same-origin"
        srcDoc={note.html}
        className="min-h-0 w-full flex-1 border-0 bg-panel"
      />
    </div>
  );
}
