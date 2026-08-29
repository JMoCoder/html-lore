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
    <Svg fill="none">
      <path d="M11 3.5h4.5" />
      <path d="M11 7.5h3" />
      <path d="M11 11.5h1.5" />
      <path d="M4 3.5v9" />
      <path d="m6.5 10.5-2.5 2.5-2.5-2.5" />
    </Svg>
  ),
  pin: ({ filled = false }: { filled?: boolean }) => (
    <Svg fill={filled ? "currentColor" : "none"}>
      <path d="M8 14.2 8 9" />
      <path d="M5.2 3.8h5.6v2.2l1.2 2.6H4l1.2-2.6z" />
    </Svg>
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
  chevronLeft: () => (
    <Svg><path d="m10 3-5 5 5 5" /></Svg>
  ),
  chevronRight: () => (
    <Svg><path d="m6 3 5 5-5 5" /></Svg>
  ),
  wrap: () => (
    <Svg>
      <path d="M3 4.5h10" />
      <path d="M3 8h7.5a2.5 2.5 0 0 1 0 5H8" />
      <path d="m9.5 11.5-1.5 1.5 1.5 1.5" />
      <path d="M3 11.5h3" />
    </Svg>
  ),
  maximize: () => (
    <Svg><path d="M4 6.5V4h2.5M12 4h2.5v2.5M14.5 12V14.5H12M6.5 14.5H4V12" /></Svg>
  ),
  minimize: () => (
    <Svg><path d="M6.5 4H4v2.5M9.5 4H12v2.5M12 9.5v2.5H9.5M4 9.5v2.5h2.5" /></Svg>
  ),
  undo: () => (
    <Svg><path d="M5 7.5H3.5V6M3.5 7.5A5 5 0 1 1 5 12" /></Svg>
  ),
  redo: () => (
    <Svg>      <path d="M11 7.5h1.5V6M12.5 7.5A5 5 0 1 0 11 12" /></Svg>
  ),
  download: () => (
    <Svg>
      <path d="M8 3v7M5.5 7.5 8 10l2.5-2.5M3.5 12.5h9" />
    </Svg>
  ),
  x: () => (
    <Svg><path d="m4 4 8 8M12 4l-8 8" /></Svg>
  ),
  book: () => (
    <Svg><path d="M3.5 3.5h4a2 2 0 0 1 2 2v7a1.5 1.5 0 0 0-1.5-1.5H3.5zM12.5 3.5h-3v7h3a1 1 0 0 0 1-1v-5z" /></Svg>
  ),
  settings: () => (
    <Svg viewBox="0 0 24 24">
      <circle cx="12" cy="12" r="3" />
      <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
    </Svg>
  ),
  help: () => (
    <Svg>
      <circle cx="8" cy="8" r="5.25" />
      <path d="M6.4 6.4a1.65 1.65 0 1 1 1.85 1.62c-.48.26-.75.58-.75 1.18" />
      <circle cx="8" cy="11.3" r="0.7" fill="currentColor" stroke="none" />
    </Svg>
  ),
  github: () => (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" aria-hidden>
      <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8Z" />
    </svg>
  ),
};
