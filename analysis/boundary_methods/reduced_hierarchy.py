"""Run reduced midpoint hierarchies on the existing joint trial likelihood."""

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import arviz as az
import numpy as np
import pymc as pm
import pytensor.tensor as pt
from scipy.special import expit, logsumexp

from screen import DISTANCES, ROOT, W, cohort_mask, load_data
from baseline_effects import DESIGN
from check_baseline_fits import simulate
from joint_pps import make_marginal_model, make_model, sufficient

REDUCTIONS = {
    "shared_width": ((0, 1, 2, 3), False),
    "reduced_condition": ((0, 1), False),
    "reduced_condition_width": ((0, 1), True),
    "shared_contrasts": ((0,), False),
    "shared_location": ((0,), False),
}
REFERENCES = ("constant", "linear", "log_distance")
CALIBRATIONS = ("pooled_marginal","no_baseline","pooled_joint","same_label_joint",
                "positive_no_time","positive_linear_time")
LOCAL = ROOT / ".for-ai-local" / "boundary-hierarchy"
SEED = 20261121


def reduce_shape(parent, n, model, prior_scale):
    """Replace only the midpoint random effects and width terms."""
    varying, person_width = REDUCTIONS[model]
    vary = np.asarray(varying)
    with parent:
        tau = pm.HalfNormal("retained_midpoint_sd", .35*prior_scale, shape=len(vary))
        z = pm.Normal("retained_midpoint_z", 0, 1, shape=(n,len(vary)))
        substitutions = {
            "tau_midpoint": pt.set_subtensor(pt.zeros(4)[vary], tau),
            "z_midpoint": pt.set_subtensor(pt.zeros((n,4))[:,vary], z),
        }
        expected_free = {"retained_midpoint_sd", "retained_midpoint_z"}
        if model == "shared_location":
            midpoint = pm.Normal("shared_midpoint_intercept", .5, .5*prior_scale)
            substitutions["beta_midpoint"] = pt.set_subtensor(pt.zeros(4)[0], midpoint)
            expected_free.add("shared_midpoint_intercept")
        else:
            betaw = pm.Normal("shared_log_width", np.log(1/6), .7*prior_scale)
            sd_w = np.zeros(4)
            z_w = np.zeros((n,4))
            if person_width:
                sd_w = pt.set_subtensor(pt.zeros(4)[0], pm.HalfNormal("shared_width_sd", .5*prior_scale))
                z_w = pt.set_subtensor(pt.zeros((n,4))[:,0], pm.Normal("shared_width_z", 0, 1, shape=n))
            substitutions.update(beta_log_width=pt.set_subtensor(pt.zeros(4)[0], betaw),
                                 tau_log_width=sd_w, z_log_width=z_w)
            expected_free.add("shared_log_width")
    changed = pm.do(parent, substitutions)
    names = {rv.name for rv in changed.free_RVs}
    if not expected_free <= names or names.intersection(substitutions):
        raise RuntimeError(f"Unexpected free variables after shape reduction: {sorted(names)}")
    return changed


def build_model(ids, at, baseline, name, prior_scale, calibration="pooled_marginal", timing=None):
    if name in REFERENCES:
        if calibration != "pooled_marginal":
            raise ValueError("The matched boundary-free references use the primary marginal likelihood.")
        return make_marginal_model(ids, at, baseline, prior_scale=prior_scale, family=name)
    if calibration in ("pooled_marginal","no_baseline"):
        calibration_data = np.full_like(baseline,np.nan) if calibration=="no_baseline" else baseline
        parent = make_marginal_model(ids, at, calibration_data, prior_scale=prior_scale)
    elif calibration in ("pooled_joint","same_label_joint"):
        correction = "pooled_cp" if calibration=="pooled_joint" else "same_label"
        parent = make_model(ids, at, baseline, correction=correction, prior_scale=prior_scale)
    else:
        session, at_time, b_time = timing
        if calibration == "positive_linear_time":
            parent = session.make_model(ids, at, baseline, at_time, b_time, order=1)
        else:
            parent = session.unadjusted.make_model(ids, at, baseline)
    if name == "full":
        return parent
    return reduce_shape(parent, len(ids), name, prior_scale)


def diagnostic(array):
    rank = np.asarray(az.rhat(array, method="rank"))
    bulk = np.asarray(az.ess(array, method="bulk"))
    tail = np.asarray(az.ess(array, method="tail"))
    if not all(np.isfinite(a).all() for a in (rank, bulk, tail)):
        return dict(max_rhat=None, min_bulk=None, min_tail=None)
    return dict(max_rhat=float(rank.max()), min_bulk=float(bulk.min()), min_tail=float(tail.min()))


def held_predictions(posterior, data, args, timing):
    base = posterior["baseline_mean"].values
    if args.calibration == "same_label_joint":
        base = base[...,args.held]
    target = posterior["corrected_curve"].values[...,args.held] + base
    count, observed, ss = (array[:,:,args.held] for array in sufficient(data[1]/1000))
    mu = target.reshape(-1,*target.shape[2:])
    sd = posterior["sigma_at"].values.reshape(len(mu),len(data[0]),1)
    if args.calibration == "positive_linear_time":
        session, times = timing
        tm, cross, xx = [array[:,:,args.held] for array in session.moments(data[1]/1000, times, 1)[3:]]
        trend = posterior["time_trend"].values.reshape(len(mu),len(data[0]),1)
        mu += trend*tm[...,0]
        ss = ss-2*trend*cross[...,0]+trend**2*xx[...,0,0]
    lpd = -.5*count*np.log(2*np.pi) - count*np.log(sd) - .5*(ss+count*(observed-mu)**2)/sd**2
    residual = (mu.mean(0)-observed)*1000
    return dict(
        log_score_per_trial=float((logsumexp(lpd,axis=0)-np.log(len(mu))).sum()/count.sum()),
        rmse_individual_ms=float(np.sqrt(np.mean(residual**2))),
        rmse_group_ms=float(np.sqrt(np.mean(residual.mean(0)**2))),
        target_trials=int(count.sum()),
    )


def summarize(trace, prior, name, data, elapsed, args, audit, definition_sha, truth=None, timing=None):
    d = trace["posterior"].dataset
    stats = trace["sample_stats"].dataset
    targets = {"corrected_curve":diagnostic(d["corrected_curve"])}
    if name not in REFERENCES:
        variables = ("midpoint_cm","sharpness_per_cm")
        if name != "shared_location":
            variables += ("beta_midpoint","population_midpoint_effect_cm")
        targets.update({key:diagnostic(d[key]) for key in variables})
    ndiv = int(stats["diverging"].values.sum())
    gates = all(x["max_rhat"] is not None and x["max_rhat"]<=1.01 and min(x["min_tail"],x["min_bulk"])>=400
                for x in targets.values())
    receipt = dict(
        model=name, calibration=args.calibration, seconds=elapsed, diagnostic_pass=bool(gates and ndiv==0),
        divergences=ndiv, target_diagnostics=targets, prior_scale=args.prior_scale,
        chains=args.chains, tune=args.tune, draws=args.draws, held_distance=args.held,
        input=audit, cohort_size=len(data[0]), local_definition_sha256=definition_sha,
    )
    if args.held is not None:
        receipt["held_predictions"] = held_predictions(d,data,args,timing)
    if name in REFERENCES:
        return receipt
    cm = d["midpoint_cm"].values
    effects = cm.mean(-2) @ W.T
    curves = d["corrected_curve"].values
    sharpness = d["sharpness_per_cm"].values
    if name == "shared_location":
        if not np.allclose(cm,cm[..., :1],atol=1e-12,rtol=0):
            raise RuntimeError("Reduced fit violates the common midpoint restriction.")
    elif name != "full":
        if not np.allclose(sharpness, sharpness[..., :1], atol=1e-12, rtol=0):
            raise RuntimeError("Reduced fit violates shared within-person width.")
        if not REDUCTIONS[name][1] and not np.allclose(sharpness, sharpness[..., :1, :1], atol=1e-12, rtol=0):
            raise RuntimeError("Reduced fit violates shared population width.")
        contrast_rows = W[:3] if name == "shared_contrasts" else W[1:3]
        fixed_contrasts = cm @ contrast_rows.T
        if len(REDUCTIONS[name][0]) < 4 and not np.allclose(fixed_contrasts, fixed_contrasts[..., :1, :], atol=1e-10):
            raise RuntimeError("Reduced fit violates imposed cross-person phase contrast equality.")
    def qs(a):
        return np.quantile(a, [.025,.5,.975], axis=(0,1)).round(6).tolist()
    receipt.update(
        posterior_mean_phase_cells_cm=qs(cm.mean(-2)), population_condition_phase_interaction_cm=qs(d["population_midpoint_effect_cm"].values),
        paired_fixed_sample_effects_cm=qs(effects),
        participant_fraction_inside=float(((cm>=10)&(cm<=100)).mean()),
        group_predicted_curve_ms=qs(curves.mean(-3)*1000),
        population_prior_effects_cm=qs(prior[0][None, ...]),
        participant_prior_fraction_inside=float(((prior[1]>=10)&(prior[1]<=100)).mean()),
        median_observed_span_ms=qs((curves[..., -1]-curves[...,0]).mean(-2)*1000),
    )
    if args.scenario != "observed":
        receipt["recovery"] = dict(scenario=args.scenario, replicate=args.replicate)
        if truth is not None:
            person = qs(cm)
            corrected_truth = truth["midpoint_cm"]
            population = d["population_midpoint_effect_cm"].values
            pop_interval = np.array(qs(population))
            pop_truth = truth["population_midpoint_effect_cm"]
            effect = np.array(qs(cm @ W[:3].T))
            true_effect = corrected_truth @ W[:3].T
            receipt["recovery"].update(
                individual_midpoint_interval_fraction=float(
                    ((person[0]<=corrected_truth)&(corrected_truth<=person[2])).mean()),
                individual_midpoint_rmse_cm=float(np.sqrt(np.mean((person[1]-corrected_truth)**2))),
                individual_effect_rmse_cm=np.sqrt(np.mean((effect[1]-true_effect)**2,axis=0)).tolist(),
                population_effects_truth_cm=pop_truth.tolist(),
                population_effects_covered=((pop_interval[0]<=pop_truth)&(pop_truth<=pop_interval[2])).tolist(),
            )
    return receipt


def simulated_trials(at, baseline, scenario, replicate):
    generator = "flat" if scenario == "flat" else "known200"
    a, b, truth = simulate(at, baseline, generator, SEED+100+replicate)
    if scenario == "flat":
        return a, b, None
    if scenario == "heterogeneous_width":
        return a, b, truth
    m = truth["midpoint_cm"]
    w = 1/(4*truth["sharpness_per_cm"])
    x = DISTANCES["registered"]
    coef = m @ np.linalg.inv(DESIGN.T)
    coef[:,2:] = truth["population_midpoint_effect_cm"][1:]
    midpoint = coef @ DESIGN.T
    theoretical_width = 15.
    old_basis = expit((x-m[...,None])/w[...,None])
    new_basis = expit((x-midpoint[...,None])/theoretical_width)
    amplitude_ms = 40. if scenario == "weak_shared_width" else 200.
    a += (amplitude_ms*(new_basis-.5)-200*(old_basis-.5))[...,None]
    return a, b, dict(truth, midpoint_cm=midpoint, sharpness_per_cm=np.full_like(m, 1/(4*theoretical_width)))


def sample(args):
    definition_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    ids, at, base, audit = load_data()
    mask = cohort_mask(ids,"primary40")
    ids, at, base = ids[mask], at[mask], base[mask]
    time_mode = args.calibration.startswith("positive")
    if time_mode and (args.scenario != "observed" or args.prior_scale != 1):
        raise ValueError("Session-time sensitivity uses the observed-data broad prior at its original scale.")
    if args.scenario == "observed":
        truth = None
    else:
        at, base, truth = simulated_trials(at, base, args.scenario, args.replicate)
    timing, target_time = None, None
    if time_mode:
        sys.path.insert(0,str(ROOT/"analysis/trial_cleaning"))
        import session_time as session

        people, _, eligible, _, timed_ids, _ = session.source()
        np.testing.assert_array_equal(ids,timed_ids)
        distance = DISTANCES["registered"][args.held] if args.held is not None else None
        rows, _, _ = session.prepare(eligible, held=distance)
        training, base = session.tensors(rows, ids)
        at_time, b_time = session.time_arrays(rows, ids, people)
        timing = (session, at_time, b_time)
        if args.held is not None:
            at, _ = session.tensors(eligible, ids)
            target_time = (session, session.time_arrays(eligible, ids, people)[0])
    else:
        training = at.copy()
        if args.held is not None:
            training[:,:,args.held,:] = np.nan
    model = build_model(ids, training, base, args.model, args.prior_scale, args.calibration, timing)
    print(f"Built {args.model}: {len(model.free_RVs)} random variable blocks.", flush=True)
    with model:
        if not np.isfinite(model.compile_logp()(model.initial_point())):
            raise RuntimeError("Invalid initial likelihood.")
        if args.check_only:
            return
        prior = None if args.model in REFERENCES else pm.draw(
            [model["population_midpoint_effect_cm"],model["midpoint_cm"]], draws=512, random_seed=SEED)
        started = time.monotonic()
        trace = pm.sample(draws=args.draws, tune=args.tune, chains=args.chains, cores=args.cores,
                          random_seed=SEED, nuts_sampler="nutpie",
                          nuts={"target_accept":args.accept, "adaptation":"diag"},
                          progressbar=False, compute_convergence_checks=False)
    if time_mode:
        trace = session.directional.complete_trace(trace, True, SEED+601)
    out = summarize(trace, prior, args.model, (ids,at,base), time.monotonic()-started, args, audit,
                    definition_sha, truth, target_time)
    d = trace["posterior"].dataset
    LOCAL.mkdir(parents=True, exist_ok=True)
    tag = f"{args.model}_{args.prior_scale:g}_hold{args.held}_{args.draws}x{args.chains}"
    if args.calibration != "pooled_marginal":
        tag += f"_{args.calibration}"
    if args.scenario != "observed":
        tag += f"_{args.scenario}_{args.replicate}"
    (LOCAL/f"{tag}.json").write_text(json.dumps(out, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    if args.held is None:
        np.savez_compressed(LOCAL/f"{tag}.npz", ids=ids, **{
            k:d[k].values for k in ("midpoint_cm","sharpness_per_cm","corrected_curve","baseline_mean","amplitude","sigma_at")
            if k in d})
    print(f"{tag}: {out['seconds']:.1f}s, diagnostics {out['diagnostic_pass']}, divergences {out['divergences']}.", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", choices=("full", *REDUCTIONS, *REFERENCES))
    parser.add_argument("--prior-scale", type=float, default=1.)
    parser.add_argument("--held", type=int, choices=range(5))
    parser.add_argument("--calibration", choices=CALIBRATIONS, default="pooled_marginal")
    parser.add_argument("--scenario", choices=("observed","flat","weak_shared_width","shared_width","heterogeneous_width"), default="observed")
    parser.add_argument("--replicate", type=int, default=0)
    parser.add_argument("--draws", type=int, default=1500)
    parser.add_argument("--tune", type=int, default=1500)
    parser.add_argument("--chains", type=int, default=4)
    parser.add_argument("--cores", type=int, default=4)
    parser.add_argument("--accept", type=float, default=.95)
    parser.add_argument("--check-only", action="store_true")
    sample(parser.parse_args())
