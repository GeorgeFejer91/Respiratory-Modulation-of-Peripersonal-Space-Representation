"""Run continuous knot profiles, matched recovery and held-distance checks."""

import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.optimize import lsq_linear

from knot_grid import FAMILIES, KnotFit, best_available, knot_support, make_grid, predict_folds
from profile import COHORTS, group_cutoffs, group_data, person_cutoffs, prepare, variance_six
from profile_grid import REFERENCES, diag_cov, intervals
from screen import DISTANCES, EFFECTS, OUT, ROOT, SUMMARY_LABELS, W, cohort_mask, load_data, phase_profiles, write_csv

SEED = 20261118
REPLICATES = 96
LIMIT = 640
PREDICTION_LIMITS = (160, 320, 640)


def profile_rows(y, cov, radius, ids, distance, tags):
    x, grid = make_grid(distance)
    cm = distance[0] + grid*np.ptp(distance)
    fit = KnotFit(distance, x, grid, cov, np.arange(len(x)))
    reference, _ = fit.reference_surface(y)
    rows, effects = [], []
    for family in FAMILIES:
        interior = knot_support(x, grid, family)
        loss, coefficient = fit.surface(y, family, LIMIT)
        point_idx = best_available(loss, x, grid, family)
        for i, pid in enumerate(ids):
            record = dict(tags, participant=pid, family=family)
            for j, cell in enumerate(SUMMARY_LABELS):
                cell_record = dict(record, cell=cell)
                if not np.isfinite(radius[i, j, 0]):
                    rows.append(dict(cell_record, status="variance_unavailable"))
                    continue
                support = loss[i, j] <= radius[i, j, 0]
                null = reference[i, j] <= radius[i, j, 0]
                localized = support.any() and not (support & ~interior).any() and not null.any()
                rows.append(dict(
                    cell_record, status="localized_knot" if localized else "unresolved",
                    point_cm=cm[point_idx[i,j]],
                    slope_change_ms_per_range=coefficient[i,j,point_idx[i,j]],
                    evaluated_points=len(cm), compatible_points=int(support.sum()),
                    compatible_intervals_cm=json.dumps(intervals(support, cm)),
                    insufficient_probe_support=bool((support & ~interior).any()),
                    outside_design_compatible=bool((support & ((grid<=0) | (grid>=1))).any()),
                    compatible_references=" ".join(n for n, flag in zip(REFERENCES, null) if flag),
                ))
            for name, weights in zip(EFFECTS, W):
                effect = dict(record, effect=name)
                active = weights != 0
                joint_radius = radius[i, :4, 1][active]
                if not np.isfinite(joint_radius).all():
                    effects.append(dict(effect, status="variance_unavailable"))
                    continue
                support = loss[i, :4][active] <= joint_radius[:, None]
                null = reference[i, :4][active] <= joint_radius[:, None]
                locations = cm[None, :]*weights[active, None]
                nonempty = support.any(-1).all()
                localized = nonempty and not (support & ~interior).any() and not null.any()
                effects.append(dict(
                    effect, status="localized_knot_contrast" if localized else "unresolved",
                    point_cm=cm[point_idx[i, :4]] @ weights,
                    conditional_lo_cm=np.where(support, locations, np.inf).min(-1).sum() if nonempty else None,
                    conditional_hi_cm=np.where(support, locations, -np.inf).max(-1).sum() if nonempty else None,
                    reference_compatible=bool(null.any()),
                    insufficient_probe_support=bool((support & ~interior).any()),
                ))
    return rows, effects


def diagnostics(distance):
    x, grid = make_grid(distance)
    rng = np.random.default_rng(SEED)
    training = np.array([0, 1, 3, 4])
    cov = np.diag([20, 30, 15, 27, 22]) + 5
    chol = np.linalg.cholesky(cov[np.ix_(training, training)])
    fit = KnotFit(distance, x, grid, cov, training)
    y = rng.normal(650, 160, len(x))
    for family in FAMILIES:
        _, _, nuisance, hinge, _ = fit.knot_parts(family)
        loss, coefficient = fit.surface(y, family, 80)
        for idx in [0, len(grid)//3, len(grid)//2, len(grid)-1]:
            design = np.column_stack([nuisance, hinge[idx]])
            white = np.linalg.solve(chol, design[training])
            target = np.linalg.solve(chol, y[training])
            bound = [np.inf]*(nuisance.shape[-1])+[80]
            direct = lsq_linear(white, target, bounds=(-np.array(bound), bound), tol=1e-12)
            np.testing.assert_allclose(loss[idx], np.square(direct.fun).sum(), atol=5e-7)
            if np.linalg.matrix_rank(white) == white.shape[1]:
                pred = fit.predict(y, family, idx, coefficient[idx], 2)
                np.testing.assert_allclose(pred, design[2] @ direct.x, atol=3e-6)
        clean_idx = np.argmin(abs(grid-.42))
        clean = 650+340*hinge[clean_idx]
        if family == "broken_line":
            clean -= 200*x
        full = KnotFit(distance, x, grid, cov, np.arange(len(x)))
        full_loss, _ = full.surface(clean, family, LIMIT)
        assert best_available(full_loss, x, grid, family) == clean_idx
        np.testing.assert_allclose(full.surface(y+300, family, LIMIT)[0], full.surface(y, family, LIMIT)[0], atol=3e-8)
    return "Direct constrained GLS, edge rank deficiency, held-probe reconstruction, noiseless knots and offset invariance."


def generator_curves(x, grid):
    idx = np.argmin(abs(grid[None, :] - np.array([.40,.44,.52,.56])[:, None]), axis=-1)
    k = grid[idx, None]
    right, left = np.maximum(x-k, 0), np.maximum(k-x, 0)
    yield "flat", np.full((4,5), 650.), None
    yield "linear", np.broadcast_to(650+160*x, (4,5)), None
    yield "near_plateau", 650 + 320*right, idx
    yield "far_plateau", 650 - 320*left, idx
    yield "broken_line", 650 - 170*x + 480*right, idx


def simulated_metrics(observed, cov, radius, distance, scenario, truth):
    x, grid = make_grid(distance)
    cm = distance[0] + grid*np.ptp(distance)
    fit = KnotFit(distance, x, grid, cov, np.arange(len(x)))
    ref_ok = (fit.reference_surface(observed)[0] <= radius[..., 0, None]).any(-1)
    report = {}
    for family in FAMILIES:
        loss, _ = fit.surface(observed, family, LIMIT)
        support = loss <= radius[..., 0, None]
        interior = knot_support(x, grid, family)
        localized = support.any(-1) & ~(support & ~interior).any(-1) & ~ref_ok
        result = {"localized_fraction": float(localized.mean())}
        if scenario == family:
            target = np.broadcast_to(truth, loss.shape[:-1])
            hit = np.take_along_axis(loss, target[..., None], -1)[..., 0]
            coverage = hit <= radius[..., 0]
            chosen = best_available(loss, x, grid, family)
            point_error = cm[chosen] - cm[truth]
            effect_error = point_error @ W.T
            result.update(
                truth_cm=cm[truth].tolist(),
                true_location_coverage=float(coverage.mean()),
                complete_four_cell_coverage=float((hit <= radius[..., 1]).all(-1).mean()),
                correctly_localized_fraction=float((coverage & localized).mean()),
                conditional_location_rmse_cm=float(np.sqrt(np.mean(point_error**2))),
                conditional_effect_rmse_cm=dict(zip(EFFECTS, np.sqrt(np.mean(effect_error**2, axis=tuple(range(effect_error.ndim-1)))))),
            )
        report[family] = result
    return report


def recovery(variance, df, observed, distance):
    rng = np.random.default_rng(SEED+1)
    x, grid = make_grid(distance)
    x_cov = np.cov(observed.reshape(len(observed), -1).T)
    person_radius = person_cutoffs(df)[:, :4]
    group_radius = group_cutoffs(len(df))[0, :4]
    result = {}
    for scenario, truth_mean, truth_indices in generator_curves(x, grid):
        size = (REPLICATES, *variance.shape)
        raw = truth_mean + rng.normal(size=size)*np.sqrt(variance)
        s2 = variance*rng.chisquare(df, size=size)/df
        population = truth_mean + rng.multivariate_normal(np.zeros(20), x_cov, size=(REPLICATES, len(df))).reshape(size)
        group_mean = population.mean(1)
        centered = population - group_mean[:, None]
        group_cov = np.einsum("rnci,rncj->rcij", centered, centered)/(len(df)*(len(df)-1))
        result[scenario] = dict(
            individuals=simulated_metrics(raw, diag_cov(s2), person_radius, distance, scenario, truth_indices),
            group=simulated_metrics(group_mean, group_cov, group_radius, distance, scenario, truth_indices),
        )
    return result


def run():
    checked = diagnostics(DISTANCES["registered"])
    ids, at, baseline, audit = load_data()
    primary = cohort_mask(ids, "primary40")
    rows, contrasts, predictive = [], [], {}
    for correction in ("pooled_cp", "same_label"):
        mean, var, df = prepare(at, baseline, correction)
        col = phase_profiles(mean)
        v = variance_six(var[primary])
        ok = np.isfinite(v) & (v > 0)
        person_cov = diag_cov(np.where(ok, v, 1))
        radius = np.where(ok.all(-1)[..., None], person_cutoffs(df[primary]), np.nan)
        usable = np.isfinite(radius[:, :4, 0]).all(-1)
        for axis, distance in DISTANCES.items():
            label = dict(axis=axis, correction=correction)
            inputs = col[primary], person_cov, radius, ids[primary]
            cells, eff = profile_rows(*inputs, distance, dict(label, cohort="primary40"))
            rows.extend(cells)
            contrasts.extend(eff)
            scores = dict(individual_profiles=predict_folds(
                col[primary][usable, :4], person_cov[usable, :4], distance, PREDICTION_LIMITS))
            for cohort in COHORTS:
                mask = cohort_mask(ids, cohort)
                agg, cov = group_data(col[mask])
                cells, eff = profile_rows(agg, cov, group_cutoffs(mask.sum()), ["equal_participant_group"],
                                          distance, dict(label, cohort=cohort))
                rows.extend(cells)
                contrasts.extend(eff)
                if cohort == "primary40":
                    scores["group_profiles"] = predict_folds(agg[:, :4], cov[:, :4], distance, PREDICTION_LIMITS)
            predictive[axis+"_"+correction] = scores
    mean, var, df = prepare(at[primary], baseline[primary], "pooled_cp")
    receipts = dict(seed=SEED, replicates=REPLICATES, input=audit, prediction_rmse_ms=predictive, diagnostics=checked,
                    registered_recovery=recovery(var, df, mean, DISTANCES["registered"]))
    candidates = OUT / "knot_profiles.csv"
    effects = OUT / "knot_contrasts.csv"
    write_csv(candidates, rows)
    write_csv(effects, contrasts)
    shared_code = [Path(__file__).with_name(name)
                   for name in ("knot_grid.py", "profile.py", "profile_grid.py", "screen.py")]
    paths = [Path(__file__), *shared_code, ROOT/"analysis/baseline_effects/baseline_effects.py",
             OUT/"KNOT_SPECIFICATION.md", candidates, effects]
    receipts["sha256"] = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    (OUT/"knot_results.json").write_text(json.dumps(receipts, indent=2, allow_nan=False)+"\n",
                                        encoding="utf-8", newline="\n")
    print(f"Wrote {len(rows)} knot profiles and {len(contrasts)} contrasts.")


if __name__ == "__main__":
    run()
