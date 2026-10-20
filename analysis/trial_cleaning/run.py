"""Fixed, exploratory trial-cleaning and rolling-average sensitivity analyses."""
import ast
import csv
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

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis/visible_sigmoid"))
import fit as visible
directional = visible.directional
from paper_analysis import clean, numeric, interaction, safe_call
from baseline_effects import test_batch

X, W, EFFECTS, CELL_NAMES = directional.X, directional.W, directional.EFFECTS, directional.CELL_NAMES
SOA_DISTANCE = dict(zip((300., 800., 1500., 2200., 2700.), (100., 73., 50., 27., 10.)))
write_csv, write_json = directional.write_csv, directional.write_json
OUT, LOCAL = ROOT / "results/trial_cleaning", ROOT / ".for-ai-local/trial_cleaning"
CONFIGS = [(f"{period}_{method}_{shape}", period == "early", method == "roll", shape)
           for period in ("full", "early") for method in ("raw", "roll")
           for shape in ("broad", "visible95")]
SEED = 20261020


def definition_hash():
    """Resume only unchanged data/model definitions; diagnostic API fixes are separate."""
    names = {"source", "trim", "prepare", "tensors", "mean_precision", "make_model"}
    tree = ast.parse(Path(__file__).read_text())
    parts = [ast.dump(node, include_attributes=False) for node in tree.body
             if isinstance(node, ast.FunctionDef) and node.name in names]
    return hashlib.sha256("\n".join(parts).encode()).hexdigest()


def source():
    loaded = []
    for name in ("study5_participants.csv", "study5_pps_trials.csv"):
        with (ROOT / "data/raw" / name).open() as stream:
            loaded.append(list(csv.DictReader(stream)))
    people, trials = loaded
    old, quality, counts = clean(people, trials)
    excluded = {r["participant_id"] for r in quality if r["excluded_catch"]}
    eligible = [r for r in trials if r["participant_id"] not in excluded
        and r["trial_type"] in ("Audio-Tactile", "Baseline") and r["outcome"] == "hit"
        and r["response_given"] == "True" and np.isfinite(numeric(r, "reaction_time_ms"))]
    ids = sorted(p["participant_id"] for p in people
                 if p["participant_id"] not in excluded | {"P011", "P033"})
    return people, trials, eligible, old, ids, counts


def trim(rows, keys):
    """One inclusive sample-SD pass; never iterate toward a desired curve."""
    frame = pd.DataFrame(rows)
    frame["rt"] = frame.reaction_time_ms.astype(float)
    group = frame.groupby(keys).rt
    means, sds, ns = group.transform("mean"), group.transform("std"), group.transform("size")
    z = (frame.rt-means)/sds
    keep = (ns < 2) | (sds == 0) | ((frame.rt >= means-2.5*sds) & (frame.rt <= means+2.5*sds))
    details = pd.DataFrame(dict(trial_id=frame.trial_id, mean_ms=means, sd_ms=sds, n=ns,
                                z=z, keep=keep))
    return [r for r, ok in zip(rows, keep) if ok], details


def prepare(eligible, early=False, local=True, held=None):
    subset = [r for r in eligible if (not early or int(r["block_number"]) <= 3)
        and not (held is not None and r["trial_type"] == "Audio-Tactile"
                 and SOA_DISTANCE[float(r["soa_ms"])] == held)]
    global_rows, global_details = trim(subset, ["participant_id"])
    local_rows, local_details = trim(global_rows,
        ["participant_id", "condition", "phase", "soa_ms", "trial_type"])
    return (local_rows if local else global_rows), global_details, local_details


def tensors(rows, ids):
    output = []
    index = {pid: i for i, pid in enumerate(ids)}
    for kind in ("Audio-Tactile", "Baseline"):
        groups = {}
        for r in rows:
            if r["participant_id"] in index and r["trial_type"] == kind:
                key = (index[r["participant_id"]], CELL_NAMES.index(r["condition"]+" "+r["phase"]),
                       list(X).index(SOA_DISTANCE[float(r["soa_ms"])]))
                groups.setdefault(key, []).append(float(r["reaction_time_ms"]))
        a = np.full((len(ids), 4, 5, max(map(len, groups.values()), default=1)), np.nan)
        for key, values in groups.items():
            a[key][:len(values)] = values
        output.append(a)
    return output


def mean_precision(counts, rolling):
    """Exact precision on original means after observing H*means, including overlap."""
    matrices, ranks = np.zeros(counts.shape+(5,)), np.zeros(counts.shape[:-1], int)
    h = np.eye(5)
    if rolling:
        h = (np.eye(5)[:-1]+np.eye(5)[1:])/2
    for index in np.ndindex(counts.shape[:-1]):
        n = counts[index]
        transform = h[np.all((h == 0) | (n[None, :] > 0), axis=1)]
        if not len(transform):
            continue
        covariance = (transform/np.maximum(n, 1))@transform.T
        matrices[index] = transform.T@np.linalg.solve(covariance, transform)
        ranks[index] = len(transform)
    return matrices, ranks


def make_model(ids, at, baseline, shape="broad", rolling=False):
    coords = {"participant": ids, "cell": CELL_NAMES, "distance": X,
              "coefficient": ("Intercept", *EFFECTS[:3]), "effect": EFFECTS[:3]}
    na, ya, ssa = directional.sufficient(at/1000)
    nb, yb, ssb = directional.sufficient(baseline/1000)
    precision, ranks = mean_precision(na, rolling)
    effective_n = np.maximum(na-1, 0).sum(-1)+ranks
    nb_cp, syb = nb.sum(-1), (nb*yb).sum(-1)
    assert (nb_cp > 0).all(), "Every inference cell needs independent Baseline calibration"
    with pm.Model(coords=coords) as model:
        sa = pm.LogNormal("sigma_at", np.log(.12), .5, dims="participant")
        sb = pm.LogNormal("sigma_baseline", np.log(.12), .5, dims="participant")
        va, vb = sa[:, None]**2, sb[:, None]**2
        bv = 1/(1/.4**2+nb_cp/vb)
        bm = bv*(.6/.4**2+syb/vb)
        brss, bsum = np.sum(ssb+nb*(yb-.6)**2, -1), syb-.6*nb_cp
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
        rss = ssa.sum(-1)+pt.sum(centered*mc, -1)
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


def sample(ids, at, baseline, shape, rolling, draws, tune, seed):
    model = make_model(ids, at, baseline, shape, rolling)
    started = time.monotonic()
    with model:
        trace = pm.sample(draws=draws, tune=tune, chains=4, cores=4, random_seed=seed,
            nuts_sampler="nutpie", nuts={"target_accept": .99, "adaptation": "diag"},
            progressbar=False, compute_convergence_checks=False)
    trace = directional.complete_trace(trace, True, seed+100)
    info, diag = directional.diagnostics(trace)
    info.update(seconds=time.monotonic()-started, shape=shape, rolling=rolling,
                chains=4, draws_per_chain=draws, tune=tune,
                definition_sha256=definition_hash(),
                model_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    return trace, info, diag


def fit_all():
    _, _, eligible, old, ids, _ = source()
    full_global, _, _ = prepare(eligible, local=False)
    assert {r["trial_id"] for r in full_global} == {r["trial_id"] for r in old}
    for j, (name, early, rolling, shape) in enumerate(CONFIGS):
        if (OUT / f"{name}_run.json").exists():
            assert json.loads((OUT/f"{name}_run.json").read_text())["definition_sha256"] == definition_hash()
            continue
        rows, _, _ = prepare(eligible, early)
        at, baseline = tensors(rows, ids)
        attempts = []
        for draws, tune in ((2000, 2000), (4000, 4000)):
            trace, info, diag = sample(ids, at, baseline, shape, rolling, draws, tune, SEED+100+j)
            attempts.append(info)
            write_json(OUT / f"{name}_attempts.json", attempts)
            if info["gate"]:
                break
        post = trace["posterior"].dataset
        keys = [k for k in post if "_effect" in k] + ["midpoint_cm", "width_cm", "sharpness_per_cm",
            "amplitude", "corrected_intercept", "baseline_mean", "sigma_at", "sigma_baseline", "corrected_curve"]
        arrays = {k: post[k].values for k in keys}
        np.savez(LOCAL / f"{name}_draws.npz", **arrays)
        diag.to_csv(OUT / f"{name}_diagnostics.csv")
        write_json(OUT / f"{name}_run.json", info)
        effects, simple, parameters = [], [], []
        for key in keys:
            if "_effect" in key:
                effects.extend(directional.summarize_draws(arrays[key], name, key, EFFECTS[:3]))
        for quantity in ("midpoint_cm", "width_cm", "sharpness_per_cm", "amplitude", "corrected_intercept"):
            values = arrays[quantity].reshape(-1, len(ids), 4)
            quantiles = np.quantile(values, [.025, .5, .975], axis=0)
            for i, pid in enumerate(ids):
                for c, cell in enumerate(CELL_NAMES):
                    parameters.append(dict(model=name, participant_id=pid, cell=cell, quantity=quantity,
                        median=quantiles[1, i, c], ci_low=quantiles[0, i, c], ci_high=quantiles[2, i, c]))
            if quantity in ("midpoint_cm", "sharpness_per_cm"):
                simple.extend(directional.summarize_draws(values.mean(1)@W.T, name, quantity, EFFECTS))
        write_csv(OUT / f"{name}_effects.csv", effects)
        write_csv(OUT / f"{name}_simple_contrasts.csv", simple)
        write_csv(OUT / f"{name}_participant_parameters.csv", parameters)
        print(name, json.dumps(info), flush=True)


def crossvalidation():
    _, _, eligible, _, ids, _ = source()
    output = OUT / "held_distance_predictions.csv"
    records = pd.read_csv(output).to_dict("records") if output.exists() else []
    completed = {(r["model"], r["held_distance_cm"]) for r in records}
    source_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    for j, (name, local, rolling) in enumerate((("global_raw", False, False),
            ("local_raw", True, False), ("local_roll", True, True))):
        for held, distance in enumerate(X):
            if (name, distance) in completed:
                info = json.loads((OUT / f"cv_{name}_{held}.json").read_text())[-1]
                assert info["definition_sha256"] == definition_hash()
                continue
            rows, _, _ = prepare(eligible, local=local, held=distance)
            at, baseline = tensors(rows, ids)
            assert not np.isfinite(at[:, :, held]).any()
            target_at, _ = tensors(eligible, ids)
            nt, yt, sst = directional.sufficient(target_at/1000)
            attempts = []
            for draws, tune in ((1000, 1000), (3000, 2000)):
                trace, info, _ = sample(ids, at, baseline, "broad", rolling, draws, tune, SEED+200+j*5+held)
                post = trace["posterior"].dataset
                mu = post.baseline_mean.values+post.corrected_curve.values[..., held]
                rhat, bulk, tail = float(np.max(az.rhat(mu))), float(np.min(az.ess(mu))), float(np.min(az.ess(mu, method="tail", prob=.05)))
                valid = bool(rhat <= 1.01 and min(bulk, tail) >= 400 and info["divergences"] == 0)
                info.update(prediction_rhat=rhat, prediction_bulk_ess=bulk,
                            prediction_tail_ess=tail, prediction_gate=valid)
                attempts.append(info)
                if valid:
                    break
            write_json(OUT / f"cv_{name}_{held}.json", attempts)
            mu = mu.reshape(-1, len(ids), 4)
            sigma = post.sigma_at.values.reshape(-1, len(ids), 1)
            n, y, sse = nt[:, :, held], yt[:, :, held], sst[:, :, held]
            lp = -.5*n*np.log(2*np.pi)-n*np.log(sigma)-.5*(sse+n*(y-mu)**2)/sigma**2
            lpd = special.logsumexp(lp, axis=0)-np.log(len(mu))
            for i, pid in enumerate(ids):
                for c, cell in enumerate(CELL_NAMES):
                    records.append(dict(model=name, held_distance_cm=distance, participant_id=pid, cell=cell,
                        n_target=int(n[i, c]), observed_AT_ms=1000*y[i, c],
                        predicted_AT_ms=1000*mu[:, i, c].mean(), error_ms=1000*(mu[:, i, c].mean()-y[i, c]),
                        block_log_predictive_density=lpd[i, c], prediction_gate=valid,
                        full_parameter_gate=info["gate"]))
            write_csv(output, records)
            print(f"CV {name} {distance:g}cm: Rhat={rhat:.4f} ESS={bulk:.0f}/{tail:.0f} gate={valid}", flush=True)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    LOCAL.mkdir(parents=True, exist_ok=True)
    {"fit": fit_all, "cv": crossvalidation}[sys.argv[1]]()
