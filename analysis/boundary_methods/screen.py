"""Run the fixed Spearman–Kärber and log-latency boundary screen."""

import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np
import scipy
from scipy import stats
from scipy.optimize import isotonic_regression

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis" / "baseline_effects"))
from baseline_effects import CELL_NAMES, DISTANCES, EFFECTS, W, CurveGrid, cohort_mask, load_data, resample_trials, write_csv

OUT = ROOT / "results" / "boundary_methods"
SEED = 20261116
BOOTSTRAPS = 999
SIMULATIONS = 256
SUMMARY_LABELS = (*CELL_NAMES, "Control equal phase", "Viscereality equal phase")


def trimmed(tensor):
    counts = np.sum(np.isfinite(tensor), axis=-1)
    assert np.all(counts > 0)
    trim = np.floor(counts * .05 + .5).astype(int)
    position = np.arange(tensor.shape[-1])
    keep = (position >= trim[..., None]) & (position < (counts - trim)[..., None])
    return np.sum(np.where(keep, np.sort(tensor, axis=-1), 0), axis=-1) / (counts - 2 * trim)


def monotone(values):
    """Equal-weight isotonic fits via the max–min interval-average formula."""
    count = values.shape[-1]
    return np.stack([
        np.maximum.reduce([
            np.minimum.reduce([values[..., first:last + 1].mean(-1) for last in range(index, count)])
            for first in range(index + 1)
        ])
        for index in range(count)
    ], axis=-1)


def karber(profile, distance):
    amplitude = np.ptp(profile, axis=-1, keepdims=True)
    scaled = np.divide(profile - profile.min(-1, keepdims=True), amplitude,
                       out=np.zeros_like(profile), where=amplitude > 1e-10)
    fitted = monotone(scaled)
    edges = np.r_[2 * distance[0] - distance[1], distance, 2 * distance[-1] - distance[-2]]
    mass = np.diff(fitted, axis=-1, prepend=0, append=1)
    centroid = mass @ ((edges[1:] + edges[:-1]) / 2)
    second = mass @ ((edges[1:]**2 + edges[1:] * edges[:-1] + edges[:-1]**2) / 3)
    limen = .6745 * np.sqrt(np.maximum(0, second - centroid**2))
    stats_ = np.stack([centroid, limen, mass[..., 0] + mass[..., -1]], axis=-1)
    return np.where((np.ptp(fitted, axis=-1) > 1e-10)[..., None], stats_, np.nan)


def phase_profiles(values):
    return np.concatenate((values, values.reshape(*values.shape[:-2], 2, 2, 5).mean(-2)), axis=-2)


def intervals(samples):
    finite = samples[np.isfinite(samples)]
    low, high = np.quantile(finite, [.025, .975]) if len(finite) else (None, None)
    return {"replicates": len(samples), "finite": len(finite), "ci_low": low, "ci_high": high}


def blank(value):
    return float(value) if np.isfinite(value) else None


def compare_predictions(y, distance, grid=None):
    target = y.reshape(-1, 5)
    loss = []
    for j, x in enumerate(distance):
        keep = np.delete(np.arange(5), j)
        train = target[:, keep]
        if grid is None:
            fit = monotone(train)
            pred = np.array([np.interp(x, distance[keep], row) for row in fit])
        else:
            _, fitted, _ = grid.fit(train, columns=keep)
            pred = fitted[:, j]
        loss.append((np.square(pred - target[:, j]), np.square(train.mean(1) - target[:, j])))
    rmses = np.sqrt(np.mean(loss, axis=(0, 2)))
    return {"candidate_rmse": float(rmses[0]), "constant_rmse": float(rmses[1])}


def compare_log_and_raw(at):
    soa = np.array([300., 800., 1500., 2200., 2700.])
    grid = CurveGrid(soa, "fixed_extrema_logistic")
    all_profiles = [("arithmetic_mean_rt", np.nanmean(at, axis=-1)),
                    ("mean_log_rt", np.nanmean(np.log(at), axis=-1) * 1000)]
    estimates = {}
    for name, profile in all_profiles:
        target = phase_profiles(profile)[..., ::-1]
        persons = target.reshape(-1, 5)
        params, fitted, bounds = grid.fit(np.vstack([persons, target.mean(0)]))
        unit_scale = 1000 if name == "mean_log_rt" else 1
        estimates[name] = dict(midpoint=params[:, 2], width=params[:, 3], bound=bounds,
                               signed_span=params[:, 1] / unit_scale,
                               in_sample_rmse=np.sqrt(((fitted - np.vstack([persons, target.mean(0)]))**2).mean(-1)) / unit_scale)
        predictive = compare_predictions(target[:, :4], soa, grid)
        estimates[name]["predictive"] = {key: value / unit_scale for key, value in predictive.items()}
    return estimates


def checks(distance):
    rng = np.random.default_rng(SEED + 1)
    test = rng.normal(size=(256, len(distance)))
    expected = np.array([isotonic_regression(row).x for row in test])
    np.testing.assert_allclose(monotone(test), expected, atol=1e-13)
    assert np.isnan(karber(np.ones(5), distance)).all()
    assert np.isnan(karber(np.arange(5.)[::-1], distance)).all()
    step = karber(np.array([0., 0., 1., 1., 1.]), distance)
    np.testing.assert_allclose(step, [(distance[1] + distance[2]) / 2,
                                      .6745 * (distance[2] - distance[1]) / np.sqrt(12), 0])
    np.testing.assert_allclose(karber(test, distance), karber(3 * test + 70, distance), atol=1e-11)
    return "256 independent SciPy PAVA comparisons, flat and reversed rejection, exact single-step moments, affine invariance"


def simulation(at, distance, rng):
    sd = np.nanstd(at, axis=-1, ddof=1)
    assert np.isfinite(sd).all()
    observed = np.isfinite(at)
    midpoint = (distance[1] + distance[2]) / 2
    summary = []
    for jump in (0, 80, 160):
        available, errors = [], []
        for _ in range(SIMULATIONS):
            profile = 650 + rng.normal(size=at.shape) * sd[..., None]
            profile[..., 2:, :] += jump
            values = karber(trimmed(np.where(observed, profile, np.nan)), distance)[..., 0]
            available.extend(values[np.isfinite(values)])
            if jump:
                errors.extend(values[np.isfinite(values)] - midpoint)
        summary.append(dict(jump_ms=jump, generated=SIMULATIONS * at.shape[0] * 4,
                            finite=len(available), median_cm=blank(np.median(available)),
                            percentile_cm=np.quantile(available, [.025, .975]).tolist(),
                            mae_cm=float(np.abs(errors).mean()) if errors else None))
    return summary


def run():
    ids, at, baseline, data = load_data()
    use = cohort_mask(ids, "primary40")
    ids, at, baseline = ids[use], at[use], baseline[use]
    rng = np.random.default_rng(SEED)
    distance = DISTANCES["registered"]
    verified = checks(distance)
    profile = phase_profiles(trimmed(at))
    prior_baseline_mean = np.nanmean(baseline, axis=(2, 3))
    np.testing.assert_allclose(
        karber(profile[:, :4], distance), karber(profile[:, :4] - prior_baseline_mean[..., None], distance),
        atol=1e-10, equal_nan=True)
    refits = np.array([phase_profiles(trimmed(resample_trials(at, rng))) for _ in range(BOOTSTRAPS)])
    groups = np.array([profile[rng.integers(len(ids), size=len(ids))].mean(0) for _ in range(BOOTSTRAPS)])
    split = [phase_profiles(trimmed(at[..., offset::2])) for offset in (0, 1)]
    log_rt = compare_log_and_raw(at)
    records = []
    summary = dict(seed=SEED, checks=verified, input=data, cohorts=[len(ids)], specs={},
                   simulation=simulation(at, distance, rng), log_rt_prediction={},
                   pava_prediction=compare_predictions(profile[:, :4], distance),
                   runtime=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__))
    for axis, distance in DISTANCES.items():
        cell = karber(profile, distance)
        group = karber(profile.mean(0), distance)
        trial_boot = karber(refits, distance)[..., 0]
        group_boot = karber(groups, distance)[..., 0]
        for pid, value, bootstrap in zip([*ids, "equal_participant_group"],
                                         [*cell, group], [*trial_boot.transpose(1, 0, 2), group_boot]):
            for index, label in enumerate(SUMMARY_LABELS):
                centroid, limen, tails = value[index]
                records.append(dict(participant=pid, cell=label, axis=axis, centroid_cm=blank(centroid),
                                    difference_limen_cm=blank(limen), padded_tail_mass=blank(tails),
                                    **intervals(bootstrap[:, index])))
        a, b = (karber(s, distance)[..., 0].ravel() for s in split)
        valid = np.isfinite(a) & np.isfinite(b)
        group_contrasts = []
        individual_contrasts = []
        for label, weights in zip(EFFECTS, W):
            required = weights != 0
            vals = cell[:, :4, 0][:, required] @ weights[required]
            bootstrap = group_boot[:, :4][:, required] @ weights[required]
            group_contrasts.append(dict(effect=label, estimate_cm=blank(group[:4, 0][required] @ weights[required]),
                                        **intervals(bootstrap)))
            individual_contrasts.append(dict(effect=label, paired_n=int(np.isfinite(vals).sum()),
                                             conditional_mean_cm=blank(np.nanmean(vals))))
        condition_delta = group[5, 0] - group[4, 0]
        condition_draws = group_boot[:, 5] - group_boot[:, 4]
        summary["specs"][axis] = dict(finite_individual_cells=int(np.isfinite(cell[:, :4, 0]).sum()),
                                      split_half_n=int(valid.sum()), split_half_rho=float(stats.spearmanr(a[valid], b[valid]).statistic),
                                      equal_phase_group_difference=dict(estimate_cm=blank(condition_delta),
                                                                        **intervals(condition_draws)),
                                      group_profile_contrasts=group_contrasts, individual_contrasts=individual_contrasts)
    log_records = []
    keys = [(pid, label) for pid in [*ids, "equal_participant_group"] for label in SUMMARY_LABELS]
    for method, value in log_rt.items():
        for index, (pid, label) in enumerate(keys):
            midpoint = value["midpoint"][index]
            interior = 300 <= midpoint <= 2700
            nominal_cm = np.interp(midpoint, [300, 800, 1500, 2200, 2700], DISTANCES["registered"][::-1])
            log_records.append(dict(method=method, participant=pid, cell=label, midpoint_soa_ms=midpoint,
                                    midpoint_nominal_cm=nominal_cm if interior else None,
                                    width_soa_ms=value["width"][index], grid_bound=bool(value["bound"][index]),
                                    outside_design=not interior, signed_span=value["signed_span"][index],
                                    in_sample_rmse=value["in_sample_rmse"][index]))
        summary["log_rt_prediction"][method] = value["predictive"]
    write_csv(OUT / "spearman_karber.csv", records)
    write_csv(OUT / "fixed_extrema_rt_scales.csv", log_records)
    files = [Path(__file__), OUT / "SPECIFICATION.md", OUT / "spearman_karber.csv", OUT / "fixed_extrema_rt_scales.csv"]
    summary["sha256"] = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    (OUT / "screen_results.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Exported {len(records)} Spearman–Kärber and {len(log_records)} fixed-extrema fits.")


if __name__ == "__main__":
    run()
