# Partial identification of monotone threshold crossings

Fixed on 2026-11-16 before fitting this analysis. Use the cleaned
participant RT means on the five tested SOAs. Assume that increasing
distance cannot speed audio–tactile RT after the specified Baseline
subtraction. Treat this as a conditional shape model and check its
compatibility with the estimated probe responses. Use participant phase
cells, equal-phase condition profiles and equal-person group profiles.

Evaluate an observed-range half response and absolute facilitation
targets of 0, 20 and 40 ms. The half response lies midway between the
expected responses at the first and last **tested** locations. It exists
only for a positive endpoint span. Absolute targets apply to the signed
contrast Audio–Tactile minus Baseline, so the corresponding response
targets are 0, −20 and −40 ms. They serve as sensitivity values. The
20 and 40 ms values are neither clinical cutoffs nor values estimated
from Study 5. All four estimands allow a gradual monotone response.

## Compatible response bands

Construct simultaneous 95% rectangular bands for the five means in
each cell. At participant level, estimate a separate standard error
for each AT and Baseline mean. Build a union-bound band across the
primitive AT and Baseline means required by the target profile, then
propagate each primitive bound through Baseline subtraction and equal
phase averaging by interval arithmetic. Use two-sided Student t
critical values with the bin degrees of freedom and the number of
primitive intervals. For pooled Baseline subtract the same cell mean
and uncertainty across all distances. Compute the half response using
raw AT bands under pooled Baseline, because a shared additive offset
cancels from the half-crossing. For same-label subtraction, propagate
all five distinct Baseline means and report an unavailable participant
band when any included primitive has fewer than two measurements.
The union-bound calculation does not require independence across these
intervals. Its marginal t intervals still assume independent Normal
responses within a bin under the fixed retained-trial working model.

At group level, calculate each participant's corrected vector and
form the same simultaneous band using t marginals across whole
participants, with five components for each phase or equal-phase
summary. Use the primary40 cohort first and the two single-exclusion
cohorts as sensitivity analyses. Use 98.75% bands per phase cell to
project simultaneous four-cell contrasts. Preserve the shape check,
possible no-rise or censoring states and numerical results together.

## Threshold sets and prediction

Intersect each box with ordered probe means. Test whether flat is
compatible within that intersection. For each of the four between-probe
intervals, test if the lower probe is at or below the target and the
upper probe at or above it under the same ordered vector. This is a
linear feasibility problem. For the half response, maximize endpoint
span under these constraints and require a positive value. Return the
closure of the entire interval if feasible. Report disconnected unions.
An included endpoint of a closed interval can be a limiting value when
the corresponding probe cannot equal the target. For absolute targets check whether the
profile can start above or end below the target. These possibilities
correspond to left or right censoring within the measured range. A
compatible plateau at the target also prevents a unique distance.
Reject the monotone model for the cell if its band admits no monotone
sequence. Preserve empty sets and unresolved states rather than
imputing a point. A crossing set is localized if it is a proper subset
of the measured span and excludes no-rise, plateau and censoring
possibilities. A contrast projects the equal-weight phase locations
for its active cells. Report unsupported or partially bounded
contrasts if any contributing cell can have no within-range crossing.

Use the same five held-distance folds as the preceding batches. Fit
weighted increasing isotonic regression to four bins and compare
straight interpolation within the observed range, plateau
extrapolation at endpoints, and the flat, linear and log-distance GLS
references. Scores evaluate the predictor's additional interpolation
assumption. A compatible threshold set requires only continuity and
monotonicity between bins.

Use seed 20261119 in registered-axis simulations with 96 whole-cohort draws per
scenario. Include flat profiles at and away from the absolute target,
a gradual linear crossing, and two strong monotone transitions with
different participant profiles and known shifts. Align Baseline
uncertainty and noise with the retained data. Check simultaneous
coverage, incorrect localization under flat and censored truth, and
set width and contrast recovery for the crossing cases. Check the
linear constraints and band projection against analytic monotone
fixtures and an independent linear-programming implementation or
exhaustive vertex enumeration. Use both existing distance maps and
keep conditional points distinct from between-probe sets.

[Dümbgen on confidence bands for shape-restricted responses](https://arxiv.org/abs/1312.6466)
provides methodological context. The Study 5 protocol uses a finite
band projection for five measured means.
