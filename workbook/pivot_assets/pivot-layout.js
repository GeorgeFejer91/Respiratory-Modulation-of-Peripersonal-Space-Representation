const byId = id => document.getElementById(id);
const cache = new Map();
let scheduled = false, groupPage = 0, pageCount = 3, pretext;

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
    const supported = !parseFloat(style.wordSpacing);
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

function layoutSettings() {
  if (!byId('settings').open) return;
  const region = byId('settings-groups');
  const groups = [...region.children];
  groups.forEach(group => {
    group.hidden = false;
    [...group.children].forEach(control => { delete control.dataset.layoutHidden; });
  });
  region.style.removeProperty('grid-template-columns');
  const fits = region.scrollHeight <= region.clientHeight + 1;
  byId('group-prev').hidden = byId('group-next').hidden = fits;
  if (fits) {
    byId('group-page').textContent = '';
    return;
  }
  region.style.gridTemplateColumns = 'minmax(0,1fr)';
  const controlPages = groups.some(group => group.scrollHeight > region.clientHeight + 1);
  const pages = controlPages ? groups.flatMap(group => [...group.children].filter(control => control.tagName !== 'H3' && !control.hidden).map(control => ({ group, control }))) : groups.map(group => ({ group }));
  pageCount = pages.length;
  groupPage = Math.min(groupPage, pageCount - 1);
  groups.forEach(group => { group.hidden = group !== pages[groupPage].group; });
  if (controlPages) [...pages[groupPage].group.children].forEach(control => {
    control.dataset.layoutHidden = String(control.tagName !== 'H3' && control !== pages[groupPage].control);
  });
  byId('group-page').textContent = `${groupPage + 1} / ${pageCount}`;
  byId('group-prev').disabled = groupPage === 0;
  byId('group-next').disabled = groupPage === pageCount - 1;
  byId('settings').dataset.layout = controlPages ? 'control-pages' : 'group-pages';
}

export function scheduleLayout() {
  if (scheduled) return;
  scheduled = true;
  requestAnimationFrame(() => {
    scheduled = false;
    layoutSettings();
    try { measureLabels(); }
    catch (error) {
      document.documentElement.dataset.pretext = 'unavailable';
      console.warn('Pretext measurement unavailable; native wrapping remains active.', error);
    }
  });
}
byId('group-prev').onclick = () => { groupPage = Math.max(0, groupPage - 1); scheduleLayout(); };
byId('group-next').onclick = () => { groupPage = Math.min(pageCount - 1, groupPage + 1); scheduleLayout(); };
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
  console.warn('Pretext unavailable; native text wrapping and control pagination remain active.', error);
});
