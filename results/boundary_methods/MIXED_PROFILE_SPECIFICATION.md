# Marginal likelihood for paired midpoint shifts

This exploratory analysis checks whether a common condition shift in
participant midpoints is recoverable when population shape parameters
are selected by maximum marginal likelihood. It follows the nonlinear
mixed-effects principle of separating a population shift from
between-person shape variation. The shape fit uses a finite lattice.
[Lindstrom and Bates (1990)](https://pubmed.ncbi.nlm.nih.gov/2242409/)

Use primary40 and the fixed cleaned Audio–Tactile hit RT mask. Fit
Gaussian log seconds. The participant-cell intercept, response
amplitude and residual variance have the same conjugate distributions
as in the joint recorded-response model. Their integration retains
the uncertainty associated with the RT level in each cell. The
population shape search has no prior weight on its candidates.
[Conditional latency likelihood](JOINT_RECORDED_SPECIFICATION.md)

## Paired shape

In either scheduled phase, a participant's Control midpoint is `u`
and their Viscereality midpoint is `u + delta`. Both conditions use
a shared phase width, with separate signed response amplitudes.
Integrate `u` over a normal-shaped discrete distribution with location
`mu` and scale `sigma`. The mean shift `delta` is common across
participants within that phase. Fit the two phase surfaces separately.
Project the phase surfaces into the group condition, phase and
interaction effects and four simple contrasts. The condition effect is
the equal-phase mean of the two `delta` values. Participant estimates
condition on the fitted population parameters.

Scale the measured distances to 0–1. The primary lattice uses:

- Latent `u` from −1.5 to 2.5, and `mu` from −0.6 to 1.6.
- Shift `delta` from −1 to 1. All three use 0.05 increments.
- `sigma` in 0, 0.08, 0.15, 0.25 and 0.4. Zero sets `u = mu`.
- Widths in 0.06, 0.09, 0.135, 0.20, 0.30, 0.45 and 0.675.

Use both distance maps. For the observed wide-lattice diagnostic, use
`u` from −1.8 to 2.8, `mu` from −0.9 to 1.9, `delta` from −1.3
to 1.3 and add a scale of 0.60. Report if a point or support set reaches
the search limits. The recorded distance–SOA relationship remains
unchanged by this parameterization.

## Calibration, prediction and effects

At every lattice candidate integrate the paired per-person likelihood
over `u`. Compare the unrestricted shift, zero shift, and boundary-free
constant, linear and log-distance bases. The last three each have
per-person levels and, when applicable, amplitudes under the same
likelihood. Hold out one complete distance at a time. Select shape on
the four training distances and compute the full minus training
log likelihood at that same shape. This integrates participant-level
uncertainty at the fitted population parameters. Divide by the held
trial count. Apply the same five folds to both shape models and all
references.

Use distinct calibration and evaluation seeds for 32 cohorts per
generator, under flat, affine, weak sigmoid and strong sigmoid
generators. Keep the observed counts. In the nonflat sigmoid
generators, phase location values are 0.45 and 0.50, midpoint scale
is 0.15, and phase shifts are 0.10 and 0.20. The width is 0.135.
The amplitudes on the log scale are 0.08 and 0.25. The affine generator
has an endpoint span of 0.08. Record shared-structure recovery with
a participant-level baseline shift correlated across phases and
a phase-specific latent midpoint generated from the matching lattice
distribution.

Calibrate improvement over the best boundary-free reference using
the 95th percentile of the maximum across the two phase improvements
in the flat and affine simulations, taking the higher of the two
cutoffs and zero. Separately calibrate the support set for shape
parameters using the maximum across phases of twice the loss of
log likelihood at the true lattice tuple. Take the higher 95th
percentile across weak and strong simulations. Use each cutoff on the
independent evaluation seeds and report the observed false selections,
effect coverage and point RMSE. Project both phase support sets into
the paired effects. These are finite-lattice compatibility intervals
calibrated under working generators. Report conditional point and
interval summaries when the boundary-free comparison remains compatible.

After inspecting the first wide-lattice fits, repeat the same independent
calibration and evaluation scheme on the wide lattice. Its observed
exhale fit was near the primary selection cutoff, motivating this
post-analysis check of how the larger search changes the cutoff.
The wide-lattice intervals use its own calibration. Retain the original
primary calibration and outputs.
