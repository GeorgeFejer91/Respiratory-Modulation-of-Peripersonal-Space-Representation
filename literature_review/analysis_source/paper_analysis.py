"""Full, browser-executable Study 5 behavioral analysis. See ANALYSIS_PLAN.md."""

import csv
import io
import json
import math
import platform
import sys
import zipfile
from collections import Counter, defaultdict
from hashlib import sha256

import numpy as np
import scipy
import matplotlib
from scipy import optimize, special, stats

from inference import (cluster_regression, holm, mixed_comparison, paired,
                       repeated_anova, sign_flip)
from descriptive_sigmoid import run as descriptive_sigmoid_analysis
from questionnaires import run as questionnaire_analysis
from participant_sigmoid import run as participant_sigmoid_analysis


SOAS = (300.,800.,1500.,2200.,2700.)
CONDITIONS = ("Control","Viscereality")
PHASES = ("Exhale","Inhale")
AXES = {"registered": dict(zip(SOAS,(100.,73.,50.,27.,10.))),
        "trajectory": dict(zip(SOAS,(100.,83.3333333333,60.,36.6666666667,20.)))}


def numeric(row,key):
    return float(row[key]) if row.get(key,"") not in ("","N/A","nan") else math.nan


def grouped_means(rows, keys, field="reaction_time_ms"):
    groups = defaultdict(list)
    for row in rows:
        value = numeric(row,field)
        if math.isfinite(value):
            groups[tuple(row[k] if k!="soa_ms" else float(row[k]) for k in keys)].append(value)
    return {key:float(np.mean(values)) for key,values in groups.items()}


def clean(people,trials,cutoff=None,exclude_partial=False):
    quality = []
    excluded = set()
    partial = {p["participant_id"] for p in people if int(p["analysis_trials"])<int(p["planned_trials"])}
    for person in people:
        pid = person["participant_id"]
        rows = [r for r in trials if r["participant_id"]==pid]
        catches = [r for r in rows if r["trial_type"]=="Catch"]
        false = sum(r["outcome"]=="false_alarm" for r in catches)
        rate = false/len(catches) if catches else None
        reject = rate is not None and rate>.30
        if reject or (exclude_partial and pid in partial):
            excluded.add(pid)
        record = {"participant_id":pid,"observed":len(rows),"planned":int(person["planned_trials"]),
            "catch_trials":len(catches),"false_alarms":false,"false_alarm_rate":rate,
            "excluded_catch":reject,"partial_session":pid in partial}
        for kind,label in (("Audio-Tactile","at"),("Baseline","baseline")):
            selected = [r for r in rows if r["trial_type"]==kind]
            hits = sum(r["outcome"]=="hit" for r in selected)
            record[label+"_hit_rate"] = hits/len(selected) if selected else None
            record[label+"_low_hit_flag"] = bool(selected and hits/len(selected)<.70)
        quality.append(record)
    eligible = [r for r in trials if r["participant_id"] not in excluded
                and r["trial_type"] in ("Audio-Tactile","Baseline")
                and r["outcome"]=="hit" and r["response_given"]=="True"
                and math.isfinite(numeric(r,"reaction_time_ms"))]
    bounds = {}
    for pid in {r["participant_id"] for r in eligible}:
        values = np.array([numeric(r,"reaction_time_ms") for r in eligible if r["participant_id"]==pid])
        mean,sd = float(values.mean()),float(values.std(ddof=1))
        bounds[pid] = (mean-2.5*sd,mean+2.5*sd)
    trimmed = [r for r in eligible if bounds[r["participant_id"]][0]<=numeric(r,"reaction_time_ms")<=bounds[r["participant_id"]][1]]
    retained = [r for r in trimmed if cutoff is None or numeric(r,"reaction_time_ms")>=cutoff]
    counts = {"participants_input":len(people),"trial_rows_input":len(trials),
        "planned_trials":sum(int(p["planned_trials"]) for p in people),
        "participants_excluded_catch":sum(q["excluded_catch"] for q in quality),
        "partial_sessions":len(partial),"recorded_hits_before_trim":len(eligible),
        "removed_2_5_sd":len(eligible)-len(trimmed),"removed_cutoff":len(trimmed)-len(retained),
        "retained_at":sum(r["trial_type"]=="Audio-Tactile" for r in retained),
        "retained_baseline":sum(r["trial_type"]=="Baseline" for r in retained),
        "missing_hit_rt":sum(r["outcome"]=="hit" and r["trial_type"] in ("Audio-Tactile","Baseline") and not math.isfinite(numeric(r,"reaction_time_ms")) for r in trials),
        "missing_at_hit_rt":sum(r["outcome"]=="hit" and r["trial_type"]=="Audio-Tactile" and not math.isfinite(numeric(r,"reaction_time_ms")) for r in trials)}
    return retained,quality,counts


def design(rows,control=False,categorical=False,scale=None):
    soa = np.array([numeric(r,"soa_ms") for r in rows])
    mean,sd = scale or (float(soa.mean()),float(soa.std(ddof=1)))
    if sd<=0 or any(s not in SOAS for s in soa):
        raise ValueError("Models require the documented nonzero five-SOA design.")
    z = (soa-mean)/sd
    c = np.array([.5 if r["condition"]=="Viscereality" else -.5 for r in rows])
    p = np.array([.5 if r["phase"]=="Inhale" else -.5 for r in rows])
    basis = [(soa==s).astype(float) for s in SOAS[1:]] if categorical else [z]
    labels = [f"SOA[{int(s)}]" for s in SOAS[1:]] if categorical else ["SOA"]
    if control:
        vectors = [np.ones(len(rows)),p,*basis,*[p*b for b in basis]]
        names = ["Intercept","Phase",*labels,*["Phase × "+label for label in labels]]
    else:
        vectors = [np.ones(len(rows)),c,p,*basis,c*p,*[c*b for b in basis],*[p*b for b in basis],*[c*p*b for b in basis]]
        names = ["Intercept","Condition","Phase",*labels,"Condition × Phase",
                 *["Condition × "+s for s in labels],*["Phase × "+s for s in labels],
                 *["Condition × Phase × "+s for s in labels]]
    return np.column_stack(vectors),names,z,(mean,sd)


def interaction(rows,*,control=False,categorical=False,random_slope=False,label="primary"):
    at = [r for r in rows if r["trial_type"]=="Audio-Tactile" and (not control or r["condition"]=="Control")]
    x,names,z,scale = design(at,control,categorical)
    y = np.array([numeric(r,"reaction_time_ms") for r in at])
    groups = np.array([r["participant_id"] for r in at])
    result = mixed_comparison(x,y,groups,names,list(range(len(names)-(4 if categorical else 1),len(names))),
        random_slope=z if random_slope else None,name=label)
    result["soa_mean_ms"],result["soa_sd_ms"] = scale
    result["classification"] = "registered question" if label in ("primary numeric interaction","Control-only numeric interaction") else "sensitivity"
    return result


def safe_call(function,fallback_name,*args,**kwargs):
    try:
        return function(*args,**kwargs)
    except (ValueError,ArithmeticError,np.linalg.LinAlgError) as error:
        return {"name":fallback_name,"status":"not_estimable","reason":str(error)}


def cell_cube(rows,baseline_correct=False):
    at = grouped_means([r for r in rows if r["trial_type"]=="Audio-Tactile"],("participant_id","condition","phase","soa_ms"))
    baseline = grouped_means([r for r in rows if r["trial_type"]=="Baseline"],("participant_id","condition","phase","soa_ms"))
    ids,arrays = [],[]
    for pid in sorted({r["participant_id"] for r in rows}):
        keys = [(pid,c,p,s) for c in CONDITIONS for p in PHASES for s in SOAS]
        if all(k in at and (not baseline_correct or k in baseline) for k in keys):
            ids.append(pid)
            arrays.append(np.array([at[k]-(baseline[k] if baseline_correct else 0) for k in keys]).reshape(2,2,5))
    return ids,np.array(arrays)


def slope_contrasts(rows,scale,baseline_correct=False):
    ids,cube = cell_cube(rows,baseline_correct)
    if len(ids)<3:
        return {"status":"not_estimable","reason":"Too few complete participant cell sets."},{}
    z = (np.array(SOAS)-scale[0])/scale[1]
    slope = np.sum((z-z.mean())*cube,axis=3)/np.sum((z-z.mean())**2)
    values = slope[:,1,1]-slope[:,1,0]-slope[:,0,1]+slope[:,0,0]
    result = paired(values,"equal-participant SOA slope interaction")
    result["sign_flip"] = sign_flip(values)
    result["classification"] = "sensitivity"
    return result,dict(zip(ids,values.tolist()))


def supplementary(rows,people):
    at = [r for r in rows if r["trial_type"]=="Audio-Tactile"]
    base = [r for r in rows if r["trial_type"]=="Baseline"]
    ac = grouped_means(at,("participant_id","condition","phase","soa_ms"))
    bc = grouped_means(base,("participant_id","condition","phase","soa_ms"))
    bcp = grouped_means(base,("participant_id","condition","phase"))
    noise = grouped_means(at,("participant_id","noise_type"))
    values = defaultdict(list)
    for person in people:
        pid=person["participant_id"]
        keys=[(pid,c,p,s) for c in CONDITIONS for p in PHASES for s in SOAS]
        cp=[(pid,c,p) for c in CONDITIONS for p in PHASES]
        if all(k in bcp for k in cp):
            b=np.array([bcp[k] for k in cp]).reshape(2,2)
            values["Baseline Condition (Viscereality − Control)"].append(float(b[1].mean()-b[0].mean()))
            values["Baseline Phase (Inhale − Exhale)"].append(float(b[:,1].mean()-b[:,0].mean()))
            values["Baseline Condition × Phase"].append(float(b[1,1]-b[1,0]-b[0,1]+b[0,0]))
        if all(k in ac and k in bc for k in keys) and all(k in bcp for k in cp):
            a=np.array([ac[k] for k in keys]).reshape(2,2,5)
            b=np.array([bc[k] for k in keys]).reshape(2,2,5)
            b_mean=np.array([bcp[k] for k in cp]).reshape(2,2)
            values["Overall AT minus within-Condition/Phase Baseline"].append(float(np.mean(a-b_mean[:,:,None])))
            values["Far AT minus within-Condition/Phase Baseline"].append(float(np.mean(a[:,:,0]-b_mean)))
            values["Far AT minus same-label Baseline"].append(float(np.mean(a[:,:,0]-b[:,:,0])))
            values["AT far-minus-near"].append(float(np.mean(a[:,:,0]-a[:,:,-1])))
            values["Baseline far-minus-near nominal label"].append(float(np.mean(b[:,:,0]-b[:,:,-1])))
            values["AT minus Baseline far-minus-near label contrast"].append(float(np.mean(a[:,:,0]-a[:,:,-1]-b[:,:,0]+b[:,:,-1])))
        if (pid,"pink") in noise and (pid,"white") in noise:
            values["Pink minus white AT"].append(noise[(pid,"pink")]-noise[(pid,"white")])
    contrasts=holm([paired(v,name) for name,v in values.items()])
    all_noise=[pid for pid in sorted({r["participant_id"] for r in at}) if all((pid,s) in noise for s in ("blue","brown","pink","white"))]
    friedman={"name":"four-noise complete-subject Friedman","status":"not_estimable","n":len(all_noise)}
    if len(all_noise)>=3:
        arrays=[np.array([noise[(pid,s)] for pid in all_noise]) for s in ("blue","brown","pink","white")]
        fit=stats.friedmanchisquare(*arrays)
        friedman.update(status="computed",chi2=float(fit.statistic),df=3,p=float(fit.pvalue),
            means=dict(zip(("blue","brown","pink","white"),[float(a.mean()) for a in arrays])))
    return contrasts,friedman


def sigmoid_fits(rows):
    baseline=grouped_means([r for r in rows if r["trial_type"]=="Baseline"],("participant_id","condition","phase"))
    grouped=defaultdict(list)
    for row in rows:
        if row["trial_type"]=="Audio-Tactile":
            grouped[(row["participant_id"],row["condition"],row["phase"])].append(row)
    records=[]
    for axis,mapping in AXES.items():
        for key,cell in sorted(grouped.items()):
            if key not in baseline:
                continue
            x=np.array([mapping[numeric(r,"soa_ms")] for r in cell])
            y=np.array([numeric(r,"reaction_time_ms")-baseline[key] for r in cell])
            unique=np.array(sorted(set(x)))
            if len(unique)!=5:
                continue
            counts=np.array([sum(x==u) for u in unique])
            means=np.array([y[x==u].mean() for u in unique])
            within=float(sum(np.sum((y[x==u]-mean)**2) for u,mean in zip(unique,means)))
            total=float(np.sum((y-y.mean())**2))
            ceiling=1-within/total if total>0 else 0.
            for level in ("trials","five_means"):
                weights=np.sqrt(counts) if level=="trials" else np.ones(5)
                lower=[-2000.,-2000.,unique.min(),.1]
                upper=[2000.,2000.,unique.max(),200.]
                def predict(theta):
                    a,b,m,s=theta
                    return a+(b-a)*special.expit((unique-m)/s)
                def residual(theta):
                    return weights*(predict(theta)-means)
                def jacobian(theta):
                    a,b,m,s=theta
                    q=special.expit((unique-m)/s)
                    common=(b-a)*q*(1-q)
                    return weights[:,None]*np.column_stack([1-q,q,-common/s,-common*(unique-m)/s**2])
                candidates=[]
                for fraction in (.25,.5,.75):
                    initial=[float(means[0]),float(means[-1]),float(unique.min()+fraction*np.ptp(unique)),20.]
                    fit=optimize.least_squares(residual,initial,jac=jacobian,bounds=(lower,upper),max_nfev=1000,ftol=1e-8,xtol=1e-8,gtol=1e-8)
                    if fit.success and np.all(np.isfinite(fit.x)):
                        candidates.append(fit)
                record={"participant_id":key[0],"condition":key[1],"phase":key[2],"axis":axis,"level":level,
                        "n_trials":len(y),"saturated_trial_r2_ceiling":ceiling,"status":"not_estimable"}
                if candidates:
                    fit=min(candidates,key=lambda f:float(f.fun@f.fun))
                    between=float(fit.fun@fit.fun)
                    sse=within+between if level=="trials" else between
                    denom=total if level=="trials" else float(np.sum((means-means.mean())**2))
                    r2=1-sse/denom if denom>0 else 0.
                    tolerance=1e-4*(np.array(upper)-np.array(lower))
                    bound=bool(np.any(fit.x-np.array(lower)<=tolerance) or np.any(np.array(upper)-fit.x<=tolerance))
                    linear=np.polyfit(unique,means,1,w=weights)
                    linear_sse=float(np.sum((weights*(np.polyval(linear,unique)-means))**2))+(within if level=="trials" else 0)
                    n=len(y) if level=="trials" else 5
                    record.update(status="computed",r2=float(r2),passes_r2=bool(r2>=.70),bound_hit=bound,
                        midpoint_cm=float(fit.x[2]),width_cm=float(fit.x[3]),lower_ms=float(fit.x[0]),upper_ms=float(fit.x[1]),
                        rmse=float(np.sqrt(sse/n)),linear_rmse=float(np.sqrt(linear_sse/n)))
                records.append(record)
    summaries=[]
    for axis in AXES:
        for level in ("trials","five_means"):
            selected=[r for r in records if r["axis"]==axis and r["level"]==level]
            successful=[r for r in selected if r["status"]=="computed"]
            all_ids={r["participant_id"] for r in selected}
            qualifying=[pid for pid in all_ids if len([r for r in successful if r["participant_id"]==pid and r["passes_r2"]])==4]
            interpretable=[pid for pid in qualifying if all(not r["bound_hit"] for r in successful if r["participant_id"]==pid)]
            summaries.append({"axis":axis,"level":level,"cells":len(selected),"computed":len(successful),
                "r2_pass_cells":sum(r["passes_r2"] for r in successful),"bound_hit_cells":sum(r["bound_hit"] for r in successful),
                "all_four_r2_participants":len(qualifying),"all_four_interpretable_participants":len(interpretable),
                "median_r2":float(np.median([r["r2"] for r in successful])) if successful else None,
                "max_r2":max((r["r2"] for r in successful),default=None),
                "max_trial_r2_ceiling":max((r["saturated_trial_r2_ceiling"] for r in selected),default=None),
                "sigmoid_better_rmse":sum(r["rmse"]<r["linear_rmse"] for r in successful)})
    return records,summaries


def curve_summaries(rows):
    at=grouped_means([r for r in rows if r["trial_type"]=="Audio-Tactile"],("participant_id","condition","phase","soa_ms"))
    base=grouped_means([r for r in rows if r["trial_type"]=="Baseline"],("participant_id","condition","phase","soa_ms"))
    base_cp=grouped_means([r for r in rows if r["trial_type"]=="Baseline"],("participant_id","condition","phase"))
    curves=[]
    for measure in ("raw_at","cell_mean_at_minus_baseline","same_label_at_minus_baseline"):
        for c in CONDITIONS:
            for p in PHASES:
                for s in SOAS:
                    vals=[]
                    for k,v in at.items():
                        if k[1:]!=(c,p,s):continue
                        if measure=="raw_at":vals.append(v)
                        elif measure=="same_label_at_minus_baseline" and k in base:vals.append(v-base[k])
                        elif measure=="cell_mean_at_minus_baseline" and k[:3] in base_cp:vals.append(v-base_cp[k[:3]])
                    if len(vals)<2:
                        continue
                    a=np.array(vals)
                    half=float(stats.t.ppf(.975,len(a)-1)*a.std(ddof=1)/np.sqrt(len(a)))
                    curves.append({"measure":measure,"condition":c,"phase":p,"soa_ms":s,"n":len(a),
                                   "mean_ms":float(a.mean()),"ci_low":float(a.mean()-half),"ci_high":float(a.mean()+half)})
    return curves


def descriptive_group_fits(curves):
    out=[]
    for axis,mapping in AXES.items():
        for condition in CONDITIONS:
            for phase in PHASES:
                data=[r for r in curves if r["measure"]=="cell_mean_at_minus_baseline" and r["condition"]==condition and r["phase"]==phase]
                if len(data)!=5:continue
                x=np.array([mapping[r["soa_ms"]] for r in data]);y=np.array([r["mean_ms"] for r in data])
                def model(theta):
                    a,b,m,s=theta
                    return a+(b-a)*special.expit((x-m)/s)
                bounds=([-2000.,-2000.,x.min(),.1],[2000.,2000.,x.max(),200.])
                fits=[]
                for fraction in (.25,.5,.75):
                    fit=optimize.least_squares(lambda t:model(t)-y,[y[np.argmin(x)],y[np.argmax(x)],x.min()+fraction*np.ptp(x),20.],bounds=bounds,max_nfev=1000)
                    if fit.success:fits.append(fit)
                if fits and np.sum((y-y.mean())**2)>0:
                    fit=min(fits,key=lambda f:float(f.fun@f.fun))
                    tolerance=1e-4*(np.array(bounds[1])-np.array(bounds[0]))
                    out.append({"axis":axis,"condition":condition,"phase":phase,"scope":"group description only; no participant replicates",
                        "points":5,"residual_df":1,"midpoint_cm":float(fit.x[2]),"width_cm":float(fit.x[3]),
                        "r2":float(1-(fit.fun@fit.fun)/np.sum((y-y.mean())**2)),
                        "bound_hit":bool(np.any(fit.x-np.array(bounds[0])<=tolerance) or np.any(np.array(bounds[1])-fit.x<=tolerance))})
    return out


def boundary_followups(records,people):
    selected=[r for r in records if r["axis"]=="registered" and r["level"]=="trials" and r["status"]=="computed"]
    ids=[p["participant_id"] for p in people if len([r for r in selected if r["participant_id"]==p["participant_id"] and r["passes_r2"] and not r["bound_hit"]])==4]
    if len(ids)<3:
        return {"status":"not_estimable","n":len(ids),"reason":"Fewer than three participants have all four interpretable trial-level curves; boundary inference and boundary-related MAIA/SpFrRef associations are gated off."}
    lookup={(r["participant_id"],r["condition"],r["phase"]):r for r in selected}
    effects={field:{pid:lookup[(pid,"Viscereality","Inhale")][field]-lookup[(pid,"Viscereality","Exhale")][field]-lookup[(pid,"Control","Inhale")][field]+lookup[(pid,"Control","Exhale")][field] for pid in ids} for field in ("midpoint_cm","width_cm")}
    contrasts=[paired(list(values.values()),field) for field,values in effects.items()]
    correlations=[]
    questionnaire=[k for k in people[0] if k.startswith("maia2_") and "item" not in k]+["spfrref_difference"]
    for field,effect in effects.items():
        for q in questionnaire:
            pairs=[]
            for person in people:
                pid=person["participant_id"]
                value=numeric(person,"spfrref_viscereality_ordinal")-numeric(person,"spfrref_control_ordinal") if q=="spfrref_difference" else numeric(person,q)
                if pid in effect and math.isfinite(value):pairs.append((effect[pid],value))
            if len(pairs)>=3 and np.std(np.array(pairs)[:,1])>0:
                rho,p=stats.spearmanr(np.array(pairs)[:,0],np.array(pairs)[:,1])
                correlations.append({"parameter":field,"questionnaire":q,"n":len(pairs),"rho":float(rho),"p":float(p),"classification":"exploratory conditional Spearman association"})
    return {"status":"computed","n":len(ids),"contrasts":contrasts,"correlations":holm(correlations)}


def analyze(people,trials,progress=None):
    """Execute every data-supported analysis in the companion contract."""
    notify=progress or (lambda text:None)
    if any(r["condition"] not in CONDITIONS or r["phase"] not in PHASES for r in trials):
        raise ValueError("Unexpected condition/phase labels.")
    notify("Cohort, response quality and participant-wide RT trimming")
    retained,quality,counts=clean(people,trials)
    at=[r for r in retained if r["trial_type"]=="Audio-Tactile"]
    primary=interaction(retained,label="primary numeric interaction")
    scale=(primary["soa_mean_ms"],primary["soa_sd_ms"])
    notify("Primary and secondary ML models; categorical and cohort sensitivities")
    models=[primary,interaction(retained,control=True,label="Control-only numeric interaction"),
        interaction(retained,categorical=True,label="categorical SOA"),
        interaction(retained,control=True,categorical=True,label="Control-only categorical SOA")]
    for label,cutoff,partial in (("exclude partial session",None,True),("RT ≥200 ms sensitivity",200.,False)):
        sensitivity,_,s_counts=clean(people,trials,cutoff=cutoff,exclude_partial=partial)
        for control in (False,True):
            for categorical in (False,True):
                name=f"{label}; {'Control' if control else 'all conditions'}; {'categorical' if categorical else 'numeric'}"
                model=safe_call(interaction,name,sensitivity,control=control,categorical=categorical,label=name)
                model["cleaning"]=s_counts
                models.append(model)
    models.append(safe_call(interaction,"random SOA slope",retained,random_slope=True,label="random SOA slope"))
    notify("Participant-cluster-robust models and participant-weighted contrasts")
    x,names,z,_=design(at,scale=scale)
    y=np.array([numeric(r,"reaction_time_ms") for r in at])
    groups=np.array([r["participant_id"] for r in at])
    regressions=[cluster_regression(x,y,groups,names,name="participant-cluster-robust raw RT")]
    regressions.append(safe_call(cluster_regression,"participant-cluster-robust log RT",x,np.log(y),groups,names,name="participant-cluster-robust log RT") if np.all(y>0) else {"name":"log RT","status":"not_estimable","reason":"Retained RT is nonpositive."})
    position=np.array([numeric(r,"trial_index")-204*(numeric(r,"part_number")-1) for r in at])
    position=(position-position.mean())/position.std(ddof=1)
    c=x[:,1];p=x[:,2]
    tx=np.column_stack([x,position,c*position,p*position,c*p*position])
    regressions.append(cluster_regression(tx,y,groups,names+["position","Condition × position","Phase × position","Condition × Phase × position"],name="time-on-task adjusted RT"))
    eligible_ids={q["participant_id"] for q in quality if not q["excluded_catch"]}
    all_at=[r for r in trials if r["trial_type"]=="Audio-Tactile" and r["participant_id"] in eligible_ids]
    hx,hn,_,_=design(all_at,scale=scale)
    regressions.append(safe_call(cluster_regression,"AT hit probability",hx,np.array([float(r["outcome"]=="hit") for r in all_at]),np.array([r["participant_id"] for r in all_at]),hn,binomial=True,name="AT hit probability"))
    slope,person_slopes=slope_contrasts(retained,scale)
    label_slope,_=slope_contrasts(retained,scale,True)
    order=[]
    for label in sorted({p["condition_order"] for p in people}):
        values=[person_slopes[p["participant_id"]] for p in people if p["condition_order"]==label and p["participant_id"] in person_slopes]
        order.append(paired(values,"Order: "+label,bayes=False))
    anovas=[]
    for corrected in (False,True):
        ids,cube=cell_cube(retained,corrected)
        if len(ids)>=3:
            anovas.extend([dict(r,measure="same-label corrected" if corrected else "raw AT") for r in repeated_anova(cube)])
    contrasts,friedman=supplementary(retained,people)
    notify("MAIA-2 scoring, spatial change, 42 rank associations and 16 moderation models")
    questionnaires=questionnaire_analysis(people,person_slopes)
    scored_people=[dict(person,**{k: str(v) if v is not None else "" for k,v in score.items() if k.startswith("maia2_")})
                   for person,score in zip(people,questionnaires["scores"])]
    notify("Sigmoid trial/mean fits, coordinate sensitivity and boundary gate")
    fits,sigmoid_summary=sigmoid_fits(retained)
    boundary=boundary_followups(fits,scored_people)
    notify("Missing-hit-RT stress scenarios with repeated trimming and ML")
    observed=defaultdict(list)
    for row in trials:
        if row["trial_type"]=="Audio-Tactile" and row["outcome"]=="hit" and math.isfinite(numeric(row,"reaction_time_ms")):
            observed[(row["participant_id"],row["condition"],row["phase"],numeric(row,"soa_ms"))].append(numeric(row,"reaction_time_ms"))
    stresses=[]
    for shift in (0.,-100.,100.,-200.,200.):
        changed=[];imputed=0;unresolved=0
        for row in trials:
            copy=dict(row)
            if row["trial_type"]=="Audio-Tactile" and row["outcome"]=="hit" and not math.isfinite(numeric(row,"reaction_time_ms")):
                key=(row["participant_id"],row["condition"],row["phase"],numeric(row,"soa_ms"))
                if key in observed:
                    sign=(1 if row["condition"]=="Viscereality" else -1)*(1 if row["phase"]=="Inhale" else -1)*np.sign(numeric(row,"soa_ms")-scale[0])
                    copy["reaction_time_ms"]=str(float(np.median(observed[key]))+shift*sign)
                    imputed+=1
                else:unresolved+=1
            changed.append(copy)
        scenario,_,_=clean(people,changed)
        fit=safe_call(interaction,f"missing RT signed shift {shift:g} ms",scenario,label=f"missing RT signed shift {shift:g} ms")
        fit.update(shift_ms=shift,imputed_hits=imputed,unresolved_hits=unresolved)
        stresses.append(fit)
    ages=np.array([numeric(p,"age_years") for p in people]);ages=ages[np.isfinite(ages)]
    curves=curve_summaries(retained)
    descriptions=descriptive_sigmoid_analysis(retained,progress=notify)
    individual=participant_sigmoid_analysis(retained,questionnaires,progress=notify,source_trials=trials)
    report={"analysis_version":"1.6","status":"reproducible analysis draft; recording linkage requires review",
        "runtime":{"python":platform.python_version(),"numpy":np.__version__,"scipy":scipy.__version__,"matplotlib":matplotlib.__version__,"platform":platform.system(),"execution":"browser Pyodide" if sys.platform=="emscripten" else "native validation"},
        "cohort":counts|{"age_mean":float(ages.mean()),"age_sd":float(ages.std(ddof=1)),"age_min":float(ages.min()),"age_max":float(ages.max()),
            "gender":dict(Counter(p["gender"] for p in people)),"handedness":dict(Counter(p["handedness"] for p in people)),"order":dict(Counter(p["condition_order"] for p in people)),
            "availability":dict(Counter(p["data_availability"] for p in people)),"trial_types":dict(Counter(r["trial_type"] for r in trials)),
            "outcomes":dict(Counter(r["outcome"] for r in trials))},
        "participant_quality":quality,"mixed_models":models,"cluster_models":regressions,
        "participant_slope_interaction":slope,"same_label_slope_interaction":label_slope,
        "order_sensitivities":order,"repeated_measures_anova":anovas,
        "supplementary_contrasts":contrasts,"four_noise_friedman":friedman,
        "sigmoid_fits":fits,"sigmoid_summary":sigmoid_summary,"boundary_followups":boundary,
        "missing_rt_stress":stresses,"group_curves":curves,"group_sigmoid_descriptions":descriptive_group_fits(curves),
        "descriptive_sigmoids":descriptions,
        "participant_sigmoids":individual,
        "questionnaire_descriptives":questionnaires["scales"],"questionnaires":questionnaires,
        "data_coverage":[
            {"domain":"Participant roster, demographics and order","status":"analysed","output":"Cohort age/gender/handedness/order, availability and participant QC"},
            {"domain":"Observed/planned trials, responses, missing RT and Catch","status":"analysed","output":"Quality denominators, exclusions and missing-RT sensitivities"},
            {"domain":"Condition × Phase × SOA reaction times","status":"analysed","output":"Mixed/cluster models, participant slopes, repeated measures and time-on-task"},
            {"domain":"Baseline, distance labels, noise type, order and RT flags","status":"analysed","output":"Supplementary contrasts, noise Friedman, order subgroups, coordinate/window sensitivities"},
            {"domain":"37 MAIA-2 items and eight dimensions","status":"analysed","output":"Scoring audit, distributions, alpha intervals and all fixed exploratory associations"},
            {"domain":"Paired spatial-frame ratings","status":"analysed","output":"Post-intervention code delta, exact sign test, main trait correlations, direction sensitivity and Condition × MAIA moderation with order/HC3 sensitivities"},
            {"domain":"Participant PPS boundary and related questionnaire inference","status":boundary["status"],"output":"Fit gate retained; group approximations remain descriptive"},
            {"domain":"Exploratory individual sigmoid proxies and normalized RT","status":individual["status"],"output":"Four fitted proxies per record, normalization, shared-plateau sensitivity, recovery/reliability and provisional questionnaire links; recording-linkage audit"},
            {"domain":"Repeated MAIA, body-boundary and small-self measures","status":"unavailable","output":"No corresponding repeated/measure columns in released tables"},
            {"domain":"Waveforms, measured breathing and acquisition provenance","status":"unavailable","output":"Source recordings and private metadata are outside the release"}],
        "unavailable_checks":[
            "Waveform cue-time and RT-onset validation: original recordings are not in the released CSVs.",
            "Measured respiratory compliance: phase labels are scheduled/instructed, not belt-verified.",
            "Pilot dates, acquisition-version effects and two source-onset exclusions: required provenance metadata are not released."],
        "interpretation":[
            "Recording-linkage audit: "+individual.get("linkage_audit",{}).get("status","unavailable")+". Full-release behavioural inference requires provenance review; the questionnaire-only spatial analysis is separate.",
            "No failure to reject is interpreted as equivalence or proof of zero effect.",
            "Same-SOA-label Baseline subtraction is not a verified cue-time-matched contrast.",
            "Sigmoid bounds are an explicit reimplementation; saturated R² ceilings independently bound viability.",
            "Four post hoc group sigmoid approximations use one selected extraction/smoothing/fitting pipeline. They do not supply participant boundary inference; bootstrap intervals condition on the chosen method.",
            "The PPS-shape extension compares explicit measured-range shape constraints with equally processed lines using nested participant prediction. Imposed S shapes do not establish empirical curvature or physiological boundaries.",
            "JZS paired-contrast Bayes factors are exploratory and are not a mixed-model Bayes factor."]}
    notify("Analysis complete")
    return report,retained
