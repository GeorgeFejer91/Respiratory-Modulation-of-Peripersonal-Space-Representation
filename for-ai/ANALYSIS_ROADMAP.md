# Results-first analysis roadmap

## Goal and status rules

Answer each level separately before selecting the paper narrative. Deliver
`results/RESULTS_REPORT.md` with evidence links and completion status for every
question. VERIFIED means a computation/check was observed; PARTIAL means some
evidence exists but the scientific identification claim remains open; BLOCKED
means the released data cannot supply a required source; NOT RUN means exactly
that. A completed analysis with an inconclusive result is not a failed task.

The initial roadmap and unpooled Bayesian specification were fixed after seeing
version-1.9 results, before calculating that extension. The later joint-model and
baseline-comparison goals followed inspection of its results and are now computed
with the limits recorded below.
These amendments are exploratory, not a new preregistration. Manuscript drafting
is paused. Use the installed Ponytail skill:
reuse preparation, scoring and contrast definitions; add only the portable model,
its report/export and proportional checks. Preserve the legacy reference.

## Active goal — usable Bayesian evidence for experimental PPS parameter effects

Recorded 2026-10-20 after the previous results: identify a scientifically usable
Bayesian statistic supporting an Inhale − Exhale effect, a Viscereality − Control
effect, or their interaction on PPS midpoint (cm) or normalized sharpness (/cm),
if supported by the observations. Retain all four participant cells and propagated
AT − Baseline uncertainty. This is an exploratory extension, not a preregistration
or a promise of a nonzero effect. Computational completion can yield an
inconclusive or unidentifiable parameter comparison.

- [x] Q10.1 Record the target: six primary contrasts (three effects × two
  parameters), plus the established simple contrasts. Preserve the primary40
  cohort, fixed cleaning, all earlier results and unadjusted frequentist outputs.
- [ ] Q10.2 Freeze a finite extension specification before new effect estimates:
  nuisance adjustments, reduced boundary-only/shared-sharpness and
  sharpness-only/shared-boundary models, proper priors, diagnostic gates,
  simulation counts and numerical extension/stopping budgets. Select restrictions
  by scientific rationale and predictive adequacy, never by favorable contrasts.
- [ ] Q10.3 Audit trial index, block, intervention order and baseline calibration
  for identifiable nuisance effects. Verify source-dependent timing before
  changing baseline matching; retain unresolved timing/linkage as explicit limits.
  Review checkpoint: `paper_analysis.clean` already applies participant-wide
  mean ±2.5 sample-SD trimming across distances, conditions, phases and AT/Baseline.
  Per-distance trimming would be a new exploratory sensitivity. Prioritise plots
  of every trial with existing exclusions marked, cell counts/distributions and
  time/block trends; fatigue or additional exclusions are not established by
  visual fit quality. Rolling averages are diagnostic unless the full inferential
  pipeline accounts for induced covariance, shape distortion and held-out testing.
- [ ] Q10.4 Fit the frozen joint hierarchical candidates with baseline and
  individual-fit uncertainty. Keep Gaussian/robust references and every failed
  fit. Do not use ANOVAs on pooled posterior medians as independent evidence.
- [ ] Q10.5 Export all six primary contrasts and simple contrasts: posterior
  estimate, 95% credible interval and directional probability, with physical units
  and population/cohort target. Assess practically meaningful effects only with
  justified thresholds; add Bayes factors only with explicit proper hypothesis
  priors and stable calculations. Posterior probabilities are not p values.
- [ ] Q10.6 Check null/known-effect recovery across repeated simulations, prior
  sensitivity, posterior prediction and matched held-out targets. A narrow
  interval or imposed visible S does not establish parameter identification;
  retain failed diagnostic gates and their consequences for interpretation.
- [ ] Q10.7 Compile the complete evidence table and classify each parameter
  effect as supported under the stated model, model-dependent, inconclusive or
  not identifiable. Distinguish RT-location/curve effects from boundary/sharpness
  effects. Stop after the declared scope and report all outcomes.

Status: **GOAL RECORDED; NEW FITS NOT RUN.** Current parameter results remain
inconclusive. Next action: freeze the finite nuisance/reduced-model and simulation
specification in the existing analysis-plan/registry owners. This amendment changes
the goal/checklist only; native results, browser publication and manuscript
snapshots are unchanged. The shared RTK/GSD/Superpowers skill baseline is unavailable
in this environment; use the existing roadmap and context checks as the bounded
fallback rather than installing dependencies or creating a second progress ledger.

## Completed computation — explicitly visible, shape-constrained Bayesian sigmoid

The owner explicitly authorizes an in-range midpoint/width restriction after
inspection of nearly linear broad fits. Fit the declared `visible95` prior (5/95%
component levels inside 10–100 cm) and `visible90` sensitivity, preserving positive
amplitude, raw observations, fixed cleaning and joint Baseline uncertainty.
The specified geometry is in `results/visible_sigmoid/specification.json`; this
is a post-results theory constraint, not evidence of observed S curvature.

- [x] Q9.1 Verify endpoint geometry, midpoint/derivative, exact marginalized
  likelihood, prior simulation and conditional export independently.
- [x] Q9.2 Run both full fits and retain every paired boundary/sharpness contrast,
  diagnostic status and prior-versus-posterior information check.
- [x] Q9.3 Run five primary held-distance refits and compare with the preserved
  broad-directional predictions on identical targets; no selection by significance.
- [x] Q9.4 Export a visibly sigmoid mean-parameter model figure, actual RT figures,
  all 40 participants' curves and boundary intervals. Inspect every page and verify
  hashes, labels, exact shape guarantees and original-data preservation.

Deliver `results/visible_sigmoid/RESULTS.md`; preserve earlier snapshots. Q1.7 is
not closed by prior-constrained intervals or visually guaranteed model curvature.
Both full fits converge with zero divergences; all 12 main boundary/sharpness
contrast intervals include zero. All 160 normalized curves satisfy the in-range
shape restriction, and every atlas page was visually inspected. Five independent
numerical checks and the full export/hash audit pass. Predictive validation is
**PARTIAL**: the 10 cm fold still fails convergence after its fixed extension;
the four converged folds have diagnostic RMSE 66.92 ms versus 45.86 ms for the
broad reference. The failed fold remains exported and whole-five-fold summaries
are provisional. The visible S is a computed model-imposed approximation, not
stronger evidence for physiological PPS boundaries. Width-cap/midpoint coupling
also limits interpretation of apparent individual precision.

## Completed reference — consistent asymptote direction across conditions

The owner rejects condition-specific reversals of the near/far RT asymptotes.
Refit with one theory-motivated orientation for all four curves: nonnegative
amplitude on increasing distance (lower RT near, higher RT far). This does not
fix the numerical heights of the plateaus or justify narrow widths. Keep the
earlier signed results as a reference; preserve raw reversed/flat observations.
The pre-fit extension is `results/directional_sigmoid/specification.json`.

- [x] Q8.1 Verify the marginalized positive-amplitude likelihood against an
  independent full-trial multivariate-normal calculation and conditional draws.
- [x] Q8.2 Fit all four cells jointly, check convergence and retain all midpoint,
  sharpness and response contrasts without selecting by significance.
- [x] Q8.3 Run all ten matched positive/unrestricted held-distance refits; report
  predictive tradeoffs, including uncertainty and failed diagnostic gates.
- [x] Q8.4 Export all 40 participants' consistently oriented curves and uncertainty,
  inspect every atlas page, and update the method recommendation with limitations.

Results: `results/directional_sigmoid/RESULTS.md`. Five numerical checks passed;
the full fit has no divergences and passes the stated convergence gate. All ten
predictive gates passed; held-distance RMSE is 46.90 ms with positive amplitudes
and 47.27 ms unrestricted, with an uncertain paired MSE difference. All six main
shape contrasts include zero. All 160 curves have the requested direction, but
156 midpoint medians are beyond the sampled range and no midpoint interval is
wholly inside it. The direction-constrained model is the requested exploratory
approximation, with the signed reference retained; Q1.7 remains open. Every atlas
page was visually inspected and full-draw summaries, contrasts and artifact hashes
were independently checked.

## Completed reference — publication-defensible individual sigmoid approximation

The owner authorizes pooling across participants and smoothing across SOA to
estimate four sigmoid curves per retained person, and requests a recommended
analysis and lead result. Use the converged native `joint_logistic_marginal` as an
explicitly exploratory approximation, with cell-noise sensitivity and the earlier
complete battery retained. This is a practical numerical choice, not demonstrated
best prediction or permission to select an effect-producing analysis.

- [x] Q7.1 Choose one common, converged estimator with baseline uncertainty and
  partial pooling across people; retain signed amplitudes and all four cells.
- [x] Q7.2 Package every retained person's parameters/intervals and measured-range
  responses alongside a clearly labelled full-sigmoid model illustration. Quantify
  how much of the transition is observed; do not equate a guaranteed S on a
  standardized axis with measured curvature.
- [x] Q7.3 Retain joint posterior Condition, Phase and interaction contrasts, plus
  simple contrasts and the noise sensitivity. Do not treat pooled medians as
  independent measurements for a new effect claim.
- [x] Q7.4 Recommend the most defensible lead finding with its model sensitivity,
  rather than the smallest nominal p value. State physiological identification
  and publication limits, verify the package and visually inspect every atlas page.

Output: `results/publication_sigmoid_choice/RECOMMENDATION.md`. No manuscript or
Pages integration is required. Q1.7 remains open even if every person has a finite
model curve. All 160 parameter records match the original full-draw summaries;
all 28 retained parameter contrasts include zero. All 40 atlas pages were visually
inspected, and the full-S row is a labelled standardized model illustration.

## Completed batch — baseline-corrected experimental effects across model families

Determine whether Inhale versus Exhale, Viscereality versus Control, or their
interaction changes the baseline-corrected PPS response. Test all three effects
for sigmoid boundary and normalized sharpness; also assess linear and logarithmic
distance models. The owner explicitly confirms subtraction of Baseline RT from
Audio–Tactile RT. Primary matching follows the existing participant × Condition ×
Phase baseline mean. Same-nominal-SOA correction is a separately labelled
sensitivity because equivalent cue timing cannot be verified from the release.
Carry uncertainty from both trial types into inference. Raw-RT models are a
reference, not the requested primary corrected analysis.

For each parameter θ, report Condition (Viscereality−Control, phase-averaged),
Phase (Inhale−Exhale, condition-averaged), and the interaction:

`Iθ = (θ_Viscereality,Inhale − θ_Viscereality,Exhale)
    − (θ_Control,Inhale − θ_Control,Exhale)`.

The overall Inhale−Exhale difference is a Phase main effect. Report it and the two
within-condition phase differences alongside the interaction; neither a significant
phase effect nor significance in only one condition establishes an interaction.

Start with a hierarchical nonlinear sigmoid model with participant-specific midpoint,
positive sharpness, baseline RT and signed response amplitude. Include Condition,
Phase and Condition × Phase in the shape parameters, with participant variation
in the repeated contrasts and explicit partial-pooling assumptions. Retain all four
cells and the fixed preparation/cohort rules. Fit individual parameters and group
effects jointly so their uncertainty remains connected.

The comparison also includes frequentist nonlinear estimation, mixed models for
linear/log-distance effects, paired contrast/resampling methods, and screened
literature sensitivities. Linear/logarithmic slopes are not sigmoid sharpness;
these families have no intrinsic plateau midpoint. Compare them on predictions
and explicitly shared observed-range response contrasts. The expanded specification
is in `workbook/ANALYSIS_PLAN.md`; the source-to-method rationale is in
`literature_review/ANALYSIS_RATIONALE.md`.

This is post-results exploratory work. **Goal and correction definition: RECORDED.
Baseline availability and focused literature audit: VERIFIED with access limits.
Expanded native registry, implementation, fits and tests: COMPUTED with diagnostic
and identification limits.** The owner has deferred Pages documentation and browser
integration for this batch. Its registry and results are in
`results/baseline_effects/`; executable source is in `analysis/baseline_effects/`.
Exhaust
the declared, scientifically distinct feasible approaches and record reasons for
omissions; do not promise an unlimited search or stop at the first significant
result. Existing results and diagnostic failures remain part of the evidence.

## Level 0 — Data and preprocessing

- [x] Q0.1 Audit released rows, missingness, source hashes and questionnaire scoring.
- [x] Q0.2 Record timing: baseline MAIA once; spatial ratings after each condition.
- [x] Q0.3 Define the four participant × Condition × Phase fitting cells uniformly.
- [x] Q0.4 Retain the fixed RT cleaning rule; never optimize it for shape or p values.
- [ ] Q0.5 Resolve P011/P033 recording linkage (BLOCKED by missing source mapping).
- [x] Q0.6 Primary new RT inference excludes both; retain three cohort sensitivities.
- [x] Q0.7 Audit baseline availability and define subtraction, matching and sign:
  4,192 retained Baseline RTs for the primary 40-record cohort, all 800 nominal-SOA
  cells populated, but only 1–6 observations per such cell; source cue timing is
  unverified. The primary correction pools baseline hits within person/condition/phase.
- [x] Q0.8 Implement and independently verify baseline correction and propagated
  uncertainty, including reused-baseline covariance, sparse cells, signed values,
  and translation invariance of a free-intercept curve. Preserve raw inputs/cleaning.

## Level 1 — Observed shape and reliability

- [x] Q1.1 Audit raw profiles and the original trial-level fit gate separately from
  model-only normalized geometry; keep flat and reversed responses.
- [x] Q1.2 Compare extraction/smoothing methods using held-out RT prediction,
  including constant, linear and broad/visible sigmoid alternatives.
- [x] Q1.3 Assess split-half reliability, condition-change reliability and known-signal
  recovery. Existing weak reliability is a result, not a reason to delete records.
- [x] Q1.4 Check whether Bayesian sigmoid prediction improves on simpler models.
- [x] Q1.5 Quantify whether posterior shape information exceeds the prior, whether
  both bends lie in the sampled range, and sensitivity to shape/nuisance priors.
- [x] Q1.6 Inspect every Bayesian raw/normalized participant plot and group plot.
- [ ] Q1.7 Establish reliable physiological boundaries for all people (PARTIAL;
  computable proxies do not satisfy this scientific identification requirement).

## Level 2 — Individual midpoint and sharpness

- [x] Q2.1 Define boundary `m` in cm and normalized sharpness `1/(4*w)` per cm;
  keep signed RT amplitude/derivative distinct from normalized sharpness.
- [x] Q2.2 Preserve the 168 existing four-cell proxies and their refit intervals.
- [x] Q2.3 Fit a genuine, explicitly specified Bayesian sigmoid posterior to each
  observed trial cell; report median, interval, amplitude, prior information and
  grid/boundary diagnostics. Do not smooth the likelihood or force nonzero amplitude.
- [x] Q2.4 Verify numerical integration against an independent calculation and a
  finer grid; check posterior predictive fit and prior-predictive plausibility.
- [x] Q2.5 Propagate draws for the uncertainty-aware analysis; retain the separately
  requested fixed-median conventional ANOVA as Q3.6.
- [x] Q2.6 State which estimates are data-informed and which remain prior-dependent;
  no claim that an assumption-free or universally best fit exists.

## Level 3 — Main experimental question

- [x] Q3.1 Preserve the prior 2×2 parameter ANOVA/ANCOVA with curve-refit uncertainty.
- [x] Q3.2 For both Bayesian parameters report Phase (Inhale−Exhale), Condition
  (Viscereality−Control), and Condition × Phase, using paired participant draws.
- [x] Q3.3 Distinguish the posterior cohort-average contrast from participant-population
  uncertainty; use paired Bayesian-bootstrap weights for the latter, clearly labelled.
- [x] Q3.4 Repeat across priors and the four linkage cohorts; no preferred result by p.
- [x] Q3.5 Decide whether observed effects are robust, inconclusive or model-dependent;
  computational estimates alone do not establish physiological changes.
- [x] Q3.6 Run the owner-requested conventional 2 × 2 RM ANOVAs on Bayesian
  posterior medians, with unadjusted p values and explicit omission of within-fit
  uncertainty; verify independently and retain all prior/cohort sensitivities.
- [x] Q3.7 Fix the joint model's likelihood, numerical proper priors, random-effects
  structure, sampler, diagnostics, cohort sensitivities and finite set of model
  checks in the native `analysis_registry.json` and per-model specifications before
  each batch, with post hoc diagnostic amendments labelled. Incorporate measured
  Baseline trials into the corrected estimand and propagate their uncertainty.
  Keep treatment priors centred on zero and justify scales from the design/measurement units; do not
  choose them from the desired interaction result. Browser feasibility is deferred.
- [x] Q3.8 Fit trial responses, all four participant curves and population effects
  in one hierarchical Bayesian analysis. Model positive sharpness on a log scale,
  retaining baseline/amplitude variation and flat/reversed responses. Export
  posterior draws; distinguish a log-sharpness coefficient (ratio of ratios)
  from the interaction in normalized sharpness on its original scale.
- [x] Q3.9 Check multiple-chain convergence, effective sample sizes, Monte Carlo
  error, prior/posterior prediction and known-signal/null recovery. Compare simpler
  response models and the fixed prior/likelihood sensitivities. Record computational
  or identification failures; numerical improvements must not be selected by
  whether they produce a positive interaction.
- [x] Q3.10 Report both parameters' paired interaction contrasts, overall Phase and
  Condition effects, and the phase difference within each condition. Give estimates,
  95% credible intervals and directional posterior probabilities; distinguish
  finite-cohort contrasts from population effects. Assess meaningful-size effects
  only after recording justified thresholds. Posterior probabilities are not p
  values. If Bayes factors are added, fix the null, alternative and proper priors
  explicitly and check the calculation's stability.
- [x] Q3.11 Independently verify the native joint implementation, inspect
  raw-data/curve/contrast plots, and retain its full
  results and sensitivities. Classify the interaction as supported under the stated
  model, model-dependent, inconclusive, or not estimable. Preserve all outcomes;
  no search-until-significant stopping rule or manuscript narrative is required.
- [x] Q3.12 Freeze a source-linked registry of baseline schemes, model families,
  estimands, inference methods and diagnostics before their new effect tests.
  Include constant, linear distance, log distance and sigmoid models; distinguish
  a literature replication, a generic sensitivity and an unsuitable/unidentifiable
  model. Add justified methods by dated amendments, preserving earlier results.
- [ ] Q3.13 Fit the frequentist nonlinear counterpart and linear/log-distance
  repeated-measures models. Test Condition, Phase and their interaction for shape
  parameters or distance coefficients, with participant dependence and uncertainty
  from both Baseline and AT. Include profile/parametric bootstrap, whole-person
  resampling and valid paired contrasts; report singular/nonidentified fits.
  **PARTIAL:** individual grid/continuous NLS, paired RM ANOVA, multivariate,
  permutation/rank/sign and refit checks are computed. A separate nonlinear
  mixed-effects fit and profile-likelihood confidence sets were not run;
  R/nlme is unavailable in the current environment. Refit stability intervals
  are not claimed to have calibrated confidence coverage.
- [x] Q3.14 Fit corresponding Bayesian linear/log-distance models and declared
  robust/prior sensitivities. Separate log distance from log RT; corrected RT can
  be negative. Report posterior contrasts and explicitly specified Bayes factors
  only where proper priors and stable computation support them.
- [x] Q3.15 Evaluate screened sigmoid/plateau/smoothing alternatives fairly,
  including the published fixed-observed-extrema logistic as a labelled sensitivity.
  Repeat tuning/baseline estimation within applicable validation/refit loops; inspect
  raw and corrected curves, recover known/null effects and retain all failures.
- [x] Q3.16 Compile every model/effect, unadjusted p or posterior summary, effect
  size/interval, cohort, correction and diagnostic status into one results inventory.
  Identify nominal findings, robust patterns, specification-sensitive findings and
  inconclusive effects separately. A general RT benefit or a significant simple
  effect alone is not a PPS boundary change or Condition × Phase interaction.

## Level 4 — Descriptive average curves and figures

- [x] Q4.1 Preserve observed equal-person cell means and earlier group fits.
- [x] Q4.2 Plot four Bayesian average response functions with raw data and uncertainty.
  An average of sigmoids need not itself be a sigmoid; do not force it into one.
- [x] Q4.3 Display midpoint and sharpness intervals with consistent units/axes and
  separate model geometry from the actual RT response; visually inspect figures.
- [x] Q4.4 Inspect all four corrected response curves and corresponding Baseline/AT
  summaries, model comparisons and experimental contrasts with uncertainty. Show
  extrapolation and imposed geometry; do not change axes to imply observed bends.

## Level 5 — Spatial frame, MAIA-2 and joint exploration

- [x] Q5.1 Preserve all eight MAIA subscales, paired spatial comparison, numerical
  delta, ordinal sensitivities and prior moderation/cell-association analyses.
- [x] Q5.2 Propagate Bayesian parameter uncertainty into four cell associations with
  baseline MAIA and same-condition spatial ratings and into parameter changes
  versus spatial delta and MAIA. Participants remain independent units.
- [x] Q5.3 Fit separate subscale models for spatial delta, MAIA and their product,
  with order adjustment, on the four orthogonal PPS summaries. The product in the
  Condition/Phase/interaction summary is the corresponding three-/four-factor
  exploratory moderation, not mediation. Keep all eight scales and both outcomes.
- [x] Q5.4 Label these modular posterior/participant-bootstrap descriptive regressions
  accurately; they are not a jointly estimated hierarchical latent-covariate model.
  Report raw uncertainty and full counts, never select scales or cleaning by results.
- [x] Q5.5 Explain whether any association survives parameter and prior uncertainty;
  do not call absent evidence proof of no biological relationship.

## Level 6 — Reproducibility and final evidence report

- [x] Q6.1 Keep the existing verified browser analysis and manuscript snapshot intact.
- [x] Q6.2 Unit/independent checks, real-browser execution, actual download and
  native/browser parity for the new results-only branch.
- [x] Q6.3 Archive data/code/artifact hashes and readable numerical tables/figures.
- [x] Q6.4 Complete `results/RESULTS_REPORT.md` with each level's findings, status,
  remaining limitations and links, without drafting manuscript prose.
- [x] Q6.5 Push the validated changes and verify the live results companion.
- [ ] Q6.6 Verify and publish the expanded corrected-model results in the browser,
  update the results-only report and link every conclusion to the full registry.
  **DEFERRED by the owner's results-only request.** Older checked browser items
  refer to their published analyses, not the new native extension.
- [x] Q6.7 Independently check and package the native corrected-model results,
  figures, model diagnostics and full inventory in
  `results/baseline_effects/RESULTS.md`, preserving the older published snapshots.

## Interpretation contract

The Bayesian extension is a quadrature approximation with a declared likelihood
and proper priors, not assumption-free inference. It deliberately provides an
unpooled posterior reference: partial pooling can stabilize estimates but can also
supply apparent similarity in weak data. A full joint hierarchical nonlinear model
is not implied by this reference and must be labelled NOT RUN unless executed
and diagnosed. Finite Bayesian medians and attractive curves do not by themselves
close Q1.7. No baseline MAIA mediator or questionnaire-driven data cleaning.

Completion means all feasible checklist computations and a candid evidence report.
It does not require a significant experimental difference, a positive correlation,
or treating every participant as having an empirically identified sigmoid.

## Current evidence checkpoint

The completed unpooled model/contrast/association computations and fixed-median
ANOVAs have run in native Python and Pyodide with independent checks and matching
numerical results. The individual and average figures have been visually inspected.
Computational completion does not close Q1.7: the individual parameters remain
poorly identified and unreliable, and experimental/questionnaire associations
are inconclusive after propagating uncertainty. Q0.5 still requires source mapping.
The requested conventional tests on fixed Bayesian posterior medians are also
computed and independently checked; none of their primary or sensitivity tests
establishes a condition, phase or interaction difference at unadjusted .05.
The native baseline-corrected extension has now run: five individual sigmoid
families, continuous/refit checks, linear/log-distance and categorical tests,
twelve joint Bayesian specifications, twenty held-distance refits, recovery and
prior/likelihood/nuisance-pooling sensitivities. Some nonlinear sampler diagnostics
still fail after the finite extension budget; these are inconclusive model results,
not null-effect evidence. The independently marginalized nuisance models converge
and retain very wide parameter intervals. Fourteen independent numerical checks
pass, and all 40 native atlas pages and average/baseline figures were inspected.
The published result archive/report/evidence and preserved legacy ZIP/PDF match
the checked local bytes. Public application input checks and editor execution
passed for that earlier snapshot. Source mapping (Q0.5), reliable physiological
identification (Q1.7), the unrun parts of Q3.13 and deferred browser integration
(Q6.6) remain open. The native report separates exploratory RT-level interactions
from unsupported PPS boundary/sharpness claims, and demonstrates why ANOVAs on
hierarchically pooled posterior medians can give false positives in a null
simulation. Earlier raw-RT browser results remain separate.
