import type { ReactNode, SVGProps } from "react";

function Svg({ children, ...props }: SVGProps<SVGSVGElement> & { children: ReactNode }) {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden {...props}>
      {children}
    </svg>
  );
}

export const Icon = {
  search: () => (
    <Svg><circle cx="7" cy="7" r="4.5" /><path d="m10.5 10.5 3 3" /></Svg>
  ),
  plus: () => (
    <Svg><path d="M8 3.5v9M3.5 8h9" /></Svg>
  ),
  filter: () => (
    <Svg><path d="M2.5 4h11M4.5 8h7M6.5 12h3" /></Svg>
  ),
  sort: () => (
    <Svg><path d="M11 3.5v9m0 0 2.5-2.5M11 12.5l-2.5-2.5M5 12.5v-9m0 0L2.5 6M5 3.5l2.5 2.5" /></Svg>
  ),
  star: ({ filled = false }: { filled?: boolean }) => (
    <Svg fill={filled ? "currentColor" : "none"}>
      <path d="m8 2.6 1.7 3.4 3.8.6-2.75 2.67.65 3.78L8 11.2l-3.4 1.85.65-3.78L2.5 6.6l3.8-.6z" />
    </Svg>
  ),
  archive: () => (
    <Svg><path d="M3 3.5h10v3H3zM3.5 6.5h9v6h-9zM6.5 9h3" /></Svg>
  ),
  restore: () => (
    <Svg><path d="M3 3.5h10v3H3zM3.5 6.5h9v6h-9zM9.5 12l-1.5-1.5M9.5 12l-1.5 1.5" /></Svg>
  ),
  share: () => (
    <Svg><circle cx="12" cy="3.5" r="1.5" /><circle cx="12" cy="12.5" r="1.5" /><circle cx="4" cy="8" r="1.5" /><path d="m5.4 7.2 5.2-2.7M5.4 8.8l5.2 2.7" /></Svg>
  ),
  edit: () => (
    <Svg><path d="M10.5 3 13 5.5 6 12.5H3.5V10zM9 4.5l2.5 2.5" /></Svg>
  ),
  trash: () => (
    <Svg><path d="M3 4.5h10M6.5 4.5v-1h3v1M4.5 4.5l.5 9h6l.5-9M6.8 7.5v4M9.2 7.5v4" /></Svg>
  ),
  external: () => (
    <Svg><path d="M6.5 4H3.5v8.5H12V9.5M9 3.5h4.5V8M13.5 3.5 7.5 9.5" /></Svg>
  ),
  moon: () => (
    <Svg><path d="M13 10.5A5.5 5.5 0 0 1 5.5 3a5.5 5.5 0 1 0 7.5 7.5Z" /></Svg>
  ),
  chevronDown: () => (
    <Svg><path d="m4 6 4 4 4-4" /></Svg>
  ),
  x: () => (
    <Svg><path d="m4 4 8 8M12 4l-8 8" /></Svg>
  ),
  book: () => (
    <Svg><path d="M3.5 3.5h4a2 2 0 0 1 2 2v7a1.5 1.5 0 0 0-1.5-1.5H3.5zM12.5 3.5h-3v7h3a1 1 0 0 0 1-1v-5z" /></Svg>
  ),
};
