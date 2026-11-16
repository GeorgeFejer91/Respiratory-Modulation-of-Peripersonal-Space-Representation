# Shared transition in recorded misses and hit latency

This exploratory model asks whether the recorded miss sequence adds
location information to the retained hit latencies when both can
change around the same distance. A miss contributes its observed
binary outcome. It has no imputed event time. The separate outcomes
are motivated by work on [joint response and latency models](https://doi.org/10.3389/fpsyg.2018.01525).
The present likelihood conditions latency on an observed hit with a
retained RT. It models recorded responses under the Study 5 trial
pipeline, with no interpretation as a latent decision process.

## Data and estimands

Use the audited Audio–Tactile trials, existing exclusions, and the
40-record primary cohort. The binomial component uses every observed
miss and hit, including hits without a retained latency. The latency
component uses the existing cleaned positive times, in log seconds.
Baseline timing at a matching nominal delay is uncertain. A pooled
cell constant is absorbed by the outcome levels. Compare the two
distance maps and the two existing linkage sensitivities that retain
one additional participant record. Results use the recorded outcome
denominators and the actual retained latency counts.

Fit a midpoint and width to each participant-by-condition-by-phase
cell. A separate group fit pools shape across participants within each
phase cell, with participant-specific outcome levels and amplitudes.
It estimates shared phase locations in the recorded sample. The aggregate
derivative peak examined in the earlier hierarchy uses the predicted
average group curve, a distinct estimand. Average the two latent phase midpoints for each condition and
report paired condition, phase and interaction contrasts, including
the established four simple contrasts. Credible intervals condition
on the model and sampled participants. Null and known-shape recovery
check their behavior under the working independent-trial likelihood.

## Models and uncertainty

For a sigmoid transition, let `q(x) = sigmoid((x - m)/w)` on the
measured range scaled to 0–1. Miss probability is
`(1-q)p_near + q p_far`, with independent Beta(1,9) endpoint priors.
Log latency has an intercept and slope on `q-0.5`. Give residual
variance an inverse-Gamma(4, 0.0675) prior in squared log seconds.
Conditional on the variance, the intercept and slope are independent
normal with means log(0.55) and zero and variances four times and one
times the residual variance. The free endpoint difference and latency
slope allow zero or either sign of change.

Compare five families. The boundary-free family mixes flat, linear and
log-distance bases independently in each component. In the flat
binomial reference, the a priori single rate has the same Beta prior.
Linear and log-distance bases are normalized across the five probes.
The other families give only latency, only miss probability, both with
separate shapes, or both with a shared shape a sigmoid. Assign equal
prior mass to the five families as a descriptive evidence comparison.
This distinguishes the shared-location assumption from an improvement
that is already available to one component. An optional prior
sensitivity gives the miss endpoints Beta(2,18).

Use uniform discrete mass on the scaled midpoint grid −0.6 to 1.6
in 0.05 steps and on widths 0.06, 0.09, 0.135, 0.20, 0.30, 0.45 and
0.675. Expand midpoint support to −1.2 to 2.2 as a sensitivity. For
each cell and group, retain conditional 95% equal-tail midpoint and
contrast intervals, in-range mass, prior mass, and posterior family
weights. Summarize how often both ends of the interval are strictly
within the measurement range. These are descriptive checks across
many cells. A conditional interval alone cannot establish an effect.

Use Gaussian conjugacy and Gauss–Jacobi quadrature for the two
components. The Bernoulli product is a polynomial separately in the
endpoint probabilities, of degree at most the total trial count in
the cell. Use enough nodes for that degree and verify the flat
binomial and Gaussian integrations against independent formulas.

## Held probes and matched recovery

Score the joint density of held recorded outcomes and available log
latencies by subtracting the training from the full-data marginal log
likelihood. This is an exact held-block score under each working model.
Hold out all observations at each probe in turn and divide pooled
scores by the number of Audio–Tactile observation rows scored. Compute
separate scores for the per-person and shared group fits. Model families
at the held probes use the same priors as their training fits. Held
latency scores use the fixed released analysis mask, including its
original cross-probe trimming.

Use 32 seed-controlled replicates of each generator on the registered
axis. Under flat, both components are distance-constant. Under the
two nonflat generators the four phase midpoints are 0.40, 0.45, 0.55
and 0.60, width 0.135, and log-RT amplitude 0.16. Miss probability either
follows the same sigmoid with a 0.14 change or stays flat. Simulate
participant levels and conditional latency retention at the observed
trial counts. Evaluate midpoint and paired-effect interval inclusion,
RMSE and joint-model selection. The recovery checks apply to these
declared signal sizes and working sampling assumptions.
