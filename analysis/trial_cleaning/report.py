"""Package the complete cleaning sensitivity family without selecting an effect."""
import hashlib
from importlib.metadata import version
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
from scipy import special, stats

from run import (ROOT, OUT, LOCAL, CONFIGS, X, W, EFFECTS, CELL_NAMES,
                 source, prepare, tensors, directional, write_csv, write_json, definition_hash)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def table(frame):
    return "\n".join(["| "+" | ".join(map(str, frame.columns))+" |",
        "| "+" | ".join(["---"]*len(frame.columns))+" |"]+
        ["| "+" | ".join(f"{v:.4g}" if isinstance(v, (float, np.floating)) else str(v) for v in row)+" |"
         for row in frame.itertuples(index=False, name=None)])


def response(draws, grid):
    return 1000*(draws["corrected_intercept"][..., None]+draws["amplitude"][..., None]*(
        special.expit((grid-draws["midpoint_cm"][..., None])/draws["width_cm"][..., None])-.5))


def main():
    _, _, eligible, _, ids, _ = source()
    runs, effects, simple, parameter_tables, quality, cohort = [], [], [], [], [], []
    display, data = {}, {}
    grid = np.linspace(10, 100, 121)
    h = (np.eye(5)[:-1]+np.eye(5)[1:])/2
    for period, early in (("full", False), ("early", True)):
        rows, _, _ = prepare(eligible, early)
        at, baseline = tensors(rows, ids)
        na, ya, ssa = directional.sufficient(at)
        bflat = baseline.reshape(len(ids), 4, -1)
        bmean = np.nanmean(bflat, -1)
        observed = ya-bmean[..., None]
        variance = np.nanvar(at, -1, ddof=1)/na+np.nanvar(bflat, -1, ddof=1)[..., None]/np.isfinite(bflat).sum(-1)[..., None]
        data[period] = dict(at=at, baseline=baseline, n=na, mean=ya, sse=ssa,
                            observed=observed, error=np.sqrt(variance), baseline_mean=bmean)
    for name, early, rolling, shape in CONFIGS:
        run = json.loads((OUT / f"{name}_run.json").read_text())
        assert run["definition_sha256"] == definition_hash()
        runs.append(dict(model=name, gate=run["gate"], divergences=run["divergences"],
                         max_rhat=run["max_rhat"], min_bulk_ess=run["min_bulk_ess"], min_tail_ess=run["min_tail_ess"]))
        e = pd.read_csv(OUT / f"{name}_effects.csv")
        e["gate"] = run["gate"]
        effects.append(e)
        simple.append(pd.read_csv(OUT / f"{name}_simple_contrasts.csv"))
        parameter_tables.append(pd.read_csv(OUT / f"{name}_participant_parameters.csv"))
        period = "early" if early else "full"
        observed = data[period]
        with np.load(LOCAL / f"{name}_draws.npz") as saved:
            arrays = {q: saved[q].reshape(-1, len(ids), 4) for q in
                ("midpoint_cm", "width_cm", "sharpness_per_cm", "amplitude", "corrected_intercept", "baseline_mean")}
            expected = 1000*(saved["corrected_curve"].reshape(-1, len(ids), 4, 5).mean(0)+arrays["baseline_mean"].mean(0)[..., None])
            assert (arrays["amplitude"] > 0).all()
            if shape == "visible95":
                assert (special.expit((10-arrays["midpoint_cm"])/arrays["width_cm"]) <= .05+1e-12).all()
                assert (special.expit((100-arrays["midpoint_cm"])/arrays["width_cm"]) >= .95-1e-12).all()
            for quantity, a in arrays.items():
                q = np.quantile(a.mean(1), [.025, .5, .975], axis=0)
                for c, cell in enumerate(CELL_NAMES):
                    cohort.append(dict(model=name, cell=cell, quantity=quantity,
                                       median=q[1, c], ci_low=q[0, c], ci_high=q[2, c]))
            for i, pid in enumerate(ids):
                for c, cell in enumerate(CELL_NAMES):
                    n, y, sse, mu = (observed["n"][i, c], observed["mean"][i, c],
                                     observed["sse"][i, c], expected[i, c])
                    total = np.sum(sse+n*(y-n@y/n.sum())**2)
                    r2_trial = 1-np.sum(sse+n*(y-mu)**2)/total if total > 0 else np.nan
                    def r2(actual, prediction):
                        denominator = np.sum((actual-actual.mean())**2)
                        return 1-np.sum((actual-prediction)**2)/denominator if denominator > 0 else np.nan
                    quality.append(dict(model=name, participant_id=pid, cell=cell, n_AT=int(n.sum()),
                        trial_R2=r2_trial, five_mean_R2=r2(y, mu), rolling_mean_R2=r2(h@y, h@mu),
                        midpoint_median=np.median(arrays["midpoint_cm"][:, i, c]),
                        midpoint_interval_width=np.ptp(np.quantile(arrays["midpoint_cm"][:, i, c], [.025, .975])),
                        midpoint_probability_in_range=np.mean((arrays["midpoint_cm"][:, i, c] >= 10) & (arrays["midpoint_cm"][:, i, c] <= 100)),
                        full_parameter_gate=run["gate"]))
            # Plot ribbons use balanced, evenly spaced draws; all tabular intervals use all draws.
            selected = np.linspace(0, len(arrays["midpoint_cm"])-1, min(1200, len(arrays["midpoint_cm"])), dtype=int)
            display[name] = {q: a[selected] for q, a in arrays.items()}
    effects = pd.concat(effects, ignore_index=True)
    pd.DataFrame(runs).to_csv(OUT / "all_runs.csv", index=False)
    effects.to_csv(OUT / "all_effects.csv", index=False)
    pd.concat(simple, ignore_index=True).to_csv(OUT / "all_simple_contrasts.csv", index=False)
    pd.concat(parameter_tables, ignore_index=True).to_csv(OUT / "all_participant_parameters.csv", index=False)
    pd.DataFrame(cohort).to_csv(OUT / "cohort_parameters.csv", index=False)
    quality = pd.DataFrame(quality)
    quality.to_csv(OUT / "fit_quality.csv", index=False)
    quality_summary = quality.groupby("model").agg(cells=("cell", "size"),
        trial_R2_ge_05=("trial_R2", lambda a: int((a >= .5).sum())),
        five_mean_R2_ge_05=("five_mean_R2", lambda a: int((a >= .5).sum())),
        rolling_R2_ge_05=("rolling_mean_R2", lambda a: int((a >= .5).sum())),
        median_midpoint_interval_cm=("midpoint_interval_width", "median"))
    quality_summary.to_csv(OUT / "fit_quality_summary.csv")
    gates = {r["model"]: r["gate"] for r in runs}

    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False, "pdf.fonttype": 42})
    colors = ["#215A8E", "#387C9B", "#B24C22", "#D37824"]
    main_name = "full_roll_visible95"
    primary = display[main_name]
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), sharex=True, sharey=True)
    norm_records = []
    for c, ax in enumerate(axes.flat):
        m, w = primary["midpoint_cm"].mean(1)[:, c], primary["width_cm"].mean(1)[:, c]
        curves = special.expit((grid-m[:, None])/w[:, None])
        low, median, high = np.quantile(curves, [.025, .5, .975], axis=0)
        m0, w0 = np.median(m), np.median(w)
        plugin = special.expit((grid-m0)/w0)
        ax.fill_between(grid, low, high, color=colors[c], alpha=.18)
        ax.plot(grid, plugin, color=colors[c], lw=2.5)
        ax.axvline(m0, color=colors[c], lw=.8, ls="--")
        ax.axhline(.5, color="#999999", lw=.7, ls=":")
        ax.text(.03, .95, f"Mean midpoint {m0:.1f} cm", transform=ax.transAxes, va="top")
        ax.set(title=CELL_NAMES[c], xlim=(10, 100), ylim=(-.03, 1.03))
        for d, x in enumerate(grid):
            norm_records.append(dict(model=main_name, cell=CELL_NAMES[c], distance_cm=x,
                median_parameter_sigmoid=plugin[d], interval_low=low[d], interval_high=high[d]))
    fig.suptitle("Local filtering + rolling averages: assumed sigmoid geometry")
    fig.supxlabel("Physical distance (cm)", y=.08)
    fig.supylabel("Unit-amplitude model component")
    gate_label = "Full-model convergence gate passed." if gates[main_name] else "Full-model convergence gate FAILED; this display is provisional."
    fig.text(.5, .018, gate_label+"\nVisible S and 5–95% endpoints inside 10–100 cm are prior constraints. This is not normalized observed RT.\n"
        "Line: sigmoid at median cohort-mean parameters; band: 95% interval for that function from 1,200 balanced draws.", ha="center", fontsize=8)
    fig.tight_layout(rect=(.025, .13, 1, .95))
    fig.savefig(OUT / "sigmoid_curves.png", dpi=180)
    fig.savefig(OUT / "sigmoid_curves.pdf")
    plt.close(fig)
    write_csv(OUT / "normalized_mean_parameter_curves.csv", norm_records)

    styles = [("raw_broad", "Broad / raw", "#777777", "--"), ("roll_broad", "Broad / rolling", "#243C58", "-"),
              ("raw_visible95", "Visible S / raw", "#8C4EA5", "--"), ("roll_visible95", "Visible S / rolling", "#B24C22", "-")]
    group_curves = {}
    for name, sub in display.items():
        group_curves[name] = response(sub, grid).mean(1)
    fig, axes = plt.subplots(2, 4, figsize=(17, 8), sharex=True)
    for r, period in enumerate(("full", "early")):
        for c, ax in enumerate(axes[r]):
            raw = data[period]["observed"][:, c]
            ax.errorbar(X, raw.mean(0), yerr=stats.sem(raw, axis=0)*stats.t.ppf(.975, len(ids)-1), fmt="o", color="#222222", ms=3, label="Unsmoothed means")
            roll = raw@h.T
            ax.plot(h@X, roll.mean(0), "s", color="#CF7900", ms=4, label="Adjacent averages")
            for suffix, label, color, line in styles:
                values = group_curves[period+"_"+suffix][:, c]
                ax.plot(grid, values.mean(0), line, color=color, lw=1.5,
                        label=label+(" *" if not gates[period+"_"+suffix] else ""))
            ax.axhline(0, color="#BBBBBB", lw=.7)
            ax.set(title=CELL_NAMES[c]+(" / all blocks" if period == "full" else " / blocks 1–3"),
                   xlim=(10, 100), xlabel="Distance (cm)", ylabel="AT − Baseline (ms)")
    axes[0, 0].legend(fontsize=7)
    axes[1, 0].legend(fontsize=7)
    fig.suptitle("Unsmoothed observations, rolling averages and expected RT responses")
    fig.text(.5, .012, "Equal participant weight; error bars are 95% intervals across people. Rolling markers are displayed at pair midpoints.\n"
        "Rolling likelihoods average the model at the original distances and account for overlap. * Failed full-model convergence gate: provisional.\n"
        "Shared direction and the visible-S geometry are model assumptions.", ha="center", fontsize=8)
    fig.tight_layout(rect=(0, .06, 1, .95))
    fig.savefig(OUT / "observed_RT.png", dpi=170)
    fig.savefig(OUT / "observed_RT.pdf")
    plt.close(fig)

    atlas_pages = []
    with PdfPages(OUT / "individual_curves.pdf") as pdf:
        for i, pid in enumerate(ids):
            for period in ("full", "early"):
                fig, axes = plt.subplots(4, 2, figsize=(12, 14))
                for c in range(4):
                    ax, norm_ax = axes[c//2, c % 2], axes[2+c//2, c % 2]
                    raw, err = data[period]["observed"][i, c], data[period]["error"][i, c]
                    ax.errorbar(X, raw, yerr=err, fmt="o", color="#222222", ms=3, lw=.7, label="Raw means ± SE")
                    ax.plot(h@X, h@raw, "s", color="#CF7900", ms=4, label="Adjacent means")
                    for suffix, label, color, line in styles:
                        sub = {q: a[:, i, c] for q, a in display[period+"_"+suffix].items()}
                        expected = response(sub, grid)
                        ax.plot(grid, expected.mean(0), line, color=color, lw=1.3,
                                label=label+(" *" if not gates[period+"_"+suffix] else ""))
                        m, w = np.median(sub["midpoint_cm"]), np.median(sub["width_cm"])
                        norm_ax.plot(grid, special.expit((grid-m)/w), line, color=color, lw=1.4, label=label)
                        if suffix == "roll_visible95":
                            lo, hi = np.quantile(special.expit((grid-sub["midpoint_cm"][:, None])/sub["width_cm"][:, None]), [.025, .975], axis=0)
                            norm_ax.fill_between(grid, lo, hi, color=color, alpha=.12)
                    ax.axhline(0, color="#AAAAAA", lw=.7)
                    ax.set(title=CELL_NAMES[c], xlim=(10, 100), xlabel="Distance (cm)", ylabel="AT − Baseline (ms)")
                    norm_ax.axhline(.5, color="#AAAAAA", ls=":", lw=.7)
                    norm_ax.set(title=CELL_NAMES[c]+" / model geometry", xlim=(10, 100), ylim=(-.03, 1.03), xlabel="Distance (cm)", ylabel="Unit-amplitude component")
                axes[0, 0].legend(fontsize=7)
                fig.suptitle(f"{pid} — {'all six blocks' if period == 'full' else 'first three blocks of EACH intervention'}\nAdded local SD filtering; raw and covariance-aware rolling fits", fontsize=13)
                fig.text(.5, .014, "Top: expected RT functions and unsmoothed observations. Rolling markers are at pair midpoints for display only.\n"
                    "Bottom: sigmoid at marginal median parameters, not normalized observations; red/purple visible-S geometry is imposed by priors.\n"
                    "Intervals use 1,200 balanced draws for plotting. * Failed full-model convergence gate: provisional. All tables use every retained draw.", ha="center", fontsize=8)
                fig.tight_layout(rect=(0, .065, 1, .94))
                pdf.savefig(fig)
                atlas_pages.append(dict(page=len(atlas_pages)+1, participant_id=pid, period=period))
                if pid == "P000" and period == "full":
                    fig.savefig(OUT / "individual_example.png", dpi=140)
                plt.close(fig)
    write_csv(OUT / "atlas_pages.csv", atlas_pages)

    predictions = pd.read_csv(OUT / "held_distance_predictions.csv")
    assert len(predictions) == 2400
    targets = ["held_distance_cm", "participant_id", "cell"]
    raw_targets = predictions[predictions.model == "global_raw"].set_index(targets).sort_index()
    for name in ("local_raw", "local_roll"):
        check = predictions[predictions.model == name].set_index(targets).sort_index()
        np.testing.assert_allclose(check[["n_target", "observed_AT_ms"]], raw_targets[["n_target", "observed_AT_ms"]], atol=0)
    by_fold = predictions.groupby(["model", "held_distance_cm"]).agg(
        RMSE_ms=("error_ms", lambda a: np.sqrt(np.mean(a*a))),
        log_predictive_score=("block_log_predictive_density", "sum"),
        gate=("prediction_gate", "all")).reset_index()
    by_fold.to_csv(OUT / "prediction_by_distance.csv", index=False)
    pred_summary = predictions.groupby("model").agg(RMSE_ms=("error_ms", lambda a: np.sqrt(np.mean(a*a))),
        log_predictive_score=("block_log_predictive_density", "sum"), all_predictive_gates=("prediction_gate", "all"))
    pred_summary.to_csv(OUT / "prediction_summary.csv")
    differences = []
    for name in ("local_raw", "local_roll"):
        check = predictions[predictions.model == name].set_index(targets).sort_index()
        difference = (check.error_ms**2-raw_targets.error_ms**2).groupby("participant_id").mean()
        interval = stats.t.interval(.95, len(difference)-1, loc=difference.mean(), scale=stats.sem(difference))
        differences.append(dict(model=name, reference="global_raw", delta_MSE_ms2=difference.mean(),
            approximate_low=interval[0], approximate_high=interval[1],
            all_predictive_gates=bool(check.prediction_gate.all() and raw_targets.prediction_gate.all())))
    write_csv(OUT / "prediction_differences.csv", differences)
    shape_effects = effects[effects.quantity.isin(["midpoint_cm_effect", "sharpness_per_cm_effect"])]
    supported = shape_effects[(shape_effects.ci_low > 0) | (shape_effects.ci_high < 0)]
    counts = pd.read_csv(OUT / "retained_counts.csv")
    fatigue = pd.read_csv(OUT / "time_trend_tests.csv")
    registered = pd.DataFrame(json.loads((OUT / "registered_RT_models.json").read_text()))
    report = f'''# Trial distributions, local SD filtering, fatigue and rolling-average rerun

## Scope and implementation

All three requested tips are implemented as a fixed exploratory sensitivity. Original
data, cleaning, browser analysis, earlier fits and manuscript are preserved. The
pre-fit specification is `specification.json`; implementation is in
`analysis/trial_cleaning/`. Primary inference retains the same 40 participants,
excluding both unresolved P011/P033 recordings. All 42 people remain in the raw
trial audit. No threshold or model was selected by sigmoid yield or significance.

**Main current adjustment:** the interventions occurred consecutively in one
session. Early blocks within an intervention do not control accumulated time.
The five subsequent joint session-time fits and their matched validation are
reported in **`SESSION_RESULTS.md`**. The eight fits below are the unadjusted
cleaning/trial-count reference battery, not a substitute for that global control.

1. Every eligible hit is shown, with per-distance violins, raw points and z-score
   labels in `every_trial_distributions.pdf` (42 pages). `trial_audit.csv` retains
   every released trial, eligibility, both filter decisions and standardized values.
2. The original participant-wide inclusive mean ±2.5 sample-SD rule is recomputed
   within each subset. One additional pass within person × condition × phase ×
   distance × trial type follows. Singleton/zero-SD cells remain. No visual tuning,
   iterative deletion or new 100/200-ms cutoff was added. For n≤8, the internally
   standardized sample-SD z score cannot exceed 2.5; limited deletion is expected.
3. Fewer trials means blocks 1–3 of EACH intervention, preserving four cells. Both
   filters are recomputed on that subset. This is a sensitivity, not proof that
   later responses are invalid. Fatigue diagnostics use the full-session cleaned
   RTs and all original performance denominators.
4. Adjacent smoothing creates four overlapping means from five distances. The
   SAME operator H acts on observations and model responses, with covariance
   sigma² H diag(1/n) Hᵀ. Within-distance SSE still informs residual scale. Overlap
   is not independent replication; the alternating mean contrast is lost. Rolling
   points are plotted at pair midpoints but the likelihood does not substitute
   f(pair midpoint) for the average of f(original distances).

Retained counts:

{table(counts[counts.cohort == 'primary40'])}

`distance_distributions.csv` preserves cell counts/means/SDs, including missing
early Baseline distance cells. Independent Baseline is pooled within participant,
condition and phase, retaining uncertainty. Missing nominal-delay Baseline cells
do not imply missing pooled calibration; the original timing concern remains.

## Bayesian parameter comparisons

Eight joint models cross full/early, raw/rolling and broad/visible95 geometry.
Nuisance priors and the two shape hierarchies match the preserved reference
analyses. Broad shapes allow transitions outside the measured range. Visible95
forces a 5–95% transition inside 10–100 cm and a sharpness floor; those are prior
assumptions. Both have positive amplitudes by construction, not discovered signs.

{table(pd.DataFrame(runs))}

Every main parameter contrast (95% equal-tail credible interval):

{table(shape_effects[['model','quantity','term','posterior_median','ci_low','ci_high','probability_positive','gate']])}

**{len(supported)}/{len(shape_effects)}** main parameter intervals exclude zero.
These are joint finite-cohort posterior contrasts, not ANOVAs on pooled point
estimates. A nonzero interval is conditional on its likelihood, priors, selection
and diagnostic status; it is not automatic physiological validation. Model failures
remain inconclusive. Population coefficients, all simple effects and response
contrasts remain exported separately. No multiplicity correction or joint-model
Bayes factor was introduced. Priors and numerical budgets were fixed before fits.

## Does fitting look better?

{table(quality_summary.reset_index())}

The three R² columns count cells out of 160. They use the posterior expected AT
response, retaining baseline level in the trial-scale calculation. Trial-level,
five-mean and four-rolling-mean R² have different denominators and information;
they are not interchangeable success rates. R²≥.5 is descriptive. Smoothing a few
means can improve apparent fit while losing shape information. None of these
counts replaces held-out prediction, parameter recovery or the historical .7 gate.

`sigmoid_curves.png` displays the representative mean-parameter geometry of
full_roll_visible95. It is an explicitly imposed S, not normalized observed data.
`observed_RT.png` retains unsmoothed means and all eight expected RT functions.
`individual_curves.pdf` contains 80 pages: full and early analyses for every
retained person, with raw observations and both model geometries. All tabular
intervals use every draw; plot ribbons use 1,200 balanced draws.

## Fatigue, trial count and registered RT questions

Time slopes control the five distance categories and are measured per observed
intervention span. Early/late comparisons use the full-session selection and
the same available distances. Variability is residual SD within distance, not
dispersion caused merely by distance differences. SD is undefined for singleton
distance groups without residual degrees of freedom; relevant tests report their
complete-person count and excluded IDs, without excluding these people from PPS
models. Miss/catch rates include original trials rather than only retained RTs.

Average participant time diagnostics, all unadjusted p values:

{table(fatigue[fatigue.term == 'Average'][['quantity','complete_participants','estimate','ci_low','ci_high','p']])}

The complete 36 contrasts are in `time_trend_tests.csv`. A time trend can reflect
practice, stimulus/block differences or fatigue; these observational checks do not
establish its cause or authorize selective later-trial deletion. `time_course.png`
shows recorded block trends. The early sensitivity is reported regardless of its
R² or effect estimates.

Recomputed registered-form raw-AT mixed tests (exploratory new-cleaning sensitivities):

{table(registered[['dataset','name','status','lr','df','p']])}

These test numeric-SOA interactions, not sigmoid boundary/sharpness. Corrected
response-level paired contrasts, permutation/rank/sign checks and whole-person resampling
are in `response_tests.csv`; they remain separate from parameter inference.

## Matched held-distance validation

Fifteen broad-model refits compare global-only/raw, global+local/raw and
global+local/rolling across five held distances. ALL held-distance AT outcomes
are excluded BEFORE calculating either cutoff or smoothing. Baseline remains
independent calibration. Each method predicts the SAME initially eligible raw
held-out hits; no test-RT outlier exclusion is learned from the targets.
RMSE compares the 800 held participant × cell × distance mean RTs per method,
with equal weight per cell. It is not individual-trial RMSE. The log score
integrates the raw held hits jointly within each cell and then sums over cells.

{table(by_fold)}

{table(pred_summary.reset_index())}

All final predictive gates: **{bool(predictions.prediction_gate.all())}**. If any
gate fails, the associated scores and complete aggregate comparison are
provisional; every failed fold remains exported. Full-parameter gates and
prediction gates are distinct. These targets include hits that earlier full-data
trimming might remove, so their scores must not be compared numerically with
older already-trimmed validation targets. Participant-paired MSE-difference
intervals are approximate diagnostics conditional on these fitted folds, not
independent replications, formal noninferiority tests or model Bayes factors.
Early/visible95 candidates were not separately cross-validated.

## Interpretation and remaining work

The requested plotting, local filtering, smaller-trial sensitivity, rolling
likelihood and condition rerun are computed. Stronger-looking R² or guaranteed
sigmoid geometry alone does not establish usable physiological parameters. The
Gaussian likelihood conditions on selected observations; it does not jointly model
the random two-stage filtering process. Repeated whole-pipeline Bayesian coverage,
false-positive calibration, new recovery studies and questionnaire follow-ups were
not run here. Previous recovery/identification limits and source timing/linkage
gaps persist. The broader Q10 scientific goal remains open until its evidence
criteria are satisfied. No manuscript or browser integration was performed.

## Reproduction

Use `analysis/baseline_effects/requirements.txt` and one BLAS/OpenMP thread:

```bash
python -m unittest discover -s analysis/trial_cleaning -p 'test_*.py' -v
python analysis/trial_cleaning/diagnostics.py
python analysis/trial_cleaning/run.py fit
python analysis/trial_cleaning/run.py cv
python analysis/trial_cleaning/session_time.py fit
python analysis/trial_cleaning/session_time.py cv
python analysis/trial_cleaning/session_report.py
python analysis/trial_cleaning/report.py
python analysis/trial_cleaning/validate_outputs.py
```

Completed fits/CV resume by model/fold and verify model-definition hashes.
Resume assumes the same released inputs; the final validator checks their hashes
against the preserved reference manifests as well as the new package.
`source_amendments.json` records a validation-driver ESS API fix and verifies that
all preprocessing/model definitions stayed identical; original source stamps are retained.
Large local
posterior draws are hashed and reproducible but not committed. The manifest hashes
inputs, dependencies, reference results and public artifacts; `trial_cleaning_results.zip`
contains the public package. Native computation is separate from browser execution.
'''
    (OUT / "RESULTS.md").write_text(report)
    package()
    print("Exported eight unadjusted models, eighty curve pages and fifteen matched predictive folds.", flush=True)


def package():
    inputs = {str(p.relative_to(ROOT)): sha(p) for p in (ROOT/"data/raw").glob("*.csv")}
    source_files = [ROOT/"analysis/trial_cleaning"/n for n in ("run.py", "diagnostics.py", "report.py", "test_pipeline.py",
        "session_time.py", "session_report.py", "test_session_time.py", "validate_outputs.py")]
    source_files += [ROOT/p for p in ("analysis/visible_sigmoid/fit.py", "analysis/directional_sigmoid/model.py",
        "analysis/baseline_effects/baseline_effects.py", "analysis/baseline_effects/joint_pps.py", "workbook/paper_analysis.py",
        "workbook/inference.py", "analysis/baseline_effects/requirements.txt")]
    references = [ROOT/p/"manifest.json" for p in ("results/baseline_effects", "results/directional_sigmoid", "results/visible_sigmoid")]
    manifest = dict(input_sha256=inputs, source_sha256={str(p.relative_to(ROOT)): sha(p) for p in source_files},
        reference_sha256={str(p.relative_to(ROOT)): sha(p) for p in references},
        local_trace_sha256={p.name: sha(p) for p in LOCAL.glob("*_draws.npz")},
        artifacts_sha256={p.name: sha(p) for p in OUT.iterdir() if p.is_file() and p.name not in ("manifest.json", "trial_cleaning_results.zip")},
        execution="native Python; not browser-validated", python=sys.version.split()[0],
        packages={name: version(name) for name in ("numpy", "scipy", "pandas", "matplotlib",
            "pymc", "pytensor", "nutpie", "arviz")},
        native_only=True, manuscript_updated=False, raw_data_changed=False)
    write_json(OUT / "manifest.json", manifest)
    with zipfile.ZipFile(OUT / "trial_cleaning_results.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(OUT.iterdir()):
            if path.is_file() and path.suffix != ".zip":
                archive.write(path, path.name)
    print("Updated the complete public archive and source/input/trace hashes.", flush=True)


if __name__ == "__main__":
    {"run": main, "package": package}[sys.argv[1] if len(sys.argv) > 1 else "run"]()
