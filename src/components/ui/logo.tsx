import Link from "next/link";

export function Logo({ size = 22 }: { size?: number }) {
  const radius = Math.max(5, Math.round(size * 0.24));

  return (
    <span className="inline-flex min-w-0 items-center gap-2.5">
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src="/html-lore-logo.svg"
        alt=""
        width={size}
        height={size}
        className="block shrink-0 object-contain shadow-[0_0_0_1px_rgb(20_26_23/0.08)] dark:shadow-[0_0_0_1px_rgb(255_255_255/0.14)]"
        style={{ width: size, height: size, borderRadius: radius }}
      />
      <span className="font-display text-[15px] font-black leading-none tracking-[-0.02em] text-ink transition-colors group-hover:text-accent-strong">
        HTM<em className="font-semibold italic text-accent">lore</em>
      </span>
    </span>
  );
}

export function HomeLink() {
  return (
    <Link
      href="/"
      className="group -ml-1 inline-flex items-center rounded-lg px-1 py-1 hover:bg-panel-raised/70"
      aria-label="HTMlore 工作台"
    >
      <Logo />
    </Link>
  );
}
