const CACHE_NAME = "html-lore-v1.1.12";
const APP_SHELL = [
  "./",
  "index.html",
  "style.css",
  "app.js",
  "config.js",
  "manifest.webmanifest",
  "assets/html-lore-logo.svg",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL)),
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(
      keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key)),
    )),
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;
  const url = new URL(event.request.url);
  if (url.origin === self.location.origin && isBackendOrContentPath(url.pathname)) return;
  if (event.request.mode === "navigate") {
    event.respondWith(
      fetch(event.request).then((response) => {
        if (!response.ok || !isHtmlResponse(response)) return response;
        const copy = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put("index.html", copy));
        return response;
      }).catch(() => caches.match("index.html")),
    );
    return;
  }
  event.respondWith(
    fetch(event.request).then((response) => {
      const copy = response.clone();
      caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
      return response;
    }).catch(() => {
      return caches.match(event.request).then((cached) => {
        if (cached) return cached;
        return fetch(event.request).then((response) => {
          const copy = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
          return response;
        });
      });
    }),
  );
});

function isBackendOrContentPath(pathname) {
  return pathname.startsWith("/api/") || pathname.startsWith("/share/") || pathname.startsWith("/content/");
}

function isHtmlResponse(response) {
  return (response.headers.get("content-type") || "").includes("text/html");
}
