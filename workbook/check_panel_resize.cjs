const { chromium } = require('playwright');
const assert = require('node:assert/strict');
(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage({ viewport:{width:1600,height:1000} });
    const base = process.argv[2] || 'http://127.0.0.1:8767/';
    const errors = []; page.on('pageerror', error => errors.push(error.message));
    await page.goto(new URL('pivot/?view=core',base).href);
    await page.locator('#table-region[aria-busy="false"]').waitFor();
    assert.equal(await page.locator('#table-height,#table-width').count(), 0, 'Sizing sliders must be removed');
    const chartBounds = await page.locator('#chart-region').boundingBox();
    assert((await page.locator('.table-sheet').boundingBox()).y >= chartBounds.y + chartBounds.height,
      'The table must be below the plot on desktop too');
    const drag = async (handle, dx, dy) => {
      await handle.scrollIntoViewIfNeeded(); const box = await handle.boundingBox();
      const y = Math.min(page.viewportSize().height-20,Math.max(20,box.y+box.height/2));
      await page.mouse.move(box.x+box.width/2,y); await page.mouse.down();
      await page.mouse.move(box.x+box.width/2+dx,y+dy,{steps:10}); await page.mouse.up();
    };
    const before = await page.locator('#table-region').boundingBox();
    await drag(page.locator('#table-region [data-resize-edge="bottom"]'),0,100);
    assert((await page.locator('#table-region').boundingBox()).height > before.height+80);
    await page.locator('#table-region [data-resize-edge="bottom"]').focus(); await page.keyboard.press('Home');
    await page.keyboard.press('ArrowUp');
    assert(await page.locator('#table-region').evaluate(element => element.scrollHeight <= element.clientHeight+1));
    const tableWidth = (await page.locator('.table-sheet').boundingBox()).width;
    await drag(page.locator('#table-region [data-resize-edge="right"]'),-100,0);
    assert((await page.locator('.table-sheet').boundingBox()).width < tableWidth-60);
    const plot = page.locator('#chart-plot'), initialHeight = (await plot.boundingBox()).height;
    await drag(page.locator('#chart-region [data-resize-edge="bottom"]'),0,90);
    assert((await plot.boundingBox()).height > initialHeight+70);
    assert.equal(await page.locator('[data-chart-point]').count(),20);
    const height = await plot.locator('svg').getAttribute('height');
    await page.locator('#chart-region [data-resize-edge="bottom"]').focus(); await page.keyboard.press('ArrowDown');
    await page.waitForFunction(previous => +document.querySelector('#chart-plot svg').getAttribute('height') > +previous, height);
    for (const [width,height] of [[320,568],[640,360],[1280,800],[1920,1080]]) {
      await page.setViewportSize({width,height});
      await page.waitForTimeout(100);
      assert(await page.locator('#table-region').evaluate(element => element.scrollHeight <= element.clientHeight+1 && element.scrollWidth <= element.clientWidth+1), `${width} nested table scrolling`);
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth+1), `${width} page overflow`);
      for (const mode of ['large','spacing']) {
        const style = await page.addStyleTag({content: mode === 'large' ? 'html{font-size:200%!important}' :
          '*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}'});
        await page.waitForTimeout(60);
        assert(await page.locator('#table-region').evaluate(element => element.scrollHeight <= element.clientHeight+1 && element.scrollWidth <= element.clientWidth+1), `${width} ${mode} nested scroll`);
        assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth+1), `${width} ${mode} overflow`);
        await style.evaluate(element=>element.remove());
      }
      await page.locator('#table-region').evaluate(element => { element.scrollTop=50; });
      assert.equal(await page.locator('#table-region').evaluate(element => element.scrollTop),0);
    }
    // Width resizing keeps the same behavior across viewport sizes.
    await page.setViewportSize({width:800,height:900});
    await page.locator('#table-region [data-resize-edge="right"]').focus();
    await page.keyboard.press('Shift+ArrowLeft'); await page.keyboard.press('Shift+ArrowLeft');
    await page.setViewportSize({width:1600,height:1000}); await page.waitForTimeout(60);
    const expanded=(await page.locator('.table-sheet').boundingBox()).width;
    await page.locator('#table-region [data-resize-edge="right"]').focus(); await page.keyboard.press('ArrowRight');
    assert((await page.locator('.table-sheet').boundingBox()).width>expanded, 'The right border grows the table at every viewport size');
    await page.goto(base); await page.frameLocator('#core-pivot').locator('#table-region[aria-busy="false"]').waitFor();
    await page.setViewportSize({width:1920,height:1080});
    const a4Width = 210 * 96 / 25.4;
    const content = page.locator('main');
    assert(Math.abs((await content.boundingBox()).width - a4Width) < 1, 'Content starts at A4 width, excluding navigation');
    assert((await page.locator('.contents').boundingBox()).x < (await content.boundingBox()).x);
    const contentEdge = page.getByRole('separator', { name:'Publication content width. Drag or use arrow keys; Home resets.', exact:true });
    await contentEdge.focus(); await page.keyboard.press('Shift+ArrowRight');
    assert((await content.boundingBox()).width > a4Width+40, 'Readers can expand beyond A4');
    await drag(contentEdge,100,0);
    assert((await content.boundingBox()).width > a4Width+120, 'Content border supports mouse resizing');
    await contentEdge.focus(); await page.keyboard.press('Home');
    assert(Math.abs((await content.boundingBox()).width - a4Width) < 1, 'Reset restores A4');
    await contentEdge.focus();
    for (let step=0;step<4;step++) await page.keyboard.press('Shift+ArrowLeft');
    await page.waitForFunction(() => {
      const heading=document.querySelector('h1'), main=document.querySelector('main');
      return heading.dataset.fit === 'fit' && heading.getBoundingClientRect().right <= main.getBoundingClientRect().right;
    });
    assert((await content.boundingBox()).width < a4Width-190, 'Readers can narrow the content too');
    await contentEdge.focus(); await page.keyboard.press('Home');
    for (const selector of ['main section','#core-pivot','figure']) {
      assert(await page.locator(selector).evaluateAll(nodes => nodes.every(node => node.getBoundingClientRect().width <= document.querySelector('main').clientWidth+1)), `${selector} shares the reading width`);
    }
    await page.locator('#phase-figure[data-interactive="ready"]').waitFor();
    assert.equal(await page.locator('figure [data-resize-edge="bottom"]').count(),3);
    const rain=page.locator('#phase-figure .publication-plot svg');
    const rainHeight=Number(await rain.getAttribute('height'));
    const rainHandle=page.locator('#phase-figure [data-resize-edge="bottom"]');
    await rainHandle.focus();await page.keyboard.press('Shift+ArrowDown');
    await page.waitForFunction(previous=>Number(document.querySelector('#phase-figure .publication-plot svg').getAttribute('height'))>previous+30,rainHeight);
    await rainHandle.focus();await page.keyboard.press('Home');
    await page.waitForFunction(previous=>Number(document.querySelector('#phase-figure .publication-plot svg').getAttribute('height'))===previous,rainHeight);
    await page.keyboard.press('Shift+ArrowUp');await page.waitForTimeout(60);
    assert(Number(await rain.getAttribute('height'))>=rainHeight,'Content sets the readable minimum');
    assert.equal(await page.locator('#phase-figure [data-point-detail]').count(),246);
    for(const width of [320,640,1280,1920]) {
      await page.setViewportSize({width,height:800}); await page.waitForTimeout(150);
      const expectedWidth = Math.min(a4Width,await page.locator('.content-column').evaluate(element=>element.clientWidth));
      assert(Math.abs((await content.boundingBox()).width-expectedWidth)<1, `${width} default fits available width`);
      const core=page.frameLocator('#core-pivot');
      await page.waitForFunction(() => {
        const frame=document.querySelector('#core-pivot');
        return frame.clientHeight >= frame.contentDocument.documentElement.scrollHeight-1;
      });
      assert(await core.locator('#table-region').evaluate(element => element.scrollHeight <= element.clientHeight+1 && element.scrollWidth <= element.clientWidth+1));
      assert(await core.locator('.linked-views').evaluate(element =>
        element.querySelector('.table-sheet').getBoundingClientRect().top >=
        element.querySelector('#chart-region').getBoundingClientRect().bottom), `${width} embedded table order`);
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth+1));
    }
    const touch=await browser.newPage({viewport:{width:390,height:844},hasTouch:true,isMobile:true});
    await touch.goto(new URL('pivot/?view=core',base).href);
    await touch.locator('#table-region[aria-busy="false"]').waitFor();
    const handle=touch.locator('#table-region [data-resize-edge="bottom"]');
    await handle.scrollIntoViewIfNeeded(); const box=await handle.boundingBox();
    const client=await touch.context().newCDPSession(touch);
    const natural=(await touch.locator('#table-region').boundingBox()).height;
    await client.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:box.x+box.width/2,y:box.y+box.height/2}]});
    await client.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:box.x+box.width/2,y:box.y+box.height/2+60}]});
    await client.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
    await touch.waitForFunction(previous=>document.querySelector('#table-region').clientHeight>previous+40,natural);
    await touch.close();
    assert.deepEqual(errors,[]);
    console.log('Panel resizing passes: A4 content default/reset, expansion, border dragging, keyboard, plot redraw, content-fit tables and one document scroll surface.');
  } finally {await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
