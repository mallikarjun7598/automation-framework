/* Registers the service worker so the apps become installable and work
   offline. Registered at root scope ("/") so it controls all /apps pages. */
(function () {
  "use strict";
  if ("serviceWorker" in navigator) {
    window.addEventListener("load", function () {
      navigator.serviceWorker
        .register("/service-worker.js", { scope: "/" })
        .catch(function (err) {
          // Non-fatal: the app still works without offline support.
          console.warn("Service worker registration failed:", err);
        });
    });
  }
})();
