"""Project monotone mean response bands into threshold sets for Study 5."""

import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.optimize import isotonic_regression
from scipy.special import expit

from knot_grid import KnotFit, make_grid
from profile import COHORTS, group_data, prepare
from profile_grid import REFERENCES, diag_cov
from screen import (DISTANCES, EFFECTS, OUT, ROOT, SUMMARY_LABELS, W, cohort_mask, load_data,
                    phase_profiles, write_csv)
from threshold_bands import MeanProbeInputs, group_bands
from threshold_sets import OrderedBand

ALPHA = .05
TARGETS = {"observed_half": None, "0ms": 0, "20ms": -20, "40ms": -40}
SEED = 20261119
REPLICATES = 96


def threshold_set(band, target):
    return band.midpoint() if target is None else band.crosses(target)


def build_rows(singles, simultaneous, targets, ids, distance, tags):
    rows, contrasts = [], []
    for name, target in targets.items():
        own = singles["at"] if target is None else singles["baseline"]
        multi = simultaneous["at"] if target is None else simultaneous["baseline"]
        band = OrderedBand.from_limits(*own[:2])
        joint = OrderedBand.from_limits(*multi[:2])
        est = threshold_set(band, target)
        sim = threshold_set(joint, target)
        for i, pid in enumerate(ids):
            row = dict(tags, participant=pid, target=name)
            for j, cell in enumerate(SUMMARY_LABELS):
                idx = i,j
                record = dict(row, cell=cell)
                if not own[2][idx]:
                    rows.append(dict(record, status="variance_unavailable"))
                    continue
                if not band.feasible[idx]:
                    rows.append(dict(record, status="monotone_incompatible"))
                    continue
                state = "localized_crossing" if est.localized[idx] else "unresolved"
                rows.append(dict(
                    record, status=state, intervals_cm=json.dumps(est.pieces(distance, idx)),
                    left_censored=bool(est.left[idx]), right_censored=bool(est.right[idx]),
                    plateau_possible=bool(est.plateau[idx]), flat_compatible=bool(band.flat[idx]),
                    no_rise_possible=bool(est.no_rise[idx]),
                ))
            for j, (effect, weights) in enumerate(zip((*EFFECTS, "Condition of equal-phase profiles"),
                                                      (*W, np.array([-1., 1.])))):
                subset = slice(0,4) if j < len(EFFECTS) else slice(4,6)
                active = np.flatnonzero(weights)
                index = np.arange(len(SUMMARY_LABELS))[subset][active]
                relative = weights[active]
                record = dict(row, effect=effect)
                if not multi[2][i,index].all():
                    contrasts.append(dict(record, status="variance_unavailable"))
                    continue
                if not joint.feasible[i,index].all():
                    contrasts.append(dict(record, status="monotone_incompatible"))
                    continue
                pieces = [sim.pieces(distance, (i,j)) for j in index]
                conditional = None
                if all(pieces):
                    extrema = np.array([[seq[0][0], seq[-1][-1]] for seq in pieces])
                    scaled = extrema*relative[:, None]
                    conditional = [scaled.min(-1).sum(), scaled.max(-1).sum()]
                resolved = sim.localized[i,index].all()
                contrasts.append(dict(
                    record, status="localized_crossing_contrast" if resolved else "unresolved",
                    conditional_within_range_lo_cm=conditional[0] if conditional else None,
                    conditional_within_range_hi_cm=conditional[1] if conditional else None,
                    no_rise_possible=bool(sim.no_rise[i,index].any()),
                    plateau_possible=bool(sim.plateau[i,index].any()),
                    censoring_possible=bool((sim.left[i,index] | sim.right[i,index]).any()),
                ))
    return rows, contrasts


def prediction(y, covariance, distance):
    x, grid = make_grid(distance)
    errors = {name: [] for name in (*REFERENCES, "isotonic_interval_linear")}
    for held in range(len(x)):
        train = np.delete(np.arange(len(x)), held)
        fit = KnotFit(distance, x, grid, covariance, train)
        _, coef = fit.reference_surface(y)
        for i, model in enumerate(REFERENCES):
            pred = fit.reference_predict(y, i, coef[..., i], held)
            errors[model].append(np.square(pred-y[..., held]))
        diagonals = np.diagonal(covariance, axis1=-2, axis2=-1).reshape(-1, len(x))
        predictions = []
        for profile, var in zip(y.reshape(-1, len(x)), diagonals):
            order = isotonic_regression(profile[train], weights=1/var[train]).x
            predictions.append(np.interp(x[held], x[train], order))
        errors["isotonic_interval_linear"].append(np.square(predictions-y[..., held].ravel()))
    return {model: float(np.sqrt(np.mean(values))) for model, values in errors.items()}


def generators(people, x):
    shape = (people,4,len(x))
    yield "flat_at_target", np.zeros(shape)
    yield "flat_below_target", np.full(shape, -90.)
    yield "linear", np.broadcast_to(-80+160*x, shape)
    centers = np.array([.37,.43,.50,.59])[:, None]
    offsets = np.linspace(-.08,.08,people)[:, None,None]
    hinge = np.clip((x-centers-offsets)/.30+.5, 0, 1)
    yield "strong_clipped_ramp", 160*hinge-110
    centers = np.array([.51,.58,.65,.72])[:, None]
    yield "strong_logistic", 180*expit((x-centers+offsets)/.09)-100


def recovery_metrics(bands, joint_bands, truth, target, distance):
    est = threshold_set(OrderedBand.from_limits(*bands[:2]), target)
    joint = threshold_set(OrderedBand.from_limits(*joint_bands[:2]), target)
    truth_set = threshold_set(OrderedBand.from_limits(truth, truth), target)
    has_crossing = truth_set.intervals.any(-1) & ~truth_set.plateau
    threshold = (truth[..., :1] + truth[..., -1:])/2 if target is None else target
    part = ((truth[..., :-1] <= threshold) & (truth[..., 1:] >= threshold)).argmax(-1)
    covered_interval = np.take_along_axis(est.intervals, np.broadcast_to(part, est.intervals.shape[:-1])[..., None], -1)[...,0]
    correct = covered_interval & has_crossing & est.localized
    widths = est.intervals @ np.diff(distance)
    joint_coverage = ((~truth_set.intervals | joint.intervals).all(-1)
                      & (~truth_set.no_rise | joint.no_rise)
                      & (~truth_set.plateau | joint.plateau)
                      & (~truth_set.left | joint.left)
                      & (~truth_set.right | joint.right))
    phase_joint_coverage = joint_coverage[..., :4].all(-1)
    known = np.broadcast_to(has_crossing, widths.shape)
    factor = {
        "true_crossing_fraction": float(has_crossing.mean()),
        "phase_joint_state_coverage": float(phase_joint_coverage.mean()),
        "localized_fraction": float(est.localized.mean()),
        "wrong_localization_fraction_when_no_unique_crossing": float(est.localized[~known].mean()) if (~known).any() else None,
        "correct_localization_fraction_when_unique": float(correct[known].mean()) if known.any() else None,
        "mean_measured_width_cm_when_unique": float(widths[known].mean()) if known.any() else None,
    }
    if not has_crossing[..., :4].all(-1).any():
        factor["condition_effect"] = None
        return factor
    z = np.broadcast_to(threshold, truth.shape[:-1]+(1,))
    below = np.take_along_axis(truth, part[...,None], -1)[...,0]
    above = np.take_along_axis(truth, part[...,None]+1, -1)[...,0]
    fraction = np.divide(z[...,0]-below, above-below, out=np.zeros_like(below), where=above>below)
    crossing = distance[part] + fraction*np.diff(distance)[part]
    true_eff = crossing[..., :4] @ W[0]
    occupied = joint.intervals[..., :4, :]
    lower = np.where(occupied, distance[:-1], np.inf).min(-1)
    upper = np.where(occupied, distance[1:], -np.inf).max(-1)
    support = occupied.any(-1).all(-1)
    lo = np.where(W[0]>0, lower, upper) @ W[0]
    hi = np.where(W[0]>0, upper, lower) @ W[0]
    known_effect = np.broadcast_to(has_crossing[..., :4].all(-1), support.shape)
    contains = support & (lo <= true_eff) & (true_eff <= hi)
    resolved = joint.localized[..., :4].all(-1)
    factor["condition_effect"] = dict(
        true_shift_min_cm=float(true_eff[has_crossing[..., :4].all(-1)].min()),
        true_shift_max_cm=float(true_eff[has_crossing[..., :4].all(-1)].max()),
        joint_contains_truth_fraction=float(contains[known_effect].mean()),
        jointly_localized_and_contains_truth_fraction=float((resolved & contains)[known_effect].mean()),
    )
    return factor


def recovery(at, baseline, distance):
    rng = np.random.default_rng(SEED)
    x, _ = make_grid(distance)
    actual = MeanProbeInputs.from_trials(at, baseline, "pooled_cp")
    person_count, cells, probes = actual.at[0].shape
    at_shape = (REPLICATES, person_count, cells, probes)
    baseline_shape = (*at_shape[:-1], 1)
    joint_means = np.column_stack([actual.at[0].reshape(person_count, -1), actual.baseline[0][..., 0]])
    group_covariance = np.cov(joint_means.T)
    out = {}

    def sampled(truth, template, shape):
        _, var, df = template
        values = truth+rng.normal(size=shape)*np.sqrt(var)
        variance = var*rng.chisquare(df, size=shape)/df
        return values, variance, df

    for scenario, truth in generators(person_count, x):
        sample_at = sampled(650+truth, actual.at, at_shape)
        sample_b = sampled(650., actual.baseline, baseline_shape)
        group_draws = rng.multivariate_normal(np.zeros(cells*(probes+1)), group_covariance,
                                              size=(REPLICATES, person_count))
        raw_group = 650+truth+group_draws[..., :cells*probes].reshape(at_shape)
        b_group = 650+group_draws[..., cells*probes:].reshape(baseline_shape)
        actual_profiles = phase_profiles(truth)
        scenarios = {}
        for name, target in TARGETS.items():
            person = MeanProbeInputs(sample_at, None if target is None else sample_b)
            person_bands = person.individual_bands(ALPHA)
            person_joint = person.individual_bands(ALPHA/4)
            group = raw_group if target is None else raw_group - b_group
            group_summary = group_bands(group, ALPHA)
            group_joint = group_bands(group, ALPHA/4)
            scenarios[name] = dict(
                individuals=recovery_metrics(person_bands, person_joint, actual_profiles, target, distance),
                group=recovery_metrics(group_summary, group_joint, actual_profiles.mean(0), target, distance),
            )
        out[scenario] = scenarios
    return out


def run():
    ids, at, baseline, audit = load_data()
    primary = cohort_mask(ids, "primary40")
    rows, contrasts, predictive = [], [], {}
    for correction in ("pooled_cp", "same_label"):
        signed = MeanProbeInputs.from_trials(at, baseline, correction)
        half = MeanProbeInputs.from_trials(at, baseline, "raw") if correction == "pooled_cp" else signed
        person = {"at": half, "baseline": signed}
        singles = {label: tuple(t[primary] for t in inp.individual_bands(ALPHA)) for label, inp in person.items()}
        joint = {label: tuple(t[primary] for t in inp.individual_bands(ALPHA/4)) for label, inp in person.items()}
        mu, var, _ = prepare(at, baseline, correction)
        usable = (np.isfinite(var) & (var>0)).all(axis=(-2,-1)) & primary
        for axis, distance in DISTANCES.items():
            labels = dict(axis=axis, correction=correction)
            prof, effects = build_rows(singles, joint, TARGETS, ids[primary], distance, dict(labels, cohort="primary40"))
            rows.extend(prof)
            contrasts.extend(effects)
            scores = {"individual_profiles": prediction(mu[usable], diag_cov(var[usable]), distance)}
            for cohort in COHORTS:
                keep = cohort_mask(ids, cohort)
                def bands(alpha):
                    return {label: tuple(t[None, ...] for t in group_bands(inp.center[keep], alpha))
                            for label, inp in person.items()}
                prof, effects = build_rows(bands(ALPHA), bands(ALPHA/4), TARGETS,
                                           ["equal_participant_group"], distance, dict(labels, cohort=cohort))
                rows.extend(prof)
                contrasts.extend(effects)
                if cohort == "primary40":
                    group, cov = group_data(mu[keep])
                    scores["group_profiles"] = prediction(group, cov, distance)
            predictive[axis+"_"+correction] = scores
    details = dict(seed=SEED, replicates=REPLICATES, input=audit, prediction_rmse_ms=predictive,
                   recovery=recovery(at[primary], baseline[primary], DISTANCES["registered"]))
    candidates, effects = OUT/"threshold_profiles.csv", OUT/"threshold_contrasts.csv"
    write_csv(candidates, rows)
    write_csv(effects, contrasts)
    shared_code = [Path(__file__).with_name(name) for name in (
        "threshold_sets.py", "threshold_bands.py", "knot_grid.py", "profile.py", "profile_grid.py", "screen.py")]
    paths = [Path(__file__), *shared_code, ROOT/"analysis/baseline_effects/baseline_effects.py",
             OUT/"THRESHOLD_SPECIFICATION.md", candidates, effects]
    details["sha256"] = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    (OUT/"threshold_results.json").write_text(json.dumps(details, indent=2, allow_nan=False)+"\n",
                                             encoding="utf-8", newline="\n")
    print(f"Wrote {len(rows)} threshold sets and {len(contrasts)} contrasts.")


if __name__ == "__main__":
    run()
