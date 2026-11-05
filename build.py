#!/usr/bin/env python3
"""DraftedCV Digital CV builder.

Edit cv-data.json, then run:  python3 build.py   (Windows: py build.py)
Generates index.html, manifest.webmanifest, sw.js, QR codes, icons, link-preview image,
contact.vcf (Save contact) and, if Chrome/Edge is installed, the downloadable PDF.
Works on Linux, macOS and Windows (no hard-coded system paths; UTF-8 everywhere).
"""
import colorsys, html, json, os, shutil, subprocess, sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)                      # run from anywhere

try:
    import qrcode, qrcode.image.svg
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit('Missing packages. Run:  pip install -r requirements.txt')

def rd(p): return (ROOT / p).read_text(encoding='utf-8')
def wr(p, s): (ROOT / p).write_text(s, encoding='utf-8', newline='\n')

D = json.loads(rd('cv-data.json'))

# ---------- validation: friendly errors instead of KeyError ----------
REQ = {'site': ['url', 'cache', 'app_short_name', 'theme_color'],
       'person': ['name', 'initials', 'title', 'email', 'phone', 'phone_href', 'location', 'links', 'availability']}
def validate():
    errs = []
    for sec, keys in REQ.items():
        if sec not in D: errs.append(f'missing section "{sec}"'); continue
        errs += [f'missing "{sec}.{k}"' for k in keys if k not in D[sec]]
    for sec in ('about', 'skill_groups', 'timeline', 'projects'):
        if not isinstance(D.get(sec), list): errs.append(f'"{sec}" must be a list')
    for i, p in enumerate(D.get('projects', [])):
        errs += [f'projects[{i}] missing "{k}"' for k in ('title', 'label', 'icon', 'summary', 'description', 'tech') if k not in p]
    if errs: sys.exit('cv-data.json problems:\n  - ' + '\n  - '.join(errs))
validate()

S, P = D['site'], D['person']
S['path'] = urlparse(S['url']).path or '/'          # derived, no duplicate setting
if not S['url'].endswith('/'): S['url'] += '/'
QR_URL = S['url'] + '?from=qr'                       # scans skip the QR welcome screen
PDF = S.get('pdf_name') or 'cv.pdf'
e = lambda t: html.escape(str(t))

# ---------- colours: per-client accent, auto-fixed for WCAG AA ----------
def hex2rgb(h): h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
def rgb2hex(c): return '#' + ''.join(f'{round(max(0, min(1, x)) * 255):02x}' for x in c)
def lum(c):
    f = lambda x: x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4
    r, g, b = map(f, c); return 0.2126 * r + 0.7152 * g + 0.0722 * b
def contrast(a, b):
    la, lb = sorted((lum(hex2rgb(a)), lum(hex2rgb(b))), reverse=True); return (la + 0.05) / (lb + 0.05)
def fit(colour, bg, target=4.6, lighter=True):
    h, l, s = colorsys.rgb_to_hls(*hex2rgb(colour))
    for _ in range(100):
        c = rgb2hex(colorsys.hls_to_rgb(h, l, s))
        if contrast(c, bg) >= target: return c
        l = min(1, l + .01) if lighter else max(0, l - .01)
    return c
ACCENT = S.get('accent', '#22d3ee')
DARK_BG, LIGHT_BG = '#0f1c36', '#f0f8ff'
ACC_D = fit(ACCENT, DARK_BG, lighter=True)           # accent text on dark cards
ACC_L = fit(ACCENT, LIGHT_BG, lighter=False)         # accent text on light theme
BTN = fit(ACCENT, '#ffffff', lighter=False)          # button bg with white text
BTN_HOVER = fit(BTN, '#ffffff', target=6.5, lighter=False)

# ---------- sections ----------
def contact_links():
    return f'''<a href="mailto:{e(P['email'])}" class="contact-link flex items-center gap-x-2 text-zinc-400" data-print-url="{e(P['email'])}"><i class="fa-solid fa-envelope w-4" aria-hidden="true"></i><span>{e(P['email'])}</span></a>
                    <a href="tel:{e(P['phone_href'])}" class="contact-link flex items-center gap-x-2 text-zinc-400"><i class="fa-solid fa-phone w-4" aria-hidden="true"></i><span>{e(P['phone'])}</span></a>
                    <span class="flex items-center gap-x-2 text-zinc-400"><i class="fa-solid fa-location-dot w-4" aria-hidden="true"></i><span>{e(P['location'])}</span></span>'''

def header():
    links = ''.join(f'''
                    <a href="{e(l['url'])}" target="_blank" rel="noopener noreferrer" class="hero-btn print-url flex items-center gap-x-2 px-5 py-2.5 bg-zinc-900 border border-zinc-800 rounded-2xl text-sm font-medium" data-print-url="{e(l['url'].split('://', 1)[-1])}">
                        <i class="{e(l['icon'])}" aria-hidden="true"></i><span>{e(l['label'])}</span></a>''' for l in P['links'])
    return f'''    <header class="max-w-7xl mx-auto px-5 sm:px-6 pt-12 sm:pt-16 pb-10 sm:pb-12">
        <div class="flex flex-col lg:flex-row items-start lg:items-center gap-8 lg:gap-10">
            <div class="hero-photo flex-shrink-0 mx-auto lg:mx-0">
                <div class="w-32 h-32 sm:w-36 sm:h-36 lg:w-44 lg:h-44 rounded-3xl bg-zinc-900 border border-zinc-800 overflow-hidden shadow-2xl">
                    <img src="{e(P.get('photo', 'headshot.png'))}" alt="Photo of {e(P['name'])}" width="176" height="176" class="w-full h-full object-cover">
                </div>
            </div>
            <div class="flex-1">
                <h1 class="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tighter heading-font mb-2">{e(P['name'])}</h1>
                <p class="hero-title accent-text text-2xl sm:text-3xl font-semibold tracking-tight mb-4">{e(P['title'])}</p>
                <div class="flex flex-wrap items-center gap-x-5 gap-y-2 text-sm">
                    {contact_links()}
                </div>
                <div class="flex flex-wrap items-center gap-3 mt-6">{links}
                    <a href="contact.vcf" download="{e(P['name'].replace(' ', '-').lower())}.vcf" class="hero-btn no-print flex items-center gap-x-2 px-5 py-2.5 bg-zinc-900 border border-zinc-800 rounded-2xl text-sm font-medium"><i class="fa-solid fa-address-card" aria-hidden="true"></i><span>Save contact</span></a>
                    <a href="{e(PDF)}" download class="accent-btn no-print flex items-center gap-x-2 px-5 py-2.5 rounded-2xl text-sm font-semibold"><i class="fa-solid fa-file-arrow-down" aria-hidden="true"></i><span>Download PDF</span></a>
                </div>
            </div>
        </div>
    </header>
'''

def about():
    ps = ''.join(f'<p class="mb-6">{e(p)}</p>' for p in D['about'])
    return f'''    <section id="about" aria-labelledby="h-about" class="max-w-7xl mx-auto px-6 pb-16 scroll-animate">
        <div class="max-w-3xl">
            <h2 id="h-about" class="section-header mb-6">About Me</h2>
            <div class="text-lg text-zinc-300 leading-relaxed">{ps}</div>
            <div class="mt-6 inline-flex items-center gap-x-2 px-4 py-2 bg-zinc-900 border border-zinc-800 rounded-2xl text-sm">
                <span class="pulse-dot w-2 h-2 rounded-full" aria-hidden="true"></span>
                <span class="ok-text font-medium">{e(P['availability'])}</span>
            </div>
        </div>
    </section>
'''

LEVELS = {'learning': 1, 'beginner': 1, 'intermediate': 2, 'confident': 3, 'advanced': 3, 'expert': 3}
def skills():
    groups = ''
    for g in D['skill_groups']:
        chips = ''
        for s in g['skills']:
            n, l = s[0], (s[1] if len(s) > 1 else '')
            lv = LEVELS.get(str(l).lower(), 2)
            chips += f'''
                    <li class="skill-chip lvl-{lv}"><span class="skill-name">{e(n)}</span>{f'<span class="skill-level">{e(l)}</span>' if l else ''}</li>'''
        groups += f'''
            <div class="bg-zinc-900 border border-zinc-800 rounded-3xl p-8">
                <div class="flex items-center gap-x-3 mb-6"><i class="{e(g['icon'])} accent-text text-xl" aria-hidden="true"></i><h3 class="font-semibold text-xl">{e(g['title'])}</h3></div>
                <ul class="skill-chips" aria-label="{e(g['title'])}">{chips}
                </ul>
            </div>'''
    h = D.get('highlight'); hl = ''
    if h:
        tags = ''.join(f'<span class="tech-tag">{e(t)}</span>' for t in h['tags'])
        hl = f'''
        <div class="mt-8 bg-zinc-900 border border-zinc-800 rounded-3xl p-8">
            <div class="flex items-start gap-x-4">
                <div class="mt-1"><i class="{e(h['icon'])} ok-text text-2xl" aria-hidden="true"></i></div>
                <div class="flex-1">
                    <h3 class="font-semibold text-xl mb-3">{e(h['title'])}</h3>
                    <p class="text-zinc-300 leading-relaxed mb-4">{e(h['text'])}</p>
                    <div class="flex flex-wrap gap-2">{tags}</div>
                </div>
            </div>
        </div>'''
    return f'''    <section id="skills" aria-labelledby="h-skills" class="max-w-7xl mx-auto px-6 pb-20 scroll-animate">
        <h2 id="h-skills" class="section-header mb-8">Skills</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">{groups}
        </div>{hl}
    </section>
'''

def experience():
    items = ''
    for t in D['timeline']:
        bul = ''.join(f'<li class="flex gap-2"><span class="accent-text mt-1.5" aria-hidden="true">•</span> {e(b)}</li>' for b in t.get('bullets', []))
        bul = f'<ul class="space-y-1.5 text-sm text-zinc-300 mt-3">{bul}</ul>' if bul else ''
        note = f'<p class="text-sm text-zinc-400 mt-1">{e(t["note"])}</p>' if t.get('note') else ''
        bg = 'dot-current' if t.get('current') else 'bg-zinc-700'
        items += f'''
            <div class="timeline-item flex gap-6">
                <div class="flex-shrink-0 w-8 h-8 {bg} rounded-2xl flex items-center justify-center mt-1 z-10"><i class="{e(t['icon'])} text-white text-sm" aria-hidden="true"></i></div>
                <div class="flex-1 pb-2">
                    <div class="flex items-center justify-between flex-wrap gap-x-4">
                        <div><h3 class="font-semibold text-xl">{e(t['title'])}</h3><p class="text-zinc-400">{e(t['org'])}</p></div>
                        <span class="text-sm text-zinc-500 font-medium whitespace-nowrap">{e(t['dates'])}</span>
                    </div>{note}{bul}
                </div>
            </div>'''
    return f'''    <section id="experience" aria-labelledby="h-exp" class="max-w-7xl mx-auto px-6 pb-20 scroll-animate">
        <h2 id="h-exp" class="section-header mb-10">Experience &amp; Education</h2>
        <div class="space-y-10 relative">{items}
        </div>
    </section>
'''

def projects():
    cards = ''
    for i, p in enumerate(D['projects']):
        tags = ''.join(f'<span class="tech-tag">{e(t)}</span>' for t in p['tech'])
        cards += f'''
            <button type="button" data-project="{i}" aria-haspopup="dialog" class="project-card text-left w-full cursor-pointer bg-zinc-900 border border-zinc-800 rounded-3xl p-7 group">
                <span class="flex items-start justify-between mb-4">
                    <span><span class="block font-semibold text-2xl card-title">{e(p['title'])}</span><span class="block text-sm ok-text mt-1">{e(p['label'])}</span></span>
                    <i class="{e(p['icon'])} text-3xl card-icon" aria-hidden="true"></i>
                </span>
                <span class="block text-zinc-300 line-clamp-3">{e(p['summary'])}</span>
                <span class="flex flex-wrap gap-2 mt-5">{tags}</span>
                <span class="sr-only">, open project details</span>
            </button>'''
    return f'''    <section id="projects" aria-labelledby="h-proj" class="max-w-7xl mx-auto px-6 pb-20 scroll-animate">
        <h2 id="h-proj" class="section-header mb-8">Featured Projects</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">{cards}
        </div>
    </section>
'''

def footer():
    links = ''.join(f'<a href="{e(l["url"])}" target="_blank" rel="noopener noreferrer" class="foot-link text-zinc-400 text-sm">{e(l["label"])}</a>' for l in P['links'])
    short = S['url'].split('://', 1)[1].rstrip('/')
    return f'''    <footer class="site-footer border-t border-zinc-800 bg-zinc-950 no-print">
        <div class="max-w-7xl mx-auto px-6 py-10 text-center">
            <p class="text-zinc-400 text-sm">© {e(P['name'])}</p>
            <div class="flex flex-wrap justify-center gap-x-6 gap-y-2 mt-4">{links}<a href="mailto:{e(P['email'])}" class="foot-link text-zinc-400 text-sm">Email</a><a href="contact.vcf" download class="foot-link text-zinc-400 text-sm">Save contact</a></div>
        </div>
    </footer>
    <section class="print-only print-qr" aria-hidden="true">
        <img src="qr-code.png" alt="">
        <p>Scan for the full interactive CV.</p>
        <p class="print-qr-url">{e(short)}</p>
    </section>
'''

MARK = '''    <a href="https://draftedcv.carrd.co" target="_blank" rel="noopener" class="dcv-mark no-print" title="This is an example Digital CV. All details are fictional.">Example CV by <b>DraftedCV</b></a>
    <p class="dcv-print">Example CV by DraftedCV · all details are fictional</p>'''
WMARK = '<p class="welcome-mark">Example CV by <b>DraftedCV</b> · fictional details</p>'

# ---------- fonts for generated images (bundled, so it works on any OS) ----------
FONT_CANDIDATES = [ROOT / 'build-fonts' / 'DejaVuSans-Bold.ttf', 'DejaVuSans-Bold.ttf', 'Arial Bold.ttf', 'arialbd.ttf',
                   '/System/Library/Fonts/Supplemental/Arial Bold.ttf', 'C:/Windows/Fonts/arialbd.ttf']
FONT_REG = [ROOT / 'build-fonts' / 'DejaVuSans.ttf', 'DejaVuSans.ttf', 'arial.ttf', 'C:/Windows/Fonts/arial.ttf']
def font(size, bold=True):
    for c in (FONT_CANDIDATES if bold else FONT_REG):
        try: return ImageFont.truetype(str(c), size)
        except OSError: continue
    try: return ImageFont.load_default(size)        # Pillow >= 10.1
    except TypeError: return ImageFont.load_default()

def gradient(w, h):
    im = Image.new('RGB', (w, h)); d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / h; d.line([(0, y), (w, y)], fill=(int(59 + 105 * t), int(93 + 7 * t), int(173 - 12 * t)))
    return im

def write_assets():
    # QR codes encode the site URL + ?from=qr (so a scan goes straight to the CV)
    qrcode.make(QR_URL, image_factory=qrcode.image.svg.SvgPathImage, border=2,
                error_correction=qrcode.constants.ERROR_CORRECT_M).save(str(ROOT / 'qr-welcome.svg'))
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, border=4, box_size=10); q.add_data(QR_URL); q.make()
    q.make_image(fill_color='black', back_color='white').convert('RGB').resize((400, 400), Image.NEAREST).save(ROOT / 'qr-code.png')
    (ROOT / 'icons').mkdir(exist_ok=True)
    def icon(size, path, pad=0):
        im = Image.new('RGB', (size, size), S['theme_color']); d = ImageDraw.Draw(im)
        if not pad: d.rounded_rectangle([size*.04]*2 + [size*.96]*2, radius=size*.18, outline=ACC_D, width=max(2, size//40))
        d.text((size/2, size/2), P['initials'], font=font(int(size*(.34 if pad else .42))), fill=ACC_D, anchor='mm'); im.save(ROOT / path)
    icon(192, 'icons/icon-192.png'); icon(512, 'icons/icon-512.png'); icon(512, 'icons/icon-maskable-512.png', pad=1); icon(180, 'apple-touch-icon.png')
    # Placeholder avatar ONLY if there is no photo yet (never overwrites a client photo)
    photo = ROOT / P.get('photo', 'headshot.png')
    if not photo.exists():
        im = gradient(480, 480); ImageDraw.Draw(im).text((240, 240), P['initials'], font=font(180), fill='white', anchor='mm'); im.save(photo)
    else:  # strip EXIF/GPS from client photos
        im = Image.open(photo)
        if im.info.get('exif') or getattr(im, 'getexif', lambda: {})():
            clean = Image.new(im.mode, im.size); clean.putdata(list(im.getdata())); clean.save(photo)
    # Link-preview image (Open Graph / Twitter), 1200x630
    og = gradient(1200, 630); d = ImageDraw.Draw(og)
    d.rounded_rectangle([60, 60, 1140, 570], radius=40, fill=S['theme_color'])
    try:
        ph = Image.open(photo).convert('RGB').resize((260, 260)); m = Image.new('L', (260, 260), 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, 259, 259], radius=48, fill=255); og.paste(ph, (120, 185), m)
    except Exception: pass
    nm = P['name']; fs = 84
    while fs > 40 and d.textlength(nm, font=font(fs)) > 700: fs -= 4
    d.text((430, 215), nm, font=font(fs), fill='white')
    d.text((432, 215 + fs + 20), P['title'], font=font(40), fill=ACC_D)
    d.text((432, 215 + fs + 85), 'Digital CV  ·  ' + S['url'].split('://', 1)[1].rstrip('/'), font=font(22, bold=False), fill='#94a3b8')
    if S.get('example_marker'): d.text((432, 500), 'Example CV by DraftedCV · fictional details', font=font(22, bold=False), fill='#c98fc6')
    og.save(ROOT / 'og-image.png', optimize=True)
    wr('favicon.svg', f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="14" fill="{S['theme_color']}"/><rect x="2" y="2" width="60" height="60" rx="12" fill="none" stroke="{ACC_D}" stroke-width="3"/>
  <text x="32" y="42" text-anchor="middle" font-family="Inter, Arial, sans-serif" font-size="26" font-weight="700" fill="{ACC_D}">{e(P['initials'])}</text>
</svg>\n''')
    # vCard 3.0 for "Save contact"
    v = P.get('vcard', {}); first = v.get('first') or P['name'].split()[0]; last = v.get('last') or ' '.join(P['name'].split()[1:])
    esc = lambda s: str(s).replace('\\', '\\\\').replace(',', '\\,').replace(';', '\\;').replace('\n', '\\n')
    lines = ['BEGIN:VCARD', 'VERSION:3.0', f'N:{esc(last)};{esc(first)};;;', f'FN:{esc(P["name"])}', f'TITLE:{esc(P["title"])}',
             f'EMAIL;TYPE=INTERNET:{P["email"]}', f'TEL;TYPE=CELL:{P["phone_href"]}', f'ADR;TYPE=WORK:;;;{esc(P["location"])};;;',
             f'URL:{S["url"]}'] + [f'URL:{l["url"]}' for l in P['links']]
    if v.get('org'): lines.append(f'ORG:{esc(v["org"])}')
    if v.get('note'): lines.append(f'NOTE:{esc(v["note"])}')
    lines.append('END:VCARD')
    (ROOT / 'contact.vcf').write_bytes(('\r\n'.join(lines) + '\r\n').encode('utf-8'))
    json_out = {"name": f"{P['name']} CV", "short_name": S['app_short_name'], "description": f"Digital CV of {P['name']}, {P['title']}",
                "id": S['path'], "start_url": S['path'], "scope": S['path'], "display": "standalone",
                "background_color": S['theme_color'], "theme_color": S['theme_color'], "icons": [
                    {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
                    {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
                    {"src": "icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}
    wr('manifest.webmanifest', json.dumps(json_out, indent=2, ensure_ascii=False) + '\n')
    wr('sw.js', rd('sw.template.js').replace('{{CACHE}}', S['cache']).replace('{{PDF}}', PDF).replace('{{PHOTO}}', P.get('photo', 'headshot.png')))

def meta():
    desc = f"{P['name']} – {P['title']}, {P['location']}. {P['availability']}."
    img = S['url'] + 'og-image.png'
    tags = [f'<meta name="description" content="{e(desc)}">', f'<link rel="canonical" href="{e(S["url"])}">',
            '<meta property="og:type" content="profile">', f'<meta property="og:title" content="{e(P["name"])} • {e(P["title"])}">',
            f'<meta property="og:description" content="{e(desc)}">', f'<meta property="og:url" content="{e(S["url"])}">',
            f'<meta property="og:image" content="{e(img)}">', '<meta property="og:image:width" content="1200">',
            '<meta property="og:image:height" content="630">', f'<meta property="og:image:alt" content="{e(P["name"])} – {e(P["title"])}">',
            '<meta name="twitter:card" content="summary_large_image">', f'<meta name="twitter:title" content="{e(P["name"])} • {e(P["title"])}">',
            f'<meta name="twitter:description" content="{e(desc)}">', f'<meta name="twitter:image" content="{e(img)}">']
    if S.get('noindex'): tags.append('<meta name="robots" content="noindex">')
    return '\n    '.join(tags)

def theme_vars():
    return (f':root{{--accent:{ACC_D};--accent-light:{ACC_L};--btn:{BTN};--btn-hover:{BTN_HOVER};}}')

def build_css():
    """Rebuild Tailwind if it is installed (npm install), so new classes are never missed."""
    local = ROOT / 'node_modules' / '.bin' / ('tailwindcss.cmd' if os.name == 'nt' else 'tailwindcss')
    if local.exists():
        subprocess.run([str(local), '-i', 'src/tailwind.css', '-o', 'css/tailwind.css', '--minify'], cwd=ROOT, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print('Rebuilt css/tailwind.css')
    else:
        print('Note: run "npm install" once so build.py can rebuild css/tailwind.css automatically.')

def find_chrome():
    for n in ('google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser', 'chrome', 'msedge'):
        if shutil.which(n): return shutil.which(n)
    for p in ('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
              r'C:\Program Files\Google\Chrome\Application\chrome.exe', r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
              r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'):
        if Path(p).exists(): return p

def build_pdf():
    chrome = find_chrome()
    if not chrome: print(f'Note: Chrome/Edge not found, {PDF} not regenerated.'); return
    out = ROOT / PDF
    subprocess.run([chrome, '--headless=new', '--disable-gpu', '--no-sandbox', '--no-pdf-header-footer',
                    '--virtual-time-budget=4000', f'--print-to-pdf={out}', (ROOT / 'index.html').as_uri() + '?from=qr'],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
    print('Built', PDF)

write_assets()
projs = [{k: p.get(k, '') for k in ('title', 'description', 'tech', 'live', 'github')} for p in D['projects']]
out = rd('template.html')
for k, v in {'{{BODY}}': header() + about() + skills() + experience() + projects() + footer(),
             '{{PROJECTS_JSON}}': json.dumps(projs, ensure_ascii=False).replace('</', '<\\/'),
             '{{MARKER}}': MARK if S.get('example_marker') else '', '{{WELCOME_MARK}}': WMARK if S.get('example_marker') else '',
             '{{META}}': meta(), '{{THEME_VARS}}': theme_vars(), '{{THEME_COLOR}}': e(S['theme_color']), '{{PDF}}': e(PDF),
             '{{NAME}}': e(P['name']), '{{TITLE}}': e(P['title']), '{{SHORT}}': e(S['app_short_name']),
             '{{URL}}': e(S['url']), '{{INITIALS}}': e(P['initials'])}.items():
    out = out.replace(k, v)
wr('index.html', out)
print('Built', S['url'], 'cache', S['cache'], f'accent dark {ACC_D} ({contrast(ACC_D, DARK_BG):.1f}:1) light {ACC_L} ({contrast(ACC_L, LIGHT_BG):.1f}:1)')
if '--no-css' not in sys.argv: build_css()
if '--no-pdf' not in sys.argv: build_pdf()
