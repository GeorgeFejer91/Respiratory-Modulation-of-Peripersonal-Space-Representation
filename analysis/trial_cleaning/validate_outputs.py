"""Independently audit the complete native cleaning/time-adjustment export."""
import csv, hashlib, json, subprocess, sys, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import special

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'analysis/trial_cleaning'))
import run, session_time
OUT,LOCAL=run.OUT,run.LOCAL
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
people,trials,eligible,old,ids,counts=run.source()
assert len(ids)==40 and not {'P011','P033'} & set(ids)
audit=pd.read_csv(OUT/'trial_audit.csv')
assert len(audit)==len(trials)==17114 and audit.trial_id.is_unique
assert int(audit.eligible_hit.sum())==13694
assert int((audit.full_global_keep & ~audit.full_local_keep).sum())==71
assert not (audit.early_global_keep ^ audit.early_local_keep).any()
assert json.loads((OUT/'trial_plot_checks.json').read_text())['plotted_hits']==13694
ordered=pd.MultiIndex.from_product([ids,run.CELL_NAMES],names=['participant_id','cell'])
model_configs=[(n,e,r,s,0) for n,e,r,s in run.CONFIGS]+[(n,False,r,s,k) for n,k,r,s in session_time.CONFIGS]
nonzero=0;passed=0
for name,early,rolling,shape,order in model_configs:
    info=json.loads((OUT/f'{name}_run.json').read_text())
    expected_hash=session_time.definition_hash() if order else run.definition_hash()
    assert info['definition_sha256']==expected_hash,name
    gate=(info['divergences']==0 and info['max_rhat']<=1.01 and min(info['min_bulk_ess'],info['min_tail_ess'])>=400)
    assert info['gate']==gate,name
    passed+=int(gate)
    assert info['draws_per_chain'] in [2000,4000] and info['tune'] in [2000,4000]
    rows,_,_=run.prepare(eligible,early)
    at,baseline=run.tensors(rows,ids)
    parameters=pd.read_csv(OUT/f'{name}_participant_parameters.csv')
    effects=pd.read_csv(OUT/f'{name}_effects.csv')
    assert len(parameters)==800
    with np.load(LOCAL/f'{name}_draws.npz') as d:
        def flat(key):return d[key].reshape(-1,len(ids),4)
        m,w,s=flat('midpoint_cm'),flat('width_cm'),flat('sharpness_per_cm')
        np.testing.assert_allclose(s,1/(4*w),rtol=1e-12,atol=1e-14)
        assert (flat('amplitude')>0).all()
        if shape=='visible95':
            assert (special.expit((10-m)/w)<=.05+1e-11).all()
            assert (special.expit((100-m)/w)>=.95-1e-11).all()
        for quantity in ['midpoint_cm','width_cm','sharpness_per_cm','amplitude','corrected_intercept']:
            q=np.quantile(flat(quantity),[.025,.5,.975],axis=0).reshape(3,-1).T
            exported=parameters[parameters.quantity==quantity].set_index(['participant_id','cell']).loc[ordered]
            np.testing.assert_allclose(exported[['ci_low','median','ci_high']],q,rtol=1e-11,atol=1e-10,err_msg=name+'/'+quantity)
        for quantity in ['midpoint_cm','sharpness_per_cm']:
            a=flat(quantity)
            direct=np.stack([((a[:,:,2]+a[:,:,3]-a[:,:,0]-a[:,:,1])/2).mean(1),
                             ((a[:,:,1]-a[:,:,0]+a[:,:,3]-a[:,:,2])/2).mean(1),
                             (a[:,:,3]-a[:,:,2]-a[:,:,1]+a[:,:,0]).mean(1)],axis=-1)
            for j,term in enumerate(run.EFFECTS[:3]):
                row=effects[(effects.quantity==quantity+'_effect') & (effects.term==term)].iloc[0]
                np.testing.assert_allclose([row.ci_low,row.posterior_median,row.ci_high],np.quantile(direct[:,j],[.025,.5,.975]),rtol=1e-11,atol=1e-10)
                nonzero+=int(row.ci_low>0 or row.ci_high<0)
        if order:
            ta,tb=session_time.time_arrays(rows,ids,people)
            mu=1000*(d['corrected_curve'].reshape(-1,len(ids),4,5).mean(0)+flat('baseline_mean').mean(0)[...,None])
            gamma=d['time_trend'].reshape(-1,len(ids),order).mean(0)
            exported=pd.read_csv(OUT/'session_fit_quality.csv')
            exported=exported[exported.model==name].set_index(['participant_id','cell'])
            for i,pid in enumerate(ids):
                for c,cell in enumerate(run.CELL_NAMES):
                    observed=[];predicted=[];design=[]
                    for distance in range(5):
                        keep=np.isfinite(at[i,c,distance])
                        t=ta[i,c,distance,keep]
                        b=np.column_stack([t**k for k in range(1,order+1)])
                        y=at[i,c,distance,keep]
                        observed.extend(y);predicted.extend(mu[i,c,distance]+1000*b@gamma[i])
                        design.extend(np.column_stack([np.eye(5)[np.full(len(t),distance)],b]))
                    observed,predicted,design=map(np.asarray,(observed,predicted,design))
                    total=np.sum((observed-observed.mean())**2)
                    r2=1-np.sum((observed-predicted)**2)/total
                    ceiling=1-np.sum((observed-design@np.linalg.lstsq(design,observed,rcond=None)[0])**2)/total
                    assert r2<=ceiling+1e-10
                    np.testing.assert_allclose(exported.loc[(pid,cell),'trial_RT_R2_including_time'],r2,atol=1e-10)

pred=pd.read_csv(OUT/'held_distance_predictions.csv')
session_pred=pd.read_csv(OUT/'session_held_distance_predictions.csv')
assert len(pred)==2400 and len(session_pred)==800
allpred=pd.concat([pred,session_pred],ignore_index=True)
keys=['held_distance_cm','participant_id','cell']
reference=pred[pred.model=='global_raw'].set_index(keys).sort_index()
for model,g in allpred.groupby('model'):
    assert len(g)==800 and not g.duplicated(keys).any()
    current=g.set_index(keys).sort_index()
    np.testing.assert_allclose(current[['n_target','observed_AT_ms']],reference[['n_target','observed_AT_ms']],rtol=0,atol=0)
    assert g.groupby('held_distance_cm').size().eq(160).all()
    for held,distance in enumerate(run.X):
        filename=(f'session_cv_{held}.json' if model.startswith('session_')
                  else f'cv_{model}_{held}.json')
        attempts=json.loads((OUT/filename).read_text())
        assert 1<=len(attempts)<=2
        info=attempts[-1]
        gate=(info['divergences']==0 and info['prediction_rhat']<=1.01
              and min(info['prediction_bulk_ess'],info['prediction_tail_ess'])>=400)
        assert info['prediction_gate']==gate
        fold=g[g.held_distance_cm==distance]
        assert fold.prediction_gate.eq(gate).all()
        assert fold.full_parameter_gate.eq(info['gate']).all()
for pdf,expected in [('every_trial_distributions.pdf',42),('individual_curves.pdf',80),('session_individual_curves.pdf',40)]:
    text=subprocess.check_output(['pdfinfo',str(OUT/pdf)],text=True)
    pages=int(next(l.split(':',1)[1] for l in text.splitlines() if l.startswith('Pages:')))
    assert pages==expected
    extracted=subprocess.check_output(['pdftotext','-layout',str(OUT/pdf),'-'],text=True)
    chunks=[p for p in extracted.split('\f') if p.strip()]
    assert len(chunks)==expected
    if pdf=='every_trial_distributions.pdf':
        for p,person in zip(chunks,people):
            assert person['participant_id'] in p
            assert 'Horizontal jitter is layout only' in p
    else:
        expected_ids=[pid for pid in ids for _ in range(2 if expected==80 else 1)]
        for p,pid in zip(chunks,expected_ids):
            assert pid in p and ('imposed' in p or 'model geometry' in p)
for family in ['baseline_effects','directional_sigmoid','visible_sigmoid']:
    base=ROOT/'results'/family
    old_manifest=json.loads((base/'manifest.json').read_text())
    for kind in ['input_sha256','source_sha256','output_sha256']:
        for key,want in old_manifest.get(kind,{}).items():
            path=next((p for p in (ROOT/key,base/key,ROOT/'data/raw'/key) if p.is_file()),None)
            assert path is not None,(family,kind,key)
            assert sha(path)==want,(family,kind,key)
m=json.loads((OUT/'manifest.json').read_text())
for kind in ['input_sha256','source_sha256','reference_sha256']:
    for key,want in m[kind].items():assert sha(ROOT/key)==want,(kind,key)
for key,want in m['local_trace_sha256'].items():assert sha(LOCAL/key)==want,key
assert set(m['artifacts_sha256'])=={p.name for p in OUT.iterdir() if p.is_file() and p.name not in ['manifest.json','trial_cleaning_results.zip']}
for key,want in m['artifacts_sha256'].items():assert sha(OUT/key)==want,key
with zipfile.ZipFile(OUT/'trial_cleaning_results.zip') as z:
    assert set(z.namelist())=={p.name for p in OUT.iterdir() if p.is_file() and p.suffix!='.zip'}
    for name in z.namelist():assert z.read(name)==(OUT/name).read_bytes(),name
print(f'PASS: 13 fits ({passed} full gates passed), all 10,400 parameter rows and 78 primary contrasts ({nonzero} nonzero intervals), raw-trial R2 identities/ceilings, 3,200 matched prediction rows, 162 labelled pages, prior results and all source/input/trace/artifact/ZIP hashes.')
