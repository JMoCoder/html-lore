"use client";

import { useEffect } from "react";

export function ServiceWorkerRegister() {
  useEffect(() => {
    if (!("serviceWorker" in navigator)) return;

    // The PWA shell cache is a production concern; during local dev it only
    // causes confusion (stale HTML/JS surviving hot reloads). Aggressively
    // unregister any leftover dev-time worker and clear its caches instead
    // of registering a new one.
    if (process.env.NODE_ENV !== "production") {
      navigator.serviceWorker.getRegistrations().then((registrations) => {
        registrations.forEach((registration) => registration.unregister());
      });
      if (typeof caches !== "undefined") {
        caches.keys().then((keys) => keys.forEach((key) => caches.delete(key)));
      }
      return;
    }

    navigator.serviceWorker.register("/sw.js").catch(() => {
      /* offline enhancement only */
    });
  }, []);
  return null;
}
