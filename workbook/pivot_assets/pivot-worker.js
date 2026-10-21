import { pivot, snapshotFrame, selectRecords, compareTuple } from './pivot-engine.mjs';

const frames = new Map();
async function load(url) {
  if (frames.has(url)) return frames.get(url);
  const response = await fetch(url, { signal: AbortSignal.timeout(30000) });
  if (!response.ok) throw new Error(`Could not load the selected data (${response.status}).`);
  const payload = await response.json();
  const frame = payload.numeric ? payload : snapshotFrame(payload);
  if (frames.size >= 2) frames.delete(frames.keys().next().value);
  frames.set(url, frame);
  return frame;
}

self.onmessage = async ({ data: request }) => {
  try {
    const frame = await load(request.url);
    if (request.action === 'metadata') {
      self.postMessage({ id: request.id, columns: frame.columns, numeric: frame.numeric });
    } else if (request.action === 'choices') {
      const index = frame.columns.indexOf(request.field);
      if (index < 0) throw new Error('This field is not in the selected source.');
      const records = selectRecords(frame, { ...request.settings, filtersEnabled: false });
      const choices = [...new Map(records.map(row => [JSON.stringify(row[index]), row[index]])).values()];
      choices.sort((a, b) => compareTuple([a ?? '(missing)'], [b ?? '(missing)']));
      self.postMessage({ id: request.id, choices });
    } else {
      self.postMessage({ id: request.id, result: pivot(frame, request.settings), columns: frame.columns, numeric: frame.numeric });
    }
  } catch (error) {
    self.postMessage({ id: request.id, error: error.message });
  }
};
