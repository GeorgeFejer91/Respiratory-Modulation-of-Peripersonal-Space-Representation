"""Exact support for horizontal shifts under an unknown common monotone RT curve."""

import hashlib
import json
import platform
from pathlib import Path

import numpy as np
import scipy
from scipy.optimize import isotonic_regression, linprog, minimize_scalar
from scipy.special import expit
from scipy.stats import t

from profile import COHORTS
from screen import DISTANCES, OUT, ROOT, cohort_mask, load_data, phase_profiles
from threshold_bands import MeanProbeInputs, group_bands

ALPHA = .05 / 6
SEED = 20261202
REPLICATES = 96
DISTANCE_TOLERANCE = 1e-7
PAIRS = (("Condition within Exhale", 0, 2), ("Condition within Inhale", 1, 3),
         ("Condition equal phase", 4, 5), ("Phase within Control", 0, 1),
         ("Phase within Viscereality", 2, 3))


def shift_atoms(distance):
    values = np.unique(np.round((distance[:, None] - distance).ravel(), 8))
    atoms = [(-np.inf, values[0], False, False)]
    for lo, hi in zip(values[:-1], values[1:]):
        atoms.extend([(lo, lo, True, True), (lo, hi, False, False)])
    atoms.extend([(values[-1], values[-1], True, True), (values[-1], np.inf, False, False)])
    reps = np.array([hi - 1 if np.isneginf(lo) else lo + 1 if np.isposinf(hi) else (lo + hi) / 2
                     for lo, hi, _, _ in atoms])
    return atoms, reps


def shifted_axis(distance, delta):
    return np.r_[distance, distance - delta]


def order_at(distance, delta):
    position = shifted_axis(distance, delta)
    return position[:, None] <= position + DISTANCE_TOLERANCE


def pooled_coordinates(distance, delta):
    positions = shifted_axis(distance, delta)
    sort = positions.argsort()
    breaks = np.r_[True, np.diff(positions[sort]) > DISTANCE_TOLERANCE]
    index = np.empty(len(sort), dtype=int)
    index[sort] = breaks.cumsum() - 1
    counts = np.bincount(index)
    return np.bincount(index, weights=positions) / counts, index, counts


def fit_sets(lower, upper, distance, shifts, allow_level):
    p = len(distance)
    group = np.repeat([0, 1], p)
    sign = group[:, None] - group
    required = lower[..., :, None] - upper[..., None, :]
    result = []
    for shift in shifts:
        order = order_at(distance, shift)
        if allow_level:
            feasible = (required[..., order & (sign == 0)] <= 1e-9).all(axis=-1)
            bottom = np.max(required, axis=(-2, -1), where=order & (sign == 1), initial=-np.inf)
            top = np.min(-required, axis=(-2, -1), where=order & (sign == -1), initial=np.inf)
            result.append(feasible & (bottom <= top + 1e-9))
        else:
            result.append((required[..., order] <= 1e-9).all(axis=-1))
    return np.stack(result, axis=-1)


def merge(intervals):
    connected = []
    for a, b, close_a, close_b in sorted(intervals, key=lambda z: (z[0], not z[2], z[1])):
        if connected and (a < connected[-1][1] or (a == connected[-1][1] and (close_a or connected[-1][3]))):
            lo, hi, inc_lo, inc_hi = connected[-1]
            connected[-1] = (lo, max(hi, b), inc_lo, close_b if b > hi else inc_hi or (close_b and b == hi))
        else:
            connected.append((a, b, close_a, close_b))
    return connected


def difference(later, earlier):
    return merge([(a - d, b - c, ca and cd, cb and cc)
                  for a, b, ca, cb in later for c, d, cc, cd in earlier])


def packed(intervals):
    return [[float(lo) if np.isfinite(lo) else None, float(hi) if np.isfinite(hi) else None,
             bool(close_lo), bool(close_hi)] for lo, hi, close_lo, close_hi in intervals]


def support_rows(lo, hi, valid, labels, distance, tags):
    atoms, representatives = shift_atoms(distance)
    for allow_level in (True, False):
        pieces = {}
        for name, first, second in PAIRS:
            good = valid[:, first] & valid[:, second]
            left = lo[good][:, [first, second]]
            right = hi[good][:, [first, second]]
            lo_fit, hi_fit = (x.reshape(-1, 2 * len(distance)) for x in (left, right))
            supported = fit_sets(lo_fit, hi_fit, distance, representatives, allow_level)
            flat_each = (left.max(-1) <= right.min(-1) + 1e-9).all(-1)
            boundary_free = flat_each if allow_level else lo_fit.max(-1) <= hi_fit.min(-1) + 1e-9
            for label in labels[~good]:
                yield dict(tags, profile=name, level_offset=allow_level, participant=str(label),
                           status="variance_unavailable")
            for label, support, flat in zip(labels[good], supported, boundary_free):
                interval = merge([atom for atom, keep in zip(atoms, support) if keep])
                pieces[label, name] = interval
                yield dict(tags, profile=name, level_offset=allow_level, participant=str(label),
                           status="compatible" if interval else "incompatible", pieces=packed(interval),
                           supports_no_transition=bool(flat),
                           full_overlap_domain=bool(support[1:-1].all()),
                           overlap_atoms_kept=int(support[1:-1].sum()), overlap_atoms=len(atoms) - 2)
        for label in labels:
            before = pieces.get((label, PAIRS[0][0]))
            after = pieces.get((label, PAIRS[1][0]))
            if before is None or after is None:
                yield dict(tags, profile="Condition × Phase", level_offset=allow_level,
                           participant=str(label), status="variance_unavailable")
            else:
                result = difference(after, before)
                yield dict(tags, profile="Condition × Phase", level_offset=allow_level,
                           participant=str(label), status="compatible" if result else "incompatible",
                           pieces=packed(result))


def fit_mean(y, distance, shifts):
    n = len(distance)
    groups = np.repeat([0., 1.], n)
    vertical_limit = [y[n:].min() - y[:n].max(), y[n:].max() - y[:n].min()]
    best = (np.inf, None, None, None, None)
    for d in sorted(shifts, key=lambda u: (abs(u), u)):
        x, index, counts = pooled_coordinates(distance, d)

        def model(level, predicted=False):
            centered = y - level * groups
            pooled = np.bincount(index, weights=centered) / counts
            fitted = isotonic_regression(pooled, weights=counts).x
            error = np.sum(np.square(centered - fitted[index]))
            return (error, fitted) if predicted else error

        if vertical_limit[0] == vertical_limit[1]:
            level = vertical_limit[0]
        else:
            trial = minimize_scalar(model, bounds=vertical_limit, method="bounded", options={"xatol": 1e-7})
            level = min((trial.x, *vertical_limit), key=model)
        loss, estimate = model(level, predicted=True)
        if loss < best[0] - 1e-8:
            best = loss, d, level, x, estimate
    return best[1:]


def predict(y, distance):
    names = ("separate_constants", "separate_isotonic", "zero_shift", "free_shift")
    errors = {key: [] for key in names}
    rows = []
    for held in range(len(distance)):
        keep = np.arange(len(distance)) != held
        x = distance[keep]
        _, shifts = shift_atoms(x)
        span = np.ptp(distance)
        shifts = np.r_[shifts[abs(shifts) < span], -span, span]
        for comparison, first, second in PAIRS:
            profiles = y[[first, second]]
            training, target = profiles[:, keep], profiles[:, held]
            fitted = dict(separate_constants=training.mean(-1),
                          separate_isotonic=[np.interp(distance[held], x, isotonic_regression(row).x)
                                             for row in training])
            selected = {}
            for name, candidates in (("zero_shift", [0.]), ("free_shift", shifts)):
                delta, level, points, curve = fit_mean(training.ravel(), x, candidates)
                fitted[name] = np.interp(distance[held] - np.array([0., delta]), points, curve) + [0., level]
                selected[name] = dict(shift_cm=float(delta), level_ms=float(level))
            for name, m in fitted.items():
                errors[name].extend(np.square(m - target))
            rows.append(dict(comparison=comparison, held_probe_index=held, observed_ms=target.tolist(),
                             predicted_ms={name: np.asarray(m).tolist() for name, m in fitted.items()},
                             conditional_fit=selected))
    return dict(rmse_ms={key: float(np.sqrt(np.mean(errors[key]))) for key in names}, folds=rows)


def recovery(observations, distance):
    residual = observations - observations.mean(axis=0)
    rng = np.random.default_rng(SEED)
    _, shifts = shift_atoms(distance)
    for delta, span in ((0., 0.), (20., 80.), (40., 160.)):
        s = np.r_[distance, distance - delta]
        population = span * expit((s - 54) / 9) + np.repeat([0., 25.], len(distance))
        samples = residual[rng.integers(len(residual), size=(REPLICATES, len(residual)))] + population
        means = samples.mean(1)
        radius = t.isf(ALPHA / (2 * len(distance)), len(residual) - 1) * samples.std(1, ddof=1) / np.sqrt(len(residual))
        for free in (True, False):
            args = means - radius, means + radius, distance
            result = fit_sets(*args, shifts, free)
            yield dict(shift_cm=delta, span_ms=span, level_offset=free, replicates=REPLICATES,
                       plant_compatible=int(fit_sets(*args, [delta], free).sum()),
                       zero_shift_excluded=int((~fit_sets(*args, [0.], free)).sum()),
                       no_compatible_shift=int((~result.any(-1)).sum()),
                       nonempty_zero_excluded=int((result.any(-1) & ~fit_sets(*args, [0.], free).ravel()).sum()),
                       full_overlap_domain=int(result[:, 1:-1].all(-1).sum()),
                       unbounded_both=int((result[:, 0] & result[:, -1]).sum()))


def checks():
    distance = DISTANCES["registered"]
    rng = np.random.default_rng(72)
    _, reps = shift_atoms(distance)
    group = np.repeat([0, 1], len(distance))
    for _ in range(6):
        lower = np.sort(rng.normal(size=(2, len(distance))), axis=-1).ravel() + rng.normal(size=2).repeat(5)
        upper = lower + rng.uniform(.1, 1.2, size=len(lower))
        for delta in np.r_[reps[::10], [-20., 0., 40.]]:
            i, j = np.where(order_at(distance, delta) & ~np.eye(len(lower), dtype=bool))
            eye = np.eye(len(lower))
            constraints = np.column_stack((eye[i] - eye[j], group[j] - group[i]))
            for free in (True, False):
                expected = linprog(np.zeros(len(lower) + 1), A_ub=constraints, b_ub=np.zeros(len(i)),
                                   bounds=[*zip(lower, upper), (None, None) if free else (0., 0.)],
                                   method="highs").success
                actual = fit_sets(lower, upper, distance, [delta], free)[0]
                assert expected == actual, (delta, expected, actual)
    tied = np.r_[distance, distance + 15]
    assert fit_sets(tied, tied, distance, [0.], True)[0]
    assert not fit_sets(tied, tied, distance, [0.], False)[0]
    trajectory = DISTANCES["trajectory"]
    n = len(trajectory)
    for first, i in enumerate(trajectory):
        for second, j in enumerate(trajectory):
            delta = round(j - i, 8)
            assert order_at(trajectory, delta)[first, n + second]
            assert order_at(trajectory, delta)[n + second, first]
            _, labels, _ = pooled_coordinates(trajectory, delta)
            assert labels[first] == labels[n + second]
    assert difference([(-np.inf, 1., False, True)], [(1., np.inf, True, False)]) == [(-np.inf, 0., False, True)]


def run():
    checks()
    ids, at, baseline, audit = load_data()
    primary = cohort_mask(ids, "primary40")
    result, forecasts, simulations = [], [], []
    for correction in ("pooled_cp", "same_label"):
        data = MeanProbeInputs.from_trials(at, baseline, correction)
        per_person = tuple(x[primary] for x in data.individual_bands(ALPHA))
        for axis, distance in DISTANCES.items():
            tags = dict(axis=axis, correction=correction)
            result.extend(support_rows(*per_person, ids[primary], distance, dict(tags, cohort="participants")))
            for cohort in COHORTS:
                keep = cohort_mask(ids, cohort)
                per_group = tuple(x[None] for x in group_bands(data.center[keep], ALPHA))
                result.extend(support_rows(*per_group, np.array(["equal_participant_group"]), distance,
                                           dict(tags, cohort=cohort)))
            profiles = phase_profiles(data.center[primary])
            forecasts.append(dict(tags, **predict(profiles.mean(0), distance)))
            if axis == "registered":
                rows = profiles[:, [4, 5]].reshape(len(profiles), -1)
                simulations.extend(dict(tags, **d) for d in recovery(rows, distance))
    pins = [Path(__file__), *(Path(__file__).with_name(f"{name}.py") for name in ("threshold_bands", "profile", "screen")),
            ROOT / "analysis/baseline_effects/baseline_effects.py", ROOT / "analysis/baseline_effects/requirements.txt",
            OUT / "MONOTONE_SHIFT_SPECIFICATION.md"]
    output = dict(input=audit, seed=SEED, observed=result, prediction=forecasts, recovery=simulations,
                  runtime=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
                  sha256={p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in pins})
    (OUT / "monotone_shift_results.json").write_text(json.dumps(output, indent=2, allow_nan=False) + "\n",
                                                     encoding="utf-8", newline="\n")
    print(f"Wrote {len(result)} shift sets, {len(forecasts)} predictive comparisons and {len(simulations)} recovery cells.")


if __name__ == "__main__":
    run()
