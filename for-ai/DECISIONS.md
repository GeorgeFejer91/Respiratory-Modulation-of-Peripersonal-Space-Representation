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
- Status: Accepted
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
- Status: Accepted analysis direction; numerical-delta and moderation extensions
  have not yet been executed or promoted to the browser/paper.
- Context: The owner prioritises the within-person spatial-frame contrast over
  absolute condition ratings and asks how MAIA-2 dimensions can explain that
  contrast. The release has paired Control/Viscereality ratings and one MAIA-2
  record per person; questionnaire timing and pictogram anchors remain unverified.
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
- Consequences: The current browser report still has 33 prior associations and
  uses three-level change direction. Neither its Trusting coefficient nor its
  p value may be relabelled as a numerical-delta result. New numerical results
  require the existing native/browser, manuscript and publication gates.
- Supersedes: Equal emphasis on separate condition-level spatial correlations
  for future follow-ups; preserves prior results, the paired comparison, privacy
  rules, exploratory status and the participant PPS-boundary gate.
