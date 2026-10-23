import {prepareWithSegments,measureLineStats} from './pivot/vendor/pretext/dist/layout.js';

const box=document.createElement('div');box.className='citation-box';box.hidden=true;
box.setAttribute('role','dialog');box.setAttribute('aria-label','Full reference');box.id='citation-box';
const content=document.createElement('div'),actions=document.createElement('div');actions.className='citation-actions';
const closeButton=document.createElement('button');closeButton.type='button';closeButton.textContent='Close reference';
const fullList=document.createElement('a');fullList.textContent='Go to reference list';fullList.href='#references';
actions.append(closeButton,fullList);box.append(content,actions);document.body.append(box);
let origin,revision=0;
function close(restore=true){box.hidden=true;origin?.setAttribute('aria-expanded','false');if(restore)origin?.focus({preventScroll:true});}
async function position(){
  const current=++revision;await document.fonts.ready;if(box.hidden||current!==revision)return;
  const bounds=origin.getBoundingClientRect();
  box.style.left=`${Math.max(16,Math.min(innerWidth-box.offsetWidth-16,bounds.left))}px`;
  box.style.top=`${Math.max(16,Math.min(innerHeight-box.offsetHeight-16,bounds.bottom+8))}px`;
  for(const node of box.querySelectorAll('.reference-text,button,.citation-actions a')){
    const s=getComputedStyle(node),width=node.clientWidth-parseFloat(s.paddingLeft)-parseFloat(s.paddingRight)-2;
    const prepared=prepareWithSegments(node.textContent,`${s.fontStyle} ${s.fontWeight} ${s.fontSize} ${s.fontFamily}`,{letterSpacing:parseFloat(s.letterSpacing)||0});
    node.dataset.citationFit=measureLineStats(prepared,Math.max(1,width)).maxLineWidth<=width+1?'fit':'reflow';
  }
}
for(const citation of document.querySelectorAll('[data-citation]')){
  citation.setAttribute('aria-haspopup','dialog');citation.setAttribute('aria-controls',box.id);citation.setAttribute('aria-expanded','false');
  citation.addEventListener('click',event=>{
    if(event.button||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;
    const reference=document.getElementById(citation.dataset.citation)?.querySelector('.reference-text');if(!reference)return;
    event.preventDefault();close(false);origin=citation;content.replaceChildren(reference.cloneNode(true));fullList.href=citation.getAttribute('href');
    box.hidden=false;citation.setAttribute('aria-expanded','true');position();closeButton.focus({preventScroll:true});
  });
}
closeButton.addEventListener('click',()=>close());fullList.addEventListener('click',()=>close(false));
document.addEventListener('keydown',event=>{if(event.key==='Escape'&&!box.hidden){event.preventDefault();close();}});
document.addEventListener('pointerdown',event=>{if(!box.hidden&&!box.contains(event.target)&&!event.target.closest?.('[data-citation]'))close(false);});
addEventListener('resize',position);
