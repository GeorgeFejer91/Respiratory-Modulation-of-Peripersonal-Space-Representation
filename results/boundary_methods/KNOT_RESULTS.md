# Continuous slope changes in Study 5

This exploratory analysis compares three continuous profiles. A near
plateau estimates an onset of distance dependence. A far plateau
estimates where distance dependence levels off. The free broken line
estimates a change between two slopes. All have a signed slope change.
The trial cleaning, uncertainty radius and group weighting follow the
preceding analysis. [Specification](KNOT_SPECIFICATION.md)

## Observed knot compatibility

Under primary40 and pooled Baseline, one of the 160
participant-by-condition-by-phase profiles localized a knot in the
near-plateau family. The same Viscereality-exhale cell (P035) produced
this result on both mappings. Its model-conditional point was 52.3 cm
on the registered mapping and 70.4 cm on the trajectory mapping. The
respective compatible sets were 36.1–88.3 cm and 48.8–89.6 cm. The
same-label sensitivity removed both localizations. This is one
exploratory cell observed across two mappings of the same trials.

No far plateau, broken line or participant equal-phase profile
localized a knot. No group phase or condition profile localized a
knot, including the alternate linkage cohorts. For primary Control
exhale, the line and log-distance references remained compatible.
Each of the other primary group profiles admitted a constant.
Every available participant and group contrast remained unresolved
across the tested families, mappings and Baseline fits. Conditional
registered group condition points ranged from −22.3 to −2.1 cm across
the three primary families, with compatible contrast envelopes of
−135 to +135 cm, the entire range allowed by the knot grid. One
same-label phase cell lacks the variance required for a person-level
set. It still contributes its observed mean to group profiles.

## Held-distance prediction

The table gives root mean squared error in ms across the same five
held-probe folds. These candidate columns use the prespecified
±320 ms slope-change limit.

| Mapping and target | Flat | Linear | Log distance | Near plateau | Far plateau | Broken line |
|---|---:|---:|---:|---:|---:|---:|
| Registered, individual | 50.47 | 55.46 | 60.18 | 55.74 | 56.11 | 57.43 |
| Trajectory, individual | 50.47 | 54.89 | 57.87 | 53.05 | 56.62 | 55.92 |
| Registered, group | 11.59 | 10.24 | 13.18 | 11.70 | 9.63 | 11.10 |
| Trajectory, group | 11.59 | 10.02 | 11.77 | 9.74 | 9.58 | 9.41 |

The best nonconstant candidate changed across group mappings. Their
errors were unchanged by the 160 and 640 ms caps in the primary group
fits. At all three caps, the constant had the lowest individual error.
It also had the lowest group error under same-label subtraction on both
mappings. The folds held out distances within the existing participant
sample. They score response prediction conditional on fixed cleaning.

## Recovery under the matched working model

The simulated change points were 46.0, 49.6, 56.8 and 60.4 cm across
the four registered cells. They implied a +10.8 cm equal-phase
condition shift. Under the family that generated the data:

| Generator | True knot localized, individual | True knot localized, group | Condition shift RMSE, individual | Condition shift RMSE, group |
|---|---:|---:|---:|---:|
| Near plateau | 19.6% | 96.9% | 16.84 cm | 2.80 cm |
| Far plateau | 3.9% | 96.1% | 18.13 cm | 2.92 cm |
| Broken line | 8.3% | 99.2% | 13.03 cm | 2.69 cm |

The RMSE uses every descriptive point estimate. Joint four-cell coverage
was 99.2–99.8% in individuals and 95.8–100% at group level, across 96
whole-cohort draws per generator. With no true knot in the flat and
linear simulations, a family localized at most 0.39% of individual cells
and 1.30% of group cells. These are per-family fractions and do not adjust
for searching across people, cells, models or mappings. The simulated
group curves shared the same strong knot across people within a cell.
Recovery from mixed or weak effects can be lower.

The data support a model-conditional onset candidate in one individual
phase cell. That cell supplies no robust paired estimate. Group and
participant condition-level boundaries remain unresolved under this
family. This batch used a finite knot grid and conservative uncertainty
sets under working independence and Normal assumptions. It contributes
to the exploratory audit.

[Profiles](knot_profiles.csv) · [Contrasts](knot_contrasts.csv) ·
[Recovery and file hashes](knot_results.json) ·
[Reproduction script](../../analysis/boundary_methods/knot.py)
