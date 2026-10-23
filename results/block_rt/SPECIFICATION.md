# Exploratory session-wide block RT analysis

Frozen before the new numerical analysis on 2026-10-23, following the owner's
question about average reaction-time drift across consecutive conditions.

- Outcome: raw Audio–Tactile hit RT in ms; reuse `paper_analysis.clean` exactly.
  No new cutoff, local filtering, normalization, smoothing or baseline subtraction.
- Chronology: `session_block = 6 * (part_number - 1) + block_number`, 1–12.
  Verify against original trial_index and recorded condition_order, rather than
  ordering by condition name. Blocks are progression indices, not elapsed minutes.
- Average retained trials (pooling SOA and phase) within participant × block,
  then give participants equal weight. Export counts, SDs and marginal 95% t CIs.
- Primary cohort: primary40 excluding P011/P033, whose recording linkage remains
  unresolved. A participant needs all 12 nonmissing block means for the primary
  repeated-measure analysis; list incomplete exclusions and retain observed means.
- Primary test: calculate each person's ordinary least-squares linear slope over
  the 12 blocks and test the population mean slope against zero using a two-sided
  one-sample t test. Negative means faster RTs later. Report ms/block, 95% t CI,
  t, df, p and signed dz. This retains the participant as the independent unit;
  do not regress just 12 grand means as though those blocks were independent.
- Fixed secondary checks: (1) quadratic coefficient from each person's
  RT ~ 1 + centered_block + centered_block² model; (2) linear block slope
  adjusted for the condition switch with RT ~ 1 + centered_block + condition.
  The latter estimates a common within-condition slope and does not identify
  carryover or an arbitrary nonlinear session trend separately from treatment.
- Descriptive paired block12-minus-block1 contrast and its 95% t CI, without an
  additional hypothesis test. Report all three tests; p values unadjusted under
  the owner's standing project policy, with exploratory pointwise uncertainty.
- Sensitivities: repeat with each linked record individually excluded (N≤41).
  Show full42 descriptives only, since it is not 42 independent recordings.
- Diagnostics: inspect participant slopes/endpoint differences using Q–Q plots,
  Shapiro screens and leave-one-participant-out mean ranges; fixed-seed 9,999
  whole-participant percentile-bootstrap CIs for the three mean coefficients.
  Diagnostics do not select another estimator or trigger exclusions.
- Figure: observed participant trajectories plus equal-person means and pointwise
  marginal 95% t CIs, zero-based ms axis, switch marked between blocks 6/7.
  Figure-only owner amendment (2026-10-23): one spaghetti panel with participant
  segments blue/solid for Control and red/dashed for Viscereality according to
  each recorded block's condition. Remove the condition-order summary panel;
  retain the overall mean and intervals. Numerical tests are unchanged.
- Preserve inputs and older analyses. Native execution only; no automatic change
  to the live paper or historical manuscript. Record runtime and SHA-256 hashes.
- Verify aggregation with independent pandas and slopes with statsmodels OLS,
  check known synthetic effects, inspect exported figures, run release/context
  gates, and update the existing roadmap with findings and publication state.

This is an exploratory test of overall RT drift, not drift-diffusion modelling,
a PPS-boundary analysis, or a causal diagnosis of practice or fatigue. Pooling
trials within blocks can reflect changing SOA/phase composition after exclusions;
the condition-adjusted check addresses a level shift, not all such confounding.
