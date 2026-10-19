# Explicitly shape-constrained Bayesian sigmoid approximation

## What was fitted

The owner requested a visible S after the broad positive-amplitude fits looked
nearly linear. This is an **exploratory, strongly theory-constrained approximation**,
not evidence that a sigmoid was observed. The specification was fixed before this
amendment's fits. Both models jointly use original AT and Baseline trials, fixed
cleaning, the same primary40 cohort, positive amplitudes and matched Baseline
uncertainty. Raw observations were not smoothed, clipped or transformed.

Primary `visible95` forces each normalized component to be at most .05 at 10 cm
and at least .95 at 100 cm. Sensitivity `visible90` uses .10/.90. With
`k=log((1-epsilon)/epsilon)`, width is `2+(90/(2*k)-2)*logistic(eta_width)` cm,
and midpoint is `10+k*width+(90-2*k*width)*logistic(eta_position)` cm.
Both logit coordinates have participant factorial hierarchies: fixed coefficients
Normal(0,1.5), random-coefficient SDs HalfNormal(1), independent noncentered scores.
The constraint couples the priors on midpoint and width. All nuisance priors and
the exact integrated Gaussian positive-amplitude likelihood match the broad
directional reference. Five independent checks passed, including endpoint geometry,
likelihood, prior simulation and conditional reconstruction.

The maximum primary width is **15.283 cm**; hence normalized
sharpness is at least **0.0164 /cm by assumption**.
All midpoint intervals must lie inside the sampled range because of their support.
Neither fact demonstrates better individual measurement or physiological validity.
Near-zero response amplitudes remain possible; their positive intervals follow
from the amplitude prior and do not establish a response.

## Numerical results and condition comparisons

| model | divergences | max_rhat | min_bulk_ess | min_tail_ess | gate |
| --- | --- | --- | --- | --- | --- |
| visible95 | 0 | 1.004 | 1437 | 1755 | True |
| visible90 | 0 | 1.002 | 5748 | 5005 | True |

All main finite-cohort parameter contrasts, with 95% credible intervals:

| model | quantity | term | posterior_median | ci_low | ci_high |
| --- | --- | --- | --- | --- | --- |
| visible95 | midpoint_cm_effect | Condition | 0.4065 | -10.23 | 10.58 |
| visible95 | midpoint_cm_effect | Phase | -1.329 | -12.37 | 8.331 |
| visible95 | midpoint_cm_effect | Condition × Phase | -3.328 | -18.45 | 6.968 |
| visible95 | sharpness_per_cm_effect | Condition | 0.0005092 | -0.01427 | 0.0189 |
| visible95 | sharpness_per_cm_effect | Phase | -0.0008644 | -0.01535 | 0.01696 |
| visible95 | sharpness_per_cm_effect | Condition × Phase | -0.002999 | -0.02679 | 0.01358 |
| visible90 | midpoint_cm_effect | Condition | -0.003634 | -4.451 | 4.895 |
| visible90 | midpoint_cm_effect | Phase | -0.1776 | -6.662 | 2.89 |
| visible90 | midpoint_cm_effect | Condition × Phase | -0.1528 | -9.052 | 4.268 |
| visible90 | sharpness_per_cm_effect | Condition | 9.8e-07 | -0.003035 | 0.003684 |
| visible90 | sharpness_per_cm_effect | Phase | -6.111e-05 | -0.004842 | 0.002119 |
| visible90 | sharpness_per_cm_effect | Condition × Phase | -5.2e-05 | -0.007053 | 0.002966 |

**0/12** intervals exclude zero across the two shape-prior variants.
Condition means Viscereality − Control; Phase means Inhale − Exhale; interaction
is the difference of phase differences. All main/simple/RT contrasts remain in
`all_effects.csv` and `all_simple_contrasts.csv`. These are joint posterior
contrasts, not ANOVAs on pooled point estimates. The logit coefficients are not
physical-unit population effects; no such mislabeled coefficients are exported.
Any nonzero interval is conditional on a post-results shape prior, not a new
preregistered discovery. No multiplicity corrections were introduced.

## What the data add to the constraints

The median individual midpoint 95% interval is **34.1 cm**
wide versus **63.4 cm** under the new prior.
The median posterior/prior interval-width ratio is **0.539**.
This is a descriptive conditional information check, not validated coverage or
test–retest reliability. All 960 individual prior/posterior summaries and 24
cohort summaries are exported. Prior comparison was independently checked against
PyMC sampling, using 5,000 prior draws. A constrained posterior can be precise
under an incorrect shape model; width contraction alone does not establish truth.

| model | width_max_cm | posterior_width_above_90pct_cap | prior_width_above_90pct_cap | midpoint_median_min_cm | midpoint_median_max_cm |
| --- | --- | --- | --- | --- | --- |
| visible95 | 15.28 | 0.5214 | 0.1836 | 55.88 | 70.04 |
| visible90 | 20.48 | 0.8758 | 0.1787 | 55.08 | 55.21 |

The width cap couples midpoint and width: as width approaches its maximum, the
allowed midpoint range collapses toward 55 cm. Posterior mass near that cap and
similar individual midpoints can therefore reflect the model trying to recover a
broad, nearly linear response while obeying the imposed S. This is a constraint
artifact, not independent evidence of precise or identical physiological boundaries.

## Held-distance comparison

Five primary95 refits omitted all AT trials at one distance across all people/cells,
retaining independent Baseline calibration. The preserved broad positive model has
the same target observations and nuisance priors; these were checked row by row.

**At least one held-distance refit still fails its predictive convergence gate after the fixed extension budget. The errors and intervals below are provisional numerical summaries, not a validated model comparison; they must not be used to claim predictive superiority or noninferiority.**

Post hoc diagnostic decomposition of the same predictions, without refitting or
changing either model:

| held_distance_cm | visible_RMSE_ms | broad_RMSE_ms | both_predictive_gates |
| --- | --- | --- | --- |
| 10 | 106.4 | 50.87 | False |
| 27 | 44.11 | 40.95 | True |
| 50 | 46.59 | 46.25 | True |
| 73 | 42.19 | 40.86 | True |
| 100 | 109.6 | 54.08 | True |

Across the **4 converged folds only**, diagnostic RMSE
is **66.92 ms** for visible95 versus
**45.86 ms** for the broad reference.
This restricted subset is not the complete cross-validation result. It retains
the declared numerical gates and is reported to show which distances drive the
prediction tradeoff; every failed fold remains exported. A visible S is not itself
a reason to prefer the constrained model for physiological measurement.

- Visible95 RMSE: **76.47 ms**.
- Broad positive-reference RMSE: **46.90 ms**.
- Visible minus broad MSE: **3648.28 ms²**, participant-paired
  approximate 95% interval **[2932.36, 4364.21]**.
- Held-block log predictive score difference: **-294.60**,
  participant-cluster SE **25.84**.
- All final predictive diagnostic gates: **False**.

Lower MSE and higher predictive log score favor the visible model. This comparison
is within the retained cohort and does not establish new-person generalization,
formal noninferiority or a Bayes factor. It tests predictive consequences of
requiring a visible S, not whether that S was observed. The 10/90 sensitivity was
not separately cross-validated. No bounds or cleaning thresholds were selected
using significance or held-out scores.

Primary posterior-predictive mean-profile discrepancy-tail probabilities are
AT **0.243**, Baseline by nominal label **0.013**.
They check the stated Gaussian model, not the truth of the sigmoid hypothesis.
The old pooled-baseline timing/variance concern remains if its discrepancy is low.

## Figures and scope

`sigmoid_curves.png` is visibly sigmoid on the measured physical-distance axis.
Its line uses the median posterior **cohort-mean midpoint and width**, transformed
into a representative unit-amplitude sigmoid. The 95% band is for that same
mean-parameter function. It is not the average individual RT curve, the pointwise
posterior median response, or a normalized observed dataset. The visibility is
guaranteed by the prior. `boundary_estimates.png` compares prior/posterior mean
midpoints. `observed_RT.png` shows actual observations and the average expected RT
function, which need not have the same appearance.

`individual_sigmoids.pdf` contains all 40 retained participants, with four raw-data
panels and four normalized model panels each. Both broad and constrained curves
remain visible on the raw-data panels. All 160 plug-in normalized curves and all
posterior draws satisfy the endpoint restriction. Parameter intervals use every
retained draw; individual/RT ribbons use 1,200 balanced draws for plotting, while
the main normalized figure uses every draw. Lines at marginal parameter medians
are not claimed to be joint MAP estimates. The 2 cm minimum width is an explicit
prior choice, not a measured resolution.

The requested visible approximation is computed. Whether these are valid
individual physiological PPS boundaries remains unresolved. Original failed fit
gates, P011/P033 recording mapping, single-session reliability and baseline-timing
limits persist. Questionnaires and a new recovery study were not run here. Earlier
unrestricted/directional results are preserved. Native execution only; no Pages
or manuscript update was performed.

## Reproduction

Use the pinned native environment in `analysis/baseline_effects/requirements.txt`:

```bash
python -m unittest discover -s analysis/visible_sigmoid -p 'test_*.py' -v
python analysis/visible_sigmoid/fit.py fit
python analysis/visible_sigmoid/fit.py cv
python analysis/visible_sigmoid/make_report.py
```

Set OPENBLAS_NUM_THREADS=1 and OMP_NUM_THREADS=1. Cross-validation resumes from its
CSV; move it aside to rerun from scratch. Large local posterior/prior draws are
hashed but not published; they can be recreated by these commands. Source, input
and public-output hashes are in `manifest.json`; public results are bundled in
`visible_results.zip`.
