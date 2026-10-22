// Optional rendered regression check. Requires Playwright + Chromium in NODE_PATH.
// Serve an audited build over HTTP, then: node workbook/check_pivot_browser.cjs URL
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const { pathToFileURL } = require('node:url');
const { join } = require('node:path');

async function check() {
  const base = process.argv[2] || 'http://127.0.0.1:8765/pivot/';
  const { pivot, csvText } = await import(pathToFileURL(join(__dirname, 'pivot_assets/pivot-engine.mjs')));
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  page.setDefaultTimeout(10000);
  const errors = [], requests = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('request', request => requests.push(request.url()));
  const ready = () => page.waitForFunction(() => document.querySelector('#table-region').getAttribute('aria-busy') === 'false' && !document.querySelector('#export').disabled);
  const count = async expected => { await ready(); await page.waitForFunction(value => document.documentElement.dataset.recordCount === String(value), expected); };
  const settings = async () => { if (!await page.locator('#settings').evaluate(element => element.open)) await page.locator('#settings-open').click(); };
  const close = id => page.locator(`#${id} [data-close="${id}"]`).click();
  const choose = async (axis, field, selected) => {
    await settings(); await page.locator(`#choose-${axis}`).click();
    await page.locator('#search').fill(field);
    await page.getByRole('checkbox', { name: field, exact: true }).setChecked(selected);
    await close('chooser'); await ready();
  };
  const filter = async (field, values) => {
    if (!await page.locator('#filters').evaluate(element => element.open)) await page.locator('#filters-open').click();
    await page.locator('#add-filter').click(); await page.locator('#search').fill(field);
    await page.getByRole('radio', { name: field, exact: true }).check();
    await page.waitForFunction(value => document.querySelector('#chooser-title').textContent === `Filter: ${value}`, field);
    for (const value of values) {
      await page.locator('#search').fill(String(value));
      await page.getByRole('checkbox', { name: String(value), exact: true }).check();
    }
    await close('chooser'); await close('filters'); await ready();
  };
  const download = async () => {
    const [file] = await Promise.all([page.waitForEvent('download'), page.locator('#export').click()]);
    const stream = await file.createReadStream(), chunks = [];
    for await (const chunk of stream) chunks.push(chunk);
    return Buffer.concat(chunks).toString('utf8');
  };
  try {
    await page.goto(base); await count(800);
    await page.waitForFunction(() => document.documentElement.dataset.pretext === '1.0.0');
    assert.equal(await page.locator('[data-chart-point]').count(), 20);
    assert(!requests.some(url => /data\/(means|trials|participants)\.json|catalog\.json|pyodide/.test(url)), 'Startup must remain lazy');
    const frame = await (await page.request.get(new URL('data/means.json', base).href)).json();
    const config = { rows: ['soa_ms'], columns: ['condition', 'phase'], values: ['corrected_rt_ms'], aggregation: 'Mean',
      totals: true, cohort: 'Primary behavioural cohort', filtersEnabled: false, filters: {} };
    assert.equal(await download(), csvText(pivot(frame, config)));
    // Invalid settings clear both views instead of leaving a stale chart.
    await settings(); await page.locator('#choose-values').click(); await page.locator('#search').fill('corrected_rt_ms');
    await page.getByRole('checkbox', {name:'corrected_rt_ms', exact:true}).uncheck(); await close('chooser');
    await page.locator('#error').waitFor({state:'visible'});
    assert.equal(await page.locator('[data-chart-point]').count(), 0);
    assert.equal(await page.locator('tbody tr').count(), 0);
    assert(await page.locator('#export').isDisabled());
    await choose('values', 'corrected_rt_ms', true); await page.locator('#settings-form button[type=submit]').click();
    await page.locator('#col-next').click();
    assert.equal(await page.locator('[data-chart-point]').count(), 20, 'Table pagination must not trim the chart');
    await page.locator('[data-chart-point]').first().focus();
    await page.keyboard.press('ArrowRight');
    assert((await page.locator('#chart-hover').innerText()).includes('800'));
    await page.locator('#chart-style').selectOption('bars');
    assert.equal(await page.locator('rect[data-chart-point]').count(), 20);
    await page.locator('#chart-style').selectOption('points');
    assert.equal(await page.locator('[data-line]').count(), 0);
    await page.locator('#chart-style').selectOption('auto');
    await page.locator('#filters-enabled').check();
    await filter('condition', ['Control']); await filter('soa_ms', [300, 1500]); await count(160);
    assert.equal(await page.locator('[data-chart-point]').count(), 4);
    assert.equal(await page.locator('#chart-legend li').count(), 2);
    config.filtersEnabled = true; config.filters = { condition: ['Control'], soa_ms: [300, 1500] };
    assert.equal(await download(), csvText(pivot(frame, config)));
    await page.locator('#filters-enabled').uncheck(); await count(800);
    await page.locator('#filters-enabled').check(); await count(160);
    const idIndex = frame.columns.indexOf('participant_id'), genderIndex = frame.columns.indexOf('gender');
    const gender = frame.rows.find(row => row[idIndex] === 'P000')[genderIndex];
    const otherGender = frame.rows.find(row => row[genderIndex] !== gender && row[genderIndex] !== null)[genderIndex];
    await filter('participant_id', ['P000']); await filter('gender', [otherGender]); await count(0);
    assert.equal(await page.locator('[data-chart-point]').count(), 0);
    assert((await page.locator('#chart-hover').innerText()).includes('No records'));
    await page.locator('#filters-open').click(); await page.locator('#clear-filters').click(); await close('filters'); await count(800);
    config.filters = {};
    await settings(); await page.locator('#aggregation').selectOption('Median'); await ready();
    assert((await page.locator('#chart-y-label').innerText()).startsWith('Median'));
    await page.locator('#settings-form button[type=submit]').click();
    config.aggregation = 'Median'; assert.equal(await download(), csvText(pivot(frame, config)));
    await choose('values', 'reaction_time_ms', true);
    await page.locator('#settings-form button[type=submit]').click();
    assert(await page.locator('#chart-measure-control').isVisible());
    await page.locator('#chart-measure').selectOption('reaction_time_ms');
    assert((await page.locator('#chart-y-label').innerText()).includes('Reaction time (ms)'));
    assert.equal(await page.locator('[data-chart-point]').count(), 20);
    await choose('columns', 'phase', false);
    assert.equal(await page.locator('#chart-legend li').count(), 2);
    await choose('rows', 'soa_ms', false); await choose('rows', 'distance_cm', true);
    assert.equal(await page.locator('#chart-x-label').innerText(), 'Distance (cm)');
    await page.locator('#aggregation').selectOption('Row count'); await ready();
    assert.equal(await page.locator('#chart-y-label').innerText(), 'Records');
    await page.locator('#source').selectOption('trials');
    await page.waitForFunction(() => document.querySelector('#status').textContent.startsWith('All trial records')); await ready();
    await page.locator('#settings-form button[type=submit]').click();
    await filter('trial_type', ['Baseline']);
    assert((await page.locator('#chart-hover').innerText()).includes('No numeric values'));
    assert.equal(await page.locator('[data-chart-point]').count(), 0);
    await settings(); await page.locator('#source').selectOption('means'); await count(800);
    await page.locator('#settings-form button[type=submit]').click();
    // Reversed network completion must retain the most recent source in both views.
    await page.reload(); await count(800);
    let delayed = 0;
    await page.route('**/data/trials.json', async route => { delayed++; await new Promise(resolve => setTimeout(resolve, 250)); await route.continue(); });
    await settings(); await page.locator('#source').selectOption('trials'); await page.locator('#source').selectOption('participants');
    await page.waitForFunction(() => document.querySelector('#status').textContent.startsWith('Participants and questionnaires')); await ready();
    await page.waitForTimeout(400);
    assert.equal(delayed, 1, 'The race check must actually delay an uncached trial request');
    assert.equal(await page.locator('#source').inputValue(), 'participants');
    assert((await page.locator('#chart-y-label').innerText()).includes('Age (years)'));
    await page.locator('#source').selectOption('saved');
    const catalog = await (await page.request.get(new URL('app/public/snapshots/catalog.json', base).href)).json();
    const entry = catalog.find(entry => entry.rows > 0 && entry.rows <= 20);
    await page.locator('#search').fill(entry.source);
    await page.getByRole('radio', { name: entry.source, exact: true }).check(); await ready();
    assert((await page.locator('#status').innerText()).includes(entry.source));
    await page.locator('#source').selectOption('means'); await count(800); await page.locator('#settings-form button[type=submit]').click();
    // Rendered text contract: page edges, labels, anchored modal and focus at small/large sizes.
    for (const [width, height] of [[320,568],[375,667],[640,360],[768,1024],[1280,800],[1920,1080]]) {
      await page.setViewportSize({ width, height });
      for (const enlarged of [false, true]) {
        await page.addStyleTag({ content: `html { font-size:${enlarged ? 200 : 100}% !important; }` });
        await page.waitForTimeout(100);
        await settings(); await page.waitForTimeout(100);
        const layout = await page.evaluate(() => {
          const modal = document.querySelector('#settings'), panel = modal.firstElementChild;
          const ticks = [...document.querySelectorAll('.chart-tick')].filter(element => element.getAttribute('text-anchor') === 'middle').map(element => element.getBoundingClientRect());
          return { page: document.documentElement.scrollWidth <= innerWidth + 1,
            panel: panel.scrollHeight <= panel.clientHeight + 1 && panel.scrollWidth <= panel.clientWidth + 1,
            ticks: ticks.every((box,index) => !index || box.left >= ticks[index-1].right),
            clipped: [...document.querySelectorAll('[data-fit-label]')].filter(element => element.getClientRects().length && element.scrollWidth > element.clientWidth + 1).map(element => element.id || element.textContent) };
        });
        assert(layout.page && layout.panel && layout.ticks && !layout.clipped.length, JSON.stringify({width,height,enlarged,layout}));
        await page.keyboard.press('Escape');
        assert.equal(await page.locator('#settings-open').evaluate(element => element === document.activeElement), true);
      }
    }
    await page.addStyleTag({ content: 'html{font-size:100%!important} *{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important} p{margin-bottom:2em!important}' });
    await page.setViewportSize({width:320,height:568}); await settings(); await page.waitForTimeout(200);
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
    await page.keyboard.press('Escape');
    // Missing cells break a line, while a genuine zero remains a point.
    const fixture = await browser.newPage({viewport:{width:375,height:667}});
    const data = {columns:['participant_id','condition','phase','soa_ms','corrected_rt_ms'],numeric:['soa_ms','corrected_rt_ms'],
      rows:[['P000','Control','Exhale',300,2],['P000','Control','Exhale',800,null],['P000','Control','Exhale',1500,0]]};
    await fixture.route('**/data/means-preview.json', route => route.fulfill({json:data}));
    await fixture.goto(base); await fixture.locator('[data-chart-point]').first().waitFor();
    assert.equal(await fixture.locator('[data-chart-point]').count(), 2);
    assert.equal((await fixture.locator('[data-line]').getAttribute('d')).match(/M/g).length, 2);
    assert.equal(await fixture.locator('[data-chart-point][data-value="0"]').count(), 1);
    data.rows = Array.from({length:101}, (_,index) => ['P000','Control','Exhale',index,index]);
    await fixture.reload(); await fixture.waitForFunction(() => document.querySelector('#chart-hover').textContent.includes('too dense'));
    assert.equal(await fixture.locator('[data-chart-point]').count(), 0);
    assert.equal(await fixture.locator('#export').isEnabled(), true);
    await fixture.route('**/vendor/pretext/**', route => route.abort());
    await fixture.reload(); await fixture.waitForFunction(() => document.documentElement.dataset.pretext === 'unavailable');
    await fixture.locator('#settings-open').click();
    assert.equal(await fixture.locator('#settings').evaluate(element => element.firstElementChild.scrollHeight <= element.firstElementChild.clientHeight + 1), true);
    await fixture.close();
    assert.deepEqual(errors, []);
    console.log('Browser checks pass: linked cells/CSV, filters and empty/missing states, summaries, grouping, multiple measures, sources/races, keyboard, six viewports, 200% text and spacing.');
  } finally { await browser.close(); }
}
check().catch(error => { console.error(error); process.exitCode = 1; });
