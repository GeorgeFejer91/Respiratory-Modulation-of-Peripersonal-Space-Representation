// Run against the production build (and the published URL) with Playwright in NODE_PATH.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');

(async()=>{
 const browser=await chromium.launch();
 try{
  const base=process.argv[2]||'http://127.0.0.1:8783/';
  const url=new URL('preprocessing/',base).href;
  const page=await browser.newPage({viewport:{width:1280,height:900},hasTouch:true});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(url);await page.locator('body[data-ready="true"]').waitFor();
  const input=await (await page.request.get(url+'data.json')).body(),data=JSON.parse(input);
  const intro=(await page.locator('#introduction').innerText()).trim().split(/\s+/).length;
  assert(intro<=1500,`Introduction is ${intro} words`);
  assert.equal(data.rows.length,17114);
  assert.equal(await page.locator('#summary tbody tr').count(),20);
  assert.equal(await page.locator('#audit tbody tr').count(),6);
  assert.equal(await page.locator('.chart svg').count(),2);
  assert.equal(await page.locator('.chart img,.chart image').count(),0);
  const download=async id=>{
   const event=page.waitForEvent('download');await page.locator('#'+id).click();
   const item=await event;let text='';for await(const chunk of await item.createReadStream())text+=chunk;
   return text;
  };
  const stage=async value=>{await page.locator(`[name=stage][value="${value}"]`).check();
   await page.waitForFunction(v=>document.body.dataset.stage===String(v),value);};
  const select=async(id,value)=>{await page.locator('#'+id).selectOption(value);
   await page.waitForFunction(([k,v])=>new URLSearchParams(location.hash.slice(1)).get(k)===v,[id,value]);};
  const rows=data.rows.map(a=>Object.fromEntries(data.columns.map((c,i)=>[c,a[i]])));
  const primary=rows.filter(r=>!['P011','P033'].includes(r.participant_id));
  const expected=primary.filter(r=>r.trimmed&&r.trial_type==='Audio-Tactile').length;
  assert((await page.locator('#after-counts').innerText()).startsWith(expected.toLocaleString('en-US')));
  const initialHeight=await page.locator('#after-chart').evaluate(n=>n.clientHeight);
  await page.waitForTimeout(500);
  assert.equal(await page.locator('#after-chart').evaluate(n=>n.clientHeight),initialHeight,'Chart height must not grow on each resize observation');
  for(let i=0;i<6;i++){
   await stage(i);
   const details=await page.locator('#after-chart .bin').evaluateAll(ns=>ns.map(n=>JSON.parse(n.dataset.pointDetail)));
   assert.equal(details.reduce((sum,r)=>sum+r['Trial count'],0),Number((await page.locator('#after-counts').innerText()).split(' AT')[0].replaceAll(',','')));
   if(i<4)assert.equal(await page.locator('#after-chart svg').getAttribute('data-ymin'),'0');
  }
  await select('normalization','range');
  assert.equal(await page.locator('#after-chart svg').getAttribute('data-unit'),'0–1 range');
  await select('cutoff','200');await select('cohort','full42');
  const settings=JSON.parse(await download('settings'));
  assert.equal(settings.data_sha256,crypto.createHash('sha256').update(input).digest('hex'));
  assert.equal(settings.settings.cutoff,'200');assert.equal(settings.settings.normalization,'range');
  assert.equal(settings.stages[0].counts.rows,17114);
  await select('view','soa');
  assert.equal(await page.locator('#after-chart [data-person]').count(),840);
  const mark=page.locator('#after-chart [data-person]').first();
  const detail=JSON.parse(await mark.getAttribute('data-point-detail'));
  await mark.focus();await page.keyboard.press('Enter');
  const box=page.getByRole('dialog',{name:'Exact point values'});await box.waitFor();
  assert((await box.innerText()).includes(String(detail.Mean)));
  await page.keyboard.press('Escape');assert(await mark.evaluate(n=>document.activeElement===n));
  await page.keyboard.press('ArrowRight');assert.equal(await page.locator('#after-chart [data-point-detail][tabindex="0"]').count(),1);
  const csv=await download('csv');assert.equal(csv.trim().split('\n').length,17115);
  assert(csv.includes('baseline reference only'));assert(csv.includes('outside participant 2.5 SD'));
  const summaries=await download('summary-csv');assert.equal(summaries.trim().split('\n').length,41);
  const svg=await download('svg');assert(svg.includes('<path'));assert(!svg.includes('<image'));assert(svg.includes('normalization=range'));
  assert(svg.includes('Small dots: participant cell means.'),'SVG must include a visible interpretation key');
  assert(svg.includes('Cohort: Full (42)'),'SVG must retain the selected cohort');
  const restored=page.url();await page.reload();await page.locator('body[data-ready="true"]').waitFor();
  assert.equal(page.url(),restored);assert.equal(await page.locator('#normalization').inputValue(),'range');
  await select('participant','P011');await select('cohort','primary40');
  assert.equal(await page.locator('#after-chart [data-point-detail]').count(),0);
  assert.match(await page.locator('#status').innerText(),/0 values available/);
  assert(await page.locator('#csv').isDisabled());
  await page.locator('#reset').click();await page.waitForFunction(()=>document.body.dataset.stage==='2');
  assert.equal(await page.locator('#cohort').inputValue(),'primary40');
  const edge=page.locator('#after-chart .resize-bottom');
  await edge.focus();const oldHeight=await page.locator('#after-chart').evaluate(n=>n.clientHeight);
  await page.keyboard.press('Shift+ArrowDown');await page.waitForTimeout(80);
  assert((await page.locator('#after-chart').evaluate(n=>n.clientHeight))>=oldHeight+49);
  await page.keyboard.press('Home');
  const widthEdge=page.locator('#after-chart .resize-right');await widthEdge.focus();
  await page.keyboard.press('Shift+ArrowLeft');await page.waitForTimeout(80);
  assert(await page.locator('#after-chart').evaluate(n=>n.clientWidth<n.parentElement.clientWidth));
  await page.keyboard.press('Home');
  // Verify independent width/height, reflow breakpoints, text enlargement and spacing.
  for(const [width,height]of [[320,800],[480,800],[481,800],[640,360],[850,800],[851,800],[1280,600],[1920,1080]]){
   await page.setViewportSize({width,height});
   for(const css of ['',':root{font-size:34px!important}',
    '*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}']){
    const style=css?await page.addStyleTag({content:css}):null;
    await select('view','soa');await page.waitForTimeout(120);
    const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1?
     [...document.querySelectorAll('main *')].filter(n=>{const r=n.getBoundingClientRect();return r.right>innerWidth+1||r.left<0;}).map(n=>n.id||n.tagName):[]);
    assert.deepEqual(overflow,[],`${width}×${height} page overflow ${css}`);
    const bounds=await page.locator('#controls,[data-fit],.chart,#table-panel,#summary,#audit').evaluateAll(ns=>ns.filter(n=>n.scrollWidth>n.clientWidth+2).map(n=>n.id||n.textContent.slice(0,60)));
    assert.deepEqual(bounds,[],`${width} controls or tables clipped ${css}`);
    assert(await page.locator('[data-fit][data-lines]').count()>0,'Real Pretext measurement');
    const tickBounds=await page.locator('.chart svg').evaluateAll(svgs=>svgs.flatMap(svg=>[...svg.querySelectorAll('text')].filter(n=>{
     const r=n.getBoundingClientRect(),s=svg.getBoundingClientRect();return r.left<s.left-1||r.right>s.right+1||r.top<s.top-1||r.bottom>s.bottom+1;
    }).map(n=>n.textContent)));
    assert.deepEqual(tickBounds,[],`${width} SVG text clipped ${css}`);
    await page.locator('#after-chart [data-point-detail]').last().tap();await box.waitFor();
    assert(await box.evaluate(n=>{const r=n.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth+1}));await page.keyboard.press('Escape');
    assert(await page.locator('#table-panel').evaluate(n=>!['auto','scroll','hidden'].includes(getComputedStyle(n).overflowY)),'Full table stays in page flow');
    if(style)await style.evaluate(n=>n.remove());
   }
  }
  await page.setViewportSize({width:1280,height:900});await select('view','soa');await stage(4);
  const artifacts=path.resolve(__dirname,'../.for-ai-local/preprocessing-check');fs.mkdirSync(artifacts,{recursive:true});
  await page.locator('#comparison').screenshot({path:path.join(artifacts,'desktop.png')});
  await page.setViewportSize({width:320,height:800});
  await page.locator('#comparison').screenshot({path:path.join(artifacts,'phone.png')});
  await page.locator('#comparison figure').first().screenshot({path:path.join(artifacts,'phone-chart.png')});
  await page.locator('#controls').screenshot({path:path.join(artifacts,'phone-controls.png')});
  await stage(5);
  const narrowSvg=await download('svg'),exportPage=await browser.newPage();
  await exportPage.setContent(narrowSvg);
  assert(await exportPage.locator('body > svg').evaluate(svg=>{
   const s=svg.getBoundingClientRect();return [...svg.querySelectorAll(':scope > text')].every(n=>{
    const r=n.getBoundingClientRect();return r.left>=s.left&&r.right<=s.right+1;});
  }),'Export headings and caption must wrap within a phone-width figure');
  await page.goto(url+'default-summary.html');assert.equal(await page.locator('#summary tbody tr').count(),20);
  const fail=await browser.newPage();await fail.route('**/preprocessing/data.json',r=>r.abort());
  await fail.goto(url);await fail.locator('body[data-ready="error"]').waitFor();
  assert(await fail.getByRole('link',{name:'Open static default comparison'}).isVisible());
  const nojs=await browser.newPage({javaScriptEnabled:false});await nojs.goto(url);
  assert(await nojs.locator('noscript a').isVisible());
  const overview=await page.request.get(base);assert((await overview.text()).includes('href="preprocessing/"'));
  for(const target of ['workbook.html','ANALYSIS_PLAN.md','DATA_RELEASE.md'])assert((await page.request.get(new URL(target,base).href)).ok());
  assert.deepEqual(errors,[]);
  console.log(`Preprocessing passes: ${intro}-word introduction; six stages, real input counts, CSV/SVG/settings, restoration, empty/error/no-JS, keyboard/touch/resize, eight viewports, enlarged/spaced text and native SVG.`);
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
