import type { Note } from "@/fixtures/notes";
import { formatDate as formatDateLocale, formatReadingMinutes, type Locale } from "@/i18n";

export function formatDate(value: string, locale: Locale = "zh-CN"): string {
  return formatDateLocale(value, locale);
}

export function noteReadingTime(note: Note, locale: Locale = "zh-CN"): string {
  const text = note.html ? note.html.replace(/<[^>]+>/g, "") : note.summary;
  return formatReadingMinutes(text.length, locale);
}

export function shareUrl(token: string): string {
  return `/share/${token}`;
}
