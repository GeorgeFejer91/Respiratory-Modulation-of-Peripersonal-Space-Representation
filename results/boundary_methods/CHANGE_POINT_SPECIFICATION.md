# Discrete boundary confidence-set screen

Fixed 2026-11-16 after the first screen and before these fits. This is an
exploratory Study 5 analysis motivated by discrete-delay onset rules in
[Hobeika et al. (2018)](https://doi.org/10.1007/s00221-017-5158-2) and
[Teraoka et al. (2024)](https://doi.org/10.1007/s00221-024-06782-2).
It uses the retained primary40 hit data and all four paired cells. Report
each phase and each condition's equal-phase mean profile. Use both axes.

The location of a two-plateau step is one of four open intervals between
adjacent sampled distances. No position within a gap has a distinct
likelihood. Admit a signed jump, so a detected but reversed transition is
visible. Compare three boundary-free families: flat, line, log distance.
Construct four contrasts relative to the nearest bin so a common intercept,
including one estimated shared baseline mean, cancels. For each candidate,
fit the amplitude by generalized least squares on these contrasts. For
individual cells use plug-in within-bin variance of retained AT means. Take
the variance of the two phase means' average as their summed estimated
variances divided by four in equal-phase participant profiles. For group
profiles calculate the covariance from whole-person contrast vectors.

Report candidate model compatibility by the approximate 95% residual
chi-square region with 4 degrees of freedom for flat and 3 for the six
one-amplitude candidates. This uses plug-in variance/covariance under a
working Gaussian approximation rather than a chi-square test for an
estimated change point. A unique compatible gap with every boundary-free
family incompatible is the provisional identification rule. A meaningful
positive jump is a further constraint. Distinguish zero compatible
candidates (misspecification or a false rejection) from multiple compatible
candidates (ambiguity). Do not apply an automatic point-valued gap midpoint
or invent a CI if the family is uncertain.

Check this rule under 256 replicates each of flat, 80-ms and 160-ms
near-to-far jumps across the second/third positions, and a no-step 80-ms
linear trend. Simulate the retained counts and estimated sampling SDs of
the AT means, and condition on those SDs. Report rejection of the generating
family and unique-step calls under each scenario. Check all five held
distances with a training-only least-squares step fit. Average tied step
predictions and extrapolate the available plateau if the other was absent
from training. Score the same unsmoothed arithmetic AT means for steps,
constant, line and log distance. These are within-person predictions
conditional on fixed cleaning. The specification screens boundary
existence and resolution, without assuming the five positions can separate
distance effects from elapsed time.
