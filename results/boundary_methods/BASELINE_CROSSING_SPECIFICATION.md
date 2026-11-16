# Linear crossings of tactile-only baseline limits

Fixed before fitting this batch on 2026-11-16. Serino et al. describe
an operational peri-trunk location in Fig. 7 by intersecting a linear
audio–tactile RT fit with the lower bound of a tactile-only confidence
interval. Some analyses in the same paper also select the fastest
unimodal tactile delay as their baseline. The preserved conference
abstract on full-body PPS supplies too little detail to establish the
same estimator or sample. The journal figure is the method source.
[Serino et al., Fig. 7](https://doi.org/10.1038/srep18603)

Fit a line with free intercept and slope to cleaned AT reaction-time
means at each tested distance. Use inverse-variance weights for an
individual cell and the covariance among participants for an
equal-person group fit. The three registered reference estimates are
the pooled tactile-only mean, its two-sided 95% lower confidence
limit, and the lower limit using the fastest unimodal tactile delay.
Check an equal-weight line as a sensitivity. The last
reference is a study-specific reporting rule. Retain selection and
sampling uncertainty in every bootstrap and note that a faster
reference can move a crossing through its effect on the RT criterion.
The lack of independent equating of each study's design makes these
adaptations of the published point estimate.

Estimate all four phase cells and equal-phase condition profiles.
Use both distance mappings and the primary40 cohort. Repeat the group
fit for both alternate exclusions. The same-label condition estimates
fit the line after nominal-label subtraction and compare with zero.
No same-label timing calibration is presumed. Treat all candidates
as exploratory. Keep a conditional point even outside the measured
range, but only call a location identified when the slope is supported
in the facilitating direction, the curve family is compatible, and
the complete crossing set is bounded inside the observed range.

Represent a crossing as a ratio of the estimated gap at the first
probe and the fitted distance slope. Use joint confidence geometry
for the intercept, slope and reference. Include empty, disconnected
and unbounded projections. For limits defined using a standard error,
condition the first projection on the observed reference margin and
propagate its variability in a separate full refit. For the
fastest-delay rule, preserve the possibilities for the selected
baseline within a joint region for the five means, and compare with
a bootstrap that repeats the selection. Never replace a set with a
percentile interval formed from finite ratios alone. Report any
opposite direction and possible absence of a within-range crossing.

Use the simulated independent-t envelope of the preceding profiles
for individual observations and the whole-participant Hotelling
ellipsoid for group means. Project the covariance to the gap and
slope. Equal-phase uncertainty carries both phase samples. For the
fastest-delay projection, include every delay whose marginal lower
bound can be below all other upper bounds in the joint region, then
take the union of its ratio sets. Report the true minimum on the
unseen mean vector separately from the observed selection. Use a
conservative extremal envelope of cell locations for each factorial
contrast at 98.75% per active phase cell. A direct difference of the
two equal-phase profile crossings is a separate estimand.

Use seed 20261120, 499 full refits and 96 independent whole-cohort
draws per working simulation scenario. Refit participant-level trials
within retained bins and group participants as whole repeated-measures
vectors. Re-estimate the line and the baseline reference on every
draw. Report finite, positive-slope and within-range fractions in
addition to descriptive crossing quantiles. The lower-limit target
in recovery uses the true baseline minus that draw's reported margin,
so variability of the margin is visible in the target itself.

Compare held-distance prediction against constant and log-distance
models on the same five folds. The reference changes the defined
crossing, while prediction tests the AT line. Compare with the
existing line under identical weights and the [monotone thresholds](THRESHOLD_RESULTS.md).
Use matched-noise group and individual recovery for flat and shallow
lines with no in-range crossing and a steep facilitating line with
known condition and phase shifts. Check ratio-set coverage, outside
and no-crossing rates, contrast recovery and the effect of varying
tactile-only noise on the operating reference. Verify the ratio
calculation against direct confidence-set inversion. The ratio sets
use the confidence ellipse geometry of [Fieller](https://doi.org/10.1111/j.2517-6161.1954.tb00159.x)
as described by [von Luxburg and Franz](https://www3.stat.sinica.edu.tw/statistica/j19n3/j19n312/j19n312.html).
