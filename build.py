"""Builds the profile README art. Run: python3 build.py

Writes assets/*-{dark,light}.svg. Every SVG is self-contained (images are
embedded) so it renders through GitHub's image proxy, and animates with CSS
and SMIL only. Backgrounds are transparent so each piece sits on GitHub's own
page colour in both themes.

One visual system: SF type, one neutral palette, hairlines for lists, a single
card style for the two hero blocks, sentence-case labels.
"""
import base64, io, math, os, textwrap
from PIL import Image

OUT = 'assets'
os.makedirs(OUT, exist_ok=True)
FONT = "-apple-system,BlinkMacSystemFont,'SF Pro Display','SF Pro Text','Helvetica Neue',Helvetica,Arial,sans-serif"
MONO = "'SF Mono',ui-monospace,Menlo,Consolas,monospace"
EASE = 'cubic-bezier(.22,.8,.24,1)'
W = 1000

THEME = {
    'dark': dict(text='#f5f5f7', sub='#a1a1a6', faint='#6e6e73', line='rgba(255,255,255,.10)',
                 card='rgba(255,255,255,.025)', chip='rgba(255,255,255,.045)', bar='rgba(255,255,255,.12)',
                 chrome='#1c1c1e', fill='#f5f5f7', shot='#000'),
    'light': dict(text='#1d1d1f', sub='#515154', faint='#86868b', line='rgba(0,0,0,.10)',
                  card='rgba(0,0,0,.018)', chip='rgba(0,0,0,.035)', bar='rgba(0,0,0,.10)',
                  chrome='#f2f2f4', fill='#1d1d1f', shot='#fff'),
}

FEATURED = [
    dict(key='sketchracer', url='sketchracer.com', stat='25', statl='F1 circuits at real scale, plus any track you draw',
         name='SketchRacer', desc='Open-world driving in the browser. Draw any track and race it, or drive real F1 circuits at full scale.',
         stack=['Three.js', 'Cloudflare', 'Vercel']),
    dict(key='prepninja', url='prepninja-tawny.vercel.app', stat='5', statl='scoring axes on every video answer, plus live coding',
         name='PrepNinja', desc='Proctored AI mock interviews, coding rounds with a sandboxed runner, and an ATS resume check.',
         stack=['React', 'Node', 'Nemotron', 'Judge0']),
    dict(key='chatsnitch', url='chatsnitch.vercel.app', stat='1', statl='permission, no network access, nothing leaves the browser',
         name='ChatSnitch', desc='Shows which of your extensions can read your ChatGPT, Claude and Gemini chats.',
         stack=['Manifest V3', 'JavaScript']),
    dict(key='jalnetra', url='jalnetra-lilac.vercel.app', stat='681', statl='river points checked every 3 hours across India',
         name='JalNetra', desc='Flood early warning on 681 rivers. Predicts which villages flood and calls the village head in Hindi.',
         stack=['AWS Lambda', 'Bedrock', 'RDS']),
]

MORE = [
    dict(slug='lerno', name='ExplAInr', kind='Google Codeclash winner', desc='Type a concept, get an animated Manim explainer'),
    dict(slug='district-mesh', name='NoBars', kind='iOS', desc='Chat, location, SOS and calls with no internet'),
    dict(slug='disasterar', name='DisasterAR', kind='iOS, ARKit', desc='Offline indoor evacuation in AR, routed around hazards'),
]

TIMELINE = [
    ('Next', 'JPMorgan Chase', 'Software Engineer', 'Joining full time after graduation'),
    ('2026', 'JPMorgan Chase', 'iOS Payments intern', 'UIKit to SwiftUI and MVVM in the Chase app'),
    ('2025', 'KPMG', 'Academic intern', 'Ministry dashboards, 40% less manual reporting'),
    ('2024', 'NetNivaran', 'Web development intern', 'Mobile-first rebuild, 60% faster loads'),
]


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def img_uri(key, w, h, q=74):
    im = Image.open(f'src/{key}.jpg').convert('RGB')
    r = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    l, t = (im.width - w) // 2, (im.height - h) // 2
    im = im.crop((l, t, l + w, t + h))
    b = io.BytesIO(); im.save(b, 'JPEG', quality=q, optimize=True, progressive=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()


def wrap(text, width):
    return textwrap.wrap(text, width)


def d(sec):
    return f'animation-delay:{sec:.2f}s'


def chips(x, y, items, t):
    out, cx = [], x
    for s in items:
        w = len(s) * 7 + 24
        out.append(f'<rect x="{cx:.0f}" y="{y}" width="{w:.0f}" height="26" rx="13" fill="{t["chip"]}" stroke="{t["line"]}"/>'
                   f'<text x="{cx + w / 2:.0f}" y="{y + 17.5}" text-anchor="middle" class="ct">{esc(s)}</text>')
        cx += w + 8
    return ''.join(out)


def svg_open(w, h, label, t, css=''):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">'
            f'<style>text{{font-family:{FONT};font-variant-numeric:tabular-nums}}'
            f'.ct{{font-size:12px;font-weight:500;fill:{t["sub"]}}}'
            f'.lb{{font-size:13px;font-weight:500;fill:{t["faint"]}}}'
            f'.up{{animation:up 1s {EASE} both}}'
            f'@keyframes up{{from{{opacity:0;transform:translateY(12px)}}to{{opacity:1;transform:none}}}}'
            f'.bi{{animation:bi 1.1s {EASE} both}}'
            f'@keyframes bi{{from{{opacity:0;filter:blur(10px);transform:translateY(6px)}}to{{opacity:1;filter:blur(0);transform:none}}}}'
            f'.hl{{transform-box:fill-box;transform-origin:left;animation:hl 1.4s {EASE} both}}'
            f'@keyframes hl{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}'
            f'{css}</style>')


def card_bg(w, h, t, r=22):
    return f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="{r}" fill="{t["card"]}" stroke="{t["line"]}"/>'


# ---------------------------------------------------------------- header
def header(mode):
    t = THEME[mode]
    H = 196
    LH, SLOT = 74, 40
    css = (f'.name{{font-size:66px;font-weight:700;letter-spacing:-2.6px;fill:{t["text"]}}}'
           f'.s1{{font-size:21px;font-weight:500;letter-spacing:-.3px;fill:{t["text"]}}}'
           f'.s2{{font-size:21px;font-weight:500;letter-spacing:-.3px;fill:{t["faint"]}}}'
           f'.num{{font-size:66px;font-weight:700;letter-spacing:-2px;fill:{t["text"]}}}'
           f'.nl{{font-size:16px;font-weight:500;fill:{t["sub"]}}}')
    keys, body = [], ''
    body += f'<text class="name bi" x="-3" y="80">Swastik Dutt</text>'
    body += f'<text class="s1 bi" style="{d(.18)}" x="0" y="128">Incoming SDE at JPMorgan Chase.</text>'
    body += f'<text class="s2 bi" style="{d(.3)}" x="0" y="158">Interned on its iOS Payments team. Final-year CS at Manipal University Jaipur.</text>'
    # "13+" odometer, right aligned
    glyphs = ['1', '3', '+']
    x0 = W - SLOT * len(glyphs)
    for i, ch in enumerate(glyphs):
        cx = x0 + i * SLOT + SLOT / 2
        if ch.isdigit():
            target = 10 + int(ch)
            keys.append(f'@keyframes o{i}{{from{{transform:translateY(0)}}to{{transform:translateY(-{target * LH}px)}}}}')
            body += f'<clipPath id="o{i}c"><rect x="{cx - SLOT / 2}" y="12" width="{SLOT}" height="{LH}"/></clipPath>'
            body += f'<g clip-path="url(#o{i}c)"><g style="animation:o{i} {1.7 + i * .2:.2f}s {EASE} .35s both">'
            for k in range(20):
                body += f'<text class="num" x="{cx}" y="{80 + k * LH}" text-anchor="middle">{k % 10}</text>'
            body += '</g></g>'
        else:
            body += f'<text class="num bi" style="{d(.9)}" x="{cx}" y="80" text-anchor="middle">{ch}</text>'
    body += f'<text class="nl bi" style="{d(.5)}" x="{W}" y="126" text-anchor="end">hackathon wins</text>'
    body += f'<rect class="hl" style="{d(.4)}" x="0" y="{H - 1}" width="{W}" height="1" fill="{t["line"]}"/>'
    s = svg_open(W, H, 'Swastik Dutt. Incoming SDE at JPMorgan Chase. 13+ hackathon wins.', t, css + ''.join(keys))
    return s + body + '</svg>\n'


# ---------------------------------------------------------------- showreel
def showreel(mode):
    t = THEME[mode]
    H = 500
    fx, fy, fw = 420, 40, 540          # browser frame
    BAR = 32
    sh = round(fw * 10 / 16)           # 16:10 screenshot
    fh = BAR + sh
    n = len(FEATURED)
    slot = 4.5
    T = slot * n
    p = 100 / n
    css = (f'.it{{opacity:0;animation:it {T}s {EASE} infinite}}'
           f'@keyframes it{{0%{{opacity:0;transform:translateY(12px)}}{p*.1:.2f}%{{opacity:1;transform:none}}'
           f'{p*.88:.2f}%{{opacity:1;transform:none}}{p*.98:.2f}%{{opacity:0;transform:translateY(-6px)}}100%{{opacity:0}}}}'
           f'.sw{{opacity:0;animation:sw {T}s linear infinite}}'
           f'@keyframes sw{{0%{{opacity:0}}{p*.06:.2f}%{{opacity:1}}{p*.94:.2f}%{{opacity:1}}{p:.2f}%{{opacity:0}}100%{{opacity:0}}}}'
           f'.shot{{opacity:0;transform-box:fill-box;transform-origin:center;animation:shot {T}s linear infinite}}'
           f'@keyframes shot{{0%{{opacity:0;transform:scale(1.06)}}{p*.12:.2f}%{{opacity:1}}'
           f'{p*.9:.2f}%{{opacity:1}}{p*1.02:.2f}%{{opacity:0;transform:scale(1)}}100%{{opacity:0;transform:scale(1)}}}}'
           f'.bar{{transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:bar {T}s linear infinite}}'
           f'@keyframes bar{{0%{{transform:scaleX(0)}}{p:.2f}%{{transform:scaleX(1)}}{p+.01:.2f}%{{transform:scaleX(0)}}100%{{transform:scaleX(0)}}}}'
           f'.tab{{font-size:13px;font-weight:500;fill:{t["faint"]};animation:tab {T}s linear infinite}}'
           f'@keyframes tab{{0%,{p:.2f}%{{fill:{t["text"]}}}{p+.01:.2f}%,100%{{fill:{t["faint"]}}}}}'
           f'.n{{font-size:44px;font-weight:700;letter-spacing:-1.6px;fill:{t["text"]}}}'
           f'.d{{font-size:16px;fill:{t["sub"]}}}'
           f'.big{{font-size:46px;font-weight:700;letter-spacing:-1.6px;fill:{t["text"]}}}'
           f'.bl{{font-size:13.5px;fill:{t["sub"]}}}'
           f'.url{{font-size:12px;fill:{t["faint"]}}}')
    s = svg_open(W, H, 'Selected work: ' + ', '.join(f['name'] for f in FEATURED), t, css)
    s += card_bg(W, H, t)
    # browser frame
    s += f'<defs><clipPath id="fr"><rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" rx="12"/></clipPath></defs>'
    s += f'<g clip-path="url(#fr)"><rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" fill="{t["shot"]}"/>'
    for i, f in enumerate(FEATURED):
        s += (f'<image class="shot" style="{d(i * slot)}" x="{fx}" y="{fy + BAR}" width="{fw}" height="{sh}" '
              f'preserveAspectRatio="xMidYMid slice" href="{img_uri(f["key"], fw * 2, sh * 2, 70)}"/>')
    s += f'<rect x="{fx}" y="{fy}" width="{fw}" height="{BAR}" fill="{t["chrome"]}"/>'
    s += f'<rect x="{fx}" y="{fy + BAR - 1}" width="{fw}" height="1" fill="{t["line"]}"/></g>'
    for k in range(3):
        s += f'<circle cx="{fx + 18 + k * 16}" cy="{fy + BAR / 2}" r="5" fill="{t["bar"]}"/>'
    uw = 230
    s += f'<rect x="{fx + fw / 2 - uw / 2}" y="{fy + 7}" width="{uw}" height="18" rx="6" fill="{t["chip"]}"/>'
    for i, f in enumerate(FEATURED):
        s += f'<text class="url sw" style="{d(i * slot)}" x="{fx + fw / 2}" y="{fy + 20}" text-anchor="middle">{esc(f["url"])}</text>'
    s += f'<rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" rx="12" fill="none" stroke="{t["line"]}"/>'
    # left column
    s += f'<text class="lb" x="40" y="{fy + 24}">Selected work</text>'
    for i, f in enumerate(FEATURED):
        b = i * slot
        s += f'<text class="n it" style="{d(b)}" x="38" y="{fy + 104}">{esc(f["name"])}</text>'
        g = f'<g class="it" style="{d(b + .08)}">'
        for j, ln in enumerate(wrap(f['desc'], 38)[:3]):
            g += f'<text class="d" x="40" y="{fy + 144 + j * 24}">{esc(ln)}</text>'
        s += g + '</g>'
        g = f'<g class="it" style="{d(b + .16)}"><text class="big" x="38" y="{fy + 272}">{esc(f["stat"])}</text>'
        bx = 40 + len(f['stat']) * 28 + 14
        for j, ln in enumerate(wrap(f['statl'], 30)[:2]):
            g += f'<text class="bl" x="{bx}" y="{fy + 248 + j * 19}">{esc(ln)}</text>'
        s += g + '</g>'
        s += f'<g class="it" style="{d(b + .24)}">{chips(40, fy + fh - 26, f["stack"], t)}</g>'
    # tabs
    bw = (fw - (n - 1) * 12) / n
    by = fy + fh + 30
    for i, f in enumerate(FEATURED):
        x = fx + i * (bw + 12)
        s += f'<rect x="{x:.1f}" y="{by}" width="{bw:.1f}" height="2" rx="1" fill="{t["bar"]}"/>'
        s += f'<rect class="bar" style="{d(i * slot)}" x="{x:.1f}" y="{by}" width="{bw:.1f}" height="2" rx="1" fill="{t["fill"]}"/>'
        s += f'<text class="tab" style="{d(i * slot)}" x="{x:.1f}" y="{by + 26}">{esc(f["name"])}</text>'
        s += f'<text class="lb sw" style="{d(i * slot)}" x="40" y="{by + 26}">0{i + 1} of 0{n}</text>'
    return s + '</svg>\n'


# ---------------------------------------------------------------- list rows (linked one by one)
ROW = 64


def row_css(t):
    return (f'.rn{{font-size:18px;font-weight:600;letter-spacing:-.3px;fill:{t["text"]}}}'
            f'.rk{{font-size:14.5px;fill:{t["sub"]}}}'
            f'.rd{{font-size:14.5px;fill:{t["faint"]}}}'
            f'.ra{{font-size:16px;fill:{t["faint"]}}}')


def project_row(m, mode, i, label=None, last=False):
    t = THEME[mode]
    top = 44 if label else 0
    H = top + ROW + (1 if last else 0)
    s = svg_open(W, H, f'{m["name"]}: {m["desc"]}', t, row_css(t))
    o = i * .1
    if label:
        s += f'<text class="lb up" x="0" y="20">{esc(label)}</text>'
    s += f'<rect class="hl" style="{d(o)}" x="0" y="{top}" width="{W}" height="1" fill="{t["line"]}"/>'
    g = f'<g class="up" style="{d(o + .1)}">'
    g += f'<text class="rn" x="0" y="{top + 39}">{esc(m["name"])}</text>'
    g += f'<text class="rk" x="200" y="{top + 39}">{esc(m["kind"])}</text>'
    g += f'<text class="rd" x="440" y="{top + 39}">{esc(m["desc"])}</text>'
    g += f'<text class="ra" x="{W}" y="{top + 39}" text-anchor="end">↗</text></g>'
    s += g
    if last:
        s += f'<rect class="hl" style="{d(o + .1)}" x="0" y="{H - 1}" width="{W}" height="1" fill="{t["line"]}"/>'
    return s + '</svg>\n'


def experience(mode):
    t = THEME[mode]
    top = 44
    H = top + ROW * len(TIMELINE) + 1
    css = row_css(t) + (f'.yr{{font-size:14.5px;font-weight:500;fill:{t["faint"]}}}'
                        f'.now{{transform-box:fill-box;transform-origin:center;animation:now 2.4s ease-out 1.2s infinite;opacity:0}}'
                        f'@keyframes now{{0%{{transform:scale(1);opacity:.5}}100%{{transform:scale(3);opacity:0}}}}')
    s = svg_open(W, H, 'Experience: ' + '; '.join(f'{a} {b}, {c}' for a, b, c, _ in TIMELINE), t, css)
    s += f'<text class="lb up" x="0" y="20">Experience</text>'
    for i, (yr, co, ro, de) in enumerate(TIMELINE):
        y = top + i * ROW
        o = .1 + i * .1
        s += f'<rect class="hl" style="{d(o)}" x="0" y="{y}" width="{W}" height="1" fill="{t["line"]}"/>'
        g = f'<g class="up" style="{d(o + .1)}">'
        if i == 0:
            g += f'<circle class="now" cx="5" cy="{y + 34}" r="4" fill="{t["fill"]}"/><circle cx="5" cy="{y + 34}" r="4" fill="{t["fill"]}"/>'
            g += f'<text class="yr" x="20" y="{y + 39}">{esc(yr)}</text>'
        else:
            g += f'<text class="yr" x="0" y="{y + 39}">{esc(yr)}</text>'
        g += f'<text class="rn" x="100" y="{y + 39}">{esc(co)}</text>'
        g += f'<text class="rk" x="340" y="{y + 39}">{esc(ro)}</text>'
        g += f'<text class="rd" x="{W}" y="{y + 39}" text-anchor="end">{esc(de)}</text></g>'
        s += g
    s += f'<rect class="hl" style="{d(.6)}" x="0" y="{H - 1}" width="{W}" height="1" fill="{t["line"]}"/>'
    return s + '</svg>\n'


# ---------------------------------------------------------------- arcade: a lap of SketchRacer
TRACK = ('M600,212 C568,160 584,78 660,66 C736,54 770,122 834,104 C898,86 958,98 958,160 '
         'C958,222 900,246 822,238 C760,232 742,196 700,218 C660,240 622,250 600,212 Z')


def arcade(mode):
    t = THEME[mode]
    H = 290
    LAP, START, LH = 6.0, 2.0, 40
    css = (f'.trk{{stroke-dasharray:1000;stroke-dashoffset:1000;animation:draw 1.8s {EASE} .1s forwards}}'
           f'@keyframes draw{{to{{stroke-dashoffset:0}}}}'
           f'.t{{font-size:38px;font-weight:700;letter-spacing:-1.4px;fill:{t["text"]}}}'
           f'.d{{font-size:16px;fill:{t["sub"]}}}'
           f'.clk{{font-family:{MONO};font-size:32px;font-weight:600;fill:{t["text"]}}}'
           f'.cta{{font-size:14px;font-weight:600;fill:{t["text"]}}}')
    cols = [('s', LAP, 6), ('t', 1.0, 10), ('h', .1, 10)]
    for c, per, k in cols:
        css += f'.r{c}{{animation:r{c} {per}s steps({k}) {START}s infinite}}@keyframes r{c}{{to{{transform:translateY(-{k * LH}px)}}}}'
    css += f'.lp{{animation:lp {LAP * 3}s steps(3) {START}s infinite}}@keyframes lp{{to{{transform:translateY(-{3 * LH}px)}}}}'
    s = svg_open(W, H, 'SketchRacer: draw a track and race it', t, css)
    s += card_bg(W, H, t)
    s += f'<text class="lb up" x="40" y="64">Play</text>'
    s += f'<text class="t up" style="{d(.08)}" x="38" y="110">Draw a track. Race it.</text>'
    g = f'<g class="up" style="{d(.16)}">'
    for j, ln in enumerate(wrap('Freehand a loop in SketchRacer and it becomes a real track with checkpoints and lap timing.', 48)):
        g += f'<text class="d" x="40" y="{142 + j * 23}">{esc(ln)}</text>'
    s += g + '</g>'
    cx, cy = 40, 238
    s += f'<g class="up" style="{d(.28)}"><text class="lb" x="{cx}" y="{cy - 38}">Lap time</text>'
    s += f'<text class="clk" x="{cx}" y="{cy}">0:0</text><text class="clk" x="{cx + 77}" y="{cy}">.</text>'
    xs = {'s': cx + 58, 't': cx + 96, 'h': cx + 116}
    for c, per, k in cols:
        s += f'<clipPath id="q{c}"><rect x="{xs[c] - 1}" y="{cy - 30}" width="21" height="{LH}"/></clipPath>'
        s += f'<g clip-path="url(#q{c})"><g class="r{c}">'
        for v in range(k + 1):
            s += f'<text class="clk" x="{xs[c]}" y="{cy + v * LH}">{v % k}</text>'
        s += '</g></g>'
    lx = cx + 190
    s += f'<text class="lb" x="{lx}" y="{cy - 38}">Lap</text>'
    s += f'<clipPath id="ql"><rect x="{lx - 1}" y="{cy - 30}" width="80" height="{LH}"/></clipPath><g clip-path="url(#ql)"><g class="lp">'
    for v in range(4):
        s += f'<text class="clk" x="{lx}" y="{cy + v * LH}">{v % 3 + 1}/3</text>'
    s += '</g></g></g>'
    s += f'<text class="cta up" style="{d(.36)}" x="{lx + 130}" y="{cy}">sketchracer.com ↗</text>'
    # track: tarmac, centre line
    s += f'<path class="trk" pathLength="1000" d="{TRACK}" fill="none" stroke="{t["bar"]}" stroke-width="24" stroke-linejoin="round"/>'
    s += f'<path class="trk" pathLength="1000" d="{TRACK}" fill="none" stroke="{t["faint"]}" stroke-width="1.2" opacity=".6" style="{d(.25)}"/>'
    vx, vy = -32, -52
    L = math.hypot(vx, vy); px_, py_ = -vy / L * 12, vx / L * 12
    seg = f'x1="{600 - px_:.1f}" y1="{212 - py_:.1f}" x2="{600 + px_:.1f}" y2="{212 + py_:.1f}"'
    s += f'<line {seg} stroke="{t["shot"]}" stroke-width="5"/>'
    s += f'<line {seg} stroke="{t["fill"]}" stroke-width="5" stroke-dasharray="3 3"/>'
    s += (f'<path pathLength="1000" d="{TRACK}" fill="none" stroke="{t["fill"]}" stroke-width="3" stroke-linecap="round" '
          f'stroke-dasharray="80 920" stroke-dashoffset="80" opacity="0">'
          f'<set attributeName="opacity" to=".5" begin="{START}s"/>'
          f'<animate attributeName="stroke-dashoffset" from="80" to="-920" dur="{LAP}s" begin="{START}s" repeatCount="indefinite"/></path>')
    s += (f'<g opacity="0"><set attributeName="opacity" to="1" begin="{START}s"/>'
          f'<animateMotion dur="{LAP}s" begin="{START}s" repeatCount="indefinite" rotate="auto" path="{TRACK}"/>'
          f'<rect x="-9" y="-5" width="18" height="10" rx="3" fill="{t["fill"]}"/>'
          f'<rect x="2" y="-3.5" width="4" height="7" rx="1" fill="{t["shot"]}" opacity=".7"/></g>')
    return s + '</svg>\n'


for f in os.listdir(OUT):
    os.remove(f'{OUT}/{f}')
for mode in ('dark', 'light'):
    open(f'{OUT}/header-{mode}.svg', 'w').write(header(mode))
    open(f'{OUT}/showreel-{mode}.svg', 'w').write(showreel(mode))
    open(f'{OUT}/experience-{mode}.svg', 'w').write(experience(mode))
    open(f'{OUT}/arcade-{mode}.svg', 'w').write(arcade(mode))
    for i, m in enumerate(MORE):
        open(f'{OUT}/{m["slug"]}-{mode}.svg', 'w').write(
            project_row(m, mode, i, label='More projects' if i == 0 else None, last=i == len(MORE) - 1))

for fn in sorted(os.listdir(OUT)):
    print(f'{fn:28} {os.path.getsize(f"{OUT}/{fn}") // 1024} KB')
