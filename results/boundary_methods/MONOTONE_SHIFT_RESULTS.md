# Relative shifts under an unknown monotone RT shape

Every estimable participant or group shift set covered the entire real
line. All groups were compatible with two constant curves, including a
single shared constant when both conditions were required to share
the RT level. The five probes leave the relative translation unresolved
under this common-shape assumption.

## Estimand and support

We compared pairs of mean RT curves linked by an unknown
nondecreasing function, a horizontal displacement and a level offset.
This removes the need to name a common sigmoid midpoint. A restricted
model fixed the vertical offset to zero. We projected simultaneous
mean bands onto the exact order regions of shifted probes, including
coincident probes and disjoint sampled domains. The method is a
restricted shape-invariant regression comparison.
[Specification](MONOTONE_SHIFT_SPECIFICATION.md) ·
[Lawton et al. (1972)](https://doi.org/10.1080/00401706.1972.10488942)

The 2,064 records cover five pairwise targets and the interaction,
two level specifications, both distance maps, both Baseline
specifications, the 40 participants and three group cohorts.
The two condition shifts enter the interaction through their set
difference. All 1,904 estimable participant targets and all 144 group
targets supported every displacement. Sixteen participant targets
lacked an estimable Baseline variance under nominal label matching.
For every estimable pair, the observed bands had a shared constant
solution. This directly certifies the unrestricted sets, including
the no-level-offset restriction. Band construction propagates the
available within-person noise and uses participant vectors at group
level. The simultaneous rectangles are conservative working-model
confidence regions.

With an unrestricted level offset, the two shifted domains can always
be put entirely apart on the latent coordinate. If each curve admits
a monotone trace, a vertical shift then lets one trace join the other
in either order. Thus both unrestricted tails remain compatible even
in some circumstances with evidence against zero shift. In Study 5
the complete overlap range was also supported, including zero shift.

## Held-probe prediction

The group models trained on four common probes per pair and scored
the held mean RT in each profile. The reported RMSE pools the 50
targets across five pairs and five probes. Some group curves enter
more than one paired comparison.

| Axis | Baseline | Separate constants | Separate isotonic | Shared monotone, zero shift | Shared monotone, free shift |
| --- | --- | ---: | ---: | ---: | ---: |
| Registered | Pooled | 9.59 | 6.58 | 6.44 | 8.59 |
| Trajectory | Pooled | 9.59 | 6.45 | 6.34 | 7.28 |
| Registered | Same label | 10.85 | 12.95 | 12.12 | 13.62 |
| Trajectory | Same label | 10.85 | 12.95 | 12.13 | 13.36 |

The scores are in ms. Under pooled Baseline a common shape predicted
better when the horizontal shift was held at zero. With nominal
same-label subtraction, separate constants predicted best. The
prediction convention interpolates training fits on a finite
representative shift grid. The support calculation evaluates all
distinct order regions separately.

## Recovery

Each generator used whole-participant residual vectors and a 25 ms
true level difference. Allowing that difference retained the planted
shift in all 96 replicates per generator and Baseline rule. For the
flat profile and the 20 cm shift of an 80 ms transition, every
unrestricted set retained all shifts. For the 40 cm shift of a
160 ms transition, zero was excluded in 96/96 pooled and 83/96
same-label replicates. Both unbounded tails were always compatible
in those strong-signal simulations.

With the level difference incorrectly forced to zero, the flat
generator excluded zero shift in 28/96 pooled and 15/96 same-label
replicates. A level difference can therefore masquerade as evidence
against zero translation. The observed data retained all shifts
under either level specification. The simulation gives neither a
participant boundary nor an estimate of the population shift.

## Reproduction

Run with the [pinned environment](../../analysis/baseline_effects/requirements.txt)
from the repository root.

```text
python -X utf8 analysis/boundary_methods/monotone_shift.py
```

The [result JSON](monotone_shift_results.json) includes the complete
compatibility unions, unavailable variance flags, all 100 held
comparisons, recovery counts and source and input hashes. The projection
was checked against linear programming. The observed results were
also verified directly from their constant witnesses.
