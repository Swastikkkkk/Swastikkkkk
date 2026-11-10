"""Builds the profile README art. Run: python3 build.py

Writes assets/*-{dark,light}.svg. Every SVG is self-contained (images are
embedded) so it renders through GitHub's image proxy, and animates with CSS
and SMIL only. Outer backgrounds are transparent so they sit on GitHub's own
page colour in both themes.
"""
import base64, io, os, random, textwrap
from PIL import Image

OUT = 'assets'
os.makedirs(OUT, exist_ok=True)
FONT = "-apple-system,BlinkMacSystemFont,'SF Pro Display','SF Pro Text','Helvetica Neue',Helvetica,Arial,sans-serif"
MONO = "'SF Mono',ui-monospace,Menlo,Consolas,monospace"
EASE = 'cubic-bezier(.22,.8,.24,1)'

THEME = {
    'dark': dict(text='#f5f5f7', sub='#a1a1a6', faint='#6e6e73', line='rgba(255,255,255,.10)',
                 card='rgba(255,255,255,.025)', chip='rgba(255,255,255,.04)', bar='rgba(255,255,255,.12)',
                 fill='#f5f5f7', star='#ffffff', shot='#000'),
    'light': dict(text='#1d1d1f', sub='#515154', faint='#86868b', line='rgba(0,0,0,.10)',
                  card='rgba(0,0,0,.018)', chip='rgba(0,0,0,.03)', bar='rgba(0,0,0,.10)',
                  fill='#1d1d1f', star='#1d1d1f', shot='#fff'),
}

FEATURED = [
    dict(key='sketchracer', stat='25', statl='F1 circuits at real scale, plus any track you draw', name='SketchRacer', kind='Browser game',
         desc='Open-world driving in the browser. Draw any track and race it, or drive real F1 circuits at full scale.',
         stack=['Three.js', 'Cloudflare', 'Vercel']),
    dict(key='prepninja', stat='5', statl='scoring axes on every video answer, plus live coding', name='PrepNinja', kind='AI platform',
         desc='Proctored AI mock interviews, coding rounds with a sandboxed runner, and an ATS resume check.',
         stack=['React', 'Node', 'Nemotron', 'Judge0']),
    dict(key='chatsnitch', stat='1', statl='permission, zero network access, nothing leaves the browser', name='ChatSnitch', kind='Chrome extension',
         desc='Shows which of your extensions can read your ChatGPT, Claude and Gemini chats.',
         stack=['Manifest V3', 'JavaScript']),
    dict(key='jalnetra', stat='681', statl='river points checked every 3 hours across India', name='JalNetra', kind='Disaster response',
         desc='Flood early warning on 681 rivers. Predicts which villages flood and calls the village head in Hindi.',
         stack=['AWS Lambda', 'Bedrock', 'RDS']),
]

MORE = [
    dict(slug='lerno', name='ExplAInr', kind='Won Google Codeclash 2.0',
         desc='Type a concept, get an animated explainer. A free LLM writes the storyboard and the Manim code.', stack=['React', 'FastAPI', 'Manim']),
    dict(slug='district-mesh', name='NoBars', kind='iOS',
         desc='Offline mesh for iPhone. Chat, live location, SOS and calls hop between phones with no internet.', stack=['Swift', 'Multipeer']),
    dict(slug='disasterar', name='DisasterAR', kind='iOS, ARKit',
         desc='Indoor evacuation in AR, fully offline. Routes around hazards to the nearest safe exit.', stack=['Swift', 'ARKit']),
]

ROLES = [
    'Incoming SDE at JPMorgan Chase',
    'Shipped SwiftUI payment flows in the Chase app',
    '13 hackathon wins, including SIH 2025',
    'Final-year CS at Manipal University Jaipur',
]

STATS = [
    ('13', '', 'hackathon wins'),
    ('68000', '+', 'teams at SIH 2025. Won it.'),
    ('1000', '+', 'teams at Google Codeclash. 1st.'),
    ('3', '', 'internships, JPMC to KPMG'),
]

TIMELINE = [
    ('2024', 'NetNivaran', 'Web dev intern', 'Mobile-first rebuild, 60% faster'),
    ('2025', 'KPMG', 'Academic intern', 'Ministry dashboards, 40% less manual work'),
    ('2026', 'JPMorgan Chase', 'iOS Payments intern', 'UIKit to SwiftUI + MVVM in the Chase app'),
    ('Next', 'JPMorgan Chase', 'Software Engineer', 'Joining full time after graduation'),
]


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def img_uri(key, w, h, q=78):
    im = Image.open(f'src/{key}.jpg').convert('RGB')
    r = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    l, t = (im.width - w) // 2, (im.height - h) // 2
    im = im.crop((l, t, l + w, t + h))
    b = io.BytesIO(); im.save(b, 'JPEG', quality=q, optimize=True, progressive=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()


def wrap(text, width):
    return textwrap.wrap(text, width)


def chips(x, y, items, t, size=12, cls='chip', style=''):
    out, cx = [], x
    for s in items:
        w = len(s) * size * 0.6 + 22
        out.append(f'<g class="{cls}" style="{style}"><rect x="{cx:.0f}" y="{y}" width="{w:.0f}" height="26" rx="13" fill="{t["chip"]}" stroke="{t["line"]}"/>'
                   f'<text x="{cx + w / 2:.0f}" y="{y + 17}" text-anchor="middle" class="ct">{esc(s)}</text></g>')
        cx += w + 8
    return ''.join(out)


def svg_open(w, h, label, t, css=''):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">'
            f'<style>text{{font-family:{FONT}}}.mono{{font-family:{MONO}}}'
            f'.ct{{font-size:12px;font-weight:500;fill:{t["sub"]}}}'
            f'.k{{font-family:{MONO};font-size:11.5px;letter-spacing:1.6px;fill:{t["faint"]}}}'
            f'.up{{animation:up .9s {EASE} both}}'
            f'@keyframes up{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:none}}}}'
            f'.fade{{animation:fade 1.2s ease both}}@keyframes fade{{from{{opacity:0}}to{{opacity:1}}}}'
            f'{css}</style>')


def d(sec):
    return f'animation-delay:{sec:.2f}s'


# ---------------------------------------------------------------- header
def header(mode):
    t = THEME[mode]
    W, H = 1000, 250
    rnd = random.Random(7)
    n = len(ROLES)
    slot = 3.2
    T = slot * n
    p = 100 / n
    css = (f'.tw{{animation:tw 4s ease-in-out infinite}}@keyframes tw{{0%,100%{{opacity:.15}}50%{{opacity:.8}}}}'
           f'.name{{font-size:68px;font-weight:700;letter-spacing:-2.6px;fill:{t["text"]}}}'
           f'.role{{font-size:22px;font-weight:500;letter-spacing:-.3px;fill:{t["sub"]};opacity:0;animation:role {T}s {EASE} infinite}}'
           f'@keyframes role{{0%{{opacity:0;transform:translateY(16px)}}{p*.12:.2f}%{{opacity:1;transform:none}}'
           f'{p*.86:.2f}%{{opacity:1;transform:none}}{p:.2f}%{{opacity:0;transform:translateY(-12px)}}100%{{opacity:0}}}}'
           f'.pill{{font-size:13px;font-weight:500;fill:{t["text"]}}}'
           f'.ring{{transform-box:fill-box;transform-origin:center;animation:ring 2.4s ease-out infinite}}'
           f'@keyframes ring{{0%{{transform:scale(1);opacity:.6}}100%{{transform:scale(3.2);opacity:0}}}}'
           f'.cur{{animation:blink 1.1s steps(1) infinite}}@keyframes blink{{50%{{opacity:0}}}}')
    s = svg_open(W, H, 'Swastik Dutt. ' + '. '.join(ROLES), t, css)
    # star field, kept to the edges so it never sits behind text
    for _ in range(70):
        x, y = rnd.uniform(4, W - 4), rnd.uniform(4, H - 4)
        if 30 < x < 640 and 40 < y < 215:
            continue
        r = rnd.choice([.6, .8, 1, 1.2])
        s += (f'<circle class="tw" style="animation-delay:{rnd.uniform(0, 4):.2f}s;animation-duration:{rnd.uniform(3, 6):.1f}s" '
              f'cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{t["star"]}"/>')
    s += f'<text class="k up" x="40" y="72">HI, I\'M</text>'
    s += f'<text class="name up" style="{d(.12)}" x="36" y="140">Swastik Dutt</text>'
    for i, r in enumerate(ROLES):
        s += f'<text class="role" style="animation-delay:{.5 + i * slot:.2f}s" x="40" y="186">{esc(r)}</text>'
    # status pill
    label = 'Incoming SDE @jpmorganchase'
    pw = len(label) * 7.4 + 46
    px = W - 40 - pw
    s += f'<g class="up" style="{d(.4)}"><rect x="{px:.0f}" y="52" width="{pw:.0f}" height="32" rx="16" fill="{t["card"]}" stroke="{t["line"]}"/>'
    s += f'<circle class="ring" cx="{px + 18:.0f}" cy="68" r="3.5" fill="{t["text"]}"/><circle cx="{px + 18:.0f}" cy="68" r="3.5" fill="{t["text"]}"/>'
    s += f'<text class="pill" x="{px + 32:.0f}" y="72.5">{esc(label)}</text></g>'
    s += f'<text class="k up" style="{d(.6)}" x="{W - 40}" y="210" text-anchor="end">NOIDA, IN<tspan class="cur"> _</tspan></text>'
    return s + '</svg>\n'


# ---------------------------------------------------------------- stats (odometer)
def stats(mode):
    t = THEME[mode]
    W, H = 1000, 132
    n = len(STATS)
    cw = (W - (n - 1) * 12) / n
    LH = 46
    css = (f'.num{{font-size:40px;font-weight:700;letter-spacing:-1.4px;fill:{t["text"]}}}'
           f'.lab{{font-size:13.5px;fill:{t["sub"]}}}')
    keys = []
    body = ''
    for i, (num, suf, lab) in enumerate(STATS):
        x = i * (cw + 12)
        body += f'<g class="up" style="{d(i * .1)}"><rect x="{x + .5:.1f}" y=".5" width="{cw - 1:.1f}" height="{H - 1}" rx="18" fill="{t["card"]}" stroke="{t["line"]}"/>'
        cx = x + 22
        txt = f'{int(num):,}'
        di = 0
        for ch in txt:
            if ch.isdigit():
                cid = f'c{i}_{di}'
                target = 10 + int(ch)
                keys.append(f'@keyframes {cid}{{from{{transform:translateY(0)}}to{{transform:translateY(-{target * LH}px)}}}}')
                body += f'<clipPath id="k{cid}"><rect x="{cx - 2:.1f}" y="18" width="30" height="{LH}"/></clipPath><g clip-path="url(#k{cid})">'
                body += f'<g style="animation:{cid} {1.6 + di * .15:.2f}s {EASE} {.2 + i * .12:.2f}s both">'
                for k in range(20):
                    body += f'<text class="num" x="{cx:.1f}" y="{56 + k * LH}">{k % 10}</text>'
                body += '</g></g>'
                cx += 24
                di += 1
            else:
                body += f'<text class="num" x="{cx:.1f}" y="56">{ch}</text>'
                cx += 11
        if suf:
            body += f'<text class="num" x="{cx + 1:.1f}" y="56">{suf}</text>'
        body += f'<text class="lab" x="{x + 22:.1f}" y="98">{esc(lab)}</text></g>'
    s = svg_open(W, H, '; '.join(f'{int(a):,}{b} {c}' for a, b, c in STATS), t, css + ''.join(keys))
    return s + body + '</svg>\n'


# ---------------------------------------------------------------- showreel
def showreel(mode):
    t = THEME[mode]
    W, H = 1000, 520
    SW, SH = 560, 350
    sx, sy = W - SW - 32, 64
    n = len(FEATURED)
    slot = 4.5
    T = slot * n
    p = 100 / n
    css = (f'.it{{opacity:0;animation:it {T}s {EASE} infinite}}'
           f'@keyframes it{{0%{{opacity:0;transform:translateY(14px)}}{p*.1:.2f}%{{opacity:1;transform:none}}'
           f'{p*.88:.2f}%{{opacity:1;transform:none}}{p*.98:.2f}%{{opacity:0;transform:translateY(-8px)}}100%{{opacity:0}}}}'
           f'.shot{{opacity:0;transform-box:fill-box;transform-origin:center;animation:shot {T}s linear infinite}}'
           f'@keyframes shot{{0%{{opacity:0;transform:scale(1.08)}}{p*.12:.2f}%{{opacity:1}}'
           f'{p*.9:.2f}%{{opacity:1}}{p*1.02:.2f}%{{opacity:0;transform:scale(1)}}100%{{opacity:0;transform:scale(1)}}}}'
           f'.bar{{transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:bar {T}s linear infinite}}'
           f'@keyframes bar{{0%{{transform:scaleX(0)}}{p:.2f}%{{transform:scaleX(1)}}{p+.01:.2f}%{{transform:scaleX(0)}}100%{{transform:scaleX(0)}}}}'
           f'.lbl{{animation:lbl {T}s linear infinite;fill:{t["faint"]}}}'
           f'@keyframes lbl{{0%,{p:.2f}%{{fill:{t["text"]}}}{p+.01:.2f}%,100%{{fill:{t["faint"]}}}}}'
           f'.n{{font-size:46px;font-weight:700;letter-spacing:-1.6px;fill:{t["text"]}}}'
           f'.d{{font-size:16px;fill:{t["sub"]}}}'
           f'.big{{font-size:52px;font-weight:700;letter-spacing:-2px;fill:{t["text"]}}}'
           f'.bl{{font-size:13.5px;fill:{t["sub"]}}}'
           f'.idx{{font-family:{MONO};font-size:12.5px;fill:{t["faint"]}}}'
           f'.lb{{font-size:13px;font-weight:500}}')
    s = svg_open(W, H, 'Showreel: ' + ', '.join(f['name'] for f in FEATURED), t, css)
    s += f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="22" fill="{t["card"]}" stroke="{t["line"]}"/>'
    s += f'<defs><clipPath id="c"><rect x="{sx}" y="{sy}" width="{SW}" height="{SH}" rx="14"/></clipPath></defs>'
    s += f'<rect x="{sx}" y="{sy}" width="{SW}" height="{SH}" rx="14" fill="{t["shot"]}"/>'
    s += '<g clip-path="url(#c)">'
    for i, f in enumerate(FEATURED):
        s += f'<image class="shot" style="{d(i * slot)}" x="{sx}" y="{sy}" width="{SW}" height="{SH}" preserveAspectRatio="xMidYMid slice" href="{img_uri(f["key"], SW * 2, SH * 2, 70)}"/>'
    s += '</g>'
    s += f'<rect x="{sx}" y="{sy}" width="{SW}" height="{SH}" rx="14" fill="none" stroke="{t["line"]}"/>'
    for i, f in enumerate(FEATURED):
        base = i * slot
        s += f'<text class="k it" style="{d(base)}" x="40" y="{sy + 34}">{esc(f["kind"].upper())}</text>'
        s += f'<text class="n it" style="{d(base + .08)}" x="38" y="{sy + 88}">{esc(f["name"])}</text>'
        g = f'<g class="it" style="{d(base + .16)}">'
        for j, ln in enumerate(wrap(f['desc'], 38)[:3]):
            g += f'<text class="d" x="40" y="{sy + 128 + j * 24}">{esc(ln)}</text>'
        s += g + '</g>'
        g = f'<g class="it" style="{d(base + .26)}"><text class="big" x="37" y="{sy + 254}">{esc(f["stat"])}</text>'
        bx = 40 + len(f['stat']) * 31 + 14
        for j, ln in enumerate(wrap(f['statl'], 30)[:2]):
            g += f'<text class="bl" x="{bx}" y="{sy + 228 + j * 19}">{esc(ln)}</text>'
        s += g + '</g>'
        s += f'<g class="it" style="{d(base + .34)}">{chips(40, sy + SH - 26, f["stack"], t)}</g>'
    bw = (SW - (n - 1) * 10) / n
    by = sy + SH + 34
    for i, f in enumerate(FEATURED):
        x = sx + i * (bw + 10)
        s += f'<rect x="{x:.1f}" y="{by}" width="{bw:.1f}" height="3" rx="1.5" fill="{t["bar"]}"/>'
        s += f'<rect class="bar" style="{d(i * slot)}" x="{x:.1f}" y="{by}" width="{bw:.1f}" height="3" rx="1.5" fill="{t["fill"]}"/>'
        s += f'<text class="lb lbl" style="{d(i * slot)}" x="{x:.1f}" y="{by + 26}">{esc(f["name"])}</text>'
    s += f'<text class="idx" x="40" y="{by + 26}">SELECTED WORK</text>'
    return s + '</svg>\n'


# ---------------------------------------------------------------- small card
def small(m, mode, i):
    t = THEME[mode]
    W, H = 330, 196
    css = (f'.n{{font-size:20px;font-weight:700;letter-spacing:-.5px;fill:{t["text"]}}}'
           f'.d{{font-size:13px;fill:{t["sub"]}}}'
           f'.go{{font-size:15px;fill:{t["faint"]}}}')
    s = svg_open(W, H, f'{m["name"]}: {m["desc"]}', t, css)
    s += f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="18" fill="{t["card"]}" stroke="{t["line"]}"/>'
    o = i * .12
    s += f'<text class="k up" style="{d(o)}" x="22" y="36">{esc(m["kind"].upper())}</text>'
    s += f'<text class="go up" style="{d(o)}" x="{W - 22}" y="38" text-anchor="end">↗</text>'
    s += f'<text class="n up" style="{d(o + .08)}" x="21" y="70">{esc(m["name"])}</text>'
    g = f'<g class="up" style="{d(o + .16)}">'
    for j, ln in enumerate(wrap(m['desc'], 43)[:3]):
        g += f'<text class="d" x="22" y="{96 + j * 19}">{esc(ln)}</text>'
    s += g + '</g>'
    s += f'<g class="up" style="{d(o + .24)}">{chips(22, H - 44, m["stack"], t, 11.5)}</g>'
    return s + '</svg>\n'


# ---------------------------------------------------------------- experience timeline
def timeline(mode):
    t = THEME[mode]
    W, H = 1000, 230
    n = len(TIMELINE)
    x0, x1, ly = 60, W - 60, 92
    step = (x1 - x0) / (n - 1)
    css = (f'.draw{{stroke-dasharray:1000;stroke-dashoffset:1000;animation:draw 1.8s {EASE} .2s forwards}}'
           f'@keyframes draw{{to{{stroke-dashoffset:0}}}}'
           f'.dot{{transform-box:fill-box;transform-origin:center;animation:pop .6s {EASE} both}}'
           f'@keyframes pop{{from{{transform:scale(0)}}to{{transform:scale(1)}}}}'
           f'.ring{{transform-box:fill-box;transform-origin:center;animation:ring 2.4s ease-out 2.2s infinite;opacity:0}}'
           f'@keyframes ring{{0%{{transform:scale(1);opacity:.5}}100%{{transform:scale(3);opacity:0}}}}'
           f'.yr{{font-family:{MONO};font-size:12px;letter-spacing:1.4px;fill:{t["faint"]}}}'
           f'.co{{font-size:17px;font-weight:650;letter-spacing:-.3px;fill:{t["text"]}}}'
           f'.ro{{font-size:13.5px;font-weight:500;fill:{t["sub"]}}}'
           f'.de{{font-size:12.5px;fill:{t["faint"]}}}')
    s = svg_open(W, H, 'Experience: ' + '; '.join(f'{a} {b}, {c}' for a, b, c, _ in TIMELINE), t, css)
    s += f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="22" fill="{t["card"]}" stroke="{t["line"]}"/>'
    s += f'<text class="k" x="36" y="44">EXPERIENCE</text>'
    s += f'<line x1="{x0}" y1="{ly}" x2="{x1}" y2="{ly}" stroke="{t["bar"]}" stroke-width="2"/>'
    s += f'<line class="draw" pathLength="1000" x1="{x0}" y1="{ly}" x2="{x1}" y2="{ly}" stroke="{t["fill"]}" stroke-width="2"/>'
    for i, (yr, co, ro, de) in enumerate(TIMELINE):
        x = x0 + i * step
        delay = .2 + 1.8 * (i / (n - 1)) * .8
        anchor = 'start' if i == 0 else ('end' if i == n - 1 else 'middle')
        last = i == n - 1
        if last:
            s += f'<circle class="ring" cx="{x:.1f}" cy="{ly}" r="6" fill="{t["fill"]}"/>'
        s += f'<circle class="dot" style="{d(delay)}" cx="{x:.1f}" cy="{ly}" r="6" fill="{t["fill"] if last else "none"}" stroke="{t["fill"]}" stroke-width="2"/>'
        if not last:
            s += f'<circle class="dot" style="{d(delay)}" cx="{x:.1f}" cy="{ly}" r="2.5" fill="{t["fill"]}"/>'
        tx = x if anchor == 'middle' else (x - 6 if anchor == 'start' else x + 6)
        g = f'<g class="up" style="{d(delay + .1)}">'
        g += f'<text class="yr" x="{tx:.1f}" y="{ly - 22}" text-anchor="{anchor}">{esc(yr.upper())}</text>'
        g += f'<text class="co" x="{tx:.1f}" y="{ly + 40}" text-anchor="{anchor}">{esc(co)}</text>'
        g += f'<text class="ro" x="{tx:.1f}" y="{ly + 62}" text-anchor="{anchor}">{esc(ro)}</text>'
        for j, ln in enumerate(wrap(de, 30)[:2]):
            g += f'<text class="de" x="{tx:.1f}" y="{ly + 86 + j * 17}" text-anchor="{anchor}">{esc(ln)}</text>'
        s += g + '</g>'
    return s + '</svg>\n'


# ---------------------------------------------------------------- arcade: a lap of SketchRacer
TRACK = ('M600,212 C568,160 584,78 660,66 C736,54 770,122 834,104 C898,86 958,98 958,160 '
         'C958,222 900,246 822,238 C760,232 742,196 700,218 C660,240 622,250 600,212 Z')


def arcade(mode):
    t = THEME[mode]
    W, H = 1000, 290
    LAP = 6.0
    START = 2.0
    css = (f'.trk{{stroke-dasharray:1000;stroke-dashoffset:1000;animation:draw 1.8s {EASE} .1s forwards}}'
           f'.trk2{{stroke-dasharray:1000;stroke-dashoffset:1000;animation:draw 1.8s {EASE} .3s forwards}}'
           f'@keyframes draw{{to{{stroke-dashoffset:0}}}}'
           f'.t{{font-size:40px;font-weight:700;letter-spacing:-1.4px;fill:{t["text"]}}}'
           f'.d{{font-size:15px;fill:{t["sub"]}}}'
           f'.clk{{font-family:{MONO};font-size:34px;font-weight:600;fill:{t["text"]}}}'
           f'.cl{{font-family:{MONO};font-size:11px;letter-spacing:1.4px;fill:{t["faint"]}}}'
           f'.cta{{font-size:13.5px;font-weight:600;fill:{t["text"]}}}'
           f'.flag{{animation:flag {LAP}s steps(1) {START}s infinite}}'
           f'@keyframes flag{{0%{{opacity:1}}6%{{opacity:.25}}100%{{opacity:.25}}}}')
    # digit columns for a ticking lap clock: s . t h  (0:0s.th)
    cols = [('s', LAP, 6), ('t', 1.0, 10), ('h', .1, 10)]
    LH = 40
    for c, per, k in cols:
        css += f'.r{c}{{animation:r{c} {per}s steps({k}) {START}s infinite}}@keyframes r{c}{{to{{transform:translateY(-{k * LH}px)}}}}'
    css += f'.lp{{animation:lp {LAP * 3}s steps(3) {START}s infinite}}@keyframes lp{{to{{transform:translateY(-{3 * LH}px)}}}}'
    s = svg_open(W, H, 'SketchRacer: draw a loop, it becomes a track, then race it', t, css)
    s += f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="22" fill="{t["card"]}" stroke="{t["line"]}"/>'
    s += f'<text class="k up" x="40" y="50">ARCADE</text>'
    s += f'<text class="t up" style="{d(.08)}" x="38" y="98">Draw it. Race it.</text>'
    g = f'<g class="up" style="{d(.16)}">'
    for j, ln in enumerate(wrap('Freehand a loop in SketchRacer and it turns into a real track with checkpoints and lap timing.', 50)):
        g += f'<text class="d" x="40" y="{130 + j * 22}">{esc(ln)}</text>'
    s += g + '</g>'
    # lap clock
    cx, cy = 40, 222
    s += f'<g class="up" style="{d(.3)}"><text class="cl" x="{cx}" y="{cy - 36}">LAP TIME</text>'
    s += f'<text class="clk" x="{cx}" y="{cy}">0:0</text>'
    xs = {'s': cx + 61, 't': cx + 102, 'h': cx + 123}
    s += f'<text class="clk" x="{cx + 82}" y="{cy}">.</text>'
    for c, per, k in cols:
        s += f'<clipPath id="q{c}"><rect x="{xs[c] - 1}" y="{cy - 30}" width="22" height="{LH}"/></clipPath>'
        s += f'<g clip-path="url(#q{c})"><g class="r{c}">'
        for v in range(k + 1):
            s += f'<text class="clk" x="{xs[c]}" y="{cy + v * LH}">{v % k}</text>'
        s += '</g></g>'
    lx = cx + 190
    s += f'<text class="cl" x="{lx}" y="{cy - 36}">LAP</text>'
    s += f'<clipPath id="ql"><rect x="{lx - 1}" y="{cy - 30}" width="80" height="{LH}"/></clipPath><g clip-path="url(#ql)"><g class="lp">'
    for v in range(4):
        s += f'<text class="clk" x="{lx}" y="{cy + v * LH}">{v % 3 + 1}/3</text>'
    s += '</g></g></g>'
    s += f'<text class="cta up" style="{d(.4)}" x="40" y="262">Play at sketchracer.com ↗</text>'
    # track
    s += f'<path class="trk" pathLength="1000" d="{TRACK}" fill="none" stroke="{t["bar"]}" stroke-width="22" stroke-linejoin="round"/>'
    s += f'<path class="trk2" pathLength="1000" d="{TRACK}" fill="none" stroke="{t["faint"]}" stroke-width="1.4" stroke-dasharray="6 9" opacity=".7" transform="translate(1.5,-1)"/>'
    s += f'<path class="trk" pathLength="1000" d="{TRACK}" fill="none" stroke="{t["sub"]}" stroke-width="1.6" opacity=".55" transform="translate(-1,1.5)"/>'
    # start / finish line (checkered) at path start, track runs roughly vertical there
    import math
    vx, vy = -32, -52
    L = math.hypot(vx, vy); px_, py_ = -vy / L * 13, vx / L * 13
    seg = f'x1="{600 - px_:.1f}" y1="{212 - py_:.1f}" x2="{600 + px_:.1f}" y2="{212 + py_:.1f}"'
    s += f'<line {seg} stroke="{t["shot"]}" stroke-width="5"/>'
    s += f'<line class="flag" {seg} stroke="{t["fill"]}" stroke-width="5" stroke-dasharray="3.25 3.25"/>'
    # trail + car
    s += (f'<path pathLength="1000" d="{TRACK}" fill="none" stroke="{t["fill"]}" stroke-width="3" stroke-linecap="round" '
          f'stroke-dasharray="70 930" stroke-dashoffset="70" opacity="0">'
          f'<set attributeName="opacity" to=".55" begin="{START}s"/>'
          f'<animate attributeName="stroke-dashoffset" from="70" to="-930" dur="{LAP}s" begin="{START}s" repeatCount="indefinite"/></path>')
    s += (f'<g opacity="0"><set attributeName="opacity" to="1" begin="{START}s"/>'
          f'<animateMotion dur="{LAP}s" begin="{START}s" repeatCount="indefinite" rotate="auto" path="{TRACK}"/>'
          f'<rect x="-9" y="-5" width="18" height="10" rx="3" fill="{t["fill"]}"/>'
          f'<rect x="2" y="-3.5" width="4" height="7" rx="1" fill="{t["shot"]}" opacity=".7"/></g>')
    return s + '</svg>\n'


for mode in ('dark', 'light'):
    open(f'{OUT}/header-{mode}.svg', 'w').write(header(mode))
    open(f'{OUT}/stats-{mode}.svg', 'w').write(stats(mode))
    open(f'{OUT}/showreel-{mode}.svg', 'w').write(showreel(mode))
    open(f'{OUT}/experience-{mode}.svg', 'w').write(timeline(mode))
    open(f'{OUT}/arcade-{mode}.svg', 'w').write(arcade(mode))
    for i, m in enumerate(MORE):
        open(f'{OUT}/{m["slug"]}-{mode}.svg', 'w').write(small(m, mode, i))

for fn in sorted(os.listdir(OUT)):
    print(f'{fn:28} {os.path.getsize(f"{OUT}/{fn}") // 1024} KB')
