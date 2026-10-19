# Consistent asymptote direction: refit and results

## Resolution

The previous signed-amplitude model allowed the response's near/far ordering to
reverse independently in each condition. That was a flexible diagnostic reference,
not a requirement of PPS physiology. The midpoint locates a transition; the
amplitude sign determines its direction. The owner now requests a common direction.

We refitted **all 160 participant × condition × phase curves** with
`corrected_RT(d) = delta + A*(logistic((d-m)/w)-0.5)`, **A >= 0**, **w > 0**.
On increasing physical distance, the near asymptote is always the lower RT and
the far asymptote the higher RT. Width and midpoint remain condition-specific with
hierarchical partial pooling. SOA runs in the opposite order to the mapped distance;
plotting increasing elapsed time instead would reverse the same curve's display.

This resolves ordering without forcing equal **numerical** plateau heights:
`L = delta - A/2`, `H = delta + A/2`, so H >= L in every draw. Making L and H
identical across a person's four conditions would be a stronger additional
measurement-invariance assumption; it was not needed or fitted here. No fitted
curve or observed trial was flipped after fitting. Reversed raw observations
remain visible as discrepancies, and arbitrarily small amplitudes remain allowed.

## Estimation and numerical checks

This is an exploratory amendment after previous results, specified in
`specification.json` before these fits. It changes the independent amplitude prior
from Normal(0,.15 seconds) to HalfNormal(.15 seconds); other priors match the earlier
converged marginalized reference. The same fixed cleaning, 40-person cohort and
participant × condition × phase Baseline calibration are retained. Baseline,
intercept and amplitude uncertainty are propagated jointly, not pre-subtracted and
then treated as independent. Baseline/offset/amplitude are integrated analytically;
the positive prior adds the exact Gaussian conditional orthant-probability factor.
Truncated-normal/Gaussian conditional draws reconstruct expected RTs afterward.

Five tests passed: likelihood versus an independent full-trial multivariate-normal
calculation, conditional moments/covariance, an empty held-out likelihood block,
monotonicity/midpoint/derivative, and posterior export. Final fit: **0
divergences, maximum Rhat 1.0029, minimum bulk/tail ESS
631/1630, diagnostic gate True**.
All sampling attempts, including any failures, remain in `fit_attempts.json`.

## Boundary and sharpness results

| quantity | term | posterior_median | ci_low | ci_high | probability_positive |
| --- | --- | --- | --- | --- | --- |
| midpoint_cm_effect | Condition | 2.347 | -60.74 | 66.15 | 0.5323 |
| midpoint_cm_effect | Phase | 8.137 | -61.95 | 64.81 | 0.6204 |
| midpoint_cm_effect | Condition × Phase | 0.5423 | -73.82 | 73.84 | 0.5064 |
| sharpness_per_cm_effect | Condition | 0.0002222 | -0.009143 | 0.01238 | 0.5403 |
| sharpness_per_cm_effect | Phase | -0.0009701 | -0.01117 | 0.009811 | 0.3285 |
| sharpness_per_cm_effect | Condition × Phase | -0.0001758 | -0.01458 | 0.01208 | 0.4749 |

These are finite-cohort paired contrasts with 95% credible intervals. Condition =
Viscereality − Control; Phase = Inhale − Exhale; interaction = difference of phase
differences. **0/6** main shape contrasts have intervals excluding zero.
Full population coefficients, response contrasts and all simple shape contrasts
are retained in `effects.csv` and `simple_parameter_contrasts.csv`. Interpret any
effect conditional on the new direction restriction and numerical diagnostics.
This is not an RM ANOVA on pooled posterior medians.

All amplitudes are positive **by assumption**, so a positive amplitude interval is
not evidence establishing a PPS response. Midpoint estimates span
**91.3–154.2 cm**; **0/160**
midpoint intervals lie wholly in the 10–100 cm sampled range. Median midpoint
interval width is **243.2 cm**. The median plug-in 10–90%
transition spans **305.7 cm**, versus 90 cm sampled;
**0/160** plug-in curves show both transition levels in
that range. Consistent direction does not itself establish identifiable plateaus,
curvature or individual physiological boundaries.

## Held-distance prediction comparison

All five AT-distance blocks were omitted in turn, across all participants/cells,
for both the positive and otherwise matched unrestricted model. Baseline remains
independent calibration. No direction, smoothing setting or p value was selected
using held-out results. Every prediction and both models' numerical attempts are
retained; **all final predictive gates passed: True**.

- Positive-amplitude RMSE: **46.90 ms**.
- Unrestricted RMSE: **47.27 ms**.
- Positive minus unrestricted MSE: **-34.91 ms²**,
  participant-paired 95% interval **[-132.36, 62.53]**.
- Held-block log predictive score difference: **8.60**,
  participant-cluster SE **8.20**.

Negative MSE differences favor the directional model; positive log-score differences
favor it. The paired uncertainty treats people as clusters and conditions on these
fitted prediction procedures; it is not a calibrated probability that one model is
true, a Bayes factor or new-participant validation. Check prediction tradeoffs
before presenting the directional model as a physiologically motivated
approximation; do not describe the direction as discovered from the constraint.

Posterior predictive mean-profile discrepancy-tail probabilities are
**AT 0.424**, **Baseline by nominal label 0.013**.
These check the stated Gaussian likelihood and pooled Baseline across nominal
labels, not the sign hypothesis. The earlier unverified cue-time-equivalence
and possible timing/variance discrepancies remain relevant.

## Figures and publication use

`average_curves.png` and all 40 pages of `individual_curves.pdf` use the measured
range and retain unsmoothed observations. Every posterior expected-response draw
and every exported median curve was checked to increase monotonically with
physical distance. The figures do not create missing plateaus by extending axes.
The earlier signed and standardized-full-S figures remain preserved references;
their condition-specific reversals are not the newly requested specification.

This model resolves the interpretational objection to reversed near/far asymptotes.
Its shape-effect conclusions, uncertainty and predictive comparison above determine
what can be reported. It does not turn an RT-location interaction into a boundary
effect or justify choosing a model because it yields significance. All prior
outcomes remain available; any p values in those outputs are still unadjusted.
Separate participant-shared numerical plateaus, robust likelihoods, questionnaires
and another recovery study were not fitted in this amendment. P011/P033 recording
mapping, original failed fit gate and individual measurement limits remain open.
Native execution only; browser/Pages and manuscripts were not updated.

## Reproduce

Use Python 3.12 and `analysis/baseline_effects/requirements.txt`, with
OPENBLAS_NUM_THREADS=1 and OMP_NUM_THREADS=1:

```bash
python -m unittest discover -s analysis/directional_sigmoid -p 'test_*.py' -v
python analysis/directional_sigmoid/model.py fit
python analysis/directional_sigmoid/model.py cv
python analysis/directional_sigmoid/report.py
```

Cross-validation resumes completed folds from its CSV; move it aside for a fresh
run. The source, inputs, local posterior trace and public outputs are hashed in
`manifest.json`; large traces remain local. The downloadable ZIP contains the
public results, figures, specifications and diagnostics.
