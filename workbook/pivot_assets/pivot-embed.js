// Use the reader's viewport rather than the growing iframe as the height reference.
const fitPlot = () => document.body.style.setProperty('--plot-default-height', `${Math.max(260,Math.min(640,parent.innerHeight*.55))}px`);
fitPlot(); parent.addEventListener('resize',fitPlot);
// Embed the existing pivot without a second data engine or duplicated controls.
if (parent !== window) {
  const fitDialog = () => {
    const navigation = parent.matchMedia('(max-width: 800px)').matches ? parent.document.querySelector('.contents')?.getBoundingClientRect().height || 0 : 0;
    document.body.style.setProperty('--host-dialog-height', `${Math.max(120, parent.innerHeight - 24 - navigation)}px`);
  };
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
