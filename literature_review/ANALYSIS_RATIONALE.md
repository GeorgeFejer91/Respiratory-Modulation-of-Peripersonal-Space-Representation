# Analysis rationale and claim boundaries

This document records the rationale for the existing exploratory analysis after
the data and results were inspected. It does not change its registration status.
Source identifiers refer to the [evidence table](EVIDENCE_TABLE.md).

## Questions and estimands

The primary question remains the Condition × instructed Phase × SOA interaction
in retained trial RTs. The exploratory question is different: how well can one
common extraction/smoothing/model rule summarize four participant-weighted RT
profiles, and how much do transition parameters depend on that rule?

For extractor `T`, the descriptive response at condition/phase `g` and position
`j` is `mean_i T(retained RTs in person i, g, j)`. Mean, median and winsorized
versions are different population summaries. The midpoint of a curve through
their group averages is generally not the average of individual midpoints.
Inference across four plotted curves cannot replace inference across people.

All candidate scores use the same target:
`mean_RT(i,g,j) - mean_{k != j} mean_RT(i,g,k)`.
Here `mean_RT` denotes an **unsmoothed arithmetic mean of retained trials**.
Predictions are centered on the training group's four unsmoothed extracted cell
summaries. This evaluates profile shape rather than absolute response speed, and
the held-out person's other cells define the target rather than enter the fitted
training curve. The constant comparator predicts zero contrast.

## Choice → rationale → safeguard → limit

| Choice | Scientific rationale | Implemented safeguard | Remaining limit |
| --- | --- | --- | --- |
| Logistic candidate | PPS transition precedent (P1–P2); compact location/scale description (M6) | Flat solutions allowed; midpoint, scale, slope and 10–90% span reported | A logistic family is an assumption, not evidence of its truth |
| Robust cell summaries | Probe sensitivity to extreme RTs and cutoffs (M1) | Five extractors, original means retained; no extra participant exclusions to improve shape | Different estimands; percentages were chosen post hoc |
| Local smoothing | Examine variance–bias tradeoffs using established estimators (M2–M4) | Unsmoothed comparator, finite disclosed grid, fitting only at measured positions | Five positions contain little shape information; smooth curves do not add it |
| Isotonic and visible-shape constraints | Explicitly ask what follows under monotonicity and measured-range S-shape assumptions (M5) | Separate constrained family; flat fits and active constraints reported | Monotonicity/plateaus are imposed; thresholds are not validated PPS criteria |
| Uniform analysis across groups | Make descriptive contrasts comparable | Same grid, objective and bounds; one winning method across four curves | Uniformity alone cannot eliminate bias or validate physiological interpretation |
| Equal participant weights | Target the average person's cell summary, not a trial-count-weighted pool | Complete repeated-measure profiles retained together | Cell precision differs; this is not a hierarchical measurement-error model |
| Finite method audit | Reveal sensitivity to analytical choices (M9) | Export every candidate, retain original tests and failed gates | Not all defensible choices are included; the grid was not preregistered |
| Nested participant prediction | Reduce optimism from selecting on the evaluation score (M8, M11) | Whole people held out; smoothing/fitting omit each target position; tuned lines and constant included | Fixed initial cleaning; post hoc families; one outer partition; overlapping training folds |
| Whole-person bootstrap | Preserve within-person dependence when describing conditional uncertainty (M7) | Resample all four profiles together; report flat and bound-hit fractions | Method search and cleaning are not repeated; constrained intervals can look artificially narrow |
| Measured-range geometry and visual inspection | Expose broad or nearly linear fitted segments | Common axes, centered observations, separate normalized model panel, extrapolation labeled | Appearance cannot establish statistical or physiological support |
| Unsmoothed curvature check | Ask whether retained observations show any departure from a line | Participant contrasts, Holm adjustment across four groups, independent numerical verification | Normality/covariance assumptions; tests any nonlinearity, not specifically a sigmoid |
| Explicit competing explanations | Expectancy and response form matter in this paradigm (P3–P4) | Baseline/cue-time limitations and failed participant gate preserved | No suitable expectancy control can be reconstructed by smoothing |

Implementation owners: [cleaning and primary models](../workbook/paper_analysis.py),
[extraction/smoothing/fitting](../workbook/descriptive_sigmoid.py),
[geometry/nested evaluation](../workbook/sigmoid_shape.py), and
[figures/report](../workbook/publication_report.py). The executable contract is
[ANALYSIS_PLAN.md](../workbook/ANALYSIS_PLAN.md); exact grids and results are in
[SIGMOID_EXPLORATION.md](../workbook/SIGMOID_EXPLORATION.md).

## What the validation actually covers

Participant-wide mean ±2.5 sample-SD trimming is performed before these candidate
comparisons. Its thresholds are calculated separately for each person from that
person's eligible AT and Baseline hit RTs across all positions. No held-out person's
RTs determine a training person's threshold. However, the omitted position can
affect its own person's precomputed cleaning threshold. Therefore the current
assessment is conditional on cleaned complete profiles, not prospective prediction
with all preprocessing learned from the four available positions.

Inner selection is repeated within outer training participants; it still uses all
five positions in those training people. The design coordinates used in shape
constraints are known in advance. These choices assess new people at the known
design. They do not establish performance at new distances or under different
stimulus timing. The small RMSE differences are not paired significance tests, and
the six overlapping training sets are not six independent experiments.

The post hoc visual criteria require the fitted 10–90% change within the observed
range, two sampled positions on either side of the midpoint, a position in the
20–80% transition, and sufficient departure from a line. These criteria make the
display requirement explicit. Their numerical cutoffs and the 4.5-cm scale floor
have no independently validated physiological status. A bound-hitting estimate
reports an assumption-sensitive approximation.

## Completed follow-up checks and remaining evidence limits

The post-results remaining-analysis amendment now addresses the feasible shape
checks on the 40-record cohort excluding both ambiguous recordings:

- **Log distance:** 160 pipelines receive the same summaries and smoothers as
  lines, with physical-distance smoothing and a log-distance response. All five
  families use the same nested person/position target. Visible sigmoids improve
  on a constant by only 0.105 ms; log distance does not improve prediction. This
  compares response shapes and cannot reproduce P3's expectancy control.
- **Geometry sensitivity:** nine fixed specifications cross three width floors
  with permissive/existing/strict coverage, flank sampling and curvature criteria.
  All are reported. Their descriptive leave-position RMSE spans 47.47–94.59 ms;
  the poorest permissive specification is retained, not discarded.
- **Selection stability:** 30 whole-person resamples repeat all 320 visible-method
  selections, keeping repeated copies together in validation folds. They select
  27 distinct methods; the most frequent appears three times. This diagnoses
  instability, not selection-adjusted confidence coverage.
- **Individual identification:** the individual extension includes known-signal
  recovery, refit intervals and repeated split halves, now also for Condition,
  Phase and interaction contrasts. Midpoint-change rank reliability is approximately
  zero. All 72 mean-contrast and 216 main association intervals across plateau and
  linkage specifications include zero. See [individual parameters](INDIVIDUAL_PARAMETERS.md).

The finite checks do not establish a physiological sigmoid. Calibrated
method-selection-adjusted intervals, serial-dependence calibration, formal
profile-likelihood regions and recovery under a wider range of generating
processes remain unestablished. These are additional research designs, not hidden
completed evidence. Existing predictions condition on participant-wide cleaning;
prospective forecasting would need preprocessing learned without the omitted
position and a deployable target. The present report makes the narrower
cleaned-profile claim.

Source recording identity, timing/breathing traces, a functioning Consensus
connector and independent dense-distance/expectancy controls remain unavailable.
Full-text coverage remains partial; the amendment below adds two direct article
inspections. Further smoothing cannot resolve the source/design limits.

## Baseline-corrected model comparison: 18 October 2026 amendment

The owner requests baseline subtraction and an expanded search for experimental
effects using Bayesian and frequentist sigmoid, linear and logarithmic models.
The analysis goal is recorded in the workbook contract; the expanded fits/tests
have **not** been run. This is a post-results extension of the literature review.

### What the literature specifically adds

| Source and access checked now | Relevant method or finding | Transfer to the new goal |
| --- | --- | --- |
| [Canzoneri et al. (2012), P1](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0044306), full-text Methods, Results and Discussion | Compared individual five-point sigmoid and linear fits; fixed sigmoid asymptotes to each cell's observed minimum/maximum, then estimated midpoint and slope; fitted tactile timing relative to sound onset | Direct audiotactile precedent for both families and a fixed-extrema sensitivity. These extrema contain sampling error; their treatment as fixed does not remove that uncertainty. Do not transfer its timing axis or sample-extrema assumptions silently to Study 5 |
| [Hobeika et al. (2020), P3](https://pubmed.ncbi.nlm.nih.gov/31805302/), indexed abstract and Crossref identity | Added a fixed-sound-distance expectancy baseline and logarithmically spaced distances; reports a linear response on log distance after expectancy subtraction | Direct rationale for the log-distance comparator. Study 5's Baseline trial labels do not establish an equivalent fixed-distance, cue-time-matched control; the full article was inaccessible |
| [Holmes et al. (2020), P4](https://pmc.ncbi.nlm.nih.gov/articles/PMC7181441/), full-text experiments, review/meta-analysis and methodological discussion | Uses conventional and Bayesian tests; questions unmatched baseline comparisons and excluding poor sigmoid fits; documents heterogeneous and sometimes insensitive/null effects | Supports joint/paired treatment of baseline measurements, explicit uncertainty and preserving unsuccessful curves. Its evidence for a near–far RT difference is a different estimand from a respiratory effect on sigmoid midpoint |
| [Beccherle et al. (2022), P6](https://pubmed.ncbi.nlm.nih.gov/35178603/), indexed abstract | In a 40-person visuotactile study, tactile-only RT depended non-monotonically on delivery delay; authors recommend removing tactile-only RT from multisensory RT | Supports examining the Baseline response rather than treating it as noise-free. Modality/body-site differences and unverified Study 5 timing limit transfer; the full-text attempt returned a challenge |

The direct PPS comparison priorities are therefore (1) a logistic with transparent
plateau assumptions and individual uncertainty, (2) a log-distance alternative
with explicit baseline/control limitations, and (3) an ordinary line/constant
benchmark. This ranking concerns relevance, not expected significance. Probit,
Gompertz, log-logistic, smooth or segmented curves remain generic methodological
candidates until an applicable source and estimand justify inclusion. A new 2025
paper on sigmoid interpersonal-discomfort ratings was screened but supplies no
direct validation for audiotactile RT boundaries.

### Correction changes the estimand, not automatically the shape

The owner specifies `corrected RT = AT RT − Baseline RT`. Following the existing
`paper_analysis.sigmoid_fits` correction, the primary Baseline mean is specific to
participant, Condition and Phase, pooled across nominal SOAs. For
`f(d)=a+A*expit((d-m)/w)`, subtracting a scalar B gives
`f(d)−B=(a−B)+A*expit((d-m)/w)`. With a free intercept and consistently transformed
constraints/priors, m and w are unchanged. This is an algebraic property, not an
empirical result attributed to the papers. Likewise, subtracting a constant
preserves a linear or log-distance slope. Shared-plateau constraints, pooling or
priors can change this invariance and must be disclosed.

The primary 40-record cohort has 4,192 retained Baseline RTs and complete nominal
cells, but just 1–6 Baseline observations per person/condition/phase/SOA. Same-label
subtraction can alter the distance profile and add considerable estimation error.
It is a useful sensitivity with unverified time matching, not an automatic
expectancy correction. A shared baseline mean introduces covariance among the
corrected trials; the planned joint likelihood/refits must retain this covariance.
No log transform or arbitrary positive offset is appropriate for signed corrected
RTs. `log(distance)` and `log(RT)` answer different questions.

### Results and stopping criteria

For every included family, test Condition, Phase and their interaction. Sigmoids
provide model-conditional 50%-amplitude locations and normalized derivatives;
ordinary linear/logarithmic functions have no intrinsic plateau midpoint. Compare
all families using observed-range predictions, mean corrected RT and far−near
response differences, without renaming these quantities PPS boundaries.

The source-linked registry will distinguish joint Bayesian estimation, frequentist
nonlinear/mixed estimation, paired tests and resampling/robustness checks. Retain
null, reversed, weakly identified and failed fits; evaluate known/null recovery,
predictive performance and baseline uncertainty. Report all unadjusted p values
as requested, with the full family and pointwise intervals. Nominal discoveries
after a method search remain exploratory; agreement among dependent model
specifications does not supply independent replication. Completion means the
feasible declared worklist is answered, including inconclusive outcomes, rather
than continuing until a significant p value appears.

This focused update used PubMed discovery, Crossref and original PLOS/PMC pages.
Consensus and a general web-search connector were unavailable. Exact searches,
retrieval hashes, screening reasons and inaccessible text are in
[the amendment ledger](searches.json). It is not an exhaustive review of every PPS
method or an assertion that every literature procedure is suitable for Study 5.

## Wording suitable for the paper (earlier analysis)

> We treated the sigmoid as a theory-motivated descriptive candidate and assessed
> sensitivity to robust extraction, smoothing and shape restrictions using one
> common procedure across conditions. We retained the primary analysis and
> participant-level fit gate, disclosed all candidate pipelines, and compared
> relative-profile predictions in held-out participants with equally processed
> linear fits and a constant. This exploratory evaluation conditions on the initial
> cleaned profiles. The resulting constrained curves illustrate the consequences
> of explicit shape assumptions; their fitted midpoints and slopes do not establish
> identified individual or physiological PPS boundaries.
