// Redraw the board and README from state.json without rolling.
import { loadState, saveState, renderAll } from './engine.mjs';
const s = loadState();
saveState(s);
renderAll(s);
