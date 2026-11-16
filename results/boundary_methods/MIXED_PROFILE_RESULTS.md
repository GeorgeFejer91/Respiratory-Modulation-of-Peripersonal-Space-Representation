# Paired midpoint shifts from maximum marginal likelihood

The log-RT model uses the same 8,478 retained Audio–Tactile latencies
as the other primary40 trial analyses. It uses a participant-specific
latent Control location and one common condition shift within each
scheduled phase. A finite-lattice maximum marginal likelihood fit
selects the population shape parameters. The integrated level,
amplitude and variance terms retain the conditional latency model's
proper nuisance priors. [Specification](MIXED_PROFILE_SPECIFICATION.md)

## Identifiability

The paired condition effect is the average of the two phase shifts.
It used the entire primary location-contrast search. On the registered
map its conditional point estimate was −47.25 cm and the support range
was −90 to +90 cm. On the trajectory map it was −38 cm with a support
range of −80 to +80 cm. The phase and Condition × Phase support
ranges also reached both endpoints allowed by the search.

On the registered map the inhale shift was estimated at −90 cm,
the lower search limit. Widening the search moved it to −117 cm,
the new lower limit. The trajectory map gave −80 cm and −104 cm,
again the lower limits. The shift estimates are sensitive to the
search bounds. The fitted inhale midpoint SD was zero on both maps
and both lattices. In that phase, the plug-in participant intervals
collapse to the fitted population locations. They condition on the
population parameters and leave their uncertainty outside the
participant intervals.

The primary exhale and inhale shape gains on the registered map
were 35.52 and 11.51 in twice-log-likelihood units against the best
boundary-free reference. The calibrated cutoff was 35.76. The gains
from freeing the condition shift were only 0.014 and 0.698 in the
same units. The trajectory map also fell below the primary shape
cutoff in both phases.

The registered exhale gain increased to 36.31 on the wider lattice.
Its fitted between-person SD reached 54 cm, the largest value tested
on that lattice. A separately run wide-lattice calibration returned
the same 35.76 shape-selection cutoff. The exhale comparison crossed
the cutoff only on the registered map and wider lattice. The
registered condition support range reached −117 to +117 cm on the
wider lattice. The small held prediction advantage for zero shift
and the full-range shift support leave the condition effect unresolved.

## Held-probe prediction

Primary registered-axis scores use five held-probe folds and are
weighted by the retained hit-RT counts.

| Model | Held log density per trial |
| --- | ---: |
| Constant | 0.427705 |
| Linear | 0.426568 |
| Log distance | 0.425131 |
| Sigmoid with zero shift | 0.429811 |
| Sigmoid with free shifts | 0.429444 |

The model with zero shift had the highest held score on both maps
and both lattices. Differences between the sigmoid models were
0.00037–0.00067 log units per trial. The shared shape can improve
prediction while the paired location shift remains unresolved.

## Matched recovery

The primary calibration and evaluation each used 32 cohorts per
generator. In independent evaluation the phase selection rule
identified a shape in at least one phase in 0 of 32 flat cohorts and
2 of 32 affine cohorts. It selected 7 of 32 weak cohorts and all 32
strong cohorts. It selected both phases in zero weak cohorts and
31 strong cohorts.

Participant midpoint RMSE averaged 23.23 cm under the weak
generator and 9.84 cm under the strong generator. Conditional
participant interval inclusion was 21.6% and 84.4%, respectively.
All 32 group condition support ranges included the inserted +13.5 cm
effect in each nonflat scenario. The broad group coverage and weak
participant coverage describe different uncertainty targets. The
wider-lattice calibration and evaluation gave the same selection
counts and condition-interval inclusion for these generators.

## Reproduction

Run `python -X utf8 analysis/boundary_methods/mixed_profile.py` with
the [pinned runtime](../../analysis/baseline_effects/requirements.txt).
Direct summation independently checked the mixed likelihood and
contrast projection. The manifest records the measured input hashes,
calibration and evaluation seeds and outputs, and result file hashes.

[Effects and support ranges](mixed_profile_effects.csv) ·
[Conditional participant estimates](mixed_profile_participants.csv) ·
[Shape geometry](mixed_profile_geometry.csv) ·
[Held probe scores](mixed_profile_held_probes.csv) ·
[Manifest](mixed_profile_results.json)
