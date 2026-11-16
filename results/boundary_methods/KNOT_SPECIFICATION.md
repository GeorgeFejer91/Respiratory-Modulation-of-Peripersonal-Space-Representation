# Continuous changes in slope

Fixed before fitting on 2026-11-16. The exploratory target is the distance
where the expected cleaned audio–tactile reaction-time profile changes slope.
A near-plateau hinge estimates the onset of distance dependence as distance
increases. A far-plateau hinge estimates where that dependence levels off.
A broken line gives the knot when both sides can have nonzero slopes. These
targets can differ from a discrete step or sigmoid midpoint.

Use the trial preparation and four phase-specific and two equal-phase
summaries from the midpoint profile batch. Fit each participant cell
and the equal-participant profile. Compare registered and trajectory
distances. Repeat with the timing-unverified same-label subtraction and
the two primary cohort linkage sensitivities for the group.

Normalize distance to the measured range. The candidate knot grid spans
−0.25 to 1.25 in 0.01 increments, plus the exact tested distances. Use
`max(x-knot,0)` for a near plateau, `max(knot-x,0)` for a far plateau,
and a line plus `max(x-knot,0)` for a broken line. Fit intercept and
signed coefficients by GLS. Search the complete grid for compatibility.
For descriptive points and held-probe fits, require probes strictly on
both sides, two per side for the free-slope broken line. Prefer a knot
near the center in numerical ties. Retain zero slope change.

Use the absolute profile radius from the midpoint analysis. At a true
Gaussian contrast vector any admissible curve attaining that vector
inherits the same coverage argument. Report disconnected sets, and
check whether any candidate falls at or beyond the first or last probe.
The null references are flat, linear and log-distance at the same
radius. A knot localizes only when the nonempty profile excludes all
these references and the compatible grid stays in the range that has
enough probes on each side for the family. Form conservative four-cell
contrasts using the marginal radii at 98.75% and extremal knots for
each active cell. Report separate phase and equal-phase profiles, point
contrasts, conditional bounds, and the identification decision.

Compare five held-distance folds using a slope-change bound of ±320 ms
per measured range. Preview sensitivity at ±160 and ±640 ms for all
families. This cap limits the departure of the two slopes where a
training grid nearly lacks leverage. For the compatibility calculation
and recovery, use ±640 ms for break coefficients. Keep the same
uncapped boundary-free competitors throughout.

Use seed 20261118 and run 96 matched whole-cohort replicates for a flat profile, a line with a
160 ms span, two plateau hinges and a broken line with opposite sides
having unequal slopes. Anchor nonzero slope changes at 320 ms per
normalized range for the plateau cases and 480 for the broken line.
Use registered knots nearest to normalized positions .40, .44, .52,
and .56, fixed independently of the observed fit. Report true-knot
coverage, correct localization, false localization under boundary-free
generators, conditional location and paired contrast RMSE. Preserve
independent within-bin sample variance uncertainty and whole-person
group covariance, matching the midpoint working-model calibration.

The finite grid limits distance resolution. A candidate only identifies
a slope change under its model. Fit and verify the profiles with
rank-deficient designs at edges, direct constrained GLS comparisons, and
known noiseless hinges and broken lines. The eventual monotone
threshold sets address a different estimand and follow this batch.

[Fong et al. threshold families](https://doi.org/10.1186/s12859-017-1863-x) and
the [Study 5 profile specification](PROFILE_SPECIFICATION.md) describe the
model forms and the reused uncertainty calibration.
