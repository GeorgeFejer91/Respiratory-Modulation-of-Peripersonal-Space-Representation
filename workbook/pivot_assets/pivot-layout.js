const cache = new Map();
let scheduled = false, pretext;

function measureLabels() {
  if (!pretext) return;
  const { prepareWithSegments, measureLineStats, measureNaturalWidth } = pretext;
  const readings = [...document.querySelectorAll('[data-fit-label],select')].filter(label => label.getClientRects().length).map(label => {
    const style = getComputedStyle(label);
    const text = label.tagName === 'SELECT' ? label.selectedOptions[0].textContent : label.textContent.trim();
    const font = `${style.fontStyle} ${style.fontWeight} ${style.fontSize} ${style.fontFamily}`;
    const spacing = parseFloat(style.letterSpacing) || 0;
    const key = JSON.stringify([text, font, spacing, document.documentElement.lang]);
    if (!cache.has(key)) cache.set(key, prepareWithSegments(text, font, { letterSpacing: spacing, whiteSpace: 'normal' }));
    const prepared = cache.get(key);
    const bounds = label.getBoundingClientRect();
    const width = Math.max(1, bounds.width - parseFloat(style.borderLeftWidth) - parseFloat(style.borderRightWidth) - parseFloat(style.paddingLeft) - parseFloat(style.paddingRight) - (label.tagName === 'SELECT' ? 24 : 0));
    const height = bounds.height - parseFloat(style.borderTopWidth) - parseFloat(style.borderBottomWidth) - parseFloat(style.paddingTop) - parseFloat(style.paddingBottom);
    const stats = measureLineStats(prepared, width);
    const lineHeight = parseFloat(style.lineHeight);
    // SVG text has painted bounds rather than an HTML line box; verify its
    // actual tick geometry in the browser instead of claiming height parity.
    const supported = !parseFloat(style.wordSpacing) && label.namespaceURI !== 'http://www.w3.org/2000/svg';
    const fit = stats.maxLineWidth <= width && stats.lineCount * lineHeight <= height + 1;
    return { label, fit: supported ? (fit ? 'fit' : 'reflow') : 'browser-only', lines: stats.lineCount, natural: measureNaturalWidth(prepared) };
  });
  for (const reading of readings) {
    reading.label.dataset.fit = reading.fit;
    reading.label.dataset.lines = reading.lines;
    reading.label.dataset.naturalWidth = reading.natural.toFixed(1);
  }
  if (cache.size > 600) cache.clear();
  document.documentElement.dataset.pretext = '1.0.0';
}

export function scheduleLayout() {
  if (scheduled) return;
  scheduled = true;
  requestAnimationFrame(() => {
    scheduled = false;
    try { measureLabels(); }
    catch (error) {
      document.documentElement.dataset.pretext = 'unavailable';
      console.warn('Pretext measurement unavailable; native wrapping remains active.', error);
    }
  });
}
document.addEventListener('pivot-layout', scheduleLayout);
const observer = new ResizeObserver(scheduleLayout);
observer.observe(document.body);
for (const dialog of document.querySelectorAll('dialog')) observer.observe(dialog);
scheduleLayout();
Promise.all([import('./vendor/pretext/dist/layout.js'), document.fonts.ready]).then(([module]) => {
  module.setLocale(document.documentElement.lang);
  pretext = module;
  scheduleLayout();
}).catch(error => {
  document.documentElement.dataset.pretext = 'unavailable';
  for (const label of document.querySelectorAll('[data-fit-label],select')) label.dataset.fit = 'unavailable';
  console.warn('Pretext unavailable; native text wrapping remains active.', error);
});
