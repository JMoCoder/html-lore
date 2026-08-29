"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Icon } from "@/components/ui/icons";
import { IconButton } from "@/components/ui/icon-button";
import { HtmlSourceEditor } from "@/features/reader/html-source-editor";
import { useI18n } from "@/i18n/locale-provider";
import { saveItemContent } from "@/lib/api";

export function SourceEditorDialog({
  open,
  itemId,
  title,
  value,
  onClose,
  onSaved,
}: {
  open: boolean;
  itemId: string;
  title: string;
  value: string;
  onClose: () => void;
  onSaved: (value: string) => void;
}) {
  const { messages: t } = useI18n();
  const e = t.reader.editor;
  const [draft, setDraft] = useState(value);
  const [original, setOriginal] = useState(value);
  const [wrap, setWrap] = useState(true);
  const [fullscreen, setFullscreen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [feedback, setFeedback] = useState(e.loaded);
  const [cursor, setCursor] = useState({ line: 1, column: 1 });
  const draftRef = useRef(value);
  const savingRef = useRef(false);
  const dirty = draft !== original;

  const close = useCallback(
    (force = false) => {
      if (!force && draftRef.current !== original && !window.confirm(e.confirmClose)) return;
      setFullscreen(false);
      onClose();
    },
    [e.confirmClose, onClose, original],
  );

  const save = useCallback(
    async (closeAfter = false) => {
      if (savingRef.current) return;
      savingRef.current = true;
      setSaving(true);
      setFeedback(e.saving);
      try {
        const content = draftRef.current;
        const result = await saveItemContent(itemId, content, (reasons) => window.confirm(e.shareSafetyConfirm(reasons)));
        if (result === "cancelled") {
          setFeedback(e.cancelled);
          return;
        }
        setDraft(content);
        setOriginal(content);
        setFeedback(e.saved);
        onSaved(content);
        if (closeAfter) close(true);
      } catch (error) {
        const message = error instanceof Error ? error.message : e.saveFailed;
        setFeedback(message === "verify-mismatch" ? e.verifyFailed : message);
      } finally {
        savingRef.current = false;
        setSaving(false);
      }
    },
    [close, e.cancelled, e.saveFailed, e.saved, e.saving, e.shareSafetyConfirm, e.verifyFailed, itemId, onSaved],
  );

  useEffect(() => {
    if (!open) return;
    function onKey(event: KeyboardEvent) {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "s") {
        event.preventDefault();
        save(event.shiftKey).catch(() => {});
      } else if (event.key === "Escape") {
        event.preventDefault();
        close();
      }
    }
    window.addEventListener("keydown", onKey, true);
    return () => window.removeEventListener("keydown", onKey, true);
  }, [close, open, save]);

  if (!open) return null;

  return (
    <div
      className={`fixed inset-0 z-50 grid bg-ink/40 ${fullscreen ? "p-0" : "place-items-center p-5"}`}
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) close();
      }}
    >
      <div
        className={`grid min-h-0 grid-rows-[auto_minmax(0,1fr)_auto] overflow-hidden border border-line bg-panel shadow-[var(--shadow-card)] ${
          fullscreen
            ? "h-dvh w-full rounded-none"
            : "h-[min(820px,calc(100dvh-40px))] w-full max-w-[1180px] rounded-[var(--radius-card)]"
        }`}
      >
        <div className="flex min-h-12 items-center justify-between gap-3 border-b border-line px-4 py-2">
          <div className="min-w-0">
            <p className="text-[13px] font-semibold text-ink">{e.codeTitle}</p>
            <p className="truncate text-[12px] text-ink-faint">{title}</p>
          </div>
          <div className="flex shrink-0 items-center gap-1.5">
            <button
              type="button"
              disabled={saving}
              onClick={() => save(false)}
              className="h-8 rounded-[var(--radius-control)] border border-line px-3 text-[12px] text-ink hover:bg-panel-raised disabled:opacity-50"
            >
              {saving ? e.saving : e.save}
            </button>
            <button
              type="button"
              disabled={saving}
              onClick={() => save(true)}
              className="h-8 rounded-[var(--radius-control)] bg-accent px-3 text-[12px] font-medium text-white hover:bg-accent-strong disabled:opacity-50"
            >
              {saving ? e.saving : e.saveAndClose}
            </button>
            <IconButton label={e.close} disabled={saving} onClick={() => close()}>
              <Icon.x />
            </IconButton>
          </div>
        </div>

        <div className="relative min-h-0 overflow-hidden">
          <HtmlSourceEditor
            value={draft}
            wrap={wrap}
            onChange={(next) => {
              draftRef.current = next;
              setDraft(next);
              setFeedback(next !== original ? e.unsaved : e.loaded);
            }}
            onCursor={setCursor}
          />
          <div className="absolute top-2.5 right-3 z-10 flex items-center gap-0.5 rounded-[var(--radius-control)] border border-line bg-panel/90 p-0.5 shadow-[var(--shadow-sm)] backdrop-blur-sm">
            <IconButton
              label={e.wrap}
              tone={wrap ? "active" : "default"}
              aria-pressed={wrap}
              onClick={() => setWrap((v) => !v)}
            >
              <Icon.wrap />
            </IconButton>
            <IconButton
              label={fullscreen ? e.exitFullscreen : e.fullscreen}
              tone={fullscreen ? "active" : "default"}
              aria-pressed={fullscreen}
              onClick={() => setFullscreen((v) => !v)}
            >
              {fullscreen ? <Icon.minimize /> : <Icon.maximize />}
            </IconButton>
          </div>
        </div>

        <div className="flex min-h-8 items-center justify-between gap-3 border-t border-line px-4 text-[11px] text-ink-faint">
          <span className="truncate">{saving ? e.saving : dirty && feedback !== e.saved ? e.unsaved : feedback}</span>
          <span className="shrink-0 tabular-nums">{e.position(cursor.line, cursor.column)}</span>
        </div>
      </div>
    </div>
  );
}
