import {violinDensity} from './pivot/pivot-chart.mjs';
import {enablePointInspection,hidePoint} from './pivot/point-inspector.js';
import {prepareWithSegments,measureNaturalWidth} from './pivot/vendor/pretext/dist/layout.js';

const ns='http://www.w3.org/2000/svg';
const colors=['#4477AA','#CC6677','#117733','#882255','#AA4499','#000000'];
const el=(tag,attributes={},text)=>{const n=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attributes))n.setAttribute(k,v);if(text!==undefined)n.textContent=text;return n;};
export function quantile(values,q){const sorted=[...values].sort((a,b)=>a-b),i=(sorted.length-1)*q,l=Math.floor(i);return sorted[l]+(sorted[Math.ceil(i)]-sorted[l])*(i-l);}
const mean=values=>values.reduce((a,b)=>a+b,0)/values.length;
function measureText(svg){
  const width=Number(svg.getAttribute('width'));
  for(const node of svg.querySelectorAll('text')){
    const style=getComputedStyle(node),x=Number(node.getAttribute('x')),anchor=node.getAttribute('text-anchor');
    const budget=anchor==='end'?x-4:anchor==='middle'?2*Math.min(x,width-x):width-x-4;
    const prepared=prepareWithSegments(node.textContent,`${style.fontStyle} ${style.fontWeight} ${style.fontSize} ${style.fontFamily}`,{letterSpacing:parseFloat(style.letterSpacing)||0});
    node.dataset.textFit=measureNaturalWidth(prepared)<=budget?'fit':'reflow';
  }
}
const numeric=(rows,key)=>rows.map(r=>Number(r[key]));
const requestedHeight=host=>Math.max(0,(parseFloat(host.closest('.plot-panel')?.style.height)||0)-12);
const domain=values=>{const low=Math.min(0,...values),high=Math.max(0,...values),pad=(high-low||1)*.08;return [low<0?low-pad:0,high+pad];};
function chart(host,{xs,ys,height=420,left=76,rain=false,xlabel='SOA (ms)',ylabel='AT − Baseline RT (ms)',xticks}){
  host.replaceChildren();const width=Math.max(240,host.clientWidth),f=parseFloat(getComputedStyle(host).fontSize);
  if(!rain){left=Math.max(left,f*4.5);height=Math.max(height,f*21,requestedHeight(host));}
  const svg=el('svg',{viewBox:`0 0 ${width} ${height}`,width,height,role:'group','aria-label':host.getAttribute('aria-label')});host.append(svg);
  const margin={left,right:Math.max(16,f*1.6),top:Math.max(20,f*1.8),bottom:Math.max(56,f*3)};
  const x=v=>left+(v-xs[0])/(xs[1]-xs[0])*(width-left-margin.right);
  const y=v=>rain?v:margin.top+(ys[1]-v)/(ys[1]-ys[0])*(height-margin.top-margin.bottom);
  const append=(tag,attrs,text)=>{const n=el(tag,attrs,text);svg.append(n);return n;};
  const line=(x1,y1,x2,y2,color='#243240',extra={})=>append('line',{x1,y1,x2,y2,stroke:color,...extra});
  const text=(px,py,label,anchor='middle',size=f)=>append('text',{x:px,y:py,'text-anchor':anchor,fill:'#243240','font-size':size},label);
  const point=(px,py,fields,color='#243240',r=3,extra={})=>append('circle',{cx:px,cy:py,r,fill:color,'data-point-detail':JSON.stringify(fields),...extra});
  const whisker=(px,low,high,color,horizontal=false)=>{
    if(horizontal){line(x(low),px,x(high),px,color,{'stroke-width':2});for(const v of [low,high])line(x(v),px-4,x(v),px+4,color);}
    else{line(px,y(low),px,y(high),color);for(const v of [low,high])line(px-4,y(v),px+4,y(v),color);}
  };
  const tickValues=(range,count)=>Array.from({length:count},(_,i)=>range[0]+(range[1]-range[0])*i/(count-1));
  const count=Math.max(2,Math.min(5,Math.floor((width-left-margin.right)/(f*3))));
  const rough=(xs[1]-xs[0])/count,power=10**Math.floor(Math.log10(rough)),ratio=rough/power;
  const step=power*(ratio>5?10:ratio>2?5:ratio>1?2:1);
  const nice=[];for(let value=Math.ceil(xs[0]/step)*step;value<=xs[1];value+=step)nice.push({value,label:Number(value.toPrecision(6))});
  const ticks=xticks||nice;
  for(const tick of ticks)text(x(tick.value),height-f*1.6,tick.label,'middle',f*.86);
  text(width/2,height-5,xlabel,'middle',f*.94);
  if(rain)line(x(0),18,x(0),height-56,'#243240',{'stroke-dasharray':'5 4','data-zero-baseline':''});
  else{
    for(const v of tickValues(ys,5)){line(left,y(v),width-16,y(v),'#e0e5e9');text(left-7,y(v)+f*.3,Number(v.toFixed(0)),'end',f*.85);}
    line(left,y(0),width-16,y(0),'#243240',{'stroke-dasharray':'5 4','data-zero-baseline':''});
    text(8,f,ylabel,'start',f*.9);
  }
  return {svg,x,y,line,text,point,whisker,append,width,height};
}
function raincloud(host,data){
  const groups=data.phase.trial_groups,records=data.phaseDeltas;
  const font=parseFloat(getComputedStyle(host).fontSize),stack=host.clientWidth<font*14;
  const step=Math.max(stack?font*5.8:Math.max(83,font*4.5),(requestedHeight(host)-(stack?160:100))/6),left=stack?28:Math.max(112,font*6.6);
  const c=chart(host,{xs:domain(numeric(records,'delta_inhale_minus_exhale_ms')),ys:[0,1],rain:true,
    height:step*6+(stack?160:100),left,xlabel:'Δ RT (ms)'});
  if(stack)c.svg.querySelector('[data-zero-baseline]').remove();
  const lookup=new Map(data.phaseGroups.map(r=>[`${r.participant_id}|${r.phase}|${r.trial_group}`,Number(r.reaction_time_ms)]));
  groups.forEach((s,i)=>{
    const color=colors[i],start=font+i*step,cy=stack?start+font*2+40:50+i*step,rows=records.filter(r=>r.trial_group===s.trial_group),values=numeric(rows,'delta_inhale_minus_exhale_ms');
    if(stack)c.line(c.x(0),cy-38,c.x(0),cy+44,'#243240',{'stroke-dasharray':'5 4','data-zero-baseline':''});
    const density=violinDensity(values);
    if(density){const coords=density.points.map(p=>`${c.x(p.value)},${cy-8-p.width*28}`);
      c.append('path',{d:`M${c.x(density.points[0].value)},${cy-8}L${coords.join('L')}L${c.x(density.points.at(-1).value)},${cy-8}Z`,fill:color,'fill-opacity':.2,stroke:color,'stroke-width':1,'data-density':'','data-bandwidth':density.bandwidth});}
    const q1=quantile(values,.25),q3=quantile(values,.75),median=quantile(values,.5),iqr=q3-q1;
    c.line(c.x(Math.min(...values.filter(v=>v>=q1-1.5*iqr))),cy,c.x(Math.max(...values.filter(v=>v<=q3+1.5*iqr))),cy,color);
    c.append('rect',{x:c.x(q1),y:cy-4,width:c.x(q3)-c.x(q1),height:8,fill:'white',stroke:color});
    c.line(c.x(median),cy-4,c.x(median),cy+4,color,{'stroke-width':2});
    rows.forEach((r,j)=>c.point(c.x(Number(r.delta_inhale_minus_exhale_ms)),cy+12+j/39*13,
      {Participant:r.participant_id,'Trial group':s.trial_group,'Exhale RT (ms)':lookup.get(`${r.participant_id}|Exhale|${s.trial_group}`),
       'Inhale RT (ms)':lookup.get(`${r.participant_id}|Inhale|${s.trial_group}`),'Inhale − Exhale (ms)':Number(r.delta_inhale_minus_exhale_ms)},color,2.8));
    c.whisker(cy+38,s.ci_low,s.ci_high,color,true);
    c.point(c.x(s.mean),cy+38,{'Statistic':'Participant mean','Trial group':s.trial_group,'Inhale − Exhale (ms)':s.mean,
      'Pointwise 95% CI low (ms)':s.ci_low,'Pointwise 95% CI high (ms)':s.ci_high,n:s.n},'white',4,{stroke:color,'stroke-width':2});
    const right=left-9;
    c.text(stack?4:right,stack?start:cy-1,s.trial_group,stack?'start':'end',font*.84);
    c.text(stack?4:right,stack?start+font:cy+font,`${s.mean>=0?'+':''}${s.mean.toFixed(2)} ms`,stack?'start':'end',font*.84);
  });
  return c;
}
function soa(host,data){
  const ids=data.soa.participant_ids,soas=data.soa.summary.map(r=>r.soa_ms);
  const records=ids.flatMap(pid=>soas.map(soa=>({pid,soa,value:mean(numeric(data.soaCells.filter(r=>r.participant_id===pid&&Number(r.soa_ms)===soa),'corrected_rt_ms'))})));
  const ticks=host.clientWidth<parseFloat(getComputedStyle(host).fontSize)*25?[300,2700]:soas;
  const c=chart(host,{xs:[180,2820],ys:domain([...records.map(r=>r.value),...data.soa.summary.flatMap(r=>[r.ci_low_ms,r.ci_high_ms])]),xticks:ticks.map(value=>({value,label:value}))});
  for(const pid of ids){const rows=records.filter(r=>r.pid===pid);c.append('polyline',{points:rows.map(r=>`${c.x(r.soa)},${c.y(r.value)}`).join(' '),fill:'none',stroke:'#777','stroke-opacity':.4});
    for(const r of rows)c.point(c.x(r.soa),c.y(r.value),{Participant:pid,'SOA (ms)':r.soa,'AT − Baseline RT (ms)':r.value},'#777',2);}
  for(const r of data.soa.summary){c.whisker(c.x(r.soa_ms),r.ci_low_ms,r.ci_high_ms,'black');c.point(c.x(r.soa_ms),c.y(r.mean_ms),{'Statistic':'Participant mean','SOA (ms)':r.soa_ms,'AT − Baseline RT (ms)':r.mean_ms,'95% CI low (ms)':r.ci_low_ms,'95% CI high (ms)':r.ci_high_ms,n:r.n},'black',4);}
  return c;
}
function blocks(host,data){
  const byPerson=new Map();for(const row of data.blockCells){if(!byPerson.has(row.participant_id))byPerson.set(row.participant_id,[]);byPerson.get(row.participant_id).push(row);}
  const people=data.blocks.participant_ids.map(pid=>[pid,byPerson.get(pid)]),summary=data.blocks.summary;
  const ticks=host.clientWidth<parseFloat(getComputedStyle(host).fontSize)*25?[1,6,12]:[1,3,6,9,12];
  const c=chart(host,{xs:[.65,12.35],ys:domain([...people.flatMap(([,rows])=>numeric(rows,'mean_rt_ms')),...summary.flatMap(r=>[r.ci_low_ms,r.ci_high_ms])]),xlabel:'Block',xticks:ticks.map(value=>({value,label:value}))});
  for(const [pid,rows] of people)for(const start of [1,7]){
    const segment=rows.filter(r=>Number(r.session_block)>=start&&Number(r.session_block)<start+6).sort((a,b)=>a.session_block-b.session_block);
    const color=segment[0].condition==='Control'?'#005a9c':'#ba2525';
    c.append('polyline',{points:segment.map(r=>`${c.x(Number(r.session_block))},${c.y(Number(r.mean_rt_ms))}`).join(' '),fill:'none',stroke:color,'stroke-opacity':.45,'stroke-dasharray':segment[0].condition==='Control'?'':'5 3'});
    for(const r of segment)c.point(c.x(Number(r.session_block)),c.y(Number(r.mean_rt_ms)),{Participant:pid,Condition:r.condition,Block:Number(r.session_block),'AT − Baseline RT (ms)':Number(r.mean_rt_ms)},color,2);
  }
  for(const r of summary){const block=Number(r.session_block);c.whisker(c.x(block),r.ci_low_ms,r.ci_high_ms,'black');c.point(c.x(block),c.y(r.mean_ms),{'Statistic':'Participant mean',Block:block,'AT − Baseline RT (ms)':r.mean_ms,'95% CI low (ms)':r.ci_low_ms,'95% CI high (ms)':r.ci_high_ms,n:r.n},'black',4);}
  c.line(c.x(6.5),20,c.x(6.5),c.height-56,'#657485',{'stroke-dasharray':'3 3'});return c;
}
const renderers={phase:raincloud,soa,blocks};
if(typeof document!=='undefined'){
  const response=await fetch('publication-data.json');if(!response.ok)throw new Error('Chart data unavailable');const data=await response.json();
  for(const host of document.querySelectorAll('[data-plot]')){
    let scheduled=false,geometry='';const render=()=>{
      const panel=host.closest('.plot-panel'),font=parseFloat(getComputedStyle(host).fontSize);
      const next=`${host.clientWidth}:${font}:${panel?.style.height}`;
      scheduled=false;if(next===geometry)return;geometry=next;
      if(panel){const minimum=host.dataset.plot==='phase'?(host.clientWidth<font*14?font*5.8*6+160:Math.max(83,font*4.5)*6+100):Math.max(420,font*21);panel.style.minHeight=`${minimum+12}px`;}
      hidePoint();const c=renderers[host.dataset.plot](host,data);enablePointInspection(c.svg);measureText(c.svg);host.closest('figure').dataset.interactive='ready';
    };
    const observer=new ResizeObserver(()=>{if(!scheduled){scheduled=true;requestAnimationFrame(render);}});observer.observe(host);if(host.closest('.plot-panel'))observer.observe(host.closest('.plot-panel'));
    document.addEventListener('panel-resize',()=>{if(!scheduled){scheduled=true;requestAnimationFrame(render);}});
    render();
  }
}
