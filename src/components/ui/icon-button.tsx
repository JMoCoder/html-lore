import type { ButtonHTMLAttributes, ReactNode } from "react";

export function IconButton({
  label,
  children,
  tone = "default",
  className = "",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  label: string;
  children: ReactNode;
  tone?: "default" | "danger" | "active";
}) {
  const tones = {
    default: "text-ink-faint hover:bg-panel-raised hover:text-ink",
    active: "bg-accent-soft text-accent-strong",
    danger: "text-ink-faint hover:bg-danger/10 hover:text-danger",
  };
  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      className={`inline-flex size-8 items-center justify-center rounded-[var(--radius-control)] transition-colors max-md:size-10 ${tones[tone]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
