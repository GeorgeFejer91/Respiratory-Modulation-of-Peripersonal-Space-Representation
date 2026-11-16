"""Discretized random-midpoint likelihood with common paired condition shifts."""

import argparse
import hashlib
import json
import platform
from pathlib import Path

import numpy as np
import scipy
from scipy.special import expit, logsumexp

from joint_recorded import LEVEL, WIDTHS, bases, interval, latency_evidence, observations
from screen import CELL_NAMES, DISTANCES, EFFECTS, OUT, ROOT, SUMMARY_LABELS, W, cohort_mask, load_data, write_csv

SEED = 20261129
REPLICATES = 32
GENERATOR_MU = np.array([9,10])
GENERATOR_DELTA = np.array([2,4])
REFERENCES = ("flat","linear","log_distance")
MODELS = (*REFERENCES,"zero_shift","free_shift")
GENERATORS = ("flat","affine","weak","strong")
PHASES = ("Exhale","Inhale")


class Lattice:
    def __init__(self, distance, expanded=False):
        self.distance = distance
        self.u = np.arange(-36,57) if expanded else np.arange(-30,51)
        self.mu = np.arange(-18,39) if expanded else np.arange(-12,33)
        self.delta = np.arange(-26,27) if expanded else np.arange(-20,21)
        self.sigma = np.array([0.,.08,.15,.25,.40,.60] if expanded else [0.,.08,.15,.25,.40])
        self.location = np.arange(self.u.min()+self.delta.min(),self.u.max()+self.delta.max()+1)
        self.basis = bases(distance,self.location/20)
        self.control = self.u-self.location[0]
        self.vis = self.delta[:,None]+self.u-self.location[0]
        self.zero = int(np.flatnonzero(self.delta==0)[0])
        offset = (self.u-self.mu[:,None])/20
        pairs = np.empty((len(self.mu),len(self.sigma),len(self.u)))
        pairs[:,0] = offset==0
        pairs[:,1:] = np.exp(-.5*(offset[:,None,:]/self.sigma[None,1:,None])**2)
        self.weights = pairs/pairs.sum(-1,keepdims=True)

    @property
    def span(self):
        return np.ptp(self.distance)

    def physical(self, locations):
        return self.distance[0]+self.span*np.asarray(locations)/20

    def likelihood(self, terms, held=None):
        use = np.ones(5)
        if held is not None:
            use[held] = 0.
        latency = latency_evidence(*(term*use for term in terms),self.basis)
        curve = latency[...,3:].reshape(len(latency),4,len(self.location),len(WIDTHS))
        a = curve[:,:2,self.control,:]
        b = curve[:,2:,self.vis,:]
        # The pair retains the same person's two conditions for each latent u.
        paired = (a[:,:,None,:,:]+b).transpose(1,2,4,0,3)
        references = latency[...,:3].sum(0).reshape(2,2,3).sum(0)
        return references, paired

    def surface(self, paired):
        peak = paired.max(-1,keepdims=True)
        likelihood = np.exp(paired-peak)@self.weights.reshape(-1,len(self.u)).T
        np.log(likelihood,out=likelihood)
        likelihood += peak
        return likelihood.sum(-2).reshape(2,len(self.delta),len(WIDTHS),len(self.mu),len(self.sigma))

    def best(self, surface):
        return [np.unravel_index(np.argmax(s),s.shape) for s in surface]

    def cells(self, indices):
        shifts = np.array([self.delta[a] for a,_,_,_ in indices])
        control = np.array([self.mu[b] for _,_,b,_ in indices])
        return self.physical(np.r_[control,control+shifts])

    def participants(self, paired, indices):
        estimates = []
        for phase,(d,w,m,s) in enumerate(indices):
            with np.errstate(divide="ignore"):
                score = paired[phase,d,w]+np.log(self.weights[m,s])
            mass = np.exp(score-logsumexp(score,axis=-1,keepdims=True))
            center = np.array([interval(self.physical(self.u),row) for row in mass])
            estimates.append((center,center+self.delta[d]*self.span/20))
        return np.stack((estimates[0][0],estimates[1][0],estimates[0][1],estimates[1][1]),axis=1)


def effect_limits(lattice, support):
    phase_positions = []
    for s in support:
        delta, _, mu, _ = np.where(s)
        control = lattice.physical(lattice.mu[mu])
        visc = lattice.physical(lattice.mu[mu]+lattice.delta[delta])
        phase_positions.append(np.stack((control,visc)))
    targets = np.vstack((np.eye(4),[.5,.5,0.,0.],[0.,0.,.5,.5],W))
    low, high = np.zeros(len(targets)), np.zeros(len(targets))
    for phase, positions in enumerate(phase_positions):
        values = targets[:,[phase,phase+2]]@positions
        low += values.min(-1)
        high += values.max(-1)
    return np.stack((low,high),axis=-1)


def phase_improvement(surface, references):
    maxima = surface.max(axis=(1,2,3,4))
    return 2*(maxima-references.max(-1))


def predictive_folds(lattice, terms, full):
    scores = []
    full_ref, full_pair = full
    complete = lattice.surface(full_pair)
    for probe, distance in enumerate(lattice.distance):
        ref, pair = lattice.likelihood(terms,held=probe)
        trained = lattice.surface(pair)
        total = int(terms[0][...,probe].sum())
        free, tied = lattice.best(trained), lattice.best(trained[:,lattice.zero:lattice.zero+1])
        tied = [(lattice.zero,*row[1:]) for row in tied]
        difference = (full_ref-ref).sum(0).tolist()
        for picks in (tied,free):
            difference.append(sum(complete[p][key]-trained[p][key] for p,key in enumerate(picks)))
        for model, gain in zip(MODELS,difference):
            scores.append(dict(probe=probe,distance_cm=distance,model=model,held_trials=total,
                               log_score_per_trial=gain/total))
    return scores


def simulated_terms(lattice, number, generator, rng):
    x = (lattice.distance-lattice.distance[0])/lattice.span
    level = LEVEL+rng.normal(0,.075,(len(number),1,1))+rng.normal(0,.05,(len(number),4,1))
    sigma = rng.uniform(.11,.18,(len(number),4,1))
    sample_locations = []
    for m in GENERATOR_MU:
        mass = lattice.weights[np.flatnonzero(lattice.mu==m)[0],2]
        sample_locations.append(rng.choice(lattice.u,size=len(number),p=mass))
    u = np.stack(sample_locations,axis=-1)
    true_midpoints = np.c_[u,u+GENERATOR_DELTA]
    if generator in ("weak","strong"):
        amplitude = .08 if generator=="weak" else .25
        level = level+amplitude*(expit((x-true_midpoints[...,None]/20)/.135)-.5)
    elif generator=="affine":
        level = level+.08*(x-.5)
    y = number*level+sigma*np.sqrt(number)*rng.normal(size=number.shape)
    ss = sigma**2*rng.chisquare(np.maximum(number-1,1))
    return (number,y,np.where(number>1,ss,0)+np.divide(y*y,number,where=number>0,out=np.zeros_like(y))),true_midpoints


def simulation(lattice, number, phase_cutoff=None, shape_cutoff=None):
    evaluate = phase_cutoff is not None
    rng = np.random.default_rng(SEED+int(evaluate))
    results = []
    for generator in GENERATORS:
        for rep in range(REPLICATES):
            synthetic, midpoints = simulated_terms(lattice,number,generator,rng)
            ref, pair = lattice.likelihood(synthetic)
            s = lattice.surface(pair)
            improvement = phase_improvement(s,ref)
            maxima = s.max(axis=(1,2,3,4))
            row = dict(generator=generator,replicate=rep,phase_improvement=improvement.tolist())
            has_boundary = generator in ("weak","strong")
            if has_boundary:
                truth = [(int(np.flatnonzero(lattice.delta==d)[0]),2,int(np.flatnonzero(lattice.mu==m)[0]),2)
                         for d,m in zip(GENERATOR_DELTA,GENERATOR_MU)]
                loss = 2*(maxima-np.array([s[p][key] for p,key in enumerate(truth)]))
                row["max_truth_deviance"] = float(loss.max())
            if evaluate:
                row["selected"] = (improvement>phase_cutoff).tolist()
                if has_boundary:
                    point = lattice.best(s)
                    support = 2*(maxima[:,None,None,None,None]-s)<=shape_cutoff
                    bands = effect_limits(lattice,support)[len(SUMMARY_LABELS):]
                    group_truth = W@lattice.physical(np.r_[GENERATOR_MU,GENERATOR_MU+GENERATOR_DELTA])
                    estimated = W@lattice.cells(point)
                    locations = lattice.participants(pair,point)
                    people_truth = lattice.physical(midpoints)
                    row.update(effect_error_cm=(estimated-group_truth).tolist(),
                               effects_cover_truth=((bands[:,0]<=group_truth+1e-9)&
                                                    (bands[:,1]>=group_truth-1e-9)).tolist(),
                               person_rmse_cm=float(np.sqrt(np.mean((locations[...,1]-people_truth)**2))),
                               conditional_person_interval_inclusion=float(((locations[...,0]<=people_truth+1e-9)&
                                                                            (locations[...,2]>=people_truth-1e-9)).mean()))
            results.append(row)
        print(f"{'Evaluation' if evaluate else 'Calibration'} {generator}: {REPLICATES} paired cohorts.",flush=True)
    return results


def cutoffs(rows):
    phase = max([0.]+[float(np.quantile([max(r["phase_improvement"]) for r in rows if r["generator"]==name],
                                      .95,method="higher")) for name in ("flat","affine")])
    shape = max(float(np.quantile([r["max_truth_deviance"] for r in rows if r["generator"]==name],
                                  .95,method="higher")) for name in ("weak","strong"))
    return phase,shape


def checks():
    rng = np.random.default_rng(112)
    lattice = Lattice(DISTANCES["registered"])
    n = np.full((3,4,5),10)
    y = rng.normal(LEVEL,.13,size=(3,4,5,10))
    _, paired = lattice.likelihood((n,y.sum(-1),np.square(y).sum(-1)))
    s = lattice.surface(paired)
    for p,d,w,m,t in ((0,4,0,7,3),(1,31,4,23,2),(1,lattice.zero,3,19,0)):
        log_weights = np.log(lattice.weights[m,t],where=lattice.weights[m,t]>0,
                             out=np.full(len(lattice.u),-np.inf))
        explicit = sum(logsumexp([v+x for v,x in zip(sample,log_weights)]) for sample in paired[p,d,w])
        np.testing.assert_allclose(s[p,d,w,m,t],explicit,atol=1e-11)
    d,w,m,t = 9,1,10,2
    supports = np.zeros_like(s,dtype=bool)
    supports[:,d,w,m,t] = True
    x = lattice.cells([(d,w,m,t)]*2)
    targets = np.r_[x,(x[0]+x[1])/2,(x[2]+x[3])/2,W@x]
    np.testing.assert_allclose(effect_limits(lattice,supports),np.column_stack((targets,targets)),atol=1e-11)


def run():
    checks()
    ids, rt, _, input_audit = load_data()
    primary = cohort_mask(ids,"primary40")
    ids, rt = ids[primary],rt[primary]
    retained = observations(rt)
    base = Lattice(DISTANCES["registered"])
    calibrated = simulation(base,retained[0])
    phase_cutoff, shape_cutoff = cutoffs(calibrated)
    evaluated = simulation(base,retained[0],phase_cutoff,shape_cutoff)
    wide = Lattice(DISTANCES["registered"],expanded=True)
    wide_calibration = simulation(wide,retained[0])
    wide_phase_cutoff, wide_shape_cutoff = cutoffs(wide_calibration)
    wide_evaluation = simulation(wide,retained[0],wide_phase_cutoff,wide_shape_cutoff)
    rows,people,grid_diagnostics,held = [],[],[],[]
    for axis,distance in DISTANCES.items():
        for expanded in (False,True):
            lattice = Lattice(distance,expanded)
            full = lattice.likelihood(retained)
            refs,pair = full
            score = lattice.surface(pair)
            candidates = lattice.best(score)
            condition_points = lattice.cells(candidates)
            maxima = score.max(axis=(1,2,3,4))
            this_shape_cutoff = wide_shape_cutoff if expanded else shape_cutoff
            support = 2*(maxima[:,None,None,None,None]-score)<=this_shape_cutoff
            bands = effect_limits(lattice,support)
            tag = dict(axis=axis,grid="expanded" if expanded else "primary")
            points = np.r_[condition_points,condition_points[:2].mean(),condition_points[2:].mean(),W@condition_points]
            for name,value,limits in zip((*SUMMARY_LABELS,*EFFECTS),points,bands):
                rows.append(dict(tag,quantity=name,point_cm=value,lower_cm=limits[0],upper_cm=limits[1]))
            for p,(d,w,m,t) in enumerate(candidates):
                limits = np.where(support[p].any(axis=(1,2,3)))[0]
                this_phase_cutoff = wide_phase_cutoff if expanded else phase_cutoff
                grid_diagnostics.append(dict(tag,phase=PHASES[p],width_cm=WIDTHS[w]*lattice.span,
                                             latent_sd_cm=lattice.sigma[t]*lattice.span,
                                             shift_cm=lattice.delta[d]*lattice.span/20,
                                             gain_over_best_reference=phase_improvement(score,refs)[p],
                                             phase_selection_cutoff=this_phase_cutoff,
                                             gain_over_zero_shift=2*(maxima[p]-score[p,lattice.zero].max()),
                                             shift_grid_touched=bool(limits[0]==0 or limits[-1]==len(lattice.delta)-1),
                                             best_reference=REFERENCES[int(refs[p].argmax())]))
            locations = lattice.participants(pair,candidates)
            for pid,sample in zip(ids,locations):
                for name,(lo,med,hi) in zip(CELL_NAMES,sample):
                    people.append(dict(tag,participant=pid,cell=name,lower_cm=lo,median_cm=med,upper_cm=hi))
            held.extend(dict(tag,**prediction) for prediction in predictive_folds(lattice,retained,full))
            print(f"{axis}, {tag['grid']}: observed profiles and five held probes.",flush=True)

    tables = {"effects":rows,"participants":people,"geometry":grid_diagnostics,"held_probes":held}
    paths = []
    for name,records in tables.items():
        path = OUT/f"mixed_profile_{name}.csv"
        write_csv(path,records)
        paths.append(path)
    for file in (Path(__file__),Path(__file__).with_name("joint_recorded.py"),
                 OUT/"MIXED_PROFILE_SPECIFICATION.md",ROOT/"analysis/baseline_effects/requirements.txt"):
        paths.append(file)
    report = dict(input=input_audit,seed=SEED,replicates=REPLICATES,calibrated_phase_deviance=phase_cutoff,
                  calibrated_shape_deviance=shape_cutoff,calibration=calibrated,evaluation=evaluated,
                  expanded=dict(calibrated_phase_deviance=wide_phase_cutoff,
                                calibrated_shape_deviance=wide_shape_cutoff,
                                calibration=wide_calibration,evaluation=wide_evaluation),
                  runtime=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),
                  sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
    (OUT/"mixed_profile_results.json").write_text(json.dumps(report,indent=2,allow_nan=False)+"\n",
                                                   encoding="utf8",newline="\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only",action="store_true")
    arguments = parser.parse_args()
    if arguments.check_only:
        checks()
        print("Mixed likelihood integration and contrast projection checks passed.")
    else:
        run()
