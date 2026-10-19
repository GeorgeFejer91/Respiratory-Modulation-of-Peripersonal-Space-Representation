"""Show assumed sigmoid geometry alongside the unchanged observations and checks."""
import hashlib
import json
import zipfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pandas as pd
from scipy import special, stats

from fit import (OUT, LOCAL, ROOT, X, CELL_NAMES, CONFIGS, W, directional)
from report import table, sha


def endpoint_check(m, w, epsilon):
    assert (special.expit((10-m)/w) <= epsilon+1e-10).all()
    assert (special.expit((100-m)/w) >= 1-epsilon-1e-10).all()


def main():
    ids, at, baseline, audit = directional.primary_data()
    grid = np.linspace(10, 100, 121)
    colors = ["#215A8E", "#387C9B", "#B24C22", "#D37824"]
    information, cohort, effects, simple, runs, geometry_diagnostics = [], [], [], [], [], []
    primary = None
    for name, epsilon in CONFIGS.items():
        run = json.loads((OUT / f"{name}_run.json").read_text())
        runs.append(dict(model=name, **run))
        with np.load(LOCAL / f"{name}_draws.npz") as d:
            values = {quantity: d[quantity].reshape(-1, len(ids), 4) for quantity in
                ("midpoint_cm", "width_cm", "sharpness_per_cm", "amplitude", "corrected_intercept", "baseline_mean")}
            assert (values["amplitude"] > 0).all()
            endpoint_check(values["midpoint_cm"], values["width_cm"], epsilon)
            if name == "visible95":
                primary = values
                primary_curve = d["corrected_curve"].reshape(-1, len(ids), 4, 5)
                primary_sigma = {q: d[q].reshape(-1, len(ids)) for q in ("sigma_at", "sigma_baseline")}
        with np.load(LOCAL / f"{name}_prior.npz") as prior:
            cap = 90/(2*np.log((1-epsilon)/epsilon))
            medians = np.median(values["midpoint_cm"], axis=0)
            geometry_diagnostics.append(dict(model=name, width_max_cm=cap,
                posterior_width_above_90pct_cap=float(np.mean(values["width_cm"] > .9*cap)),
                prior_width_above_90pct_cap=float(np.mean(prior["width_cm"] > .9*cap)),
                midpoint_median_min_cm=medians.min(), midpoint_median_max_cm=medians.max()))
            for quantity in ("midpoint_cm", "width_cm", "sharpness_per_cm"):
                post_q = np.quantile(values[quantity], [.025, .5, .975], axis=0)
                prior_q = np.quantile(prior[quantity], [.025, .5, .975], axis=0)
                for i, pid in enumerate(ids):
                    for c, cell in enumerate(CELL_NAMES):
                        information.append(dict(model=name, participant_id=pid, cell=cell, quantity=quantity,
                            prior_low=prior_q[0, i, c], prior_median=prior_q[1, i, c], prior_high=prior_q[2, i, c],
                            posterior_low=post_q[0, i, c], posterior_median=post_q[1, i, c], posterior_high=post_q[2, i, c],
                            interval_width_ratio=(post_q[2, i, c]-post_q[0, i, c])/(prior_q[2, i, c]-prior_q[0, i, c])))
                pq = np.quantile(values[quantity].mean(1), [.025, .5, .975], axis=0)
                rq = np.quantile(prior[quantity].mean(1), [.025, .5, .975], axis=0)
                for c, cell in enumerate(CELL_NAMES):
                    cohort.append(dict(model=name, cell=cell, quantity=quantity,
                        prior_low=rq[0, c], prior_median=rq[1, c], prior_high=rq[2, c],
                        posterior_low=pq[0, c], posterior_median=pq[1, c], posterior_high=pq[2, c]))
        effects.append(pd.read_csv(OUT / f"{name}_effects.csv"))
        simple.append(pd.read_csv(OUT / f"{name}_simple_contrasts.csv"))
    information = pd.DataFrame(information)
    cohort = pd.DataFrame(cohort)
    effects = pd.concat(effects, ignore_index=True)
    information.to_csv(OUT / "prior_posterior_information.csv", index=False)
    pd.DataFrame(geometry_diagnostics).to_csv(OUT / "geometry_diagnostics.csv", index=False)
    cohort.to_csv(OUT / "cohort_parameters.csv", index=False)
    effects.to_csv(OUT / "all_effects.csv", index=False)
    pd.concat(simple, ignore_index=True).to_csv(OUT / "all_simple_contrasts.csv", index=False)
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False, "pdf.fonttype": 42})
    # This is a mean-parameter sigmoid, not the average of individual response curves.
    cohort_m, cohort_w = primary["midpoint_cm"].mean(1), primary["width_cm"].mean(1)
    median_m, median_w = np.median(cohort_m, 0), np.median(cohort_w, 0)
    endpoint_check(median_m, median_w, .05)
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), sharex=True, sharey=True)
    normalized_records = []
    for c, ax in enumerate(axes.flat):
        normalized = special.expit((grid-cohort_m[:, c, None])/cohort_w[:, c, None])
        low, med, high = np.quantile(normalized, [.025, .5, .975], axis=0)
        plugin = special.expit((grid-median_m[c])/median_w[c])
        ax.fill_between(grid, low, high, color=colors[c], alpha=.16)
        ax.plot(grid, plugin, color=colors[c], lw=2.6)
        ax.axvline(median_m[c], ls="--", lw=.8, color=colors[c])
        ax.plot(median_m[c], .5, "o", color=colors[c], ms=5)
        ax.axhline(.5, color="#888888", ls=":", lw=.7)
        mq = np.quantile(cohort_m[:, c], [.025, .5, .975])
        ax.text(.03, .97, f"Mean midpoint {mq[1]:.1f} [{mq[0]:.1f}, {mq[2]:.1f}] cm", transform=ax.transAxes, va="top", fontsize=9)
        ax.set(title=CELL_NAMES[c], xlim=(10, 100), ylim=(-.03, 1.03))
        for j, d in enumerate(grid):
            normalized_records.append(dict(cell=CELL_NAMES[c], distance_cm=d, median_parameter_sigmoid=plugin[j],
                pointwise_posterior_median=med[j], credible_low=low[j], credible_high=high[j]))
    fig.suptitle("Shape-constrained Bayesian PPS approximation", fontsize=15)
    fig.supxlabel("Physical distance (cm)", y=.075)
    fig.supylabel("Normalized model component (unit amplitude)")
    fig.text(.5, .018, "Visible S and 5–95% transition inside 10–100 cm are imposed by the prior.\n"
             "Line: sigmoid at median cohort-mean midpoint/width; band: 95% interval for that mean-parameter function.\n"
             "This is model geometry, not normalized observed RTs or an average participant response curve.", ha="center", fontsize=8)
    fig.tight_layout(rect=(.025, .12, 1, .95))
    fig.savefig(OUT / "sigmoid_curves.png", dpi=190)
    fig.savefig(OUT / "sigmoid_curves.pdf")
    plt.close(fig)
    directional.write_csv(OUT / "normalized_mean_parameter_curves.csv", normalized_records)
    boundary = cohort[(cohort.model == "visible95") & (cohort.quantity == "midpoint_cm")]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    for c, row in enumerate(boundary.itertuples(index=False)):
        ax.plot([row.prior_low, row.prior_high], [c+.08]*2, color="#BBBBBB", lw=5, label="Prior 95% interval" if c == 0 else None)
        ax.plot([row.posterior_low, row.posterior_high], [c-.08]*2, color=colors[c], lw=3, label="Posterior 95% interval" if c == 0 else None)
        ax.plot(row.posterior_median, c-.08, "o", color=colors[c])
    ax.set(yticks=range(4), yticklabels=CELL_NAMES, xlim=(10, 100), xlabel="Mean participant midpoint (cm), conditional on the shape prior")
    ax.invert_yaxis()
    ax.legend(loc="upper left", bbox_to_anchor=(0, -.18), ncol=2, fontsize=9)
    fig.suptitle("Bayesian boundary approximations: prior and posterior")
    fig.text(.5, .015, "In-range boundaries are guaranteed by the model; these intervals do not establish physiological identification.", ha="center", fontsize=8)
    fig.tight_layout(rect=(0, .06, 1, .94))
    fig.savefig(OUT / "boundary_estimates.png", dpi=180)
    fig.savefig(OUT / "boundary_estimates.pdf")
    plt.close(fig)
    bflat = baseline.reshape(len(ids), 4, -1)
    y = np.nanmean(at, -1)-np.nanmean(bflat, -1)[..., None]
    counts = np.isfinite(at).sum(-1)
    error = np.sqrt(np.nanvar(at, -1, ddof=1)/counts +
        (np.nanvar(bflat, -1, ddof=1)/np.isfinite(bflat).sum(-1))[..., None])
    step = max(1, len(primary["midpoint_cm"])//1200)
    sub = {name: a[::step] for name, a in primary.items()}
    group_rt = np.zeros((len(sub["midpoint_cm"]), 4, len(grid)))
    reference = pd.read_csv(ROOT / "results/directional_sigmoid/measured_range_curves.csv")
    curve_rows = []
    with PdfPages(OUT / "individual_sigmoids.pdf") as pdf:
        for i, pid in enumerate(ids):
            fig, axes = plt.subplots(2, 4, figsize=(13, 7.5))
            for c, cell in enumerate(CELL_NAMES):
                m, w, a, delta = [np.median(primary[q][:, i, c]) for q in
                    ("midpoint_cm", "width_cm", "amplitude", "corrected_intercept")]
                endpoint_check(np.array(m), np.array(w), .05)
                component = special.expit((grid-sub["midpoint_cm"][:, i, c, None])/sub["width_cm"][:, i, c, None])
                rt = 1000*(sub["corrected_intercept"][:, i, c, None]+sub["amplitude"][:, i, c, None]*(component-.5))
                group_rt[:, c] += rt/len(ids)
                lo, med, hi = np.quantile(rt, [.025, .5, .975], axis=0)
                mq = np.quantile(primary["midpoint_cm"][:, i, c], [.025, .5, .975])
                plugin = special.expit((grid-m)/w)
                original = reference[(reference.participant_id == pid)&(reference.cell == cell)].sort_values("distance_cm")
                assert len(original) == len(grid)
                top = axes[0, c]
                top.fill_between(grid, lo, hi, color=colors[c], alpha=.16)
                top.plot(grid, 1000*(delta+a*(plugin-.5)), color=colors[c], lw=2, label="Shape-constrained sigmoid")
                top.plot(grid, original.expected_RT_median_ms, color="#888888", ls="--", lw=1, label="Broad directional reference")
                top.errorbar(X, y[i, c], yerr=error[i, c], fmt="o", ms=3, capsize=2, color="#222222")
                top.set(title=cell, xlabel="Distance (cm)", ylabel="AT minus Baseline RT (ms)", xlim=(8, 102))
                if c == 0:
                    top.legend(fontsize=6.5, loc="lower left")
                bottom = axes[1, c]
                qlo, qmed, qhi = np.quantile(component, [.025, .5, .975], axis=0)
                bottom.fill_between(grid, qlo, qhi, color=colors[c], alpha=.16)
                bottom.plot(grid, plugin, color=colors[c], lw=2.3)
                bottom.axvline(m, color=colors[c], ls="--", lw=.7)
                bottom.axhline(.5, color="#888888", ls=":", lw=.7)
                bottom.text(.03, .97, f"m {m:.1f} [{mq[0]:.1f}, {mq[2]:.1f}] cm\n"
                            f"Width {w:.1f} cm; sharpness {1/(4*w):.4f} /cm", transform=bottom.transAxes, va="top", fontsize=7.5)
                bottom.set(xlabel="Distance (cm)", ylabel="Normalized model component", xlim=(10, 100), ylim=(-.03, 1.03))
                for j, d in enumerate(grid):
                    curve_rows.append(dict(participant_id=pid, cell=cell, distance_cm=d,
                        normalized_parameter_sigmoid=plugin[j], normalized_credible_low=qlo[j], normalized_credible_high=qhi[j],
                        parameter_RT_ms=1000*(delta+a*(plugin[j]-.5)), expected_RT_low_ms=lo[j], expected_RT_median_ms=med[j], expected_RT_high_ms=hi[j]))
            limits = np.array([ax.get_ylim() for ax in axes[0]])
            for ax in axes[0]:
                ax.set_ylim(limits[:, 0].min(), limits[:, 1].max())
            fig.suptitle(f"{pid}: explicitly shape-constrained Bayesian sigmoid approximation", fontsize=13)
            fig.text(.5, .025, "Top: unsmoothed means ± marginal SE; baseline error is shared. Bottom: unit-amplitude model geometry.\n"
                     "Visible S, common direction and in-range transition are imposed. Lines use marginal parameter medians; bands are 95% model intervals.\n"
                     "Normalization does not transform the observations. A small-amplitude RT response may remain nearly flat despite the normalized S.", ha="center", fontsize=8)
            fig.tight_layout(rect=(0, .105, 1, .95))
            pdf.savefig(fig)
            if i == 0:
                fig.savefig(OUT / "individual_example.png", dpi=150)
            plt.close(fig)
    directional.write_csv(OUT / "individual_curves.csv", curve_rows)
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), sharex=True, sharey=True)
    for c, ax in enumerate(axes.flat):
        lo, med, hi = np.quantile(group_rt[:, c], [.025, .5, .975], axis=0)
        ax.fill_between(grid, lo, hi, color=colors[c], alpha=.16)
        ax.plot(grid, med, color=colors[c], lw=2)
        ax.errorbar(X, y[:, c].mean(0), yerr=stats.t.ppf(.975, len(ids)-1)*stats.sem(y[:, c], axis=0),
            fmt="o", ms=4, capsize=3, color="#222222")
        ax.set_title(CELL_NAMES[c])
        ax.set_xlim(8, 102)
    fig.suptitle("Actual RT observations and the constrained Bayesian response estimate")
    fig.supxlabel("Physical distance (cm)", y=.07)
    fig.supylabel("AT minus matched Baseline RT (ms)")
    fig.text(.5, .02, "Dots: equal-participant means ± 95% CI; bands: 95% expected-response intervals.\n"
             "This averages individual RT curves. It differs from the normalized mean-parameter sigmoid figure.", ha="center", fontsize=8)
    fig.tight_layout(rect=(.025, .10, 1, .95))
    fig.savefig(OUT / "observed_RT.png", dpi=180)
    fig.savefig(OUT / "observed_RT.pdf")
    plt.close(fig)
    cv = pd.read_csv(OUT / "held_distance_predictions.csv")
    ref = pd.read_csv(ROOT / "results/directional_sigmoid/held_distance_predictions.csv")
    ref = ref[ref.model == "positive_amplitude"].copy()
    assert len(cv) == len(ref) == 800
    keys = ["participant_id", "cell", "held_distance_cm"]
    joined = cv.merge(ref, on=keys, suffixes=("_visible", "_broad"), validate="one_to_one")
    np.testing.assert_allclose(joined.observed_AT_ms_visible, joined.observed_AT_ms_broad)
    by = joined.assign(mse_visible=joined.error_ms_visible**2, mse_broad=joined.error_ms_broad**2,
        lpd_difference=joined.block_log_predictive_density_visible-joined.block_log_predictive_density_broad).groupby("participant_id").agg(
        mse_visible=("mse_visible", "mean"), mse_broad=("mse_broad", "mean"), lpd_difference=("lpd_difference", "sum"))
    delta = by.mse_visible-by.mse_broad
    half = stats.t.ppf(.975, len(ids)-1)*stats.sem(delta)
    comparison = dict(visible95_RMSE_ms=np.sqrt(by.mse_visible.mean()), broad_RMSE_ms=np.sqrt(by.mse_broad.mean()),
        MSE_difference=delta.mean(), MSE_low=delta.mean()-half, MSE_high=delta.mean()+half,
        log_score_difference=by.lpd_difference.sum(), log_score_cluster_SE=np.sqrt(len(ids))*by.lpd_difference.std(ddof=1),
        all_predictive_gates=bool(cv.prediction_gate.all() and ref.prediction_gate.all()))
    folds = []
    for distance, block in joined.groupby("held_distance_cm"):
        folds.append(dict(held_distance_cm=distance, visible_RMSE_ms=np.sqrt(np.mean(block.error_ms_visible**2)),
            broad_RMSE_ms=np.sqrt(np.mean(block.error_ms_broad**2)),
            both_predictive_gates=bool(block.prediction_gate_visible.all() and block.prediction_gate_broad.all())))
    pd.DataFrame(folds).to_csv(OUT / "prediction_by_distance.csv", index=False)
    stable = joined[joined.prediction_gate_visible & joined.prediction_gate_broad]
    comparison.update(converged_folds=int(stable.held_distance_cm.nunique()),
        converged_fold_visible_RMSE_ms=float(np.sqrt(np.mean(stable.error_ms_visible**2))) if len(stable) else None,
        converged_fold_broad_RMSE_ms=float(np.sqrt(np.mean(stable.error_ms_broad**2))) if len(stable) else None)
    directional.write_json(OUT / "prediction_comparison.json", comparison)
    by.to_csv(OUT / "prediction_by_participant.csv")
    rng = np.random.default_rng(20261019)
    ppc = {}
    mu_at = primary_curve[::step]+sub["baseline_mean"][..., None]
    for label, tensor, mu, sigma_name in (("AT", at, mu_at, "sigma_at"),
            ("Baseline_by_nominal_label", baseline, sub["baseline_mean"][..., None], "sigma_baseline")):
        n, obs, _ = directional.sufficient(tensor/1000)
        variance = primary_sigma[sigma_name][::step, :, None, None]**2/n
        discrepancy = np.mean((obs-mu)**2/variance, axis=(1, 2, 3))
        replicated = np.mean(rng.normal(size=mu_at.shape)**2, axis=(1, 2, 3))
        ppc[label] = float(np.mean(replicated >= discrepancy))
    directional.write_json(OUT / "posterior_predictive_checks.json", ppc)
    main = effects[effects.quantity.isin(["midpoint_cm_effect", "sharpness_per_cm_effect"])]
    hits = main[(main.ci_low > 0)|(main.ci_high < 0)]
    info = information[(information.model == "visible95") & (information.quantity == "midpoint_cm")]
    predictive_status = ("All final predictive gates passed." if comparison["all_predictive_gates"] else
        "At least one held-distance refit still fails its predictive convergence gate after the fixed extension budget. "
        "The errors and intervals below are provisional numerical summaries, not a validated model comparison; "
        "they must not be used to claim predictive superiority or noninferiority.")
    report = f"""# Explicitly shape-constrained Bayesian sigmoid approximation

## What was fitted

The owner requested a visible S after the broad positive-amplitude fits looked
nearly linear. This is an **exploratory, strongly theory-constrained approximation**,
not evidence that a sigmoid was observed. The specification was fixed before this
amendment's fits. Both models jointly use original AT and Baseline trials, fixed
cleaning, the same primary40 cohort, positive amplitudes and matched Baseline
uncertainty. Raw observations were not smoothed, clipped or transformed.

Primary `visible95` forces each normalized component to be at most .05 at 10 cm
and at least .95 at 100 cm. Sensitivity `visible90` uses .10/.90. With
`k=log((1-epsilon)/epsilon)`, width is `2+(90/(2*k)-2)*logistic(eta_width)` cm,
and midpoint is `10+k*width+(90-2*k*width)*logistic(eta_position)` cm.
Both logit coordinates have participant factorial hierarchies: fixed coefficients
Normal(0,1.5), random-coefficient SDs HalfNormal(1), independent noncentered scores.
The constraint couples the priors on midpoint and width. All nuisance priors and
the exact integrated Gaussian positive-amplitude likelihood match the broad
directional reference. Five independent checks passed, including endpoint geometry,
likelihood, prior simulation and conditional reconstruction.

The maximum primary width is **{90/(2*np.log(19)):.3f} cm**; hence normalized
sharpness is at least **{1/(4*(90/(2*np.log(19)))):.4f} /cm by assumption**.
All midpoint intervals must lie inside the sampled range because of their support.
Neither fact demonstrates better individual measurement or physiological validity.
Near-zero response amplitudes remain possible; their positive intervals follow
from the amplitude prior and do not establish a response.

## Numerical results and condition comparisons

{table(pd.DataFrame(runs)[['model','divergences','max_rhat','min_bulk_ess','min_tail_ess','gate']])}

All main finite-cohort parameter contrasts, with 95% credible intervals:

{table(main[['model','quantity','term','posterior_median','ci_low','ci_high']])}

**{len(hits)}/12** intervals exclude zero across the two shape-prior variants.
Condition means Viscereality − Control; Phase means Inhale − Exhale; interaction
is the difference of phase differences. All main/simple/RT contrasts remain in
`all_effects.csv` and `all_simple_contrasts.csv`. These are joint posterior
contrasts, not ANOVAs on pooled point estimates. The logit coefficients are not
physical-unit population effects; no such mislabeled coefficients are exported.
Any nonzero interval is conditional on a post-results shape prior, not a new
preregistered discovery. No multiplicity corrections were introduced.

## What the data add to the constraints

The median individual midpoint 95% interval is **{np.median(info.posterior_high-info.posterior_low):.1f} cm**
wide versus **{np.median(info.prior_high-info.prior_low):.1f} cm** under the new prior.
The median posterior/prior interval-width ratio is **{info.interval_width_ratio.median():.3f}**.
This is a descriptive conditional information check, not validated coverage or
test–retest reliability. All 960 individual prior/posterior summaries and 24
cohort summaries are exported. Prior comparison was independently checked against
PyMC sampling, using 5,000 prior draws. A constrained posterior can be precise
under an incorrect shape model; width contraction alone does not establish truth.

{table(pd.DataFrame(geometry_diagnostics))}

The width cap couples midpoint and width: as width approaches its maximum, the
allowed midpoint range collapses toward 55 cm. Posterior mass near that cap and
similar individual midpoints can therefore reflect the model trying to recover a
broad, nearly linear response while obeying the imposed S. This is a constraint
artifact, not independent evidence of precise or identical physiological boundaries.

## Held-distance comparison

Five primary95 refits omitted all AT trials at one distance across all people/cells,
retaining independent Baseline calibration. The preserved broad positive model has
the same target observations and nuisance priors; these were checked row by row.

**{predictive_status}**

Post hoc diagnostic decomposition of the same predictions, without refitting or
changing either model:

{table(pd.DataFrame(folds))}

Across the **{comparison['converged_folds']} converged folds only**, diagnostic RMSE
is **{comparison['converged_fold_visible_RMSE_ms']:.2f} ms** for visible95 versus
**{comparison['converged_fold_broad_RMSE_ms']:.2f} ms** for the broad reference.
This restricted subset is not the complete cross-validation result. It retains
the declared numerical gates and is reported to show which distances drive the
prediction tradeoff; every failed fold remains exported. A visible S is not itself
a reason to prefer the constrained model for physiological measurement.

- Visible95 RMSE: **{comparison['visible95_RMSE_ms']:.2f} ms**.
- Broad positive-reference RMSE: **{comparison['broad_RMSE_ms']:.2f} ms**.
- Visible minus broad MSE: **{comparison['MSE_difference']:.2f} ms²**, participant-paired
  approximate 95% interval **[{comparison['MSE_low']:.2f}, {comparison['MSE_high']:.2f}]**.
- Held-block log predictive score difference: **{comparison['log_score_difference']:.2f}**,
  participant-cluster SE **{comparison['log_score_cluster_SE']:.2f}**.
- All final predictive diagnostic gates: **{comparison['all_predictive_gates']}**.

Lower MSE and higher predictive log score favor the visible model. This comparison
is within the retained cohort and does not establish new-person generalization,
formal noninferiority or a Bayes factor. It tests predictive consequences of
requiring a visible S, not whether that S was observed. The 10/90 sensitivity was
not separately cross-validated. No bounds or cleaning thresholds were selected
using significance or held-out scores.

Primary posterior-predictive mean-profile discrepancy-tail probabilities are
AT **{ppc['AT']:.3f}**, Baseline by nominal label **{ppc['Baseline_by_nominal_label']:.3f}**.
They check the stated Gaussian model, not the truth of the sigmoid hypothesis.
The old pooled-baseline timing/variance concern remains if its discrepancy is low.

## Figures and scope

`sigmoid_curves.png` is visibly sigmoid on the measured physical-distance axis.
Its line uses the median posterior **cohort-mean midpoint and width**, transformed
into a representative unit-amplitude sigmoid. The 95% band is for that same
mean-parameter function. It is not the average individual RT curve, the pointwise
posterior median response, or a normalized observed dataset. The visibility is
guaranteed by the prior. `boundary_estimates.png` compares prior/posterior mean
midpoints. `observed_RT.png` shows actual observations and the average expected RT
function, which need not have the same appearance.

`individual_sigmoids.pdf` contains all 40 retained participants, with four raw-data
panels and four normalized model panels each. Both broad and constrained curves
remain visible on the raw-data panels. All 160 plug-in normalized curves and all
posterior draws satisfy the endpoint restriction. Parameter intervals use every
retained draw; individual/RT ribbons use 1,200 balanced draws for plotting, while
the main normalized figure uses every draw. Lines at marginal parameter medians
are not claimed to be joint MAP estimates. The 2 cm minimum width is an explicit
prior choice, not a measured resolution.

The requested visible approximation is computed. Whether these are valid
individual physiological PPS boundaries remains unresolved. Original failed fit
gates, P011/P033 recording mapping, single-session reliability and baseline-timing
limits persist. Questionnaires and a new recovery study were not run here. Earlier
unrestricted/directional results are preserved. Native execution only; no Pages
or manuscript update was performed.

## Reproduction

Use the pinned native environment in `analysis/baseline_effects/requirements.txt`:

```bash
python -m unittest discover -s analysis/visible_sigmoid -p 'test_*.py' -v
python analysis/visible_sigmoid/fit.py fit
python analysis/visible_sigmoid/fit.py cv
python analysis/visible_sigmoid/make_report.py
```

Set OPENBLAS_NUM_THREADS=1 and OMP_NUM_THREADS=1. Cross-validation resumes from its
CSV; move it aside to rerun from scratch. Large local posterior/prior draws are
hashed but not published; they can be recreated by these commands. Source, input
and public-output hashes are in `manifest.json`; public results are bundled in
`visible_results.zip`.
"""
    (OUT / "RESULTS.md").write_text(report)
    sources = list(Path(__file__).parent.glob("*.py")) + [ROOT / "analysis/directional_sigmoid/model.py",
        ROOT / "analysis/directional_sigmoid/report.py", ROOT / "analysis/baseline_effects/baseline_effects.py",
        ROOT / "analysis/baseline_effects/joint_pps.py", ROOT / "analysis/baseline_effects/requirements.txt"]
    directional.write_json(OUT / "manifest.json", dict(input_sha256=audit["input_sha256"],
        source_sha256={str(p.relative_to(ROOT)): sha(p) for p in sources},
        trace_sha256={p.name: sha(p) for p in sorted(LOCAL.glob("*.npz"))}, native_only=True,
        reference_sha256={str(p.relative_to(ROOT)): sha(p) for p in [ROOT / "results/directional_sigmoid/held_distance_predictions.csv",
            ROOT / "results/directional_sigmoid/measured_range_curves.csv"]},
        output_sha256={p.name: sha(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name not in ("manifest.json", "visible_results.zip")}))
    with zipfile.ZipFile(OUT / "visible_results.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        for p in sorted(OUT.iterdir()):
            if p.is_file() and p.name != "visible_results.zip":
                archive.write(p, p.name)
    print("Packaged two constrained fits, 160 visibly sigmoid components, 40 atlas pages, prior checks and five prediction folds.")


if __name__ == "__main__":
    main()
