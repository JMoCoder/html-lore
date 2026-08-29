"use client";

import type { Note } from "@/fixtures/notes";
import { NoteCard } from "@/features/workspace/note-card";
import { useI18n } from "@/i18n/locale-provider";

export function NoteGrid({
  notes,
  onFavorite,
  onPin,
  onArchive,
  onDelete,
  onShare,
}: {
  notes: Note[];
  onFavorite: (note: Note) => void;
  onPin: (note: Note) => void;
  onArchive: (note: Note) => void;
  onDelete: (note: Note) => void;
  onShare: (note: Note) => void;
}) {
  const { messages: t } = useI18n();

  if (notes.length === 0) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-1 px-6 py-24 text-center">
        <p className="text-sm text-ink-soft">{t.noteGrid.emptyTitle}</p>
        <p className="text-xs text-ink-faint">{t.noteGrid.emptyHint}</p>
      </div>
    );
  }

  return (
    <section className="scroll-thin grid min-w-0 flex-1 content-start grid-cols-[repeat(auto-fill,minmax(min(100%,280px),1fr))] gap-3 overflow-y-auto p-4">
      {notes.map((note) => (
        <NoteCard
          key={note.id}
          note={note}
          onFavorite={onFavorite}
          onPin={onPin}
          onArchive={onArchive}
          onDelete={onDelete}
          onShare={onShare}
        />
      ))}
    </section>
  );
}
