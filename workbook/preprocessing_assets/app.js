import '../vendor/d3/d3.min.js';
import {derive,SOAS,finite,histogram} from './engine.mjs';
import {enablePointInspection,hidePoint} from '../pivot/point-inspector.js';
import {resizePanel} from '../pivot/panel-resize.js';
import {prepareWithSegments,measureLineStats} from '../pivot/vendor/pretext/dist/layout.js';

const d3=globalThis.d3, $=id=>document.getElementById(id);
const defaults={stage:'2',cohort:'primary40',participant:'all',condition:'all',phase:'all',cutoff:'none',normalization:'z',view:'distribution'};
const descriptions=[
  'The starting view contains every released record in the selected cohort and display filters. Only finite audio–tactile RTs enter the charts. Missing responses and other trial types remain in the audit and download.',
  'Keep audio–tactile and baseline hits with a response and finite RT, after the participant catch-error rule (>30% false alarms). Catch trials inform that rule but are not RT targets. No RT-window flags are applied.',
  'Remove responses outside each participant’s mean ± 2.5 sample SD, calculated once across eligible audio–tactile and baseline hits in both conditions and phases. Removed values are not replaced.',
  'Apply the optional RT ≥200 ms sensitivity after the SD filter. With the sensitivity off, this step changes no observations. This is not the recorded 200–2000 ms flag.',
  'Subtract each participant’s retained baseline mean within the same condition and phase from each retained audio–tactile RT. Baseline pools nominal SOAs. Negative values mean faster audio–tactile responses; this transformation does not exclude trials.',
  'Put corrected RTs on a within-person scale using all retained corrected audio–tactile trials before the display filters. Z-scores use sample SD; min–max uses the observed range. Constant or missing reference distributions give missing values.'
];
const formats={mean:v=>finite(v)?v.toPrecision(6):'Missing',count:v=>v.toLocaleString('en-US')};
const names=['Control · Exhale','Control · Inhale','Viscereality · Exhale','Viscereality · Inhale'];
const colors=['#236594','#236594','#a43f36','#a43f36'];
let data,stages,before,after,state,sourceHash='',scheduled=false,cacheKey='';
const download=(name,text,type)=>{
  const url=URL.createObjectURL(new Blob([text],{type})),a=document.createElement('a');
  a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
};
const csvText=rows=>{
  if(!rows.length)return '';
  const keys=Object.keys(rows[0]),quote=v=>v==null?'':('"'+String(v).replaceAll('"','""')+'"');
  return [keys,...rows.map(r=>keys.map(k=>r[k]))].map(row=>row.map(quote).join(',')).join('\r\n')+'\r\n';
};
function readState() {
  return Object.fromEntries(Object.keys(defaults).map(key=>[key,key==='stage'?document.querySelector('[name=stage]:checked').value:$(key).value]));
}
function restore() {
  const params=new URLSearchParams(location.hash.slice(1));
  for(const [key,fallback]of Object.entries(defaults)){
    const value=params.get(key)||fallback;
    if(key==='stage'){
      const control=document.querySelector('[name=stage][value="'+(/^[0-5]$/.test(value)?value:fallback)+'"]');
      control.checked=true;
    }else{
      $(key).value=[...$(key).options].some(o=>o.value===value)?value:fallback;
    }
  }
}
function measure() {
  for(const node of document.querySelectorAll('[data-fit]')){
    const s=getComputedStyle(node),width=node.clientWidth-parseFloat(s.paddingLeft)-parseFloat(s.paddingRight);
    const prepared=prepareWithSegments(node.textContent.trim(),s.fontStyle+' '+s.fontWeight+' '+s.fontSize+' '+s.fontFamily,
      {letterSpacing:parseFloat(s.letterSpacing)||0});
    const stats=measureLineStats(prepared,Math.max(1,width));
    node.dataset.fit=stats.maxLineWidth<=width+1?'fit':'reflow';
    node.dataset.lines=String(stats.lineCount);
    node.style.minHeight=Math.ceil(stats.lineCount*parseFloat(s.lineHeight)+parseFloat(s.paddingTop)+parseFloat(s.paddingBottom))+'px';
  }
}
function extent(values) {
  let low=0,high=0;for(const v of values)if(finite(v)){low=Math.min(low,v);high=Math.max(high,v);}
  const padding=(high-low||1)*.04;
  return [low<0?low-padding:0,high+padding];
}
const atValues=s=>s.rows.filter(r=>r.trial_type==='Audio-Tactile'&&finite(r.value)).map(r=>r.value);
function renderChart(id,stage,domain,maxCount) {
  const host=$(id);host.querySelector('svg')?.remove();
  const font=parseFloat(getComputedStyle(host).fontSize),width=host.clientWidth-12;
  const minimum=Math.max(320,font*15);
  host.style.minHeight=(minimum+12)+'px';
  const height=Math.max(minimum,(parseFloat(host.style.height)||0)-12),left=Math.max(48,font*3.2),right=font*2.2;
  const bottom=height-font*3.3,top=font*1.5,distribution=state.view==='distribution';
  const svg=d3.select(host).append('svg').attr('xmlns','http://www.w3.org/2000/svg')
    .attr('width',width).attr('height',height).attr('viewBox','0 0 '+width+' '+height)
    .attr('role','group').attr('aria-label',stage.title+': '+(distribution?'trial distribution':'participant SOA means')+'; '+stage.unit)
    .attr('data-stage',stage.id).attr('data-unit',stage.unit)
    .style('font-family','Arial, sans-serif').style('font-size',font+'px').style('background','white').style('color','#243240');
  svg.append('title').text(stage.title+' · '+stage.unit);
  svg.append('desc').text('Descriptive preprocessing view. Exact data in the table and CSV. '+descriptions[stage.id]);
  if(!stage.counts.plotted){
    ['No available','AT values.'].forEach((line,i)=>svg.append('text').attr('x',16).attr('y',font*(3+i*1.4)).attr('fill','#243240').text(line));
    return;
  }
  const x=d3.scaleLinear().domain(distribution?domain:[300,2700]).range([left,width-right]);
  const y=d3.scaleLinear().domain(distribution?[0,maxCount||1]:domain).range([bottom,top]);
  svg.attr('data-ymin',y.domain()[0]).attr('data-ymax',y.domain()[1]);
  svg.append('g').attr('transform','translate(0,'+bottom+')')
    .call(d3.axisBottom(x).tickValues(distribution?x.ticks(Math.max(2,Math.floor((width-left-right)/(font*4)))):
      width-left-right<font*8?[300,2700]:width/font<26?[300,1500,2700]:SOAS)
      .tickFormat(distribution?d3.format('~s'):d3.format('d')).tickSizeOuter(0));
  svg.append('g').attr('transform','translate('+left+',0)').call(d3.axisLeft(y).ticks(4).tickFormat(d3.format('~s')).tickSizeOuter(0));
  svg.selectAll('.tick text').attr('font-size',font*.82);
  svg.append('text').attr('x',left).attr('y',font).attr('fill','#243240').attr('font-size',font*.88)
    .text(distribution?'Trial count':stage.unit);
  svg.append('text').attr('x',(left+width-right)/2).attr('y',height-font*.4).attr('text-anchor','middle').attr('fill','#243240')
    .attr('font-size',font*.9).text(distribution?(stage.unit==='ms'?'RT (ms)':stage.unit):'SOA (ms)');
  if(!distribution){
    svg.append('line').attr('x1',left).attr('x2',width-right).attr('y1',y(0)).attr('y2',y(0))
      .attr('stroke','#697886').attr('stroke-dasharray','4 3').attr('data-zero','');
    for(let group=0;group<4;group++){
      const [condition,phase]=names[group].split(' · ');
      const rows=stage.summary.filter(r=>r.condition===condition&&r.phase===phase);
      const people=stage.people.filter(r=>r.condition===condition&&r.phase===phase);
      const path=SOAS.map(soa=>rows.find(r=>r.soa===soa));
      svg.append('path').datum(path).attr('d',d3.line().defined(Boolean).x(r=>x(r.soa)).y(r=>y(r.mean)))
        .attr('fill','none').attr('stroke',colors[group]).attr('stroke-width',2).attr('stroke-dasharray',group%2?'5 3':null);
      svg.selectAll('circle.person-'+group).data(people).join('circle').attr('cx',r=>x(r.soa)).attr('cy',r=>y(r.value))
        .attr('r',2.4).attr('fill',colors[group]).attr('opacity',.32).attr('data-person','')
        .attr('data-point-detail',r=>JSON.stringify({Participant:r.participant_id,Condition:r.condition,Phase:r.phase,'SOA (ms)':r.soa,
          Stage:stage.title,Units:stage.unit,Mean:r.value,'Trials in this cell':r.n_trials}));
      for(const r of rows){
        const mark=svg.append(group%2?'rect':'circle');
        if(group%2)mark.attr('x',x(r.soa)-4).attr('y',y(r.mean)-4).attr('width',8).attr('height',8);
        else mark.attr('cx',x(r.soa)).attr('cy',y(r.mean)).attr('r',4.5);
        mark.attr('fill',colors[group]).attr('stroke','white').attr('stroke-width',1)
          .attr('data-point-detail',JSON.stringify({Stage:stage.title,Condition:r.condition,Phase:r.phase,'SOA (ms)':r.soa,
            Units:stage.unit,'Participant-weighted mean':r.mean,'Sample SD of participant means':r.sd,'Participants (n)':r.n}));
      }
    }
  }else{
    const bins=histogram(atValues(stage),domain);
    svg.selectAll('rect.bin').data(bins).join('rect').attr('class','bin')
      .attr('x',b=>x(b.low)).attr('y',b=>y(b.n)).attr('width',b=>Math.max(0,x(b.high)-x(b.low)-1))
      .attr('height',b=>bottom-y(b.n)).attr('fill','#236594')
      .attr('data-point-detail',(b,i)=>JSON.stringify({Stage:stage.title,Units:stage.unit,'Bin lower (inclusive)':b.low,
        ['Bin upper ('+(i===bins.length-1?'inclusive':'exclusive')+')']:b.high,'Trial count':b.n}));
  }
  enablePointInspection(svg.node());
}
function renderTables() {
  const keys=new Set([...before.summary,...after.summary].map(r=>JSON.stringify([r.condition,r.phase,r.soa])));
  const body=$('summary').tBodies[0];body.replaceChildren();
  for(const key of [...keys].sort((a,b)=>{const x=JSON.parse(a),y=JSON.parse(b);return x[0].localeCompare(y[0])||x[1].localeCompare(y[1])||x[2]-y[2];})){
    const [condition,phase,soa]=JSON.parse(key),tr=document.createElement('tr'),heading=document.createElement('th');
    heading.scope='row';heading.textContent=condition+' · '+phase+' · '+soa+' ms';tr.append(heading);
    for(const [label,stage]of [['Before',before],['After',after]]){
      const r=stage.summary.find(r=>r.condition===condition&&r.phase===phase&&r.soa===soa),td=document.createElement('td');
      td.dataset.label=label;td.className='number';
      td.textContent=r?formats.mean(r.mean)+' · '+formats.mean(r.sd)+' · '+r.n:'Missing · Missing · 0';
      td.title=r?'Mean: '+r.mean+'; SD: '+r.sd+'; n: '+r.n:'No available cell';
      const units=document.createElement('small');units.textContent=stage.unit;td.append(units);tr.append(td);
    }body.append(tr);
  }
  if(!keys.size){const tr=body.insertRow(),td=tr.insertCell();td.colSpan=3;td.textContent='No participant means for this selection.';}
  $('audit').tBodies[0].replaceChildren();
  for(const s of stages){const tr=$('audit').tBodies[0].insertRow();
    if(s.id===Number(state.stage))tr.setAttribute('aria-current','step');
    [s.id+' · '+s.title,s.counts.rows,s.counts.plotted,s.counts.baseline].forEach((v,i)=>{
      const td=document.createElement(i?'td':'th');if(!i)td.scope='row';td.textContent=String(v);tr.append(td);
    });
  }
}
function render() {
  scheduled=false;if(!data)return;hidePoint();state=readState();
  const key=JSON.stringify({...state,stage:null,view:null});
  if(key!==cacheKey){stages=derive(data,state);cacheKey=key;}
  after=stages[Number(state.stage)];before=stages[Math.max(0,Number(state.stage)-1)];
  history.replaceState(null,'','#'+new URLSearchParams(state));
  $('step-title').textContent=after.id+' · '+after.title;
  $('step-description').textContent=descriptions[after.id];
  const removed=before.counts.at-after.counts.at;
  $('status').textContent=formats.count(removed)+' audio–tactile rows removed at this step. '+
    formats.count(after.counts.plotted)+' values available from '+after.counts.participants+' participants. '+
    (after.counts.missing?after.counts.missing+' retained AT rows have no plotted value. ':'')+
    (state.cohort==='full42'?'Full release includes the unresolved P011/P033 linkage.':'Primary cohort excludes P011/P033.');
  const sameUnits=before.unit===after.unit;
  $('scale-note').textContent=sameUnits?'Both panels use the same axes for a direct comparison.':
    'Units change at this step: each panel has its own value scale. Compare shape and coverage; do not subtract these values.';
  const domains=[before,after].map(s=>extent(state.view==='distribution'?atValues(s):s.people.map(r=>r.value)));
  if(sameUnits)domains[0]=domains[1]=[Math.min(domains[0][0],domains[1][0]),Math.max(domains[0][1],domains[1][1])];
  const maxCount=Math.max(1,...[before,after].flatMap((s,i)=>histogram(atValues(s),domains[i]).map(b=>b.n)));
  for(const [i,prefix,s]of [[0,'before',before],[1,'after',after]]){
    $(prefix+'-title').textContent=(after.id===0?'Starting view':prefix==='before'?'Before':'After')+' · '+s.title;
    $(prefix+'-counts').textContent=formats.count(s.counts.plotted)+' AT values · '+s.counts.participants+' participants · '+s.counts.baseline+' baseline rows';
    renderChart(prefix+'-chart',s,domains[i],maxCount);
  }
  $('chart-note').textContent=state.view==='distribution'?
    'All finite audio–tactile trial values, without sampling. 24 equal-width bins; heights are counts, not densities. Excluded and missing rows are tracked separately.':
    'Small dots: participant cell means. Large circles (Exhale) and squares (Inhale): equally weighted participant means. Blue: Control; red: Viscereality. Solid: Exhale; dashed: Inhale. No inferential intervals or fitted curves.';
  renderTables();measure();
  for(const id of ['csv','summary-csv','settings','svg'])$(id).disabled=false;
  $('csv').disabled=stages[0].rows.length===0;
  $('summary-csv').disabled=before.summary.length+after.summary.length===0;
  document.body.dataset.ready='true';document.body.dataset.stage=state.stage;
}
function schedule(){if(!scheduled){scheduled=true;requestAnimationFrame(render);}}
function trialRows() {
  const a=new Map(before.rows.map(r=>[r.trial_id,r])),b=new Map(after.rows.map(r=>[r.trial_id,r]));
  const original=stages[0].rows;
  return original.map(r=>({trial_id:r.trial_id,participant_id:r.participant_id,condition:r.condition,phase:r.phase,
    trial_type:r.trial_type,soa_ms:r.soa,recorded_rt_ms:r.rt,
    before_stage:before.title,before_retained:a.has(r.trial_id),before_value:a.get(r.trial_id)?.value??null,before_units:before.unit,
    after_stage:after.title,after_retained:b.has(r.trial_id),after_value:b.get(r.trial_id)?.value??null,after_units:after.unit,
    status:!b.has(r.trial_id)?(!r.eligible?'ineligible response or participant':!r.trimmed?'outside participant 2.5 SD':'below minimum RT'):
      !finite(b.get(r.trial_id).value)?(r.trial_type==='Baseline'&&after.id>=4?'baseline reference only':'missing value or undefined normalization'):'retained',
    baseline_mean_ms:b.get(r.trial_id)?.baseline??null}));
}
function summaryRows() {
  return [before,after].flatMap((s,i)=>s.summary.map(r=>({panel:i?'after':'before',stage:s.title,units:s.unit,...r})));
}
async function start() {
  await document.fonts.ready;
  const response=await fetch('data.json');if(!response.ok)throw new Error('Data request failed ('+response.status+').');
  const raw=await response.arrayBuffer();
  sourceHash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',raw))].map(b=>b.toString(16).padStart(2,'0')).join('');
  data=JSON.parse(new TextDecoder().decode(raw));
  const index=data.columns.indexOf('participant_id');
  for(const id of [...new Set(data.rows.map(r=>r[index]))].sort())$('participant').add(new Option(id,id));
  restore();
  document.querySelector('form').addEventListener('submit',e=>e.preventDefault());
  $('controls').addEventListener('change',schedule);
  $('reset').addEventListener('click',()=>{history.replaceState(null,'',location.pathname);restore();schedule();});
  addEventListener('hashchange',()=>{restore();schedule();});
  $('share').addEventListener('click',async()=>{
    try{await navigator.clipboard.writeText(location.href);$('status').textContent='Link copied with the current processing step and display settings.';}
    catch{$('status').textContent='Copy the current address from your browser; it includes this view’s settings.';}
  });
  $('csv').addEventListener('click',()=>download('preprocessing-trials.csv',csvText(trialRows()),'text/csv;charset=utf-8'));
  $('summary-csv').addEventListener('click',()=>download('preprocessing-summaries.csv',csvText(summaryRows()),'text/csv;charset=utf-8'));
  $('settings').addEventListener('click',()=>download('preprocessing-view.json',JSON.stringify({
    schema_version:1,settings:state,url:location.href,data_sha256:sourceHash,...data.provenance,
    stages:stages.map(s=>({stage:s.title,units:s.unit,counts:s.counts})),
    interpretation:'Descriptive only. Participant sample SD is not a confidence interval; no fitting or inference.',
  },null,2),'application/json'));
  $('svg').addEventListener('click',()=>{
    const sources=[...document.querySelectorAll('.chart svg')],width=Math.max(...sources.map(s=>Number(s.getAttribute('width'))));
    const output=document.createElementNS('http://www.w3.org/2000/svg','svg');
    output.setAttribute('xmlns','http://www.w3.org/2000/svg');output.setAttribute('width',String(width));
    const desc=document.createElementNS(output.namespaceURI,'desc');
    desc.textContent='Descriptive preprocessing comparison. '+new URLSearchParams(state)+'; data SHA-256: '+sourceHash;output.append(desc);
    let height=12;
    const text=content=>{
      const lines=[];let line='';
      for(const word of content.split(/\s+/)){
        const next=line?line+' '+word:word;
        if(line&&measureLineStats(prepareWithSegments(next,'18px Arial'),width-24).lineCount>1){lines.push(line);line=word;}
        else line=next;
      }if(line)lines.push(line);
      for(const line of lines){const node=document.createElementNS(output.namespaceURI,'text');height+=25;
        for(const [name,value]of Object.entries({x:12,y:height,'font-family':'Arial, sans-serif','font-size':18,fill:'#243240'}))node.setAttribute(name,String(value));
        node.textContent=line;output.append(node);
      }height+=10;
    };
    text('Descriptive preprocessing comparison');
    text(['cohort','participant','condition','phase','cutoff','normalization'].map(key=>
      ({cohort:'Cohort',participant:'Participant',condition:'Condition',phase:'Phase',cutoff:'Minimum RT',normalization:'Normalization'})[key]+': '+$(key).selectedOptions[0].textContent).join('; '));
    sources.forEach((s,i)=>{text((i?'After: ':'Before: ')+(i?after.title:before.title));
      const clone=s.cloneNode(true);clone.setAttribute('x','0');clone.setAttribute('y',String(height));
      output.append(clone);height+=Number(s.getAttribute('height'))+12;
    });
    text($('chart-note').textContent);
    if(after.id>=4)text('Correction: AT minus matched Baseline. Negative corrected milliseconds mean faster audio–tactile responses.');
    text('Descriptive values only; no fitted curves or inferential intervals.');
    output.setAttribute('height',String(height));output.setAttribute('viewBox','0 0 '+width+' '+height);
    const background=document.createElementNS(output.namespaceURI,'rect');
    background.setAttribute('width','100%');background.setAttribute('height','100%');background.setAttribute('fill','white');output.prepend(background);
    download('preprocessing-comparison.svg',output.outerHTML,'image/svg+xml');
  });
  for(const id of ['before-chart','after-chart'])resizePanel($(id),{label:id.replace('-',' '),minimumHeight:320});
  resizePanel($('table-panel'),{label:'Summary table',table:true,resizeHeight:false});
  const observer=new ResizeObserver(schedule);observer.observe(document.querySelector('main'));
  for(const id of ['before-chart','after-chart'])observer.observe($(id));
  document.addEventListener('panel-resize',schedule);render();
}
start().catch(error=>{
  $('status').textContent='The interactive data could not be loaded. Use the static comparison below or reload. '+error.message;
  const a=document.createElement('a');a.href='default-summary.html';a.textContent='Open static default comparison';$('status').append(' ',a);
  document.body.dataset.ready='error';
});
