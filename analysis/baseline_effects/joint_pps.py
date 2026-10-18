"""Native joint baseline/AT hierarchical models. Requires PyMC and nutpie.

Gaussian fits use exact trial sufficient statistics, including within-cell SSE.
Student-t fits use every retained trial. Baseline uncertainty is shared correctly.
"""
import argparse
import json
import time

import arviz as az
import numpy as np
import pymc as pm
import pytensor.tensor as pt

from baseline_effects import (OUT, LOCAL, SEED, DESIGN, W, EFFECTS, CELL_NAMES,
    DISTANCES, load_data, cohort_mask, write_json, write_csv, test_batch)


def sufficient(tensor):
    n = np.isfinite(tensor).sum(-1)
    mean = np.divide(np.nansum(tensor, axis=-1), n, out=np.zeros(n.shape), where=n > 0)
    sse = np.nansum((tensor-mean[..., None])**2, axis=-1)
    return n, mean, sse


def hierarchy(name, n, center, fixed_sd, random_sd):
    beta = pm.Normal("beta_"+name, np.asarray(center), fixed_sd, dims="coefficient")
    tau = pm.HalfNormal("tau_"+name, random_sd, dims="coefficient")
    z = pm.Normal("z_"+name, 0, 1, dims=("participant", "coefficient"))
    return pt.dot(beta+z*tau, DESIGN.T)


def make_marginal_model(ids, at, baseline, prior_scale=1., cell_noise=False):
    """Integrate independent Gaussian nuisance priors exactly, then draw conditionals.

    This is an explicitly different nuisance-pooling sensitivity, not a silent
    change to the primary model. The shape hierarchy and shared baseline remain.
    """
    coordinates = {"participant": ids, "cell": CELL_NAMES, "distance": DISTANCES["registered"],
        "coefficient": ("Intercept", *EFFECTS[:3]), "effect": EFFECTS[:3], "nuisance": ("offset", "amplitude", "baseline")}
    na, ya, ssa = sufficient(at/1000)
    nb, yb, ssb = sufficient(baseline/1000)
    nb_cp, syb = nb.sum(-1), (nb*yb).sum(-1)
    with pm.Model(coords=coordinates) as model:
        noise_dims = ("participant", "cell") if cell_noise else "participant"
        sa = pm.LogNormal("sigma_at", np.log(.12), .5, dims=noise_dims)
        sb = pm.LogNormal("sigma_baseline", np.log(.12), .5, dims=noise_dims)
        va, vb = (sa**2, sb**2) if cell_noise else (sa[:, None]**2, sb[:, None]**2)
        base_variance = 1/(1/.4**2+nb_cp/vb)
        base_mean = base_variance*(.6/.4**2+syb/vb)
        base_rss = np.sum(ssb+nb*(yb-.6)**2, axis=-1)
        base_sum = syb-.6*nb_cp
        pm.Potential("likelihood_baseline", pt.sum(-.5*(nb_cp*pt.log(vb)+pt.log1p(.4**2*nb_cp/vb)+base_rss/vb-base_sum**2*base_variance/vb**2)))
        midpoint = hierarchy("midpoint", len(ids), [.5, 0., 0., 0.], .5*prior_scale, .35*prior_scale)
        width = pt.exp(hierarchy("log_width", len(ids), [np.log(1/6), 0., 0., 0.], .7*prior_scale, .5*prior_scale))
        pm.Deterministic("midpoint_cm", 10+90*midpoint, dims=("participant", "cell"))
        pm.Deterministic("sharpness_per_cm", 1/(360*width), dims=("participant", "cell"))
        q = pm.math.sigmoid(((DISTANCES["registered"]-10)/90-midpoint[..., None])/width[..., None])-.5
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
        pm.Potential("likelihood_at", pt.sum(-.5*(logdet+quadratic)))
        # These independent standard normals do not enter the marginalized likelihood.
        z = pm.Normal("z_nuisance", 0, 1, dims=("participant", "cell", "nuisance"))
        offset = base_mean+c00*v0+c01*v1+pt.sqrt(c00)*z[..., 0]
        amplitude = c01*v0+c11*v1+c01/pt.sqrt(c00)*z[..., 0]+pt.sqrt(pt.maximum(c11-c01*c01/c00, 1e-15))*z[..., 1]
        b = base_mean+base_variance/offset_variance*(offset-base_mean)+pt.sqrt(base_variance*.2**2/offset_variance)*z[..., 2]
        delta = offset-b
        pm.Deterministic("baseline_mean", b, dims=("participant", "cell"))
        pm.Deterministic("amplitude", amplitude, dims=("participant", "cell"))
        pm.Deterministic("corrected_intercept", delta, dims=("participant", "cell"))
        curve = pm.Deterministic("corrected_curve", delta[..., None]+amplitude[..., None]*q, dims=("participant", "cell", "distance"))
        pm.Deterministic("population_midpoint_effect_cm", 90*model["beta_midpoint"][1:], dims="effect")
        pm.Deterministic("population_log_sharpness_effect", -model["beta_log_width"][1:], dims="effect")
        for metric in ("midpoint_cm", "sharpness_per_cm"):
            pm.Deterministic(metric+"_effect", pt.dot(W[:3], model[metric].mean(0)), dims="effect")
        pm.Deterministic("mean_RT_effect_ms", 1000*pt.dot(W[:3], curve.mean((0, 2))), dims="effect")
        pm.Deterministic("far_minus_near_effect_ms", 1000*pt.dot(W[:3], (curve[..., -1]-curve[..., 0]).mean(0)), dims="effect")
    return model


def make_model(ids, at, baseline, family="logistic", correction="pooled_cp", likelihood="gaussian", prior_scale=1., nuisance_model="hierarchical", cell_noise=False):
    if nuisance_model == "marginal_independent":
        return make_marginal_model(ids, at, baseline, prior_scale, cell_noise)
    n = len(ids)
    at, baseline = at/1000., baseline/1000.
    coordinates = {"participant": ids, "cell": CELL_NAMES,
        "distance": DISTANCES["registered"], "coefficient": ("Intercept", *EFFECTS[:3]),
        "effect": EFFECTS[:3], "metric": ("midpoint_cm", "sharpness_per_cm")}
    with pm.Model(coords=coordinates) as model:
        # Priors are stated in seconds. Baseline means are not pre-subtracted data.
        base_dims = ("participant", "cell") if correction == "pooled_cp" else ("participant", "cell", "distance")
        b = pm.Normal("baseline_mean", .6, .4, dims=base_dims)
        b_at = b[..., None] if correction == "pooled_cp" else b
        delta = pm.Deterministic("corrected_intercept", hierarchy("delta", n, [0.]*4, .2, .12), dims=("participant", "cell"))
        sigma_at = pm.LogNormal("sigma_at", np.log(.12), .5, dims="participant")
        sigma_b = pm.LogNormal("sigma_baseline", np.log(.12), .5, dims="participant")
        if family == "constant":
            curve = pt.broadcast_to(delta[..., None], (n, 4, 5))
        else:
            amplitude = pm.Deterministic("amplitude", hierarchy("amplitude", n, [0.]*4, .15, .15), dims=("participant", "cell"))
            if family == "logistic":
                midpoint = hierarchy("midpoint", n, [.5, 0., 0., 0.], .5*prior_scale, .35*prior_scale)
                log_width = hierarchy("log_width", n, [np.log(1/6), 0., 0., 0.], .7*prior_scale, .5*prior_scale)
                width = pt.exp(log_width)
                pm.Deterministic("midpoint_cm", 10+90*midpoint, dims=("participant", "cell"))
                pm.Deterministic("sharpness_per_cm", 1/(360*width), dims=("participant", "cell"))
                pm.Deterministic("population_midpoint_effect_cm", 90*model["beta_midpoint"][1:], dims="effect")
                pm.Deterministic("population_log_sharpness_effect", -model["beta_log_width"][1:], dims="effect")
                q = pm.math.sigmoid(((DISTANCES["registered"]-10)/90-midpoint[..., None])/width[..., None])-.5
                for metric in ("midpoint_cm", "sharpness_per_cm"):
                    pm.Deterministic(metric+"_effect", pt.dot(W[:3], model[metric].mean(0)), dims="effect")
            else:
                x = DISTANCES["registered"] if family == "linear" else np.log(DISTANCES["registered"])
                q = (x-x.mean())/np.ptp(x)
            curve = delta[..., None] + amplitude[..., None]*q
        pm.Deterministic("corrected_curve", curve, dims=("participant", "cell", "distance"))
        pm.Deterministic("mean_RT_effect_ms", 1000*pt.dot(W[:3], curve.mean((0, 2))), dims="effect")
        pm.Deterministic("far_minus_near_effect_ms", 1000*pt.dot(W[:3], (curve[..., -1]-curve[..., 0]).mean(0)), dims="effect")
        if family in ("constant", "linear", "log_distance"):
            pm.Deterministic("population_mean_RT_effect_ms", 1000*model["beta_delta"][1:], dims="effect")
            if family != "constant":
                pm.Deterministic("population_far_minus_near_effect_ms", 1000*model["beta_amplitude"][1:], dims="effect")
        mu_at = b_at+curve
        if likelihood == "gaussian":
            for name, tensor, mean, sigma in (("at", at, mu_at, sigma_at), ("baseline", baseline, b_at, sigma_b)):
                count, observed, sse = sufficient(tensor)
                sd = sigma[:, None, None]
                pm.Potential("likelihood_"+name, pt.sum(-count*pt.log(sd)-.5*(sse+count*(observed-mean)**2)/sd**2))
        else:
            nu = pm.Deterministic("nu", 2+pm.Exponential("nu_minus_two", 1/15))
            for name, tensor, mean, sigma in (("at", at, mu_at, sigma_at), ("baseline", baseline, pt.broadcast_to(b_at, at.shape[:3]), sigma_b)):
                index = np.where(np.isfinite(tensor))
                pm.StudentT("observed_"+name, nu=nu, mu=mean[index[:3]], sigma=sigma[index[0]], observed=tensor[index])
    return model


def summarize_draws(data, model_name, quantity, labels):
    flat = data.reshape(-1, data.shape[-1])
    return [dict(model=model_name, quantity=quantity, term=label, posterior_mean=float(flat[:, j].mean()),
        posterior_median=float(np.median(flat[:, j])), ci_low=float(np.quantile(flat[:, j], .025)),
        ci_high=float(np.quantile(flat[:, j], .975)), probability_positive=float(np.mean(flat[:, j] > 0)))
        for j, label in enumerate(labels)]


def save_results(trace, ids, model_name, elapsed, configuration):
    posterior = trace["posterior"].dataset
    arrays = {name: value.values for name, value in posterior.data_vars.items()}
    statistics = trace["sample_stats"].dataset
    arrays.update({"sample_stats__"+name: value.values for name, value in statistics.data_vars.items()})
    # Local traces are ignored by Git; compression dominates runtime for these floats.
    np.savez(LOCAL / (model_name+"_draws.npz"), **arrays)
    target_names = [name for name in posterior.data_vars if name.endswith("_effect") or "_effect_" in name or name in ("population_log_sharpness_effect",)]
    effect_records = []
    for name in target_names:
        effect_records.extend(summarize_draws(posterior[name].values, model_name, name, EFFECTS[:3]))
    write_csv(OUT / (model_name+"_effects.csv"), effect_records)
    diag = az.summary(trace, kind="diagnostics", round_to="none")
    diag.to_csv(OUT / (model_name+"_diagnostics.csv"))
    target_diag = az.summary(trace, var_names=target_names, kind="diagnostics", round_to="none")
    rhat_col = "r_hat" if "r_hat" in diag else "rhat"
    divergences = int(statistics["diverging"].values.sum())
    summary = dict(model=model_name, seconds=elapsed, divergences=divergences,
        max_rhat=float(diag[rhat_col].max()), min_bulk_ess=float(diag["ess_bulk"].min()), min_tail_ess=float(diag["ess_tail"].min()),
        target_max_rhat=float(target_diag[rhat_col].max()), target_min_bulk_ess=float(target_diag["ess_bulk"].min()), target_min_tail_ess=float(target_diag["ess_tail"].min()),
        configuration=configuration, n_participants=len(ids), posterior_draws_per_chain=posterior.sizes["draw"], chains=posterior.sizes["chain"])
    summary["target_diagnostic_gate"] = bool(divergences == 0 and summary["target_max_rhat"] <= 1.01 and min(summary["target_min_bulk_ess"], summary["target_min_tail_ess"]) >= 400)
    write_json(OUT / (model_name+"_run.json"), summary)
    if "midpoint_cm" in posterior:
        records, point_values, point_meta = [], [], []
        for metric in ("midpoint_cm", "sharpness_per_cm"):
            draws = posterior[metric].values.reshape(-1, len(ids), 4)
            medians = np.median(draws, axis=0)
            for i, pid in enumerate(ids):
                for j, cell in enumerate(CELL_NAMES):
                    v = draws[:, i, j]
                    records.append(dict(model=model_name, participant_id=pid, cell=cell, metric=metric, median=medians[i, j],
                        ci_low=np.quantile(v, .025), ci_high=np.quantile(v, .975)))
            for effect, a in zip(EFFECTS[:3], (medians@W[:3].T).T):
                point_values.append(a)
                point_meta.append(dict(model=model_name, metric=metric, effect=effect,
                    interpretation="Conventional posterior-median ANOVA ignores fit uncertainty; group pooling makes estimates dependent"))
        write_csv(OUT / (model_name+"_participant_parameters.csv"), records)
        write_csv(OUT / (model_name+"_point_tests.csv"), test_batch(np.array(point_values).T, point_meta))
    print(json.dumps(summary, indent=2), flush=True)


CONFIGS = {
    "joint_logistic": dict(family="logistic"),
    "joint_logistic_wide": dict(family="logistic", prior_scale=2.),
    "joint_logistic_student": dict(family="logistic", likelihood="student"),
    "joint_logistic_same_label": dict(family="logistic", correction="same_label"),
    "joint_constant": dict(family="constant"),
    "joint_linear": dict(family="linear"),
    "joint_log_distance": dict(family="log_distance"),
    "joint_logistic_marginal": dict(family="logistic", nuisance_model="marginal_independent"),
    "joint_logistic_heterogeneous": dict(family="logistic", nuisance_model="marginal_independent", cell_noise=True),
    "joint_constant_student": dict(family="constant", likelihood="student"),
    "joint_linear_student": dict(family="linear", likelihood="student"),
    "joint_log_distance_student": dict(family="log_distance", likelihood="student"),
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("model", choices=CONFIGS)
    parser.add_argument("--draws", type=int, default=1500)
    parser.add_argument("--tune", type=int, default=1500)
    parser.add_argument("--target-accept", type=float, default=.95)
    parser.add_argument("--adaptation", choices=["diag", "low_rank"], default="diag")
    args = parser.parse_args()
    ids, at, baseline, _ = load_data()
    mask = cohort_mask(ids, "primary40")
    ids, at, baseline = ids[mask], at[mask], baseline[mask]
    config = {"correction": "pooled_cp", "likelihood": "gaussian", "prior_scale": 1., **CONFIGS[args.model]}
    model = make_model(ids, at, baseline, **config)
    specification = {**config, "priors": {
        "baseline_mean_seconds": "Normal(.6,.4), independently for each matched baseline pool",
        "corrected_intercept_seconds": "four fixed coefficients Normal(0,.2), independent participant coefficient SDs HalfNormal(.12)",
        "signed_amplitude_seconds": "four fixed coefficients Normal(0,.15), independent participant coefficient SDs HalfNormal(.15)",
        "midpoint_normalized": "fixed intercept Normal(.5,.5*s), other fixed coefficients Normal(0,.5*s); random coefficient SDs HalfNormal(.35*s)",
        "log_width_normalized": "fixed intercept Normal(log(1/6),.7*s), other fixed coefficients Normal(0,.7*s); random coefficient SDs HalfNormal(.5*s)",
        "sigma_seconds": "independent by participant and trial type, LogNormal(log(.12),.5)",
        "student_df": "2+Exponential(rate=1/15); common AT/Baseline",
        "coding": "Condition and Phase ±.5; interaction product; all random coefficients independent conditional on SDs"},
        "chains": 4, "draws": args.draws, "tune": args.tune, "target_accept": args.target_accept, "adaptation": args.adaptation}
    if config.get("nuisance_model") == "marginal_independent":
        specification["priors"]["corrected_intercept_seconds"] = "independent Normal(0,.2) by participant × cell; integrated analytically"
        specification["priors"]["signed_amplitude_seconds"] = "independent Normal(0,.15) by participant × cell; integrated analytically"
        specification["amendment"] = "Nuisance-pooling sensitivity added after primary sampling difficulties; same shape priors; all effects retained regardless of direction"
    if config.get("cell_noise"):
        specification["priors"]["sigma_seconds"] = "independent by participant × cell and trial type, LogNormal(log(.12),.5)"
        specification["amendment"] += "; cell-varying residual scales added after inspecting unequal within-person cell noise, with identical priors across all cells"
    write_json(OUT / (args.model+"_specification.json"), specification)
    started = time.monotonic()
    with model:
        if config.get("nuisance_model") == "marginal_independent":
            prior = pm.sample_prior_predictive(draws=500, var_names=["midpoint_cm", "sharpness_per_cm"], random_seed=SEED)["prior"].dataset
            rng = np.random.default_rng(SEED+2)
            m, w = prior["midpoint_cm"].values, 1/(4*prior["sharpness_per_cm"].values)
            q = 1/(1+np.exp(np.clip(-(DISTANCES["registered"]-m[..., None])/w[..., None], -700, 700)))-.5
            curve = rng.normal(0, .2, m.shape)[..., None]+rng.normal(0, .15, m.shape)[..., None]*q
            np.savez_compressed(LOCAL / (args.model+"_prior.npz"), corrected_curve=curve)
        else:
            prior = pm.sample_prior_predictive(draws=500, var_names=["corrected_curve", "mean_RT_effect_ms", "far_minus_near_effect_ms"], random_seed=SEED)
            np.savez_compressed(LOCAL / (args.model+"_prior.npz"), **{k: v.values for k, v in prior["prior"].dataset.data_vars.items()})
        trace = pm.sample(draws=args.draws, tune=args.tune, chains=4, cores=4, random_seed=SEED,
            nuts_sampler="nutpie", nuts={"target_accept": args.target_accept, "adaptation": args.adaptation}, progressbar=False,
            compute_convergence_checks=False)
    save_results(trace, ids, args.model, time.monotonic()-started, config)


if __name__ == "__main__":
    main()
