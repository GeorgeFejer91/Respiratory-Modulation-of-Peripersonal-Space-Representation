// Shared click/tap details. Numbers use their full round-trip representation.
let box, content, selected, measurePending = 0;
if (typeof document !== 'undefined') {
  const css = document.createElement('link');
  css.rel = 'stylesheet'; css.href = new URL('./point-inspector.css', import.meta.url).href;
  document.head.append(css);
}

function close() {
  if (!box || box.hidden) return;
  box.hidden = true;
  if (selected?.isConnected) selected.focus({preventScroll:true});
}
export function hidePoint() { if(box) box.hidden=true; }
function adjacent(direction) {
  const points = [...selected.closest('svg').querySelectorAll('[data-point-detail]')];
  const next = points[(points.indexOf(selected)+direction+points.length)%points.length];
  points.forEach(point => point.setAttribute('tabindex','-1'));
  next.setAttribute('tabindex','0'); next.focus({preventScroll:true});
  showPoint(next, JSON.parse(next.dataset.pointDetail));
}
function createBox() {
  box = document.createElement('div'); box.className = 'point-inspector'; box.hidden = true;
  box.setAttribute('role','dialog'); box.setAttribute('aria-label','Exact point values');
  content = document.createElement('dl'); content.setAttribute('aria-live','polite');
  const controls = document.createElement('div'); controls.className = 'point-inspector-actions';
  for (const [label, action] of [['Previous point',()=>adjacent(-1)],['Next point',()=>adjacent(1)],['Close',close]]) {
    const button=document.createElement('button'); button.type='button'; button.textContent=label;
    button.addEventListener('click',action); controls.append(button);
  }
  box.append(content, controls); document.body.append(box);
  addEventListener('keydown',event=>{if(event.key==='Escape'&&!box.hidden){event.preventDefault();close();}});
  document.addEventListener('pointerdown',event=>{
    if (!box.hidden && !box.contains(event.target) && !event.target.closest?.('[data-point-detail]')) close();
  });
  addEventListener('resize',()=>{if(!box.hidden) position();});
}
async function position() {
  const revision=++measurePending;
  await document.fonts.ready;
  if(box.hidden || revision!==measurePending) return;
  const bounds=selected.getBoundingClientRect();
  box.style.left=`${Math.max(8,Math.min(innerWidth-box.offsetWidth-8,bounds.right+8))}px`;
  box.style.top=`${Math.max(8,Math.min(innerHeight-box.offsetHeight-8,bounds.bottom+8))}px`;
  // Measure the real loaded typography; wrapping/scrolling absorbs enlarged text.
  try {
    const {prepareWithSegments,measureLineStats}=await import('./vendor/pretext/dist/layout.js');
    for(const node of box.querySelectorAll('dt,dd,button')){
      const s=getComputedStyle(node), font=`${s.fontStyle} ${s.fontWeight} ${s.fontSize} ${s.fontFamily}`;
      const width=Math.max(1,node.clientWidth-parseFloat(s.paddingLeft)-parseFloat(s.paddingRight)-2);
      const prepared=prepareWithSegments(node.textContent,font,{letterSpacing:parseFloat(s.letterSpacing)||0});
      const stats=measureLineStats(prepared,width);
      node.dataset.pointFit=stats.maxLineWidth<=width+1?'fit':'reflow';
    }
  } catch { box.dataset.measurement='unavailable'; }
}
export function showPoint(node, detail) {
  if(!box) createBox();
  selected=node; content.replaceChildren();
  for(const [label,value] of Object.entries(detail)){
    const term=document.createElement('dt'), definition=document.createElement('dd');
    term.textContent=label; definition.textContent=value===null?'Missing':String(value);
    content.append(term,definition);
  }
  box.hidden=false; position();
}
export function enablePointInspection(root) {
  const points=[...root.querySelectorAll('[data-point-detail]')];
  points.forEach((node,index)=>{
    node.setAttribute('role','button'); node.setAttribute('tabindex',index?'-1':'0');
    const detail=JSON.parse(node.dataset.pointDetail);
    node.setAttribute('aria-label',Object.entries(detail).map(([k,v])=>`${k}: ${v}`).join('; '));
    node.addEventListener('click',event=>{event.preventDefault();showPoint(node,detail);});
    node.addEventListener('keydown',event=>{
      if(['Enter',' '].includes(event.key)){event.preventDefault();showPoint(node,detail);}
      if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','Home','End'].includes(event.key)){
        event.preventDefault();
        const next=event.key==='Home'?0:event.key==='End'?points.length-1:
          Math.max(0,Math.min(points.length-1,points.indexOf(node)+(['ArrowLeft','ArrowUp'].includes(event.key)?-1:1)));
        points.forEach(point=>point.setAttribute('tabindex','-1'));
        points[next].setAttribute('tabindex','0'); points[next].focus();
        if(box&&!box.hidden) showPoint(points[next],JSON.parse(points[next].dataset.pointDetail));
      }
    });
  });
  // Dense plots have small marks: nearby blank-space taps choose the nearest
  // observed mark. Previous/Next and arrow keys expose covered observations.
  root.addEventListener('click',event=>{
    if(event.target.closest?.('[data-point-detail]')) return;
    let nearest, distance=16;
    for(const node of points){
      const r=node.getBoundingClientRect();
      const delta=Math.hypot(event.clientX-(r.left+r.width/2),event.clientY-(r.top+r.height/2));
      if(delta<distance){distance=delta;nearest=node;}
    }
    if(nearest) showPoint(nearest,JSON.parse(nearest.dataset.pointDetail));
  });
}
