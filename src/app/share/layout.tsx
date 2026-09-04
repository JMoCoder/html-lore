import type { ReactNode } from "react";
import type { Metadata } from "next";

/** Inlined so the tab icon does not request `/favicon.ico` (often behind reverse-proxy auth). */
const SHARE_FAVICON =
  "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'%3E%3Crect width='512' height='512' rx='128' fill='%23141a17'/%3E%3Cpath d='M152 142h168l108 108v122H152z' fill='%23fff'/%3E%3Cpath d='M320 142v108h108' fill='%23dcece5'/%3E%3Ccircle cx='256' cy='292' r='32' fill='%232f7f68'/%3E%3Crect x='239' y='324' width='34' height='76' rx='17' fill='%232f7f68'/%3E%3C/svg%3E";

export const metadata: Metadata = {
  robots: { index: false, follow: false },
  icons: {
    icon: [{ url: SHARE_FAVICON, type: "image/svg+xml" }],
  },
};

export default function ShareLayout({ children }: { children: ReactNode }) {
  return children;
}
