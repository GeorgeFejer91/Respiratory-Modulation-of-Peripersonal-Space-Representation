"""Post hoc, uniformly selected group sigmoid descriptions; no participant gate.

Five design positions are the observations. Smoothing never creates extra data.
See SIGMOID_EXPLORATION.md for the selection target, constraints and limitations.
Only NumPy/SciPy are required, including when this module runs in Pyodide.
"""

from collections import defaultdict

import numpy as np
from scipy import optimize, special, stats


SEED = 20261016
LABELS = [(c, p) for c in ("Control", "Viscereality") for p in ("Exhale", "Inhale")]
SOAS_NEAR_TO_FAR = (2700., 2200., 1500., 800., 300.)
DISTANCES = np.array([10., 27., 50., 73., 100.])


def extract_cells(rows):
    """Equal person weight, with five alternative within-person cell summaries."""
    groups = defaultdict(list)
    for r in rows:
        if r["trial_type"] == "Audio-Tactile":
            groups[(r["participant_id"], r["condition"], r["phase"], float(r["soa_ms"]))].append(float(r["reaction_time_ms"]))
    ids = sorted({key[0] for key in groups})
    complete = [pid for pid in ids if all((pid, c, p, s) in groups for c, p in LABELS for s in SOAS_NEAR_TO_FAR)]
    summaries = {"mean": np.mean, "median": np.median,
                 "trim10": lambda a: stats.trim_mean(a, .1),
                 "trim20": lambda a: stats.trim_mean(a, .2),
                 "winsor20": lambda a: np.mean(np.clip(a, *np.sort(a)[[int(.2*len(a)), len(a)-int(.2*len(a))-1]]))}
    cubes = {name: np.array([[[float(fn(np.array(groups[(pid, c, p, s)]))) for s in SOAS_NEAR_TO_FAR]
                             for c, p in LABELS] for pid in complete]) for name, fn in summaries.items()}
    return complete, cubes, sorted(set(ids)-set(complete))


def smoother_specs():
    return ([("none", 0.), ("isotonic", 0.)]
            + [(k, b) for k in ("gaussian_constant", "gaussian_linear") for b in (.1, .15, .2, .3, .4, .5, .65, .8)]
            + [("tricube_linear", b) for b in (.5, .75, 1., 1.5)]
            + [("curvature_penalty", b) for b in (.0001, .001, .01, .1, 1., 10.)]
            + [("gaussian_isotonic", b) for b in (.15, .2, .3, .5)])


def smooth(x, y, kind, strength):
    x, y = np.asarray(x), np.asarray(y)
    if kind == "none":
        return y.copy()
    if kind == "isotonic":
        return np.array([optimize.isotonic_regression(a, increasing=True).x for a in y])
    if kind == "gaussian_isotonic":
        return smooth(x, smooth(x, y, "gaussian_constant", strength), "isotonic", 0.)
    if kind == "curvature_penalty":
        d = np.zeros((len(x)-2, len(x)))
        for i in range(len(x)-2):
            h1, h2 = x[i+1]-x[i], x[i+2]-x[i+1]
            d[i, i:i+3] = [1/h1, -1/h1-1/h2, 1/h2]
        return np.linalg.solve(np.eye(len(x))+strength*d.T@d, y.T).T
    u = np.abs((x[:, None]-x[None, :])/strength)
    weights = np.maximum(1-u**3, 0.)**3 if kind == "tricube_linear" else np.exp(-.5*u*u)
    if kind == "gaussian_constant":
        return y @ (weights/weights.sum(1)[:, None]).T
    hat = []
    for i, center in enumerate(x):
        z = np.column_stack([np.ones(len(x)), x-center])
        hat.append(np.linalg.pinv(z.T@(weights[i, :, None]*z))[0] @ z.T * weights[i])
    return y @ np.array(hat).T


class ProfileGrid:
    """Global finite-grid search; offset/amplitude solved exactly at each shape."""

    def __init__(self, fine=False, expanded=False, visible=False):
        self.midpoints = np.linspace(-.5 if expanded else 0., 1.5 if expanded else 1., 241 if fine else 61)
        self.widths = np.geomspace(.01 if expanded else .05, 2. if expanded else 1., 81 if fine else 35)
        m, w = np.meshgrid(self.midpoints, self.widths, indexing="ij")
        self.shapes = np.column_stack([m.ravel(), w.ravel()])
        self.amplitude_limit = 1000. if expanded else 500.
        self.cache = {}
        self.allowed = np.ones(len(self.shapes), dtype=bool)
        if visible:
            self.allowed = visible_geometry(self.shapes, (DISTANCES-10)/90)[0]
            if not np.any(self.allowed):
                raise ValueError("No grid shapes satisfy the measured-range criteria.")

    def fit(self, x, y, shared_width=False):
        key = tuple(x)
        if key not in self.cache:
            q = special.expit((np.asarray(x)[None, :]-self.shapes[:, 0, None])/self.shapes[:, 1, None])
            qc = q-q.mean(1)[:, None]
            self.cache[key] = q.mean(1), qc, np.sum(qc*qc, axis=1)
        qmean, qc, ss = self.cache[key]
        centered = y-y.mean(1)[:, None]
        numerator = centered@qc.T
        amplitude = np.clip(numerator/np.maximum(ss, 1e-30), 0., self.amplitude_limit)
        base = y.mean(1)[:, None]-amplitude*qmean[None, :]
        loss = np.sum(centered*centered, axis=1)[:, None]-2*amplitude*numerator+amplitude*amplitude*ss
        loss[:, ~self.allowed] = np.inf
        if shared_width:
            by = loss.reshape(len(y), len(self.midpoints), len(self.widths))
            iw = np.argmin(by.min(axis=1).sum(axis=0))
            index = np.argmin(by[:, :, iw], axis=1)*len(self.widths)+iw
        else:
            index = np.argmin(loss, axis=1)
        return np.column_stack([base[np.arange(len(y)), index], amplitude[np.arange(len(y)), index], self.shapes[index]])


def predict(parameters, x):
    return parameters[:, 0, None]+parameters[:, 1, None]*special.expit((np.asarray(x)[None, :]-parameters[:, 2, None])/parameters[:, 3, None])


def visible_geometry(shapes, x):
    """Post hoc display/sampling criteria, not a physiological significance test."""
    m, w = shapes[:, 0, None], shapes[:, 1, None]
    q = special.expit((x[None, :]-m)/w)
    dense = np.linspace(min(x), max(x), 181)
    curve = special.expit((dense[None, :]-m)/w)
    z = dense-dense.mean()
    residual = curve-curve.mean(1)[:, None]-(curve@z/(z@z))[:, None]*z
    departure = np.max(np.abs(residual), axis=1)/np.maximum(np.ptp(curve, axis=1), 1e-30)
    below, above = np.sum(x[None, :] < m, axis=1), np.sum(x[None, :] > m, axis=1)
    central = np.sum((q >= .2) & (q <= .8), axis=1)
    coverage = (q[:, 0] <= .1) & (q[:, -1] >= .9)
    passes = coverage & (below >= 2) & (above >= 2) & (central >= 1) & (departure >= .05)
    return passes, q, below, above, central, departure


def fit_line(x, y):
    z = x-x.mean()
    slope = y@z/(z@z)
    return np.column_stack([y.mean(1)-slope*x.mean(), slope])


def predict_line(parameters, x):
    return parameters[:, :1]+parameters[:, 1:2]*np.asarray(x)[None, :]


def parameter_rows(parameters, distances=DISTANCES):
    span, origin = float(np.ptp(distances)), float(np.min(distances))
    result = []
    for (c, p), (base, amplitude, m, w) in zip(LABELS, parameters):
        width = float(w*span)
        result.append({"condition": c, "phase": p, "lower_asymptote_ms": float(base),
                       "upper_asymptote_ms": float(base+amplitude), "amplitude_ms": float(amplitude),
                       "midpoint_cm": float(origin+m*span), "width_cm": width,
                       "normalized_steepness_per_cm": float(1/(4*width)),
                       "midpoint_slope_ms_per_cm": float(amplitude/(4*width)),
                       "transition_10_90_cm": float(2*np.log(9)*width),
                       "midpoint_at_bound": bool(m <= 1e-8 or m >= 1-1e-8),
                       "width_at_bound": bool(w <= .05+1e-8 or w >= 1-1e-8),
                       "amplitude_at_bound": bool(amplitude >= 500-1e-6),
                       "flat_unidentified": bool(amplitude < 1e-6)})
    return result


def candidate_id(aggregation, kind, strength, shared):
    return f"{aggregation}/{kind}/{strength:g}/{'shared' if shared else 'separate'}"


def score_candidates(cubes, x, progress=None, family="logistic", fold_count=6):
    """Hold out people AND positions before extraction/smoothing/model fitting.

    A fixed raw-mean within-person shape target permits aggregation comparisons.
    Scores select a method; they are not unbiased post-selection test estimates.
    """
    n = len(cubes["mean"])
    folds = np.array_split(np.random.default_rng(SEED).permutation(n), min(fold_count, n))
    grid = ProfileGrid(visible=family=="visible")
    raw = cubes["mean"]
    prepared = []
    constant_errors, linear_errors = [], []
    for test in folds:
        train = np.setdiff1d(np.arange(n), test)
        for j in range(len(x)):
            keep = np.arange(len(x)) != j
            target = raw[test, :, j]-raw[test][:, :, keep].mean(2)
            train_raw = raw[train].mean(0)[:, keep]
            z = x[keep]-x[keep].mean()
            slope = train_raw@z/(z@z)
            linear = slope*(x[j]-x[keep].mean())
            constant_errors.append(float(np.mean(target**2)))
            linear_errors.append(float(np.mean((target-linear[None, :])**2)))
            prepared.append((train, keep, j, target))
    weights = np.array([len(target) for _, _, _, target in prepared])
    records = []
    for aggregation, cube in cubes.items():
        if progress:
            progress(f"{family} search: {aggregation} extraction (uniform four-curve methods)")
        for kind, strength in smoother_specs():
            for shared in ((False,) if family=="linear" else (False, True)):
                sq = []
                for train, keep, j, target in prepared:
                    y = cube[train].mean(0)[:, keep]
                    ys = smooth(x[keep], y, kind, strength)
                    pars = fit_line(x[keep], ys) if family=="linear" else grid.fit(x[keep], ys, shared)
                    pred = predict_line if family=="linear" else predict
                    contrast = pred(pars, x[[j]])[:, 0]-y.mean(1)
                    sq.append(float(np.mean((target-contrast[None, :])**2)))
                ys = smooth(x, cube.mean(0), kind, strength)
                params = fit_line(x, ys) if family=="linear" else grid.fit(x, ys, shared)
                fold_rmse = np.sqrt(np.mean(np.array(sq).reshape(len(folds), len(x)), axis=1))
                records.append({"method": candidate_id(aggregation, kind, strength, shared),
                                "aggregation": aggregation, "smoother": kind, "strength": strength,
                                "shared_width": shared, "family": family,
                                "tuning_rmse_ms": float(np.sqrt(np.average(sq, weights=weights))),
                                "fold_rmse_ms": fold_rmse.tolist(),
                                "fold_rmse_se_ms": float(np.std(fold_rmse, ddof=1)/np.sqrt(len(folds))),
                                "parameters": parameter_rows(params) if family!="linear" else params.tolist()})
    records.sort(key=lambda r: (r["tuning_rmse_ms"], r["method"]))
    return records, {"constant_shape_rmse_ms": float(np.sqrt(np.average(constant_errors, weights=weights))),
                     "linear_shape_rmse_ms": float(np.sqrt(np.average(linear_errors, weights=weights))),
                     "folds": [[int(i) for i in fold] for fold in folds],
                     "target": "Raw within-person mean at omitted position minus that person's mean of the other four positions",
                     "caution": "Method selection uses these scores; not an independent confirmatory prediction test. Fold errors are dependent."}


def run(rows, progress=None, bootstrap_draws=1000):
    ids, cubes, incomplete = extract_cells(rows)
    if len(ids) < 6:
        return {"status": "not_estimable", "reason": "At least six complete participants are required for the uniform search."}
    x = (DISTANCES-DISTANCES.min())/np.ptp(DISTANCES)
    candidates, validation = score_candidates(cubes, x, progress)
    chosen = candidates[0]
    cube = cubes[chosen["aggregation"]]
    kind, strength, shared = chosen["smoother"], chosen["strength"], chosen["shared_width"]
    fine = ProfileGrid(fine=True)

    def estimate(values, coordinates=x, grid=fine):
        return grid.fit(coordinates, smooth(coordinates, values.mean(0), kind, strength), shared)

    parameters = estimate(cube)
    rows_out = parameter_rows(parameters)
    display_x = np.linspace(0., 1., 181)
    rng = np.random.default_rng(SEED+1)
    draws, bands, centered_bands = [], [], []
    for b in range(bootstrap_draws):
        if progress and b % 200 == 0:
            progress(f"Whole-participant bootstrap: {b}/{bootstrap_draws}; same resample for all four curves")
        indices = rng.integers(0, len(ids), len(ids))
        params = estimate(cube[indices])
        draws.append(params)
        bands.append(predict(params, display_x))
        centered_bands.append(predict(params, display_x)-cube[indices].mean(0).mean(1)[:, None])
    draws = np.array(draws)
    bands = np.percentile(bands, [2.5, 97.5], axis=0)
    centered_bands = np.percentile(centered_bands, [2.5, 97.5], axis=0)
    for j, record in enumerate(rows_out):
        valid = draws[:, j, 1] >= 1e-6
        record["bootstrap_nonflat_draws"] = int(sum(valid))
        record["bootstrap_flat_fraction"] = float(1-np.mean(valid))
        record["bootstrap_midpoint_bound_fraction"] = float(np.mean((draws[:, j, 2] <= 1e-8) | (draws[:, j, 2] >= 1-1e-8)))
        record["bootstrap_width_bound_fraction"] = float(np.mean((draws[:, j, 3] <= .05+1e-8) | (draws[:, j, 3] >= 1-1e-8)))
        values = {"midpoint_cm": 10+90*draws[:, j, 2], "width_cm": 90*draws[:, j, 3],
                  "midpoint_slope_ms_per_cm": draws[:, j, 1]/(360*draws[:, j, 3]),
                  "amplitude_ms": draws[:, j, 1]}
        for name, vector in values.items():
            interval = np.percentile(vector[valid], [2.5, 97.5]).tolist() if np.any(valid) else [None, None]
            record[name+"_conditional_bootstrap_low"], record[name+"_conditional_bootstrap_high"] = interval
    comparisons = []
    for label, weights in (("Control Inhale − Exhale", [-1, 1, 0, 0]),
                           ("Viscereality Inhale − Exhale", [0, 0, -1, 1]),
                           ("Viscereality − Control at Exhale", [-1, 0, 1, 0]),
                           ("Viscereality − Control at Inhale", [0, -1, 0, 1]),
                           ("Condition × Phase", [1, -1, -1, 1])):
        weights = np.array(weights)
        valid = np.all(draws[:, weights != 0, 1] >= 1e-6, axis=1)
        for name, values, point in (("midpoint_cm", 10+90*draws[:, :, 2], 10+90*parameters[:, 2]),
                                    ("width_cm", 90*draws[:, :, 3], 90*parameters[:, 3]),
                                    ("midpoint_slope_ms_per_cm", draws[:, :, 1]/(360*draws[:, :, 3]), parameters[:, 1]/(360*parameters[:, 3]))):
            interval = np.percentile(values[valid]@weights, [2.5, 97.5]).tolist() if np.any(valid) else [None, None]
            comparisons.append({"contrast": label, "parameter": name, "estimate": float(point@weights),
                                "conditional_bootstrap_low": interval[0], "conditional_bootstrap_high": interval[1],
                                "nonflat_draws": int(sum(valid)), "classification": "descriptive, conditional on selected method"})
    # Robust reference is fixed, transparent and separate from the tuning winner.
    reference = fine.fit(x, smooth(x, cubes["trim20"].mean(0), "gaussian_constant", .3), False)
    reference_id = candidate_id("trim20", "gaussian_constant", .3, False)
    trajectory = np.array([20., 36.6666666667, 60., 83.3333333333, 100.])
    tx = (trajectory-trajectory.min())/np.ptp(trajectory)
    expanded = ProfileGrid(fine=True, expanded=True)
    sensitivity = {
        "robust_reference_method": reference_id,
        "robust_reference_tuning_rmse_ms": next(r["tuning_rmse_ms"] for r in candidates if r["method"] == reference_id),
        "robust_reference_parameters": parameter_rows(reference),
        "robust_reference_points_ms": cubes["trim20"].mean(0).tolist(),
        "robust_reference_predictions_ms": predict(reference, display_x).tolist(),
        "trajectory_axis_parameters": parameter_rows(estimate(cube, tx), trajectory),
        "expanded_bounds_parameters": parameter_rows(estimate(cube, grid=expanded)),
        "expanded_bounds": "Normalized midpoint [-0.5,1.5], width [0.01,2], amplitude [0,1000] ms; flags in this table refer to the main bounds.",
    }
    for j, record in enumerate(rows_out):
        record["raw_point_rmse_ms"] = float(np.sqrt(np.mean((predict(parameters, x)[j]-cubes["mean"].mean(0)[j])**2)))
    from sigmoid_shape import audit
    shape_audit = audit(cubes, x, ids, candidates, parameters, progress, bootstrap_draws)
    return {"status": "computed", "classification": "post hoc descriptive regularized group sigmoids",
            "participants": len(ids), "participant_ids": ids, "excluded_incomplete_participants": incomplete,
            "seed": SEED, "bootstrap_seed": SEED+1, "bootstrap_draws": bootstrap_draws,
            "bootstrap_scope": "Participant cluster percentile intervals conditional on chosen method and nonflat curves; method selection is not repeated. Boundary mass is reported separately. Bands include flat draws.",
            "formula": "RT(d) = lower + amplitude * expit((d - midpoint) / width)",
            "parameter_definitions": "width is logistic scale, not a Gaussian SD; normalized midpoint steepness = 1/(4*width), RT derivative = amplitude/(4*width), 10–90% span = 2*ln(9)*width",
            "bounds": {"midpoint_cm": [10, 100], "width_cm": [4.5, 90], "amplitude_ms": [0, 500]},
            "grid": {"selection_midpoints": 61, "selection_widths": 35, "final_midpoints": 241, "final_widths": 81},
            "selection": "Smallest crossed person/position shape-prediction RMSE; one pipeline/hyperparameter set for all four curves. Post hoc tuning, no new significance test.",
            "selected_method": chosen["method"], "selected_tuning_rmse_ms": chosen["tuning_rmse_ms"],
            "candidate_count": len(candidates), "candidates": candidates, "validation": validation,
            "parameters": rows_out, "comparisons": comparisons, "sensitivity": sensitivity,
            "shape_audit": shape_audit,
            "distances_cm": DISTANCES.tolist(), "soa_ms_near_to_far": list(SOAS_NEAR_TO_FAR),
            "raw_points_ms": cubes["mean"].mean(0).tolist(),
            "extracted_points_ms": cube.mean(0).tolist(),
            "smoothed_points_ms": smooth(x, cube.mean(0), kind, strength).tolist(),
            "display_distance_cm": (10+90*display_x).tolist(), "predictions_ms": predict(parameters, display_x).tolist(),
            "pointwise_bootstrap_low_ms": bands[0].tolist(), "pointwise_bootstrap_high_ms": bands[1].tolist(),
            "centered_bootstrap_low_ms": centered_bands[0].tolist(),
            "centered_bootstrap_high_ms": centered_bands[1].tolist()}
