"""Finite, exploratory native analysis of baseline-subtracted Study 5 responses.

Run from the repository root. Existing browser/manuscript results are untouched.
No specification is selected by its experimental p value.
"""
import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from scipy import linalg, special, stats

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "workbook"))
from paper_analysis import clean
from participant_sigmoid import trial_tensor, summarize, resample_trials
from descriptive_sigmoid import smooth
from inference import paired, repeated_anova

SEED = 20261018
OUT = ROOT / "results/baseline_effects"
LOCAL = ROOT / ".for-ai-local/baseline_effects"
DISTANCES = {"registered": np.array([10., 27., 50., 73., 100.]),
             "trajectory": np.array([20., 36.6666666667, 60., 83.3333333333, 100.])}
CELL_NAMES = ("Control Exhale", "Control Inhale", "Viscereality Exhale", "Viscereality Inhale")
EFFECTS = ("Condition", "Phase", "Condition × Phase", "Phase within Control",
           "Phase within Viscereality", "Condition within Exhale", "Condition within Inhale")
W = np.array([[-.5, -.5, .5, .5], [-.5, .5, -.5, .5], [1., -1., -1., 1.],
              [-1., 1., 0., 0.], [0., 0., -1., 1.], [-1., 0., 1., 0.], [0., -1., 0., 1.]])
DESIGN = np.column_stack([np.ones(4), [-.5, -.5, .5, .5], [-.5, .5, -.5, .5], [.25, -.25, -.25, .25]])
COHORTS = {"primary40": ("P011", "P033"), "exclude_P011": ("P011",),
           "exclude_P033": ("P033",), "provisional42": ()}
FAMILIES = ("logistic", "probit", "gompertz", "loglogistic", "fixed_extrema_logistic")
REGISTRY = {
    "status": "finite batches specified before their execution; later diagnostic and nominal-hit amendments labelled; exploratory, not preregistered",
    "seed": SEED, "primary": "primary40 / pooled_cp / mean / registered / unsmoothed",
    "correction": "Audio-Tactile minus participant × Condition × Phase Baseline mean",
    "correction_sensitivities": ["same_label (timing equivalence unverified)", "raw reference"],
    "cohorts": COHORTS, "families": FAMILIES,
    "extractors": ["mean", "median"], "smoothers": ["none", "gaussian_constant bandwidth .15 of distance range"],
    "axes": list(DISTANCES), "curve_weights": "equal distance means; trial-count-weighted logistic sensitivity",
    "grid": {"midpoint_normalized": [-.5, 1.5, 61], "width_normalized": [.025, 2., 41],
             "signed_amplitude_bound_ms": 1000, "loglogistic_min_midpoint_cm": 1},
    "tests": ["paired t / equivalent one-df RM ANOVA", "sign-flip 19999", "Wilcoxon", "sign test",
              "paired JZS BF10", "participant bootstrap 4999", "leave-one-person-out"],
    "categorical_distance": "univariate RM ANOVA with GG sphericity adjustment and multivariate Hotelling test",
    "p_values": "unadjusted; GG is a sphericity adjustment, not a multiple-testing correction",
    "shape_refits": "500 two-level participant/trial bootstraps, primary40, mean, registered, unsmoothed, all five families, both baseline corrections; stability intervals, not validated coverage",
    "prediction": "leave-one-distance-out, every primary40 cell, raw/pooled/same-label; constant/linear/log-distance/five sigmoid families",
    "bayesian": {"joint_likelihood": "original Baseline and Audio-Tactile; corrected curve = AT expectation minus Baseline expectation",
                 "primary": "hierarchical Gaussian logistic, random participant coefficients for all four factorial contrasts",
                 "sensitivity": ["twice-wide shape priors", "Student-t trial likelihood", "same-label Baseline Gaussian", "post-hoc independent-nuisance marginal Gaussian model", "post-hoc participant × cell residual scales"],
                 "comparators": ["constant", "linear", "log-distance"],
                 "chains": 4, "draws": 1500, "tune": 1500, "target_accept": .95,
                 "diagnostic_extension": "up to 6000 tuning / 12000 retained draws per chain, target accept .99; numerical extensions only for failed diagnostics; retain failures",
                 "gate": "rank Rhat <= 1.01, bulk/tail ESS >= 400 for target contrasts, no divergences"},
    "stopping": "complete this finite battery and diagnostic-driven extensions, regardless of effect direction/p value",
    "limits": "No causal mediation, positive-amplitude requirement, forced plateau, negative-RT log transform, or significance-selected cleaning. Native execution only."
}
REGISTRY["numerical_checks"] = {
    "continuous_refinement": "all five families × both baseline corrections × four cohorts; unsmoothed means on registered axis; finer 121×81 grid and bounded continuous multistart least squares",
    "matched_noise_recovery": "20 replicates each: flat, null80, known80, known200 ms amplitudes; retained counts/noise; known midpoint effects +10,-10,+15cm; log-width effects +.15,-.15,+.2",
    "joint_recovery": "one null80 and one known200 dataset; diagnostic rather than repeated coverage validation",
    "bayesian_cv": "20 held-distance refits: constant, linear, log-distance and hierarchical logistic; independent baseline calibration retained; four chains 1500/1500, diagnostic extension 3000 tune/6000 draws",
    "tie_rule": "neutral-shape order within max(1e-8,1e-10 × centered weighted sum of squares) objective tolerance",
    "nominal_hit_audit": "post hoc: all three nominal-hit specifications, continuous refinement plus 500 refits; all six contrasts retained; no new confirmatory claim",
    "marginal_model": "post hoc nuisance-pooling sensitivity after primary sampling difficulties; independent N(0,.2) corrected intercept and N(0,.15) amplitude (seconds), integrated analytically; original shape hierarchy",
    "heterogeneous_model": "post hoc cell-specific LogNormal(log(.12),.5) residual scales after visual inspection of unequal cell noise; independent nuisance model and same shape priors; all experimental contrasts retained",
    "robust_RT_followup": "post hoc Student-t constant, linear and log-distance counterparts to check the RT-level interaction suggested by the Student-t sigmoid; all level/distance effects, including population fixed coefficients, retained; 1500 tune/draw initially, 3000 tune/6000 draws only if diagnostics require"
}


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n")


def write_csv(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not records:
        raise ValueError(f"No records for {path}")
    keys = list(dict.fromkeys(k for row in records for k in row))
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys, lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def load_data():
    files = [ROOT / "data/raw" / name for name in ("study5_participants.csv", "study5_pps_trials.csv")]
    loaded = []
    for path in files:
        with path.open() as stream:
            loaded.append(list(csv.DictReader(stream)))
    people, trials = loaded
    retained, quality, counts = clean(people, trials)
    ids, at, incomplete = trial_tensor(retained)
    b_ids, baseline, b_incomplete = trial_tensor([{**r, "trial_type": "Audio-Tactile"}
        for r in retained if r["trial_type"] == "Baseline"])
    assert ids == b_ids and not incomplete and not b_incomplete
    assert at.shape[:3] == baseline.shape[:3] == (42, 4, 5)
    audit = {"counts_full42": counts, "input_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
             "cell_order": CELL_NAMES, "distance_order_cm": DISTANCES["registered"].tolist()}
    mask = cohort_mask(ids, "primary40")
    audit["primary40_counts"] = {"AT": int(np.isfinite(at[mask]).sum()), "Baseline": int(np.isfinite(baseline[mask]).sum())}
    return np.array(ids), at, baseline, audit


def cohort_mask(ids, cohort):
    return ~np.isin(ids, COHORTS[cohort])


def profiles(at, baseline, correction, extraction="mean"):
    y, _ = summarize(at, extraction)
    # Baseline subtraction is always the mean, including robust AT extraction.
    b = np.nanmean(baseline.reshape(*baseline.shape[:2], -1), axis=-1)
    if correction == "pooled_cp":
        return y - b[..., None]
    if correction == "same_label":
        return y - np.nanmean(baseline, axis=-1)
    if correction == "raw":
        return y
    raise ValueError(correction)


def test_batch(values, metadata, seed=SEED):
    """Person is the unit; common random resampling draws across specifications."""
    n, k = values.shape
    assert len(metadata) == k and np.isfinite(values).all()
    rng = np.random.default_rng(seed)
    sign = rng.choice([-1., 1.], (19999, n))
    perm = np.abs(sign @ values / n)
    weights = rng.multinomial(n, np.full(n, 1/n), size=4999) / n
    boot = weights @ values
    loo = (values.sum(0)[None, :] - values) / (n - 1)
    loo_sd = np.sqrt(np.maximum(0., ((values**2).sum(0)[None, :] - values**2 - (n-1)*loo**2)/(n-2)))
    loo_p = 2*stats.t.sf(np.abs(loo) / np.maximum(loo_sd/np.sqrt(n-1), 1e-30), n-2)
    records = []
    for j, meta in enumerate(metadata):
        a = values[:, j]
        result = paired(a, bayes=True)
        result.pop("name")
        nonzero = a[a != 0]
        result.update(meta)
        result.update(F=result.get("t", 0.)**2, p_signflip=float((1+np.sum(perm[:, j] >= abs(a.mean())-1e-12))/20000),
            p_wilcoxon=float(stats.wilcoxon(a).pvalue) if len(nonzero) else 1.,
            p_sign=float(stats.binomtest(int(np.sum(nonzero > 0)), len(nonzero), .5).pvalue) if len(nonzero) else 1.,
            bootstrap_low=float(np.quantile(boot[:, j], .025)), bootstrap_high=float(np.quantile(boot[:, j], .975)),
            loo_estimate_min=float(loo[:, j].min()), loo_estimate_max=float(loo[:, j].max()),
            loo_p_min=float(loo_p[:, j].min()), loo_p_max=float(loo_p[:, j].max()))
        records.append(result)
    return records


def response_analysis(ids, at, baseline):
    tests, omnibus, descriptive = [], [], []
    for cohort in COHORTS:
        mask = cohort_mask(ids, cohort)
        values, metadata = [], []
        for correction in ("pooled_cp", "same_label", "raw"):
            for extraction in ("mean", "median"):
                y = profiles(at[mask], baseline[mask], correction, extraction)
                common = dict(cohort=cohort, correction=correction, extraction=extraction)
                for k, cell in enumerate(CELL_NAMES):
                    for d in range(5):
                        a = y[:, k, d]
                        descriptive.append({**common, "cell": cell, "distance_cm": DISTANCES["registered"][d],
                            "n": len(a), "mean_ms": a.mean(), "se_ms": stats.sem(a)})
                for r in repeated_anova(y.reshape(-1, 2, 2, 5)):
                    omnibus.append({**common, **r, "method": "RM ANOVA"})
                h = linalg.helmert(5).T
                for label, w in zip(EFFECTS[:3], W[:3]):
                    z = np.einsum("ncd,c,dk->nk", y, w, h)
                    mean = z.mean(0)
                    t2 = len(z) * mean @ np.linalg.solve(np.cov(z.T), mean)
                    q = z.shape[1]
                    f = (len(z)-q)*t2/(q*(len(z)-1))
                    omnibus.append({**common, "effect": label + " × distance", "method": "Hotelling",
                        "n": len(z), "F": f, "df1": q, "df2": len(z)-q, "p": stats.f.sf(f, q, len(z)-q)})
                metrics = {("mean_RT_ms", "none"): y.mean(-1), ("far_minus_near_ms", "none"): y[..., -1]-y[..., 0]}
                for axis, distances in DISTANCES.items():
                    for scale in ("linear", "log"):
                        x = distances if scale == "linear" else np.log(distances)
                        xc = x-x.mean()
                        metrics[(scale+"_distance_slope", axis)] = y @ xc/(xc@xc)
                for (metric, axis), cell_values in metrics.items():
                    for effect, a in zip(EFFECTS, (cell_values @ W.T).T):
                        metadata.append({**common, "axis": axis, "metric": metric, "effect": effect})
                        values.append(a)
                    if metric in ("mean_RT_ms", "far_minus_near_ms"):
                        metadata.append({**common, "axis": axis, "metric": metric, "effect": "Grand mean"})
                        values.append(cell_values.mean(-1))
        bcp = np.nanmean(baseline[mask].reshape(mask.sum(), 4, -1), axis=-1)
        for effect, a in zip(EFFECTS, (bcp @ W.T).T):
            metadata.append(dict(cohort=cohort, correction="baseline_reference", extraction="mean", axis="none", metric="mean_RT_ms", effect=effect))
            values.append(a)
        tests.extend(test_batch(np.array(values).T, metadata))
    write_csv(OUT / "response_tests.csv", tests)
    write_csv(OUT / "categorical_distance_tests.csv", omnibus)
    write_csv(OUT / "observed_profiles.csv", descriptive)
    return tests


def shape_basis(d, m, w, family):
    """m and w in cm; all families have q(m)=.5 and q'(m)=1/(4w)."""
    z = (np.asarray(d)[None, :] - m[:, None]) / w[:, None]
    if family in ("logistic", "fixed_extrema_logistic"):
        return special.expit(z)
    if family == "probit":
        return special.ndtr(z * np.sqrt(2*np.pi)/4)
    if family == "gompertz":
        return np.exp(-np.log(2)*np.exp(np.clip(-z/(2*np.log(2)), -700, 700)))
    if family == "loglogistic":
        return special.expit((np.log(d)[None, :] - np.log(m[:, None])) * m[:, None]/w[:, None])
    raise ValueError(family)


class CurveGrid:
    def __init__(self, distances, family, fine=False):
        self.distances, self.family = np.asarray(distances), family
        lo, span = self.distances.min(), np.ptp(self.distances)
        m = np.linspace(lo-.5*span, lo+1.5*span, 121 if fine else 61)
        if family == "loglogistic":
            m = np.linspace(1., lo+1.5*span, len(m))
        w = np.geomspace(.025*span, 2*span, 81 if fine else 41)
        mm, ww = np.meshgrid(m, w, indexing="ij")
        self.m, self.w = mm.ravel(), ww.ravel()
        neutral = ((self.m-(lo+.5*span))/(.25*span))**2 + (np.log(self.w/(span/6))/np.log(2))**2
        order = np.lexsort((self.w, self.m, neutral))
        self.m, self.w = self.m[order], self.w[order]
        self.bound = (np.isin(self.m, m[[0, -1]]) | np.isin(self.w, w[[0, -1]]))
        self.q = shape_basis(self.distances, self.m, self.w, family)

    def fit(self, y, weights=None, columns=None):
        y = np.asarray(y)
        q = self.q if columns is None else self.q[:, columns]
        weights = np.ones_like(y) if weights is None else np.asarray(weights)
        sw, sy = weights.sum(1)[:, None], (weights*y).sum(1)[:, None]
        sq = weights @ q.T
        q_centered = q-q.mean(1)[:, None]
        sq_centered = weights@q_centered.T
        den = np.maximum(weights @ (q_centered*q_centered).T - sq_centered*sq_centered/sw, 1e-20)
        centered_y = y-sy/sw
        num = (weights*centered_y) @ q_centered.T
        if self.family == "fixed_extrema_logistic":
            magnitude = np.ptp(y, axis=1)[:, None]
            center = (y.max(1)+y.min(1))[:, None]/2
            centered_q = q-.5
            signed_numerator = (weights*(y-center)) @ centered_q.T
            amp = magnitude*np.where(signed_numerator >= 0, 1., -1.)
            b = center-amp/2
            loss = (weights*(y-center)**2).sum(1)[:, None] - 2*amp*signed_numerator + amp*amp*(weights@(centered_q**2).T)
        else:
            amp = np.clip(num/den, -1000., 1000.)
            b = (sy-amp*sq)/sw
            loss = (weights*centered_y**2).sum(1)[:, None] - 2*amp*num + amp*amp*den
        # Numerically indistinguishable plateaus need a translation-invariant tie rule.
        tolerance = np.maximum(1e-8, 1e-10*np.sum(weights*centered_y**2, axis=1))
        index = np.argmax(loss <= loss.min(1)[:, None]+tolerance[:, None], axis=1)
        row = np.arange(len(y))
        params = np.column_stack([b[row, index], amp[row, index], self.m[index], self.w[index]])
        predicted = params[:, 0, None] + params[:, 1, None]*self.q[index]
        return params, predicted, self.bound[index] | (np.abs(params[:, 1]) >= 999.999)


def curve_specifications():
    for correction in ("pooled_cp", "same_label"):
        for extraction in ("mean", "median"):
            for axis in DISTANCES:
                for smoother in ("none", "gaussian_constant"):
                    for family in FAMILIES:
                        yield dict(correction=correction, extraction=extraction, axis=axis, smoother=smoother, family=family, weighting="equal_means")
        for axis in DISTANCES:
            yield dict(correction=correction, extraction="mean", axis=axis, smoother="none", family="logistic", weighting="trial_counts")


def curve_analysis(ids, at, baseline):
    cells, diagnostics, tests = [], [], []
    by_cohort = {name: ([], []) for name in COHORTS}
    grids = {(a, f): CurveGrid(d, f) for a, d in DISTANCES.items() for f in FAMILIES}
    for spec in curve_specifications():
        d = DISTANCES[spec["axis"]]
        y = profiles(at, baseline, spec["correction"], spec["extraction"]).reshape(-1, 5)
        target = smooth((d-d.min())/np.ptp(d), y, spec["smoother"], .15)
        weights = np.isfinite(at).sum(-1).reshape(-1, 5) if spec["weighting"] == "trial_counts" else None
        pars, pred, bound = grids[spec["axis"], spec["family"]].fit(target, weights)
        pars = pars.reshape(len(ids), 4, 4)
        for i, pid in enumerate(ids):
            for k, cell in enumerate(CELL_NAMES):
                a, amp, m, w = pars[i, k]
                cells.append({**spec, "participant_id": pid, "cell": cell, "lower_plateau_ms": a, "amplitude_ms": amp,
                    "midpoint_cm": m, "width_cm": w, "sharpness_per_cm": 1/(4*w), "signed_slope_ms_per_cm": amp/(4*w),
                    "grid_bound": bool(bound.reshape(len(ids), 4)[i, k])})
        for cohort in COHORTS:
            mask = cohort_mask(ids, cohort)
            meta, vals = by_cohort[cohort]
            for metric, v in (("midpoint_cm", pars[:, :, 2]), ("sharpness_per_cm", 1/(4*pars[:, :, 3]))):
                for effect, a in zip(EFFECTS[:3], (v[mask] @ W[:3].T).T):
                    meta.append({**spec, "cohort": cohort, "metric": metric, "effect": effect})
                    vals.append(a)
            diagnostics.append({**spec, "cohort": cohort, "n_cells": int(mask.sum()*4),
                "grid_bound_cells": int(bound.reshape(len(ids), 4)[mask].sum()),
                "midpoint_outside_cells": int(((pars[mask, :, 2] < d.min()) | (pars[mask, :, 2] > d.max())).sum()),
                "negative_amplitude_cells": int((pars[mask, :, 1] < 0).sum()),
                "prediction_rmse_ms": float(np.sqrt(np.mean((pred.reshape(len(ids), 4, 5)[mask]-y.reshape(len(ids), 4, 5)[mask])**2)))})
    for cohort, (metadata, vals) in by_cohort.items():
        tests.extend(test_batch(np.array(vals).T, metadata))
    write_csv(OUT / "curve_point_tests.csv", tests)
    write_csv(OUT / "curve_cells.csv", cells)
    write_csv(OUT / "curve_diagnostics.csv", diagnostics)
    return tests


def prediction_analysis(ids, at, baseline):
    mask = cohort_mask(ids, "primary40")
    records = []
    d = DISTANCES["registered"]
    for correction in ("pooled_cp", "same_label", "raw"):
        y = profiles(at[mask], baseline[mask], correction).reshape(-1, 5)
        for family in ("constant", "linear", "log_distance", *FAMILIES):
            pred = np.empty_like(y)
            for held in range(5):
                train = np.arange(5) != held
                if family in FAMILIES:
                    grid = CurveGrid(d, family)
                    _, fitted, _ = grid.fit(y[:, train], columns=train)
                    pred[:, held] = fitted[:, held]
                else:
                    x = np.log(d) if family == "log_distance" else d
                    design = np.ones((5, 1)) if family == "constant" else np.column_stack([np.ones(5), x])
                    beta = np.linalg.lstsq(design[train], y[:, train].T, rcond=None)[0]
                    pred[:, held] = design[held] @ beta
            error = ((pred-y)**2).reshape(mask.sum(), 4, 5)
            for i, pid in enumerate(ids[mask]):
                records.append(dict(correction=correction, family=family, participant_id=pid,
                    held_distance_mse_ms2=float(error[i].mean()), held_distance_mae_ms=float(np.abs(pred-y).reshape(mask.sum(), 4, 5)[i].mean())))
    write_csv(OUT / "prediction_by_person.csv", records)


def bootstrap_shapes(ids, at, baseline, draws=500):
    mask = cohort_mask(ids, "primary40")
    at, baseline = at[mask], baseline[mask]
    n = len(at)
    rng = np.random.default_rng(SEED+50)
    grids = {f: CurveGrid(DISTANCES["registered"], f) for f in FAMILIES}
    draws_by_spec = {(cor, fam): [] for cor in ("pooled_cp", "same_label") for fam in FAMILIES}
    for draw in range(draws):
        indices = rng.integers(0, n, n)
        a = resample_trials(at[indices], rng)
        b = resample_trials(baseline[indices], rng)
        for correction in ("pooled_cp", "same_label"):
            y = profiles(a, b, correction).reshape(-1, 5)
            for family, grid in grids.items():
                pars, _, _ = grid.fit(y)
                pars = pars.reshape(n, 4, 4)
                values = np.stack([pars[:, :, 2], 1/(4*pars[:, :, 3])], -1)
                draws_by_spec[correction, family].append(W[:3] @ values.mean(0))
        if (draw+1) % 50 == 0:
            print(f"Shape bootstrap {draw+1}/{draws}", flush=True)
    records = []
    for (correction, family), data in draws_by_spec.items():
        samples = np.array(data)
        for j, effect in enumerate(EFFECTS[:3]):
            for k, metric in enumerate(("midpoint_cm", "sharpness_per_cm")):
                v = samples[:, j, k]
                records.append(dict(cohort="primary40", correction=correction, family=family, effect=effect, metric=metric,
                    draws=draws, refit_median=np.median(v), refit_low=np.quantile(v, .025), refit_high=np.quantile(v, .975),
                    positive_fraction=np.mean(v > 0),
                    limitation="two-level stability interval; sparse singleton baseline resampling understates within-label uncertainty"))
    write_csv(OUT / "curve_refit_stability.csv", records)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=["registry", "frequentist", "bootstrap"])
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    LOCAL.mkdir(parents=True, exist_ok=True)
    ids, at, baseline, audit = load_data()
    if args.stage == "registry":
        write_json(OUT / "analysis_registry.json", REGISTRY)
        write_json(OUT / "data_audit.json", audit)
        print(json.dumps(audit, indent=2))
    elif args.stage == "frequentist":
        print("Response and categorical-distance tests", flush=True)
        response_analysis(ids, at, baseline)
        print("Finite curve family and preprocessing battery", flush=True)
        curve_analysis(ids, at, baseline)
        print("Held-distance predictions", flush=True)
        prediction_analysis(ids, at, baseline)
        print("Frequentist battery complete", flush=True)
    else:
        bootstrap_shapes(ids, at, baseline)


if __name__ == "__main__":
    main()
