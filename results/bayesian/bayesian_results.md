# Study 5 — Bayesian parameter results

Results-only exploratory extension. The version-1.9 manuscript and complete analysis are preserved.

## 1. Can we compute individual sigmoids, and are they identified?

All 168 participant × condition × phase cells have proper sigmoid posteriors under each of four declared priors (672 fits). The main behavioural cohort excludes P011, P033 and contains 40 records. Recording copies share posterior draws and resampling weights; the source mapping is still unresolved.

**Computability is established; individual physiological boundary identification is not.** Of the 160 primary cells, 0 have their entire 95% midpoint interval inside 10–100 cm. Only 5 signed-amplitude intervals exclude zero. Median joint shape information gain is 0.108 nats. Median posterior probability that both 10–90% bends lie within the measured range is 0.0615. These are descriptive diagnostics, not a new physiological pass/fail gate.

The primary prior midpoint is centred at 55 cm. An average posterior midpoint near 55 cm is therefore not evidence that the measured PPS boundary is 55 cm. Sharpness also depends strongly on the declared width support; averages of prior-dependent parameters must retain that qualification.

## 2. Does a sigmoid predict better than simpler responses?

Each distance was held out and all its trials excluded from fitting. RMSE uses the held-out raw cell mean, equal participant/cell/distance weighting, and no smoothing. Model probabilities use explicit equal prior probabilities and proper nuisance priors; they are not assumption-free shape evidence.

| Prior | Model | Held-distance RMSE (ms) | Sigmoid minus comparator RMSE, 95% paired-person interval (ms) |
| --- | --- | ---: | --- |
| primary | constant | 48 | -0.594 [-2.45, 1.13] |
| primary | linear | 52.1 | -4.69 [-6.61, -2.68] |
| primary | log_distance | 54.5 | -7.04 [-9.66, -4.28] |
| primary | sigmoid | 47.4 | — |
| expanded_support | constant | 48 | -0.799 [-2, 0.359] |
| expanded_support | linear | 52.1 | -4.9 [-7.14, -2.48] |
| expanded_support | log_distance | 54.5 | -7.25 [-9.94, -4.04] |
| expanded_support | sigmoid | 47.2 | — |
| concentrated_width | constant | 48 | -0.437 [-2.39, 1.45] |
| concentrated_width | linear | 52.1 | -4.54 [-6.44, -2.55] |
| concentrated_width | log_distance | 54.5 | -6.89 [-9.46, -4] |
| concentrated_width | sigmoid | 47.6 | — |
| wide_nuisance | constant | 48.1 | 0.625 [-1.86, 2.88] |
| wide_nuisance | linear | 53.1 | -4.39 [-5.96, -2.71] |
| wide_nuisance | log_distance | 56.4 | -7.68 [-10.7, -4.5] |
| wide_nuisance | sigmoid | 48.7 | — |

Negative differences favour the sigmoid. A small advantage over a constant does not identify its midpoint/width or establish observed S curvature.

## 3. Do midpoint or sharpness differ by condition or phase?

Condition = Viscereality−Control; Phase = Inhale−Exhale; interaction = the difference of those phase effects. Four cells stay paired within each participant. The following are primary-prior posterior plus Bayesian-bootstrap descriptive intervals; finite-cohort posterior intervals and every prior/cohort sensitivity are separately exported. This is not a fully hierarchical population-effects model.

| Parameter | Effect | Median | 95% interval | Probability above zero |
| --- | --- | ---: | --- | ---: |
| midpoint_cm | Condition | -0.532 | [-23.8, 23.1] | 0.48 |
| normalized_steepness_per_cm | Condition | 0.000101 | [-0.0122, 0.0115] | 0.51 |
| midpoint_cm | Phase | 0.565 | [-23.2, 25.3] | 0.52 |
| normalized_steepness_per_cm | Phase | -0.000217 | [-0.0121, 0.0108] | 0.49 |
| midpoint_cm | Condition × Phase | -4.1 | [-50.5, 43.5] | 0.44 |
| normalized_steepness_per_cm | Condition × Phase | -0.00101 | [-0.0257, 0.021] | 0.46 |

Midpoints use cm; normalized sharpness uses cm⁻¹. These intervals quantify model-conditional and modular participant uncertainty; they do not establish equivalence when zero is included.

### Descriptive cell-average parameters

These are means of conditional individual parameters, not fitted boundaries of the average response function. Their proximity to the prior centre and their sensitivity to width support prevent a physiological interpretation.

| Cell | Parameter | Conditional mean, median [95% interval] |
| --- | --- | --- |
| Control · Exhale | midpoint_cm | 54.4 [30.6, 76.5] |
| Control · Exhale | normalized_steepness_per_cm | 0.0216 [0.0124, 0.0357] |
| Control · Inhale | midpoint_cm | 56.3 [32.6, 79.6] |
| Control · Inhale | normalized_steepness_per_cm | 0.0222 [0.0124, 0.0367] |
| Viscereality · Exhale | midpoint_cm | 55.3 [32.5, 78.4] |
| Viscereality · Exhale | normalized_steepness_per_cm | 0.0226 [0.0124, 0.0359] |
| Viscereality · Inhale | midpoint_cm | 54.2 [30.4, 77.9] |
| Viscereality · Inhale | normalized_steepness_per_cm | 0.0214 [0.0119, 0.0346] |

## 4. Prior sensitivity and reliability

| Prior | Median midpoint interval width (cm) | Median sharpness | Median shape information (nats) | Cell amplitude intervals excluding zero |
| --- | ---: | ---: | ---: | ---: |
| primary | 173 | 0.00967 | 0.108 | 5 |
| expanded_support | 259 | 0.00973 | 0.0828 | 4 |
| concentrated_width | 174 | 0.0153 | 0.12 | 7 |
| wide_nuisance | 174 | 0.0119 | 0.202 | 7 |

| Parameter | Split-half four-cell-mean rho | Split-half condition-change rho | Matched-sigmoid recovery rho |
| --- | ---: | ---: | ---: |
| midpoint_cm | 0.156 | 0.032 | 0.456 |
| normalized_steepness_per_cm | 0.15 | -0.134 | 0.0435 |

Ten split halves measure within-session stability, not test–retest reliability. Recovery uses 20 replicates of 80-ms sigmoid signals with the actual design/counts and a matched Gaussian noise model; it does not validate arbitrary RT distributions or real physiological boundaries. Flat and linear simulations remain in the full export.

| Prior | Prior-predictive negative RT fraction | Prior residual SD 95% range (ms) |
| --- | ---: | --- |
| primary | 3.0% | [60.3, 280] |
| expanded_support | 3.0% | [60.3, 280] |
| concentrated_width | 3.2% | [60.3, 280] |
| wide_nuisance | 12.5% | [60.3, 280] |

The Gaussian working model admits negative RTs, especially under the deliberately wider prior. This is an explicit prior-predictive limitation, not a positive-support RT model. Bayesian fitting still assumes a likelihood, priors, noise structure and finite integration support.

## 5. Spatial ratings, MAIA-2 and joint exploration

The same-condition rating is paired with each condition's two respiratory-phase estimates. MAIA-2 is measured once before the experiment; spatial change compares two post-intervention ratings. Eight continuous subscales stay separate. Numerical spatial changes assume comparable category spacing; rank/direction sensitivities retain that limitation.

| Prior | Rank-association intervals excluding zero / 92 | Joint-model coefficient intervals excluding zero / 192 |
| --- | ---: | ---: |
| primary | 0 / 92 | 0 / 192 |
| expanded_support | 0 / 92 | 0 / 192 |
| concentrated_width | 0 / 92 | 0 / 192 |
| wide_nuisance | 0 / 92 | 0 / 192 |

Across four priors and four recording cohorts the download retains 1472 rank-association records and 3072 joint-model coefficient records. They are repeated exploratory sensitivities, not independent replications. Rank intervals combine latent-parameter draws with paired recording-group bootstrap counts. Joint coefficients combine latent draws with Bayesian-bootstrap WLS, controlling for order. Neither is a full latent-covariate posterior.

Each joint model includes centred MAIA, spatial delta, their product and presentation order. The product on the Condition contrast addresses Condition × MAIA × spatial change; the product on the Condition × Phase contrast additionally varies with respiratory phase. All three scientific coefficients and all four orthogonal summaries are retained. No causal mediation is identified.

## 6. What is complete and what remains unresolved?

The computational Bayesian reference, individual tables, prediction, prior sensitivity, paired experimental contrasts, descriptive curves and full exploratory links are implemented. The results do not establish reliable participant-level physiological midpoint/sharpness identification or a robust experimental/questionnaire effect. A full joint hierarchical nonlinear model, serial-dependence/positive-support likelihood sensitivity and independent test–retest data have not been supplied by this extension. No claim of a universally best model is made.

Raw RT panels and conditional unit-amplitude geometry are separate. Normalized S geometry is implied by choosing a sigmoid family. Its appearance does not establish observed curvature. Average functions integrate over people and posterior draws and need not themselves be sigmoids.

The download records sources and artifact hashes. The broader level-by-level synthesis is `results/RESULTS_REPORT.md`; `for-ai/ANALYSIS_ROADMAP.md` owns the active checklist. Manuscript drafting remains paused. Earlier frequentist p values are unadjusted; the new probabilities are not p values or multiplicity-adjusted guarantees.

Methodological context: [Hedge et al., reliability and individual differences](https://doi.org/10.3758/s13428-017-0935-1); [Stan guide to posterior predictive checks](https://mc-stan.org/docs/stan-users-guide/posterior-predictive-checks.html). The conjugate likelihood, quadrature and modular summaries are explicitly specified and independently verified in this repository, not attributed to either source.
