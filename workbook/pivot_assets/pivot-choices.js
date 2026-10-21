const byId = id => document.getElementById(id);
let selection = null, page = 0, capacity = 8;

export function showDetail(value) {
  byId('detail-value').textContent = String(value);
  byId('detail').showModal();
}

export function openChoices(title, choices, selected, onChange, single = false) {
  selection = { choices, selected: new Set(selected.map(value => JSON.stringify(value))), onChange, single };
  page = 0;
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
  capacity = Math.max(1, Math.min(10, Math.floor(region.clientHeight / Math.max(52, font * 3.4))));
  page = Math.min(page, Math.max(0, Math.ceil(choices.length / capacity) - 1));
  region.replaceChildren();
  for (const [offset, choice] of choices.slice(page * capacity, (page + 1) * capacity).entries()) {
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
    text.textContent = displayLabel.length > labelLimit ? `Value ${page * capacity + offset + 1}` : displayLabel;
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
      detail.setAttribute('aria-label', `Read full value ${page * capacity + offset + 1}`);
      detail.onclick = event => { event.preventDefault(); showDetail(fullLabel); };
      label.append(detail);
    }
    region.append(label);
  }
  byId('choice-page').textContent = choices.length ? `${page + 1} / ${Math.ceil(choices.length / capacity)}` : 'No matches';
  byId('choice-prev').disabled = page === 0;
  byId('choice-next').disabled = (page + 1) * capacity >= choices.length;
  document.dispatchEvent(new Event('pivot-layout'));
}

byId('search').oninput = () => { page = 0; renderChoices(); };
byId('choice-prev').onclick = () => { page--; renderChoices(); };
byId('choice-next').onclick = () => { page++; renderChoices(); };
for (const button of document.querySelectorAll('[data-close]')) button.onclick = () => byId(button.dataset.close).close();
