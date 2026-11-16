# Horizontal shifts of a common monotone RT profile

Estimate a relative shift without imposing a logistic shape or an
absolute midpoint. Compare two signed RT curves at the five observed
positions, using an arbitrary nondecreasing function `f`. For the first
curve the mean at distance `x` is `f(x)`. For the second it is
`c + f(x - delta)`. Positive delta shifts the second curve outward.
The main analysis leaves the RT level difference `c` free. A restricted
sensitivity sets `c=0`. Both curves share scale and shape. This is a
two-curve restriction within the shape-invariant regression family.
[Lawton et al. (1972)](https://doi.org/10.1080/00401706.1972.10488942)

Use the established trial cleaning, the primary40 and two linkage
cohorts, both distance axes, and pooled or nominal same-label Baseline.
Pooled subtraction changes the fitted vertical offset and leaves
within-cell contrasts unchanged. The unverified timing match makes
same-label results a sensitivity. Evaluate the two phase-specific
condition comparisons, the equal-phase condition comparison, and the
phase comparison within each condition. Report individual and equal-
participant group curve comparisons separately. Use the paired set
difference between phase-specific condition shifts for the interaction.

## Exact shift compatibility

The ordering of the ten shifted input locations changes only at
differences between observed locations. Evaluate every point of
coincidence, each open interval between them, and the two unbounded
intervals. Retain disconnected pieces and open ends. Coincident
positions must have the same value of `f`. The calculations merge
coordinate differences within 10⁻⁷ cm to represent the exact fractional
trajectory positions in floating point.

For a given shift, let `a_i` be 0 for the first curve and 1 for the second.
Use simultaneous mean bands `[L_i,U_i]` for the observed probes. The
order constraints are feasible exactly when there is an offset `c`
with `L_i - a_i c <= U_j - a_j c` for all ordered pairs `(i,j)`,
including both directions at ties. The least feasible nondecreasing
sequence is the running maximum of shifted lower bounds. These
inequalities supply lower and upper bounds for `c`. Test whether
both curves can be constant separately. Empty sets indicate the common
shape fails the observed-band comparison. A boundary shift requires
a nonempty bounded shift set, a transition rather than two constants,
and compatibility with the timing and linkage sensitivities.

Use the existing primitive mean bands within participants and
participant-mean bands at group level. Divide the error budget across
all six profiles for simultaneous comparisons and the interaction.
Use cohort-specific trial counts and propagate Baseline uncertainty.
Bands rely on the stated within-bin or between-participant working
assumptions. They represent a conservative rectangular projection.
Preserve all exact ties and unbounded intervals. Also report support
within the offset design span, interpreted as a restricted overlap
sensitivity. With a free vertical offset and disjoint sampled
domains, any two compatible monotone sequences can be joined by a
monotone curve. Thus overlap support alone does not identify an
unrestricted shift. This comparison also supplies no absolute
boundary location.

## Calibration and held-probe checks

Verify the rectangular projection against linear programming on
small random and planted cases, including coincidence, zero shift,
two constant curves, incompatible slopes, and unbounded translation.
Use 96 matched whole-participant recovery replicates for a flat
population profile, a 20 cm shift of an 80 ms transition, and a 40 cm
shift of a 160 ms transition on the registered map. Add a 25 ms vertical
offset to the second curve. Plant a logistic only to generate known
relative shifts, carrying through both the unrestricted vertical
offset and the zero-offset sensitivity. Preserve observed participant
covariance by resampling centered vectors. Record coverage of the
plant, rejection of zero shifts and evidence that depends on assumed
overlap. Use seed 20261202.

For primary40 mean-curve prediction, refit on four common probes.
Compare independent constants, separate isotonic fits, a common
monotone shape with zero horizontal shift and free vertical offset,
and the fitted common monotone shape with both shifts free. Use equal
probe weights so level and shape choices are visible in the loss.
Choose the smallest absolute horizontal representative on a tie,
restrict training candidates to full design span, and use linear
interpolation with edge clamping to score held mean RT. This supplies
an explicit prediction convention for the set-valued fit. It leaves
the exact support calculation unchanged. Do not interpret between-
probe ranks or better held prediction as evidence of an absolute PPS
boundary.
