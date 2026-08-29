import { en } from "@/i18n/messages/en";
import { ja } from "@/i18n/messages/ja";
import { zhCN } from "@/i18n/messages/zh-CN";
import type { Locale, Messages } from "@/i18n/types";

export const LOCALE_STORAGE_KEY = "html-lore-locale";
export const DEFAULT_LOCALE: Locale = "zh-CN";

const catalogs: Record<Locale, Messages> = {
  "zh-CN": zhCN,
  en,
  ja,
};

export function getMessages(locale: Locale): Messages {
  return catalogs[locale] ?? catalogs[DEFAULT_LOCALE];
}

export function isLocale(value: string): value is Locale {
  return value === "zh-CN" || value === "en" || value === "ja";
}

export function resolveLocale(value: string | null | undefined): Locale {
  if (value && isLocale(value)) return value;
  return DEFAULT_LOCALE;
}

export function formatDate(value: string, locale: Locale): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat(locale, { month: "short", day: "numeric", year: "numeric" }).format(date);
}

export function formatDateTime(value: string, locale: Locale): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat(locale, { dateStyle: "medium", timeStyle: "short" }).format(date);
}

export function formatReadingMinutes(textLength: number, locale: Locale): string {
  const minutes = Math.max(1, Math.round(textLength / 550));
  return getMessages(locale).meta.readingMinutes(minutes);
}

export type { Locale, Messages } from "@/i18n/types";
export { LOCALES, LOCALE_LABELS } from "@/i18n/types";
