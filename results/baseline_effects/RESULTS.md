# Baseline-corrected Study 5: native results

Results only; no manuscript rewrite or GitHub Pages integration. These are exploratory analyses on the unchanged public data. Primary inference excludes the unresolved P011/P033 reused recording, leaving 40 participants, 8,478 Audio–Tactile trials and 4,192 Baseline trials. All p values are unadjusted. Condition means Viscereality − Control; Phase means Inhale − Exhale; interaction is their difference of differences.

**Main finding.** The completed battery does not establish a reliable Condition, Phase or interaction effect on PPS midpoint or normalized sharpness. Finite individual sigmoid parameters are obtainable, but their physiological interpretation is not supported by identification, visual shape and recovery checks. This is uncertainty about effects, not proof that effects are exactly zero.

**What is supported at the response level.** Audio–Tactile RT averaged **18.65 ms faster than matched baseline** (AT − Baseline = −18.65 ms, 95% CI −27.26 to −10.04, paired p = 0.0000865, JZS BF10 = 277.5). Raw AT RT was 18.47 ms slower during inhale (p = .00240); Baseline was 20.63 ms slower during inhale (p = .00869). After subtraction, the phase difference was −2.16 ms (95% CI −12.15 to 7.82, p = .664). The corrected Condition difference was −7.30 ms (p = .112), and the interaction −14.09 ms (p = .119). These are response-level effects, not PPS boundary estimates.

**Exploratory RT interaction.** The Student-t sigmoid suggested an RT-level interaction despite unresolved shape mixing. Three post hoc response-only Student-t models test that finding without sigmoid parameters; all effects were retained. The population condition × phase RT-location contrasts are compared with their Gaussian counterparts below. A Student-t location is its mean under the assumed symmetric, finite-variance likelihood; it is a robust estimate of central response time. Distribution-sensitive effects do not establish a PPS boundary or sharpness change. These are sensitivity analyses of the same dataset, not independent replications.

| model | posterior_median | ci_low | ci_high | target_diagnostic_gate |
| --- | --- | --- | --- | --- |
| joint_constant | -14.6 | -30.1 | 1.02 | 1 |
| joint_linear | -14.8 | -30.2 | 0.7 | 1 |
| joint_log_distance | -14.7 | -30.4 | 0.609 | 1 |
| joint_constant_student | -17.5 | -32.4 | -2.83 | 1 |
| joint_linear_student | -17.8 | -32.8 | -2.98 | 1 |
| joint_log_distance_student | -17.7 | -32.8 | -2.52 | 1 |

**Primary response-model tests.** Pooled baseline subtraction matches participant × Condition × Phase. Linear and logarithmic models use distance, not log-transformed corrected RT. Their slopes have no intrinsic sigmoid midpoint.

| metric | Condition | Phase | Condition × Phase |
| --- | --- | --- | --- |
| mean_RT_ms | 0.112 | 0.664 | 0.119 |
| far_minus_near_ms | 0.572 | 0.848 | 0.472 |
| linear_distance_slope | 0.379 | 0.667 | 0.865 |
| log_distance_slope | 0.547 | 0.953 | 0.863 |

The categorical-distance RM ANOVA also found no Condition × distance, Phase × distance or three-way interaction: sphericity-adjusted p = .689, .260 and .395. Multivariate Hotelling counterparts gave p = .775, .181 and .591. The overall distance effect was p = .0314 after a Greenhouse–Geisser sphericity adjustment (uncorrected p = .0130), but fell to p = .289 under same-nominal-label baseline subtraction. That sensitivity has unverified cue-time equivalence. Sphericity adjustment is distinct from multiple-testing correction.

**Independent individual curve fits.** Five families were fitted uniformly: logistic, probit, Gompertz, log-logistic and the fixed-observed-extrema logistic sensitivity motivated by Canzoneri et al. (2012; doi:10.1371/journal.pone.0044306). The generic alternative families are methodological sensitivities, not claimed PPS-literature replications. Every family uses the same d50 midpoint and normalized derivative at d50. Signed amplitudes and flat/reversed curves are retained. Primary continuous logistic estimates are:

| metric | effect | estimate | ci_low | ci_high | p |
| --- | --- | --- | --- | --- | --- |
| midpoint_cm | Condition | 0.995 | -12.5 | 14.5 | 0.883 |
| midpoint_cm | Phase | 2.21 | -10.1 | 14.5 | 0.719 |
| midpoint_cm | Condition × Phase | -18.9 | -43.9 | 6.01 | 0.133 |
| sharpness_per_cm | Condition | 0.00284 | -0.00907 | 0.0148 | 0.632 |
| sharpness_per_cm | Phase | 0.00692 | -0.00353 | 0.0174 | 0.188 |
| sharpness_per_cm | Condition × Phase | -0.00945 | -0.0328 | 0.0139 | 0.417 |

Across 84 grid specifications, four cohorts and six parameter contrasts, 6 of 2016 rows had p < .05; these rows are correlated sensitivity analyses, not independent replications. No primary unsmoothed mean/registered-axis family gave a significant parameter effect. None of the 240 continuous-refinement tests for those primary fitting choices was significant. All 60 primary refit-stability intervals included zero.

**Nominal findings retained rather than hidden.** The six grid hits reduce to three fitting choices. Median extraction with pooled correction gave a phase–sharpness p = .0493, changing to .0521 under continuous refinement. Same-label correction + trajectory distance + Gaussian smoothing + log-logistic fitting gave phase–sharpness p = .0463 (continuous p = .0336); its 500-refit stability interval was −.01118 to .01458 /cm, and one-person deletion could raise p to .0623. A same-label fixed-extrema condition effect appeared only in the exclude-P011 cohort (grid p = .0361), changing to .111 under continuous refinement. All 18 post hoc refit intervals across these three choices included zero. Sparse singleton-baseline resampling and two-level bootstrap coverage limits remain explicit; these are stability intervals, not claimed calibrated confidence intervals.

**Joint Bayesian analysis.** The likelihood jointly uses original Baseline and AT observations; it carries shared baseline uncertainty instead of treating corrected trials as independent. Midpoint and log-width have population factorial coefficients and participant random coefficients for all four factorial terms. Baseline/intercept/amplitude variation is retained, and amplitudes may be negative or near zero. Exact Gaussian trial sufficient statistics retain within-cell variation; Student-t sensitivity uses every trial. Below are finite-cohort contrasts under the initial hierarchical nuisance model, with 95% equal-tail credible intervals:

| quantity | term | posterior_median | ci_low | ci_high | probability_positive |
| --- | --- | --- | --- | --- | --- |
| midpoint_cm_effect | Condition | 9.89 | -33.5 | 50.2 | 0.683 |
| midpoint_cm_effect | Phase | 18.2 | -40.7 | 61.4 | 0.779 |
| midpoint_cm_effect | Condition × Phase | 10.1 | -51.7 | 71.2 | 0.63 |
| sharpness_per_cm_effect | Condition | 0.000151 | -0.00715 | 0.0116 | 0.565 |
| sharpness_per_cm_effect | Phase | 6.52e-05 | -0.00822 | 0.0114 | 0.528 |
| sharpness_per_cm_effect | Condition × Phase | 0.000921 | -0.00953 | 0.016 | 0.758 |

Numerical caution: models failing the prespecified target gate are joint_logistic, joint_logistic_wide, joint_logistic_student, joint_logistic_same_label. Failed diagnostics are not evidence for a null effect. Full model and target-specific Rhat, ESS, divergences, priors, likelihoods and sampling counts are retained in the diagnostic/specification files. Interrupted low-rank numerical attempts yielded no reported results; reported extensions use standard adaptation.

A post hoc nuisance-pooling sensitivity analytically integrates independent Normal(0,.2 seconds) corrected intercepts and Normal(0,.15 seconds) amplitudes, while retaining the original paired shape hierarchy and baseline uncertainty. Its integrated likelihood was checked against a full multivariate-normal calculation. This tests sensitivity to pooling the response-level nuisance parameters; both approaches retain fitting uncertainty. Its contrasts are:

| quantity | term | posterior_median | ci_low | ci_high | probability_positive |
| --- | --- | --- | --- | --- | --- |
| midpoint_cm_effect | Condition | -3.33 | -83.4 | 76.1 | 0.466 |
| midpoint_cm_effect | Phase | -5.55 | -87.1 | 71.7 | 0.447 |
| midpoint_cm_effect | Condition × Phase | -7.33 | -90.6 | 79.7 | 0.436 |
| sharpness_per_cm_effect | Condition | 0.000395 | -0.00291 | 0.00422 | 0.628 |
| sharpness_per_cm_effect | Phase | -0.000517 | -0.00452 | 0.00272 | 0.334 |
| sharpness_per_cm_effect | Condition × Phase | 0.000438 | -0.00547 | 0.00471 | 0.597 |

There are 0 parameter contrasts whose 95% interval excludes zero across the six logistic joint-model specifications. A further post hoc sensitivity allows each participant × condition × phase its own residual scale, with identical priors in all cells; it addresses the unequal cell noise seen in the observed profiles. All outputs, including any failed-diagnostic result, are in `joint_all_effects.csv`; within-condition phase and within-phase condition contrasts are in `joint_simple_effects.csv`. Directional probabilities are not p values. Joint-model Bayes factors were not computed; JZS factors in the contrast tables refer only to their explicitly specified paired tests.

Other Bayesian response-level intervals excluding zero (if any) are listed below. These are finite-cohort response contrasts, not population midpoint coefficients. They do not establish a boundary or sharpness change; model and diagnostic sensitivity must be retained.

| model | quantity | term | posterior_median | ci_low | ci_high | target_diagnostic_gate |
| --- | --- | --- | --- | --- | --- | --- |
| joint_logistic_student | mean_RT_effect_ms | Condition × Phase | -17.8 | -32.4 | -3.24 | 0 |
| joint_linear | mean_RT_effect_ms | Condition × Phase | -14.8 | -29.6 | -0.071 | 1 |
| joint_constant_student | mean_RT_effect_ms | Condition × Phase | -17.5 | -32 | -3.48 | 1 |
| joint_constant_student | population_mean_RT_effect_ms | Condition × Phase | -17.5 | -32.4 | -2.83 | 1 |
| joint_linear_student | mean_RT_effect_ms | Condition × Phase | -17.8 | -32 | -3.67 | 1 |
| joint_linear_student | population_mean_RT_effect_ms | Condition × Phase | -17.8 | -32.8 | -2.98 | 1 |
| joint_log_distance_student | mean_RT_effect_ms | Condition × Phase | -17.7 | -32.1 | -3.25 | 1 |
| joint_log_distance_student | population_mean_RT_effect_ms | Condition × Phase | -17.7 | -32.8 | -2.52 | 1 |

**Prediction and measurement quality.** Twenty held-distance refits compare the four hierarchical response families. Reported prediction errors are against held-out AT means, with Baseline retained as independent calibration. Every final fold passed its predictive Rhat/ESS/divergence gate. Logistic prediction did not improve on linear prediction: paired MSE difference +16.96 ms², 95% CI −8.72 to 42.64; total held-block log-score difference +0.645, participant-cluster SE 3.93. These checks assess prediction within the retained cohort, not generalization to new people.

| family | held_distance_RMSE_ms |
| --- | --- |
| constant | 46.5 |
| linear | 45.2 |
| log_distance | 46.1 |
| logistic | 45.4 |

Posterior predictive checks limit interpretation beyond sampler convergence. The constant Student-t model misses the AT distance-mean structure (discrepancy tail probability .001), so its interaction is not a reason to prefer that model. The linear Student-t model gives .098 for both AT and Baseline mean-profile discrepancies; the log-distance Student-t model gives .052 and .089. Gaussian models pooling Baseline across nominal distance labels give low Baseline discrepancy probabilities (.013–.027), consistent with the baseline-timing concern; the same-label model fits those means but has unresolved sampling diagnostics and timing equivalence. These are discrepancy checks, not proof that any model is true.

Unpooled flexible sigmoid fits overfit severely: primary logistic held-distance RMSE was 189.8 ms versus 48.0 ms for a constant and 54.1 ms for fixed-extrema logistic. In the primary finite-grid logistic fits, 99/160 cells touched a numerical bound, 67 midpoints lay outside 10–100 cm, and 63 amplitudes were negative. A shifted free-intercept fit has exactly the same shape after subtracting one constant baseline per cell; independently checked translation invariance prevents attributing an artificial shape improvement to subtraction.

| model | midpoint_95ci_inside_observed_range | median_midpoint_interval_width_cm | amplitude_95ci_excludes_zero |
| --- | --- | --- | --- |
| joint_logistic | 0 | 206 | 14 |
| joint_logistic_wide | 0 | 225 | 15 |
| joint_logistic_student | 0 | 242 | 21 |
| joint_logistic_same_label | 0 | 253 | 3 |
| joint_logistic_marginal | 0 | 241 | 5 |
| joint_logistic_heterogeneous | 0 | 249 | 4 |

Visual inspection of `average_curves.png` and the participant atlas preserves unsmoothed observations and uncertainty on the measured distance range. The average fits are close to linear over that range, with no resolved pair of sigmoid plateaus. No axis manipulation or forced normalization was used to create an apparent S shape.

**Recovery checks.** Eighty matched-noise finite-grid simulations (20 each: flat, null80, known80, known200 ms amplitudes) show weak individual recovery at an 80 ms signal: median midpoint rank correlation .222 and sharpness correlation −.044 in the known-effect scenario. Even at 200 ms, finite-grid sharpness correlation was only .104. In separate joint Bayesian checks, the null80 dataset gave population intervals covering zero. A known200 dataset recovered the inserted midpoint effects +10, −10, +15 cm with posterior medians +10.53, −10.84, +14.59 and intervals [6.03,15.20], [−15.45,−5.97], [6.00,23.19]. These two Bayesian simulations demonstrate behavior, not repeated-simulation coverage or power calibration.

**Do not use pooled posterior medians as independent measurements.** Conventional ANOVAs on hierarchical posterior medians produced six p < .05 results in the deliberately zero-population-effect null80 simulation, including extremely small p values. Shared group shrinkage and omitted fit uncertainty make those conventional point-parameter tests unsuitable as independent evidence. They remain exported because the owner requested this approach; use the joint posterior contrasts for inference. This does not retroactively change the earlier unpooled browser model or its separate point-estimate tests.

**What this batch covers.** Baseline signs/matching, the two distance axes, four linkage cohorts for frequentist analyses, raw and two corrected profiles, mean/median extraction, Gaussian smoothing, trial-weight sensitivity, five sigmoid families, continuous refinement, repeated-measures and multivariate tests, paired t/permutation/rank/sign tests, leave-one-person checks, whole-person and trial refits, twelve joint Bayesian constant/linear/log-distance/logistic specifications, likelihood/prior/nuisance-pooling sensitivities, prediction and recovery. The new joint Bayesian fits use the primary40 cohort; full42 frequentist outputs are provisional and do not establish independent recordings. Same-label timing remains unverified. Profile-likelihood confidence sets, a separate frequentist nonlinear mixed-effects fit (R/nlme unavailable) and new questionnaire analyses were not run in this batch. Additional splines/kernels cannot create missing plateau observations; arbitrary polynomial or linear/log fits have no uniquely defined sigmoid boundary. No claim is made that every imaginable model has been exhausted.

**Files and reproducibility.** `analysis_registry.json` labels the finite batches and post hoc diagnostic amendments. `response_tests.csv`, `categorical_distance_tests.csv`, `curve_point_tests.csv`, `continuous_curve_tests.csv`, `curve_refit_stability.csv`, both `nominal_hit_*` tables, `joint_all_effects.csv`, `joint_simple_effects.csv`, `joint_all_diagnostics.csv` and the recovery/prediction tables retain the full result family. `participant_curves_native.pdf` contains all 40 primary participants. Source, dependency and data hashes are in `manifest.json`. Large posterior traces are local execution artifacts, not committed or bundled. Browser execution/Pages documentation and manuscript rewriting were set aside for this request.
