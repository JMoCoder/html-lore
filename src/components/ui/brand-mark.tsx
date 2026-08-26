export function BrandMark({ compact = false }: { compact?: boolean }) {
  return (
    <span className="flex items-center gap-2.5 text-ink">
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src="/html-lore-logo.svg" alt="" width={28} height={28} className="size-7" />
      {compact ? null : (
        <span className="font-serif text-[1.35rem] leading-none tracking-tight">
          HTM<em className="not-italic text-accent">lore</em>
        </span>
      )}
    </span>
  );
}
