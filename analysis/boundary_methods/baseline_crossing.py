"""Fit linear crossings of tactile-only references with ratio uncertainty."""

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.stats import f, t

from crossing_ratio import ratio_intervals
from knot_grid import KnotFit, make_grid
from profile import COHORTS, envelope, moments
from profile_grid import REFERENCES, diag_cov
from screen import (DISTANCES, EFFECTS, OUT, ROOT, SUMMARY_LABELS, W, cohort_mask, load_data,
                    resample_trials, write_csv)

SEED = 20261120
BOOTSTRAPS = 499
RECOVERY = 96
RULES = ("pooled_mean", "pooled_lower95", "fastest_delay_lower95", "same_label_zero")
EFFECT_WEIGHTS = (*W, np.array([0., 0., 0., 0., -1., 1.]))
EFFECT_NAMES = (*EFFECTS, "Condition of equal-phase profiles")


def phase_average(values, variance=False):
    phase_pairs = values.reshape(*values.shape[:-2], 2, 2, values.shape[-1])
    combined = phase_pairs.sum(-2)/(4 if variance else 2)
    return np.concatenate((values, combined), axis=-2)


def phase_stats(mean, var, df):
    var6 = phase_average(var, variance=True)
    denom = phase_average(var**2/df, variance=True)[..., 4:, :]/4
    phase_totals = 2*phase_average(df)[..., 4:, :]
    combined_df = np.divide(var6[..., 4:, :]**2, denom, out=phase_totals, where=denom>0)
    df6 = np.concatenate((df, combined_df), axis=-2)
    return phase_average(mean), var6, df6


def primitive(at, baseline, rule):
    a, va, da = moments(at)
    if rule.startswith("pooled"):
        baseline = baseline.reshape(*baseline.shape[:-2], 1, -1)
    b, vb, db = moments(baseline)
    if rule == "same_label_zero":
        var = va + vb
        baseline_term = np.divide(vb**2, db, out=np.full_like(vb, np.nan), where=db>0)
        denom = va**2/da + baseline_term
        df = np.divide(var**2, denom, out=np.full_like(var, np.nan), where=denom>0)
        return a-b, var, df, np.concatenate((da, db), axis=-1)
    means = np.concatenate((a, b), axis=-1)
    vars_ = np.concatenate((va, vb), axis=-1)
    dfs = np.concatenate((da, db), axis=-1)
    return means, vars_, dfs, dfs


@dataclass
class JointInputs:
    means: np.ndarray
    covariance: np.ndarray
    degrees: np.ndarray
    radii: np.ndarray | None
    available: np.ndarray

    @classmethod
    def individual(cls, mean, var, df, envelope_df, radius=True):
        y, v, dfs = phase_stats(mean, var, df)
        valid = np.isfinite(v).all(-1) & (v[..., :5] > 0).all(-1) & np.isfinite(dfs).all(-1)
        if radius:
            valid &= (v>0).all(-1)
        cov = diag_cov(np.where(np.isfinite(v) & (v>=0), v, 1.))
        cov = np.where(valid[..., None, None], cov, np.eye(v.shape[-1]))
        radii = None
        if radius:
            n = envelope_df.shape[-1]
            paired = envelope_df.reshape(-1, 2, 2*n)
            any_leading = (*envelope_df.shape[:-2], 2, 2*n)
            paired = paired.reshape(any_leading)
            radii = np.full((*y.shape[:-1], 2), np.nan)
            for index in zip(*np.where(valid)):
                j = index[-1]
                dfs_used = envelope_df[index] if j < 4 else paired[(*index[:-1], j-4)]
                radii[index] = envelope(tuple(np.sort(dfs_used)))
        return cls(y, cov, dfs, radii, valid)

    @classmethod
    def group(cls, observations, radius=True):
        joined = phase_average(observations)
        n = joined.shape[-3]
        average = joined.mean(-3)
        centered = joined-average[..., None, :, :]
        cov = np.einsum("...nci,...ncj->...cij", centered, centered)/(n*(n-1))
        d = average.shape[-1]
        available = np.linalg.eigvalsh(cov)[..., 0] > 1e-12
        radii = None
        if radius:
            levels = d*(n-1)/(n-d)*f.ppf([.95, .9875], d, n-d)
            radii = np.broadcast_to(levels, (*average.shape[:-1], 2))
        fallback = np.eye(d)
        return cls(average, np.where(available[...,None,None],cov,fallback),
                   np.full_like(average, n-1), radii, available)


def fit_line(inputs, x, weighting):
    cov = inputs.covariance[..., :5, :5]
    design = np.column_stack((np.ones_like(x), x))
    whiten = np.linalg.cholesky(cov)
    if weighting == "gls":
        weighted = np.linalg.solve(whiten, np.broadcast_to(design, (*cov.shape[:-2], *design.shape)))
        projection = np.linalg.pinv(weighted) @ np.linalg.inv(whiten)
    else:
        projection = np.broadcast_to(np.linalg.pinv(design), (*cov.shape[:-2], 2, len(x)))
    fit = (projection @ inputs.means[..., :5, None])[..., 0]
    residual = inputs.means[..., :5] - fit @ design.T
    white = np.linalg.solve(whiten, residual[..., None])
    lack_of_fit = np.square(white).sum(axis=(-2, -1))
    return fit, projection, lack_of_fit


def make_targets(inputs, rule):
    d = inputs.means.shape[-1]
    if d == 5:
        basis = np.zeros((1, 5))
        margins = np.zeros((*inputs.means.shape[:-1], 1))
    else:
        basis = np.eye(d)[5:]
        variances = np.diagonal(inputs.covariance, axis1=-2, axis2=-1)[...,5:]
        margins = t.ppf(.975, inputs.degrees[...,5:])*np.sqrt(variances)
        if rule == "pooled_mean":
            margins = np.zeros_like(margins)
    return basis, margins


def merge_sets(items):
    ordered = sorted([(-np.inf if low is None else low, np.inf if high is None else high)
                      for low, high in items])
    merged = []
    for low, high in ordered:
        if merged and low <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], high))
        else:
            merged.append((low, high))
    return [(None if lo == -np.inf else lo, None if hi == np.inf else hi) for lo, hi in merged]


@dataclass
class CrossingResult:
    sets: np.ndarray
    points: np.ndarray
    slopes: np.ndarray
    valid: np.ndarray
    localized: np.ndarray
    line_compatible: np.ndarray
    slope_supported: np.ndarray
    possible_references: np.ndarray


def evaluate(inputs, x, rule, weighting, radius_index=0):
    fitted, line, loss = fit_line(inputs, x, weighting)
    basis, margins = make_targets(inputs, rule)
    base = inputs.means @ basis.T
    selected = base.argmin(-1)
    selected_gap = np.take_along_axis(base-margins, selected[..., None], -1)[..., 0] - fitted[..., 0]
    slope = fitted[..., 1]
    supported = np.abs(slope) > 1e-10
    point = np.divide(selected_gap, slope, out=np.full_like(slope, np.nan), where=supported & inputs.available)
    if inputs.radii is None:
        return point, slope
    cutoff = inputs.radii[..., radius_index]
    compatible = inputs.available & (loss <= cutoff)
    cells = inputs.means.shape[:-1]
    sets = np.empty(cells, dtype=object)
    localized = np.zeros(cells, dtype=bool)
    positive = np.zeros(cells, dtype=bool)
    n_refs = np.zeros(cells, dtype=int)
    for index in zip(*np.where(inputs.available)):
        y = fitted[index]
        rad = cutoff[index]
        cov = inputs.covariance[index]
        projection = np.pad(line[index], [(0, 0), (0, cov.shape[-1]-5)])
        slope_var = projection[1] @ cov @ projection[1]
        positive[index] = y[1] > np.sqrt(rad*slope_var)
        reference_se = np.sqrt(np.einsum("ij,jk,ik->i", basis, cov, basis)*rad)
        plausible = base[index]-reference_se <= (base[index]+reference_se).min()
        candidates = []
        for j in np.flatnonzero(plausible):
            gap = base[index][j] - margins[index][j] - y[0]
            joint = np.stack((basis[j]-projection[0], projection[1]))
            candidates.extend(ratio_intervals(gap, y[1], joint @ cov @ joint.T, rad))
        permitted = merge_sets(candidates)
        sets[index] = permitted
        n_refs[index] = plausible.sum()
        bounded = (permitted and all(lo is not None and hi is not None and 0 < lo <= hi < 1
                                     for lo, hi in permitted))
        localized[index] = bool(bounded and compatible[index] and positive[index])
    return CrossingResult(sets, point, slope, inputs.available, localized, compatible, positive, n_refs)


def score_folds(inputs, distance):
    x, grid = make_grid(distance)
    mean, cov = inputs.means[..., :5], inputs.covariance[..., :5, :5]
    complete = inputs.available[..., :4].all(-1)
    mask = np.broadcast_to(complete[..., None], mean[..., :4, 0].shape)
    errors = {name: [] for name in (*REFERENCES, "linear_equal_weight")}
    for held in range(len(x)):
        train = np.delete(np.arange(len(x)), held)
        fit = KnotFit(distance, x, grid, cov, train)
        _, coef = fit.reference_surface(mean)
        for k, name in enumerate(REFERENCES):
            prediction = fit.reference_predict(mean, k, coef[...,k], held)
            errors[name].append(np.square(prediction[..., :4]-mean[..., :4, held])[mask])
        design = np.column_stack((np.ones_like(x), x))
        prediction = (mean[...,train] @ np.linalg.pinv(design[train]).T) @ design[held]
        errors["linear_equal_weight"].append(np.square(prediction[..., :4]-mean[..., :4, held])[mask])
    return {k: float(np.sqrt(np.mean(v))) for k,v in errors.items()}


def cm_from_normal(z, distance):
    return None if z is None else float(distance[0]+z*np.ptp(distance))


def data_rows(singles, joint, ids, distance, tags):
    rows, contrasts = [], []
    for i, pid in enumerate(ids):
        case = dict(tags, participant=pid)
        for j, cell in enumerate(SUMMARY_LABELS):
            idx = i,j
            row = dict(case, cell=cell)
            if not singles.valid[idx]:
                rows.append(dict(row, status="variance_unavailable"))
                continue
            points = singles.sets[idx]
            rows.append(dict(
                row, status="localized" if singles.localized[idx] else "unresolved",
                point_cm=cm_from_normal(singles.points[idx], distance) if np.isfinite(singles.points[idx]) else None,
                slope_ms_per_range=singles.slopes[idx],
                line_compatible=bool(singles.line_compatible[idx]),
                positive_slope_supported=bool(singles.slope_supported[idx]),
                plausible_references=int(singles.possible_references[idx]),
                inside_point=bool(0 < singles.points[idx] < 1),
                unbounded_set=any(a is None or b is None for a,b in points),
                location_set_cm=json.dumps([[cm_from_normal(a, distance),cm_from_normal(b, distance)] for a,b in points]),
            ))
        for name, weights in zip(EFFECT_NAMES, EFFECT_WEIGHTS):
            active = np.flatnonzero(weights)
            contrast = dict(case, effect=name)
            if not joint.valid[i, active].all():
                contrasts.append(dict(contrast, status="variance_unavailable"))
                continue
            locations = joint.sets[i, active]
            lows, highs = [], []
            if all(len(u) for u in locations):
                for weight, pieces in zip(weights[active], locations):
                    low, high = pieces[0][0], pieces[-1][1]
                    a, b = (low, high) if weight > 0 else (high, low)
                    lows.append(-np.inf if a is None else a*weight)
                    highs.append(np.inf if b is None else b*weight)
            low = float(sum(lows)*np.ptp(distance)) if len(lows) and np.isfinite(lows).all() else None
            high = float(sum(highs)*np.ptp(distance)) if len(highs) and np.isfinite(highs).all() else None
            effect = joint.points[i, active] @ weights[active]
            contrasts.append(dict(
                contrast, status="localized" if joint.localized[i, active].all() else "unresolved",
                point_cm=effect*np.ptp(distance) if np.isfinite(effect) else None,
                conditional_envelope_low_cm=low, conditional_envelope_high_cm=high,
                any_empty=not all(len(u) for u in locations),
                any_unbounded=any(a is None or b is None for pieces in locations for a,b in pieces),
            ))
    return rows, contrasts


def refit_records(points, slopes, ids, distance, rule, level):
    shifted = distance[0]+points*np.ptp(distance)
    rows = []
    for i, pid in enumerate(ids):
        for j, name in enumerate(SUMMARY_LABELS):
            finite = np.isfinite(shifted[:,i,j])
            accepted = finite & (slopes[:,i,j] > 0)
            values = shifted[finite,i,j]
            q = np.quantile(values, [.025,.5,.975]) if values.size else (None,None,None)
            rows.append(dict(rule=rule, level=level, participant=pid, cell=name, draws=len(points),
                             finite=int(finite.sum()), positive_slope=int(accepted.sum()),
                             within_design=int((accepted & (points[:,i,j]>0) & (points[:,i,j]<1)).sum()),
                             finite_quantile025_cm=q[0], finite_median_cm=q[1], finite_quantile975_cm=q[2]))
    return rows


def boot(at, baseline, ids, distance):
    rng = np.random.default_rng(SEED)
    x, _ = make_grid(distance)
    rules = {rule: {"people": [], "group": []} for rule in RULES}
    for _ in range(BOOTSTRAPS):
        sa, sb = resample_trials(at, rng), resample_trials(baseline, rng)
        pp = rng.integers(0, len(at), len(at))
        for rule in RULES:
            row = rules[rule]
            inputs = JointInputs.individual(*primitive(sa, sb, rule), radius=False)
            row["people"].append(evaluate(inputs, x, rule, "gls"))
            means = primitive(at[pp], baseline[pp], rule)[0]
            group = JointInputs.group(means[None, ...], radius=False)
            row["group"].append(evaluate(group, x, rule, "gls"))
    reports = []
    for rule, draws in rules.items():
        for level, samples in draws.items():
            point, slope = (np.stack(values) for values in zip(*samples))
            labels = ids if level == "people" else ["equal_participant_group"]
            reports.extend(refit_records(point, slope, labels, distance, rule, level))
    return reports


def sim_inputs(at, baseline, x, rng):
    """Generate retained trial arrays on the observed masks for all three scenarios."""
    at_sd = np.nanstd(at, axis=-1, ddof=1)
    pooled_sd = np.nanstd(baseline.reshape(*baseline.shape[:-2], -1), axis=-1, ddof=1)
    _, baseline_var, baseline_df = moments(baseline)
    b_sd = np.sqrt(baseline_var*(baseline_df+1))
    b_sd = np.where(np.isfinite(b_sd), b_sd, pooled_sd[..., None])
    b_mean = np.broadcast_to(650., baseline.shape[:-1])
    known_scenarios = (
        ("flat", 0., np.full(4, np.nan)),
        ("shallow_outside", 20., np.full(4, -.5)),
        ("steep_shift", 180., np.array([.36, .42, .50, .56])),
    )
    for name, slope, trial_crossing in known_scenarios:
        truth = np.broadcast_to(650+slope*(x-np.nan_to_num(trial_crossing[...,None])), at.shape[:-1]).copy()
        if name == "flat":
            truth += 30
        for noise_factor in (1., 1.75) if name == "steep_shift" else (1.,):
            at_obs = truth[..., None] + rng.normal(size=(RECOVERY,*at.shape))*at_sd[...,None]
            b_obs = b_mean[..., None] + rng.normal(size=(RECOVERY,*baseline.shape))*b_sd[...,None]*noise_factor
            yield name, noise_factor, truth, at_obs, b_obs


def in_set(z, limits):
    return any((lo is None or lo <= z) and (hi is None or z <= hi) for lo,hi in limits)


def assess_recovery(inputs, reference, true_line, x, distance, rule):
    c = evaluate(inputs, x, rule, "gls")
    joint = evaluate(inputs, x, rule, "gls", 1)
    _, margin = make_targets(inputs, rule)
    observed_choice = inputs.means[...,5:].argmin(-1) if rule == "fastest_delay_lower95" else np.zeros(
        margin.shape[:-1], dtype=int)
    margin = np.take_along_axis(margin, observed_choice[..., None], -1)[...,0]
    base = 0. if rule == "same_label_zero" else reference
    intercept = true_line[...,0]-(reference if rule == "same_label_zero" else 0.)
    slope = true_line[...,1]
    true_value = np.divide(base-margin-intercept, slope,
                           out=np.full_like(margin, np.nan), where=np.abs(slope)>1e-10)
    inside = (true_value > 0) & (true_value < 1) & (slope > 0)
    included = np.zeros_like(c.valid)
    included_joint = np.zeros_like(c.valid)
    for ij in zip(*np.where(c.valid & np.isfinite(true_value))):
        included[ij] = in_set(true_value[ij], c.sets[ij])
        included_joint[ij] = in_set(true_value[ij], joint.sets[ij])
    size = np.ptp(distance)
    points = c.points[..., :4]
    q = (true_value[..., :4] @ W[0])*size
    error = (points @ W[0])*size-q
    finite_effect = np.isfinite(error)
    valid_cell = c.valid[..., :4]
    known = np.isfinite(true_value[..., :4]) & valid_cell
    missing = valid_cell & ~inside[..., :4]
    stable = joint.localized[..., :4].all(-1) & included_joint[..., :4].all(-1)
    report = dict(
        phase_cell_coverage=float(included[..., :4][known].mean()) if known.any() else None,
        joint_coverage=float(included_joint[..., :4].all(-1)[known.all(-1)].mean()) if known.all(-1).any() else None,
        noiseless_target_inside=float(inside[..., :4][valid_cell].mean()),
        false_localization_when_no_design_crossing=float(c.localized[...,:4][missing].mean()) if missing.any() else None,
        correct_localization_of_inside=float((c.localized & included)[...,:4][inside[...,:4]].mean()) if inside[...,:4].any() else None,
        mean_margin_ms=float(np.nanmean(margin[..., :4])),
        median_condition_absolute_error_cm=float(np.median(np.abs(error[finite_effect]))) if finite_effect.any() else None,
        condition_effect_jointly_localized_and_contains_all_locations=float(stable.mean()) if np.isfinite(q).any() else None,
    )
    return report


def recovery(at, baseline, distance):
    x, _ = make_grid(distance)
    design = np.column_stack((np.ones_like(x), x))
    rng = np.random.default_rng(SEED+1)
    scenarios = {}
    for name, noise_factor, rt, av, bv in sim_inputs(at, baseline, x, rng):
        desc = f"{name}_baseline_sd_x{noise_factor:g}"
        summaries = {}
        for rule in RULES:
            available = primitive(av, bv, rule)
            # The group calibration uses matched between-person covariance,
            # including the observed dependence of AT and baseline means.
            corrected = rule == "same_label_zero"
            observed = primitive(at, baseline, "fastest_delay_lower95" if corrected else rule)[0]
            width = observed.shape[-1]
            across = np.cov(observed.reshape(len(at), -1).T)
            center = np.concatenate((rt,np.full((*rt.shape[:-1], width-5),650.)), axis=-1)
            perturbation = rng.multivariate_normal(np.zeros(across.shape[0]),across,size=(RECOVERY,len(at)))
            # Vary baseline measurement noise while leaving the generating AT line fixed.
            shaped = perturbation.reshape(RECOVERY,len(at),4,width)
            shaped[...,5:] *= noise_factor
            obs = center+shaped
            g = JointInputs.group(obs[...,:5]-obs[...,5:] if corrected else obs)
            p = JointInputs.individual(*available)
            coefficients = phase_average(rt) @ np.linalg.pinv(design).T
            summaries[rule] = dict(
                individuals=assess_recovery(p, 650., coefficients, x, distance, rule),
                group=assess_recovery(g, 650., coefficients.mean(0), x, distance, rule),
            )
        scenarios[desc] = summaries
    return scenarios


def numerical_checks():
    x, _ = make_grid(DISTANCES["registered"])
    rng = np.random.default_rng(SEED)
    design = np.column_stack((np.ones_like(x), x))
    a = rng.normal(size=(6,6))
    v = (a @ a.T)[None,...]
    artificial = np.r_[610+100*x, 650.][None,:]
    joint = JointInputs(artificial, v, np.full_like(artificial,40.), np.array([[4.,5.]]), np.array([True]))
    fit, projection, loss = fit_line(joint, x, "gls")
    np.testing.assert_allclose(fit[0], [610.,100.])
    assert loss[0] < 1e-10
    actual = evaluate(joint, x, "pooled_mean", "gls")
    assert actual.localized[0]
    np.testing.assert_allclose(actual.points[0], .4)
    shifted = JointInputs(artificial+200, v, joint.degrees, joint.radii, joint.available)
    np.testing.assert_allclose(evaluate(shifted, x, "pooled_mean", "gls").points, actual.points)
    target = np.r_[np.linspace(560,690,5),650.].reshape(1,-1)
    noisy = JointInputs(target, v, joint.degrees, joint.radii, joint.available)
    fit, _, _ = fit_line(noisy, x, "gls")
    direct = np.linalg.solve(design.T @ np.linalg.solve(v[0,:5,:5], design),
                             design.T @ np.linalg.solve(v[0,:5,:5], target[0,:5]))
    np.testing.assert_allclose(fit[0], direct)
    assert merge_sets([(None,0.),(-1.,1.),(1.1,None)]) == [(None,1.),(1.1,None)]
    return "Known crossing recovery, paired translation invariance, direct GLS and disconnected interval union."


def run():
    diagnostics = numerical_checks()
    ids, at, baseline, audit = load_data()
    primary = cohort_mask(ids,"primary40")
    rows, contrasts, predictions = [], [], {}
    for rule in RULES:
        data = primitive(at, baseline, rule)
        person = JointInputs.individual(*[v[primary] for v in data])
        for axis, distance in DISTANCES.items():
            x, _ = make_grid(distance)
            for weight in ("gls", "equal"):
                if weight == "equal" and axis != "registered":
                    continue
                settings = dict(rule=rule, axis=axis, weighting=weight)
                ps = evaluate(person, x, rule, weight)
                pj = evaluate(person, x, rule, weight, 1)
                p, r = data_rows(ps, pj, ids[primary], distance, dict(settings, cohort="primary40"))
                rows.extend(p)
                contrasts.extend(r)
                for cohort in COHORTS:
                    mask = cohort_mask(ids,cohort)
                    group = JointInputs.group(data[0][mask][None,...])
                    gs = evaluate(group, x, rule, weight)
                    gj = evaluate(group, x, rule, weight, 1)
                    p, r = data_rows(gs, gj, ["equal_participant_group"], distance, dict(settings,cohort=cohort))
                    rows.extend(p)
                    contrasts.extend(r)
                    if cohort == "primary40" and weight == "gls" and rule in ("pooled_mean","same_label_zero"):
                        predictions[axis+"_"+rule] = dict(individual=score_folds(person,distance),group=score_folds(group,distance))
    distance = DISTANCES["registered"]
    b_rows = boot(at[primary],baseline[primary],ids[primary],distance)
    sim = recovery(at[primary],baseline[primary],distance)
    details = dict(input=audit, seed=SEED, refits=BOOTSTRAPS, recovery_draws=RECOVERY,
                   fixtures=diagnostics, prediction_rmse_ms=predictions, recovery=sim)
    paths = [OUT / f"baseline_crossing_{name}.csv" for name in ("profiles","contrasts","refits")]
    for path, contents in zip(paths,(rows,contrasts,b_rows)):
        write_csv(path,contents)
    dependencies = ["crossing_ratio.py","profile.py","profile_grid.py","knot_grid.py","screen.py"]
    covered = [Path(__file__), *(Path(__file__).with_name(p) for p in dependencies),
               ROOT/"analysis/baseline_effects/baseline_effects.py", OUT/"BASELINE_CROSSING_SPECIFICATION.md", *paths]
    details["sha256"] = {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in covered}
    (OUT/"baseline_crossing_results.json").write_text(json.dumps(details,indent=2,allow_nan=False)+"\n",
                                                    encoding="utf-8",newline="\n")
    print(f"Wrote {len(rows)} boundary profiles, {len(contrasts)} contrasts and {len(b_rows)} refit summaries.")


if __name__ == "__main__":
    run()
