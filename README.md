# DraftedCV – Digital CV demo / template (v2)

Live demo: https://stocks84.github.io/draftedcv-digital-cv-demo/

**All content is fictional example data** ("Alex Morgan", example.com email, Ofcom drama-range phone number, made-up employers and projects).

## Features
- Personal CV website built from one data file (`cv-data.json`)
- QR welcome screen (encodes the site URL + `?from=qr`, so a scan opens the CV directly; also skipped in the installed app). "Show QR" button in the nav for networking.
- **Save contact** button (vCard), **Download PDF** (real PDF, generated at build time)
- Link previews for LinkedIn/WhatsApp/email (Open Graph + Twitter card + generated `og-image.png`)
- Dark / Light theme (follows the device until the visitor chooses), WCAG AA contrast in both
- Keyboard and screen-reader friendly: project cards are buttons, accessible dialogs (focus trap, Esc, focus return), skip link, reduced-motion support
- Installable phone app (PWA), fully offline incl. icons and fonts
- No third-party requests: fonts (Inter, Space Grotesk) and Font Awesome icons are self-hosted (GDPR-friendly)
- Print stylesheet: single column A4, 10.5pt text, QR code back to the live CV
- Per-client accent colour (`site.accent`), auto-adjusted for contrast

## New client copy (≈15 min)
1. Create the client repo from this one using GitHub's **"Use this template"** (no history is copied).
2. Edit `cv-data.json`: `site.url`, `site.cache` (unique, e.g. `jane-smith-v1`), `app_short_name`, `accent`, `pdf_name`, and all `person` / `about` / `skill_groups` / `timeline` / `projects` content. Set `site.example_marker` to `false` for paying clients; `site.noindex` to `true` to hide from search engines.
3. Replace `headshot.png` with the client's square photo (EXIF/GPS data is stripped on build). If no photo exists, an initials avatar is generated.
4. Build (Linux / macOS / Windows):
   ```
   pip install -r requirements.txt
   npm install            # once, lets build.py rebuild Tailwind CSS
   python3 build.py       # Windows: py build.py
   ```
   This regenerates `index.html`, CSS, QR codes, icons, manifest, `sw.js`, `og-image.png`, `contact.vcf`, and the PDF (needs Chrome or Edge installed; use `--no-pdf` to skip).
5. Commit, push, enable GitHub Pages (main branch, root). Scan the QR to check.
6. After any later edit: bump `site.cache` (e.g. `-v2`) and rebuild so installed apps update.

Files edited by hand: `cv-data.json`, `headshot.png`. Layout lives in `template.html` + `build.py`; styles in `css/style.css`.

Third-party assets: Inter & Space Grotesk (SIL OFL, `fonts/`), Font Awesome Free 6.5.1 (`vendor/fa/LICENSE.txt`), DejaVu Sans (`build-fonts/`, used only to draw generated images).
