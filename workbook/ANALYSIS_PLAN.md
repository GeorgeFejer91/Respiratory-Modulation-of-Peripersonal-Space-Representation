# Publication companion: analysis contract

## Goal

Make the paper's 42-person behavioral analysis reproducible entirely in a web
browser, from the released deidentified CSVs through preprocessing, models,
diagnostics, figures, and downloadable results. The executable owner is the
marimo workbook; the same Python routines support independent native validation.

The project owner authorized this work and public release of the deidentified
data on 2026-10-15 and confirmed that the study already has ethical approval.
See DATA_RELEASE.md for the field audit and verified-backup record. No name,
identity crosswalk, source path, collection date, or recording is published.

## Cohort and cleaning

Use the supplied participant table as the independent-person roster. Report
observed versus planned trials, partial sessions, response quality, missing hit
RTs, demographics, questionnaire availability, and complete Condition × Phase ×
SOA cells. Exclude participants with Catch false-alarm rate >30%; flag hit rates
below 70% without automatically excluding them. Retain the partial session in
the primary cohort, with an explicit exclusion sensitivity.

The primary RT population is recorded Audio-Tactile/Baseline hits. Calculate each
participant's mean and sample SD over those trial types together; retain RTs
within mean ±2.5 SD, inclusive. Do not add the stored 100/200-ms window flags to
this primary rule. The ≥200-ms cutoff is a sensitivity after the primary trim.
Misses and missing hit RTs remain in response-quality denominators. No primary
imputation, participant questionnaire exclusion, or interactive preview filter
is allowed to change this contract.

## Registered questions as operationalized in the current Methods

- Primary: trial-level Gaussian ML, raw Audio-Tactile RT, all Condition × Phase ×
  numeric SOA terms, participant random intercept; full versus reduced model
  omitting the three-way term, likelihood-ratio chi-square with 1 df.
- Secondary: Control-only Phase × numeric SOA comparison, also random intercept.
- Code Control/Viscereality as −.5/+.5 and Exhale/Inhale as −.5/+.5. Standardize
  SOA with its trial-level sample mean/SD. Report scaling with every model.
- The sigmoid boundary gate is trial-level R²≥.70 in all four participant
  Condition × Phase cells. Gate failure prevents boundary inference and its
  questionnaire associations; five-mean or group curves cannot rescue it.

The linked AsPredicted PDF is the registration source. This contract implements
the distinctions documented in the active Methods; it does not claim that
unspecified priors, curve bounds, or metadata were present in the registration.

## Sensitivities and supplementary analyses

Execute and label: categorical SOA; partial-session exclusion; ≥200-ms cutoff;
participant random SOA slopes; participant-cluster-robust raw/log RT regression;
equal-person five-SOA slope contrasts with t interval, sign-flip test and
exploratory paired JZS Bayes factor; complete-subject 2×2×5 repeated-measures
ANOVA with Greenhouse–Geisser correction; hit-probability logistic regression;
within-condition time-on-task adjustment; and missing-hit-RT median plus signed
0/±100/±200-ms stress scenarios, with the RT trim recomputed per scenario.

Report participant-level Baseline condition/phase/interaction, overall
Audio-Tactile-minus-Baseline, far-minus-near, same-label Baseline sensitivity,
pink-minus-white, four-noise complete-subject Friedman and order-stratified
contrasts. Supply raw and Holm-adjusted supplementary p-values. Paired JZS tests
use Cauchy scale √2/2 and are not a registered mixed-model Bayes factor.

For nonlinear curves use f(x)=a+(b−a)expit((x−m)/s), a,b∈[−2000,2000] ms,
m within the sampled distance range, s∈[.1,200] cm; fit registered and
trajectory-implied axes separately. These explicit computational bounds are a
transparent reimplementation, not a claim to recover unavailable historical
optimizer settings. Trial objectives use exact SOA sufficient statistics.
Also report the saturated five-SOA R² ceiling: any trial-level curve depending
only on these SOAs is bounded by that ceiling, independent of sigmoid bounds.
Compare in-sample sigmoid/linear RMSE descriptively. Report five-mean fits and
group fits separately. Interpret boundary parameters only when all four trial
curves pass the gate without parameter-bound hits. Any conditional MAIA/SpFrRef
associations are explicitly exploratory, with their estimand and multiplicity
reported; do not manufacture values when the gate fails.

## Questionnaire and spatial-frame exploration

This extension was specified on 2026-10-16 after inspecting the release schema,
availability and the MAIA-2 development paper, before calculating the new
questionnaire associations. It is post hoc, not a preregistration. Direct retrieval
of the AsPredicted PDF returned HTTP 403; the existing manuscript describes trait
and pictographic correlates as exploratory but is not an independent copy of the
registration. Its exact questionnaire wording remains unverified. After inspecting
the association results, the project owner requested unadjusted reporting instead
of the initially specified Holm adjustment. This reporting amendment retains all
33 comparisons and their exploratory status; it is not a preregistered decision.
The owner subsequently confirmed that MAIA-2 was completed once before the
experiment and spatial-frame ratings after each intervention. This administration
timing is owner-confirmed; it is not reconstructed from timestamps in the CSVs.

Recompute the eight MAIA-2 means from the 37 items using Mehling et al. (2018),
Table 2: Noticing 1–4; Not-Distracting 5–10; Not-Worrying 11–15; Attention
Regulation 16–22; Emotional Awareness 23–27; Self-Regulation 28–31; Body
Listening 32–34; Trusting 35–37. Reverse items 5–10, 11, 12 and 15 as 5−response.
Require all items of each subscale; do not impute or fall back to stored scores.
Audit stored scores with tolerance 1e−6 and preserve the original CSVs. Report
item response frequencies, missingness, observed floor/ceiling fractions,
corrected item–rest Pearson correlations and raw Cronbach alpha per subscale.
Use 2,000 participant bootstrap draws for pointwise percentile 95% intervals on
means and alpha; keep negative estimates and report undefined draws. Alpha is a
limited internal-consistency diagnostic, not evidence of unidimensionality or
validity. Do not perform item deletion, a new 37-item factor model, median splits,
a pooled MAIA total, or clinical classification with this 41-person sample.

Treat A–H/1–8 spatial-frame ratings as ordered categories. Validate both encodings;
display condition distributions and all 64 paired transitions. For complete
pairs, report Viscereality higher/equal/lower than Control and an exact two-sided
binomial sign test among non-ties, with a Clopper–Pearson interval on the higher
fraction among non-ties. This one exploratory condition comparison is a separate
test family. Also report paired dominance (higher minus lower divided by all
pairs), its participant-bootstrap interval, and counts by condition order. Do not
label higher codes allocentric without the administered pictogram anchor key;
that key is absent from the release. The overall paired comparison uses direction;
the numerical-change extension below states its additional spacing assumption.

The fixed exploratory association family has 33 comparisons: each of eight
MAIA-2 dimensions versus Control rating, Viscereality rating, the direction of
the paired rating change (−1/0/+1), and the existing equal-participant raw-RT
Condition × Phase SOA-slope contrast; plus rating-change direction versus that
behavioural contrast. Slopes use all five cell means, the primary cohort/trim and
the primary SOA scaling. Positive contrast means (Viscereality Inhale−Exhale)
minus (Control Inhale−Exhale); it is not a PPS boundary. Use pairwise-complete
people, Spearman rho with average ranks, 19,999 random permutations and the
(extreme+1)/(draws+1) two-sided absolute-statistic p value. Report all 33 p values
without multiple-testing correction; undefined tests remain unestimated in output.
The plus-one rule is part of Monte Carlo permutation inference, not a correction
across tests. Report 2,000 paired-participant
bootstrap percentile intervals, re-ranking each resample. Intervals are
pointwise, not simultaneous; permutation inference assumes exchangeable people
under independence and is not covariate-adjusted. Seed all new resampling with
20261116. Show all associations, never select a subscale by significance.

### Numerical change and pre-experiment trait moderation

This amendment is fixed before calculating the new numerical-delta associations
and models, after inspecting the earlier direction/absolute-rating associations.
It is exploratory. Define `spfrref_delta = Viscereality code - Control code` for
complete pairs, irrespective of presentation order. These are two post-intervention
ratings, not a pre/post spatial baseline. Retain negative differences and zeros.
Report the delta distribution, mean, SD, median, quartiles and range. The primary
condition comparison remains the exact sign test above; no additional intercept
or paired-mean hypothesis test replaces it.

The main trait analyses are all eight continuous MAIA-2 subscale means against
numerical delta, using the same 19,999-permutation absolute-tail Spearman test and
2,000 paired-person bootstrap intervals. Add one ancillary delta-versus-raw-RT
slope-interaction correlation. Use a separate generator seeded 20261117, after
the legacy results; do not change the 33 earlier association estimates or draws.
The eight existing MAIA-versus-change-direction correlations are ordinal
sensitivities. Absolute-rating associations remain supplementary audit results.
No total score, median split or significance-based subscale selection is used.

For each of the eight subscales, fit two participant-level OLS models:
`delta ~ 1 + centred_MAIA` and
`delta ~ 1 + centred_MAIA + centred_Viscereality_first`.
Centre predictors at their analysis-sample means; order is 0 for Control-first
and 1 for Viscereality-first. Unknown order excludes a person only from the order
sensitivity. These 16 fits estimate Condition × MAIA moderation in a two-level
repeated-measures linear model. The order term corresponds to Condition × Order.
Independently verify the equivalence against a long-format model with participant
intercepts, Condition and these interactions. Report the slope in spatial-code
steps per one MAIA point, ordinary SE, two-sided t p value, pointwise 95% t interval,
and interaction F=t² with (1,n-k) degrees of freedom. Classical inference assumes
independent participants, a linear conditional mean and homoskedastic Gaussian
errors. Also report HC3 SE, two-sided t p value and interval with n-k degrees of
freedom as an approximate heteroskedasticity sensitivity. Neither approach makes
the categories interval-scaled. Export sample size, centring, order coefficient,
R², maximum leverage and Cook distance; retain undefined fits explicitly.

All p values are unadjusted; all eight subscales and both model specifications are
reported. Correlation, direction sensitivity and interaction fits reuse the same
people and are not independent replications. Numerical code differences assume
comparable A–H steps; ranking differences does not remove this assumption. Keep
direction-only sensitivity and unverified pictogram meaning explicit. A baseline
MAIA trait can moderate the condition contrast but cannot mediate within-person
intervention-induced MAIA change here. No mediation model is fitted. Adjustment
for order does not establish absence of carryover or remove all confounding.

Questionnaire descriptives use the questionnaire roster; behavioural links use
the intersection with valid participant slopes. Missing questionnaires never
remove a person from the primary RT analysis. Descriptive inter-subscale
correlations (28) carry no separate hypothesis tests. No pre/post MAIA contrast,
body-boundary or small-self result can be produced from absent columns. Retain
the boundary gate for every boundary-related questionnaire hypothesis.

See [the questionnaire review](../literature_review/QUESTIONNAIRES.md) for sources,
access limitations, registration crosswalk and the domain coverage inventory.

## Post hoc four-curve descriptive extension

The active goal additionally requires a visibly S-shaped PPS-like transition
inside the measured range, with midpoint sampling and steepness diagnostics,
fair predictive comparisons and visual figure review. The extension now includes
320 explicitly shape-constrained pipelines and 160 equally processed linear
pipelines alongside the original 320 sigmoids. Six outer participant folds repeat
selection inside the training set. Raw unsmoothed curvature is tested separately
and is not a sigmoid-specific test. Full methods, thresholds, failure findings,
literature-access limits and the distinction between imposed shape and empirical
support are recorded in [SIGMOID_EXPLORATION.md](SIGMOID_EXPLORATION.md).

The owner subsequently requested four uniform group sigmoid approximations,
including signal extraction and smoothing when useful. This separate analysis
does not require the participant fit gate: it estimates descriptive group shapes,
not participant boundaries or their questionnaire associations. Its full contract,
scientific sources and limitations are in [SIGMOID_EXPLORATION.md](SIGMOID_EXPLORATION.md).

Use the same cleaned AT trials, equal participant weights and all five positions.
Compare 320 combinations of five cell extractions, 32 smoothers and separate/shared
width fitting. Select one pipeline for all four curves by a common raw-mean shape
prediction target with held-out participants and positions; retain constant and
linear benchmarks and all alternatives. Report midpoint, logistic width, 10–90%
span and midpoint derivative, with bounds and coordinate sensitivity. Resample
whole participants together across the four curves 1,000 times, report flat and
bound-hit fractions, and distinguish conditional intervals from uncertainty in
the method search. Show observed summaries and clearly marked extrapolations.
Do not treat smoothing/interpolation as new independent observations.

## Individual sigmoid proxies: owner-authorised exploratory extension

The owner selected four Condition × Phase curves per person as primary and
requested a common-plateau normalized display. This amendment is fixed before
new individual-proxy results. It neither changes the original trial-level R²
gate nor relabels its unavailable follow-ups as recovered boundaries.

Use the existing retained AT trials and nominal distances (10, 27, 50, 73,
100 cm). Every complete participant receives four records; report missing cells
explicitly without imputation. Preserve signed amplitudes and flat outcomes.
Fit `b + a*logistic((x-m)/w)` on scaled distance, with a in [-500,500] ms,
m in [0,1] and w in [.05,1]. The primary descriptive family restricts geometry
using the existing measured-range criteria (10–90% coverage, two positions on
each side, at least one in the 20–80% transition, ≥5% departure from a line).
These restrictions impose curvature. A broad-shape family omits them. Offsets
and signed amplitudes are solved exactly at each shape; no positive amplitude
floor is permitted. A flat fit has no identified midpoint, even when a
regularizer supplies a numeric proxy.

Compare 3 summaries (mean, median, 20% trimmed mean), 4 smoothers (none,
Gaussian local constant at .15/.30 of the distance span, Gaussian local linear
at .30), and 3 shape penalties (0,1,4) uniformly: 36 methods per sigmoid family,
12 equally processed lines, and a constant. The penalty shrinks midpoint and
log width toward a leave-one-person-out same-cell pooled shape, with scales
.25 of the span and log(2), respectively. Divide profile SSE by a working
mean-variance estimate from available trial cells (floor 1 ms²). This is
penalized profile estimation, not a fully Bayesian posterior. Select one
method for all people/cells using omitted-position prediction; do not tune
against MAIA, spatial ratings or their p values. Six outer participant folds
repeat tuning on training people only and then predict each held-out person's
omitted position from their remaining four. Pooled shapes for held-out people
use training people only. Compare the broad, visible, line and constant families.
These evaluations condition on the original cleaning and the known design;
they are post hoc, not independent confirmatory evidence. Use seed 20261018.

Use the existing 61×35 shape grid and a 241×81 resolution sensitivity. Apply
500 fixed-person, within-cell trial bootstrap draws, refitting pooled shapes,
for pointwise parameter intervals. Separately perform 500 hierarchical
person-plus-trial bootstrap draws for association intervals, recomputing pools
and excluding all copies of the target person from its pool. These intervals
condition on the selected method and shape restrictions. Report 10 repeated
stratified split-half reliability checks and 30 simulation replicates each
under flat, linear and known-sigmoid signals with empirical residuals and
trial counts. Recovery is a design-specific diagnostic, not population validity
or full confidence-interval calibration.

Export midpoint (cm), width (cm), normalized steepness magnitude 1/(4w), signed
RT derivative a/(4w), signed amplitude, fit error, all uncertainty and diagnostics.
Keep direct unregularized and grid-resolution sensitivities. A joint sensitivity
shares lower/upper asymptotes across the four curves within each person, using
the selected preprocessing/penalty; compare its omitted-position prediction.
Normalize displays as `(RT-min(b,b+a))/abs(a)`, retaining direction and values
outside [0,1] without clipping. Normalized model curves have common 0/1 plateaus
by definition. When amplitude is zero normalization is undefined; when its
bootstrap interval includes zero, mark observed-point normalization unstable.
Show raw observations/curves alongside normalized geometry for every person.
An affine rescaling does not change midpoint or width or create empirical
curvature. Shared-plateau fits make an additional measurement assumption.

The new association catalogue is 126 tests: 8 MAIA subscales × 3 parameters
(midpoint, normalized steepness, signed RT derivative) × 5 summaries (four
Condition × Phase cells and equal-phase Viscereality–Control contrast), plus
the 3 parameter contrasts versus numerical spatial delta and its direction-only
sensitivity. The 27 numerical contrast associations are the main follow-up;
96 cell-specific correlations and 3 directional correlations are supplementary.
Use complete people, Spearman rho and 19,999 absolute-tail pairing permutations
with the plus-one rule, all unadjusted. Undefined/tied constants remain
unestimated. Pointwise intervals use the hierarchical bootstrap above, not
naive repeated-observation sampling. Each participant contributes once to each
test. Baseline MAIA is a trait correlate; spatial delta compares two
post-intervention ratings. Preserve all 42 earlier questionnaire correlations
and 16 moderation fits. Report sensitivity of correlations to unregularized,
finer-grid and shared-plateau estimates descriptively, without selecting a
specification by significance. These tests concern fitted proxies; they cannot
establish a latent physiological boundary or mediation.

Before calculating the new correlations, individual fitting exposed identical
408-row behavioural records for P011 and P033 with reversed condition labels
and different questionnaire responses. The correct recording-to-person mapping
is unresolved. Preserve all source rows, flag both fits and all full-release
RT–questionnaire inference as provisional, and repeat RT-only method selection
and all 126 correlations excluding both records, excluding P011, and excluding
P033. These three sensitivities add 378 unadjusted tests, all reported; they
do not identify the correct mapping. Keep linked records together in outer
prediction folds, exclude them together from shape pools, and resample linked
record groups together in the association bootstrap. Within-cell trial noise
is still resampled separately for ambiguous records, so full-release intervals
remain conditional diagnostics. The standalone MAIA–spatial analysis does not
use these RT records. Original behavioural results require provenance review
before treating the release as 42 independent recordings.

After the initial RT-only prediction/recovery pass, the shared-plateau extension
is expanded to the same 500 parameter/association bootstrap draws, split-half
checks and 126 tests in each of the four linkage specifications. This is a
post-results extension, not preregistration or an independent confirmation.
It fulfils the owner's common-plateau normalization request and follows the
shared model's lower prediction error; no result is selected by its questionnaire
p value. Both models remain fully reported (1,008 unadjusted association tests
across models and linkage specifications). Simulations add a shared-plateau
sigmoid-generating scenario, keeping the original flat, linear and
condition-varying-plateau scenarios; each known sigmoid has an 80-ms signed
amplitude and randomly sampled interior grid shapes. This distinguishes recovery
under the added plateau assumption from recovery when it is violated.

## Numerical and browser verification

Profile ML uses Woodbury sufficient statistics, preserving the exact Gaussian
likelihood without constructing a trial-by-trial covariance matrix. Verify
likelihoods/coefficients against statsmodels ML fits and cluster covariance
against its sandwich implementation. Verify repeated-measures and JZS routines
against independent mathematical cases. Record package versions, source hashes,
model convergence, numerical tolerances, and any non-estimable check.

The public workbook downloads the CSVs and runs NumPy/SciPy in Pyodide. It must
execute the real 42-person pipeline in a browser and export results agreeing
with native validation. A precomputed HTML report does not satisfy this goal.

## Evidence boundaries

The CSVs cannot verify waveform timing, belt-based respiratory compliance,
pilot dates, acquisition-version labels, or which two historical participants
had a different RT onset definition. Mark those source-dependent checks as
unavailable; do not infer private metadata from arbitrary IDs. Baseline
subtraction by nominal SOA is not a verified cue-time-matched comparison.
The old 40-person manuscript values must not be relabelled as 42-person results.
New outputs are a reproducible analysis draft for author review, with reporting
reconciled against their exact run.
