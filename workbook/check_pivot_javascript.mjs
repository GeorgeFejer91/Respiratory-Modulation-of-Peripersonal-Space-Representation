import { readFileSync } from 'node:fs';
import { pivot, snapshotFrame, csvText } from './pivot_assets/pivot-engine.mjs';

const payload = JSON.parse(readFileSync(0, 'utf8'));
const results = payload.cases.map(test => {
  try { return pivot(payload.frames[test.frame], test.settings); }
  catch (error) { return { error: error.message }; }
});
process.stdout.write(JSON.stringify({ results, snapshot: snapshotFrame(payload.snapshots[0]),
  csv: csvText({ columns: ['a', 'b'], rows: [['=literal', 'quote"comma,']] }) }));
