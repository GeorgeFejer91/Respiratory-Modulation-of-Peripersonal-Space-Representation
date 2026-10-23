import { resizePanel } from './pivot/panel-resize.js';
// Reuse the locked Pretext runtime for both tool and question navigation.
for (const link of document.querySelectorAll('.contents a')) link.setAttribute('data-measure', '');
const links = [...document.querySelectorAll('.contents a')];
const sections = links.map(link => document.querySelector(link.hash));
const menu = document.querySelector('.contents details');
const mobile = matchMedia('(max-width: 800px)');
function fitMenu() { document.querySelector('.contents').style.position = menu.getBoundingClientRect().height > innerHeight-32 ? 'static' : ''; }
function syncMenu() { menu.open = !mobile.matches; requestAnimationFrame(fitMenu); }
menu.addEventListener('toggle',fitMenu);
addEventListener('resize',fitMenu);
syncMenu();
mobile.addEventListener('change', syncMenu);
for (const link of links) link.addEventListener('click', () => {
  if (mobile.matches) menu.open = false;
});
await import('./pivot/text-fit.js');

let scheduled = false;
function updateCurrent() {
  const target = sections.find(section => `#${section.id}` === location.hash);
  const top = target?.getBoundingClientRect().top;
  const current = top >= 0 && top < innerHeight ? target : sections.filter(section => section.getBoundingClientRect().top <= 120).at(-1) || sections[0];
  for (const link of links) {
    if (link.hash === `#${current.id}`) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  }
  scheduled = false;
}
addEventListener('scroll', () => {
  if (!scheduled) { scheduled = true; requestAnimationFrame(updateCurrent); }
}, { passive: true });
addEventListener('resize', updateCurrent);
addEventListener('hashchange', updateCurrent);
updateCurrent();

// Shared geometry for current figure surfaces; native-chart owners can reuse this wrapper.
for (const figure of document.querySelectorAll('figure')) {
  const surface = figure.querySelector(':scope > a:has(img), :scope > [data-live-chart]');
  if (!surface) continue;
  const panel = document.createElement('div'); panel.className = 'plot-panel';
  surface.before(panel); panel.append(surface);
  resizePanel(panel,{label:figure.querySelector('figcaption strong')?.textContent || 'Figure'});
}

const coreFrame = document.getElementById('core-pivot');
addEventListener('message', event => {
  if (event.origin !== location.origin || event.source !== coreFrame.contentWindow ||
      event.data?.type !== 'study5-core-height') return;
  const height = event.data.height;
  if (Number.isFinite(height) && height >= 200 && height <= 5000000) coreFrame.style.height = `${height}px`;
});

try { await import('./publication-charts.js'); }
catch(error) {
  for(const host of document.querySelectorAll('[data-plot]')) host.textContent='Chart could not load. Exact data and static figure downloads remain available in the Results archive.';
  console.warn('Chart data could not load:',error);
}
