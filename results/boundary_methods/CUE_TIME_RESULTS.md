# Evidence under the documented tactile-cue offset

Recordings verified a 500 ms difference between Audio–Tactile and
Baseline cue times at the same nominal label in 15 cleared sessions.
The analysis applies that offset to the public primary40 as a
sensitivity. Public participant labels do not identify the verified
subset. [Source timing methods](../../manuscript/sections/methods.tex)
· [Numerical specification](CUE_TIME_SPECIFICATION.md)

## Exact timing matches

The common absolute cue times arise from 300 ms Audio–Tactile with
800 ms Baseline and 2200 ms Audio–Tactile with 2700 ms Baseline.
They correspond to 100 and 27 cm on the registered axis. These
two corrected means give a far-minus-near contrast. Any logistic
midpoint and positive width can span two values after choosing
the curve level and signed amplitude, so this comparison has no
free midpoint estimate.

| Difference in corrected far-minus-near RT | Mean, ms | Paired 95% interval, ms |
|---|---:|---:|
| Viscereality minus Control | −7.09 | −44.82 to +30.64 |
| Inhale minus Exhale | −8.50 | −47.50 to +30.51 |
| Condition × Phase | +10.39 | −50.19 to +70.97 |

These are paired differences across the 40 public participant
records under the offset assumption.

## Interpolated timing matches

Linear interpolation of the tactile-only mean provides two additional
positions, for 800 and 1500 ms Audio–Tactile. The 2700 ms probe
requires extrapolating beyond the latest tactile-only cue and is
excluded. The covariance preserves contributions from a Baseline
mean shared across interpolated probes.

All 512 estimable records were compatible with all 121 midpoint
grid locations. Four records lacked a within-person variance because
one Baseline bin contains only one retained trial. The mean remains
available to the group analysis. There was no difference in the
localization decision across linkage cohorts or distance mappings.

The flat model had lowest held-probe RMSE on both mappings.
Under the registered mapping its errors were 71.84 ms for
individual profiles and 12.32 ms for group profiles. The corresponding
errors for the best sigmoid reduction were 78.36 and 30.49 ms.

A simulated 160 ms transition at the matched four probes localized in
23.4% of group phase profiles and none of the participant phase
profiles, with 97.9% and 100% known-shape compatibility respectively.
With a flat generator, 0.26% of group phase profiles and no
participant phase profiles localized a midpoint. The working
simulation fixes the within-participant covariance at its estimated
value and draws whole-participant group vectors at matched covariance.
The fitted RT scale, Gaussian noise and interpolation are assumptions.

The observed offset leaves two exact matches, and the interpolation
adds model-derived comparisons. Neither analysis supplies a
participant or condition-level boundary estimate. Nominal SOA
and distance remain one-to-one within each mapping.

[Exactly matched profiles](cue_time_exact_pairs.csv) ·
[Interpolated profiles](cue_time_interpolated_profiles.csv) ·
[Estimates and hashes](cue_time_results.json) ·
[Code](../../analysis/boundary_methods/cue_time.py)
