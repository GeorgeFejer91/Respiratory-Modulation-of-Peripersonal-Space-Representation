"""Explicitly shape-constrained Bayesian sigmoid approximation, not shape evidence.

The new geometric prior is separate from preserved broad-directional results.
The Gaussian nuisance integration and conditional reconstruction are unchanged.
"""
import json
from pathlib import Path
import sys
import time

import arviz as az
import numpy as np
import pandas as pd
import pymc as pm
import pytensor.tensor as pt
from scipy import special

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "directional_sigmoid"))
import model as directional
from baseline_effects import DESIGN

ROOT, X, CELL_NAMES = directional.ROOT, directional.X, directional.CELL_NAMES
W, EFFECTS = directional.W, directional.EFFECTS
write_csv, write_json = directional.write_csv, directional.write_json
OUT = ROOT / "results/visible_sigmoid"
LOCAL = ROOT / ".for-ai-local/visible_sigmoid"
CONFIGS = {"visible95": .05, "visible90": .10}
SEED = 20261019


def geometry(position_fraction, width_fraction, epsilon):
    """Guarantee the epsilon/(1-epsilon) transition fits inside 10–100 cm."""
    k = np.log((1-epsilon)/epsilon)
    width = 2+(90/(2*k)-2)*width_fraction
    midpoint = 10+k*width+(90-2*k*width)*position_fraction
    return midpoint, width


def make_model(ids, at, baseline, epsilon=.05):
    coordinates = {"participant": ids, "cell": CELL_NAMES, "distance": X,
        "coefficient": ("Intercept", *EFFECTS[:3]), "effect": EFFECTS[:3]}
    na, ya, ssa = directional.sufficient(at/1000)
    nb, yb, ssb = directional.sufficient(baseline/1000)
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
        position = directional.hierarchy("position_fraction", len(ids), [0.]*4, 1.5, 1.)
        fraction = directional.hierarchy("width_fraction", len(ids), [0.]*4, 1.5, 1.)
        m, w = geometry(pm.math.sigmoid(position), pm.math.sigmoid(fraction), epsilon)
        pm.Deterministic("midpoint_cm", m, dims=("participant", "cell"))
        pm.Deterministic("width_cm", w, dims=("participant", "cell"))
        pm.Deterministic("sharpness_per_cm", 1/(4*w), dims=("participant", "cell"))
        q = pm.math.sigmoid((X-m[..., None])/w[..., None])-.5
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
        score = -.5*(logdet+quadratic)+np.log(2)+pm.logcdf(pm.Normal.dist(0., 1.), amp_mean/pt.sqrt(c11))
        pm.Potential("likelihood_at", pt.sum(score))
        for name, value in dict(base_mean=base_mean, base_variance=base_variance,
                offset_variance=offset_variance, offset_mean=base_mean+c00*v0+c01*v1,
                amp_mean=amp_mean, c00=c00, c01=c01, c11=c11).items():
            pm.Deterministic("conditional_"+name, value, dims=("participant", "cell"))
        # Nonlinear geometry couples location and width; latent coefficients are not cm effects.
        for metric in ("midpoint_cm", "sharpness_per_cm"):
            pm.Deterministic(metric+"_effect", pt.dot(W[:3], model[metric].mean(0)), dims="effect")
    return model


def sample(ids, at, baseline, epsilon, draws, tune, seed):
    model = make_model(ids, at, baseline, epsilon)
    started = time.monotonic()
    with model:
        trace = pm.sample(draws=draws, tune=tune, chains=4, cores=4, random_seed=seed,
            nuts_sampler="nutpie", nuts={"target_accept": .99, "adaptation": "diag"},
            progressbar=False, compute_convergence_checks=False)
    trace = directional.complete_trace(trace, True, seed+100)
    info, diag = directional.diagnostics(trace)
    info.update(epsilon=epsilon, chains=4, draws_per_chain=draws, tune=tune,
                seconds=time.monotonic()-started)
    return trace, info, diag


def prior_draws(epsilon, n):
    rng = np.random.default_rng(SEED+900)
    def latent():
        beta = rng.normal(0, 1.5, (5000, 4))
        tau = np.abs(rng.normal(0, 1., (5000, 4)))
        z = rng.normal(size=(5000, n, 4))
        return (beta[:, None]+tau[:, None]*z)@DESIGN.T
    m, w = geometry(special.expit(latent()), special.expit(latent()), epsilon)
    return {"midpoint_cm": m, "width_cm": w, "sharpness_per_cm": 1/(4*w)}


def fit_all():
    ids, at, baseline, _ = directional.primary_data()
    for name, epsilon in CONFIGS.items():
        attempts = []
        for draws, tune in ((3000, 3000), (6000, 6000)):
            trace, info, diag = sample(ids, at, baseline, epsilon, draws, tune, SEED+930)
            attempts.append(info)
            write_json(OUT / f"{name}_attempts.json", attempts)
            if info["gate"]:
                break
        posterior = trace["posterior"].dataset
        arrays = {key: var.values for key, var in posterior.data_vars.items()}
        arrays.update({"sample_stats__"+key: var.values for key, var in trace["sample_stats"].dataset.data_vars.items()})
        np.savez(LOCAL / f"{name}_draws.npz", **arrays)
        np.savez(LOCAL / f"{name}_prior.npz", **prior_draws(epsilon, len(ids)))
        diag.to_csv(OUT / f"{name}_diagnostics.csv")
        write_json(OUT / f"{name}_run.json", info)
        effects, simple, parameters = [], [], []
        for key, a in arrays.items():
            if "_effect" in key:
                effects.extend(directional.summarize_draws(a, name, key, EFFECTS[:3]))
        for quantity in ("midpoint_cm", "width_cm", "sharpness_per_cm", "amplitude", "corrected_intercept"):
            a = arrays[quantity].reshape(-1, len(ids), 4)
            q = np.quantile(a, [.025, .5, .975], axis=0)
            for i, pid in enumerate(ids):
                for c, cell in enumerate(CELL_NAMES):
                    parameters.append(dict(model=name, participant_id=pid, cell=cell, quantity=quantity,
                        median=q[1, i, c], ci_low=q[0, i, c], ci_high=q[2, i, c]))
            if quantity in ("midpoint_cm", "sharpness_per_cm"):
                simple.extend(directional.summarize_draws(a.mean(1)@W.T, name, quantity, EFFECTS))
        write_csv(OUT / f"{name}_effects.csv", effects)
        write_csv(OUT / f"{name}_simple_contrasts.csv", simple)
        write_csv(OUT / f"{name}_participant_parameters.csv", parameters)
        print(name, json.dumps(info), flush=True)


def crossvalidation():
    # The full directional reference has the same folds, trials, calibration and nuisance priors.
    ids, at, baseline, _ = directional.primary_data()
    na, ya, ssa = directional.sufficient(at/1000)
    records, output = [], OUT / "held_distance_predictions.csv"
    if output.exists():
        records = pd.read_csv(output).to_dict("records")
    completed = {r["held_distance_cm"] for r in records}
    for held, distance in enumerate(X):
        if distance in completed:
            continue
        train = at.copy()
        train[:, :, held] = np.nan
        attempts = []
        for draws, tune in ((1500, 1500), (6000, 3000)):
            trace, info, _ = sample(ids, train, baseline, .05, draws, tune, SEED+940+held)
            post = trace["posterior"].dataset
            mu = post["baseline_mean"].values+post["corrected_curve"].values[..., held]
            rhat = float(np.max(az.rhat(mu)))
            bulk = float(np.min(az.ess(mu)))
            tail = float(np.min(az.ess(mu, method="tail", prob=.05)))
            valid = bool(rhat <= 1.01 and min(bulk, tail) >= 400 and info["divergences"] == 0)
            attempts.append(dict(**info, prediction_rhat=rhat, prediction_bulk_ess=bulk,
                                 prediction_tail_ess=tail, prediction_gate=valid))
            if valid:
                break
        write_json(OUT / f"cv_{held}_diagnostics.json", attempts)
        mu = mu.reshape(-1, len(ids), 4)
        sigma = post["sigma_at"].values.reshape(-1, len(ids), 1)
        n, mean, sse = na[:, :, held], ya[:, :, held], ssa[:, :, held]
        logp = -.5*n*np.log(2*np.pi)-n*np.log(sigma)-.5*(sse+n*(mean-mu)**2)/sigma**2
        lpd = special.logsumexp(logp, axis=0)-np.log(len(mu))
        for i, pid in enumerate(ids):
            for c, cell in enumerate(CELL_NAMES):
                records.append(dict(model="visible95", held_distance_cm=distance, participant_id=pid, cell=cell,
                    predicted_AT_ms=1000*mu[:, i, c].mean(), observed_AT_ms=1000*mean[i, c],
                    error_ms=1000*(mu[:, i, c].mean()-mean[i, c]), block_log_predictive_density=lpd[i, c],
                    prediction_gate=valid))
        write_csv(output, records)
        print(f"CV visible95 held {distance:g}cm: Rhat={rhat:.4f}, ESS={bulk:.0f}/{tail:.0f}, gate={valid}", flush=True)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    LOCAL.mkdir(parents=True, exist_ok=True)
    {"fit": fit_all, "cv": crossvalidation}[sys.argv[1]]()
