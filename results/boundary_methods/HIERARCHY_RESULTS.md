# Hierarchical PPS boundary sensitivity

The signed Gaussian marginal likelihood conditions on the same
retained observations for all reference and shape fits. All five
primary observed-data shape fits passed the target diagnostic gate.
The fixed population effect and the sampled participants' paired
effects are separate estimands. Positive condition contrasts denote
Viscereality minus Control. [Specification](HIERARCHY_SPECIFICATION.md)

## Observed midpoint uncertainty

| Primary model | Population condition median, cm | 95% credible interval, cm |
|---|---:|---:|
| Full | −3.54 | −83.46 to +76.79 |
| Shared population width | −3.12 | −85.22 to +79.22 |
| Reduced midpoint condition variation | −2.94 | −81.41 to +76.99 |
| Reduced midpoint condition variation with participant width | −4.56 | −79.27 to +73.84 |
| Shared participant contrasts | −4.31 | −83.95 to +76.33 |

The model with participant-specific width gave intervals of −44.10
to +40.59 cm and −123.81 to +112.89 cm at half and twice the primary
shape-prior scale. Its prior fraction of latent midpoints inside the
measured range was 51.2% at the primary scale, and 56.4% in the
posterior. The full model changed from 50.6% to 49.6%.

Across 6,000 posterior draws in each primary fit, zero draws gave
both condition-average profiles a qualifying positive derivative
peak. This used the registered 10–100 cm grid and the prespecified
interior peak rule, including its check on derivative values at the
edges. The result holds at a minimum fitted span of zero. The
population contrast of latent midpoints therefore remains conditional
on component shape even where parameter diagnostics pass.

Among the qualified sensitivities, at zero minimum span the
double-prior-scale participant-width fit had one qualifying pair in
6,000 draws and the shared-location fit had two in 6,000. The largest
qualification fraction for any single phase or condition curve was
1.35%. No observed fit had a qualifying pair with a minimum span of
20 or 40 ms.

The positive-amplitude stress tests passed the target diagnostic
gate after extension. The population condition interval was −47.34
to +46.12 cm without session time and −47.77 to +47.26 cm with the
linear session-time term. The explicit joint pooled and same-label
calibrations failed the shape gate after extension. They remain
numerically unresolved. The no-Baseline marginal fit qualified.

## Prediction at held probes

All 40 model-by-probe fits in the primary comparison have a qualified
attempt. The initial full-model fit at 73 cm had one divergence.
Its prespecified extended attempt passed with zero divergences.
Log score is the held participant-cell-block log density per trial,
pooled across probes by the retained trial counts. RMSE weights
the five probes equally.

| Model | Held log score per trial | Individual RMSE, ms | Group RMSE, ms |
|---|---:|---:|---:|
| Constant | 0.79896 | 47.94 | 9.79 |
| Linear | 0.79688 | 50.12 | 7.35 |
| Log distance | 0.79445 | 51.20 | 9.47 |
| Full | 0.80286 | 47.29 | 8.52 |
| Shared population width | 0.80298 | 47.26 | 8.54 |
| Reduced midpoint condition variation | 0.80296 | 47.27 | 8.54 |
| Reduced with participant width | 0.80289 | 47.24 | 8.53 |
| Shared participant contrasts | 0.80299 | 47.28 | 8.55 |
| Shared location with factorial widths | 0.80287 | 47.26 | 8.54 |

Differences among the primary sigmoid models' density scores were
below 0.00014 per trial. The linear reference had the lowest group
mean prediction error. The five folds reuse participants and have
overlapping training sets. The reported rankings are descriptive.

A sixth shape sensitivity gives each participant a single midpoint
across their four cells while preserving factorial widths. It fitted
the full observed data with a passed diagnostic gate. Its three
midpoint population contrasts are fixed to zero. Its 50 cm held
fit initially failed the target diagnostic gate. Its 6,000-draw
extension passed. The model achieved essentially the same density
score as the other sigmoid fits. Held predictions cannot distinguish
factorial midpoint variation from factorial width variation in
this comparison.

## Matched recovery

Both reduced-condition fits ran the four predeclared cohorts for
each of the four generators. Thirty of 32 fits passed, with one
failed flat fit under each width model. All 24 nonflat fits passed.
The table gives mean participant midpoint RMSE across qualified
cohorts. The condition effect truth was +10 cm.

| Generator | Shared width RMSE, cm | Participant width RMSE, cm | Participant intervals containing the shape truth |
|---|---:|---:|---:|
| 40 ms, shared width | 22.59 | 23.21 | 100% in both models |
| 200 ms, shared width | 7.90 | 7.93 | 87.3% and 87.8% |
| 200 ms, heterogeneous widths | 8.72 | 8.73 | 80.5% and 80.2% |

The weak generator's individual condition-contrast RMSEs were
12.52 and 12.78 cm. Its wide intervals covered the truth despite
substantially larger midpoint error. The population condition
intervals covered the inserted effect in all 24 nonflat fits.
The population phase interval covered its truth in three of four
heterogeneous-width cohorts for either model.

Both planted condition curves had qualifying interior peaks in
each weak cohort, with expected observed-design spans of
34.6–35.3 ms. The eight fitted weak cohorts yielded zero qualifying
peak pairs in 4,800 evaluated draws at the zero- and 20-ms thresholds.
The six qualified flat fits had zero in 3,600 draws. All 9,600
evaluated draws across the 16 strong fits supported paired peaks at
all three span thresholds. At zero threshold, the aggregate peak
contrast interval contained the true contrast in all eight
strong shared-width fits and four of eight strong heterogeneous-width
fits. The planted aggregate differences were 9–10.5 cm and 12–13 cm,
respectively, measured on the 0.5 cm grid. Four fixed seeds per
generator give a stress test of recovery at these signal sizes.

## Run records

[Matched prediction summary](hierarchy_prediction.csv) ·
[Individual probe receipts](hierarchy_held_probes.csv) ·
[Diagnostics, observed estimates and recovery receipts](hierarchy_fit_inventory.json) ·
[Participant midpoint summaries](hierarchy_participant_midpoints.csv) ·
[Observed aggregate peaks](hierarchy_group_peaks.csv) ·
[Recovery aggregate peaks](hierarchy_recovery_geometry.csv)

The exports include 399 group rows across 19 observed configurations,
5,320 conditional participant rows, and 672 recovery geometry rows across
32 attempts. The inventory hashes the sources, retained trial inputs and
result tables. To regenerate these tables from the fit receipts and
posterior arrays, run `hierarchy_geometry.py` and then `hierarchy_report.py`
under `analysis/boundary_methods/`. The sampling environment uses the
[pinned runtime](../../analysis/baseline_effects/requirements.txt).
