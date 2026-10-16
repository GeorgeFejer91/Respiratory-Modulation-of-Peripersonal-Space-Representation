# MAIA-2 and spatial frame of reference: review and analysis rationale

**Reviewed 16 October 2026, UTC.** The goal is to analyse every released data
domain, including interoceptive self-report and spatial-frame ratings, with
auditable scoring and uncertainty. This focused narrative review supports a
post hoc extension; it is not a systematic review or a preregistration.

## The three closest analysis precedents

1. **Mehling et al. (2018), MAIA-2 development.** The
   [full paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC6279042/) describes eight
   dimensions, the revised 37-item instrument, internal consistency, inter-scale
   correlations and factor analyses in 1,090 museum visitors. Table 2 provides
   the final item ordering. This supports retaining the eight dimensions; it
   does not validate a new pooled score or factor structure in our 41 respondents.
2. **Eggart, Todd and Valdés-Stauber (2021), applied MAIA-2 psychometrics.** This
   [study in major depression](https://pubmed.ncbi.nlm.nih.gov/34170963/) reports
   alpha/omega, change sensitivity and clinical change thresholds. Reliability
   varied by subscale and occasion, including weaker Noticing and Not-Distracting
   at baseline. This supports reporting sample-specific reliability. The sample
   was hospitalized patients (110 enrolled; 87 pre/post); its clinical thresholds
   and change analyses do not transfer to our single MAIA record per person.
   **Access: indexed abstract**, not full methods.
3. **Hanley, Dambrun and Garland (2020), spatial frames and body boundaries.** A
   [randomized mindfulness study](https://pubmed.ncbi.nlm.nih.gov/33747250/) in 45
   healthy young adults used five sessions and repeated self-report measures.
   Its reported changes in spatial frames motivate examining this experiential
   outcome here. It does not establish a breath-VR effect, a PPS boundary, or our
   A–H anchor direction. Its repeated-session ANOVA and mediation cannot simply
   be copied into this paired-condition dataset. **Access: indexed abstract**,
   not its instrument or full analysis details.

The [original MAIA study](https://pubmed.ncbi.nlm.nih.gov/23133619/) (Mehling et
al., 2012; indexed abstract) also describes eight constructs and a mixed-method
development process. [Garfinkel et al. (2015)](https://pubmed.ncbi.nlm.nih.gov/25451381/)
distinguish self-reported interoceptive sensibility, objective task accuracy and
metacognitive awareness in 80 people. Its indexed abstract supports keeping these
constructs distinct: our MAIA scores are not heartbeat-detection accuracy,
measured respiratory compliance or evidence of a physiological mechanism.

[McNeish (2018)](https://pubmed.ncbi.nlm.nih.gov/28557467/), inspected at abstract
level, cautions that alpha has restrictive assumptions and discusses alternatives
including omega. We report raw alpha with uncertainty as an internal-consistency
diagnostic, not a validity certificate or automatic cutoff. Factor-based omega
also needs a defensible measurement model. We do not fit a new 37-item factor
model or delete items to optimize reliability in 41 respondents. Strong latent-
structure or cross-language invariance claims need separate validation. This is
our modelling judgment, not a universal minimum-n rule attributed to a paper.

## Scoring and parameters retained

MAIA-2 items use 0–5. Following the development paper's final map and reversal
direction, compute means for Noticing (1–4), Not-Distracting (5–10), Not-Worrying
(11–15), Attention Regulation (16–22), Emotional Awareness (23–27), Self-Regulation
(28–31), Body Listening (32–34) and Trusting (35–37). Reverse 5–10, 11, 12 and 15
as `5 − response`. The main paper was accessible; the supplementary questionnaire
and official UCSF site were not. Independent recomputation matches all 328 stored
subscale scores (41 × 8). This checks numerical agreement, not the language,
wording or timing of the administered form.

Retain each subscale's n, missingness, mean/SD, median/IQR, range, floor/ceiling
counts, alpha with a participant-bootstrap interval, and corrected item–rest
correlations. Export all 37 raw response frequency distributions. Require complete
constituent items for each subscale, with no imputation or fallback to stored
scores. The release has one fully missing questionnaire record and no partially
completed MAIA forms. Missing questionnaires do not exclude behavioural data.

For spatial frames, retain category frequencies, the 8 × 8 transition table and
within-person higher/equal/lower counts. An exact sign test uses change direction
without assuming equal distances between pictures. Report ties, the higher
fraction among non-ties with an exact binomial interval, and paired dominance
`(higher − lower) / all pairs` with a whole-person bootstrap interval. Show
order-stratified counts; these are descriptions, not a powered test of period
or carryover effects. Higher A–H codes are **not labelled allocentric** until the
administered anchor key is verified.

An ordinal regression could extend this analysis in a larger, well-documented
design. Sparse categories, 41 pairs and unverified administration/anchor details
make the exact directional comparison a useful minimal analysis here. No paired
normal-mean test assumes that A–H steps are equal physical or psychological units.

## Associations and multiplicity

Before calculating the new associations, the contract fixed 33 comparisons:
eight dimensions × four outcomes (Control spatial rating, Viscereality rating,
paired rating-change direction and raw-RT SOA-slope interaction), plus rating-change
direction versus the behavioural interaction. The latter contrast is
`(Viscereality Inhale − Exhale) − (Control Inhale − Exhale)` in slopes through five
participant cell means, in ms per primary SOA SD. It does not estimate a PPS boundary.

Spearman rho uses complete participant pairs and average ranks. Use 19,999
permutations under the independence null, a two-sided absolute-statistic tail and
the plus-one p-value rule. All 33 p values are reported without multiple-testing
correction; undefined tests remain unestimated. The plus-one rule is part of Monte
Carlo permutation inference, not adjustment across tests. The project owner
requested unadjusted reporting after inspecting the initial results, replacing
the initially specified Holm adjustment. This amendment does not make the
analyses preregistered or confirmatory. Pointwise 95%
intervals use 2,000 paired-person bootstrap draws, re-ranking within each draw;
degenerate draws are excluded and counted. Intervals are not simultaneous.
Permutation inference assumes exchangeable people under independence and does
not control demographic, order or other confounding. The behavioural contrast's
measurement uncertainty is not corrected by ranking.

The [installed SciPy 1.17.1 documentation](https://github.com/scipy/scipy/tree/v1.17.1/scipy/stats)
was inspected locally: Spearman guidance recommends permutation inference for
smaller samples; permutation documentation explains the plus-one correction and
alternative two-sided conventions. Online documentation hosts were blocked.
This is a **local software-reference inspection**, not another paper retrieval.
Our absolute-tail convention is explicit; it is not assumed identical to SciPy's
default doubled-smaller-tail convention.

The spatial condition comparison is a separate, single exploratory test family.
The 28 inter-subscale correlations are descriptive, with no additional p-value
screening. No median splits, significance-driven subscale/covariate selection,
or attenuation correction using uncertain alpha estimates is performed.

## Registration crosswalk

The [AsPredicted registration](https://aspredicted.org/az9f89.pdf) returned HTTP 403
on 16 October 2026. No accessible local copy was found. This does not establish
that a questionnaire hypothesis was absent. Current Methods and the executable
contract are the available account; older introductions describe trait moderation
more strongly, reinforcing the need to verify the original before submission.

| Question | Available plan evidence | Treatment here |
| --- | --- | --- |
| Condition × Phase × SOA RT | Current Methods describe a registered primary question | Existing pipeline retained |
| Individual midpoint/sharpness | Current Methods describe conditional fit-based inference | Trial-level gate retained |
| MAIA/SpFrRef versus boundaries | Current contract treats conditional associations as exploratory | Unestimated when the boundary gate fails |
| MAIA scoring/item/reliability audit | No newly verified registered prescription | Post hoc measurement audit |
| Paired spatial condition comparison | No newly verified registered directional test | Two-sided exploratory sign test |
| 33 rank associations | Post hoc extension; unadjusted reporting chosen after inspecting results | Report all with unadjusted p values and pointwise uncertainty |
| Repeated MAIA/body-boundary/small-self | Mentioned constructs do not establish available measurements | Unavailable without corresponding fields |

See [ANALYSIS_PLAN.md](../workbook/ANALYSIS_PLAN.md) and
[questionnaires.py](../workbook/questionnaires.py). Fixing this contract before
calculation limits selective reporting; it does not make the work confirmatory.

## Coverage of all released data domains

| Domain | Available data | Output / limit |
| --- | --- | --- |
| Roster, demographics and condition order | 42 people | Age/gender/handedness/order, completeness and QC |
| Planned/observed trials, index/part/block, responses and Catch | 17,114 trials | Quality denominators, missingness, cleaning and time-on-task |
| Condition, instructed phase, SOAs/distance labels | Trial design | Primary/sensitivity models, curves and coordinate checks |
| AT/Baseline, noise and recorded RT flags | Trial-level fields | Supplementary contrasts, noise Friedman and window sensitivities |
| 37 MAIA items/eight scores | 41 complete forms | Scoring, item/scale distributions and reliability uncertainty |
| Spatial-frame ratings | 41 pairs | Distributions, transitions, exact comparison and associations |
| Trait–behaviour links | 41 joint records | All 33 associations; RT slope is not a boundary |
| Participant boundary links | No four qualifying curves per person | Remain not estimable |
| Repeated MAIA/body-boundary/small-self | No corresponding columns | Not reconstructed from another measure |
| Measured respiration, waveforms, versions/dates | Outside release | Source-dependent checks unavailable |

“All data” means every released domain has an analysis or availability disposition.
It does not mean testing every variable combination or treating identifiers and
duplicated encodings as independent outcomes.

## Findings and interpretation

There are 41 questionnaire records; all 42 people remain in the primary behavioural
cohort. All 328 MAIA scores match. Raw alpha is 0.565 for Noticing and 0.589 for
Emotional Awareness; the other six range from 0.704 to 0.861. Intervals are
reported and no item is discarded because of these estimates.

Spatial ratings are higher under Viscereality for 22 people, lower for 6 and tied
for 13: exact two-sided p=0.00372. Among 28 non-ties, the higher fraction is 0.786
(exact 95% CI 0.590–0.917); paired dominance is 0.390 (percentile CI 0.171–0.610).
Both condition medians are D, illustrating why a median alone misses paired change.
Higher/equal/lower counts are 13/6/2 for Control-first and 9/7/4 for Viscereality-first;
these do not rule out period/carryover effects.

All 33 associations are reported without multiple-testing correction; four have
unadjusted p<.05. Among the 24 MAIA–spatial comparisons, Trusting correlates with
Viscereality ratings (rho=0.322, pointwise 95% CI 0.004–0.602, p=0.04255) and with
rating-change direction (rho=0.335, CI 0.025–0.606, p=0.03445). Direction means
lower/same/higher, not the magnitude of change. These related outcomes are not
independent replication. Self Regulation (rho=−0.357, CI −0.603 to −0.050,
p=0.02310) and Body Listening (rho=−0.312, CI −0.545 to −0.018, p=0.04740) correlate
with the raw-RT slope interaction. Each association uses 41 complete pairs.
Every estimate, unadjusted p value and pointwise interval is exported. These
post hoc associations are exploratory, with multiple comparisons and confounding
limiting inference. They do not rescue missing participant PPS boundaries or
establish an interoceptive mechanism; non-significance does not establish independence.

## Search and evidence limits

Six peer-reviewed works were retained: one full article and five indexed
abstracts. Consensus MCP and a general web-search connector were unavailable.
The multi-source skill guided public PubMed discovery, refinement to applied
MAIA-2 validation and original-source retrieval. Broad questionnaire/spatial
searches were refined to the named primary studies. Full-text attempts for Hanley
and Eggart, the MAIA supplement, and searches on ordinal/metric pitfalls and
permutation p values returned challenges; they supply no claimed full-paper
evidence. The [evidence ledger](../analysis/questionnaire_literature_sources.json)
records every URL, actual access, hashes, included claims and limitations.

This bounded search is not an exhaustive survey through 2026. The next documentary
needs are the original registration, administered pictogram key and MAIA
language/timing record. Computation can be reviewed independently of these
unresolved construct and provenance questions.
