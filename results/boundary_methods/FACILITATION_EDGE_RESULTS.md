# Farthest sampled probe with detectable facilitation

In primary40, the farthest probe with detectable facilitation moved
with the tactile-only reference. The Viscereality equal-phase profile
selected 73 cm with pooled Baseline, 100 cm with nominal label matching
and 27 cm when the +500 ms sensitivity restricted the analysis to exact
cue-time matches. The paired condition difference in facilitation
included zero at every tested probe. These are exploratory group results.

## Observed profiles

We tested two operational rules adapted from published analyses. The
first used paired signed ranks on mean-log differences and Holm
adjustment. The second used paired t tests on raw means, a Bonferroni
adjustment and a JZS Bayes factor threshold of 3. Differences are
Baseline minus Audio–Tactile RT. Inference uses whole participants and
the adjustment covers probes within one profile.
[Specification](FACILITATION_EDGE_SPECIFICATION.md) ·
[Teraoka et al. (2024)](https://muroran-it.repo.nii.ac.jp/record/2000223/files/Comparison%20of%20peripersonal%20space%20in%20front%20and%20rear%20spaces.pdf) ·
[Rahmani et al. (2025)](https://dael.euracoustics.org/confs/fa2025/data/articles/000866.pdf)

| Tactile-only reference | Rule | Control exhale | Viscereality exhale | Control inhale | Viscereality inhale | Control equal phase | Viscereality equal phase |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Pooled | Signed rank | 50 | 50 | 10 | 100 | 50 | 73 |
| Pooled | Paired t and JZS | 50 | 50 | 10 | 73 | 50 | 73 |
| Same nominal label | Both | — | — | — | 100 | 50 | 100 |
| Exact +500 ms matches | Both | — | — | — | 27 | — | 27 |

Probe locations are registered cm. A dash indicates no selection.
The JSON gives both distance maps and every qualifying probe. At
nominal labels, Viscereality equal phase qualified at 10, 27 and
100 cm, with holes at 50 and 73 cm. The 100 cm raw mean difference
was 32.41 ms (95% simultaneous interval [11.24, 53.58] ms). The
paired Viscereality-minus-Control difference at that probe was
15.52 ms (interval [−17.67, 48.72] ms). Nominal labels leave the
absolute cue times unverified.

Under the +500 ms sensitivity, the Viscereality equal-phase result at
27 cm was 24.17 ms ([2.79, 45.55] ms, adjusted p = .024, BF₁₀ = 3.49).
The paired condition contrast was −1.48 ms ([−31.92, 28.96] ms).
At BF₁₀ > 10 no exact-match probe qualified in any cohort. Both rules
selected 27 cm for Control equal phase in the linkage sensitivity that
excluded P033. Neither rule selected 100 cm under exact matching.
These two positions support an endpoint comparison under the offset
assumption. The public data lack the crosswalk for the 15 directly
verified sessions. [Cue timing and calibrated comparisons](CUE_TIME_RESULTS.md)

All 504 simultaneous intervals for paired RT contrasts included zero
across the seven factorial and simple contrasts, two rules, three
tactile-only references and three cohorts. These intervals measure
differences in facilitation. With paired t and JZS under nominal matching,
both equal-phase conditions selected the same probe in 178/999 paired
participant resamples, different probes in 656/999 and at least one
returned no selection in 165/999. Under exact matching those counts were
213/999, 75/999 and 711/999. Removing the 100 cm probe changed the
Viscereality nominal equal-phase selection to 27 cm. The deletion check
reapplies the selection rule to retained positions. Held-out RT prediction
requires a curve, evaluated in the separate
[monotone threshold analysis](THRESHOLD_RESULTS.md).

## Recovery and interpretation

Under the zero-facilitation generator, at least one of the six group
profiles selected a probe in 5–22 of 96 simulated cohorts across the
six method and reference configurations. At 40 ms or its log-scale
analogue, both equal-phase profiles recovered the planted farthest
facilitated probe in 83–91 cohorts. At 120 ms they recovered it in
84–95 cohorts. With constant nonzero facilitation across the sampled
positions, both conditions selected the outermost probe in all 96
cohorts for every method and reference. A qualifying outer probe
describes detected facilitation at that position. Interpreting it as
a transition requires assumptions about the profile between and
beyond sampled distances.

The published rules apply at group level and depend on error rates,
sample size and the tactile-only comparison. They supply no
participant-level location. The observed group profile selections
give different sampled farthest points under some references, with
paired condition contrasts in facilitation unresolved. Evidence from
fully sampled, cue-time matched profiles would be needed to estimate a
condition boundary shift from these rules.

## Reproduction

Run with the [pinned environment](../../analysis/baseline_effects/requirements.txt)
from the repository root.

```text
python -X utf8 analysis/boundary_methods/facilitation_edge.py
```

The [results](facilitation_edge_results.json) contain all 108 group
profiles, the paired comparisons, 24 recovery batches, input
denominators, software versions and source hashes.
