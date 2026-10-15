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
  Condition × Phase cells. Gate failure prevents boundary and questionnaire
  inference; five-mean or group curves cannot rescue it.

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
