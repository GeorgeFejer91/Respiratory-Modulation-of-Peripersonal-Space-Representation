// Run against an HTTP-served production build with Playwright in NODE_PATH.
const { chromium } = require('playwright');
const assert = require('node:assert/strict');

(async () => {
  const base = process.argv[2] || 'http://127.0.0.1:8771/';
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ permissions: ['clipboard-read', 'clipboard-write'] });
  try {
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    const copied = () => page.evaluate(() => navigator.clipboard.readText());
    const ready = () => page.waitForFunction(() => document.querySelector('#table-region').getAttribute('aria-busy') === 'false');
    const cell = (row, column) => page.locator('#pivot-table tr').nth(row).locator('th,td').nth(column);
    for (const suffix of ['pivot/', 'pivot/?view=core']) {
      await page.goto(new URL(suffix, base).href); await ready();
      assert.equal(await page.locator('#pivot-table').getAttribute('role'), 'grid', 'The result must support cell selection');
      assert(await page.locator('#copy-selection').isDisabled());
      await cell(0, 0).focus(); await page.keyboard.press('Shift+ArrowDown');
      assert.equal(await page.locator('[aria-selected=true]').count(), 2, 'Keyboard range starts at the focused cell');
      await cell(1, 1).click(); await cell(2, 2).click({ modifiers: ['Shift'] });
      assert.equal(await page.locator('[aria-selected=true]').count(), 4);
      await page.keyboard.press('Control+c');
      const expected = await page.locator('#pivot-table').evaluate(table => [1, 2].map(r => [1, 2].map(c => table.rows[r].cells[c].dataset.copyValue).join('\t')).join('\r\n'));
      assert.equal(await copied(), expected, 'A rectangle must paste as two Excel rows and two columns');
      await page.locator('#copy-selection').click(); assert.equal(await copied(), expected);
      await cell(1, 1).click(); await page.keyboard.press('Shift+ArrowRight'); await page.keyboard.press('Shift+ArrowDown');
      assert.equal(await page.locator('[aria-selected=true]').count(), 4);
      await page.keyboard.press('Control+c'); assert.equal(await copied(), expected);
      await page.keyboard.press('Escape'); assert.equal(await page.locator('[aria-selected=true]').count(), 0);
      // Dragging in either direction selects a rectangle, not text fragments.
      const start = await cell(2, 2).boundingBox(), end = await cell(1, 1).boundingBox();
      await page.mouse.move(start.x + start.width / 2, start.y + start.height / 2); await page.mouse.down();
      await page.mouse.move(end.x + end.width / 2, end.y + end.height / 2, { steps: 8 }); await page.mouse.up();
      assert.equal(await page.locator('[aria-selected=true]').count(), 4);
      await page.keyboard.press('Control+c'); assert.equal(await copied(), expected);
      await page.locator('#select-all-cells').click();
      const cells = await page.locator('#pivot-table th,#pivot-table td').count();
      assert.equal(await page.locator('[aria-selected=true]').count(), cells);
      await page.locator('#settings-open').click();
      await page.locator('#aggregation').selectOption('Median'); await ready();
      await page.locator('#settings-form button[type=submit]').click();
      assert.equal(await page.locator('[aria-selected=true]').count(), 0, 'New results must clear stale selections');
    }
    // Raw values, zero and missing cells retain their positions.
    const fixture = { columns: ['participant_id','condition','phase','soa_ms','corrected_rt_ms'], numeric: ['soa_ms','corrected_rt_ms'],
      rows: [['P0','Control','Exhale',300,1.234567891234],['P0','Control','Exhale',800,0],['P0','Control','Exhale',1500,null]] };
    await page.route('**/data/means-preview.json', route => route.fulfill({ json: fixture }));
    await page.goto(new URL('pivot/', base).href); await ready();
    await cell(1, 1).click(); await cell(3, 1).click({ modifiers: ['Shift'] });
    await page.keyboard.press('Control+c'); assert.equal(await copied(), '1.234567891234\r\n0\r\n');
    // Same-origin iframe in the actual paper, including a denied async clipboard.
    await page.goto(base);
    const embed = page.frameLocator('iframe').first();
    await embed.locator('#pivot-table tbody tr').first().waitFor();
    await embed.locator('#pivot-table tbody td').first().click();
    const frame = page.frames().find(frame => frame.url().includes('view=core'));
    await frame.evaluate(() => { navigator.clipboard.writeText = () => Promise.reject(new Error('Denied')); });
    await embed.locator('#copy-selection').click();
    assert.equal(await copied(), '300', 'Copy must work inside the paper even when async clipboard access is denied');
    // Touch taps can extend a range while native panning remains available.
    const touch = await browser.newPage({ viewport: { width: 375, height: 667 }, hasTouch: true });
    await touch.goto(new URL('pivot/?view=core', base).href);
    await touch.locator('#pivot-table tbody tr').first().waitFor();
    await touch.locator('#pivot-table tbody tr').nth(0).locator('td').nth(0).tap();
    await touch.locator('#extend-selection').tap();
    await touch.locator('#pivot-table tbody tr').nth(1).locator('td').nth(0).tap();
    assert.equal(await touch.locator('[aria-selected=true]').count(), 2);
    for (const width of [320, 640, 1280]) {
      await touch.setViewportSize({ width, height: 667 });
      await touch.waitForFunction(() => document.querySelector('#copy-selection').dataset.naturalWidth);
      assert(await touch.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
    }
    assert.deepEqual(errors, []);
    await page.goto(new URL('pivot/?view=core', base).href); await ready();
    await cell(1, 1).click(); await cell(2, 2).click({ modifiers: ['Shift'] });
    await page.screenshot({ path: '.for-ai-local/table-copy-desktop.png', fullPage: true });
    await touch.setViewportSize({ width: 375, height: 667 });
    await touch.screenshot({ path: '.for-ai-local/table-copy-phone.png', fullPage: true });
    console.log('Table copy passes: mouse/keyboard/touch ranges, raw precision, zero/missing, reset, select all, real clipboard and embedded fallback.');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
