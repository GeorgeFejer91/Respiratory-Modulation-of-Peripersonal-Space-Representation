// Serve a production build, then run with Playwright available in NODE_PATH.
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

async function checkQuestionnaireDetails(page, base) {
  const figure = page.getByRole('figure', { name: /Baseline MAIA-2/ });
  assert.equal(await figure.getByRole('listitem').count(), 8);
  const details = page.locator('#questionnaire-scores');
  const trigger = details.locator(':scope > summary');
  await page.waitForFunction(() => Number(document.querySelector('#questionnaire-scores summary span').dataset.naturalWidth) > 0);
  const itemTrigger = details.locator('#questionnaire-items summary');
  const chooser = details.getByRole('combobox', { name: 'Participant' });
  assert(!await chooser.isVisible());
  const [response] = await Promise.all([
    page.waitForResponse(new URL('questionnaire-data.json', base).href),
    trigger.press('Enter'),
  ]);
  const { scales, participants } = await response.json();
  assert.equal(participants.length, 42);
  await chooser.waitFor();
  assert.equal(await chooser.locator('option').count(), participants.length);
  assert.equal(await details.locator('#maia-items dd:visible').count(), 0);
  await itemTrigger.press('Enter');
  await details.locator('#maia-items dd').last().waitFor();
  assert.equal(await details.locator('#maia-items dd').count(), 37);
  const fields = [...scales.map(scale => scale.field), ...scales.flatMap(scale => scale.items)
    .map(item => 'maia2_item_' + String(item).padStart(2, '0'))];
  for (const person of [participants[0], participants.find(row => row.maia2_noticing === '')]) {
    await chooser.selectOption(person.participant_id);
    for (const field of fields) {
      assert.equal(await details.locator(`[data-field="${field}"]`).innerText(), person[field] || 'Missing');
    }
    for (const field of ['spfrref_control', 'spfrref_viscereality']) {
      assert.equal(await details.locator(`[data-field="${field}"]`).innerText(),
        person[field] ? `${person[field]} (${person[field + '_ordinal']})` : 'Missing');
    }
  }
  await chooser.selectOption(participants[0].participant_id);
  assert.equal(await page.locator('#questionnaire-items[open]').count(), 1);
  const [download] = await Promise.all([page.waitForEvent('download'),
    page.getByRole('link', { name: 'Download the released participant scores and responses (CSV)' }).click()]);
  assert.deepEqual(fs.readFileSync(await download.path()),
    fs.readFileSync(path.join(__dirname, '../data/raw/study5_participants.csv')));
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage();
    const base = process.argv[2] || 'http://127.0.0.1:8766/';
    const errors = [];
    let questionnaireRequests = 0;
    page.on('request', request => {
      if (request.url() === new URL('questionnaire-data.json', base).href) questionnaireRequests++;
    });
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(base);
    await page.waitForFunction(() => document.querySelector('header [data-measure]').dataset.fit === 'fit');
    const paperSections = ['abstract', 'introduction', 'methods', 'results', 'discussion', 'reproducibility', 'references'];
    assert.deepEqual(await page.locator('main > section').evaluateAll(sections => sections.map(section => section.id)),
      paperSections, 'The live overview has the full article in reading order');
    assert.deepEqual(await page.locator('#results > section').evaluateAll(sections => sections.map(section => section.id)),
      ['baseline', 'phase', 'blocks', 'shape', 'parameters', 'effects', 'sensitivity', 'averages', 'questionnaires', 'data']);
    assert.equal(await page.locator('.article-header a[href="https://aspredicted.org/az9f89.pdf"]').count(), 1);
    assert.match(await page.locator('.article-header').innerText(), /BIAL Foundation/);
    assert.match(await page.locator('#article-citation').innerText(), /Fejer, G., Holzapfel, T., Gaebler, M., & Lenggenhager, B\. \(2026\)/);
    assert.deepEqual(await page.locator('.contents a, main a[data-citation]').evaluateAll(links => links
      .filter(link => !document.getElementById(link.hash.slice(1))).map(link => link.hash)), []);
    await page.getByRole('region', { name: 'Spatial frame of reference after Viscereality and Control' }).waitFor();
    const spatialFigure = page.getByRole('figure', { name: /Paired spatial-frame ratings/ });
    assert.equal(await spatialFigure.getByRole('listitem').count(), 3);
    assert.deepEqual(await spatialFigure.getByRole('listitem').allTextContents(),
      ['More spatially extended (22)', 'Same category (13)', 'Less spatially extended (6)']);
    assert.match(await page.locator('#spatial-frame').innerText(), /exact 95% CI 59.0%–91.7%.*p = 0.00372/);
    assert.match(await page.locator('#spatial-frame').innerText(), /Spearman ρ = 0.376/);
    await page.waitForFunction(() => [...document.querySelectorAll('#spatial-frame [data-measure]')]
      .every(label => Number(label.dataset.naturalWidth) > 0));
    assert(await spatialFigure.locator('.spatial-bar').evaluateAll(bars => bars.every(bar => {
      const count = Number(bar.closest('li').dataset.count);
      return Math.abs(bar.getBoundingClientRect().width - bar.parentElement.clientWidth * count / 41) < 1;
    })), 'Bar widths reproduce the plotted counts on a shared 0–41 scale');
    const spatialResize = spatialFigure.getByRole('separator', { name: /^Figure 4 width/ });
    const originalWidth = await spatialResize.getAttribute('aria-valuenow');
    await spatialResize.press('ArrowLeft');
    await page.waitForFunction(original => Number(document.querySelector('#spatial-frame-figure [role="separator"]').getAttribute('aria-valuenow')) < Number(original), originalWidth);
    await spatialResize.press('Home');
    const noScript = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 320, height: 568 } });
    const noScriptPage = await noScript.newPage();
    await noScriptPage.goto(new URL('#spatial-frame', base).href);
    assert.equal(await noScriptPage.locator('#spatial-frame-figure .spatial-bar').count(), 3);
    assert.equal(await noScriptPage.locator('#maia-summary .spatial-bar').count(), 8);
    await noScript.close();
    assert.equal(questionnaireRequests, 0, 'Original values load on demand');
    await checkQuestionnaireDetails(page, base);
    assert.match(await page.locator('#blocks-answer').innerText(), /no clear systematic RT decline/);
    assert.match(await page.locator('#blocks-answer').innerText(), /−0.12 ms per block.*p = .840/);
    await page.locator('#blocks-figure[data-interactive="ready"]').waitFor();
    const blockResults = await (await page.request.get(new URL('results/block_rt/results.json', base).href)).json();
    assert.equal(blockResults.tests.linear_ms_per_block.n, 39);
    assert.equal(blockResults.measure, 'corrected_rt_ms');
    assert.match(await page.locator('#blocks-figure .figure-note').innerText(), /AT − matched Baseline RT/);
    assert(blockResults.tests.linear_ms_per_block.ci_low_ms < 0 && blockResults.tests.linear_ms_per_block.ci_high_ms > 0);
    const [blockDownload] = await Promise.all([page.waitForEvent('download'), page.locator('#blocks-data-export').click()]);
    const blockStream = await blockDownload.createReadStream(), blockChunks = [];
    for await (const chunk of blockStream) blockChunks.push(chunk);
    assert.deepEqual(Buffer.concat(blockChunks), fs.readFileSync(path.join(__dirname, '../results/block_rt/summary.csv')), 'Actual Segment 3 download matches verified block means');
    await page.waitForFunction(() => [...document.querySelectorAll('#blocks [data-measure]')].every(link => +link.dataset.naturalWidth > 0));
    assert.match(await page.locator('#phase-answer').innerText(), /18.47 ms slower during inhale/);
    assert.match(await page.locator('#phase-answer').innerText(), /corrected phase effect was inconclusive/);
    assert.equal(await page.locator('#phase > a, #phase > details').count(), 0, 'Keep the supplemental comparison and link list off the overview');
    await page.locator('#phase-figure[data-interactive="ready"]').waitFor();
    await page.locator('#phase-figure[data-interactive="ready"]').waitFor();
    assert.match(await page.locator('#phase-figure .figure-note').innerText(), /[Rr]ight of zero means slower during inhale/);
    assert.match(await page.locator('#phase-figure .figure-note').innerText(), /belt recordings are unavailable/);
    const phase = await (await page.request.get(new URL('results/phase_rt/results.json', base).href)).json();
    assert.equal(phase.primary_measure, 'corrected_rt_ms');
    assert.match(await page.locator('#phase-answer').innerText(), /^Raw audio–tactile responses/);
    assert.match(await page.locator('#phase-figure .figure-note').innerText(), /Rainclouds/);
    assert.equal(await page.locator('#phase-corrected-figure').count(), 0);
    assert(phase.phase_means.Inhale.mean > phase.phase_means.Exhale.mean);
    assert(phase.contrasts.reaction_time_ms.ci_low > 0);
    assert(phase.contrasts.corrected_rt_ms.ci_low < 0 && phase.contrasts.corrected_rt_ms.ci_high > 0);
    assert.deepEqual(phase.trial_groups.map(s => s.trial_group), ['AT 300 ms','AT 800 ms','AT 1500 ms','AT 2200 ms','AT 2700 ms','Baseline']);
    assert(phase.trial_groups.every(s => s.n === 40 && s.mean > 0));
    const phaseCsv = await page.request.get(new URL('results/phase_rt/trial_group_summary.csv', base).href);
    assert.deepEqual(await phaseCsv.body(), fs.readFileSync(path.join(__dirname, '../results/phase_rt/trial_group_summary.csv')), 'Archived Segment 2 CSV remains available');
    const research = await browser.newPage();
    await research.goto(new URL('literature_review/RESPIRATION_RT.html', base).href);
    assert.match(await research.locator('main').innerText(), /Multisensory synchrony-detection tasks/);
    assert.match(await research.locator('main').innerText(), /cannot be called a confirmation of a synchrony-detection result/);
    assert.equal(await research.locator('main table').count(), 0);
    const ledger = await (await research.request.get(new URL('literature_review/respiration_rt_sources.json', base).href)).json();
    assert.equal(ledger.sources.length, 12);
    for (const width of [320, 1280]) {
      await research.setViewportSize({width, height:800});
      assert(await research.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), `Research page ${width}px overflow`);
    }
    await research.close();
    assert.equal(await page.locator('#baseline-title').innerText(), 'Does reaction time differ across SOAs?');
    await page.locator('#soa-figure[data-interactive="ready"]').waitFor();
    const soa = await (await page.request.get(new URL('results/pps_soa/results.json', base).href)).json();
    assert.equal(await page.locator('#soa-statistics').innerText(), soa.apa);
    assert.equal(soa.anova.n, 40);
    assert.equal(soa.measure, 'corrected_rt_ms');
    assert.equal(await page.locator('main section[data-primary-measure="corrected_rt_ms"]').count(), 3);
    assert.match(await page.locator('#soa-figure .figure-note').innerText(), /AT − matched Baseline RT/);
    assert.equal(soa.execution, 'native Python; saved display in browser');
    assert((await page.request.get(new URL('results/pps_soa/results.zip', base).href)).ok());
    const [soaDownload] = await Promise.all([page.waitForEvent('download'), page.locator('.soa-downloads a[href$=".zip"]').click()]);
    const soaStream = await soaDownload.createReadStream(), soaChunks = [];
    for await (const chunk of soaStream) soaChunks.push(chunk);
    assert.deepEqual(Buffer.concat(soaChunks), fs.readFileSync(path.join(__dirname, '../results/pps_soa/results.zip')), 'Actual Segment 1 download matches verified local archive');
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
    const inputs = ['Condition', 'Phase'].map(name => core.getByRole('checkbox', { name, exact: true }));
    for (const [condition, phase, curves] of [[false, false, 1], [true, false, 2], [false, true, 2], [true, true, 4]]) {
      await inputs[0].setChecked(condition);
      await inputs[1].setChecked(phase);
      await core.locator('#table-region[aria-busy="false"]').waitFor();
      assert.equal(await core.locator('[data-chart-point]').count(), curves * 5, 'Unchecked factors pool observations instead of hiding them');
      assert.equal(await core.locator('tbody tr').count(), 5);
      assert.equal(await core.locator('html').getAttribute('data-record-count'), '800', 'Pooling retains every participant cell');
      assert(await core.locator('[data-sd-whisker]').evaluateAll(nodes => nodes.every(node => +node.dataset.n === 40)));
      assert.equal(await core.locator('#chart-x-label').innerText(), 'SOA (ms)');
      const legends = await core.locator('#chart-legend').innerText();
      assert.equal(legends.includes('Control'), condition);
      assert.equal(legends.includes('Exhale'), phase);
    }
    assert.equal(await core.locator('input[type="checkbox"]:visible').count(), 2);
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
        const individual = await core.locator('[data-chart-point][data-row="0"]').evaluateAll(nodes => nodes.map(node => +node.dataset.value));
        const normalized = await core.locator('[data-chart-point]').first().getAttribute('data-value');
        assert.notEqual(normalized, original);
        if (method === 'norm') assert(await core.locator('[data-chart-point]').evaluateAll(nodes => nodes.every(node => +node.dataset.value >= 0 && +node.dataset.value <= 1)));
        await inputs[1].uncheck();
        await core.locator('#table-region[aria-busy="false"]').waitFor();
        const pooled = await core.locator('[data-chart-point]').first().getAttribute('data-value');
        assert(Math.abs(+pooled - (individual[0] + individual[1]) / 2) < 1e-12, 'Pooled normalized curves average within participant, using the same normalization');
        assert.equal(await core.locator('html').getAttribute('data-record-count'), '800');
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
    assert.equal(await core.locator('thead th').count(), 9, 'Means and SDs have separate columns');
    assert.equal(await core.locator('tbody td').nth(2).getAttribute('data-copy-value'), await core.locator('[data-sd-whisker]').first().getAttribute('data-sd'));
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
        assert(await page.locator('#phase-figure').evaluate(figure => figure.scrollWidth <= figure.clientWidth + 1), `${width} ${mode} phase figure overflow`);
        assert(await page.locator('#blocks-figure').evaluate(figure => figure.scrollWidth <= figure.clientWidth + 1), `${width} ${mode} block figure overflow`);
        assert(await spatialFigure.evaluate(figure => figure.scrollWidth <= figure.clientWidth + 1
          && [...figure.querySelectorAll('[data-measure]')].every(label => label.scrollHeight <= label.clientHeight + 1)),
        `${width} ${mode} spatial figure overflow`);
        for (const region of ['#maia-summary', '#questionnaire-scores']) {
          assert(await page.locator(region).evaluate(node => node.scrollWidth <= node.clientWidth + 1
            && [...node.querySelectorAll('[data-measure]')].every(label =>
              +label.dataset.naturalWidth > 0 && label.scrollHeight <= label.clientHeight + 1)),
          `${width} ${mode} ${region} measurement or reflow failed`);
        }
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
      await page.locator('.contents a[href="#phase"]').click();
      await page.waitForFunction(() => document.querySelector('.contents a[href="#phase"]').hasAttribute('aria-current'));
      assert.equal(new URL(page.url()).hash, '#phase');
      if (!await page.locator('.contents details').evaluate(menu => menu.open)) await page.locator('.contents summary').click();
      await page.locator('.contents a[href="#blocks"]').click();
      await page.waitForFunction(() => document.querySelector('.contents a[href="#blocks"]').hasAttribute('aria-current'));
      assert.equal(new URL(page.url()).hash, '#blocks');
      if (!await page.locator('.contents details').evaluate(menu => menu.open)) await page.locator('.contents summary').click();
      await page.locator('.contents a[href="#questionnaires"]').click();
      await page.waitForFunction(() => document.querySelector('.contents a[href="#questionnaires"]').hasAttribute('aria-current'));
      assert.equal(new URL(page.url()).hash, '#questionnaires');
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
    const phone = await browser.newContext({ viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true, reducedMotion: 'reduce' });
    const touchPage = await phone.newPage();
    touchPage.on('pageerror', error => errors.push(error.message));
    await touchPage.goto(new URL('#data', base).href);
    const touchCore = touchPage.frameLocator('#core-pivot');
    await touchCore.locator('#table-region[aria-busy="false"]').waitFor();
    await touchCore.getByRole('checkbox', { name: 'Condition', exact: true }).tap();
    await touchCore.locator('#table-region[aria-busy="false"]').waitFor();
    assert.equal(await touchCore.locator('[data-chart-point]').count(), 10);
    await touchCore.getByRole('switch', { name: 'Normalize RT', exact: true }).tap();
    await touchCore.locator('#table-region[aria-busy="false"]').waitFor();
    assert((await touchCore.locator('#chart-y-label').innerText()).includes('(0–1)'));
    await touchCore.locator('#core-controls').screenshot({ path: '.for-ai-local/core-checkboxes-phone.png' });
    await touchPage.goto(new URL('#spatial-frame', base).href);
    await touchPage.locator('#spatial-frame-figure .resize-edge').waitFor();
    assert(await touchPage.locator('#spatial-frame-title').evaluate(title =>
      title.getBoundingClientRect().top >= document.querySelector('.contents').getBoundingClientRect().bottom),
    'The mobile deep link clears the sticky navigation');
    await touchPage.locator('#questionnaire-scores > summary').tap();
    await touchPage.getByRole('combobox', { name: 'Participant' }).waitFor();
    await touchPage.locator('#questionnaire-items > summary').tap();
    await touchPage.locator('#maia-items dd').last().waitFor();
    assert.equal(await touchPage.locator('#maia-items dd:visible').count(), 37);
    await phone.close();
    assert.deepEqual(errors, []);
    console.log('PASS: both questionnaire charts and no-script fallback, original scores/items/CSV, Segment 3 graph and CSV, complete article, pivot grouping and pooling, keyboard/touch, normalization and export, Pretext, four viewports, 200% text and spacing.');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
