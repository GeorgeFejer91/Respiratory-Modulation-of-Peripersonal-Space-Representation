const scores = document.getElementById('questionnaire-scores');
const participant = document.getElementById('questionnaire-participant');
const status = document.getElementById('questionnaire-status');
const itemDetails = document.getElementById('questionnaire-items');

function renderValues(list, rows) {
  list.replaceChildren(...rows.flatMap(([label, value, field]) => {
    const term = document.createElement('dt');
    const score = document.createElement('dd');
    term.textContent = label;
    score.textContent = value || 'Missing';
    score.dataset.field = field;
    return [term, score];
  }));
}

async function loadScores() {
  status.textContent = 'Loading participant scores…';
  try {
    const response = await fetch('questionnaire-data.json');
    if (!response.ok) throw new Error(`Questionnaire data returned HTTP ${response.status}`);
    const { scales, participants } = await response.json();
    const records = new Map(participants.map(record => [record.participant_id, record]));
    for (const id of records.keys()) participant.add(new Option(id, id));

    function render() {
      const record = records.get(participant.value);
      renderValues(document.getElementById('maia-scores'),
        scales.map(({ label, field }) => [label, record[field], field]));
      renderValues(document.getElementById('spatial-scores'), ['Control', 'Viscereality'].map(condition => {
        const field = 'spfrref_' + condition.toLowerCase();
        const value = record[field] ? `${record[field]} (${record[field + '_ordinal']})` : '';
        return [condition, value, field];
      }));
      if (!itemDetails.open) return;
      document.getElementById('maia-items').replaceChildren(...scales.map(({ label, items }) => {
        const group = document.createElement('div');
        const heading = document.createElement('h3');
        const list = document.createElement('dl');
        heading.textContent = label;
        renderValues(list, items.map(item => {
          const number = String(item).padStart(2, '0');
          const field = 'maia2_item_' + number;
          return [`Item ${number}`, record[field], field];
        }));
        group.append(heading, list);
        return group;
      }));
    }
    participant.addEventListener('change', render);
    itemDetails.addEventListener('toggle', render);
    render();
    document.getElementById('questionnaire-record').hidden = false;
    status.textContent = '';
  } catch (error) {
    status.textContent = 'Participant scores could not load. Use the released CSV below.';
    console.warn(error);
  }
}

scores.hidden = false;
scores.addEventListener('toggle', function revealScores() {
  if (!scores.open) return;
  scores.removeEventListener('toggle', revealScores);
  loadScores();
});
