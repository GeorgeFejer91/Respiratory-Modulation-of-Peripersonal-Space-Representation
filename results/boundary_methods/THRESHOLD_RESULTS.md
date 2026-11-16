# Monotone threshold sets in Study 5

The analysis requires the corrected mean RT to increase monotonically
with distance. It allows any continuous monotone response between
probes. It tests the half response within the observed endpoint range
and crossings of 0, 20 and 40 ms of facilitation. The absolute values
are exploratory reference levels. [Specification](THRESHOLD_SPECIFICATION.md)

## Observed location sets

No participant or equal-person group profile localized any of the
four crossings on either distance mapping or in either Baseline fit.
All 5,456 available contrast entries also remained unresolved.
These entries include different targets and sensitivities applied
to the same trials.

In primary40 with pooled Baseline, the observed-range half response
admitted every measured interval in all 160 phase-specific participant
profiles and all six group profiles. The absolute 0 ms target was
compatible with a crossing beyond the farthest probe in every one of
the six group profiles. At 20 ms, every group profile admitted every
interval as well as either censoring direction. At 40 ms, some group
profiles narrowed the within-range portion but retained a possible
crossing before the nearest probe. For example, the Viscereality
equal-phase group profile is compatible with the 10–27 cm interval
or a crossing before 10 cm on the registered axis. In the Control
equal-phase group profile only left censoring was compatible for this
threshold. These states depend on the monotonicity assumption and the
choice of facilitation threshold.

The same-label sensitivity left one individual phase cell without enough
baseline trials for uncertainty in any target. Its mean still contributes
to group profiles. All estimable rectangles admitted an ordered sequence.

## Held-distance prediction

The isotonic predictor uses inverse-variance weights, linear
interpolation between training probes and a plateau outside their
range. The half-response and threshold sets allow any continuous
monotone interpolation. The scores are root mean squared errors in ms
for the existing participants at held-out distances.

| Mapping and target | Flat | Linear | Log distance | Isotonic |
|---|---:|---:|---:|---:|
| Registered, pooled, individual | 50.47 | 55.46 | 60.18 | 48.91 |
| Trajectory, pooled, individual | 50.47 | 54.89 | 57.87 | 49.11 |
| Registered, pooled, group | 11.59 | 10.24 | 13.18 | 7.11 |
| Trajectory, pooled, group | 11.59 | 10.02 | 11.77 | 6.98 |
| Registered, same-label, individual | 78.85 | 94.67 | 99.17 | 84.43 |
| Trajectory, same-label, individual | 78.85 | 92.73 | 95.70 | 84.55 |
| Registered, same-label, group | 11.37 | 16.33 | 16.45 | 13.53 |
| Trajectory, same-label, group | 11.37 | 15.87 | 15.85 | 13.53 |

The isotonic fit improved prediction under pooled Baseline. The flat
model predicted best under same-label subtraction. Neither prediction
comparison estimates a crossing.

## Recovery

The matched simulations used a flat curve at and below zero, a gradual
line, and strong increasing clipped-ramp and logistic profiles with
participant-specific crossovers. Neither flat case produced false
localization at any of the four targets. For the two strong curves,
the true observed-range half response was localized in 4.4–5.2% of
individual profiles and 12.0–15.5% of group profiles. At the
absolute 20 ms target the group crossing localized in every replicate.
The mean group within-range widths were 30.2 and 32.6 cm, and the
simultaneous group condition envelopes contained the simulated
+14.05 and +11.67 cm shifts in every replicate. Individual
20 ms crossing localization reached 2.7–3.4%.

Simultaneous state coverage retained all compatible truth intervals,
plateaus, absent half responses and censoring cases. One group scenario,
with the whole profile exactly at the 0 ms target, gave 88/96 (91.7%)
joint coverage. Other scenarios gave 99.8–100% across both units.
The interval construction follows the stated Normal and independent
within-mean working assumptions. The simulation draws give a
limited-precision check of coverage.

The combination of wide response bands and five separated probes limits
location inference under the monotone assumption. The results retain
within-range intervals and directions of possible censoring for each
participant, phase and condition.

[Profiles](threshold_profiles.csv) · [Contrasts](threshold_contrasts.csv) ·
[Recovery and file hashes](threshold_results.json) ·
[Reproduction script](../../analysis/boundary_methods/threshold.py)
