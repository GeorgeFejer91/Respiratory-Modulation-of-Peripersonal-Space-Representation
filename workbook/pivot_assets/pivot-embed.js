// Embed the existing pivot without a second data engine or duplicated controls.
if (parent !== window) {
  const fitDialog = () => document.body.style.setProperty('--host-dialog-height', `${Math.max(120, parent.innerHeight - 24)}px`);
  fitDialog();
  parent.addEventListener('resize', fitDialog);
  // Dialogs must fit the reader's viewport, rather than the full-height frame.
  for (const dialog of document.querySelectorAll('dialog')) {
    new MutationObserver(() => {
      if (dialog.open) {
        fitDialog();
        window.frameElement.scrollIntoView({ block: 'start', behavior: 'instant' });
      }
    }).observe(dialog, { attributes: true, attributeFilter: ['open'] });
  }
  let scheduled = false, priorHeight = 0;
  const resize = () => {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(() => {
      scheduled = false;
      const height = Math.ceil(document.body.getBoundingClientRect().height) + 8;
      if (height !== priorHeight) {
        priorHeight = height;
        parent.postMessage({ type: 'study5-core-height', height }, location.origin);
      }
    });
  };
  new ResizeObserver(resize).observe(document.body);
  resize();
}
