"""Results-only conjugate/grid Bayesian reference; see ANALYSIS_PLAN.md.

This is an unpooled working Gaussian model. Modular participant resampling is
reported separately from its conditional posterior; neither is a joint hierarchy.
"""

import numpy as np
from scipy import special, stats

from descriptive_sigmoid import DISTANCES, LABELS
from paper_analysis import clean
from participant_sigmoid import CONTRAST_WEIGHTS, linkage_audit, trial_tensor
from questionnaires import SCALES, rank_correlation, score_people


SEED = 20261021
DRAWS = 2000
PRIORS = ("primary", "expanded_support", "concentrated_width", "wide_nuisance")
PARAMETERS = ("midpoint_cm", "normalized_steepness_per_cm")
EFFECTS = ("Mean", "Condition", "Phase", "Condition × Phase")
WEIGHTS = np.vstack([np.full(4, .25), CONTRAST_WEIGHTS])
U = (DISTANCES - 10.) / 90.
DISPLAY_U = np.linspace(0., 1., 81)


def sufficient(tensor):
    values = np.asarray(tensor) / 1000.
    return (np.isfinite(values).sum(-1).astype(float), np.nansum(values, axis=-1),
            np.nansum(values * values, axis=-1))


def quantiles(values, weights, probabilities=(.025, .5, .975)):
    """Continuous interpolation through midpoint CDFs on a quadrature grid."""
    order = np.argsort(values)
    value, inverse = np.unique(np.asarray(values)[order], return_inverse=True)
    mass = np.bincount(inverse, weights=np.asarray(weights)[order])
    cdf = (np.cumsum(mass) - .5 * mass) / mass.sum()
    return np.interp(probabilities, cdf, value).tolist()


class ShapeGrid:
    def __init__(self, prior="primary", fine=False):
        if prior not in PRIORS:
            raise ValueError("Unknown predeclared prior.")
        self.prior = prior
        nm, nw = (161, 121) if fine else (81, 61)
        limits = (-1., 2., .0125, 4.) if prior == "expanded_support" else (-.5, 1.5, .025, 2.)
        m = np.linspace(*limits[:2], nm)
        logw = np.linspace(*np.log(limits[2:]), nw)
        mm, ll = np.meshgrid(m, logw, indexing="ij")
        self.m, self.w = mm.ravel(), np.exp(ll.ravel())
        mass = np.ones((nm, nw))
        mass[[0, -1], :] *= .5
        mass[:, [0, -1]] *= .5
        if prior == "concentrated_width":
            mass *= stats.norm.pdf(ll, np.log(1. / 6), np.log(3.))
        self.logprior = np.log(mass.ravel() / mass.sum())
        self.shape = (nm, nw)
        self.nuisance = 16. if prior == "wide_nuisance" else 4.
        self.basis = special.expit((U[None, :] - self.m[:, None]) / self.w[:, None]) - .5

    def fit(self, counts, sums, squares):
        fit = conjugate(counts, sums, squares, self.basis, self.nuisance)
        logz = special.logsumexp(fit["log_ml"] + self.logprior)
        fit.update(weights=np.exp(fit["log_ml"] + self.logprior - logz), logz=float(logz), grid=self)
        return fit


def conjugate(counts, sums, squares, basis, nuisance=4.):
    """Integrate signed coefficients and variance exactly at each fixed basis."""
    n, sy, syy = (np.asarray(a, dtype=float) for a in (counts, sums, squares))
    q = np.atleast_2d(basis)
    if q.shape[1] != len(n) or np.any(n < 0) or not np.all(np.isfinite([n, sy, syy])):
        raise ValueError("Invalid likelihood sufficient statistics.")
    precision = 1. / nuisance
    p00 = n.sum() + precision
    p01 = q @ n
    p11 = (q * q) @ n + precision
    determinant = p00 * p11 - p01 * p01
    v00, v01, v11 = p11 / determinant, -p01 / determinant, p00 / determinant
    h0, h1 = sy.sum() + .6 * precision, q @ sy
    b, a = v00 * h0 + v01 * h1, v01 * h0 + v11 * h1
    alpha = 2. + n.sum() / 2.
    scale = .02 + .5 * (syy.sum() + .6**2 * precision - b * h0 - a * h1)
    if np.any(scale <= 0):
        raise ValueError("Nonpositive posterior variance scale.")
    log_ml = (-n.sum() / 2. * np.log(2. * np.pi)
              + .5 * (2. * np.log(precision) - np.log(determinant))
              + 2. * np.log(.02) - alpha * np.log(scale)
              + special.gammaln(alpha) - special.gammaln(2.))
    return dict(log_ml=log_ml, b=b, a=a, v00=v00, v01=v01, v11=v11,
                alpha=alpha, scale=scale)


def draw_parameters(fit, rng, draws=DRAWS):
    index = np.searchsorted(np.cumsum(fit["weights"]), rng.random(draws))
    index = np.minimum(index, len(fit["weights"]) - 1)
    sigma2 = fit["scale"][index] / rng.gamma(fit["alpha"], size=draws)
    z = rng.standard_normal((2, draws))
    v00, v01, v11 = (fit[key][index] for key in ("v00", "v01", "v11"))
    b = fit["b"][index] + np.sqrt(sigma2 * v00) * z[0]
    a = fit["a"][index] + np.sqrt(sigma2) * (
        v01 / np.sqrt(v00) * z[0] + np.sqrt(np.maximum(v11 - v01*v01/v00, 0.)) * z[1])
    grid = fit["grid"]
    return np.stack([b, a, grid.m[index], grid.w[index]], axis=-1), np.sqrt(sigma2)


def shape_summary(fit):
    grid, weights = fit["grid"], fit["weights"]
    result = {}
    for name, values in (("midpoint_cm", 10. + 90.*grid.m), ("width_cm", 90.*grid.w),
                         ("normalized_steepness_per_cm", 1./(360.*grid.w))):
        lo, median, hi = quantiles(values, weights)
        result.update({name: median, name+"_low": lo, name+"_high": hi})
    positive = weights > 0
    result["shape_information_nats"] = float(np.sum(weights[positive] * (
        np.log(weights[positive]) - grid.logprior[positive])))
    posterior, prior = weights.reshape(grid.shape), np.exp(grid.logprior).reshape(grid.shape)
    for label, axis in (("midpoint", 1), ("width", 0)):
        p, q = posterior.sum(axis), prior.sum(axis)
        keep = p > 0
        result[label+"_information_nats"] = float(np.sum(p[keep] * np.log(p[keep]/q[keep])))
        result[label+"_edge_mass"] = float(p[0]+p[-1])
    covered = ((grid.m - np.log(9.)*grid.w >= 0.) & (grid.m + np.log(9.)*grid.w <= 1.))
    result["probability_10_90_inside_measured_range"] = float(weights @ covered)
    result["prior_probability_10_90_inside_measured_range"] = float(np.exp(grid.logprior) @ covered)
    result["probability_midpoint_in_measured_range"] = float(weights @ ((grid.m >= 0) & (grid.m <= 1)))
    return result


def models_and_prediction(counts, sums, squares, grid, sigmoid):
    bases = {"constant": np.zeros((1, 5)), "linear": (U-.5)[None, :],
             "log_distance": ((np.log(DISTANCES)-np.log(10.))/np.log(10.)-.5)[None, :],
             "sigmoid": grid.basis}
    full = {name: conjugate(counts, sums, squares, q, grid.nuisance) for name, q in bases.items()}
    z = {name: (sigmoid["logz"] if name == "sigmoid" else float(f["log_ml"][0]))
         for name, f in full.items()}
    probabilities = special.softmax(list(z.values()))
    evidence = [{"model": name, "log_marginal_likelihood": z[name], "posterior_model_probability": float(prob)}
                for name, prob in zip(z, probabilities)]
    rows = []
    for j in range(5):
        train = [a.copy() for a in (counts, sums, squares)]
        for a in train:
            a[j] = 0.
        for name, q in bases.items():
            f = conjugate(*train, q, grid.nuisance)
            lp = grid.logprior if name == "sigmoid" else np.zeros(1)
            logz = float(special.logsumexp(f["log_ml"] + lp))
            weights = np.exp(f["log_ml"] + lp - logz)
            prediction = float(weights @ (f["b"] + f["a"]*q[:, j]))
            rows.append(dict(model=name, held_distance_cm=float(DISTANCES[j]),
                             observed_mean_ms=float(1000.*sums[j]/counts[j]),
                             predicted_mean_ms=1000.*prediction,
                             squared_mean_error_ms2=float((1000.*(prediction-sums[j]/counts[j]))**2),
                             held_block_log_predictive_density=z[name]-logz,
                             held_trials=int(counts[j])))
    return evidence, rows


def interval(values):
    values = np.asarray(values)
    good = values[np.isfinite(values)]
    if not len(good):
        return dict(median=None, low=None, high=None, probability_positive=None, valid_draws=0)
    lo, median, hi = np.quantile(good, [.025, .5, .975])
    return dict(median=float(median), low=float(lo), high=float(hi),
                probability_positive=float(np.mean(good > 0)), valid_draws=int(len(good)))


def parameter_metrics(draws):
    return np.stack([10.+90.*draws[..., 2], 1./(360.*draws[..., 3])], axis=-1)


def weighted_regression(design, weights, outcomes):
    """Paired Bayesian-bootstrap WLS, retaining dependence of each four-cell draw."""
    x, w, y = map(np.asarray, (design, weights, outcomes))
    if len(x) <= x.shape[1] or np.linalg.matrix_rank(x) < x.shape[1]:
        return None
    lhs = np.einsum("ni,dn,nj->dij", x, w, x)
    rhs = np.einsum("ni,dn,dnk->dik", x, w, y)
    return np.linalg.solve(lhs, rhs)


def recording_weights(rng, ids, draws, bootstrap=False, linked_groups=()):
    mapping = {pid: group[0] for group in linked_groups for pid in group}
    groups = [mapping.get(pid, pid) for pid in ids]
    _, inverse = np.unique(groups, return_inverse=True)
    n = int(inverse.max())+1
    weights = (rng.multinomial(n, np.full(n, 1./n), size=draws) if bootstrap
               else rng.exponential(size=(draws, n)))
    return weights[:, inverse].astype(float)


def weighted_rank_correlation(x, y, weights):
    """Integer weights reproduce ordinary Spearman on expanded bootstrap records."""
    def ranks(values):
        order = np.argsort(values, axis=-1, kind="stable")
        sorted_values = np.take_along_axis(values, order, axis=-1)
        sorted_weights = np.take_along_axis(weights, order, axis=-1)
        cumulative = np.cumsum(sorted_weights, axis=-1)
        before = cumulative - sorted_weights
        n = values.shape[-1]
        new = np.concatenate([np.ones((len(values), 1), bool), np.diff(sorted_values, axis=-1) != 0], axis=-1)
        end = np.concatenate([np.diff(sorted_values, axis=-1) != 0, np.ones((len(values), 1), bool)], axis=-1)
        first = np.maximum.accumulate(np.where(new, np.arange(n), 0), axis=-1)
        last = np.minimum.accumulate(np.where(end, np.arange(n), n-1)[:, ::-1], axis=-1)[:, ::-1]
        mid = .5*(np.take_along_axis(before, first, axis=-1)+np.take_along_axis(cumulative, last, axis=-1))
        return np.take_along_axis(mid, np.argsort(order, axis=-1), axis=-1)
    rx, ry = ranks(x), ranks(y)
    total = weights.sum(1, keepdims=True)
    rx -= np.sum(weights*rx, axis=-1, keepdims=True)/total
    ry -= np.sum(weights*ry, axis=-1, keepdims=True)/total
    denominator = np.sqrt(np.sum(weights*rx*rx, axis=-1)*np.sum(weights*ry*ry, axis=-1))
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.sum(weights*rx*ry, axis=-1)/denominator


def cohort_results(draws, ids, scored, prior, rng, linked_groups=()):
    records = {r["participant_id"]: r for r in scored}
    all_metrics = parameter_metrics(draws)
    contrasts = np.einsum("dnck,ec->dnek", all_metrics, WEIGHTS)
    group, cell_summaries, associations, regressions = [], [], [], []
    ambiguous = sorted({pid for group in linked_groups for pid in group})
    specifications = list(dict.fromkeys([(), tuple(ambiguous), *[(pid,) for pid in ambiguous]]))
    for excluded in specifications:
        keep = np.array([i for i, pid in enumerate(ids) if pid not in excluded])
        n, nd = len(keep), len(draws)
        if not n:
            continue
        q = [records[ids[i]] for i in keep]
        y, metric = contrasts[:, keep], all_metrics[:, keep]
        weights = recording_weights(rng, [ids[i] for i in keep], nd, linked_groups=linked_groups)
        weights /= weights.sum(1, keepdims=True)
        finite_cohort, population = y.mean(1), np.einsum("dn,dnek->dek", weights, y)
        common = dict(prior=prior, excluded_ids=",".join(excluded), n=n)
        cell_mean = metric.mean(1)
        cell_population = np.einsum("dn,dnck->dck", weights, metric)
        for c, (condition, phase) in enumerate(LABELS):
            for k, parameter in enumerate(PARAMETERS):
                for scope, values in (("finite cohort posterior", cell_mean[:, c, k]),
                                      ("posterior + Bayesian bootstrap", cell_population[:, c, k])):
                    cell_summaries.append(common | dict(condition=condition, phase=phase,
                        parameter=parameter, scope=scope) | interval(values))
        for e, effect in enumerate(EFFECTS):
            for k, parameter in enumerate(PARAMETERS):
                for scope, values in (("finite cohort posterior", finite_cohort[:, e, k]),
                                      ("posterior + Bayesian bootstrap", population[:, e, k])):
                    group.append(common | dict(effect=effect, parameter=parameter, scope=scope) | interval(values))
        catalogue = []
        for k, parameter in enumerate(PARAMETERS):
            for scale in SCALES:
                x = "maia2_"+scale
                for c, (condition, phase) in enumerate(LABELS):
                    catalogue.append((x, parameter, condition+" · "+phase, metric[:, :, c, k]))
                catalogue.append((x, parameter, "Condition", y[:, :, 1, k]))
            for x in ("spfrref_delta", "spfrref_change_direction"):
                catalogue.append((x, parameter, "Condition", y[:, :, 1, k]))
            for c, (condition, phase) in enumerate(LABELS):
                catalogue.append(("spfrref_"+condition.lower()+"_ordinal", parameter,
                                  condition+" · "+phase, metric[:, :, c, k]))
        for field, parameter, effect, outcome in catalogue:
            x = np.array([r.get(field) if r.get(field) is not None else np.nan for r in q])
            good = np.isfinite(x)
            valid = int(good.sum())
            row = common | dict(predictor=field, parameter=parameter, summary=effect, n_complete=valid,
                                interval_scope="posterior + paired participant bootstrap")
            if valid < 4 or np.ptp(x[good]) == 0:
                associations.append(row | interval([]))
                continue
            bootstrap = recording_weights(rng, [ids[i] for i in keep[good]], nd, bootstrap=True,
                                          linked_groups=linked_groups)
            by = outcome[:, good]
            bx = np.broadcast_to(x[good], by.shape)
            associations.append(row | interval(weighted_rank_correlation(bx, by, bootstrap)))
        spatial = np.array([r.get("spfrref_delta") if r.get("spfrref_delta") is not None else np.nan for r in q])
        order = np.array([{"Control-Viscereality": 0., "Viscereality-Control": 1.}.get(
            r["condition_order"], np.nan) for r in q])
        for scale in SCALES:
            maia = np.array([r.get("maia2_"+scale) if r.get("maia2_"+scale) is not None else np.nan for r in q])
            good = np.isfinite(maia) & np.isfinite(spatial) & np.isfinite(order)
            a, s, o = (v[good]-v[good].mean() if good.any() else np.empty(0) for v in (maia, spatial, order))
            design = np.column_stack([np.ones(good.sum()), a, s, a*s, o])
            ww = weights[:, good]
            if good.any():
                ww /= ww.sum(1, keepdims=True)
            coefficients = weighted_regression(design, ww, y[:, good].reshape(nd, good.sum(), 8))
            for e, effect in enumerate(EFFECTS):
                for k, parameter in enumerate(PARAMETERS):
                    for j, term in enumerate(("MAIA", "spatial_delta", "MAIA × spatial_delta"), 1):
                        values = [] if coefficients is None else coefficients[:, j, e*2+k]
                        regressions.append(common | dict(scale=scale, term=term, effect=effect,
                            parameter=parameter, n_complete=int(good.sum()), order_adjusted=True,
                            interval_scope="modular posterior + Bayesian bootstrap WLS") | interval(values))
    return group, cell_summaries, associations, regressions


def average_curves(draws, tensor, ids, rng, excluded=()):
    keep = np.array([i for i, pid in enumerate(ids) if pid not in excluded])
    d = draws[:, keep]
    weights = rng.exponential(size=d.shape[:2])
    weights /= weights.sum(1, keepdims=True)
    observed = np.nanmean(tensor[keep], axis=-1)
    result = []
    for c, (condition, phase) in enumerate(LABELS):
        q = special.expit((DISPLAY_U[None, None, :]-d[:, :, c, 2, None])/d[:, :, c, 3, None])
        functions = 1000.*(d[:, :, c, 0, None]+d[:, :, c, 1, None]*(q-.5))
        average = np.einsum("dn,dnx->dx", weights, functions)
        geometry = np.einsum("dn,dnx->dx", weights, q)
        result.append(dict(condition=condition, phase=phase, distance_cm=(10.+90.*DISPLAY_U).tolist(),
            posterior_average_ms=np.quantile(average, [.025, .5, .975], axis=0).tolist(),
            conditional_average_geometry=np.quantile(geometry, [.025, .5, .975], axis=0).tolist(),
            observed_mean_ms=observed[:, c].mean(0).tolist(),
            observed_se_ms=(observed[:, c].std(0, ddof=1)/np.sqrt(len(keep))).tolist()))
    return result


def reliability_and_recovery(tensor, ids, rng, repeats=20, halves=10, excluded=()):
    grid = ShapeGrid()
    primary = np.array([i for i, pid in enumerate(ids) if pid not in excluded])
    def estimates(statistics):
        result = []
        for n, sy, syy in zip(*(s.reshape(-1, 5) for s in statistics)):
            fit = grid.fit(n, sy, syy)
            summary = shape_summary(fit)
            result.append([summary[p] for p in PARAMETERS])
        return np.array(result).reshape(len(ids), 4, 2)
    reliability = []
    n = np.isfinite(tensor).sum(-1)
    for repeat in range(halves):
        random = rng.random(tensor.shape)
        random[~np.isfinite(tensor)] = np.inf
        rank = np.argsort(np.argsort(random, axis=-1), axis=-1)
        mask = rank < (n//2)[..., None]
        fits = [estimates(sufficient(np.where(mask if h == 0 else ~mask, tensor, np.nan))) for h in (0, 1)]
        values = [np.einsum("nck,ec->nek", f[primary], WEIGHTS) for f in fits]
        for e, effect in enumerate(EFFECTS):
            for k, parameter in enumerate(PARAMETERS):
                reliability.append(dict(repeat=repeat, summary=effect, parameter=parameter,
                    rho=float(rank_correlation(values[0][:, e, k], values[1][:, e, k]))))
    counts, sums, squares = sufficient(tensor)
    means = sums / counts
    sigma = np.sqrt(np.sum(squares-sums*sums/counts, axis=-1)/np.sum(counts-1, axis=-1))
    recoveries = []
    for scenario in ("flat", "linear", "sigmoid"):
        for repeat in range(repeats):
            m = rng.uniform(.25, .75, size=counts.shape[:2])
            w = np.exp(rng.uniform(np.log(.05), np.log(.15), size=counts.shape[:2]))
            basis = special.expit((U-m[..., None])/w[..., None])-.5
            signal = means.mean(-1)[..., None] + (.08*basis if scenario == "sigmoid" else
                     .08*(U-.5) if scenario == "linear" else np.zeros(5))
            sample_mean = signal + sigma[..., None]/np.sqrt(counts)*rng.standard_normal(counts.shape)
            within = sigma[..., None]**2*rng.chisquare(counts-1)
            fits = estimates((counts, sample_mean*counts, within+counts*sample_mean**2))
            for k, parameter in enumerate(PARAMETERS):
                truth = 10.+90.*m if k == 0 else 1./(360.*w)
                recoveries.append(dict(scenario=scenario, repeat=repeat, parameter=parameter,
                    recovery_rho=(float(rank_correlation(truth[primary].ravel(), fits[primary, :, k].ravel()))
                                  if scenario == "sigmoid" else None),
                    fitted_median=float(np.median(fits[primary, :, k])),
                    fitted_between_cell_sd=float(np.std(fits[primary, :, k]))))
    return reliability, recoveries


def run(people, trials, progress=None, draws=DRAWS, simulation_repeats=20, split_halves=10):
    notify = progress or (lambda _: None)
    retained, quality, counts = clean(people, trials)
    ids, tensor, incomplete = trial_tensor(retained)
    if not ids:
        return dict(status="not_estimable", reason="No complete four-cell trial profiles.")
    scored, _ = score_people(people)
    audit = linkage_audit(trials)
    linked_groups = [g["participant_ids"] for g in audit["groups"]]
    ambiguous = sorted({pid for group in linked_groups for pid in group})
    statistics = sufficient(tensor)
    flat = [s.reshape(-1, 5) for s in statistics]
    cells, predictions, evidence, groups, cell_summaries, associations, regressions = [], [], [], [], [], [], []
    individual_curves, grid_checks, averages = [], [], []
    rng = np.random.default_rng(SEED)
    for prior in PRIORS:
        notify("Bayesian raw-trial sigmoid posteriors · "+prior)
        grid = ShapeGrid(prior)
        parameters = np.empty((draws, len(ids), 4, 4))
        for i, (n, sy, syy) in enumerate(zip(*flat)):
            person, cell = divmod(i, 4)
            condition, phase = LABELS[cell]
            fit = grid.fit(n, sy, syy)
            samples, sigma = draw_parameters(fit, rng, draws)
            parameters[:, person, cell] = samples
            summary = shape_summary(fit)
            common = dict(prior=prior, participant_id=ids[person], condition=condition, phase=phase,
                          ambiguous_recording=ids[person] in ambiguous, n_trials=int(n.sum()))
            amplitude = interval(1000.*samples[:, 1])
            q = special.expit((U[None, :]-samples[:, 2, None])/samples[:, 3, None])
            mean = samples[:, 0, None]+samples[:, 1, None]*(q-.5)
            discrepancy = np.sum(n*(sy/n-mean)**2/sigma[:, None]**2, axis=1)
            replicated = np.sum(rng.standard_normal((draws, 5))**2, axis=1)
            cells.append(common | summary | {"amplitude_"+k: v for k, v in amplitude.items()} |
                         dict(predictive_discrepancy_probability=float(np.mean(replicated >= discrepancy))))
            ev, pred = models_and_prediction(n, sy, syy, grid, fit)
            evidence.extend(common | row for row in ev)
            predictions.extend(common | row for row in pred)
            if prior == "primary":
                xx = DISPLAY_U[None, :]
                geometry = special.expit((xx-samples[:, 2, None])/samples[:, 3, None])
                functions = 1000.*(samples[:, 0, None]+samples[:, 1, None]*(geometry-.5))
                variances = (syy-sy*sy/n)/np.maximum(n-1, 1)
                individual_curves.append(common | dict(distance_cm=(10.+90.*DISPLAY_U).tolist(),
                    response_ms=np.quantile(functions, [.025, .5, .975], axis=0).tolist(),
                    conditional_geometry=np.quantile(geometry, [.025, .5, .975], axis=0).tolist(),
                    observed_mean_ms=(1000.*sy/n).tolist(), observed_se_ms=(1000.*np.sqrt(variances/n)).tolist()))
        notify("Propagating individual uncertainty · "+prior)
        for linked in linked_groups:
            if not all(pid in ids for pid in linked):
                continue
            for pid in linked[1:]:
                source, target = ids.index(linked[0]), ids.index(pid)
                for cell in range(4):
                    matches = [c for c in range(4) if all(np.allclose(s[source, c], s[target, cell],
                               rtol=1e-12, atol=1e-14) for s in statistics)]
                    if matches:
                        # Exact recording copies share posterior draws, including swapped labels.
                        parameters[:, target, cell] = parameters[:, source, matches[0]]
        gr, cc, aa, rr = cohort_results(parameters, ids, scored, prior, rng, linked_groups)
        groups.extend(gr); cell_summaries.extend(cc); associations.extend(aa); regressions.extend(rr)
        if prior == "primary":
            averages = average_curves(parameters, tensor, ids, rng, ambiguous)
    notify("Bayesian quadrature resolution check")
    fine = ShapeGrid(fine=True)
    base = [r for r in cells if r["prior"] == "primary"]
    for original, (n, sy, syy) in zip(base, zip(*flat)):
        fit = fine.fit(n, sy, syy)
        summary = shape_summary(fit)
        row = {key: original[key] for key in ("participant_id", "condition", "phase")}
        for parameter in PARAMETERS:
            row[parameter+"_fine"] = summary[parameter]
            row[parameter+"_difference"] = summary[parameter]-original[parameter]
        grid_checks.append(row)
    notify("Bayesian split-half and matched-likelihood recovery checks")
    reliability, recovery = reliability_and_recovery(tensor, ids, rng, simulation_repeats, split_halves, ambiguous)
    prior_rng = np.random.default_rng(SEED+1)
    variance = .02/prior_rng.gamma(2., size=10000)
    prior_predictive = []
    for prior in PRIORS:
        grid = ShapeGrid(prior)
        index = prior_rng.choice(len(grid.m), size=len(variance), p=np.exp(grid.logprior))
        beta = np.array([.6, 0.])+prior_rng.standard_normal((len(variance), 2))*np.sqrt(variance[:, None]*grid.nuisance)
        q = grid.basis[index]
        predictive = beta[:, :1]+beta[:, 1:] * q + np.sqrt(variance[:, None])*prior_rng.standard_normal(q.shape)
        prior_predictive.append(dict(prior=prior, negative_rt_fraction=float(np.mean(predictive < 0)),
            prior_sigma_ms=np.quantile(1000.*np.sqrt(variance), [.025, .5, .975]).tolist(),
            prior_response_ms=np.quantile(1000.*predictive, [.025, .5, .975]).tolist()))
    return dict(status="computed", analysis_version="Bayesian results 1.0", seed=SEED, posterior_draws=draws,
        cohort=counts, participant_ids=ids, incomplete_profile_ids=incomplete,
        linkage_audit=audit, primary_excluded_ids=ambiguous,
        cells=cells, model_evidence=evidence, prediction=predictions, group_contrasts=groups,
        group_cell_summaries=cell_summaries,
        associations=associations, joint_moderation=regressions, individual_curves=individual_curves,
        average_curves=averages, quadrature_checks=grid_checks, reliability=reliability,
        recovery=recovery, prior_predictive=prior_predictive,
        assumptions="Unpooled Gaussian trial likelihood, proper normal–inverse-gamma nuisance prior and finite-grid shape integration. No smoothing or nonzero amplitude constraint. All sigmoid parameters are conditional on that model; the model comparison also permits constant, linear and log-distance responses.",
        uncertainty="Conditional posterior draws plus separately labelled paired Bayesian-bootstrap group/regression sensitivities and posterior-plus-participant-bootstrap rank intervals. These are modular descriptive analyses, not a full joint hierarchical nonlinear/covariate posterior.",
        limits="Fixed prior choices, cleaning, nominal distances, independent Gaussian trial errors and unresolved source linkage. Sparse positions can leave midpoint/width prior-dependent. Matched-likelihood simulation is not robustness to all RT distributions. No mediation, no questionnaire-driven cleaning, no manuscript update.")
