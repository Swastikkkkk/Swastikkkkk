"""Builds the profile README art. Run: python3 build.py

Writes assets/*.svg (dark + light) from src/*.jpg. SVGs embed their images so
they render through GitHub's image proxy, and animate with plain CSS.
"""
import base64, io, os, textwrap
from PIL import Image

OUT = 'assets'
os.makedirs(OUT, exist_ok=True)
FONT = "-apple-system,BlinkMacSystemFont,'SF Pro Display','SF Pro Text','Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif"
MONO = "'SF Mono',ui-monospace,Menlo,Consolas,monospace"

THEME = {
    'dark':  dict(bg='#0a0a0a', card='#111111', line='#262626', text='#fafafa', sub='#a1a1a1', faint='#6b6b6b',
                  chip='#1a1a1a', chipLine='#2e2e2e', bar='#2a2a2a', fill='#fafafa', shot='#000'),
    'light': dict(bg='#ffffff', card='#fafafa', line='#e5e5e5', text='#0a0a0a', sub='#525252', faint='#a3a3a3',
                  chip='#ffffff', chipLine='#e5e5e5', bar='#e5e5e5', fill='#0a0a0a', shot='#fff'),
}

FEATURED = [
    dict(key='sketchracer', stat='25', statl='F1 circuits at real scale, plus any track you draw', name='SketchRacer', kind='Browser game',
         desc='Open-world driving in the browser. Draw any track and race it, or drive real F1 circuits at full scale.',
         stack=['Three.js', 'Cloudflare', 'Vercel']),
    dict(key='prepninja', stat='5', statl='scoring axes on every video answer, plus live coding rounds', name='PrepNinja', kind='AI platform',
         desc='Proctored AI mock interviews, coding rounds with a sandboxed runner, and an ATS resume check.',
         stack=['React', 'Node', 'Gemini', 'Judge0']),
    dict(key='chatsnitch', stat='1', statl='permission, zero network access, nothing leaves the browser', name='ChatSnitch', kind='Chrome extension',
         desc='Shows which of your extensions can read your ChatGPT, Claude and Gemini chats. One permission, no network.',
         stack=['Manifest V3', 'JavaScript']),
    dict(key='jalnetra', stat='681', statl='river points checked every 3 hours across India', name='JalNetra', kind='Disaster response',
         desc='Flood early warning on 681 rivers. Predicts which villages flood and calls the village head in Hindi.',
         stack=['AWS Lambda', 'Bedrock', 'RDS']),
]

MORE = [
    dict(slug='lerno', name='Lerno.ai', kind='Won Google Codeclash 2.0',
         desc='Type a concept, get an animated explainer. Claude writes the storyboard and the Manim code.', stack=['React', 'FastAPI', 'Manim']),
    dict(slug='district-mesh', name='District Mesh', kind='iOS',
         desc='Offline mesh for iPhone. Chat, live location, SOS and calls hop between phones with no internet.', stack=['Swift', 'Multipeer']),
    dict(slug='amexpert', name='AmExpert', kind='AI agent',
         desc='Resolves card-servicing requests over voice, WhatsApp, SMS and email with a deterministic policy engine.', stack=['Node', 'LangGraph']),
    dict(slug='agentdrift', name='agentdrift', kind='Dev tool',
         desc='Finds rules that clash across AGENTS.md, CLAUDE.md and .cursorrules, then merges them into one.', stack=['Python', 'CLI']),
    dict(slug='disasterar', name='DisasterAR', kind='iOS, ARKit',
         desc='Indoor evacuation in AR, fully offline. Routes around hazards to the nearest safe exit.', stack=['Swift', 'ARKit']),
    dict(slug='brag-ext', name='brag-ext', kind='Chrome extension',
         desc='Turns any GitHub repo into a short promo video. Voices run locally in the browser.', stack=['TypeScript', 'Remotion']),
]


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def img_uri(key, w, h, q=80):
    im = Image.open(f'src/{key}.jpg').convert('RGB')
    r = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    l, t = (im.width - w) // 2, (im.height - h) // 2
    im = im.crop((l, t, l + w, t + h))
    b = io.BytesIO(); im.save(b, 'JPEG', quality=q, optimize=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()


def lines(text, width):
    return textwrap.wrap(text, width)


def chips(x, y, items, t, size=12):
    out, cx = [], x
    for s in items:
        w = len(s) * size * 0.58 + 22
        out.append(f'<rect x="{cx:.0f}" y="{y}" width="{w:.0f}" height="26" rx="13" fill="{t["chip"]}" stroke="{t["chipLine"]}"/>'
                   f'<text x="{cx + w / 2:.0f}" y="{y + 17}" text-anchor="middle" class="chip">{esc(s)}</text>')
        cx += w + 8
    return ''.join(out)


def svg_open(w, h, label, t, extra_css=''):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">'
            f'<style>text{{font-family:{FONT}}}.mono{{font-family:{MONO}}}'
            f'.chip{{font-size:12px;font-weight:500;fill:{t["sub"]}}}{extra_css}</style>')


# ---------------------------------------------------------------- showreel
def showreel(mode):
    t = THEME[mode]
    W, H = 1000, 500
    SW, SH = 560, 350          # screenshot
    sx, sy = W - SW - 40, 70
    n = len(FEATURED)
    slot = 4.0                  # seconds per slide
    T = slot * n
    p = 100 / n                 # percent per slide
    css = (f'.slide{{opacity:0;animation:show {T}s infinite}}'
           f'@keyframes show{{0%{{opacity:0;transform:translateY(10px)}}{p*0.12:.2f}%{{opacity:1;transform:translateY(0)}}'
           f'{p*0.9:.2f}%{{opacity:1;transform:translateY(0)}}{p:.2f}%{{opacity:0;transform:translateY(-6px)}}100%{{opacity:0}}}}'
           f'.shot{{opacity:0;animation:shot {T}s infinite}}'
           f'@keyframes shot{{0%{{opacity:0;transform:scale(1.04)}}{p*0.15:.2f}%{{opacity:1;transform:scale(1)}}'
           f'{p*0.9:.2f}%{{opacity:1}}{p:.2f}%{{opacity:0}}100%{{opacity:0}}}}'
           f'.bar{{transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:bar {T}s linear infinite}}'
           f'@keyframes bar{{0%{{transform:scaleX(0)}}{p:.2f}%{{transform:scaleX(1)}}{p+0.01:.2f}%{{transform:scaleX(0)}}100%{{transform:scaleX(0)}}}}'
           f'.k{{font-size:12px;letter-spacing:1.6px;fill:{t["faint"]}}}'
           f'.n{{font-size:44px;font-weight:700;letter-spacing:-1.4px;fill:{t["text"]}}}'
           f'.d{{font-size:16px;fill:{t["sub"]}}}'
           f'.idx{{font-size:13px;fill:{t["faint"]}}}')
    s = svg_open(W, H, 'Showreel: ' + ', '.join(f['name'] for f in FEATURED), t, css)
    s += f'<rect width="{W}" height="{H}" rx="20" fill="{t["bg"]}" stroke="{t["line"]}"/>'
    s += f'<defs><clipPath id="c"><rect x="{sx}" y="{sy}" width="{SW}" height="{SH}" rx="14"/></clipPath></defs>'
    s += f'<rect x="{sx}" y="{sy}" width="{SW}" height="{SH}" rx="14" fill="{t["card"]}" stroke="{t["line"]}"/>'
    for i, f in enumerate(FEATURED):
        d = f'animation-delay:{i * slot}s'
        s += f'<g clip-path="url(#c)"><image class="shot" style="{d};transform-origin:{sx + SW/2}px {sy + SH/2}px" x="{sx}" y="{sy}" width="{SW}" height="{SH}" href="{img_uri(f["key"], SW*2, SH*2, 72)}"/></g>'
        g = f'<g class="slide" style="{d}">'
        g += f'<text class="k mono" x="44" y="112">{esc(f["kind"].upper())}</text>'
        g += f'<text class="n" x="42" y="166">{esc(f["name"])}</text>'
        for j, ln in enumerate(lines(f['desc'], 38)):
            g += f'<text class="d" x="44" y="{206 + j * 25}">{esc(ln)}</text>'
        g += chips(44, 300, f['stack'], t)
        g += f'<text class="idx mono" x="44" y="{sy + SH}">0{i+1} / 0{n}</text>'
        s += g + '</g>'
    # progress segments
    bw = (SW - (n - 1) * 8) / n
    for i in range(n):
        x = sx + i * (bw + 8)
        s += f'<rect x="{x:.1f}" y="{sy + SH + 28}" width="{bw:.1f}" height="3" rx="1.5" fill="{t["bar"]}"/>'
        s += f'<rect class="bar" style="animation-delay:{i * slot}s" x="{x:.1f}" y="{sy + SH + 28}" width="{bw:.1f}" height="3" rx="1.5" fill="{t["fill"]}"/>'
        s += f'<text class="idx" x="{x:.1f}" y="{sy + SH + 54}">{esc(FEATURED[i]["name"])}</text>'
    return s + '</svg>\n'


# ---------------------------------------------------------------- featured card
def card(f, mode):
    t = THEME[mode]
    W, H = 500, 300
    css = (f'.n{{font-size:26px;font-weight:700;letter-spacing:-.7px;fill:{t["text"]}}}'
           f'.k{{font-size:11px;letter-spacing:1.4px;fill:{t["faint"]}}}'
           f'.big{{font-size:64px;font-weight:700;letter-spacing:-2.5px;fill:{t["text"]}}}'
           f'.bl{{font-size:14px;fill:{t["sub"]}}}'
           f'.d{{font-size:14px;fill:{t["sub"]}}}'
           f'.go{{font-size:13px;font-weight:600;fill:{t["text"]}}}'
           f'.rise{{animation:rise 1s cubic-bezier(.2,.7,.2,1) .2s both}}'
           f'@keyframes rise{{from{{opacity:0;transform:translateY(12px)}}to{{opacity:1;transform:translateY(0)}}}}')
    s = svg_open(W, H, f'{f["name"]}: {f["desc"]}', t, css)
    s += f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="20" fill="{t["card"]}" stroke="{t["line"]}"/>'
    s += f'<text class="k mono" x="28" y="44">{esc(f["kind"].upper())}</text>'
    s += f'<text class="go" x="{W - 28}" y="44" text-anchor="end">Open ↗</text>'
    s += f'<text class="n" x="27" y="82">{esc(f["name"])}</text>'
    s += f'<g><text class="big" x="24" y="164">{esc(f["stat"])}</text>'
    bx = 24 + len(f["stat"]) * 38 + 18
    for j, ln in enumerate(lines(f["statl"], 34)[:2]):
        s += f'<text class="bl" x="{bx}" y="{136 + j * 20}">{esc(ln)}</text>'
    s += '</g>'
    s += f'<line x1="28" y1="192" x2="{W-28}" y2="192" stroke="{t["line"]}"/>'
    for j, ln in enumerate(lines(f['desc'], 60)[:2]):
        s += f'<text class="d" x="28" y="{220 + j * 20}">{esc(ln)}</text>'
    s += chips(28, H - 46, f['stack'], t)
    return s + '</svg>\n'


# ---------------------------------------------------------------- small card
def small(m, mode):
    t = THEME[mode]
    W, H = 330, 190
    css = (f'.n{{font-size:19px;font-weight:700;letter-spacing:-.4px;fill:{t["text"]}}}'
           f'.k{{font-size:10.5px;letter-spacing:1.3px;fill:{t["faint"]}}}'
           f'.d{{font-size:13px;fill:{t["sub"]}}}'
           f'.go{{font-size:15px;fill:{t["faint"]}}}')
    s = svg_open(W, H, f'{m["name"]}: {m["desc"]}', t, css)
    s += f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="16" fill="{t["card"]}" stroke="{t["line"]}"/>'
    s += f'<text class="k mono" x="20" y="34">{esc(m["kind"].upper())}</text>'
    s += f'<text class="go" x="{W - 20}" y="36" text-anchor="end">↗</text>'
    s += f'<text class="n" x="19" y="66">{esc(m["name"])}</text>'
    for j, ln in enumerate(lines(m['desc'], 44)[:3]):
        s += f'<text class="d" x="20" y="{92 + j * 19}">{esc(ln)}</text>'
    s += chips(20, H - 42, m['stack'], t, 11.5)
    return s + '</svg>\n'


for mode in ('dark', 'light'):
    open(f'{OUT}/showreel-{mode}.svg', 'w').write(showreel(mode))
    for f in FEATURED:
        open(f'{OUT}/{f["key"]}-{mode}.svg', 'w').write(card(f, mode))
    for m in MORE:
        open(f'{OUT}/{m["slug"]}-{mode}.svg', 'w').write(small(m, mode))

for fn in sorted(os.listdir(OUT)):
    print(f'{fn:28} {os.path.getsize(f"{OUT}/{fn}") // 1024} KB')
