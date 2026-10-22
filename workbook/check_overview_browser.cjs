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
    assert.equal(await page.locator('main p').count(), 0, 'Keep the reading page free of explanatory paragraphs');
    assert.equal(await page.locator('main section h2').count(), 9);
    const core = page.frameLocator('#core-pivot');
    await core.locator('#table-region[aria-busy="false"]').waitFor();
    assert.equal(await core.locator('html').getAttribute('data-record-count'), '800');
    const correction = core.getByRole('switch', { name: 'Baseline correction', exact: true });
    assert.equal(await correction.getAttribute('aria-checked'), 'true', 'Correction starts on');
    assert((await core.locator('#chart-y-label').innerText()).includes('Baseline − RT (ms)'));
    assert((await core.locator('#table-caption').innerText()).includes('Baseline − RT (ms)'));
    assert.equal(await core.locator('[data-chart-point]').count(), 20);
    assert.equal(await core.locator('[data-sd-whisker]').count(), 20);
    const firstMean = await core.locator('[data-chart-point]').first().getAttribute('data-value');
    const firstSD = await core.locator('[data-sd-whisker]').first().getAttribute('data-sd');
    const tableDetail = await core.locator('tbody td').nth(1).getAttribute('title');
    assert(tableDetail.includes(`Mean: ${firstMean}; sample SD: ${firstSD}; n: 40`));
    assert.equal(await core.locator('[draggable],.field-area,#pivot-clear').count(), 0);
    assert.equal(await core.locator('#chart-x-label').innerText(), 'SOA (ms)');
    assert.deepEqual(await core.locator('tbody tr td:first-child').allTextContents(), ['300', '800', '1,500', '2,200', '2,700']);
    const inputs = ['Control', 'Viscereality', 'Exhale', 'Inhale'].map(name => core.getByRole('checkbox', { name, exact: true }));
    for (let mask = 0; mask < 16; mask++) {
      for (let i = 0; i < inputs.length; i++) await inputs[i].setChecked(Boolean(mask & (1 << i)));
      await core.locator('#table-region[aria-busy="false"]').waitFor();
      const count = ((mask & 1 ? 1 : 0) + (mask & 2 ? 1 : 0)) * ((mask & 4 ? 1 : 0) + (mask & 8 ? 1 : 0));
      assert.equal(await core.locator('[data-chart-point]').count(), count * 5, 'Every checkbox combination filters both views');
      assert.equal(await core.locator('tbody tr').count(), count ? 5 : 0);
      assert.equal(await core.locator('#chart-x-label').innerText(), 'SOA (ms)');
    }
    assert.equal(await core.locator('input[type="checkbox"]:visible').count(), 4);
    // Native checkboxes support Space and preserve focus.
    await inputs[0].press('Space');
    await core.locator('#table-region[aria-busy="false"]').waitFor();
    assert.equal(await core.locator('[data-chart-point]').count(), 10);
    await inputs[0].press('Space');
    await core.locator('#table-region[aria-busy="false"]').waitFor();
    const normalize = core.getByRole('switch', { name: 'Normalize RT', exact: true });
    assert.equal(await normalize.getAttribute('aria-checked'), 'false');
    for (const method of ['norm', 'z']) {
      await core.locator('#core-normalization-method').selectOption(method);
      await core.locator('#table-region[aria-busy="false"]').waitFor();
      for (const corrected of [true, false]) {
        if ((await correction.getAttribute('aria-checked') === 'true') !== corrected) await correction.click();
        await core.locator('#table-region[aria-busy="false"]').waitFor();
        const original = await core.locator('[data-chart-point]').first().getAttribute('data-value');
        await normalize.press('Space');
        await core.locator('#table-region[aria-busy="false"]').waitFor();
        assert((await core.locator('#chart-y-label').innerText()).includes(method === 'norm' ? '(0–1)' : '(z-score)'));
        assert((await core.locator('#table-caption').innerText()).includes(method === 'norm' ? '(0–1)' : '(z-score)'));
        const normalized = await core.locator('[data-chart-point]').first().getAttribute('data-value');
        assert.notEqual(normalized, original);
        if (method === 'norm') assert(await core.locator('[data-chart-point]').evaluateAll(nodes => nodes.every(node => +node.dataset.value >= 0 && +node.dataset.value <= 1)));
        await inputs[1].uncheck();
        await core.locator('#table-region[aria-busy="false"]').waitFor();
        assert.equal(await core.locator('[data-chart-point]').first().getAttribute('data-value'), normalized, 'Hiding a condition must not renormalize participants');
        await inputs[1].check();
        await core.locator('#table-region[aria-busy="false"]').waitFor();
        const [normDownload] = await Promise.all([page.waitForEvent('download'), core.locator('#export').click()]);
        const normStream = await normDownload.createReadStream(), normChunks = [];
        for await (const chunk of normStream) normChunks.push(chunk);
        const normCSV = Buffer.concat(normChunks).toString('utf8');
        assert(normCSV.includes((corrected ? 'baseline_benefit_' : 'reaction_time_') + method));
        assert(normCSV.includes(normalized) && normCSV.includes(' · SD') && normCSV.includes(' · n'));
        await normalize.press('Enter');
        await core.locator('#table-region[aria-busy="false"]').waitFor();
        assert.equal(await core.locator('[data-chart-point]').first().getAttribute('data-value'), original);
      }
    }
    await correction.click();
    await core.locator('#table-region[aria-busy="false"]').waitFor();
    assert(await core.locator('[data-sd-whisker]').evaluateAll(nodes => nodes.every(node => +node.dataset.n === 40 && +node.dataset.high > +node.dataset.low)));
    assert(await core.locator('.chart-tick').allTextContents().then(ticks => ticks.includes('0')));
    const correctedMean = await core.locator('[data-chart-point]').first().getAttribute('data-value');
    const correctedSD = await core.locator('[data-sd-whisker]').first().getAttribute('data-sd');
    await correction.press('Space');
    await core.locator('#table-region[aria-busy="false"]').waitFor();
    assert.equal(await correction.getAttribute('aria-checked'), 'false');
    assert((await core.locator('#chart-y-label').innerText()).includes('Reaction time (ms)'));
    assert.notEqual(await core.locator('[data-chart-point]').first().getAttribute('data-value'), correctedMean);
    await correction.press('Enter');
    await core.locator('#table-region[aria-busy="false"]').waitFor();
    assert.equal(await correction.getAttribute('aria-checked'), 'true');
    assert.equal(await core.locator('[data-chart-point]').first().getAttribute('data-value'), correctedMean);
    assert.equal(await core.locator('[data-sd-whisker]').first().getAttribute('data-sd'), correctedSD);
    assert((await core.locator('#chart-y-label').innerText()).includes('Baseline − RT (ms)'));
    assert(await core.locator('.chart-tick').allTextContents().then(ticks => ticks.includes('0')), 'Corrected plots must label the zero reference');
    const [correctedDownload] = await Promise.all([page.waitForEvent('download'), core.locator('#export').click()]);
    const correctedStream = await correctedDownload.createReadStream(), correctedChunks = [];
    for await (const chunk of correctedStream) correctedChunks.push(chunk);
    const correctedCSV = Buffer.concat(correctedChunks).toString('utf8');
    assert(correctedCSV.includes('baseline_benefit_ms') && correctedCSV.includes(correctedMean));
    assert(!correctedCSV.includes('corrected_rt_ms'), 'CSV names the reversed measure explicitly');
    await correction.click();
    await core.locator('#table-region[aria-busy="false"]').waitFor();
    await core.locator('#core-spread').selectOption('mean');
    assert.equal(await core.locator('[data-sd-whisker]').count(), 0);
    assert(!(await core.locator('tbody td').nth(1).innerText()).includes('±'));
    await core.locator('#core-spread').selectOption('sd');
    assert.equal(await core.locator('[data-sd-whisker]').count(), 20);
    assert((await core.locator('tbody td').nth(1).innerText()).includes('±'));
    const [download] = await Promise.all([page.waitForEvent('download'), core.locator('#export').click()]);
    const stream = await download.createReadStream(), chunks = [];
    for await (const chunk of stream) chunks.push(chunk);
    const exported = Buffer.concat(chunks).toString('utf8');
    assert(exported.includes('reaction_time_ms') && !exported.includes('corrected_rt_ms'));
    assert(exported.includes(' · SD') && exported.includes(' · n'));
    assert.equal(exported.trim().split('\n').length, 6);
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
      await core.locator('html[data-pretext="1.0.0"]').waitFor();
      assert(await core.locator('#core-controls [data-fit-label]').evaluateAll(labels => labels.every(label => Number(label.dataset.naturalWidth) > 0)), 'New labels use real Pretext measurement');
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
      if (!await page.locator('.contents details').evaluate(menu => menu.open)) await page.locator('.contents summary').click();
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
    const phone = await browser.newContext({ viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true });
    const touchPage = await phone.newPage();
    touchPage.on('pageerror', error => errors.push(error.message));
    await touchPage.goto(new URL('#data', base).href);
    const touchCore = touchPage.frameLocator('#core-pivot');
    await touchCore.locator('#table-region[aria-busy="false"]').waitFor();
    await touchCore.getByRole('checkbox', { name: 'Control', exact: true }).tap();
    await touchCore.locator('#table-region[aria-busy="false"]').waitFor();
    assert.equal(await touchCore.locator('[data-chart-point]').count(), 10);
    await touchCore.getByRole('switch', { name: 'Normalize RT', exact: true }).tap();
    await touchCore.locator('#table-region[aria-busy="false"]').waitFor();
    assert((await touchCore.locator('#chart-y-label').innerText()).includes('(0–1)'));
    await touchCore.locator('#core-controls').screenshot({ path: '.for-ai-local/core-checkboxes-phone.png' });
    await phone.close();
    assert.deepEqual(errors, []);
    console.log('PASS: fixed SOA, all 16 condition/phase selections, native/touch/keyboard checkboxes, raw/corrected trial-based 0–1 and z-scores with CSV, linked summaries/SD/zero scale, cohort/style, embedded reflow/settings, links, navigation, Pretext, four viewports, 200% text and spacing.');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
