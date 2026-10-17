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
from participant_report import diagnostics, contrast_diagnostics, repeated_primary, repeated_rows


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
            ("spatial_change.svg", "spatial_change", "study5_spatial_change.png"),
            ("participant_diagnostics.svg", "participant_diagnostics", "study5_participant_diagnostics.png"),
            ("participant_example.svg", "participant_example", "study5_participant_example.png"),
            ("remaining_robustness.svg", "remaining_robustness", "study5_remaining_robustness.png"),
            ("parameter_repeated_measures.svg", "parameter_repeated_measures", "study5_parameter_repeated_measures.png"),
            ("spatial_pps.svg", "spatial_pps", "study5_spatial_pps.png"),
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
    labels={r["field"]:r["label"] for r in q["scales"]}
    delta=q["delta_associations"][:8]
    direction={r["x"]:r for r in q["associations"] if r["y"]=="spfrref_change_direction"}
    models={(r["field"],r["model"]):r for r in q["moderation"]}
    delta_rows="\n".join(rf"{labels[r['x']]} & {r['rho']:.3f} & [{r['ci_low']:.3f}, {r['ci_high']:.3f}] & {r['p']:.4f} & {direction[r['x']]['rho']:.3f} & {direction[r['x']]['p']:.4f} \\" for r in delta)
    model_rows=[]
    for r in delta:
        a,b=(models[(r["x"],m)] for m in ("unadjusted","order_adjusted"))
        model_rows.append(rf"{labels[r['x']]} & {a['beta']:.3f} & {a['p']:.4f} & {a['hc3_p']:.4f} & {b['beta']:.3f} & {b['p']:.4f} & {b['hc3_p']:.4f} \\")
    model_rows="\n".join(model_rows)
    trust=delta[-1];trust_direction=direction["maia2_trusting"]
    a,b=(models[("maia2_trusting",m)] for m in ("unadjusted","order_adjusted"))
    noticing,noticing_order=(models[("maia2_noticing",m)] for m in ("unadjusted","order_adjusted"))
    ancillary=q["delta_associations"][-1];desc=s["delta_descriptives"]
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

MAIA-2 was administered once before the experiment and spatial-frame ratings after each intervention, as confirmed by the project owner. The main follow-up outcome was the signed numerical code difference $\Delta=\mathrm{{Viscereality}}-\mathrm{{Control}}$, irrespective of presentation order. Mean $\Delta$ was {desc['mean']:.3f} category steps (SD {desc['sd']:.3f}), median {desc['median']:.0f}, interquartile range {desc['q1']:.0f}--{desc['q3']:.0f}, and range {desc['min']:.0f} to {desc['max']:.0f}. These are post-intervention condition differences, not changes from a pre-intervention spatial baseline; their numerical magnitudes assume comparable category steps.

\begin{{table}}[htbp]
\centering\small
\begin{{tabular}}{{lrlrrr}}
\hline
Dimension & $\rho_\Delta$ & 95\% interval & $p_\Delta$ & $\rho_\mathrm{{dir}}$ & $p_\mathrm{{dir}}$ \\
\hline
{delta_rows}
\hline
\end{{tabular}}
\caption{{Pre-experiment MAIA-2 and signed spatial change, $n=41$. Main analyses correlate numerical $\Delta$ with each dimension; direction-only ($-1,0,+1$) correlations are ordinal sensitivities. All $p$ values are unadjusted two-sided permutation values; intervals are pointwise paired-participant bootstrap intervals.}}
\label{{study5:tab:spatial_delta}}
\end{{table}}

Trusting was positively associated with numerical $\Delta$: $\rho={trust['rho']:.3f}$, pointwise 95\% CI $[{trust['ci_low']:.3f},{trust['ci_high']:.3f}]$, unadjusted permutation $p={trust['p']:.4f}$ (Table~\ref{{study5:tab:spatial_delta}}; Fig.~\ref{{study5:fig:spatial_delta}}). The direction-only sensitivity was also positive ($\rho={trust_direction['rho']:.3f}$, $p={trust_direction['p']:.4f}$). The other seven numerical-delta correlations had $p>.05$; this does not establish absence of associations. The ancillary correlation between numerical $\Delta$ and the raw-RT Condition $\times$ Phase SOA-slope interaction was $\rho={ancillary['rho']:.3f}$, pointwise 95\% CI $[{ancillary['ci_low']:.3f},{ancillary['ci_high']:.3f}]$, $p={ancillary['p']:.4f}$. The RT contrast is not a PPS boundary.

\begin{{table}}[htbp]
\centering\small
\begin{{tabular}}{{lrrrrrr}}
\hline
& \multicolumn{{3}}{{c}}{{MAIA only}} & \multicolumn{{3}}{{c}}{{With presentation order}} \\
Dimension & $b$ & $p$ & $p_\mathrm{{HC3}}$ & $b$ & $p$ & $p_\mathrm{{HC3}}$ \\
\hline
{model_rows}
\hline
\end{{tabular}}
\caption{{Condition $\times$ MAIA moderation, fitted through participant-level numerical $\Delta$, $n=41$ per model. Slopes are code steps per one MAIA point. Ordinary two-sided $t$ inference is equivalent to the repeated-measures interaction $F=t^2$; HC3 provides approximate heteroskedasticity-sensitive inference. Residual degrees of freedom are 39 and 38. All $p$ values are unadjusted; the companion exports all intervals, $F$ statistics and model diagnostics.}}
\label{{study5:tab:spatial_moderation}}
\end{{table}}

The Trusting interaction slope was {a['beta']:.3f} code steps per MAIA point, $F(1,{a['df']})={a['F']:.3f}$, $p={a['p']:.4f}$. Its HC3 interval was $[{a['hc3_ci_low']:.3f},{a['hc3_ci_high']:.3f}]$, $p={a['hc3_p']:.4f}$. Accounting for presentation order gave $b={b['beta']:.3f}$, $F(1,{b['df']})={b['F']:.3f}$, $p={b['p']:.4f}$; HC3 95\% CI $[{b['hc3_ci_low']:.3f},{b['hc3_ci_high']:.3f}]$, $p={b['hc3_p']:.4f}$. Noticing depended on the uncertainty estimator: ordinary $p={noticing['p']:.4f}$ and {noticing_order['p']:.4f}, versus HC3 $p={noticing['hc3_p']:.4f}$ and {noticing_order['hc3_p']:.4f}, without/with order respectively. This less consistent pattern is reported alongside its non-detection in the main rank analysis (Table~\ref{{study5:tab:spatial_moderation}}).

These are exploratory associations and trait-moderation estimates, not mediation or independent replications. The analysis direction was chosen after inspecting earlier results, all intervals are pointwise, and no multiple-testing correction was applied. The 33 earlier absolute-rating, direction and behavioural associations remain available as supplementary audit outputs, alongside the nine new delta correlations and 16 moderation fits. Small sample size, uncertain reliability, category-spacing assumptions and possible confounding/carryover limit inference. Boundary-related questionnaire associations remain unestimated under the original fit gate.

\begin{{figure}}[htbp]
\centering
\includegraphics[width=\textwidth]{{study5_spatial_change.png}}
\caption{{\textbf{{Pre-experiment traits and post-intervention spatial change.}} Left: all eight MAIA-2 correlations with numerical $\Delta$ and pointwise bootstrap 95\% intervals. Right: Condition $\times$ MAIA slopes with and without presentation order and HC3 95\% intervals. Higher $\Delta$ means higher recorded Viscereality codes relative to Control; the administered pictogram direction is unverified.}}
\label{{study5:fig:spatial_delta}}
\end{{figure}}

\begin{{figure}}[htbp]
\centering
\includegraphics[width=\textwidth]{{study5_questionnaires.png}}
\caption{{\textbf{{Questionnaire coverage and paired spatial ratings.}} Left: individual recomputed MAIA-2 subscale scores, means and pointwise 95\% participant-bootstrap intervals. Right: counts for all Control/Viscereality category pairs; vertical position above the matching-category diagonal indicates a higher Viscereality code. All 41 paired records are represented. A--H preserve the recorded ordering without assuming equal psychological distances or a verified anchor direction.}}
\label{{study5:fig:questionnaires}}
\end{{figure}}

"""


def individual_results(r):
    scores={a['family']:a['outer_rmse_ms'] for a in r['prediction']['scores']}
    summary=diagnostics(r)
    stat=lambda model,metric:next(a for a in summary if a['model']==model and a['parameter']==metric and a['scenario']=='sigmoid')
    separate=stat('individual_plateaus','midpoint_cm');shared=stat('shared_plateaus','midpoint_cm')
    stable=[sum(a['normalization_stable'] for a in r[k]) for k in ('parameters','shared_parameters')]
    labels=[('maia2_noticing','Noticing'),('maia2_not_distracting','Not Distracting'),('maia2_not_worrying','Not Worrying'),
            ('maia2_attention_regulation','Attention Regulation'),('maia2_emotional_awareness','Emotional Awareness'),
            ('maia2_self_regulation','Self-Regulation'),('maia2_body_listening','Body Listening'),('maia2_trusting','Trusting'),('spfrref_delta','Spatial code difference')]
    table=[]
    for field,label in labels:
        values=[]
        for key in ('associations','shared_associations'):
            for metric in ('midpoint_cm','normalized_steepness_per_cm','midpoint_slope_ms_per_cm'):
                a=next(a for a in r[key] if a['x']==field and a['y']==metric+'_condition_delta')
                values.append(f"{a['rho']:.2f} ({a['p']:.3f})")
        table.append((label,values))
    rows='\n'.join(label+' & '+' & '.join(values[:3])+r' \\' for label,values in table)
    shared_rows='\n'.join(label+' & '+' & '.join(values[3:])+r' \\' for label,values in table)
    return rf"""\subsection{{Individual sigmoid proxies and plateau normalization}}

The additional exploratory extension obtained {r['curve_count']} four-cell sigmoid approximations from {r['participants']} participant records. Uniform selection among 84 candidates chose mean extraction, Gaussian local-constant smoothing with a 27-cm bandwidth, and a shape penalty of 4. Separate plateaus were primary; sharing both plateaus across each person's four curves was a sensitivity. Expected increasing direction occurred in {sum(a['expected_direction'] for a in r['parameters'])}/168 primary fits; decreasing responses were retained. The visible S shape was imposed by the measured-range constraints, so numerical parameter availability does not establish physiological boundaries.

Nested omitted-position prediction RMSE was {scores['visible']:.3f}~ms for the visible family, {scores['broad']:.3f} for broad sigmoids, {scores['linear']:.3f} for lines, {scores['constant']:.3f} for a constant, and {scores['shared_plateaus']:.3f} for shared plateaus (Fig.~\ref{{study5:fig:individual_diagnostics}}). The shared-plateau improvement over a constant was only {scores['constant']-scores['shared_plateaus']:.3f}~ms. These descriptive scores do not test the significance of differences between overlapping folds.

Normalizing by each fitted lower plateau and absolute amplitude gives common asymptotes 0 and 1 while preserving midpoint and width. Raw observations were not clipped. The plateau-separation bootstrap interval excluded zero for only {stable[0]}/168 separate-plateau fits and {stable[1]}/168 shared-plateau fits; the latter represent ten people with four repeated flags. All 42 shared-model point fits converged under the specified alternating solver, without a guarantee of global optimality. The 42-page downloadable atlas shows all four raw-RT profiles with standard errors above their normalized model geometry, with recording-linkage flags.

Midpoint split-half rank reliability was low: medians {separate['median_split_half_rho']:.3f} and {shared['median_split_half_rho']:.3f} for separate and shared plateaus, respectively, across ten splits and four cells. Corresponding median conditional midpoint interval widths were {separate['median_interval_width']:.2f} and {shared['median_interval_width']:.2f}~cm. With known 80-ms sigmoids and cell-specific baselines, median midpoint recovery correlations across 30 simulations were {separate['median_recovery_rho']:.3f} and {shared['median_recovery_rho']:.3f}. Under shared-baseline simulated truth, shared-model midpoint recovery improved to {next(a['median_recovery_rho'] for a in summary if a['model']=='shared_plateaus' and a['parameter']=='midpoint_cm' and a['scenario']=='sigmoid_shared_plateaus'):.3f}. Width-derived steepness remained poorly recovered. These checks concern the stated simulations and within-session splits; they do not measure test--retest reliability or interval coverage.

Table~\ref{{study5:tab:individual_links}} gives all 27 main questionnaire associations for each model. Four primary or shared-model point-estimate tests had unadjusted $p<.05$, but all 54 refit-bootstrap intervals included zero. For example, the spatial-change/midpoint-change correlation moved from approximately zero under separate plateaus to $\rho=.331$ under shared plateaus. This model dependence and weak parameter reliability preclude a stable boundary association claim. Different nominal findings appeared for MAIA Not Distracting, Emotional Awareness and Attention Regulation across specifications; no finding was selected as the primary outcome after inspection. Both complete sets of 126 associations and three linkage-exclusion specifications are retained, yielding 1,008 unadjusted tests. Excluding both ambiguous records, or each separately, repeated RT-only method selection; the selected smoothing/penalty choices differed. Those sensitivity analyses cannot determine the correct recording mapping. All RT--questionnaire inference remains provisional until that linkage is resolved.

\begin{{table}}[htbp]
\centering\small
\begin{{tabular}}{{lrrr}}
\multicolumn{{4}}{{c}}{{Separate plateaus}} \\
Baseline trait / spatial change & Midpoint & Steepness & RT slope \\
\hline
{rows}
\hline
\multicolumn{{4}}{{c}}{{Shared plateaus}} \\
Baseline trait / spatial change & Midpoint & Steepness & RT slope \\
\hline
{shared_rows}
\end{{tabular}}
\caption{{Exploratory Spearman correlations of baseline MAIA-2 or spatial-code difference with Viscereality--Control parameter differences (equal phase weights; $n=41$). Cells give $\rho$ (unadjusted pairing-permutation $p$). Parameters come from four fitted curves per person. All refit-bootstrap intervals include zero; complete intervals, cell-specific correlations and recording-exclusion sensitivities are in the companion. Full-release RT linkage is unresolved.}}
\label{{study5:tab:individual_links}}
\end{{table}}

\begin{{figure}}[htbp]
\centering
\includegraphics[width=\textwidth]{{study5_participant_diagnostics.png}}
\caption{{Individual-parameter audit. Prediction differences are small; midpoint intervals are wide and split-half reliability is low. The lower-right panel compares the same 27 main association estimates under the two plateau assumptions. Neither normalized appearance nor numerical fit availability establishes a reliable PPS boundary.}}
\label{{study5:fig:individual_diagnostics}}
\end{{figure}}

"""


def repeated_results(r):
    rows,label=repeated_primary(r["participant_sigmoids"])
    anova=[a for a in rows if a["predictor"]=="none"]
    moderators=[a for a in rows if a["predictor"]!="none" and a["effect"]=="Condition" and a["order_adjusted"] and a["predictor"]!="spfrref_change_direction"]
    significant=lambda a:a["p"] is not None and a["p"]<.05
    nonzero=lambda a:a["refit_ci_low"] is not None and (a["refit_ci_low"]>0 or a["refit_ci_high"]<0)
    def fmt(x):return "NA" if x is None else f"{x:.4g}"
    def interval(a):return f"[{fmt(a['refit_ci_low'])}, {fmt(a['refit_ci_high'])}]"
    model_names={"individual_plateaus":"Separate","shared_plateaus":"Shared"}
    metric_names={"midpoint_cm":"Midpoint","normalized_steepness_per_cm":"Sharpness"}
    effect_names={"Condition":"C","Phase":"P","Condition × Phase":r"C $\times$ P"}
    table="\n".join(f"{model_names[a['model']]} & {metric_names[a['parameter']]} & {effect_names[a['effect']]} & {fmt(a['F'])} & {fmt(a['p'])} & {interval(a)} \\\\" for a in anova)
    covariates=[]
    for a in moderators:
        if a["model"]!="shared_plateaus":continue
        other=next(b for b in moderators if b["model"]=="individual_plateaus" and b["parameter"]==a["parameter"] and b["predictor"]==a["predictor"])
        name=a["predictor"].replace("maia2_","").replace("spfrref_delta","Spatial change").replace("_"," ").title()
        covariates.append(f"{metric_names[a['parameter']]} & {name} & {fmt(a['estimate'])} & {fmt(a['p'])} & {interval(a)} & {interval(other)} \\\\")
    covtable="\n".join(covariates)
    exceptional=[a for a in repeated_rows(r["participant_sigmoids"]) if nonzero(a)]
    exceptions="; ".join(
        f"{model_names[a['model']]} plateaus, {metric_names[a['parameter']]}, {a['effect'].replace(' × ', ' by ')} by {a['predictor'].replace('maia2_','').replace('_',' ')}, "
        f"{a['cohort']}, {'with' if a['order_adjusted'] else 'without'} order adjustment: {interval(a)}"
        for a in exceptional) or "None"
    return rf"""\subsection{{Repeated-measures analysis of PPS midpoint and sharpness}}

The next exploratory question concerned all four fitted Condition $\times$ Phase profiles and their relationship to baseline MAIA-2 and post-intervention spatial change. The main presentation excludes both ambiguous recordings ({label}; {anova[0]['n']} behavioural records). Both plateau specifications remain reported; fitting methods were chosen from RT prediction without questionnaire outcomes. No multiple-testing correction was applied.

The 2$\times$2 ANOVA on point estimates yielded {sum(map(significant,anova))} of {len(anova)} conventional terms with $p<.05$ across midpoint and normalized sharpness (Table~\ref{{study5:tab:parameter_anova}}). However, {sum(map(nonzero,anova))} of their 95\% curve-refit intervals excluded zero. These two uncertainty calculations answer different conditional questions: the conventional ANOVA treats the estimated parameters as observed data, whereas hierarchical resampling re-estimates the curves and shared pooling. Small conventional $p$ values cannot overcome unstable fitted parameters.

\begin{{table}}[htbp]
\centering\small
\begin{{tabular}}{{lllrrl}}
Plateaus & Outcome & Effect & $F$ & $p$ & 95\% refit interval \\
\hline
{table}
\end{{tabular}}
\caption{{Exploratory parameter RM ANOVA. C denotes Viscereality minus Control, P denotes Inhale minus Exhale, and C $\times$ P is the difference of phase effects. Each $F$ has (1,{anova[0]['df2']}) df. Intervals describe the corresponding mean contrast in cm or normalized sharpness (cm$^{{-1}}$), not the $F$ statistic.}}
\label{{study5:tab:parameter_anova}}
\end{{table}}

With presentation order included, {sum(map(significant,moderators))} of {len(moderators)} Condition-moderation terms had conventional $p<.05$; {sum(map(nonzero,moderators))} curve-refit intervals excluded zero. Table~\ref{{study5:tab:parameter_covariates}} reports all eight MAIA-2 dimensions and spatial-code change for both outcomes. Covariate slopes describe how Viscereality--Control parameter change varies per score point. The spatial model compares changes measured in the same participants; it cannot establish that spatial experience caused a PPS change. MAIA-2 is a baseline trait and is not an intervention mediator.

\begin{{table}}[htbp]
\centering\scriptsize
\begin{{tabular}}{{llrrll}}
Outcome & Covariate & Shared $\beta$ & Shared $p$ & Shared refit interval & Separate refit interval \\
\hline
{covtable}
\end{{tabular}}
\caption{{Order-adjusted Condition $\times$ covariate terms. Each MAIA-2 dimension and spatial delta enters a separate continuous-covariate model. Coefficients use cm or cm$^{{-1}}$ per score point. The companion also reports ordinary/HC3 uncertainty, both order specifications, between-person means, Phase and three-way moderation, ordinal-direction sensitivity and every recording exclusion.}}
\label{{study5:tab:parameter_covariates}}
\end{{table}}

All 1,328 nominal ANOVA/ANCOVA terms across four linkage specifications and both plateau models were retained. Across that entire family, {len(exceptional)} refit intervals excluded zero: {exceptions}. These isolated sensitivity results were absent from the both-excluded primary presentation and do not establish a mapping-robust association. Hierarchical intervals used 500 curve-refitting resamples per specification; these condition on the earlier RT-selected method and cleaning and do not estimate selection-adjusted coverage. The previously near-zero change-score reliability remains a central limitation for interpreting questionnaire associations. A better-fitting numerical sigmoid is insufficient to identify a physiological boundary or establish questionnaire influence.

\begin{{figure}}[htbp]
\centering
\includegraphics[width=\textwidth]{{study5_parameter_repeated_measures.png}}
\caption{{Repeated-measures parameter analysis excluding both ambiguous records. Upper panels show the three within-person effects; lower panels show order-adjusted Condition moderation. Points and 95\% hierarchical curve-refit intervals retain both plateau models. Sharpness is $1/(4s)$ for logistic width $s$ in cm. These are fitted proxies with previously weak reliability.}}
\label{{study5:fig:parameter_repeated_measures}}
\end{{figure}}

"""


def spatial_results(r):
    p=r['participant_sigmoids'];cells,label=repeated_primary(p,'spatial_cell_associations')
    models,_=repeated_primary(p,'spatial_parameter_models');adjusted=[a for a in models if a['order_adjusted']]
    all_cells=repeated_rows(p,'spatial_cell_associations');all_models=repeated_rows(p,'spatial_parameter_models')
    def f(value):return 'NA' if value is None else f'{value:.4g}'
    def nonzero(a,lo,hi):return a[lo] is not None and (a[lo]>0 or a[hi]<0)
    table=[]
    for model,name in (('individual_plateaus','Separate'),('shared_plateaus','Shared')):
        for condition,phase in (('Control','Exhale'),('Control','Inhale'),('Viscereality','Exhale'),('Viscereality','Inhale')):
            selected=[next(a for a in cells if a['model']==model and a['condition']==condition and a['phase']==phase and a['metric']==metric)
                for metric in ('midpoint_cm','normalized_steepness_per_cm')]
            table.append(f"{name} & {condition}/{phase} & {selected[0]['rho']:.3f} & {selected[0]['p']:.3f} & {selected[1]['rho']:.3f} & {selected[1]['p']:.3f}"+r' \\')
    cell_table='\n'.join(table);table=[]
    for a in adjusted:
        if a['effect'] not in ('Mean across cells','Condition'):continue
        name='Separate' if a['model']=='individual_plateaus' else 'Shared'
        outcome='Midpoint' if a['parameter']=='midpoint_cm' else 'Sharpness'
        component='Between' if a['predictor']=='spfrref_mean' else 'Within'
        table.append(f"{name} & {outcome} & {component} & {f(a['estimate'])} & {f(a['p'])} & [{f(a['refit_ci_low'])}, {f(a['refit_ci_high'])}]"+r' \\')
    model_table='\n'.join(table)
    nominal_cells=sum(a['p'] is not None and a['p']<.05 for a in cells)
    nominal_models=sum(a['p'] is not None and a['p']<.05 for a in adjusted)
    nonzero_cells=sum(nonzero(a,'ci_low','ci_high') for a in all_cells)
    nonzero_models=sum(nonzero(a,'refit_ci_low','refit_ci_high') for a in all_models)
    reused=sum(a['predictor']=='spfrref_delta' for a in all_models)
    return rf"""\subsection{{Condition-matched spatial ratings and PPS parameters}}

This further post-results analysis matched each condition's spatial rating to that condition's Exhale and Inhale PPS proxies. The main presentation excluded both ambiguous recordings and used {cells[0]['n']} complete questionnaire records. Each cell association contained one observation per participant; the two phases sharing a spatial rating were not counted as independent people. Both plateau specifications and every recording sensitivity were retained without questionnaire-based retuning.

Across the {len(cells)} main condition-specific rank associations, {nominal_cells} had unadjusted $p<.05$ (Table~\ref{{study5:tab:spatial_pps_cells}}). All corresponding curve-refit intervals included zero (Fig.~\ref{{study5:fig:spatial_pps}}). These estimates do not establish a consistent association in any of the four condition/phase cells.

\begin{{table}}[htbp]
\centering\small
\begin{{tabular}}{{llrrrr}}
Plateaus & Condition/phase & Midpoint $\rho$ & $p$ & Sharpness $\rho$ & $p$ \\
\hline
{cell_table}
\end{{tabular}}
\caption{{Spatial ratings and PPS proxies from the same condition, $n={cells[0]['n']}$. All $p$ values are unadjusted two-sided pairing-permutation values. Hierarchical intervals refit the curves and retain uncertain pooling; the complete CSVs also include all recording sensitivities and valid-draw counts.}}
\label{{study5:tab:spatial_pps_cells}}
\end{{table}}

The within/between decomposition asked whether mean spatial ratings predicted overall PPS parameters or their phase contrast, and whether spatial-rating changes predicted the PPS condition or condition-by-phase contrasts. With presentation order included, {nominal_models}/{len(adjusted)} conventional coefficient tests had $p<.05$; every curve-refit interval included zero. Table~\ref{{study5:tab:spatial_pps_models}} presents mean-level and condition-change coefficients; phase-dependent associations are retained in the figure and complete tables. Within-change coefficients reproduce the earlier spatial-delta models and are not independent evidence.

\begin{{table}}[htbp]
\centering\small
\begin{{tabular}}{{lllrrl}}
Plateaus & Outcome & Spatial component & Slope & $p$ & 95\% refit interval \\
\hline
{model_table}
\end{{tabular}}
\caption{{Order-adjusted between-person level and within-person change associations. Slopes are cm or cm$^{{-1}}$ per spatial-code step. Each contrast regression uses one summary per person; ordinary tests condition on estimated PPS parameters. Both plateau models remain reported.}}
\label{{study5:tab:spatial_pps_models}}
\end{{table}}

The complete extension contains {len(all_cells)} cell correlations and {len(all_models)} coefficient records, including {reused} reused within-change coefficients, so {len(all_cells)+len(all_models)-reused} nominal tests were added. Across all cohorts and plateau models, {nonzero_cells}/{len(all_cells)} cell-association and {nonzero_models}/{len(all_models)} coefficient refit intervals excluded zero. Cell intervals used {min(a['bootstrap_valid'] for a in all_cells)}--{max(a['bootstrap_valid'] for a in all_cells)} valid resamples; undefined draws were counted. Numerical spatial means/differences assume comparable category steps, while cell-specific ranks and the earlier direction-only models provide ordinal sensitivities. The post-intervention timing, unresolved source mapping and poor PPS-parameter reliability preclude causal mediation or physiological-boundary claims. These uncertain associations do not establish absence of a relationship, and questionnaire scores were not used as cleaning criteria.

\begin{{figure}}[htbp]
\centering
\includegraphics[width=\textwidth]{{study5_spatial_pps.png}}
\caption{{\textbf{{Spatial experience and fitted PPS parameters.}} Upper panels show same-condition rank associations separately for all four Condition $\times$ Phase cells. Lower panels separate mean spatial level between people from spatial change within people, including their phase dependence and presentation-order adjustment. Points and 95\% hierarchical curve-refit intervals retain both plateau specifications. All observations are exploratory fitted proxies; numerical category spacing and low parameter reliability limit interpretation.}}
\label{{study5:fig:spatial_pps}}
\end{{figure}}

"""


def robustness_results(r):
    extension=r['robustness'];p=r['participant_sigmoids'];g=extension['group_shape']
    models=extension['recording_linkage'];scores={a['family']:a['outer_rmse_ms'] for a in g['prediction']['scores']}
    summary=[a for a in contrast_diagnostics(p) if a['contrast']=='condition_delta']
    reliability=lambda model,metric:next(a['median_split_half_rho'] for a in summary if a['model']==model and a['parameter']==metric)
    rows=[]
    for s in models:
        m=s['mixed_models'][0];b=m['coefficients'][-1]
        rows.append(', '.join(s['excluded_ids'])+f" & {m['participants']} & {b['estimate']:.2f} & [{b['ci_low']:.2f}, {b['ci_high']:.2f}] & {m['p']:.3f}"+r' \\')
    table='\n'.join(rows)
    cohort=next(s for s in p['linkage_sensitivities'] if len(s['excluded_ids'])==2)
    midpoint=next(a for a in cohort['contrasts'] if a['model']=='individual_plateaus' and a['contrast']=='condition_delta' and a['parameter']=='midpoint_cm')
    all_cohorts=[p]+p['linkage_sensitivities']
    associations=[a for s in all_cohorts for key in ('associations','shared_associations') for a in s[key] if a['scope']=='main']
    nonzero=sum(a['ci_low']>0 or a['ci_high']<0 for a in associations)
    contrasts=[a for s in all_cohorts for a in s['contrasts']]
    contrast_nonzero=sum(a['ci_low']>0 or a['ci_high']<0 for a in contrasts)
    geometry=[a['leave_position_rmse_ms'] for a in g['geometry_sensitivities'] if a['status']=='computed']
    return rf"""\subsection{{Recording exclusions and remaining robustness checks}}

An explicitly post-results amendment reran the primary behavioural models after excluding the two ambiguous records together and each separately. The numeric Condition $\times$ Phase $\times$ SOA result remained uncertain in every specification (Table~\ref{{study5:tab:linkage_models}}). All three categorical-interaction and Control-only numeric/categorical comparisons also had unadjusted $p>.05$. Raw/log cluster models, equal-person slope contrasts and raw-RT repeated-measures ANOVA are retained in the companion. These exclusions test sensitivity and do not identify the correct recording-to-person mapping.

\begin{{table}}[htbp]
\centering\small
\begin{{tabular}}{{lrrrr}}
Excluded & Records & Estimate & 95\% interval & $p$ \\
\hline
{table}
\end{{tabular}}
\caption{{Primary numeric interaction after recording exclusions. Estimates are ms per cohort-specific SOA SD, with model-based Wald intervals; $p$ is the unadjusted full/reduced ML likelihood-ratio comparison. Cleaning and SOA scaling were recomputed for each cohort.}}
\label{{study5:tab:linkage_models}}
\end{{table}}

For the four fitted curves per person, equal-phase Condition, equal-condition Phase and Condition $\times$ Phase contrasts were calculated for midpoint, normalized steepness and signed RT derivative under both plateau models. All four linkage specifications received 500 person/group-plus-trial refits. Across {len(contrasts)} mean contrasts, {contrast_nonzero} conditional refit intervals excluded zero; across {len(associations)} main questionnaire associations, {nonzero} did so. For example, the separate-plateau mean midpoint change excluding both ambiguous records was {midpoint['estimate']:.2f}~cm, with interval [{midpoint['ci_low']:.2f}, {midpoint['ci_high']:.2f}]~cm. The sizeable point shift reflects a fitted, partially pooled proxy; the wide interval and weak reliability prevent interpreting it as demonstrated PPS contraction.

The changes used in correlations were themselves unstable. Across ten splits, median rank correlations for midpoint change were {reliability('individual_plateaus','midpoint_cm'):.3f} and {reliability('shared_plateaus','midpoint_cm'):.3f} for separate and shared plateaus, respectively. Corresponding normalized-steepness values were {reliability('individual_plateaus','normalized_steepness_per_cm'):.3f} and {reliability('shared_plateaus','normalized_steepness_per_cm'):.3f}; signed RT-slope values were {reliability('individual_plateaus','midpoint_slope_ms_per_cm'):.3f} and {reliability('shared_plateaus','midpoint_slope_ms_per_cm'):.3f}. Known-signal simulations also assessed all three contrasts. Shared-model midpoint-change recovery was better when truth shared plateaus, but this simulation-specific improvement does not establish reliable observed individual differences (Fig.~\ref{{study5:fig:remaining_robustness}}).

The group-response audit excluded both ambiguous recordings ($n={g['participants']}$) and added 160 log-distance pipelines with the same extraction/smoothing choices as lines. Six-outer/five-inner participant/position prediction gave RMSEs {scores['logistic']:.3f}~ms for broad sigmoids, {scores['visible']:.3f} for visible sigmoids, {scores['linear']:.3f} for lines, {scores['logarithmic']:.3f} for log distance and {scores['constant']:.3f} for a constant. The visible family's improvement over a constant was {scores['constant']-scores['visible']:.3f}~ms; this small descriptive difference is not a significance test or physiological validation. The log-distance comparison does not reproduce the expectancy-controlled design of \citet{{hobeika2019capturing}}. Unsmoothed nonlinear-component tests in the four curves all had unadjusted $p>.05$.

Nine fixed geometry specifications crossed three width floors with permissive, existing and strict visibility criteria. Their descriptive leave-position RMSE ranged from {min(geometry):.2f} to {max(geometry):.2f}~ms; the large error under one permissive specification illustrates instability when an omitted position leaves the transition poorly constrained. Thirty whole-person resamples repeated all 320 visible-method selections with repeated copies kept in the same validation fold. They selected {len(g['selection_frequencies'])} distinct pipelines, and the most frequent appeared only {max(a['draws'] for a in g['selection_frequencies'])} times. These finite sensitivity checks retain all outcomes; thirty draws describe selection instability and do not provide calibrated selection-adjusted tail intervals.

\begin{{figure}}[htbp]
\centering
\includegraphics[width=\textwidth]{{study5_remaining_robustness.png}}
\caption{{Post-results robustness extension. Top left: primary RT interaction and model-based uncertainty across recording exclusions, rescaled to a common one-second SOA increment. Top right: five response families on the same 40-record prediction target. Bottom left: reliability of fitted Condition differences. Bottom right: midpoint-change point estimates and intervals that refit the models. Large fitted shifts can coexist with very uncertain, unreliable changes.}}
\label{{study5:fig:remaining_robustness}}
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

All reported behavioral computations were executed in the marimo browser companion with Pyodide, Python {r['runtime']['python']}, NumPy {r['runtime']['numpy']}, SciPy {r['runtime']['scipy']}, and Matplotlib {r['runtime']['matplotlib']}. The archived browser download records input, code, and output SHA-256 hashes. Native reference checks independently verified random-intercept ML fits, cluster-robust linear and binomial coefficients/uncertainty, repeated-measures $F$ statistics, and JZS quadrature. Additional native references checked questionnaire alpha through its covariance identity, the exact ordinal sign test and interval, all 42 rank correlations, and all 16 moderation fits including ordinary and HC3 uncertainty. Independent long-format participant-intercept models verified the delta regression's Condition $\times$ MAIA slope, standard error, $F$ statistic and $p$ value. Every questionnaire result was also compared across native and browser runtimes. A failed or unavailable check is distinguished from a computed null result.

The released CSVs do not contain waveforms, belt recordings, acquisition-version labels, collection dates, or the private provenance needed to identify two historically documented RT-onset variants. The browser analysis therefore does not rerun waveform timing, measured respiratory compliance, pilot-date classification, version-specific contrasts, or that source-definition exclusion. Historical source audits remain historical evidence, rather than new 42-person verification.
"""
    q=r["questionnaires"];s=q["spatial"]
    trust=q["delta_associations"][7]
    abstract=abstract.replace("The full data-supported pipeline", rf"An exploratory paired ordinal comparison in {s['n_pairs']} participants found higher post-intervention spatial-frame codes under Viscereality (exact sign-test $p={s['p']:.4f}$). Pre-experiment MAIA-2 Trusting correlated with the numerical Viscereality--Control difference ($\rho={trust['rho']:.3f}$, unadjusted $p={trust['p']:.4f}$); its moderation estimate remained positive with order and HC3 sensitivities. These post hoc associations are not evidence of mediation. The full data-supported pipeline")
    abstract=abstract.replace(f"{c['participants_input']} participants and",f"{c['participants_input']} participant records and")
    abstract=abstract.replace("The full data-supported pipeline", "A further exploratory extension produced 168 individual sigmoid proxies and common-plateau displays, but midpoint reliability was low and all main refit-bootstrap association intervals included zero. Condition-matched spatial associations also remained uncertain. An audit found two identical behavioural recordings with reversed intervention labels and different questionnaire responses; full-release behavioural inference is provisional pending source mapping. The full data-supported pipeline")
    results=results.replace(f"all {c['participants_input']} participants in",f"all {c['participants_input']} participant records in")
    results=results.replace("\\subsection{Primary interaction and sensitivity analyses}",
        "A recording-integrity audit found that P011 and P033 share all 408 behavioural trial records, with Control/Viscereality labels swapped, despite different questionnaire responses. The CSVs were preserved; the correct recording-to-person mapping is unresolved. Full-release behavioural inference below is provisional and cannot assume 42 independent recordings. The new individual-parameter extension reports explicit exclusions of both records and of each separately. Questionnaire-only spatial/MAIA results do not depend on the RT mapping.\n\n\\subsection{Primary interaction and sensitivity analyses}")
    results=results.replace("\\subsection{Reproducibility and evidence limits}",questionnaire_results(q)+individual_results(r['participant_sigmoids'])+robustness_results(r)+repeated_results(r)+spatial_results(r)+"\\subsection{Reproducibility and evidence limits}")
    results=results.replace("A failed or unavailable check is distinguished", "For individual proxies, independent KernelReg smoothing and scalar least-squares grid objectives checked all 168 primary fits; weighted least squares checked shared plateaus conditionally, and SciPy independently checked correlations across both models and recording exclusions. Every individual result was compared across native and browser runtimes. A failed or unavailable check is distinguished")
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
