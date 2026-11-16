"""Run midpoint compatibility, shared-shape fits and matched recovery."""

import hashlib
import json
import platform
from functools import lru_cache
from pathlib import Path

import numpy as np
import scipy
from scipy import stats

from profile_grid import (MODELS, REFERENCES, ShapeGrid, WeightedBasis, contrast_range,
                          diag_cov, intervals, joint_shapes, predict_folds, reduced_choices)
from screen import DISTANCES, OUT, ROOT, SUMMARY_LABELS, cohort_mask, load_data, phase_profiles, write_csv
from baseline_effects import EFFECTS, W

SEED = 20261117
REPLICATES = 96
CALIBRATION = 16_384
ALPHA = .05
N_CELLS = 4
COHORTS = ("primary40", "exclude_P011", "exclude_P033")


def moments(values):
    count = np.isfinite(values).sum(-1)
    if (count == 0).any():
        raise ValueError("The fixed release must contain a response at each modelled probe.")
    means = np.nanmean(values, axis=-1)
    squares = np.nansum(np.square(values - means[..., None]), axis=-1)
    denom = (count-1)*count
    variance = np.divide(squares, denom, out=np.full_like(means, np.nan), where=denom > 0)
    return means, variance, count-1


def prepare(at, baseline, correction):
    mean, variance, df = moments(at)
    if correction == "same_label":
        b_mean, b_var, b_df = moments(baseline)
        total = variance + b_var
        safe = np.where(b_df > 0, b_df, np.nan)
        df = total**2 / (variance**2 / df + b_var**2 / safe)
        mean, variance = mean - b_mean, total
    return mean, variance, df


def variance_six(variance):
    phase_pairs = variance.reshape(-1, 2, 2, 5)
    return np.concatenate((variance, phase_pairs.sum(-2)/4), axis=1)


@lru_cache(maxsize=None)
def envelope(degrees):
    df = np.asarray(degrees)
    if (df <= 0).any() or not np.isfinite(df).all():
        raise ValueError("Every bin needs an estimated positive variance.")
    rng = np.random.default_rng(SEED)
    t = rng.standard_t(df, size=(CALIBRATION, len(df)))
    levels = np.quantile(np.square(t).sum(-1), [1-ALPHA, 1-ALPHA/N_CELLS], method="higher")
    return tuple(levels)


def person_cutoffs(df):
    flat_df = np.concatenate((df.reshape(-1, 4, 1, 5).repeat(2, axis=2),
                              df.reshape(-1, 2, 2, 5)), axis=1).reshape(-1, 6, 10)
    thresholds = np.full((*flat_df.shape[:-1], 2), np.nan)
    for person in range(len(df)):
        for cell in range(6):
            degrees = flat_df[person, cell, :5 if cell < 4 else 10]
            if np.isfinite(degrees).all() and (degrees > 0).all():
                thresholds[person, cell] = envelope(tuple(np.sort(degrees)))
    return thresholds


def group_cutoffs(observations):
    dim = 4
    p = [1-ALPHA, 1-ALPHA/N_CELLS]
    values = dim*(observations-1)/(observations-dim)*stats.f.ppf(p, dim, observations-dim)
    return np.broadcast_to(values, (1, 6, 2))


def group_data(people):
    cov = np.einsum("nci,ncj->cij", people-people.mean(0), people-people.mean(0))
    return people.mean(0, keepdims=True), cov[None, ...] / (len(people)*(len(people)-1))


def shape_loss(means, cov, grid):
    grid_shape = (len(grid.normalized_midpoint), len(grid.relative_width))
    engine = WeightedBasis(cov, grid.shapes.reshape(-1, 5))
    loss, amp = engine.surface(means)
    return loss.reshape(*means.shape[:-1], *grid_shape), amp.reshape(*means.shape[:-1], *grid_shape)


def profile_rows(means, cov, cutoffs, ids, grid, labels):
    loss, amplitude = shape_loss(means, cov, grid)
    reference, _ = WeightedBasis(cov, grid.reference_shapes).surface(means)
    base = grid.design_subset
    narrowed = loss[..., base, :]
    relative = narrowed + 1e-10*((grid.normalized_midpoint[base,None]-.5)**2+np.log(grid.relative_width*6)**2)
    best_m, best_w = np.divmod(relative.reshape(*relative.shape[:-2], -1).argmin(-1), len(grid.relative_width))
    summary = []
    for i, pid in enumerate(ids):
        for c, name in enumerate(SUMMARY_LABELS):
            record = {**labels, "participant": pid, "cell": name}
            if not np.isfinite(cutoffs[i,c,0]):
                summary.append(dict(**record, status="variance_unavailable"))
                continue
            supported = (loss[i,c] <= cutoffs[i,c,0]).any(-1)
            inside = (grid.midpoints > grid.distance[0]) & (grid.midpoints < grid.distance[-1])
            null_ok = reference[i,c] <= cutoffs[i,c,0]
            set_ok = supported.any()
            resolved = set_ok and not supported[~inside].any() and not null_ok.any()
            summary.append(dict(
                **record, status="bounded_transition" if resolved else "unresolved",
                best_midpoint_cm=grid.midpoints[base][best_m[i,c]],
                best_width_cm=np.ptp(grid.distance)*grid.relative_width[best_w[i,c]],
                best_span_ms=amplitude[i,c,base,:][best_m[i,c],best_w[i,c]],
                cutoff=cutoffs[i,c,0], profile_min=loss[i,c].min(),
                evaluated_points=len(supported), compatible_points=int(supported.sum()),
                touches_expanded_grid=bool(supported[0] or supported[-1]),
                both_outside_flanks=bool(supported[0] and supported[-1]),
                profile_set_cm=json.dumps(intervals(supported, grid.midpoints)),
                compatible_references=" ".join(n for n, flag in zip(REFERENCES, null_ok) if flag),
                reference_losses=json.dumps(reference[i,c].tolist()),
            ))
    return summary, loss, reference


def joint_rows(loss, reference, cutoffs, ids, grid, labels):
    grid_indices = grid.design_subset
    shapes = loss[..., :4, :, :]
    valid = np.isfinite(cutoffs[:, :4, 1]).all(-1)
    point = reduced_choices(shapes[..., grid_indices, :], grid.normalized_midpoint[grid_indices],
                            grid.relative_width)
    compatible = shapes <= cutoffs[:, :4, 1, None, None]
    boundary_free = (reference[:, :4, :] <= cutoffs[:, :4, 1, None]).any(-1)
    outputs = []
    for model, (m, w) in point.items():
        permitted = joint_shapes(compatible, model)
        for i, pid in enumerate(ids):
            block = permitted[i]
            profile_ok = block.any(axis=(-2, -1)).all()
            selected = grid.midpoints[grid_indices][m[i]]
            for weights, effect in zip(W, EFFECTS):
                record = {**labels, "participant": pid, "model": model, "effect": effect}
                if not valid[i]:
                    outputs.append(dict(**record, status="variance_unavailable"))
                    continue
                conditional = contrast_range(block, grid.midpoints, weights, model)
                active = weights != 0
                location = block[active].any(-1)
                outside = location[:, (grid.midpoints <= grid.distance[0]) | (grid.midpoints >= grid.distance[-1])].any()
                can_flat = boundary_free[i, active].any()
                if not profile_ok:
                    status = "shared_set_empty"
                elif model in ("shared_midpoint", "shared_both"):
                    status = "zero_imposed"
                elif can_flat or outside:
                    status = "unresolved"
                else:
                    status = "bounded_transition_contrast"
                outputs.append(dict(
                    **record, status=status, point_cm=float(selected @ weights),
                    conditional_set_lo_cm=conditional[0] if conditional else None,
                    conditional_set_hi_cm=conditional[1] if conditional else None,
                    boundary_free_compatible=bool(can_flat), outside_design_compatible=bool(outside),
                    point_midpoints_cm=json.dumps(selected.tolist()),
                    point_widths_cm=json.dumps((np.ptp(grid.distance)*grid.relative_width[w[i]]).tolist()),
                ))
    return outputs


def diagnostics():
    grid = ShapeGrid.logistic(DISTANCES["registered"])
    q = grid.shapes
    chosen = np.vstack([grid.reference_shapes, q[52,13], q[80,2]])
    values = np.array([597., 612., 650., 631., 679.])
    cov = np.diag([10., 20., 11., 30., 15.]) + 2.3
    engine = WeightedBasis(cov, chosen)
    losses, amplitudes = engine.surface(values)
    whitening = np.linalg.cholesky(cov)
    for idx, basis in enumerate(chosen):
        design = np.stack((np.ones(5), basis), axis=-1)
        y = np.linalg.solve(whitening, values)
        x = np.linalg.solve(whitening, design)
        estimate = np.linalg.lstsq(x, y, rcond=None)[0]
        np.testing.assert_allclose(losses[idx], np.square(y-x@estimate).sum(), atol=2e-9)
        np.testing.assert_allclose(amplitudes[idx], estimate[1], atol=2e-9)
    np.testing.assert_allclose(engine.surface(values+1e3)[0], losses, atol=2e-9)
    midpoint, width, _ = truth_shapes(grid)
    response = q[midpoint, width]
    clean = 650 + 160*response
    surface, _ = shape_loss(clean, np.broadcast_to(cov, (4, 5, 5)), grid)
    result = reduced_choices(surface, grid.normalized_midpoint, grid.relative_width)
    for name in ("free", "shared_width"):
        np.testing.assert_array_equal(result[name][0], midpoint)
        np.testing.assert_array_equal(result[name][1], width)
    grid_fixture = np.zeros((4, 3, 2), dtype=bool)
    grid_fixture[:, :, 0] = np.array([[1,0,1],[0,0,1],[1,1,0],[0,1,1]])
    shared = joint_shapes(grid_fixture, "shared_width")
    assert intervals(shared[0].any(-1), np.array([1., 2., 3.])) == [[1., 1.],[3., 3.]]
    assert contrast_range(shared, np.array([1., 2., 3.]), W[2], "shared_width") == [-2., 2.]
    assert not joint_shapes(grid_fixture, "shared_midpoint").any()
    return "Independent direct GLS, offset invariance, synthetic recovery and disconnected joint-set checks."


def truth_shapes(grid):
    m = np.argmin(np.abs(grid.normalized_midpoint[None, :] - np.array([.40,.475,.55,.70])[:,None]), axis=-1)
    w = int(np.argmin(np.abs(grid.relative_width - 1/6)))
    varied = np.argmin(np.abs(grid.relative_width[None, :] - np.array([.12,.21,.29,.37])[:,None]), axis=-1)
    return m, w, varied


def simulated_scenarios(grid):
    m, w, varied = truth_shapes(grid)
    same = np.full(4, m[0])
    return (
        ("flat", 0, same, np.full(4, w)),
        ("80ms_null", 80, same, np.full(4, w)),
        ("160ms_shared_width_effect", 160, m, np.full(4, w)),
        ("80ms_varying_width_effect", 80, m, varied),
    )


def effect_summary(point, grid, true):
    truth = grid.midpoints[true] @ W.T
    result = {}
    for name, (m, _) in point.items():
        estimates = grid.midpoints[m] @ W.T
        error = estimates-truth
        result[name] = {
            effect: {"bias_cm": float(e.mean()), "rmse_cm": float(np.sqrt(np.square(e).mean()))}
            for effect, e in zip(EFFECTS, np.moveaxis(error, -1, 0))
        }
    return result


def simulate_people(variance, df, cutoffs, grid):
    rng = np.random.default_rng(SEED+1)
    base = grid.design_subset
    shape = grid.shapes
    engine = WeightedBasis(diag_cov(variance), shape[base].reshape(-1, 5))
    summaries = {}
    for label, amp, midpoint, width in simulated_scenarios(grid):
        observed = 650 + amp*shape[midpoint,width] + rng.normal(size=(REPLICATES,*variance.shape))*np.sqrt(variance)
        estimated_variance = variance*rng.chisquare(df, size=observed.shape)/df
        target_basis = shape[midpoint,width]
        result = []
        observed_null = []
        observed_true = []
        for k in range(REPLICATES):
            c = diag_cov(estimated_variance[k])
            fitted = WeightedBasis(c, np.r_[np.zeros((1,5)),target_basis])
            loss, _ = fitted.surface(observed[k])
            fixed = np.take_along_axis(loss[..., 1:], np.arange(4)[None,:,None], -1)[...,0]
            observed_true.append(fixed)
            observed_null.append(loss[...,0])
            loss_known, _ = engine.surface(observed[k])
            result.append(reduced_choices(loss_known.reshape(len(variance),4,base.sum(),-1),
                                          grid.normalized_midpoint[base], grid.relative_width))
        best = {name: tuple(np.stack([row[name][j] for row in result]) + (np.flatnonzero(base)[0] if j==0 else 0)
                            for j in range(2)) for name in MODELS}
        true_loss = np.array(observed_true)
        summaries[label] = dict(
            generator_midpoints_cm=grid.midpoints[midpoint].tolist(),
            generator_widths_cm=(grid.relative_width[width]*np.ptp(grid.distance)).tolist(),
            fixed_true_shape_coverage=float(np.mean(true_loss <= cutoffs[:,:4,0])),
            simultaneous_fixed_true_shape_coverage=float(np.mean((true_loss <= cutoffs[:,:4,1]).all(-1))),
            fraction_flat_compatible=float(np.mean(np.array(observed_null) <= cutoffs[:,:4,0])),
            midpoint_error_by_reduction=None if amp==0 else effect_summary(best, grid, midpoint),
        )
    return summaries


def simulate_group(means, grid):
    rng = np.random.default_rng(SEED+2)
    n = len(means)
    empirical = np.cov(means.reshape(n,20).T)
    index = np.flatnonzero(grid.design_subset)
    q = grid.shapes
    cutoff = group_cutoffs(n)[0,:4,1]
    reports = {}
    for label, amp, midpoint, width in simulated_scenarios(grid):
        target = 650 + amp*q[midpoint,width]
        points, hit = [], []
        for noise in rng.multivariate_normal(np.zeros(20), empirical, size=(REPLICATES,n)):
            synthetic = target + noise.reshape(n,4,5)
            y, cov = group_data(synthetic)
            reference = WeightedBasis(cov, q[midpoint,width])
            test, _ = reference.surface(y)
            hit.append((test[0].diagonal() <= cutoff).all())
            loss, _ = shape_loss(y, cov, grid)
            points.append(reduced_choices(loss[..., index, :], grid.normalized_midpoint[index], grid.relative_width))
        packed = {name: tuple(np.concatenate([row[name][j] for row in points]) + (index[0] if j==0 else 0)
                              for j in range(2)) for name in MODELS}
        reports[label] = dict(simultaneous_fixed_true_shape_coverage=float(np.mean(hit)),
                              midpoint_error_by_reduction=None if amp==0 else effect_summary(packed, grid, midpoint))
    return reports


def run():
    independently_checked = diagnostics()
    ids, at, baseline, audit = load_data()
    rows, contrasts, predictive, span_sensitivity = [], [], {}, {}
    primary = cohort_mask(ids, "primary40")
    mean, var, df = prepare(at, baseline, "pooled_cp")
    b = np.nanmean(baseline, axis=(2,3))
    np.testing.assert_allclose(np.diff(mean, axis=-1), np.diff(mean-b[...,None], axis=-1), atol=1e-12)
    for correction in ("pooled_cp", "same_label"):
        mean, var, df = prepare(at, baseline, correction)
        col = phase_profiles(mean)
        v = variance_six(var[primary])
        real_cov = diag_cov(np.where(np.isfinite(v) & (v>0), v, 1.))
        cutoffs = person_cutoffs(df[primary])
        cutoffs = np.where((np.isfinite(v) & (v>0)).all(-1)[...,None], cutoffs, np.nan)
        usable = np.isfinite(cutoffs[:,:4,0]).all(-1)
        for axis, distance in DISTANCES.items():
            grid = ShapeGrid.logistic(distance)
            labels = dict(axis=axis, correction=correction, cohort="primary40")
            combinations, loss, refs = profile_rows(col[primary], real_cov, cutoffs, ids[primary], grid, labels)
            rows.extend(combinations)
            contrasts.extend(joint_rows(loss, refs, cutoffs, ids[primary], grid, labels))
            validate_scores = predict_folds(col[primary][usable,:4], real_cov[usable,:4], grid)
            predictive[axis+"_"+correction] = dict(individual_units=int(usable.sum()), held_person_cells_rmse_ms=validate_scores)
            for cohort in COHORTS:
                mask = cohort_mask(ids, cohort)
                aggregate, cov = group_data(col[mask])
                radius = group_cutoffs(mask.sum())
                labels = dict(axis=axis, correction=correction, cohort=cohort)
                label = ["equal_participant_group"]
                combinations, loss, refs = profile_rows(aggregate, cov, radius, label, grid, labels)
                rows.extend(combinations)
                contrasts.extend(joint_rows(loss, refs, radius, label, grid, labels))
                if cohort == "primary40":
                    predictive[axis+"_"+correction]["held_group_profile_rmse_ms"] = predict_folds(aggregate[:,:4], cov[:,:4], grid)
                    if correction == "pooled_cp":
                        span_sensitivity[axis] = {
                            str(span): dict(
                                held_person_cells_rmse_ms=predict_folds(col[primary][:,:4], real_cov[:,:4], grid, span),
                                held_group_profile_rmse_ms=predict_folds(aggregate[:,:4], cov[:,:4], grid, span),
                            )
                            for span in (80., 160., 320.)
                        }
    grid = ShapeGrid.logistic(DISTANCES["registered"])
    m, v, df = prepare(at[primary], baseline[primary], "pooled_cp")
    receipts = {
        "seed": SEED, "replicates": REPLICATES, "cutoff_draws": CALIBRATION,
        "input": audit, "diagnostics": independently_checked,
        "registered_recovery_people": simulate_people(v, df, person_cutoffs(df), grid),
        "registered_recovery_group": simulate_group(m, grid),
        "prediction": predictive,
        "posthoc_predictive_span_limits_ms": span_sensitivity,
        "descriptive_mean_of_paired_estimates": summarize_participant_points(contrasts),
        "runtime": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
    }
    profile_path = OUT / "midpoint_profiles.csv"
    contrast_path = OUT / "midpoint_reduction_contrasts.csv"
    write_csv(profile_path, rows)
    write_csv(contrast_path, contrasts)
    files = [Path(__file__), Path(__file__).with_name("profile_grid.py"),
             OUT / "PROFILE_SPECIFICATION.md", profile_path, contrast_path]
    receipts["sha256"] = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    (OUT/"profile_results.json").write_text(json.dumps(receipts, indent=2, allow_nan=False)+"\n",
                                           encoding="utf-8", newline="\n")
    print(f"Wrote {len(rows)} midpoint profiles and {len(contrasts)} reduction contrasts.")


def summarize_participant_points(records):
    groups = {}
    for row in records:
        if row["participant"] == "equal_participant_group" or "point_cm" not in row:
            continue
        keys = ("axis", "correction", "cohort", "model", "effect")
        key = tuple(row[k] for k in keys)
        groups.setdefault(key, []).append(row["point_cm"])
    return [dict(zip(keys, key), n=len(values), conditional_mean_cm=float(np.mean(values)))
            for key, values in groups.items()]


if __name__ == "__main__":
    run()
