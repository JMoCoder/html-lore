import type { Note } from "@/fixtures/notes";
import { NoteCard } from "@/features/workspace/note-card";

export function NoteGrid({ notes }: { notes: Note[] }) {
  if (notes.length === 0) {
    return (
      <div className="flex flex-1 items-center justify-center px-6 py-24 text-sm text-ink-faint">
        没有符合筛选的笔记。
      </div>
    );
  }

  return (
    <section className="grid flex-1 grid-cols-1 gap-4 p-5 md:grid-cols-2 xl:grid-cols-3">
      {notes.map((note) => (
        <NoteCard key={note.id} note={note} />
      ))}
    </section>
  );
}
