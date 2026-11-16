"""Grid-integrated common boundary of observed misses and conditional log latency."""

import argparse
import hashlib
import json
import platform
from pathlib import Path

import numpy as np
import scipy
from scipy.special import betaln, expit, gammaln, logsumexp, roots_jacobi

from profile import COHORTS
from response_boundary import counts
from screen import DISTANCES, EFFECTS, OUT, ROOT, SUMMARY_LABELS, W, cohort_mask, load_data, write_csv

SEED = 20261128
REPLICATES = 32
WIDTHS = np.array([.06, .09, .135, .20, .30, .45, .675])
MODELS = ("boundary_free", "latency_shape", "miss_shape", "separate_shapes", "shared_shape")
TRUTH = np.array([.40, .45, .55, .60])
LOG_BETA = (1., 9.)
LEVEL = np.log(.55)
IG_SHAPE, IG_SCALE = 4., .0675


def bases(distance, midpoint):
    x = (distance-distance[0])/np.ptp(distance)
    gradual = (np.log(distance)-np.log(distance[0]))/np.log(distance[-1]/distance[0])
    sigmoid = expit((x-midpoint[:, None, None])/WIDTHS[None,:,None])
    return np.vstack((x*0, x, gradual, sigmoid.reshape(-1,len(x))))


def miss_quadrature(basis, max_count, prior):
    # Each conditional likelihood is a polynomial of degree at most max_count
    # in either endpoint. Gauss–Jacobi integrates against the Beta prior.
    nodes, mass = roots_jacobi(max_count//2+1, prior[1]-1, prior[0]-1)
    endpoints = (nodes+1)/2
    weights = np.log(mass/mass.sum())
    weights = (weights[:,None]+weights[None,:]).reshape(-1)
    near, far = np.meshgrid(endpoints,endpoints,indexing="ij")
    q = basis[:,None,:]
    rate = (1-q)*near.reshape(1,-1,1)+q*far.reshape(1,-1,1)
    log_terms = np.concatenate((np.log(rate),np.log1p(-rate)),axis=-1)
    return log_terms, weights


def miss_evidence(total, miss, quadrature):
    n, m = total.reshape(-1,5), miss.reshape(-1,5)
    observations, reverse = np.unique(np.concatenate((m,n-m),axis=-1),axis=0,return_inverse=True)
    log_terms, weights = quadrature
    result = np.empty((len(observations),len(log_terms)))
    for start in range(0,len(log_terms),16):
        sl = slice(start,start+16)
        block = log_terms[sl]
        loglike = (observations @ block.reshape(-1,10).T).reshape(len(observations),len(block),len(weights))
        result[:,sl] = logsumexp(loglike+weights,axis=-1)
    return result[reverse].reshape(*total.shape[:-1],len(log_terms))


def latency_evidence(number, total, squares, basis):
    q = basis-.5
    q[0] = 0
    a = .25+number.sum(-1,keepdims=True)
    b = number @ q.T
    d = 1.+number @ (q*q).T
    det = a*d-b*b
    u = .25*LEVEL+total.sum(-1,keepdims=True)
    v = total @ q.T
    residual = squares.sum(-1,keepdims=True)+.25*LEVEL**2-(d*u*u-2*b*u*v+a*v*v)/det
    shape = IG_SHAPE+number.sum(-1,keepdims=True)/2
    scale = IG_SCALE+np.maximum(residual,0)/2
    if np.any(residual < -1e-8):
        raise ArithmeticError("Invalid Gaussian residual moment")
    return ((np.log(.25)-np.log(det))/2+gammaln(shape)-gammaln(IG_SHAPE)
            +IG_SHAPE*np.log(IG_SCALE)-shape*np.log(scale)
            -(shape-IG_SHAPE)*np.log(2*np.pi))


def evidence(total, miss, n, y, y2, basis, quadrature, held=None):
    use = np.ones(5)
    if held is not None:
        use[held] = 0
    return (latency_evidence(n*use,y*use,y2*use,basis),
            miss_evidence((total*use).astype(int),(miss*use).astype(int),quadrature))


def shape_evidence(rt, miss):
    gradual_rt = logsumexp(rt[...,:3],axis=-1)-np.log(3)
    gradual_miss = logsumexp(miss[...,:3],axis=-1)-np.log(3)
    width_count = rt.shape[-1]-3
    rt_shape = logsumexp(rt[...,3:],axis=-1)-np.log(width_count)
    miss_shape = logsumexp(miss[...,3:],axis=-1)-np.log(width_count)
    shared_shape = logsumexp(rt[...,3:]+miss[...,3:],axis=-1)-np.log(width_count)
    return np.stack((gradual_rt+gradual_miss,rt_shape+gradual_miss,
                     gradual_rt+miss_shape,rt_shape+miss_shape,shared_shape),axis=-1)


def midpoint_mass(loglike):
    cells = loglike.reshape(*loglike.shape[:-1],-1,len(WIDTHS))
    log_m = logsumexp(cells,axis=-1)
    return np.exp(log_m-logsumexp(log_m,axis=-1,keepdims=True))


def interval(locations, mass):
    indices = np.searchsorted(np.cumsum(mass),[.025,.5,.975])
    return locations[indices]


def projected_weights(x, mass, weights):
    steps = np.round(2*np.asarray(weights)).astype(int)
    probability = np.ones(1)
    minimum = 0
    for coef, p in zip(steps,mass):
        if coef == 0:
            continue
        expanded = np.zeros((len(x)-1)*abs(coef)+1)
        expanded[::abs(coef)] = p if coef>0 else p[::-1]
        probability = np.convolve(probability,expanded)
        minimum += min(0,coef)*(len(x)-1)
    axis = x[0]*sum(weights)+(x[1]-x[0])*(minimum+np.arange(len(probability)))/2
    return axis,probability


def intervals(x, rt, miss, names, distance, tags):
    scores = shape_evidence(rt,miss)
    family_weight = np.exp(scores-logsumexp(scores,axis=-1,keepdims=True))
    prior_fraction = np.mean((x>=distance[0]-1e-10)&(x<=distance[-1]+1e-10))
    rows = []
    parameters = {"latency_shape":rt[...,3:],"miss_shape":miss[...,3:],
                  "shared_shape":rt[...,3:]+miss[...,3:]}
    targets = [*(np.eye(4)),[.5,.5,0,0],[0,0,.5,.5],*W]
    labels = (*SUMMARY_LABELS,*EFFECTS)
    for model, likelihood in parameters.items():
        mass = midpoint_mass(likelihood)
        for i, name in enumerate(names):
            for j, (label, weights) in enumerate(zip(labels,targets)):
                axis, p = projected_weights(x,mass[i],weights)
                a,b,c = interval(axis,p)
                row = dict(tags,participant=name,model=model,quantity=label,
                           lower_cm=a,median_cm=b,upper_cm=c)
                if j < len(SUMMARY_LABELS):
                    inside = (axis>=distance[0]-1e-9)&(axis<=distance[-1]+1e-9)
                    row.update(fraction_inside=float(p[inside].sum()),
                               interval_inside=bool(a>distance[0]+1e-9 and c<distance[-1]-1e-9))
                if j < 4:
                    row.update(prior_midpoint_fraction_inside=prior_fraction)
                    row.update({f"weight_{name}":w for name,w in zip(MODELS,family_weight[i,j])})
                rows.append(row)
    return rows


def data_by_cohort(evidences, mask):
    return tuple(value[mask].sum(0,keepdims=True) for value in evidences)


def observations(rt):
    if np.any(np.isfinite(rt)&(rt<=0)):
        raise ValueError("Expected positive released, cleaned RTs")
    log_rt = np.log(rt/1000)
    return np.isfinite(log_rt).sum(-1),np.nansum(log_rt,axis=-1),np.nansum(log_rt**2,axis=-1)


def simulate(rng, total, retention, name, distance):
    z = expit(((distance-distance[0])/np.ptp(distance)-TRUTH[:,None])/.135)
    level = rng.uniform(.045,.091,(len(total),4,1))
    miss_prob = level+.14*z if name=="both" else np.broadcast_to(level,total.shape)
    misses = rng.binomial(total,miss_prob)
    retained = rng.binomial(total-misses,retention)
    mu = rng.normal(LEVEL,.09,(len(total),4,1))
    if name != "flat":
        mu = mu+.16*(z-.5)
    sd = rng.uniform(.115,.18,(len(total),1,1))
    sums = retained*mu+sd*np.sqrt(retained)*rng.normal(size=total.shape)
    numerator = np.divide(sums**2,retained,where=retained>0,out=np.zeros_like(sums))
    squares = sd**2*rng.chisquare(np.maximum(1,retained-1))
    squares = np.where(retained>1,squares,0)+numerator
    return misses,retained,sums,squares


def recovery(total, miss, counts_rt, basis, quadrature, distance, grid):
    rng = np.random.default_rng(SEED)
    x = distance[0]+np.ptp(distance)*grid
    true_location = distance[0]+np.ptp(distance)*TRUTH
    true_effects = W@true_location
    hits = total-miss
    retention = np.divide(counts_rt,hits,where=hits>0,out=np.zeros_like(hits,dtype=float))
    rows = []
    for name in ("flat","both","latency_only"):
        for rep in range(REPLICATES):
            test = evidence(total,*simulate(rng,total,retention,name,distance),basis,quadrature)
            for target, arrays in (("participant",test),("shared_group",tuple(a.sum(0,keepdims=True) for a in test))):
                rt, m = arrays
                score = shape_evidence(rt,m)
                weights = np.exp(score-logsumexp(score,axis=-1,keepdims=True))
                pm = midpoint_mass(rt[...,3:]+m[...,3:])
                q = np.array([[interval(x,v) for v in person] for person in pm])
                interior = (q[...,0]>distance[0]+1e-9)&(q[...,2]<distance[-1]-1e-9)
                row = dict(generator=name,replicate=rep,target=target,
                           shared_family_top_fraction=float((score.argmax(-1)==4).mean()),
                           shared_family_mean_weight=float(weights[...,4].mean()),
                           midpoint_interval_inside_fraction=float(interior.mean()),
                           shared_weight_over_half_and_inside=float((interior&(weights[...,4]>.5)).mean()))
                if name!="flat":
                    row["midpoint_rmse_cm"] = float(np.sqrt(np.mean((q[...,1]-true_location)**2)))
                    row["midpoint_coverage"] = float(((q[...,0]<=true_location+1e-9)&(q[...,2]>=true_location-1e-9)).mean())
                    effect_bounds = np.array([[interval(*projected_weights(x,person,w)) for w in W] for person in pm])
                    effect_inside = (effect_bounds[...,0]<=true_effects+1e-9)&(effect_bounds[...,2]>=true_effects-1e-9)
                    row["paired_interval_inclusion"] = effect_inside.mean(0).tolist()
                    row["paired_rmse_cm"] = np.sqrt(((effect_bounds[...,1]-true_effects)**2).mean(0)).tolist()
                rows.append(row)
        print(f"Completed {name} recovery ({REPLICATES} cohorts).",flush=True)
    return rows


def checks():
    from scipy.stats import multivariate_t

    q = bases(DISTANCES["registered"],np.array([.4]))
    trials = np.array([[11,12,8,12,10]],dtype=int)
    misses = np.array([[1,0,3,0,1]],dtype=int)
    quadrature = miss_quadrature(q,int(trials.sum()),LOG_BETA)
    fitted = miss_evidence(trials,misses,quadrature)
    p = misses.sum()
    np.testing.assert_allclose(fitted[0,0],betaln(1+p,9+trials.sum()-p)-betaln(1,9),atol=1e-12)
    y = np.array([-.41,-.45,-.55,-.73,-.81])
    fit = latency_evidence(np.ones((1,5)),y[None],(y*y)[None],q)
    for i, shape in enumerate(q):
        covariate = shape-.5 if i else np.zeros(5)
        design = np.column_stack((np.ones(5),covariate))
        covariance = np.eye(5)+(design*np.array([4,1]))@design.T
        independent = multivariate_t.logpdf(y,np.repeat(LEVEL,5),
                                             (IG_SCALE/IG_SHAPE)*covariance,df=2*IG_SHAPE)
        np.testing.assert_allclose(fit[0,i],independent,atol=1e-12)
    points = np.arange(4)*.15
    p = np.eye(4)[[0,1,2,3]]
    for w in W:
        x, mass = projected_weights(points,p,w)
        np.testing.assert_allclose(interval(x,mass),points@w,atol=1e-12)
    reduced_count = np.zeros((1,5),dtype=int)
    np.testing.assert_allclose(miss_evidence(reduced_count,reduced_count,quadrature),0,atol=1e-12)
    np.testing.assert_allclose(latency_evidence(reduced_count,reduced_count,reduced_count,q),0,atol=1e-12)


def run():
    checks()
    ids, rt, _, audit = load_data()
    observed, lows, _, unavailable = counts(ids)
    n, y, y2 = observations(rt)
    full = observed[0]
    misses = lows["miss"][0]
    if np.any(n>full-misses-unavailable[0]):
        raise ValueError("Cleaned response times exceed the available hit latencies")
    primary = cohort_mask(ids,"primary40")
    shape_outputs, held_outputs, simulated = [], [], []
    for key, distance in DISTANCES.items():
        for variant in ("primary","expanded_midpoints","beta_2_18"):
            if key!="registered" and variant=="beta_2_18":
                continue
            grid = np.arange(-24,45)/20 if variant=="expanded_midpoints" else np.arange(-12,33)/20
            locations = distance[0]+np.ptp(distance)*grid
            q = bases(distance,grid)
            prior = (2.,18.) if variant=="beta_2_18" else LOG_BETA
            quadrature = miss_quadrature(q,int(full.sum(-1).max()),prior)
            raw = (full,misses,n,y,y2)
            fitted = evidence(*raw,q,quadrature)
            tag = dict(distance=key,variant=variant)
            shape_outputs.extend(intervals(locations,*(a[primary] for a in fitted),ids[primary],
                                           distance,dict(tag,cohort="primary40",target="participant")))
            for cohort in COHORTS:
                mask = cohort_mask(ids,cohort)
                group_fits = data_by_cohort(fitted,mask)
                shape_outputs.extend(intervals(locations,*group_fits,["sample"],distance,
                                               dict(tag,cohort=cohort,target="shared_group")))
            full_person = shape_evidence(*(a[primary] for a in fitted))
            full_group = shape_evidence(*data_by_cohort(fitted,primary))
            for h,d in enumerate(distance):
                trained = evidence(*raw,q,quadrature,held=h)
                person_diff = full_person-shape_evidence(*(a[primary] for a in trained))
                group_diff = full_group-shape_evidence(*data_by_cohort(trained,primary))
                targets = int(full[primary,:,h].sum())
                for mode, diff in (("participant",person_diff),("shared_group",group_diff)):
                    for j,name in enumerate(MODELS):
                        held_outputs.append(dict(tag,target=mode,model=name,probe_index=h,distance_cm=d,
                                                 trials=targets,log_score_per_trial=float(diff[...,j].sum()/targets)))
            print(f"{key}, {variant}: observed and five held probes complete.",flush=True)
            if key=="registered" and variant=="primary":
                simulated = recovery(full[primary],misses[primary],n[primary],q,quadrature,distance,grid)
    rows = []
    for key in DISTANCES:
        for variant in ("primary","expanded_midpoints","beta_2_18"):
            for target in ("participant","shared_group"):
                for model in MODELS:
                    these = [r for r in held_outputs if (r["distance"],r["variant"],r["target"],r["model"])
                             == (key,variant,target,model)]
                    if these:
                        value = np.average([r["log_score_per_trial"] for r in these],weights=[r["trials"] for r in these])
                        rows.append(dict(distance=key,variant=variant,target=target,model=model,log_score_per_trial=value))
    outputs = [OUT/f"joint_recorded_{name}.csv" for name in ("intervals","held_probes","prediction")]
    for path, records in zip(outputs,(shape_outputs,held_outputs,rows)):
        write_csv(path,records)
    sources = Path(__file__).parent
    baseline = ROOT/"analysis/baseline_effects"
    hashes = [*outputs,Path(__file__),sources/"response_boundary.py",sources/"screen.py",
              sources/"profile.py",baseline/"baseline_effects.py",baseline/"requirements.txt",
              OUT/"JOINT_RECORDED_SPECIFICATION.md"]
    manifest = dict(seed=SEED,replicates=REPLICATES,recovery=simulated,input=audit,
                    sample={"observed_AT":int(full[primary].sum()),"misses":int(misses[primary].sum()),
                            "retained_hit_rt":int(n[primary].sum())},
                    environment={"python":platform.python_version(),"numpy":np.__version__,"scipy":scipy.__version__},
                    sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in hashes})
    (OUT/"joint_recorded_results.json").write_text(json.dumps(manifest,indent=2,allow_nan=False)+"\n",encoding="utf8",newline="\n")
    print(f"Wrote {len(shape_outputs)} interval rows, {len(held_outputs)} held-score rows and {len(simulated)} recovery summaries.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only",action="store_true")
    args = parser.parse_args()
    if args.check_only:
        checks()
        print("Gaussian and binomial integration, contrast and empty-data checks passed.")
    else:
        run()
