# DraftedCV – Digital CV demo / template

Live demo: https://stocks84.github.io/draftedcv-digital-cv-demo/

**All content is fictional example data** ("Alex Morgan", example.com email, Ofcom drama-range phone number, made-up employers and projects).

Features: personal CV website, QR welcome screen on every open (encodes the site's own URL), installable phone app (PWA) with offline support, light/dark + Classic view, print/PDF styles with a QR code for paper CVs.

## New client copy (≈15 min)
1. Copy this repo to a new repo (e.g. `jane-smith-cv`).
2. Edit `cv-data.json`: `site.url`, `site.path` (`/<repo>/`), `site.cache` (unique, e.g. `jane-smith-v1`), `app_short_name`, and all `person` / `about` / `skills` / `timeline` / `projects` content. Set `site.example_marker` to `false` for paying clients.
3. Replace `headshot.png` with the client's photo (square), or leave the initials avatar.
4. `pip install qrcode pillow && python3 build.py` – regenerates `index.html`, QR codes, icons, manifest and `sw.js`.
5. Commit, push, enable GitHub Pages (main branch, root). Scan the QR to check.
6. After any later edit: bump `site.cache` (e.g. `-v2`) and rebuild so installed apps update.

Files edited by hand: `cv-data.json`, `headshot.png`. Layout lives in `template.html` + `build.py`; styles in `css/`.
If you add new Tailwind classes, rebuild CSS with `npm run build:css`.
