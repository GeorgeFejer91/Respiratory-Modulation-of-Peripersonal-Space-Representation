# Study 5 · Reproducible publication companion analysis

reproducible analysis draft; recording linkage requires review

The released dataset contains 42 participant records and 17,114 observed trials of 17,136 planned slots. The primary participant-wide mean ±2.5 sample-SD trim removed 382 recorded hits, retaining 8,916 Audio–Tactile and 4,396 Baseline RTs. There were 105 hit-labelled trials without RT (80 Audio–Tactile).

**Recording-linkage review:** unresolved recording-to-questionnaire linkage. Check the recording audit before interpreting behavioural inference and RT–questionnaire links; questionnaire-only results are separate.

## Primary question

The Condition × Phase × numeric SOA random-intercept ML comparison gives χ²(1)=0.023519, p=0.878116. The interaction is 0.814770 ms per SOA SD, model-based 95% Wald CI [-9.598235, 11.227775]. A non-significant result does not establish equivalence or a zero effect.

## Mixed-model comparisons

| Comparison | Participants | LR | df | p | Status |
| --- | ---: | ---: | ---: | ---: | --- |
| primary numeric interaction | 42 | 0.0235187 | 1 | 0.878116 | computed |
| Control-only numeric interaction | 42 | 0.623509 | 1 | 0.429746 | computed |
| categorical SOA | 42 | 2.27321 | 4 | 0.685651 | computed |
| Control-only categorical SOA | 42 | 3.5632 | 4 | 0.468334 | computed |
| exclude partial session; all conditions; numeric | 41 | 0.0597421 | 1 | 0.806904 | computed |
| exclude partial session; all conditions; categorical | 41 | 1.79883 | 4 | 0.772696 | computed |
| exclude partial session; Control; numeric | 41 | 1.13427 | 1 | 0.286867 | computed |
| exclude partial session; Control; categorical | 41 | 5.07549 | 4 | 0.279639 | computed |
| RT ≥200 ms sensitivity; all conditions; numeric | 42 | 0.0235187 | 1 | 0.878116 | computed |
| RT ≥200 ms sensitivity; all conditions; categorical | 42 | 2.27321 | 4 | 0.685651 | computed |
| RT ≥200 ms sensitivity; Control; numeric | 42 | 0.623509 | 1 | 0.429746 | computed |
| RT ≥200 ms sensitivity; Control; categorical | 42 | 3.5632 | 4 | 0.468334 | computed |
| random SOA slope | 42 | 0.0313655 | 1 | 0.859428 | computed |
| missing RT signed shift 0 ms | 42 | 0.00251586 | 1 | 0.959996 | computed |
| missing RT signed shift -100 ms | 42 | 0.187398 | 1 | 0.665091 | computed |
| missing RT signed shift 100 ms | 42 | 0.342866 | 1 | 0.55818 | computed |
| missing RT signed shift -200 ms | 42 | 0.628969 | 1 | 0.427734 | computed |
| missing RT signed shift 200 ms | 42 | 1.30422 | 1 | 0.253444 | computed |

## Sigmoid viability

0/168 registered-axis trial cells satisfy R²≥.70. The maximum saturated five-SOA trial-level R² ceiling is 0.430205. Any deterministic curve depending only on these SOAs is bounded by this ceiling, independently of sigmoid parameter bounds. Boundary inference and its MAIA/SpFrRef associations remain gated when participant fits are not interpretable. Group and five-mean fits are descriptive.

## Supplementary participant contrasts

| Contrast | n | Estimate (ms) | 95% CI | p | Holm p |
| --- | ---: | ---: | --- | ---: | ---: |
| Baseline Condition (Viscereality − Control) | 42 | 6.7496 | [-10.0864, 23.5855] | 0.422823 | 1 |
| Baseline Phase (Inhale − Exhale) | 42 | 18.0775 | [3.2797, 32.8752] | 0.0178864 | 0.143091 |
| Baseline Condition × Phase | 42 | 17.4327 | [1.5625, 33.3029] | 0.0321265 | 0.224886 |
| Overall AT minus within-Condition/Phase Baseline | 42 | -18.8132 | [-27.0010, -10.6254] | 3.53787e-05 | 0.000353787 |
| Far AT minus within-Condition/Phase Baseline | 42 | -10.4967 | [-24.9018, 3.9083] | 0.148762 | 0.743812 |
| Far AT minus same-label Baseline | 42 | -24.8291 | [-40.4312, -9.2271] | 0.00255238 | 0.0229714 |
| AT far-minus-near | 42 | 13.7969 | [-1.8240, 29.4178] | 0.0818716 | 0.49123 |
| Baseline far-minus-near nominal label | 42 | 11.6886 | [-6.9002, 30.2774] | 0.211288 | 0.84515 |
| AT minus Baseline far-minus-near label contrast | 42 | 2.1083 | [-18.4429, 22.6596] | 0.836892 | 1 |
| Pink minus white AT | 42 | -2.8577 | [-9.2964, 3.5810] | 0.375306 | 1 |

## Four uniformly estimated descriptive sigmoids

Selected from 320 pipelines: `winsor20/gaussian_constant/0.5/separate`. Tuning shape RMSE 47.053 ms; linear benchmark 47.317 ms; constant benchmark 47.437 ms. These are post hoc selection scores, not an independent test of sigmoid superiority. The fits describe the extracted RT summary; winsorized summaries need not equal raw means.

| Condition / phase | Midpoint (cm) | Width (cm) | RT slope at midpoint (ms/cm) | Conditional midpoint interval (cm) | Flat bootstrap draws |
| --- | ---: | ---: | ---: | --- | ---: |
| Control / Exhale | 71.50 | 35.29 | 0.0907 | [37.56, 88.00] | 0.9% |
| Control / Inhale | 96.25 | 42.56 | 0.0846 | [18.48, 100.00] | 8.7% |
| Viscereality / Exhale | 82.75 | 35.29 | 0.0900 | [31.82, 100.00] | 3.2% |
| Viscereality / Inhale | 25.38 | 30.38 | 0.0686 | [10.00, 93.32] | 8.7% |

width is logistic scale, not a Gaussian SD; normalized midpoint steepness = 1/(4*width), RT derivative = amplitude/(4*width), 10–90% span = 2*ln(9)*width.

Participant cluster percentile intervals conditional on chosen method and nonflat curves; method selection is not repeated. Boundary mass is reported separately. Bands include flat draws.

Only five positions were sampled. Full S-shaped extrapolations and asymptotes are model assumptions. The report includes all candidate scores and parameters, a fixed robust reference, trajectory-axis and expanded-bound sensitivity, and paired descriptive comparisons.

## Visible PPS-like shape: stronger exploratory audit

At least 10–90% of the logistic amplitude inside 10–100 cm; at least two sampled positions on each side of the midpoint; at least one in the 20–80% transition; maximum departure from the best dense-grid line at least 5% of the fitted observed range; positive nonflat amplitude. These post hoc display/sampling thresholds are not a validated physiological PPS definition.

Original pipelines satisfying the criterion in all four curves: 0/320. Shape-constrained selection: `trim10/gaussian_isotonic/0.15/separate`; tuning RMSE 47.086 ms. Fair tuned line: `median/gaussian_isotonic/0.3/separate`; tuning RMSE 47.178 ms.

| Prediction family | Nested outer RMSE (ms) |
| --- | ---: |
| logistic | 47.772 |
| visible | 47.634 |
| linear | 47.701 |
| constant | 47.437 |

Six outer participant folds; five inner participant folds crossed with omitted positions. Each family selects extraction, smoothing and fitting using training participants only. Outer predictions also omit the target position from fitting. Inner selection sees all design positions in training participants. Evaluation conditions on profiles cleaned beforehand using each person's eligible AT and Baseline hit RTs across all positions. People do not share cleaning thresholds, but an omitted position can affect its own person's threshold. This is relative-profile prediction for new people at the known design, not end-to-end prediction from uncleaned trials; families/criteria were developed post hoc. Overlapping training sets preclude treating folds as independent replicates or this evaluation as a confirmatory test.

Shape-constrained curves satisfy the geometry by construction when nonflat. Their existence is not evidence that the measurements contain an S-shaped transition. Intervals condition on the selected pipeline and shape constraints. Neither smoothing nor display interpolation adds independent observed positions.

The four imposed-shape midpoint/width estimates, constraint hits and conditional intervals are exported separately. Raw-mean curvature tests assess any nonlinearity, not sigmoid shape; see their exported statistics and assumptions. Evaluate empirical support separately from the imposed geometry.

## MAIA-2 and spatial frame of reference: exploratory

41/42 participants have all 37 MAIA-2 items. All eight dimensions were recomputed: 328 stored scores matched; 0 mismatched. Subscale means require all constituent items. Blank responses remain missing; no MAIA total was formed.

| MAIA-2 dimension | n | Mean | SD | Alpha | Pointwise 95% alpha interval |
| --- | ---: | ---: | ---: | ---: | --- |
| Noticing | 41 | 3.24 | 0.66 | 0.57 | [0.19, 0.74] |
| Not Distracting | 41 | 2.24 | 0.85 | 0.84 | [0.72, 0.91] |
| Not Worrying | 41 | 2.29 | 0.82 | 0.70 | [0.51, 0.81] |
| Attention Regulation | 41 | 2.96 | 0.67 | 0.78 | [0.65, 0.86] |
| Emotional Awareness | 41 | 3.47 | 0.70 | 0.59 | [0.31, 0.74] |
| Self Regulation | 41 | 2.85 | 0.86 | 0.81 | [0.69, 0.89] |
| Body Listening | 41 | 2.80 | 0.92 | 0.78 | [0.60, 0.87] |
| Trusting | 41 | 3.59 | 0.98 | 0.86 | [0.78, 0.91] |

Alpha is a sample internal-consistency diagnostic, not evidence of validity or a basis for deleting items.

Spatial-frame paired ratings: n=41; Viscereality higher=22, lower=6, tied=13. Two-sided exact sign-test p=0.0037191659212112427; ties are excluded only from the binomial denominator. Higher fraction among non-ties=0.79, exact 95% CI [0.59, 0.92]. This is an exploratory ordinal condition comparison. The administered anchor key is unavailable; higher codes are not automatically labelled allocentric.

Owner-confirmed: MAIA-2 once before the experiment; spatial-frame ratings after each intervention. Timing is not reconstructed from CSV timestamps.

### Main follow-up: numerical spatial change

Delta = post-Viscereality code minus post-Control code, independent of presentation order. Mean=0.76, SD=1.48, median=1.00. These differences assume comparable category steps.

| Pre-experiment MAIA-2 dimension | n | Spearman rho with delta | Pointwise 95% interval | Unadjusted permutation p |
| --- | ---: | ---: | --- | ---: |
| Noticing | 41 | 0.27 | [-0.02, 0.53] | 0.08725 |
| Not Distracting | 41 | 0.10 | [-0.24, 0.39] | 0.54660 |
| Not Worrying | 41 | 0.09 | [-0.23, 0.42] | 0.56570 |
| Attention Regulation | 41 | 0.11 | [-0.19, 0.41] | 0.48095 |
| Emotional Awareness | 41 | -0.06 | [-0.38, 0.25] | 0.69920 |
| Self Regulation | 41 | 0.21 | [-0.14, 0.50] | 0.19150 |
| Body Listening | 41 | 0.17 | [-0.16, 0.46] | 0.29535 |
| Trusting | 41 | 0.38 | [0.08, 0.63] | 0.01605 |

### Condition × MAIA moderation

Participant delta ~ intercept + centred MAIA, with/without centred Viscereality-first (0=Control-first, 1=Viscereality-first). Each subscale fitted separately. Beta estimates Condition × MAIA in code steps per MAIA point; F=t² with (1,n-k) df. HC3 uses t tails with n-k df as an approximate sensitivity. Order adjustment does not eliminate carryover.

| MAIA-2 dimension | Model | n | Slope | F(1,df) | df | Classical p | HC3 95% interval | HC3 p |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| Noticing | unadjusted | 41 | 0.64 | 3.46 | 39 | 0.07054 | [0.11, 1.17] | 0.01846 |
| Noticing | order_adjusted | 41 | 0.60 | 2.91 | 38 | 0.09616 | [0.06, 1.15] | 0.03124 |
| Not Distracting | unadjusted | 41 | 0.39 | 2.05 | 39 | 0.16060 | [-0.34, 1.11] | 0.28498 |
| Not Distracting | order_adjusted | 41 | 0.47 | 2.90 | 38 | 0.09678 | [-0.29, 1.23] | 0.21787 |
| Not Worrying | unadjusted | 41 | 0.14 | 0.23 | 39 | 0.63708 | [-0.65, 0.92] | 0.72609 |
| Not Worrying | order_adjusted | 41 | 0.10 | 0.12 | 38 | 0.73197 | [-0.80, 1.00] | 0.82128 |
| Attention Regulation | unadjusted | 41 | 0.42 | 1.48 | 39 | 0.23125 | [-0.39, 1.23] | 0.29702 |
| Attention Regulation | order_adjusted | 41 | 0.41 | 1.38 | 38 | 0.24769 | [-0.46, 1.28] | 0.34889 |
| Emotional Awareness | unadjusted | 41 | -0.07 | 0.04 | 39 | 0.84892 | [-0.74, 0.61] | 0.84573 |
| Emotional Awareness | order_adjusted | 41 | -0.08 | 0.05 | 38 | 0.81805 | [-0.72, 0.57] | 0.80593 |
| Self Regulation | unadjusted | 41 | 0.47 | 3.15 | 39 | 0.08380 | [-0.12, 1.05] | 0.11437 |
| Self Regulation | order_adjusted | 41 | 0.47 | 3.14 | 38 | 0.08434 | [-0.13, 1.07] | 0.12409 |
| Body Listening | unadjusted | 41 | 0.24 | 0.87 | 39 | 0.35733 | [-0.25, 0.72] | 0.33171 |
| Body Listening | order_adjusted | 41 | 0.24 | 0.91 | 38 | 0.34511 | [-0.22, 0.71] | 0.29634 |
| Trusting | unadjusted | 41 | 0.61 | 7.68 | 39 | 0.00851 | [0.06, 1.16] | 0.02932 |
| Trusting | order_adjusted | 41 | 0.62 | 7.99 | 38 | 0.00747 | [0.09, 1.16] | 0.02349 |

Post hoc pre-experiment trait moderation, not mediation. Code differences assume comparable category steps. Direction-only correlations are ordinal sensitivities; earlier absolute-rating results are supplementary. Correlation and interaction models are not independent replications.

42 rank correlations (9 numerical-delta and 33 retained earlier comparisons); 16 moderation fits, each with classical and HC3 inference; one overall paired sign test. No multiple-testing correction.

The eight direction-only associations are ordinal sensitivities; all 33 earlier associations remain in the supplementary download. The behavioural correlate is a raw-RT SOA-slope interaction, not a sigmoid boundary. Two-sided permutation test of independence; pointwise paired-person percentile 95% intervals with re-ranking; undefined bootstrap draws excluded and counted. No covariate adjustment.

- Exploratory extension; exact questionnaire wording in the registration could not be retrieved (HTTP 403).
- MAIA-2 measures self-reported interoceptive dimensions, not objective interoceptive accuracy.
- Alpha describes internal consistency under restrictive assumptions; it does not establish unidimensionality or validity. No item deletion or factor-model claim.
- A–H ordering is preserved, but pictogram anchor direction is unverified. Timing was confirmed by the owner; administered language remains undocumented.
- Numerical spatial-code differences assume comparable category steps; Spearman ranking and HC3 uncertainty do not remove that measurement assumption.
- No repeated MAIA, perceived-body-boundary or small-self fields are released. Boundary-related correlations remain gated.
- Small sample, multiplicity, ties, unadjusted confounding and uncertain behavioural contrast reliability limit association interpretation.

## Coverage of released data

| Domain | Status | Output |
| --- | --- | --- |
| Participant roster, demographics and order | analysed | Cohort age/gender/handedness/order, availability and participant QC |
| Observed/planned trials, responses, missing RT and Catch | analysed | Quality denominators, exclusions and missing-RT sensitivities |
| Condition × Phase × SOA reaction times | analysed | Mixed/cluster models, participant slopes, repeated measures and time-on-task |
| Baseline, distance labels, noise type, order and RT flags | analysed | Supplementary contrasts, noise Friedman, order subgroups, coordinate/window sensitivities |
| 37 MAIA-2 items and eight dimensions | analysed | Scoring audit, distributions, alpha intervals and all fixed exploratory associations |
| Paired spatial-frame ratings | analysed | Post-intervention code delta, exact sign test, main trait correlations, direction sensitivity and Condition × MAIA moderation with order/HC3 sensitivities |
| Participant PPS boundary and related questionnaire inference | not_estimable | Fit gate retained; group approximations remain descriptive |
| Exploratory individual sigmoid proxies and normalized RT | computed | Four fitted proxies per record, normalization, shared-plateau sensitivity, recovery/reliability and provisional questionnaire links; recording-linkage audit |
| Remaining behavioural/shape robustness checks | analysed | Primary-model linkage exclusions, mean parameter contrasts and change-score reliability/recovery, refit association intervals for every exclusion, log-distance benchmark, nine geometry specifications and repeated method selection |
| PPS parameter repeated-measures ANOVA/ANCOVA | computed | 2×2 effects and continuous baseline MAIA/spatial-change covariates for midpoint/sharpness; both plateau models, four linkage cohorts, order/HC3 and 500 curve-refit intervals |
| Repeated MAIA, body-boundary and small-self measures | unavailable | No corresponding repeated/measure columns in released tables |
| Waveforms, measured breathing and acquisition provenance | unavailable | Source recordings and private metadata are outside the release |

## Interpretation and unavailable provenance

- Recording-linkage audit: unresolved recording-to-questionnaire linkage. Full-release behavioural inference requires provenance review; the questionnaire-only spatial analysis is separate.
- No failure to reject is interpreted as equivalence or proof of zero effect.
- Same-SOA-label Baseline subtraction is not a verified cue-time-matched contrast.
- Sigmoid bounds are an explicit reimplementation; saturated R² ceilings independently bound viability.
- Four post hoc group sigmoid approximations use one selected extraction/smoothing/fitting pipeline. They do not supply participant boundary inference; bootstrap intervals condition on the chosen method.
- The PPS-shape extension compares explicit measured-range shape constraints with equally processed lines using nested participant prediction. Imposed S shapes do not establish empirical curvature or physiological boundaries.
- JZS paired-contrast Bayes factors are exploratory and are not a mixed-model Bayes factor.
- Waveform cue-time and RT-onset validation: original recordings are not in the released CSVs.
- Measured respiratory compliance: phase labels are scheduled/instructed, not belt-verified.
- Pilot dates, acquisition-version effects and two source-onset exclusions: required provenance metadata are not released.

## Reproducibility

Runtime: {"execution": "browser Pyodide", "matplotlib": "3.10.8", "numpy": "2.4.3", "platform": "Emscripten", "python": "3.14.2", "scipy": "1.17.1"}

The result ZIP contains model and diagnostic tables, participant QC, cell/curve summaries, sigmoid fits, the retained RT table, SVG figures, and the full JSON report. The manifest records exact input/output hashes. Primary models always use the fixed analysis contract and are independent of the preparation preview controls.

## Individual sigmoid proxies and normalized RT

All numbers are exploratory fitted proxies. Visible geometry is imposed, reverse responses are retained, and the original failed participant boundary gate is unchanged. Numeric midpoint/width values in flat or weak profiles reflect constraints/regularization, not identified physiological boundaries.

**Recording-linkage audit:** unresolved recording-to-questionnaire linkage. Matching recordings with different questionnaire records cannot establish independent participants. Preserve source rows; resolve the original mapping. New RT–questionnaire results are provisional; exclusion sensitivities do not identify the correct mapping.

168 curves; selected method `visible/mean/gaussian_constant/0.3/penalty4`. Subtract the fitted lower plateau and divide by absolute fitted amplitude. This is an affine display transformation, not new evidence. Do not clip observations; skip zero amplitude and flag intervals containing zero. Joint sensitivity shares plateaus across each person's four curves.

84 methods: 36 visible, 36 broad and 12 lines, plus a constant. Six outer participant/linked-record-group folds repeat tuning on training people, using omitted-position prediction; test-person fits use four positions and pooling from training people only. Linked copies are excluded together from each person's pool. Scores condition on earlier cleaning. Shared-plateau sensitivity uses the selected visible preprocessing and penalty.

500 fixed-record within-cell trial resamples for full-release parameters; 500 person/linked-record-group plus trial resamples with refitted pools for association and mean-contrast intervals in each of four linkage specifications. Conditional on cohort-specific selected method, original cleaning and constraints; no correction for method selection or within-cell serial dependence. 19,999 pairing permutations; all 126 p values per specification unadjusted. Unresolved linked records make full-release inference provisional; exclusions do not identify the correct mapping.

| Family | Outer prediction RMSE (ms) |
| --- | ---: |
| visible | 48.507 |
| broad | 51.694 |
| linear | 48.269 |
| constant | 47.437 |
| shared_plateaus | 47.237 |

### Individual plateaus: all 27 main contrast associations

Intervals include refitting uncertainty; permutation p values condition on point estimates. All are unadjusted and provisional.

| Questionnaire | Parameter difference | n | rho | 95% interval | p |
| --- | --- | ---: | ---: | --- | ---: |
| maia2_noticing | midpoint_cm | 41 | -0.1192 | [-0.3768, 0.3501] | 0.4543 |
| maia2_not_distracting | midpoint_cm | 41 | 0.3126 | [-0.3810, 0.4585] | 0.0483 |
| maia2_not_worrying | midpoint_cm | 41 | 0.2491 | [-0.3647, 0.4963] | 0.1185 |
| maia2_attention_regulation | midpoint_cm | 41 | -0.0338 | [-0.5063, 0.3480] | 0.8298 |
| maia2_emotional_awareness | midpoint_cm | 41 | -0.3403 | [-0.4673, 0.3580] | 0.0318 |
| maia2_self_regulation | midpoint_cm | 41 | -0.0728 | [-0.4453, 0.3775] | 0.6496 |
| maia2_body_listening | midpoint_cm | 41 | 0.0008 | [-0.4497, 0.3724] | 0.9964 |
| maia2_trusting | midpoint_cm | 41 | 0.0242 | [-0.3670, 0.3533] | 0.8803 |
| maia2_noticing | normalized_steepness_per_cm | 41 | -0.0668 | [-0.4539, 0.3334] | 0.6818 |
| maia2_not_distracting | normalized_steepness_per_cm | 41 | -0.1540 | [-0.5206, 0.4178] | 0.3313 |
| maia2_not_worrying | normalized_steepness_per_cm | 41 | 0.1490 | [-0.4053, 0.4786] | 0.3488 |
| maia2_attention_regulation | normalized_steepness_per_cm | 41 | -0.0321 | [-0.3850, 0.4835] | 0.8402 |
| maia2_emotional_awareness | normalized_steepness_per_cm | 41 | -0.1812 | [-0.5190, 0.4051] | 0.2541 |
| maia2_self_regulation | normalized_steepness_per_cm | 41 | -0.0728 | [-0.4222, 0.4178] | 0.6472 |
| maia2_body_listening | normalized_steepness_per_cm | 41 | -0.2780 | [-0.5175, 0.3285] | 0.0768 |
| maia2_trusting | normalized_steepness_per_cm | 41 | -0.1485 | [-0.4631, 0.3161] | 0.3512 |
| maia2_noticing | midpoint_slope_ms_per_cm | 41 | -0.0127 | [-0.2788, 0.3464] | 0.9377 |
| maia2_not_distracting | midpoint_slope_ms_per_cm | 41 | -0.2017 | [-0.3699, 0.1753] | 0.2024 |
| maia2_not_worrying | midpoint_slope_ms_per_cm | 41 | 0.0547 | [-0.2776, 0.3417] | 0.7313 |
| maia2_attention_regulation | midpoint_slope_ms_per_cm | 41 | 0.1679 | [-0.1554, 0.4823] | 0.2917 |
| maia2_emotional_awareness | midpoint_slope_ms_per_cm | 41 | 0.0743 | [-0.2951, 0.3524] | 0.6481 |
| maia2_self_regulation | midpoint_slope_ms_per_cm | 41 | 0.0786 | [-0.2984, 0.3622] | 0.6226 |
| maia2_body_listening | midpoint_slope_ms_per_cm | 41 | -0.1445 | [-0.3944, 0.2828] | 0.3668 |
| maia2_trusting | midpoint_slope_ms_per_cm | 41 | -0.0022 | [-0.3422, 0.3024] | 0.9889 |
| spfrref_delta | midpoint_cm | 41 | -0.0011 | [-0.4063, 0.4178] | 0.9942 |
| spfrref_delta | normalized_steepness_per_cm | 41 | 0.1679 | [-0.3547, 0.4579] | 0.2903 |
| spfrref_delta | midpoint_slope_ms_per_cm | 41 | 0.1432 | [-0.1602, 0.4586] | 0.3746 |

### Shared-plateau sensitivity: all 27 main contrast associations

Intervals include refitting uncertainty; permutation p values condition on point estimates. All are unadjusted and provisional.

| Questionnaire | Parameter difference | n | rho | 95% interval | p |
| --- | --- | ---: | ---: | --- | ---: |
| maia2_noticing | midpoint_cm | 41 | 0.0947 | [-0.2926, 0.4089] | 0.5600 |
| maia2_not_distracting | midpoint_cm | 41 | 0.0782 | [-0.3954, 0.4526] | 0.6362 |
| maia2_not_worrying | midpoint_cm | 41 | 0.0555 | [-0.4072, 0.3749] | 0.7297 |
| maia2_attention_regulation | midpoint_cm | 41 | 0.1605 | [-0.3647, 0.4108] | 0.3110 |
| maia2_emotional_awareness | midpoint_cm | 41 | -0.0565 | [-0.3761, 0.4297] | 0.7242 |
| maia2_self_regulation | midpoint_cm | 41 | 0.0736 | [-0.4007, 0.3934] | 0.6471 |
| maia2_body_listening | midpoint_cm | 41 | 0.0186 | [-0.4042, 0.3998] | 0.9073 |
| maia2_trusting | midpoint_cm | 41 | 0.2960 | [-0.3049, 0.4750] | 0.0594 |
| maia2_noticing | normalized_steepness_per_cm | 41 | -0.0475 | [-0.4495, 0.3457] | 0.7707 |
| maia2_not_distracting | normalized_steepness_per_cm | 41 | -0.1128 | [-0.5202, 0.4275] | 0.4798 |
| maia2_not_worrying | normalized_steepness_per_cm | 41 | 0.1932 | [-0.3752, 0.5064] | 0.2204 |
| maia2_attention_regulation | normalized_steepness_per_cm | 41 | -0.0596 | [-0.3881, 0.4790] | 0.7096 |
| maia2_emotional_awareness | normalized_steepness_per_cm | 41 | -0.1446 | [-0.4964, 0.3914] | 0.3648 |
| maia2_self_regulation | normalized_steepness_per_cm | 41 | -0.0812 | [-0.4442, 0.4055] | 0.6119 |
| maia2_body_listening | normalized_steepness_per_cm | 41 | -0.2261 | [-0.4899, 0.3348] | 0.1572 |
| maia2_trusting | normalized_steepness_per_cm | 41 | -0.1892 | [-0.4904, 0.3122] | 0.2367 |
| maia2_noticing | midpoint_slope_ms_per_cm | 41 | -0.0682 | [-0.3595, 0.3086] | 0.6685 |
| maia2_not_distracting | midpoint_slope_ms_per_cm | 41 | -0.2217 | [-0.4284, 0.3277] | 0.1643 |
| maia2_not_worrying | midpoint_slope_ms_per_cm | 41 | 0.2099 | [-0.3205, 0.4386] | 0.1838 |
| maia2_attention_regulation | midpoint_slope_ms_per_cm | 41 | -0.3901 | [-0.5271, 0.4066] | 0.0118 |
| maia2_emotional_awareness | midpoint_slope_ms_per_cm | 41 | -0.2126 | [-0.4286, 0.3376] | 0.1812 |
| maia2_self_regulation | midpoint_slope_ms_per_cm | 41 | -0.1301 | [-0.4348, 0.3176] | 0.4188 |
| maia2_body_listening | midpoint_slope_ms_per_cm | 41 | -0.1824 | [-0.4785, 0.3239] | 0.2585 |
| maia2_trusting | midpoint_slope_ms_per_cm | 41 | -0.2731 | [-0.4817, 0.3298] | 0.0843 |
| spfrref_delta | midpoint_cm | 41 | 0.3310 | [-0.2602, 0.4609] | 0.0344 |
| spfrref_delta | normalized_steepness_per_cm | 41 | 0.1556 | [-0.3732, 0.4234] | 0.3295 |
| spfrref_delta | midpoint_slope_ms_per_cm | 41 | 0.1651 | [-0.3422, 0.3682] | 0.2989 |

All 126 tests per model, all three linkage-exclusion specifications (1,008 tests total), parameter tables, reliability/recovery, normalized trial RTs and a 42-page curve atlas are in the download. Exclusion sensitivities do not determine the correct recording mapping.

## Remaining-analysis robustness checks

Post-results amendment: all specifications were fixed before this extension. Exclusions preserve the original CSVs and cannot resolve recording identity.

| Excluded records | Comparison | n records | LR p (unadjusted) |
| --- | --- | ---: | ---: |
| P011, P033 | Primary numeric linkage sensitivity | 40 | 0.87344 |
| P011, P033 | Primary categorical linkage sensitivity | 40 | 0.65222 |
| P011, P033 | Control-only numeric linkage sensitivity | 40 | 0.45674 |
| P011, P033 | Control-only categorical linkage sensitivity | 40 | 0.50197 |
| P011 | Primary numeric linkage sensitivity | 41 | 0.83859 |
| P011 | Primary categorical linkage sensitivity | 41 | 0.72489 |
| P011 | Control-only numeric linkage sensitivity | 41 | 0.46371 |
| P011 | Control-only categorical linkage sensitivity | 41 | 0.45171 |
| P033 | Primary numeric linkage sensitivity | 41 | 0.91337 |
| P033 | Primary categorical linkage sensitivity | 41 | 0.59934 |
| P033 | Control-only numeric linkage sensitivity | 41 | 0.42288 |
| P033 | Control-only categorical linkage sensitivity | 41 | 0.51447 |

### Cohort mean fitted-parameter contrasts

Pointwise 95% intervals resample people (linked records together) and trials and refit both models. They condition on the selected method and cleaning. These are model-dependent proxies, not validated PPS boundaries.

| Cohort | Plateau model | Contrast | Parameter | Mean | 95% refit interval |
| --- | --- | --- | --- | ---: | --- |
| Full release | individual_plateaus | condition_delta | midpoint_cm | -15.1250 | [-27.1522, 17.6300] |
| Full release | individual_plateaus | condition_delta | normalized_steepness_per_cm | 0.0093 | [-0.0176, 0.0281] |
| Full release | individual_plateaus | condition_delta | midpoint_slope_ms_per_cm | 0.0676 | [-0.5412, 0.3256] |
| Full release | individual_plateaus | phase_delta | midpoint_cm | -16.9464 | [-24.7497, 16.1509] |
| Full release | individual_plateaus | phase_delta | normalized_steepness_per_cm | 0.0067 | [-0.0208, 0.0270] |
| Full release | individual_plateaus | phase_delta | midpoint_slope_ms_per_cm | 0.0330 | [-0.5687, 0.3316] |
| Full release | individual_plateaus | condition_by_phase | midpoint_cm | -46.9643 | [-55.1433, 30.0721] |
| Full release | individual_plateaus | condition_by_phase | normalized_steepness_per_cm | 0.0101 | [-0.0400, 0.0403] |
| Full release | individual_plateaus | condition_by_phase | midpoint_slope_ms_per_cm | 0.2056 | [-0.8230, 0.8085] |
| Full release | shared_plateaus | condition_delta | midpoint_cm | -16.5357 | [-27.7854, 17.2435] |
| Full release | shared_plateaus | condition_delta | normalized_steepness_per_cm | 0.0089 | [-0.0170, 0.0277] |
| Full release | shared_plateaus | condition_delta | midpoint_slope_ms_per_cm | 0.2383 | [-0.2478, 0.4698] |
| Full release | shared_plateaus | phase_delta | midpoint_cm | -16.8214 | [-24.7345, 14.8628] |
| Full release | shared_plateaus | phase_delta | normalized_steepness_per_cm | 0.0068 | [-0.0206, 0.0268] |
| Full release | shared_plateaus | phase_delta | midpoint_slope_ms_per_cm | 0.1782 | [-0.3125, 0.4437] |
| Full release | shared_plateaus | condition_by_phase | midpoint_cm | -42.5714 | [-49.6919, 28.8797] |
| Full release | shared_plateaus | condition_by_phase | normalized_steepness_per_cm | 0.0107 | [-0.0394, 0.0397] |
| Full release | shared_plateaus | condition_by_phase | midpoint_slope_ms_per_cm | 0.3593 | [-0.5490, 0.7222] |
| Exclude P011,P033 | individual_plateaus | condition_delta | midpoint_cm | -16.0688 | [-28.1662, 18.1631] |
| Exclude P011,P033 | individual_plateaus | condition_delta | normalized_steepness_per_cm | 0.0021 | [-0.0198, 0.0265] |
| Exclude P011,P033 | individual_plateaus | condition_delta | midpoint_slope_ms_per_cm | -0.0088 | [-0.5117, 0.4494] |
| Exclude P011,P033 | individual_plateaus | phase_delta | midpoint_cm | -15.0563 | [-27.6755, 16.9983] |
| Exclude P011,P033 | individual_plateaus | phase_delta | normalized_steepness_per_cm | 0.0033 | [-0.0219, 0.0277] |
| Exclude P011,P033 | individual_plateaus | phase_delta | midpoint_slope_ms_per_cm | 0.0064 | [-0.6650, 0.4657] |
| Exclude P011,P033 | individual_plateaus | condition_by_phase | midpoint_cm | -40.1625 | [-57.0572, 29.7056] |
| Exclude P011,P033 | individual_plateaus | condition_by_phase | normalized_steepness_per_cm | 0.0001 | [-0.0468, 0.0411] |
| Exclude P011,P033 | individual_plateaus | condition_by_phase | midpoint_slope_ms_per_cm | -0.0669 | [-0.9610, 0.8733] |
| Exclude P011,P033 | shared_plateaus | condition_delta | midpoint_cm | -17.2125 | [-29.1225, 18.7931] |
| Exclude P011,P033 | shared_plateaus | condition_delta | normalized_steepness_per_cm | 0.0021 | [-0.0196, 0.0259] |
| Exclude P011,P033 | shared_plateaus | condition_delta | midpoint_slope_ms_per_cm | 0.0662 | [-0.3025, 0.5005] |
| Exclude P011,P033 | shared_plateaus | phase_delta | midpoint_cm | -14.9625 | [-27.1378, 15.9492] |
| Exclude P011,P033 | shared_plateaus | phase_delta | normalized_steepness_per_cm | 0.0034 | [-0.0215, 0.0273] |
| Exclude P011,P033 | shared_plateaus | phase_delta | midpoint_slope_ms_per_cm | 0.0805 | [-0.2908, 0.4872] |
| Exclude P011,P033 | shared_plateaus | condition_by_phase | midpoint_cm | -34.8750 | [-51.8756, 28.3819] |
| Exclude P011,P033 | shared_plateaus | condition_by_phase | normalized_steepness_per_cm | 0.0015 | [-0.0461, 0.0404] |
| Exclude P011,P033 | shared_plateaus | condition_by_phase | midpoint_slope_ms_per_cm | 0.0661 | [-0.6462, 0.8764] |
| Exclude P011 | individual_plateaus | condition_delta | midpoint_cm | 1.8293 | [-5.9547, 4.8590] |
| Exclude P011 | individual_plateaus | condition_delta | normalized_steepness_per_cm | -0.0038 | [-0.0055, 0.0037] |
| Exclude P011 | individual_plateaus | condition_delta | midpoint_slope_ms_per_cm | -0.0723 | [-0.4850, 0.2657] |
| Exclude P011 | individual_plateaus | phase_delta | midpoint_cm | 1.7927 | [-4.8755, 5.0959] |
| Exclude P011 | individual_plateaus | phase_delta | normalized_steepness_per_cm | -0.0011 | [-0.0038, 0.0049] |
| Exclude P011 | individual_plateaus | phase_delta | midpoint_slope_ms_per_cm | -0.0537 | [-0.4503, 0.3184] |
| Exclude P011 | individual_plateaus | condition_by_phase | midpoint_cm | -0.6585 | [-11.4704, 9.0284] |
| Exclude P011 | individual_plateaus | condition_by_phase | normalized_steepness_per_cm | -0.0069 | [-0.0100, 0.0082] |
| Exclude P011 | individual_plateaus | condition_by_phase | midpoint_slope_ms_per_cm | 0.0233 | [-0.7306, 0.7571] |
| Exclude P011 | shared_plateaus | condition_delta | midpoint_cm | -4.9390 | [-11.2317, 4.1127] |
| Exclude P011 | shared_plateaus | condition_delta | normalized_steepness_per_cm | 0.0028 | [-0.0023, 0.0048] |
| Exclude P011 | shared_plateaus | condition_delta | midpoint_slope_ms_per_cm | -0.0001 | [-0.2302, 0.1783] |
| Exclude P011 | shared_plateaus | phase_delta | midpoint_cm | -2.5976 | [-9.7989, 3.7765] |
| Exclude P011 | shared_plateaus | phase_delta | normalized_steepness_per_cm | -0.0004 | [-0.0027, 0.0040] |
| Exclude P011 | shared_plateaus | phase_delta | midpoint_slope_ms_per_cm | 0.1079 | [-0.1050, 0.2603] |
| Exclude P011 | shared_plateaus | condition_by_phase | midpoint_cm | -0.6585 | [-9.0732, 11.4009] |
| Exclude P011 | shared_plateaus | condition_by_phase | normalized_steepness_per_cm | -0.0003 | [-0.0069, 0.0062] |
| Exclude P011 | shared_plateaus | condition_by_phase | midpoint_slope_ms_per_cm | 0.1521 | [-0.3039, 0.3266] |
| Exclude P033 | individual_plateaus | condition_delta | midpoint_cm | -16.4817 | [-27.2401, 17.6936] |
| Exclude P033 | individual_plateaus | condition_delta | normalized_steepness_per_cm | 0.0070 | [-0.0154, 0.0302] |
| Exclude P033 | individual_plateaus | condition_delta | midpoint_slope_ms_per_cm | 0.0270 | [-0.5374, 0.3579] |
| Exclude P033 | individual_plateaus | phase_delta | midpoint_cm | -16.2988 | [-30.1578, 20.6104] |
| Exclude P033 | individual_plateaus | phase_delta | normalized_steepness_per_cm | 0.0054 | [-0.0197, 0.0275] |
| Exclude P033 | individual_plateaus | phase_delta | midpoint_slope_ms_per_cm | -0.0046 | [-0.5979, 0.3056] |
| Exclude P033 | individual_plateaus | condition_by_phase | midpoint_cm | -46.1341 | [-51.8579, 31.2558] |
| Exclude P033 | individual_plateaus | condition_by_phase | normalized_steepness_per_cm | 0.0054 | [-0.0392, 0.0379] |
| Exclude P033 | individual_plateaus | condition_by_phase | midpoint_slope_ms_per_cm | 0.1052 | [-0.8418, 0.7632] |
| Exclude P033 | shared_plateaus | condition_delta | midpoint_cm | -17.5244 | [-27.7596, 16.9770] |
| Exclude P033 | shared_plateaus | condition_delta | normalized_steepness_per_cm | 0.0067 | [-0.0152, 0.0298] |
| Exclude P033 | shared_plateaus | condition_delta | midpoint_slope_ms_per_cm | 0.1763 | [-0.2411, 0.5037] |
| Exclude P033 | shared_plateaus | phase_delta | midpoint_cm | -16.2073 | [-29.3131, 19.0166] |
| Exclude P033 | shared_plateaus | phase_delta | normalized_steepness_per_cm | 0.0054 | [-0.0194, 0.0270] |
| Exclude P033 | shared_plateaus | phase_delta | midpoint_slope_ms_per_cm | 0.1291 | [-0.2823, 0.4757] |
| Exclude P033 | shared_plateaus | condition_by_phase | midpoint_cm | -41.3415 | [-46.8503, 30.3796] |
| Exclude P033 | shared_plateaus | condition_by_phase | normalized_steepness_per_cm | 0.0065 | [-0.0382, 0.0374] |
| Exclude P033 | shared_plateaus | condition_by_phase | midpoint_slope_ms_per_cm | 0.2202 | [-0.5193, 0.7130] |

### Reliability of the changes used in correlations

| Model | Parameter change | Median split-half rho | Recovery rho: cell-specific / shared baseline truth |
| --- | --- | ---: | --- |
| individual_plateaus | midpoint_cm | -0.074 | 0.102 / 0.120 |
| individual_plateaus | normalized_steepness_per_cm | 0.052 | -0.032 / -0.043 |
| individual_plateaus | midpoint_slope_ms_per_cm | 0.064 | 0.079 / 0.102 |
| shared_plateaus | midpoint_cm | 0.066 | 0.173 / 0.396 |
| shared_plateaus | normalized_steepness_per_cm | -0.009 | 0.087 / 0.051 |
| shared_plateaus | midpoint_slope_ms_per_cm | 0.155 | 0.074 / 0.055 |

### Group shape comparison without ambiguous recordings

Post-results exclusion-cohort audit. Nested scores compare five response families on the same cleaned-profile target. Log distance is not an expectancy control. Nine geometry specifications are all reported with frozen preprocessing; their leave-position scores are descriptive and use all people. Thirty repeated-selection resamples diagnose instability, not tail confidence coverage. Original cleaning is fixed; no serial-dependence or physiological validation is claimed.

| Family | Outer prediction RMSE (ms) |
| --- | ---: |
| logistic | 47.993 |
| visible | 47.915 |
| linear | 48.087 |
| logarithmic | 48.121 |
| constant | 48.020 |

All nine geometry specifications and 30 repeated-selection draws are exported. The repeated selections chose 27 distinct methods. No preferred appearance was selected after inspection.

Remaining evidence limits: recording-to-person mapping, waveforms and breathing traces, acquisition timing, independent dense-distance validation, serial-dependence calibration and method-selection-adjusted interval coverage remain unavailable or unestablished.

## PPS parameters: repeated-measures ANOVA and ANCOVA

Exploratory 2×2 ANOVA and continuous-covariate ANCOVA of fitted midpoint and normalized sharpness; 1,328 unadjusted tests over both plateau models and four linkage cohorts. One-df contrast regressions give balanced RM effects; four-cell means give between-person covariate effects. Main presentation excludes both ambiguous records and adjusts moderation for order. Classical/HC3 tests condition on estimated parameters and ignore pooled-fit dependence; 500 hierarchical curve-refit intervals expose additional uncertainty. Spatial delta is a post-intervention correlate, not a causal mediator. Method selection and cleaning are fixed; poor reliability remains a limit.

Main presentation: Exclude P011/P033. Sharpness = 1/(4 × width in cm); larger values mean a narrower transition. MAIA dimensions are fitted separately and kept continuous. Spatial delta is Viscereality − Control.

| Model | Parameter | Effect / covariate | n | Estimate | F (1, df) | Unadjusted p | HC3 p | 95% curve-refit interval |
| --- | --- | --- | ---: | ---: | --- | ---: | ---: | --- |
| individual_plateaus | midpoint_cm | Condition | 40 | -16.069 | 5352.9 (1, 39) | 2.3008e-43 | 3.7562e-43 | [-28.166, 18.163] |
| individual_plateaus | normalized_steepness_per_cm | Condition | 40 | 0.0021217 | 70.846 (1, 39) | 2.6527e-10 | 3.6574e-10 | [-0.019819, 0.026516] |
| individual_plateaus | midpoint_cm | Phase | 40 | -15.056 | 3439.7 (1, 39) | 1.1861e-39 | 1.9326e-39 | [-27.675, 16.998] |
| individual_plateaus | normalized_steepness_per_cm | Phase | 40 | 0.0033216 | 206.88 (1, 39) | 3.5145e-17 | 5.33e-17 | [-0.021875, 0.027727] |
| individual_plateaus | midpoint_cm | Condition × Phase | 40 | -40.162 | 3420.3 (1, 39) | 1.3224e-39 | 2.1547e-39 | [-57.057, 29.706] |
| individual_plateaus | normalized_steepness_per_cm | Condition × Phase | 40 | 0.000135 | 0.11316 (1, 39) | 0.73838 | 0.74155 | [-0.046825, 0.041068] |
| individual_plateaus | midpoint_cm | Condition × maia2_noticing | 39 | -0.14542 | 0.13427 (1, 36) | 0.71619 | 0.73304 | [-5.6159, 6.6963] |
| individual_plateaus | normalized_steepness_per_cm | Condition × maia2_noticing | 39 | 0.00024076 | 0.29508 (1, 36) | 0.59033 | 0.61018 | [-0.0052728, 0.0047924] |
| individual_plateaus | midpoint_cm | Condition × maia2_not_distracting | 39 | -0.039922 | 0.016569 (1, 36) | 0.8983 | 0.9308 | [-4.8041, 4.9214] |
| individual_plateaus | normalized_steepness_per_cm | Condition × maia2_not_distracting | 39 | 6.8413e-05 | 0.038863 (1, 36) | 0.84483 | 0.88391 | [-0.0044813, 0.0037332] |
| individual_plateaus | midpoint_cm | Condition × maia2_not_worrying | 39 | 0.093853 | 0.11008 (1, 36) | 0.74198 | 0.72251 | [-3.6171, 4.3169] |
| individual_plateaus | normalized_steepness_per_cm | Condition × maia2_not_worrying | 39 | 0.00028585 | 0.83141 (1, 36) | 0.36793 | 0.39171 | [-0.0035529, 0.0043253] |
| individual_plateaus | midpoint_cm | Condition × maia2_attention_regulation | 39 | -0.056601 | 0.025642 (1, 36) | 0.87367 | 0.88868 | [-5.9981, 5.9628] |
| individual_plateaus | normalized_steepness_per_cm | Condition × maia2_attention_regulation | 39 | -2.1522e-05 | 0.0029576 (1, 36) | 0.95693 | 0.96261 | [-0.0042399, 0.0055319] |
| individual_plateaus | midpoint_cm | Condition × maia2_emotional_awareness | 39 | -0.47404 | 2.1258 (1, 36) | 0.15351 | 0.22866 | [-5.1435, 4.996] |
| individual_plateaus | normalized_steepness_per_cm | Condition × maia2_emotional_awareness | 39 | -0.00097013 | 8.2482 (1, 36) | 0.0067965 | 0.037465 | [-0.0056918, 0.0042448] |
| individual_plateaus | midpoint_cm | Condition × maia2_self_regulation | 39 | -0.38241 | 1.7009 (1, 36) | 0.20044 | 0.33824 | [-4.8833, 4.2247] |
| individual_plateaus | normalized_steepness_per_cm | Condition × maia2_self_regulation | 39 | -0.00031914 | 0.92623 (1, 36) | 0.34227 | 0.32025 | [-0.0044918, 0.0036644] |
| individual_plateaus | midpoint_cm | Condition × maia2_body_listening | 39 | -0.12899 | 0.24134 (1, 36) | 0.62622 | 0.59062 | [-4.3681, 3.732] |
| individual_plateaus | normalized_steepness_per_cm | Condition × maia2_body_listening | 39 | -8.7877e-05 | 0.089039 (1, 36) | 0.76712 | 0.78454 | [-0.0042975, 0.0029107] |
| individual_plateaus | midpoint_cm | Condition × maia2_trusting | 39 | -0.17079 | 0.46648 (1, 36) | 0.49898 | 0.43744 | [-3.3588, 3.9623] |
| individual_plateaus | normalized_steepness_per_cm | Condition × maia2_trusting | 39 | -0.00028313 | 1.0394 (1, 36) | 0.31475 | 0.44531 | [-0.0038734, 0.0031636] |
| individual_plateaus | midpoint_cm | Condition × spfrref_delta | 39 | -0.040856 | 0.065979 (1, 36) | 0.79875 | 0.72795 | [-2.2474, 2.528] |
| individual_plateaus | normalized_steepness_per_cm | Condition × spfrref_delta | 39 | 0.00026442 | 2.3455 (1, 36) | 0.13439 | 0.26417 | [-0.0018964, 0.0027085] |
| shared_plateaus | midpoint_cm | Condition | 40 | -17.213 | 528.09 (1, 39) | 2.8045e-24 | 4.4433e-24 | [-29.122, 18.793] |
| shared_plateaus | normalized_steepness_per_cm | Condition | 40 | 0.0020807 | 49.509 (1, 39) | 1.911e-08 | 2.5279e-08 | [-0.019567, 0.025897] |
| shared_plateaus | midpoint_cm | Phase | 40 | -14.963 | 505.65 (1, 39) | 6.1725e-24 | 9.7659e-24 | [-27.138, 15.949] |
| shared_plateaus | normalized_steepness_per_cm | Phase | 40 | 0.0034296 | 188.79 (1, 39) | 1.5706e-16 | 2.3674e-16 | [-0.021471, 0.027251] |
| shared_plateaus | midpoint_cm | Condition × Phase | 40 | -34.875 | 588.26 (1, 39) | 3.9114e-25 | 6.217e-25 | [-51.876, 28.382] |
| shared_plateaus | normalized_steepness_per_cm | Condition × Phase | 40 | 0.0015381 | 5.9225 (1, 39) | 0.019633 | 0.021117 | [-0.046079, 0.040434] |
| shared_plateaus | midpoint_cm | Condition × maia2_noticing | 39 | 0.98709 | 0.56967 (1, 36) | 0.4553 | 0.33503 | [-4.8088, 8.0768] |
| shared_plateaus | normalized_steepness_per_cm | Condition × maia2_noticing | 39 | 0.00030051 | 0.32976 (1, 36) | 0.56937 | 0.57473 | [-0.0052661, 0.0048238] |
| shared_plateaus | midpoint_cm | Condition × maia2_not_distracting | 39 | 0.51529 | 0.25281 (1, 36) | 0.61817 | 0.58978 | [-5.0348, 5.5806] |
| shared_plateaus | normalized_steepness_per_cm | Condition × maia2_not_distracting | 39 | 0.00018299 | 0.20014 (1, 36) | 0.65729 | 0.72765 | [-0.0043327, 0.0039125] |
| shared_plateaus | midpoint_cm | Condition × maia2_not_worrying | 39 | -0.50309 | 0.28924 (1, 36) | 0.59402 | 0.69086 | [-5.0997, 4.6582] |
| shared_plateaus | normalized_steepness_per_cm | Condition × maia2_not_worrying | 39 | 0.00051364 | 1.9839 (1, 36) | 0.16756 | 0.19605 | [-0.0034576, 0.0043403] |
| shared_plateaus | midpoint_cm | Condition × maia2_attention_regulation | 39 | 1.6483 | 2.0922 (1, 36) | 0.1567 | 0.098762 | [-5.3213, 7.479] |
| shared_plateaus | normalized_steepness_per_cm | Condition × maia2_attention_regulation | 39 | -9.4529e-05 | 0.04093 (1, 36) | 0.84081 | 0.84462 | [-0.0041826, 0.0055614] |
| shared_plateaus | midpoint_cm | Condition × maia2_emotional_awareness | 39 | 1.4997 | 1.9258 (1, 36) | 0.17375 | 0.40899 | [-5.7892, 7.5345] |
| shared_plateaus | normalized_steepness_per_cm | Condition × maia2_emotional_awareness | 39 | -0.0012186 | 9.6149 (1, 36) | 0.0037387 | 0.017192 | [-0.0055624, 0.0040532] |
| shared_plateaus | midpoint_cm | Condition × maia2_self_regulation | 39 | -0.39354 | 0.1572 (1, 36) | 0.69409 | 0.64662 | [-5.395, 5.3519] |
| shared_plateaus | normalized_steepness_per_cm | Condition × maia2_self_regulation | 39 | -0.00036748 | 0.87892 (1, 36) | 0.35474 | 0.3025 | [-0.0044705, 0.0036972] |
| shared_plateaus | midpoint_cm | Condition × maia2_body_listening | 39 | -0.81705 | 0.89704 (1, 36) | 0.34989 | 0.46859 | [-5.3606, 3.5289] |
| shared_plateaus | normalized_steepness_per_cm | Condition × maia2_body_listening | 39 | 8.0998e-05 | 0.054155 (1, 36) | 0.8173 | 0.80711 | [-0.0043973, 0.0029805] |
| shared_plateaus | midpoint_cm | Condition × maia2_trusting | 39 | 1.2584 | 2.4282 (1, 36) | 0.12791 | 0.4118 | [-3.5522, 6.2485] |
| shared_plateaus | normalized_steepness_per_cm | Condition × maia2_trusting | 39 | -0.00053019 | 2.7314 (1, 36) | 0.10709 | 0.2364 | [-0.0039265, 0.003041] |
| shared_plateaus | midpoint_cm | Condition × spfrref_delta | 39 | 0.65965 | 1.633 (1, 36) | 0.20946 | 0.20183 | [-2.2636, 3.2557] |
| shared_plateaus | normalized_steepness_per_cm | Condition × spfrref_delta | 39 | 9.266e-05 | 0.19483 (1, 36) | 0.66157 | 0.75766 | [-0.001929, 0.0026058] |

Conventional F/p and HC3 treat fitted parameters as outcomes. They do not propagate curve fitting or shared-pool uncertainty. Interpret them beside the refit intervals and the previously weak parameter-change reliability. All 1,328 terms, both order specifications, phase/three-way moderators, between-person effects and spatial-direction sensitivities are exported. No multiplicity correction was applied.
