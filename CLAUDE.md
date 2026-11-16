# DraftedCV Digital CV demo

Fictional digital CV template (v2). Live: https://stocks84.github.io/draftedcv-digital-cv-demo/

## Stack
Static HTML/CSS/JS PWA. Python `build.py` generates the page, CSS, QR, icons, manifest, service worker, vCard, OG image and PDF from `cv-data.json` and `template.html`. Tailwind CSS v3 for utility CSS.

## Commands
- Install: `pip install -r requirements.txt` and `npm install`
- Run: open `index.html`, or `python3 -m http.server 8000`
- Check (no formal tests): `python3 -m py_compile build.py && node --check js/main.js sw.js sw.template.js`
- Build: `python3 build.py` (needs Chrome or Edge for the PDF; `--no-pdf` skips it). CSS only: `npm run build:css`

## Layout
- Edit by hand: `cv-data.json`, `headshot.png`. Layout: `template.html`, `build.py`, `css/style.css`
- `src/tailwind.css` → committed `css/tailwind.css`; `js/`, `fonts/`, `vendor/`, `build-fonts/`

## Conventions
- Demo data is fictional only. After edits, bump `site.cache` (e.g. `-v2`) and rebuild so installed apps update.
- Do not run a full `build.py` from a Stop hook (it writes files and may need a browser).
- Never commit secrets or `willsto84@gmail.com`. Git author must be `Stocks84 <124254214+Stocks84@users.noreply.github.com>`. Do not push to `main` or merge without Will's approval.

## End-of-job report
Every finished coding job must be reported in this shape. Only list a check under CHECKS RUN if it actually ran; anything untested goes under NOT CHECKED, never left out.

PROJECT: repo and branch
PULL REQUEST: link (or not created)
PREVIEW: link or how to open it (or unavailable)
BUILT: what changed, in plain words
CHECKS RUN: what ran and the result
NOT CHECKED: what nobody tested (e.g. real phone, live data, emails)
KNOWN ISSUES: list, or none
COST / USAGE: where to see it; never guess a number
NEXT DECISION: exactly what Will needs to say yes or no to
