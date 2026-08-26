import Link from "next/link";

export default function NotFound() {
  return (
    <main className="grid min-h-dvh place-items-center bg-bg px-6">
      <div className="text-center">
        <p className="text-[15px] font-semibold text-ink">没有这篇笔记</p>
        <p className="mt-1 text-[13px] text-ink-faint">可能已删除，或链接不完整。</p>
        <Link
          href="/"
          className="mt-4 inline-flex h-8 items-center rounded-[var(--radius-control)] border border-line px-3 text-[13px] text-ink-soft hover:bg-panel"
        >
          返回工作台
        </Link>
      </div>
    </main>
  );
}
