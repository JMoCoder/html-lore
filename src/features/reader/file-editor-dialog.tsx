"use client";

import { useCallback, useEffect, useRef, useState, type PointerEvent as ReactPointerEvent, type ReactNode } from "react";
import { Icon } from "@/components/ui/icons";
import { IconButton } from "@/components/ui/icon-button";
import { injectFileEditorRuntime, stripFileEditorRuntime } from "@/features/reader/file-editor-runtime";
import { useI18n } from "@/i18n/locale-provider";
import { saveItemContent } from "@/lib/api";

type Mode = "text" | "element";
type Selection = {
  path: string;
  tag: string;
  text: string;
  style: {
    color?: string;
    backgroundColor?: string;
    fontSize?: number | string;
    lineHeight?: number | string;
    fontWeight?: string;
    fontStyle?: string;
    textDecoration?: string;
    textAlign?: string;
  };
};

const MIN_PANEL = 240;
const MAX_PANEL = 480;
const DEFAULT_PANEL = 320;

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}

function normalizeColor(value: string, fallback: string) {
  const text = value.trim();
  if (/^#[0-9a-f]{6}$/i.test(text)) return text.toLowerCase();
  if (/^#[0-9a-f]{3}$/i.test(text)) {
    return `#${text
      .slice(1)
      .split("")
      .map((part) => `${part}${part}`)
      .join("")}`.toLowerCase();
  }
  return fallback;
}

function normalizeWeight(value: string) {
  const number = Number(value);
  if (number >= 650) return "700";
  if (number >= 550) return "600";
  if (number >= 350) return "400";
  return "";
}

function normalizeAlign(value: string) {
  return value === "left" || value === "center" || value === "right" ? value : "";
}

export function FileEditorDialog({
  open,
  itemId,
  title,
  html,
  onClose,
  onSaved,
}: {
  open: boolean;
  itemId: string;
  title: string;
  html: string;
  onClose: () => void;
  onSaved: (value: string) => void;
}) {
  const { messages: t } = useI18n();
  const e = t.reader.editor;
  const frameRef = useRef<HTMLIFrameElement>(null);
  const [srcdoc, setSrcdoc] = useState("");
  const [original, setOriginal] = useState("");
  const [dirty, setDirty] = useState(false);
  const [saving, setSaving] = useState(false);
  const [feedback, setFeedback] = useState(e.fileLoading);
  const [mode, setMode] = useState<Mode>("text");
  const [collapsed, setCollapsed] = useState(false);
  const [panelWidth, setPanelWidth] = useState(DEFAULT_PANEL);
  const [selection, setSelection] = useState<Selection | null>(null);
  const [history, setHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const historyRef = useRef({ list: [] as string[], index: -1 });
  const syncing = useRef(false);
  const historyTimer = useRef(0);
  const modeRef = useRef<Mode>("text");
  const savingRef = useRef(false);
  const requestSeq = useRef(0);

  const loadDocument = useCallback((source: string) => {
    setSrcdoc(injectFileEditorRuntime(source));
    setSelection(null);
  }, []);

  useEffect(() => {
    if (!open) return;
    setOriginal(html);
    setDirty(false);
    setMode("text");
    modeRef.current = "text";
    setCollapsed(false);
    setFeedback(e.fileLoaded);
    loadDocument(html);
    historyRef.current = { list: [html], index: 0 };
    setHistory([html]);
    setHistoryIndex(0);
  }, [open]); // eslint-disable-line react-hooks/exhaustive-deps

  function post(message: Record<string, unknown>) {
    frameRef.current?.contentWindow?.postMessage(message, "*");
  }

  function serializeFrame() {
    const doc = frameRef.current?.contentDocument;
    return doc ? stripFileEditorRuntime(doc) : "";
  }

  function requestHtml() {
    return new Promise<string>((resolve, reject) => {
      const requestId = `file-edit-${Date.now()}-${++requestSeq.current}`;
      const fallback = window.setTimeout(() => {
        window.removeEventListener("message", listener);
        const html = serializeFrame();
        if (html.trim()) resolve(html);
        else reject(new Error(e.emptyContent));
      }, 1500);
      const listener = (event: MessageEvent) => {
        if (event.source !== frameRef.current?.contentWindow) return;
        const message = event.data || {};
        if (message.type !== "html-lore-file-editor-serialized" || message.requestId !== requestId) return;
        window.clearTimeout(fallback);
        window.removeEventListener("message", listener);
        const html = String(message.html || "") || serializeFrame();
        if (html.trim()) resolve(html);
        else reject(new Error(e.emptyContent));
      };
      window.addEventListener("message", listener);
      post({ type: "html-lore-file-editor-serialize", requestId });
    });
  }

  function pushHistory(next: string) {
    const { list, index } = historyRef.current;
    const trimmed = list.slice(0, index + 1);
    if (trimmed[trimmed.length - 1] === next) return;
    const nextList = [...trimmed, next];
    historyRef.current = { list: nextList, index: nextList.length - 1 };
    setHistory(nextList);
    setHistoryIndex(nextList.length - 1);
  }

  function scheduleHistory() {
    window.clearTimeout(historyTimer.current);
    historyTimer.current = window.setTimeout(() => {
      requestHtml()
        .then((next) => {
          if (next) pushHistory(next);
        })
        .catch(() => {});
    }, 650);
  }

  function markDirty() {
    setDirty(true);
    setFeedback(e.fileUnsaved);
  }

  useEffect(() => {
    if (!open) return;
    function onMessage(event: MessageEvent) {
      if (event.source !== frameRef.current?.contentWindow) return;
      const message = event.data || {};
      if (message.type === "html-lore-file-editor-select" || message.type === "html-lore-file-editor-direct-text") {
        syncing.current = true;
        setSelection(message.selection as Selection);
        queueMicrotask(() => {
          syncing.current = false;
        });
        if (message.type === "html-lore-file-editor-direct-text") {
          markDirty();
          scheduleHistory();
        } else {
          setFeedback(dirty ? e.fileUnsaved : e.fileLoaded);
        }
      } else if (message.type === "html-lore-file-editor-unsupported") {
        setFeedback(e.fileUnsupported);
      }
    }
    window.addEventListener("message", onMessage);
    return () => window.removeEventListener("message", onMessage);
  });

  const close = useCallback(
    (force = false) => {
      if (!force && dirty && !window.confirm(e.fileConfirmClose)) return;
      window.clearTimeout(historyTimer.current);
      onClose();
    },
    [dirty, e.fileConfirmClose, onClose],
  );

  async function save(closeAfter = false) {
    if (savingRef.current) return;
    savingRef.current = true;
    setSaving(true);
    setFeedback(e.saving);
    try {
      window.clearTimeout(historyTimer.current);
      if (mode === "text" && selection?.path) applyChange("text", selection);
      await new Promise<void>((resolve) => {
        requestAnimationFrame(() => requestAnimationFrame(() => resolve()));
      });
      const content = await requestHtml();
      const result = await saveItemContent(itemId, content, (reasons) => window.confirm(e.shareSafetyConfirm(reasons)));
      if (result === "cancelled") {
        setFeedback(e.cancelled);
        return;
      }
      setOriginal(content);
      setDirty(false);
      setFeedback(e.fileSaved);
      onSaved(content);
      if (closeAfter) close(true);
    } catch (error) {
      const message = error instanceof Error ? error.message : e.fileSaveFailed;
      setFeedback(message === "verify-mismatch" ? e.verifyFailed : message);
    } finally {
      savingRef.current = false;
      setSaving(false);
    }
  }

  function applyChange(changed: string, nextSelection = selection) {
    if (syncing.current || !nextSelection?.path) return;
    const style: Record<string, string> = {};
    const current = nextSelection.style || {};
    if (changed === "color") style.color = normalizeColor(String(current.color || ""), "");
    if (changed === "backgroundColor") style.backgroundColor = normalizeColor(String(current.backgroundColor || ""), "");
    if (changed === "fontSize") style.fontSize = current.fontSize ? `${clamp(Number(current.fontSize), 10, 48)}px` : "";
    if (changed === "lineHeight") style.lineHeight = current.lineHeight ? String(clamp(Number(current.lineHeight), 1, 2.4)) : "";
    if (changed === "fontWeight") style.fontWeight = String(current.fontWeight || "");
    if (changed === "fontStyle") style.fontStyle = current.fontStyle === "italic" ? "italic" : "";
    if (changed === "textDecoration") style.textDecoration = String(current.textDecoration || "");
    if (changed === "textAlign") style.textAlign = normalizeAlign(String(current.textAlign || ""));
    post({
      type: "html-lore-file-editor-apply",
      path: nextSelection.path,
      silent: changed === "text",
      values: {
        ...(changed === "text" && mode === "text" ? { text: nextSelection.text } : {}),
        style,
      },
    });
    markDirty();
    if (changed === "text") scheduleHistory();
    else requestHtml().then((next) => next && pushHistory(next)).catch(() => {});
  }

  function stepHistory(direction: number) {
    const next = historyRef.current.index + direction;
    const list = historyRef.current.list;
    if (next < 0 || next >= list.length) return;
    historyRef.current = { list, index: next };
    setHistoryIndex(next);
    const htmlValue = list[next];
    setDirty(htmlValue !== original);
    loadDocument(htmlValue);
    setFeedback(htmlValue !== original ? e.fileUnsaved : e.fileLoaded);
  }

  function startResize(event: ReactPointerEvent<HTMLDivElement>) {
    if (collapsed) return;
    event.preventDefault();
    const startX = event.clientX;
    const startWidth = panelWidth;
    const onMove = (move: globalThis.PointerEvent) => setPanelWidth(clamp(startWidth + startX - move.clientX, MIN_PANEL, MAX_PANEL));
    const onUp = () => {
      window.removeEventListener("pointermove", onMove);
      window.removeEventListener("pointerup", onUp);
    };
    window.addEventListener("pointermove", onMove);
    window.addEventListener("pointerup", onUp);
  }

  useEffect(() => {
    if (!open) return;
    function onKey(event: KeyboardEvent) {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "s") {
        event.preventDefault();
        save(event.shiftKey).catch(() => {});
      } else if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "z") {
        event.preventDefault();
        stepHistory(event.shiftKey ? 1 : -1);
      } else if (event.key === "Escape") {
        event.preventDefault();
        close();
      }
    }
    window.addEventListener("keydown", onKey, true);
    return () => window.removeEventListener("keydown", onKey, true);
  });

  if (!open) return null;

  const selectedName = selection?.tag ? `<${selection.tag}>` : e.fileNoSelection;
  const bold = normalizeWeight(String(selection?.style.fontWeight || "")) === "700";
  const italic = String(selection?.style.fontStyle || "") === "italic";
  const underline = String(selection?.style.textDecoration || "").includes("underline");
  const strike = String(selection?.style.textDecoration || "").includes("line-through");

  return (
    <div className="fixed inset-0 z-50 grid grid-rows-[auto_minmax(0,1fr)] bg-bg">
      <div className="flex min-h-12 items-center justify-between gap-3 border-b border-line bg-panel px-4 py-2">
        <div className="min-w-0">
          <p className="text-[13px] font-semibold text-ink">{e.fileTitle}</p>
          <p className="truncate text-[12px] text-ink-faint">{title}</p>
        </div>
        <div className="flex shrink-0 flex-wrap items-center justify-end gap-1.5">
          <button
            type="button"
            onClick={() => {
              setMode("text");
              modeRef.current = "text";
              post({ type: "html-lore-file-editor-mode", mode: "text" });
            }}
            className={`h-8 rounded-[var(--radius-control)] border px-3 text-[12px] ${
              mode === "text" ? "border-accent/50 bg-accent-soft text-accent-strong" : "border-line text-ink-soft hover:bg-panel-raised"
            }`}
          >
            {e.fileTextMode}
          </button>
          <button
            type="button"
            onClick={() => {
              setMode("element");
              modeRef.current = "element";
              post({ type: "html-lore-file-editor-mode", mode: "element" });
            }}
            className={`h-8 rounded-[var(--radius-control)] border px-3 text-[12px] ${
              mode === "element" ? "border-accent/50 bg-accent-soft text-accent-strong" : "border-line text-ink-soft hover:bg-panel-raised"
            }`}
          >
            {e.fileElementMode}
          </button>
          <IconButton label={e.undo} disabled={historyIndex <= 0} onClick={() => stepHistory(-1)}>
            <Icon.undo />
          </IconButton>
          <IconButton label={e.redo} disabled={historyIndex >= history.length - 1} onClick={() => stepHistory(1)}>
            <Icon.redo />
          </IconButton>
          <button
            type="button"
            disabled={!selection}
            onClick={() => {
              if (!selection) return;
              post({
                type: "html-lore-file-editor-apply",
                path: selection.path,
                values: {
                  style: {
                    color: "",
                    backgroundColor: "",
                    fontSize: "",
                    lineHeight: "",
                    fontWeight: "",
                    fontStyle: "",
                    textDecoration: "",
                    textAlign: "",
                  },
                },
              });
              markDirty();
              requestHtml().then((next) => next && pushHistory(next)).catch(() => {});
            }}
            className="h-8 rounded-[var(--radius-control)] border border-line px-3 text-[12px] text-ink hover:bg-panel-raised disabled:opacity-50"
          >
            {e.fileReset}
          </button>
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

      <div className="relative min-h-0 overflow-hidden bg-sidebar">
        <iframe
          ref={frameRef}
          title={e.fileTitle}
          srcDoc={srcdoc}
          onLoad={() => post({ type: "html-lore-file-editor-mode", mode: modeRef.current })}
          className="h-full border-0 bg-white transition-[width] duration-200"
          style={{ width: collapsed ? "100%" : `calc(100% - ${panelWidth}px)` }}
        />
        <button
          type="button"
          aria-label={collapsed ? e.expandPanel : e.collapsePanel}
          title={collapsed ? e.expandPanel : e.collapsePanel}
          onClick={() => setCollapsed((v) => !v)}
          className="absolute top-2.5 z-10 inline-flex size-8 items-center justify-center rounded-[var(--radius-control)] border border-line bg-panel/80 text-ink-soft backdrop-blur-sm hover:text-ink"
          style={{ right: collapsed ? 18 : panelWidth + 18 }}
        >
          {collapsed ? <Icon.chevronLeft /> : <Icon.chevronRight />}
        </button>
        {collapsed ? null : (
          <div
            role="separator"
            aria-orientation="vertical"
            aria-label={e.resizePanel}
            onPointerDown={startResize}
            className="absolute top-0 bottom-0 z-[2] w-1 cursor-col-resize bg-line"
            style={{ right: panelWidth }}
          />
        )}
        <aside
          className={`absolute inset-y-0 right-0 overflow-y-auto border-l border-line bg-panel p-4 shadow-[var(--shadow-card)] transition-transform duration-200 ${
            collapsed ? "translate-x-full" : "translate-x-0"
          }`}
          style={{ width: panelWidth }}
        >
          <div className="mb-3">
            <p className="text-[13px] font-semibold text-ink">{e.fileSelected}</p>
            <p className="text-[12px] text-ink-faint">{selectedName}</p>
          </div>
          <label className="block text-[11px] text-ink-faint">
            {e.fileText}
            <textarea
              rows={5}
              disabled={mode !== "text" || !selection}
              value={selection?.text ?? ""}
              onChange={(event) => {
                const next = selection ? { ...selection, text: event.target.value } : null;
                setSelection(next);
                applyChange("text", next ?? undefined);
              }}
              className="mt-1 w-full rounded-md border border-line bg-sidebar px-2 py-1.5 text-[13px] text-ink disabled:opacity-50"
            />
          </label>
          <div className="mt-3 grid grid-cols-[1fr_1fr_auto] items-end gap-2">
            <label className="block text-[11px] text-ink-faint">
              {e.fileColor}
              <input
                type="color"
                disabled={!selection}
                value={normalizeColor(String(selection?.style.color || "#000000"), "#000000")}
                onChange={(event) => {
                  if (!selection) return;
                  const next = { ...selection, style: { ...selection.style, color: event.target.value } };
                  setSelection(next);
                  applyChange("color", next);
                }}
                className="mt-1 h-8 w-full rounded-md border border-line bg-sidebar p-1"
              />
            </label>
            <label className="block text-[11px] text-ink-faint">
              {e.fileBackground}
              <input
                type="color"
                disabled={!selection}
                value={normalizeColor(String(selection?.style.backgroundColor || "#ffffff"), "#ffffff")}
                onChange={(event) => {
                  if (!selection) return;
                  const next = { ...selection, style: { ...selection.style, backgroundColor: event.target.value } };
                  setSelection(next);
                  applyChange("backgroundColor", next);
                }}
                className="mt-1 h-8 w-full rounded-md border border-line bg-sidebar p-1"
              />
            </label>
            <div className="flex items-center gap-1">
              <StyleToggle
                label={e.bold}
                pressed={bold}
                onClick={() => {
                  if (!selection) return;
                  const next = { ...selection, style: { ...selection.style, fontWeight: bold ? "" : "700" } };
                  setSelection(next);
                  applyChange("fontWeight", next);
                }}
              >
                B
              </StyleToggle>
              <StyleToggle
                label={e.italic}
                pressed={italic}
                onClick={() => {
                  if (!selection) return;
                  const next = { ...selection, style: { ...selection.style, fontStyle: italic ? "" : "italic" } };
                  setSelection(next);
                  applyChange("fontStyle", next);
                }}
              >
                <em>I</em>
              </StyleToggle>
              <StyleToggle
                label={e.underline}
                pressed={underline}
                onClick={() => {
                  if (!selection) return;
                  const decoration = [!underline && "underline", strike && "line-through"].filter(Boolean).join(" ");
                  const next = { ...selection, style: { ...selection.style, textDecoration: decoration } };
                  setSelection(next);
                  applyChange("textDecoration", next);
                }}
              >
                <span className="underline">U</span>
              </StyleToggle>
              <StyleToggle
                label={e.strike}
                pressed={strike}
                onClick={() => {
                  if (!selection) return;
                  const decoration = [underline && "underline", !strike && "line-through"].filter(Boolean).join(" ");
                  const next = { ...selection, style: { ...selection.style, textDecoration: decoration } };
                  setSelection(next);
                  applyChange("textDecoration", next);
                }}
              >
                <span className="line-through">S</span>
              </StyleToggle>
            </div>
          </div>
          <div className="mt-3 grid grid-cols-2 gap-2">
            <label className="block text-[11px] text-ink-faint">
              {e.fileFontSize}
              <input
                type="number"
                min={10}
                max={48}
                disabled={!selection}
                value={selection?.style.fontSize ? Math.round(Number(selection.style.fontSize)) : ""}
                onChange={(event) => {
                  if (!selection) return;
                  const next = { ...selection, style: { ...selection.style, fontSize: event.target.value } };
                  setSelection(next);
                  applyChange("fontSize", next);
                }}
                className="mt-1 h-8 w-full rounded-md border border-line bg-sidebar px-2 text-[13px] text-ink"
              />
            </label>
            <label className="block text-[11px] text-ink-faint">
              {e.fileLineHeight}
              <input
                type="number"
                min={1}
                max={2.4}
                step={0.1}
                disabled={!selection}
                value={selection?.style.lineHeight ? Number(selection.style.lineHeight).toFixed(1) : ""}
                onChange={(event) => {
                  if (!selection) return;
                  const next = { ...selection, style: { ...selection.style, lineHeight: event.target.value } };
                  setSelection(next);
                  applyChange("lineHeight", next);
                }}
                className="mt-1 h-8 w-full rounded-md border border-line bg-sidebar px-2 text-[13px] text-ink"
              />
            </label>
            <label className="block text-[11px] text-ink-faint">
              {e.fileFontWeight}
              <select
                disabled={!selection}
                value={normalizeWeight(String(selection?.style.fontWeight || ""))}
                onChange={(event) => {
                  if (!selection) return;
                  const next = { ...selection, style: { ...selection.style, fontWeight: event.target.value } };
                  setSelection(next);
                  applyChange("fontWeight", next);
                }}
                className="mt-1 h-8 w-full rounded-md border border-line bg-sidebar px-2 text-[13px] text-ink"
              >
                <option value="">{e.fileInherit}</option>
                <option value="400">400</option>
                <option value="600">600</option>
                <option value="700">700</option>
              </select>
            </label>
            <label className="block text-[11px] text-ink-faint">
              {e.fileAlign}
              <select
                disabled={!selection}
                value={normalizeAlign(String(selection?.style.textAlign || ""))}
                onChange={(event) => {
                  if (!selection) return;
                  const next = { ...selection, style: { ...selection.style, textAlign: event.target.value } };
                  setSelection(next);
                  applyChange("textAlign", next);
                }}
                className="mt-1 h-8 w-full rounded-md border border-line bg-sidebar px-2 text-[13px] text-ink"
              >
                <option value="">{e.fileInherit}</option>
                <option value="left">{e.alignLeft}</option>
                <option value="center">{e.alignCenter}</option>
                <option value="right">{e.alignRight}</option>
              </select>
            </label>
          </div>
          <p className="mt-3 text-[11px] text-ink-faint">{feedback}</p>
        </aside>
      </div>
    </div>
  );
}

function StyleToggle({
  label,
  pressed,
  onClick,
  children,
}: {
  label: string;
  pressed: boolean;
  onClick: () => void;
  children: ReactNode;
}) {
  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      aria-pressed={pressed}
      onClick={onClick}
      className={`inline-flex size-8 items-center justify-center rounded-[var(--radius-control)] border text-[12px] font-semibold ${
        pressed ? "border-accent/50 bg-accent-soft text-accent-strong" : "border-line text-ink-soft hover:bg-sidebar"
      }`}
    >
      {children}
    </button>
  );
}
