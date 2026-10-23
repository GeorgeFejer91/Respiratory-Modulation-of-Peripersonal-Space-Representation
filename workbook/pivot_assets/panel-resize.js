// Shared border controls; content stays in document flow without clipping.
let panelId = 0;
export function resizePanel(panel, { label, width = panel, height = panel, setWidth, minimumHeight = 240, table = false, west = false, resizeHeight = true } = {}) {
  if (panel.dataset.resizable !== undefined) return;
  panel.dataset.resizable = '';
  if (!panel.id) panel.id = `resizable-panel-${++panelId}`;
  if (!width.id) width.id = `${panel.id}-width`;
  if (!height.id) height.id = `${panel.id}-height`;
  panel.classList.add('resizable-panel');
  let drag, frame;
  const maxWidth = () => width.parentElement.clientWidth;
  const minHeight = () => table ? 0 : Math.max(minimumHeight, parseFloat(getComputedStyle(height).minHeight) || 0);
  const apply = (axis, value) => {
    if (axis === 'width') {
      value = Math.max(Math.min(240, maxWidth()), Math.min(maxWidth(), value));
      if (setWidth) setWidth(value);
      else width.style.width = `${value / maxWidth() * 100}%`;
    } else height.style.height = `${Math.max(minHeight(), value)}px`;
    document.dispatchEvent(new Event('panel-resize'));
    document.dispatchEvent(new Event('pivot-layout'));
  };
  for (const edge of [...(west ? ['left'] : []), 'right', ...(resizeHeight ? ['bottom'] : [])]) {
    const axis = edge === 'bottom' ? 'height' : 'width';
    const handle = document.createElement('div');
    handle.className = `resize-edge resize-${edge}`; handle.dataset.resizeEdge = edge;
    handle.tabIndex = 0; handle.setAttribute('role', 'separator');
    handle.setAttribute('aria-label', `${label} ${axis}. Drag or use arrow keys; Home resets.`);
    handle.setAttribute('aria-orientation', axis === 'width' ? 'vertical' : 'horizontal');
    handle.setAttribute('aria-controls', axis === 'width' ? width.id : height.id);
    handle.title = `Drag to resize ${label.toLowerCase()} ${axis}. Double-click to reset.`;
    const reset = () => {
      if (axis === 'width') { width.style.width = ''; width.parentElement.style.removeProperty('--table-share'); }
      else height.style.height = '';
      document.dispatchEvent(new Event('panel-resize')); document.dispatchEvent(new Event('pivot-layout'));
    };
    handle.addEventListener('dblclick', reset);
    handle.addEventListener('pointerdown', event => {
      if (event.button !== 0) return;
      event.preventDefault(); handle.focus({ preventScroll: true }); handle.setPointerCapture(event.pointerId);
      drag = { id:event.pointerId, x:event.clientX, y:event.clientY,
        width:width.getBoundingClientRect().width, height:height.getBoundingClientRect().height };
    });
    handle.addEventListener('pointermove', event => {
      if (!drag || drag.id !== event.pointerId) return;
      const value = axis === 'width' ? drag.width + (event.clientX - drag.x) * (edge === 'left' ? -1 : 1) : drag.height + event.clientY - drag.y;
      cancelAnimationFrame(frame); frame = requestAnimationFrame(() => apply(axis, value));
    });
    for (const type of ['pointerup', 'pointercancel', 'lostpointercapture']) handle.addEventListener(type, () => { drag = null; });
    handle.addEventListener('keydown', event => {
      if (event.key === 'Home') { event.preventDefault(); reset(); return; }
      const direction = ['ArrowRight','ArrowDown'].includes(event.key) ? 1 : ['ArrowLeft','ArrowUp'].includes(event.key) ? -1 : 0;
      if (!direction) return;
      event.preventDefault();
      const current = (axis === 'width' ? width : height).getBoundingClientRect()[axis];
      apply(axis, current + direction * (event.shiftKey ? 50 : 10) * (edge === 'left' ? -1 : 1));
    });
    panel.append(handle);
    new ResizeObserver(() => {
      const value = (axis === 'width' ? width : height).getBoundingClientRect()[axis];
      handle.setAttribute('aria-valuenow', String(Math.round(value)));
      handle.setAttribute('aria-valuetext', `${Math.round(value)} pixels`);
      handle.setAttribute('aria-valuemin', String(axis === 'width' ? Math.min(240,maxWidth()) : minHeight()));
      handle.setAttribute('aria-valuemax', String(axis === 'width' ? maxWidth() : Math.max(4000,value)));
    }).observe(axis === 'width' ? width : height);
  }
}
