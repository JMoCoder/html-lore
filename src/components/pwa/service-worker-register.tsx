"use client";

import { useEffect } from "react";

export function ServiceWorkerRegister() {
  useEffect(() => {
    const media = window.matchMedia("(display-mode: standalone)");
    const syncStandalone = () => {
      const iosStandalone = "standalone" in navigator && Boolean((navigator as Navigator & { standalone?: boolean }).standalone);
      document.documentElement.classList.toggle("standalone", media.matches || iosStandalone);
    };
    syncStandalone();
    media.addEventListener("change", syncStandalone);

    if (!("serviceWorker" in navigator)) {
      return () => media.removeEventListener("change", syncStandalone);
    }

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
      return () => media.removeEventListener("change", syncStandalone);
    }

    navigator.serviceWorker.register("/sw.js").catch(() => {
      /* offline enhancement only */
    });
    return () => media.removeEventListener("change", syncStandalone);
  }, []);
  return null;
}
