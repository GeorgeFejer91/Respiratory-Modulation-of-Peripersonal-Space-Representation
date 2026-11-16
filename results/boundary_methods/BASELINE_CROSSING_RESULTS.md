# Linear crossings of tactile-only RT references

Serino et al. estimated a trunk PPS location at the intersection of a
fitted audio–tactile RT line and the lower 95% confidence limit of
tactile-only RT. Study 5 applies that operational rule to each
participant, phase and condition, and to the equal-participant group
profile. The other references are the pooled mean, the lower limit of
the fastest tactile-only delay, and zero after timing-unverified
same-label subtraction. [Serino et al., Fig. 7](https://doi.org/10.1038/srep18603)
· [Study 5 specification](BASELINE_CROSSING_SPECIFICATION.md)

## Observed locations

No crossing localized among 3,084 estimable profiles. All 4,092
estimable contrasts were unresolved. These counts include repeated
analyses of the same observations across the reference rules, distance
mappings, weighting choices and group linkage cohorts. The sparse
same-label baseline bin prevents individual uncertainty estimation for
one phase cell and its equal-phase profile when that bin is needed.

In the primary sample, using the registered axis and the pooled lower
95% limit, 68 of 160 participant phase cells had a finite point inside
the measured range. In 159 of 160 cells the uncertainty set was
unbounded. The remaining cell, P004 Control exhale, supported a
positive slope but its compatible crossing ranged from −11.7 to 199.3 cm,
beyond both measured endpoints. That same participant's Control
equal-phase profile also supported a positive slope, with a much wider
crossing set.

The group phase points included 16.6 cm for Control exhale and 47.9 cm
for Viscereality inhale. Each group's slope was compatible with zero,
and both locations had the entire real line in their ratio sets. All
eight contrasts were unbounded under the registered pooled lower-limit
fit. In that fit the difference of the equal-phase profile point
locations was −5.2 cm. Averaging phase-specific fitted differences gave
+93.0 cm. Both depend on extrapolation and weak slopes. All five
baseline delays remained plausible candidates for the fastest one in
every primary group profile.

## Sensitivity and recovery

Each of the 499 group refits recomputed the tactile reference and the
RT slope. With the pooled lower limit, 260 Control-exhale refits and 184
Viscereality-inhale refits gave a positive-slope crossing within the
measured range. The fastest-delay lower-limit rule reduced those counts
to 65 and 74. The retained ratio sets permit unbounded and disconnected
locations. The finite refit quantiles are descriptive.

In the matched simulations, the strong line rose by 180 ms across the
measured range. The pooled-mean crossings differed by +12.6 cm between
conditions. That rule correctly localized 16.3% of participant cells
and 93.5% of group cells in the first noise scenario. The pooled
lower-limit rule correctly localized 10.5% of individual in-range
crossings and 57.0% of group in-range crossings. Raising baseline
noise by 75% at both simulation levels while holding the AT line fixed moved the mean pooled
lower-limit margin from 42.6 to 74.6 ms for individuals. Group in-range
localization fell to 1.8%. None of the 96 draws per flat or shallow
scenario falsely localized a crossing. Coverage for finite generating
crossings reached 99.7–100% per phase cell. The simulated sets are
conservative and condition on the observed margin for the lower-limit
rules. The full empirical refits carry uncertainty in that margin.

For registered pooled data, group held-distance RMSE was 11.59 ms for
the constant, 10.24 for the GLS line and 7.90 for the equal-weight line.
The earlier isotonic interpolation scored 7.11 ms on those same
held distances. For individuals the constant had lower error than
either line. The same-label group comparison favored the constant.
Prediction of a line profile and identification of the crossing are
separate outcomes. These are exploratory native results based on the
five Study 5 probe locations.

[Profiles](baseline_crossing_profiles.csv) ·
[Contrasts](baseline_crossing_contrasts.csv) ·
[Refits](baseline_crossing_refits.csv) ·
[Simulations and hashes](baseline_crossing_results.json) ·
[Code](../../analysis/boundary_methods/baseline_crossing.py)
