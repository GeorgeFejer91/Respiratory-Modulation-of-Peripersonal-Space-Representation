export const aggregations = ['Mean', 'Median', 'Sum', 'Count nonmissing', 'Standard deviation', 'Minimum', 'Maximum', 'Unique values', 'Row count'];

export function snapshotFrame(snapshot) {
  const columns = snapshot.columns;
  const rows = snapshot.rows.map(row => columns.map(field => row[field] === '' ? null : row[field]));
  const numeric = [];
  const types = Object.fromEntries(columns.map(field => [field, 'text']));
  columns.forEach((field, index) => {
    const present = rows.map(row => row[index]).filter(value => value !== null);
    if (present.length && present.every(value => value === 'True' || value === 'False')) {
      rows.forEach(row => { if (row[index] !== null) row[index] = row[index] === 'True'; });
      if (present.length === rows.length) { numeric.push(field); types[field] = 'boolean'; }
    } else if (present.length && present.every(value => String(value).trim() !== '' && !Number.isNaN(Number(value)))) {
      rows.forEach(row => { if (row[index] !== null) row[index] = Number(row[index]); });
      numeric.push(field);
      types[field] = present.length === rows.length && present.every(value => /^[+-]?\d+$/.test(value)) ? 'integer' : 'number';
    }
  });
  return { columns, rows, numeric, types };
}

export function selectRecords(frame, settings) {
  const participant = frame.columns.indexOf('participant_id');
  const excluded = { 'Primary behavioural cohort': ['P011', 'P033'], 'Exclude P011': ['P011'], 'Exclude P033': ['P033'] }[settings.cohort] || [];
  const filters = settings.filtersEnabled ? Object.entries(settings.filters || {}).filter(([, values]) => values.length) : [];
  const selections = [...filters, ...Object.entries(settings.seriesFilters || {})]
    .map(([field, values]) => [frame.columns.indexOf(field), new Set(values.map(value => JSON.stringify(value)))]);
  return frame.rows.filter(row => (participant < 0 || !excluded.includes(row[participant])) &&
    selections.every(([index, values]) => index >= 0 && values.has(JSON.stringify(row[index]))));
}

function compareValue(left, right) {
  if (typeof left === 'string' && typeof right !== 'string') return 1;
  if (typeof right === 'string' && typeof left !== 'string') return -1;
  return left < right ? -1 : left > right ? 1 : 0;
}

export function compareTuple(left, right) {
  for (let index = 0; index < left.length; index++) {
    const order = compareValue(left[index], right[index]);
    if (order) return order;
  }
  return 0;
}

function summarize(values, aggregation) {
  const present = values.filter(value => value !== null && !Number.isNaN(value));
  if (aggregation === 'Row count') return values.length;
  if (aggregation === 'Count nonmissing') return present.length;
  if (aggregation === 'Unique values') return new Set(present).size;
  if (!present.length) return null;
  if (aggregation === 'Minimum') return present.reduce((a, b) => Math.min(a, Number(b)), Infinity);
  if (aggregation === 'Maximum') return present.reduce((a, b) => Math.max(a, Number(b)), -Infinity);
  if (aggregation === 'Median') {
    present.sort((a, b) => Number(a) - Number(b));
    const middle = Math.floor(present.length / 2);
    return present.length % 2 ? Number(present[middle]) : (Number(present[middle - 1]) + Number(present[middle])) / 2;
  }
  let sum = 0, correction = 0;
  for (const value of present) {
    const next = Number(value) - correction;
    const total = sum + next;
    correction = (total - sum) - next;
    sum = total;
  }
  if (aggregation === 'Sum') return sum;
  const mean = sum / present.length;
  if (aggregation === 'Mean') return mean;
  if (aggregation === 'Standard deviation') {
    if (present.length < 2) return null;
    return Math.sqrt(present.reduce((total, value) => total + (Number(value) - mean) ** 2, 0) / (present.length - 1));
  }
  throw new Error('Unknown summary.');
}

export function pivot(frame, settings) {
  if (settings.rawRecords) {
    const rows = selectRecords(frame, settings);
    return { columns: frame.columns, rows, rawRecords: true, axisCount: 0,
      count: rows.length, dataRowCount: rows.length, series: [], contexts: {} };
  }
  // Display benefit reverses the established correction without changing source records.
  if (settings.values.some(field => ['baseline_benefit_ms', 'baseline_benefit_norm', 'baseline_benefit_z'].includes(field)) && !frame.columns.includes('baseline_benefit_ms')) {
    const corrected = frame.columns.indexOf('corrected_rt_ms');
    if (corrected < 0) throw new Error('Baseline correction is unavailable for this source.');
    frame = { ...frame, columns: [...frame.columns, 'baseline_benefit_ms'],
      numeric: [...frame.numeric, 'baseline_benefit_ms'], types: { ...frame.types, baseline_benefit_ms: 'number' },
      rows: frame.rows.map(row => [...row, row[corrected] === null ? null : -row[corrected]]) };
  }
  // A linear trial transform commutes with cell averaging. References use all retained AT trials.
  for (const field of settings.values.filter(field => /^(reaction_time|baseline_benefit)_(norm|z)$/.test(field))) {
    if (frame.columns.includes(field)) continue;
    const sourceField = field.replace(/_(norm|z)$/, '_ms');
    const participant = frame.columns.indexOf('participant_id'), value = frame.columns.indexOf(sourceField);
    if (participant < 0 || value < 0 || !frame.normalizers) throw new Error('Participant RT normalization is unavailable for this source.');
    frame = { ...frame, columns: [...frame.columns, field], numeric: [...frame.numeric, field],
      types: { ...frame.types, [field]: 'number' }, rows: frame.rows.map(row => {
        const stats = frame.normalizers[row[participant]]?.[sourceField];
        const offset = field.endsWith('_z') ? stats?.mean : stats?.low;
        const scale = field.endsWith('_z') ? stats?.sd : stats?.high - stats?.low;
        return [...row, row[value] !== null && Number.isFinite(offset) && scale > 0 ? (row[value] - offset) / scale : null];
      }) };
  }
  if (settings.participantSummary) {
    if (settings.aggregation !== 'Mean' || !frame.columns.includes('participant_id')) {
      throw new Error('Participant summaries require participant IDs and Mean.');
    }
    const source = selectRecords(frame, settings);
    const indices = [...new Set(['participant_id', ...settings.rows, ...settings.columns])].map(field => frame.columns.indexOf(field));
    if (indices.some(index => index < 0)) throw new Error('Unknown participant-summary field.');
    const grouped = new Map();
    for (const row of source) {
      const key = JSON.stringify(indices.map(index => row[index]));
      if (!grouped.has(key)) grouped.set(key, []);
      grouped.get(key).push(row);
    }
    const records = [...grouped.values()].map(rows => {
      const record = [...rows[0]];
      for (const field of settings.values) {
        const index = frame.columns.indexOf(field);
        record[index] = summarize(rows.map(row => row[index]), 'Mean');
      }
      return record;
    });
    const result = pivot({ ...frame, rows: records }, { ...settings, participantSummary: false,
      includeSD: true, includeObservations: true, totals: false, filtersEnabled: false, cohort: 'Full release' });
    result.count = source.length;
    result.participantSummary = true;
    return result;
  }
  const { rows, columns, values, aggregation, totals } = settings;
  if (!aggregations.includes(aggregation)) throw new Error('Choose a summary.');
  if (rows.some(field => columns.includes(field))) throw new Error('A field can be in Rows or Columns, not both.');
  if (values.some(field => rows.includes(field) || columns.includes(field))) throw new Error('Values must differ from Rows and Columns.');
  if (!values.length && aggregation !== 'Row count') throw new Error('Choose a Values field, or use Row count.');
  if ([...rows, ...columns, ...values].some(field => !frame.columns.includes(field))) throw new Error('Unknown field.');
  if (!['Count nonmissing', 'Unique values', 'Row count'].includes(aggregation) && values.some(field => !frame.numeric.includes(field))) {
    throw new Error('Choose numeric Values fields, or use Count nonmissing / Unique values for text.');
  }
  const source = selectRecords(frame, settings);
  const rowNames = rows.length ? rows : ['All records'];
  if (!source.length) return { columns: rowNames, rows: [], axisCount: rowNames.length, count: 0, dataRowCount: 0, series: [], contexts: {} };
  const rowFields = rows.map(field => frame.columns.indexOf(field));
  const colFields = columns.map(field => frame.columns.indexOf(field));
  const measures = aggregation === 'Row count' ? ['Record count'] : values;
  const measureFields = measures.map(field => frame.columns.indexOf(field));
  const rowGroups = new Map(), columnGroups = new Map(), cells = new Map();
  const keys = (record, indices) => indices.map(index => record[index] ?? '(missing)');
  for (const record of source) {
    const row = rows.length ? keys(record, rowFields) : ['All records'];
    const column = keys(record, colFields);
    const rowKey = JSON.stringify(row), columnKey = JSON.stringify(column);
    if (!rowGroups.has(rowKey)) rowGroups.set(rowKey, { label: row, records: [] });
    if (!columnGroups.has(columnKey)) columnGroups.set(columnKey, { label: column, records: [] });
    rowGroups.get(rowKey).records.push(record);
    columnGroups.get(columnKey).records.push(record);
    const key = JSON.stringify([rowKey, columnKey]);
    if (!cells.has(key)) cells.set(key, []);
    cells.get(key).push(record);
  }
  if ((rowGroups.size + 1) * (columnGroups.size + 1) * measures.length > 100000) {
    throw new Error('This pivot exceeds 100,000 cells. Filter records or remove a high-cardinality axis.');
  }
  const orderedRows = [...rowGroups.entries()].sort((a, b) => compareTuple(a[1].label, b[1].label));
  const orderedColumns = [...columnGroups.entries()].sort((a, b) => compareTuple(a[1].label, b[1].label));
  const descriptors = measures.flatMap((measure, index) => orderedColumns.map(([key, group]) => ({ measure, index, key, label: group.label })));
  if (totals && columns.length) measures.forEach((measure, index) => descriptors.push({ measure, index, total: true, label: ['Grand total'] }));
  const axisLabel = (value, field) => typeof value === 'boolean' ? (value ? 'True' : 'False') :
    typeof value === 'number' && frame.types?.[field] === 'number' && Number.isInteger(value) ? value.toFixed(1) : String(value);
  const resultColumns = rowNames.concat(descriptors.map(part => [part.measure, ...part.label.map((value, index) => axisLabel(value, columns[index]))].join(' · ')));
  const aggregate = (records, index) => summarize(records.map(record => aggregation === 'Row count' ? 1 : record[measureFields[index]]), aggregation);
  const stats = [];
  const resultRows = orderedRows.map(([rowKey, group]) => group.label.concat(descriptors.map(part => {
    const records = part.total ? group.records : cells.get(JSON.stringify([rowKey, part.key]));
    return records ? aggregate(records, part.index) : null;
  })));
  if (settings.includeSD && aggregation === 'Mean') {
    for (const [rowKey, group] of orderedRows) {
      stats.push(descriptors.map(part => {
        const records = part.total ? group.records : cells.get(JSON.stringify([rowKey, part.key])) || [];
        const values = records.map(record => record[measureFields[part.index]]);
        return { n: values.filter(value => value !== null && Number.isFinite(value)).length,
          sd: summarize(values, 'Standard deviation'), ...(settings.includeObservations ? {
            observations: records.map(record => ({ participant: record[frame.columns.indexOf('participant_id')],
              value: record[measureFields[part.index]] })).sort((a, b) => compareValue(a.participant, b.participant)) } : {}) };
      }));
    }
  }
  if (totals) resultRows.push(['Grand total', ...Array(rowNames.length - 1).fill(''), ...descriptors.map(part =>
    aggregate(part.total || !columns.length ? source : columnGroups.get(part.key).records, part.index))]);
  const series = descriptors.map((part, index) => ({ measure: part.measure, group: part.label,
    total: Boolean(part.total), column: rowNames.length + index }));
  const contexts = {};
  for (const field of ['units', 'parameter', 'quantity']) {
    const index = frame.columns.indexOf(field);
    if (index >= 0) contexts[field] = [...new Set(source.map(record => record[index]).filter(value => value !== null))];
  }
  return { columns: resultColumns, rows: resultRows, axisCount: rowNames.length, count: source.length,
    dataRowCount: orderedRows.length, series, contexts, ...(settings.includeSD ? { stats } : {}) };
}

export function csvText(result) {
  const escape = value => '"' + String(typeof value === 'boolean' ? (value ? 'True' : 'False') : value ?? '').replaceAll('"', '""') + '"';
  const expand = (row, index) => row.flatMap((value, column) => column < result.axisCount ? [value] :
    [value, result.stats[index]?.[column - result.axisCount]?.sd ?? null, result.stats[index]?.[column - result.axisCount]?.n ?? null]);
  const columns = result.stats ? result.columns.flatMap((value, column) => column < result.axisCount ? [value] : [value, `${value} · SD`, `${value} · n`]) : result.columns;
  const rows = result.stats ? result.rows.map(expand) : result.rows;
  return '\uFEFF' + [columns, ...rows].map(row => row.map(escape).join(',')).join('\r\n') + '\r\n';
}
