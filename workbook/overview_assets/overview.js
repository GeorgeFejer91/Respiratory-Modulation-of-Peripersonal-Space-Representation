// Reuse the locked Pretext runtime for both tool and question navigation.
for (const link of document.querySelectorAll('.contents a')) link.setAttribute('data-measure', '');
await import('./pivot/text-fit.js');

const links = [...document.querySelectorAll('.contents a')];
const sections = links.map(link => document.querySelector(link.hash));
let scheduled = false;
function updateCurrent() {
  const current = sections.filter(section => section.getBoundingClientRect().top <= 120).at(-1) || sections[0];
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
updateCurrent();

const coreFrame = document.getElementById('core-pivot');
addEventListener('message', event => {
  if (event.origin !== location.origin || event.source !== coreFrame.contentWindow ||
      event.data?.type !== 'study5-core-height') return;
  const height = event.data.height;
  if (Number.isFinite(height) && height >= 200 && height <= 20000) coreFrame.style.height = `${height}px`;
});
