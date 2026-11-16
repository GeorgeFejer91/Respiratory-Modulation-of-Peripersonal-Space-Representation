# Midpoint compatibility and shared-shape results

The [profile specification](PROFILE_SPECIFICATION.md) tests the locations
that remain compatible with the data after fitting a separate level and
amplitude. It also compares four reductions of the logistic shape. The
result is that a common shape assumption can improve prediction or recover
a simulated effect, while the observed Study 5 data still leave the
participant and condition midpoints unresolved.

## Midpoint sets

With pooled participant-by-condition-by-phase Baseline subtraction, the
analysis found **0 of 160 localized participant cell midpoints** on either
distance axis. The entire expanded midpoint grid was compatible in
159 of the 160 cells. For the remaining cell, the set still reached an
outside-range grid boundary. Under same-label correction, all 159
estimable cells retained the entire grid. One participant phase cell
lacked enough same-label Baseline observations to estimate its bin
variance. The group calculation used its observed bin means.

Each of the four equal-participant group cell profiles and both equal-phase
condition profiles retained the entire expanded midpoint grid on both
axes. These search limits were −80 and 190 nominal cm on the registered
axis and −60 and 180 nominal cm on the trajectory axis. They are limits of
the search, with compatibility at each tested point, and do not imply
physical distances outside the experiment. The same result held when
retaining either of the two linked recordings separately. Every group
profile admitted at least one boundary-free reference. On the pooled
correction, Control-exhale was compatible with a line and a logarithmic
gradient but incompatible with a flat response at the stated cutoff.
Under same-label subtraction all six group profiles admitted a flat
response. Equivalent baseline cue timing has not been established.

The shared-width model minimized loss at a Viscereality–Control group
midpoint difference of −19.13 nominal cm on the registered axis. Its
simultaneous conditional contrast projection still spanned the full
−270 to 270 nominal cm allowed by the grid. The free model gave a
different point difference, −52.88 cm, with the same range. The
shared-midpoint models fixed that contrast to zero by design. The
[contrast export](midpoint_reduction_contrasts.csv) marks these cases
separately and retains the participant points and group profiles.
Grid-conditioned extrema are distinct from resolved effect estimates.

The profile analysis follows the principle of retaining nuisance-optimized
likelihood information across candidate locations. The presence of a
near-zero amplitude makes location unidentified, so this analysis uses
absolute compatibility with calibrated observation-space regions. It
does not interpret a one-degree-of-freedom likelihood-ratio cutoff as
regular at zero amplitude. [Raue et al. (2009)](https://doi.org/10.1093/bioinformatics/btp358)
and [Davies (1977)](https://doi.org/10.1093/biomet/64.2.247) motivate these
distinct checks; the Study 5 calibration and scope are in the specification.

## Held-distance prediction

The registered-axis primary shape fits yield the following held-distance
RMSEs on raw AT targets, in ms. Each column scores the same observed
targets across models. The group prediction uses the raw-profile covariance.

| Model | Participant cell means | Equal-participant group means |
| --- | ---: | ---: |
| Constant | 50.47 | 11.59 |
| Linear distance | 55.46 | 10.24 |
| Log distance | 60.18 | 13.18 |
| Separate midpoint and width | 189.13 | 202.36 |
| Shared width | 187.97 | 267.51 |
| Shared midpoint | 86.09 | 8.89 |
| Shared midpoint and width | 104.57 | 119.14 |

The flexible curves can extrapolate badly when a held endpoint carries
much of the information about a plateau. Reducing the maximum allowed
observed-bin span from 1,000 to 80 ms lowered the separate-shape error to
51.05 ms and the shared-width error to 51.10 ms for participant cells. At
that limit, sharing both parameters yielded 50.29 ms, close to 50.47 ms
for a constant. At limits of 160 and 320 ms, all four sigmoid versions
had larger participant errors than a constant. The group shared-midpoint
prediction remained 8.89 ms across the four limits on the registered axis
and 8.78 ms on the trajectory axis under the primary correction. Its
midpoint uncertainty and implied zero differences remained unresolved
and imposed, respectively. Under same-label correction the best group
RMSE came from a constant on both axes. These are descriptive predictions
across five dependent folds, with the span comparisons labelled post hoc.

## Recovery

The calibrated individual-cell regions contained the true generating
curve in 99.1–99.2% of simulated cells across the four scenarios.
Simultaneous four-cell coverage was 99.2–99.6%. The 95% nominal target
was conservative in these matched-Gaussian simulations, so the study's
wide profiles should not be interpreted as a sharp lower bound on what
every possible calibrated procedure could resolve. The group simultaneous
coverage ranged from 95.8% to 100% across 96 whole-cohort replicates per
scenario. Under simulation with an exactly flat response, 97.9% of
individual cells retained the flat reference.

Sharing width improved midpoint recovery in the 160-ms, shared-width
scenario, whose true Condition effect was 16.875 cm. Its participant-level
RMSE declined from 44.56 to 28.25 cm. The equal-participant group profile
RMSE declined from 4.27 to 3.57 cm. With an 80-ms signal and varying
widths, sharing width changed the group Condition RMSE from 34.01 to
11.17 cm, with the generating width restriction false in that scenario.
Coverage is checked at the true curve under the simulated error
distribution. The point-recovery comparisons use fixed matched
participant variances, and the separate coverage check re-estimates
them. These scenarios demonstrate which signals the design and
estimators could recover under their assumptions.

## Reproduction

Run `python -X utf8 analysis/boundary_methods/profile.py` from the
repository root with the pinned workbook validation environment. The
[profile export](midpoint_profiles.csv) retains disconnected
compatibility sets and search-bound flags. The [manifest](profile_results.json)
contains all seven recovery contrasts for each reduction, separate
participant and group prediction results, observed input hashes, and the
software versions. The script compares profile calculations to a
direct five-point GLS fit and checks offset invariance, known-shape
recovery and small finite joint-set fixtures.
