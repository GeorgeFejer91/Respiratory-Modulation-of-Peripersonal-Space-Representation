// Pure descriptive calculations. Canonical eligibility/trim flags come from Python.
export const SOAS = [300,800,1500,2200,2700];
export const STAGES = [
  ['Released records','Recorded RT (ms)'],
  ['Eligible responses','RT (ms)'],
  ['2.5-SD filter','RT (ms)'],
  ['Minimum RT sensitivity','RT (ms)'],
  ['Matched baseline','AT − Baseline (ms)'],
  ['Within-person normalization','Normalized AT − Baseline'],
];
export const finite = v => typeof v === 'number' && Number.isFinite(v);
export function describe(values) {
  const a=values.filter(finite), n=a.length;
  const mean=n?a.reduce((s,v)=>s+v,0)/n:null;
  return {mean,sd:n>1?Math.sqrt(a.reduce((s,v)=>s+(v-mean)**2,0)/(n-1)):null,n};
}
function groups(rows,key) {
  const result=new Map();
  for(const row of rows){const id=key(row);if(!result.has(id))result.set(id,[]);result.get(id).push(row);}
  return result;
}
const cell=r=>JSON.stringify([r.participant_id,r.condition,r.phase]);
export function summaries(rows) {
  const at=rows.filter(r=>r.trial_type==='Audio-Tactile'&&finite(r.value)&&SOAS.includes(r.soa));
  const people=[...groups(at,r=>JSON.stringify([r.participant_id,r.condition,r.phase,r.soa])).values()]
    .map(a=>({participant_id:a[0].participant_id,condition:a[0].condition,phase:a[0].phase,soa:a[0].soa,
      value:describe(a.map(r=>r.value)).mean,n_trials:a.length}));
  const summary=[...groups(people,r=>JSON.stringify([r.condition,r.phase,r.soa])).values()]
    .map(a=>({condition:a[0].condition,phase:a[0].phase,soa:a[0].soa,...describe(a.map(r=>r.value))}))
    .sort((a,b)=>a.condition.localeCompare(b.condition)||a.phase.localeCompare(b.phase)||a.soa-b.soa);
  return {people,summary};
}
export function derive(data, settings) {
  const all=data.rows.map(a=>Object.fromEntries(data.columns.map((c,i)=>[c,a[i]])))
    .filter(r=>settings.cohort==='full42'||!['P011','P033'].includes(r.participant_id));
  const eligible=all.filter(r=>r.eligible), trimmed=all.filter(r=>r.trimmed);
  const floor=trimmed.filter(r=>settings.cutoff!=='200'||r.rt>=200);
  const baseline=new Map([...groups(floor.filter(r=>r.trial_type==='Baseline'),cell)]
    .map(([key,a])=>[key,describe(a.map(r=>r.rt)).mean]));
  const raw=a=>a.map(r=>({...r,value:r.rt}));
  const corrected=floor.map(r=>({...r,baseline:baseline.get(cell(r))??null,
    value:r.trial_type==='Audio-Tactile'&&finite(baseline.get(cell(r)))?r.rt-baseline.get(cell(r)):null}));
  const references=new Map([...groups(corrected.filter(r=>finite(r.value)),r=>r.participant_id)].map(([key,a])=>{
    const values=a.map(r=>r.value);
    return [key,{...describe(values),low:Math.min(...values),high:Math.max(...values)}];
  }));
  const normalized=corrected.map(r=>{
    const ref=references.get(r.participant_id),range=settings.normalization==='range';
    const scale=ref?(range?ref.high-ref.low:ref.sd):null;
    return {...r,value:finite(r.value)&&finite(scale)&&scale>0?(r.value-(range?ref.low:ref.mean))/scale:null};
  });
  return [raw(all),raw(eligible),raw(trimmed),raw(floor),corrected,normalized].map((source,i)=>{
    // Display selections never redefine trimming, baseline or normalization.
    const rows=source.filter(r=>['participant','condition','phase'].every(k=>{
      const field=k==='participant'?'participant_id':k;return settings[k]==='all'||r[field]===settings[k];
    }));
    const at=rows.filter(r=>r.trial_type==='Audio-Tactile');
    return {id:i,title:STAGES[i][0],unit:i===5?(settings.normalization==='range'?'0–1 range':'z-score'):'ms',
      rows,...summaries(rows),counts:{rows:rows.length,at:at.length,
        baseline:rows.filter(r=>r.trial_type==='Baseline').length,
        plotted:at.filter(r=>finite(r.value)).length,missing:at.filter(r=>!finite(r.value)).length,
        participants:new Set(at.filter(r=>finite(r.value)).map(r=>r.participant_id)).size}};
  });
}
export function histogram(values, domain, count=24) {
  const width=(domain[1]-domain[0]||1)/count;
  const bins=Array.from({length:count},(_,i)=>({low:domain[0]+i*width,high:domain[0]+(i+1)*width,n:0}));
  for(const v of values.filter(finite))bins[Math.max(0,Math.min(count-1,Math.floor((v-domain[0])/width)))].n++;
  return bins;
}
