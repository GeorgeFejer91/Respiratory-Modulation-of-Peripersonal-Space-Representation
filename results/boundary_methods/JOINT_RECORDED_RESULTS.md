# Can recorded misses locate the same boundary as hit latency?

The analysis used 9,588 observed Audio–Tactile trials in primary40.
It counted 801 recorded misses and used 8,478 retained hit latencies.
The binary likelihood includes hits with missing or excluded latencies.
The latency likelihood uses the retained positive times. Each component
has its own level and amplitude. The shared model gives them a common
sigmoid midpoint and width. [Specification](JOINT_RECORDED_SPECIFICATION.md)

## Midpoints and paired effects

Only one of 160 participant phase cells had a conditional shared
midpoint interval wholly within the measured range in the primary fit.
The same Control-exhale cell, P004, recurred on both distance maps and
under both prior sensitivities. Its interval was 37–91 cm on the
registered map and 48–96 cm on the trajectory map. The model giving
only latency a sigmoid returned the same interval on each map. The
shared model's weight in that cell ranged from 0.126 to 0.172 under
the five equally weighted model families.

Every group phase and equal-phase location interval extended beyond
the measured range. For the shared model, the primary group condition
contrast was +2.25 cm on the registered map with a conditional 95%
interval of −128.25 to +126 cm. On the trajectory map the interval was
−118 to +108 cm. The median changed direction across the two linkage
cohorts on each map. Wider location support widened these intervals.
All 4,515 exported paired contrasts included zero. The contrasts span
different models and sensitivities on the same data.

## Prediction at unobserved probes

Each of five folds held out both outcomes at one probe. Scores are
log predictive densities per observed Audio–Tactile row. The latency
contribution is on the log-seconds scale and uses the fixed
cleaning mask.

| Model | Participant score | Shared group score |
| --- | ---: | ---: |
| Boundary-free bases | 0.12977 | 0.13034 |
| Latency sigmoid | 0.13213 | 0.13351 |
| Miss sigmoid | 0.13086 | 0.13018 |
| Separate sigmoids | 0.13323 | 0.13334 |
| Shared sigmoid | 0.13323 | 0.13193 |

The table uses the registered map and primary priors. For participant
fits, separate and shared sigmoid scores differed by less than 0.00012
per trial across the two maps and all prior variants. For group fits,
the latency-sigmoid model gave the highest score in every variant.
Its advantage over the shared sigmoid ranged from 0.00144 to 0.00254
log units per trial. The five folds use overlapping training data.
These comparisons leave the shared location assumption unresolved.

## Matched recovery

Each generator used 32 cohorts at the observed trial counts and
modeled the fraction of hits with a retained latency in each bin.
The table summarizes the shared sigmoid fits. RMSE is the mean of
the cohort-specific midpoint RMSEs. The condition truth for the
nonflat generators was +13.5 cm on the registered scale.

| Generator | Participant midpoint RMSE, cm | Shared group midpoint RMSE, cm | Group midpoint interval inclusion | Group condition interval inclusion |
| --- | ---: | ---: | ---: | ---: |
| Flat miss and latency |  |  |  |  |
| Both outcomes have the same transition | 12.34 | 3.38 | 96.1% | 30/32 |
| Latency transition, flat miss rate | 13.45 | 3.33 | 98.4% | 32/32 |

The flat generator produced zero wholly in-range conditional
midpoint intervals in either fit. Under the common-transition
generator, 11.7% of participant phase intervals and every group
phase interval localized within the range. The shared family had
the highest evidence weight in 61.7% of those group phase cells.
With a latency-only transition, the shared fit still gave interior
group phase intervals in all cohorts. Its family weight ranked
first in 7.8% of group phase cells. Thus a conditional interval can
localize the latency component even when the miss probability has
no transition.

## Reproduction

Run `python -X utf8 analysis/boundary_methods/joint_recorded.py`
with the [pinned numerical runtime](../../analysis/baseline_effects/requirements.txt).
The Gaussian integration agrees with a direct multivariate
Student-t density. The flat Bernoulli integral agrees with the
beta-function ratio, and independent two-dimensional integration
also agrees for sampled nonconstant shapes under both endpoint
priors. The [manifest](joint_recorded_results.json) includes the
observed denominators, software versions, recovery diagnostics,
and input and output hashes.

[Conditional intervals and weights](joint_recorded_intervals.csv) ·
[Held probe scores](joint_recorded_held_probes.csv) ·
[Combined held scores](joint_recorded_prediction.csv)
