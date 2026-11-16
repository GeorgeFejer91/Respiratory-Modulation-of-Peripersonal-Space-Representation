# Midpoint profile and shared-shape reductions

Fixed before the new fits on 2026-11-16. This is exploratory and uses the
existing Study 5 cleaning, the five SOAs, primary40 and the signed AT
distance profile. Estimate all four phase-specific cells and the two
equal-phase condition profiles. The location of the equal-person profile
differs from the mean of participant-level locations.

## Location sets

At each midpoint and width, fit a free level and signed amplitude by GLS.
Limit the fitted response change across the five design locations to
±1,000 ms, a broad bound fixed before prediction. This avoids unstable
held-endpoint extrapolation when a fitted basis is nearly constant on
the four training bins. Calibration assumes the generating curves lie
inside the bound. Break numerical ties toward the middle of the measured
range and width one sixth of that range.
Use the registered and trajectory axes. The primary midpoint grid spans
normalized coordinates −0.5 through 1.5 in 0.025 steps. The expanded grid
spans −1 through 2 in the same steps. Logistic width covers 0.025–2 times
the measured range on a 41-point log grid, with 1/6 added exactly.
Use the profile loss at each midpoint minimized over width. Retain the
absolute compatibility sets, disconnected components, search-edge hits,
and positions outside the measured probe span. These are sets on a finite
grid, with endpoints quantized to the grid. A lowest-loss location is
reported separately as a model-conditional point estimate.

For individual phase cells, use sample variances of retained distance means.
The absolute cutoff is calibrated with the 95th percentile of an upper
envelope, the sum of five squared t statistics with the bin-specific
degrees of freedom. Under independent Normal responses across and within bins, the
weighted GLS residual at a true shape is at most the sum evaluated at
the true level and amplitude, which has this envelope distribution.
Estimate the quantile using 16,384 fixed draws for each distinct vector of
degrees of freedom. For equal-phase participant profiles, use the
corresponding 10-statistic envelope from both phases. The same inequality
holds when averaging noisy means with inverse-variance weights in residual
space. For group profiles use the exact Hotelling radius under iid
multivariate Normal participant contrast vectors, with the covariance
computed among whole participants. It has dimension four after removal
of the common level. For simultaneous four-cell sets, use the same
envelopes at 98.75% per cell. These are working-model calibrations:
fixed trimming conditions on selection, and residual serial dependence
and non-normal participant contrasts could affect coverage.

Compare flat, linear and log-distance adequacy at the same cutoffs.
The finite grid admits zero amplitude. Test existence of an identified
transition separately from the best relative fit. A nominal midpoint is
considered localized only when its set is nonempty, wholly inside the
measured range, and all three boundary-free references are incompatible.
This rule is evaluated across both axes; it is neither a physiological
claim nor a multiplicity-adjusted list of individual discoveries.

## Reduced models

Compare free midpoint/width with shared-width, shared-midpoint and
shared-both reductions within each four-cell participant profile and
for the four equal-person group cells. Levels and signed amplitudes
remain cell-specific. Minimize the sum of cell GLS losses, a working
block objective for the group. For joint compatibility use the
simultaneous per-cell cutoffs and shared-parameter intersection. Compute
identification-aware contrast ranges from the joint sets. Preserve the
group profile contrasts and the mean of paired conditional participant
estimates separately. Mark tests with a boundary-free alternative
enabled, outside-range geometry, or an empty set. A zero midpoint
contrast imposed by sharing is a model restriction.

Compare the four reductions with a flat, a line and a log-distance
model over five held-distance folds, training on the other four. Use
the same unsmoothed positive RT target and covariance estimated from
training bins. Report scores for individual profiles and equal-person
group profiles. Held-out observations can still affect earlier fixed
cleaning. This evaluates within-design response prediction.

After the first execution showed large errors for several held-endpoint
predictions, add a post hoc predictive sensitivity at ±80, ±160 and
±320 ms. The limits correspond to the simulation amplitudes and twice
the larger one. Refit and score every candidate at every limit on both
axes under the primary correction. These comparisons do not recalibrate
the compatibility sets or promote a model.

## Recovery and verification

Use the seed 20261117 and 96 independent whole-cohort replicates per
scenario. Simulate matched counts and bin variances, including
independent sample variance uncertainty in the coverage check. The
matched-SD working simulation uses a flat curve, an 80-ms nonzero
curve with null midpoint differences, a 160-ms curve with condition
and phase midpoint differences, and an 80-ms curve with those midpoint
differences and variable widths. Report single-cell and simultaneous
coverage at the generating grid shape, boundary-free decisions,
paired midpoint effect bias and RMSE for every reduction. Fix the
generating locations and widths from the grid independently of the
observed optimum. A separate matched-covariance simulation checks
group profile recovery. Verify the GLS surface against direct least
squares on small fixtures, plus offset invariance, known-shape recovery,
nesting of reductions, and compatibility-set calculations.

Use both previously prepared Baseline and Audio–Tactile data. Pooled
same-cell Baseline subtraction leaves every contrast unchanged by
construction. Its uncertainty is common to all bins, so it cancels
after removal of the level. Repeat group and participant fits with
same-label Baseline subtraction as a timing-unverified sensitivity,
propagating both bin variances. Use a Welch degrees-of-freedom
approximation for the within-person envelopes in this sensitivity.
Keep group means with a recorded Baseline observation at every bin.
If its within-bin variance cannot be estimated, flag the affected
individual profile and omit it from the complete four-cell fit.
Preserve current primary40 as the main cohort. Compare both single
exclusion cohorts for the group profile. The full42 dataset, which
contains the unresolved reused recording, receives no iid-group
confidence claim. Source timing and cohort order remain separate
audit questions.
