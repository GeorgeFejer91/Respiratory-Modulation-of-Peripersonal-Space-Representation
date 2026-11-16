# Reduced hierarchical midpoint models

This exploratory family extends the existing joint trial likelihoods. The
published full hierarchy uses four fixed and four participant-varying
coefficients for midpoint and log-width. Change only the shape hierarchy
first. This isolates the effect of stronger sharing on boundary recovery.
Use primary40 and the registered distance axis. Preserve the phase,
condition and interaction fixed midpoint effects in every model.

| Shape model | Participant location effects allowed to vary | Width |
|---|---|---|
| Full benchmark | Intercept, condition, phase and interaction | Full factorial hierarchy |
| Shared width | Intercept, condition, phase and interaction | One population width |
| Reduced condition | Intercept and condition | One population width |
| Reduced condition and width | Intercept and condition | A participant width shared across cells |
| Shared participant contrasts | Intercept | One population width |
| Shared location sensitivity | Intercept only and no fixed midpoint contrasts | Full factorial hierarchy |

The shared-participant-contrasts model imposes equal within-person
condition and phase contrasts across people. Reduced-condition models
permit between-person condition contrast variation. Both impose equal
phase and interaction contrasts across people. Summarize the population
effects, between-person variation, conditional individual shapes and
equal-person group response profile separately.

Reuse the signed Gaussian marginal baseline model with independent
nuisance priors and conditioned AT and Baseline trial likelihoods.
Compare baseline data included as calibrated, omitted from the AT
intercept, and nominally delay-matched where timing is unverified.
Use the same nuisance hierarchy for the direct pooled versus
same-label comparison. The no-Baseline fit retains the independent
offset prior and omits the tactile-only observations.
Use the preexisting positive-amplitude analysis for the direct no-time
versus linear session-time comparison, preserving the same trial eligibility
and shape. Keep analogous flat, linear and log-distance benchmarks.
Use `pm.do` to substitute narrower latent shape expressions into the
existing likelihoods. Verify log probability and shape transformations
independently. [PyMC model transformation](https://www.pymc.io/projects/docs/en/latest/api/model/generated/pymc.model.transform.do.html)

Check a matched prior-width sensitivity at scales .5 and 2 for the
location and width priors around the existing priors. Compare posterior
mass within measured distance bounds, compatible boundary-free
responses, observed span, held-distance trial density and RMSE, and
participant, condition and phase recovery. Include zero-amplitude
generators and strong transitions with common or heterogeneous width
and known condition effects. Retain the imposed equalities in all
participant result labels. Posterior concentration under strong sharing
does not itself establish a transition.

Use seed 20261121 and four chains with 1,500 warmup and 1,500 retained
draws initially. Fixed quantities are checked before interpreting
posterior summaries. Use the original trial-time normalization in
the linear session-time sensitivity. Its held probes use the parent
procedure of removing the held AT probe before cleaning and scoring
against eligible held trials.
Report rank-normalized R-hat, bulk and tail ESS, divergences and
posterior-predictive checks. Use the parent fixed diagnostics
(R-hat ≤1.01, bulk and tail ESS ≥400 and zero divergences for target
parameters). Reserve reduced-draw warmup only for runtime testing,
and keep failed diagnostics as evidence. For the pooled/same-label
explicit joint models and the positive no-time/time comparison,
allow one diagnostic extension to 3,000 warmup and 6,000 retained
draws with target acceptance .99. Keep the failed initial runs.
Refit on five held-distance
folds. Begin with the native signed likelihood and test the two reduced
condition variants against it before the time, baseline and prior
sensitivity expansion.

The matched registered-axis predictive comparison refits all five
shape structures and the three boundary-free references at all five
probe deletions. Use an identical signed Gaussian marginal
likelihood, offset prior and per-participant scale across the eight
models. The references use a constant basis, centered distance,
or centered log distance. Per-distance scores are held-trial log
predictive density and RMSE of the unsmoothed held response. Average
log scores with held-trial counts as weights. Combine RMSE across
the five equally weighted probes. These fits use fixed cleaning.

The additional shared-location sensitivity fits the observed trials and
the same five held probes while preserving factorial widths and sharing
one midpoint within each participant. In this model, all within-person
midpoint shifts are zero by construction. The diagnostic gate evaluates
the stochastic midpoint, width and corrected curve. Compare prediction
to assess width variation as an alternative to a changing boundary.

Keep a latent midpoint separate from the maximum positive slope of
an aggregated expected response. Compute draws for four phase-specific
group profiles and both equal-phase condition profiles. The latter
average phase curves before taking the derivative. For the aggregate
peak, require one interior maximum of the derivative, nonnegative
derivative throughout the design and derivative below half peak at
both design endpoints. Evaluate in 0.5 cm increments and report the
frequency of meeting this definition at across-design RT shifts of
0, 20 and 40 ms. These target values test sensitivity to the minimum
visible shift and have no clinical interpretation. Also record the
model-conditional credible intervals for participant phase midpoints
and their equal-phase averages. The average of latent midpoints is
a different estimand from the peak of an equal-phase response.

## First signed-fit checkpoint

All five observed-data signed models completed four chains at the
initial draw count, with zero divergences and the target diagnostic
gate passed. The median population condition effect ranged from
−4.56 to −2.94 cm across the four reductions. Every 95% interval
spanned zero. For reduced condition and participant width the
interval was −79.27 to +73.84 cm. For the full model it was −83.46
to +76.79 cm. The reduced model's posterior probability of an
individual cell midpoint within 10–100 cm averaged 56.4%, compared
with 51.2% under its shape prior. Independent likelihood comparisons
verified all four graph reductions at matched parameter vectors.

The first matching-generator fit used the reduced-condition model,
a common 15 cm width and a 200 ms total amplitude. It recovered the
true +10 cm population condition shift with a posterior median of
+6.94 cm and interval of +2.87 to +11.10 cm. Participant midpoint
RMSE was 7.63 cm, and 88.1% of individual midpoint intervals
contained their generating value. These are observations from one
synthetic cohort. Held probes, additional recovery and calibration
fits remain necessary.

## Prior, aggregation and timing checkpoint

### Repeated recovery comparison

Use four matched synthetic cohorts per generator, indexed 0–3, for the
two reduced-condition fits with population or participant width. Reuse
the existing seed-0 receipts. The generators are flat, 40 ms full
response amplitude with shared 15 cm width, and 200 ms amplitude with
shared or heterogeneous widths. Both shared-width generators retain
fixed phase and interaction contrasts. The nonflat generators set
the population condition, phase and interaction midpoint shifts to
+10, −10 and +15 cm. The designated weak generator reduces the
observable response span and retains the midpoint contrast. Record
target diagnostic pass counts, conditional midpoint interval inclusion,
participant and contrast RMSE, population interval inclusion and
aggregate peak qualification under the same rule as the observed
fits. Report descriptive fixed-seed recovery frequencies alongside
denominators. Exempt failed runs from numerical summaries of qualified
fits and retain them in the run inventory. Use every tenth draw
within each chain for simulated aggregate peak fractions. All
observed peak fractions and recovery interval summaries use all draws.

The model with participant width gave population condition intervals
of −44.10 to +40.59 cm, −79.27 to +73.84 cm, and −123.81 to +112.89 cm
at prior scales .5, 1 and 2. All three passed diagnostics. In the
6,000 posterior draws for each primary signed model, no draw met
the peak criteria in both condition-average curves even with a
minimum response span of zero. Analytic aggregate derivatives
agreed with finite differences.

The longer positive-amplitude fits passed the target gate. The
condition intervals were −47.34 to +46.12 cm without session time
and −47.77 to +47.26 cm with a linear session-time term. The
explicit pooled and same-label calibration fits failed the
shape gate even after the diagnostic extension. Before interpretation,
compare the remaining held-distance models and report the calibrated
and numerically unresolved fits separately.
