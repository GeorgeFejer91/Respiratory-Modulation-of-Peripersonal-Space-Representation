"""Partial-identification screen for missing or slow tactile responses."""

import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.optimize import isotonic_regression
from scipy.special import expit
from scipy.stats import beta, t

from profile import COHORTS
from screen import (CELL_NAMES, DISTANCES, OUT, ROOT, cohort_mask, load_data,
                    phase_profiles, write_csv)
from threshold import build_rows, recovery_metrics

SEED = 20261122
DRAWS = 96
EVENTS = {"miss":None, "miss_or_slow400":400, "miss_or_slow600":600, "miss_or_slow800":800}
SOA = (2700.,2200.,1500.,800.,300.)


def counts(ids):
    shape = (2,len(ids),len(CELL_NAMES),len(SOA))
    total = np.zeros(shape,dtype=int)
    lower = {event: np.zeros(shape,dtype=int) for event in EVENTS}
    unrecorded = np.zeros(shape,dtype=int)
    index = {p:i for i,p in enumerate(ids)}
    kind = {"Audio-Tactile":0,"Baseline":1}
    table = ROOT/"data/raw/study5_pps_trials.csv"
    with table.open(encoding="utf-8",newline="") as stream:
        for row in csv.DictReader(stream):
            group = row["trial_type"]
            pid = row["participant_id"]
            if pid not in index or group not in kind:
                continue
            key = (kind[group],index[pid],CELL_NAMES.index(row["condition"]+" "+row["phase"]),
                   SOA.index(float(row["soa_ms"])))
            if row["outcome"] not in ("hit","miss"):
                raise ValueError("Unexpected released tactile outcome.")
            miss = row["outcome"] == "miss"
            known = bool(row["reaction_time_ms"].strip())
            if miss == (row["response_given"]=="True") or (miss and known):
                raise ValueError("Released outcome, response and RT do not agree.")
            total[key] += 1
            unrecorded[key] += (not miss and not known)
            for event, cutoff in EVENTS.items():
                lower[event][key] += miss or (
                    cutoff is not None and known and float(row["reaction_time_ms"]) > cutoff)
    if np.any(total<=0):
        raise ValueError("Every included participant has tactile observations at every probe.")
    upper = {ev: a if EVENTS[ev] is None else a+unrecorded for ev,a in lower.items()}
    return total, lower, upper, unrecorded


def exact_limits(n, low, high, tail):
    a = np.where(low==0, 0., beta.ppf(tail,low,n-low+1))
    b = np.where(high==n, 1., beta.isf(tail,high+1,n-high))
    return a,b


def contrast_correction(lower, upper, correction):
    if correction == "same_label":
        return lower[0]-upper[1],upper[0]-lower[1]
    return lower[0],upper[0]


def individual_limits(n, low, high, correction, alpha):
    sources = 2 if correction=="same_label" else 1
    tail = alpha/(2*sources*len(SOA))
    phase = contrast_correction(*exact_limits(n,low,high,tail),correction)
    equal = contrast_correction(*exact_limits(n,low,high,tail/2),correction)
    summarized = tuple(np.concatenate((a,phase_profiles(b)[...,4:,:]),axis=-2)
                       for a,b in zip(phase,equal))
    return *summarized,np.ones(summarized[0].shape[:-1],dtype=bool)


def equal_person_limits(n, low, high, correction, alpha):
    lower, upper = contrast_correction(low/n,high/n,correction)
    lower, upper = phase_profiles(lower),phase_profiles(upper)
    count = lower.shape[-3]
    radius = t.isf(alpha/(2*len(SOA)),count-1)/np.sqrt(count)
    floor = -1 if correction=="same_label" else 0
    lo = np.maximum(floor,lower.mean(-3)-radius*lower.std(-3,ddof=1))
    hi = np.minimum(1,upper.mean(-3)+radius*upper.std(-3,ddof=1))
    return lo,hi,np.ones_like(lo[...,0],dtype=bool)


def predictions(rates, counts, distance):
    errors = dict(flat=[],linear=[],log_distance=[],isotonic=[])
    y = rates.reshape(-1,len(distance))
    w = counts.reshape(-1,len(distance))
    log_x = np.log(distance)
    for held in range(len(distance)):
        train = np.delete(np.arange(len(distance)),held)
        obs, weight = y[:,train],w[:,train]
        center = np.sum(obs*weight,axis=-1)/weight.sum(-1)
        errors["flat"].append(np.square(center-y[:,held]))
        for name,x in (("linear",distance),("log_distance",log_x)):
            mean_x = (weight*x[train]).sum(-1)/weight.sum(-1)
            offset = x[train]-mean_x[:,None]
            slope = ((obs-center[:,None])*weight*offset).sum(-1)/(offset**2*weight).sum(-1)
            pred = np.clip(center+slope*(x[held]-mean_x),0,1)
            errors[name].append(np.square(pred-y[:,held]))
        fit = [isotonic_regression(sample,weights=wt).x for sample,wt in zip(obs,weight)]
        pred = np.array([np.interp(distance[held],distance[train],a) for a in fit])
        errors["isotonic"].append(np.square(pred-y[:,held]))
    return {k:100*float(np.sqrt(np.mean(a))) for k,a in errors.items()}


def recover(n, distance):
    rng = np.random.default_rng(SEED)
    x = (distance-distance[0])/np.ptp(distance)
    person = np.linspace(-.025,.025,n.shape[0])[:,None,None]
    centers = np.array([.40,.46,.54,.61])[:,None]
    truths = {"flat":np.full(n.shape,.08),
              "linear":np.broadcast_to(.04+.15*x,n.shape),
              "steep":.035+person+.20*expit((x-centers)/.08)}
    out = {}
    for name, prob in truths.items():
        a = rng.binomial(n,prob,size=(DRAWS,*n.shape))
        s = np.stack((a,np.zeros_like(a)))
        denom = np.broadcast_to(n,s.shape)
        correction = "pooled"
        q = phase_profiles(prob)
        p_r = [individual_limits(denom,s,s,correction,alpha) for alpha in (.05,.0125)]
        g_r = [equal_person_limits(denom,s,s,correction,alpha) for alpha in (.05,.0125)]
        out[name] = dict(individual=recovery_metrics(*p_r,q,None,distance),
                         group=recovery_metrics(*g_r,q.mean(0),None,distance))
    return out


def check_intervals():
    n = np.array([20,20,20])
    l,u = exact_limits(n,np.array([0,3,20]),np.array([0,3,20]),.025)
    np.testing.assert_allclose(u[0],1-.025**(1/20))
    np.testing.assert_allclose(l[-1],.025**(1/20))
    a,b = exact_limits(n,np.array([0,3,20]),np.array([1,4,20]),.025)
    np.testing.assert_array_equal(a,l)
    assert ((b>=u)&(a<=b)).all()


def run():
    check_intervals()
    ids,_,_,audit = load_data()
    n,low,high,missing = counts(ids)
    primary = cohort_mask(ids,"primary40")
    rows,effects,score = [],[],{}
    for event in EVENTS:
        a,b = low[event],high[event]
        for axis, distance in DISTANCES.items():
            label = dict(axis=axis,event=event)
            for correction in ("pooled","same_label"):
                targets = {"observed_half":None}
                def add(data, people, cohort, individual=False):
                    calc = individual_limits if individual else equal_person_limits
                    bands = [calc(*data,correction,alpha) for alpha in (.05,.0125)]
                    packed = bands if individual else [tuple(x[None,...] for x in k) for k in bands]
                    reports = build_rows(*({"at":q} for q in packed),targets,people,distance,
                                         dict(label,correction=correction,cohort=cohort))
                    rows.extend(reports[0])
                    effects.extend(reports[1])
                add(tuple(v[:,primary] for v in (n,a,b)),ids[primary],"primary40",individual=True)
                for cohort in COHORTS:
                    keep = cohort_mask(ids,cohort)
                    add(tuple(v[:,keep] for v in (n,a,b)),["equal_participant_group"],cohort)
            code = {}
            for mode,bound in (("lower_events",a),("upper_events",b)):
                al = n[0,primary]
                rate = bound[0,primary]/al
                group = rate.mean(0)
                code[mode] = dict(individual=predictions(rate,al,distance),
                                  group=predictions(group,np.ones_like(group),distance))
            score[axis+"_"+event] = code
    files = [OUT/"response_threshold_profiles.csv",OUT/"response_threshold_contrasts.csv"]
    for path,response in zip(files,(rows,effects)):
        write_csv(path,response)
    covered = [Path(__file__),Path(__file__).with_name("threshold.py"),
               Path(__file__).with_name("threshold_sets.py"),OUT/"RESPONSE_SPECIFICATION.md",*files]
    receipt = dict(input=audit, seed=SEED, draws=DRAWS,
                   primary_trials=n[:,primary].sum((1,2,3)).tolist(),
                   primary_misses=low["miss"][:,primary].sum((1,2,3)).tolist(),
                   primary_unknown_latencies=missing[:,primary].sum((1,2,3)).tolist(),
                   held_probability_rmse_percentage_points=score,recovery=recover(n[0,primary],DISTANCES["registered"]),
                   sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in covered})
    (OUT/"response_threshold_results.json").write_text(json.dumps(receipt,indent=2,allow_nan=False)+"\n",
                                                      encoding="utf-8")
    print(f"Wrote {len(rows)} response-boundary profiles and {len(effects)} contrasts.")


if __name__ == "__main__":
    run()
