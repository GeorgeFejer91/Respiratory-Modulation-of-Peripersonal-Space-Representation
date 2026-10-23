// Read-only spreadsheet interaction over the existing result table.
const table = document.getElementById('pivot-table');
const region = document.getElementById('table-region');
const copy = document.getElementById('copy-selection');
const all = document.getElementById('select-all-cells');
const extend = document.getElementById('extend-selection');
const status = document.getElementById('selection-status');
let rows = [], anchor, end, active, dragging = false, selected = new Set();
const available = () => rows.length && region.getAttribute('aria-busy') === 'false';
const point = cell => [cell.parentElement.rowIndex, cell.cellIndex];
const cellAt = ([r, c]) => rows[r]?.[c];
const bounds = () => [Math.min(anchor[0], end[0]), Math.max(anchor[0], end[0]), Math.min(anchor[1], end[1]), Math.max(anchor[1], end[1])];
const layout = () => document.dispatchEvent(new Event('pivot-layout'));

function paint() {
  const next = new Set();
  if (anchor) {
    const [top, bottom, left, right] = bounds();
    for (let r = top; r <= bottom; r++) for (let c = left; c <= right; c++) next.add(rows[r][c]);
    status.textContent = `${bottom - top + 1} rows × ${right - left + 1} columns selected`;
  } else status.textContent = 'No cells selected';
  for (const cell of selected) if (!next.has(cell)) cell.setAttribute('aria-selected', 'false');
  for (const cell of next) if (!selected.has(cell)) cell.setAttribute('aria-selected', 'true');
  selected = next;
  copy.disabled = !anchor || !available();
  layout();
}

function select(cell, extending = false, focus = true) {
  if (!cell || !available()) return;
  if (active) active.tabIndex = -1;
  active = cell; active.tabIndex = 0;
  end = point(cell);
  if (!extending || !anchor) anchor = end;
  paint();
  if (focus) cell.focus({ preventScroll: true });
}

export function resetSelection() {
  anchor = end = null; dragging = false;
  rows = [...table.rows].map(row => [...row.cells]);
  for (const row of rows) for (const cell of row) {
    cell.tabIndex = -1;
    cell.setAttribute('role', cell.tagName === 'TH' ? 'columnheader' : 'gridcell');
    cell.setAttribute('aria-selected', 'false');
  }
  active = rows[0]?.[0];
  if (active) active.tabIndex = 0;
  extend.setAttribute('aria-pressed', 'false');
  all.disabled = extend.disabled = !available();
  paint();
}

const extending = event => event.shiftKey || extend.getAttribute('aria-pressed') === 'true';
table.addEventListener('pointerdown', event => {
  if (event.pointerType === 'touch' || event.button !== 0) return;
  const cell = event.target.closest('th,td');
  if (!cell || !available()) return;
  event.preventDefault(); dragging = true;
  select(cell, extending(event));
});
document.addEventListener('pointermove', event => {
  if (!dragging) return;
  const cell = document.elementFromPoint(event.clientX, event.clientY)?.closest('#pivot-table th,#pivot-table td');
  if (cell && cell !== active) {
    select(cell, true);
    cell.scrollIntoView({ block: 'nearest', inline: 'nearest' });
  }
});
for (const type of ['pointerup', 'pointercancel', 'blur']) window.addEventListener(type, () => { dragging = false; });
table.addEventListener('click', event => {
  if (event.pointerType === 'touch' || event.detail === 0) select(event.target.closest('th,td'), extending(event));
});
extend.onclick = () => extend.setAttribute('aria-pressed', String(extend.getAttribute('aria-pressed') !== 'true'));
function selectAll(focus = true) {
  if (!available()) return;
  anchor = [0, 0]; select(rows.at(-1).at(-1), true, focus);
}
all.onclick = () => selectAll(false);
table.addEventListener('keydown', event => {
  if (!available()) return;
  const cell = event.target.closest('th,td');
  if (!cell) return;
  const [r, c] = point(cell), command = event.ctrlKey || event.metaKey;
  if (command && event.key.toLowerCase() === 'a') { event.preventDefault(); selectAll(); return; }
  if (event.key === 'Escape') { anchor = end = null; paint(); return; }
  let target;
  if (event.key === 'ArrowRight') target = [r, Math.min(c + 1, rows[r].length - 1)];
  if (event.key === 'ArrowLeft') target = [r, Math.max(c - 1, 0)];
  if (event.key === 'ArrowDown') target = [Math.min(r + 1, rows.length - 1), c];
  if (event.key === 'ArrowUp') target = [Math.max(r - 1, 0), c];
  if (event.key === 'Home') target = [command ? 0 : r, 0];
  if (event.key === 'End') target = [command ? rows.length - 1 : r, rows[r].length - 1];
  if (target) {
    if (event.shiftKey && !anchor) anchor = point(cell);
    event.preventDefault(); select(cellAt(target), event.shiftKey);
    active.scrollIntoView({ block: 'nearest', inline: 'nearest' });
  }
});

function clipboardText() {
  const [top, bottom, left, right] = bounds();
  // Excel TSV: unformatted numbers, empty missing cells, quoted embedded separators.
  const quote = value => /[\t\r\n"]/.test(value) ? `"${value.replaceAll('"', '""')}"` : value;
  return rows.slice(top, bottom + 1).map(row => row.slice(left, right + 1).map(cell => quote(cell.dataset.copyValue)).join('\t')).join('\r\n');
}
table.addEventListener('copy', event => {
  if (!anchor || !available()) return;
  event.preventDefault(); event.clipboardData.setData('text/plain', clipboardText());
  status.textContent = 'Selection copied. Paste into Excel.'; layout();
});
copy.onclick = async () => {
  if (!anchor || !available()) return;
  const text = clipboardText();
  try { await navigator.clipboard.writeText(text); }
  catch {
    // Same-origin embeds can deny the asynchronous API. Use the user-initiated
    // native copy command without changing selection or published values.
    const input = document.createElement('textarea');
    input.value = text; input.setAttribute('aria-label', 'Selected cells');
    input.style.cssText = 'position:fixed;inset:0;width:1px;height:1px;opacity:0';
    document.body.append(input); input.select();
    let success = false;
    try { success = document.execCommand('copy'); } catch { /* Report the manual shortcut below. */ }
    input.remove(); copy.focus({ preventScroll: true });
    if (!success) {
      active?.focus({ preventScroll: true });
      status.textContent = 'Press Ctrl+C (Mac: ⌘C) to copy the selected cells.'; layout(); return;
    }
  }
  status.textContent = 'Selection copied. Paste into Excel.'; layout();
};
