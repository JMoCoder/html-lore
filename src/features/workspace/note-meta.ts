import type { Note } from "@/fixtures/notes";

export function formatDate(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("zh-CN", { month: "short", day: "numeric", year: "numeric" }).format(date);
}

export function noteReadingTime(note: Note): string {
  const minutes = Math.max(1, Math.round(note.html.replace(/<[^>]+>/g, "").length / 550));
  return `${minutes} 分钟`;
}

export function shareUrl(token: string): string {
  return `/share/${token}`;
}
