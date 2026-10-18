# Decision log

Record only durable choices whose rationale future agents would otherwise have
to rediscover. Source and tests remain the authority for implementation facts.

## D-0001 — Minimal control plane before product scaffolding

- Date: 2026-10-02
- Status: Accepted
- Context: The project needs a predictable AI entrypoint without choosing an
  application stack or inventing product structure prematurely.
- Decision: Use a short root `AGENTS.md` that routes to a lowercase `for-ai/`
  control plane. Keep product output outside that folder and add project files,
  skills, and protocols only for current requirements.
- Consequences: New agents get a reliable map and readiness gates. The first
  product task must still choose the smallest suitable output structure.
- Supersedes: None

## Record format

For later decisions, add one compact entry with:

- identifier and title;
- date and status (`Proposed`, `Accepted`, `Superseded`, or `Rejected`);
- context;
- decision;
- consequences;
- supersession link when applicable.

Do not rewrite accepted history to hide a changed direction. Add a superseding
decision and link both entries.

## D-0002 — Private unified publication candidate

- Date: 2026-10-02
- Status: Superseded for the audited CSV release by D-0004
- Context: The cleared export includes 42 independent people and a separate
  private identity/provenance archive.
- Decision: Publish only deidentified primary behavioral rows in this private
  repository, renumbered contiguously from `P000` to `P041`. Keep the source
  crosswalk and raw recordings outside it; require an ethics and consent review
  before any public visibility change.
- Consequences: One person key joins the two CSVs. The private source archive
  remains necessary for provenance audits and any future source correction.
- Supersedes: None

## D-0003 — Preserve the earlier manuscript as a draft

- Date: 2026-10-02
- Status: Superseded by D-0004; historical material remains archived
- Context: The active manuscript reports 40 people, while the current
  publication-data candidate contains 42.
- Decision: Keep the complete existing preprint and referenced figures
  available for writing, but do not relabel its estimates as 42-person results.
  Promote analyses only after a reproducible rerun and review.
- Consequences: The Overleaf project compiles, but the scientific submission
  gate remains open until the text, tables, and figures are refreshed.
- Supersedes: None

## D-0004 — Browser analysis and authorised deidentified release

- Date: 2026-10-15
- Status: Accepted; source-private visibility superseded by D-0011
- Context: The owner requested a complete browser-based marimo paper companion,
  authorised participant-data publication after name removal and backup, and
  confirmed existing ethical approval.
- Decision: Publish the audited 42-person CSV pair with the executable workbook;
  retain verified separate private backups and private source-repository visibility.
  Execute the fixed data-supported analysis in Pyodide, validate numerics natively,
  and derive manuscript statistics/figures from the exact browser download. Preserve
  the prior 40-person text and figures as historical material.
- Consequences: Full browser computation and actual Pages deployment require their
  own observed checks. Missing private provenance stays unavailable and failed
  sigmoid gates leave boundary follow-ups not estimable. Author review, collection
  history and ethics-statement details remain necessary before paper submission.
- Supersedes: D-0002's restriction on this exact CSV release and D-0003's active
  40-person draft state; their privacy and preservation principles remain.

## D-0005 — Uniform descriptive sigmoid extension

- Date: 2026-10-15
- Status: Accepted; computational completion criterion superseded by D-0006
- Context: The owner explicitly requested broad signal extraction and smoothing
  to obtain four descriptive sigmoids with midpoint/steepness comparisons and
  complete the Results, even if participant-level boundary inference fails.
- Decision: Retain the original tests and gate; add a post hoc 320-pipeline
  uniform group analysis, common-target prediction scores, 1,000 participant
  bootstrap draws and full method/coordinate/bound sensitivity. Use the exact
  browser download for the expanded Results and figures.
- Consequences: Four computable group curves achieve the descriptive goal.
  Their broad intervals, flat resamples, small advantage over a line and
  extrapolated plateaus prevent a precise physiological-boundary claim.
- Supersedes: Any reading of D-0004 that would prevent this expressly authorized
  descriptive extension. Its participant inference gate and privacy rules remain.

## D-0006 — Visible, supported PPS-like transition

- Date: 2026-10-15
- Status: Accepted
- Context: The owner requires visible sigmoid curvature rather than a fitted
  sigmoid that looks linear, and extends the goal to a characteristic PPS shape.
- Decision: Assess measured-range transition coverage, midpoint sampling,
  curvature, equally processed linear prediction and visual figure quality.
  Evaluate explicit shape constraints as a labeled sensitivity; never count
  enforced geometry as empirical support. Retain unsuccessful alternatives.
- Consequences: Four computational curves alone no longer complete the goal.
  Report an unresolved scientific goal when the observed data do not support it.
- Supersedes: D-0005's claim that computable curves alone achieve completion.

## D-0007 — Spatial change as the follow-up outcome

- Date: 2026-10-16
- Status: Accepted analysis direction; timing and execution updated by D-0008.
- Context: The owner prioritises the within-person spatial-frame contrast over
  absolute condition ratings and asks how MAIA-2 dimensions can explain that
  contrast. The release has paired Control/Viscereality ratings and one MAIA-2
  record per person; questionnaire timing and pictogram anchors were unverified
  when this direction was accepted.
- Decision: Define `delta_spfrref = Viscereality code - Control code` for complete
  pairs, irrespective of presentation order. These are condition differences,
  not verified pre/post changes. Retain the existing two-sided exact sign test
  as the single overall paired condition comparison, with transitions, ties and
  condition distributions for context. Make the numerical delta the main outcome
  for subsequent MAIA–spatial associations; retain previous absolute-rating
  associations as supplementary audit results rather than deleting their history.
- Implementation specification: Examine each of the eight continuous MAIA-2
  subscale means against delta using Spearman correlation, participant-pair
  permutation inference and pointwise paired-person bootstrap intervals. Keep
  unadjusted p values and report every comparison. Do not create a MAIA total,
  dichotomise subscales, or select Trusting as a newly confirmatory predictor
  because it showed the earlier exploratory association. Fix the new comparison
  set and resampling details before computing it and record this post-results
  change in the executable analysis contract before promotion.
- Measurement interpretation: Numerical differences count steps on the recorded
  A–H/1–8 coding. Their magnitudes assume comparable category steps; Spearman
  ranking after subtraction does not remove that assumption. Retain
  `sign(delta_spfrref)` as an ordinal sensitivity and distinguish it in labels
  and exports. Do not call higher codes allocentric/egocentric without the
  administered anchor key or describe code differences as physical distances.
- Model option: A repeated-measures ANCOVA or mixed model with Condition,
  centred continuous MAIA and Condition × MAIA asks whether the condition contrast
  varies with MAIA. With two complete conditions, a linear delta-on-MAIA regression
  expresses the same interaction question under the corresponding linear model
  assumptions. Include presentation order in a prespecified sensitivity; this
  does not establish the absence of carryover. Avoid fitting all eight correlated
  subscales and their interactions together in the 41-person sample or treating
  correlation and interaction results as independent replication. This model
  remains an option, not a completed test or an automatic replacement for the
  main delta correlations.
- Causal boundary: This is association/moderation, not evidence of mediation.
  A single MAIA record cannot identify a within-person Condition → MAIA change →
  spatial-change pathway. Verify administration timing before calling MAIA a
  precondition trait moderator; do not infer a causal mechanism from correlations.
- Consequences at acceptance: The browser report had 33 prior associations and
  uses three-level change direction. Neither its Trusting coefficient nor its
  p value may be relabelled as a numerical-delta result. New numerical results
  require the existing native/browser, manuscript and publication gates.
- Supersedes: Equal emphasis on separate condition-level spatial correlations
  for future follow-ups; preserves prior results, the paired comparison, privacy
  rules, exploratory status and the participant PPS-boundary gate.

## D-0008 — Baseline MAIA and post-intervention spatial contrasts

- Date: 2026-10-16
- Status: Implemented; actual browser download, independent numerical checks,
  native/browser parity and manuscript PDF visually verified.
- Context: The owner confirmed that MAIA-2 is administered once before the
  experiment, spatial ratings after each intervention, and requested execution
  of all proposed analyses. Timing is owner-confirmed; CSV timestamps do not
  independently establish it. The pictogram key and MAIA language remain absent.
- Decision: Implement all eight subscale correlations with signed numerical
  delta, one ancillary delta–RT correlation, and eight separate continuous-trait
  interaction models with/without centred presentation order. Fix 19,999
  permutations, 2,000 paired bootstrap draws and seed 20261117 before calculating
  the extension. Report ordinary interaction F/t inference and HC3 approximate
  t uncertainty, diagnostics and all estimates without multiple-testing
  correction. Preserve the 33 earlier associations and their random stream.
- Interpretation: Delta compares post-Viscereality with post-Control, regardless
  of sequence. MAIA is a baseline correlate/moderator, not a mediator. Numerical
  delta assumes comparable category steps; direction-only correlations remain
  sensitivities. Neither order adjustment nor HC3 resolves carryover, ordinal
  measurement or causal identification. The amendment remains post hoc.
- Verification: Independently compare all 16 fits with statsmodels and verify
  their ordinary interaction inference using long-format participant-intercept
  models. Require actual browser execution, complete native/browser parity,
  manuscript reconciliation and visual PDF review before promotion/publication.
- Supersedes: D-0007's unresolved timing, optional model and unexecuted-extension
  state. Preserves its estimand, full reporting, measurement limits and PPS gate.

## D-0009 — Individual sigmoid proxies and questionnaire links

- Date: 2026-10-16
- Status: Accepted exploratory goal; execution subject to the existing gates.
- Context: The owner requests the best defensible participant-specific sigmoid
  approximations and additional questionnaire associations, with explicit
  caveats in the paper. They selected four Condition × Phase curves per person
  as primary, rather than pooling respiratory phases during curve fitting.
- Decision: Compare one common catalogue of extraction, local smoothing and
  shape-pooling methods across all people/cells, selected using RT prediction
  without questionnaires. Fit both measured-range sigmoid geometry and a broad
  shape sensitivity; compare lines/constants. Report signed response amplitude,
  midpoint, width, normalized steepness and actual RT derivative, intervals,
  stability, recovery and all person-level plots. Do not set an amplitude floor
  or conceal reverse, flat or weakly informed fits. Link the estimates to all
  eight baseline MAIA dimensions and Viscereality–Control spatial delta with
  unadjusted inference and the complete comparison set fixed before calculation.
- Interpretation: The requested complete parameter table is exploratory model
  output, not a claim that every individual has an identified PPS boundary.
  Constrained curvature, shrinkage and normalized model plots cannot supply
  empirical evidence of a transition. The original trial-level gate and its
  unavailable confirmatory follow-ups stay intact.
- Supersedes: Any restriction against a separately labelled individual-proxy
  extension after the failed original gate; preserves that gate and D-0006's
  distinction between imposed geometry and observed PPS shape.

### D-0009 implementation and linkage amendment

The owner also requested common RT plateaus. Implement fitted lower/upper
asymptote normalization to 0/1, preserving raw RTs, reverse direction and midpoint;
flag amplitudes whose bootstrap interval includes zero. Retain separate and
within-person shared plateau models. Full-release output contains 168 primary
proxies and 168 shared-model sensitivities. Recovery and reliability do not support
calling every proxy an identified boundary; preserve that distinction in paper,
plots and workbook. All questionnaire p values remain unadjusted.

The execution audit discovered matching 408-trial records for P011/P033 with
swapped condition labels and different questionnaire responses. Preserve source
CSVs, request source mapping, keep linked recordings together in new CV folds and
out of each other's pooling priors, and report exclusions of both and each
separately. Do not silently choose an identity or claim 42 independent behavioural
recordings. Original full-release calculations remain an explicitly provisional
audit record. Questionnaire-only MAIA/spatial results do not depend on RT mapping.

### D-0009 remaining-analysis amendment

Complete the finite post-results checks in `workbook/ANALYSIS_PLAN.md`: primary
behavioural linkage exclusions, uncertainty and stability of parameter changes,
refit intervals for every exclusion, log-distance prediction, a fixed geometry
grid and repeated method selection. Preserve all outcomes and report the earlier
analyses separately. Selection frequencies are stability diagnostics, not
selection-adjusted confidence coverage. Completion of these checks does not
close the empirical boundary-identification goal or source-mapping requirement.

### D-0010 — repeated-measures parameter question

Use balanced 2×2 contrast ANOVAs/ANCOVAs for fitted midpoint and normalized
sharpness, with baseline MAIA dimensions and spatial delta kept continuous.
Each predictor enters separately, with order and HC3 sensitivities and hierarchical
curve-refit intervals. Emphasise both-ambiguous-record exclusion for this new
question; retain all four linkage specifications and both plateau models.
Select curve fitting using RT prediction only. No significant-result or causal
goal is implied; unreliable fitted differences remain unreliable after ANOVA.
The full fixed specification and test count are in workbook/ANALYSIS_PLAN.md.

## D-0011 — Public repository and UnderTree project

- Date: 2026-10-16
- Status: Accepted
- Context: The owner explicitly identified `GeorgeFejer91/Study5_Publication`
  and requested adding it to UnderTree and making that repository public.
- Decision: Add a local clone through UnderTree's project-folder workflow and
  make the existing GitHub repository public after reviewing tracked files and
  history. Preserve the manuscript's LaTeX sources; project registration does
  not imply conversion or ChatGPT manuscript-sharing permission.
- Consequences: Public visibility covers source and reachable Git history as
  well as the previously authorised CSV release. Private backups, identity
  records and raw recordings remain excluded. Scientific interpretation,
  submission readiness and live Pages deployment keep their separate gates.
- Supersedes: The source-private visibility requirement in D-0002 and D-0004;
  the deidentification, backup and scientific-evidence requirements remain.


## D-0012 — Results before manuscript narrative

- Date: 2026-10-17
- Status: Accepted
- Context: The owner requests an explicit analysis roadmap and a level-by-level
  results report before agreeing the paper narrative, including a Bayesian
  approximation for four individual sigmoid cells and exploratory joint links.
- Decision: Make `ANALYSIS_ROADMAP.md` the question/checklist owner; freeze manuscript
  drafting and preserve version-1.9 paper/reference outputs. Add a separately run,
  hashed results-only Bayesian extension, retaining all former estimates.
- Consequences: Bayesian likelihood/priors/approximation, prediction, prior
  sensitivity and propagated uncertainty are explicit. A finite posterior estimate
  does not establish a physiological boundary. Joint spatial × MAIA exploration
  is labelled exploratory/modular rather than mediation. The results report
  states computational completion separately from scientific identification.
- Supersedes: Requirements to refresh manuscript prose/PDFs for each new analysis
  during this phase. Privacy, actual-browser, independent-check and Pages gates
  remain; prior scientific claims and audit records stay available.

## D-0013 — Joint Bayesian respiratory interaction goal

- Date: 2026-10-18
- Status: Goal accepted; joint model not yet specified numerically or run.
- Context: Following the unpooled Bayesian and conventional posterior-median
  analyses, the owner prioritises testing a PPS interaction involving Inhale
  versus Exhale in one Bayesian parameter-fitting analysis.
- Decision: Make the Condition × Phase difference of differences in boundary and
  normalized sharpness the next joint-model target. Retain the Phase main effect
  and both within-condition phase contrasts. Estimate curves and repeated-measures
  effects jointly with partial pooling; the roadmap owns the ordered work.
- Consequences: Fix likelihood/priors/diagnostics and sensitivities before fitting;
  label the extension post-results exploratory. Preserve the current cohort,
  preparation, published findings and manuscript pause. Completion requires a
  checked, reproducible answer including any inconclusive result. A desired
  significant interaction is not a method-selection or stopping criterion.
- Supersedes: The earlier completion summary's scope; it now excludes the newly
  opened joint-model tasks Q3.7–Q3.11. Existing results remain valid records of
  their stated analyses and do not become results of a joint hierarchy.
