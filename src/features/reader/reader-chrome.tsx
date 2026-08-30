"use client";

import dynamic from "next/dynamic";
import { useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Icon } from "@/components/ui/icons";
import { IconButton } from "@/components/ui/icon-button";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { formatDate } from "@/features/workspace/note-meta";
import { ShareDialog } from "@/features/share/share-dialog";
import type { Note } from "@/fixtures/notes";
import { useI18n } from "@/i18n/locale-provider";
import { apiJson, itemApiHref, itemContentDownloadHref, itemContentHref, listShares, triggerDownload } from "@/lib/api";
import type { Manifest } from "@/server/types";

const SourceEditorDialog = dynamic(
  () => import("@/features/reader/source-editor-dialog").then((m) => m.SourceEditorDialog),
  { ssr: false },
);
const FileEditorDialog = dynamic(
  () => import("@/features/reader/file-editor-dialog").then((m) => m.FileEditorDialog),
  { ssr: false },
);

const PANEL_WIDTH = 320;

export function ReaderChrome({
  note,
  html,
  interactiveEnabled = true,
}: {
  note: Note;
  html: string;
  interactiveEnabled?: boolean;
}) {
  const router = useRouter();
  const params = useSearchParams();
  const { locale, messages: t } = useI18n();
  const [panelOpen, setPanelOpen] = useState(params.get("edit") === "1");
  const [sourceOpen, setSourceOpen] = useState(false);
  const [fileOpen, setFileOpen] = useState(false);
  const [title, setTitle] = useState(note.title);
  const [summary, setSummary] = useState(note.summary);
  const [collection, setCollection] = useState(note.collection || "Inbox");
  const collectionRef = useRef(collection);
  const [collectionOptions, setCollectionOptions] = useState<string[]>([note.collection || "Inbox"]);
  const [tags, setTags] = useState(note.tags.join(", "));
  const [source, setSource] = useState(html);
  const [contentRevision, setContentRevision] = useState(0);
  const [message, setMessage] = useState("");
  const [favorite, setFavorite] = useState(note.favorite);
  const [archived, setArchived] = useState(note.archived);
  const [shareToken, setShareToken] = useState(note.shareToken);
  const [shareOpen, setShareOpen] = useState(false);
  const [moreOpen, setMoreOpen] = useState(false);
  const moreRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    collectionRef.current = collection;
  }, [collection]);

  useEffect(() => {
    if (!moreOpen) return;
    function onPointerDown(event: MouseEvent) {
      if (moreRef.current?.contains(event.target as Node)) return;
      setMoreOpen(false);
    }
    document.addEventListener("mousedown", onPointerDown);
    return () => document.removeEventListener("mousedown", onPointerDown);
  }, [moreOpen]);

  useEffect(() => {
    apiJson<Manifest>("/api/manifest")
      .then((manifest) => {
        setCollectionOptions(manifest.collections.map((row) => row.name).filter(Boolean));
      })
      .catch(() => {});
  }, []);

  function updateCollection(value: string) {
    collectionRef.current = value;
    setCollection(value);
    const cleaned = value.trim();
    if (cleaned) {
      setCollectionOptions((current) => (current.includes(cleaned) ? current : [...current, cleaned]));
    }
  }

  async function saveMetadata() {
    const nextCollection = collectionRef.current.trim() || "Inbox";
    updateCollection(nextCollection);
    await apiJson(itemApiHref(note.id, "metadata"), {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title,
        summary,
        collection: nextCollection,
        tags: tags.split(",").map((tag) => tag.trim()).filter(Boolean),
      }),
    });
    setMessage(t.reader.metadataSaved);
    router.refresh();
  }

  function handleContentSaved(next: string) {
    setSource(next);
    setContentRevision(Date.now());
    setMessage(t.reader.contentSaved);
    router.refresh();
  }

  async function patchState(values: { favorite?: boolean; archived?: boolean }) {
    await apiJson(itemApiHref(note.id, "state"), {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(values),
    });
    if (values.favorite != null) setFavorite(values.favorite);
    if (values.archived != null) setArchived(values.archived);
    router.refresh();
  }

  const toolbarItems = [
    {
      key: "favorite",
      label: t.reader.favorite,
      active: favorite,
      onClick: () => patchState({ favorite: !favorite }),
      icon: <Icon.star filled={favorite} />,
    },
    {
      key: "archive",
      label: t.reader.archive,
      onClick: () => patchState({ archived: !archived }),
      icon: <Icon.archive />,
    },
    {
      key: "share",
      label: t.reader.share,
      active: Boolean(shareToken),
      onClick: () => setShareOpen(true),
      icon: <Icon.share />,
    },
    {
      key: "download",
      label: t.reader.download,
      onClick: () => triggerDownload(itemContentDownloadHref(note.id)),
      icon: <Icon.download />,
    },
    {
      key: "original",
      label: t.reader.openOriginal,
      onClick: () => window.open(itemContentHref(note.id), "_blank"),
      icon: <Icon.external />,
    },
  ];

  return (
    <div className="app-shell flex flex-col bg-bg">
      <header className="relative z-50 flex h-14 shrink-0 items-center gap-1 border-b border-line bg-bg px-2 md:gap-2 md:px-4">
        <Link
          href="/"
          className="group inline-flex items-center gap-1 rounded-lg px-2 py-1 text-[13px] text-ink-soft transition-colors hover:bg-panel hover:text-ink max-md:size-10 max-md:justify-center max-md:px-0"
        >
          <span className="inline-flex transition-transform duration-150 group-hover:-translate-x-0.5">
            <Icon.chevronLeft />
          </span>
          <span className="desktop-only">{t.reader.back}</span>
        </Link>
        <div className="mx-auto flex min-w-0 max-w-xl flex-1 items-center justify-center gap-2">
          <h1 className="truncate text-[14px] font-semibold tracking-tight text-ink">{title}</h1>
          <span className="hidden shrink-0 text-[11px] text-ink-faint md:inline">
            {collection} · {formatDate(note.updated, locale)}
          </span>
        </div>
        <div className="flex items-center gap-0.5">
          <div className="hidden items-center gap-0.5 md:flex">
            {toolbarItems.map((item) => (
              <IconButton key={item.key} label={item.label} tone={item.active ? "active" : "default"} onClick={item.onClick}>
                {item.icon}
              </IconButton>
            ))}
            <div className="mx-1 h-5 w-px bg-line" />
          </div>
          <div ref={moreRef} className="relative md:hidden">
            <IconButton
              label={t.reader.more}
              tone={moreOpen ? "active" : "default"}
              onClick={() => setMoreOpen((value) => !value)}
            >
              <Icon.more />
            </IconButton>
            {moreOpen ? (
              <div className="absolute top-full right-0 z-30 mt-1.5 w-max min-w-[10rem] rounded-[var(--radius-card)] border border-line bg-panel-raised p-1.5 shadow-[var(--shadow-card)]">
                {toolbarItems.map((item) => (
                  <button
                    key={item.key}
                    type="button"
                    onClick={() => {
                      setMoreOpen(false);
                      item.onClick();
                    }}
                    className={`mb-0.5 flex h-11 w-full items-center gap-2 rounded-lg px-2.5 text-left text-[13px] last:mb-0 ${
                      item.active ? "bg-panel font-medium text-ink" : "text-ink-soft hover:bg-panel hover:text-ink"
                    }`}
                  >
                    {item.icon}
                    {item.label}
                  </button>
                ))}
              </div>
            ) : null}
          </div>
          <IconButton
            label={panelOpen ? t.reader.panelOpen : t.reader.panelClosed}
            tone={panelOpen ? "active" : "default"}
            onClick={() => {
              setMoreOpen(false);
              setPanelOpen((v) => !v);
            }}
          >
            <Icon.edit />
          </IconButton>
        </div>
      </header>

      <div className="relative flex min-h-0 flex-1 overflow-hidden">
        <iframe
          title={title}
          sandbox="allow-scripts"
          src={`${itemContentHref(note.id)}?v=${contentRevision}`}
          className="min-w-0 flex-1 border-0 bg-panel"
        />

        {panelOpen ? (
          <button
            type="button"
            aria-label={t.reader.panelOpen}
            className="fixed inset-x-0 bottom-0 top-14 z-30 bg-ink/30 md:hidden"
            onClick={() => setPanelOpen(false)}
          />
        ) : null}

        <aside
          aria-hidden={!panelOpen}
          style={{ width: PANEL_WIDTH, marginRight: panelOpen ? 0 : -PANEL_WIDTH }}
          className={`reader-panel shrink-0 border-l border-line bg-sidebar transition-[margin] duration-200 ease-out ${
            panelOpen
              ? "is-open max-md:fixed max-md:inset-y-0 max-md:right-0 max-md:z-40 max-md:mr-0! max-md:w-full! max-md:border-l-0 max-md:pt-[env(safe-area-inset-top,0px)] max-md:pb-[env(safe-area-inset-bottom,0px)]"
              : "max-md:hidden"
          }`}
        >
          <div
            className={`scroll-thin h-full w-[320px] overflow-y-auto p-4 transition duration-200 ease-out max-md:w-full ${
              panelOpen ? "translate-x-0 opacity-100" : "translate-x-3 opacity-0 max-md:translate-x-0"
            }`}
          >
            <div className="flex items-center justify-between gap-2">
              <h2 className="text-[11px] font-medium tracking-[0.08em] text-ink-faint">{t.reader.noteInfo}</h2>
              <div className="flex items-center gap-0.5">
                <ThemeToggle />
                <IconButton className="md:hidden" label={t.reader.panelOpen} onClick={() => setPanelOpen(false)}>
                  <Icon.x />
                </IconButton>
              </div>
            </div>
            <div className="mt-3 space-y-3 text-[13px]">
              <label className="block text-[11px] text-ink-faint">
                {t.reader.title}
                <input value={title} onChange={(e) => setTitle(e.target.value)} className="mt-0.5 h-8 w-full rounded-md border border-line bg-panel px-2 text-[13px] text-ink" />
              </label>
              <label className="block text-[11px] text-ink-faint">
                {t.reader.summary}
                <textarea
                  value={summary}
                  onChange={(e) => setSummary(e.target.value)}
                  rows={6}
                  className="mt-0.5 min-h-28 w-full resize-y rounded-md border border-line bg-panel px-2 py-2 text-[13px] leading-5 text-ink"
                />
              </label>
              <label className="block text-[11px] text-ink-faint">
                {t.reader.collection}
                <CollectionField value={collection} options={collectionOptions} disabled={archived} onChange={updateCollection} />
              </label>
              <label className="block text-[11px] text-ink-faint">
                {t.reader.tags}
                <input value={tags} onChange={(e) => setTags(e.target.value)} className="mt-0.5 h-8 w-full rounded-md border border-line bg-panel px-2 text-[13px] text-ink" />
              </label>
              <button
                type="button"
                disabled={archived}
                onClick={() => saveMetadata().catch((err: Error) => setMessage(err.message))}
                className="h-8 w-full rounded-[var(--radius-control)] border border-line text-[12px] hover:bg-panel-raised disabled:opacity-50"
              >
                {t.reader.saveMetadata}
              </button>
            </div>

            <div className="mt-5 border-t border-line pt-4">
              {archived ? (
                <p className="text-[12px] text-ink-faint">{t.reader.archivedLocked}</p>
              ) : (
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => setSourceOpen(true)}
                    className="h-8 rounded-[var(--radius-control)] border border-line text-[12px] text-ink hover:bg-panel-raised"
                  >
                    {t.reader.editor.editCode}
                  </button>
                  <button
                    type="button"
                    onClick={() => setFileOpen(true)}
                    className="h-8 rounded-[var(--radius-control)] border border-line text-[12px] text-ink hover:bg-panel-raised"
                  >
                    {t.reader.editor.editFile}
                  </button>
                </div>
              )}
            </div>

            {message ? <p className="mt-3 text-[11px] text-ink-soft">{message}</p> : null}
          </div>
        </aside>
      </div>
      {shareOpen ? (
        <ShareDialog
          key={note.id}
          open
          itemId={note.id}
          title={title}
          interactiveEnabled={interactiveEnabled}
          onClose={() => setShareOpen(false)}
          onChanged={() => {
            listShares()
              .then((body) => {
                const active = body.shares.find((row) => row.item_id === note.id && row.active);
                const token = active?.url_path.split("/").filter(Boolean)[1];
                setShareToken(token);
              })
              .catch(() => setShareToken(undefined));
            router.refresh();
          }}
        />
      ) : null}
      {sourceOpen ? (
        <SourceEditorDialog
          key={`src-${note.id}`}
          open
          itemId={note.id}
          title={title}
          value={source}
          onClose={() => setSourceOpen(false)}
          onSaved={handleContentSaved}
        />
      ) : null}
      {fileOpen ? (
        <FileEditorDialog
          key={`file-${note.id}`}
          open
          itemId={note.id}
          title={title}
          html={source}
          onClose={() => setFileOpen(false)}
          onSaved={handleContentSaved}
        />
      ) : null}
    </div>
  );
}

const ADD_COLLECTION = "__add__";
const fieldClass =
  "mt-0.5 h-8 w-full rounded-md border border-line bg-panel px-2 text-[13px] text-ink outline-none focus:border-accent/60 disabled:opacity-50";

function CollectionField({
  value,
  options,
  disabled,
  onChange,
}: {
  value: string;
  options: string[];
  disabled?: boolean;
  onChange: (value: string) => void;
}) {
  const { messages: t } = useI18n();
  const [adding, setAdding] = useState(false);
  const previous = useRef(value || "Inbox");

  const names = useMemo(() => {
    const unique = new Set(options.filter(Boolean));
    if (value.trim()) unique.add(value.trim());
    unique.add("Inbox");
    return [...unique].sort((a, b) => a.localeCompare(b, "zh"));
  }, [options, value]);

  function finishAdd(next: string) {
    const cleaned = next.trim();
    setAdding(false);
    if (cleaned) {
      previous.current = cleaned;
      onChange(cleaned);
      return;
    }
    onChange(previous.current);
  }

  if (adding) {
    return (
      <input
        autoFocus
        disabled={disabled}
        value={value}
        placeholder={t.reader.addCollectionPlaceholder}
        aria-label={t.reader.addCollection}
        onChange={(event) => onChange(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter") {
            event.preventDefault();
            finishAdd(value);
          }
          if (event.key === "Escape") {
            event.preventDefault();
            setAdding(false);
            onChange(previous.current);
          }
        }}
        onBlur={() => finishAdd(value)}
        className={fieldClass}
      />
    );
  }

  return (
    <select
      disabled={disabled}
      value={names.includes(value) ? value : value || "Inbox"}
      aria-label={t.reader.collection}
      onChange={(event) => {
        if (event.target.value === ADD_COLLECTION) {
          previous.current = value.trim() || "Inbox";
          onChange("");
          setAdding(true);
          return;
        }
        previous.current = event.target.value;
        onChange(event.target.value);
      }}
      className={fieldClass}
    >
      {names.map((name) => (
        <option key={name} value={name}>
          {name}
        </option>
      ))}
      <option value={ADD_COLLECTION}>{t.reader.addCollection}</option>
    </select>
  );
}
