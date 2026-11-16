"""Test exactly matched and interpolated baselines under a +500 ms offset."""

import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.stats import f, t

from profile import COHORTS, envelope, group_data, moments
from profile_grid import REFERENCES, ShapeGrid, WeightedBasis, diag_cov, intervals, predict_folds
from screen import DISTANCES, EFFECTS, OUT, ROOT, SUMMARY_LABELS, W, cohort_mask, load_data, write_csv

SOA = np.array([2700,2200,1500,800,300])
OFFSET = 500
SEED = 20261123
REPS = 96


def matching(method):
    targets = SOA+OFFSET
    if method=="exact":
        included = np.isin(targets,SOA)
    else:
        included = (targets>=SOA.min()) & (targets<=SOA.max())
    base = np.eye(len(SOA))
    h = np.stack([np.interp(targets[included],SOA[::-1],v[::-1]) for v in base],axis=-1)
    used = h.any(0)
    return included,used,h[:,used]


def prepare(at,baseline,selected,used,mapping):
    ma,va,da = moments(at[...,selected,:])
    mb,vb,db = moments(baseline[...,used,:])
    means = ma-mb@mapping.T
    cov = diag_cov(va)+np.einsum("ib,...b,jb->...ij",mapping,vb,mapping)
    ds = np.concatenate((da,db),axis=-1)
    d = len(mapping)
    cells = np.concatenate((means,means.reshape(len(means),2,2,d).mean(2)),axis=1)
    all_cov = np.concatenate((cov,cov.reshape(len(cov),2,2,d,d).sum(2)/4),axis=1)
    all_df = np.concatenate((np.concatenate((ds,ds),axis=-1),ds.reshape(len(ds),2,-1)),axis=1)
    available = np.isfinite(all_cov).all(axis=(-2,-1)) & (all_df>0).all(-1)
    radii = np.full(cells.shape[:-1],np.nan)
    for i,j in zip(*np.where(available)):
        degrees = all_df[i,j,:ds.shape[-1]] if j<4 else all_df[i,j]
        radii[i,j] = envelope(tuple(np.sort(degrees)))[0]
    return cells,np.where(available[...,None,None],all_cov,np.eye(d)),radii


def group_limit(n,d):
    return d*(n-1)/(n-d)*f.ppf(.95,d,n-d)


def calc(means,cov,distance):
    grid = ShapeGrid.logistic(distance)
    candidates = grid.shapes.reshape(-1,len(distance))
    loss, spans = WeightedBasis(cov,candidates,span_limit=1000.).surface(means)
    surface = loss.reshape(*means.shape[:-1],len(grid.midpoints),len(grid.relative_width))
    reference = WeightedBasis(cov,grid.reference_shapes,span_limit=1000.).surface(means)[0]
    return grid,surface,spans,reference


def profile(means,cov,radii,distance,ids,tags):
    grid,loss,spans,ref = calc(means,cov,distance)
    inside = (grid.midpoints>distance[0]) & (grid.midpoints<distance[-1])
    rows = []
    for i,pid in enumerate(ids):
        for j,cell in enumerate(SUMMARY_LABELS):
            row = dict(tags,participant=pid,cell=cell)
            radius = radii[i,j]
            if not np.isfinite(radius):
                rows.append(dict(row,status="variance_unavailable"))
                continue
            opt = loss[i,j].argmin()
            support = (loss[i,j]<=radius).any(-1)
            refs = [key for key,ok in zip(REFERENCES,ref[i,j]<=radius) if ok]
            localized = support.any() and not (support & ~inside).any() and not refs
            rows.append(dict(row,status="localized" if localized else "unresolved",
                conditional_midpoint_cm=grid.midpoints[opt//len(grid.relative_width)],
                conditional_fitted_span_ms=spans[i,j,opt],
                intervals_cm=json.dumps(intervals(support,grid.midpoints)),
                compatible_points=int(support.sum()),tested_points=len(support),
                compatible_references=" ".join(refs),first_probe_cm=distance[0],last_probe_cm=distance[-1]))
    return rows


def exact_results(at,b,ids):
    valid,used,m = matching("exact")
    ma = np.nanmean(at[...,valid,:],axis=-1)
    mb = np.nanmean(b[...,used,:],axis=-1)
    adjusted = ma-mb@m.T
    gradient = adjusted[...,1]-adjusted[...,0]
    records = [dict(participant=pid,cell=cell,near_ms=mean[0],far_ms=mean[1],far_minus_near_ms=y)
               for pid,means,values in zip(ids,adjusted,gradient)
               for cell,mean,y in zip(SUMMARY_LABELS[:4],means,values)]
    targets = np.concatenate((gradient,gradient@W.T),axis=-1)
    n = len(ids)
    avg = targets.mean(0)
    r = t.ppf(.975,n-1)*targets.std(0,ddof=1)/np.sqrt(n)
    group = [dict(contrast=label,mean_ms=a,low_ms=a-b,high_ms=a+b)
             for label,a,b in zip((*SUMMARY_LABELS[:4],*EFFECTS),avg,r)]
    return records,group


def recovery(values,cov,radius,distance):
    rng = np.random.default_rng(SEED)
    grid = ShapeGrid.logistic(distance)
    m = int(np.argmin(abs(grid.normalized_midpoint-.53)))
    w = int(np.argmin(abs(grid.relative_width-1/6)))
    shape = grid.shapes[m,w]
    noise = rng.normal(size=(REPS,*values.shape))
    p_noise = np.einsum("ncij,rncj->rnci",np.linalg.cholesky(cov),noise)
    n,d = len(values),len(distance)
    all_cov = np.cov(values.reshape(n,-1).T)
    g_noise = rng.multivariate_normal(np.zeros(4*d),all_cov,size=(REPS,n)).reshape(REPS,n,4,d)
    endpoints = (grid.midpoints <= distance[0]) | (grid.midpoints >= distance[-1])
    pfit = WeightedBasis(cov,grid.shapes.reshape(-1,d))
    pref = WeightedBasis(cov,grid.reference_shapes)

    def flags(loss,ref,rad):
        loss = loss.reshape(*rad.shape,len(grid.midpoints),len(grid.relative_width))
        allowed = np.isfinite(rad)
        support = (loss<=rad[...,None,None]).any(-1)
        loc = support.any(-1) & ~support[...,endpoints].any(-1) & ~(ref<=rad[...,None]).any(-1)
        return [z[allowed].mean() for z in (loc,loss[...,m,w]<=rad,ref[...,0]<=rad)]

    out = {}
    for amp in (0,160):
        p_stats,g_stats = [],[]
        placement = amp*shape
        for individual,group in zip(p_noise+placement,g_noise+placement):
            p_stats.append(flags(pfit.surface(individual)[0],pref.surface(individual)[0],radius))
            mean,vc = group_data(group)
            _,loss,_,ref = calc(mean,vc,distance)
            g_stats.append(flags(loss,ref,np.full(mean.shape[:-1],group_limit(n,d-1))))
        keys = ("localized_fraction","shape_coverage","flat_compatible_fraction")
        out[str(amp)] = {k:dict(zip(keys,np.mean(v,axis=0))) for k,v in (("people",p_stats),("group",g_stats))}
    return out


def run():
    ids,at,baseline,audit = load_data()
    primary = cohort_mask(ids,"primary40")
    pairs,exact = exact_results(at[primary],baseline[primary],ids[primary])
    selected,used,mapping = matching("interpolated")
    np.testing.assert_allclose(SOA[used]@mapping.T,SOA[selected]+OFFSET)
    values,cov,rad = prepare(at,baseline,selected,used,mapping)
    rows,predict = [],{}
    for name,locations in DISTANCES.items():
        x = locations[selected]
        tags = dict(axis=name,cohort="primary40")
        rows.extend(profile(values[primary],cov[primary],rad[primary],x,ids[primary],tags))
        all_usable = np.isfinite(rad[:,:4]).all(-1) & primary
        pred = predict_folds(values[all_usable,:4],cov[all_usable,:4],ShapeGrid.logistic(x),160.)
        predict[name] = {"individual":pred}
        for cohort in COHORTS:
            m = cohort_mask(ids,cohort)
            mean,vc = group_data(values[m])
            limit = np.full(mean.shape[:-1],group_limit(int(m.sum()),len(x)-1))
            rows.extend(profile(mean,vc,limit,x,["equal_participant_group"],dict(tags,cohort=cohort)))
            if cohort=="primary40":
                predict[name]["group"] = predict_folds(mean[:,:4],vc[:,:4],ShapeGrid.logistic(x),160.)
    sim = recovery(values[primary,:4],cov[primary,:4],rad[primary,:4],DISTANCES["registered"][selected])
    files = [OUT/"cue_time_exact_pairs.csv",OUT/"cue_time_interpolated_profiles.csv"]
    for path,table in zip(files,(pairs,rows)):
        write_csv(path,table)
    dependencies = [Path(__file__),Path(__file__).with_name("profile.py"),Path(__file__).with_name("profile_grid.py"),
                    OUT/"CUE_TIME_SPECIFICATION.md",*files]
    m = dict(input=audit,exact_group_contrasts_ms=exact,interpolated_AT_soas=SOA[selected].tolist(),
             baseline_soas=SOA[used].tolist(),operator=mapping.tolist(),predictions_ms=predict,
             seed=SEED,simulation_cohorts=REPS,recovery_by_span_ms=sim,
             sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in dependencies})
    (OUT/"cue_time_results.json").write_text(json.dumps(m,indent=2,allow_nan=False)+"\n",encoding="utf-8",newline="\n")
    print(f"Wrote {len(pairs)} exact-pair summaries and {len(rows)} interpolated midpoint profiles.")


if __name__ == "__main__":
    run()
