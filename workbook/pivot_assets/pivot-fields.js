import { fieldLabel } from './pivot-chart.mjs';

const factors = ['soa_ms', 'condition', 'phase', 'distance_cm', 'participant_id'];
const byId = id => document.getElementById(id);

// Native dragging on desktop; the same moves are available by tap or keyboard.
export function pivotFields(settings, changed) {
  let selected;
  function move(field, axis, before = null) {
    if (!factors.includes(field)) return;
    for (const key of ['rows', 'columns']) settings[key] = settings[key].filter(value => value !== field);
    if (axis) {
      const index = settings[axis].indexOf(before);
      settings[axis].splice(index < 0 ? settings[axis].length : index, 0, field);
    }
    changed();
  }
  function refresh() {
    const focused = document.activeElement?.dataset.field;
    for (const axis of ['available', 'rows', 'columns']) {
      const region = byId(`field-${axis}`);
      region.replaceChildren();
      const fields = axis === 'available' ? factors.filter(field => !settings.rows.includes(field) && !settings.columns.includes(field)) : settings[axis];
      for (const field of fields) {
        const button = document.createElement('button');
        button.type = 'button'; button.textContent = fieldLabel(field);
        button.dataset.field = field; button.dataset.axis = axis;
        button.dataset.fitLabel = ''; button.draggable = true;
        button.setAttribute('aria-label', axis === 'available' ? `Add ${fieldLabel(field)}` : `${fieldLabel(field)} in ${axis}. Move or remove field`);
        button.onclick = () => {
          if (axis === 'available') { move(field, ['condition', 'phase'].includes(field) ? 'columns' : 'rows'); return; }
          selected = { field, axis };
          byId('field-menu-title').textContent = fieldLabel(field);
          byId('field-up').disabled = settings[axis].indexOf(field) === 0;
          byId('field-down').disabled = settings[axis].indexOf(field) === settings[axis].length - 1;
          byId('field-menu').showModal();
        };
        button.ondragstart = event => { event.dataTransfer.setData('text/plain', field); event.dataTransfer.effectAllowed = 'move'; };
        region.append(button);
      }
      if (!fields.length) {
        const empty = document.createElement('span');
        empty.textContent = axis === 'available' ? 'All fields are in the layout' : 'Drop or add a field';
        empty.dataset.fitLabel = ''; region.append(empty);
      }
      region.ondragover = event => { event.preventDefault(); event.dataTransfer.dropEffect = 'move'; };
      region.ondrop = event => {
        event.preventDefault();
        const field = event.dataTransfer.getData('text/plain');
        const before = event.target.closest('[data-field]')?.dataset.field;
        if (field !== before) move(field, axis === 'available' ? null : axis, before);
      };
    }
    byId('pivot-clear').disabled = !settings.rows.length && !settings.columns.length;
    if (focused) document.querySelector(`[data-field="${focused}"]`)?.focus({ preventScroll: true });
    document.dispatchEvent(new Event('pivot-layout'));
  }
  byId('pivot-clear').onclick = () => { settings.rows = []; settings.columns = []; changed(); };
  for (const axis of ['rows', 'columns']) byId(`field-to-${axis}`).onclick = () => {
    byId('field-menu').close(); move(selected.field, axis);
  };
  for (const [id, offset] of [['up', -1], ['down', 1]]) byId(`field-${id}`).onclick = () => {
    const fields = settings[selected.axis], index = fields.indexOf(selected.field);
    [fields[index], fields[index + offset]] = [fields[index + offset], fields[index]];
    byId('field-menu').close(); changed();
  };
  byId('field-remove').onclick = () => { byId('field-menu').close(); move(selected.field, null); };
  refresh();
  return refresh;
}
