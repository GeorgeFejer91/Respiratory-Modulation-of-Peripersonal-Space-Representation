# Individual sigmoid parameters and common RT plateaus

Evidence checked 16 October 2026. This is an exploratory extension requested after
the original participant fit gate failed. Four Condition × Phase curves per person
remain the primary specification. All numerical results and the complete method
comparison are generated in the browser; the original gated hypotheses remain
unestimated. The [analysis contract](../workbook/ANALYSIS_PLAN.md) records the
protocol and subsequent amendments.

## Scientific motivation and limits

The [PPS evidence review](EVIDENCE_TABLE.md) provides both sigmoid precedents and
contrary evidence about expectancy and response shape. Those findings motivate a
candidate model, rather than a requirement that these data follow it. The earlier
review also explains local regression, identifiability and nested prediction.

[Ahn et al. (2011)](https://doi.org/10.1037/a0020684) report that hierarchical
Bayesian estimation improved parameter recovery over individual- or group-level
maximum likelihood in an Iowa Gambling Task simulation. This motivates examining
partial pooling and recovery here. Our estimator is a penalized finite-grid point
fit with bootstrap uncertainty, **not that paper's Bayesian model**. Its penalty,
bandwidth and visible-shape constraints are explicitly exploratory choices.

[Hedge, Powell and Sumner (2018)](https://doi.org/10.3758/s13428-017-0935-1)
show that robust group effects in common cognitive tasks need not yield reliable
individual differences for correlation studies. This supports assessing reliability
directly before interpreting PPS–MAIA links. Their results do not determine the
reliability of this experiment; our split-half and recovery analyses address it
with their own limited scope. Random split halves assess within-session stability,
not test–retest reliability, and simulation recovery depends on its assumed signal
and empirical residual distribution.

## What normalization does

For `RT(d) = b + a expit((d − m)/s)`, define the lower plateau
`L = min(b, b+a)` and separation `A = |a|`. Then
`normalized_RT = (RT − L)/A`. The fitted lower and upper plateaus are exactly
0 and 1. This affine transformation preserves midpoint `m` and width `s` and
retains decreasing curves. Normalized steepness magnitude is `1/(4s)` per cm;
the original signed RT derivative is `a/(4s)` ms/cm. These are different estimands.
This algebra is our derivation, not a claim borrowed from the cited papers.

The plateaus are fitted asymptotes, not necessarily observed endpoints. Observed
RTs can lie outside 0–1 and are never clipped. Flat curves cannot be normalized;
an amplitude interval containing zero flags an unstable denominator. Scaling a
weak response to unit amplitude can make it look strong, so every participant's
atlas page places raw means and uncertainty above the normalized **model-only**
geometry. Shared axes and identical panel sizes make the four shapes comparable.

| Specification | Purpose | Important assumption |
| --- | --- | --- |
| Separate plateaus for four individual curves | Primary flexible descriptive proxy | Five positions must inform four parameters; visible geometry and pooling can dominate |
| Pooled shape penalty, with strength selected uniformly | Stabilize weak shape estimates using other records | Individuals share useful shape information; not evidence that their boundaries are equal |
| Shared RT plateaus across one person's four curves | Reduce nuisance parameters; normalization sensitivity | All four responses share baseline and amplitude, including direction |
| Unregularized and finer-grid sensitivities | Show dependence on penalty/discretization | Neither removes sparse sampling or fixes linkage |
| Broad sigmoid, line and constant benchmarks | Assess prediction without requiring visible bends | Lower prediction error alone does not establish parameter recovery |

All 84 candidates use the same outcome target. Six outer folds repeat tuning,
holding linked recordings together. No questionnaire association enters selection.
The shared-plateau optimizer uses three starts and alternating exact conditional
updates; convergence is reported and is not a proof of a global optimum. Five
observed positions cannot justify adding fictitious plateau observations.

## Questionnaire links and recording integrity

MAIA-2 is a baseline trait; spatial ratings follow each intervention. The main
links correlate each of eight subscales with the Viscereality−Control parameter
difference (equal phase weights), and correlate that difference with the numerical
spatial-rating difference. Four separate curves remain the fitted units; averaging
their parameters to define a condition contrast does not replace those curves.
There are 27 main comparisons per model, 96 supplementary cell-specific MAIA links,
and three ordinal-direction sensitivities: 126 per model. Both plateau models and
three recording-exclusion specifications give 1,008 reported unadjusted tests.
Intervals are pointwise. No multiple-testing correction is applied, as requested.
Point-estimate permutation p values condition on estimated proxies; hierarchical
bootstrap intervals refit the parameters and therefore address additional uncertainty.
They need not give matching significance decisions.

The audit found that **P011 and P033 share all 408 behavioural records with
intervention labels swapped, despite different questionnaire responses**. Their
original recording-to-person mapping must be resolved. Source CSVs are preserved;
both curves are flagged. Linked copies are excluded together from each other's
pool and kept together in outer folds. Excluding both, or each separately, repeats
method selection and all associations. These sensitivities do not identify the
correct mapping. Full-release behavioural inference and RT–questionnaire links are
provisional; the questionnaire-only spatial/MAIA analysis does not use these RTs.

## Completed remaining-analysis amendment

The browser now adds 500 refits for each recording-exclusion cohort, rather than
leaving those associations at point estimates. It also reports all 72 cohort-mean
Condition, Phase and interaction contrasts across two models and four linkage
specifications. Every interval includes zero, as do all 216 main association
intervals across those specifications. No multiplicity adjustment was introduced.

The changes used in correlations have weak split-half rank reliability. Median
rho for midpoint change is −.074 with separate plateaus and .066 with shared
plateaus; normalized-steepness change is .052 and −.009. Signed RT-slope change
is .064 and .155. Known-signal contrast recovery is reported for both simulated
plateau structures. A large model point difference can result from pooled shape
centres without a well-identified physiological change; refitting uncertainty
must accompany it. The protocol is a post-results extension, not a new confirmation.

## Search and access record

The [machine-readable ledger](../analysis/participant_literature_sources.json)
records queries, exact URLs, retrieval hashes and failed access. Searches refined
from general hierarchical nonlinear individual estimation to cognitive-model
individual differences and exact titles. Ahn's PubMed abstract/metadata and Hedge's
indexed MEDLINE abstract were read. Ahn's publication year is **2011** (PubMed
indexing in 2013 is not the publication date). PMC attempts returned challenges.
Wilson and Collins' *Ten simple rules for the computational modeling of behavioral
data* was discovered, but its text was inaccessible and supplies no substantive
claim here. Consensus and a general web-search connector were unavailable; this
was a focused PubMed search, not a multi-provider or systematic review. No tool
or access capability is implied by the review's existence.

Implementations: [fitting and resampling](../workbook/participant_sigmoid.py),
[normalization and atlas](../workbook/participant_report.py), and the full
[browser results](../results/browser-analysis/analysis_report.md).
