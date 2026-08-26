import type { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "ghost" | "quiet";

const styles: Record<Variant, string> = {
  primary:
    "bg-accent text-paper hover:opacity-90 dark:text-[#0c1412]",
  ghost:
    "border border-line bg-transparent text-ink hover:bg-accent-soft",
  quiet:
    "text-ink-soft hover:bg-accent-soft hover:text-ink",
};

export function Button({
  variant = "primary",
  className = "",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant }) {
  return (
    <button
      className={`inline-flex h-9 items-center justify-center rounded-full px-4 text-sm tracking-wide transition-colors duration-150 disabled:opacity-50 ${styles[variant]} ${className}`}
      {...props}
    />
  );
}
