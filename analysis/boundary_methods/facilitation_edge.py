"""Compare published rules for the farthest detectable tactile facilitation."""

import hashlib
import json
import platform
from functools import lru_cache
from pathlib import Path

import numpy as np
import scipy
from scipy import stats
from scipy.optimize import brentq

from adjacent_rule import boot_counts, paired_selection
from cue_time import matching
from profile import COHORTS
from screen import DISTANCES, EFFECTS, OUT, ROOT, SUMMARY_LABELS, W, cohort_mask, load_data
from inference import holm, jzs

SEED = 20261201
BOOTSTRAPS = 999
REPLICATES = 96
ALPHA = .05


def prepare(at, baseline, correction):
    n_probe = at.shape[-2]
    if correction == "offset_exact":
        included, used, weights = matching("exact")
        at_mean = np.nanmean(at[..., included, :], axis=-1)
        base_mean = np.nanmean(baseline[..., used, :], axis=-1) @ weights.T
        probes = np.flatnonzero(included)
    else:
        at_mean = np.nanmean(at, axis=-1)
        base_mean = (np.nanmean(baseline, axis=(-2, -1))[..., None] if correction == "pooled"
                     else np.nanmean(baseline, axis=-1))
        probes = np.arange(n_probe)
    differences = base_mean - at_mean
    phases = differences.reshape(len(at), 2, 2, len(probes)).mean(axis=2)
    return np.concatenate((differences, phases), axis=1), probes


def mean_statistics(values):
    n = values.shape[-3]
    k = values.shape[-1]
    mean = values.mean(axis=-3)
    se = values.std(axis=-3, ddof=1) / np.sqrt(n)
    t = np.divide(mean, se, out=np.zeros_like(mean), where=se > 0)
    radius = stats.t.isf(ALPHA / (2 * k), n - 1) * se
    return mean, t, np.stack((mean - radius, mean + radius), axis=-1)


def holm_array(raw):
    order = np.argsort(raw, axis=-1)
    ordered = np.take_along_axis(raw, order, axis=-1)
    adjusted = np.minimum(1., np.maximum.accumulate(ordered * np.arange(raw.shape[-1], 0, -1), axis=-1))
    return np.take_along_axis(adjusted, np.argsort(order, axis=-1), axis=-1)


@lru_cache(maxsize=None)
def bf_threshold(n):
    # The JZS integrand is increasing in |t|, so one cutoff serves all resamples.
    return brentq(lambda t: jzs(t, n) - 3., 0., 10.)


def qualifies(values, rule):
    if rule == "signed_rank_holm":
        upper = stats.wilcoxon(values, axis=-3, method="asymptotic", alternative="greater").pvalue
        upper = np.where(np.isfinite(upper), upper, .5)
        adjusted = holm_array(2 * np.minimum(upper, 1 - upper))
        return (upper < .5) & (adjusted < ALPHA), adjusted, {}
    mean, t, _ = mean_statistics(values)
    n = values.shape[-3]
    adjusted = np.minimum(1., 2 * values.shape[-1] * stats.t.sf(abs(t), n - 1))
    supported = (mean > 0) & (adjusted < ALPHA) & (t >= bf_threshold(n))
    return supported, adjusted, {"t": t}


def select(supported):
    return np.where(supported, np.arange(supported.shape[-1]), -1).max(axis=-1)


def locations(probes):
    return {key: values[probes].tolist() for key, values in DISTANCES.items()}


def probe_number(selection, probes):
    return int(probes[selection]) if selection >= 0 else None


def observed(values, probes, rule):
    n, _, k = values.shape
    qualified, p, extra = qualifies(values, rule)
    mean, _, interval = mean_statistics(values)
    if "t" in extra:
        factors = np.array([[jzs(t, n) for t in row] for row in extra["t"]])
        extra = {"bf10": factors.tolist(),
                 "qualifies_at_bf10_gt_10": ((mean > 0) & (p < ALPHA) & (factors > 10)).tolist()}
        np.testing.assert_array_equal(qualified, (mean > 0) & (p < ALPHA) & (factors >= 3))

    rng = np.random.default_rng(SEED)
    draws = values[rng.integers(n, size=(BOOTSTRAPS, n))]
    selected = select(qualifies(draws, rule)[0])
    stability = {}
    for label, control, viscereality in (("Exhale", 0, 2), ("Inhale", 1, 3), ("equal_phase", 4, 5)):
        states = paired_selection(selected[:, control], selected[:, viscereality])
        stability[label] = {k.replace("gap", "probe"): v for k, v in states.items()}
    deletions = []
    for held in range(k):
        kept = np.delete(np.arange(k), held)
        choice = select(qualifies(values[..., kept], rule)[0])
        deletions.append([probe_number(i, probes[kept]) for i in choice])
    contrasts = np.einsum("ec,ncp->nep", W, values[:, :4])
    difference, _, difference_ci = mean_statistics(contrasts)
    return dict(probes=probes.tolist(), distance_cm=locations(probes), participants=n,
                mean=mean.tolist(), median=np.median(values, axis=0).tolist(),
                simultaneous_intervals=interval.tolist(), adjusted_p=p.tolist(),
                qualifying=qualified.tolist(), selected_probe=[probe_number(i, probes) for i in select(qualified)],
                bootstrap_counts_none_then_near_to_far=boot_counts(selected, k).tolist(),
                paired_selection=stability, delete_one_probe_selection=deletions,
                paired_rt_contrasts=difference.tolist(), paired_rt_intervals=difference_ci.tolist(), **extra)


def recovery(values, probes, rule, log_rt):
    rng = np.random.default_rng(SEED + 1)
    residuals = values - values.mean(axis=0)
    shape = probes <= np.array([1, 1, 2, 2, 1, 2])[:, None]
    for amplitude, flat in ((0., True), (40., False), (120., False), (120., True)):
        change = np.log1p(amplitude / 500) if log_rt else amplitude
        signal = np.full(shape.shape, change) if flat else change * shape
        sample = residuals[rng.integers(len(values), size=(REPLICATES, len(values)))] + signal
        choice = select(qualifies(sample, rule)[0])
        truth = select(signal > 0)
        correct = choice == truth
        yield dict(amplitude_equivalent_ms=amplitude, constant=flat, replicates=REPLICATES,
                   truth_probe=[probe_number(i, probes) for i in truth],
                   correct_counts=correct.sum(0).tolist(), no_selection_counts=(choice < 0).sum(0).tolist(),
                   wrong_probe_counts=((choice >= 0) & ~correct).sum(0).tolist(),
                   both_equal_phase_correct=int(correct[:, -2:].all(-1).sum()),
                   any_selected=int((choice >= 0).any(-1).sum()))


def checks():
    rng = np.random.default_rng(602)
    planted = rng.normal(0., .25, (40, 6, 5)) + (np.arange(5) <= 2)
    cases = [{"p": value} for value in (.013, .06, .0001, .07, .013)]
    holm(cases)
    raw = np.array([row["p"] for row in cases])
    np.testing.assert_allclose(holm_array(raw), [row["p_holm"] for row in cases])
    for rule in ("signed_rank_holm", "paired_t_jzs"):
        np.testing.assert_array_equal(select(qualifies(planted, rule)[0]), np.full(6, 2))
        np.testing.assert_array_equal(select(qualifies(-planted, rule)[0]), np.full(6, -1))
    assert np.flatnonzero(matching("exact")[0]).tolist() == [1, 4]


def run():
    checks()
    ids, at, baseline, audit = load_data()
    estimates, simulations = [], []
    for rule, log_rt in (("signed_rank_holm", True), ("paired_t_jzs", False)):
        latencies = (np.log(at), np.log(baseline)) if log_rt else (at, baseline)
        for correction in ("pooled", "same_label", "offset_exact"):
            values, probes = prepare(*latencies, correction)
            tags = dict(rule=rule, baseline=correction, rt_scale="mean_log" if log_rt else "mean_ms")
            for cohort in COHORTS:
                mask = cohort_mask(ids, cohort)
                estimates.append(dict(tags, cohort=cohort, **observed(values[mask], probes, rule)))
            primary = values[cohort_mask(ids, "primary40")]
            simulations.extend(dict(tags, **row) for row in recovery(primary, probes, rule, log_rt))
    scripts = Path(__file__).parent
    pins = [Path(__file__), *(scripts / f"{name}.py" for name in ("adjacent_rule", "cue_time", "profile", "screen")),
            ROOT / "workbook/inference.py", ROOT / "analysis/baseline_effects/baseline_effects.py",
            ROOT / "analysis/baseline_effects/requirements.txt", OUT / "FACILITATION_EDGE_SPECIFICATION.md"]
    result = dict(input=audit, seed=SEED, bootstrap_replicates=BOOTSTRAPS, profiles=SUMMARY_LABELS,
                  effects=EFFECTS, observed=estimates, recovery=simulations,
                  runtime=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
                  sha256={p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in pins})
    (OUT / "facilitation_edge_results.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
    print(f"Verified {len(estimates)} cohort × method × baseline combinations and {len(simulations)} recovery batches.")


if __name__ == "__main__":
    run()
