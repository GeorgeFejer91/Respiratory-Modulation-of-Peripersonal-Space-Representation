# Publication-focused sigmoid analysis choice

## Decision and goal

Use **one hierarchical Bayesian logistic model**, with partial pooling across people
and a continuous response across the five SOA-mapped distances, to describe four
curves per participant. The selected existing exploratory estimator is
`joint_logistic_marginal`; the cell-noise `joint_logistic_heterogeneous` fit is its retained
sensitivity. This is a choice after seeing results, not a newly confirmed primary
analysis or evidence that this specification predicts best. No new effect test,
cleaning change, bandwidth search, prior restriction or curve fitting occurred here.

The goal is a reproducible, publication-defensible estimate and comparison of
midpoint and sharpness in every retained participant × condition × phase cell,
with uncertainty and explicit identification limits. Across-person smoothing is
hierarchical partial pooling, not averaging adjacent participant IDs. Across-SOA
smoothing is the continuous logistic likelihood, not repeated filtering until a
desired shape or p value appears. The model uses original AT and Baseline trials
jointly and propagates shared baseline uncertainty.

## Why this choice

It supplies **160 finite curves for all 40 retained participants**, preserves all
four cells and signed amplitudes, and passes convergence checks: zero divergences,
maximum Rhat 1.0019, minimum bulk ESS 2111 and
minimum tail ESS 2360. Independent nuisance integration avoids
the unresolved mixing problems in the initial hierarchical-nuisance model. It has
the same shape hierarchy, but different intercept/amplitude pooling assumptions.
Cell-varying residual noise remains a sensitivity, not another replication.

The scientific rationale is theory-motivated sigmoid estimation with partial
pooling, checked by prediction, identifiability and recovery. See the existing
[PPS methods rationale](../../literature_review/ANALYSIS_RATIONALE.md) and
[individual-parameter review](../../literature_review/INDIVIDUAL_PARAMETERS.md).
Canzoneri et al. (2012), doi:10.1371/journal.pone.0044306, supplies a PPS sigmoid
precedent, not justification for forced individual shapes. Ahn et al. (2011),
doi:10.1037/a0020684, motivates partial pooling through recovery in another task;
it does not validate this model. Hedge et al. (2018),
doi:10.3758/s13428-017-0935-1, motivates checking individual reliability.
This package uses the already accessed evidence; it is not a new literature search.

## What the smoothing actually supplies

The marginal-median midpoint estimates span **62.9–84.0 cm**.
Their median 95% interval width is **245.0 cm**;
**0/160** intervals lie wholly
inside the measured 10–100 cm range. Only **4/160**
amplitude intervals exclude zero. Finite values are model-based approximations,
not established individual physiological boundaries. These identification counts
use all retained draws; the earlier predictive-check summary used thinned draws
and therefore has slightly different approximate counts and interval widths.

The fitted 10–90% transition width is **418 cm** at
the median, versus a **90 cm** sampled range. **0/160**
plug-in curves show both 10% and 90% levels inside that range. This is why the
measured-range plots look nearly linear even though their mathematical functions
are sigmoids. Stronger kernel smoothing alone usually removes curvature; a narrow
visible S would additionally require a shape/width assumption that these
observations have not established. A prior centred on zero effects is not a
constraint that effects must be zero.

`individual_sigmoids.pdf` includes every participant. Its top row shows unsmoothed
data, a plug-in logistic and posterior expected-response uncertainty on the measured
range. The bottom row shows each fitted sigmoid on its standardized coordinate
with the measured segment shaded. It makes the complete S visible **by definition**;
its unmeasured bends are explicitly model extrapolation. This row is a methodological
illustration, not a figure establishing a physiological transition. No observed
RT was clipped, normalized by an unstable amplitude, or altered. Plug-in curves use
marginal medians and are not claimed to be a joint MAP or an individually validated
best curve. Response ribbons use 1,000 balanced draws; parameter intervals use all
12,000 retained draws. Ribbons are conditional on the stated model.

## Statistical comparison across the four cells

Use **joint posterior paired contrasts**, carrying parameter uncertainty and shared
pooling through the analysis. Condition = Viscereality − Control, Phase = Inhale −
Exhale, interaction = difference of phase differences. The main finite-cohort
contrasts and 95% credible intervals are:

| quantity | effect | posterior_median | ci_low | ci_high |
| --- | --- | --- | --- | --- |
| midpoint_cm | Condition | -3.325 | -83.35 | 76.11 |
| midpoint_cm | Phase | -5.552 | -87.09 | 71.73 |
| midpoint_cm | Condition × Phase | -7.334 | -90.59 | 79.69 |
| sharpness_per_cm | Condition | 0.0003947 | -0.002911 | 0.00422 |
| sharpness_per_cm | Phase | -0.0005172 | -0.004517 | 0.002722 |
| sharpness_per_cm | Condition × Phase | 0.0004381 | -0.005473 | 0.004709 |

All intervals include zero. `joint_parameter_contrasts.csv` retains all main and
simple contrasts from both converged variants. A conventional RM ANOVA on smoothed
or pooled point estimates treats shared estimates as independent measurements and
omits fit uncertainty. The earlier zero-population-effect simulation produced
six nominally significant point-median tests; those are not suitable evidence for
choosing this analysis. Their full outputs remain in the original batch.

## Which result belongs at the front

For the PPS question, lead with the **uncertainty of the boundary/sharpness
estimates and the absence of a clearly supported condition or phase difference**,
not a selected smoothing-dependent p value. The group-level positive result that
is easiest to defend is **AT − Baseline = −18.65 ms**, 95% CI [−27.26, −10.04],
unadjusted paired p = .0000865. This establishes overall RT facilitation under the
specified baseline matching; it does not locate a PPS boundary.

If discussing the experimental interaction, the clearest exploratory candidate
is the **Student-t linear RT model**: Condition × Phase = −17.82 ms,
95% credible interval [−32.82, −2.98]. Its log-distance counterpart agrees, but
Gaussian population models and the primary paired test (p = .119) do not establish
it. Present the likelihood sensitivity next to the result. This is an RT-location
interaction, not evidence of a boundary or sharpness change, and was found after
a broad method search. The nominal heavily smoothed sharpness p = .0336 is less
defensible as the lead: its refit interval crosses zero and deletion sensitivity
can raise p above .05. All p values remain unadjusted as requested.

## Publication status and limits

The approximation and its inconclusive parameter comparison are reportable as an
exploratory analysis with these disclosures. **A significant PPS boundary or
sharpness finding is not currently supported.** Publication acceptance cannot be
guaranteed by smoothing. The trial likelihood, priors and participant hierarchy
remain assumptions; convergence is not validation. The existing held-distance
comparison used a different nuisance-pooling model and favored no sigmoid over a
line; the selected marginalized variant has not had a separate cross-validation
or repeated-simulation coverage study. Its pooled-baseline predictive discrepancy
and unverified baseline-label timing remain unresolved.

P011/P033 remain excluded together because their recording-to-person mapping is
unresolved; this choice supplies every *retained* person's estimates, not 42
independent records. Questionnaire analyses were not repeated. Native execution
only; Pages and manuscript assets are unchanged. Reproduce with
`python analysis/publication_sigmoid_choice.py` after the native joint runs in
`analysis/baseline_effects/README.md`. Large posterior draws stay local and are
recreated by those commands; the public curve/parameter tables remain sufficient
to inspect the delivered plots. See the [full original batch](../baseline_effects/RESULTS.md).
