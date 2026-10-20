"""Joint session-wide RT drift and PPS, retaining baseline and shape uncertainty."""
import ast
import hashlib
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

import run as unadjusted
from run import (ROOT, OUT, LOCAL, X, W, EFFECTS, CELL_NAMES, source, prepare, tensors,
                 mean_precision, directional, visible, write_csv, write_json)

CONFIGS = [("session_linear_raw_broad", 1, False, "broad"),
           ("session_linear_roll_broad", 1, True, "broad"),
           ("session_linear_raw_visible95", 1, False, "visible95"),
           ("session_linear_roll_visible95", 1, True, "visible95"),
           ("session_quadratic_raw_broad", 2, False, "broad")]


def definition_hash():
    tree = ast.parse(Path(__file__).read_text())
    names = {"time_arrays", "moments", "make_model"}
    text = unadjusted.definition_hash()+"\n"+"\n".join(ast.dump(node, include_attributes=False)
        for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names)
    return hashlib.sha256(text.encode()).hexdigest()


def time_arrays(rows, ids, people):
    planned = {r["participant_id"]: int(r["planned_trials"]) for r in people}
    timed = [{**r, "reaction_time_ms": str((int(r["trial_index"])-1)/(planned[r["participant_id"]]-1)-.5)}
             for r in rows]
    return tensors(timed, ids)


def moments(rt, trial_time, order):
    """Exact within-distance RT/time statistics, preserving irregular trial order."""
    assert np.array_equal(np.isfinite(rt), np.isfinite(trial_time))
    n, mean, sse = directional.sufficient(rt)
    features = np.stack([trial_time**j for j in range(1, order+1)], axis=-1)
    feature_mean = np.divide(np.nansum(features, axis=-2), n[..., None],
        out=np.zeros(n.shape+(order,)), where=n[..., None] > 0)
    centered_y = np.nan_to_num(rt-mean[..., None])
    centered_b = np.nan_to_num(features-feature_mean[..., None, :])
    cross = np.einsum("...t,...tk->...k", centered_y, centered_b)
    bb = np.einsum("...ti,...tj->...ij", centered_b, centered_b)
    return n, mean, sse, feature_mean, cross, bb


def make_model(ids, at, baseline, at_time, baseline_time, shape="broad", rolling=False, order=1):
    coords = {"participant": ids, "cell": CELL_NAMES, "distance": X,
        "coefficient": ("Intercept", *EFFECTS[:3]), "effect": EFFECTS[:3],
        "time_basis": ["linear", "quadratic"][:order]}
    na, ya0, ssa0, ta, ca, aa = moments(at/1000, at_time, order)
    nb, yb0, ssb0, tb, cb, bb = moments(baseline/1000, baseline_time, order)
    precision, ranks = mean_precision(na, rolling)
    effective_n = np.maximum(na-1, 0).sum(-1)+ranks
    nb_cp = nb.sum(-1)
    assert (nb_cp > 0).all()
    with pm.Model(coords=coords) as model:
        beta = pm.Normal("beta_time", 0., .2, dims="time_basis")
        tau = pm.HalfNormal("tau_time", .15, dims="time_basis")
        z = pm.Normal("z_time", 0., 1., dims=("participant", "time_basis"))
        trend = pm.Deterministic("time_trend", beta+tau*z, dims=("participant", "time_basis"))
        g = trend[:, None, None, :]
        ya = ya0-pt.sum(ta*g, -1)
        yb = yb0-pt.sum(tb*g, -1)
        ssa = ssa0-2*pt.sum(ca*g, -1)+pt.sum(aa*g[..., :, None]*g[..., None, :], (-1, -2))
        ssb = ssb0-2*pt.sum(cb*g, -1)+pt.sum(bb*g[..., :, None]*g[..., None, :], (-1, -2))
        sa = pm.LogNormal("sigma_at", np.log(.12), .5, dims="participant")
        sb = pm.LogNormal("sigma_baseline", np.log(.12), .5, dims="participant")
        va, vb = sa[:, None]**2, sb[:, None]**2
        syb = pt.sum(nb*yb, -1)
        bv = 1/(1/.4**2+nb_cp/vb)
        bm = bv*(.6/.4**2+syb/vb)
        brss, bsum = pt.sum(ssb+nb*(yb-.6)**2, -1), syb-.6*nb_cp
        pm.Potential("likelihood_baseline", pt.sum(-.5*(nb_cp*pt.log(vb)
            +pt.log1p(.4**2*nb_cp/vb)+brss/vb-bsum**2*bv/vb**2)))
        if shape == "broad":
            m = 10+90*directional.hierarchy("midpoint", len(ids), [.5, 0, 0, 0], .5, .35)
            w = 90*pt.exp(directional.hierarchy("log_width", len(ids), [np.log(1/6), 0, 0, 0], .7, .5))
            pm.Deterministic("population_midpoint_effect_cm", 90*model["beta_midpoint"][1:], dims="effect")
            pm.Deterministic("population_log_sharpness_effect", -model["beta_log_width"][1:], dims="effect")
        elif shape == "visible95":
            pos = pm.math.sigmoid(directional.hierarchy("position_fraction", len(ids), [0.]*4, 1.5, 1.))
            wid = pm.math.sigmoid(directional.hierarchy("width_fraction", len(ids), [0.]*4, 1.5, 1.))
            m, w = visible.geometry(pos, wid, .05)
        else:
            raise ValueError(shape)
        pm.Deterministic("midpoint_cm", m, dims=("participant", "cell"))
        pm.Deterministic("width_cm", w, dims=("participant", "cell"))
        pm.Deterministic("sharpness_per_cm", 1/(4*w), dims=("participant", "cell"))
        q = pm.math.sigmoid((X-m[..., None])/w[..., None])-.5
        mq = pt.sum(precision*q[..., None, :], axis=-1)
        n, sq, sqq = precision.sum((-1, -2)), pt.sum(mq, -1), pt.sum(q*mq, -1)
        ov, av = bv+.2**2, .15**2
        p00, p01, p11 = 1/ov+n/va, sq/va, 1/av+sqq/va
        det = p00*p11-p01*p01
        c00, c01, c11 = p11/det, -p01/det, p00/det
        centered = ya-bm[..., None]
        mc = pt.sum(precision*centered[..., None, :], axis=-1)
        v0, v1 = pt.sum(mc, -1)/va, pt.sum(q*mc, -1)/va
        rss = pt.sum(ssa, -1)+pt.sum(centered*mc, -1)
        quadratic = rss/va-(c00*v0*v0+2*c01*v0*v1+c11*v1*v1)
        logdet = effective_n*pt.log(va)+pt.log(det*ov*av)
        am = c01*v0+c11*v1
        pm.Potential("likelihood_at", pt.sum(-.5*(logdet+quadratic)+np.log(2)
            +pm.logcdf(pm.Normal.dist(0., 1.), am/pt.sqrt(c11))))
        for name, value in dict(base_mean=bm, base_variance=bv, offset_variance=ov,
                offset_mean=bm+c00*v0+c01*v1, amp_mean=am, c00=c00, c01=c01, c11=c11).items():
            pm.Deterministic("conditional_"+name, value, dims=("participant", "cell"))
        for quantity in ("midpoint_cm", "sharpness_per_cm"):
            pm.Deterministic(quantity+"_effect", pt.dot(W[:3], model[quantity].mean(0)), dims="effect")
    return model


def sample(ids, at, baseline, at_time, baseline_time, shape, rolling, order, draws, tune, seed):
    model = make_model(ids, at, baseline, at_time, baseline_time, shape, rolling, order)
    start = time.monotonic()
    with model:
        trace = pm.sample(draws=draws, tune=tune, chains=4, cores=4, random_seed=seed,
            nuts_sampler="nutpie", nuts={"target_accept": .99, "adaptation": "diag"},
            progressbar=False, compute_convergence_checks=False)
    trace = directional.complete_trace(trace, True, seed+100)
    info, diag = directional.diagnostics(trace)
    info.update(seconds=time.monotonic()-start, shape=shape, rolling=rolling, time_order=order,
        chains=4, draws_per_chain=draws, tune=tune, definition_sha256=definition_hash(),
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), seed=seed)
    return trace, info, diag


def fit_all():
    people, _, eligible, _, ids, _ = source()
    rows, _, _ = prepare(eligible)
    at, baseline = tensors(rows, ids)
    at_time, baseline_time = time_arrays(rows, ids, people)
    for j, (name, order, rolling, shape) in enumerate(CONFIGS):
        path = OUT / f"{name}_run.json"
        if path.exists():
            assert json.loads(path.read_text())["definition_sha256"] == definition_hash()
            continue
        attempts = []
        for draws, tune in ((2000, 2000), (4000, 4000)):
            trace, info, diag = sample(ids, at, baseline, at_time, baseline_time, shape, rolling, order,
                                       draws, tune, 20261420+j)
            attempts.append(info)
            write_json(OUT / f"{name}_attempts.json", attempts)
            if info["gate"]:
                break
        post = trace["posterior"].dataset
        keys = [k for k in post if "_effect" in k]+["midpoint_cm", "width_cm", "sharpness_per_cm",
            "amplitude", "corrected_intercept", "baseline_mean", "sigma_at", "sigma_baseline",
            "corrected_curve", "time_trend", "beta_time"]
        arrays = {k: post[k].values for k in keys}
        np.savez(LOCAL / f"{name}_draws.npz", **arrays)
        diag.to_csv(OUT / f"{name}_diagnostics.csv")
        write_json(path, info)
        effects, simple, parameters = [], [], []
        for key in keys:
            if "_effect" in key:
                effects.extend(directional.summarize_draws(arrays[key], name, key, EFFECTS[:3]))
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
    people, _, eligible, _, ids, _ = source()
    target_at, _ = tensors(eligible, ids)
    target_time, _ = time_arrays(eligible, ids, people)
    n, y, ss, tm, cross, xx = moments(target_at/1000, target_time, 1)
    path = OUT / "session_held_distance_predictions.csv"
    records = pd.read_csv(path).to_dict("records") if path.exists() else []
    completed = {r["held_distance_cm"] for r in records}
    for held, distance in enumerate(X):
        if distance in completed:
            assert json.loads((OUT/f"session_cv_{held}.json").read_text())[-1]["definition_sha256"] == definition_hash()
            continue
        rows, _, _ = prepare(eligible, held=distance)
        at, baseline = tensors(rows, ids)
        at_time, baseline_time = time_arrays(rows, ids, people)
        assert not np.isfinite(at[:, :, held]).any()
        attempts = []
        for draws, tune in ((1000, 1000), (3000, 2000)):
            trace, info, _ = sample(ids, at, baseline, at_time, baseline_time, "broad", False, 1,
                                       draws, tune, 20261520+held)
            post = trace["posterior"].dataset
            coefficient = post.time_trend.values[..., 0]
            base_mu = post.baseline_mean.values+post.corrected_curve.values[..., held]
            mu = base_mu+coefficient[..., None]*tm[:, :, held, 0]
            rhat, bulk, tail = float(np.max(az.rhat(mu))), float(np.min(az.ess(mu))), float(np.min(az.ess(mu, method="tail", prob=.05)))
            valid = bool(rhat <= 1.01 and min(bulk, tail) >= 400 and info["divergences"] == 0)
            info.update(prediction_rhat=rhat, prediction_bulk_ess=bulk, prediction_tail_ess=tail, prediction_gate=valid)
            attempts.append(info)
            if valid:
                break
        write_json(OUT / f"session_cv_{held}.json", attempts)
        g = coefficient.reshape(-1, len(ids), 1)
        sigma = post.sigma_at.values.reshape(-1, len(ids), 1)
        base_mu = base_mu.reshape(-1, len(ids), 4)
        adjusted_mean = y[:, :, held]-g*tm[:, :, held, 0]
        adjusted_ss = ss[:, :, held]-2*g*cross[:, :, held, 0]+g*g*xx[:, :, held, 0, 0]
        lp = -.5*n[:, :, held]*np.log(2*np.pi)-n[:, :, held]*np.log(sigma)-.5*(
            adjusted_ss+n[:, :, held]*(adjusted_mean-base_mu)**2)/sigma**2
        lpd = special.logsumexp(lp, axis=0)-np.log(len(g))
        predicted = mu.reshape(-1, len(ids), 4).mean(0)
        for i, pid in enumerate(ids):
            for c, cell in enumerate(CELL_NAMES):
                records.append(dict(model="session_linear_raw_broad", held_distance_cm=distance,
                    participant_id=pid, cell=cell, n_target=int(n[i, c, held]),
                    observed_AT_ms=1000*y[i, c, held], predicted_AT_ms=1000*predicted[i, c],
                    error_ms=1000*(predicted[i, c]-y[i, c, held]), block_log_predictive_density=lpd[i, c],
                    prediction_gate=valid, full_parameter_gate=info["gate"]))
        write_csv(path, records)
        print(f"CV session linear {distance:g}cm: Rhat={rhat:.4f} ESS={bulk:.0f}/{tail:.0f} gate={valid}", flush=True)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    LOCAL.mkdir(parents=True, exist_ok=True)
    {"fit": fit_all, "cv": crossvalidation}[sys.argv[1]]()
