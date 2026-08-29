"use client";

import { LocaleProvider } from "@/i18n/locale-provider";
import { ServiceWorkerRegister } from "@/components/pwa/service-worker-register";

export function AppProviders({ children }: { children: React.ReactNode }) {
  return (
    <LocaleProvider>
      {children}
      <ServiceWorkerRegister />
    </LocaleProvider>
  );
}
