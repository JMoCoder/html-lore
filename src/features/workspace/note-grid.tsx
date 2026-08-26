import type { Note } from "@/fixtures/notes";
import { NoteCard } from "@/features/workspace/note-card";

export function NoteGrid({ notes }: { notes: Note[] }) {
  if (notes.length === 0) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-1 px-6 py-24 text-center">
        <p className="text-sm text-ink-soft">没有符合当前筛选的笔记。</p>
        <p className="text-xs text-ink-faint">试试清空标签或搜索词。</p>
      </div>
    );
  }

  return (
    <section className="scroll-thin grid flex-1 content-start grid-cols-[repeat(auto-fill,minmax(280px,1fr))] gap-3 overflow-y-auto p-4">
      {notes.map((note) => (
        <NoteCard key={note.id} note={note} />
      ))}
    </section>
  );
}
