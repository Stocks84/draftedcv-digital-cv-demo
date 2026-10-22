#!/usr/bin/env python3
"""DraftedCV Digital CV builder. Edit cv-data.json, then run: python3 build.py
Generates index.html, manifest.webmanifest, sw.js, QR codes, avatar + PWA icons."""
import json, html
from pathlib import Path
import qrcode, qrcode.image.svg
from PIL import Image, ImageDraw, ImageFont

D = json.load(open('cv-data.json')); S, P = D['site'], D['person']
e = lambda t: html.escape(str(t))

def header():
    links = ''.join(f'''
                    <a href="{e(l['url'])}" target="_blank" rel="noopener" class="flex items-center gap-x-2 px-5 py-2.5 bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 rounded-2xl text-sm font-medium transition-all">
                        <i class="{e(l['icon'])}"></i><span>{e(l['label'])}</span></a>''' for l in P['links'])
    return f'''    <!-- Hero / Header -->
    <header class="max-w-7xl mx-auto px-5 sm:px-6 pt-12 sm:pt-16 pb-10 sm:pb-12">
        <div class="flex flex-col lg:flex-row items-start lg:items-center gap-8 lg:gap-10">
            <div class="flex-shrink-0 mx-auto lg:mx-0">
                <div class="w-32 h-32 sm:w-36 sm:h-36 lg:w-44 lg:h-44 rounded-3xl bg-zinc-900 border border-zinc-800 overflow-hidden shadow-2xl">
                    <img src="headshot.png" alt="{e(P['name'])}" class="w-full h-full object-cover">
                </div>
            </div>
            <div class="flex-1">
                <h1 class="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tighter heading-font mb-2">{e(P['name'])}</h1>
                <p class="text-2xl sm:text-3xl text-cyan-400 font-semibold tracking-tight mb-4">{e(P['title'])}</p>
                <div class="flex flex-wrap items-center gap-x-5 gap-y-2 text-sm">
                    <a href="mailto:{e(P['email'])}" class="flex items-center gap-x-2 text-zinc-400 hover:text-white transition-colors"><i class="fa-solid fa-envelope w-4"></i><span>{e(P['email'])}</span></a>
                    <a href="tel:{e(P['phone_href'])}" class="flex items-center gap-x-2 text-zinc-400 hover:text-white transition-colors"><i class="fa-solid fa-phone w-4"></i><span>{e(P['phone'])}</span></a>
                    <span class="flex items-center gap-x-2 text-zinc-400"><i class="fa-solid fa-location-dot w-4"></i><span>{e(P['location'])}</span></span>
                </div>
                <div class="flex items-center gap-x-4 mt-6">{links}
                </div>
            </div>
        </div>
    </header>
'''

def about():
    ps = ''.join(f'<p class="mb-6">{e(p)}</p>' for p in D['about'])
    return f'''    <section id="about" class="max-w-7xl mx-auto px-6 pb-16 scroll-animate">
        <div class="max-w-3xl">
            <h2 class="section-header mb-6 flex items-center gap-x-3"><span>About Me</span></h2>
            <div class="prose prose-invert text-lg text-zinc-300 leading-relaxed">{ps}</div>
            <div class="mt-6 inline-flex items-center gap-x-2 px-4 py-2 bg-zinc-900 border border-zinc-800 rounded-2xl text-sm">
                <div class="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
                <span class="text-emerald-400 font-medium">{e(P['availability'])}</span>
            </div>
        </div>
    </section>
'''

def skills():
    groups = ''
    for g in D['skill_groups']:
        rows = ''.join(f'''
                    <div>
                        <div class="flex justify-between text-sm mb-1.5"><span class="font-medium">{e(n)}</span><span class="text-zinc-500">{e(l)}</span></div>
                        <div class="h-2 bg-zinc-800 rounded-full overflow-hidden"><div class="skill-bar h-2 bg-cyan-500 rounded-full" style="width:{int(w)}%" data-width="{int(w)}"></div></div>
                    </div>''' for n, l, w in g['skills'])
        groups += f'''
            <div class="bg-zinc-900 border border-zinc-800 rounded-3xl p-8">
                <div class="flex items-center gap-x-3 mb-6"><i class="{e(g['icon'])} text-cyan-400 text-xl"></i><h3 class="font-semibold text-xl">{e(g['title'])}</h3></div>
                <div class="space-y-5">{rows}
                </div>
            </div>'''
    h = D.get('highlight'); hl = ''
    if h:
        tags = ''.join(f'<span class="tech-tag">{e(t)}</span>' for t in h['tags'])
        hl = f'''
        <div class="mt-8 bg-zinc-900 border border-zinc-800 rounded-3xl p-8">
            <div class="flex items-start gap-x-4">
                <div class="mt-1"><i class="{e(h['icon'])} text-emerald-400 text-2xl"></i></div>
                <div class="flex-1">
                    <h3 class="font-semibold text-xl mb-3">{e(h['title'])}</h3>
                    <p class="text-zinc-300 leading-relaxed mb-4">{e(h['text'])}</p>
                    <div class="flex flex-wrap gap-2">{tags}</div>
                </div>
            </div>
        </div>'''
    return f'''    <section id="skills" class="max-w-7xl mx-auto px-6 pb-20 scroll-animate">
        <h2 class="section-header mb-8">Skills</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">{groups}
        </div>{hl}
    </section>
'''

def experience():
    items = ''
    for t in D['timeline']:
        bul = ''.join(f'<li class="flex gap-2"><span class="text-blue-400 mt-1.5">•</span> {e(b)}</li>' for b in t.get('bullets', []))
        bul = f'<ul class="space-y-1.5 text-sm text-zinc-300 mt-3">{bul}</ul>' if bul else ''
        note = f'<p class="text-sm text-zinc-400 mt-1">{e(t["note"])}</p>' if t.get('note') else ''
        bg = 'bg-cyan-600' if t.get('current') else 'bg-zinc-700'
        items += f'''
            <div class="timeline-item flex gap-6">
                <div class="flex-shrink-0 w-8 h-8 {bg} rounded-2xl flex items-center justify-center mt-1 z-10"><i class="{e(t['icon'])} text-white text-sm"></i></div>
                <div class="flex-1 pb-2">
                    <div class="flex items-center justify-between flex-wrap gap-x-4">
                        <div><h3 class="font-semibold text-xl">{e(t['title'])}</h3><p class="text-zinc-400">{e(t['org'])}</p></div>
                        <span class="text-sm text-zinc-500 font-medium whitespace-nowrap">{e(t['dates'])}</span>
                    </div>{note}{bul}
                </div>
            </div>'''
    return f'''    <section id="experience" class="max-w-7xl mx-auto px-6 pb-20 scroll-animate">
        <h2 class="section-header mb-10">Experience &amp; Education</h2>
        <div class="space-y-10 relative">{items}
        </div>
    </section>
'''

def projects():
    cards = ''
    for i, p in enumerate(D['projects']):
        tags = ''.join(f'<span class="tech-tag">{e(t)}</span>' for t in p['tech'])
        cards += f'''
            <div onclick="showProjectModal({i})" class="project-card cursor-pointer bg-zinc-900 border border-zinc-800 hover:border-zinc-700 rounded-3xl p-7 group">
                <div class="flex items-start justify-between mb-4">
                    <div><h3 class="font-semibold text-2xl group-hover:text-cyan-400 transition-colors">{e(p['title'])}</h3><p class="text-sm text-emerald-400 mt-1">{e(p['label'])}</p></div>
                    <i class="{e(p['icon'])} text-3xl text-zinc-700 group-hover:text-blue-500 transition-colors"></i>
                </div>
                <p class="text-zinc-300 line-clamp-3">{e(p['summary'])}</p>
                <div class="flex flex-wrap gap-2 mt-5">{tags}</div>
            </div>'''
    return f'''    <section id="projects" class="max-w-7xl mx-auto px-6 pb-20 scroll-animate">
        <h2 class="section-header mb-8">Featured Projects</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">{cards}
        </div>
    </section>
'''

def footer():
    links = ''.join(f'<a href="{e(l["url"])}" target="_blank" rel="noopener" class="text-zinc-500 hover:text-white text-sm">{e(l["label"])}</a>' for l in P['links'])
    short = S['url'].split('://', 1)[1].rstrip('/')
    return f'''    <footer class="border-t border-zinc-800 bg-zinc-950">
        <div class="max-w-7xl mx-auto px-6 py-10 text-center">
            <p class="text-zinc-400 text-sm">© {e(P['name'])}</p>
            <div class="flex justify-center gap-x-6 mt-4">{links}<a href="mailto:{e(P['email'])}" class="text-zinc-500 hover:text-white text-sm">Email</a></div>
        </div>
    </footer>
    <section class="print-only print-qr" aria-hidden="true">
        <img src="qr-code.png" alt="QR code linking to {e(S['url'])}">
        <p>Scan for the full interactive CV.</p>
        <p style="font-size:8.5pt;">{e(short)}</p>
    </section>
'''

MARK = '''    <a href="https://draftedcv.carrd.co" target="_blank" rel="noopener" class="dcv-mark no-print" title="This is an example Digital CV. All details are fictional.">Example CV by <b>DraftedCV</b></a>
    <style>
    .dcv-mark{position:fixed;right:12px;bottom:12px;z-index:40;font:500 11px/1 Inter,system-ui,sans-serif;color:#fff;text-decoration:none;padding:7px 11px;border-radius:999px;background:linear-gradient(90deg,#3B5DAD,#A464A1);opacity:.85;box-shadow:0 4px 14px rgba(0,0,0,.3)}
    .dcv-mark:hover{opacity:1}.dcv-mark b{font-weight:700}
    .welcome-mark{color:#94a3b8;font-size:.72rem;margin:-.75rem 0 1.25rem}.welcome-mark b{background:linear-gradient(90deg,#7b9be6,#c98fc6);-webkit-background-clip:text;background-clip:text;color:transparent}
    @media print{.dcv-print{display:block!important;text-align:center;font-size:8pt;color:#666;margin-top:6pt}}
    </style>
    <p class="dcv-print" style="display:none">Example CV by DraftedCV · all details are fictional</p>'''
WMARK = '<p class="welcome-mark">Example CV by <b>DraftedCV</b> · fictional details</p>'

def write_assets():
    # QR codes (encode the site's own URL)
    qrcode.make(S['url'], image_factory=qrcode.image.svg.SvgPathImage, border=2, error_correction=qrcode.constants.ERROR_CORRECT_M).save('qr-welcome.svg')
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, border=4, box_size=10); q.add_data(S['url']); q.make()
    q.make_image(fill_color='black', back_color='white').convert('RGB').resize((400, 400), Image.NEAREST).save('qr-code.png')
    try: font = lambda s: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', s)
    except Exception: font = lambda s: ImageFont.load_default()
    def icon(size, path, pad=0, radius=True):
        im = Image.new('RGB', (size, size), '#0a1428'); d = ImageDraw.Draw(im)
        if not pad: d.rounded_rectangle([size*.04]*2+[size*.96]*2, radius=size*.18, outline='#22d3ee', width=max(2, size//40))
        f = font(int(size*(.34 if pad else .42))); d.text((size/2, size/2), P['initials'], font=f, fill='#22d3ee', anchor='mm'); im.save(path)
    icon(192, 'icons/icon-192.png'); icon(512, 'icons/icon-512.png'); icon(512, 'icons/icon-maskable-512.png', pad=1); icon(180, 'apple-touch-icon.png')
    # Placeholder "headshot": initials avatar (swap for the client's photo, keep the filename)
    if not Path('headshot.png').exists() or S.get('example_marker'):
        im = Image.new('RGB', (480, 480)); d = ImageDraw.Draw(im)
        for y in range(480): d.line([(0, y), (480, y)], fill=(int(59+(164-59)*y/480), int(93+(100-93)*y/480), int(173+(161-173)*y/480)))
        d.text((240, 240), P['initials'], font=font(180), fill='white', anchor='mm'); im.save('headshot.png')
    Path('favicon.svg').write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="14" fill="#0a1428"/><rect x="2" y="2" width="60" height="60" rx="12" fill="none" stroke="#22d3ee" stroke-width="3"/>
  <text x="32" y="42" text-anchor="middle" font-family="Inter, Arial, sans-serif" font-size="26" font-weight="700" fill="#22d3ee">{e(P['initials'])}</text>
</svg>\n''')
    json.dump({"name": f"{P['name']} CV", "short_name": S['app_short_name'], "description": f"Digital CV of {P['name']}, {P['title']}",
               "id": S['path'], "start_url": S['path'], "scope": S['path'], "display": "standalone",
               "background_color": S['theme_color'], "theme_color": S['theme_color'], "icons": [
                   {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
                   {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
                   {"src": "icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]},
              open('manifest.webmanifest', 'w'), indent=2)
    sw = Path('sw.template.js').read_text().replace('{{CACHE}}', S['cache'])
    Path('sw.js').write_text(sw)

write_assets()
projs = [{k: p[k] for k in ('title', 'description', 'tech', 'live', 'github')} for p in D['projects']]
out = Path('template.html').read_text()
for k, v in {'{{BODY}}': header()+about()+skills()+experience()+projects()+footer(),
             '{{PROJECTS_JSON}}': json.dumps(projs, ensure_ascii=False).replace('</', '<\\/'),
             '{{MARKER}}': MARK if S.get('example_marker') else '', '{{WELCOME_MARK}}': WMARK if S.get('example_marker') else '',
             '{{NAME}}': e(P['name']), '{{TITLE}}': e(P['title']), '{{SHORT}}': e(S['app_short_name']),
             '{{URL}}': e(S['url']), '{{INITIALS}}': e(P['initials'])}.items():
    out = out.replace(k, v)
Path('index.html').write_text(out)
print('Built', S['url'], 'cache', S['cache'])
