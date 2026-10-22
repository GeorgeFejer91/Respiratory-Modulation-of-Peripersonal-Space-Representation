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
    async function remove(field) {
      await core.locator(`.field-area button[data-field="${field}"]`).click();
      await core.locator('#field-remove').click();
      await core.locator('#table-region[aria-busy="false"]').waitFor();
    }
    async function add(field) {
      await core.locator(`#field-available button[data-field="${field}"]`).click();
      await core.locator('#table-region[aria-busy="false"]').waitFor();
    }
    await remove('condition');
    assert.equal(await core.locator('[data-chart-point]').count(), 10);
    await remove('phase');
    assert.equal(await core.locator('[data-chart-point]').count(), 5);
    const rawStarted = Date.now();
    await remove('soa_ms');
    assert(await correction.isDisabled(), 'Ungrouped records preserve their original fields');
    assert.equal(await core.locator('#chart-region').isVisible(), false);
    const rawRecords = +(await core.locator('html').getAttribute('data-record-count'));
    assert(rawRecords > 15000);
    assert.equal(await core.locator('tbody tr').count(), rawRecords);
    console.log(`Raw trial view: ${rawRecords} rows rendered in ${Date.now() - rawStarted} ms (single local/runtime observation).`);
    const [rawDownload] = await Promise.all([page.waitForEvent('download'), core.locator('#export').click()]);
    const rawStream = await rawDownload.createReadStream(), rawChunks = [];
    for await (const chunk of rawStream) rawChunks.push(chunk);
    const rawCSV = Buffer.concat(rawChunks).toString('utf8');
    assert(rawCSV.includes('trial_id') && rawCSV.includes('retained_global'));
    assert.equal(rawCSV.trim().split('\n').length, rawRecords + 1);
    await add('condition');
    assert.equal(await core.locator('[data-chart-point]').count(), 2, 'Condition-only summary pools SOAs within person');
    await add('phase');
    assert.equal(await core.locator('[data-chart-point]').count(), 4);
    await add('soa_ms');
    assert.equal(await core.locator('[data-chart-point]').count(), 20);
    // Move a field between areas by keyboard/touch actions, then reorder it.
    await core.locator('#field-columns button[data-field="condition"]').press('Enter');
    await core.locator('#field-to-rows').click();
    await core.locator('#table-region[aria-busy="false"]').waitFor();
    assert.equal(await core.locator('tbody tr').count(), 10);
    assert.equal(await core.locator('[data-chart-point]').count(), 20);
    await core.locator('#field-rows button[data-field="condition"]').click();
    await core.locator('#field-to-columns').click();
    await core.locator('#table-region[aria-busy="false"]').waitFor();
    await core.locator('#field-columns button[data-field="condition"]').click();
    await core.locator('#field-up').click();
    await core.locator('#table-region[aria-busy="false"]').waitFor();
    assert.equal(await core.locator('#field-columns button').first().getAttribute('data-field'), 'condition');
    // Actual native drag path, with the same move available through the menu.
    await core.locator('#field-columns button[data-field="phase"]').dragTo(core.locator('#field-rows'));
    await core.locator('#table-region[aria-busy="false"]').waitFor();
    assert.equal(await core.locator('#field-rows button[data-field="phase"]').count(), 1);
    await core.locator('#field-rows button[data-field="phase"]').click();
    await core.locator('#field-to-columns').click();
    await core.locator('#table-region[aria-busy="false"]').waitFor();
    assert(await core.locator('[data-sd-whisker]').evaluateAll(nodes => nodes.every(node => +node.dataset.n === 40 && +node.dataset.high > +node.dataset.low)));
    assert.equal(await core.locator('input[type="checkbox"]:visible').count(), 0);
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
    await core.locator('#core-filter').click();
    await core.locator('#filters-open').click();
    await core.locator('#add-filter').click();
    await core.locator('#choices').getByRole('button', {name:'Condition', exact:true}).click();
    await core.locator('#choices').getByRole('button', {name:'Control', exact:true}).click();
    await core.locator('#chooser [data-close="chooser"]').click();
    await core.locator('#filters [data-close="filters"]').click();
    await core.locator('html[data-record-count="400"]').waitFor();
    assert.equal(await core.locator('[data-chart-point]').count(), 10);
    await core.locator('#core-filter').click();
    await core.locator('html[data-record-count="800"]').waitFor();
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
    await core.locator('#pivot-clear').click();
    await core.locator('html[data-record-count="17114"]').waitFor();
    assert.equal(await core.locator('tbody tr').count(), 17114);
    await add('soa_ms');
    await core.locator('html[data-record-count="840"]').waitFor();
    await core.locator('#settings-open').click();
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
    assert.deepEqual(errors, []);
    console.log('PASS: field list, native drag and keyboard moves/reordering, raw record table/CSV, linked summaries/SD/zero scale, cohort/style, embedded reflow/settings, links, navigation, Pretext, four viewports, 200% text and spacing.');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
