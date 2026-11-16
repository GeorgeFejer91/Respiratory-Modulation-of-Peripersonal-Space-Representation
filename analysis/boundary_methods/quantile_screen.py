"""Check for a discrete gap at the lower, middle and upper RT quartiles."""

import hashlib
import json
import platform
from pathlib import Path

import numpy as np
import scipy
from scipy import stats

from change_point import D, LABELS, bases, fit_contrasts, predict, simulation, trial_covariance, unique_gap
from screen import DISTANCES, OUT, ROOT, SEED, SUMMARY_LABELS, cohort_mask, load_data, phase_profiles, resample_trials, write_csv

QUANTILES = np.array([.25, .5, .75])
BOOTSTRAPS = 499


def observed_quantiles(tensor):
    values = np.sort(tensor, axis=-1)
    count = np.isfinite(values).sum(-1)
    if np.any(count == 0):
        raise ValueError("Cannot estimate a quantile with no retained trials.")
    position = (count[..., None] - 1) * QUANTILES
    lower = np.floor(position).astype(int)
    upper = np.ceil(position).astype(int)
    a = np.take_along_axis(values, lower, axis=-1)
    b = np.take_along_axis(values, upper, axis=-1)
    return a + (position - lower) * (b - a)


def run():
    ids, at, _, audit = load_data()
    include = cohort_mask(ids, "primary40")
    ids, at = ids[include], at[include]
    rng = np.random.default_rng(SEED + 3)
    quantile = observed_quantiles(at)
    reference = np.moveaxis(np.nanquantile(at, QUANTILES, axis=-1), 0, -1)
    np.testing.assert_allclose(quantile, reference, atol=1e-12)
    replicates = np.array([observed_quantiles(resample_trials(at, rng)) for _ in range(BOOTSTRAPS)])
    variance = replicates.var(0, ddof=1)
    n = np.isfinite(at).sum(-1)
    sigma = np.sqrt(np.mean(np.nanvar(at, axis=-1, ddof=1), axis=-1, keepdims=True))
    records, summary = [], {}
    for k, q in enumerate(QUANTILES):
        sample = phase_profiles(quantile[..., k])
        v = variance[..., k]
        full_variance = np.concatenate((v, v.reshape(len(ids), 2, 2, 5).sum(-2) / 4), axis=1)
        usable = (np.isfinite(full_variance) & (full_variance > 0)).all(-1)
        group_cov = np.stack([np.cov((sample[:, i] @ D.T).T) / len(ids) for i in range(len(SUMMARY_LABELS))])
        gaussian_variance = q * (1-q) * (sigma / stats.norm.pdf(stats.norm.ppf(q)))**2 / n
        entry = dict(simulation=simulation(gaussian_variance, DISTANCES["registered"]),
                     untestable_individual_cells=int((~usable[:, :4]).sum()), axes={})
        for axis, dist in DISTANCES.items():
            basis = bases(dist)
            person_cov = trial_covariance(full_variance[usable])
            a, _, p = fit_contrasts(sample[usable], person_cov, basis)
            amp, _, group_p = fit_contrasts(sample.mean(0), group_cov, basis)
            all_p = np.full((*usable.shape, len(LABELS)), np.nan)
            all_a = all_p.copy()
            all_p[usable], all_a[usable] = p, a
            comp = all_p[:, :4] >= .05
            entry["axes"][axis] = dict(unique_gaps=int(unique_gap(comp).sum()),
                                       unique_positive_gaps=int((unique_gap(comp) & (comp[..., 1:5] & (all_a[:, :4, 1:5] > 0)).any(-1)).sum()),
                                       boundary_free_compatible=int(comp[..., [0, 5, 6]].any(-1).sum()),
                                       group_compatibility={label: [name for name, val in zip(LABELS, row) if val >= .05]
                                                            for label, row in zip(SUMMARY_LABELS, group_p)},
                                       held_distance_rmse_ms=predict(dist, sample[:, :4]))
            for pid, probs, estimates in zip([*ids, "equal_participant_group"], [*all_p, group_p], [*all_a, amp]):
                for label, row, est in zip(SUMMARY_LABELS, probs, estimates):
                    for family, prob, value in zip(LABELS, row, est):
                        finite = np.isfinite(prob)
                        records.append(dict(participant=pid, cell=label, quantile=q, axis=axis, family=family,
                                            compatibility_p=float(prob) if finite else None,
                                            span_ms=float(value) if finite else None,
                                            compatible=bool(prob >= .05) if finite else None))
        summary[str(q)] = entry
    csv = OUT / "quantile_candidates.csv"
    write_csv(csv, records)
    sources = [Path(__file__), Path(__file__).with_name("change_point.py"), Path(__file__).with_name("screen.py"),
               OUT / "QUANTILE_SPECIFICATION.md", csv]
    manifest = dict(input=audit, quantiles=summary,
                    runtime=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
                    checks="All observed bin quantiles agree with numpy.nanquantile.",
                    sha256={p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources})
    (OUT / "quantile_results.json").write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Exported {len(records)} quantile candidate fits.")


if __name__ == "__main__":
    run()
