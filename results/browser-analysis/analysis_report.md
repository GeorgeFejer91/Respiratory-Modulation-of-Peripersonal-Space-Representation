# Study 5 · Reproducible publication companion analysis

reproducible analysis draft for author review

The released dataset contains 42 independent participants and 17,114 observed trials of 17,136 planned slots. The primary participant-wide mean ±2.5 sample-SD trim removed 382 recorded hits, retaining 8,916 Audio–Tactile and 4,396 Baseline RTs. There were 105 hit-labelled trials without RT (80 Audio–Tactile).

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

All 33 fixed associations are exported with Spearman rho, paired-person bootstrap intervals, permutation p and Holm p. 0/33 have Holm p<.05. The behavioural correlate is a raw-RT SOA-slope interaction, not a sigmoid boundary. Two-sided permutation test of independence; pointwise paired-person percentile 95% intervals with re-ranking; undefined bootstrap draws excluded and counted. No covariate adjustment.

- Exploratory extension; exact questionnaire wording in the registration could not be retrieved (HTTP 403).
- MAIA-2 measures self-reported interoceptive dimensions, not objective interoceptive accuracy.
- Alpha describes internal consistency under restrictive assumptions; it does not establish unidimensionality or validity. No item deletion or factor-model claim.
- A–H ordering is preserved, but pictogram anchor direction and questionnaire administration timing are absent from the released data.
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
| Paired spatial-frame ratings | analysed | Category distributions/transitions, exact sign test, order counts and rank associations |
| Participant PPS boundary and related questionnaire inference | not_estimable | Fit gate retained; group approximations remain descriptive |
| Repeated MAIA, body-boundary and small-self measures | unavailable | No corresponding repeated/measure columns in released tables |
| Waveforms, measured breathing and acquisition provenance | unavailable | Source recordings and private metadata are outside the release |

## Interpretation and unavailable provenance

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
