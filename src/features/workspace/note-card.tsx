"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Icon } from "@/components/ui/icons";
import { ClientOnly } from "@/components/ui/client-only";
import { formatDate, noteReadingTime, shareUrl } from "@/features/workspace/note-meta";
import { itemContentHref, readHref } from "@/lib/api";
import type { Note } from "@/fixtures/notes";
import { useI18n } from "@/i18n/locale-provider";

export function NoteCard({
  note,
  onFavorite,
  onArchive,
  onDelete,
  onShare,
}: {
  note: Note;
  onFavorite: (note: Note) => void;
  onArchive: (note: Note) => void;
  onDelete: (note: Note) => void;
  onShare: (note: Note) => void;
}) {
  const router = useRouter();
  const { locale, messages: t } = useI18n();
  const stop = (e: { stopPropagation: () => void }) => e.stopPropagation();
  const actions = note.archived
    ? [
        {
          key: "favorite",
          label: note.favorite ? t.noteCard.unfavorite : t.noteCard.favorite,
          active: note.favorite,
          onClick: () => onFavorite(note),
          icon: <Icon.star filled={note.favorite} />,
        },
        {
          key: "archive",
          label: t.noteCard.unarchive,
          onClick: () => onArchive(note),
          icon: <Icon.restore />,
        },
        {
          key: "delete",
          label: t.noteCard.delete,
          danger: true,
          onClick: () => onDelete(note),
          icon: <Icon.trash />,
        },
      ]
    : [
        {
          key: "favorite",
          label: note.favorite ? t.noteCard.unfavorite : t.noteCard.favorite,
          active: note.favorite,
          onClick: () => onFavorite(note),
          icon: <Icon.star filled={note.favorite} />,
        },
        {
          key: "archive",
          label: t.noteCard.archive,
          onClick: () => onArchive(note),
          icon: <Icon.archive />,
        },
        {
          key: "edit",
          label: t.noteCard.edit,
          onClick: () => router.push(`${readHref(note.id)}?edit=1`),
          icon: <Icon.edit />,
        },
        {
          key: "share",
          label: t.noteCard.share,
          active: Boolean(note.shareToken),
          onClick: () => onShare(note),
          icon: <Icon.share />,
        },
        {
          key: "original",
          label: t.noteCard.openOriginal,
          onClick: () => window.open(itemContentHref(note.id), "_blank"),
          icon: <Icon.external />,
        },
      ];

  return (
    <article className="group relative flex min-w-0 flex-col rounded-[var(--radius-card)] border border-line bg-panel shadow-[var(--shadow-sm)] transition duration-150 hover:border-accent/35 hover:shadow-[var(--shadow-card)]">
      <div className="flex min-w-0 items-center justify-between gap-2 px-4 pt-2.5">
        <Link
          href={readHref(note.id)}
          className="min-w-0 truncate text-[11px] leading-5 font-medium tracking-[0.06em] text-ink-faint outline-none focus-visible:ring-2 focus-visible:ring-accent/40"
        >
          {note.collection}
        </Link>
        <div className="flex h-5 shrink-0 items-center gap-1 text-accent">
          {note.favorite ? (
            <span aria-label={t.noteCard.favorite} title={t.noteCard.favorite}>
              <Icon.star filled />
            </span>
          ) : null}
          {note.shareToken ? (
            <a
              href={shareUrl(note.shareToken)}
              target="_blank"
              rel="noreferrer"
              onClick={stop}
              aria-label={t.noteCard.shared}
              title={t.noteCard.shared}
              className="inline-flex"
            >
              <Icon.share />
            </a>
          ) : null}
        </div>
      </div>

      <Link
        href={readHref(note.id)}
        className="flex min-w-0 flex-col px-4 pt-2 pb-4 outline-none focus-visible:ring-2 focus-visible:ring-accent/40"
      >
        <h2 className="min-w-0 truncate text-[15px] font-semibold leading-snug tracking-tight text-ink">
          {note.title}
        </h2>
        <p className="mt-2 line-clamp-2 h-[42px] overflow-hidden text-[13px] leading-[21px] text-ink-soft">
          {note.summary}
        </p>
        <div className="mt-3 flex min-w-0 items-center justify-between gap-3">
          <p className="min-w-0 truncate text-[11px] text-ink-faint">
            {note.tags.slice(0, 3).map((tag) => (
              <span key={tag} className="mr-2 last:mr-0">#{tag}</span>
            ))}
          </p>
          <ClientOnly>
            <span className="shrink-0 text-[11px] tabular-nums text-ink-faint">
              {formatDate(note.updated, locale)} · {noteReadingTime(note, locale)}
            </span>
          </ClientOnly>
        </div>
      </Link>

      <div
        className="pointer-events-none absolute top-2 right-2 z-10 opacity-0 transition-opacity duration-150 group-hover:pointer-events-auto group-hover:opacity-100 group-focus-within:pointer-events-auto group-focus-within:opacity-100"
        onClick={stop}
      >
        <div
          className="grid h-7 overflow-hidden rounded-[var(--radius-card)] border border-line bg-panel-raised shadow-[var(--shadow-sm)]"
          style={{ gridTemplateColumns: `repeat(${actions.length}, 1.75rem)` }}
        >
          {actions.map((action) => (
            <CardAction
              key={action.key}
              label={action.label}
              active={action.active}
              danger={action.danger}
              onClick={(e) => {
                stop(e);
                action.onClick();
              }}
            >
              {action.icon}
            </CardAction>
          ))}
        </div>
      </div>
    </article>
  );
}

function CardAction({
  label,
  active = false,
  danger = false,
  onClick,
  children,
}: {
  label: string;
  active?: boolean;
  danger?: boolean;
  onClick: (e: { stopPropagation: () => void }) => void;
  children: ReactNode;
}) {
  const tone = danger
    ? "text-ink-faint hover:bg-danger/10 hover:text-danger"
    : active
      ? "bg-accent-soft text-accent-strong"
      : "text-ink-faint hover:bg-accent-soft hover:text-ink";

  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      onClick={onClick}
      className={`inline-flex h-full w-full items-center justify-center ${tone}`}
    >
      {children}
    </button>
  );
}
