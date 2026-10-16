# Why examine sigmoid PPS curves? A miniature literature review

**Evidence review: 16 October 2026 (Europe/Berlin).** This focused narrative review
explains the rationale and limits of the Study 5 exploratory analysis. It is not a
systematic review, a preregistration, or evidence that the desired curve must exist.

The defensible aim is to assess whether a common, transparent analysis can describe
four distance-dependent reaction-time profiles with identifiable transitions. A
sigmoid is a theory-motivated candidate. Smoothing and shape constraints are tools
whose influence must be measured; they cannot establish a physiological boundary
merely by producing a smooth S.

## Read this folder

- [Evidence table](EVIDENCE_TABLE.md): 16 relevant works, what was actually read,
  the claim each supports, and the limits of transferring it to Study 5.
- [Analysis rationale](ANALYSIS_RATIONALE.md): estimands, choice-by-choice
  justification, implementation links, and outstanding checks.
- [Search record](SEARCH_LOG.md) and [machine-readable retrieval record](searches.json):
  queries, screening, unavailable providers, and failed access attempts.
- [Bibliography](references.bib): reusable citations; inclusion does not imply
  that the full paper or book was accessible.
- [Source ledger](../analysis/sigmoid_literature_sources.json): exact inspected URLs,
  retrieval hashes and access levels.

## 1. The theoretical case for a sigmoid is plausible, not compulsory

In the looming-sound paradigm, sound distance is related to tactile reaction time.
[Canzoneri, Magosso and Serino (2012)](https://doi.org/10.1371/journal.pone.0044306)
provide direct audiotactile precedent for investigating a distance-dependent
transition. [Noel et al. (2020)](https://doi.org/10.1093/cercor/bhaa103) report sigmoid
visuotactile facilitation and rapid recalibration with stimulus history. These
studies motivate asking about transition location and sharpness. Their accessible
abstracts do not validate Study 5's particular bandwidths, trimming percentages,
parameter bounds, or respiratory manipulation.

A logistic curve provides interpretable descriptive quantities:

`RT(d) = a + A / (1 + exp(-(d-m)/s))`.

Here `m` is the half-amplitude location, `s` is a positive distance scale, and the
midpoint RT slope is `A/(4s)`. The 10–90% transition spans `2 ln(9) s`. Scale `s`
is not a Gaussian standard deviation, and a fitted midpoint is not automatically
an independently measured PPS boundary. For `A=0`, location and scale are
unidentified. With only five positions, good curve prediction can coexist with
poorly determined parameters. The broader distinction between fit and parameter
identifiability is supported by [Raue et al. (2009)](https://doi.org/10.1093/bioinformatics/btp358),
whose work concerns dynamical models rather than this RT model.

PPS theory also permits alternatives. The inspected author code associated with
[Straka, Noel and Hoffmann (2022)](https://doi.org/10.1371/journal.pcbi.1010464)
computes transition and slope summaries from impact-prediction profiles. This is
mechanistic model output, not an empirical validation of a logistic fit to human
RTs. It supports considering location and slope as descriptive questions without
assuming that one response function is mandatory.

## 2. Contrary evidence is central to the rationale

[Hobeika et al. (2020)](https://doi.org/10.1016/j.jneumeth.2019.108534) explicitly
question mandatory sigmoid fitting. Their abstract describes a fixed-distance
control for expectancy and a distance effect that becomes linear on a logarithmic
distance scale after accounting for expectancy. This matters because apparent
distance effects can depend on stimulus propagation and anticipation, as well as
spatial processing. Study 5's nominal Baseline delay labels do not establish the
same control: trial-relative tactile-cue timing cannot be assumed equal across
trial types. Smoothing cannot repair that design limitation.

[Holmes et al. (2020)](https://doi.org/10.1007/s00221-020-05771-5), reporting four
experiments and a meta-analysis, describe mixed support, small effects and
concerns about expectancy, controls and flexible analyses. This is a particularly
important counterweight to selecting only papers that report clear boundaries.
The source set therefore supports investigating distance-related responses, but
does not establish agreement that all such responses should be sigmoid. A claim
of field-wide consensus would exceed this limited review.

The three most directly useful starting papers are Canzoneri for experimental
precedent, Hobeika for a specific alternative explanation and response form, and
Holmes for critical experimental and meta-analytic evidence. Noel adds evidence
from a related sensory paradigm. Differences in modality, body location,
expectancy controls and outcome definitions limit direct transfer to Study 5.

## 3. Why examine robust summaries and smoothing?

RT summaries can be sensitive to extreme responses and exclusion rules.
[Ratcliff (1993)](https://doi.org/10.1037/0033-2909.114.3.510) compares approaches to
RT outliers and reports that robust distribution summaries can be less affected
by outliers and cutoffs than moment-based measures. This motivates checking means,
medians, trimmed means and winsorized means. It does not establish that a specific
20% rule is optimal here, that slow responses are invalid, or that these summaries
estimate the same quantity. Study 5 retains the original RT analysis and treats
these additional summaries as sensitivity choices.

Local-constant and local-linear kernels, local weighted regression, curvature
penalties and isotonic regression are established estimation families. The
[evidence table](EVIDENCE_TABLE.md) links the inspected official implementations
and their methodological references. A smoother trades variability for bias; an
isotonic fit imposes monotonicity. Neither creates new measurements. The Study 5
discrete penalty is not an exact smoothing spline, and its tricube candidate is
not the full iteratively robust LOWESS algorithm. These distinctions prevent
borrowing a method's reputation for a different implementation.

Trying several methods is defensible when the purpose is to reveal dependence on
choices. [Steegen et al. (2016)](https://doi.org/10.1177/1745691616658637) motivate
reporting a range of reasonable processing choices because a single selected
analysis can conceal fragile conclusions. Study 5's finite grid is inspired by
that transparency principle. It is not an exhaustive multiverse: choices about
the grid, cleaning, coordinates and curve families remain outside it. Reporting
only the smoothest or most sigmoid-looking winner would defeat this rationale.

## 4. What makes the comparison informative?

Every condition uses the same candidate set, selection rule and bounds. Each
person receives equal weight after within-person extraction. Candidates predict
the same centered, unsmoothed mean-RT contrast in held-out people, so they are not
rewarded simply for fitting their own smoothed targets. Equally processed linear
fits and a zero-contrast constant provide simpler benchmarks.

[Varma and Simon (2006)](https://doi.org/10.1186/1471-2105-7-91) show that reporting
the minimum cross-validation error used to select a model can be optimistic; their
simulations support nesting tuning inside an outer evaluation. The principle
motivates Study 5's inner pipeline selection and outer participant folds, although
their classifier experiments are not a validation of this particular regression
design. [Varoquaux et al. (2017)](https://doi.org/10.1016/j.neuroimage.2016.10.038)
further caution that cross-validation itself can be variable in small scientific
datasets. Tiny differences between RMSEs should not be treated as decisive tests.

The evaluation conditions on the already-cleaned participant profiles. Initial
participant-wide RT thresholds use all that person's eligible trials, including
the position later omitted from fitting. Training and test people remain separate,
but this is not an end-to-end prospective prediction of an unseen position from
uncleaned trials. The common scoring target also measures relative profile shape,
not absolute RT accuracy. Method families and visual thresholds were developed
after observing the data, so nesting does not retroactively make them confirmatory.

Participant-cluster bootstrapping preserves the four repeated-measure profiles
together. Its present intervals condition on the selected pipeline and imposed
bounds; parameter intervals additionally exclude flat fits. This is useful
conditional uncertainty, not a complete account of model-search uncertainty.

## 5. What the present data justify

The [verified browser report](../results/browser-analysis/analysis_report.md)
contains 42 participants and five nominal positions. None of the original 320
pipelines met the specified visible-transition criteria in all four curves. The
selected original curves had 10–90% spans of approximately 134–187 cm, exceeding
the sampled 90-cm range. A shape-constrained search produced four visible S curves,
but three scales reached the imposed floor and one midpoint reached the sampling
limit.

Nested prediction RMSE was 47.634 ms for the constrained family, 47.701 ms for the
tuned linear family, 47.772 ms for the original sigmoid family, and 47.437 ms for
the constant. These are descriptive scores, not independent replicate tests.
The unsmoothed curvature tests did not establish nonlinearity after correction;
that also does not establish linearity. The participant-level boundary gate
remains 0/168. A group curve cannot supply the missing participant boundaries.

The supported conclusion is therefore an **exploratory, reproducible analysis of
how extraction and shape assumptions affect four group profiles**. The data do
not presently establish four identified physiological PPS boundaries. Further
work should prioritize the unresolved checks in the rationale document and an
independent design with better transition sampling and expectancy control. Adding
more smoothers solely until the curves look persuasive would not strengthen this
conclusion.

## Access and interpretation limits

Consensus MCP was unavailable; it was not used. The installed multi-source search
skill guided PubMed discovery, exact-title refinement, and official/author-source
inspection. The nine empirical or methodological papers used here were inspected
at indexed-abstract level; six method references were checked through official
software sources, and the PPS impact model through author code. Full-paper
retrieval attempts were blocked or returned browser challenges. Current-literature
queries also encountered challenges. This review consequently supports bounded
claims from the inspected material, not detailed replications of inaccessible
papers or an exhaustive account of the literature through 2026.
