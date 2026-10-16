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

## Outstanding work, not completed evidence

1. **Compare a log-distance response fairly.** P3 motivates `a+b log(d)` alongside
   constant, linear and logistic families under the same target and nested
   selection. The current 800 candidates do not include this family. Such a
   comparison could be exploratory with existing data, but would not reproduce
   P3's expectancy-controlled experiment or repair Study 5's timing limitations.
2. **Vary visible-shape thresholds and scale floors uniformly.** Existing expanded
   bounds concern the original family; they do not provide a systematic sensitivity
   analysis of all visible-shape criteria. Fix and disclose a finite grid before
   examining additional fits; report all outcomes without choosing the most
   attractive geometry.
3. **Assess parameter identification beyond conditional intervals.** M10 motivates
   checking how much data constrain parameters. The current profiled optimizer is
   not a profile-likelihood confidence analysis. Repeating selection in resampling,
   appropriate simulation/recovery checks and sensitivity to the participant split
   would probe additional uncertainties; none has been demonstrated by this review.
4. **Separate prospective preprocessing from target construction if forecasting is
   claimed.** Re-estimate preprocessing without the omitted position and define a
   deployable target. The present report makes the narrower cleaned-profile claim.
5. **Obtain stronger external evidence.** Full-text examination, a functioning
   Consensus search, and an independent dense-distance/expectancy-controlled study
   remain necessary for broader literature or physiological claims.

These are prioritized open checks, not a promise that a successful sigmoid will
emerge. They do not prevent reporting the present exploratory findings with their
limits. The empirical goal remains open while a constrained approximation lacks
support beyond simpler benchmarks or has poorly identified parameters.

## Wording suitable for the paper

> We treated the sigmoid as a theory-motivated descriptive candidate and assessed
> sensitivity to robust extraction, smoothing and shape restrictions using one
> common procedure across conditions. We retained the primary analysis and
> participant-level fit gate, disclosed all candidate pipelines, and compared
> relative-profile predictions in held-out participants with equally processed
> linear fits and a constant. This exploratory evaluation conditions on the initial
> cleaned profiles. The resulting constrained curves illustrate the consequences
> of explicit shape assumptions; their fitted midpoints and slopes do not establish
> identified individual or physiological PPS boundaries.
