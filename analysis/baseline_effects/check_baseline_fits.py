"""Continuous optimization, finer-grid and matched-noise recovery checks.

These are fixed numerical/measurement checks, not significance-based selection.
"""
import argparse

import numpy as np
from scipy import optimize, stats

from baseline_effects import (OUT, SEED, DISTANCES, FAMILIES, COHORTS, EFFECTS, W,
    DESIGN, CELL_NAMES, CurveGrid, shape_basis, load_data, cohort_mask, profiles,
    write_csv, write_json, test_batch, resample_trials, smooth)


def continuous_fit(y, family, initial, d=None):
    d = DISTANCES["registered"] if d is None else np.asarray(d)
    span = np.ptp(d)
    lower_m = 1. if family == "loglogistic" else d.min()-.5*span
    upper_m = d.min()+1.5*span
    lower_w, upper_w = .025*span, 2*span
    neutral = [d.min()+span/2, span/6]
    if family == "fixed_extrema_logistic":
        magnitude = np.ptp(y)
        candidates = []
        for sign in (-1, 1):
            a = y.min() if sign > 0 else y.max()
            for m, width in (initial[2:], neutral):
                def residual(theta):
                    return a+sign*magnitude*shape_basis(d, theta[:1], np.exp(theta[1:]), family)[0]-y
                fit = optimize.least_squares(residual, [m, np.log(width)], bounds=([lower_m, np.log(lower_w)], [upper_m, np.log(upper_w)]),
                    max_nfev=2000, ftol=1e-10, xtol=1e-10, gtol=1e-10)
                candidates.append((fit.cost, np.array([a, sign*magnitude, fit.x[0], np.exp(fit.x[1])]), fit.success))
    else:
        candidates = []
        for start in (initial, [y.mean()-np.ptp(y)/2, np.ptp(y), *neutral]):
            theta = np.array([start[0], start[1], start[2], np.log(start[3])])
            def residual(t):
                return t[0]+t[1]*shape_basis(d, t[2:3], np.exp(t[3:4]), family)[0]-y
            fit = optimize.least_squares(residual, theta, bounds=([-np.inf, -1000., lower_m, np.log(lower_w)], [np.inf, 1000., upper_m, np.log(upper_w)]),
                x_scale=[100., 100., 90., 1.], max_nfev=2000, ftol=1e-10, xtol=1e-10, gtol=1e-10)
            candidates.append((fit.cost, np.array([*fit.x[:3], np.exp(fit.x[3])]), fit.success))
    # Retain the finite-grid solution if a local optimizer cannot improve it.
    pred = initial[0]+initial[1]*shape_basis(d, initial[2:3], initial[3:4], family)[0]
    candidates.append((np.sum((pred-y)**2)/2, initial, True))
    return min(candidates, key=lambda v: v[0])


def refinement():
    ids, at, baseline, _ = load_data()
    metadata_by_cohort = {c: [] for c in COHORTS}
    values_by_cohort = {c: [] for c in COHORTS}
    records, checks = [], []
    for correction in ("pooled_cp", "same_label"):
        y = profiles(at, baseline, correction).reshape(-1, 5)
        for family in FAMILIES:
            grid = CurveGrid(DISTANCES["registered"], family)
            fine = CurveGrid(DISTANCES["registered"], family, fine=True)
            coarse_params, coarse_pred, _ = grid.fit(y)
            fine_params, fine_pred, _ = fine.fit(y)
            solutions = [continuous_fit(yy, family, p) for yy, p in zip(y, fine_params)]
            pars = np.array([v[1] for v in solutions]).reshape(len(ids), 4, 4)
            for j, (yy, solution) in enumerate(zip(y, solutions)):
                loss, p, success = solution
                coarse_loss = np.sum((coarse_pred[j]-yy)**2)/2
                fine_loss = np.sum((fine_pred[j]-yy)**2)/2
                checks.append(dict(correction=correction, family=family, participant_id=ids[j//4], cell=CELL_NAMES[j%4],
                    coarse_sse=2*coarse_loss, fine_sse=2*fine_loss, continuous_sse=2*loss, optimizer_success=bool(success),
                    midpoint_grid=p[2]-coarse_params[j, 2], sharpness_grid=1/(4*p[3])-1/(4*coarse_params[j, 3])))
                records.append(dict(correction=correction, family=family, participant_id=ids[j//4], cell=CELL_NAMES[j%4],
                    plateau_ms=p[0], amplitude_ms=p[1], midpoint_cm=p[2], width_cm=p[3], sharpness_per_cm=1/(4*p[3])))
            for cohort in COHORTS:
                mask = cohort_mask(ids, cohort)
                for metric, v in (("midpoint_cm", pars[:, :, 2]), ("sharpness_per_cm", 1/(4*pars[:, :, 3]))):
                    for effect, value in zip(EFFECTS[:3], (v[mask] @ W[:3].T).T):
                        metadata_by_cohort[cohort].append(dict(cohort=cohort, correction=correction, family=family, metric=metric, effect=effect))
                        values_by_cohort[cohort].append(value)
            print(correction, family, "continuous fits complete", flush=True)
    tests = []
    for cohort in COHORTS:
        tests.extend(test_batch(np.array(values_by_cohort[cohort]).T, metadata_by_cohort[cohort]))
    write_csv(OUT / "continuous_curve_tests.csv", tests)
    write_csv(OUT / "continuous_curve_cells.csv", records)
    write_csv(OUT / "continuous_fit_checks.csv", checks)


def simulate(at, baseline, scenario, seed):
    """Retained-trial design/noise; simulation is conditional on original cleaning."""
    rng = np.random.default_rng(seed)
    n = len(at)
    base = np.nanmean(baseline.reshape(n, 4, -1), -1)
    sig_at = np.nanstd(at-np.nanmean(at, -1)[..., None], axis=(1, 2, 3), ddof=1)
    sig_b = np.nanstd(baseline-np.nanmean(baseline, -1)[..., None], axis=(1, 2, 3), ddof=1)
    known = scenario.startswith("known")
    beta_m = np.array([55., 10., -10., 15.]) if known else np.array([55., 0., 0., 0.])
    beta_lw = np.array([np.log(15), .15, -.15, .2]) if known else np.array([np.log(15), 0., 0., 0.])
    m = (beta_m + rng.normal(size=(n, 4))*[10., 6., 6., 6.])@DESIGN.T
    width = np.exp((beta_lw+rng.normal(size=(n, 4))*[.2, .1, .1, .1])@DESIGN.T)
    amplitude = 0. if scenario == "flat" else (200. if scenario == "known200" else 80.)
    q = 1/(1+np.exp(-(DISTANCES["registered"][None, None, :]-m[..., None])/width[..., None]))
    mu_at = base[..., None]-20+amplitude*(q-.5)
    a = mu_at[..., None]+rng.normal(size=at.shape)*sig_at[:, None, None, None]
    b = base[..., None, None]+rng.normal(size=baseline.shape)*sig_b[:, None, None, None]
    a[~np.isfinite(at)] = np.nan
    b[~np.isfinite(baseline)] = np.nan
    truth = dict(midpoint_cm=m, sharpness_per_cm=1/(4*width), population_midpoint_effect_cm=beta_m[1:],
                 population_log_sharpness_effect=-beta_lw[1:])
    return a, b, truth


def recovery():
    ids, at, baseline, _ = load_data()
    mask = cohort_mask(ids, "primary40")
    at, baseline = at[mask], baseline[mask]
    grid = CurveGrid(DISTANCES["registered"], "logistic")
    records = []
    for scenario in ("flat", "null80", "known80", "known200"):
        for replicate in range(20):
            a, b, truth = simulate(at, baseline, scenario, SEED+200+replicate)
            y = profiles(a, b, "pooled_cp").reshape(-1, 5)
            p, _, bound = grid.fit(y)
            p = p.reshape(len(at), 4, 4)
            for metric, values in (("midpoint_cm", p[:, :, 2]), ("sharpness_per_cm", 1/(4*p[:, :, 3]))):
                contrasts = values@W[:3].T
                actual = truth[metric]@W[:3].T
                for j, effect in enumerate(EFFECTS[:3]):
                    result = stats.ttest_1samp(contrasts[:, j], 0)
                    records.append(dict(scenario=scenario, replicate=replicate, metric=metric, effect=effect,
                        estimate=contrasts[:, j].mean(), true_sample_contrast=actual[:, j].mean() if scenario != "flat" else "undefined",
                        p=result.pvalue, recovered_nominal=bool(result.pvalue < .05), bound_cells=int(bound.sum()),
                        cell_spearman=float(stats.spearmanr(values.ravel(), truth[metric].ravel()).statistic) if scenario != "flat" else "undefined"))
    write_csv(OUT / "matched_noise_recovery.csv", records)


def nominal_followup():
    """Explicitly post hoc numerical/stability audit of all three nominal-hit specifications."""
    specs = [dict(cohort="primary40", correction="pooled_cp", extraction="median", axis="registered", smoother="none", family="loglogistic"),
        dict(cohort="primary40", correction="same_label", extraction="mean", axis="trajectory", smoother="gaussian_constant", family="loglogistic"),
        dict(cohort="exclude_P011", correction="same_label", extraction="mean", axis="registered", smoother="none", family="fixed_extrema_logistic")]
    ids, at, baseline, _ = load_data()
    tests, stability = [], []
    for spec in specs:
        mask = cohort_mask(ids, spec["cohort"])
        a, b = at[mask], baseline[mask]
        n = len(a)
        d = DISTANCES[spec["axis"]]
        grid, fine = CurveGrid(d, spec["family"]), CurveGrid(d, spec["family"], fine=True)
        def target(a, b):
            return smooth((d-d.min())/np.ptp(d), profiles(a, b, spec["correction"], spec["extraction"]).reshape(-1, 5), spec["smoother"], .15)
        y = target(a, b)
        initial, _, _ = fine.fit(y)
        p = np.array([continuous_fit(yy, spec["family"], pp, d)[1] for yy, pp in zip(y, initial)]).reshape(n, 4, 4)
        meta, values = [], []
        for metric, data in (("midpoint_cm", p[:, :, 2]), ("sharpness_per_cm", 1/(4*p[:, :, 3]))):
            for effect, v in zip(EFFECTS[:3], (data@W[:3].T).T):
                meta.append({**spec, "metric": metric, "effect": effect, "status": "post-hoc numerical audit"})
                values.append(v)
        tests.extend(test_batch(np.array(values).T, meta))
        rng = np.random.default_rng(SEED+450)
        boot = []
        for draw in range(500):
            index = rng.integers(0, n, n)
            ap, bp = resample_trials(a[index], rng), resample_trials(b[index], rng)
            pars, _, _ = grid.fit(target(ap, bp))
            pars = pars.reshape(n, 4, 4)
            boot.append(W[:3] @ np.stack([pars[:, :, 2], 1/(4*pars[:, :, 3])], -1).mean(0))
        boot = np.array(boot)
        for j, effect in enumerate(EFFECTS[:3]):
            for k, metric in enumerate(("midpoint_cm", "sharpness_per_cm")):
                v = boot[:, j, k]
                stability.append({**spec, "effect": effect, "metric": metric, "draws": 500,
                    "refit_low": np.quantile(v, .025), "refit_high": np.quantile(v, .975), "median": np.median(v),
                    "status": "post-hoc grid-refit stability; singleton baseline and two-level bootstrap limitations remain"})
        print("Nominal-hit audit complete:", spec, flush=True)
    write_csv(OUT / "nominal_hit_continuous_checks.csv", tests)
    write_csv(OUT / "nominal_hit_refit_checks.csv", stability)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=["refinement", "recovery", "nominal"])
    args = parser.parse_args()
    {"refinement": refinement, "recovery": recovery, "nominal": nominal_followup}[args.stage]()
