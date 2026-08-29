"use client";

import { useI18n } from "@/i18n/locale-provider";

export function ShareShell({
  title,
  html,
  styles,
  mode,
}: {
  title: string;
  summary: string;
  html: string;
  styles: string;
  mode: string;
}) {
  const { messages: t } = useI18n();
  const srcDoc = `<!doctype html><html><head><meta charset="utf-8">${styles}</head><body>${html}</body></html>`;
  return (
    <div className="flex min-h-dvh flex-col bg-panel">
      <header className="flex h-9 shrink-0 items-center justify-between border-b border-line px-4 text-[11px] text-ink-faint">
        <span className="font-display font-semibold tracking-tight text-ink-soft">{t.sharePage.brand}</span>
        <span className="inline-flex items-center gap-1.5">
          <span className="size-1.5 rounded-full bg-accent" />
          {mode === "interactive" ? t.sharePage.modeInteractive : t.sharePage.modeSafe}
        </span>
      </header>
      <iframe
        title={title}
        sandbox="allow-scripts"
        srcDoc={srcDoc}
        className="min-h-0 w-full flex-1 border-0 bg-panel"
      />
    </div>
  );
}
