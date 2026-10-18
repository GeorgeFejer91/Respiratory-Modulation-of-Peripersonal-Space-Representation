"""Out-of-sample, posterior-predictive and recovery checks for joint PPS fits."""
import argparse
import csv
import json
import time

import arviz as az
import numpy as np
import pymc as pm
from scipy import special, stats

from baseline_effects import (OUT, LOCAL, SEED, DISTANCES, CELL_NAMES, EFFECTS,
    load_data, cohort_mask, profiles, write_csv, write_json)
from joint_pps import make_model, sufficient, CONFIGS, save_results
from check_baseline_fits import simulate


def primary_data():
    ids, at, base, _ = load_data()
    mask = cohort_mask(ids, "primary40")
    return ids[mask], at[mask], base[mask]


def crossvalidation():
    ids, at, base = primary_data()
    all_count, all_mean, all_sse = sufficient(at/1000)
    def previous(name):
        path = OUT/name
        if not path.exists():
            return []
        with path.open() as stream:
            return list(csv.DictReader(stream))
    records = previous("joint_held_distance_predictions.csv")
    diagnostics = previous("joint_held_distance_diagnostics.csv")
    completed = {(r["family"], float(r["held_distance_cm"])) for r in records}
    for family in ("constant", "linear", "log_distance", "logistic"):
        for held in range(5):
            if (family, DISTANCES["registered"][held]) in completed:
                continue
            training = at.copy()
            training[:, :, held, :] = np.nan
            model = make_model(ids, training, base, family=family)
            for attempt, draws, tune, accept in ((0, 1500, 1500, .95), (1, 6000, 3000, .99)):
                started = time.monotonic()
                with model:
                    trace = pm.sample(draws=draws, tune=tune, chains=4, cores=2, random_seed=SEED+100+held,
                        nuts_sampler="nutpie", nuts={"target_accept": accept, "adaptation": "diag"}, progressbar=False,
                        var_names=["corrected_curve", "baseline_mean", "sigma_at"], compute_convergence_checks=False)
                posterior = trace["posterior"].dataset
                mu = posterior["corrected_curve"].values[..., held] + posterior["baseline_mean"].values
                rhat = float(np.max(az.rhat(mu)))
                ess = float(np.min(az.ess(mu)))
                divergences = int(trace["sample_stats"].dataset["diverging"].values.sum())
                valid = rhat <= 1.01 and ess >= 400 and divergences == 0
                diagnostics.append(dict(family=family, held_distance_cm=DISTANCES["registered"][held], attempt=attempt,
                    chains=4, draws=draws, tune=tune, max_prediction_rhat=rhat, min_prediction_ess=ess,
                    divergences=divergences, passed=valid, seconds=time.monotonic()-started))
                if valid:
                    break
            mu = mu.reshape(-1, len(ids), 4)
            sd = posterior["sigma_at"].values.reshape(-1, len(ids), 1)
            count, observed, sse = all_count[:, :, held], all_mean[:, :, held], all_sse[:, :, held]
            log_likelihood = -.5*count*np.log(2*np.pi)-count*np.log(sd)-.5*(sse+count*(observed-mu)**2)/sd**2
            lpd = special.logsumexp(log_likelihood, axis=0)-np.log(len(mu))
            predicted = mu.mean(0)
            for i, pid in enumerate(ids):
                for c, cell in enumerate(CELL_NAMES):
                    records.append(dict(family=family, held_distance_cm=DISTANCES["registered"][held], participant_id=pid, cell=cell,
                        block_log_predictive_density=lpd[i, c], predicted_AT_ms=1000*predicted[i, c], observed_AT_ms=1000*observed[i, c],
                        error_ms=1000*(predicted[i, c]-observed[i, c]), diagnostic_gate=valid))
            write_csv(OUT / "joint_held_distance_predictions.csv", records)
            write_csv(OUT / "joint_held_distance_diagnostics.csv", diagnostics)
            print(f"CV {family}, held {DISTANCES['registered'][held]:g} cm: Rhat={rhat:.4f}, ESS={ess:.0f}, divergences={divergences}", flush=True)


def predictive_checks():
    ids, at, baseline = primary_data()
    rng = np.random.default_rng(SEED+700)
    records, curves, prior_records, identification = [], [], [], []
    count_at, mean_at, sse_at = sufficient(at/1000)
    count_b, mean_b, sse_b = sufficient(baseline/1000)
    for name, config in CONFIGS.items():
        path = LOCAL / (name+"_draws.npz")
        if not path.exists():
            continue
        data = np.load(path)
        correction = config.get("correction", "pooled_cp")
        step = max(1, data["corrected_curve"].shape[1]//250)
        def draws(key):
            a = data[key][:, ::step]
            return a.reshape(-1, *a.shape[2:])
        curve = draws("corrected_curve")
        b = draws("baseline_mean")
        b = b[..., None] if correction == "pooled_cp" else b
        mu_at = b+curve
        sa, sb = draws("sigma_at"), draws("sigma_baseline")
        sigma_a = sa[..., None] if sa.ndim == 3 else sa[:, :, None, None]
        sigma_b = sb[..., None] if sb.ndim == 3 else sb[:, :, None, None]
        # Gaussian sampling for exact mean-discrepancy checks; Student model gets
        # a direct trial-wise simulation because its sample mean is not Gaussian.
        if config.get("likelihood") == "student":
            nu = draws("nu")
            rep_at = np.zeros_like(curve)
            rep_b = np.zeros_like(curve)
            for j in range(len(curve)):
                a = mu_at[j, ..., None]+sigma_a[j, ..., None]*rng.standard_t(nu[j], size=at.shape)
                bb = b[j, ..., None]+sigma_b[j, ..., None]*rng.standard_t(nu[j], size=baseline.shape)
                a[~np.isfinite(at)] = np.nan
                bb[~np.isfinite(baseline)] = np.nan
                rep_at[j], rep_b[j] = np.nanmean(a, -1), np.nanmean(bb, -1)
            variance_factor = nu[:, None, None, None]/(nu[:, None, None, None]-2)
            working_var = sigma_a**2*variance_factor
            baseline_variance = sigma_b**2*variance_factor
        else:
            rep_at = mu_at+sigma_a/np.sqrt(count_at)*rng.normal(size=curve.shape)
            rep_b = b+sigma_b/np.sqrt(count_b)*rng.normal(size=curve.shape)
            working_var = sigma_a**2
            baseline_variance = sigma_b**2
        for kind, observed, replicate, predicted, variance, count in (
            ("AT mean-profile residual", mean_at, rep_at, mu_at, working_var, count_at),
            ("Baseline mean-profile residual", mean_b, rep_b, b, baseline_variance, count_b)):
            t_obs = np.sum(count*(observed-predicted)**2/variance, axis=(1, 2, 3))
            t_rep = np.sum(count*(replicate-predicted)**2/variance, axis=(1, 2, 3))
            records.append(dict(model=name, discrepancy=kind, observed_median=np.median(t_obs),
                replicated_median=np.median(t_rep), posterior_predictive_p=np.mean(t_rep >= t_obs)))
        if correction == "pooled_cp":
            corrected_rep = rep_at - (np.sum(rep_b*count_b, axis=-1)/count_b.sum(-1))[..., None]
        else:
            corrected_rep = rep_at-rep_b
        for c, cell in enumerate(CELL_NAMES):
            for d, distance in enumerate(DISTANCES["registered"]):
                expected = 1000*curve[:, :, c, d].mean(1)
                predictive = 1000*corrected_rep[:, :, c, d].mean(1)
                curves.append(dict(model=name, cell=cell, distance_cm=distance, mean_ms=expected.mean(),
                    ci_low=np.quantile(expected, .025), ci_high=np.quantile(expected, .975),
                    predictive_low=np.quantile(predictive, .025), predictive_high=np.quantile(predictive, .975)))
        prior = np.load(LOCAL / (name+"_prior.npz"))["corrected_curve"]
        for label, v in (("prior", prior*1000), ("posterior", curve*1000)):
            prior_records.append(dict(model=name, distribution=label, quantity="corrected expected RT over people/cells/distances",
                median=np.median(v), low=np.quantile(v, .025), high=np.quantile(v, .975)))
        if "midpoint_cm" in data:
            m, sh, amp = draws("midpoint_cm"), draws("sharpness_per_cm"), draws("amplitude")
            mlo, mhi = np.quantile(m, [.025, .975], axis=0)
            alo, ahi = np.quantile(amp, [.025, .975], axis=0)
            identification.append(dict(model=name, cells=160,
                midpoint_95ci_inside_observed_range=int(((mlo >= 10)&(mhi <= 100)).sum()),
                median_midpoint_interval_width_cm=float(np.median(mhi-mlo)),
                amplitude_95ci_excludes_zero=int(((alo > 0)|(ahi < 0)).sum()),
                median_midpoint_cm=float(np.median(m)), median_sharpness_per_cm=float(np.median(sh))))
    write_csv(OUT / "posterior_predictive_checks.csv", records)
    write_csv(OUT / "joint_group_curves.csv", curves)
    write_csv(OUT / "prior_predictive_ranges.csv", prior_records)
    write_csv(OUT / "joint_identification.csv", identification)


def recovery():
    ids, at, baseline = primary_data()
    records = []
    for scenario in ("null80", "known200"):
        a, b, truth = simulate(at, baseline, scenario, SEED+300)
        model = make_model(ids, a, b)
        start = time.monotonic()
        with model:
            trace = pm.sample(draws=3000, tune=3000, chains=4, cores=1, random_seed=SEED+301,
                nuts_sampler="nutpie", nuts={"target_accept": .99, "adaptation": "diag"},
                progressbar=False, compute_convergence_checks=False)
        save_results(trace, ids, "recovery_"+scenario, time.monotonic()-start, dict(scenario=scenario, synthetic=True))
        posterior = trace["posterior"].dataset
        for metric in ("midpoint_cm", "sharpness_per_cm", "population_midpoint_effect_cm", "population_log_sharpness_effect"):
            target = truth[metric]
            values = posterior[metric].values.reshape(-1, *target.shape)
            median = np.median(values, 0)
            lo, hi = np.quantile(values, [.025, .975], axis=0)
            records.append(dict(scenario=scenario, metric=metric, rmse=float(np.sqrt(np.mean((median-target)**2))),
                fraction_95ci_covering_truth=float(np.mean((lo <= target)&(hi >= target))),
                correlation=float(stats.spearmanr(median.ravel(), target.ravel()).statistic) if target.size > 3 else "not_applicable"))
    write_csv(OUT / "joint_recovery_checks.csv", records)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=["cv", "predictive", "recovery"])
    args = parser.parse_args()
    {"cv": crossvalidation, "predictive": predictive_checks, "recovery": recovery}[args.stage]()
