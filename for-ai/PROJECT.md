# Project contract

## Purpose and primary goal

Publish the Study 5 paper's reproducible analysis as a live marimo companion on
GitHub Pages. Readers must be able to run preparation, every data-supported model,
diagnostics and figures entirely in the browser and download the analysis record.
Maintain a self-contained Overleaf draft reconciled to an actual 42-record browser
run. The project owner authorised public release of the deidentified data and
confirmed ethical approval; see `workbook/DATA_RELEASE.md`.

The active goal is to extend the analysis to four sigmoid transitions
characteristic of peripersonal-space experiments (Control/Viscereality ×
Exhale/Inhale): visible lower and upper bends within the sampled range, an
interpretable midpoint, and measurable steepness. Use a uniform, scientifically
justified extraction/smoothing/fitting procedure; evaluate predictive performance
against equally processed lines and inspect the figures visually. Report when
the measurements do not support the desired shape. An imposed S shape or a
sigmoid that appears only after extrapolation does not complete this goal.

The earlier 320-pipeline analysis produced four computable descriptive curves,
but all four 10–90% transitions exceed the measured range. That computational
milestone does not satisfy the new shape requirement. Maintain the full method
audit and uncertainty, run the extension in the browser, and reconcile the Results
to the actual browser download. The original participant fit gate and the evidence
needed for a physiological PPS boundary remain separate.

The current evidence goal is to make the rationale for this exploratory extension
scientifically defensible. Maintain a miniature review in `literature_review/`
with supporting and contrary PPS evidence, method-to-claim links, search/access
records, and explicit unresolved checks. Use Consensus when configured and the
installed multi-source search workflow; disclose unavailable providers. Completion
means a traceable rationale and calibrated claims, not a guaranteed sigmoid or a
retrospective claim of preregistration. Link the review from the browser companion
and reconcile its conclusions with the manuscript.

The current coverage goal is to analyse every released data domain, including
all 37 MAIA-2 items, the eight scored dimensions, and paired spatial-frame-of-
reference ratings. Audit scoring against the instrument, report missingness and
uncertainty, and connect questionnaire measures to supported behavioural summaries.
Maintain a domain coverage table and a questionnaire literature review. New
questionnaire analyses are exploratory; they cannot revive failed participant
boundary estimates or substitute for measures absent from the release. At the
owner's request after inspecting results, report questionnaire/spatial associations
with unadjusted p values, pointwise intervals and the full comparison count.
Record post-results reporting or estimand changes explicitly.

For spatial-frame follow-ups, prioritise each participant's recorded-code change,
`delta_spfrref = Viscereality - Control`, over separate condition-level
correlations. Retain one paired condition comparison and absolute ratings for
descriptive context and the audit trail. The numerical delta is distinct from
the lower/same/higher direction retained as an ordinal sensitivity; its category-
spacing assumption needs an ordinal sensitivity. MAIA-2 subscales remain
continuous, separate dimensions. A Condition × MAIA interaction addresses
moderation. The owner confirmed MAIA-2 was completed once before the experiment
and spatial ratings after each intervention. The single baseline MAIA measurement
cannot establish intervention-induced mediation. Retain eight main delta
correlations, the ancillary delta–RT link, and all eight moderation models with
and without presentation order, with classical and HC3 uncertainty. Preserve
the 33 earlier associations as supplementary results. See
[D-0007](DECISIONS.md#d-0007--spatial-change-as-the-follow-up-outcome) and
[D-0008](DECISIONS.md#d-0008--baseline-maia-and-post-intervention-spatial-contrasts)
for the accepted analysis direction and execution contract.

The owner has extended the active analysis goal to four participant-specific
Condition × Phase sigmoid approximations for every person (168 curves in the
released cohort), with midpoint, width and midpoint slope, visual inspection,
and additional links to baseline MAIA-2 and signed spatial-rating differences.
Use a uniform, outcome-blind fitting comparison, assess local smoothing and
partial pooling, and retain uncertainty, simpler-model prediction and recovery
diagnostics. A finite regularized estimate is a model-dependent proxy; it does
not reverse the original failed participant boundary gate. Never create a
nonzero response amplitude or discard reverse/flat profiles to guarantee a
visible physiological transition. See D-0009 and the participant extension in
`workbook/ANALYSIS_PLAN.md`.

## Repeated-measures parameter goal

The current analysis goal is to answer whether fitted PPS midpoint and normalized
sharpness differ across all four Condition × Phase cells and whether those
differences relate to baseline MAIA-2 dimensions or post-intervention spatial-code
change. Implement 2×2 repeated-measures ANOVAs and continuous-covariate ANCOVAs,
with order sensitivity and curve-refitting uncertainty. Emphasise the cohort
excluding both ambiguous recordings; retain all records and each single exclusion
as sensitivities, under both plateau models. Select fitting rules using RT
prediction alone. Completion means the full model family, independent checks,
browser execution and calibrated answers, not significant effects or validated
physiological boundaries. See the repeated-measures amendment in
`workbook/ANALYSIS_PLAN.md`.

The implementation evaluates 1,328 nominal terms, with 500 curve refits per
cohort/model. In the both-excluded cohort, all 12 ANOVA and 36 main
order-adjusted Condition-moderation intervals include zero despite 11 small
conventional ANOVA p values. Pooling-dependent point-parameter ANOVAs are not
reliable significance tests for physiological changes; retain the refit intervals
and weak-reliability finding prominently.

## Non-goals

- No names, source IDs/paths, private crosswalks, collection dates or recordings
  in the public artifact; keep verified backups outside it.
- Public repository visibility is owner-authorised under D-0011. Private backups,
  identity/provenance records and raw recordings remain excluded.
- No exploratory result presented as preregistered or author-approved final work.
- Do not fabricate physiological compliance, provenance or gated boundary results.

## Ownership

- `workbook/`: marimo application/editor, shared schema and preparation checks,
  fixed analysis contract, portable inference, reports, figures and Pages build.
- `data/raw/`: audited release CSV pair, arbitrary contiguous participant IDs.
- `analysis/prepare_publication.py`: consumes verified browser results to refresh
  manuscript statistics, tables, figure assets and the compiled draft manifest;
  it does not recompute models.
- `manuscript/`: self-contained Overleaf source and figures. `results/` and
  `figures/`: browser-produced publication-draft artifacts and native validation.
- `literature_review/`: focused scientific synthesis, evidence table, analysis
  rationale and reproducible search record; no participant data or copied papers.
- `for-ai/`: agent instructions, historical writing and source analyses.
  `.for-ai-local/`: ignored builds and local diagnostics.

## Verified scientific boundaries

The released cohort contains 42 participant records (`P000`–`P041`) and 17,114
observed trials. An individual-profile audit found identical behavioural records
for P011/P033 with opposite condition labels and different questionnaires; the
recording-to-person linkage is unresolved. Do not claim 42 independent recordings
until source provenance resolves it. Keep their fits flagged and report the
specified exclusion sensitivities for new RT–questionnaire associations. The
standalone MAIA–spatial comparison does not use RT records.
The active manuscript derives from the browser analysis;
the 40-person text/figures are archived. Author review remains necessary before
submission, including collection/stopping history, ethics-statement details and
registration interpretations. The public CSVs cannot reproduce waveform timing,
measured belt compliance, dates, version labels or private source-onset exclusions.

The [registration](https://aspredicted.org/az9f89.pdf) remains the registration
source. `workbook/ANALYSIS_PLAN.md` states the executable operationalisation,
explicit ambiguities and computational bounds. Fit-gated follow-ups remain not
estimable when the gate fails. Native numerical agreement is distinct from
browser verification; source pushes are distinct from successful deployment.

## Individual-proxy implementation outcome

The companion computes 168 four-cell sigmoid proxies under one selected rule and
an additional shared-plateau specification, with unclipped fitted-asymptote RT
normalization, 500-resample intervals, nested prediction, split-half stability,
known-signal recovery and all fixed questionnaire links. The computational and
visual-output goal is implemented; reliable individual PPS boundary identification
remains unsupported. Full-release midpoint split-half rho is .047 (separate) and
.106 (shared), and all 216 main association intervals across four linkage specifications include zero.
All 72 mean parameter-contrast intervals include zero; midpoint-change split-half
rho is −.074 (separate) and .066 (shared). The remaining-analysis amendment adds
primary-model linkage exclusions, five-family group prediction with log distance,
nine geometry specifications and 30 repeated method selections. These feasible
checks are complete; stable physiological boundary identification is not. The atlas shows
raw evidence alongside normalized geometry. P011/P033 source mapping remains
unresolved; retain flagged outputs and all three exclusion sensitivities. See
`literature_review/INDIVIDUAL_PARAMETERS.md` and the archived browser results.
