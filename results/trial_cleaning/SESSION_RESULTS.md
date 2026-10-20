# Main adjustment: continuous session-wide RT trend and PPS

The owner clarified that Control and Viscereality occurred consecutively in one
sitting. **Early blocks of each intervention do not control accumulated time.**
The early subset remains a smaller-trial sensitivity in `RESULTS.md`; it is not a
fatigue exclusion. This subsequent exploratory amendment was specified before its
five fits in `session_specification.json`, after inspecting the earlier results.

The computed readout is **0/30** nonzero main parameter
intervals, including **0/24** in fits passing
the full convergence gate. Time control has not established a Condition, Phase or
interaction effect on midpoint or sharpness. Forced visible-S geometry remains
a conditional approximation; the mean-profile checks below assess its adequacy
separately from sampling convergence.

## What changed

Use original global trial indices 1–408, spanning parts 1–204 and 205–408, with
`u=(trial_index-1)/(planned_trials-1)-.5`. Do not reset time by condition or
renormalize after trimming/holding out trials. Recorded trial order is a proxy,
not verified elapsed time. Intervention order remains balanced, 20 per sequence.

Each participant has a shared additive RT trend in BOTH AT and Baseline models.
The main trend is linear; quadratic/raw/broad is a fixed sensitivity. Population
coefficients have Normal(0,.2 seconds) priors and participant SDs HalfNormal(.15),
with noncentered participant variation. Signs are unrestricted. Baseline,
intercept/amplitude and shape priors match the preceding sensitivity battery.

This is joint estimation, not fixed-slope preprocessing. Exact within-distance
RT/time cross-products preserve each retained trial's timing. Trend uncertainty
propagates to the four curves, boundary/sharpness and paired contrasts. Rolling
candidates retain the transformed model and overlap covariance. Cutoffs were
not reselected after estimating drift. The corrected function is evaluated at a
common session reference; ideal same-time AT-minus-Baseline cancels shared drift.

## Diagnostics and experimental parameter contrasts

| model | gate | max_rhat | min_bulk_ess | min_tail_ess | divergences |
| --- | --- | --- | --- | --- | --- |
| session_linear_raw_broad | False | 1.011 | 424.9 | 1104 | 0 |
| session_linear_roll_broad | True | 1.006 | 502.7 | 815.5 | 0 |
| session_linear_raw_visible95 | True | 1.007 | 829.3 | 958.8 | 0 |
| session_linear_roll_visible95 | True | 1.004 | 454.9 | 791.3 | 0 |
| session_quadratic_raw_broad | True | 1.01 | 420.2 | 865 | 0 |

All six main contrasts per model, with 95% credible intervals:

| model | quantity | term | posterior_median | ci_low | ci_high | probability_positive | gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| session_linear_raw_broad | midpoint_cm_effect | Condition | -3.279 | -61.99 | 55.11 | 0.448 | False |
| session_linear_raw_broad | midpoint_cm_effect | Phase | 4.113 | -67.03 | 57.12 | 0.5601 | False |
| session_linear_raw_broad | midpoint_cm_effect | Condition × Phase | -7.308 | -80.75 | 62.39 | 0.4158 | False |
| session_linear_raw_broad | sharpness_per_cm_effect | Condition | 0.0002511 | -0.009326 | 0.01233 | 0.5431 | False |
| session_linear_raw_broad | sharpness_per_cm_effect | Phase | -0.0009812 | -0.01112 | 0.01138 | 0.3481 | False |
| session_linear_raw_broad | sharpness_per_cm_effect | Condition × Phase | -6.59e-05 | -0.01531 | 0.0131 | 0.4927 | False |
| session_linear_roll_broad | midpoint_cm_effect | Condition | -0.1847 | -55.28 | 55.54 | 0.4966 | True |
| session_linear_roll_broad | midpoint_cm_effect | Phase | 7.459 | -65.52 | 57.71 | 0.6111 | True |
| session_linear_roll_broad | midpoint_cm_effect | Condition × Phase | -5.99 | -77.62 | 61.16 | 0.4274 | True |
| session_linear_roll_broad | sharpness_per_cm_effect | Condition | 0.0009423 | -0.01189 | 0.01704 | 0.617 | True |
| session_linear_roll_broad | sharpness_per_cm_effect | Phase | -0.00132 | -0.01517 | 0.0135 | 0.3351 | True |
| session_linear_roll_broad | sharpness_per_cm_effect | Condition × Phase | -0.0004383 | -0.02047 | 0.0161 | 0.4567 | True |
| session_linear_raw_visible95 | midpoint_cm_effect | Condition | 0.3651 | -10.16 | 10.52 | 0.5501 | True |
| session_linear_raw_visible95 | midpoint_cm_effect | Phase | -2.017 | -13 | 7.303 | 0.3046 | True |
| session_linear_raw_visible95 | midpoint_cm_effect | Condition × Phase | -4.474 | -21.34 | 6.323 | 0.2154 | True |
| session_linear_raw_visible95 | sharpness_per_cm_effect | Condition | 0.001653 | -0.01287 | 0.03072 | 0.6426 | True |
| session_linear_raw_visible95 | sharpness_per_cm_effect | Phase | -0.0002538 | -0.01485 | 0.03466 | 0.4628 | True |
| session_linear_raw_visible95 | sharpness_per_cm_effect | Condition × Phase | -0.002524 | -0.02754 | 0.02895 | 0.3429 | True |
| session_linear_roll_visible95 | midpoint_cm_effect | Condition | 0.2038 | -14.43 | 13.33 | 0.5122 | True |
| session_linear_roll_visible95 | midpoint_cm_effect | Phase | -4.844 | -18.54 | 6.488 | 0.2065 | True |
| session_linear_roll_visible95 | midpoint_cm_effect | Condition × Phase | -11.78 | -33.55 | 4.283 | 0.0795 | True |
| session_linear_roll_visible95 | sharpness_per_cm_effect | Condition | 0.01621 | -0.01663 | 0.05688 | 0.8181 | True |
| session_linear_roll_visible95 | sharpness_per_cm_effect | Phase | 0.009849 | -0.02084 | 0.05594 | 0.6911 | True |
| session_linear_roll_visible95 | sharpness_per_cm_effect | Condition × Phase | -0.009137 | -0.05183 | 0.03452 | 0.3164 | True |
| session_quadratic_raw_broad | midpoint_cm_effect | Condition | -2.974 | -60.02 | 54.63 | 0.4513 | True |
| session_quadratic_raw_broad | midpoint_cm_effect | Phase | 4.392 | -66.42 | 56.45 | 0.5628 | True |
| session_quadratic_raw_broad | midpoint_cm_effect | Condition × Phase | -7.059 | -78.11 | 62.82 | 0.4165 | True |
| session_quadratic_raw_broad | sharpness_per_cm_effect | Condition | 0.0004113 | -0.009295 | 0.01285 | 0.5673 | True |
| session_quadratic_raw_broad | sharpness_per_cm_effect | Phase | -0.0008991 | -0.01126 | 0.01157 | 0.366 | True |
| session_quadratic_raw_broad | sharpness_per_cm_effect | Condition × Phase | -5.984e-05 | -0.01549 | 0.0139 | 0.4909 | True |

**0/30** main parameter intervals exclude zero. Condition
means Viscereality−Control; Phase means Inhale−Exhale; interaction is the difference
of phase differences. These are finite-cohort joint posterior effects with
individual/time uncertainty retained. Failed model gates are inconclusive, not
evidence for zero effects. Among the fits passing the full gate,
**0/24** intervals exclude zero. Intervals
containing zero do not establish equivalence or the absence of an effect.
All population coefficients, response effects and simple
contrasts remain in their CSVs. No multiplicity correction or model Bayes factor
was introduced. No pooled-median ANOVA was used as independent evidence.

## Estimated global RT change

| model | target | basis | median_ms | ci_low_ms | ci_high_ms | probability_negative | gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| session_linear_raw_broad | population | linear | 7.24 | -21.68 | 35.95 | 0.3084 | False |
| session_linear_raw_broad | finite_cohort | linear | 6.779 | -7.563 | 21.2 | 0.179 | False |
| session_linear_roll_broad | population | linear | 6.924 | -20.98 | 35.78 | 0.311 | True |
| session_linear_roll_broad | finite_cohort | linear | 6.673 | -7.467 | 20.62 | 0.1757 | True |
| session_linear_raw_visible95 | population | linear | 6.461 | -23.31 | 35.58 | 0.3292 | True |
| session_linear_raw_visible95 | finite_cohort | linear | 6.714 | -7.36 | 20.94 | 0.1766 | True |
| session_linear_roll_visible95 | population | linear | 6.285 | -22.7 | 34.92 | 0.3341 | True |
| session_linear_roll_visible95 | finite_cohort | linear | 6.523 | -7.435 | 20.54 | 0.1861 | True |
| session_quadratic_raw_broad | population | linear | 6.8 | -22.16 | 36.38 | 0.3191 | True |
| session_quadratic_raw_broad | finite_cohort | linear | 6.867 | -7.336 | 20.94 | 0.171 | True |
| session_quadratic_raw_broad | population | quadratic | 47.02 | 3.239 | 87.95 | 0.01787 | True |
| session_quadratic_raw_broad | finite_cohort | quadratic | 47.33 | 20.29 | 73.74 | 0.0003125 | True |

The linear coefficient in ms is the modelled start-to-end RT change over the full
planned trial span. The quadratic coefficient multiplies u², whose endpoints are
.25 and whose center is zero; it is not itself an endpoint difference. Negative
linear values mean speeding up. A time effect is an RT-level finding, not a PPS
boundary/sharpness effect. Priors allow slowing, speeding or approximately flat RT.
In the quadratic sensitivity, the finite-cohort quadratic coefficient is
47.33 [20.29, 73.74] ms.
Its quadratic component alone is therefore
11.83 [5.07, 18.43] ms
higher at either planned endpoint than at centered time. This is evidence of a
curved time component under that model, not a uniform RT decline or a causal
fatigue diagnosis. The separate linear term remains in the total time function.
`global_time_trend.png` shows observed chronological block trajectories by order
and the estimated additive model component. Stimulus changes, practice, carryover
and fatigue are not causally separable merely by adjusting for these trends.

Posterior-predictive group mean-profile discrepancy tails:

| model | trial_type | draws | mean_profile_tail_probability | gate |
| --- | --- | --- | --- | --- |
| session_linear_raw_broad | AT | 600 | 0.4667 | False |
| session_linear_raw_broad | Baseline | 600 | 0.09333 | False |
| session_linear_roll_broad | AT | 600 | 0.455 | True |
| session_linear_roll_broad | Baseline | 600 | 0.07333 | True |
| session_linear_raw_visible95 | AT | 600 | 0 | True |
| session_linear_raw_visible95 | Baseline | 600 | 0.085 | True |
| session_linear_roll_visible95 | AT | 600 | 0 | True |
| session_linear_roll_visible95 | Baseline | 600 | 0.085 | True |
| session_quadratic_raw_broad | AT | 600 | 0.4383 | True |
| session_quadratic_raw_broad | Baseline | 600 | 0.08333 | True |

These check AT/Baseline means across nominal distances under the Gaussian model.
Low tails flag unresolved fit; convergence alone does not establish adequacy.
Both visible95 fits returned **0/600** replicated AT mean-profile discrepancies
as extreme as the observed one. This finite Monte Carlo frequency is not an
exact zero probability or a classical p value. It flags poor average-profile
adequacy under those constrained models, despite their successful sampling gates;
the visible S is not validated by the attractive normalized display.
The original baseline-timing uncertainty is not resolved by a time covariate.
`session_fit_quality.csv` reports descriptive trial RT R² INCLUDING the time
predictor. A gain there need not reflect better distance-shape identification.

## Matched prediction after time control

Five additional linear/raw/broad refits use the same held AT trials as the
unadjusted local/raw model. Both filters learn from training RTs only, and the
original global time coordinate stays fixed. Target RTs do not set cutoffs;
their recorded time metadata is used to predict their raw response. Predictive
scores integrate trend, baseline, shape and nuisance uncertainty jointly.
RMSE uses the 800 held participant × cell × distance mean RTs, equally weighted;
the log score integrates all raw held hits jointly within each cell. This is
mean-response prediction error, not individual-trial RMSE.

| model | held_distance_cm | RMSE_ms | log_score | prediction_gate |
| --- | --- | --- | --- | --- |
| local_raw | 10 | 66.05 | 659.5 | True |
| local_raw | 27 | 53.84 | 764.7 | True |
| local_raw | 50 | 57.27 | 823.9 | True |
| local_raw | 73 | 52.19 | 997.8 | True |
| local_raw | 100 | 69.14 | 652 | True |
| session_linear_raw_broad | 10 | 66.14 | 661.2 | True |
| session_linear_raw_broad | 27 | 53.77 | 756.9 | True |
| session_linear_raw_broad | 50 | 57.27 | 837.6 | True |
| session_linear_raw_broad | 73 | 52.2 | 1000 | True |
| session_linear_raw_broad | 100 | 69.23 | 650.5 | True |

| model | RMSE_ms | log_score | all_predictive_gates |
| --- | --- | --- | --- |
| local_raw | 60.07 | 3898 | True |
| session_linear_raw_broad | 60.1 | 3906 | True |

All matched predictive gates: **True**. Any failed
fold makes its scores and full aggregate comparison provisional. These within-
cohort checks do not establish new-person generalization, causal identification
or physiological validity. Other time/rolling/visible95 models were not separately
cross-validated. Every failed gate is retained.

## Figures, provenance and scientific status

`session_sigmoid_curves.png` illustrates the mean-parameter linear/raw/visible95
geometry. Its visible S and in-range transition are prior assumptions, not
normalized observations. Its band uses every retained posterior draw.
`session_observed_RT.png` retains raw observations beside time-standardized
summaries and expected corrected functions. Adjusted-marker bars show trend
uncertainty only; raw-marker intervals describe between-person variability.
Blue adjusted markers are displaced +1 cm horizontally for visibility; fitting
and exported distances retain their original values.
`session_individual_curves.pdf` contains all 40 participants and four cells.
Plot curves use 1,200 balanced draws; every exported numerical interval uses all
draws. Nonconverged functions are explicitly marked provisional.

This controls a specified shared additive RT-level time process; it does not
exclude fatigue, carryover, type-specific drift or time-varying PPS shape. Parameter
recovery, repeated full-pipeline coverage and the remaining Q10 model extensions
remain open. Cleaning selection is conditioned on rather than jointly generated.
Raw data, previous results, questionnaires, browser and manuscript remain intact.
The package manifest in `RESULTS.md` covers both this amendment and the eight
unadjusted sensitivities. No significant parameter effect or physiological
measurement is guaranteed by implementing these adjustments.
