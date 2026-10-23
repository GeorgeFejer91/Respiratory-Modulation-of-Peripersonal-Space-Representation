import './vendor/d3/d3.min.js';
import {violinDensity} from './pivot/pivot-chart.mjs';
import {enablePointInspection,hidePoint} from './pivot/point-inspector.js';
import {prepareWithSegments,measureLineStats} from './pivot/vendor/pretext/dist/layout.js';

const d3=globalThis.d3;
const colors=['#4477AA','#CC6677','#117733','#882255','#AA4499','#000000'];
const layers=['dots','density','box','mean','ci'];
const download=(name,text,type)=>{
  const url=URL.createObjectURL(new Blob([text],{type})),link=document.createElement('a');
  link.href=url;link.download=name;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
};

export function mountPhaseExplorer(host,data,measureSvg){
  const controls=document.getElementById('phase-controls'),panel=host.closest('.plot-panel');
  const outcome=document.getElementById('phase-outcome'),status=document.getElementById('phase-view-status');
  let displayed=[],scheduled=false,geometry='';
  const measureControls=()=>{
    for(const node of controls.querySelectorAll('[data-phase-label]')){
      const s=getComputedStyle(node),width=node.clientWidth-parseFloat(s.paddingLeft)-parseFloat(s.paddingRight);
      const prepared=prepareWithSegments(node.textContent,`${s.fontStyle} ${s.fontWeight} ${s.fontSize} ${s.fontFamily}`,{letterSpacing:parseFloat(s.letterSpacing)||0});
      node.dataset.phaseFit=measureLineStats(prepared,Math.max(1,width)).maxLineWidth<=width+1?'fit':'reflow';
    }
  };
  function render(){
    scheduled=false;
    const checks=[...controls.querySelectorAll('[data-phase-group]')];
    checks.find(n=>n.dataset.phaseGroup==='Baseline').disabled=outcome.value==='corrected';
    const names=checks.filter(n=>n.checked&&!n.disabled).map(n=>n.dataset.phaseGroup);
    const enabled=new Set([...controls.querySelectorAll('[data-phase-layer]:checked')].map(n=>n.dataset.phaseLayer));
    const style=getComputedStyle(host),font=parseFloat(style.fontSize),width=host.clientWidth;
    const next=JSON.stringify([names,[...enabled],outcome.value,width,font,style.letterSpacing,panel?.style.height]);
    if(next===geometry){measureControls();return;}geometry=next;
    hidePoint();host.replaceChildren();
    const view=data.phaseExplorer[outcome.value],groups=view.groups.filter(g=>names.includes(g.trial_group));
    displayed=view.rows.filter(r=>names.includes(r.trial_group));
    const mask=layers.reduce((sum,layer,i)=>sum+(enabled.has(layer)?1<<i:0),0);
    Object.assign(host.dataset,{toolbox:'d3-7.9.0',outcome:outcome.value,groups:String(groups.length),layers:String(mask)});
    const corrected=outcome.value==='corrected',label=corrected?'AT − Baseline':'Raw RT';
    document.getElementById('phase-note-outcome').textContent=corrected?'Baseline-corrected RT differences':'Raw RT differences';
    document.getElementById('phase-caption').textContent=`${label} phase differences across trial types`;
    document.getElementById('phase-view-formula').textContent=corrected?
      'Δ = (Inhale AT − Inhale Baseline) − (Exhale AT − Exhale Baseline), in ms. Baseline is omitted because self-subtraction gives zero.':
      'Δ = Inhale RT − Exhale RT, in ms. Baseline pools its retained trials within each condition and phase.';
    for(const button of controls.querySelectorAll('[data-phase-export]'))button.disabled=!displayed.length;
    status.textContent=groups.length?`${label}: ${groups.length} trial types, 40 participants per type. Positive Δ means slower during inhale.${mask?'':' No layers selected; turn on a layer to show data.'}`:
      'No trial types selected. Select a trial type or reset the plot.';
    if(!groups.length){host.textContent='Select a trial type to display its paired differences.';if(panel)panel.style.minHeight='120px';measureControls();return;}
    const stack=width<font*14,tail=stack?Math.max(160,font*4):Math.max(100,font*3.6);
    const minimumStep=stack?font*5.8:Math.max(83,font*4.5);
    const minimum=minimumStep*groups.length+tail;
    if(panel)panel.style.minHeight=`${minimum+12}px`;
    const height=Math.max(minimum,(parseFloat(panel?.style.height)||0)-12),step=(height-tail)/groups.length;
    const left=stack?28:Math.max(112,font*6.6),right=Math.max(16,font*1.6);
    const extent=d3.extent([...displayed.map(r=>r.delta_ms),...groups.flatMap(g=>[g.ci_low,g.ci_high]),0]);
    const pad=(extent[1]-extent[0]||1)*.08;
    const x=d3.scaleLinear().domain([extent[0]<0?extent[0]-pad:0,extent[1]+pad]).range([left,width-right]);
    const svg=d3.select(host).append('svg').attr('xmlns','http://www.w3.org/2000/svg')
      .attr('width',width).attr('height',height).attr('viewBox',`0 0 ${width} ${height}`)
      .attr('role','group').attr('aria-label',`${label}: Inhale minus Exhale paired differences in ms`)
      .attr('data-xmin',x.domain()[0]).attr('data-xmax',x.domain()[1])
      .style('font-family','Arial, sans-serif').style('font-size',`${font}px`).style('background','white').style('color','#243240');
    svg.append('title').text(`${label}: Inhale − Exhale (ms)`);
    svg.append('desc').text(`Exploratory primary40 participant differences. Equal condition weights; pointwise paired t 95% confidence intervals. ${document.getElementById('phase-view-formula').textContent}`);
    const cy=i=>stack?font+i*step+font*2+40:50+i*step;
    const zero=stack?groups.map((_,i)=>`M${x(0)},${cy(i)-38}V${cy(i)+44}`).join(''):`M${x(0)},18V${height-font*3}`;
    svg.append('path').attr('d',zero).attr('fill','none').attr('stroke','#243240').attr('stroke-dasharray','5 4').attr('data-zero-baseline','');
    const count=Math.max(2,Math.min(5,Math.floor((width-left-right)/(font*3))));
    const ticks=[...new Set([...x.ticks(count),0])].sort((a,b)=>a-b);
    svg.append('g').attr('transform',`translate(0,${height-font*2.3})`).call(d3.axisBottom(x).tickValues(ticks).tickSizeOuter(0))
      .attr('font-family','Arial, sans-serif').attr('font-size',font*.86);
    svg.append('text').attr('x',width/2).attr('y',height-5).attr('text-anchor','middle').attr('fill','#243240').attr('font-size',font*.94).text('Δ RT (ms)');
    const rows=svg.selectAll('g.phase-row').data(groups,g=>g.trial_group).join('g').attr('class','phase-row');
    rows.each(function(summary,i){
      const row=d3.select(this),name=summary.trial_group,color=colors[data.phase.trial_groups.findIndex(g=>g.trial_group===name)];
      const records=displayed.filter(r=>r.trial_group===name),values=records.map(r=>r.delta_ms).sort(d3.ascending),center=cy(i);
      const line=(x1,y1,x2,y2,attributes={})=>{const mark=row.append('line').attr('x1',x1).attr('y1',y1).attr('x2',x2).attr('y2',y2).attr('stroke',color);for(const [k,v]of Object.entries(attributes))mark.attr(k,v);return mark;};
      if(enabled.has('density')){
        const density=violinDensity(values);
        if(density)row.append('path').datum(density.points).attr('d',d3.area().x(p=>x(p.value)).y0(center-8).y1(p=>center-8-p.width*28))
          .attr('fill',color).attr('fill-opacity',.2).attr('stroke',color).attr('data-density','').attr('data-bandwidth',density.bandwidth);
      }
      if(enabled.has('box')){
        const q1=d3.quantileSorted(values,.25),median=d3.quantileSorted(values,.5),q3=d3.quantileSorted(values,.75),iqr=q3-q1;
        const box=row.append('g').attr('data-box','').attr('data-q1',q1).attr('data-median',median).attr('data-q3',q3);
        box.append('line').attr('x1',x(values.find(v=>v>=q1-1.5*iqr))).attr('x2',x(values.findLast(v=>v<=q3+1.5*iqr))).attr('y1',center).attr('y2',center).attr('stroke',color);
        box.append('rect').attr('x',x(q1)).attr('y',center-4).attr('width',x(q3)-x(q1)).attr('height',8).attr('fill','white').attr('stroke',color);
        line(x(median),center-4,x(median),center+4,{'stroke-width':2});
      }
      if(enabled.has('dots'))row.selectAll('circle.person').data(records,r=>r.participant_id).join('circle')
        .attr('class','person').attr('cx',r=>x(r.delta_ms)).attr('cy',(_,j)=>center+12+j/Math.max(1,records.length-1)*13).attr('r',2.8).attr('fill',color)
        .attr('data-phase-point','').attr('data-point-detail',r=>JSON.stringify({Participant:r.participant_id,'Trial group':name,Outcome:label,
          'Exhale RT (ms)':r.exhale_ms,'Inhale RT (ms)':r.inhale_ms,'Inhale − Exhale (ms)':r.delta_ms,
          ...(corrected?{'Exhale raw AT (ms)':r.raw_exhale_ms,'Inhale raw AT (ms)':r.raw_inhale_ms,'Exhale Baseline (ms)':r.baseline_exhale_ms,'Inhale Baseline (ms)':r.baseline_inhale_ms}:{})}));
      if(enabled.has('ci')){
        line(x(summary.ci_low),center+38,x(summary.ci_high),center+38,{'stroke-width':2,'data-phase-ci':''});
        for(const value of [summary.ci_low,summary.ci_high])line(x(value),center+34,x(value),center+42);
      }
      if(enabled.has('mean'))row.append('circle').datum(summary).attr('cx',x(summary.mean)).attr('cy',center+38).attr('r',4).attr('fill','white').attr('stroke',color).attr('stroke-width',2)
        .attr('data-phase-mean','').attr('data-point-detail',JSON.stringify({Statistic:'Participant mean','Trial group':name,Outcome:label,'Inhale − Exhale (ms)':summary.mean,
          'Pointwise 95% CI low (ms)':summary.ci_low,'Pointwise 95% CI high (ms)':summary.ci_high,n:summary.n}));
      const labels=[name,...(enabled.has('mean')?[`${summary.mean>=0?'+':''}${summary.mean.toFixed(2)} ms`]:[])];
      row.selectAll('text.row-label').data(labels).join('text').attr('class','row-label').attr('x',stack?4:left-9)
        .attr('y',(_,j)=>stack?font+i*step+j*font:center-1+j*font).attr('text-anchor',stack?'start':'end').attr('fill','#243240').attr('font-size',font*.84).text(d=>d);
    });
    enablePointInspection(svg.node());measureSvg(svg.node());measureControls();host.closest('figure').dataset.interactive='ready';
  }
  function schedule(){if(!scheduled){scheduled=true;requestAnimationFrame(render);}}
  controls.addEventListener('change',schedule);
  controls.querySelector('#phase-reset').addEventListener('click',()=>{
    outcome.value='raw';for(const check of controls.querySelectorAll('input[type="checkbox"]'))check.checked=true;render();
  });
  controls.querySelector('#phase-csv').addEventListener('click',()=>{
    const fields=['participant_id','trial_group','exhale_ms','inhale_ms','delta_ms','raw_exhale_ms','raw_inhale_ms','baseline_exhale_ms','baseline_inhale_ms'];
    const cell=v=>`"${String(v).replaceAll('"','""')}"`;
    const rows=[['outcome',...fields],...displayed.map(r=>[outcome.value,...fields.map(k=>r[k])])];
    download(`phase-${outcome.value}-values.csv`,rows.map(r=>r.map(cell).join(',')).join('\n')+'\n','text/csv;charset=utf-8');
  });
  controls.querySelector('#phase-svg').addEventListener('click',()=>download(`phase-${outcome.value}.svg`,new XMLSerializer().serializeToString(host.querySelector('svg')),'image/svg+xml'));
  const observer=new ResizeObserver(schedule);observer.observe(host);observer.observe(controls);if(panel)observer.observe(panel);
  document.addEventListener('panel-resize',schedule);document.fonts.ready.then(schedule);render();
}
