"""Project individual mean RT uncertainty into farthest sampled facilitation sets."""

import hashlib
import json
import platform
from pathlib import Path

import numpy as np
import scipy
from scipy.stats import t

from cue_time import matching
from profile import moments
from screen import DISTANCES, EFFECTS, OUT, ROOT, SUMMARY_LABELS, W, cohort_mask, load_data, write_csv
from threshold_bands import MeanProbeInputs

ALPHA = .05
SEED = 20261208
REPLICATES = 96
CONTRASTS = (*EFFECTS, "Condition of equal-phase profiles")


def prepare(at, baseline, reference):
    probes = np.arange(at.shape[-2])
    if reference == "offset_exact":
        included, used, weights = matching("exact")
        if not np.array_equal(weights, np.eye(int(included.sum()))):
            raise ValueError("Exact cue matches must pair corresponding probe means without reuse.")
        return MeanProbeInputs(moments(at[..., included, :]), moments(baseline[..., used, :])), probes[included]
    return MeanProbeInputs.from_trials(at, baseline, reference), probes


def mean_limits(stats, tail):
    means, variance, df = stats
    radius = t.isf(tail, df) * np.sqrt(variance)
    return means - radius, means + radius


def profile_limits(stats, alpha, primitive_count):
    phase = mean_limits(stats, alpha / (2 * primitive_count))
    joint = mean_limits(stats, alpha / (4 * primitive_count))
    return tuple(
        np.concatenate((separate, paired.reshape(*paired.shape[:-2], 2, 2, paired.shape[-1]).mean(-2)), axis=-2)
        for separate, paired in zip(phase, joint, strict=True)
    )


def project_endpoints(at_lower, at_upper, base_lower, base_upper):
    """Return compatible probes in near-to-far order, followed by no facilitation."""
    available = np.isfinite(np.concatenate((at_lower, at_upper, base_lower, base_upper), axis=-1)).all(-1)
    if base_upper.shape[-1] == 1:
        # A common Baseline value must let all farther probe means be at least as high.
        ceiling = np.minimum(at_upper, base_upper)
        largest_baseline = np.minimum.accumulate(ceiling[..., ::-1], axis=-1)[..., ::-1]
        farther_ceiling = np.concatenate((largest_baseline[..., 1:], base_upper), axis=-1)
        possible = (base_lower <= farther_ceiling) & (at_lower < farther_ceiling)
        none = base_lower <= largest_baseline[..., :1]
    else:
        nonpositive = base_lower <= at_upper
        farther_nonpositive = np.logical_and.accumulate(nonpositive[..., ::-1], axis=-1)[..., ::-1]
        unrestricted = np.ones_like(nonpositive[..., :1])
        possible = (base_upper > at_lower) & np.concatenate((farther_nonpositive[..., 1:], unrestricted), axis=-1)
        none = farther_nonpositive[..., :1]
    return np.concatenate((possible, none), axis=-1) & available[..., None], available


def endpoint_sets(inputs, alpha):
    count = inputs.at[0].shape[-1] + inputs.baseline[0].shape[-1]
    return project_endpoints(*profile_limits(inputs.at, alpha, count), *profile_limits(inputs.baseline, alpha, count))


def paired_bounds(states, available, distances):
    probes = states[..., :-1]
    lower = np.min(np.where(probes, distances, np.inf), axis=-1)
    upper = np.max(np.where(probes, distances, -np.inf), axis=-1)
    weights = np.pad(W, ((0, 0), (0, 2)))
    weights = np.vstack((weights, [0, 0, 0, 0, -1, 1]))
    for name, row in zip(CONTRASTS, weights, strict=True):
        active = np.flatnonzero(row)
        signed = row[active]
        valid = available[..., active].all(-1)
        undefined = states[..., active, -1].any(-1)
        finite = probes[..., active, :].any(-1).all(-1)
        lo = np.sum(signed * np.where(signed > 0, lower[..., active], upper[..., active]), axis=-1)
        hi = np.sum(signed * np.where(signed > 0, upper[..., active], lower[..., active]), axis=-1)
        yield name, valid, undefined, np.where(finite, lo, np.nan), np.where(finite, hi, np.nan)


def omitted_sets(inputs, probes):
    for local, global_index in enumerate(probes):
        keep = np.arange(len(probes)) != local
        at = tuple(values[..., keep] for values in inputs.at)
        baseline = inputs.baseline
        if baseline[0].shape[-1] > 1:
            baseline = tuple(values[..., keep] for values in baseline)
        states, available = endpoint_sets(MeanProbeInputs(at, baseline), ALPHA)
        yield int(global_index), probes[keep], states, available


def observed_rows(inputs, probes, ids, reference):
    states, available = endpoint_sets(inputs, ALPHA)
    joint, valid = endpoint_sets(inputs, ALPHA / 4)
    omissions = list(omitted_sets(inputs, probes))
    profiles, contrasts = [], []
    for i, pid in enumerate(ids):
        for j, name in enumerate(SUMMARY_LABELS):
            mask = states[i, j]
            selected = probes[mask[:-1]]
            localized = mask.sum() == 1 and not mask[-1]
            eligible = bool(available[i, j])
            profiles.append(dict(
                participant=pid, reference=reference, profile=name, available=eligible,
                localized=bool(localized), no_facilitation_possible=bool(mask[-1]) if eligible else None,
                compatible_probe_indices=json.dumps(selected.tolist()),
                registered_cm=json.dumps(DISTANCES["registered"][selected].tolist()),
                trajectory_cm=json.dumps(DISTANCES["trajectory"][selected].tolist()),
                outermost_probe_possible=bool(mask[-2]) if eligible else None,
                omission_sets=json.dumps({
                    omitted: dict(
                        probe_indices=kept[sets[i, j, :-1]].tolist(), available=bool(estimable[i, j]),
                        no_facilitation=bool(sets[i, j, -1]) if estimable[i, j] else None,
                    )
                    for omitted, kept, sets, estimable in omissions
                }),
            ))
    for axis, distances in DISTANCES.items():
        for name, valid_rows, undefined, low, high in paired_bounds(joint, valid, distances[probes]):
            for i, pid in enumerate(ids):
                has_limits = np.isfinite(low[i])
                contrasts.append(dict(
                    participant=pid, reference=reference, axis=axis, effect=name,
                    available=bool(valid_rows[i]), undefined_possible=bool(undefined[i]) if valid_rows[i] else None,
                    conditional_low_cm=float(low[i]) if has_limits else None,
                    conditional_high_cm=float(high[i]) if has_limits else None,
                    excludes_zero=bool(valid_rows[i] and not undefined[i] and (low[i] > 0 or high[i] < 0)),
                ))
    return profiles, contrasts


def simulate_summary(stats, truth, rng):
    means, variance, df = stats
    shape = (REPLICATES, *means.shape)
    df_positive = np.maximum(df, 1)
    sampled_mean = truth + rng.normal(size=shape) * np.sqrt(variance)
    sampled_variance = variance * rng.chisquare(df_positive, size=shape) / df_positive
    return sampled_mean, sampled_variance, df


def recovery(inputs, probes, rng):
    for name, strength, edges in (
        ("zero", 0, [4] * 4), ("constant_120ms", 120, [4] * 4),
        ("step_40ms", 40, [1, 1, 2, 2]), ("step_120ms", 120, [1, 1, 2, 2]),
    ):
        signal = strength * (probes <= np.asarray(edges)[:, None])
        truth = np.max(np.where(signal > 0, np.arange(len(probes)), -1), axis=-1)
        truth = np.concatenate((truth, truth[::2]))
        planted = MeanProbeInputs(simulate_summary(inputs.at, 650 - signal, rng),
                                  simulate_summary(inputs.baseline, 650, rng))
        sets, available = endpoint_sets(planted, ALPHA)
        joint, valid = endpoint_sets(planted, ALPHA / 4)
        covered = sets[..., np.arange(len(SUMMARY_LABELS)), truth]
        unique = sets.sum(-1) == 1
        truth_states = np.eye(len(probes) + 1, dtype=bool)[truth]
        axes = {}
        for axis, distances in DISTANCES.items():
            bounds = {}
            fitted_bounds = paired_bounds(joint, valid, distances[probes])
            truth_bounds = paired_bounds(truth_states, np.ones(len(truth), dtype=bool), distances[probes])
            for fitted, known in zip(fitted_bounds, truth_bounds, strict=True):
                label, valid_rows, undefined, low, high = fitted
                truth_undefined, truth_cm = known[2:4]
                finite = np.isfinite(low)
                truth_covered = undefined if truth_undefined else (low <= truth_cm) & (truth_cm <= high)
                bounds[label] = dict(
                    available=int(valid_rows.sum()), undefined_possible=int((undefined & valid_rows).sum()),
                    truth_cm=None if truth_undefined else float(truth_cm),
                    truth_covered=int((valid_rows & truth_covered).sum()),
                    finite_conditional=int(finite.sum()),
                    mean_conditional_width_cm=float(np.mean((high - low)[finite])) if finite.any() else None,
                )
            axes[axis] = bounds
        count = lambda mask: mask.sum(axis=(0, 1)).tolist()
        yield dict(generator=name, truth_probe_indices=[int(probes[i]) if i >= 0 else None for i in truth],
                   available=count(available), coverage=count(covered), unique_correct=count(unique & covered),
                   unique_incorrect=count(unique & ~covered), paired_effects=axes)


def run():
    ids, at, baseline, audit = load_data()
    keep = cohort_mask(ids, "primary40")
    rng = np.random.default_rng(SEED)
    profiles, contrasts, simulations = [], [], {}
    for reference in ("pooled_cp", "same_label", "offset_exact"):
        inputs, probes = prepare(at[keep], baseline[keep], reference)
        rows, paired = observed_rows(inputs, probes, ids[keep], reference)
        profiles.extend(rows)
        contrasts.extend(paired)
        simulations[reference] = list(recovery(inputs, probes, rng))

    sets_path = OUT / "individual_facilitation_profiles.csv"
    contrasts_path = OUT / "individual_facilitation_contrasts.csv"
    write_csv(sets_path, profiles)
    write_csv(contrasts_path, contrasts)
    scripts = Path(__file__).parent
    files = [
        Path(__file__), *(scripts / f"{name}.py" for name in ("cue_time", "profile", "screen", "threshold_bands")),
        ROOT / "analysis/baseline_effects/baseline_effects.py", ROOT / "analysis/baseline_effects/requirements.txt",
        OUT / "INDIVIDUAL_FACILITATION_SPECIFICATION.md", sets_path, contrasts_path,
    ]
    result = dict(input=audit, seed=SEED, replicates=REPLICATES, profile_rows=len(profiles),
                  contrast_rows=len(contrasts), simulation=simulations,
                  runtime=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
                  sha256={path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest() for path in files})
    (OUT / "individual_facilitation_results.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
    print(f"Wrote {len(profiles)} individual endpoint sets and {len(contrasts)} paired contrast bounds.")


if __name__ == "__main__":
    run()
