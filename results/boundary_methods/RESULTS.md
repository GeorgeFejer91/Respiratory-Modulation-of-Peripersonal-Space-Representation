# First alternative PPS boundary estimates

These native exploratory screens use the 40-record cohort, excluding both
unresolved linked recordings. There are 8,478 retained audio–tactile hits in
160 participant-by-condition-by-phase cells. Each script retains the five
SOAs and also reports equal-phase condition profiles. A location calculated
from an equal-person mean response is a group profile parameter. It generally
differs from a mean of individual parameters.

## Spearman–Kärber and log-latency sigmoid

The [first specification](SPECIFICATION.md) uses Ferroni's adapted
Spearman–Kärber estimator and Ferri's mean-log-RT fixed-extrema sigmoid.
Spearman–Kärber returned a location in 135/160 cells and paired condition
contrasts could be calculated across all four cells for 21/40 people. The
within-session odd/even split correlation across supported phase-specific
and equal-phase profiles was ρ = .042 (169 profile pairs nested within
40 people). Those profile pairs do not furnish independent-person inference.
The underlying monotone RT profile yielded held-distance RMSE 48.89 ms
versus 48.77 ms for a training mean.

| Equal-participant profile | Centroid (nominal cm) | Conditional 95% bootstrap interval |
| --- | ---: | ---: |
| Control, exhale | 53.38 | [39.10, 73.58] |
| Control, inhale | 72.46 | [38.98, 79.57] |
| Viscereality, exhale | 59.13 | [34.43, 70.96] |
| Viscereality, inhale | 58.37 | [33.30, 79.68] |
| Control, equal phase | 68.87 | [44.03, 75.27] |
| Viscereality, equal phase | 56.44 | [33.37, 73.15] |

The difference between the last two profiles is −12.43 cm
(Viscereality minus Control, paired conditional 95% interval
[−32.71, 18.71], 989/999 draws with two finite centroids).
All seven paired group contrasts derived from the four cell profiles
include zero. The CSV gives uncertainty and the finite draw count for
every participant and aggregate. Pooled own-cell baseline subtraction
gave identical shape results by affine invariance.

Under 40,960 simulated flat profiles with the retained counts and SDs,
Spearman–Kärber produced a centroid in 32,649 (79.7%). Those centroids had
median 54.46 cm and central 95% range [32.06, 76.98] cm on the nominal
axis. With true 80-ms and 160-ms steps across the 27–50 cm gap, the mean
absolute centroid errors around the true gap midpoint were 11.34 and
7.38 cm among finite estimates. These results check estimator behavior
conditional on independent Gaussian within-bin noise, with no claim
of coverage under the full experimental process.

For the log-latency sigmoid, 37/160 phase-specific fits hit at least one
grid limit and 17/160 had a midpoint outside the sampled SOAs, with
overlap. In held-distance prediction, the sigmoid yielded RMSE 0.0744
natural-log units versus 0.0649 for a training mean. The matched raw
RT comparison yielded 54.46 versus 48.02 ms. The output reports
location, range/bound flags and prediction. Parameter uncertainty
for the log-latency sigmoid remains to be evaluated with a location
profile that admits a boundary-free state.

## Discrete change point

The [change-point specification](CHANGE_POINT_SPECIFICATION.md) retains the
four possible inter-probe gaps and three boundary-free families. On the
nominal axis, 13/160 cells had a single compatible gap family and 7 of
those jumps were positive in the hypothesized direction. At least one
boundary-free family remained compatible in 141/160 cells. The signed
step predicted held-out means with RMSE 49.99 ms versus 48.02 ms for a constant.

For the Control-exhale mean profile, one positive step between 50 and 73 cm
was compatible on the registered scale (estimated jump 21.81 ms). A line
was also compatible on the trajectory scale, on which the same observed
probes span 60–83.33 cm. Both equal-phase condition profiles allowed
boundary-free alternatives. The group contrast therefore has no uniquely
identified change point in each condition in this screen.

In matched Gaussian sampling-error simulations, the unique-step procedure
selected any gap in 674/40,960 flat cases (1.6%) and in 950/40,960 linear
cases (2.3%). Correct unique-gap recovery was 16.4% for an 80-ms true
step and 50.9% for a 160-ms step. The generating family stayed compatible
in about 95% of simulations by design under the known-variance Gaussian
approximation. Estimated observational variances, model misspecification
and repeated observations can affect real-world behavior.

## Distributional RT profiles

The [quantile specification](QUANTILE_SPECIFICATION.md) applies the discrete
profile comparison to the .25, .50 and .75 RT quantiles.

| RT quantile | Single compatible gap, signed | Single compatible gap, positive | Held-distance step / constant RMSE (ms) |
| --- | ---: | ---: | ---: |
| .25 | 5/160 | 4/160 | 47.25 / 44.30 |
| .50 | 1/160 | 0/160 | 57.05 / 53.40 |
| .75 | 5/160 | 2/160 | 73.18 / 68.20 |

The .25 Viscereality-exhale group profile retained only the third gap,
on both distance mappings. The .50 and .75 profiles did not locate
that gap uniquely. Both equal-phase conditions retained a boundary-free
alternative for all three quantiles. Correct unique-gap recovery in
the simulated 80-ms step ranged from 7.8% to 9.4% across quantiles.
This is a distributional sensitivity, with separate fits and no
multiplicity-adjusted claim across quantiles.

## Reproduction

Run from the repository root with the [workbook environment](../../workbook/requirements-validation.txt).

```text
python -X utf8 analysis/boundary_methods/screen.py
python -X utf8 analysis/boundary_methods/change_point.py
python -X utf8 analysis/boundary_methods/quantile_screen.py
```

[Spearman–Kärber](spearman_karber.csv), [raw/log sigmoid](fixed_extrema_rt_scales.csv),
[change-point](change_point_candidates.csv), and [quantile](quantile_candidates.csv)
tables retain all numerical estimates and non-estimates. JSON manifests
for the [first](screen_results.json), [step](change_point_results.json)
and [quantile](quantile_results.json) batches include input and artifact
hashes, simulations and software versions. The [audit](../../literature_review/BOUNDARY_METHOD_AUDIT.md)
records the planned remaining analyses and source constraints.
