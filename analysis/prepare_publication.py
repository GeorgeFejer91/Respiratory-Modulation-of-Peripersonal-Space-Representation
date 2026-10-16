"""Promote an actual browser download into the paper; never rerun its analysis.

Usage: python analysis/prepare_publication.py path/to/browser-results.zip
Requires the workbook environment only to render the report's figure data.
"""

import argparse
import json
import shutil
import sys
import zipfile
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "workbook"))
from publication_report import figure_bytes


def promote(path):
    with zipfile.ZipFile(path) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        report = json.loads(archive.read("analysis_results.json"))
        if report["runtime"]["execution"] != "browser Pyodide":
            raise ValueError("Publication input must be an actual browser run.")
        for name, expected in manifest["artifact_sha256"].items():
            if sha256(archive.read(name)).hexdigest() != expected:
                raise ValueError(f"Artifact hash mismatch: {name}")
        for name, expected in manifest["source_sha256"].items():
            if sha256((ROOT / "data/raw" / name).read_bytes()).hexdigest() != expected:
                raise ValueError(f"Input data changed: {name}")
        for name, expected in manifest["code_sha256"].items():
            if sha256((ROOT / "workbook" / name).read_bytes()).hexdigest() != expected:
                raise ValueError(f"Analysis code changed: {name}; rerun in the browser.")
        target = ROOT / "results/browser-analysis"
        target.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target / "browser-results.zip")
        for name in archive.namelist():
            if "/" not in name and name != "retained_rt_trials.csv" and not name.endswith(".svg"):
                (target / name).write_bytes(archive.read(name))
        for name, measure, paper_name in (
            ("raw_at_curves.svg", "raw_at", "study5_current_rt_soa_curves.png"),
            ("same_label_facilitation.svg", "same_label_at_minus_baseline", "study5_delay_matched_facilitation.png"),
            ("descriptive_sigmoids.svg", "descriptive_sigmoids", "study5_descriptive_sigmoids.png"),
            ("sigmoid_extrapolation.svg", "sigmoid_extrapolation", "study5_sigmoid_extrapolation.png"),
            ("pps_shape.svg", "pps_shape", "study5_pps_shape.png"),
            ("sigmoid_geometry.svg", "sigmoid_geometry", "study5_sigmoid_geometry.png"),
            ("questionnaire_summary.svg", "questionnaire_summary", "study5_questionnaires.png"),
        ):
            (ROOT / "figures" / name).write_bytes(archive.read(name))
            (ROOT / "manuscript/figures" / paper_name).write_bytes(figure_bytes(report, measure, "png"))
        (ROOT / "figures/questionnaire_associations.svg").write_bytes(archive.read("questionnaire_associations.svg"))
    write_text(report)
    print("Promoted verified browser report, tables, figures and manuscript statistics.")


def shape_results(d):
    a=d["shape_audit"]
    scores={row["family"]:row["outer_rmse_ms"] for row in a["nested_prediction"]["scores"]}
    pvalues=", ".join(f"{row['p_holm']:.3f}" for row in a["raw_curvature"]["rows"])
    intervals="; ".join(f"[{row['midpoint_cm_conditional_bootstrap_low']:.2f}, {row['midpoint_cm_conditional_bootstrap_high']:.2f}]" for row in a["visible_parameters"])
    table="\n".join(f"{r['condition']} & {r['phase']} & {r['midpoint_cm']:.2f} & {r['width_cm']:.2f} & {r['midpoint_slope_ms_per_cm']:.4f} & {'Yes' if r['width_at_bound'] else 'No'} \\\\" for r in a["visible_parameters"])
    return rf"""\subsection{{Measured-range PPS shape and predictive support}}

The stronger exploratory goal required a visible transition within the observed range, rather than a sigmoid that is nearly linear over that range. None of the {d['candidate_count']} original pipelines met all measured-range criteria in all four curves. An additional {len(a['visible_candidates'])} pipelines imposed those criteria, while {len(a['linear_candidates'])} linear pipelines received the same extraction and smoothing options. The lowest-scoring constrained method used 10\% per-tail trimming, a Gaussian bandwidth of 13.5~cm, increasing isotonic projection and separate logistic widths. Its tuning RMSE was {a['visible_tuning_rmse_ms']:.3f}~ms, versus {a['linear_tuning_rmse_ms']:.3f}~ms for the tuned linear family. These are method-selection scores.

\begin{{table}}[htbp]
\centering\small
\begin{{tabular}}{{llrrrr}}
\hline
Condition & Phase & Midpoint (cm) & Width (cm) & Slope (ms/cm) & Width floor \\
\hline
{table}
\hline
\end{{tabular}}
\caption{{Imposed-shape descriptive estimates. A visible transition is enforced by the model constraints; it is not an empirical finding. Conditional intervals and constraint-hit frequencies are provided in the companion.}}
\end{{table}}

Three of the four width estimates reached the 4.5-cm minimum, and the Control/Inhale midpoint reached the upper sampling constraint. Conditional 95\% midpoint intervals, in table order, were {intervals}~cm. These intervals are truncated by the shape restrictions and exclude flat resamples; they do not establish stable physiological boundaries.

Six outer participant folds repeated the complete pipeline selection inside each training set, using five inner participant folds crossed with omitted positions. Outer RMSE was {scores['logistic']:.3f}~ms for the original sigmoid family, {scores['visible']:.3f}~ms for the constrained family, {scores['linear']:.3f}~ms for tuned lines and {scores['constant']:.3f}~ms for a constant. The constrained curve's small advantage over tuned lines did not extend to the constant benchmark. These exploratory estimates address new participants at the known design positions; overlapping training sets and post hoc family development preclude a confirmatory model-superiority claim.

A separate unsmoothed participant-level test projected each five-position curve onto the three contrasts orthogonal to an intercept and distance. Hotelling tests of these nonlinear components gave Holm-adjusted $p$ values of {pvalues}, in table order. This test concerns any nonlinearity, not specifically a sigmoid, and assumes multivariate-normal participant contrasts. Failure to detect curvature does not prove linearity. Together, the predictive results and active constraints leave the data-supported PPS-shape goal unresolved, despite obtaining four visibly S-shaped model approximations.

\begin{{figure}}[htbp]
\centering
\includegraphics[width=\textwidth]{{study5_pps_shape.png}}
\caption{{\textbf{{Measured-range PPS-shaped sensitivity.}} Common linear axes preserve between-curve scale comparisons. Raw means (open circles), trimmed summaries (black points), fitted curves and the tuned line are each centered on their corresponding five-position mean; subtracting a constant cannot create curvature. Bands resample participants jointly, refit the constrained model and recenter each draw. They condition on the selected extraction and shape restrictions. Asterisks mark active width or midpoint constraints. All five observed positions remain visible.}}
\label{{study5:fig:pps_shape}}
\end{{figure}}

\begin{{figure}}[htbp]
\centering
\includegraphics[width=\textwidth]{{study5_sigmoid_geometry.png}}
\caption{{\textbf{{Fitted shape separated from empirical support.}} The vertical axis normalizes each fitted asymptotic RT change to 0--1. Colored lines show the imposed-shape family; dashed gray lines retain the original best-score family. This diagnostic displays model geometry only, without observations or empirical uncertainty on this scale. It shows why the original curves did not display both plateaus within the measured range, and how explicit constraints produce an S shape. It is not additional evidence for that shape in the measurements.}}
\label{{study5:fig:sigmoid_geometry}}
\end{{figure}}
"""


def questionnaire_results(q):
    s=q["spatial"]
    rows="\n".join(f"{r['label']} & {r['mean']:.2f} & {r['sd']:.2f} & {r['alpha']:.3f} & [{r['alpha_ci_low']:.3f}, {r['alpha_ci_high']:.3f}] \\\\" for r in q["scales"])
    nominal=[r for r in q["associations"] if r["p"] is not None and r["p"]<.05]
    labels={r["field"]:r["label"] for r in q["scales"]}
    labels.update(spfrref_control_ordinal="Control spatial rating", spfrref_viscereality_ordinal="Viscereality spatial rating",
                  spfrref_change_direction="spatial rating-change direction", rt_slope_interaction="raw-RT slope interaction")
    details="; ".join(rf"{labels[r['x']]} with {labels[r['y']]} ($\rho={r['rho']:.3f}$, pointwise 95\% CI $[{r['ci_low']:.3f}, {r['ci_high']:.3f}]$, unadjusted $p={r['p']:.4f}$)" for r in nominal)
    rho=[r["rho"] for r in q["associations"] if r["rho"] is not None]
    order="; ".join(f"{r['condition_order']}: {r['higher']}/{r['ties']}/{r['lower']}" for r in s["order_counts"])
    return rf"""\subsection{{MAIA-2 and spatial frame of reference}}

This post hoc extension analysed {q['maia_complete']} complete MAIA-2 records and {s['n_pairs']} complete spatial-frame pairs. All {q['scoring']['matches']} stored MAIA-2 subscale scores matched independent recomputation from the 37 items, including reverse scoring; there were {q['scoring']['mismatches']} mismatches. The participant with missing questionnaires remained in the behavioural cohort. Table~\ref{{study5:tab:maia}} reports all eight dimensions and internal-consistency uncertainty. These are self-reported interoceptive dimensions, not objective interoceptive accuracy. The lower alpha estimates for Noticing and Emotional Awareness warrant caution; no items were removed to improve reliability.

\begin{{table}}[htbp]
\centering\small
\begin{{tabular}}{{lrrrr}}
\hline
Dimension & Mean & SD & Alpha & 95\% alpha interval \\
\hline
{rows}
\hline
\end{{tabular}}
\caption{{MAIA-2 subscale scores (0--5), each with $n={q['maia_complete']}$. Intervals are pointwise percentile intervals from 2,000 participant-bootstrap draws. Alpha is a sample internal-consistency diagnostic, not a test of dimensionality or validity.}}
\label{{study5:tab:maia}}
\end{{table}}

Viscereality spatial-frame ratings were higher than Control for {s['higher']} participants, lower for {s['lower']}, and tied for {s['ties']} (Fig.~\ref{{study5:fig:questionnaires}}). The two-sided exact sign test gave $p={s['p']:.5f}$. Among the {s['non_ties']} non-ties, the higher-rating proportion was {s['higher_fraction_non_ties']:.3f}, exact 95\% CI $[{s['higher_fraction_ci_low']:.3f}, {s['higher_fraction_ci_high']:.3f}]$. Paired dominance across all {s['n_pairs']} pairs was {s['paired_dominance']:.3f}, percentile 95\% CI $[{s['dominance_ci_low']:.3f}, {s['dominance_ci_high']:.3f}]$. Both condition medians were category D. Higher/equal/lower counts by condition order were {order}. These descriptive order counts do not rule out period or carryover effects. The administered pictogram key is absent from the release, so a higher A--H code is not assigned an allocentric or egocentric interpretation. This exploratory ordinal difference does not establish a PPS-boundary change or its mechanism.

All 33 fixed rank associations were estimated from 41 complete participant pairs each, including 24 MAIA--spatial comparisons. Spearman coefficients ranged from {min(rho):.3f} to {max(rho):.3f}. No multiple-testing correction was applied; {len(nominal)} of 33 comparisons had unadjusted $p<.05$: {details}. Higher Trusting scores accompanied higher Viscereality codes and a more positive direction of Viscereality--Control change. Change direction records lower, unchanged or higher ratings, without measuring the magnitude of the shift. These related spatial outcomes do not provide independent replication. The companion exports all 33 coefficients, pointwise paired-person bootstrap intervals and unadjusted permutation $p$ values. The behavioural correlate was the raw-RT Condition $\times$ Phase SOA-slope interaction; it was not an individual sigmoid midpoint or width. The reporting choice was changed after inspecting these results. The findings remain exploratory: multiple comparisons, small sample size, ties, uncertain measurement reliability and unadjusted confounding limit inference. Boundary-related questionnaire associations remained unestimated under the original fit gate.

\begin{{figure}}[htbp]
\centering
\includegraphics[width=\textwidth]{{study5_questionnaires.png}}
\caption{{\textbf{{Questionnaire coverage and paired spatial ratings.}} Left: individual recomputed MAIA-2 subscale scores, means and pointwise 95\% participant-bootstrap intervals. Right: counts for all Control/Viscereality category pairs; vertical position above the matching-category diagonal indicates a higher Viscereality code. All 41 paired records are represented. A--H preserve the recorded ordering without assuming equal psychological distances or a verified anchor direction.}}
\label{{study5:fig:questionnaires}}
\end{{figure}}

"""


def write_text(r):
    c = r["cohort"]
    models = r["mixed_models"]
    primary = models[0]
    b = primary["coefficients"][-1]
    slopes = r["participant_slope_interaction"]
    supp = r["supplementary_contrasts"]
    raw_anova = next(a for a in r["repeated_measures_anova"] if a["measure"] == "raw AT" and a["effect"] == "Condition × Phase × SOA")
    sigmoid = r["sigmoid_summary"][0]
    means = r["sigmoid_summary"][1]
    d = r["descriptive_sigmoids"]

    def p(value):
        return "<.001" if value < .001 else "=" + f"{value:.3f}".lstrip("0")

    def interval(row):
        return f"[{row['ci_low']:.2f}, {row['ci_high']:.2f}]"

    abstract = rf"""Peripersonal space (PPS) is often inferred from tactile reaction time during an approaching sound. We tested whether instructed respiratory phase changed this SOA-dependent response differently in breath-coupled virtual reality (Viscereality) and Control. The released cohort comprised {c['participants_input']} participants and {c['retained_at']:,} retained audio--tactile hit trials. The planned Condition $\times$ Phase $\times$ SOA mixed-model interaction was not detected, $\chi^{{2}}(1)={primary['lr']:.3f}$, $p{p(primary['p'])}$; categorical-SOA and partial-session-exclusion sensitivities agreed. Audio--tactile responses were {abs(supp[3]['estimate']):.1f}~ms faster than tactile-only Baseline responses on average, but equal nominal delay labels do not establish matched cue times. None of {sigmoid['cells']} participant-by-condition-by-phase trial-level sigmoid fits met the planned $R^{{2}}\geq .70$ threshold. The maximum saturated five-SOA trial-level $R^{{2}}$ ceiling was {sigmoid['max_trial_r2_ceiling']:.3f}, precluding this threshold for any curve of SOA alone. Boundary, sharpness, and boundary-related questionnaire inference therefore remained unestimated. The full data-supported pipeline, diagnostics, and downloadable results run in a marimo browser companion. These data do not demonstrate the predicted Viscereality-specific respiratory modulation; confidence intervals and source-timing and respiratory-compliance limits constrain interpretation.
"""
    # LaTeX thousands separators must not introduce punctuation into math.
    abstract = abstract.replace(f"{c['retained_at']:,}", f"{c['retained_at']:,}".replace(",", "{,}"))
    abstract = abstract.replace("Boundary, sharpness, and boundary-related questionnaire inference therefore remained unestimated.",
        "Participant-boundary and boundary-related questionnaire inference therefore remained unestimated. "
        "A separate post hoc comparison of 800 uniformly processed sigmoid and linear pipelines produced four explicit shape-constrained approximations. "
        "Their visible S shapes were imposed; nested participant prediction did not improve on a constant, and unsmoothed curvature tests did not establish nonlinearity. Midpoint and steepness estimates remain assumption-dependent descriptions.")
    results = rf"""\section{{Results}}

\subsection{{Released cohort and response quality}}

The analysis used all {c['participants_input']} participants in the released tables ({c['gender']['female']} women, {c['gender']['male']} men; mean age {c['age_mean']:.1f} years, SD {c['age_sd']:.1f}, range {c['age_min']:.0f}--{c['age_max']:.0f}). Twenty-one completed each condition order. There were 17{{,}}114 observed trials of 17{{,}}136 planned slots: 10{{,}}068 Audio--Tactile, 5{{,}}033 Baseline, and 2{{,}}013 Catch trials. Forty-one sessions were complete; one partial session lacked 22 trials but supplied all 20 Condition $\times$ Phase $\times$ SOA cells. There were 24 Catch false alarms, and no participant exceeded the 30\% Catch exclusion rule. Low-hit-rate flags are reported without adding an exclusion criterion.

Among hit-labelled trials, {c['missing_hit_rt']} RTs were missing ({c['missing_at_hit_rt']} Audio--Tactile and 25 Baseline). These trials remained in hit-rate denominators. The participant-wide mean $\pm$ 2.5-SD trim removed {c['removed_2_5_sd']} of 13{{,}}694 recorded hit RTs, retaining 8{{,}}916 Audio--Tactile and 4{{,}}396 Baseline RTs. Adding a 200-ms minimum after trimming removed no further observations. Forty-one participants had the full questionnaire measures and one had PPS measures only.

\subsection{{Primary interaction and sensitivity analyses}}

Adding the Condition $\times$ Phase $\times$ numeric-SOA term to the trial-level random-intercept ML model did not improve fit, $\chi^{{2}}(1)={primary['lr']:.3f}$, $p{p(primary['p'])}$. With symmetric Condition/Phase coding and standardized SOA, its estimate was {b['estimate']:.2f}~ms per SOA SD (SE {b['se']:.2f}; 95\% model-based Wald CI ${interval(b)}$). This interval permits effects in either direction and does not establish equivalence.

The categorical-SOA comparison gave $\chi^{{2}}(4)={models[2]['lr']:.2f}$, $p{p(models[2]['p'])}$. Excluding the partial session left 41 participants (numeric $p{p(models[4]['p'])}$; categorical $p{p(models[5]['p'])}$). The Control-only Phase $\times$ SOA test was also not detected (numeric $p{p(models[1]['p'])}$; categorical $p{p(models[3]['p'])}$). Allowing a participant random SOA slope yielded $p{p(models[-1]['p'])}$. The participant-cell repeated-measures three-way interaction was $F(4,164)={raw_anova['F']:.2f}$, Greenhouse--Geisser $\epsilon={raw_anova['epsilon_GG']:.3f}$, corrected $p{p(raw_anova['p_GG'])}$.

The equal-participant five-SOA slope contrast was {slopes['estimate']:.2f}~ms per SOA SD, 95\% CI ${interval(slopes)}$, $t(41)={slopes['t']:.3f}$, $p{p(slopes['p'])}$. The Monte Carlo sign-flip test used 19{{,}}999 draws with a fixed seed ($p{p(slopes['sign_flip']['p'])}$). Its exploratory paired JZS factor was $\mathrm{{BF}}_{{10}}={slopes['bf10_jzs']:.3f}$ ($\mathrm{{BF}}_{{01}}={slopes['bf01_jzs']:.2f}$). This normal-likelihood participant model is distinct from the registered mixed model; the slope distribution departed from normality (Shapiro--Wilk $p{p(slopes['shapiro_p'])}$).

"""
    labels = ["Raw RT", "Log RT", "Time-on-task-adjusted RT", "Hit probability (log odds)"]
    results += "The exploratory participant-cluster-robust models gave the following three-way terms. Normal Wald intervals use the documented finite-cluster sandwich correction.\n\n\\begin{center}\n\\begin{tabular}{lrrr}\nModel & Estimate & 95\\% CI & $p$ \\\\\n\\hline\n"
    for label, model in zip(labels, r["cluster_models"]):
        row = next(q for q in model["coefficients"] if q["term"] == "Condition × Phase × SOA")
        results += rf"{label} & {row['estimate']:.3f} & ${interval(row)}$ & ${p(row['p']).lstrip('=')}$ \\" + "\n"
    results += "\\end{tabular}\n\\end{center}\n\n"
    results += rf"""The missing-hit-RT stress tests imputed only the {c['missing_at_hit_rt']} Audio--Tactile hits lacking RTs, then recomputed trimming. Median-only imputation gave $p{p(r['missing_rt_stress'][0]['p'])}$; signed $-200$ and $+200$~ms scenarios gave $p{p(r['missing_rt_stress'][3]['p'])}$ and $p{p(r['missing_rt_stress'][4]['p'])}$, respectively. These specified scenarios do not recover missed-trial RTs or identify the missingness mechanism. Full model coefficients, scaling, diagnostics, intermediate tables, and all stress scenarios are in the companion's downloadable report.

\begin{{figure}}[htbp]
\centering
\includegraphics[width=\textwidth]{{study5_current_rt_soa_curves.png}}
\caption{{\textbf{{Audio--Tactile RT by SOA, Condition, and instructed respiratory phase in the 42-person cohort.}} Each point averages participant means with equal person weight; all cells contain 42 participants. Intervals are pointwise 95\% $t$ intervals across participant means. Longer SOAs correspond to nearer nominal auditory positions. Lines connect means and are not sigmoid fits; inference comes from the stated models.}}
\label{{study5:fig:current_rt_soa}}
\end{{figure}}

\subsection{{Sigmoid viability and descriptive PPS shape}}

None of {sigmoid['cells']} trial-level participant $\times$ Condition $\times$ Phase sigmoid fits reached $R^{{2}}\geq .70$ (median $R^{{2}}={sigmoid['median_r2']:.3f}$; maximum {sigmoid['max_r2']:.3f}). The largest saturated five-SOA trial-level $R^{{2}}$ ceiling was {sigmoid['max_trial_r2_ceiling']:.3f}. Thus no deterministic sigmoid of these SOAs could reach .70 in any cell, independent of the particular nonlinear optimizer or parameter bounds. Sigmoids improved unpenalized in-sample RMSE over a line in {sigmoid['sigmoid_better_rmse']}/{sigmoid['cells']} cells; this does not establish stable boundaries.

Fitting four parameters to five SOA means instead yielded {means['r2_pass_cells']}/{means['cells']} qualifying cells and {means['all_four_r2_participants']} participants passing all four cells, with none having four bound-free fits. Such fits have one residual degree of freedom and were not used to rescue the failed trial-level gate. Replacing approximate registered distances with trajectory-implied positions left the trial-level pass count at zero. Parameter-bound diagnostics and group fits are supplied descriptively. Participant midpoint/sharpness contrasts and their MAIA-2 or pictographic associations were not estimable under the planned fit gate.

"""
    results += rf"""\subsection{{Four uniformly estimated descriptive sigmoid curves}}

A separate post hoc analysis obtained nonflat sigmoid approximations for all four Condition $\times$ Phase groups using a single extraction, smoothing, and fitting rule (Figure~\ref{{study5:fig:descriptive_sigmoids}}). All 42 participants contributed all five positions with equal person weight. The search compared {d['candidate_count']} pipelines spanning mean, median, trimmed-mean and winsorized summaries; Gaussian local-constant/local-linear and tricube local-linear smoothing; curvature penalization; isotonic projection; and separate versus shared logistic widths. The original trial-level gate above was retained as a distinct analysis.

The lowest crossed participant/position prediction score selected 20\% per-tail winsorization within participant cells, Gaussian local-constant smoothing with bandwidth 0.5 of the nominal distance span (45~cm), and separate logistic widths. This same pipeline was applied to all four curves. The tuning RMSE was {d['selected_tuning_rmse_ms']:.3f}~ms, compared with {d['validation']['linear_shape_rmse_ms']:.3f}~ms for a line and {d['validation']['constant_shape_rmse_ms']:.3f}~ms for a constant. The fixed prediction target was each held-out person's raw mean at the omitted position minus that person's raw mean across the other four positions. The small advantage over a line is a post-selection descriptive score, not independent evidence of sigmoid superiority.

For $f(d)=a+A\operatorname{{expit}}((d-m)/s)$, $m$ is the half-amplitude midpoint, $s$ is the logistic width, and the RT derivative at the midpoint is $A/(4s)$. Smaller widths indicate sharper normalized transitions; RT slopes additionally depend on amplitude. Width is not a Gaussian standard deviation. Estimates refer to the registration's approximate distance labels.

\begin{{center}}
\small
\begin{{tabular}}{{lrrr}}
Condition / phase & $m$ (cm) & $s$ (cm) & $f'(m)$ (ms/cm) \\
\hline
"""
    for row in d["parameters"]:
        results += rf"{row['condition']} / {row['phase']} & {row['midpoint_cm']:.2f} & {row['width_cm']:.2f} & {row['midpoint_slope_ms_per_cm']:.4f} \\" + "\n"
    results += "\\end{tabular}\n\\end{center}\n\n"
    midpoint_intervals = "; ".join(f"[{row['midpoint_cm_conditional_bootstrap_low']:.1f}, {row['midpoint_cm_conditional_bootstrap_high']:.1f}]" for row in d["parameters"])
    widths = ", ".join(f"{row['transition_10_90_cm']:.1f}" for row in d["parameters"])
    flat = ", ".join(f"{100*row['bootstrap_flat_fraction']:.1f}\\%" for row in d["parameters"])
    bounds = ", ".join(f"{100*row['bootstrap_midpoint_bound_fraction']:.1f}\\%" for row in d["parameters"])
    contrast = next(row for row in d["comparisons"] if row["contrast"] == "Condition × Phase" and row["parameter"] == "midpoint_cm")
    phase_contrasts = [next(row for row in d["comparisons"] if row["contrast"] == label and row["parameter"] == "midpoint_cm") for label in ("Control Inhale − Exhale", "Viscereality Inhale − Exhale")]
    reference = d["sensitivity"]
    alternative = ", ".join(f"{row['midpoint_cm']:.1f}" for row in reference["robust_reference_parameters"])
    trajectory = ", ".join(f"{row['midpoint_cm']:.1f}" for row in reference["trajectory_axis_parameters"])
    expanded = ", ".join(f"{row['midpoint_cm']:.1f}" for row in reference["expanded_bounds_parameters"])
    results += rf"""The 1{{,}}000 whole-participant bootstrap resamples preserved each person's four curves together and refitted smoothing and the sigmoid model. Conditional 95\% percentile intervals for the four midpoints, in table order, were {midpoint_intervals}~cm. Flat fits occurred in {flat} of resamples; midpoint-bound hits, including flat draws, occurred in {bounds}. Midpoint and width intervals exclude flat draws, for which these parameters are unidentified, and condition on the selected pipeline. They do not include uncertainty from choosing among 320 methods and should not be treated as unconditional coverage guarantees.

Descriptively, the Inhale-minus-Exhale midpoint difference was {phase_contrasts[0]['estimate']:.2f}~cm in Control and {phase_contrasts[1]['estimate']:.2f}~cm in Viscereality. Their difference was {contrast['estimate']:.2f}~cm, conditional bootstrap interval [{contrast['conditional_bootstrap_low']:.2f}, {contrast['conditional_bootstrap_high']:.2f}]~cm, based on {contrast['nonflat_draws']} resamples with all contributing curves nonflat. No confirmatory test was assigned to this post hoc group-parameter contrast. The report includes all paired midpoint, width and RT-slope comparisons.

The fitted 10--90\% transition spans were {widths}~cm, each exceeding the sampled 90-cm span. Consequently, the complete S shapes and their asymptotes depend on extrapolation. A fixed alternative using 20\% trimmed means and a narrower Gaussian bandwidth of 0.3 yielded midpoints {alternative}~cm, with tuning RMSE {reference['robust_reference_tuning_rmse_ms']:.3f}~ms. Applying the selected rule to trajectory-implied coordinates yielded {trajectory}~cm; expanding the midpoint/width/amplitude search bounds yielded {expanded}~cm. These method and coordinate sensitivities limit a literal boundary interpretation. All candidate scores and parameter estimates, including edge and flat solutions, remain available in the companion.

\begin{{figure}}[htbp]
\centering
\includegraphics[width=\textwidth]{{study5_descriptive_sigmoids.png}}
\caption{{\textbf{{Four uniformly estimated descriptive sigmoids.}} Open gray circles are raw participant-weighted means; black points are participant-weighted winsorized cell summaries; crosses show Gaussian-kernel-smoothed summaries. Solid curves are logistic approximations fitted to the five smoothed design points, with no interpolated observations added to the fit. Vertical dotted lines mark the fitted midpoints. Bands are pointwise participant-bootstrap percentiles conditional on the selected pipeline, including flat resamples. The full search, parameter uncertainty, and model extrapolations are available in the browser companion.}}
\label{{study5:fig:descriptive_sigmoids}}
\end{{figure}}

{shape_results(d)}

\subsection{{Baseline, sound, and order diagnostics}}

Across ten supplementary paired contrasts, Holm adjustment was applied as one family. Overall Audio--Tactile minus within-Condition/Phase mean Baseline RT was {supp[3]['estimate']:.2f}~ms, 95\% CI ${interval(supp[3])}$, unadjusted $p{p(supp[3]['p'])}$, Holm $p{p(supp[3]['p_holm'])}$. Baseline Inhale minus Exhale RT was {supp[1]['estimate']:.2f}~ms, 95\% CI ${interval(supp[1])}$, unadjusted $p{p(supp[1]['p'])}$, Holm $p{p(supp[1]['p_holm'])}$. The Baseline Condition $\times$ Phase contrast was {supp[2]['estimate']:.2f}~ms, 95\% CI ${interval(supp[2])}$, unadjusted $p{p(supp[2]['p'])}$, Holm $p{p(supp[2]['p_holm'])}$. These checks neither establish phase invariance nor provide adjusted evidence of a Baseline phase difference.

The far-minus-near Audio--Tactile difference was {supp[6]['estimate']:.2f}~ms, 95\% CI ${interval(supp[6])}$; the analogous Baseline nominal-label difference was {supp[7]['estimate']:.2f}~ms, 95\% CI ${interval(supp[7])}$. Their difference was {supp[8]['estimate']:.2f}~ms, 95\% CI ${interval(supp[8])}$. Far Audio--Tactile minus Baseline was {supp[4]['estimate']:.2f}~ms using the Condition/Phase reference and {supp[5]['estimate']:.2f}~ms using the same nominal SOA label (Holm $p{p(supp[5]['p_holm'])}$ for the latter). Equal labels do not establish cue-time matching; these differences cannot isolate auditory proximity or remove temporal expectancy.

Pink-minus-white Audio--Tactile RT was {supp[9]['estimate']:.2f}~ms, 95\% CI ${interval(supp[9])}$. Among the {r['four_noise_friedman']['n']} participants with all four noise types available, the exploratory Friedman test gave $\chi^{{2}}(3)={r['four_noise_friedman']['chi2']:.2f}$, $p{p(r['four_noise_friedman']['p'])}$. This availability-defined subset cannot be assigned to an acquisition version from the released tables. The two order subgroups each contained 21 participants; their slope contrasts were {r['order_sensitivities'][0]['estimate']:.2f}~ms, 95\% CI ${interval(r['order_sensitivities'][0])}$, and {r['order_sensitivities'][1]['estimate']:.2f}~ms, 95\% CI ${interval(r['order_sensitivities'][1])}$. These descriptive subgroup results do not establish order equivalence.

\begin{{figure}}[htbp]
\centering
\includegraphics[width=\textwidth]{{study5_delay_matched_facilitation.png}}
\caption{{\textbf{{Exploratory Audio--Tactile minus Baseline RT paired by nominal SOA label.}} Points average 42 participant differences within Condition $\times$ Phase $\times$ label. Negative values indicate faster Audio--Tactile responses. Baseline has no sound; matching labels does not establish equal trial-relative tactile-cue time. Intervals are pointwise 95\% $t$ intervals across participants. Lines connect means and carry no boundary inference.}}
\label{{study5:fig:delay_matched_facilitation}}
\end{{figure}}

\subsection{{Reproducibility and evidence limits}}

All reported behavioral computations were executed in the marimo browser companion with Pyodide, Python {r['runtime']['python']}, NumPy {r['runtime']['numpy']}, SciPy {r['runtime']['scipy']}, and Matplotlib {r['runtime']['matplotlib']}. The archived browser download records input, code, and output SHA-256 hashes. Native reference checks independently verified random-intercept ML fits, cluster-robust linear and binomial coefficients/uncertainty, repeated-measures $F$ statistics, and JZS quadrature. Additional native references checked questionnaire alpha through its covariance identity, the exact ordinal sign test and interval, and rank correlations. Every questionnaire result was also compared across native and browser runtimes. A failed or unavailable check is distinguished from a computed null result.

The released CSVs do not contain waveforms, belt recordings, acquisition-version labels, collection dates, or the private provenance needed to identify two historically documented RT-onset variants. The browser analysis therefore does not rerun waveform timing, measured respiratory compliance, pilot-date classification, version-specific contrasts, or that source-definition exclusion. Historical source audits remain historical evidence, rather than new 42-person verification.
"""
    q=r["questionnaires"];s=q["spatial"]
    nominal=sum(a["p"] is not None and a["p"]<.05 for a in q["associations"])
    abstract=abstract.replace("The full data-supported pipeline", f"An exploratory paired ordinal comparison in {s['n_pairs']} participants found higher spatial-frame codes under Viscereality (exact sign-test $p={s['p']:.4f}$). Questionnaire associations were reported without multiple-testing correction; {nominal} of 33 comparisons had unadjusted $p<.05$, including two positive Trusting--spatial associations. The full data-supported pipeline")
    results=results.replace("\\subsection{Reproducibility and evidence limits}",questionnaire_results(q)+"\\subsection{Reproducibility and evidence limits}")
    for name, content in (("abstract", abstract), ("results", results)):
        (ROOT / "manuscript/sections" / f"{name}.tex").write_text(content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("browser_zip", type=Path)
    parser.add_argument("--preprint-pdf", type=Path, help="Archive the already compiled, visually checked draft PDF.")
    args = parser.parse_args()
    promote(args.browser_zip)
    if args.preprint_pdf:
        pdf = args.preprint_pdf.read_bytes()
        if not pdf.startswith(b"%PDF-"):
            raise ValueError("Expected a compiled PDF.")
        (ROOT / "results/study5-preprint.pdf").write_bytes(pdf)
        sources = sorted(p for p in (ROOT / "manuscript").rglob("*") if p.suffix in (".tex", ".bib", ".png"))
        provenance = {"status": "Analysis draft for author review", "pdf_sha256": sha256(pdf).hexdigest(),
            "manuscript_sha256": {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in sources},
            "browser_zip_sha256": sha256(args.browser_zip.read_bytes()).hexdigest()}
        (ROOT / "results/preprint_manifest.json").write_text(json.dumps(provenance, indent=2) + "\n")
