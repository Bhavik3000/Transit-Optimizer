// This is a basic Service Worker to pass the PWA installation requirements
self.addEventListener('install', (e) => {
    console.log('[Service Worker] Installed');
});

self.addEventListener('fetch', (e) => {
    // We aren't caching anything offline yet, just passing requests through
});