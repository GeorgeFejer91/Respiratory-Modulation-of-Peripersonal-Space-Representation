const byId = id => document.getElementById(id);
let selection = null;

export function showDetail(value) {
  byId('detail-value').textContent = String(value);
  byId('detail').showModal();
}

export function openChoices(title, choices, selected, onChange, single = false) {
  selection = { choices, selected: new Set(selected.map(value => JSON.stringify(value))), onChange, single };
  byId('chooser-title').textContent = title;
  byId('search').value = '';
  if (!byId('chooser').open) byId('chooser').showModal();
  renderChoices();
}

export function renderChoices() {
  if (!selection || !byId('chooser').open) return;
  const query = byId('search').value.toLowerCase();
  const choices = selection.choices.filter(choice => String(choice.label).toLowerCase().includes(query));
  const region = byId('choices');
  const font = parseFloat(getComputedStyle(region).fontSize);
  region.replaceChildren();
  for (const [index, choice] of choices.entries()) {
    const label = document.createElement('label');
    label.className = 'choice';
    const input = document.createElement('input');
    input.type = selection.single ? 'radio' : 'checkbox';
    input.name = 'choice';
    input.checked = selection.selected.has(JSON.stringify(choice.value));
    const text = document.createElement('span');
    const fullLabel = String(choice.label);
    const displayLabel = choice.shortLabel || fullLabel;
    const labelLimit = Math.min(42, Math.max(8, Math.floor((region.clientWidth - 110) / (font * .65)) * 2));
    text.textContent = displayLabel.length > labelLimit ? `Value ${index + 1}` : displayLabel;
    text.dataset.fitLabel = '';
    input.setAttribute('aria-label', fullLabel);
    input.onchange = () => {
      const key = JSON.stringify(choice.value);
      if (selection.single) selection.selected.clear();
      input.checked ? selection.selected.add(key) : selection.selected.delete(key);
      selection.onChange([...selection.selected].map(value => JSON.parse(value)));
      if (selection.single) byId('chooser').close();
    };
    label.append(input, text);
    if (fullLabel !== displayLabel || displayLabel.length > labelLimit) {
      const detail = document.createElement('button');
      detail.type = 'button';
      detail.textContent = 'Read';
      detail.dataset.fitLabel = '';
      detail.setAttribute('aria-label', `Read full value ${index + 1}`);
      detail.onclick = event => { event.preventDefault(); showDetail(fullLabel); };
      label.append(detail);
    }
    region.append(label);
  }
  if (!choices.length) region.textContent = 'No matches';
  document.dispatchEvent(new Event('pivot-layout'));
}

byId('search').oninput = renderChoices;
for (const button of document.querySelectorAll('[data-close]')) button.onclick = () => byId(button.dataset.close).close();
