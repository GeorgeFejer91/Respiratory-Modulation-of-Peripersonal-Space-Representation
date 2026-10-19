"""Report the directional amendment without replacing previous result snapshots."""
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

from model import OUT, LOCAL, ROOT, X, CELL_NAMES, primary_data, sufficient, write_csv, write_json


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def table(frame):
    lines = ["| " + " | ".join(frame.columns) + " |", "| " + " | ".join("---" for _ in frame.columns) + " |"]
    for row in frame.itertuples(index=False, name=None):
        lines.append("| " + " | ".join(f"{v:.4g}" if isinstance(v, (float, np.floating)) else str(v) for v in row) + " |")
    return "\n".join(lines)


def main():
    ids, at, baseline, audit = primary_data()
    run = json.loads((OUT / "run.json").read_text())
    data = np.load(LOCAL / "positive_draws.npz")
    values = {name: data[name].reshape(-1, len(ids), 4) for name in
        ("midpoint_cm", "sharpness_per_cm", "amplitude", "corrected_intercept", "baseline_mean")}
    assert (values["amplitude"] > 0).all() and (values["sharpness_per_cm"] > 0).all()
    assert (np.diff(data["corrected_curve"], axis=-1) >= -1e-12).all()
    count, observed, _ = sufficient(at/1000)
    nb, observed_b, _ = sufficient(baseline/1000)
    bflat = baseline.reshape(len(ids), 4, -1)
    corrected = 1000*(observed-np.nanmean(bflat, -1)[..., None]/1000)
    error = np.sqrt(np.nanvar(at, -1, ddof=1)/count +
        (np.nanvar(bflat, -1, ddof=1)/np.isfinite(bflat).sum(-1))[..., None])
    quantities = {name: np.quantile(a, [.025, .5, .975], axis=0) for name, a in values.items()}
    m, sharp = quantities["midpoint_cm"][1], quantities["sharpness_per_cm"][1]
    lo_m, hi_m = quantities["midpoint_cm"][[0, 2]]
    width = 1/(4*sharp)
    both_plateaus = ((m-np.log(9)*width >= 10)&(m+np.log(9)*width <= 100))
    # Thinning is balanced across the four chains; inferential intervals above use every draw.
    selected = np.arange(0, len(values["amplitude"]), max(1, len(values["amplitude"])//1200))
    plot_draws = {name: v[selected] for name, v in values.items()}
    grid = np.linspace(10, 100, 121)
    group = np.zeros((len(selected), 4, len(grid)))
    colors = ["#215A8E", "#387C9B", "#B24C22", "#D37824"]
    rows, plateau_rows = [], []
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False,
        "axes.spines.right": False, "pdf.fonttype": 42})
    with PdfPages(OUT / "individual_curves.pdf") as pdf:
        for i, pid in enumerate(ids):
            fig, axes = plt.subplots(2, 2, figsize=(10, 8), sharex=True, sharey=True)
            for c, ax in enumerate(axes.flat):
                mp, sp, ap, dp = [plot_draws[name][:, i, c] for name in
                    ("midpoint_cm", "sharpness_per_cm", "amplitude", "corrected_intercept")]
                predicted = 1000*(dp[:, None]+ap[:, None]*(special.expit((grid-mp[:, None])*4*sp[:, None])-.5))
                assert np.all(np.diff(predicted, axis=-1) >= -1e-12)
                group[:, c] += predicted/len(ids)
                low, med, high = np.quantile(predicted, [.025, .5, .975], axis=0)
                assert (np.diff(med) >= -1e-12).all()
                for j, d in enumerate(grid):
                    rows.append(dict(participant_id=pid, cell=CELL_NAMES[c], distance_cm=d,
                        expected_RT_low_ms=low[j], expected_RT_median_ms=med[j], expected_RT_high_ms=high[j]))
                for label, draws in (("near_lower_asymptote_ms", values["corrected_intercept"][:, i, c]-values["amplitude"][:, i, c]/2),
                                     ("far_upper_asymptote_ms", values["corrected_intercept"][:, i, c]+values["amplitude"][:, i, c]/2)):
                    q = 1000*np.quantile(draws, [.025, .5, .975])
                    plateau_rows.append(dict(participant_id=pid, cell=CELL_NAMES[c], quantity=label,
                        median=q[1], ci_low=q[0], ci_high=q[2]))
                ax.fill_between(grid, low, high, color=colors[c], alpha=.16)
                ax.plot(grid, med, lw=2, color=colors[c])
                ax.errorbar(X, corrected[i, c], yerr=error[i, c], fmt="o", color="#222222", ms=4, capsize=2)
                ax.set_title(CELL_NAMES[c])
                ax.set_xlim(8, 102)
                ax.axhline(0, color="#888888", ls=":", lw=.6)
                ax.text(.03, .97, f"Midpoint {m[i,c]:.1f} [{lo_m[i,c]:.1f}, {hi_m[i,c]:.1f}] cm\n"
                    f"Sharpness {sharp[i,c]:.4f} /cm", transform=ax.transAxes, va="top", fontsize=8,
                    bbox=dict(facecolor="white", alpha=.85, edgecolor="none"))
            fig.suptitle(f"{pid}: common near-to-far direction in all four conditions", fontsize=13)
            fig.supxlabel("Increasing physical distance (cm); measured range", y=.075)
            fig.supylabel("Audio–Tactile minus matched Baseline RT (ms)")
            fig.text(.5, .018, "Dots: unsmoothed means ± marginal SE; baseline error is shared. "
                     "Band: 95% expected-response interval.\nNear lower / far higher RT is imposed by A ≥ 0; "
                     "a flat-looking curve or an unobserved plateau remains possible.", ha="center", fontsize=8)
            fig.tight_layout(rect=(.025, .10, 1, .95))
            pdf.savefig(fig)
            if i == 0:
                fig.savefig(OUT / "individual_example.png", dpi=170)
            plt.close(fig)
    write_csv(OUT / "measured_range_curves.csv", rows)
    write_csv(OUT / "asymptotes.csv", plateau_rows)
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), sharex=True, sharey=True)
    for c, ax in enumerate(axes.flat):
        low, med, high = np.quantile(group[:, c], [.025, .5, .975], axis=0)
        ax.fill_between(grid, low, high, color=colors[c], alpha=.16)
        ax.plot(grid, med, lw=2, color=colors[c])
        ax.errorbar(X, corrected[:, c].mean(0), yerr=stats.t.ppf(.975, len(ids)-1)*stats.sem(corrected[:, c], 0),
            fmt="o", color="#222222", ms=4, capsize=3)
        ax.set_title(CELL_NAMES[c])
        ax.set_xlim(8, 102)
    fig.suptitle("Common-direction hierarchical sigmoid: 40 retained participants")
    fig.supxlabel("Increasing physical distance (cm)", y=.07)
    fig.supylabel("AT minus matched Baseline RT (ms)")
    fig.text(.5, .018, "Dots: equal-participant means ± 95% CI; bands: 95% expected-response intervals.\n"
             "All fitted directions are constrained to increasing RT. Raw observations retain their original direction.", ha="center", fontsize=8)
    fig.tight_layout(rect=(.025, .10, 1, .95))
    fig.savefig(OUT / "average_curves.png", dpi=180)
    fig.savefig(OUT / "average_curves.pdf")
    plt.close(fig)
    prediction = pd.read_csv(OUT / "held_distance_predictions.csv")
    assert len(prediction) == 1600 and not prediction.duplicated(["model", "held_distance_cm", "participant_id", "cell"]).any()
    byperson = prediction.groupby(["participant_id", "model"]).agg(
        mse=("error_ms", lambda v: np.mean(v*v)), lpd=("block_log_predictive_density", "sum")).unstack("model")
    difference = byperson.mse.positive_amplitude-byperson.mse.unrestricted
    half = stats.t.ppf(.975, len(ids)-1)*stats.sem(difference)
    lpd = byperson.lpd.positive_amplitude-byperson.lpd.unrestricted
    comparison = dict(positive_RMSE_ms=np.sqrt(byperson.mse.positive_amplitude.mean()),
        unrestricted_RMSE_ms=np.sqrt(byperson.mse.unrestricted.mean()),
        positive_minus_unrestricted_MSE=difference.mean(), mse_ci_low=difference.mean()-half, mse_ci_high=difference.mean()+half,
        positive_minus_unrestricted_log_score=lpd.sum(), participant_cluster_log_score_SE=np.sqrt(len(ids))*lpd.std(ddof=1),
        all_prediction_gates=bool(prediction.prediction_gate.all()))
    write_json(OUT / "prediction_comparison.json", comparison)
    rng = np.random.default_rng(20261019)
    expected = data["corrected_curve"].reshape(-1, len(ids), 4, 5)[selected]+plot_draws["baseline_mean"][..., None]
    sa = data["sigma_at"].reshape(-1, len(ids))[selected, :, None, None]
    sb = data["sigma_baseline"].reshape(-1, len(ids))[selected, :, None, None]
    ppc = {}
    for name, obs, mu, sigma, counts in (("AT", observed, expected, sa, count),
            ("Baseline_by_nominal_label", observed_b, plot_draws["baseline_mean"][..., None], sb, nb)):
        variance = sigma**2/counts
        discrepancy = np.mean((obs-mu)**2/variance, axis=(1, 2, 3))
        replicated = np.mean(rng.normal(size=expected.shape)**2, axis=(1, 2, 3))
        ppc[name] = float(np.mean(replicated >= discrepancy))
    write_json(OUT / "posterior_predictive_checks.json", ppc)
    effects = pd.read_csv(OUT / "effects.csv")
    shape = effects[effects.quantity.isin(["midpoint_cm_effect", "sharpness_per_cm_effect"])]
    hits = shape[(shape.ci_low > 0)|(shape.ci_high < 0)]
    report = f"""# Consistent asymptote direction: refit and results

## Resolution

The previous signed-amplitude model allowed the response's near/far ordering to
reverse independently in each condition. That was a flexible diagnostic reference,
not a requirement of PPS physiology. The midpoint locates a transition; the
amplitude sign determines its direction. The owner now requests a common direction.

We refitted **all 160 participant × condition × phase curves** with
`corrected_RT(d) = delta + A*(logistic((d-m)/w)-0.5)`, **A >= 0**, **w > 0**.
On increasing physical distance, the near asymptote is always the lower RT and
the far asymptote the higher RT. Width and midpoint remain condition-specific with
hierarchical partial pooling. SOA runs in the opposite order to the mapped distance;
plotting increasing elapsed time instead would reverse the same curve's display.

This resolves ordering without forcing equal **numerical** plateau heights:
`L = delta - A/2`, `H = delta + A/2`, so H >= L in every draw. Making L and H
identical across a person's four conditions would be a stronger additional
measurement-invariance assumption; it was not needed or fitted here. No fitted
curve or observed trial was flipped after fitting. Reversed raw observations
remain visible as discrepancies, and arbitrarily small amplitudes remain allowed.

## Estimation and numerical checks

This is an exploratory amendment after previous results, specified in
`specification.json` before these fits. It changes the independent amplitude prior
from Normal(0,.15 seconds) to HalfNormal(.15 seconds); other priors match the earlier
converged marginalized reference. The same fixed cleaning, 40-person cohort and
participant × condition × phase Baseline calibration are retained. Baseline,
intercept and amplitude uncertainty are propagated jointly, not pre-subtracted and
then treated as independent. Baseline/offset/amplitude are integrated analytically;
the positive prior adds the exact Gaussian conditional orthant-probability factor.
Truncated-normal/Gaussian conditional draws reconstruct expected RTs afterward.

Five tests passed: likelihood versus an independent full-trial multivariate-normal
calculation, conditional moments/covariance, an empty held-out likelihood block,
monotonicity/midpoint/derivative, and posterior export. Final fit: **{run['divergences']}
divergences, maximum Rhat {run['max_rhat']:.4f}, minimum bulk/tail ESS
{run['min_bulk_ess']:.0f}/{run['min_tail_ess']:.0f}, diagnostic gate {run['gate']}**.
All sampling attempts, including any failures, remain in `fit_attempts.json`.

## Boundary and sharpness results

{table(shape[['quantity','term','posterior_median','ci_low','ci_high','probability_positive']])}

These are finite-cohort paired contrasts with 95% credible intervals. Condition =
Viscereality − Control; Phase = Inhale − Exhale; interaction = difference of phase
differences. **{len(hits)}/6** main shape contrasts have intervals excluding zero.
Full population coefficients, response contrasts and all simple shape contrasts
are retained in `effects.csv` and `simple_parameter_contrasts.csv`. Interpret any
effect conditional on the new direction restriction and numerical diagnostics.
This is not an RM ANOVA on pooled posterior medians.

All amplitudes are positive **by assumption**, so a positive amplitude interval is
not evidence establishing a PPS response. Midpoint estimates span
**{m.min():.1f}–{m.max():.1f} cm**; **{int(((lo_m >= 10)&(hi_m <= 100)).sum())}/160**
midpoint intervals lie wholly in the 10–100 cm sampled range. Median midpoint
interval width is **{np.median(hi_m-lo_m):.1f} cm**. The median plug-in 10–90%
transition spans **{np.median(2*np.log(9)*width):.1f} cm**, versus 90 cm sampled;
**{int(both_plateaus.sum())}/160** plug-in curves show both transition levels in
that range. Consistent direction does not itself establish identifiable plateaus,
curvature or individual physiological boundaries.

## Held-distance prediction comparison

All five AT-distance blocks were omitted in turn, across all participants/cells,
for both the positive and otherwise matched unrestricted model. Baseline remains
independent calibration. No direction, smoothing setting or p value was selected
using held-out results. Every prediction and both models' numerical attempts are
retained; **all final predictive gates passed: {comparison['all_prediction_gates']}**.

- Positive-amplitude RMSE: **{comparison['positive_RMSE_ms']:.2f} ms**.
- Unrestricted RMSE: **{comparison['unrestricted_RMSE_ms']:.2f} ms**.
- Positive minus unrestricted MSE: **{comparison['positive_minus_unrestricted_MSE']:.2f} ms²**,
  participant-paired 95% interval **[{comparison['mse_ci_low']:.2f}, {comparison['mse_ci_high']:.2f}]**.
- Held-block log predictive score difference: **{comparison['positive_minus_unrestricted_log_score']:.2f}**,
  participant-cluster SE **{comparison['participant_cluster_log_score_SE']:.2f}**.

Negative MSE differences favor the directional model; positive log-score differences
favor it. The paired uncertainty treats people as clusters and conditions on these
fitted prediction procedures; it is not a calibrated probability that one model is
true, a Bayes factor or new-participant validation. Check prediction tradeoffs
before presenting the directional model as a physiologically motivated
approximation; do not describe the direction as discovered from the constraint.

Posterior predictive mean-profile discrepancy-tail probabilities are
**AT {ppc['AT']:.3f}**, **Baseline by nominal label {ppc['Baseline_by_nominal_label']:.3f}**.
These check the stated Gaussian likelihood and pooled Baseline across nominal
labels, not the sign hypothesis. The earlier unverified cue-time-equivalence
and possible timing/variance discrepancies remain relevant.

## Figures and publication use

`average_curves.png` and all 40 pages of `individual_curves.pdf` use the measured
range and retain unsmoothed observations. Every posterior expected-response draw
and every exported median curve was checked to increase monotonically with
physical distance. The figures do not create missing plateaus by extending axes.
The earlier signed and standardized-full-S figures remain preserved references;
their condition-specific reversals are not the newly requested specification.

This model resolves the interpretational objection to reversed near/far asymptotes.
Its shape-effect conclusions, uncertainty and predictive comparison above determine
what can be reported. It does not turn an RT-location interaction into a boundary
effect or justify choosing a model because it yields significance. All prior
outcomes remain available; any p values in those outputs are still unadjusted.
Separate participant-shared numerical plateaus, robust likelihoods, questionnaires
and another recovery study were not fitted in this amendment. P011/P033 recording
mapping, original failed fit gate and individual measurement limits remain open.
Native execution only; browser/Pages and manuscripts were not updated.

## Reproduce

Use Python 3.12 and `analysis/baseline_effects/requirements.txt`, with
OPENBLAS_NUM_THREADS=1 and OMP_NUM_THREADS=1:

```bash
python -m unittest discover -s analysis/directional_sigmoid -p 'test_*.py' -v
python analysis/directional_sigmoid/model.py fit
python analysis/directional_sigmoid/model.py cv
python analysis/directional_sigmoid/report.py
```

Cross-validation resumes completed folds from its CSV; move it aside for a fresh
run. The source, inputs, local posterior trace and public outputs are hashed in
`manifest.json`; large traces remain local. The downloadable ZIP contains the
public results, figures, specifications and diagnostics.
"""
    (OUT / "RESULTS.md").write_text(report)
    source_files = list(Path(__file__).parent.glob("*.py")) + [ROOT / "analysis/baseline_effects/baseline_effects.py",
        ROOT / "analysis/baseline_effects/joint_pps.py", ROOT / "analysis/baseline_effects/requirements.txt"]
    write_json(OUT / "manifest.json", dict(input_sha256=audit["input_sha256"],
        source_sha256={str(p.relative_to(ROOT)): sha(p) for p in source_files},
        local_trace_sha256=sha(LOCAL / "positive_draws.npz"), native_only=True,
        output_sha256={p.name: sha(p) for p in sorted(OUT.iterdir())
            if p.is_file() and p.name not in ("manifest.json", "directional_results.zip")}))
    with zipfile.ZipFile(OUT / "directional_results.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        for p in sorted(OUT.iterdir()):
            if p.is_file() and p.name != "directional_results.zip":
                archive.write(p, p.name)
    print(f"Packaged 160 consistently oriented curves, 40 atlas pages, {len(shape)} main shape contrasts and 10 prediction folds.")


if __name__ == "__main__":
    main()
