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
wording or timing of the administered form. The project owner has since confirmed
that MAIA-2 was administered once before the experiment and spatial-frame ratings
after each intervention. This timing is owner-confirmed, not reconstructed from
CSV timestamps; the administered MAIA language and spatial pictogram key remain
unverified.

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
design. Sparse categories, 41 pairs and the unverified anchor key make the exact
directional comparison useful here. It remains the single overall paired condition
test and does not assume equal physical or psychological steps between categories.

## Associations and multiplicity

Before calculating the initial associations, the contract fixed 33 comparisons:
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

### Numerical change and baseline-trait moderation amendment

After reviewing those results, the owner prioritised signed spatial change and
confirmed the administration timing. The main follow-up outcome is now
`delta = post-Viscereality code − post-Control code`, independent of presentation
order. These are two post-intervention ratings, not a spatial pre/post baseline.
Eight subscale–delta correlations are the main association analyses; delta versus
the raw-RT slope interaction is ancillary. The same permutation and bootstrap
procedures apply, with a separately fixed seed (20261117). The earlier 33 estimates
remain exactly unchanged and supplementary, including the eight direction-only
sensitivities. There are 42 rank correlations in the complete audit, not eight
new confirmatory tests. Ranking numerical differences does not remove the
assumption that category steps are comparable.

For each continuous subscale separately, fit `delta ~ centred MAIA` and the
presentation-order sensitivity `delta ~ centred MAIA + centred order` (0 =
Control-first, 1 = Viscereality-first). With two complete conditions, the delta
slope estimates the Condition × MAIA interaction in the corresponding linear
repeated-measures model. The ordinary interaction test is `F = t²`, with 1 and
39 residual degrees of freedom, or 1 and 38 when including order. Independent
long-format participant-intercept fits verify this equivalence numerically.
Report ordinary uncertainty alongside HC3 heteroskedasticity-sensitive standard
errors and approximate t intervals/p values, plus leverage and Cook-distance
diagnostics; retain every participant. This is a modelling choice with independent
software validation, not a method attributed to the papers above.

All 16 fits and both uncertainty estimates are retained. No multiple-testing
correction is applied. Small-sample robust uncertainty is approximate; it does not
solve ordinal spacing, measurement error, confounding or carryover. Adding order
addresses a mean order difference in delta, not every possible period effect.
The baseline trait is a correlate/moderator, not a within-person mediator:
Condition cannot explain a change in a MAIA score measured only before exposure.
Correlations and interaction models reuse the same participants and are not
independent replications. The complete amendment was fixed in the executable
contract before computing these new estimates, after the earlier results were
known; it remains post hoc.

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
| Nine numerical-delta correlations and 16 moderation fits | Owner-authorised post-results amendment with confirmed measurement timing | All eight subscales, order/HC3 sensitivities; unadjusted and exploratory |
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
| Spatial-frame ratings | 41 post-intervention pairs | Distributions, transitions, exact comparison and signed numerical delta |
| Baseline traits and spatial/behavioural contrasts | 41 joint records | All 42 rank correlations and 16 moderation fits; RT slope is not a boundary |
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

Numerical delta has mean 0.756 category steps (SD 1.480), median 1, IQR 0–2 and
range −3 to 5. Of the eight main subscale correlations, Trusting shows the clearest
association with delta (rho=0.376, pointwise 95% CI 0.081–0.627, unadjusted
p=0.01605). Noticing has rho=0.273, p=0.08725; the other six main correlations also
have p>.05. Numerical delta is not clearly associated with the raw-RT slope
interaction (rho=−0.020, CI −0.328 to 0.294, p=0.90465).

The Trusting interaction slope is 0.613 code steps per MAIA point,
F(1,39)=7.681, ordinary p=0.00851; its HC3 95% CI is 0.065–1.160, p=0.02932.
Accounting for presentation order gives b=0.624, F(1,38)=7.987, ordinary
p=0.00747; HC3 CI 0.089–1.159, p=0.02349. Noticing is sensitive to the uncertainty
estimator: ordinary p=0.07054/0.09616 without/with order, versus HC3
p=0.01846/0.03124. This is less consistent across the planned analyses and does
not justify selecting whichever estimator produces a small p value.

The 33 earlier supplementary associations remain unadjusted; four have p<.05.
Among the 24 earlier MAIA–spatial comparisons, Trusting correlates with
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
language record. Administration timing is now owner-confirmed. Computation can
be reviewed independently of the remaining
unresolved construct and provenance questions.
