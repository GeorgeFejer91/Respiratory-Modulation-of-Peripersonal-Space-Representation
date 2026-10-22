const labels = { soa_ms: 'SOA (ms)', distance_cm: 'Distance (cm)', corrected_rt_ms: 'Corrected RT (ms)',
  baseline_benefit_ms: 'Baseline − RT (ms)',
  reaction_time_norm: 'Reaction time (0–1)', baseline_benefit_norm: 'Baseline − RT (0–1)',
  reaction_time_z: 'Reaction time (z-score)', baseline_benefit_z: 'Baseline − RT (z-score)',
  reaction_time_ms: 'Reaction time (ms)', baseline_mean_ms: 'Baseline RT (ms)', n_trials: 'Trials per cell',
  participant_id: 'Participant', condition: 'Condition', phase: 'Breathing phase', age_years: 'Age (years)',
  midpoint_cm: 'Midpoint (cm)', width_cm: 'Width (cm)', normalized_steepness_per_cm: 'Normalized sharpness (cm⁻¹)' };
const fieldUnit = field => /_per_cm(?:_|$)/.test(field) ? 'cm⁻¹' : /_cm(?:_|$)/.test(field) ? 'cm' : /_ms(?:_|$)/.test(field) ? 'ms' : '';
export const fieldLabel = field => labels[field] || field.replaceAll('_', ' ') + (fieldUnit(field) ? ` (${fieldUnit(field)})` : '');
export function measureLabel(field, aggregation) {
  if (aggregation === 'Row count') return 'Records';
  const label = fieldLabel(field);
  if (['Count nonmissing', 'Unique values'].includes(aggregation)) {
    return `${aggregation === 'Unique values' ? 'Distinct values' : 'Count present'} · ${label.replace(/ \([^)]*\)$/, '')}`;
  }
  return `${aggregation === 'Standard deviation' ? 'Sample SD' : aggregation} · ${label}`;
}

// One chart point is exactly one pivot cell. Other row fields become series;
// no second groupby, averaging of summaries, or parsing of flattened labels.
export function chartModel(result, settings, measure) {
  const xField = ['soa_ms', 'distance_cm'].find(field => settings.rows.includes(field)) || settings.rows[0];
  const xIndex = xField ? settings.rows.indexOf(xField) : 0;
  const otherAxes = settings.rows.map((field, index) => ({ field, index })).filter(axis => axis.index !== xIndex);
  const groups = new Map(), points = [], xValues = [];
  const descriptors = result.series.filter(part => !part.total && part.measure === measure);
  const seenX = new Set();
  for (let rowIndex = 0; rowIndex < result.dataRowCount; rowIndex++) {
    const row = result.rows[rowIndex], x = row[xIndex];
    if (!seenX.has(JSON.stringify(x))) { seenX.add(JSON.stringify(x)); xValues.push(x); }
    for (const part of descriptors) {
      const rowGroup = otherAxes.map(axis => row[axis.index]);
      const key = JSON.stringify([rowGroup, part.group]);
      if (!groups.has(key)) {
        const text = [...otherAxes.map(axis => `${fieldLabel(axis.field)}: ${row[axis.index]}`),
          ...part.group.map((value, index) => settings.columns[index] ? String(value) : '')].filter(Boolean);
        groups.set(key, { key, label: text.join(' · ') || (result.participantSummary ? 'All participants' : fieldLabel(measure)), points: [] });
      }
      const stats = result.stats?.[rowIndex]?.[part.column - result.axisCount];
      const point = { x, y: row[part.column], row: rowIndex, column: part.column, series: key, ...(stats || {}) };
      groups.get(key).points.push(point);
      points.push(point);
    }
  }
  const numericX = xValues.length > 0 && xValues.every(value => typeof value === 'number' && Number.isFinite(value));
  if (numericX) xValues.sort((a, b) => a - b);
  const order = new Map(xValues.map((value, index) => [JSON.stringify(value), index]));
  for (const group of groups.values()) group.points.sort((a, b) => order.get(JSON.stringify(a.x)) - order.get(JSON.stringify(b.x)));
  const counts = ['Row count', 'Count nonmissing', 'Unique values'].includes(settings.aggregation);
  const contextual = !counts && !fieldUnit(measure) && /^(median|mean|low|high|estimate|value|posterior_.*)$/.test(measure);
  const units = contextual ? [...new Set(result.contexts?.units ||
    [...(result.contexts?.parameter || []), ...(result.contexts?.quantity || [])].map(fieldUnit).filter(Boolean))] : [];
  return { series: [...groups.values()], points, xValues, numericX, xLabel: xField ? fieldLabel(xField) : 'All records',
    yLabel: measureLabel(measure, settings.aggregation) + (units.length === 1 ? ` (${units[0]})` : ''),
    mixedUnits: units.length > 1, missingCount: points.filter(point => point.y === null).length };
}

const byId = id => document.getElementById(id);
const svgNS = 'http://www.w3.org/2000/svg';
const dashes = ['', '7 4', '2 4', '10 3 2 3'];
const format = value => value.toLocaleString(undefined, { maximumSignificantDigits: 6 });
function svgElement(tag, attributes = {}, text) {
  const node = document.createElementNS(svgNS, tag);
  for (const [name, value] of Object.entries(attributes)) node.setAttribute(name, value);
  if (text !== undefined) node.textContent = text;
  return node;
}
export function clearChart(message) {
  byId('chart-plot').replaceChildren();
  byId('chart-legend').replaceChildren();
  byId('chart-hover').textContent = message;
  byId('chart-note').textContent = '';
  byId('chart-y-label').textContent = 'Linked chart';
  byId('chart-x-label').textContent = '';
  byId('chart-region').setAttribute('aria-busy', 'false');
}

export function renderChart(result, settings, measure, mode, source) {
  const model = chartModel(result, settings, measure);
  clearChart('Hover or tap a point to compare series at that x. Keyboard: Tab, then arrow keys.');
  byId('chart-y-label').textContent = model.yLabel;
  byId('chart-x-label').textContent = model.xLabel;
  const weights = source === 'means' ? 'Participant-distance cells weighted equally.' : source === 'trials' ? 'Trial records weighted equally.' : 'Descriptive source-record summaries.';
  const showSD = result.participantSummary && settings.sdWhiskers;
  byId('chart-note').textContent = result.participantSummary ?
    `Participant means${showSD ? ' ±1 sample SD' : ''}; pooled factors averaged within each person. Descriptive, not a confidence interval.` :
    `${weights} Table scrolling and size do not change the chart. Grand totals omitted; ${model.missingCount} missing cells shown as gaps. Lines connect summaries; no fitted model or uncertainty intervals.`;
  if (/_norm$|_z$/.test(measure)) byId('chart-note').textContent += measure.endsWith('_z') ?
    ' Within-person z-scores use the mean and sample SD of all retained AT trials before cell averaging and series selection. Zero/undefined SD gives missing scores.' :
    ' Within-person 0–1 scores use the minimum/maximum of all retained AT trials before cell averaging and series selection. Constant ranges give missing scores; SD whiskers may extend beyond 0–1.';
  if (!result.count) { byId('chart-hover').textContent = 'No records match these filters. Clear filters or choose other values.'; return; }
  if (model.mixedUnits) { byId('chart-hover').textContent = 'Multiple measurement units are selected. Filter parameter, quantity or units before plotting these summaries on one axis. The pivot table and CSV remain available.'; return; }
  const present = model.points.filter(point => typeof point.y === 'number' && Number.isFinite(point.y));
  if (!present.length) { byId('chart-hover').textContent = 'No numeric values to plot for this measure. Missing cells remain in the table.'; return; }
  // Keep an explicit limit rather than silently sampling or freezing the phone.
  if (model.points.length > 4000 || model.series.length > 48 || model.xValues.length > 100) {
    byId('chart-hover').textContent = 'This chart is too dense to display (limit: 4,000 cells, 48 series, 100 x values). Filter records or remove a grouping field. The complete pivot is available in the table and CSV.';
    return;
  }
  const plot = byId('chart-plot');
  const font = parseFloat(getComputedStyle(plot).fontSize);
  const width = Math.max(240, plot.clientWidth), height = Math.max(240, font * 15);
  const margin = { left: font * 4.5, right: font, top: font, bottom: font * 2.5 };
  const innerWidth = width - margin.left - margin.right, innerHeight = height - margin.top - margin.bottom;
  const chart = svgElement('svg', { viewBox: `0 0 ${width} ${height}`, width, height, role: 'group',
    'aria-label': `${model.yLabel} by ${model.xLabel}. ${model.series.length} series. Values also available in the pivot table.` });
  plot.append(chart);
  const bars = mode === 'bars' || mode === 'auto' && !model.numericX;
  const low = Math.min(...present.map(point => point.y - (showSD && Number.isFinite(point.sd) ? point.sd : 0))),
    high = Math.max(...present.map(point => point.y + (showSD && Number.isFinite(point.sd) ? point.sd : 0)));
  let yMin = Math.min(0, low), yMax = Math.max(0, high);
  const pad = (yMax - yMin || Math.abs(yMax) * .1 || 1) * .12;
  if (yMin < 0) yMin -= pad;
  yMax += pad;
  const yScale = value => margin.top + innerHeight * (yMax - value) / (yMax - yMin);
  const xMin = model.xValues[0], xMax = model.xValues.at(-1);
  const categorical = bars || !model.numericX;
  const categoryWidth = innerWidth / model.xValues.length;
  const xScale = value => categorical ? margin.left + categoryWidth * (model.xValues.findIndex(x => JSON.stringify(x) === JSON.stringify(value)) + .5) :
    margin.left + (xMax === xMin ? innerWidth / 2 : innerWidth * (value - xMin) / (xMax - xMin));
  const tick = (x, y, text, anchor) => {
    const node = svgElement('text', { x, y, 'text-anchor': anchor, 'data-fit-label': '', class: 'chart-tick' }, text);
    chart.append(node); return node;
  };
  for (let index = 0; index <= 4; index++) {
    const value = yMin + (yMax - yMin) * index / 4, y = yScale(value);
    chart.append(svgElement('line', { x1: margin.left, x2: width - margin.right, y1: y, y2: y, class: 'chart-grid' }));
    tick(margin.left - 8, y + font * .3, value.toLocaleString(undefined, { notation: 'compact', maximumFractionDigits: 1 }), 'end');
  }
  const maxTicks = Math.max(2, Math.floor(innerWidth / (font * 4)));
  const tickCount = Math.min(model.xValues.length, maxTicks);
  const indices = new Set(Array.from({length:tickCount}, (_, index) => tickCount === 1 ? 0 : Math.round(index * (model.xValues.length - 1) / (tickCount - 1))));
  const xTicks = [];
  model.xValues.forEach((value, index) => {
    if (!indices.has(index)) return;
    // Categorical ticks use positions: full labels stay available on points/table.
    xTicks.push(tick(xScale(value), height - font * .6, model.numericX ? format(value) : String(index + 1), 'middle'));
  });
  const boxes = xTicks.map(node => node.getBoundingClientRect()), retained = [];
  boxes.forEach((box, index) => {
    if (index === boxes.length - 1) while (retained.length && boxes[retained.at(-1)].right + 6 > box.left) retained.pop();
    if (!retained.length || boxes[retained.at(-1)].right + 6 <= box.left) retained.push(index);
  });
  xTicks.forEach((node, index) => { if (!retained.includes(index)) node.remove(); });
  if (!model.numericX) byId('chart-x-label').textContent += ' · category positions (full labels on points and table)';
  chart.append(svgElement('line', { x1: margin.left, x2: width - margin.right, y1: yScale(0), y2: yScale(0),
    class: 'chart-zero', 'data-zero-baseline': '', 'aria-label': 'Zero reference' }));
  if (yMin < 0) tick(margin.left - 8, yScale(0) + font * .3, '0', 'end');
  const focusable = [];
  model.series.forEach((series, seriesIndex) => {
    const color = `var(--chart-${seriesIndex % 6 + 1})`, dash = dashes[seriesIndex % dashes.length];
    const group = svgElement('g', { fill: color, stroke: color, 'data-series': series.label });
    chart.append(group);
    if (!bars && mode !== 'points') {
      let path = '', penDown = false;
      for (const value of model.xValues) {
        const point = series.points.find(point => point.x === value);
        if (!point || point.y === null || !Number.isFinite(point.y)) { penDown = false; continue; }
        path += `${penDown ? 'L' : 'M'}${xScale(point.x)},${yScale(point.y)} `;
        penDown = true;
      }
      group.append(svgElement('path', { d: path, fill: 'none', 'stroke-width': 2, 'stroke-dasharray': dash, 'data-line': '' }));
    }
    for (const point of series.points) {
      if (point.y === null || !Number.isFinite(point.y)) continue;
      const x = xScale(point.x), y = yScale(point.y);
      const barWidth = categoryWidth * .8 / model.series.length;
      const center = bars ? x - categoryWidth * .4 + (seriesIndex + .5) * barWidth - .5 : x;
      let whisker;
      if (showSD && Number.isFinite(point.sd)) {
        const upper = yScale(point.y + point.sd), lower = yScale(point.y - point.sd);
        whisker = svgElement('path', { d: `M${center},${upper}V${lower} M${center - 4},${upper}H${center + 4} M${center - 4},${lower}H${center + 4}`,
          fill: 'none', 'stroke-width': 1.5, 'data-sd-whisker': '', 'data-sd': point.sd, 'data-n': point.n,
          'pointer-events': 'none', 'data-low': point.y - point.sd, 'data-high': point.y + point.sd });
      }
      const attributes = bars ? { x: x - categoryWidth * .4 + seriesIndex * barWidth,
        y: Math.min(y, yScale(0)), width: Math.max(.5, barWidth - 1), height: Math.max(1, Math.abs(y - yScale(0))) } : { cx: x, cy: y, r: 5 };
      const node = svgElement(bars ? 'rect' : 'circle', { ...attributes, 'data-chart-point': '', 'data-row': point.row,
        'data-column': point.column, 'data-value': point.y, tabindex: focusable.length ? -1 : 0, role: 'button', 'stroke-width': 2 });
      const spread = value => value.n === undefined ? '' : ` · SD: ${Number.isFinite(value.sd) ? format(value.sd) : 'undefined (n < 2)'} · n: ${value.n}`;
      const detail = `${seriesIndex + 1}. ${series.label} · ${model.xLabel}: ${point.x} · ${model.yLabel}: ${format(point.y)}${spread(point)}`;
      node.setAttribute('aria-label', detail);
      node.append(svgElement('title', {}, detail));
      const reveal = () => { byId('chart-hover').textContent = detail; document.dispatchEvent(new Event('pivot-layout')); };
      const compare = () => {
        const values = model.series.map((item, index) => {
          const other = item.points.find(other => other.x === point.x), value = other?.y;
          return `${index + 1}. ${item.label}: ${value === null || value === undefined ? '— (missing)' : format(value) + spread(other)}`;
        });
        byId('chart-hover').textContent = `${model.xLabel}: ${point.x} · ${model.yLabel} · ${values.join('; ')}`;
        document.dispatchEvent(new Event('pivot-layout'));
      };
      node.addEventListener('pointerenter', compare);
      node.addEventListener('focus', reveal);
      node.addEventListener('click', compare);
      node.addEventListener('keydown', event => {
        if (['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Home', 'End'].includes(event.key)) {
          event.preventDefault();
          const current = focusable.indexOf(node);
          const next = event.key === 'Home' ? 0 : event.key === 'End' ? focusable.length - 1 :
            Math.max(0, Math.min(focusable.length - 1, current + (['ArrowLeft', 'ArrowUp'].includes(event.key) ? -1 : 1)));
          focusable.forEach(pointNode => pointNode.setAttribute('tabindex', '-1'));
          focusable[next].setAttribute('tabindex', '0'); focusable[next].focus();
        } else if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); reveal(); }
      });
      focusable.push(node); group.append(node);
      if (whisker) group.append(whisker);
    }
    const item = document.createElement('li'), sample = svgElement('svg', { width: 28, height: 16, 'aria-hidden': true });
    sample.append(svgElement('line', { x1: 0, x2: 28, y1: 8, y2: 8, stroke: color, 'stroke-width': 3, 'stroke-dasharray': dash }));
    const label = document.createElement('span'); label.textContent = `${seriesIndex + 1}. ${series.label}`; label.dataset.fitLabel = '';
    item.append(sample, label); byId('chart-legend').append(item);
  });
  document.dispatchEvent(new Event('pivot-layout'));
}
