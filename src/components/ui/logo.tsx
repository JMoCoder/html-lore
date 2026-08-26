import Link from "next/link";

export function Logo({ size = 22 }: { size?: number }) {
  return (
    <span className="inline-flex items-center gap-2">
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src="/html-lore-logo.svg" alt="" width={size} height={size} style={{ width: size, height: size }} />
      <span className="font-display text-[15px] font-semibold tracking-tight text-ink">
        HTMlore
      </span>
    </span>
  );
}

export function HomeLink() {
  return (
    <Link href="/" className="inline-flex items-center gap-2 rounded-lg px-1 py-1 hover:bg-panel-raised/70" aria-label="HTMlore 工作台">
      <Logo />
    </Link>
  );
}
