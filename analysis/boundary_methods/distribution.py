"""Lognormal location and dispersion profiles of retained positive AT RT."""

import hashlib
import json
import platform
from functools import lru_cache

import numpy as np
import scipy
from scipy.special import digamma, polygamma
from scipy.stats import norm

from profile import (ALPHA, CALIBRATION, COHORTS, group_cutoffs, group_data,
                     joint_rows, moments, person_cutoffs, profile_rows, variance_six)
from profile_grid import REFERENCES, ShapeGrid, WeightedBasis, diag_cov
from screen import DISTANCES, OUT, ROOT, W, cohort_mask, load_data, phase_profiles, write_csv

SEED = 20261124
REPLICATES = 96
SHIFTS = (0, 150)
COMPONENTS = ("log_location", "log_scale")


def scale_stats(df):
    shape = df / 2
    return (digamma(shape) - np.log(shape)) / 2, polygamma(1, shape) / 4


def components(values):
    mean, variance, df = moments(values)
    if (df < 1).any() or (variance <= 0).any():
        raise ValueError("These profiles require positive within-probe variation and at least two hits.")
    bias, scale_variance = scale_stats(df)
    log_scale = .5*np.log(variance*(df+1)) - bias
    return (mean, log_scale), (variance, scale_variance), df


@lru_cache(maxsize=None)
def scale_envelope(degrees):
    df = np.asarray(degrees)
    bias, var = scale_stats(df)
    rng = np.random.default_rng(SEED)
    pivot = (.5*np.log(rng.chisquare(df, size=(CALIBRATION, len(df)))/df)-bias)/np.sqrt(var)
    return np.quantile(np.square(pivot).sum(-1), [1-ALPHA, 1-ALPHA/4], method="higher")


def scale_cutoffs(df):
    return np.array([[scale_envelope(tuple(np.sort(d))) for d in (*s, *s.reshape(2, 10))] for s in df])


def features_predictions(means, variances, grid, span):
    shapes = np.vstack((grid.reference_shapes,grid.shapes[grid.design_subset].reshape(-1,5)))
    names = (*REFERENCES, "logistic")
    out = {name: [] for name in names}
    cov = diag_cov(variances)
    for held in range(5):
        fitter = WeightedBasis(cov, shapes, np.delete(np.arange(5),held), span)
        loss, amplitude = fitter.surface(means)
        best = loss[...,3:].argmin(-1) + 3
        for i, name in enumerate(names):
            selected = best if name == "logistic" else np.full(best.shape,i)
            amp = np.take_along_axis(amplitude,selected[...,None],-1)[...,0]
            out[name].append(fitter.predict(means,selected,amp,held))
    return {name:np.stack(series,axis=-1) for name,series in out.items()}


def score_predictions(values, means, variances, grid, span):
    centers, scales = [features_predictions(m,v,grid,span) for m,v in zip(means,variances)]
    pairs = {name:(name,name) for name in REFERENCES}
    pairs.update(location_only=("logistic","flat"), scale_only=("flat","logistic"), both=("logistic","logistic"))
    out = {}
    for name, (location, scale) in pairs.items():
        lpdf = norm.logpdf(values, loc=centers[location][...,None],
                           scale=np.exp(scales[scale][...,None])) - values
        per_probe = np.nanmean(lpdf,axis=-1)
        out[name] = dict(equal_person_log_density=float(per_probe.mean()),
                         trial_weighted_log_density=float(np.nanmean(lpdf)),
                         probe_log_density=per_probe.mean(axis=(0,1)).tolist())
    return out


def recovery(means, df, cutoffs, grid):
    """Use exact lognormal sufficient statistics with observed blocks and counts."""
    rng = np.random.default_rng(SEED + 1)
    shape_grid = grid.shapes.reshape(-1,5)
    m = np.argmin(np.abs(grid.midpoints[None,:] - np.array([55,45,65,60])[:,None]),axis=-1)
    w = np.argmin(abs(grid.relative_width-1/6))
    targets = m*len(grid.relative_width)+w
    feature_shape = shape_grid[targets]
    inside = (grid.midpoints>grid.distance[0]) & (grid.midpoints<grid.distance[-1])
    person_cut = [v[:,:4,0] for v in cutoffs]
    group_cut = group_cutoffs(len(df))[0,:4,0]
    bias, v_scale = scale_stats(df)
    v = diag_cov(v_scale)
    scale_engine = WeightedBasis(v,shape_grid)
    scale_ref = WeightedBasis(v,grid.reference_shapes)
    results = {}

    def performance(fitter, ref, feature, cutoff, structured):
        loss = fitter.surface(feature)[0]
        null = (ref.surface(feature)[0] <= cutoff[...,None]).any(-1)
        supported = (loss.reshape(*feature.shape[:-1],len(grid.midpoints),-1) <= cutoff[...,None,None]).any(-1)
        local = supported.any(-1) & ~(supported & ~inside).any(-1) & ~null
        fixed = np.take_along_axis(loss,np.broadcast_to(targets[...,None],(*loss.shape[:-1],1)),-1)[...,0]
        mask = np.repeat(grid.design_subset,len(grid.relative_width))
        narrowing = np.where(mask,loss,np.inf)
        peak = grid.midpoints[narrowing.argmin(-1)//len(grid.relative_width)]
        error = (peak-grid.midpoints[m]) @ W[0]
        return (local.mean(), (fixed<=cutoff).mean() if structured else 0, np.square(error).mean() if structured else 0)

    for label, loc_span, scale_span in (("flat",0,0),("location",.18,0),("scale",0,.35)):
        mu = means[0].mean(-1,keepdims=True) + loc_span*feature_shape
        scale = means[1].mean(-1,keepdims=True) + scale_span*feature_shape
        spread = np.exp(scale)
        p = [[],[]]
        g = [[],[]]
        for _ in range(REPLICATES):
            trial_var = spread**2 * rng.chisquare(df)/df
            estimated = (mu + rng.normal(size=mu.shape)*spread/np.sqrt(df+1), .5*np.log(trial_var)-bias)
            v_mu = diag_cov(trial_var/(df+1))
            loc_engine = WeightedBasis(v_mu,shape_grid)
            loc_ref = WeightedBasis(v_mu,grid.reference_shapes)
            for k, (feature, fitter, ref, effect) in enumerate(zip(estimated,(loc_engine,scale_engine),
                                                                (loc_ref,scale_ref),(loc_span,scale_span))):
                p[k].append(performance(fitter,ref,feature,person_cut[k],bool(effect)))
                average,cov = group_data(feature)
                g[k].append(performance(WeightedBasis(cov,shape_grid),WeightedBasis(cov,grid.reference_shapes),
                                        average,group_cut[None,:],bool(effect)))
        reports = {}
        for k, name in enumerate(COMPONENTS):
            reports[name] = {}
            for level, raw in (("participant",p[k]),("group",g[k])):
                detected, covered, mse = np.mean(raw,axis=0)
                structured = bool((loc_span,scale_span)[k])
                reports[name][level] = dict(localized_fraction=detected, conditional_truth_in_set=covered if structured else None,
                                            conditional_point_condition_rmse_cm=np.sqrt(mse) if structured else None)
        results[label] = reports
    results["truths"] = dict(midpoints_cm=grid.midpoints[m].tolist(),condition_effect_cm=float(grid.midpoints[m]@W[0]))
    return results


def run():
    ids, at, _, audit = load_data()
    rows, contrasts, prediction = [], [], []
    recovery_report = None
    for shift in SHIFTS:
        values = np.log((at-shift)/1000)
        means, variances, df = components(values)
        thresholds = person_cutoffs(df), scale_cutoffs(df)
        primary = cohort_mask(ids,"primary40")
        for axis, distance in DISTANCES.items():
            grid = ShapeGrid.logistic(distance)
            for cap in (1.5,2,3):
                s = score_predictions(values[primary],tuple(z[primary] for z in means),
                                      tuple(z[primary] for z in variances),grid,np.log(cap))
                prediction.extend(dict(shift_ms=shift,axis=axis,span_ratio=cap,model=name,
                                       probe_log_density=json.dumps(v.pop("probe_log_density")),**v) for name,v in s.items())
            for name, y, var, cutoff in zip(COMPONENTS,means,variances,thresholds):
                label = dict(axis=axis, shift_ms=shift, component=name)
                expanded = phase_profiles(y)
                estimates = [(expanded[primary],diag_cov(variance_six(var[primary])),cutoff[primary],
                              ids[primary],"primary40")]
                for cohort in COHORTS:
                    keep = cohort_mask(ids,cohort)
                    average, cov = group_data(expanded[keep])
                    estimates.append((average,cov,group_cutoffs(int(keep.sum())),
                                      ["equal_participant_group"],cohort))
                for y_use, cov, cuts, labels, cohort in estimates:
                    tags = dict(label,cohort=cohort)
                    result, loss, ref = profile_rows(y_use,cov,cuts,labels,grid,tags)
                    for row in result:
                        if "best_span_ms" in row:
                            row["best_span_log_units"] = row.pop("best_span_ms")
                    rows.extend(result)
                    contrasts.extend(joint_rows(loss,ref,cuts,labels,grid,tags))
            if not shift and axis == "registered":
                recovery_report = recovery(tuple(z[primary] for z in means),df[primary],
                                           tuple(z[primary] for z in thresholds),grid)
    path = OUT/"distribution_results.json"
    write_csv(OUT/"distribution_profiles.csv",rows)
    write_csv(OUT/"distribution_contrasts.csv",contrasts)
    write_csv(OUT/"distribution_prediction.csv",prediction)
    scripts = ROOT/"analysis/boundary_methods"
    files = [*OUT.glob("distribution_*.csv"),*(scripts/f"{name}.py" for name in
             ("distribution","profile","profile_grid","screen")),
             ROOT/"analysis/baseline_effects/baseline_effects.py", OUT/"DISTRIBUTION_SPECIFICATION.md"]
    receipt = dict(input=audit, seed=SEED, replicates=REPLICATES, recovery=recovery_report,
                   support_shifts_ms=SHIFTS,python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,
                   sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)})
    path.write_text(json.dumps(receipt,indent=2,allow_nan=False)+"\n",encoding="utf8",newline="\n")
    print(f"Wrote {len(rows)} profiles, {len(contrasts)} contrasts and {len(prediction)} prediction rows.")


if __name__ == "__main__":
    run()
