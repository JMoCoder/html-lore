"use client";

import { APP_SITE_URL } from "@/server/version";
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
    <div className="app-shell flex flex-col bg-panel">
      <header className="flex h-10 shrink-0 items-center justify-between border-b border-line px-4 text-[11px] text-ink-faint">
        <a
          href={APP_SITE_URL}
          target="_blank"
          rel="noreferrer"
          aria-label={t.sharePage.brandHome}
          title={t.sharePage.brandHome}
          className="font-display font-semibold tracking-tight text-ink-soft hover:text-accent-strong"
        >
          {t.sharePage.brand}
        </a>
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
