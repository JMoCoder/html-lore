"use client";

import { LOCALES, LOCALE_LABELS } from "@/i18n";
import { useI18n } from "@/i18n/locale-provider";

export function LanguageSwitcher({ compact = false }: { compact?: boolean }) {
  const { locale, setLocale, messages } = useI18n();

  if (compact) {
    return (
      <label className="inline-flex items-center">
        <span className="sr-only">{messages.locale.choose}</span>
        <select
          value={locale}
          onChange={(e) => setLocale(e.target.value as typeof locale)}
          aria-label={messages.locale.choose}
          className="h-7 appearance-none rounded-lg border border-line bg-panel px-2 text-[11px] text-ink outline-none focus:border-accent/60"
        >
          {LOCALES.map((code) => (
            <option key={code} value={code}>
              {LOCALE_LABELS[code]}
            </option>
          ))}
        </select>
      </label>
    );
  }

  return (
    <div
      role="group"
      aria-label={messages.locale.choose}
      className="inline-flex h-9 rounded-[var(--radius-control)] border border-line bg-panel p-0.5"
    >
      {LOCALES.map((code) => {
        const active = locale === code;
        return (
          <button
            key={code}
            type="button"
            onClick={() => setLocale(code)}
            aria-pressed={active}
            className={`h-8 rounded-[8px] px-3 text-[12px] ${
              active ? "bg-panel-raised font-medium text-ink shadow-[var(--shadow-sm)]" : "text-ink-soft hover:text-ink"
            }`}
          >
            {LOCALE_LABELS[code]}
          </button>
        );
      })}
    </div>
  );
}
