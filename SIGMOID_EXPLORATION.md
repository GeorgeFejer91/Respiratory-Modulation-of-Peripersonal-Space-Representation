# Four-curve descriptive sigmoid goal

The owner explicitly requested a broad investigation of signal extraction,
local/kernel smoothing and smooth approximations, with a uniform analysis yielding
four descriptive Condition × Phase sigmoid curves, their midpoints and steepness.
This is a post hoc descriptive extension; the original raw-RT test and trial-level
fit-gated boundary analysis remain identifiable as their original analyses.

## Acceptance criteria

- Use all eligible participants under the same documented cleaning rule, with
  equal participant weight and the same extraction/smoothing/fitting algorithm
  across all four curves. Do not select a separate favorable method per curve.
- Search the scientific methods literature and record what each source supports.
  No citation can by itself establish a sigmoid or a PPS boundary in these data.
- Compare raw and robust cell aggregation, local constant/linear kernels,
  penalized smoothers, monotonic projection, direct constrained fits and pooling
  or regularization. Fit actual observed design points; an interpolated display
  grid adds no independent observations.
- Select a single descriptive method using explicit predictive/stability
  criteria within this post hoc exploratory exercise. Report the alternatives, including
  those whose sigmoid fits are poor or whose shapes are effectively flat.
- Produce all four model-based approximations and report midpoint, logistic
  scale/width, 10–90% transition width and derivative at the midpoint. State the
  coordinate convention. Show unsmoothed observations alongside fitted curves.
- Quantify uncertainty by resampling whole participants together across all four
  curves, refitting the extraction and fit. Record boundary hits and sensitivity
  to tuning/bounds. Identify model-dependent extrapolation beyond sampled support.
- Complete the paper's Results from these exact outputs and make the full
  extension executable/downloadable in the marimo browser workbook.

## Selection rule and interpretation

Prefer performance on held-out participants/design points and stable prediction
over in-sample R² of smoothed pseudo-observations. Retain a constant and a line as
diagnostic benchmarks. Stronger smoothing, shape constraints and shared-parameter
assumptions must remain visible in the report. A computable midpoint is a
descriptive model parameter; a narrow, data-supported physiological boundary
requires additional evidence. Report any dependence on regularization explicitly.

## Executed uniform analysis

The complete implementation is [descriptive_sigmoid.py](descriptive_sigmoid.py).
Candidate families and tuning choices were developed after inspecting the data;
none of this extension is described as preregistered. The final auditable search
uses 320 pipelines, the same five positions and all 42 complete participants.

| Component | Alternatives |
| --- | --- |
| Within-person cell extraction | Mean; median; 10% and 20% per-tail trimmed mean; 20% per-tail winsorized mean |
| No smoothing / shape restriction | Unsmoothed; increasing isotonic projection |
| Gaussian local constant / local linear | Each at normalized bandwidth .10, .15, .20, .30, .40, .50, .65, .80 |
| Tricube local linear | Bandwidth .50, .75, 1.00, 1.50; no robust residual iterations |
| Discrete curvature penalty | Lambda .0001, .001, .01, .1, 1, 10 |
| Gaussian then isotonic | Bandwidth .15, .20, .30, .50 |
| Logistic fitting | Separate widths or a common width across four curves |

This is 5 extractions × 32 smoothers × 2 fitting structures. Equal person weights
follow extraction; no participant is removed to make the group curves look better.
Winsorization replaces `floor(.20*n)` observations in each tail by the adjacent
retained order statistic. The penalty shrinks differences between adjacent slopes
at the actual unequal positions; it is not an exact cubic smoothing spline.
Tricube local linear fitting is a LOESS-like candidate, without claiming to
reproduce the full robust LOWESS algorithm.

Write normalized distance `x=(d−10)/90`. The logistic is
`RT = a + A * expit((x−m)/w)`, with `A∈[0,500] ms`, `m∈[0,1]`, and
`w∈[.05,1]`. Offset and amplitude are profiled analytically at each shape.
Selection searches 61 equally spaced midpoints × 35 geometrically spaced widths;
final estimates and bootstrap refits use 241 × 81. The smallest allowed 10–90%
transition is 19.8 cm, close to the minimum 17-cm design spacing. These are explicit
regularization choices, not established physiological constraints. Flat `A=0`
solutions remain possible and make midpoint/width unidentified. Expanded bounds
are also reported: midpoint `[-.5,1.5]`, width `[.01,2]`, amplitude `[0,1000]`.

### Common prediction target

Six fixed participant folds (seed 20261016) are crossed with five held-out
positions. Each fit uses only the training participants at the other four
positions, including the smoother. The prediction is centered on the training
curve's four unsmoothed extracted summaries. Each test person's target is their
raw mean at the omitted position minus their raw mean over the other four
positions. This fixes the scoring estimand across extraction methods with
different overall RT levels. The winner has the smallest mean squared error,
averaged across participants, positions and four curves. Constant and linear
benchmarks use the same folds/target. Reported scores are used for tuning and are
not unbiased post-selection generalization estimates. Fold errors are dependent.

Earlier prototypes compared within-extraction leave-position-out errors; those
scores cannot compare the different extraction estimands directly. The final
selection above uses the common raw-mean shape target for every candidate.

### Four curves obtained in the actual browser

The selected pipeline is `winsor20/gaussian_constant/0.5/separate`: a 45-cm Gaussian
kernel after participant-cell winsorization, then four separate logistic fits
under identical bounds. All four point estimates are nonflat and interior.

| Condition / phase | Midpoint (cm) | Logistic width (cm) | Midpoint RT slope (ms/cm) | Conditional midpoint interval (cm) |
| --- | ---: | ---: | ---: | --- |
| Control / Exhale | 71.50 | 35.29 | .0907 | [37.56, 88.00] |
| Control / Inhale | 96.25 | 42.56 | .0846 | [18.48, 100.00] |
| Viscereality / Exhale | 82.75 | 35.29 | .0900 | [31.82, 100.00] |
| Viscereality / Inhale | 25.38 | 30.38 | .0686 | [10.00, 93.32] |

The tuning RMSE is 47.053 ms, versus 47.317 ms for a line and 47.437 ms for a
constant. This is a small predictive improvement. The model describes winsorized
summaries, whose vertical levels differ from raw arithmetic means. It does not
establish sigmoid superiority. The 10–90% transition spans are 155.1, 187.0, 155.1,
and 133.5 cm, all wider than the sampled 90-cm span. Dashed full-S extrapolations
are displayed explicitly as model assumptions outside the observations.

`s` (called width in outputs) is the logistic scale in cm, not a Gaussian sigma.
Half-amplitude location is `m`; normalized midpoint slope is `1/(4s)`; RT slope
is `A/(4s)`; the 10–90% span is `2*ln(9)*s`. Subtracting a constant Baseline within
person/condition/phase translates these equivariant curves without changing their
shapes. The extension uses retained AT data and makes no same-label cue-time claim.

### Uncertainty and alternative approximations

One thousand whole-participant bootstrap draws (seed 20261017) preserve all four
curves and all five positions together. Extraction is deterministic within a
person and cached; the resampled group extraction, smoother and fit are recomputed.
The intervals above condition on the selected method and nonflat resamples.
Flat fractions are .9%, 8.7%, 3.2%, and 8.7%; midpoint-bound fractions, including
flat draws, are 2.0%, 21.0%, 6.3%, and 14.1%. Curve bands include flat resamples.
The bootstrap does not rerun selection; the intervals do not represent total
uncertainty including the method search or guarantee unconditional coverage.

The paired midpoint interaction is −82.125 cm, conditional interval
[−107.25, 25.62] cm from 828 jointly nonflat draws. It is a descriptive comparison,
with no confirmatory p value. All midpoint, width and RT-slope comparisons are
exported. The original raw-RT interaction remains p=.878116, and the original
participant fit gate remains 0/168. Group fits do not provide independent people
for boundary/questionnaire correlations.

A fixed trimmed-mean/Gaussian .30 reference also produces four interior sigmoid
midpoints (61.75, 84.63, 68.13, 31.38 cm) but has a worse common-target score
(48.784 ms). Trajectory-implied positions and expanded fitting bounds are separate
sensitivity outputs. The full JSON contains all candidate parameters and scores;
CSV exports contain the ranking, selected parameters and paired comparisons.

## Scientific sources and what they support

Online research used the following accessible official software documentation
and author repositories. It verified the methods and their cited bibliographic
references; it did **not** establish that the full cited papers/books were read.
Journal/search endpoints for Europe PMC, Crossref and PLOS returned the cloud
proxy's HTTP 403. Their domains were added to the saved environment configuration
draft; that draft requires publishing before it can change access. No claim of an
exhaustive literature review is made. Exact accessed-source hashes are recorded
in [sigmoid_literature_sources.json](../analysis/sigmoid_literature_sources.json).

| Source inspected | Support and limit |
| --- | --- |
| [statsmodels KernelReg documentation/source](https://github.com/statsmodels/statsmodels/blob/main/statsmodels/nonparametric/kernel_regression.py), citing Li & Racine (2007), *Nonparametric Econometrics* | Local-constant (Nadaraya–Watson) and local-linear Gaussian smoothing; prediction-based bandwidth assessment. Does not validate our particular bandwidth or PPS interpretation. |
| [statsmodels LOWESS source](https://github.com/statsmodels/statsmodels/blob/main/statsmodels/nonparametric/smoothers_lowess.py), citing Cleveland (1979), JASA 74, 829–836 | Local weighted regression as a signal-extraction family. Our tricube candidate omits robust residual iterations. |
| [SciPy smoothing-spline documentation/source](https://github.com/scipy/scipy/blob/main/scipy/interpolate/_bsplines.py), citing Wahba (1990), DOI 10.1137/1.9781611970128 | Fit–smoothness tradeoff and cross-validation. Our finite-difference penalty is an analogous discrete regularizer, not this spline implementation. |
| [SciPy isotonic regression](https://github.com/scipy/scipy/blob/main/scipy/optimize/_isotonic.py), citing Busing (2022), DOI 10.18637/jss.v102.c01 | Order-constrained least-squares projection. Monotonicity is imposed, not discovered by this projection. |
| [drc logistic model](https://github.com/DoseResponse/drc/blob/master/man/logistic.Rd), [joint/robust fitting options](https://github.com/DoseResponse/drc/blob/master/man/drm.Rd), [book citation](https://github.com/DoseResponse/drc/blob/master/inst/citation), Ritz et al. (2019), DOI 10.1201/b21966 | Ordinary four-parameter logistic parameterization, fixed/shared parameters and robust response modeling. Ordinary logistic is distinct from log-logistic. No claim that this repository's Python code is drc. |
| [SciPy bootstrap documentation](https://github.com/scipy/scipy/blob/main/scipy/stats/_resampling.py), citing Efron & Tibshirani (1993), *An Introduction to the Bootstrap* | Resampling-based parameter uncertainty. Our unit is the participant cluster; post-selection and boundary limitations are stated separately. |
| [Straka, Noel & Hoffmann author repository](https://github.com/ctu-vras/pps-normative-model), PLoS Computational Biology (2022), DOI 10.1371/journal.pcbi.1010464 | PPS profiles also have mechanistic impact-prediction models. The repository does not justify forcing the present RT data into a physiological sigmoid. |

With only five positions, adding wavelet detail, unconstrained five-parameter
asymmetry, or densely interpolated pseudo-observations cannot create independent
information about the transition. The finite, auditable search above achieves the
requested descriptive four-curve goal while retaining that limitation.
