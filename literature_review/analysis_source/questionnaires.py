"""Exploratory MAIA-2 and ordinal spatial-frame analyses; see ANALYSIS_PLAN.md."""

import numpy as np
from scipy import stats

from preparation import validate_questionnaire_rows


SCALES = {
    "noticing": (1, 4), "not_distracting": (5, 10), "not_worrying": (11, 15),
    "attention_regulation": (16, 22), "emotional_awareness": (23, 27),
    "self_regulation": (28, 31), "body_listening": (32, 34), "trusting": (35, 37),
}
REVERSED = {5, 6, 7, 8, 9, 10, 11, 12, 15}
BOOTSTRAPS = 2000
PERMUTATIONS = 19999
SEED = 20261116
DELTA_SEED = 20261117


def number(row, key):
    value = row.get(key, "")
    return float(value) if value not in ("", None) else np.nan


def finite(value):
    return float(value) if np.isfinite(value) else None


def interval(draws):
    valid = np.asarray(draws)[np.isfinite(draws)]
    return (np.quantile(valid, [.025, .975]).tolist() if len(valid) else [None, None])


def alpha(items):
    """Raw alpha; final dimensions are people × items, optionally batched."""
    k = items.shape[-1]
    total_variance = items.sum(axis=-1).var(axis=-1, ddof=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        value = k / (k - 1) * (1 - items.var(axis=-2, ddof=1).sum(axis=-1) / total_variance)
    return np.where(total_variance > 0, value, np.nan)


def rank_correlation(x, y):
    rx, ry = stats.rankdata(x, axis=-1), stats.rankdata(y, axis=-1)
    rx, ry = rx - rx.mean(axis=-1, keepdims=True), ry - ry.mean(axis=-1, keepdims=True)
    denominator = np.sqrt((rx * rx).sum(axis=-1) * (ry * ry).sum(axis=-1))
    with np.errstate(divide="ignore", invalid="ignore"):
        return (rx * ry).sum(axis=-1) / denominator


def score_people(people):
    validate_questionnaire_rows(people)
    scored, audit = [], []
    for person in people:
        record = {"participant_id": person["participant_id"], "condition_order": person["condition_order"]}
        for name, (start, stop) in SCALES.items():
            field = "maia2_" + name
            items = [number(person, f"maia2_item_{i:02d}") for i in range(start, stop + 1)]
            items = [5 - value if i in REVERSED else value for i, value in zip(range(start, stop + 1), items)]
            value = float(np.mean(items)) if all(np.isfinite(items)) else np.nan
            record[field] = finite(value)
            stored = number(person, field)
            audit.append({"participant_id": person["participant_id"], "field": field,
                          "recomputed": finite(value), "stored": finite(stored),
                          "status": "match" if np.isfinite(value) and np.isfinite(stored) and abs(value-stored) <= 1e-6
                          else "mismatch" if np.isfinite(value) and np.isfinite(stored)
                          else "stored_only" if np.isfinite(stored) else "recomputed_only" if np.isfinite(value) else "missing"})
        for condition in ("control", "viscereality"):
            key = "spfrref_" + condition + "_ordinal"
            record[key] = finite(number(person, key))
        c, v = (number(record, "spfrref_" + name + "_ordinal") for name in ("control", "viscereality"))
        record["spfrref_delta"] = finite(v - c)
        record["spfrref_change_direction"] = finite(np.sign(v - c))
        scored.append(record)
    return scored, audit


def describe(values):
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    return {"n": len(values), "mean": float(values.mean()) if len(values) else None,
            "sd": float(values.std(ddof=1)) if len(values) > 1 else None,
            "median": float(np.median(values)) if len(values) else None,
            "q1": float(np.quantile(values, .25)) if len(values) else None,
            "q3": float(np.quantile(values, .75)) if len(values) else None,
            "min": float(values.min()) if len(values) else None,
            "max": float(values.max()) if len(values) else None}


def spatial_summary(scored, rng, bootstrap_draws):
    pairs = [r for r in scored if r["spfrref_change_direction"] is not None]
    direction = np.array([r["spfrref_change_direction"] for r in pairs])
    higher, lower, ties = (int(np.sum(direction == v)) for v in (1, -1, 0))
    n = len(pairs)
    result = {"status": "computed" if n else "not_estimable", "n_pairs": n,
              "missing_pairs": len(scored)-n, "higher": higher, "lower": lower, "ties": ties,
              "non_ties": higher+lower, "p": None, "higher_fraction_non_ties": None,
              "higher_fraction_ci_low": None, "higher_fraction_ci_high": None,
              "paired_dominance": float(direction.mean()) if n else None,
              "dominance_ci_low": None, "dominance_ci_high": None,
              "method": "two-sided exact sign test, ties excluded from binomial denominator",
              "interpretation": "Higher means a higher A–H code; administered pictogram anchors are unavailable."}
    if higher+lower:
        test = stats.binomtest(higher, higher+lower, .5)
        ci = test.proportion_ci(method="exact")
        result.update(p=float(test.pvalue), higher_fraction_non_ties=higher/(higher+lower),
                      higher_fraction_ci_low=float(ci.low), higher_fraction_ci_high=float(ci.high))
    if n:
        draws = direction[rng.integers(n, size=(bootstrap_draws, n))].mean(axis=1)
        result["dominance_ci_low"], result["dominance_ci_high"] = interval(draws)
    result["order_counts"] = [dict(condition_order=order,
        n=sum(r["condition_order"] == order for r in pairs),
        **{label: sum(r["condition_order"] == order and r["spfrref_change_direction"] == sign for r in pairs)
           for label, sign in (("higher", 1), ("ties", 0), ("lower", -1))})
        for order in sorted({r["condition_order"] for r in scored})]
    result["transitions"] = [{"control": c, "viscereality": v,
        "n": sum(r["spfrref_control_ordinal"] == c and r["spfrref_viscereality_ordinal"] == v for r in pairs)}
        for c in range(1, 9) for v in range(1, 9)]
    result["distributions"] = [{"condition": condition, "category": category,
        "n": sum(r["spfrref_" + condition.lower() + "_ordinal"] == category for r in scored)}
        for condition in ("Control", "Viscereality") for category in range(1, 9)]
    # Medians and quartiles refer only to category codes, not physical distances.
    result["descriptives"] = [{"condition": c, **{k: v for k, v in describe(
        [number(r, "spfrref_"+c.lower()+"_ordinal") for r in scored]).items() if k not in ("mean", "sd")}}
        for c in ("Control", "Viscereality")]
    return result


def association(scored, xkey, ykey, rng, permutations, bootstrap_draws):
    pairs = np.array([(number(r, xkey), number(r, ykey)) for r in scored], dtype=float)
    pairs = pairs[np.isfinite(pairs).all(axis=1)]
    n = len(pairs)
    out = {"x": xkey, "y": ykey, "n": n, "status": "not_estimable", "rho": None,
           "ci_low": None, "ci_high": None, "p": None, "bootstrap_valid": 0}
    if n < 3 or np.ptp(pairs[:, 0]) == 0 or np.ptp(pairs[:, 1]) == 0:
        out["reason"] = "Fewer than three complete pairs or a constant variable."
        return out
    x, y = pairs.T
    rho = float(rank_correlation(x, y))
    rx, ry = stats.rankdata(x), stats.rankdata(y)
    rx, ry = rx - rx.mean(), ry - ry.mean()
    shuffled = rng.permuted(np.tile(ry, (permutations, 1)), axis=1)
    null = (shuffled * rx).sum(axis=1) / np.sqrt((rx*rx).sum() * (ry*ry).sum())
    p = (int(np.sum(np.abs(null) >= abs(rho)-1e-12)) + 1) / (permutations + 1)
    indices = rng.integers(n, size=(bootstrap_draws, n))
    draws = rank_correlation(x[indices], y[indices])
    lo, hi = interval(draws)
    out.update(status="computed", rho=rho, p=p, ci_low=lo, ci_high=hi,
               bootstrap_valid=int(np.isfinite(draws).sum()))
    return out


def moderation(scored, field, adjust_order=False):
    """Two-condition interaction via participant deltas; independent long-model validation."""
    order_codes = {"Control-Viscereality": 0., "Viscereality-Control": 1.}
    values = [(number(r, field), number(r, "spfrref_delta"), order_codes.get(r["condition_order"], np.nan)) for r in scored]
    values = [r for r in values if np.isfinite(r[:2]).all() and (not adjust_order or np.isfinite(r[2]))]
    n, k = len(values), 3 if adjust_order else 2
    out = {"field": field, "model": "order_adjusted" if adjust_order else "unadjusted",
           "n": n, "excluded": len(scored)-n, "status": "not_estimable", "df": n-k,
           "beta": None, "se": None, "t": None, "F": None, "df_num": 1,
           "p": None, "ci_low": None, "ci_high": None, "hc3_status": "not_estimable",
           "hc3_se": None, "hc3_p": None, "hc3_ci_low": None, "hc3_ci_high": None,
           "intercept": None, "order_beta": None, "maia_mean": None, "maia_sd": None,
           "order_mean": None, "r_squared": None, "max_leverage": None, "max_cook_distance": None}
    if n <= k:
        return out | {"reason": "Insufficient complete participants for residual degrees of freedom."}
    x, y, order = np.array(values).T
    design = np.column_stack([np.ones(n), x-x.mean()])
    if adjust_order:
        design = np.column_stack([design, order-order.mean()])
    if np.linalg.matrix_rank(design) != k:
        return out | {"reason": "Constant or collinear predictor; interaction is not identified."}
    bread = np.linalg.inv(design.T @ design)
    coefficients = np.linalg.lstsq(design, y, rcond=None)[0]
    residuals = y-design @ coefficients
    rss = float(residuals @ residuals)
    if rss <= np.finfo(float).eps * max(1., float(y @ y)):
        return out | {"reason": "Zero residual variance; sampling uncertainty is not estimable."}
    variance = rss/(n-k)
    se = float(np.sqrt(variance*bread[1, 1]))
    beta = float(coefficients[1]); t = beta/se
    critical = stats.t.ppf(.975, n-k)
    leverage = np.sum(design*(design @ bread), axis=1)
    out.update(status="computed", beta=beta, se=se, t=t, F=t*t,
        p=float(2*stats.t.sf(abs(t), n-k)), ci_low=float(beta-critical*se), ci_high=float(beta+critical*se),
        intercept=float(coefficients[0]), order_beta=float(coefficients[2]) if adjust_order else None,
        maia_mean=float(x.mean()), maia_sd=float(x.std(ddof=1)),
        order_mean=float(order.mean()) if adjust_order else None,
        r_squared=float(1-rss/np.sum((y-y.mean())**2)), max_leverage=float(leverage.max()))
    if np.all(1-leverage > 1e-12):
        weights = (residuals/(1-leverage))**2
        covariance = bread @ (design.T @ (design*weights[:, None])) @ bread
        robust_se = float(np.sqrt(max(0., covariance[1, 1])))
        out["max_cook_distance"] = float(np.max(weights*leverage/(k*variance)))
        if robust_se > 0:
            out.update(hc3_status="computed", hc3_se=robust_se,
                hc3_p=float(2*stats.t.sf(abs(beta/robust_se), n-k)),
                hc3_ci_low=float(beta-critical*robust_se), hc3_ci_high=float(beta+critical*robust_se))
    return out


def run(people, person_slopes, *, bootstrap_draws=BOOTSTRAPS, permutations=PERMUTATIONS):
    rng = np.random.default_rng(SEED)
    scored, audit = score_people(people)
    for row in scored:
        row["rt_slope_interaction"] = person_slopes.get(row["participant_id"])
    scales, items = [], []
    for name, (start, stop) in SCALES.items():
        field = "maia2_" + name
        indices = list(range(start, stop+1))
        matrix = np.array([[number(p, f"maia2_item_{i:02d}") for i in indices] for p in people])
        matrix[:, [i in REVERSED for i in indices]] = 5 - matrix[:, [i in REVERSED for i in indices]]
        complete = matrix[np.isfinite(matrix).all(axis=1)]
        values = np.array([number(p, field) for p in scored])
        d = describe(values)
        d.update(field=field, label=name.replace("_", " ").title(), items=len(indices),
                 missing=len(people)-d["n"], alpha=None, alpha_ci_low=None, alpha_ci_high=None,
                 alpha_bootstrap_valid=0, mean_ci_low=None, mean_ci_high=None,
                 floor_n=int(np.sum(values == 0)), ceiling_n=int(np.sum(values == 5)))
        if len(complete) > 1:
            boot = complete[rng.integers(len(complete), size=(bootstrap_draws, len(complete)))]
            draws = alpha(boot)
            d["alpha"] = finite(alpha(complete))
            d["alpha_ci_low"], d["alpha_ci_high"] = interval(draws)
            d["alpha_bootstrap_valid"] = int(np.isfinite(draws).sum())
            d["mean_ci_low"], d["mean_ci_high"] = interval(boot.mean(axis=(1, 2)))
        scales.append(d)
        for j, i in enumerate(indices):
            raw = np.array([number(p, f"maia2_item_{i:02d}") for p in people])
            rest = np.delete(complete, j, axis=1).sum(axis=1)
            corr = float(stats.pearsonr(complete[:, j], rest).statistic) if len(complete) > 2 and np.ptp(complete[:, j]) > 0 and np.ptp(rest) > 0 else None
            observed = int(np.isfinite(raw).sum())
            items.append({"item": i, "scale": field, "reverse_scored": i in REVERSED,
                "n": observed, "missing": len(people)-observed,
                **{f"response_{v}_n": int(np.sum(raw == v)) for v in range(6)},
                "raw_floor_fraction": float(np.sum(raw == 0)/observed) if observed else None,
                "raw_ceiling_fraction": float(np.sum(raw == 5)/observed) if observed else None,
                "corrected_item_rest_pearson_r": corr, "item_rest_n": len(complete)})
    spatial = spatial_summary(scored, rng, bootstrap_draws)
    spatial["delta_descriptives"] = describe([number(r, "spfrref_delta") for r in scored])
    spatial["delta_distribution"] = [{"delta": v, "n": sum(r["spfrref_delta"] == v for r in scored)} for v in range(-7, 8)]
    fields = ["maia2_"+name for name in SCALES]
    targets = ["spfrref_control_ordinal", "spfrref_viscereality_ordinal", "spfrref_change_direction", "rt_slope_interaction"]
    associations = [association(scored, x, y, rng, permutations, bootstrap_draws)
                    for x, y in [(x, y) for x in fields for y in targets] + [(targets[2], targets[3])]]
    interscale = []
    for i, x in enumerate(fields):
        for y in fields[i+1:]:
            pairs = np.array([(number(r, x), number(r, y)) for r in scored])
            pairs = pairs[np.isfinite(pairs).all(axis=1)]
            interscale.append({"x": x, "y": y, "n": len(pairs), "rho": finite(rank_correlation(*pairs.T)) if len(pairs)>2 else None})
    delta_rng = np.random.default_rng(DELTA_SEED)
    delta_associations = [association(scored, field, "spfrref_delta", delta_rng, permutations, bootstrap_draws) for field in fields]
    delta_associations.append(association(scored, "spfrref_delta", "rt_slope_interaction", delta_rng, permutations, bootstrap_draws))
    models = [moderation(scored, field, adjusted) for field in fields for adjusted in (False, True)]
    return {"status": "exploratory; no questionnaire result is a validated PPS boundary",
        "participants": len(people), "maia_complete": sum(all(r[f] is not None for f in fields) for r in scored),
        "scoring": {"source": "https://pmc.ncbi.nlm.nih.gov/articles/PMC6279042/",
            "rule": "Complete-subscale item means; reverse items 5–10, 11, 12, 15 as 5−response; no imputation or total score.",
            "matches": sum(r["status"] == "match" for r in audit),
            "mismatches": sum(r["status"] == "mismatch" for r in audit),
            "unverifiable_stored": sum(r["status"] == "stored_only" for r in audit),
            "tolerance": 1e-6},
        "scoring_audit": audit, "scores": scored, "scales": scales, "items": items,
        "spatial": spatial, "associations": associations, "interscale_descriptive": interscale,
        "delta_associations": delta_associations, "moderation": models,
        "administration": "Owner-confirmed: MAIA-2 once before the experiment; spatial-frame ratings after each intervention. Timing is not reconstructed from CSV timestamps.",
        "delta_analysis": {"definition": "Viscereality post-intervention code minus Control post-intervention code, irrespective of presentation order",
            "seed": DELTA_SEED, "main_correlations": 8, "ancillary_correlations": 1, "moderation_models": 16,
            "comparison_count": "42 rank correlations (9 numerical-delta and 33 retained earlier comparisons); 16 moderation fits, each with classical and HC3 inference; one overall paired sign test. No multiple-testing correction.",
            "scope": "Post hoc pre-experiment trait moderation, not mediation. Code differences assume comparable category steps. Direction-only correlations are ordinal sensitivities; earlier absolute-rating results are supplementary. Correlation and interaction models are not independent replications.",
            "model": "Participant delta ~ intercept + centred MAIA, with/without centred Viscereality-first (0=Control-first, 1=Viscereality-first). Each subscale fitted separately. Beta estimates Condition × MAIA in code steps per MAIA point; F=t² with (1,n-k) df. HC3 uses t tails with n-k df as an approximate sensitivity. Order adjustment does not eliminate carryover."},
        "resampling": {"seed": SEED, "bootstrap_draws": bootstrap_draws, "permutations": permutations,
            "association_family_size": 33, "adjustment": "none",
            "reporting_change": "Unadjusted reporting requested after inspecting the association results; all 33 comparisons retained as exploratory.",
            "scope": "Two-sided permutation test of independence; pointwise paired-person percentile 95% intervals with re-ranking; undefined bootstrap draws excluded and counted. No covariate adjustment."},
        "limitations": ["Exploratory extension; exact questionnaire wording in the registration could not be retrieved (HTTP 403).",
            "MAIA-2 measures self-reported interoceptive dimensions, not objective interoceptive accuracy.",
            "Alpha describes internal consistency under restrictive assumptions; it does not establish unidimensionality or validity. No item deletion or factor-model claim.",
            "A–H ordering is preserved, but pictogram anchor direction is unverified. Timing was confirmed by the owner; administered language remains undocumented.",
            "Numerical spatial-code differences assume comparable category steps; Spearman ranking and HC3 uncertainty do not remove that measurement assumption.",
            "No repeated MAIA, perceived-body-boundary or small-self fields are released. Boundary-related correlations remain gated.",
            "Small sample, multiplicity, ties, unadjusted confounding and uncertain behavioural contrast reliability limit association interpretation."]}
