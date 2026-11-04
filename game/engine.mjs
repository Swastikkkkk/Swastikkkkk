// Snakes & Ladders board for the profile README.
// Everything here is pure: state in, SVG/markdown out. roll.mjs does the IO.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export const REPO = 'Swastikkkkk/Swastikkkkk';
export const ROLL_URL =
  `https://github.com/${REPO}/issues/new?title=snl%7Croll&body=` +
  encodeURIComponent('Just press "Create". A GitHub Action rolls the dice, moves the token and closes this issue in about 30 seconds.');

const N = 6;                 // 6 x 6 board
export const LAST = N * N;   // 36
const CELL = 124, PAD = 28, TOP = 150;
const W = PAD * 2 + N * CELL;
const H = TOP + N * CELL + 70;

export const PROJECTS = {
  4:  { name: 'brag-ext',      tag: 'Chrome extension', desc: 'Turns any GitHub repo into a short promo video. Voices run locally in the browser.', code: 'https://github.com/Swastikkkkk/brag-ext' },
  9:  { name: 'agentdrift',    tag: 'Python CLI',       desc: 'Finds rules that clash across AGENTS.md, CLAUDE.md and .cursorrules, then merges them into one file.', code: 'https://github.com/Swastikkkkk/agentdrift', live: 'https://agentdrift.vercel.app' },
  13: { name: 'Guardian',      tag: 'FastAPI',          desc: 'Safe-route engine that scores streets from OSM, weather and camera events.', code: 'https://github.com/Swastikkkkk/guardian-backend' },
  17: { name: 'DisasterAR',    tag: 'Swift, ARKit',     desc: 'Indoor evacuation in AR that works fully offline, routing around hazards to the nearest safe exit.', code: 'https://github.com/Swastikkkkk/disasterevac' },
  20: { name: 'District Mesh', tag: 'Swift',            desc: 'Offline mesh for iPhone. Messages, live location, SOS and calls hop between phones with no internet.', code: 'https://github.com/Swastikkkkk/District_Mesh' },
  24: { name: 'AmExpert',      tag: 'AI agent',         desc: 'Agent that resolves card-servicing requests over voice, WhatsApp, SMS and email, with a deterministic policy engine.', code: 'https://github.com/Swastikkkkk/amexpert', live: 'https://amexpert.vercel.app' },
  27: { name: 'Lerno.ai',      tag: 'Codeclash winner', desc: 'Type a concept, get an animated explainer. Claude writes the storyboard and Manim code. Won Google Codeclash 2.0.', code: 'https://github.com/Swastikkkkk/lerno', live: 'https://lerno-peach.vercel.app' },
  30: { name: 'ChatSnitch',    tag: 'Chrome extension', desc: 'Shows which of your Chrome extensions can read your ChatGPT, Claude and Gemini chats.', code: 'https://github.com/Swastikkkkk/chatsnitch', live: 'https://chatsnitch.vercel.app' },
  33: { name: 'JalNetra',      tag: 'AWS',              desc: 'Flood early warning. Watches 681 river points and calls the village head in Hindi once a person approves.', code: 'https://github.com/Swastikkkkk/jalnetra', live: 'https://d1oi8xa605dsj6.cloudfront.net' },
  35: { name: 'PrepNinja',     tag: 'AI interviews',    desc: 'Proctored AI mock interviews, coding rounds with a sandboxed runner, and an ATS resume check.', code: 'https://github.com/Swastikkkkk/PrepNinja', live: 'https://prepninja-tawny.vercel.app' },
  36: { name: 'SketchRacer',   tag: 'Finish line',      desc: 'Open-world driving game in the browser. Draw any track and race it, or drive real F1 circuits.', code: 'https://github.com/Swastikkkkk/swastikk-drive', live: 'https://www.sketchracer.com' },
};
export const LADDERS = {
  3:  { to: 14, label: 'KPMG internship' },
  8:  { to: 19, label: 'SIH 2025 win' },
  21: { to: 32, label: 'JPMorgan Chase' },
};
export const SNAKES = {
  16: { to: 6,  label: 'merge conflict' },
  29: { to: 18, label: 'works locally' },
  34: { to: 23, label: 'npm install' },
};

export const freshState = () => ({
  position: 1, rolls: 0, games: 0, gameRolls: 0, resetNext: false,
  last: null, history: [], players: {}, winners: [],
});

export function loadState() {
  const p = path.join(ROOT, 'game', 'state.json');
  return fs.existsSync(p) ? JSON.parse(fs.readFileSync(p, 'utf8')) : freshState();
}
export function saveState(s) {
  fs.writeFileSync(path.join(ROOT, 'game', 'state.json'), JSON.stringify(s, null, 2) + '\n');
}

export function roll(state, user, rnd = Math.random) {
  if (state.resetNext) { state.position = 1; state.resetNext = false; state.gameRolls = 0; }
  const dice = 1 + Math.floor(rnd() * 6);
  const from = state.position;
  let land = from + dice, bounced = false;
  if (land > LAST) { land = LAST - (land - LAST); bounced = true; }
  let to = land, event = null;
  if (LADDERS[land]) { to = LADDERS[land].to; event = { type: 'ladder', label: LADDERS[land].label }; }
  else if (SNAKES[land]) { to = SNAKES[land].to; event = { type: 'snake', label: SNAKES[land].label }; }
  const move = { user, dice, from, land, to, event, bounced, at: new Date().toISOString() };
  state.rolls += 1;
  state.gameRolls += 1;
  state.position = to;
  state.last = move;
  state.history = [move, ...state.history].slice(0, 6);
  state.players[user] = (state.players[user] || 0) + 1;
  move.won = to === LAST;
  if (move.won) {
    state.games += 1;
    state.winners = [{ user, at: move.at, rolls: state.gameRolls }, ...state.winners].slice(0, 5);
    state.resetNext = true;
  }
  return move;
}

// ---------- geometry ----------
function cell(n) {
  const i = n - 1, row = Math.floor(i / N), c = i % N;
  const col = row % 2 === 0 ? c : N - 1 - c;
  const x = PAD + col * CELL, y = TOP + (N - 1 - row) * CELL;
  return { x, y, cx: x + CELL / 2, cy: y + CELL / 2 };
}
const esc = (s) => String(s).replace(/[&<>"']/g, (ch) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]));
const f = (n) => Math.round(n * 10) / 10;

const THEMES = {
  dark: {
    bg: '#0a0a0a', cellA: '#101010', cellB: '#141414', line: '#232323', num: '#6b6b6b',
    text: '#fafafa', sub: '#9a9a9a', proj: '#1b1b1b', projLine: '#383838',
    ladder: '#e5e5e5', snake: '#bf5af2', snakeStripe: '#e3b8fb', token: '#fafafa', tokenInner: '#0a0a0a',
    pip: '#0a0a0a', die: '#fafafa', chip: '#1b1b1b', chipLine: '#333',
  },
  light: {
    bg: '#ffffff', cellA: '#fafafa', cellB: '#f4f4f5', line: '#e4e4e7', num: '#a1a1aa',
    text: '#0a0a0a', sub: '#52525b', proj: '#ffffff', projLine: '#d4d4d8',
    ladder: '#3f3f46', snake: '#a64fd6', snakeStripe: '#e7c6f7', token: '#0a0a0a', tokenInner: '#ffffff',
    pip: '#fafafa', die: '#0a0a0a', chip: '#f4f4f5', chipLine: '#e4e4e7',
  },
};

function ladderSvg(a, b, t, label) {
  const p = cell(a), q = cell(b);
  const dx = q.cx - p.cx, dy = q.cy - p.cy, len = Math.hypot(dx, dy);
  const ux = dx / len, uy = dy / len, nx = -uy * 11, ny = ux * 11;
  let s = `<g class="ladder">`;
  s += `<line x1="${f(p.cx + nx)}" y1="${f(p.cy + ny)}" x2="${f(q.cx + nx)}" y2="${f(q.cy + ny)}"/>`;
  s += `<line x1="${f(p.cx - nx)}" y1="${f(p.cy - ny)}" x2="${f(q.cx - nx)}" y2="${f(q.cy - ny)}"/>`;
  for (let d = 18; d < len - 10; d += 24) {
    const x = p.cx + ux * d, y = p.cy + uy * d;
    s += `<line class="rung" x1="${f(x + nx)}" y1="${f(y + ny)}" x2="${f(x - nx)}" y2="${f(y - ny)}"/>`;
  }
  return s + `</g>`;
}

function snakeSvg(a, b, t, seed) {
  const p = cell(a), q = cell(b);                  // a = head (higher square), b = tail
  const dx = q.cx - p.cx, dy = q.cy - p.cy, len = Math.hypot(dx, dy);
  const nx = -dy / len, ny = dx / len;
  const waves = Math.max(1.5, len / 150), amp = 20;
  const pts = [];
  for (let i = 0; i <= 60; i++) {
    const k = i / 60, w = Math.sin(k * Math.PI * 2 * waves + seed) * amp * Math.sin(Math.PI * Math.min(1, k * 1.15));
    pts.push([p.cx + dx * k + nx * w, p.cy + dy * k + ny * w]);
  }
  const d = 'M' + pts.map(([x, y]) => `${f(x)} ${f(y)}`).join(' L');
  const [hx, hy] = pts[0], [ax, ay] = pts[3];
  const hl = Math.hypot(ax - hx, ay - hy), ex = (ax - hx) / hl, ey = (ay - hy) / hl;
  return `<g class="snake"><path class="body" d="${d}"/><path class="stripe" d="${d}"/>` +
    `<circle class="head" cx="${f(hx)}" cy="${f(hy)}" r="11"/>` +
    `<circle class="eye" cx="${f(hx - ey * 4 - ex * 2)}" cy="${f(hy + ex * 4 - ey * 2)}" r="2"/>` +
    `<circle class="eye" cx="${f(hx + ey * 4 - ex * 2)}" cy="${f(hy - ex * 4 - ey * 2)}" r="2"/></g>`;
}

function dieSvg(x, y, size, value, t) {
  const r = size / 2, o = size * 0.27;
  const at = { 1: [[0, 0]], 2: [[-1, -1], [1, 1]], 3: [[-1, -1], [0, 0], [1, 1]], 4: [[-1, -1], [1, -1], [-1, 1], [1, 1]],
    5: [[-1, -1], [1, -1], [0, 0], [-1, 1], [1, 1]], 6: [[-1, -1], [1, -1], [-1, 0], [1, 0], [-1, 1], [1, 1]] }[value] || [];
  let s = `<g class="die" transform="translate(${x + r} ${y + r})"><g class="spin"><rect x="${-r}" y="${-r}" width="${size}" height="${size}" rx="${size * 0.22}" fill="${t.die}"/>`;
  for (const [i, j] of at) s += `<circle cx="${f(i * o)}" cy="${f(j * o)}" r="${f(size * 0.085)}" fill="${t.pip}"/>`;
  return s + `</g></g>`;
}

export function renderSvg(state, theme) {
  const t = THEMES[theme];
  const last = state.last;
  const cur = state.position;
  let s = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" role="img" aria-label="Snakes and Ladders board. The token is on square ${cur}.">`;
  s += `<style>
  text{font-family:-apple-system,BlinkMacSystemFont,'SF Pro Text','Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif}
  .num{font-family:'SF Mono',ui-monospace,Menlo,Consolas,monospace;font-size:11px;fill:${t.num}}
  .pname{font-size:14.5px;font-weight:650;letter-spacing:-.2px;fill:${t.text};paint-order:stroke;stroke:${t.proj};stroke-width:5px;stroke-linejoin:round}
  .ptag{font-size:10.5px;fill:${t.sub};paint-order:stroke;stroke:${t.proj};stroke-width:4px;stroke-linejoin:round}
  .ev{font-size:10.5px;font-weight:600;paint-order:stroke;stroke-width:4px;stroke-linejoin:round}
  .ladder line{stroke:${t.ladder};stroke-width:3.5;stroke-linecap:round}
  .ladder .rung{stroke-width:3}
  .snake .body{fill:none;stroke:${t.snake};stroke-width:12;stroke-linecap:round;stroke-linejoin:round}
  .snake .stripe{fill:none;stroke:${t.snakeStripe};stroke-width:3;stroke-dasharray:2 9;stroke-linecap:round;opacity:.8}
  .snake .head{fill:${t.snake}} .snake .eye{fill:${t.bg}}
  .h1{font-size:27px;font-weight:700;letter-spacing:-.7px;fill:${t.text}}
  .h2{font-size:13.5px;fill:${t.sub}}
  .s1{font-size:15px;font-weight:600;fill:${t.text};letter-spacing:-.2px}
  .s2{font-size:12.5px;fill:${t.sub}}
  .foot{font-size:11.5px;fill:${t.sub}}
  .spin{animation:spin .9s cubic-bezier(.2,.8,.2,1) both}
  @keyframes spin{from{transform:rotate(-200deg) scale(.6);opacity:0}to{transform:rotate(0) scale(1);opacity:1}}
  .ring{fill:none;stroke:${t.token};stroke-width:2;transform-box:fill-box;transform-origin:center;animation:ping 2.2s ease-out 3s infinite}
  @keyframes ping{0%{transform:scale(1);opacity:.7}100%{transform:scale(2.4);opacity:0}}
  </style>`;
  s += `<rect width="${W}" height="${H}" rx="18" fill="${t.bg}"/>`;

  // header
  s += `<text class="h1" x="${PAD}" y="58">Snakes &amp; Ladders</text>`;
  s += `<text class="h2" x="${PAD}" y="84">Every square is something I built. Ladders are wins, snakes are dev pain.</text>`;
  s += `<text class="h2" x="${PAD}" y="104">Anyone can roll. Move the token, see where you land.</text>`;
  const dieX = W - PAD - 64;
  if (last) {
    s += dieSvg(dieX, 40, 64, last.dice, t);
    const line1 = `@${last.user} rolled a ${last.dice}`;
    let line2 = last.event ? `${last.land} → ${last.to}, ${last.event.type}: ${last.event.label}` : `${last.from} → ${last.to}${last.bounced ? ', bounced back' : ''}`;
    if (last.won) line2 = `${last.from} → 36, reached the finish`;
    s += `<text class="s1" x="${dieX - 18}" y="64" text-anchor="end">${esc(line1)}</text>`;
    s += `<text class="s2" x="${dieX - 18}" y="86" text-anchor="end">${esc(line2)}</text>`;
  } else {
    s += `<g transform="translate(${dieX} 40)"><rect width="64" height="64" rx="14" fill="none" stroke="${t.projLine}" stroke-width="2" stroke-dasharray="5 5"/></g>`;
    s += `<text class="s1" x="${dieX - 18}" y="64" text-anchor="end">No rolls yet</text>`;
    s += `<text class="s2" x="${dieX - 18}" y="86" text-anchor="end">Be the first</text>`;
  }

  // cells
  for (let n = 1; n <= LAST; n++) {
    const { x, y, cx, cy } = cell(n);
    const p = PROJECTS[n];
    const fill = p ? t.proj : ((Math.floor((n - 1) / N) + n) % 2 ? t.cellA : t.cellB);
    const stroke = n === cur ? t.token : p ? t.projLine : t.line;
    s += `<rect x="${x + 2}" y="${y + 2}" width="${CELL - 4}" height="${CELL - 4}" rx="10" fill="${fill}" stroke="${stroke}" stroke-width="${n === cur ? 2 : 1}"/>`;
    s += `<text class="num" x="${x + 12}" y="${y + 22}">${String(n).padStart(2, '0')}</text>`;
  }
  // ladders and snakes
  for (const [a, v] of Object.entries(LADDERS)) s += ladderSvg(+a, v.to, t);
  let seed = 0;
  for (const [a, v] of Object.entries(SNAKES)) s += snakeSvg(+a, v.to, t, (seed += 1.3));
  // labels on top
  for (let n = 1; n <= LAST; n++) {
    const { x, y, cx, cy } = cell(n);
    const p = PROJECTS[n];
    if (p) {
      s += `<text class="pname" x="${cx}" y="${cy + 6}" text-anchor="middle">${esc(p.name)}</text>`;
      s += `<text class="ptag" x="${cx}" y="${cy + 24}" text-anchor="middle">${esc(p.tag)}</text>`;
    }
    if (n === 1) s += `<text class="pname" x="${cx}" y="${cy + 6}" text-anchor="middle" style="stroke:${t.cellB}">Start</text>`;
    if (LADDERS[n]) s += `<text class="ev" x="${cx}" y="${y + CELL - 14}" text-anchor="middle" fill="${t.text}" stroke="${t.bg}">↑ ${esc(LADDERS[n].label)}</text>`;
    if (SNAKES[n]) s += `<text class="ev" x="${x + CELL - 12}" y="${y + 22}" text-anchor="end" fill="${t.snake}" stroke="${t.bg}">↓ ${esc(SNAKES[n].label)}</text>`;
  }

  // token, animated along from -> land -> to
  const to = cell(cur);
  if (last) {
    const a = cell(last.from), l = cell(last.land);
    const k = (c) => `translate(${f(c.cx)}px,${f(c.cy - 30)}px)`;
    s += `<style>.tok{animation:mv 2.2s cubic-bezier(.45,0,.2,1) .7s both}
    @keyframes mv{0%{transform:${k(a)}}${last.land !== last.to ? `45%{transform:${k(l)}}62%{transform:${k(l)}}` : ''}100%{transform:${k(to)}}}</style>`;
  } else {
    s += `<style>.tok{transform:translate(${f(to.cx)}px,${f(to.cy - 30)}px)}</style>`;
  }
  s += `<g class="tok"><circle class="ring" r="13"/><circle r="13" fill="${t.token}"/><circle r="5" fill="${t.tokenInner}"/></g>`;

  // footer
  const fy = TOP + N * CELL + 40;
  s += `<text class="foot" x="${PAD}" y="${fy}">${state.rolls} roll${state.rolls === 1 ? '' : 's'} · ${Object.keys(state.players).length} player${Object.keys(state.players).length === 1 ? '' : 's'} · ${state.games} game${state.games === 1 ? '' : 's'} finished</text>`;
  s += `<text class="foot" x="${W - PAD}" y="${fy}" text-anchor="end">Click the board to roll</text>`;
  return s + `</svg>\n`;
}

// ---------- README ----------
function landingMd(state) {
  const n = state.position, p = PROJECTS[n];
  const links = (q) => [q.live && `[Live](${q.live})`, `[Code](${q.code})`].filter(Boolean).join(' · ');
  if (p) {
    const head = n === LAST ? `**Square 36, the finish: [${p.name}](${p.live || p.code}).**` : `**Square ${n}: [${p.name}](${p.live || p.code}).**`;
    return `${head} ${p.desc} ${links(p)}`;
  }
  if (n === 1) return `**The token is on Start.** First project, brag-ext, is a roll of 3 away.`;
  const next = Object.keys(PROJECTS).map(Number).find((k) => k > n);
  const q = PROJECTS[next];
  return `**Square ${n}.** Nothing shipped here yet. Next up: [${q.name}](${q.live || q.code}) on square ${next}, a roll of ${next - n <= 6 ? next - n : 'a few'} away.`;
}

export function gameMd(state) {
  const pic = `<picture><source media="(prefers-color-scheme: dark)" srcset="game/board-dark.svg"><img src="game/board-light.svg" width="100%" alt="Snakes and Ladders board, token on square ${state.position}"></picture>`;
  let md = `<a href="${ROLL_URL}">${pic}</a>\n\n`;
  md += `<p align="center"><a href="${ROLL_URL}"><b>Roll the dice</b></a> &nbsp;·&nbsp; <sub>opens a ready-made issue, hit Create and a bot moves the token</sub></p>\n\n`;
  md += landingMd(state) + `\n\n`;
  if (state.history.length) {
    md += `<details><summary>Last ${state.history.length} moves</summary>\n\n| Player | Roll | Move |\n| --- | --- | --- |\n`;
    for (const m of state.history) {
      const what = m.won ? `${m.from} → 36, finished` : m.event ? `${m.from} → ${m.land}, ${m.event.type} to ${m.to}` : `${m.from} → ${m.to}${m.bounced ? ' (bounced)' : ''}`;
      md += `| [@${esc(m.user)}](https://github.com/${esc(m.user)}) | ${m.dice} | ${what} |\n`;
    }
    const top = Object.entries(state.players).sort((a, b) => b[1] - a[1]).slice(0, 5);
    md += `\n**Most rolls:** ${top.map(([u, c]) => `[@${esc(u)}](https://github.com/${esc(u)}) ${c}`).join(' · ')}\n`;
    if (state.winners.length) md += `\n**Brought it home:** ${state.winners.map((w) => `[@${esc(w.user)}](https://github.com/${esc(w.user)}) in ${w.rolls} rolls`).join(' · ')}\n`;
    md += `\n</details>\n`;
  }
  return md;
}

export function updateReadme(state) {
  const p = path.join(ROOT, 'README.md');
  const s = fs.readFileSync(p, 'utf8');
  const out = s.replace(/<!--GAME:START-->[\s\S]*?<!--GAME:END-->/, `<!--GAME:START-->\n${gameMd(state)}<!--GAME:END-->`);
  fs.writeFileSync(p, out);
}

export function renderAll(state) {
  fs.writeFileSync(path.join(ROOT, 'game', 'board-dark.svg'), renderSvg(state, 'dark'));
  fs.writeFileSync(path.join(ROOT, 'game', 'board-light.svg'), renderSvg(state, 'light'));
  updateReadme(state);
}
