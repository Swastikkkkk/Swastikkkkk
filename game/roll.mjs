// Called by the workflow when someone opens a "snl|roll" issue.
// PLAYER comes from the issue author. Prints GitHub step outputs.
import { loadState, saveState, roll, renderAll, PROJECTS, LAST } from './engine.mjs';

const player = (process.env.PLAYER || 'someone').replace(/[^A-Za-z0-9-]/g, '').slice(0, 39) || 'someone';
const state = loadState();
const m = roll(state, player);
saveState(state);
renderAll(state);

const p = PROJECTS[m.to];
let msg = `You rolled a **${m.dice}**. `;
if (m.won) msg += `Straight to square 36. You finished the board, nice.`;
else if (m.event?.type === 'ladder') msg += `Square ${m.land} has a ladder (${m.event.label}), up to ${m.to}.`;
else if (m.event?.type === 'snake') msg += `Square ${m.land} is a snake (${m.event.label}), down to ${m.to}.`;
else msg += `${m.from} → ${m.to}${m.bounced ? ', bounced back off 36' : ''}.`;
if (p) msg += `\n\nYou landed on **${p.name}**: ${p.desc}${p.live ? `\n\nTry it: ${p.live}` : ''}`;
msg += `\n\nThe board on https://github.com/Swastikkkkk updates in a few seconds.`;

console.log(`roll=${m.dice}`);
console.log(`msg<<SNL_EOF\n${msg}\nSNL_EOF`);
