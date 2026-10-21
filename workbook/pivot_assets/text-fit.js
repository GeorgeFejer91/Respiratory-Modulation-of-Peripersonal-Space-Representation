const regions = [...document.querySelectorAll('[data-measure]')];
try {
  const { prepareWithSegments, measureLineStats, measureNaturalWidth, setLocale } =
    await import('./vendor/pretext/dist/layout.js');
  await document.fonts.ready;
  setLocale(document.documentElement.lang);
  const prepared = new Map();
  function measure() {
    for (const region of regions) {
      const style = getComputedStyle(region);
      const text = region.textContent.trim();
      const font = `${style.fontStyle} ${style.fontWeight} ${style.fontSize} ${style.fontFamily}`;
      const spacing = parseFloat(style.letterSpacing) || 0;
      const key = JSON.stringify([text, font, spacing]);
      if (!prepared.has(key)) prepared.set(key, prepareWithSegments(text, font, { letterSpacing: spacing }));
      const handle = prepared.get(key);
      region.style.width = `${Math.min(Math.ceil(measureNaturalWidth(handle)) + 3, region.parentElement.clientWidth)}px`;
      const width = region.clientWidth;
      const stats = measureLineStats(handle, Math.max(1, width - 2));
      const height = stats.lineCount * parseFloat(style.lineHeight);
      region.style.minHeight = `${Math.ceil(height)}px`;
      region.dataset.fit = stats.maxLineWidth <= width && height <= region.clientHeight + 1 ? 'fit' : 'reflow';
      region.dataset.naturalWidth = measureNaturalWidth(handle).toFixed(2);
      region.dataset.lines = String(stats.lineCount);
    }
    if (prepared.size > 100) prepared.clear();
  }
  let scheduled = false;
  new ResizeObserver(() => {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(() => { scheduled = false; measure(); });
  }).observe(document.querySelector('header'));
  measure();
} catch (error) {
  for (const region of regions) region.dataset.fit = 'unavailable';
  console.warn('Text measurement unavailable; labels retain natural wrapping.', error);
}
