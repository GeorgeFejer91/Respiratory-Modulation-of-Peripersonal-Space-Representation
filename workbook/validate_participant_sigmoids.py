"""Independent numerical references for the individual-parameter extension."""

import argparse
import csv
import json
from pathlib import Path

import numpy as np
from scipy.special import expit
from scipy.stats import spearmanr
from statsmodels.nonparametric.kernel_regression import KernelReg

from descriptive_sigmoid import LABELS
from participant_sigmoid import PenalizedGrid, X, METRICS, CELL_NAMES
from paper_analysis import clean
from preparation import FILES, load_pair


def scalar_profile(y, shapes, variance=1., center=None, strength=0.):
    best=None
    for m,w in shapes:
        q=expit((X-m)/w);design=np.column_stack([np.ones(5),q])
        b,a=np.linalg.lstsq(design,y,rcond=None)[0]
        a=np.clip(a,-500.,500.);b=np.mean(y-a*q)
        loss=np.sum((y-b-a*q)**2)/max(variance,1.)
        if strength:loss+=strength*(((m-center[0])/.25)**2+(np.log(w/center[1])/np.log(2))**2)
        if best is None or round(loss,10)<best[0]:best=(round(loss,10),np.array([b,a,m,w]))
    return best[1]


def validate(root, report_path):
    report=json.loads(report_path.read_text());r=report['participant_sigmoids']
    people,trials=load_pair(*[(root/'data/raw'/n).read_bytes() for n in FILES])
    retained,_,_=clean(people,trials)
    ids=r['plot_data']['participant_ids'];n=len(ids)
    assert n==42 and r['curve_count']==168 and r['candidate_count']==84
    # Independent source-record comparison, including schedule fields omitted by the hash audit.
    aa=[a for a in trials if a['participant_id']=='P011'];bb=[a for a in trials if a['participant_id']=='P033']
    assert len(aa)==len(bb)==408
    for a,b in zip(aa,bb):
        assert a['condition']!=b['condition']
        assert all(a[k]==b[k] for k in a if k not in ('participant_id','trial_id','condition'))
    pa=next(a for a in people if a['participant_id']=='P011');pb=next(a for a in people if a['participant_id']=='P033')
    assert any(pa[k]!=pb[k] for k in pa if k.startswith('maia2_item'))
    audit=r['linkage_audit']['groups'];assert audit[0]['participant_ids']==['P011','P033']
    folds=r['prediction']['outer_folds'];seen=[]
    for fold in folds:
        members=fold['test_participant_ids'];seen.extend(members)
        assert ('P011' in members)==('P033' in members)
    assert sorted(seen)==ids
    # Fixed selected mean/Gaussian method; changing the winner requires a new reference.
    method=r['selected_method']
    assert method['aggregation']=='mean' and method['smoother']=='gaussian_constant'
    means=np.array(r['plot_data']['raw_means']);variances=np.array(r['plot_data']['raw_se'])**2
    smooth=np.empty_like(means)
    for i,j in np.ndindex(n,4):
        smooth[i,j]=KernelReg(means[i,j],X,'c',reg_type='lc',bw=[method['bandwidth']]).fit(X)[0]
    # Solve each finite-grid candidate separately using lstsq, including the leave-record-group-out prior.
    shapes=PenalizedGrid().shapes;reference=np.empty((n,4,4))
    for i,pid in enumerate(ids):
        excluded={'P011','P033'} if pid in ('P011','P033') else {pid}
        pooled=smooth[[a not in excluded for a in ids]].mean(0)
        for j in range(4):
            center=scalar_profile(pooled[j],shapes)[2:]
            reference[i,j]=scalar_profile(smooth[i,j],shapes,variances[i,j].mean(),center,method['penalty'])
    pars=np.array(r['plot_data']['parameters']);joint=np.array(r['plot_data']['shared_parameters'])
    error=float(np.max(abs(reference-pars)));np.testing.assert_allclose(reference,pars,atol=1e-8,rtol=0)
    joint_errors=[]
    for i in range(n):
        assert np.ptp(joint[i,:,0])==np.ptp(joint[i,:,1])==0
        q=expit((X-joint[i,:,2,None])/joint[i,:,3,None]).ravel()
        design=np.column_stack([np.ones(20),q]);weight=np.repeat(1/np.maximum(variances[i].mean(-1),1.),5)
        b,a=np.linalg.lstsq(design*np.sqrt(weight[:,None]),smooth[i].ravel()*np.sqrt(weight),rcond=None)[0]
        a=np.clip(a,-500,500);b=np.average(smooth[i].ravel()-a*q,weights=weight)
        joint_errors.append(float(np.max(abs(np.array([b,a])-joint[i,0,:2]))))
    assert max(joint_errors)<1e-8
    for rows,pp,scores in ((r['parameters'],pars,r['participant_scores']),(r['shared_parameters'],joint,r['shared_participant_scores'])):
        for i,pid in enumerate(ids):
            record=next(a for a in scores if a['participant_id']==pid)
            for j,cell in enumerate(CELL_NAMES):
                row=next(a for a in rows if (a['participant_id'],a['condition'],a['phase'])==(pid,*LABELS[j]))
                b,a,m,w=pp[i,j];expected=[10+90*m,1/(360*w),a/(360*w)]
                np.testing.assert_allclose([row[k] for k in METRICS],expected,atol=1e-10)
                assert row['normalization_stable']==(row['amplitude_ci_low']>0 or row['amplitude_ci_high']<0)
                if not row['flat']:
                    np.testing.assert_allclose((b+a*.5-row['lower_plateau_ms'])/abs(a),.5,atol=1e-10)
                for k,v in zip(METRICS,expected):np.testing.assert_allclose(record[k+'_'+cell],v,atol=1e-10)
            for k in METRICS:
                delta=sum(record[k+'_'+c] for c in CELL_NAMES[2:])/2-sum(record[k+'_'+c] for c in CELL_NAMES[:2])/2
                np.testing.assert_allclose(record[k+'_condition_delta'],delta,atol=1e-10)
    corr_errors=[]
    for spec in [r]+r['linkage_sensitivities']:
        for testkey,scorekey in (('associations','participant_scores'),('shared_associations','shared_participant_scores')):
            assert len(spec[testkey])==126 and sum(t['scope']=='main' for t in spec[testkey])==27
            for test in spec[testkey]:
                pairs=np.array([(a[test['x']],a[test['y']]) for a in spec[scorekey]],dtype=float)
                pairs=pairs[np.isfinite(pairs).all(1)];assert len(pairs)==test['n']
                rho=float(spearmanr(pairs[:,0],pairs[:,1]).statistic)
                if np.isfinite(rho):
                    corr_errors.append(abs(rho-test['rho']));assert corr_errors[-1]<1e-12
                else:assert test['rho'] is None
    normalized_path=report_path.parent/'participant_normalized_rt.csv'
    normalized_count=None
    if normalized_path.exists():
        normalized=list(csv.DictReader(normalized_path.open()));byid={a['trial_id']:a for a in retained if a['trial_type']=='Audio-Tactile'}
        assert len(normalized)==len(byid)==8916
        parameter_map={(a['participant_id'],a['condition'],a['phase']):a for a in r['parameters']}
        for row in normalized:
            raw=byid[row['trial_id']];assert row['reaction_time_ms']==str(raw['reaction_time_ms'])
            p=parameter_map[(raw['participant_id'],raw['condition'],raw['phase'])]
            expected=(float(raw['reaction_time_ms'])-p['lower_plateau_ms'])/abs(p['signed_amplitude_ms'])
            np.testing.assert_allclose(float(row['normalized_rt']),expected,rtol=1e-12)
        normalized_count=len(normalized)
    return {'status':'passed','individual_grid_max_parameter_error':error,'shared_conditional_ols_max_error':max(joint_errors),
            'correlation_checks':len(corr_errors),'max_spearman_error':max(corr_errors),'normalized_trials_checked':normalized_count,
            'source_records_matched':408,'folds_checked':len(folds),
            'scope':'Independent KernelReg + scalar lstsq grid objective and pooling; common-plateau conditional weighted OLS; parameter units/deltas; SciPy correlations across both models and exclusions; source linkage and folds. Numerical agreement does not establish scientific identification or global shared-model optimality.'}


if __name__=='__main__':
    root=Path(__file__).resolve().parents[1];parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report',type=Path,default=root/'results/browser-analysis/analysis_results.json')
    parser.add_argument('--output',type=Path,default=root/'.for-ai-local/participant-sigmoids/validation.json')
    args=parser.parse_args();result=validate(root,args.report)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
