"use client";

import Link from "next/link";
import { useI18n } from "@/i18n/locale-provider";

export function NotFoundView() {
  const { messages: t } = useI18n();

  return (
    <main className="grid min-h-dvh place-items-center bg-bg px-6">
      <div className="text-center">
        <p className="text-[15px] font-semibold text-ink">{t.notFound.title}</p>
        <p className="mt-1 text-[13px] text-ink-faint">{t.notFound.hint}</p>
        <Link
          href="/"
          className="mt-4 inline-flex h-8 items-center rounded-[var(--radius-control)] border border-line px-3 text-[13px] text-ink-soft hover:bg-panel"
        >
          {t.notFound.back}
        </Link>
      </div>
    </main>
  );
}
