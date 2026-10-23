const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{const browser=await chromium.launch();try{
 const page=await browser.newPage({viewport:{width:1280,height:900}});
 await page.goto(process.argv[2]||'http://127.0.0.1:8781/');
 assert.equal(await page.locator('#references').count(),1,'The paper needs an end References segment');
 assert.match(await page.locator('#phase-title').innerText(),/general reaction times.*inhalation.*exhalation/i);
 const citations=page.locator('#phase a[data-citation]');assert(await citations.count()>=4);
 await page.waitForFunction(()=>document.querySelector('[data-citation]')?.getAttribute('aria-haspopup')==='dialog');
 for(let i=0;i<await citations.count();i++){
  const citation=citations.nth(i),id=await citation.getAttribute('data-citation');
  const reference=page.locator(`#${id}`);assert.equal(await reference.count(),1);
  await citation.focus();await page.keyboard.press('Enter');
  const box=page.getByRole('dialog',{name:'Full reference',exact:true});await box.waitFor();
  assert((await box.innerText()).includes(await reference.locator('.reference-text').innerText()));
  assert.equal(await box.locator('a[href^="https://doi.org/"]').count(),1);
  await page.keyboard.press('Escape');assert.equal(await box.isVisible(),false);
  assert(await citation.evaluate(n=>n===document.activeElement));
 }
 for(const width of [320,640,1440]){
  await page.setViewportSize({width,height:800});
  const style=await page.addStyleTag({content:'body{font-size:34px!important}*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}'});
  await citations.first().click();const box=page.getByRole('dialog',{name:'Full reference',exact:true});await box.waitFor();await page.waitForTimeout(80);
  assert(await box.evaluate(n=>{const r=n.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth+1&&r.bottom<=innerHeight+1}));
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  assert(await box.locator('[data-citation-fit]').count()>0);
  await page.keyboard.press('Escape');await style.evaluate(n=>n.remove());
 }
 console.log('Citations pass: end references, APA author-year links/full entries, keyboard focus/Escape, DOI links, responsive boxes and Pretext.');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
