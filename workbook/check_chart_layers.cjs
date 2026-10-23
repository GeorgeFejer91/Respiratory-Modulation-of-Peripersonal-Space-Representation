// Production build: NODE_PATH=<Playwright packages> node workbook/check_chart_layers.cjs <pivot URL>
const { chromium } = require('playwright');
const assert = require('node:assert/strict');

(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1280, height: 900 }, hasTouch: true });
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    const base = new URL(process.argv[2] || 'http://127.0.0.1:8767/pivot/');
    base.searchParams.set('view', 'core');
    await page.goto(base.href);
    const ready = () => page.locator('#table-region[aria-busy="false"]').waitFor();
    await ready();
    const keys = ['summary', 'line', 'dots', 'spaghetti', 'violin', 'errors'];
    assert.equal(await page.getByRole('group', { name: 'Graph display', exact: true }).count(), 1);
    assert.equal(await page.getByRole('group', { name: 'Error bars / whiskers', exact: true }).count(), 1);
    assert.equal(await page.getByRole('button', { name: 'Mean points', exact: true }).count(), 1);
    const toggle = key => page.locator(`[data-chart-layer="${key}"]`);
    const set = async (key, active) => {
      if ((await toggle(key).getAttribute('aria-pressed') === 'true') !== active) await toggle(key).click();
    };
    const download = async selector => {
      const [file] = await Promise.all([page.waitForEvent('download'), page.locator(selector).click()]);
      const chunks = []; for await (const chunk of await file.createReadStream()) chunks.push(chunk);
      return Buffer.concat(chunks).toString('utf8');
    };
    const originalCSV = await download('#export');
    await toggle('errors').hover();
    assert.equal(await toggle('errors').evaluate(node => getComputedStyle(node).backgroundColor),
      await toggle('summary').evaluate(node => getComputedStyle(node).backgroundColor), 'Selected whiskers keep their contrast on hover');
    for (let mask = 0; mask < 64; mask++) {
      for (const [i, key] of keys.entries()) await set(key, Boolean(mask & 1 << i));
      assert.equal(await page.locator('[data-chart-point]').count(), mask & 1 ? 20 : 0);
      assert.equal(await page.locator('[data-sd-whisker]').count(), mask & 32 ? 20 : 0);
      assert.equal(await page.locator('[data-line]').count(), mask & 2 ? 4 : 0);
      assert.equal(await page.locator('[data-participant-point]').count(), mask & 12 ? 800 : 0);
      assert.equal(await page.locator('[data-spaghetti]').count(), mask & 8 ? 160 : 0);
      assert.equal(await page.locator('[data-violin]').count(), mask & 16 ? 20 : 0);
      if (mask) assert.equal(await page.locator('[data-zero-baseline]').count(), 1);
      else assert.match(await page.locator('#chart-hover').innerText(), /Choose at least one/);
    }
    assert.equal(await download('#export'), originalCSV, 'Presentation must never change summary data');
    const csv = await download('#chart-data-export');
    assert.equal(csv.trim().split('\n').length, 801);
    assert.match(csv.split('\n')[0], /participant_id.*soa_ms.*condition.*phase.*baseline_benefit_ms/);
    assert(!csv.includes('P011') && !csv.includes('P033'));
    await set('summary', false); await set('line', false); await set('violin', false);
    assert.equal(await page.locator('[data-sd-whisker]').count(), 20, 'Whiskers are independent of mean points/lines');
    await page.locator('[data-error-whisker]').first().focus(); await page.keyboard.press('Enter');
    assert.match(await page.locator('#chart-hover').innerText(), /SD:/);
    await page.keyboard.press('Escape');
    for (const metric of ['se', 'ci95', 'mean', 'sd']) {
      await page.locator('#core-spread').selectOption(metric);
      assert.equal(await page.locator('[data-chart-point]').count(), 0);
      assert.equal(await page.locator('[data-error-whisker]').count(), metric === 'mean' ? 0 : 20);
    }
    await set('errors', false);
    assert.match(await page.locator('#chart-note').innerText(), /Error whiskers are hidden/);
    const dot = page.locator('[data-participant-point]').first();
    await dot.focus(); await page.keyboard.press('ArrowRight');
    assert.match(await page.locator('#chart-hover').innerText(), /P\d+.*Participant mean/);
    // The topmost dot is touchable; covered observations remain reachable by arrows/CSV.
    await page.locator('[data-participant-point]').last().tap();
    assert.match(await page.locator('#chart-hover').innerText(), /Participant mean/);
    await toggle('dots').focus(); await page.keyboard.press('Space');
    assert.equal(await toggle('dots').getAttribute('aria-pressed'), 'false');
    await page.keyboard.press('Enter'); assert.equal(await toggle('dots').getAttribute('aria-pressed'), 'true');
    for (const method of ['norm', 'z']) {
      await page.locator('#core-normalization-method').selectOption(method); await ready();
      await page.getByRole('switch', { name: 'Normalize RT', exact: true }).click(); await ready();
      for (const corrected of [false, true]) {
        await page.getByRole('switch', { name: 'Baseline correction', exact: true }).click(); await ready();
        assert.equal(await page.locator('[data-participant-point]').count(), 800);
        assert.match((await download('#chart-data-export')).split('\n')[0], new RegExp((corrected ? 'baseline_benefit_' : 'reaction_time_') + method));
      }
      await page.getByRole('switch', { name: 'Normalize RT', exact: true }).click(); await ready();
    }
    for (const [condition, phase, series] of [[false,false,1],[true,false,2],[false,true,2],[true,true,4]]) {
      await page.getByRole('checkbox', { name: 'Condition', exact: true }).setChecked(condition);
      await page.getByRole('checkbox', { name: 'Phase', exact: true }).setChecked(phase); await ready();
      assert.equal(await page.locator('[data-participant-point]').count(), series * 200);
      assert.equal(await page.locator('[data-spaghetti]').count(), series * 40);
    }
    for (const key of keys) await set(key, true);
    for (const [width,height] of [[320,568],[375,667],[640,360],[768,1024],[799,360],[801,1024],[1280,800],[1920,1080]]) {
      await page.setViewportSize({ width, height });
      for (const mode of ['normal','large','spacing']) {
        const style = await page.addStyleTag({ content: mode === 'large' ? 'html{font-size:200%!important}' : mode === 'spacing' ?
          '*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}' : 'html{}' });
        await page.waitForTimeout(100);
        await page.waitForFunction(() => [...document.querySelectorAll('#chart-layers [data-fit-label]')].every(label => +label.dataset.naturalWidth > 0));
        assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), `${width} ${mode} page overflow`);
        assert(await page.locator('#chart-layers [data-fit-label]').evaluateAll(labels => labels.every(label => label.scrollWidth <= label.clientWidth + 1)), `${width} ${mode} label overflow`);
        assert(await page.locator('[data-participant-point]').evaluateAll(nodes => nodes.every(node => {
          const box = node.ownerSVGElement.viewBox.baseVal;
          return +node.getAttribute('cy') >= 0 && +node.getAttribute('cy') <= box.height;
        })), 'All participant values fit the y extent');
        await style.evaluate(node => node.remove());
      }
    }
    const conditionLabel = page.locator('[data-group-field="condition"] + span');
    const summaryLabel = toggle('summary');
    await conditionLabel.evaluate(label => { label.textContent = 'Versuchsbedingung und Gruppenzuordnung'; });
    await summaryLabel.evaluate(label => { label.textContent = 'Participant-weighted mean response points'; });
    for (const width of [320,801,1920]) {
      await page.setViewportSize({ width, height: 800 });
      await page.evaluate(() => document.dispatchEvent(new Event('pivot-layout')));
      await page.waitForTimeout(100);
      const noFit = await page.locator('#core-controls [data-fit-label],#chart-layers [data-fit-label]').evaluateAll(labels => labels.filter(label =>
        !Number(label.dataset.naturalWidth) || label.scrollWidth > label.clientWidth + 1).map(label => ({text:label.textContent, width:label.clientWidth, scroll:label.scrollWidth, natural:label.dataset.naturalWidth})));
      assert.deepEqual(noFit, [], `${width}: Long labels retain measured full-text access`);
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
    }
    // Missing observations break pairing; small/constant groups have no invented density.
    const fixture = await browser.newPage();
    const frame = { columns:['participant_id','condition','phase','soa_ms','reaction_time_ms','corrected_rt_ms'],
      numeric:['soa_ms','reaction_time_ms','corrected_rt_ms'], rows:[
        ['P000','Control','Exhale',300,10,2], ['P000','Control','Exhale',800,null,null], ['P000','Control','Exhale',1500,0,0],
        ['P001','Control','Exhale',300,10,2], ['P002','Control','Exhale',300,10,2]] };
    await fixture.route('**/data/means-core-preview.json', route => route.fulfill({ json: frame }));
    await fixture.goto(base.href); await fixture.locator('#table-region[aria-busy="false"]').waitFor();
    await fixture.locator('[data-chart-layer="spaghetti"]').click();
    await fixture.locator('[data-chart-layer="violin"]').click();
    assert.equal(await fixture.locator('[data-violin]').count(), 0);
    assert.equal((await fixture.locator('[data-spaghetti][data-participant="P000"]').getAttribute('d')).match(/M/g).length, 2);
    assert.equal(await fixture.locator('[data-participant-point][data-value="0"]').count(), 1);
    assert.match(await fixture.locator('#chart-note').innerText(), /n < 3 or zero SD/);
    await fixture.close();
    assert.deepEqual(errors, []);
    console.log('Figure layers pass: 64 independent display/whisker combinations, participant CSV, pairing/gaps, KDE edge cases, normalization/grouping, keyboard/touch, eight viewports, long labels, 200% text, spacing and real Pretext.');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
