import type { ReactNode } from "react";
import type { Metadata } from "next";

export const metadata: Metadata = {
  robots: { index: false, follow: false },
  icons: {
    icon: [{ url: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'/%3E" }],
  },
};

export default function ShareLayout({ children }: { children: ReactNode }) {
  return children;
}
