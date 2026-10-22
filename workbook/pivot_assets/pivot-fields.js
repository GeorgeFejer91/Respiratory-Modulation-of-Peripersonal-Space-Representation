import { fieldLabel } from './pivot-chart.mjs';

const factors = ['soa_ms', 'condition', 'phase', 'distance_cm', 'participant_id'];
const areas = ['available', 'rows', 'columns'];
const byId = id => document.getElementById(id);

// All input methods stage a move; only a valid drop changes the shared layout.
export function pivotFields(settings, changed) {
  let drag, touch, ghost, animation;
  const region = axis => byId(`field-${axis}`);
  const announce = text => { byId('field-announcement').textContent = text; };
  const buttons = axis => [...region(axis).querySelectorAll('button')].filter(button => button.dataset.field !== drag?.field);
  function target(axis, before = null) {
    if (!drag) return;
    drag.axis = axis; drag.before = before;
    for (const area of areas) {
      region(area).toggleAttribute('data-drop-active', area === axis);
      for (const button of region(area).querySelectorAll('button')) button.toggleAttribute('data-drop-before', button.dataset.field === before);
    }
  }
  function begin(field, kind) {
    cancel(); drag = { field, kind };
    document.querySelector(`[data-field="${field}"]`).setAttribute('data-dragging', '');
    announce(`${fieldLabel(field)} picked up. Choose a box; drop to apply. Escape cancels.`);
  }
  function cancel() {
    cancelAnimationFrame(animation); ghost?.remove(); ghost = null;
    for (const element of document.querySelectorAll('[data-drop-active],[data-drop-before],[data-dragging]')) {
      for (const attribute of ['data-drop-active', 'data-drop-before', 'data-dragging']) element.removeAttribute(attribute);
    }
    drag = null; touch = null;
  }
  function drop(axis, before = null) {
    const field = drag?.field;
    cancel();
    if (!factors.includes(field) || !areas.includes(axis) || field === before) return;
    const prior = JSON.stringify([settings.rows, settings.columns]);
    for (const key of ['rows', 'columns']) settings[key] = settings[key].filter(value => value !== field);
    if (axis !== 'available') {
      const index = settings[axis].indexOf(before);
      settings[axis].splice(index < 0 ? settings[axis].length : index, 0, field);
    }
    if (prior !== JSON.stringify([settings.rows, settings.columns])) changed();
    document.querySelector(`[data-field="${field}"]`)?.focus({ preventScroll: true });
    announce(`${fieldLabel(field)} dropped in ${axis === 'available' ? 'Available fields' : axis}.`);
  }
  function atPoint(x, y) {
    const element = document.elementFromPoint(x, y);
    const box = element?.closest('.field-area');
    target(box?.dataset.axis, element?.closest('button[data-field]')?.dataset.field);
  }
  function touchFrame() {
    if (!touch || !drag) return;
    // The embedded pivot is same-origin; scroll the reader's visible viewport.
    const frame = window.frameElement?.getBoundingClientRect() || { left: 0, top: 0 };
    const host = window.frameElement ? window.parent : window;
    const y = touch.y - frame.top, x = touch.x - frame.left;
    ghost.style.left = `${Math.max(0, Math.min(innerWidth - ghost.offsetWidth, x + 12))}px`;
    ghost.style.top = `${Math.max(0, y - 44)}px`;
    atPoint(x, y);
    host.scrollBy(0, touch.y < 40 ? -12 : touch.y > host.innerHeight - 40 ? 12 : 0);
    animation = requestAnimationFrame(touchFrame);
  }
  function refresh() {
    const focused = document.activeElement?.dataset.field;
    for (const axis of areas) {
      const box = region(axis);
      box.dataset.axis = axis; box.tabIndex = 0;
      box.replaceChildren();
      const fields = axis === 'available' ? factors.filter(field => !settings.rows.includes(field) && !settings.columns.includes(field)) : settings[axis];
      for (const field of fields) {
        const button = document.createElement('button');
        button.type = 'button'; button.textContent = fieldLabel(field);
        button.dataset.field = field; button.dataset.axis = axis;
        button.dataset.fitLabel = ''; button.draggable = true;
        button.setAttribute('aria-label', `Drag ${fieldLabel(field)} from ${axis}. Space to pick up`);
        button.setAttribute('aria-describedby', 'field-instructions');
        button.ondragstart = event => {
          begin(field, 'native'); event.dataTransfer.setData('text/plain', field); event.dataTransfer.effectAllowed = 'move';
        };
        button.ondragend = () => cancel();
        button.onpointerdown = event => {
          if (event.pointerType === 'mouse' || !event.isPrimary || event.button !== 0) return;
          const frame = window.frameElement?.getBoundingClientRect() || { left: 0, top: 0 };
          touch = { x: event.clientX + frame.left, y: event.clientY + frame.top, startX: event.clientX, startY: event.clientY };
          button.setPointerCapture(event.pointerId);
        };
        button.onpointermove = event => {
          if (!touch) return;
          const frame = window.frameElement?.getBoundingClientRect() || { left: 0, top: 0 };
          const point = { ...touch, x: event.clientX + frame.left, y: event.clientY + frame.top };
          if (!drag && Math.hypot(event.clientX - touch.startX, event.clientY - touch.startY) > 6) {
            begin(field, 'touch'); touch = point;
            ghost = button.cloneNode(true); ghost.classList.add('field-drag-ghost');
            ghost.removeAttribute('data-field'); ghost.removeAttribute('data-fit-label');
            ghost.removeAttribute('data-dragging'); ghost.removeAttribute('aria-describedby');
            ghost.tabIndex = -1; ghost.setAttribute('aria-hidden', 'true'); document.body.append(ghost);
            animation = requestAnimationFrame(touchFrame);
          } else touch = point;
        };
        button.onpointerup = event => {
          if (drag?.kind === 'touch') { atPoint(event.clientX, event.clientY); drop(drag.axis, drag.before); }
          else touch = null;
        };
        button.onpointercancel = () => {
          if (drag?.kind !== 'native') { cancel(); announce('Move cancelled. Layout unchanged.'); }
        };
        box.append(button);
      }
      if (!fields.length) {
        const empty = document.createElement('span');
        empty.textContent = axis === 'available' ? 'Drop here to remove a field' : 'Drop a field here';
        empty.dataset.fitLabel = ''; box.append(empty);
      }
      box.ondragover = event => {
        if (drag?.kind !== 'native') return;
        event.preventDefault(); event.dataTransfer.dropEffect = 'move';
        target(axis, event.target.closest('button[data-field]')?.dataset.field);
      };
      box.ondragleave = event => { if (drag?.kind === 'native' && !box.contains(event.relatedTarget)) target(null); };
      box.ondrop = event => { event.preventDefault(); if (drag?.kind === 'native') drop(axis, event.target.closest('button[data-field]')?.dataset.field); };
    }
    byId('pivot-clear').disabled = !settings.rows.length && !settings.columns.length;
    if (focused) document.querySelector(`[data-field="${focused}"]`)?.focus({ preventScroll: true });
    document.dispatchEvent(new Event('pivot-layout'));
  }
  byId('core-controls').addEventListener('keydown', event => {
    if (event.key === 'Escape' && drag) {
      const field = drag.field; cancel(); announce('Move cancelled. Layout unchanged.');
      document.querySelector(`[data-field="${field}"]`)?.focus(); event.preventDefault(); return;
    }
    const field = event.target.dataset.field;
    const box = event.target.closest('.field-area');
    if (!box) return;
    if ([' ', 'Enter'].includes(event.key)) {
      event.preventDefault();
      if (!drag && field) { begin(field, 'keyboard'); target(box.dataset.axis); box.focus(); }
      else if (drag?.kind === 'keyboard') drop(box.dataset.axis, field || drag.before);
      return;
    }
    if (drag?.kind !== 'keyboard') return;
    const axis = box.dataset.axis;
    if (['ArrowLeft', 'ArrowRight'].includes(event.key)) {
      const next = areas[(areas.indexOf(axis) + (event.key === 'ArrowLeft' ? 2 : 1)) % areas.length];
      target(next); region(next).focus();
    } else if (['ArrowUp', 'ArrowDown', 'Home', 'End'].includes(event.key)) {
      const choices = buttons(axis), index = choices.findIndex(button => button.dataset.field === drag.before);
      const position = event.key === 'Home' ? 0 : event.key === 'End' ? choices.length :
        Math.max(0, Math.min(choices.length, (index < 0 ? choices.length : index) + (event.key === 'ArrowUp' ? -1 : 1)));
      target(axis, choices[position]?.dataset.field); box.focus();
    } else return;
    event.preventDefault(); announce(`${drag.axis}, ${drag.before ? `before ${fieldLabel(drag.before)}` : 'at end'}. Enter to drop.`);
  });
  byId('pivot-clear').onclick = () => { cancel(); settings.rows = []; settings.columns = []; changed(); };
  window.addEventListener('blur', cancel);
  refresh();
  return refresh;
}
