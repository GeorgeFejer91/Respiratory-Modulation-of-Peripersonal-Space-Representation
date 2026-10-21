import { aggregations, csvText } from './pivot-engine.mjs';
import { openChoices, renderChoices, showDetail } from './pivot-choices.js';

const byId = id => document.getElementById(id);
const worker = new Worker(new URL('./pivot-worker.js', import.meta.url), { type: 'module' });
const pending = new Map();
let requestId = 0, generation = 0, sourceGeneration = 0, result, resultSettings, fields = [], numeric = [], catalog;
let rowPage = 0, columnPage = 0, rowCapacity = 8, columnCapacity = 4;
let source = 'means', saved = null, fullMeans = false, fullMeansRequest;
let workerFailure;
const settings = { rows: ['distance_cm'], columns: ['condition', 'phase'], values: ['corrected_rt_ms'], aggregation: 'Mean', totals: true, cohort: 'Primary behavioural cohort', filtersEnabled: false, filters: {} };
const names = { means: 'Participant-distance means', trials: 'All trial records', participants: 'Participants and questionnaires', saved: 'Saved analysis table' };
const sourceURL = () => source === 'saved' ? `app/public/snapshots/${saved.file}` : `data/${source === 'means' && !fullMeans ? 'means-preview' : source}.json`;

worker.onmessage = ({ data: reply }) => {
  const handlers = pending.get(reply.id);
  if (!handlers) return;
  pending.delete(reply.id);
  reply.error ? handlers.reject(new Error(reply.error)) : handlers.resolve(reply);
};
worker.onerror = () => {
  workerFailure = new Error('The pivot worker could not start. Reload the page or open the marimo notebook.');
  for (const handlers of pending.values()) handlers.reject(workerFailure);
  pending.clear();
  reportError(workerFailure);
};
function request(action, extra = {}) {
  if (workerFailure) return Promise.reject(workerFailure);
  return new Promise((resolve, reject) => {
    const id = ++requestId;
    pending.set(id, { resolve, reject });
    worker.postMessage({ id, action, url: sourceURL(), settings, ...extra });
  });
}
async function fullFields() {
  if (source !== 'means' || fullMeans) return;
  if (!fullMeansRequest) fullMeansRequest = request('metadata', { url: 'data/means.json' }).then(reply => {
    if (source === 'means') {
      fields = reply.columns;
      numeric = reply.numeric;
      fullMeans = true;
    }
  }).finally(() => { fullMeansRequest = null; });
  return fullMeansRequest;
}
function reportError(error) {
  result = null;
  byId('pivot-table').tHead.replaceChildren();
  byId('pivot-table').tBodies[0].replaceChildren();
  byId('table-caption').textContent = 'Pivot unavailable';
  byId('summary').textContent = 'No pivot calculated';
  byId('row-page').textContent = byId('col-page').textContent = '';
  for (const id of ['row-prev', 'row-next', 'col-prev', 'col-next']) byId(id).disabled = true;
  delete document.documentElement.dataset.recordCount;
  document.body.dataset.flow = 'true';
  byId('error').textContent = error.message;
  byId('error').hidden = false;
  byId('table-region').setAttribute('aria-busy', 'false');
  byId('export').disabled = true;
  byId('status').textContent = 'Adjust Pivot settings and apply again.';
}
async function update() {
  const revision = ++generation;
  const submitted = structuredClone(settings);
  byId('table-region').setAttribute('aria-busy', 'true');
  byId('error').hidden = true;
  byId('export').disabled = true;
  try {
    const reply = await request('pivot', { settings: submitted });
    if (revision !== generation) return;
    result = reply.result;
    resultSettings = submitted;
    if (!(source === 'means' && fullMeans && reply.columns.length < fields.length)) {
      fields = reply.columns;
      numeric = reply.numeric;
    }
    rowPage = columnPage = 0;
    byId('table-region').setAttribute('aria-busy', 'false');
    byId('export').disabled = false;
    byId('summary').textContent = `${result.count.toLocaleString()} source records · ${submitted.filtersEnabled ? 'Filters on' : 'Filters off'}`;
    const measure = submitted.aggregation === 'Row count' ? 'Records' : submitted.values.join(', ');
    byId('table-caption').textContent = `${submitted.aggregation} · ${measure === 'corrected_rt_ms' ? 'Corrected RT (ms)' : measure}`;
    byId('status').textContent = source === 'saved' ? saved.source : `${names[source]} · ${submitted.cohort}`;
    document.documentElement.dataset.recordCount = String(result.count);
    renderTable();
    requestAnimationFrame(() => {
      if (!document.documentElement.dataset.readyMs) document.documentElement.dataset.readyMs = performance.now().toFixed(1);
      import('./pivot-layout.js').then(module => module.scheduleLayout()).catch(error => console.warn('Text geometry unavailable; readable browser layout remains active.', error));
    });
  } catch (error) { if (revision === generation) reportError(error); }
}

function cellText(value) {
  if (value === null) return '—';
  if (typeof value === 'number') return Number.isFinite(value) ? value.toLocaleString(undefined, { maximumSignificantDigits: 6 }) : String(value);
  return String(value);
}
function tableCell(tag, label, full, fallback = 'Read full value') {
  const cell = document.createElement(tag);
  const text = String(label);
  const button = document.createElement('button');
  button.type = 'button';
  button.textContent = text.length > 36 ? fallback : text;
  button.dataset.fitLabel = '';
  button.setAttribute('aria-label', String(full));
  button.onclick = () => showDetail(full);
  cell.append(button);
  return cell;
}
export function renderTable() {
  if (!result) return;
  const table = byId('pivot-table'), region = byId('table-region');
  const font = parseFloat(getComputedStyle(table).fontSize);
  const width = region.clientWidth;
  document.body.dataset.compact = String(width / font < 18);
  columnCapacity = Math.max(1, Math.floor((width - Math.max(90, font * 6)) / Math.max(125, font * 8)));
  columnPage = Math.min(columnPage, Math.max(0, Math.ceil((result.columns.length - result.axisCount) / columnCapacity) - 1));
  const start = result.axisCount + columnPage * columnCapacity;
  const displayed = result.columns.slice(start, start + columnCapacity);
  const header = document.createElement('tr');
  const rowTitle = resultSettings.rows.join(' / ') || 'All records';
  header.append(tableCell('th', rowTitle === 'distance_cm' ? 'Distance (cm)' : rowTitle, rowTitle));
  displayed.forEach(label => {
    const shorter = (resultSettings.values.length === 1 || resultSettings.aggregation === 'Row count') && resultSettings.columns.length ? label.split(' · ').slice(1).join(' · ') : label;
    header.append(tableCell('th', shorter, label));
  });
  table.tHead.replaceChildren(header);
  const captionHeight = byId('table-caption').getBoundingClientRect().height;
  const headerHeight = table.tHead.getBoundingClientRect().height;
  rowCapacity = Math.max(1, Math.min(50, Math.floor((region.clientHeight - captionHeight - headerHeight - 3) / Math.max(60, font * 3.8))));
  rowPage = Math.min(rowPage, Math.max(0, result.rows.length - 1));
  const tbody = table.tBodies[0];
  tbody.replaceChildren();
  result.rows.slice(rowPage, rowPage + rowCapacity).forEach((row, index) => {
    const tr = document.createElement('tr');
    const rowLabel = row.slice(0, result.axisCount).map(cellText).filter(Boolean).join(' / ');
    tr.append(tableCell('td', rowLabel, rowLabel, `Row ${rowPage + index + 1}`));
    row.slice(start, start + columnCapacity).forEach(value => tr.append(tableCell('td', cellText(value), value ?? 'Missing value')));
    tbody.append(tr);
  });
  while (table.getBoundingClientRect().height > region.clientHeight && tbody.rows.length > 1) {
    rowCapacity--;
    tbody.lastElementChild.remove();
  }
  const minimumHeight = document.querySelector('.page-header').getBoundingClientRect().height +
    document.querySelector('.page-footer').getBoundingClientRect().height +
    document.querySelector('.table-heading').getBoundingClientRect().height + captionHeight + headerHeight +
    (tbody.rows[0]?.getBoundingClientRect().height || 60) + 12;
  document.body.dataset.flow = String(minimumHeight > document.documentElement.clientHeight);
  byId('row-page').textContent = result.rows.length ? `${rowPage + 1}–${Math.min(rowPage + rowCapacity, result.rows.length)} / ${result.rows.length}` : '0 rows';
  byId('col-page').textContent = `${Math.min(columnPage * columnCapacity + 1, result.columns.length - result.axisCount)}–${Math.min((columnPage + 1) * columnCapacity, result.columns.length - result.axisCount)} / ${result.columns.length - result.axisCount}`;
  byId('row-prev').disabled = rowPage === 0;
  byId('row-next').disabled = rowPage + rowCapacity >= result.rows.length;
  byId('col-prev').disabled = columnPage === 0;
  byId('col-next').disabled = (columnPage + 1) * columnCapacity >= result.columns.length - result.axisCount;
  document.dispatchEvent(new Event('pivot-layout'));
}

for (const name of aggregations) byId('aggregation').add(new Option({ 'Standard deviation': 'Sample SD', 'Count nonmissing': 'Count present', 'Unique values': 'Distinct' }[name] || name, name));
for (const axis of ['rows', 'columns', 'values']) byId(`choose-${axis}`).onclick = () => {
  openChoices(`Choose ${axis}`, fields.map(field => ({ label: field, value: field })), settings[axis], chosen => {
    settings[axis] = chosen;
    byId(`choose-${axis}`).textContent = `${axis[0].toUpperCase() + axis.slice(1)}: ${chosen.length} fields`;
  });
};
byId('settings-open').onclick = async () => {
  byId('settings').showModal();
  byId('settings-open').setAttribute('aria-expanded', 'true');
  import('./pivot-layout.js').then(module => module.scheduleLayout()).catch(error => console.warn('Layout unavailable.', error));
  document.dispatchEvent(new Event('pivot-layout'));
  for (const axis of ['rows', 'columns', 'values']) byId(`choose-${axis}`).disabled = true;
  try { await fullFields(); }
  catch (error) { reportError(error); }
  finally { for (const axis of ['rows', 'columns', 'values']) byId(`choose-${axis}`).disabled = false; }
};
byId('settings').onclose = () => byId('settings-open').setAttribute('aria-expanded', 'false');
byId('settings-form').onsubmit = event => {
  event.preventDefault();
  settings.aggregation = byId('aggregation').value;
  settings.totals = byId('totals').checked;
  settings.cohort = byId('cohort').value;
  byId('settings').close();
  update();
};
byId('filters-enabled').onchange = event => {
  settings.filtersEnabled = event.target.checked;
  byId('filters-open').hidden = !settings.filtersEnabled;
  update();
};
byId('filters-open').onclick = async () => {
  try { await fullFields(); byId('filters').showModal(); }
  catch (error) { reportError(error); }
};
function renderFilters() {
  byId('active-filters').replaceChildren();
  const configured = Object.entries(settings.filters);
  if (configured.length) {
    const button = document.createElement('button');
    button.textContent = `Edit filters (${configured.length})`;
    button.dataset.fitLabel = '';
    button.onclick = () => openChoices('Edit filter', configured.map(([field, values]) => ({ label: `${field}: ${values.length || 'all'} values`, value: field })), [], chosen => {
      if (chosen.length) setTimeout(() => chooseFilterValues(chosen[0]), 0);
    }, true);
    byId('active-filters').append(button);
  }
}
async function chooseFilterValues(field) {
  try {
    const reply = await request('choices', { field });
    openChoices(`Filter: ${field}`, reply.choices.map(value => ({ label: value === null ? '(missing)' : String(value), value })), settings.filters[field] || [], chosen => {
      settings.filters[field] = chosen;
      renderFilters();
      update();
    });
  } catch (error) { reportError(error); }
}
byId('add-filter').onclick = () => openChoices('Choose filter field', fields.map(field => ({ label: field, value: field })), [], chosen => {
  if (!chosen.length) return;
  setTimeout(() => chooseFilterValues(chosen[0]), 0);
}, true);
byId('clear-filters').onclick = () => { settings.filters = {}; renderFilters(); update(); };
async function changeSource(key, entry = null) {
  const sourceRevision = ++sourceGeneration;
  generation++;
  source = key; saved = entry; settings.filters = {}; renderFilters();
  byId('source').value = key;
  byId('status').textContent = `Loading ${names[key]}…`;
  for (const axis of ['rows', 'columns', 'values']) byId(`choose-${axis}`).disabled = true;
  const prior = { ...settings, rows: [...settings.rows], columns: [...settings.columns], values: [...settings.values] };
  settings.rows = []; settings.columns = []; settings.values = []; settings.aggregation = 'Row count';
  try {
    const reply = await request('pivot');
    if (sourceRevision !== sourceGeneration) return;
    fields = reply.columns; numeric = reply.numeric;
    const savedKeys = ['model', 'cohort', 'prior', 'quantity', 'parameter', 'term', 'contrast', 'participant_id', 'cell', 'basis', 'distance_cm', 'soa_ms', 'effect', 'measure', 'units', 'metric'].filter(field => fields.includes(field));
    settings.rows = key === 'saved' ? (savedKeys.length ? savedKeys : [fields[0]]) : [key === 'participants' ? 'participant_id' : 'distance_cm'];
    settings.columns = ['condition', 'phase'].filter(field => fields.includes(field) && !settings.rows.includes(field));
    const preferredValue = ['corrected_rt_ms', 'reaction_time_ms', 'posterior_median', 'median', 'age_years'].find(field => numeric.includes(field) && !settings.rows.includes(field) && !settings.columns.includes(field));
    settings.values = [preferredValue || numeric.find(field => !settings.rows.includes(field) && !settings.columns.includes(field))].filter(Boolean);
    settings.aggregation = settings.values.length ? 'Mean' : 'Row count';
    settings.totals = key !== 'saved';
    byId('aggregation').value = settings.aggregation;
    byId('totals').checked = settings.totals;
    for (const axis of ['rows', 'columns', 'values']) byId(`choose-${axis}`).textContent = `${axis[0].toUpperCase() + axis.slice(1)}: ${settings[axis].length} fields`;
    byId('saved-table').hidden = key !== 'saved';
    update();
  } catch (error) { if (sourceRevision === sourceGeneration) { Object.assign(settings, prior); reportError(error); } }
  finally {
    if (sourceRevision === sourceGeneration) for (const axis of ['rows', 'columns', 'values']) byId(`choose-${axis}`).disabled = false;
  }
}
async function chooseSaved() {
  try {
    if (!catalog) {
      const response = await fetch('app/public/snapshots/catalog.json', { signal: AbortSignal.timeout(30000) });
      if (!response.ok) throw new Error('Saved-table catalogue could not load.');
      catalog = await response.json();
    }
    openChoices('Choose saved table', catalog.map(entry => ({ label: entry.source, shortLabel: entry.source.split('/').pop().replaceAll('_', ' '), value: entry.file })), saved ? [saved.file] : [], chosen => changeSource('saved', catalog.find(entry => entry.file === chosen[0])), true);
  } catch (error) { reportError(error); }
}
byId('source').onchange = event => event.target.value === 'saved' ? chooseSaved() : changeSource(event.target.value);
byId('saved-table').onclick = chooseSaved;
byId('pages-open').onclick = () => byId('page-links').showModal();
byId('about-data').onclick = () => showDetail('Totals are recomputed from the underlying source records. Corrected RT = retained Audio–Tactile RT − participant × Condition × Phase baseline mean. Repeated distance cells are not extra participants. P011 and P033 have linked recordings and are excluded from the primary behavioural cohort. Saved parameter summaries remain descriptive; averaging posterior medians does not fit a new model.');
byId('filter-help').onclick = () => showDetail('Add a field, then choose the values to include. Empty selections include all values, including missing entries. Disabling Activate filters ignores every selection and preserves them for later. Clear filters removes all field selections.');
byId('chooser').addEventListener('close', () => { byId('source').value = source; });
byId('row-prev').onclick = () => { rowPage = Math.max(0, rowPage - rowCapacity); renderTable(); };
byId('row-next').onclick = () => { rowPage += rowCapacity; renderTable(); };
byId('col-prev').onclick = () => { columnPage--; renderTable(); };
byId('col-next').onclick = () => { columnPage++; renderTable(); };
byId('export').onclick = () => {
  if (!result) return;
  const url = URL.createObjectURL(new Blob([csvText(result)], { type: 'text/csv;charset=utf-8' }));
  const link = document.createElement('a');
  link.href = url; link.download = 'study5-pivot.csv'; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 60000);
};
let resizeScheduled = false;
new ResizeObserver(() => {
  if (resizeScheduled) return;
  resizeScheduled = true;
  requestAnimationFrame(() => { resizeScheduled = false; renderTable(); renderChoices(); });
}).observe(document.body);
update();
