import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';
import { pivot, snapshotFrame, csvText } from './pivot_assets/pivot-engine.mjs';
import { chartModel, measureLabel } from './pivot_assets/pivot-chart.mjs';

const payload = JSON.parse(readFileSync(0, 'utf8'));
const results = payload.cases.map(test => {
  try { return pivot(payload.frames[test.frame], test.settings); }
  catch (error) { return { error: error.message }; }
});
// The chart reads cells, never re-aggregates them or includes grand totals.
for (const [index, result] of results.entries()) {
  if (result.error) continue;
  const settings = payload.cases[index].settings;
  for (const measure of settings.aggregation === 'Row count' ? ['Record count'] : settings.values) {
    const model = chartModel(result, settings, measure);
    assert.equal(model.points.length, result.dataRowCount * result.series.filter(part => !part.total && part.measure === measure).length);
    for (const point of model.points) assert.equal(point.y, result.rows[point.row][point.column]);
    assert(model.points.every(point => point.row < result.dataRowCount));
  }
}
const participantCase = payload.cases.findIndex(test => test.frame === 'people-edge');
const participantResult = results[participantCase];
assert.equal(participantResult.rows[0][1], 8); // A = (2+4+6)/3 = 4; B = (10+14)/2 = 12.
assert.equal(participantResult.stats[0][0].n, 2);
assert(Math.abs(participantResult.stats[0][0].sd - Math.sqrt(32)) < 1e-12);
assert.equal(participantResult.stats[1][0].n, 1);
assert.equal(participantResult.stats[1][0].sd, null);
assert(csvText(participantResult).includes(' · SD'));
const frame = payload.frames['Participant-distance means'];
const selection = { rows: ['soa_ms'], columns: ['condition', 'phase'], values: ['corrected_rt_ms', 'reaction_time_ms'],
  aggregation: 'Mean', totals: true, cohort: 'Primary behavioural cohort', filtersEnabled: true,
  filters: { condition: ['Control'], soa_ms: [300, 1500] } };
const selected = pivot(frame, selection);
const chart = chartModel(selected, selection, 'corrected_rt_ms');
assert.equal(selected.count, 160);
assert.equal(chart.series.length, 2);
assert.deepEqual(chart.xValues, [300, 1500]);
assert.equal(chart.xLabel, 'SOA (ms)');
assert.equal(chart.yLabel, 'Mean · Corrected RT (ms)');
assert(chart.series.every(series => series.label.includes('Control')));
const hand = { columns: ['x', 'group', 'rt'], numeric: ['x', 'rt'], rows: [[1, 'A', 2], [1, 'A', 4], [2, 'A', null], [3, 'A', 0], [1, 'B', 12]] };
const handSettings = { ...selection, rows: ['x'], columns: ['group'], values: ['rt'], cohort: 'Full release', filtersEnabled: false };
const handResult = pivot(hand, handSettings);
assert.equal(handResult.rows.at(-1).at(-1), 4.5); // 18 / 4, not a mean of cell means.
const handChart = chartModel(handResult, handSettings, 'rt');
assert.deepEqual(handChart.series[0].points.map(point => point.y), [3, null, 0]);
assert.equal(handChart.missingCount, 3);
const groupedSettings = { ...handSettings, rows: ['x', 'group'], columns: [] };
assert.equal(chartModel(pivot(hand, groupedSettings), groupedSettings, 'rt').series.length, 2);
const countSettings = { ...handSettings, aggregation: 'Row count', values: [] };
assert.equal(chartModel(pivot(hand, countSettings), countSettings, 'Record count').yLabel, 'Records');
assert(!measureLabel('corrected_rt_ms', 'Count nonmissing').includes('(ms)'));
const emptySettings = { ...selection, filters: { condition: ['absent'] } };
assert.equal(chartModel(pivot(frame, emptySettings), emptySettings, 'corrected_rt_ms').points.length, 0);
const mixedSettings = { ...handSettings, rows: ['group'], columns: [] };
assert.equal(chartModel(pivot(hand, mixedSettings), mixedSettings, 'rt').numericX, false);
const unitFrame = { columns: ['parameter', 'median'], numeric: ['median'], rows: [['midpoint_cm', 50], ['normalized_steepness_per_cm', .02]] };
const unitSettings = { ...handSettings, rows: ['parameter'], columns: [], values: ['median'] };
assert(chartModel(pivot(unitFrame, unitSettings), unitSettings, 'median').mixedUnits);
unitSettings.filtersEnabled = true; unitSettings.filters = {parameter:['midpoint_cm']};
assert.equal(chartModel(pivot(unitFrame, unitSettings), unitSettings, 'median').yLabel, 'Mean · median (cm)');
process.stdout.write(JSON.stringify({ results, snapshot: snapshotFrame(payload.snapshots[0]),
  csv: csvText({ columns: ['a', 'b'], rows: [['=literal', 'quote"comma,']] }) }));
