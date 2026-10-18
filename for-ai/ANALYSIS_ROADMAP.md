# Results-first analysis roadmap

## Goal and status rules

Answer each level separately before selecting the paper narrative. Deliver
`results/RESULTS_REPORT.md` with evidence links and completion status for every
question. VERIFIED means a computation/check was observed; PARTIAL means some
evidence exists but the scientific identification claim remains open; BLOCKED
means the released data cannot supply a required source; NOT RUN means exactly
that. A completed analysis with an inconclusive result is not a failed task.

This roadmap and the Bayesian specification were fixed after seeing version-1.9
results, before calculating the new extension. They are exploratory, not a new
preregistration. Manuscript drafting is paused. Use the installed Ponytail skill:
reuse preparation, scoring and contrast definitions; add only the portable model,
its report/export and proportional checks. Preserve the legacy reference.

## Active next goal — joint Bayesian interaction test

Determine whether respiratory phase changes PPS boundary or normalized sharpness
differently under Viscereality and Control, using one joint model of the retained
trial responses. The target for either parameter θ is:

`Iθ = (θ_Viscereality,Inhale − θ_Viscereality,Exhale)
    − (θ_Control,Inhale − θ_Control,Exhale)`.

The overall Inhale−Exhale difference is a Phase main effect. Report it and the two
within-condition phase differences alongside the interaction; neither a significant
phase effect nor significance in only one condition establishes an interaction.

Use a hierarchical nonlinear sigmoid model with participant-specific midpoint,
positive sharpness, baseline RT and signed response amplitude. Include Condition,
Phase and Condition × Phase in the shape parameters, with participant variation
in the repeated contrasts and explicit partial-pooling assumptions. Retain all four
cells and the fixed preparation/cohort rules. Fit individual parameters and group
effects jointly so their uncertainty remains connected.

This is a new post-results exploratory analysis. **Goal/specification direction:
RECORDED. Numerical protocol, implementation, fitting and new results: NOT RUN.**
The next executable action is Q3.7 below. The aim is a defensible test capable of
detecting an interaction when supported; completion does not require a positive
finding. Existing results and diagnostic failures remain part of the evidence.

## Level 0 — Data and preprocessing

- [x] Q0.1 Audit released rows, missingness, source hashes and questionnaire scoring.
- [x] Q0.2 Record timing: baseline MAIA once; spatial ratings after each condition.
- [x] Q0.3 Define the four participant × Condition × Phase fitting cells uniformly.
- [x] Q0.4 Retain the fixed RT cleaning rule; never optimize it for shape or p values.
- [ ] Q0.5 Resolve P011/P033 recording linkage (BLOCKED by missing source mapping).
- [x] Q0.6 Primary new RT inference excludes both; retain three cohort sensitivities.

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
- [ ] Q3.7 Fix the joint model's likelihood, numerical proper priors, random-effects
  structure, sampler, diagnostics, cohort sensitivities and finite set of model
  checks in `workbook/ANALYSIS_PLAN.md` before its first fit. Keep treatment priors
  centred on zero and justify scales from the design/measurement units; do not
  choose them from the desired interaction result. Verify browser feasibility.
- [ ] Q3.8 Fit trial responses, all four participant curves and population effects
  in one hierarchical Bayesian analysis. Model positive sharpness on a log scale,
  retaining baseline/amplitude variation and flat/reversed responses. Export
  posterior draws; distinguish a log-sharpness coefficient (ratio of ratios)
  from the interaction in normalized sharpness on its original scale.
- [ ] Q3.9 Check multiple-chain convergence, effective sample sizes, Monte Carlo
  error, prior/posterior prediction and known-signal/null recovery. Compare simpler
  response models and the fixed prior/likelihood sensitivities. Record computational
  or identification failures; numerical improvements must not be selected by
  whether they produce a positive interaction.
- [ ] Q3.10 Report both parameters' paired interaction contrasts, overall Phase and
  Condition effects, and the phase difference within each condition. Give estimates,
  95% credible intervals and directional posterior probabilities; distinguish
  finite-cohort contrasts from population effects. Assess meaningful-size effects
  only after recording justified thresholds. Posterior probabilities are not p
  values. If Bayes factors are added, fix the null, alternative and proper priors
  explicitly and check the calculation's stability.
- [ ] Q3.11 Independently verify the joint implementation and actual browser
  execution/download, inspect raw-data/curve/contrast plots, and publish its full
  results and sensitivities. Classify the interaction as supported under the stated
  model, model-dependent, inconclusive, or not estimable. Preserve all outcomes;
  no search-until-significant stopping rule or manuscript narrative is required.

## Level 4 — Descriptive average curves and figures

- [x] Q4.1 Preserve observed equal-person cell means and earlier group fits.
- [x] Q4.2 Plot four Bayesian average response functions with raw data and uncertainty.
  An average of sigmoids need not itself be a sigmoid; do not force it into one.
- [x] Q4.3 Display midpoint and sharpness intervals with consistent units/axes and
  separate model geometry from the actual RT response; visually inspect figures.

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
A full joint hierarchical nonlinear model remains NOT RUN and is now the active
next analysis (Q3.7–Q3.11). The existing results report, browser controls and public
Pages deployment are verified.
The published result archive/report/evidence and preserved legacy ZIP/PDF match
the checked local bytes. Public application input checks and editor execution
passed. Source mapping (Q0.5), reliable physiological identification (Q1.7), and
the newly requested joint interaction analysis (Q3.7–Q3.11) remain open.
