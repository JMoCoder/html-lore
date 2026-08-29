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

  useEffect(() => {
    collectionRef.current = collection;
  }, [collection]);

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

  return (
    <div className="flex h-dvh flex-col bg-bg">
      <header className="flex h-14 shrink-0 items-center gap-2 border-b border-line px-4">
        <Link
          href="/"
          className="group inline-flex items-center gap-1.5 rounded-lg px-2 py-1 text-[13px] text-ink-soft transition-colors hover:bg-panel hover:text-ink"
        >
          <span className="inline-flex transition-transform duration-150 group-hover:-translate-x-0.5">
            <Icon.chevronLeft />
          </span>
          {t.reader.back}
        </Link>
        <div className="mx-auto flex min-w-0 max-w-xl flex-1 items-center justify-center gap-2">
          <h1 className="truncate text-[14px] font-semibold tracking-tight text-ink">{title}</h1>
          <span className="shrink-0 text-[11px] text-ink-faint">
            {collection} · {formatDate(note.updated, locale)}
          </span>
        </div>
        <div className="flex items-center gap-0.5">
          <IconButton label={t.reader.favorite} tone={favorite ? "active" : "default"} onClick={() => patchState({ favorite: !favorite })}>
            <Icon.star filled={favorite} />
          </IconButton>
          <IconButton label={t.reader.archive} onClick={() => patchState({ archived: !archived })}>
            <Icon.archive />
          </IconButton>
          <IconButton label={t.reader.share} tone={shareToken ? "active" : "default"} onClick={() => setShareOpen(true)}>
            <Icon.share />
          </IconButton>
          <IconButton label={t.reader.download} onClick={() => triggerDownload(itemContentDownloadHref(note.id))}>
            <Icon.download />
          </IconButton>
          <IconButton label={t.reader.openOriginal} onClick={() => window.open(itemContentHref(note.id), "_blank")}>
            <Icon.external />
          </IconButton>
          <div className="mx-1 h-5 w-px bg-line" />
          <IconButton
            label={panelOpen ? t.reader.panelOpen : t.reader.panelClosed}
            tone={panelOpen ? "active" : "default"}
            onClick={() => setPanelOpen((v) => !v)}
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

        <aside
          aria-hidden={!panelOpen}
          style={{ width: PANEL_WIDTH, marginRight: panelOpen ? 0 : -PANEL_WIDTH }}
          className="shrink-0 border-l border-line bg-sidebar transition-[margin] duration-200 ease-out"
        >
          <div
            className={`scroll-thin h-full w-[320px] overflow-y-auto p-4 transition duration-200 ease-out ${
              panelOpen ? "translate-x-0 opacity-100" : "translate-x-3 opacity-0"
            }`}
          >
            <div className="flex items-center justify-between gap-2">
              <h2 className="text-[11px] font-medium tracking-[0.08em] text-ink-faint">{t.reader.noteInfo}</h2>
              <ThemeToggle />
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
      <ShareDialog
        open={shareOpen}
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
      <SourceEditorDialog
        open={sourceOpen}
        itemId={note.id}
        title={title}
        value={source}
        onClose={() => setSourceOpen(false)}
        onSaved={handleContentSaved}
      />
      <FileEditorDialog
        open={fileOpen}
        itemId={note.id}
        title={title}
        html={source}
        onClose={() => setFileOpen(false)}
        onSaved={handleContentSaved}
      />
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
