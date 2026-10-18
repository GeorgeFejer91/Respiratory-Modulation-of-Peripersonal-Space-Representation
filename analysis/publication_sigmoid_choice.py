"""Package an explicitly exploratory sigmoid choice from existing joint draws.

No observations, priors, smoothing settings or effect tests are changed. The
standardized full-S view illustrates the parameterization, not observed bends.
"""
import hashlib
import json
from pathlib import Path
import sys
import zipfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pandas as pd
from scipy.special import expit

sys.path.insert(0, str(Path(__file__).resolve().parent / "baseline_effects"))
from baseline_effects import (ROOT, OUT, LOCAL, CELL_NAMES, DISTANCES, load_data,
    cohort_mask, profiles, write_csv, write_json)

DEST = ROOT / "results/publication_sigmoid_choice"
MODEL = "joint_logistic_marginal"


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def markdown(frame):
    columns = list(frame.columns)
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in frame.itertuples(index=False, name=None):
        lines.append("| " + " | ".join(f"{v:.4g}" if isinstance(v, (float, np.floating)) else str(v) for v in row) + " |")
    return "\n".join(lines)


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    ids, at, baseline, audit = load_data()
    assert audit["input_sha256"] == json.loads((OUT / "manifest.json").read_text())["input_sha256"]
    keep = cohort_mask(ids, "primary40")
    ids, at, baseline = ids[keep], at[keep], baseline[keep]
    run = json.loads((OUT / (MODEL+"_run.json")).read_text())
    assert run["target_diagnostic_gate"] and run["max_rhat"] <= 1.01
    assert min(run["min_bulk_ess"], run["min_tail_ess"]) >= 400
    archive = LOCAL / (MODEL+"_draws.npz")
    with np.load(archive) as source:
        arrays = {k: source[k].reshape(-1, len(ids), 4) for k in
                  ("midpoint_cm", "sharpness_per_cm", "amplitude", "corrected_intercept")}
        x = DISTANCES["registered"]
        exact = (arrays["corrected_intercept"][..., None] +
                 arrays["amplitude"][..., None] *
                 (expit((x-arrays["midpoint_cm"][..., None])*4*arrays["sharpness_per_cm"][..., None])-.5))
        np.testing.assert_allclose(exact, source["corrected_curve"].reshape(exact.shape), atol=1e-12)
    quantiles = {k: np.quantile(v, [.025, .5, .975], axis=0) for k, v in arrays.items()}
    m = quantiles["midpoint_cm"][1]
    s = quantiles["sharpness_per_cm"][1]
    width = 1/(4*s)
    amplitude = quantiles["amplitude"][1]
    intercept = quantiles["corrected_intercept"][1]
    assert np.isfinite(m).all() and (s > 0).all() and (np.abs(amplitude) > 1e-12).all()
    z = np.linspace(-6, 6, 241)
    normalized = expit(np.sign(amplitude)[..., None]*z)
    np.testing.assert_allclose(normalized[..., 120], .5)
    np.testing.assert_allclose(np.abs(normalized[..., -1]-normalized[..., 0]), np.tanh(3))
    # Independently check the signed raw RT derivative at each plug-in midpoint.
    epsilon = 1e-4
    derivative = 1000*amplitude*(expit(epsilon/width)-expit(-epsilon/width))/(2*epsilon)
    np.testing.assert_allclose(derivative, 1000*amplitude*s, rtol=1e-8)
    y = profiles(at, baseline, "pooled_cp")
    nb = np.isfinite(baseline.reshape(len(ids), 4, -1)).sum(-1)
    error = np.sqrt(np.nanvar(at, -1, ddof=1)/np.isfinite(at).sum(-1) +
                    (np.nanvar(baseline.reshape(len(ids), 4, -1), -1, ddof=1)/nb)[..., None])
    parameters, curve_records, observed = [], [], []
    colors = ["#215A8E", "#387C9B", "#B24C22", "#D37824"]
    grid = np.linspace(10, 100, 121)
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False,
                         "axes.spines.right": False, "pdf.fonttype": 42})
    with PdfPages(DEST / "individual_sigmoids.pdf") as pdf:
        for i, pid in enumerate(ids):
            fig, axes = plt.subplots(2, 4, figsize=(13, 7))
            for c, cell in enumerate(CELL_NAMES):
                mq = quantiles["midpoint_cm"][:, i, c]
                sq = quantiles["sharpness_per_cm"][:, i, c]
                aq = 1000*quantiles["amplitude"][:, i, c]
                lower, upper = m[i, c]-np.log(9)*width[i, c], m[i, c]+np.log(9)*width[i, c]
                parameters.append(dict(participant_id=pid, cell=cell, model=MODEL,
                    midpoint_cm=mq[1], midpoint_ci_low=mq[0], midpoint_ci_high=mq[2],
                    sharpness_per_cm=sq[1], sharpness_ci_low=sq[0], sharpness_ci_high=sq[2],
                    plugin_width_cm=width[i, c], transition_10pct_cm=lower, transition_90pct_cm=upper,
                    plugin_amplitude_ms=aq[1], amplitude_ci_low=aq[0], amplitude_ci_high=aq[2],
                    amplitude_excludes_zero=bool(aq[0] > 0 or aq[2] < 0),
                    midpoint_interval_inside_observed_range=bool(mq[0] >= 10 and mq[2] <= 100),
                    plugin_both_10_90_plateaus_observed=bool(lower >= 10 and upper <= 100)))
                # All draws are used in the parameter table; balanced thinning is only for plotting.
                sampled = {k: v[::12, i, c] for k, v in arrays.items()}
                predicted = 1000*(sampled["corrected_intercept"][:, None] + sampled["amplitude"][:, None] *
                    (expit((grid-sampled["midpoint_cm"][:, None])*4*sampled["sharpness_per_cm"][:, None])-.5))
                low, med, high = np.quantile(predicted, [.025, .5, .975], axis=0)
                plugin = 1000*(intercept[i, c]+amplitude[i, c]*(expit((grid-m[i, c])/width[i, c])-.5))
                for j, distance in enumerate(grid):
                    curve_records.append(dict(participant_id=pid, cell=cell, distance_cm=distance,
                        expected_RT_low_ms=low[j], expected_RT_median_ms=med[j], expected_RT_high_ms=high[j],
                        plugin_RT_ms=plugin[j]))
                for j, distance in enumerate(x):
                    observed.append(dict(participant_id=pid, cell=cell, distance_cm=distance,
                        corrected_RT_mean_ms=y[i, c, j], marginal_sampling_SE_ms=error[i, c, j],
                        AT_trials=int(np.isfinite(at[i, c, j]).sum()), baseline_pool_trials=int(nb[i, c])))
                ax = axes[0, c]
                ax.fill_between(grid, low, high, color=colors[c], alpha=.16)
                ax.plot(grid, med, color="#666666", ls=":", lw=1, label="Posterior median response")
                ax.plot(grid, plugin, color=colors[c], lw=2, label="Plug-in logistic")
                ax.errorbar(x, y[i, c], yerr=error[i, c], fmt="o", color="#222222", ms=3, capsize=2)
                ax.set_title(cell)
                ax.set_xlim(8, 102)
                ax.set_xlabel("Measured distance (cm)")
                ax.set_ylabel("AT minus Baseline RT (ms)")
                ax.text(.03, .97, f"m = {mq[1]:.1f} [{mq[0]:.1f}, {mq[2]:.1f}] cm\n"
                        f"sharpness = {sq[1]:.4f} /cm", transform=ax.transAxes, va="top", fontsize=8,
                        bbox=dict(facecolor="white", alpha=.85, edgecolor="none"))
                if c == 0:
                    ax.legend(loc="lower left", fontsize=7)
                ax = axes[1, c]
                a, b = (x[[0, -1]]-m[i, c])/width[i, c]
                ax.axvspan(a, b, color=colors[c], alpha=.16, label="Measured distance segment")
                ax.plot(z, normalized[i, c], color="#888888", ls="--", lw=1.5)
                measured_z = np.linspace(a, b, 100)
                ax.plot(measured_z, expit(np.sign(amplitude[i, c])*measured_z), color=colors[c], lw=3)
                ax.axvline(0, lw=.6, color="#999999")
                ax.set(xlim=(-6, 6), ylim=(-.04, 1.04), xlabel="Standardized distance: (d - m) / width",
                       ylabel="Unit-amplitude model geometry")
                ax.set_title("Model geometry: " + ("increasing" if aq[1] > 0 else "decreasing"), fontsize=9)
                ax.text(.03, .05, f"10–90% transition width: {upper-lower:.0f} cm\n"
                        + ("Amplitude direction supported" if aq[0] > 0 or aq[2] < 0 else "Amplitude interval includes zero"),
                        transform=ax.transAxes, fontsize=8, bbox=dict(facecolor="white", alpha=.8, edgecolor="none"))
            # Shared response axes within a person; normalization is only in the labelled model row.
            limits = np.array([ax.get_ylim() for ax in axes[0]])
            for ax in axes[0]:
                ax.set_ylim(limits[:, 0].min(), limits[:, 1].max())
            fig.suptitle(f"{pid}: partial pooling across participants and a continuous sigmoid across SOA", fontsize=13)
            fig.text(.5, .025, "Top: unsmoothed observations ± marginal SE; band = 95% expected-response interval. "
                     "Baseline error is shared across distances.\nBottom: standardized model illustration, with measured segment shaded. "
                     "Centering/scaling guarantees a visible S; extrapolated bends are assumptions, not observations.\n"
                     "Plug-in curves use marginal parameter medians; they differ from the pointwise posterior median response. "
                     "Signed amplitudes and all four cells are retained.", ha="center", fontsize=8)
            fig.tight_layout(rect=(0, .11, 1, .95))
            pdf.savefig(fig)
            if i == 0:
                fig.savefig(DEST / "individual_example.png", dpi=170)
            plt.close(fig)
    assert len(parameters) == 160 and len(observed) == 800 and len(curve_records) == 19360
    write_csv(DEST / "participant_parameters.csv", parameters)
    write_csv(DEST / "measured_range_curves.csv", curve_records)
    write_csv(DEST / "unsmoothed_observations.csv", observed)
    effects = pd.read_csv(OUT / "joint_simple_effects.csv")
    effects = effects[(effects.model.isin([MODEL, "joint_logistic_heterogeneous"])) &
                      effects.quantity.isin(["midpoint_cm", "sharpness_per_cm"])]
    assert len(effects) == 28 and effects.target_diagnostic_gate.all()
    effects.to_csv(DEST / "joint_parameter_contrasts.csv", index=False)
    main_effects = effects[(effects.model == MODEL) & effects.effect.isin(["Condition", "Phase", "Condition × Phase"])]
    frame = pd.DataFrame(parameters)
    report = f"""# Publication-focused sigmoid analysis choice

## Decision and goal

Use **one hierarchical Bayesian logistic model**, with partial pooling across people
and a continuous response across the five SOA-mapped distances, to describe four
curves per participant. The selected existing exploratory estimator is
`{MODEL}`; the cell-noise `joint_logistic_heterogeneous` fit is its retained
sensitivity. This is a choice after seeing results, not a newly confirmed primary
analysis or evidence that this specification predicts best. No new effect test,
cleaning change, bandwidth search, prior restriction or curve fitting occurred here.

The goal is a reproducible, publication-defensible estimate and comparison of
midpoint and sharpness in every retained participant × condition × phase cell,
with uncertainty and explicit identification limits. Across-person smoothing is
hierarchical partial pooling, not averaging adjacent participant IDs. Across-SOA
smoothing is the continuous logistic likelihood, not repeated filtering until a
desired shape or p value appears. The model uses original AT and Baseline trials
jointly and propagates shared baseline uncertainty.

## Why this choice

It supplies **160 finite curves for all 40 retained participants**, preserves all
four cells and signed amplitudes, and passes convergence checks: zero divergences,
maximum Rhat {run['max_rhat']:.4f}, minimum bulk ESS {run['min_bulk_ess']:.0f} and
minimum tail ESS {run['min_tail_ess']:.0f}. Independent nuisance integration avoids
the unresolved mixing problems in the initial hierarchical-nuisance model. It has
the same shape hierarchy, but different intercept/amplitude pooling assumptions.
Cell-varying residual noise remains a sensitivity, not another replication.

The scientific rationale is theory-motivated sigmoid estimation with partial
pooling, checked by prediction, identifiability and recovery. See the existing
[PPS methods rationale](../../literature_review/ANALYSIS_RATIONALE.md) and
[individual-parameter review](../../literature_review/INDIVIDUAL_PARAMETERS.md).
Canzoneri et al. (2012), doi:10.1371/journal.pone.0044306, supplies a PPS sigmoid
precedent, not justification for forced individual shapes. Ahn et al. (2011),
doi:10.1037/a0020684, motivates partial pooling through recovery in another task;
it does not validate this model. Hedge et al. (2018),
doi:10.3758/s13428-017-0935-1, motivates checking individual reliability.
This package uses the already accessed evidence; it is not a new literature search.

## What the smoothing actually supplies

The marginal-median midpoint estimates span **{m.min():.1f}–{m.max():.1f} cm**.
Their median 95% interval width is **{np.median(quantiles['midpoint_cm'][2]-quantiles['midpoint_cm'][0]):.1f} cm**;
**{frame.midpoint_interval_inside_observed_range.sum()}/160** intervals lie wholly
inside the measured 10–100 cm range. Only **{frame.amplitude_excludes_zero.sum()}/160**
amplitude intervals exclude zero. Finite values are model-based approximations,
not established individual physiological boundaries. These identification counts
use all retained draws; the earlier predictive-check summary used thinned draws
and therefore has slightly different approximate counts and interval widths.

The fitted 10–90% transition width is **{np.median(2*np.log(9)*width):.0f} cm** at
the median, versus a **90 cm** sampled range. **{frame.plugin_both_10_90_plateaus_observed.sum()}/160**
plug-in curves show both 10% and 90% levels inside that range. This is why the
measured-range plots look nearly linear even though their mathematical functions
are sigmoids. Stronger kernel smoothing alone usually removes curvature; a narrow
visible S would additionally require a shape/width assumption that these
observations have not established. A prior centred on zero effects is not a
constraint that effects must be zero.

`individual_sigmoids.pdf` includes every participant. Its top row shows unsmoothed
data, a plug-in logistic and posterior expected-response uncertainty on the measured
range. The bottom row shows each fitted sigmoid on its standardized coordinate
with the measured segment shaded. It makes the complete S visible **by definition**;
its unmeasured bends are explicitly model extrapolation. This row is a methodological
illustration, not a figure establishing a physiological transition. No observed
RT was clipped, normalized by an unstable amplitude, or altered. Plug-in curves use
marginal medians and are not claimed to be a joint MAP or an individually validated
best curve. Response ribbons use 1,000 balanced draws; parameter intervals use all
12,000 retained draws. Ribbons are conditional on the stated model.

## Statistical comparison across the four cells

Use **joint posterior paired contrasts**, carrying parameter uncertainty and shared
pooling through the analysis. Condition = Viscereality − Control, Phase = Inhale −
Exhale, interaction = difference of phase differences. The main finite-cohort
contrasts and 95% credible intervals are:

{markdown(main_effects[['quantity','effect','posterior_median','ci_low','ci_high']])}

All intervals include zero. `joint_parameter_contrasts.csv` retains all main and
simple contrasts from both converged variants. A conventional RM ANOVA on smoothed
or pooled point estimates treats shared estimates as independent measurements and
omits fit uncertainty. The earlier zero-population-effect simulation produced
six nominally significant point-median tests; those are not suitable evidence for
choosing this analysis. Their full outputs remain in the original batch.

## Which result belongs at the front

For the PPS question, lead with the **uncertainty of the boundary/sharpness
estimates and the absence of a clearly supported condition or phase difference**,
not a selected smoothing-dependent p value. The group-level positive result that
is easiest to defend is **AT − Baseline = −18.65 ms**, 95% CI [−27.26, −10.04],
unadjusted paired p = .0000865. This establishes overall RT facilitation under the
specified baseline matching; it does not locate a PPS boundary.

If discussing the experimental interaction, the clearest exploratory candidate
is the **Student-t linear RT model**: Condition × Phase = −17.82 ms,
95% credible interval [−32.82, −2.98]. Its log-distance counterpart agrees, but
Gaussian population models and the primary paired test (p = .119) do not establish
it. Present the likelihood sensitivity next to the result. This is an RT-location
interaction, not evidence of a boundary or sharpness change, and was found after
a broad method search. The nominal heavily smoothed sharpness p = .0336 is less
defensible as the lead: its refit interval crosses zero and deletion sensitivity
can raise p above .05. All p values remain unadjusted as requested.

## Publication status and limits

The approximation and its inconclusive parameter comparison are reportable as an
exploratory analysis with these disclosures. **A significant PPS boundary or
sharpness finding is not currently supported.** Publication acceptance cannot be
guaranteed by smoothing. The trial likelihood, priors and participant hierarchy
remain assumptions; convergence is not validation. The existing held-distance
comparison used a different nuisance-pooling model and favored no sigmoid over a
line; the selected marginalized variant has not had a separate cross-validation
or repeated-simulation coverage study. Its pooled-baseline predictive discrepancy
and unverified baseline-label timing remain unresolved.

P011/P033 remain excluded together because their recording-to-person mapping is
unresolved; this choice supplies every *retained* person's estimates, not 42
independent records. Questionnaire analyses were not repeated. Native execution
only; Pages and manuscript assets are unchanged. Reproduce with
`python analysis/publication_sigmoid_choice.py` after the native joint runs in
`analysis/baseline_effects/README.md`. Large posterior draws stay local and are
recreated by those commands; the public curve/parameter tables remain sufficient
to inspect the delivered plots. See the [full original batch](../baseline_effects/RESULTS.md).
"""
    (DEST / "RECOMMENDATION.md").write_text(report)
    inputs = {str(p.relative_to(ROOT)): sha(p) for p in
              [Path(__file__), archive, OUT / (MODEL+"_run.json"), OUT / "joint_simple_effects.csv"]}
    inputs.update({"data/raw/"+name: digest for name, digest in audit["input_sha256"].items()})
    write_json(DEST / "manifest.json", dict(model=MODEL, purpose="exploratory publication-method choice; no new fits/tests",
        input_sha256=inputs, output_sha256={p.name: sha(p) for p in sorted(DEST.iterdir())
            if p.is_file() and p.name not in ("manifest.json", "publication_choice.zip")},
        validation="draw-to-response identity, sigmoid geometry and signed derivative, counts, full convergence gate",
        native_only=True, pages_updated=False, manuscript_updated=False))
    with zipfile.ZipFile(DEST / "publication_choice.zip", "w", zipfile.ZIP_DEFLATED) as bundle:
        for p in sorted(DEST.iterdir()):
            if p.is_file() and p.name != "publication_choice.zip":
                bundle.write(p, p.name)
    print(f"Packaged {len(parameters)} participant × cell curves, 40 atlas pages and an explicit recommendation.")


if __name__ == "__main__":
    main()
