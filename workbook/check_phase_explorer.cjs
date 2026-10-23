const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch();
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1000},hasTouch:true});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  const base=process.argv[2]||'http://127.0.0.1:8781/';
  await page.goto(base);await page.locator('#phase-figure[data-interactive="ready"]').waitFor();
  assert.equal(await page.locator('#phase-controls').count(),1,'Segment 2 needs its own relevant controls');
  const host=page.locator('[data-plot="phase"]');
  const data=await (await page.request.get(new URL('publication-data.json',base).href)).json();
  assert.equal(await host.getAttribute('data-toolbox'),'d3-7.9.0');
  assert.equal(await host.locator('[data-phase-point]').count(),240);
  assert.equal(await host.locator('[data-density]').count(),6);
  const layers=['dots','density','box','mean','ci'];
  for(let bits=0;bits<32;bits++){
   for(let i=0;i<5;i++)await page.locator(`[data-phase-layer="${layers[i]}"]`).setChecked(Boolean(bits&(1<<i)));
   await page.waitForFunction(mask=>document.querySelector('[data-plot="phase"]').dataset.layers===String(mask),bits);
   for(const [i,selector,count] of [[0,'[data-phase-point]',240],[1,'[data-density]',6],[2,'[data-box]',6],[3,'[data-phase-mean]',6],[4,'[data-phase-ci]',6]]){
    assert.equal(await host.locator(selector).count(),bits&(1<<i)?count:0,`Layer ${layers[i]} in combination ${bits}`);
   }
   assert.equal(await host.locator('[data-point-detail]').count(),(bits&1?240:0)+(bits&8?6:bits&16?6:0),'Every visible point/interval needs exact-value inspection');
   if(bits===16){const interval=host.locator('[data-point-detail]').first();await interval.focus();await page.keyboard.press('Enter');const box=page.getByRole('dialog',{name:'Exact point values'});await box.waitFor();assert((await box.innerText()).includes(String(data.phase.trial_groups[0].ci_low)));await page.keyboard.press('Escape');}
   assert.equal(await host.locator('[data-zero-baseline]').count(),1);
  }
  await page.getByRole('button',{name:'Reset phase plot',exact:true}).click();
  await page.locator('#phase-outcome').selectOption('corrected');
  await page.waitForFunction(()=>document.querySelector('[data-plot="phase"]').dataset.outcome==='corrected');
  assert.equal(await host.locator('[data-phase-point]').count(),200);
  assert.equal(await host.locator('[data-phase-mean]').count(),5);
  assert.equal(await page.locator('[data-phase-group="Baseline"]').isDisabled(),true);
  const actual=await host.locator('[data-phase-point]').evaluateAll(nodes=>nodes.map(n=>JSON.parse(n.dataset.pointDetail)));
  for(const row of data.phaseExplorer.corrected.rows){
   const point=actual.find(p=>p.Participant===row.participant_id&&p['Trial group']===row.trial_group);
   assert.equal(point['Inhale − Exhale (ms)'],row.delta_ms);
  }
  const point=host.locator('[data-phase-point]').first();await point.focus();await page.keyboard.press('Enter');
  await page.getByRole('dialog',{name:'Exact point values'}).waitFor();await page.keyboard.press('Escape');
  assert.equal(await point.evaluate(n=>n===document.activeElement),true);
  const downloadEvent=page.waitForEvent('download');await page.getByRole('button',{name:'Download displayed phase values (CSV)',exact:true}).click();
  const download=await downloadEvent;let csv='';for await(const chunk of await download.createReadStream())csv+=chunk;
  assert.equal(csv.trim().split('\n').length,201);assert(csv.includes('corrected'));
  assert(csv.includes(String(data.phaseExplorer.corrected.rows[0].delta_ms)));
  const svgEvent=page.waitForEvent('download');await page.getByRole('button',{name:'Download current phase plot (SVG)',exact:true}).click();
  const svgDownload=await svgEvent;let svg='';for await(const chunk of await svgDownload.createReadStream())svg+=chunk;
  assert(svg.includes('<svg'));assert(!svg.includes('<image'));assert(svg.includes('AT − Baseline'));
  for(const name of ['AT 300 ms','AT 800 ms','AT 1500 ms','AT 2200 ms','AT 2700 ms'])await page.locator(`[data-phase-group="${name}"]`).uncheck();
  await page.waitForFunction(()=>document.querySelector('[data-plot="phase"]').dataset.groups==='0');
  assert.equal(await host.locator('[data-point-detail]').count(),0);
  assert.equal(await page.getByRole('button',{name:'Download displayed phase values (CSV)',exact:true}).isDisabled(),true);
  await page.getByRole('button',{name:'Reset phase plot',exact:true}).click();
  assert.equal(await host.locator('[data-phase-point]').count(),240);
  for(const width of [320,640,1280,1920]){
   await page.setViewportSize({width,height:800});
   for(const css of ['','body{font-size:34px!important}',
    '*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}']){
    const style=css?await page.addStyleTag({content:css}):null;await page.waitForTimeout(100);
    assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),`${width} page overflow`);
    assert(await page.locator('#phase-controls').evaluate(n=>n.scrollWidth<=n.clientWidth+1),`${width} controls overflow`);
    assert(await page.locator('#phase-controls [data-phase-fit]').count()>0,'Real Pretext measurement is required');
    await host.locator('[data-phase-point]').first().tap();
    const box=page.getByRole('dialog',{name:'Exact point values'});await box.waitFor();
    assert(await box.evaluate(n=>{const r=n.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth+1}));await page.keyboard.press('Escape');
    if(style)await style.evaluate(n=>n.remove());
   }
  }
  assert.deepEqual(errors,[]);console.log('Phase explorer passes: D3, 32 layer combinations, corrected pairing, groups/empty/reset, exact values, CSV/SVG, keyboard/touch and reflow.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
