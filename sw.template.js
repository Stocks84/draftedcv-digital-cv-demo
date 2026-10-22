// Service worker: offline support for the CV. Bump CACHE on each release.
const CACHE = '{{CACHE}}';
const CORE = [
  './', 'index.html', 'css/style.css', 'css/tailwind.css', 'js/main.js',
  'favicon.svg', 'apple-touch-icon.png', 'icons/icon-192.png', 'icons/icon-512.png',
  'icons/icon-maskable-512.png', 'qr-code.png', 'qr-welcome.svg', 'headshot.png',
  'manifest.webmanifest'
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const put = res => { if (res && (res.ok || res.type === 'opaque')) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); } return res; };
  // HTML: network-first so updates show; fall back to cache offline.
  if (req.mode === 'navigate') {
    e.respondWith(fetch(req).then(put).catch(() => caches.match(req).then(r => r || caches.match('index.html'))));
    return;
  }
  // Everything else (CSS, JS, fonts, images, PDF): cache-first, refreshed in the background.
  e.respondWith(caches.match(req).then(hit => {
    const net = fetch(req).then(put).catch(() => hit);
    return hit || net;
  }));
});
