// Serve a production build, then run with Playwright available in NODE_PATH.
const { chromium } = require('playwright');
const assert = require('node:assert/strict');

(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage();
    const base = process.argv[2] || 'http://127.0.0.1:8766/';
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(base);
    await page.waitForFunction(() => document.querySelector('header [data-measure]').dataset.fit === 'fit');
    assert.equal(await page.locator('main section').count(), 9);
    assert.equal(await page.locator('.contents a').count(), 9);
    const core = page.frameLocator('#core-pivot');
    await core.locator('#table-region[aria-busy="false"]').waitFor();
    assert.equal(await core.locator('html').getAttribute('data-record-count'), '800');
    assert((await core.locator('#chart-y-label').innerText()).includes('Reaction time (ms)'));
    assert.equal(await core.locator('[data-chart-point]').count(), 20);
    const [download] = await Promise.all([page.waitForEvent('download'), core.locator('#export').click()]);
    const stream = await download.createReadStream(), chunks = [];
    for await (const chunk of stream) chunks.push(chunk);
    const exported = Buffer.concat(chunks).toString('utf8');
    assert(exported.includes('reaction_time_ms') && !exported.includes('corrected_rt_ms'));
    assert.equal(exported.trim().split('\n').length, 7);
    await core.locator('#settings-open').click();
    await core.locator('#aggregation').selectOption('Median');
    await core.locator('#table-region[aria-busy="false"]').waitFor();
    await core.locator('#settings-form button[type="submit"]').click();
    assert((await core.locator('#chart-y-label').innerText()).startsWith('Median'));
    await core.locator('#chart-style').selectOption('points');
    assert.equal(await core.locator('[data-line]').count(), 0);
    await core.locator('#settings-open').click();
    await core.locator('#cohort').selectOption('Full release');
    await core.locator('html[data-record-count="840"]').waitFor();
    await core.locator('#source').selectOption('trials');
    await core.locator('html[data-record-count="17114"]').waitFor();
    await core.locator('#source').selectOption('participants');
    await core.locator('html[data-record-count="42"]').waitFor();
    await core.locator('#source').selectOption('means');
    await core.locator('html[data-record-count="840"]').waitFor();
    await core.locator('#settings-form button[type="submit"]').click();
    // Every internal evidence/tool link must exist in the actual artifact.
    const paths = await page.locator('a').evaluateAll(links => [...new Set(links
      .map(link => link.getAttribute('href')).filter(href => !/^(https?:|#)/.test(href)))]);
    for (const path of paths) assert((await page.request.get(new URL(path, base).href)).ok(), `Missing ${path}`);
    for (const [width, height] of [[320, 568], [640, 360], [900, 900], [1920, 1080]]) {
      await page.setViewportSize({ width, height });
      await page.evaluate(() => document.fonts.ready);
      await page.waitForFunction(() => {
        const frame = document.querySelector('#core-pivot');
        return frame.clientHeight >= frame.contentDocument.body.getBoundingClientRect().height;
      });
      assert(await core.locator('html').evaluate(element => element.scrollWidth <= element.clientWidth + 1), `${width} embedded overflow`);
      await core.locator('#settings-open').click();
      assert(await core.locator('#settings').evaluate(dialog => dialog.getBoundingClientRect().width <= innerWidth), `${width} settings width`);
      await core.locator('#settings-form button[type="submit"]').click();
      for (const mode of ['normal', 'large', 'spacing']) {
        await page.addStyleTag({ content: mode === 'large' ? 'body {font-size:34px}' : mode === 'spacing'
          ? 'body {font-size:17px} * {line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important} p {margin-bottom:2em!important}'
          : 'body {font-size:17px}' });
        await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
        assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), `${width} ${mode} page overflow`);
        assert.deepEqual(await page.locator('.contents a, header a').evaluateAll(links => links.filter(link => link.scrollWidth > link.clientWidth + 1 || link.scrollHeight > link.clientHeight + 1).map(link => link.textContent)), [], `${width} ${mode} clipped navigation`);
        await core.locator('body').evaluate((body, mode) => {
          body.style.fontSize = mode === 'large' ? '32px' : '16px';
          body.style.letterSpacing = mode === 'spacing' ? '.12em' : '';
          body.style.wordSpacing = mode === 'spacing' ? '.16em' : '';
        }, mode);
        await core.locator('#settings-open').click();
        assert(await core.locator('#settings').evaluate((dialog, height) => dialog.getBoundingClientRect().bottom <= height + 1, height), `${width} ${mode} dialog exceeds reader viewport`);
        await core.locator('#settings-form button[type="submit"]').click();
      }
      // Remove overrides before interaction checks.
      await page.locator('style').evaluateAll(styles => styles.forEach(style => style.remove()));
      await page.locator('.contents a[href="#effects"]').click();
      await page.waitForFunction(() => document.querySelector('.contents a[href="#effects"]').hasAttribute('aria-current'));
      assert.equal(new URL(page.url()).hash, '#effects');
    }
    await page.goto(base);
    await page.keyboard.press('Tab');
    assert.equal(await page.evaluate(() => document.activeElement.className), 'skip');
    await page.keyboard.press('Enter');
    assert.equal(new URL(page.url()).hash, '#overview');
    await page.setViewportSize({ width: 1280, height: 900 });
    await page.screenshot({ path: '.for-ai-local/overview-desktop.png', fullPage: true });
    await page.setViewportSize({ width: 320, height: 568 });
    await page.screenshot({ path: '.for-ai-local/overview-phone.png', fullPage: true });
    assert.deepEqual(errors, []);
    console.log('PASS: nine sections, inline core pivot/chart, raw-RT CSV, aggregation/cohort/style controls, embedded reflow/settings, artifact links, scroll tracking, keyboard, Pretext, four viewports, 200% text and spacing.');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
