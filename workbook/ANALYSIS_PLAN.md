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

## Remaining-analysis amendment (post-results, fixed before this extension)

Keep the earlier outputs intact. Resolve the following computational gaps without
choosing specifications by questionnaire significance. This is an exploratory
amendment after the original and individual-proxy results, not preregistration.

1. Recompute cleaning, primary/Control-only numeric and categorical ML models,
   raw/log participant-cluster regressions, equal-person slope contrasts and
   raw-RT repeated-measures ANOVA excluding P011/P033 together and each alone.
   Report all three specifications; exclusion cannot identify the correct mapping.
2. For both individual plateau models, report equal-phase Condition, equal-condition
   Phase and Condition × Phase contrasts for midpoint, normalized steepness and
   signed RT derivative. Reuse the existing full-release hierarchical resamples
   for pointwise intervals on the cohort mean contrasts. Add the same 500
   person-plus-trial refits for each exclusion specification, including all 126
   association intervals per model. These remain conditional on each cohort's
   RT-selected method. Do not add tests to find a significant specification.
   Extend the existing ten split halves and 30 known-signal simulations to all
   three contrasts; distinguish individual-difference recovery from a group effect.
3. On the cohort excluding both ambiguous recordings, compare constant, linear,
   log-distance and broad/visible logistic group responses with the existing
   six-outer/five-inner participant/omitted-position prediction target. The
   log-distance family has the same 160 extraction/smoothing options as the
   linear family; smoothing still uses physical-distance coordinates. This is
   a response-shape comparison, not a replication of expectancy controls.
4. Freeze that cohort's RT-selected visible preprocessing and evaluate nine
   geometry specifications: width floors 2.25/4.5/9 cm crossed with permissive,
   existing and strict criteria. Their (tail fraction, minimum departure from
   line, positions per flank, central fraction) are (.20,.025,1,.10),
   (.10,.05,2,.20), and (.05,.10,2,.30). Report all fits and leave-position errors;
   do not choose a replacement by appearance. Use 30 whole-person resamples
   repeating all 320 visible-method selections, grouping repeated copies during
   validation, as a selection-stability diagnostic. Thirty draws are insufficient
   for tail confidence intervals; report ranges, frequencies and flat fractions.

Use independent seed 20261019 for the added resampling, preserving prior random
streams and outputs. Derived-contrast reliability/recovery ranks round values to
12 decimal places before ranking, as do the fitted scores used in associations:
shared-plateau cancellation otherwise lets
machine-precision noise split mathematical ties across native and browser runtimes.
Point-parameter tables, cohort means and RMSEs retain their original precision.
Existing cleaning remains fixed in group resampling; these
checks do not provide end-to-end forecasting, model-selection-adjusted confidence
coverage, serial-dependence calibration, dense-distance physiological validation,
or missing acquisition provenance. Those limits cannot be removed by smoothing.

## Repeated-measures parameter amendment (post-results)

Goal: answer how all four Condition × Phase fitted PPS profiles differ and how
baseline MAIA-2 dimensions and spatial-rating change relate to midpoint and
sharpness. Freeze this specification before inspecting its results. These are
exploratory ANOVAs/ANCOVAs of fitted proxies, not a replacement for the failed
registered boundary gate or evidence of causal questionnaire influence.

- Outcomes: midpoint in cm and normalized midpoint sharpness, `1/(4*width_cm)`.
  Higher sharpness means a narrower transition. Keep amplitude and signed RT
  derivative separate; affine plateau normalization does not identify a boundary.
- Retain each cohort's existing RT-selected visible fit and both separate/shared
  plateau specifications. The shared model's prior predictive advantage motivates
  reporting it alongside the original fit, not selecting results by significance.
  Emphasise exclusion of both P011/P033 for the new question; report the full
  release and each single exclusion as explicit sensitivities.
- For each outcome, fit the complete 2×2 within-person ANOVA: Condition, Phase,
  and Condition × Phase. These one-df effects need no sphericity correction.
- Fit each of the eight continuous baseline MAIA-2 dimensions separately as a
  between-person covariate; fit numerical spatial-code delta separately. Do not
  dichotomise scales or fit all eight simultaneously in this small sample.
  The spatial direction (−1/0/+1) is an ordinal-spacing sensitivity, not a second
  independent outcome or manipulation. Spatial delta is not a baseline mediator.
- Use four orthogonal participant summaries: four-cell mean, Viscereality−Control
  averaged across phases, Inhale−Exhale averaged across conditions, and the
  difference of those phase effects. Regress each on the centred covariate, with
  and without centred presentation order. Covariate slopes give the between-person
  main effect and the Condition/Phase/interaction moderation terms of the balanced
  RM ANCOVA. The Condition slope is the main change-to-change question for spatial
  ratings. All four cells contribute; phase is never collapsed out of the model.
- Report beta, classical F=t², df, unadjusted p, partial eta² and HC3 sensitivity.
  These condition on fitted outcomes and do not account for shared-pool or curve
  uncertainty. Attach 95% percentile intervals from the existing 500 hierarchical
  person/group-plus-trial curve refits in every cohort/model, including all model
  slopes. Keep the selected method/cleaning fixed; count undefined resamples.
  No multiplicity correction, selection on p, or claim of calibrated coverage.
- Retain 6 ANOVA terms and 160 covariate terms per plateau model/cohort: 1,328
  nominal tests overall, with HC3 as a sensitivity of the same covariate tests.
  Primary presentation uses both-excluded ANOVAs and order-adjusted Condition
  moderation by the eight MAIA dimensions and spatial delta; the full family is
  downloadable. Missing predictors are excluded per model, never imputed.
- Validate ANOVAs with statsmodels AnovaRM and all regression/HC3 terms with
  independent OLS references; test effect signs, known interactions, invariance to
  participant offsets, missingness, constant predictors and refit interval counts.
  Compare every result across native/Pyodide and reconcile the paper and figures.

The previous poor parameter/change reliability remains part of the answer.
Partial pooling can produce small conventional ANOVA standard errors despite
uncertain cohort-level curve shifts; refit intervals must accompany those tests.
No result can repair the missing source mapping or prove a physiological boundary.

## Condition-matched spatial ratings and PPS parameters (post-results)

The owner requested a direct association analysis matching the spatial rating
from each intervention to that condition's Exhale/Inhale PPS estimates. Fix this
amendment before computing its results. It follows inspection of earlier delta
analyses and remains exploratory. PPS outcomes are fitted midpoint (cm) and
normalized sharpness, not an additional subjective PPS questionnaire.

- Retain the four fitted cells per person, existing RT-selected methods, both
  plateau models and all four recording-linkage cohorts. The main presentation
  excludes both ambiguous recordings. Do not use questionnaire outcomes to
  select a curve, cleaning rule, cohort or smoothing method.
- For each of the four cells and each outcome, correlate the parameter with
  the spatial rating from that same condition using Spearman ranks and 19,999
  two-sided pairing permutations. Each test contains one observation per person;
  the two phase estimates sharing a spatial rating are not independent people.
- Separate between-person spatial level, the mean of the two condition ratings,
  from within-person spatial change, Viscereality minus Control. In the balanced
  repeated-measures decomposition, regress the four-cell PPS mean and Phase
  contrast on mean spatial rating; regress the Condition and Condition × Phase
  contrasts on spatial change. This estimates the between-person association,
  its phase dependence, the within-person association after allowing an average
  condition effect, and its phase dependence. The latter two reuse the already
  specified spatial-delta models rather than supplying independent replication.
  Report each with and without centred presentation order, classical and HC3
  uncertainty. Numerical means/differences assume comparable category steps;
  the cell-specific rank analyses and existing direction-only models provide
  complementary ordinal sensitivities.
- Attach 95% percentile intervals using the same 500 person/linked-record-group
  plus within-cell trial resamples and refitted curves in each cohort. Count
  undefined draws. Keep all prior random streams unchanged; use a separate
  permutation stream seeded 20261020 for the added correlations. Method selection,
  original cleaning, serial dependence and uncertainty in the rating instrument
  are not calibrated by these conditional intervals.
- Export 64 cell correlations and 128 regression coefficient records across
  cohorts/models: 192 estimates, including 64 reused within-change coefficients.
  Thus 128 tests are added, not 192 independent new hypotheses. All p values are
  unadjusted. Missing rating pairs remain missing; use complete pairs for the
  within/between decomposition and available condition ratings for cell ranks.
- Independently check ranks with SciPy, regression/HC3 with statsmodels, and
  coefficient identities against a long-format within/between design. Test
  opposite known within/between effects, phase interactions, participant-offset
  cancellation, missingness, constant ratings and all refit counts. Compare all
  new fields across native/Pyodide. Display the main cell associations and model
  slopes with refit intervals and update the publication draft from the browser
  download.

These are associations of post-intervention experience and uncertain fitted PPS
proxies. They do not establish mediation, causal direction or a physiological
boundary. Neither spatial ratings nor MAIA scores are data-quality exclusions.

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

## Results-only Bayesian approximation (post-results, 17 October 2026)

Manuscript drafting is paused at the owner's request. The ordered questions and
completion criteria are in `for-ai/ANALYSIS_ROADMAP.md`; retain the existing
version-1.9 full analysis/reference and add a separately executable browser branch.
Fix the following before computing this branch. It is exploratory and unpooled,
not the preregistered model or a fully hierarchical nonlinear analysis.

1. Reuse validated inputs, `clean`, nominal distances and the four-cell trial
   tensor. Fit raw retained Audio–Tactile RTs in seconds, without smoothing or
   normalization in the likelihood. Keep both ambiguous recordings in the audit
   table; primary inference excludes both, with full and each single exclusion
   retained. With unpooled priors, excluding other people cannot change a person's
   fit; subset the same draws for cohort comparisons rather than refit identical
   individual models. Never borrow questionnaire information during fitting.
2. Working likelihood: independent Gaussian trial RTs within each person/cell,
   `RT(d) = b + a*(expit((u-m)/w)-.5) + error`, `u=(d-10)/90`. Amplitude is signed
   and may be zero. A common residual variance within that cell is an explicit
   assumption, not a claim of assumption-free Bayesian inference. Original
   trimming and unmodelled trial dependence/heteroskedasticity remain limitations.
3. Proper nuisance prior: `variance ~ InvGamma(shape=2, scale=.02 s²)` and
   `(b,a)|variance ~ Normal((.6,0), variance*diag(4,4))`. Constant models keep only
   the same intercept prior; line and log-distance models use centered bases
   ranging from −.5 to +.5 and the same signed-amplitude prior. Integrate nuisance
   coefficients and variance analytically using normal–inverse-gamma conjugacy.
4. Four predeclared sigmoid priors, none selected by p or appearance: primary
   uniform midpoint `m in [-.5,1.5]`, log-uniform width `w in [.025,2]`; a doubled
   support prior `m in [-1,2], w in [.0125,4]`; a width-concentrated sensitivity
   with the primary support and `log(w) ~ Normal(log(1/6), log(3))`; and a
   wider-nuisance sensitivity with the primary shape support and `diag(16,16)`.
   Primary grids have 81 midpoint × 61 log-width nodes with trapezoid weights;
   repeat every primary individual posterior on 161 × 121 nodes. Report grid
   support/boundary mass, marginal and joint prior-to-posterior KL information,
   prior-predictive negative-RT probability and noise ranges. No visible-shape
   truncation or positive amplitude floor is allowed.
5. Compare constant, linear, log-distance and sigmoid responses using equal prior
   model probabilities (explicitly model/prior-dependent). Refit each held-out
   distance and compare exact block log-predictive density and raw cell-mean RMSE.
   Use equal participant/cell/distance weights for RMSE; retain all model scores.
   Predictive comparison is exploratory and conditional on fixed earlier cleaning.
6. Draw 2,000 joint parameter samples per person/cell/prior, seed 20261021.
   Report midpoint, width, normalized sharpness `1/(4*width_cm)`, signed amplitude,
   interval, posterior positive-amplitude probability, posterior measured-range
   10–90% coverage and predictive discrepancy. A posterior median is a declared
   absolute-loss point summary, not an assertion of a unique best-fitting curve.
   Do not replace a mixture/posterior mean curve by a sigmoid fit to plotted points.
7. For the primary prior, add ten stratified random split halves and 20 simulation
   replicates each under flat, linear and known 80-ms sigmoid signals, using the
   observed counts/noise scales and the declared Gaussian likelihood. These are
   within-session/matched-likelihood diagnostics, not test–retest reliability or
   calibration under every data-generating process. Keep unsuccessful recovery.
8. For all four priors/cohorts, carry draws into paired Condition, Phase and
   Condition × Phase contrasts. Report both the finite-cohort posterior contrast
   and posterior plus paired Bayesian-bootstrap (Dirichlet) participant-weight
   intervals/probabilities. The latter is a modular descriptive population
   sensitivity, not a jointly estimated hierarchical treatment-effect posterior.
9. Preserve the old tests. New exploratory rank associations cover both parameters
   against all eight baseline MAIA scales in the four cells and Condition contrast,
   parameter Condition changes against spatial delta and its direction, and
   same-condition spatial ratings in four cells: 92 per prior/cohort. Report
   posterior-plus-paired-participant-bootstrap rank intervals (resampled copies
   retain the same sampled latent parameter), not p values on exact medians.
10. For each MAIA scale separately, regress each of the four orthogonal PPS
    summaries (mean, Condition, Phase, Condition × Phase) on centered MAIA,
    centered spatial delta, their product, and centered presentation order. Keep
    missing pairs excluded. Report all three scientific coefficients for each
    outcome: 192 coefficient records per prior/cohort. Propagate the same latent
    draws and paired Bayesian-bootstrap weights through weighted least squares;
    label intervals/probabilities modular, not a full latent-covariate posterior.
    The product on the Condition summary addresses Condition × MAIA × spatial
    change; on the interaction summary it additionally depends on Phase. No
    causal mediation or questionnaire-driven cleaning is inferred.
11. Plot equal-person posterior average RT functions with observed means and
    uncertainty, midpoint/sharpness summaries, and every raw/normalized individual
    curve. Display normalized sigmoid geometry as conditional model geometry;
    finite midpoint and sharpness estimates remain interpretable only under the
    imposed sigmoid model. Inspect every page and propagate uncertainty in the
    average curves. Publish a results-only report with checklist status, precise
    comparisons and explicit unresolved scientific goals, without editing paper
    prose or promoting a new manuscript PDF.
12. Independently check conjugate marginal likelihood and prediction with a
    multivariate Student-t reference, coefficient identities, missingness and
    synthetic effects. Verify native/browser numerical parity and an actual
    browser download; hash all new inputs/code/artifacts. Keep version-1.9 code,
    reference ZIP, paper sources and PDF byte-identical.

All older frequentist p values remain unadjusted. New posterior probabilities and
modular intervals are not p values, familywise guarantees or proof of equivalence.
A full joint hierarchical nonlinear/covariate model has not been run unless it is
separately specified, executed and diagnosed; this extension does not imply one.

Bayesian resampling clarification, fixed before the first run: repeated copies
of an audited identical recording share the same posterior cell draws (with the
observed label permutation) and share resampling weights. Group/regression weights
are exponential draws per recording group; rank associations use multinomial
recording-group counts and weighted midranks, exactly equivalent to expanding the
paired bootstrap records. This retains ties and does not count duplicate trials
as independent evidence. Source mapping remains unresolved; primary inference
still excludes both records.

### Requested conventional tests of Bayesian point estimates

After reviewing the uncertainty-propagating results, the owner requested ordinary
statistical tests treating each Bayesian approximation as one fixed observation.
Use the existing marginal posterior medians of midpoint and normalized sharpness
from `shape_summary`, separately for every participant × condition × phase. This
is a post-results exploratory addition, with no new fit, smoothing, transformation,
fit-quality exclusion, posterior weighting or choice of prior by significance.
The existing primary prior and 40-record cohort remain primary.

Run a balanced 2 × 2 repeated-measures ANOVA for each parameter. Calculate each
one-df effect through its participant contrast: Condition = Viscereality−Control
averaged across phases; Phase = Inhale−Exhale averaged across conditions; interaction
= (Viscereality Inhale−Exhale)−(Control Inhale−Exhale). For each effect, F=t² with
df=(1,n−1); retain mean contrast, conventional 95% t interval, SE, F, unadjusted p
and partial η². Sphericity corrections are unnecessary for these two-level terms.
Normality diagnostics do not select a different test or cohort. These intervals
omit within-cell posterior uncertainty, by design, and are distinct from the
earlier posterior/bootstrap intervals and the regularized-fit ANOVAs.

Retain all four prior and four cohort specifications (96 effect records). The
full cohort still contains the two linked recording copies and is provisional;
its ordinary independent-participant standard errors do not resolve that issue.
Verify every F/p/df against statsmodels AnovaRM and verify actual browser/native
parity. Export `bayesian_point_estimate_anova.csv` in the Bayesian results download
and display the six primary terms in the workbook/report. Do not select a point
summary or fitting method to obtain significance.

## Baseline-corrected model comparison goal (18 October 2026)

The owner now prioritizes baseline-corrected responses and all three experimental
effects: Inhale−Exhale, Viscereality−Control and their interaction. This is a
post-results goal/specification amendment, not a preregistration or a completed
analysis. It extends the pending joint hierarchy; it does not change the previously
published raw-RT Bayesian branch or the preserved manuscript. Numerical fitting
settings, a finite specification registry and executable/browser checks remain to
be completed before these new effect tests. The source rationale and access record
are in [the literature review](../literature_review/README.md).

### Correction and measurement target

1. Primary corrected trial response is `Y_i,c,p,j = AT_RT_i,c,p,j − B_i,c,p`, in ms,
   where `B_i,c,p` is the arithmetic mean of all retained Baseline hit RTs from the
   same participant, intervention and breathing phase, pooling nominal SOAs.
   Apply this to all four cells. Negative values mean faster responses than that
   baseline; preserve negative values and zero. Control is an experimental
   condition, not a substitute for the Baseline trial type. Keep source RTs intact.
2. Reuse the fixed participant-wide cleaning rule on raw RTs before subtraction,
   including both trial types in its thresholds. Do not retrim, log-transform,
   floor, take absolute values or min–max scale corrected values to obtain a result.
   The primary cohort excludes both P011/P033; retain the three linkage sensitivities.
3. Same-nominal-SOA subtraction `AT_RT_i,c,p,j − B_i,c,p,SOA(j)` is a separate
   sensitivity. It is not a verified cue-time-matched expectancy correction.
   The retained primary cohort has 8,478 AT and 4,192 Baseline trials, all 800
   person/condition/phase/SOA cells present per trial type; each Baseline cell
   has only 1–6 trials, versus 10–30 per person/condition/phase baseline pool.
   Do not estimate a variance from a singleton or silently impute a missing cell.
4. Baseline means are estimated measurements. Reusing one mean across many AT
   trials induces shared subtraction error. Carry both data sources through a
   joint likelihood or resample Baseline and AT observations with participant
   pairing intact, recomputing the correction in every refit. Sparse-cell and
   serial-dependence assumptions require explicit handling; a singleton bootstrap
   alone cannot quantify that baseline mean's sampling uncertainty.
5. A joint raw-trial likelihood is permitted as an implementation of the corrected
   estimand: for the primary correction, model `E(Baseline)=B_i,c,p` and
   `E(AT|d)=B_i,c,p + g_i,c,p(d)`, and report `g(d)` in corrected ms. Give `g` a free
   intercept and signed amplitude; do not force its far plateau to zero. A
   same-label sensitivity permits baseline variation over nominal SOAs and derives
   the corresponding AT−Baseline response. Merely fitting AT with an intercept,
   without incorporating measured Baseline trials, is not this joint correction.
6. With a free intercept and translated bounds/priors where applicable, subtracting
   a scalar baseline shifts the curve vertically without changing its midpoint,
   width or distance slope. Verify this invariant. Common-plateau normalization
   is a different assumption. Any shape change after a scalar subtraction must
   be traced to constraints, pooling or priors rather than called new data evidence.

### Model and estimand registry to implement

| Family | Quantities and experimental tests | Role and limitation |
| --- | --- | --- |
| Constant corrected response | Overall facilitation and Condition/Phase/interaction effects on its level | Null distance comparator; an RT level effect is not a boundary change |
| Linear distance, `g(d)=a+b*d` | Signed slope in ms/cm and its Condition/Phase/interaction contrasts | Required alternative; no intrinsic PPS midpoint or plateau sharpness |
| Log distance, `g(d)=a+b*log(d/d_ref)` | Signed log-distance slope, derivative `b/d` at fixed design distances, and the three contrasts | Required alternative motivated by Hobeika et al.; `d_ref=50 cm` fixes units, not a fitted boundary; not log RT |
| Ordinary logistic, `g(d)=a+A*(expit((d-m)/w)−.5)` | Midpoint `m`, width `w>0`, normalized sharpness `1/(4*w)` and all three experimental effects | Main nonlinear family; signed amplitude may be zero; report identification and prior/bound sensitivity |
| Literature fixed-extrema logistic | Same targets, fixing asymptotes to the minimum/maximum of the five unsmoothed distance means as in Canzoneri et al. | Required labelled sensitivity; permit either orientation, recompute extrema in refits and do not count them as known constants |
| Other screened sigmoid families | Probit, log-logistic and asymmetric Gompertz candidates; compare 50%-of-amplitude location and normalized derivative there | Generic response-function sensitivities until direct PPS use is verified; native parameters/inflections are not interchangeable with logistic midpoint/width |
| Flexible distance response | Categorical distance and a bounded low-complexity smooth/segmented candidate, subject to identifiability with five distances | Shape check; no automatic sigmoid boundary; register smoothing/segment constraints and any threshold before fitting |

Retain the registered-distance axis and existing trajectory-coordinate sensitivity;
do not choose coordinates by p. Register the exact usable combinations and reasons
for excluded/redundant combinations rather than blindly crossing every setting.
Smooth and unsmoothed variants must predict the same unsmoothed target, using
validation confined to training observations. The prior local smoothing audit
is existing evidence, not a new baseline-corrected result.

Across families also report the same five-distance average corrected RT and
far-minus-near contrast `g(100 cm)−g(10 cm)` on the primary registered axis, with all
three experimental contrasts. Use the corresponding sampled 20–100 cm endpoints
for the trajectory-axis sensitivity, not an extrapolated 10-cm response.
These are observed-range response estimands, not substitutes for a physiological
boundary. For sigmoid alternatives, derive a common 50%-amplitude location and
normalized derivative analytically/numerically; do not compare unlike scale
parameters or manufacture a midpoint for a line/logarithm. Do not divide observations
by an uncertain fitted amplitude. Flag weakly identified shape parameters in flat
profiles and report any undefined amplitude-normalized ratios explicitly.

### Inference, prioritization and completion

- Bayesian: jointly fit baseline, four individual curves and population Condition,
  Phase and interaction effects with participant partial pooling. Include the
  corresponding constant/linear/log-distance hierarchies. Fix numerical proper
  priors, random effects, likelihoods and finite sensitivities before fitting;
  include a robust real-valued likelihood for corrected RT as a sensitivity.
  A positive-support model can instead describe original RTs and derive mean
  differences; it cannot be applied directly to signed corrected values.
- Frequentist: nonlinear likelihood/mixed estimation for sigmoid parameters;
  linear mixed/repeated-measures estimation for distance/log-distance slopes and
  response levels, keeping all required lower-order terms. Respect participant
  dependence. Pair parameter contrasts for RM ANOVA/t tests, with separate
  baseline-and-curve-refit uncertainty; these algebraically equivalent tests are
  one result, not independent confirmations. Assess weak identification with
  profiles and null-based parametric bootstrap instead of assuming regular
  chi-square asymptotics at flat/boundary fits. Whole-person/within-person
  resampling, robust covariance and valid sign-flip tests are declared sensitivities,
  with their exchangeability/symmetry assumptions and limitations recorded.
- For both approaches, check observed-range prediction against a constant,
  linear and logarithmic curve, known-effect and null recovery, baseline uncertainty,
  split-half reliability, prior/constraint influence, convergence and failed fits.
  Preserve the earlier fixed cleaning and its held-out-validation limitation.
  Distinguish finite-cohort contrasts, population coefficients and nonlinear
  back-transformations; report original-unit contrasts as well as log-sharpness
  ratio summaries. Smoothing or partial pooling is not additional observed signal.
- For each target, report the average Condition and Phase effects, their direct
  difference-of-differences interaction, and simple effects in both directions.
  Significance in one cell and its absence in another is not an interaction test.
  Keep all frequentist p values unadjusted as requested and report the total family.
  Report pointwise 95% confidence/credible intervals, effect sizes, posterior
  directional probabilities and explicit Bayes-factor hypotheses/priors where
  computed. Neither an unadjusted p nor a posterior sign probability accounts
  automatically for searching across specifications.
- Deliver a complete model/effect inventory and results-first summary, highlighting
  relevant nominal findings with their actual uncertainty, baseline scheme, cohort
  and diagnostics. Separate stability across reasonable specifications from
  selection-dependent findings; correlated specifications are not replications.
  Preserve null, opposite, nonidentified and failed results. Finish the declared
  finite worklist and document literature/access/feasibility gaps regardless of
  significance. Additional methods need a scientific reason and dated amendment.
- Completion requires independent numerical checks, actual browser execution and
  download, all corrected/raw/normalized figures inspected, full results publication
  and updated checklist/report. The current amendment records a goal; it claims
  no new model fit, significant effect, browser computation or physiological boundary.
