"""Joint Gaussian Baseline/AT sigmoids with an optional positive amplitude.

Integrate baseline, corrected intercept and amplitude analytically. Positivity
adds the exact Gaussian posterior orthant probability, rather than clipping fits.
"""
import json
from pathlib import Path
import sys
import time

import arviz as az
import numpy as np
import pymc as pm
import pytensor.tensor as pt
from scipy import special, stats

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "baseline_effects"))
from baseline_effects import (ROOT, SEED, DISTANCES, CELL_NAMES, EFFECTS, W,
    load_data, cohort_mask, write_json, write_csv)
from joint_pps import hierarchy, sufficient, summarize_draws

OUT = ROOT / "results/directional_sigmoid"
LOCAL = ROOT / ".for-ai-local/directional_sigmoid"
X = DISTANCES["registered"]


def primary_data():
    ids, at, baseline, audit = load_data()
    original = json.loads((ROOT / "results/baseline_effects/manifest.json").read_text())
    assert audit["input_sha256"] == original["input_sha256"]
    keep = cohort_mask(ids, "primary40")
    return ids[keep], at[keep], baseline[keep], audit


def make_model(ids, at, baseline, positive=True):
    coordinates = {"participant": ids, "cell": CELL_NAMES, "distance": X,
        "coefficient": ("Intercept", *EFFECTS[:3]), "effect": EFFECTS[:3]}
    na, ya, ssa = sufficient(at/1000)
    nb, yb, ssb = sufficient(baseline/1000)
    nb_cp, syb = nb.sum(-1), (nb*yb).sum(-1)
    with pm.Model(coords=coordinates) as model:
        sa = pm.LogNormal("sigma_at", np.log(.12), .5, dims="participant")
        sb = pm.LogNormal("sigma_baseline", np.log(.12), .5, dims="participant")
        va, vb = sa[:, None]**2, sb[:, None]**2
        base_variance = 1/(1/.4**2+nb_cp/vb)
        base_mean = base_variance*(.6/.4**2+syb/vb)
        base_rss = np.sum(ssb+nb*(yb-.6)**2, axis=-1)
        base_sum = syb-.6*nb_cp
        pm.Potential("likelihood_baseline", pt.sum(-.5*(nb_cp*pt.log(vb)+pt.log1p(.4**2*nb_cp/vb)
            +base_rss/vb-base_sum**2*base_variance/vb**2)))
        midpoint = hierarchy("midpoint", len(ids), [.5, 0., 0., 0.], .5, .35)
        width = pt.exp(hierarchy("log_width", len(ids), [np.log(1/6), 0., 0., 0.], .7, .5))
        pm.Deterministic("midpoint_cm", 10+90*midpoint, dims=("participant", "cell"))
        pm.Deterministic("sharpness_per_cm", 1/(360*width), dims=("participant", "cell"))
        q = pm.math.sigmoid(((X-10)/90-midpoint[..., None])/width[..., None])-.5
        n = na.sum(-1)
        sq, sqq = pt.sum(na*q, -1), pt.sum(na*q*q, -1)
        offset_variance = base_variance+.2**2
        amplitude_variance = .15**2
        p00, p01, p11 = 1/offset_variance+n/va, sq/va, 1/amplitude_variance+sqq/va
        determinant = p00*p11-p01*p01
        c00, c01, c11 = p11/determinant, -p01/determinant, p00/determinant
        centered = ya-base_mean[..., None]
        v0, v1 = pt.sum(na*centered, -1)/va, pt.sum(na*q*centered, -1)/va
        rss = pt.sum(ssa+na*centered**2, -1)
        quadratic = rss/va-(c00*v0*v0+2*c01*v0*v1+c11*v1*v1)
        logdet = n*pt.log(va)+pt.log(determinant*offset_variance*amplitude_variance)
        amp_mean = c01*v0+c11*v1
        score = -.5*(logdet+quadratic)
        if positive:
            score += np.log(2)+pm.logcdf(pm.Normal.dist(0., 1.), amp_mean/pt.sqrt(c11))
        pm.Potential("likelihood_at", pt.sum(score))
        for name, value in dict(base_mean=base_mean, base_variance=base_variance,
                offset_variance=offset_variance, offset_mean=base_mean+c00*v0+c01*v1,
                amp_mean=amp_mean, c00=c00, c01=c01, c11=c11).items():
            pm.Deterministic("conditional_"+name, value, dims=("participant", "cell"))
        pm.Deterministic("population_midpoint_effect_cm", 90*model["beta_midpoint"][1:], dims="effect")
        pm.Deterministic("population_log_sharpness_effect", -model["beta_log_width"][1:], dims="effect")
        for metric in ("midpoint_cm", "sharpness_per_cm"):
            pm.Deterministic(metric+"_effect", pt.dot(W[:3], model[metric].mean(0)), dims="effect")
    return model


def nuisance_draws(conditional, positive, rng):
    """Exact conditional draws after Gaussian marginalization/orthant restriction."""
    get = lambda name: conditional["conditional_"+name]
    mu, sd = get("amp_mean"), np.sqrt(get("c11"))
    if positive:
        amplitude = stats.truncnorm.rvs(-mu/sd, np.inf, loc=mu, scale=sd, size=mu.shape, random_state=rng)
    else:
        amplitude = mu+sd*rng.normal(size=mu.shape)
    offset = get("offset_mean")+get("c01")/get("c11")*(amplitude-mu) + \
        np.sqrt(np.maximum(get("c00")-get("c01")**2/get("c11"), 0))*rng.normal(size=mu.shape)
    baseline = get("base_mean")+get("base_variance")/get("offset_variance")*(offset-get("base_mean")) + \
        np.sqrt(get("base_variance")*.2**2/get("offset_variance"))*rng.normal(size=mu.shape)
    return amplitude, offset-baseline, baseline


def complete_trace(trace, positive, seed):
    posterior = trace["posterior"].to_dataset()
    values = {name: var.values for name, var in posterior.data_vars.items()}
    amplitude, delta, baseline = nuisance_draws(values, positive, np.random.default_rng(seed))
    curve = delta[..., None]+amplitude[..., None]*(special.expit(
        (X-values["midpoint_cm"][..., None])*4*values["sharpness_per_cm"][..., None])-.5)
    for name, value in dict(amplitude=amplitude, corrected_intercept=delta, baseline_mean=baseline).items():
        posterior[name] = (("chain", "draw", "participant", "cell"), value)
    posterior["corrected_curve"] = (("chain", "draw", "participant", "cell", "distance"), curve)
    for name, v in (("mean_RT_effect_ms", 1000*curve.mean((2, 4))@W[:3].T),
                    ("far_minus_near_effect_ms", 1000*(curve[..., -1]-curve[..., 0]).mean(2)@W[:3].T)):
        posterior[name] = (("chain", "draw", "effect"), v)
    trace["posterior"].dataset = posterior
    return trace


def diagnostics(trace):
    posterior = trace["posterior"].dataset
    diag = az.summary(trace, kind="diagnostics", round_to="none")
    targets = [name for name in posterior if "_effect" in name]
    target = az.summary(trace, var_names=targets, kind="diagnostics", round_to="none")
    result = dict(max_rhat=float(diag.r_hat.max()), min_bulk_ess=float(diag.ess_bulk.min()),
        min_tail_ess=float(diag.ess_tail.min()), target_max_rhat=float(target.r_hat.max()),
        target_min_bulk_ess=float(target.ess_bulk.min()), target_min_tail_ess=float(target.ess_tail.min()),
        divergences=int(trace["sample_stats"].dataset["diverging"].values.sum()))
    result["gate"] = bool(result["divergences"] == 0 and result["max_rhat"] <= 1.01 and
        min(result["min_bulk_ess"], result["min_tail_ess"]) >= 400)
    return result, diag


def sample(ids, at, baseline, positive, draws=3000, tune=3000, seed=SEED+810):
    model = make_model(ids, at, baseline, positive)
    started = time.monotonic()
    with model:
        trace = pm.sample(draws=draws, tune=tune, chains=4, cores=4, random_seed=seed,
            nuts_sampler="nutpie", nuts={"target_accept": .99, "adaptation": "diag"},
            progressbar=False, compute_convergence_checks=False)
    trace = complete_trace(trace, positive, seed+100)
    summary, diag = diagnostics(trace)
    summary.update(seconds=time.monotonic()-started, draws_per_chain=draws, tune=tune, chains=4,
                   positive_amplitude=positive)
    return trace, summary, diag


def full_fit():
    ids, at, baseline, _ = primary_data()
    attempts = []
    for draws, tune in ((3000, 3000), (6000, 6000)):
        trace, summary, diag = sample(ids, at, baseline, True, draws, tune)
        attempts.append(summary)
        write_json(OUT / "fit_attempts.json", attempts)
        if summary["gate"]:
            break
    posterior = trace["posterior"].dataset
    arrays = {name: var.values for name, var in posterior.data_vars.items()}
    arrays.update({"sample_stats__"+name: var.values for name, var in trace["sample_stats"].dataset.data_vars.items()})
    np.savez(LOCAL / "positive_draws.npz", **arrays)
    diag.to_csv(OUT / "diagnostics.csv")
    write_json(OUT / "run.json", summary)
    effects, simple, parameters = [], [], []
    for name in posterior:
        if "_effect" in name:
            effects.extend(summarize_draws(posterior[name].values, "positive_amplitude", name, EFFECTS[:3]))
    for name in ("midpoint_cm", "sharpness_per_cm", "amplitude", "corrected_intercept"):
        values = arrays[name].reshape(-1, len(ids), 4)
        q = np.quantile(values, [.025, .5, .975], axis=0)
        for i, pid in enumerate(ids):
            for c, cell in enumerate(CELL_NAMES):
                parameters.append(dict(participant_id=pid, cell=cell, quantity=name,
                    median=q[1, i, c], ci_low=q[0, i, c], ci_high=q[2, i, c]))
        if name in ("midpoint_cm", "sharpness_per_cm"):
            simple.extend(summarize_draws(values.mean(1)@W.T, "positive_amplitude", name, EFFECTS))
    write_csv(OUT / "effects.csv", effects)
    write_csv(OUT / "simple_parameter_contrasts.csv", simple)
    write_csv(OUT / "participant_parameters.csv", parameters)
    print(json.dumps(summary), flush=True)


def crossvalidation():
    ids, at, baseline, _ = primary_data()
    na, ya, ssa = sufficient(at/1000)
    output, records = OUT / "held_distance_predictions.csv", []
    if output.exists():
        import pandas as pd
        records = pd.read_csv(output).to_dict("records")
    completed = {(r["model"], r["held_distance_cm"]) for r in records}
    for positive in (True, False):
        name = "positive_amplitude" if positive else "unrestricted"
        for held, distance in enumerate(X):
            if (name, distance) in completed:
                continue
            train = at.copy()
            train[:, :, held] = np.nan
            attempts = []
            for draws, tune in ((1500, 1500), (6000, 3000)):
                trace, diag, _ = sample(ids, train, baseline, positive, draws, tune, SEED+820+held)
                posterior = trace["posterior"].dataset
                mu = posterior["baseline_mean"].values+posterior["corrected_curve"].values[..., held]
                rhat = float(np.max(az.rhat(mu)))
                bulk, tail = float(np.min(az.ess(mu))), float(np.min(az.ess(mu, method="tail", prob=.05)))
                valid = bool(rhat <= 1.01 and min(bulk, tail) >= 400 and diag["divergences"] == 0)
                attempts.append(dict(**diag, prediction_rhat=rhat, prediction_bulk_ess=bulk,
                                     prediction_tail_ess=tail, prediction_gate=valid))
                if valid:
                    break
            write_json(OUT / f"cv_{name}_{held}_diagnostics.json", attempts)
            mu = mu.reshape(-1, len(ids), 4)
            sd = posterior["sigma_at"].values.reshape(-1, len(ids), 1)
            n, mean, sse = na[:, :, held], ya[:, :, held], ssa[:, :, held]
            score = -.5*n*np.log(2*np.pi)-n*np.log(sd)-.5*(sse+n*(mean-mu)**2)/sd**2
            lpd = special.logsumexp(score, axis=0)-np.log(len(mu))
            for i, pid in enumerate(ids):
                for c, cell in enumerate(CELL_NAMES):
                    records.append(dict(model=name, held_distance_cm=distance, participant_id=pid, cell=cell,
                        block_log_predictive_density=lpd[i, c], predicted_AT_ms=1000*mu[:, i, c].mean(),
                        observed_AT_ms=1000*mean[i, c], error_ms=1000*(mu[:, i, c].mean()-mean[i, c]),
                        prediction_gate=valid))
            write_csv(output, records)
            print(f"CV {name}, held {distance:g}cm: Rhat {rhat:.4f}, bulk/tail ESS {bulk:.0f}/{tail:.0f}, gate {valid}", flush=True)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    LOCAL.mkdir(parents=True, exist_ok=True)
    {"fit": full_fit, "cv": crossvalidation}[sys.argv[1]]()
