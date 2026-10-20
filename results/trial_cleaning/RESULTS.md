# Trial distributions, local SD filtering, fatigue and rolling-average rerun

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

| period | filter | cohort | AT | Baseline | missing_AT_distance_cells | missing_Baseline_distance_cells |
| --- | --- | --- | --- | --- | --- | --- |
| full | global | primary40 | 8478 | 4192 | 0 | 0 |
| full | local | primary40 | 8407 | 4192 | 0 | 0 |
| early | global | primary40 | 4299 | 2133 | 0 | 1 |
| early | local | primary40 | 4299 | 2133 | 0 | 1 |

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

| model | gate | divergences | max_rhat | min_bulk_ess | min_tail_ess |
| --- | --- | --- | --- | --- | --- |
| full_raw_broad | True | 0 | 1.008 | 564.6 | 1162 |
| full_raw_visible95 | True | 0 | 1.008 | 717 | 848.3 |
| full_roll_broad | False | 0 | 1.012 | 378.3 | 705.7 |
| full_roll_visible95 | False | 0 | 1.007 | 244.6 | 732.1 |
| early_raw_broad | False | 0 | 1.015 | 365 | 653.4 |
| early_raw_visible95 | True | 0 | 1.005 | 714 | 882.6 |
| early_roll_broad | False | 0 | 1.011 | 648.5 | 1765 |
| early_roll_visible95 | True | 0 | 1.009 | 498.4 | 597.3 |

Every main parameter contrast (95% equal-tail credible interval):

| model | quantity | term | posterior_median | ci_low | ci_high | probability_positive | gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| full_raw_broad | midpoint_cm_effect | Condition | -2.544 | -60.77 | 56.53 | 0.4623 | True |
| full_raw_broad | midpoint_cm_effect | Phase | 6.069 | -63.17 | 58.68 | 0.5845 | True |
| full_raw_broad | midpoint_cm_effect | Condition × Phase | -5.813 | -78.45 | 65.01 | 0.4303 | True |
| full_raw_broad | sharpness_per_cm_effect | Condition | 0.0003135 | -0.0096 | 0.01207 | 0.5516 | True |
| full_raw_broad | sharpness_per_cm_effect | Phase | -0.0009749 | -0.01134 | 0.01094 | 0.3476 | True |
| full_raw_broad | sharpness_per_cm_effect | Condition × Phase | -0.0001489 | -0.01526 | 0.01326 | 0.4815 | True |
| full_raw_visible95 | midpoint_cm_effect | Condition | 0.5433 | -10.39 | 10.71 | 0.5613 | True |
| full_raw_visible95 | midpoint_cm_effect | Phase | -2.337 | -13.35 | 7.296 | 0.2867 | True |
| full_raw_visible95 | midpoint_cm_effect | Condition × Phase | -5.025 | -22.7 | 5.936 | 0.2006 | True |
| full_raw_visible95 | sharpness_per_cm_effect | Condition | 0.002369 | -0.01238 | 0.03268 | 0.6805 | True |
| full_raw_visible95 | sharpness_per_cm_effect | Phase | -0.0001721 | -0.01412 | 0.03712 | 0.4773 | True |
| full_raw_visible95 | sharpness_per_cm_effect | Condition × Phase | -0.002157 | -0.02749 | 0.03273 | 0.36 | True |
| full_roll_broad | midpoint_cm_effect | Condition | -0.4115 | -58.03 | 56 | 0.4931 | False |
| full_roll_broad | midpoint_cm_effect | Phase | 6.832 | -64.63 | 57.32 | 0.6048 | False |
| full_roll_broad | midpoint_cm_effect | Condition × Phase | -5.32 | -76.63 | 65.06 | 0.4336 | False |
| full_roll_broad | sharpness_per_cm_effect | Condition | 0.0007773 | -0.01057 | 0.0164 | 0.6064 | False |
| full_roll_broad | sharpness_per_cm_effect | Phase | -0.00131 | -0.01457 | 0.01263 | 0.3261 | False |
| full_roll_broad | sharpness_per_cm_effect | Condition × Phase | -0.000354 | -0.01989 | 0.01551 | 0.4604 | False |
| full_roll_visible95 | midpoint_cm_effect | Condition | 0.4791 | -14.31 | 13.37 | 0.5279 | False |
| full_roll_visible95 | midpoint_cm_effect | Phase | -4.177 | -17.56 | 7.437 | 0.2369 | False |
| full_roll_visible95 | midpoint_cm_effect | Condition × Phase | -11.42 | -33.54 | 4.129 | 0.08125 | False |
| full_roll_visible95 | sharpness_per_cm_effect | Condition | 0.01378 | -0.01762 | 0.05492 | 0.791 | False |
| full_roll_visible95 | sharpness_per_cm_effect | Phase | 0.00687 | -0.02219 | 0.05489 | 0.6431 | False |
| full_roll_visible95 | sharpness_per_cm_effect | Condition × Phase | -0.009386 | -0.05011 | 0.03353 | 0.3079 | False |
| early_raw_broad | midpoint_cm_effect | Condition | -10.06 | -71.04 | 69.61 | 0.3655 | False |
| early_raw_broad | midpoint_cm_effect | Phase | -1.517 | -64.73 | 63 | 0.4773 | False |
| early_raw_broad | midpoint_cm_effect | Condition × Phase | -9.855 | -80.69 | 66.79 | 0.3924 | False |
| early_raw_broad | sharpness_per_cm_effect | Condition | 0.001595 | -0.02998 | 0.05505 | 0.6566 | False |
| early_raw_broad | sharpness_per_cm_effect | Phase | -0.0002752 | -0.04366 | 0.03914 | 0.4619 | False |
| early_raw_broad | sharpness_per_cm_effect | Condition × Phase | 0.0001131 | -0.04938 | 0.0553 | 0.5122 | False |
| early_raw_visible95 | midpoint_cm_effect | Condition | 6.592 | -5.454 | 20.69 | 0.8461 | True |
| early_raw_visible95 | midpoint_cm_effect | Phase | 1.715 | -11.02 | 15.27 | 0.6106 | True |
| early_raw_visible95 | midpoint_cm_effect | Condition × Phase | -0.7946 | -16.48 | 13.99 | 0.4529 | True |
| early_raw_visible95 | sharpness_per_cm_effect | Condition | 0.01392 | -0.01497 | 0.04869 | 0.8334 | True |
| early_raw_visible95 | sharpness_per_cm_effect | Phase | 0.006344 | -0.02074 | 0.04263 | 0.674 | True |
| early_raw_visible95 | sharpness_per_cm_effect | Condition × Phase | 0.002344 | -0.03362 | 0.04262 | 0.5653 | True |
| early_roll_broad | midpoint_cm_effect | Condition | -6.231 | -74.03 | 75.46 | 0.4223 | False |
| early_roll_broad | midpoint_cm_effect | Phase | 0.2173 | -72.55 | 71.98 | 0.5033 | False |
| early_roll_broad | midpoint_cm_effect | Condition × Phase | -4.61 | -83.81 | 75.33 | 0.4527 | False |
| early_roll_broad | sharpness_per_cm_effect | Condition | 0.0008832 | -0.02453 | 0.04493 | 0.6478 | False |
| early_roll_broad | sharpness_per_cm_effect | Phase | -0.0003825 | -0.03822 | 0.02842 | 0.4277 | False |
| early_roll_broad | sharpness_per_cm_effect | Condition × Phase | -0.0002015 | -0.04563 | 0.03767 | 0.4695 | False |
| early_roll_visible95 | midpoint_cm_effect | Condition | 3.354 | -10.21 | 17.11 | 0.7002 | True |
| early_roll_visible95 | midpoint_cm_effect | Phase | -1.476 | -16.84 | 13.8 | 0.4161 | True |
| early_roll_visible95 | midpoint_cm_effect | Condition × Phase | -6.704 | -24.86 | 8.314 | 0.1936 | True |
| early_roll_visible95 | sharpness_per_cm_effect | Condition | 0.007939 | -0.02831 | 0.04574 | 0.7036 | True |
| early_roll_visible95 | sharpness_per_cm_effect | Phase | 0.001669 | -0.02917 | 0.0479 | 0.5504 | True |
| early_roll_visible95 | sharpness_per_cm_effect | Condition × Phase | -0.009928 | -0.05214 | 0.03225 | 0.2929 | True |

**0/48** main parameter intervals exclude zero.
These are joint finite-cohort posterior contrasts, not ANOVAs on pooled point
estimates. A nonzero interval is conditional on its likelihood, priors, selection
and diagnostic status; it is not automatic physiological validation. Model failures
remain inconclusive. Population coefficients, all simple effects and response
contrasts remain exported separately. No multiplicity correction or joint-model
Bayes factor was introduced. Priors and numerical budgets were fixed before fits.

## Does fitting look better?

| model | cells | trial_R2_ge_05 | five_mean_R2_ge_05 | rolling_R2_ge_05 | median_midpoint_interval_cm |
| --- | --- | --- | --- | --- | --- |
| early_raw_broad | 160 | 0 | 3 | 6 | 270.5 |
| early_raw_visible95 | 160 | 0 | 25 | 35 | 44.18 |
| early_roll_broad | 160 | 0 | 2 | 7 | 290 |
| early_roll_visible95 | 160 | 0 | 24 | 39 | 64.47 |
| full_raw_broad | 160 | 0 | 17 | 25 | 259.1 |
| full_raw_visible95 | 160 | 0 | 36 | 47 | 39.29 |
| full_roll_broad | 160 | 0 | 18 | 27 | 251.3 |
| full_roll_visible95 | 160 | 0 | 44 | 52 | 59.04 |

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

| quantity | complete_participants | estimate | ci_low | ci_high | p |
| --- | --- | --- | --- | --- | --- |
| AT_RT_time_slope_ms | 40 | 1.539 | -14.35 | 17.43 | 0.8457 |
| AT_late_minus_early_RT_ms | 40 | 1.818 | -6.245 | 9.882 | 0.6508 |
| AT_late_minus_early_SD_ms | 40 | -4.384 | -9.221 | 0.4535 | 0.07444 |
| AT_late_minus_early_miss_rate | 40 | 0.02557 | 0.001442 | 0.0497 | 0.03837 |
| Baseline_RT_time_slope_ms | 40 | 8.785 | -9.514 | 27.08 | 0.3375 |
| Baseline_late_minus_early_RT_ms | 40 | 4.06 | -5.982 | 14.1 | 0.4185 |
| Baseline_late_minus_early_SD_ms | 39 | 3.26 | -4.213 | 10.73 | 0.3827 |
| Baseline_late_minus_early_miss_rate | 40 | 0.03207 | -0.0001698 | 0.06431 | 0.05116 |
| Catch_late_minus_early_false_alarm_rate | 40 | -0.002292 | -0.01316 | 0.008572 | 0.6719 |

The complete 36 contrasts are in `time_trend_tests.csv`. A time trend can reflect
practice, stimulus/block differences or fatigue; these observational checks do not
establish its cause or authorize selective later-trial deletion. `time_course.png`
shows recorded block trends. The early sensitivity is reported regardless of its
R² or effect estimates.

Recomputed registered-form raw-AT mixed tests (exploratory new-cleaning sensitivities):

| dataset | name | status | lr | df | p |
| --- | --- | --- | --- | --- | --- |
| full_local | full_factorial | computed | 0.003307 | 1 | 0.9541 |
| full_local | full_control | computed | 1.124 | 1 | 0.289 |
| early_local | early_factorial | computed | 1.202 | 1 | 0.2728 |
| early_local | early_control | computed | 1.133 | 1 | 0.2871 |

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

| model | held_distance_cm | RMSE_ms | log_predictive_score | gate |
| --- | --- | --- | --- | --- |
| global_raw | 10 | 64.86 | 713.4 | True |
| global_raw | 27 | 52.65 | 813.8 | True |
| global_raw | 50 | 57.1 | 858.2 | True |
| global_raw | 73 | 52.04 | 1025 | True |
| global_raw | 100 | 69.47 | 691.3 | True |
| local_raw | 10 | 66.05 | 659.5 | True |
| local_raw | 27 | 53.84 | 764.7 | True |
| local_raw | 50 | 57.27 | 823.9 | True |
| local_raw | 73 | 52.19 | 997.8 | True |
| local_raw | 100 | 69.14 | 652 | True |
| local_roll | 10 | 66.26 | 640.8 | True |
| local_roll | 27 | 57.28 | 742.2 | True |
| local_roll | 50 | 57.51 | 831.5 | True |
| local_roll | 73 | 55.8 | 980.7 | True |
| local_roll | 100 | 69.76 | 651.3 | True |

| model | RMSE_ms | log_predictive_score | all_predictive_gates |
| --- | --- | --- | --- |
| global_raw | 59.62 | 4102 | True |
| local_raw | 60.07 | 3898 | True |
| local_roll | 61.58 | 3847 | True |

All final predictive gates: **True**. If any
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
