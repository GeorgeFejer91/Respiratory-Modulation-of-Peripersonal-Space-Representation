import { resizePanel } from './panel-resize.js';
import { aggregations, csvText } from './pivot-engine.mjs';
import { openChoices, renderChoices, showDetail } from './pivot-choices.js';
import { clearChart, renderChart, fieldLabel, measureLabel } from './pivot-chart.mjs';
import { resetSelection } from './pivot-selection.js';

const byId = id => document.getElementById(id);
let digits = 6, numberFormat = new Intl.NumberFormat(undefined, { maximumSignificantDigits: digits });
const coreView = new URLSearchParams(location.search).get('view') === 'core';
if (coreView) {
  document.body.classList.add('embedded-core');
  const style = document.createElement('link');
  style.rel = 'stylesheet'; style.href = 'pivot-embed.css'; document.head.append(style);
  import('./pivot-embed.js');
}
const worker = new Worker(new URL('./pivot-worker.js', import.meta.url), { type: 'module' });
const pending = new Map();
let requestId = 0, generation = 0, sourceGeneration = 0, result, resultSettings, resultSource, fields = [], numeric = [], catalog;
let source = 'means', saved = null, fullMeans = false, fullMeansRequest;
let workerFailure;
let chartGeometry = '';
const chartLayers = { summary: true, line: true, dots: false, spaghetti: false, violin: false };
let coreCorrected = true, coreNormalized = false;
let normalizationMethod = 'norm';
const settings = { rows: ['soa_ms'], columns: ['condition', 'phase'], values: ['corrected_rt_ms'], aggregation: 'Mean', totals: true, cohort: 'Primary behavioural cohort', filtersEnabled: false, filters: {} };
if (coreView) {
  settings.values = ['baseline_benefit_ms'];
  settings.totals = false;
  settings.sdWhiskers = true;
  byId('totals').checked = false;
  byId('core-controls').hidden = false;
  byId('choose-values').textContent = 'Values: baseline_benefit_ms';
  byId('source').replaceChildren(new Option('Core behavioural data', 'means'));
  byId('source').disabled = true;
  byId('choose-rows').closest('section').hidden = true;
  byId('totals').closest('label').hidden = true;
}
function coreControls() {
  if (!coreView) return;
  byId('core-spread').disabled = settings.aggregation !== 'Mean';
  byId('core-spread').closest('label').hidden = settings.aggregation !== 'Mean';
  byId('totals').disabled = true;
  byId('totals').checked = false;
  const corrected = coreCorrected;
  byId('core-correction').setAttribute('aria-checked', String(corrected));
  byId('core-correction-state').textContent = corrected ? 'On' : 'Off';
  byId('core-correction-formula').textContent = corrected ? 'Baseline − RT (ms)' : 'Uncorrected RT (ms)';
  byId('core-normalize').setAttribute('aria-checked', String(coreNormalized));
  byId('core-normalize-state').textContent = coreNormalized ? 'On' : 'Off';
}
if (coreView) {
  const setCoreMeasure = () => {
    settings.values = [(coreCorrected ? 'baseline_benefit' : 'reaction_time') + (coreNormalized ? `_${normalizationMethod}` : '_ms')];
    byId('choose-values').textContent = `Values: ${settings.values[0]}`;
    update();
  };
  byId('core-correction').onclick = () => { coreCorrected = !coreCorrected; setCoreMeasure(); };
  byId('core-normalize').onclick = () => { coreNormalized = !coreNormalized; setCoreMeasure(); };
  byId('core-normalization-method').onchange = event => { normalizationMethod = event.target.value; setCoreMeasure(); };
  byId('core-spread').onchange = () => {
    settings.sdWhiskers = byId('core-spread').value === 'sd'; labelTable(); renderTable(); drawChart();
  };
  for (const checkbox of document.querySelectorAll('[data-group-field]')) checkbox.onchange = () => {
    settings.columns = [...document.querySelectorAll('[data-group-field]:checked')].map(input => input.dataset.groupField);
    update();
  };
}
const names = { means: 'Participant-distance means', trials: 'All trial records', participants: 'Participants and questionnaires', saved: 'Saved analysis table' };
const sourceURL = () => coreView && !settings.rows.length && !settings.columns.length ? 'data/trials.json' :
  source === 'saved' ? `app/public/snapshots/${saved.file}` : `data/${source === 'means' && !fullMeans ? (coreView ? (coreNormalized ? 'means-normalized' : 'means-core-preview') : 'means-preview') : source}.json`;

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
  if (coreView) return;
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
  clearChart('Chart unavailable. Adjust Pivot settings to calculate both views again.');
  byId('chart-measure').disabled = true;
  byId('empty-table').hidden = true;
  byId('pivot-table').tHead.replaceChildren();
  byId('pivot-table').tBodies[0].replaceChildren();
  byId('table-caption').textContent = 'Pivot unavailable';
  byId('summary').textContent = 'No pivot calculated';
  delete document.documentElement.dataset.recordCount;
  document.body.dataset.flow = 'true';
  byId('error').textContent = error.message;
  byId('error').hidden = false;
  byId('table-region').setAttribute('aria-busy', 'false');
  resetSelection();
  byId('export').disabled = true;
  byId('status').textContent = 'Adjust Pivot settings to calculate again.';
}
async function update() {
  const revision = ++generation;
  coreControls();
  const submitted = structuredClone(settings);
  submitted.rawRecords = coreView && !submitted.rows.length && !submitted.columns.length;
  submitted.participantSummary = coreView && !submitted.rawRecords && source === 'means' && submitted.aggregation === 'Mean';
  if (submitted.participantSummary) submitted.totals = false;
  byId('table-region').setAttribute('aria-busy', 'true');
  resetSelection();
  byId('chart-region').setAttribute('aria-busy', 'true');
  byId('error').hidden = true;
  byId('export').disabled = true;
  if (coreView) byId('summary').textContent = submitted.rawRecords ? 'Loading trial records…' : 'Updating summary…';
  try {
    const reply = await request('pivot', { settings: submitted, url: submitted.rawRecords ? 'data/trials.json' : sourceURL() });
    if (revision !== generation) return;
    result = reply.result;
    resultSettings = submitted;
    resultSource = submitted.rawRecords ? 'trials' : source;
    coreControls();
    if (coreView || !(source === 'means' && fullMeans && reply.columns.length < fields.length)) {
      fields = reply.columns;
      numeric = reply.numeric;
    }
    byId('table-region').setAttribute('aria-busy', 'false');
    byId('export').disabled = false;
    byId('summary').textContent = `${result.count.toLocaleString()} source records · ${submitted.filtersEnabled ? 'Filters on' : 'Filters off'}`;
    labelTable();
    byId('status').textContent = source === 'saved' ? saved.source : `${names[resultSource]} · ${submitted.cohort}${coreView && !result.rawRecords ? ' · retained Audio–Tactile data' : ''}`;
    document.body.dataset.rawRecords = String(Boolean(result.rawRecords));
    byId('chart-region').hidden = Boolean(result.rawRecords);
    document.documentElement.dataset.recordCount = String(result.count);
    renderTable();
    const measures = submitted.aggregation === 'Row count' ? ['Record count'] : submitted.values;
    const priorMeasure = byId('chart-measure').value;
    byId('chart-measure').replaceChildren(...measures.map(field => new Option(fieldLabel(field), field)));
    if (measures.includes(priorMeasure)) byId('chart-measure').value = priorMeasure;
    byId('chart-measure').disabled = false;
    byId('chart-measure-control').hidden = measures.length < 2;
    drawChart();
    requestAnimationFrame(() => {
      if (!document.documentElement.dataset.readyMs) document.documentElement.dataset.readyMs = performance.now().toFixed(1);
      import('./pivot-layout.js').then(module => module.scheduleLayout()).catch(error => console.warn('Text geometry unavailable; readable browser layout remains active.', error));
    });
  } catch (error) { if (revision === generation) reportError(error); }
}

function cellText(value) {
  if (value === null) return '—';
  if (typeof value === 'number') return Number.isFinite(value) ? numberFormat.format(value) : String(value);
  return String(value);
}
function labelTable() {
  if (!result) return;
  const config = resultSettings;
  byId('table-caption').textContent = result.rawRecords ? 'Trial records · ungrouped · exclusion flags retained' : result.stats ?
    `${config.values.map(fieldLabel).join(' / ')} · ${settings.sdWhiskers ? 'Mean ± SD' : 'Mean'}` :
    config.aggregation === 'Row count' ? 'Records' : config.values.map(field => measureLabel(field, config.aggregation)).join(' / ');
}
function tableCell(tag, label, full, copyValue = label) {
  const cell = document.createElement(tag);
  cell.textContent = String(label);
  cell.title = String(full);
  cell.dataset.copyValue = String(copyValue ?? '');
  return cell;
}
function sizeTable() {
  const table = byId('pivot-table'), region = byId('table-region');
  const font = parseFloat(getComputedStyle(table).fontSize);
  const width = region.clientWidth;
  document.body.dataset.compact = String(width / font < 18);
  const columns = result ? result.rawRecords ? result.columns.length : result.columns.length - result.axisCount + 1 : 1;
  const next = width / columns < font * 5 ? 3 : 6;
  if (next === digits) return false;
  digits = next; numberFormat = new Intl.NumberFormat(undefined, { maximumSignificantDigits: digits });
  return true;
}
const displayCell = (value, stats) => stats && settings.sdWhiskers ? `${cellText(value)} ± ${cellText(stats.sd)}` : cellText(value);
export function renderTable() {
  if (!result) return;
  sizeTable();
  const table = byId('pivot-table');
  const header = document.createElement('tr');
  if (result.rawRecords) {
    for (const field of result.columns) header.append(tableCell('th', fieldLabel(field), field));
    table.tHead.replaceChildren(header);
    const fragment = document.createDocumentFragment();
    for (const row of result.rows) {
      const tr = document.createElement('tr');
      for (const value of row) tr.append(tableCell('td', cellText(value), value ?? 'Missing value', value));
      fragment.append(tr);
    }
    table.tBodies[0].replaceChildren(fragment);
    byId('empty-table').hidden = result.count > 0;
    resetSelection();
    document.dispatchEvent(new Event('pivot-layout'));
    return;
  }
  const rowTitle = resultSettings.rows.join(' / ') || 'All records';
  header.append(tableCell('th', resultSettings.rows.map(fieldLabel).join(' / ') || 'All records', rowTitle));
  result.columns.slice(result.axisCount).forEach(label => {
    const shorter = (resultSettings.values.length === 1 || resultSettings.aggregation === 'Row count') && resultSettings.columns.length ? label.split(' · ').slice(1).join(' · ') : label;
    header.append(tableCell('th', shorter, label));
  });
  table.tHead.replaceChildren(header);
  const tbody = table.tBodies[0];
  tbody.replaceChildren();
  byId('empty-table').hidden = result.count > 0;
  result.rows.forEach((row, rowIndex) => {
    const tr = document.createElement('tr');
    const rowLabel = row.slice(0, result.axisCount).map(cellText).filter(Boolean).join(' / ');
    tr.append(tableCell('td', rowLabel, rowLabel, row.slice(0, result.axisCount).map(value => value ?? '').join(' / ')));
    row.slice(result.axisCount).forEach((value, columnIndex) => {
      const stats = result.stats?.[rowIndex]?.[columnIndex];
      tr.append(stats ? tableCell('td', displayCell(value, stats), `Mean: ${value ?? 'missing'}; sample SD: ${stats.sd ?? 'undefined (n < 2)'}; n: ${stats.n}`,
        settings.sdWhiskers && value !== null ? `${value} ± ${stats.sd ?? '—'}` : value) :
        tableCell('td', cellText(value), value ?? 'Missing value', value));
    });
    tbody.append(tr);
  });
  resetSelection();
  document.dispatchEvent(new Event('pivot-layout'));
}

function drawChart(force = true) {
  if (result?.rawRecords) { clearChart('Add grouping fields to create a summary chart.'); return; }
  const plot = byId('chart-plot');
  const geometry = `${plot.clientWidth}:${plot.clientHeight}:${getComputedStyle(plot).fontSize}`;
  if (result && (force || chartGeometry !== geometry)) {
    chartGeometry = geometry;
    byId('chart-layers').hidden = !result.participantSummary;
    byId('chart-style').closest('label').hidden = Boolean(result.participantSummary);
    document.querySelector('[data-chart-layer="summary"]').textContent = settings.sdWhiskers ? 'Mean ± SD' : 'Mean dots';
    renderChart(result, { ...resultSettings, sdWhiskers: settings.sdWhiskers,
      ...(result.participantSummary ? { chartLayers } : {}) }, byId('chart-measure').value, byId('chart-style').value, resultSource);
  }
}
for (const button of document.querySelectorAll('[data-chart-layer]')) button.onclick = () => {
  const key = button.dataset.chartLayer;
  chartLayers[key] = !chartLayers[key];
  button.setAttribute('aria-pressed', String(chartLayers[key]));
  drawChart();
};
byId('chart-data-export').onclick = () => {
  if (!result?.participantSummary) return;
  const measure = byId('chart-measure').value;
  const columns = ['participant_id', ...resultSettings.rows, ...resultSettings.columns, measure];
  const rows = [];
  for (let row = 0; row < result.dataRowCount; row++) for (const part of result.series.filter(part => !part.total && part.measure === measure)) {
    for (const observation of result.stats[row][part.column - result.axisCount].observations) {
      rows.push([observation.participant, ...result.rows[row].slice(0, result.axisCount), ...part.group, observation.value]);
    }
  }
  const url = URL.createObjectURL(new Blob([csvText({ columns, rows })], { type: 'text/csv;charset=utf-8' }));
  const link = document.createElement('a'); link.href = url; link.download = 'participant-chart-values.csv'; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
};
byId('chart-measure').onchange = () => drawChart();
byId('chart-style').onchange = () => drawChart();

for (const name of aggregations) byId('aggregation').add(new Option({ 'Standard deviation': 'Sample SD', 'Count nonmissing': 'Count present', 'Unique values': 'Distinct' }[name] || name, name));
for (const axis of ['rows', 'columns', 'values']) byId(`choose-${axis}`).onclick = () => {
  const count = ['Row count', 'Count nonmissing', 'Unique values'].includes(settings.aggregation);
  const available = fields.filter(field => ['rows', 'columns', 'values'].every(other => other === axis || !settings[other].includes(field)) &&
    (axis !== 'values' || count || numeric.includes(field) || settings.values.includes(field)));
  openChoices(`Choose ${axis}`, available.map(field => ({ label: field, value: field })), settings[axis], chosen => {
    settings[axis] = chosen;
    byId(`choose-${axis}`).textContent = `${axis[0].toUpperCase() + axis.slice(1)}: ${chosen.length} fields`;
    update();
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
  byId('settings').close();
};
byId('aggregation').onchange = event => { settings.aggregation = event.target.value; update(); };
byId('totals').onchange = event => { settings.totals = event.target.checked; update(); };
byId('cohort').onchange = event => { settings.cohort = event.target.value; update(); };
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
byId('add-filter').onclick = () => openChoices('Choose filter field', (coreView ? ['participant_id', 'condition', 'phase', 'soa_ms', 'distance_cm'] : fields).map(field => ({ label: coreView ? fieldLabel(field) : field, value: field })), [], chosen => {
  if (!chosen.length) return;
  setTimeout(() => chooseFilterValues(chosen[0]), 0);
}, true);
byId('clear-filters').onclick = () => { settings.filters = {}; renderFilters(); update(); };
async function changeSource(key, entry = null) {
  const sourceRevision = ++sourceGeneration;
  generation++;
  source = key; saved = entry; settings.filters = {}; renderFilters();
  byId('table-region').setAttribute('aria-busy', 'true');
  byId('chart-region').setAttribute('aria-busy', 'true');
  byId('export').disabled = true;
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
    settings.rows = key === 'saved' ? (savedKeys.length ? savedKeys : [fields[0]]) : [key === 'participants' ? 'participant_id' : 'soa_ms'];
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
byId('about-data').onclick = () => showDetail((coreView ? 'Baseline correction on: participant × Condition × Phase baseline mean − retained Audio–Tactile RT. Positive values indicate faster responses than baseline; negative values remain visible. Off: uncorrected RT. ' : '') + 'Totals are recomputed from the underlying source records. The original corrected_rt_ms field remains retained Audio–Tactile RT − participant × Condition × Phase baseline mean. Repeated distance cells are not extra participants. P011 and P033 have linked recordings and are excluded from the primary behavioural cohort. Saved parameter summaries remain descriptive; averaging posterior medians does not fit a new model.');
byId('filter-help').onclick = () => showDetail('Add a field, then choose the values to include. Empty selections include all values, including missing entries. Disabling Activate filters ignores every selection and preserves them for later. Clear filters removes all field selections.');
byId('chooser').addEventListener('close', () => { byId('source').value = source; });
byId('export').onclick = () => {
  if (!result) return;
  const url = URL.createObjectURL(new Blob([csvText(result)], { type: 'text/csv;charset=utf-8' }));
  const link = document.createElement('a');
  link.href = url; link.download = result.rawRecords ? 'study5-trial-records.csv' : 'study5-pivot.csv'; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 60000);
};
let resizeScheduled = false;
new ResizeObserver(() => {
  if (resizeScheduled) return;
  resizeScheduled = true;
  requestAnimationFrame(() => { resizeScheduled = false; reformatTable(); renderChoices(); drawChart(false); });
}).observe(document.body);
new ResizeObserver(() => drawChart(false)).observe(byId('chart-plot'));
function reformatTable() {
  if (!result || !sizeTable()) return;
  // Reformat existing cells without replacing selection nodes or full-precision copy values.
  [...byId('pivot-table').tBodies[0].rows].forEach((row, index) => {
    const values = result.rawRecords ? result.rows[index] : result.rows[index].slice(result.axisCount);
    values.forEach((value, column) => {
      row.cells[column + (result.rawRecords ? 0 : 1)].textContent = displayCell(value, result.stats?.[index]?.[column]);
    });
  });
}
new ResizeObserver(reformatTable).observe(byId('table-region'));
const sheet = document.querySelector('.table-sheet'), views = document.querySelector('.linked-views');
const splitLayout = matchMedia('(min-width:1100px)');
const sideBySide = () => splitLayout.matches;
splitLayout.addEventListener('change', () => {
  sheet.style.width = ''; byId('chart-region').style.width = '';
});
resizePanel(byId('table-region'), { label:'Table', width:sheet, height:byId('pivot-table'), table:true, west:true,
  setWidth: value => {
    if (sideBySide()) views.style.setProperty('--table-share', `${Math.min(70,Math.max(20,value/views.clientWidth*100))}%`);
    else sheet.style.width = `${value/views.clientWidth*100}%`;
  } });
resizePanel(byId('chart-region'), { label:'Plot', height:byId('chart-plot'),
  setWidth: value => {
    if (sideBySide()) views.style.setProperty('--table-share', `${Math.min(70,Math.max(20,(views.clientWidth-value-20)/views.clientWidth*100))}%`);
    else byId('chart-region').style.width = `${value/views.clientWidth*100}%`;
  } });
update();
