/* Service worker — gives the apps offline support and makes them installable.
   Strategy: precache the app shell, then serve cache-first with a network
   fallback. Bump CACHE_VERSION whenever the shell assets change. */
const CACHE_VERSION = "myapps-v1";
const APP_SHELL = [
  "/apps",
  "/apps/todo",
  "/apps/expenses",
  "/static/apps.css",
  "/static/todo.js",
  "/static/expenses.js",
  "/static/pwa.js",
  "/manifest.webmanifest",
];

self.addEventListener("install", function (event) {
  event.waitUntil(
    caches.open(CACHE_VERSION).then(function (cache) {
      return cache.addAll(APP_SHELL);
    })
  );
  self.skipWaiting();
});

self.addEventListener("activate", function (event) {
  // Remove old caches from previous versions.
  event.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(
        keys
          .filter(function (k) { return k !== CACHE_VERSION; })
          .map(function (k) { return caches.delete(k); })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener("fetch", function (event) {
  // Only handle GET requests; let the browser handle the rest.
  if (event.request.method !== "GET") return;

  event.respondWith(
    caches.match(event.request).then(function (cached) {
      if (cached) return cached;
      return fetch(event.request)
        .then(function (response) {
          // Cache successful same-origin responses for next time.
          const copy = response.clone();
          caches.open(CACHE_VERSION).then(function (cache) {
            if (response.ok && event.request.url.startsWith(self.location.origin)) {
              cache.put(event.request, copy);
            }
          });
          return response;
        })
        .catch(function () {
          // Offline and not cached: fall back to the apps hub if possible.
          return caches.match("/apps");
        });
    })
  );
});
