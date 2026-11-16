"""Screen which discrete boundary and boundary-free profiles fit the five bins."""

import hashlib
import json
import platform
from pathlib import Path

import numpy as np
import scipy
from scipy import stats

from screen import (DISTANCES, OUT, ROOT, SEED, SIMULATIONS, SUMMARY_LABELS,
                    cohort_mask, load_data, phase_profiles, write_csv)

LABELS = ("flat", "gap_1", "gap_2", "gap_3", "gap_4", "linear", "log_distance")
D = np.eye(5)[1:] - np.eye(5)[0]


def bases(distance):
    steps = (np.arange(5) >= np.arange(1, 5)[:, None]).astype(float)
    affine = np.stack((distance, np.log(distance)))
    affine -= affine[:, :1].copy()
    affine /= affine[:, -1:].copy()
    return np.vstack((np.zeros((1, 5)), steps, affine))


def fit_contrasts(profile, cov, basis):
    """GLS projection after removing the free intercept through contrasts."""
    y = profile @ D.T
    q = basis @ D.T
    chol = np.linalg.cholesky(cov)
    white_y = np.linalg.solve(chol, y[..., None])[..., 0]
    white_q = np.linalg.solve(chol, np.broadcast_to(q.T, (*profile.shape[:-1], 4, len(basis))))
    numerator = (white_y[..., :, None] * white_q).sum(-2)
    denominator = np.square(white_q).sum(-2)
    amplitude = np.divide(numerator, denominator, out=np.zeros_like(numerator), where=denominator > 0)
    residual = white_y[..., :, None] - amplitude[..., None, :] * white_q
    discrepancy = np.square(residual).sum(-2)
    return amplitude, discrepancy, stats.chi2.sf(discrepancy, [4, 3, 3, 3, 3, 3, 3])


def unique_gap(compatible):
    return (compatible.sum(-1) == 1) & compatible[..., 1:5].any(-1)


def trial_covariance(variance):
    return np.einsum("ij,...j,kj->...ik", D, variance, D)


def predict(distance, profile):
    targets = profile.reshape(-1, 5)
    q = bases(distance)
    errors = []
    for held in range(5):
        keep = np.delete(np.arange(5), held)
        y, train_basis = targets[:, keep], q[:, keep]
        mean_y = y.mean(1, keepdims=True)
        mean_q = train_basis.mean(1)
        centered = train_basis - mean_q[:, None]
        denominator = (centered**2).sum(1)
        amplitude = np.divide((y - mean_y) @ centered.T, denominator,
                              out=np.zeros((len(y), len(q))), where=denominator > 0)
        intercept = mean_y - amplitude * mean_q
        discrepancy = np.square(y[:, None, :] - intercept[..., None]
                                - amplitude[..., None] * train_basis).sum(-1)
        predictions = intercept + amplitude * q[:, held]
        gap = discrepancy[:, 1:5]
        tie = np.isclose(gap, gap.min(1, keepdims=True), rtol=1e-12, atol=1e-8)
        step = (predictions[:, 1:5] * tie).sum(1) / tie.sum(1)
        ordered = np.column_stack((predictions[:, 0], step, predictions[:, 5:7]))
        errors.append(np.square(targets[:, held, None] - ordered))
    return dict(zip(("flat", "step", "linear", "log_distance"),
                    np.sqrt(np.asarray(errors).mean((0, 1))).tolist()))


def independent_check(profile, covariance, basis, amplitude, discrepancy):
    """Validate the contrast calculation against direct five-point GLS."""
    diagonal = np.array([5., 9., 13., 7., 24.])
    y = np.array([710., 620., 640., 680., 710.])
    a, resid, _ = fit_contrasts(y, trial_covariance(diagonal), basis)
    for idx, response in enumerate(basis):
        design = np.stack((np.ones(5), response), axis=1)
        center, slope = np.linalg.lstsq(design / np.sqrt(diagonal[:, None]),
                                       y / np.sqrt(diagonal), rcond=None)[0]
        np.testing.assert_allclose(a[idx], slope, atol=1e-9)
        np.testing.assert_allclose(resid[idx], np.sum((y - center - slope * response)**2 / diagonal), atol=1e-9)
    shared = np.random.default_rng(SEED).normal(size=profile.shape[:-1])
    again = fit_contrasts(profile + shared[..., None] * 500, covariance, basis)
    np.testing.assert_allclose(again[0], amplitude, atol=1e-10)
    np.testing.assert_allclose(again[1], discrepancy, atol=1e-10)


def simulation(variance, distance):
    rng = np.random.default_rng(SEED + 2)
    basis = bases(distance)
    cov = trial_covariance(variance)
    cases = [("flat", 0, 0), ("80_ms_step", 2, 80), ("160_ms_step", 2, 160), ("80_ms_linear", 5, 80)]
    output = []
    for label, index, amplitude in cases:
        noise = rng.normal(size=(SIMULATIONS, *variance.shape)) * np.sqrt(variance)
        amps, _, p = fit_contrasts(noise + amplitude * basis[index], cov, basis)
        compatible = p >= .05
        unique = unique_gap(compatible)
        output.append(dict(scenario=label, cases=unique.size,
                           generating_family_retained=int(compatible[..., index].sum()),
                           unique_gap=int(unique.sum()),
                           correct_unique_gap=int((unique & compatible[..., index]).sum()) if index == 2 else None,
                           positive_unique_gap=int((unique & ((compatible[..., 1:5] & (amps[..., 1:5] > 0)).any(-1))).sum())))
    return output


def run():
    ids, at, _, audit = load_data()
    include = cohort_mask(ids, "primary40")
    ids, at = ids[include], at[include]
    mean = phase_profiles(np.nanmean(at, axis=-1))
    variance = np.nanvar(at, axis=-1, ddof=1) / np.isfinite(at).sum(-1)
    var6 = np.concatenate((variance, variance.reshape(len(ids), 2, 2, 5).sum(-2) / 4), axis=1)
    person_cov = trial_covariance(var6)
    group_cov = np.stack([np.cov((mean[:, i] @ D.T).T) / len(ids) for i in range(len(SUMMARY_LABELS))])
    records, summaries = [], {}
    for axis, distance in DISTANCES.items():
        q = bases(distance)
        amp, dev, p = fit_contrasts(mean, person_cov, q)
        independent_check(mean, person_cov, q, amp, dev)
        group_amp, group_dev, group_p = fit_contrasts(mean.mean(0), group_cov, q)
        for pid, slopes, deviations, probabilities in zip(
            [*ids, "equal_participant_group"], [*amp, group_amp], [*dev, group_dev], [*p, group_p]
        ):
            for cell, slope, deviation, probability in zip(SUMMARY_LABELS, slopes, deviations, probabilities):
                for k, name in enumerate(LABELS):
                    gap = 1 <= k <= 4
                    records.append(dict(axis=axis, participant=pid, cell=cell, family=name,
                                        gap_low_cm=distance[k-1] if gap else None, gap_high_cm=distance[k] if gap else None,
                                        amplitude_ms=float(slope[k]), discrepancy=float(deviation[k]),
                                        compatibility_p=float(probability[k]), compatible=bool(probability[k] >= .05)))
        comp = p[:, :4] >= .05
        groups = group_p >= .05
        summaries[axis] = dict(
            unique_gaps=int(unique_gap(comp).sum()),
            unique_positive_gaps=int((unique_gap(comp) & (comp[..., 1:5] & (amp[:, :4, 1:5] > 0)).any(-1)).sum()),
            no_compatible=int((comp.sum(-1) == 0).sum()),
            boundary_free_compatible=int(comp[..., [0, 5, 6]].any(-1).sum()),
            group_compatibility={name: [model for model, flag in zip(LABELS, cc) if flag]
                                 for name, cc in zip(SUMMARY_LABELS, groups)},
            held_distance_rmse_ms=predict(distance, mean[:, :4]),
        )
    csv = OUT / "change_point_candidates.csv"
    write_csv(csv, records)
    sources = (Path(__file__), Path(__file__).with_name("screen.py"), OUT / "CHANGE_POINT_SPECIFICATION.md", csv)
    manifest = dict(input=audit, summaries=summaries, simulation=simulation(variance, DISTANCES["registered"]),
                    runtime=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
                    checks="All seven contrast projections match independent five-point GLS; shift invariance verified.",
                    sha256={p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources})
    (OUT / "change_point_results.json").write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Exported {len(records)} change-point and boundary-free candidate fits.")


if __name__ == "__main__":
    run()
