import Link from "next/link";
import type { Note } from "@/fixtures/notes";

export function ShareShell({ note }: { note: Note }) {
  return (
    <div className="flex min-h-dvh flex-col bg-paper">
      <header className="flex h-10 items-center justify-between px-4 text-[11px] tracking-wide text-ink-faint">
        <Link href="/" className="font-serif text-sm tracking-tight text-ink-soft">
          HTM<span className="text-accent">lore</span>
        </Link>
        <span>安全分享 · 只读</span>
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
