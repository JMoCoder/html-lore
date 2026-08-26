import Link from "next/link";

export default function NotFound() {
  return (
    <main className="flex min-h-dvh flex-col items-center justify-center gap-3 bg-paper text-ink">
      <p className="font-serif text-2xl tracking-tight">没有这篇笔记</p>
      <Link href="/" className="text-sm text-accent hover:underline">
        返回工作台
      </Link>
    </main>
  );
}
