# First detectable adjacent RT decrease

The group-level rule selected the **same 50–73 cm registered gap** in
Control exhale and Viscereality exhale under raw audiotactile RT. No gap
was selected after subtracting tactile-only RT at each nominal delay.
The adjacent-delay results leave participant boundaries and condition
shifts unresolved.

## Estimand and design

Hobeika et al. used post-hoc comparisons of adjacent delays to locate
the onset of group RT facilitation. Their transition analyses excluded
the simultaneous sound–touch probe. Study 5 has five positive nominal
stimulus onset asynchronies (SOAs). The
[adaptation](ADJACENT_RULE_SPECIFICATION.md) walks from far to near and
selects the first gap where the mean of participants' paired
farther-minus-nearer RT differences is positive at a Bonferroni-adjusted
one-sided p < .05. The adjustment covers the four gaps within each
profile. The gap endpoints are sampled positions, with no fitted
position inside the gap. [Hobeika et al. (2019), §3](https://pmc.ncbi.nlm.nih.gov/articles/PMC6731720/)

The primary cohort excludes both records with unresolved recording
linkage and retains 8,478 audiotactile and 4,192 tactile-only RTs from 40
participants after the established cleaning. Each 41-person sensitivity
excludes one of the disputed records. Within a participant and phase,
subtracting a single pooled Baseline leaves adjacent differences
identical to raw RT. Same-label subtraction uses the nominal SOA labels.
Their absolute AT-to-Baseline cue timing is uncertain.
[Cue timing](CUE_TIME_RESULTS.md)

## Observed selection and uncertainty

The two selected primary gaps span 60–83.33 cm on the trajectory map.
Neither inhale profile nor either equal-phase profile selected a gap.

| Primary40 raw or pooled Baseline profile | Farther minus nearer RT (ms) | Two-sided 95% simultaneous interval (ms) | Adjusted one-sided p | Bootstrap selecting 50–73 cm |
| --- | ---: | ---: | ---: | ---: |
| Control exhale | 20.06 | [−0.31, 40.43] | .02757 | 639/999 |
| Viscereality exhale | 16.68 | [−0.91, 34.27] | .03488 | 556/999 |

The two-sided intervals allocate error to both tails across the four
gaps and include zero. The directional selection tests allocate error
to one tail. At the same gap, the paired Viscereality-minus-Control
difference in the exhale RT change was **−3.38 ms** (95% simultaneous
interval [−27.66, 20.89] ms). This contrast measures a difference in
RT changes. All 168 paired RT contrast intervals included zero across
seven effects, four gaps, three cohorts and two baseline variants.
Intervals are simultaneous across gaps within each effect.

Control exhale selected the gap in both linkage sensitivities.
Viscereality exhale selected it only in the sensitivity excluding P033.
Same-label subtraction gave no selection in all 18 profiles across the
three cohorts. Among 999 paired participant resamples in the primary
raw exhale profiles, both conditions selected some shared gap in 386,
selected different gaps in 71, and at least one condition returned no
gap in 542. After same-label subtraction, neither exhale condition
selected a gap in 800 resamples and both selected some shared gap in four.

| Registered probe omitted | Control exhale gap (cm) | Viscereality exhale gap (cm) |
| --- | --- | --- |
| 10, 27 or 100 cm, each separately | 50–73 | 50–73 |
| 50 cm | 27–73 | No selection |
| 73 cm | No selection | 50–100 |

Omitting a probe changes which positions count as adjacent. This is a
stability check, and the rule supplies no prediction for the omitted RT.
The separate calibrated discrete step predicts held-probe mean RTs and
keeps gradual shapes as references. The step's held RMSE was 49.99 ms
versus 48.02 ms for a constant across participant phase cells.
[Discrete change point](RESULTS.md#discrete-change-point)

## Matched recovery

Each generator resampled centered whole profiles from primary40
participants, retaining the observed cross-cell and cross-probe
dependence. The step generator planted different gaps in the two
conditions and used the same gap in both phases within each condition.
The flat generator selected at least one gap across six profiles in
26/96 raw cohorts and 22/96 same-label cohorts. Each profile was treated
as its own comparison family.

| Planted step | Both equal-phase condition gaps recovered, raw or pooled | Both equal-phase condition gaps recovered, same-label |
| --- | ---: | ---: |
| 40 ms | 91/96 | 82/96 |
| 120 ms | 91/96 | 92/96 |

The recovery results describe a discrete step with the simulated
amplitudes and gap locations. The observed exhale gap depended on
baseline choice and probe coverage. The group comparisons supply no
participant-specific estimate, and finding the same gap in both
conditions leaves any within-gap difference unidentified.

## Reproduction

Run from the repository root using the pinned
[native analysis environment](../../analysis/baseline_effects/requirements.txt).

```text
python -X utf8 analysis/boundary_methods/adjacent_rule.py
```

The [result JSON](adjacent_rule_results.json) contains every observed
profile and gap, RT intervals, paired selection counts, simulation
counts, trial-release hashes, source hashes and software versions.
