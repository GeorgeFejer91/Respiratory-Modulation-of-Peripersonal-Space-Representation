"""Measured-range PPS shape audit and nested participant prediction comparison."""

from collections import Counter

import numpy as np
from scipy import stats

from descriptive_sigmoid import (DISTANCES, LABELS, SEED, ProfileGrid, fit_line,
                                 parameter_rows, predict, predict_line,
                                 score_candidates, smooth, visible_geometry, extract_cells,
                                 response_coordinates)


def geometry(parameters, x):
    passed, q, below, above, central, departure = visible_geometry(parameters[:, 2:], x)
    return [dict(condition=c, phase=p, nonflat=bool(v[1] >= 1e-6),
                 near_fraction=float(q[j, 0]), far_fraction=float(q[j, -1]),
                 positions_below_midpoint=int(below[j]), positions_above_midpoint=int(above[j]),
                 positions_in_20_80_transition=int(central[j]),
                 relative_departure_from_line=float(departure[j]),
                 visible_transition=bool(passed[j] and v[1] >= 1e-6))
            for j, ((c, p), v) in enumerate(zip(LABELS, parameters))]


def fit_method(cubes, x, method, grid):
    y = cubes[method["aggregation"]].mean(0)
    ys = smooth(x, y, method["smoother"], method["strength"])
    return (fit_line(response_coordinates(x,method["family"]), ys) if method["family"] in ("linear","logarithmic")
            else grid.fit(x, ys, method["shared_width"])), y


def nested_prediction(cubes, x, ids, progress=None, families=("logistic","visible","linear")):
    """All tuning occurs inside each outer training set; test people stay unseen."""
    n = len(ids)
    folds = np.array_split(np.random.default_rng(SEED+10).permutation(n), min(6, n))
    errors = {f: np.zeros((n, 4, 5)) for f in (*families,"constant")}
    records = []
    for k, test in enumerate(folds):
        train = np.setdiff1d(np.arange(n), test)
        train_cubes = {key: cube[train] for key, cube in cubes.items()}
        record = {"fold": k+1, "test_participant_ids": [ids[i] for i in test], "methods": {}}
        for family in families:
            if progress:
                progress(f"Nested prediction: outer fold {k+1}/{len(folds)}, {family}")
            ranking, _ = score_candidates(train_cubes, x, family=family, fold_count=5)
            chosen = ranking[0]
            record["methods"][family] = {
                "selected_method": chosen["method"], "inner_tuning_rmse_ms": chosen["tuning_rmse_ms"],
                "inner_scores": [{"method": r["method"], "rmse_ms": r["tuning_rmse_ms"]} for r in ranking]}
            grid = ProfileGrid(visible=family=="visible")
            for j in range(len(x)):
                keep = np.arange(len(x)) != j
                subset = {key: cube[:, :, keep] for key, cube in train_cubes.items()}
                pars, y = fit_method(subset, x[keep], chosen, grid)
                prediction = (predict_line if family in ("linear","logarithmic") else predict)(pars, response_coordinates(x[[j]],family))[:, 0]-y.mean(1)
                target = cubes["mean"][test, :, j]-cubes["mean"][test][:, :, keep].mean(2)
                errors[family][test, :, j] = (target-prediction[None, :])**2
                errors["constant"][test, :, j] = target**2
        records.append(record)
    return {
        "outer_seed": SEED+10, "outer_folds": records,
        "scope": "Six outer participant folds; five inner participant folds crossed with omitted positions. "
                 "Each family selects extraction, smoothing and fitting using training participants only. Outer predictions "
                 "also omit the target position from fitting. Inner selection sees all design positions in "
                 "training participants. Evaluation conditions on profiles cleaned beforehand using each person's "
                 "eligible AT and Baseline hit RTs across all positions. People do not share cleaning thresholds, "
                 "but an omitted position can affect its own person's threshold. This is relative-profile prediction "
                 "for new people at the known design, not end-to-end prediction from uncleaned trials; "
                 "families/criteria were developed post hoc. Overlapping training sets preclude treating "
                 "folds as independent replicates or this evaluation as a confirmatory test.",
        "scores": [{"family": f, "outer_rmse_ms": float(np.sqrt(e.mean())),
                    "per_curve_rmse_ms": np.sqrt(e.mean((0, 2))).tolist(),
                    "per_participant_mse": e.mean((1, 2)).tolist()} for f, e in errors.items()]}


def followup_audit(rows,excluded_ids,progress=None,selection_draws=30):
    """Finite post-results checks on a cohort without ambiguous recordings."""
    ids,cubes,incomplete=extract_cells([r for r in rows if r["participant_id"] not in excluded_ids])
    if len(ids)<6:return {"status":"not_estimable","reason":"At least six complete records required."}
    x=(DISTANCES-10)/90
    prediction=nested_prediction(cubes,x,ids,progress,families=("logistic","visible","linear","logarithmic"))
    rankings={family:score_candidates(cubes,x,progress,family=family)[0] for family in ("visible","logarithmic")}
    chosen=rankings["visible"][0]
    specifications=("permissive",dict(tail=.20,departure_min=.025,flank_positions=1,central_fraction=.10)), ("existing",{}), ("strict",dict(tail=.05,departure_min=.10,flank_positions=2,central_fraction=.30))
    sensitivity=[]
    for label,spec in specifications:
        for floor in (.025,.05,.10):
            record=dict(criteria=label,width_floor_cm=90*floor,criteria_values=spec or dict(tail=.1,departure_min=.05,flank_positions=2,central_fraction=.2))
            try:grid=ProfileGrid(fine=True,visible=True,width_floor=floor,geometry_spec=spec)
            except ValueError:
                sensitivity.append(record|{"status":"not_estimable","reason":"No grid shape satisfies these criteria."});continue
            pars,points=fit_method(cubes,x,chosen,grid);errors=[]
            for j in range(5):
                keep=np.arange(5)!=j
                p,y=fit_method({key:v[:,:,keep] for key,v in cubes.items()},x[keep],chosen,grid)
                pred=predict(p,x[[j]])[:,0]-y.mean(1)
                target=cubes["mean"][:,:,j]-cubes["mean"][:,:,keep].mean(2)
                errors.append((target-pred)**2)
            parameters=parameter_rows(pars)
            for k,r in enumerate(parameters):r["width_at_bound"]=bool(pars[k,3]<=floor+1e-8 or pars[k,3]>=1-1e-8)
            sensitivity.append(record|dict(status="computed",parameters=parameters,allowed_shapes=int(grid.allowed.sum()),
                leave_position_rmse_ms=float(np.sqrt(np.mean(errors))),
                raw_point_rmse_ms=float(np.sqrt(np.mean((predict(pars,x)-cubes["mean"].mean(0))**2)))))
    rng=np.random.default_rng(20261019);selections=[];grid=ProfileGrid(fine=True,visible=True)
    for b in range(selection_draws):
        if progress:progress(f"Group method-selection stability: {b+1}/{selection_draws}")
        indices=rng.integers(0,len(ids),len(ids));sample={key:v[indices] for key,v in cubes.items()}
        ranking,_=score_candidates(sample,x,family="visible",identities=indices)
        pars,_=fit_method(sample,x,ranking[0],grid)
        selections.append(dict(replicate=b+1,method=ranking[0]["method"],parameters=parameter_rows(pars)))
    frequencies=Counter(r["method"] for r in selections)
    raw=curvature_test(cubes["mean"],x)
    for r in raw["rows"]:r.pop("p_holm",None)
    raw["method"]=raw["method"].replace("Holm correction across four curves.","All four p values unadjusted.")
    return dict(status="computed",excluded_ids=excluded_ids,participants=len(ids),participant_ids=ids,
        incomplete_participants=incomplete,prediction=prediction,selected_visible_method=chosen,
        log_distance_candidates=rankings["logarithmic"],geometry_sensitivities=sensitivity,
        selection_resamples=selections,selection_frequencies=[dict(method=k,draws=v) for k,v in frequencies.most_common()],
        raw_curvature=raw,selection_seed=20261019,
        interpretation="Post-results exclusion-cohort audit. Nested scores compare five response families on the same cleaned-profile target. Log distance is not an expectancy control. Nine geometry specifications are all reported with frozen preprocessing; their leave-position scores are descriptive and use all people. Thirty repeated-selection resamples diagnose instability, not tail confidence coverage. Original cleaning is fixed; no serial-dependence or physiological validation is claimed.")


def curvature_test(raw, x):
    """Hotelling test of all three departures from a line; NOT a sigmoid test."""
    basis = np.linalg.qr(np.column_stack([np.ones(5), x]), mode="complete")[0][:, 2:]
    n = len(raw)
    rows = []
    for j, (c, p) in enumerate(LABELS):
        contrasts = raw[:, j]@basis
        mean = contrasts.mean(0)
        covariance = np.cov(contrasts, rowvar=False)
        if np.linalg.matrix_rank(covariance) < 3 or n <= 3:
            rows.append(dict(condition=c, phase=p, status="not_estimable", reason="Singular covariance or insufficient participants"))
            continue
        t2 = n*float(mean@np.linalg.solve(covariance, mean))
        f = t2*(n-3)/(3*(n-1))
        rows.append(dict(condition=c, phase=p, status="computed", n=n, hotelling_t2=t2,
                         f=f, df1=3, df2=n-3, p=float(stats.f.sf(f, 3, n-3)),
                         nonlinear_component_rms_ms=float(np.sqrt(np.mean((basis@mean)**2)))))
    valid = sorted([r for r in rows if r["status"]=="computed"], key=lambda r:r["p"])
    last = 0.
    for i, r in enumerate(valid):
        last = min(1., max(last, (len(valid)-i)*r["p"]))
        r["p_holm"] = last
    return {"method": "Post hoc Hotelling T-squared on three orthonormal contrasts orthogonal to intercept "
                       "and distance; raw unsmoothed participant means. Assumes independent people, "
                       "multivariate-normal contrasts and nonsingular covariance. Holm correction across "
                       "four curves. Detects any nonlinearity, not specifically an S shape; a large p value "
                       "does not establish linearity.", "rows": rows}


def audit(cubes, x, ids, candidates, selected_parameters, progress=None, bootstrap_draws=1000):
    visible, _ = score_candidates(cubes, x, progress, family="visible")
    linear, _ = score_candidates(cubes, x, progress, family="linear")
    chosen = visible[0]
    grid = ProfileGrid(fine=True, visible=True)
    params, points = fit_method(cubes, x, chosen, grid)
    line, line_points = fit_method(cubes, x, linear[0], grid)
    dense = np.linspace(0, 1, 181)
    rng = np.random.default_rng(SEED+1)
    draws, bands = [], []
    for b in range(bootstrap_draws):
        if progress and b%200==0:
            progress(f"Shape-constrained participant bootstrap: {b}/{bootstrap_draws}")
        index = rng.integers(0, len(ids), len(ids))
        p, y = fit_method({key:cube[index] for key,cube in cubes.items()}, x, chosen, grid)
        draws.append(p)
        bands.append(predict(p, dense)-y.mean(1)[:, None])
    draws = np.array(draws)
    interval = np.percentile(bands, [2.5,97.5], axis=0)
    rows = parameter_rows(params)
    for j, r in enumerate(rows):
        nonflat = draws[:, j, 1] >= 1e-6
        r["bootstrap_flat_fraction"] = float(1-nonflat.mean())
        r["bootstrap_width_floor_fraction"] = float(np.mean(draws[:, j, 3] <= .05+1e-8))
        # Two design positions on each side restrict m to the open interval (x[1], x[-2]).
        r["midpoint_at_sampling_limit"] = bool(min(params[j,2]-x[1], x[-2]-params[j,2]) <= 1/240+1e-8)
        r["bootstrap_midpoint_sampling_limit_fraction"] = float(np.mean(
            np.minimum(draws[:,j,2]-x[1],x[-2]-draws[:,j,2]) <= 1/240+1e-8))
        for name, values in (("midpoint_cm",10+90*draws[:,j,2]),("width_cm",90*draws[:,j,3]),
                             ("midpoint_slope_ms_per_cm",draws[:,j,1]/(360*draws[:,j,3]))):
            ci = np.percentile(values[nonflat],[2.5,97.5]).tolist() if nonflat.any() else [None,None]
            r[name+"_conditional_bootstrap_low"], r[name+"_conditional_bootstrap_high"] = ci
    original_pass = 0
    for candidate in candidates:
        ps = np.array([[r["lower_asymptote_ms"],r["amplitude_ms"],(r["midpoint_cm"]-10)/90,r["width_cm"]/90]
                       for r in candidate["parameters"]])
        original_pass += all(r["visible_transition"] for r in geometry(ps, x))
    return {
        "criteria": "At least 10–90% of the logistic amplitude inside 10–100 cm; at least two sampled "
                    "positions on each side of the midpoint; at least one in the 20–80% transition; "
                    "maximum departure from the best dense-grid line at least 5% of the fitted observed "
                    "range; positive nonflat amplitude. These post hoc display/sampling thresholds are "
                    "not a validated physiological PPS definition.",
        "original_geometry": geometry(selected_parameters, x),
        "original_candidates_with_four_visible_transitions": original_pass,
        "visible_candidates": visible, "linear_candidates": linear,
        "visible_method": chosen["method"], "visible_tuning_rmse_ms": chosen["tuning_rmse_ms"],
        "visible_parameters": rows, "visible_geometry": geometry(params, x),
        "visible_points_ms": points.tolist(), "visible_predictions_ms": predict(params, dense).tolist(),
        "visible_centered_bootstrap_low_ms": interval[0].tolist(),
        "visible_centered_bootstrap_high_ms": interval[1].tolist(),
        "linear_method": linear[0]["method"], "linear_tuning_rmse_ms": linear[0]["tuning_rmse_ms"],
        "linear_points_ms": line_points.tolist(), "linear_predictions_ms": predict_line(line,dense).tolist(),
        "nested_prediction": nested_prediction(cubes, x, ids, progress),
        "raw_curvature": curvature_test(cubes["mean"], x),
        "interpretation": "Shape-constrained curves satisfy the geometry by construction when nonflat. "
                          "Their existence is not evidence that the measurements contain an S-shaped transition. "
                          "Intervals condition on the selected pipeline and shape constraints. Neither smoothing "
                          "nor display interpolation adds independent observed positions."}
