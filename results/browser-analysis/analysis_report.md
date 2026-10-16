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

500 fixed-record within-cell trial resamples for parameters; 500 person/linked-record-group plus trial resamples with refitted pools for association intervals. Conditional on selected method, original cleaning and constraints; no correction for method selection or within-cell serial dependence. 19,999 pairing permutations; all 126 p values per specification unadjusted. Unresolved linked records make full-release inference provisional; exclusion sensitivities report point estimates/p values without bootstrap intervals.

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
| maia2_trusting | midpoint_cm | 41 | 0.0242 | [-0.3670, 0.3552] | 0.8803 |
| maia2_noticing | normalized_steepness_per_cm | 41 | -0.0668 | [-0.4539, 0.3334] | 0.6818 |
| maia2_not_distracting | normalized_steepness_per_cm | 41 | -0.1540 | [-0.5206, 0.4178] | 0.3313 |
| maia2_not_worrying | normalized_steepness_per_cm | 41 | 0.1490 | [-0.4053, 0.4801] | 0.3488 |
| maia2_attention_regulation | normalized_steepness_per_cm | 41 | -0.0321 | [-0.3846, 0.4835] | 0.8402 |
| maia2_emotional_awareness | normalized_steepness_per_cm | 41 | -0.1812 | [-0.5190, 0.4054] | 0.2541 |
| maia2_self_regulation | normalized_steepness_per_cm | 41 | -0.0728 | [-0.4222, 0.4175] | 0.6472 |
| maia2_body_listening | normalized_steepness_per_cm | 41 | -0.2780 | [-0.5175, 0.3280] | 0.0768 |
| maia2_trusting | normalized_steepness_per_cm | 41 | -0.1485 | [-0.4598, 0.3182] | 0.3512 |
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
| maia2_noticing | midpoint_cm | 41 | 0.0947 | [-0.2920, 0.4089] | 0.5600 |
| maia2_not_distracting | midpoint_cm | 41 | 0.0782 | [-0.3954, 0.4526] | 0.6362 |
| maia2_not_worrying | midpoint_cm | 41 | 0.0555 | [-0.4072, 0.3749] | 0.7297 |
| maia2_attention_regulation | midpoint_cm | 41 | 0.1605 | [-0.3647, 0.4108] | 0.3110 |
| maia2_emotional_awareness | midpoint_cm | 41 | -0.0565 | [-0.3761, 0.4297] | 0.7242 |
| maia2_self_regulation | midpoint_cm | 41 | 0.0736 | [-0.4015, 0.3934] | 0.6471 |
| maia2_body_listening | midpoint_cm | 41 | 0.0186 | [-0.4042, 0.3998] | 0.9073 |
| maia2_trusting | midpoint_cm | 41 | 0.2960 | [-0.3049, 0.4750] | 0.0594 |
| maia2_noticing | normalized_steepness_per_cm | 41 | -0.0475 | [-0.4495, 0.3462] | 0.7707 |
| maia2_not_distracting | normalized_steepness_per_cm | 41 | -0.1128 | [-0.5202, 0.4275] | 0.4798 |
| maia2_not_worrying | normalized_steepness_per_cm | 41 | 0.1932 | [-0.3798, 0.5074] | 0.2204 |
| maia2_attention_regulation | normalized_steepness_per_cm | 41 | -0.0596 | [-0.3881, 0.4790] | 0.7096 |
| maia2_emotional_awareness | normalized_steepness_per_cm | 41 | -0.1446 | [-0.4964, 0.3914] | 0.3648 |
| maia2_self_regulation | normalized_steepness_per_cm | 41 | -0.0812 | [-0.4442, 0.4055] | 0.6119 |
| maia2_body_listening | normalized_steepness_per_cm | 41 | -0.2261 | [-0.4929, 0.3346] | 0.1572 |
| maia2_trusting | normalized_steepness_per_cm | 41 | -0.1892 | [-0.4893, 0.3122] | 0.2367 |
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
