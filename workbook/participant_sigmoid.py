"""Exploratory individual sigmoid proxies; the original boundary gate is unchanged."""

from collections import Counter, defaultdict
from hashlib import sha256
import json

import numpy as np
from scipy import special, stats

from descriptive_sigmoid import (DISTANCES, LABELS, SOAS_NEAR_TO_FAR, ProfileGrid,
                                 fit_line, predict, predict_line, smooth)
from questionnaires import SCALES, association, finite, rank_correlation

SEED = 20261018
BOOTSTRAPS = 500
X = (DISTANCES-10)/90
METRICS = ("midpoint_cm", "normalized_steepness_per_cm", "midpoint_slope_ms_per_cm")
CELL_NAMES = ("control_exhale", "control_inhale", "viscereality_exhale", "viscereality_inhale")
SMOOTHERS = (("none", 0.), ("gaussian_constant", .15), ("gaussian_constant", .3), ("gaussian_linear", .3))


def linkage_audit(rows):
    """Detect reused trial records without inferring a participant's true identity."""
    grouped=defaultdict(list)
    for r in rows:grouped[r["participant_id"]].append(r)
    fields=("trial_index","trial_type","phase","soa_ms","noise_type","reaction_time_ms","outcome","response_given")
    matches=defaultdict(list)
    for pid,records in grouped.items():
        signature=sorted(tuple(str(r.get(k,"")) for k in fields) for r in records)
        matches[sha256(json.dumps(signature).encode()).hexdigest()].append(pid)
    duplicates=[]
    for ids in matches.values():
        if len(ids)<2:continue
        a=sorted(grouped[ids[0]],key=lambda r:int(r.get("trial_index",0)))
        relationships=[]
        for pid in ids[1:]:
            b=sorted(grouped[pid],key=lambda r:int(r.get("trial_index",0)))
            relationships.append("swapped" if all(x["condition"]!=y["condition"] for x,y in zip(a,b)) else "same or mixed")
        duplicates.append({"participant_ids":sorted(ids),"trial_count_per_record":len(a),"condition_label_relationship":relationships})
    return {"status":"unresolved recording-to-questionnaire linkage" if duplicates else "no identical behavioural records detected",
            "groups":duplicates,"matching_fields":list(fields),
            "interpretation":("Matching recordings with different questionnaire records cannot establish independent participants. Preserve source rows; resolve the original mapping. New RT–questionnaire results are provisional; exclusion sensitivities do not identify the correct mapping."
                              if duplicates else "No exact recording reuse found by this audit; this does not verify acquisition provenance.")}


def trial_tensor(rows):
    groups = defaultdict(list)
    for r in rows:
        if r["trial_type"] == "Audio-Tactile":
            groups[(r["participant_id"], r["condition"], r["phase"], float(r["soa_ms"]))].append(float(r["reaction_time_ms"]))
    all_ids = sorted({k[0] for k in groups})
    ids = [i for i in all_ids if all((i,c,p,s) in groups for c,p in LABELS for s in SOAS_NEAR_TO_FAR)]
    if not ids:
        return ids, np.empty((0,4,5,0)), all_ids
    size = max(len(groups[(i,c,p,s)]) for i in ids for c,p in LABELS for s in SOAS_NEAR_TO_FAR)
    tensor = np.full((len(ids),4,5,size), np.nan)
    for j,i in enumerate(ids):
        for k,(c,p) in enumerate(LABELS):
            for l,s in enumerate(SOAS_NEAR_TO_FAR):
                values = groups[(i,c,p,s)]; tensor[j,k,l,:len(values)] = values
    return ids, tensor, sorted(set(all_ids)-set(ids))


def summarize(tensor, aggregation):
    n = np.sum(np.isfinite(tensor), axis=-1)
    if np.any(n == 0):
        raise ValueError("Every fitted cell requires observed trials.")
    if aggregation == "mean":
        y = np.nanmean(tensor, axis=-1)
    elif aggregation == "median":
        y = np.nanmedian(tensor, axis=-1)
    elif aggregation == "trim20":
        values = np.sort(tensor, axis=-1); k = np.floor(.2*n).astype(int)
        positions = np.arange(tensor.shape[-1])
        keep = (positions >= k[...,None]) & (positions < (n-k)[...,None])
        y = np.sum(np.where(keep, values, 0.), axis=-1)/(n-2*k)
    else:
        raise ValueError("Unknown extraction method.")
    centered = tensor-np.nanmean(tensor,axis=-1)[...,None]
    variance = np.nansum(centered**2,axis=-1)/np.maximum(n-1,1)
    # Working precision only; bootstrap uncertainty does not rely on this being a median SE.
    fallback = np.maximum(np.median(variance,axis=(1,2)),1.)[:,None,None]
    return y, np.where(n>1,variance,fallback)/n


def resample_trials(tensor, rng):
    n = np.sum(np.isfinite(tensor),axis=-1)
    indices = (rng.random(tensor.shape)*n[...,None]).astype(int)
    sampled = np.take_along_axis(tensor,indices,axis=-1)
    sampled[np.arange(tensor.shape[-1]) >= n[...,None]] = np.nan
    return sampled


class PenalizedGrid:
    """Exact signed offset/amplitude profile on a common finite shape grid."""

    def __init__(self, visible=True, fine=False):
        reference = ProfileGrid(fine=fine, visible=visible)
        shapes = reference.shapes[reference.allowed]
        neutral = ((shapes[:,0]-.5)/.25)**2+(np.log(shapes[:,1]/.15)/np.log(2))**2
        self.shapes = shapes[np.lexsort((shapes[:,1],shapes[:,0],neutral))]
        self.cache = {}

    def basis(self,x):
        key=tuple(x)
        if key not in self.cache:
            q=special.expit((np.asarray(x)[None,:]-self.shapes[:,0,None])/self.shapes[:,1,None])
            qc=q-q.mean(1)[:,None]
            self.cache[key]=(q,qc,np.sum(qc**2,axis=1))
        return self.cache[key]

    def penalty(self,centers):
        return ((self.shapes[None,:,0]-centers[:,None,0])/.25)**2+(np.log(self.shapes[None,:,1]/centers[:,None,1])/np.log(2))**2

    def fit(self,x,y,variance=None,centers=None,strength=0.):
        q,qc,ss=self.basis(x)
        centered=y-y.mean(1)[:,None];numerator=centered@qc.T
        a=np.clip(numerator/np.maximum(ss,1e-30),-500.,500.)
        loss=np.sum(centered**2,axis=1)[:,None]-2*a*numerator+a*a*ss
        objective=loss/np.maximum(variance if variance is not None else np.ones(len(y)),1.)[:,None]
        if strength:
            objective=objective+strength*self.penalty(centers)
        # Deterministic neutral-shape tie breaking for flat/numerically identical losses.
        index=np.argmin(np.round(objective,10),axis=1);r=np.arange(len(y))
        amplitude=a[r,index]
        return np.column_stack([y.mean(1)-amplitude*q.mean(1)[index],amplitude,self.shapes[index]])


def method_catalogue():
    methods=[]
    for family in ("visible","broad","linear"):
        for aggregation in ("mean","median","trim20"):
            for smoother,bandwidth in SMOOTHERS:
                for penalty in ((0.,) if family=="linear" else (0.,1.,4.)):
                    methods.append(dict(family=family,aggregation=aggregation,smoother=smoother,
                        bandwidth=bandwidth,penalty=penalty,
                        method=f"{family}/{aggregation}/{smoother}/{bandwidth:g}/penalty{penalty:g}"))
    return methods


def estimate(cube,variances,method,grid,x=X,training=None,identities=None):
    n=len(cube)
    y=smooth(x,cube.reshape(-1,len(x)),method["smoother"],method["bandwidth"]).reshape(n,4,len(x))
    if training is not None:
        source=smooth(x,training.reshape(-1,len(x)),method["smoother"],method["bandwidth"]).reshape(len(training),4,len(x))
        pooled=np.broadcast_to(source.mean(0),(n,4,len(x)))
    else:
        identities=np.arange(n) if identities is None else np.asarray(identities)
        pooled=np.array([y[identities!=i].mean(0) if np.any(identities!=i) else np.zeros_like(y[0]) for i in identities])
    centers=grid.fit(x,pooled.reshape(-1,len(x)))[:,2:]
    pars=grid.fit(x,y.reshape(-1,len(x)),np.mean(variances,axis=-1).ravel(),centers,method["penalty"])
    return pars.reshape(n,4,4),centers.reshape(n,4,2),y


def shared_plateaus(y,variances,method,grid,centers,initial,x=X):
    """Alternating exact grid/linear updates, with three signed starts per person."""
    n=len(y);q,_,_=grid.basis(x);variance=np.maximum(variances.mean(-1),1.)
    weight=np.repeat(1/variance,len(x),axis=1)
    target=y.reshape(n,-1);penalty=method["penalty"]*grid.penalty(centers.reshape(-1,2))
    best=np.full(n,np.inf);result=initial.copy();converged=np.zeros(n,dtype=bool)
    for start in (None,50.,-50.):
        a=initial[:,:,1].mean(1) if start is None else np.full(n,start)
        b=y.mean((1,2))-.5*a;previous=None;settled=np.zeros(n,dtype=bool)
        for iteration in range(60):
            residual=(y-b[:,None,None]).reshape(-1,len(x));aa=np.repeat(a,4)
            loss=(np.sum(residual**2,axis=1)[:,None]-2*aa[:,None]*(residual@q.T)+aa[:,None]**2*np.sum(q*q,axis=1))/variance.ravel()[:,None]+penalty
            index=np.argmin(np.round(loss,10),axis=1).reshape(n,4)
            design=q[index].reshape(n,-1)
            qm=np.sum(weight*design,axis=1)/weight.sum(1);ym=np.sum(weight*target,axis=1)/weight.sum(1)
            z=design-qm[:,None]
            new_a=np.clip(np.sum(weight*z*(target-ym[:,None]),axis=1)/np.maximum(np.sum(weight*z*z,axis=1),1e-30),-500.,500.)
            new_b=ym-new_a*qm
            if previous is not None:
                settled=np.all(index==previous,axis=1)&(np.abs(new_a-a)<1e-8)
            a,b,previous=new_a,new_b,index
            if np.all(settled):break
        pars=np.concatenate([np.broadcast_to(b[:,None,None],(n,4,1)),np.broadcast_to(a[:,None,None],(n,4,1)),grid.shapes[index]],axis=-1)
        objective=np.sum(weight*(target-predict(pars.reshape(-1,4),x).reshape(n,-1))**2,axis=1)+penalty[np.arange(n*4),index.ravel()].reshape(n,4).sum(1)
        better=objective<best-1e-10;result[better]=pars[better];best[better]=objective[better];converged[better]=settled[better]
    return result,converged


def candidate_scores(cubes,variances,grids,identities=None):
    records=[]
    for method in method_catalogue():
        errors=[]
        for j in range(5):
            keep=np.arange(5)!=j;cube=cubes[method["aggregation"]][:,:,keep]
            if method["family"]=="linear":
                y=smooth(X[keep],cube.reshape(-1,4),method["smoother"],method["bandwidth"])
                pars=fit_line(X[keep],y)
                pred=(predict_line(pars,X[[j]])[:,0]-predict_line(pars,X[keep]).mean(1)).reshape(-1,4)
            else:
                pars,_,_=estimate(cube,variances[:,:,keep],method,grids[method["family"]],X[keep],identities=identities)
                pred=(predict(pars.reshape(-1,4),X[[j]])[:,0]-predict(pars.reshape(-1,4),X[keep]).mean(1)).reshape(-1,4)
            target=cubes["mean"][:,:,j]-cubes["mean"][:,:,keep].mean(2)
            errors.append((target-pred)**2)
        mse=np.mean(errors,axis=(0,2))
        records.append(method|{"tuning_rmse_ms":float(np.sqrt(mse.mean())),"per_participant_mse":mse.tolist()})
    return sorted(records,key=lambda r:(r["tuning_rmse_ms"],r["method"]))


def nested_prediction(cubes,variances,ids,progress=None,identities=None):
    n=len(ids);identities=np.arange(n) if identities is None else np.asarray(identities)
    unique=np.unique(identities)
    folds=[np.flatnonzero(np.isin(identities,fold)) for fold in np.array_split(np.random.default_rng(SEED).permutation(unique),min(6,len(unique)))]
    families=("visible","broad","linear","constant","shared_plateaus")
    errors={f:np.zeros((n,4,5)) for f in families};records=[]
    grids={f:PenalizedGrid(f=="visible") for f in ("visible","broad")}
    for k,test in enumerate(folds):
        if progress:progress(f"Individual sigmoid prediction: outer participant fold {k+1}/{len(folds)}")
        train=np.setdiff1d(np.arange(n),test);train_cubes={key:v[train] for key,v in cubes.items()}
        scores=candidate_scores(train_cubes,variances[train],grids,identities[train])
        choices={f:next(r for r in scores if r["family"]==f) for f in ("visible","broad","linear")}
        records.append({"fold":k+1,"test_participant_ids":[ids[i] for i in test],"selected_methods":{f:r["method"] for f,r in choices.items()},
                        "inner_scores":[{k:r[k] for k in ("method","tuning_rmse_ms")} for r in scores]})
        for j in range(5):
            keep=np.arange(5)!=j;target=cubes["mean"][test,:,j]-cubes["mean"][test][:,:,keep].mean(2)
            errors["constant"][test,:,j]=target**2
            for family,method in choices.items():
                cube=cubes[method["aggregation"]][test][:,:,keep]
                if family=="linear":
                    y=smooth(X[keep],cube.reshape(-1,4),method["smoother"],method["bandwidth"])
                    pars=fit_line(X[keep],y)
                    prediction=(predict_line(pars,X[[j]])[:,0]-predict_line(pars,X[keep]).mean(1)).reshape(-1,4)
                else:
                    pars,centers,y=estimate(cube,variances[test][:,:,keep],method,grids[family],X[keep],training=cubes[method["aggregation"]][train][:,:,keep])
                    prediction=(predict(pars.reshape(-1,4),X[[j]])[:,0]-predict(pars.reshape(-1,4),X[keep]).mean(1)).reshape(-1,4)
                    if family=="visible":
                        joint,_=shared_plateaus(y,variances[test][:,:,keep],method,grids[family],centers,pars,X[keep])
                        pred=(predict(joint.reshape(-1,4),X[[j]])[:,0]-predict(joint.reshape(-1,4),X[keep]).mean(1)).reshape(-1,4)
                        errors["shared_plateaus"][test,:,j]=(target-pred)**2
                errors[family][test,:,j]=(target-prediction)**2
    return {"outer_folds":records,"scores":[{"family":f,"outer_rmse_ms":float(np.sqrt(v.mean())),"per_cell_rmse_ms":np.sqrt(v.mean(0)).tolist(),
        "per_participant_mse":v.mean((1,2)).tolist()} for f,v in errors.items()]}


def metrics(parameters):
    return np.stack([10+90*parameters[...,2],1/(360*parameters[...,3]),parameters[...,1]/(360*parameters[...,3])],axis=-1)


def catalogue():
    out=[]
    for summary in (*CELL_NAMES,"condition_delta"):
        for metric in METRICS:
            for scale in SCALES:
                out.append(dict(x="maia2_"+scale,y=metric+"_"+summary,metric=metric,summary=summary,
                                scope="main" if summary=="condition_delta" else "supplementary"))
    for field in ("spfrref_delta","spfrref_change_direction"):
        for metric in METRICS:
            out.append(dict(x=field,y=metric+"_condition_delta",metric=metric,summary="condition_delta",
                            scope="main" if field=="spfrref_delta" else "direction sensitivity"))
    return out


def person_records(parameters,ids,questionnaires):
    source={r["participant_id"]:r for r in questionnaires["scores"]};values=metrics(parameters);records=[]
    for i,pid in enumerate(ids):
        r=dict(source[pid])
        for k,name in enumerate(METRICS):
            for j,cell in enumerate(CELL_NAMES):r[name+"_"+cell]=float(values[i,j,k])
            r[name+"_condition_delta"]=float(values[i,2:,k].mean()-values[i,:2,k].mean())
        records.append(r)
    return records


def correlations(records):
    out=[]
    for comparison in catalogue():
        pairs=np.array([(r[comparison["x"]],r[comparison["y"]]) for r in records],dtype=float)
        pairs=pairs[np.isfinite(pairs).all(1)]
        out.append(finite(rank_correlation(*pairs.T)) if len(pairs)>2 else None)
    return out


def run(rows,questionnaires,progress=None,bootstrap_draws=BOOTSTRAPS,simulation_draws=30,source_trials=None):
    ids,tensor,missing=trial_tensor(rows)
    if len(ids)<6:
        return {"status":"not_estimable","reason":"At least six people with all 20 cells are required.","incomplete_participants":missing}
    audit=linkage_audit(rows if source_trials is None else source_trials)
    identities=np.arange(len(ids))
    for group in audit["groups"]:
        members=[ids.index(pid) for pid in group["participant_ids"] if pid in ids]
        identities[members]=min(members) if members else -1
    cubes={a:summarize(tensor,a)[0] for a in ("mean","median","trim20")};variances=summarize(tensor,"mean")[1]
    grids={f:PenalizedGrid(f=="visible") for f in ("visible","broad")}
    if progress:progress("Individual sigmoid proxies: 84 uniform extraction/smoothing/shape methods")
    candidates=candidate_scores(cubes,variances,grids,identities)
    chosen=next(r for r in candidates if r["family"]=="visible")
    grid=grids["visible"];cube=cubes[chosen["aggregation"]]
    pars,centers,smoothed=estimate(cube,variances,chosen,grid,identities=identities)
    nested=nested_prediction(cubes,variances,ids,progress,identities)
    unregularized,_,_=estimate(cube,variances,chosen|{"penalty":0.},grid,identities=identities)
    fine,_,_=estimate(cube,variances,chosen,PenalizedGrid(fine=True),identities=identities)
    shared,shared_converged=shared_plateaus(smoothed,variances,chosen,grid,centers,pars)
    rng=np.random.default_rng(SEED+1);draws=[];association_draws=[];shared_draws=[];shared_association_draws=[]
    for b in range(bootstrap_draws):
        if progress and b%100==0:progress(f"Individual parameters and hierarchical associations: bootstrap {b}/{bootstrap_draws}")
        sample=resample_trials(tensor,rng);sy,sv=summarize(sample,chosen["aggregation"])
        bp,bc,by=estimate(sy,sv,chosen,grid,identities=identities);draws.append(bp)
        joint,_=shared_plateaus(by,sv,chosen,grid,bc,bp);shared_draws.append(joint)
        unique=np.unique(identities)
        sampled_groups=rng.choice(unique,len(unique),replace=True)
        indices=np.concatenate([np.flatnonzero(identities==g) for g in sampled_groups]);sample=resample_trials(tensor[indices],rng)
        sy,sv=summarize(sample,chosen["aggregation"]);bp,bc,by=estimate(sy,sv,chosen,grid,identities=identities[indices])
        association_draws.append(correlations(person_records(bp,[ids[i] for i in indices],questionnaires)))
        joint,_=shared_plateaus(by,sv,chosen,grid,bc,bp)
        shared_association_draws.append(correlations(person_records(joint,[ids[i] for i in indices],questionnaires)))
    draws=np.array(draws);association_draws=np.array(association_draws,dtype=float)
    values=metrics(pars);boot_values=metrics(draws);parameters=[]
    for i,pid in enumerate(ids):
        for j,(condition,phase) in enumerate(LABELS):
            base,amplitude,m,w=pars[i,j];low,high=np.percentile(draws[:,i,j,1],[2.5,97.5])
            row={"participant_id":pid,"condition":condition,"phase":phase,"status":"exploratory model-dependent proxy",
                "base_ms":float(base),"signed_amplitude_ms":float(amplitude),"lower_plateau_ms":float(min(base,base+amplitude)),
                "upper_plateau_ms":float(max(base,base+amplitude)),"width_cm":float(90*w),
                "amplitude_ci_low":float(low),"amplitude_ci_high":float(high),"flat":bool(abs(amplitude)<1e-6),
                "normalization_stable":bool(low>0 or high<0),"expected_direction":bool(amplitude>0),
                "bootstrap_expected_direction_fraction":float(np.mean(draws[:,i,j,1]>0)),
                "raw_mean_rmse_ms":float(np.sqrt(np.mean((predict(pars[i,j][None,:],X)[0]-cubes['mean'][i,j])**2))),
                "prior_midpoint_cm":float(10+90*centers[i,j,0]),"prior_width_cm":float(90*centers[i,j,1]),
                "unregularized_midpoint_cm":float(10+90*unregularized[i,j,2]),"fine_grid_midpoint_cm":float(10+90*fine[i,j,2]),
                "shared_plateau_midpoint_cm":float(10+90*shared[i,j,2]),"width_at_floor":bool(w<=.05+1e-8)}
            for k,metric in enumerate(METRICS):
                row[metric]=float(values[i,j,k]);interval=np.percentile(boot_values[:,i,j,k],[2.5,97.5])
                row[metric+"_ci_low"],row[metric+"_ci_high"]=map(float,interval)
            parameters.append(row)
    shared_draws=np.array(shared_draws);shared_values=metrics(shared);shared_boot=metrics(shared_draws);shared_parameters=[]
    for i,pid in enumerate(ids):
        for j,(condition,phase) in enumerate(LABELS):
            base,amplitude,m,w=shared[i,j];lo,hi=np.percentile(shared_draws[:,i,j,1],[2.5,97.5])
            row=dict(participant_id=pid,condition=condition,phase=phase,status="shared-plateau model-dependent proxy",
                base_ms=float(base),signed_amplitude_ms=float(amplitude),lower_plateau_ms=float(min(base,base+amplitude)),
                upper_plateau_ms=float(max(base,base+amplitude)),width_cm=float(90*w),amplitude_ci_low=float(lo),amplitude_ci_high=float(hi),
                flat=bool(abs(amplitude)<1e-6),normalization_stable=bool(lo>0 or hi<0),expected_direction=bool(amplitude>0),
                converged=bool(shared_converged[i]),bootstrap_expected_direction_fraction=float(np.mean(shared_draws[:,i,j,1]>0)),
                raw_mean_rmse_ms=float(np.sqrt(np.mean((predict(shared[i,j][None,:],X)[0]-cubes['mean'][i,j])**2))))
            for k,metric in enumerate(METRICS):
                row[metric]=float(shared_values[i,j,k]);interval=np.percentile(shared_boot[:,i,j,k],[2.5,97.5])
                row[metric+"_ci_low"],row[metric+"_ci_high"]=map(float,interval)
            shared_parameters.append(row)
    scored=person_records(pars,ids,questionnaires);associations=[];perm_rng=np.random.default_rng(SEED+2)
    alternatives={name:correlations(person_records(p,ids,questionnaires)) for name,p in
                  (("unregularized",unregularized),("fine_grid",fine),("shared_plateaus",shared))}
    for k,comparison in enumerate(catalogue()):
        r=association(scored,comparison["x"],comparison["y"],perm_rng,19999,0)|comparison
        valid=association_draws[:,k][np.isfinite(association_draws[:,k])]
        lo,hi=np.percentile(valid,[2.5,97.5]) if len(valid) else (None,None)
        r.update(ci_low=finite(lo) if lo is not None else None,ci_high=finite(hi) if hi is not None else None,
                 bootstrap_valid=len(valid),hierarchical_bootstrap_valid=len(valid))
        r.update({name+"_rho":v[k] for name,v in alternatives.items()});associations.append(r)
    shared_associations=[];shared_scored=person_records(shared,ids,questionnaires);shared_rng=np.random.default_rng(SEED+3)
    shared_association_draws=np.array(shared_association_draws,dtype=float)
    for k,comparison in enumerate(catalogue()):
        r=association(shared_scored,comparison["x"],comparison["y"],shared_rng,19999,0)|comparison
        valid=shared_association_draws[:,k][np.isfinite(shared_association_draws[:,k])]
        lo,hi=np.percentile(valid,[2.5,97.5]) if len(valid) else (None,None)
        r.update(ci_low=finite(lo) if lo is not None else None,ci_high=finite(hi) if hi is not None else None,
                 bootstrap_valid=len(valid),hierarchical_bootstrap_valid=len(valid))
        shared_associations.append(r)
    if progress:progress("Individual sigmoid split-half stability and known-signal recovery")
    reliability=[]
    for repetition in range(10):
        halves=[np.full_like(tensor,np.nan),np.full_like(tensor,np.nan)]
        for index in np.ndindex(tensor.shape[:3]):
            a=tensor[index];a=a[np.isfinite(a)];a=rng.permutation(a)
            for side in (0,1):halves[side][index][:len(a[side::2])]=a[side::2]
        if any(np.any(np.sum(np.isfinite(h),axis=-1)==0) for h in halves):continue
        fits=[];joint_fits=[]
        for h in halves:
            sy,sv=summarize(h,chosen["aggregation"]);p,pc,py=estimate(sy,sv,chosen,grid,identities=identities);fits.append(metrics(p))
            joint,_=shared_plateaus(py,sv,chosen,grid,pc,p);joint_fits.append(metrics(joint))
        for model,halffits in (("individual_plateaus",fits),("shared_plateaus",joint_fits)):
            for j,(c,p) in enumerate(LABELS):
                for k,m in enumerate(METRICS):reliability.append(dict(model=model,repetition=repetition+1,condition=c,phase=p,parameter=m,rho=finite(rank_correlation(halffits[0][:,j,k],halffits[1][:,j,k]))))
    residuals=tensor-cubes["mean"][...,None];simulation=[]
    eligible=grid.shapes[(grid.shapes[:,0]>=.3)&(grid.shapes[:,0]<=.6)&(grid.shapes[:,1]>=.08)&(grid.shapes[:,1]<=.16)]
    for scenario in ("flat","linear","sigmoid","sigmoid_shared_plateaus"):
        for b in range(simulation_draws):
            truth=np.zeros((len(ids),4,4));truth[:,:,0]=cubes["mean"].mean(2);truth[:,:,1]=80.
            if scenario=="sigmoid_shared_plateaus":truth[:,:,0]=cubes["mean"].mean((1,2))[:,None]
            truth[:,:,2:]=eligible[rng.integers(0,len(eligible),(len(ids),4))]
            signal=predict(truth.reshape(-1,4),X).reshape(len(ids),4,5)
            if scenario=="flat":signal=np.broadcast_to(truth[:,:,0,None],signal.shape)
            elif scenario=="linear":signal=truth[:,:,0,None]+80*X
            sample=resample_trials(residuals,rng)+signal[...,None]
            sy,sv=summarize(sample,chosen["aggregation"]);p,pc,py=estimate(sy,sv,chosen,grid,identities=identities)
            joint,_=shared_plateaus(py,sv,chosen,grid,pc,p)
            for model,fit in (("individual_plateaus",p),("shared_plateaus",joint)):
                row={"model":model,"scenario":scenario,"replicate":b+1,"median_abs_amplitude_ms":float(np.median(abs(fit[:,:,1]))),
                     "positive_amplitude_fraction":float(np.mean(fit[:,:,1]>0)),"midpoint_sd_cm":float(np.std(10+90*fit[:,:,2],ddof=1))}
                if scenario.startswith("sigmoid"):
                    for k,m in enumerate(METRICS):
                        fitted,known=metrics(fit)[...,k].ravel(),metrics(truth)[...,k].ravel()
                        row[m+"_recovery_rho"]=finite(rank_correlation(fitted,known))
                        row[m+"_rmse"]=float(np.sqrt(np.mean((fitted-known)**2)))
                simulation.append(row)
    linkage_sensitivities=[]
    flagged=sorted({pid for g in audit["groups"] for pid in g["participant_ids"] if pid in ids})
    exclusion_sets=([flagged]+[[pid] for pid in flagged]) if flagged else []
    for drop in exclusion_sets:
        if progress:progress("Recording-linkage exclusion sensitivity: "+", ".join(drop))
        keep=np.array([i for i,pid in enumerate(ids) if pid not in drop]);subset={k:v[keep] for k,v in cubes.items()}
        scores=candidate_scores(subset,variances[keep],grids,identities[keep]);method=next(r for r in scores if r["family"]=="visible")
        sp,sc,sy=estimate(subset[method["aggregation"]],variances[keep],method,grid,identities=identities[keep])
        joint,_=shared_plateaus(sy,variances[keep],method,grid,sc,sp)
        records=person_records(sp,[ids[i] for i in keep],questionnaires);tests=[]
        for c in catalogue():tests.append(association(records,c["x"],c["y"],perm_rng,19999,0)|c)
        joint_records=person_records(joint,[ids[i] for i in keep],questionnaires)
        joint_tests=[association(joint_records,c["x"],c["y"],shared_rng,19999,0)|c for c in catalogue()]
        linkage_sensitivities.append({"excluded_ids":drop,"participants":len(keep),"selected_method":method["method"],"associations":tests,"shared_associations":joint_tests,
                                     "participant_scores":records,"shared_participant_scores":joint_records})
    return {"status":"computed","participants":len(ids),"curve_count":len(parameters),"incomplete_participants":missing,
        "linkage_audit":audit,"linkage_sensitivities":linkage_sensitivities,
        "selected_method":chosen,"candidate_count":len(candidates),"candidates":candidates,"parameters":parameters,
        "shared_parameters":shared_parameters,"shared_associations":shared_associations,"shared_participant_scores":shared_scored,
        "prediction":nested,"participant_scores":scored,"associations":associations,"reliability":reliability,"recovery":simulation,
        "plot_data":{"participant_ids":ids,"raw_means":cubes["mean"].tolist(),"raw_se":np.sqrt(variances).tolist(),
                     "extracted":cube.tolist(),"parameters":pars.tolist(),"shared_parameters":shared.tolist()},
        "shared_plateau_converged":int(shared_converged.sum()),"bootstrap_draws":bootstrap_draws,"seed":SEED,
        "interpretation":"All numbers are exploratory fitted proxies. Visible geometry is imposed, reverse responses are retained, and the original failed participant boundary gate is unchanged. Numeric midpoint/width values in flat or weak profiles reflect constraints/regularization, not identified physiological boundaries.",
        "normalization":"Subtract the fitted lower plateau and divide by absolute fitted amplitude. This is an affine display transformation, not new evidence. Do not clip observations; skip zero amplitude and flag intervals containing zero. Joint sensitivity shares plateaus across each person's four curves.",
        "uncertainty":"500 fixed-record within-cell trial resamples for parameters; 500 person/linked-record-group plus trial resamples with refitted pools for association intervals. Conditional on selected method, original cleaning and constraints; no correction for method selection or within-cell serial dependence. 19,999 pairing permutations; all 126 p values per specification unadjusted. Unresolved linked records make full-release inference provisional; exclusion sensitivities report point estimates/p values without bootstrap intervals.",
        "selection_scope":"84 methods: 36 visible, 36 broad and 12 lines, plus a constant. Six outer participant/linked-record-group folds repeat tuning on training people, using omitted-position prediction; test-person fits use four positions and pooling from training people only. Linked copies are excluded together from each person's pool. Scores condition on earlier cleaning. Shared-plateau sensitivity uses the selected visible preprocessing and penalty."}
