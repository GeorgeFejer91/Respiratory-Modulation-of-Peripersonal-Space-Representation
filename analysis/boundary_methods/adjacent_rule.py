"""Group first detectable adjacent decrease with paired cluster resampling."""

import hashlib
import json
import platform
from pathlib import Path

import numpy as np
import scipy
from scipy import stats

from profile import COHORTS
from screen import DISTANCES, EFFECTS, OUT, ROOT, SUMMARY_LABELS, W, cohort_mask, load_data, phase_profiles

SEED = 20261130
BOOTSTRAPS = 999
RECOVERY = 96
ALPHA = .05


def comparison(profiles):
    differences = np.diff(profiles,axis=-1)
    count = differences.shape[-3]
    number_gaps = differences.shape[-1]
    mean = differences.mean(axis=-3)
    se = differences.std(axis=-3,ddof=1)/np.sqrt(count)
    t_value = np.divide(mean,se,out=np.zeros_like(mean),where=se>0)
    t_value = np.where((se==0)&(mean!=0),np.copysign(np.inf,mean),t_value)
    adjusted = np.minimum(1,number_gaps*stats.t.sf(t_value,count-1))
    edge = stats.t.isf(ALPHA/(2*number_gaps),count-1)*se
    selected = np.where(adjusted<ALPHA,np.arange(number_gaps),-1).max(-1)
    return selected, mean, adjusted, np.stack((mean-edge,mean+edge),axis=-1)


def gap_location(reference, points):
    if reference<0:
        return None
    left,right = points[reference:reference+2]
    return dict(probe_indices=[int(left),int(right)],
                **{name:axis[[left,right]].tolist() for name,axis in DISTANCES.items()})


def boot_counts(selection, number_gaps):
    return np.stack([(selection==gap).sum(axis=0) for gap in range(-1,number_gaps)],axis=-1)


def paired_selection(control, viscereality):
    a, b = control>=0, viscereality>=0
    same = a&b&(control==viscereality)
    states = dict(neither=~a&~b,control_only=a&~b,viscereality_only=~a&b,
                  same_gap=same,different_gaps=a&b&~same)
    return {name:int(mask.sum()) for name,mask in states.items()}


def summarize_observed(profiles, rng, correction, cohort):
    selected,means,pvals,intervals = comparison(profiles)
    indices = rng.integers(len(profiles),size=(BOOTSTRAPS,len(profiles)))
    resampled = comparison(profiles[indices])[0]
    frequencies = boot_counts(resampled,profiles.shape[-1]-1)
    points = np.arange(profiles.shape[-1])
    held = []
    for h in points:
        kept = points[points!=h]
        result = comparison(profiles[...,kept])[0]
        held.append([gap_location(gap,kept) for gap in result])
    combined = []
    for j, label in enumerate(SUMMARY_LABELS):
        combined.append(dict(correction=correction,cohort=cohort,profile=label,participants=len(profiles),
                             gap=gap_location(selected[j],points),
                             adjacent_differences_ms=means[j].tolist(),
                             adjusted_one_sided_p=pvals[j].tolist(),
                             simultaneous_intervals_ms=intervals[j].tolist(),
                             bootstrap_counts_none_then_near_to_far=frequencies[j].tolist(),
                             delete_one_probe_gap=[case[j] for case in held]))
    label_pairs = (("Exhale",0,2),("Inhale",1,3),("equal_phase",4,5))
    joint_selection = {name:paired_selection(resampled[:,a],resampled[:,b]) for name,a,b in label_pairs}
    effects = np.einsum("ec,ncd->ned",W,profiles[:,:4])
    _, values, _, limits = comparison(effects)
    paired_jumps = [dict(effect=name,adjacent_effects_ms=mu.tolist(),simultaneous_intervals_ms=ci.tolist())
                    for name,mu,ci in zip(EFFECTS,values,limits)]
    return combined,dict(correction=correction,cohort=cohort,
                         paired_bootstrap_states=joint_selection,
                         paired_rt_adjacent_effects=paired_jumps)


def recovery(profiles, rng, correction):
    residual = profiles-profiles.mean(axis=0)
    shape = np.arange(5)>np.array([1,1,2,2])[:,None]
    steps = phase_profiles(shape.astype(float)[None])[0]
    truth = np.array([1,1,2,2,1,2])
    for amplitude in (0.,40.,120.):
        samples = rng.integers(len(profiles),size=(RECOVERY,len(profiles)))
        choice = comparison(residual[samples]+amplitude*steps)[0]
        correct = choice==(-1 if amplitude==0 else truth)
        meta = dict(correction=correction,amplitude_ms=amplitude,replicates=RECOVERY,
                    correct_state_counts=correct.sum(0).tolist(),
                    none_counts=(choice<0).sum(0).tolist(),
                    wrong_gap_counts=((choice>=0)&~correct).sum(0).tolist(),
                    both_conditions_correct=int(correct[:,-2:].all(-1).sum()),
                    any_gap=int((choice>=0).any(-1).sum()))
        yield meta


def checks():
    rng = np.random.default_rng(49)
    values = rng.normal(0,1,(40,6,5))
    _,_,pval,_ = comparison(values)
    direct = stats.ttest_1samp(np.diff(values,axis=-1),0,axis=0,alternative="greater")
    np.testing.assert_allclose(pval,np.minimum(1,direct.pvalue*4),atol=1e-13)
    points = np.arange(5)
    expected = np.array([0,0,1,1,2,2])
    planted = values+100*(points>expected[:,None])
    np.testing.assert_array_equal(comparison(planted)[0],expected)
    np.testing.assert_array_equal(comparison(values.mean(-1,keepdims=True)*np.ones(5))[0],-1)
    assert gap_location(1,np.array([0,1,3,4]))["probe_indices"] == [1,3]


def run():
    checks()
    ids, at, baseline, audit = load_data()
    at_mean = np.nanmean(at,axis=-1)
    baseline_mean = np.nanmean(baseline,axis=-1)
    pooled = np.nanmean(baseline,axis=(-2,-1))[...,None]
    np.testing.assert_allclose(np.diff(at_mean-pooled,axis=-1),np.diff(at_mean,axis=-1),atol=1e-10)
    observed, recovered, paired = [], [], []
    for correction, values in (("raw_or_pooled",at_mean),("same_label",at_mean-baseline_mean)):
        profiles = phase_profiles(values)
        for cohort in COHORTS:
            selected = cohort_mask(ids,cohort)
            rows, contrasts = summarize_observed(profiles[selected],np.random.default_rng(SEED),correction,cohort)
            observed.extend(rows)
            paired.append(contrasts)
        recovered.extend(recovery(profiles[cohort_mask(ids,"primary40")],np.random.default_rng(SEED+1),correction))
    sources = [Path(__file__),Path(__file__).with_name("screen.py"),Path(__file__).with_name("profile.py"),
               ROOT/"analysis/baseline_effects/requirements.txt",OUT/"ADJACENT_RULE_SPECIFICATION.md"]
    result = dict(input=audit,seed=SEED,runtime=dict(python=platform.python_version(),numpy=np.__version__,
                                                     scipy=scipy.__version__),
                  profiles=SUMMARY_LABELS,bootstrap_replicates=BOOTSTRAPS,
                  observed=observed,paired=paired,recovery=recovered,
                  sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sources})
    (OUT/"adjacent_rule_results.json").write_text(
        json.dumps(result,indent=2,allow_nan=False)+"\n",encoding="utf8",newline="\n")
    print(f"Verified adjacent comparisons for {len(observed)} group profiles and {len(recovered)} recovery batches.")


if __name__=="__main__":
    run()
