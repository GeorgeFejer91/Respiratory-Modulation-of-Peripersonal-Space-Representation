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
        ):
            (ROOT / "figures" / name).write_bytes(archive.read(name))
            (ROOT / "manuscript/figures" / paper_name).write_bytes(figure_bytes(report, measure, "png"))
    write_text(report)
    print("Promoted verified browser report, tables, figures and manuscript statistics.")


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

    def p(value):
        return "<.001" if value < .001 else "=" + f"{value:.3f}".lstrip("0")

    def interval(row):
        return f"[{row['ci_low']:.2f}, {row['ci_high']:.2f}]"

    abstract = rf"""Peripersonal space (PPS) is often inferred from tactile reaction time during an approaching sound. We tested whether instructed respiratory phase changed this SOA-dependent response differently in breath-coupled virtual reality (Viscereality) and Control. The released cohort comprised {c['participants_input']} participants and {c['retained_at']:,} retained audio--tactile hit trials. The planned Condition $\times$ Phase $\times$ SOA mixed-model interaction was not detected, $\chi^{{2}}(1)={primary['lr']:.3f}$, $p{p(primary['p'])}$; categorical-SOA and partial-session-exclusion sensitivities agreed. Audio--tactile responses were {abs(supp[3]['estimate']):.1f}~ms faster than tactile-only Baseline responses on average, but equal nominal delay labels do not establish matched cue times. None of {sigmoid['cells']} participant-by-condition-by-phase trial-level sigmoid fits met the planned $R^{{2}}\geq .70$ threshold. The maximum saturated five-SOA trial-level $R^{{2}}$ ceiling was {sigmoid['max_trial_r2_ceiling']:.3f}, precluding this threshold for any curve of SOA alone. Boundary, sharpness, and boundary-related questionnaire inference therefore remained unestimated. The full data-supported pipeline, diagnostics, and downloadable results run in a marimo browser companion. These data do not demonstrate the predicted Viscereality-specific respiratory modulation; confidence intervals and source-timing and respiratory-compliance limits constrain interpretation.
"""
    # LaTeX thousands separators must not introduce punctuation into math.
    abstract = abstract.replace(f"{c['retained_at']:,}", f"{c['retained_at']:,}".replace(",", "{,}"))
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

All reported behavioral computations were executed in the marimo browser companion with Pyodide, Python {r['runtime']['python']}, NumPy {r['runtime']['numpy']}, SciPy {r['runtime']['scipy']}, and Matplotlib {r['runtime']['matplotlib']}. The archived browser download records input, code, and output SHA-256 hashes. Native reference checks independently verified random-intercept ML fits, cluster-robust linear and binomial coefficients/uncertainty, repeated-measures $F$ statistics, and JZS quadrature. A failed or unavailable check is distinguished from a computed null result.

The released CSVs do not contain waveforms, belt recordings, acquisition-version labels, collection dates, or the private provenance needed to identify two historically documented RT-onset variants. The browser analysis therefore does not rerun waveform timing, measured respiratory compliance, pilot-date classification, version-specific contrasts, or that source-definition exclusion. Historical source audits remain historical evidence, rather than new 42-person verification.
"""
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
