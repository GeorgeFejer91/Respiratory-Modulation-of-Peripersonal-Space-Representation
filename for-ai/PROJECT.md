# Project contract

## Active scope: browser analysis and a living publication on GitHub Pages

The owner now makes GitHub Pages the primary analysis workspace and the primary
reader-facing publication/preprint, with source and reproducible releases in this
repository (D-0015, 2026-10-21). Develop the HTML paper and its analyses together:
questions, methods, results, figures, interpretation, references and downloadable
evidence must trace to the same declared data/code/result version. The ordered
[analysis roadmap](ANALYSIS_ROADMAP.md) remains the single active checklist.
Publication-ready is an acceptance goal, not a status conferred by hosting.

General figure rule: quantitative data plots use an actual zero reference. When
all plotted values and uncertainty are nonnegative, the y-axis lower bound is
exactly zero with no padding below it. When values or intervals extend below
zero, retain their full extent and mark zero explicitly rather than clipping data.

This supersedes the results-only pause for authoring the current HTML publication.
Keep the version-1.9 LaTeX/Typst/PDF and reference artifacts as historical
snapshots; do not automatically overwrite or promote them. Preserve the
results-only report as evidence for the living paper. Native-only analyses must
be labelled until actual browser execution and numerical parity are verified;
port the existing methods in finite stages rather than replacing them with a
spreadsheet engine. Skill installation alone does not migrate any analysis.

The main estimands are participant-specific PPS midpoint (cm) and normalized
midpoint sharpness `1/(4*width_cm)` in all four Control/Viscereality ×
Exhale/Inhale cells. First establish what is estimable and reliable; then assess
Condition, Phase and Condition × Phase. Describe the four average response curves
and their uncertainty. Explore links with eight baseline MAIA-2 subscales and
post-condition spatial ratings only after documenting the measurement limits.

The scientific inference goal remains to **identify usable Bayesian evidence for
Phase, Condition or
Condition × Phase effects on PPS boundary or normalized sharpness**, with the six
primary parameter contrasts and validity requirements in `ANALYSIS_ROADMAP.md`
(Q10). The completed Bayesian/frequentist battery remains the reference. Freeze
the next finite nuisance/reduced-model extension before fitting; report an
inconclusive result if evidence or identification remains insufficient.
The completed native sensitivity batch implements every-trial distribution plots, one
additional distance-specific SD filter, blocks 1–3 of each intervention as a
fewer-trial sensitivity, and adjacent rolling means with their full covariance.
Source is `analysis/trial_cleaning/`; its pre-fit specification and complete
results are in `results/trial_cleaning/`. Preserve original cleaning/results,
matched unsmoothed held-out targets and all eight unadjusted Bayesian variants.
The owner clarified that both interventions share one sitting. The main current
control is a jointly estimated RT trend over continuous global trial order, with
five adjusted fits/five additional predictive folds in `session_specification.json`
and `SESSION_RESULTS.md` under that results directory. Early blocks of each
intervention are not a fatigue exclusion. Neither time adjustment nor smoothing
guarantees a supported PPS parameter effect.
Fixed analyses retain `corrected RT = Audio–Tactile RT − Baseline RT`.
Use the existing within-participant × Condition × Phase baseline mean as the
primary correction for both interventions and phases; retain same-nominal-SOA
subtraction as a timing-unverified sensitivity and raw RT as a reference. Propagate
baseline-estimation uncertainty. Plateau normalization is not baseline subtraction.
Owner display amendment (2026-10-22): Segment 0's baseline correction is a toggle,
on by default, showing `baseline_benefit_ms = Baseline RT − Audio–Tactile RT`.
Use the same matched baseline and retained data; preserve participant-weighted
means, sample SD/n, nulls and negative values. Off shows uncorrected RT. Label the
direction in the table/chart and the derived CSV measure explicitly. Original
trial records and `corrected_rt_ms` remain unchanged, including the ungrouped
table, fixed analysis outputs and standalone pivot. Disable the toggle for the
ungrouped original-record view. This display reversal is not a new model/refit.

Retain the joint hierarchical sigmoid as the first nonlinear approach, alongside
frequentist nonlinear estimation and linear/log-distance models. Report midpoint
and normalized sharpness for identifiable sigmoids; lines/log curves instead
provide distance slopes and response contrasts, not intrinsic PPS boundaries.
Screen additional literature methods in an explicit finite registry, recording
implemented, redundant, unsuitable and inaccessible approaches. Prioritize relevant
experimental results while reporting the full family, uncertainty and failures.
The earlier results-first phase produced the expanded native batch in
`analysis/baseline_effects/`, with its finite registry, complete numerical outputs
and results-only report in `results/baseline_effects/`. It preserves failed
diagnostics and labels post hoc checks. These results are separate from the
existing browser and manuscript snapshots; native execution does not establish
browser execution. Neither significance nor an unlimited search is a scientific
stopping criterion. `ANALYSIS_ROADMAP.md` records the remaining evidence limits.

A Bayesian extension is authorized. It must disclose likelihood, priors and
approximation, compare simpler response models, check prior sensitivity and
prediction, and propagate individual uncertainty. Bayesian inference is not
assumption-free and a finite posterior median is not an identified physiological
boundary. No fitting, cleaning, priors or cohort may be chosen by questionnaire
significance. All frequentist p values remain unadjusted at the owner's request;
report the full comparison family and pointwise uncertainty.

The owner authorizes pooling across participants and smoothing across SOA. Use
one common estimator for all four participant cells; retain raw observations,
parameter uncertainty and labels for imposed/extrapolated sigmoid geometry.
The earlier signed-amplitude reference is the converged native
`joint_logistic_marginal`, with its publication recommendation and all-person
display preserved in `results/publication_sigmoid_choice/`. The owner now requires
the near/far asymptote orientation to be the same across conditions. The completed
directional extension is a positive-amplitude hierarchical sigmoid on increasing physical
distance: near RT lower, far RT higher in every cell. Direction is a model
assumption, not evidence obtained from a positive-only posterior. Preserve near-zero
responses and compare held-distance predictions with the otherwise matched signed
model. Equal direction does not require identical numerical plateau heights.
Source/specification/results belong in `analysis/directional_sigmoid/` and
`results/directional_sigmoid/`; do not flip old estimates or hide reversed data.
The refit and matched held-distance comparison are now verified. Use this as the
owner-requested exploratory directional approximation, retaining its weak boundary
identification and the signed-model sensitivity; it is not a validated individual
physiological measurement or evidence that the sign was discovered.

The owner additionally authorizes a visible in-range S through explicit midpoint/
width constraints. The completed approximation is `visible95` with 5/95% endpoint levels in
the measured 10–100 cm, plus a 10/90% sensitivity, in `analysis/visible_sigmoid/`
and `results/visible_sigmoid/`. Fit and evaluate it as an exploratory, strongly
theory-constrained approximation. Its in-range transition, sharpness floor and
normalized S are assumptions; retain actual RT observations, prior-information
checks and held-distance comparison. Never treat these guarantees as validation
of a physiological PPS boundary or select the bounds by experimental significance.

The owner also requested conventional 2 × 2 RM ANOVAs treating individual Bayesian
posterior medians as fixed measurements. Retain this separately labelled analysis,
all prior/cohort sensitivities and its omission of within-fit uncertainty.

## Browser companion and ownership

Segment 1 first tests the basic SOA-dependent RT phenomenon with a five-level
within-person omnibus ANOVA, existing cleaning/primary40, equal Condition × Phase
cell averages and always-GG correction. Show participant RT profiles, marginal
95% t CIs, APA statistics and hashed downloads; see `results/pps_soa/`. This
exploratory prerequisite does not establish spatial specificity or a PPS boundary.
The page displays native saved results and labels that execution limit.

The landing page is a compact ten-section scientific overview, built from
`workbook/overview_assets/`. Segment 0 is the central descriptive explorer;
each later section contains one question and a link to its analysis/evidence.
Segment 1 additionally shows its initial SOA graph and APA result directly.
Segment 2 additionally answers the overall Inhale−Exhale RT question using the
saved native primary40 paired contrasts: raw AT slowing during inhale and an
inconclusive matched-baseline-corrected phase effect. It gives a compact answer,
cohort/weighting/uncertainty labels and links to the complete contrast family;
it does not execute or refit that analysis in the browser.
Its Figure 2 uses literal released phase labels, showing participant raw RT pairs
and paired raw/baseline/AT−Baseline differences with 95% t CIs. Raw phase means
are Exhale 662.19 ms and Inhale 680.66 ms. `workbook/phase_rt.py` owns the native
label-direction audit, figure and hashed exports in `results/phase_rt/`.
State the scheduled/instructed label limit: the release cannot verify actual
respiratory physiology or acquisition-side labelling without belt recordings.
The section menu stays fixed beside desktop content and collapses at the phone's
bottom edge; embedded dialogs reserve space for this navigation.
Keep narrative, assumptions and detailed results in those linked reports. The original
executable workbook remains at `/workbook.html`, with `/editor/` unchanged.
The overview displays archived evidence and does not execute or refit models.
Segment 0 embeds the existing worker-based pivot in a same-origin, auto-height
frame. Its core-data starting view uses a compact Audio–Tactile RT
means payload, primary 40 cohort and equal-person summaries. The X-axis is fixed to the released SOA values (300, 800, 1500, 2200, 2700 ms).
Condition (Control/Viscereality) and phase (Exhale/Inhale) use four native
checkboxes, all initially checked, to select series in both the table and chart.
Clearing either group gives an empty result. Segment 0 has no field dragging,
axis reassignment or ungrouped trial-record mode.
The full pivot subpage retains its broader source catalogue.
Baseline correction uses the default-on Baseline − RT toggle described above;
Mean/Mean ± SD presentation uses a select updating both views. The adjacent
default-off Normalize RT toggle offers 0–1 min–max and z-score methods.
For each participant, estimate minimum/maximum and mean/sample SD using all
retained AT trials across both conditions, both phases and all SOAs, before
display selection. Apply the same linear transform to cell means, then aggregate
across people. With correction on, references use Baseline − AT RT; off uses
raw RT. One shared scale preserves within-person comparisons; zero/undefined
scales yield missing values. Dimensionless CSV fields end in _norm or _z.
This is descriptive normalization, not a physiological or new inferential method;
methods and researched sources are in workbook/RT_NORMALIZATION.md. Normalization
metadata loads lazily in means-normalized.json; the compact startup payload is
unchanged. Source data and fixed analyses stay unchanged.
Readers can change cohort, aggregation, chart style and filters and export every
row/column. For Mean over
the participant-distance source, pool unselected factors within each participant
before computing across-person means, sample SDs (n−1) and nonmissing n at each
SOA/group. These SDs describe participant variation, not SEM or confidence intervals;
n<2 has undefined SD. Full-value details and CSV retain mean/SD/n even when the
display hides SD. Preserve the existing
correction, cleaning, primary40 and cohort sensitivities; no model is refitted.

The owner has resumed GitHub Pages work for sequential visual exploration.
The separate `/pivot/` page prioritizes fast loading and smartphone compatibility
using lightweight JavaScript, a worker and lazy JSON prepared by the existing
Python owner. The first table uses only a compact default-view payload; larger
field sets, trials and saved tables load on demand. Keep Python/Pyodide off this
page's startup path. Its Pivot settings select the audited release,
participant-distance means, questionnaires or a lazy catalogue of tracked public
result CSVs. A linked SVG chart consumes the same structured worker cells as
the table, initially by SOA with Condition × Phase series. Settings apply live;
chart measure/style change presentation, with separate units, missing gaps and
explicit dense/mixed-unit states. Nonnegative chart values start at zero; when
negative values must remain visible, the chart retains them and marks zero as a
reference. It contains no heatmap or explanatory report. Pivot interaction
remains descriptive; it does not refit models or silently change the paper's
analysis. The scientific inference roadmap stays open.
The sibling `/exploratory/` subpage preserves the expanded exploration controls,
heatmap, source inspection and downloads, sharing the pivot preparation and
saved-result catalogue rather than fitting new models.
The original marimo pivot remains available under `/pivot/app/`. Any Excel-like
or data table shown on a live page must render its complete result in one table,
with internal scrolling and user controls for table height and width. Do not split
table rows or columns across Next/Previous buttons. Pivot settings retain ordered
stretch groups; chooser lists scroll to expose all options without paging. Locked
Pretext 1.0.0 measures bounded labels after the first table. Preserve user text
enlargement; very short enlarged layouts may use deliberate outer document flow.
Browser-size emulation does not establish actual iPhone/Safari verification.

Keep the [application](https://georgefejer91.github.io/Study5_Publication/) and
[editable workbook](https://georgefejer91.github.io/Study5_Publication/editor/)
runnable in the browser. Preserve the established full analysis and its exact
version-1.9 reference. New analyses need an explicit specification, separate run
state and independently hashed download before they can support the living paper.
Source push, numerical verification, browser execution and Pages deployment are
separate observed gates. Do not describe source push alone as deployment.

- `workbook/`: browser execution, preparation, fixed analysis, portable models,
  reports, figures and Pages build. `ANALYSIS_PLAN.md` owns executable specifications.
- `data/raw/`: audited public participant/trial CSV pair; preserve unchanged.
- `results/`: verified statistical outputs, reference records and final results
  report. `figures/`: publication-draft assets. Keep new results distinct from the
  preserved manuscript snapshot.
- `analysis/prepare_publication.py`: legacy promotion into the historical
  manuscript; do not invoke as part of the HTML publication transition.
- `manuscript/`: preserved version-1.9 LaTeX and derived Typst snapshot, not the
  current publication's editing destination.
- `literature_review/`: traceable evidence, supporting and contrary sources,
  method-to-claim links and actual access records.
- `for-ai/`: scope, roadmap, decisions and verification instructions, not final
  deliverables. `.for-ai-local/`: ignored execution diagnostics/builds.

## Measurement and provenance boundaries

The release contains 42 participant records and 17,114 trials. P011/P033 share all
408 behavioural rows with condition labels swapped and different questionnaires;
the correct recording-to-person mapping is unresolved. Primary new behavioural
inference excludes both; retain full release and each single exclusion as
sensitivities. Never claim 42 independent recordings or silently choose a mapping.
Standalone MAIA–spatial analyses do not depend on the ambiguous RT mapping.

MAIA-2 was measured once before the experiment. Spatial ratings were collected
after each intervention, once per condition, not per respiratory phase. Use
Viscereality minus Control for within-person changes. Numerical category deltas
assume comparable spacing; retain ordinal rank/direction sensitivities. The
administered pictogram anchor key is missing, so higher codes cannot be labelled
more allocentric or egocentric. Trait moderation and post-intervention association
do not establish causal mediation.

The original trial-level sigmoid gate failed (0/168 cells at R²≥.70). Existing
regularized fits, smoothing, common-plateau normalization and Bayesian priors cannot
reverse that empirical result. Retain flat/reversed observations, unrestricted
signed-amplitude reference fits,
raw observations, simpler-model prediction, recovery, reliability and uncertainty.
An imposed normalized S or extrapolated plateau is not evidence of observed
curvature. Parameter differences and correlations require their own uncertainty.

The [registration](https://aspredicted.org/az9f89.pdf) remains the registration
source; later sigmoid/questionnaire extensions are explicitly exploratory.
The CSVs cannot verify belt compliance, waveform timing, acquisition dates,
version labels or private onset exclusions. Do not fabricate those checks.

## Release and non-goals

Public visibility, release of the audited deidentified CSV pair and existing
ethical approval are owner-authorized; see D-0004/D-0011 and
`workbook/DATA_RELEASE.md`. Keep names, crosswalks, private backups, recordings,
source paths and private provenance outside public artifacts. No repeated release
permission is needed for these unchanged audited inputs.

No automatic historical-manuscript rewrite, guaranteed acceptance, invented
physiological boundary, questionnaire-driven cleaning, guaranteed observed
sigmoid, significance target or causal mediation claim belongs in the active task.
Author review, collection/stopping
history and source mapping remain separate from computational completion.
