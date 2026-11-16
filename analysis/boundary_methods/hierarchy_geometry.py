"""Distinguish latent participant midpoints from equal-person RT-profile peaks."""

import json

import numpy as np
from scipy.special import expit

from screen import OUT, ROOT, SUMMARY_LABELS, W, write_csv

GRID = np.linspace(10, 100, 181)
SPANS = (0., 20., 40.)
LABELS = (*SUMMARY_LABELS, "Condition")
LOCAL = ROOT / ".for-ai-local" / "boundary-hierarchy"


def equal_phase(values):
    return np.stack((values[..., :2].mean(-1),values[..., 2:4].mean(-1)), axis=-1)


def group_curves(midpoints, sharpness, amplitude, grid=GRID, chunk=48):
    """Expected group RT differences and derivatives in ms and ms/cm."""
    aggregate, derivatives = [], []
    for start in range(0,len(midpoints),chunk):
        seg = slice(start,start+chunk)
        rate = 4*sharpness[seg][...,None]
        grouped = (grid-midpoints[seg][...,None])*rate
        q = expit(grouped)
        scale = amplitude[seg][...,None]*1000
        mu = (scale*(q-.5)).mean(1)
        derivative = (scale*rate*q*expit(-grouped)).mean(1)
        aggregate.append(mu)
        derivatives.append(derivative)
    aggregate = np.concatenate(aggregate).swapaxes(-1,-2)
    derivatives = np.concatenate(derivatives).swapaxes(-1,-2)
    return tuple(np.concatenate((a,equal_phase(a)),axis=-1).swapaxes(-1,-2)
                 for a in (aggregate,derivatives))


def group_peaks(curves, derivative, grid=GRID):
    argmax = derivative.argmax(-1)
    height = derivative.max(-1)
    interior = derivative[...,1:-1]
    peaks = ((interior>0) & (interior>=derivative[...,:-2])
             & (interior>derivative[...,2:])).sum(-1)
    eligible = ((argmax>0) & (argmax<len(grid)-1) & (height>0)
                & (peaks==1) & (derivative.min(-1)>=-1e-10)
                & (derivative[...,0]<height/2) & (derivative[...,-1]<height/2))
    return grid[argmax], eligible, curves[...,-1]-curves[...,0]


def row_summary(draws, valid):
    use = draws[valid]
    lo, med, hi = (np.quantile(use,[.025,.5,.975]) if len(use) else (None,None,None))
    return dict(draws=len(draws), qualifying=len(use), fraction=float(valid.mean()),
                lower_cm=lo, median_cm=med, upper_cm=hi)


def examine(path, include_participants=True):
    receipt = json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
    tags = dict(model=receipt["model"], calibration=receipt.get("calibration","pooled_marginal"),
                prior_scale=receipt["prior_scale"], draws_per_chain=receipt["draws"],
                diagnostic_pass=receipt["diagnostic_pass"])
    stride = 1
    if "recovery" in receipt:
        stride = 10
        tags.update(scenario=receipt["recovery"]["scenario"],replicate=receipt["recovery"]["replicate"])
    tags["posterior_draw_stride"] = stride
    with np.load(path) as loaded:
        ids = loaded["ids"]
        mats = [loaded[k][:,::stride].reshape(-1,len(ids),4)
                for k in ("midpoint_cm","sharpness_per_cm","amplitude")]
        midpoint, _, _ = mats
    curves, derivative = group_curves(*mats)
    x, eligible, spans = group_peaks(curves,derivative)
    cells, per_person = [], []
    for span in SPANS:
        valid = eligible & (spans>span)
        for j, label in enumerate(SUMMARY_LABELS):
            cells.append(dict(tags, cell=label, minimum_span_ms=span, **row_summary(x[:,j],valid[:,j])))
        values = x[:,5]-x[:,4]
        cells.append(dict(tags, cell="Condition", minimum_span_ms=span,
                          **row_summary(values,valid[:,4] & valid[:,5])))
    if not include_participants:
        return cells, per_person
    latent = np.concatenate((midpoint,equal_phase(midpoint),
                             (midpoint @ W[0]).reshape(len(midpoint),len(ids),1)),axis=-1)
    for i, pid in enumerate(ids):
        for j, label in enumerate(LABELS):
            draws = latent[:,i,j]
            Q = row_summary(draws,np.ones(len(draws),dtype=bool))
            if j < 6:
                Q["fraction_inside"] = float(((draws>=10)&(draws<=100)).mean())
            per_person.append(dict(tags, participant=pid, cell=label, **Q))
    return cells, per_person


def checks():
    m = np.full((1,3,4),55.)
    w = np.full_like(m,1/60)
    a = np.full_like(m,.100)
    raw, derivative = group_curves(m,w,a)
    location, admissible, _ = group_peaks(raw,derivative)
    np.testing.assert_allclose(location,55)
    assert admissible.all()
    # Signed mixtures can cancel the distance profile and make a peak undefined.
    a[:,0,:], a[:,1,:], a[:,2,:] = .1,-.1,0.
    _, admissible, _ = group_peaks(*group_curves(m,w,a))
    assert not admissible.any()
    # The equal-phase peak differs from the arithmetic mean of two midpoints.
    m[...,2], m[...,3] = 40,70
    a[...] = .08
    a[...,2] = .24
    group = group_peaks(*group_curves(m,w,a))[0]
    assert 40<=group[0,5]<48


def run():
    checks()
    rows, people, simulated = [], [], []
    for path in sorted(LOCAL.glob("*_holdNone_*x4*.npz")):
        meta = json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
        if "population_condition_phase_interaction_cm" not in meta:
            continue
        if "recovery" in meta:
            simulated.extend(examine(path,include_participants=False)[0])
            continue
        group, latent = examine(path)
        rows.extend(group)
        people.extend(latent)
    write_csv(OUT/"hierarchy_group_peaks.csv", rows)
    write_csv(OUT/"hierarchy_participant_midpoints.csv", people)
    if simulated:
        write_csv(OUT/"hierarchy_recovery_geometry.csv",simulated)
    print(f"Wrote {len(rows)} group peak summaries and {len(people)} latent participant summaries.")


if __name__ == "__main__":
    run()
