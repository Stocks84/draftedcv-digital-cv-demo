// Service worker: offline support for the CV. build.py fills in CACHE from cv-data.json (bump site.cache on each release).
const CACHE = 'dcv-demo-v2';
const CORE = [
  './', 'index.html', 'css/style.css', 'css/tailwind.css', 'css/fonts.css', 'js/main.js',
  'vendor/fa/css/fa.min.css', 'vendor/fa/webfonts/fa-solid-900.woff2', 'vendor/fa/webfonts/fa-brands-400.woff2',
  'fonts/inter-latin-400-normal.woff2', 'fonts/inter-latin-500-normal.woff2', 'fonts/inter-latin-600-normal.woff2',
  'fonts/inter-latin-700-normal.woff2', 'fonts/space-grotesk-latin-500-normal.woff2',
  'fonts/space-grotesk-latin-600-normal.woff2', 'fonts/space-grotesk-latin-700-normal.woff2',
  'favicon.svg', 'apple-touch-icon.png', 'icons/icon-192.png', 'icons/icon-512.png',
  'icons/icon-maskable-512.png', 'qr-code.png', 'qr-welcome.svg', 'headshot.png',
  'contact.vcf', 'alex-morgan-cv.pdf', 'manifest.webmanifest'
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
  if (req.method !== 'GET' || !req.url.startsWith(self.location.origin)) return;
  const put = res => { if (res && res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); } return res; };
  // HTML: network-first so updates show; fall back to cache offline (ignore ?from=qr etc.).
  if (req.mode === 'navigate') {
    e.respondWith(fetch(req).then(put).catch(() => caches.match(req, { ignoreSearch: true }).then(r => r || caches.match('index.html'))));
    return;
  }
  // Everything else: cache-first, refreshed in the background.
  e.respondWith(caches.match(req).then(hit => {
    const net = fetch(req).then(put).catch(() => hit);
    return hit || net;
  }));
});
