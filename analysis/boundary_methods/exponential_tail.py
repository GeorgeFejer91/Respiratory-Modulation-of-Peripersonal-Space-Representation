"""Conditioned positive ex-Gaussian RT with shared Gaussian dispersion."""

import argparse
import hashlib
import json
import time
from importlib.metadata import version
from pathlib import Path

import numpy as np
import pymc as pm
import pytensor.tensor as pt
from filelock import FileLock
from scipy.special import expit, log_ndtr, logsumexp

from reduced_hierarchy import diagnostic
from screen import DISTANCES, ROOT, W, cohort_mask, load_data
from baseline_effects import DESIGN

SEED = 20261125
X = DISTANCES["registered"]
LOCAL = ROOT / ".for-ai-local" / "boundary-exponential-tail"
MODELS = ("flat","linear_tail","tail","center")
SHAPES = ("tail","center")
TRUTH = np.array([48.,45.,58.,55.])


def ex_parameters(mu, sd, tau, log_cdf, log_add, log):
    """Return the normal-CDF shift and constant shared by a probe's trials."""
    rate = sd/tau
    offset = mu/tau+(rate**2)/2
    log_normalizer = log_add(log_cdf(mu/sd), offset+log_cdf(-mu/sd-rate))
    return rate, offset-log_normalizer-log(tau)


def ex_logpdf(y, mu, sd, tau, log_cdf, log_add, log):
    """Log PDF conditioned on a positive response, in the same units as y."""
    rate, offset = ex_parameters(mu,sd,tau,log_cdf,log_add,log)
    return offset-y/tau+log_cdf((y-mu)/sd-rate)


def build(rt, model):
    i,c,d,_ = index = np.where(np.isfinite(rt))
    counts = np.isfinite(rt).sum(axis=-1)
    totals = np.nansum(rt,axis=-1)
    n = len(rt)
    shape = (n,4)
    with pm.Model() as graph:
        center = pm.Normal("core_center", .51, .16, shape=shape)
        log_tau = pm.Normal("tail_level", np.log(.12), .7, shape=shape)
        sd = pm.LogNormal("core_sd", np.log(.10), .5, shape=n)
        mu = pt.broadcast_to(center[...,None],(*shape,5))
        log_mean = pt.broadcast_to(log_tau[...,None],(*shape,5))
        if model in SHAPES:
            fixed = pm.Normal("midpoint_fixed_cm", np.array([55.,0.,0.,0.]), 45., shape=4)
            scale = pm.HalfNormal("midpoint_re_sd_cm",31.5,shape=2)
            z = pm.Normal("midpoint_re_z",0,1,shape=(n,2))
            m = pm.Deterministic("midpoint_cm", pt.dot(fixed,DESIGN.T) + pt.dot(z*scale,DESIGN[:,:2].T))
            width = pm.LogNormal("width_cm", np.log(15.), .7)
            q = pm.math.sigmoid((X-m[...,None])/width)-.5
        elif model == "linear_tail":
            q = (X-X.mean())/np.ptp(X)
        if model in ("tail","linear_tail"):
            amplitude = pm.Normal("log_tail_amplitude",0,.7,shape=shape)
            log_mean += amplitude[...,None]*q
        elif model == "center":
            amplitude = pm.Normal("center_amplitude_seconds",0,.15,shape=shape)
            mu += amplitude[...,None]*q
        trial_mu = pm.Deterministic("trial_mu",mu)
        trial_tau = pm.Deterministic("trial_tau",pt.exp(log_mean))
        log_cdf = lambda z: pm.logcdf(pm.Normal.dist(),z)
        rate, offset = ex_parameters(trial_mu,sd[:,None,None],trial_tau,log_cdf,pt.logaddexp,pt.log)
        probe_terms = counts*offset-totals/trial_tau
        trial_terms = log_cdf((rt[index]-trial_mu[i,c,d])/sd[i]-rate[i,c,d])
        pm.Potential("positive_tail_likelihood",probe_terms.sum()+trial_terms.sum())
    return graph


def simulate(rt, scenario):
    rng = np.random.default_rng(SEED+13)
    n = len(rt)
    mu = np.nanmedian(rt,axis=(2,3))[...,None,None] - .09
    sig = rng.uniform(.07,.11,size=n)[:,None,None,None]
    tau = rng.uniform(.08,.14,size=(n,4,1,1))
    if scenario == "shift":
        q = expit((X-TRUTH[:,None])/15)-.5
        tau = tau*np.exp(.75*q[...,None])
    draw = rng.normal(mu,sig,size=rt.shape)+rng.exponential(tau,size=rt.shape)
    while (invalid := draw<=0).any():
        replacement = rng.normal(mu,sig,size=rt.shape)+rng.exponential(tau,size=rt.shape)
        draw[invalid] = replacement[invalid]
    return np.where(np.isfinite(rt),draw,np.nan)


def held_score(posterior, rt, held):
    mu,tau = (posterior[k].values.reshape(-1,*rt.shape[:2],5)[...,held,None]
              for k in ("trial_mu","trial_tau"))
    sd = posterior["core_sd"].values.reshape(-1,len(rt),1,1)
    y = rt[:,:,held,:]
    score = []
    for j in range(0,len(mu),128):
        sl = slice(j,j+128)
        lp = ex_logpdf(y,mu[sl],sd[sl],tau[sl],log_ndtr,np.logaddexp,np.log)
        score.append(np.nansum(lp,axis=-1))
    marginal = logsumexp(np.concatenate(score),axis=0)-np.log(len(mu))
    return dict(log_score_per_trial=float(marginal.sum()/np.isfinite(y).sum()),
                target_trials=int(np.isfinite(y).sum()))


def fit_receipt(args, ids, rt, audit):
    source_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if args.scenario != "observed":
        rt = simulate(rt,args.scenario)
    train = rt.copy()
    if args.held is not None:
        train[:,:,args.held,:] = np.nan
    m = build(train,args.model)
    with m:
        assert np.isfinite(m.compile_logp()(m.initial_point()))
        if args.check_only:
            return
        before = None if args.model not in SHAPES else pm.draw(m["midpoint_cm"],draws=512,random_seed=SEED)
        start = time.monotonic()
        fit = pm.sample(draws=args.draws,tune=args.tune,chains=args.chains,cores=args.cores,
                        random_seed=SEED,nuts_sampler="nutpie",nuts={"target_accept":args.accept,"adaptation":"diag"},
                        progressbar=False,compute_convergence_checks=False)
    posterior = fit["posterior"].dataset
    ndiv = int(fit["sample_stats"].dataset["diverging"].values.sum())
    diagnostic_vars = ["trial_mu","trial_tau","core_sd"]
    if args.model in SHAPES:
        diagnostic_vars.extend(("midpoint_cm","width_cm"))
    estimates = {key:diagnostic(posterior[key]) for key in diagnostic_vars}
    gate = ndiv==0 and all(v["max_rhat"] is not None and v["max_rhat"]<=1.01 and
                           min(v["min_bulk"],v["min_tail"])>=400 for v in estimates.values())
    out = dict(model=args.model,scenario=args.scenario,held_probe_index=args.held,chains=args.chains,
               warmup=args.tune,draws=args.draws,target_accept=args.accept,cores=args.cores,
               diagnostic_pass=gate,diagnostics=estimates,divergences=ndiv,
               input=audit,participant_order=ids.tolist(),seed=SEED,seconds=time.monotonic()-start,
               runtime={name:version(name) for name in ("pymc","pytensor","nutpie","scipy","numpy")},
               source_sha256=source_sha)
    if args.model in SHAPES:
        cm = posterior["midpoint_cm"].values
        qs = lambda x: np.quantile(x,[.025,.5,.975],axis=(0,1)).tolist()
        change = posterior["trial_mu" if args.model=="center" else "trial_tau"].values
        span = (change[...,-1]-change[...,0])*1000
        locations = qs(cm)
        out.update(prior_midpoint_fraction_inside=float(((before>=10)&(before<=100)).mean()),
                   posterior_midpoint_fraction_inside=float(((cm>=10)&(cm<=100)).mean()),
                   population_midpoint_contrasts_cm=qs(posterior["midpoint_fixed_cm"].values[...,1:]),
                   paired_fixed_sample_contrasts_cm=qs(cm.mean(-2)@W.T),
                   width_cm=qs(posterior["width_cm"].values),
                   group_component_span_ms=qs(span.mean(-2)),participant_component_span_ms=qs(span),
                   participant_midpoints_cm=locations)
        if args.scenario=="shift":
            lo, med, hi = np.asarray(locations)
            contrast_truth = TRUTH @ W.T
            paired = np.asarray(out["paired_fixed_sample_contrasts_cm"])
            out["recovery"] = dict(
                truth_cm=TRUTH.tolist(), paired_truth_cm=contrast_truth.tolist(),
                individual_midpoint_rmse_cm=float(np.sqrt(np.mean((med-TRUTH)**2))),
                individual_interval_coverage=float(((lo<=TRUTH)&(TRUTH<=hi)).mean()),
                paired_intervals_cover_truth=((paired[0]<=contrast_truth)&(contrast_truth<=paired[2])).tolist(),
            )
    if args.held is not None:
        out["held_predictions"] = held_score(posterior,rt,args.held)
    return out


def sample(args):
    ids, rt, _, audit = load_data()
    keep = cohort_mask(ids,"primary40")
    ids, rt = ids[keep], rt[keep]/1000
    if np.any(np.isfinite(rt)&(rt<=0)):
        raise ValueError("The positive RT likelihood needs strictly positive retained hits.")
    if args.check_only:
        fit_receipt(args,ids,rt,audit)
        return
    LOCAL.mkdir(parents=True,exist_ok=True)
    tag = f"{args.model}_{args.scenario}_hold{args.held}_{args.draws}x{args.chains}"
    receipt = LOCAL/f"{tag}.json"
    expected = dict(model=args.model,scenario=args.scenario,held_probe_index=args.held,
                    chains=args.chains,warmup=args.tune,draws=args.draws,target_accept=args.accept,
                    seed=SEED,participant_order=ids.tolist())
    # Different queues can reach the same fold while its first worker is sampling.
    with FileLock(receipt.with_suffix(".lock"),preserve_lock_file=True,fallback_to_soft=False):
        if receipt.exists():
            out = json.loads(receipt.read_text(encoding="utf8"))
            release_ok = out["input"]["input_sha256"]==audit["input_sha256"]
            out.setdefault("target_accept",.95)  # Older initial receipts used the CLI default.
            if not release_ok or any(out.get(k)!=v for k,v in expected.items()):
                raise ValueError(f"Existing fit has different settings or data in {receipt.name}")
            print(f"Reused {receipt.name} after checking its settings and released data.")
            return
        out = fit_receipt(args,ids,rt,audit)
        temp = receipt.with_suffix(".tmp")
        temp.write_text(json.dumps(out,indent=2,allow_nan=False)+"\n",encoding="utf8",newline="\n")
        temp.replace(receipt)
    print(f"{tag}: gate {out['diagnostic_pass']}, {out['divergences']} divergences, {out['seconds']:.1f} s.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model",choices=MODELS)
    parser.add_argument("--scenario",choices=("observed","flat","shift"),default="observed")
    parser.add_argument("--held",type=int,choices=range(5))
    parser.add_argument("--draws",type=int,default=1500)
    parser.add_argument("--tune",type=int,default=1500)
    parser.add_argument("--chains",type=int,default=4)
    parser.add_argument("--cores",type=int,default=2)
    parser.add_argument("--accept",type=float,default=.95)
    parser.add_argument("--check-only",action="store_true")
    sample(parser.parse_args())
