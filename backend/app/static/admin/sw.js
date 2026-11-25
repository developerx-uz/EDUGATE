// EDUGATE Service Worker (PWA)
const CACHE_NAME = 'edugate-cache-v2';
const CORE_ASSETS = [
  '/edugate/manifest.json',
  '/edugate/static/admin/icons/icon-192.png',
  '/edugate/static/admin/icons/icon-512.png'
];

self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(CORE_ASSETS).catch((err) => {
        console.warn('EDUGATE SW cache warning:', err);
      });
    })
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);
  // API so'rovlari hech qachon keshlanmaydi
  if (url.pathname.includes('/api/')) return;

  event.respondWith(
    fetch(event.request)
      .then((networkResponse) => networkResponse)
      .catch(() => caches.match(event.request))
  );
});
