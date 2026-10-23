# Search and screening record

Review date: **16 October 2026, Europe/Berlin**. Earlier verified material from
15 October was reused. This is a focused narrative review, not a systematic
search or a formal consensus estimate.

## Question and scope

In human looming-stimulus tactile-response experiments, what supports a sigmoid
description of distance-related responses, what challenges it, and what methods
justify robust extraction, smoothing, model comparison and parameter uncertainty?
The focal outcome is continuous RT, not binary detection probability. A
psychometric-function citation therefore cannot by itself validate the RT model.

Included: direct PPS experiments, critical or meta-analytic PPS evidence,
relevant methodological papers, and official software/author sources for the
actual estimation families. Excluded from the synthesis: unrelated search
matches, inaccessible content, unverified bibliography entries, and claims beyond
the inspected abstract or code. No participant data were sent to search services.

## Tools actually used

The installed `multi-source-web-search` skill guided broad discovery, exact-title
refinement, evidence screening and source inspection. PubMed public searches and
indexed records were retrieved over HTTPS; official method and author code was
inspected through GitHub. Skills and active tool metadata were checked for
Consensus. **No Consensus MCP tool/server or general search connector was
available. Consensus searches were not executed.** Existing `consensus.app` links
in the repository bibliography are historical links, not evidence of a Consensus
run in this review.

## Search rounds

| Round | Query or retrieval | Result and decision |
| --- | --- | --- |
| Earlier broad discovery, reused | `"peripersonal space" AND (sigmoid OR logistic OR boundary)` | Followed by exact-title PPS searches; four relevant indexed abstracts retained (P1–P4) |
| Earlier narrowing, reused | Exact titles beginning `Dynamic sounds capture`, `Rapid Recalibration`, `Capturing the dynamics`, `Do sounds near the hand` | Selected experimental precedent, related-modality evidence, methodological alternative and critical meta-analysis; unrelated matches discarded |
| Currentness check | `"peripersonal space" AND (sigmoid OR logistic OR expectancy) AND 2021:2026[dp]` | Browser challenge; no current-coverage claim |
| Validation rationale | `"Bias in error estimation when using cross-validation for model selection"` | Varma & Simon, PMID 16504092; also inspected relevant returned Varoquaux et al., PMID 27989847 |
| Transparency, broad then narrow | `"The multiverse analysis"`, then `"Increasing Transparency Through a Multiverse Analysis"` | Initial mediation example less direct; refined query identified Steegen et al., PMID 27694465 |
| RT extraction rationale | `"Methods for dealing with reaction time outliers"` | Ratcliff, PMID 8272468; retained |
| Identification, broad then narrow | Full Raue title, then `"Structural and practical identifiability analysis"` | First attempt challenged; shorter refinement returned the exact Raue et al. record, PMID 19505944, among unrelated application papers |
| Selection-bias alternative | Exact Cawley & Talbot title | Returned unrelated record; excluded. JMLR full-paper URL was network-blocked |
| Additional critique | `"researcher degrees of freedom" AND "false-positive"` | Browser challenge; excluded |
| Bibliography/current-method checks | `"Computational models of peripersonal space representation"`; exact Wichmann & Hill part-I title | Browser challenges; existing repository entries were not promoted to inspected evidence |
| Independent source lane | Straka et al. author `FN_std_PPS_properties.m`, plus previously inspected official statsmodels/SciPy/drc sources | Author code re-fetched with matching hash; implementation sources support method descriptions, not empirical shape claims |

Exact URLs, response hashes, selected PMIDs and rejection decisions are recorded
in [searches.json](searches.json). The earlier sources and their hashes are in the
[source ledger](../analysis/sigmoid_literature_sources.json). No PRISMA counts are
claimed: this was targeted screening with reused records, not a reproducible
exhaustive database export. The evidence table contains 16 distinct works: nine
indexed abstracts, six methodological references inspected through software
sources, and one PPS model inspected through author code.

## Full-text attempts and stopping rule

PMC pages for Varma and Holmes returned browser challenges rather than articles.
Earlier PPS full-text attempts had the same limitation. The JMLR paper endpoint
and an attempted Columbia author-copy endpoint returned proxy CONNECT 403. The
author-copy URL was not verified as an available paper and is not cited as one.
Earlier Europe PMC, Crossref and PLOS access was blocked. These responses were
not treated as full text; no challenge or network restriction was bypassed.

The review stopped after broad discovery, a refined methodological round, source
reading and contrary-evidence checks had produced a coherent limited synthesis,
while additional current/full-text lanes were unavailable. This is a practical
access stop, not evidence that all relevant papers were found or that the field
agrees. Detailed sample sizes, exclusions, risk-of-bias assessments and exact
methods from inaccessible papers are deliberately not inferred from abstracts.

## Searches ready for Consensus when configured — NOT RUN

1. In human audiotactile looming paradigms, how consistent is evidence for a
   sigmoid PPS boundary after accounting for temporal expectancy and sound
   propagation? Include contrary experiments and meta-analyses.
2. How do logistic, log-distance and monotonic nonparametric response functions
   compare for PPS RT profiles, and what sampling supports midpoint and slope
   identification?
3. What evidence supports robust RT summaries and smoothing with sparse repeated
   measurements, and how should model-search uncertainty be evaluated?
4. What experiments or reviews published since 2020 change the conclusions of
   Hobeika et al. and Holmes et al.?

Any future results should be deduplicated by DOI/PMID and checked against the
original paper before changing the review. Positive results alone should not
define the inclusion criteria.

## Questionnaire extension, 16 October 2026

A second focused search covers MAIA-2 scoring, sample reliability, spatial frames
and association methods. See [the questionnaire review](QUESTIONNAIRES.md) and
[its complete retrieval ledger](../analysis/questionnaire_literature_sources.json):
six peer-reviewed works (one full article, five indexed abstracts), with all
22 retrieval/local-reference records, refinement queries and access failures.
The registration endpoint returned HTTP 403; the repository account was not
misrepresented as an inspected original registration.

## Baseline/model goal amendment, 18 October 2026 (UTC)

Question: Which literature-supported response models and inference methods can
test Condition, Phase and their interaction after subtracting Baseline RT from
AT RT, without confusing general facilitation with sigmoid boundary/sharpness?

The installed multi-source search workflow guided broad PubMed discovery, Crossref
discovery/identity checking, then focused original-source retrieval. Consensus MCP
and a general web-search connector were unavailable; neither ran. Only research
queries and public bibliographic identifiers were sent externally, not study data.

| Round | Query or source | Screening/access outcome |
| --- | --- | --- |
| Broad, baseline | `"peripersonal space" AND (baseline OR expectancy) AND (sigmoid OR logistic OR logarithmic)` | Three indexed records returned; retained Hobeika (PMID 31805302); body-ownership papers were less direct for the model comparison |
| Broad, inference | `"peripersonal space" AND (Bayesian OR "mixed effects" OR "mixed-effects")` | Ten returned records; retained Beccherle (35178603), reused Straka (36103520); other returned titles concern different constructs, neural models or paradigms rather than this parameter-inference question |
| Recent check | `"peripersonal space" AND (sigmoid OR logarithmic OR "curve fitting") AND 2021:2026[dp]` | One returned record (40684675), interpersonal-discomfort ratings; abstract read, excluded as direct evidence for audiotactile RT parameters |
| Independent discovery | Crossref `peripersonal space sigmoid baseline logarithmic`, five returned items | Broad book/chapter/thesis metadata, no sufficiently direct new fitting protocol; not used as substantive evidence |
| Narrowing, original method | Canzoneri DOI 10.1371/journal.pone.0044306, publisher full text | Methods, fitting results and discussion inspected; confirms individual five-point sigmoid/linear comparison and observed-extrema plateaus |
| Narrowing, critical evidence | Holmes PMC7181441, full text | Experimental Bayesian/conventional results and review/meta-analysis methodological sections inspected; baseline/control and fit-selection concerns retained |
| Narrowing, log-distance method | Hobeika DOI and exact Crossref DOI record | DOI full-text route returned CONNECT 403; Crossref confirmed identity. Claims remain based on the inspected indexed abstract |
| Narrowing, tactile baseline | Beccherle PMC9015983 | HTTP 200 browser challenge; no full text read. Indexed abstract is the substantive access level |

The three priorities emerging from the inspected evidence are logistic, logarithmic
distance and ordinary linear/constant comparison; they are not ranked by anticipated
significance. Probit/asymmetric/segmented candidates require additional applicable
method evidence and a fixed estimand before implementation. The full-text successes
supersede earlier access failures only for those exact retrieved sources; older
failure records remain valid historical observations.

This bounded update stopped after the direct sigmoid precedent, logarithmic
alternative and critical review established the comparison's scope; additional
returned records did not establish a competing directly applicable protocol.
The PubMed result pages are not an exhaustive database export, absence from these
queries is not absence from the literature, and inaccessible full text remains a
coverage limit. The new goal and source inspection are completed; expanded model
fits/effect tests are NOT RUN. Exact URLs, hashes, dispositions and claim limits
are stored under `baseline_model_amendment` in [searches.json](searches.json).

## Breathing phase, RT and external multisensory synchrony

The 23 October 2026 targeted follow-up compares the six trial-group phase deltas
with respiratory RT studies, contrary findings and explicit external synchrony-
detection tasks. The [comparison](RESPIRATION_RT.md) and [12-source query/access
ledger](respiration_rt_sources.json) distinguish inspected full texts from abstracts
and institutional reports. No directly matching respiratory-phase external
synchrony-judgment experiment was identified in these queries; no absence claim
or direct replication is inferred. Consensus required reauthentication, so native
web search/open supplied the evidence. No additional fitted model was run.
