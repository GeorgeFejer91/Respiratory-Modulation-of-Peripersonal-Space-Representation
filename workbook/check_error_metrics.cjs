// Production build; Playwright in NODE_PATH. Checks separate numeric error cells.
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage({ hasTouch: true, permissions: ['clipboard-read', 'clipboard-write'] });
    await page.goto(new URL('pivot/?view=core', process.argv[2] || 'http://127.0.0.1:8771/').href);
    await page.locator('#table-region[aria-busy="false"]').waitFor();
    assert.equal(await page.getByRole('combobox', { name:'Error metric', exact: true }).count(), 1, 'Independent error metric selector');
    const select = page.getByRole('combobox', { name:'Error metric', exact: true });
    let originalCSV;
    for (const [mode, columns, whiskers] of [['sd',9,20],['se',9,20],['ci95',13,20],['mean',5,0]]) {
      await select.selectOption(mode);
      assert.equal(await page.locator('#pivot-table thead th').count(), columns);
      assert.equal(await page.locator('[data-error-whisker]').count(), whiskers);
      assert(await page.locator('#pivot-table tbody tr').evaluateAll(rows => rows.every(row => [...row.cells].every(cell => !cell.textContent.includes('±')))));
      const point = JSON.parse(await page.locator('[data-chart-point]').first().getAttribute('data-point-detail'));
      const row = await page.locator('#pivot-table tbody tr').first().locator('td').evaluateAll(cells => cells.map(cell => cell.dataset.copyValue));
      assert.equal(Number(row[1]), point['Mean · Baseline − RT (ms)']);
      if (mode !== 'mean') {
        const path = page.locator('[data-error-whisker]').first();
        const low = Number(await path.getAttribute('data-low')), high = Number(await path.getAttribute('data-high'));
        if (mode === 'ci95') { assert.equal(Number(row[2]), low); assert.equal(Number(row[3]), high); }
        else assert(Math.abs((high-low)/2 - Number(row[2])) < 1e-10);
      }
      await page.locator('#pivot-table tbody tr').first().locator('td').nth(1).click();
      if (mode !== 'mean') await page.keyboard.press('Shift+ArrowRight');
      await page.keyboard.press('Control+c');
      const copied = await page.evaluate(() => navigator.clipboard.readText());
      assert.equal(copied, row.slice(1, mode === 'mean' ? 2 : 3).join('\t'));
      const [download] = await Promise.all([page.waitForEvent('download'),page.locator('#export').click()]);
      const chunks=[]; for await (const chunk of await download.createReadStream()) chunks.push(chunk);
      const csv=Buffer.concat(chunks).toString('utf8');
      assert.match(csv,/95% CI lower/); assert.match(csv,/ · SE/);
      if(originalCSV) assert.equal(csv,originalCSV); else originalCSV=csv;
    }
    await select.selectOption('ci95');
    await select.focus(); await page.keyboard.press('ArrowUp'); await page.keyboard.press('Enter');
    assert.equal(await select.inputValue(), 'se');
    for (const width of [320,640,1280,1920]) {
      await page.setViewportSize({width,height:800});
      for (const mode of ['sd','se','ci95','mean']) {
        await select.selectOption(mode);
        await page.waitForTimeout(80);
        assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth+1));
        assert(Number(await select.getAttribute('data-natural-width')) > 0, 'Actual Pretext measurement');
        assert(await page.locator('#pivot-table tbody tr').evaluateAll(rows => rows.every(row => [...row.cells].every(cell => cell.scrollWidth <= cell.clientWidth+1))));
      }
      await select.selectOption('ci95');
      for (const css of ['html{font-size:200%!important}','*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}']) {
        const style=await page.addStyleTag({content:css}); await page.waitForTimeout(100);
        assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth+1));
        assert(await page.locator('#table-region').evaluate(el=>el.scrollWidth<=el.clientWidth+1 && el.scrollHeight<=el.clientHeight+1));
        await style.evaluate(el=>el.remove());
      }
    }
    await page.setViewportSize({width:375,height:667}); await select.selectOption('ci95');
    await page.screenshot({path:'.for-ai-local/error-metrics-phone.png',fullPage:true});
    await page.setViewportSize({width:1280,height:900});
    await page.screenshot({path:'.for-ai-local/error-metrics-desktop.png',fullPage:true});
    console.log('Error metrics pass: independent selector, SD/SE/95% CI/none, separate numeric cells, chart agreement, clipboard, keyboard, responsive and Pretext.');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode=1; });
