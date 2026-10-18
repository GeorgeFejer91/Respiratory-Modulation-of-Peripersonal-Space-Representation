# Project contract

## Active scope: results before narrative

The owner has paused manuscript drafting. Pin down the Study 5 results in the
ordered, itemized [analysis roadmap](ANALYSIS_ROADMAP.md), then deliver a
results-only report stating how far each level is satisfied. Do not select a
paper narrative or refresh LaTeX/Typst prose/PDFs during this phase. The existing
manuscript is a preserved version-1.9 snapshot, not the destination for new results.

The main estimands are participant-specific PPS midpoint (cm) and normalized
midpoint sharpness `1/(4*width_cm)` in all four Control/Viscereality ×
Exhale/Inhale cells. First establish what is estimable and reliable; then assess
Condition, Phase and Condition × Phase. Describe the four average response curves
and their uncertainty. Explore links with eight baseline MAIA-2 subscales and
post-condition spatial ratings only after documenting the measurement limits.

The active goal is a **literature-supported Bayesian and frequentist comparison
of baseline-corrected PPS models**, testing Phase, Condition and Condition × Phase.
The owner explicitly specifies `corrected RT = Audio–Tactile RT − Baseline RT`.
Use the existing within-participant × Condition × Phase baseline mean as the
primary correction for both interventions and phases; retain same-nominal-SOA
subtraction as a timing-unverified sensitivity and raw RT as a reference. Propagate
baseline-estimation uncertainty. Plateau normalization is not baseline subtraction.

Retain the joint hierarchical sigmoid as the first nonlinear approach, alongside
frequentist nonlinear estimation and linear/log-distance models. Report midpoint
and normalized sharpness for identifiable sigmoids; lines/log curves instead
provide distance slopes and response contrasts, not intrinsic PPS boundaries.
Screen additional literature methods in an explicit finite registry, recording
implemented, redundant, unsuitable and inaccessible approaches. Prioritize relevant
experimental results while reporting the full family, uncertainty and failures.
The expanded fits/tests are **NOT RUN**; `ANALYSIS_ROADMAP.md` defines completion.
Neither a significant result nor exhausting an unlimited set of methods is a
scientific stopping criterion.

A Bayesian extension is authorized. It must disclose likelihood, priors and
approximation, compare simpler response models, check prior sensitivity and
prediction, and propagate individual uncertainty. Bayesian inference is not
assumption-free and a finite posterior median is not an identified physiological
boundary. No fitting, cleaning, priors or cohort may be chosen by questionnaire
significance. All frequentist p values remain unadjusted at the owner's request;
report the full comparison family and pointwise uncertainty.
The owner also requested conventional 2 × 2 RM ANOVAs treating individual Bayesian
posterior medians as fixed measurements. Retain this separately labelled analysis,
all prior/cohort sensitivities and its omission of within-fit uncertainty.

## Browser companion and ownership

Keep the [application](https://georgefejer91.github.io/Study5_Publication/) and
[editable workbook](https://georgefejer91.github.io/Study5_Publication/editor/)
runnable in the browser. Preserve the established full analysis and its exact
version-1.9 reference. New results-only analyses may have a separate run button
and independently hashed download, allowing manuscript work to stay frozen.
Source push, numerical verification, browser execution and Pages deployment are
separate observed gates. Do not describe source push alone as deployment.

- `workbook/`: browser execution, preparation, fixed analysis, portable models,
  reports, figures and Pages build. `ANALYSIS_PLAN.md` owns executable specifications.
- `data/raw/`: audited public participant/trial CSV pair; preserve unchanged.
- `results/`: verified statistical outputs, reference records and final results
  report. `figures/`: publication-draft assets. Keep new results distinct from the
  preserved manuscript snapshot.
- `analysis/prepare_publication.py`: promotes verified legacy browser results into
  the manuscript; do not invoke while manuscript drafting is paused.
- `manuscript/`: preserved canonical LaTeX and derived Typst snapshot.
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
reverse that empirical result. Retain flat/reversed profiles, signed amplitudes,
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

No manuscript narrative, submission-ready claim, invented physiological boundary,
questionnaire-driven cleaning, guaranteed sigmoid, significance target or causal
mediation claim belongs in the active task. Author review, collection/stopping
history and source mapping remain separate from computational completion.
