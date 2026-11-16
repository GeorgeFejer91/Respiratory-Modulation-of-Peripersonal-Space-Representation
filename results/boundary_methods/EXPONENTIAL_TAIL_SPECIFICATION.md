# Exponentially tailed RT under a shared Gaussian core

This sensitivity distinguishes an additive exponential tail from a
Gaussian center in the retained positive hit distribution. The
ex-Gaussian quantities are descriptive response parameters.
[Parameter interpretation](https://doi.org/10.3758/PBR.16.5.798)

Use primary40, the registered distance axis and the original retained
trial counts. Condition the likelihood on positive RT. The Gaussian SD
is participant-specific and shared across cells and distances. The
Gaussian center and log tail mean each have a participant-by-cell level.
Compare four nested distance specifications with the same priors for
these levels.

| Model | Gaussian center | Log exponential tail mean |
|---|---|---|
| Flat | Constant | Constant |
| Linear tail | Constant | Linear distance |
| Tail boundary | Constant | Logistic distance |
| Center boundary | Logistic distance | Constant |

For boundary fits use one positive population width, four population
midpoint coefficients and noncentered participant variation in midpoint
intercept and condition. Amplitudes may be negative, zero or positive.
These are alternative exploratory decompositions. Allowing both
components independent shapes would add two latent transitions to each
five-probe cell. Per-probe trial counts can be as small as two. Report
which boundaries remain conditional on sharing these nuisance quantities.

Use seed 20261125, up to four chains and the same initial 1,500 tune and
draw counts and convergence gate as the other hierarchies. Allow a
single .99 diagnostic extension with 3,000 tune and 6,000 retained
draws for failed target fits. Keep all receipts. A pilot with fewer
draws verifies code and runtime separately.

For held prediction, refit on four probes and score each participant-by-cell
block of retained RTs on the fifth by posterior log predictive density.
Report probe-wise density and the count-weighted aggregate across the
five folds. In the shape fits report prior and posterior midpoint
in-range fractions, phase and paired condition effects, fitted span
and conditional credible intervals. A posterior location needs
support for component change and adequate held prediction.

Simulate a flat and an exponential-tail boundary generator with the
actual participant levels and trial counts. The boundary generator's
log-tail plateau difference is 0.75 with positive signed amplitude and its four
midpoints are 48, 45, 58 and 55 cm. The shape model shares a 15 cm
width in this generator. Fit both scenarios first as recovery examples,
checking conditional location and contrasts in the planted data.

## Implementation record

The shared log normalizer and the part of the log density linear in
RT can be summed within a participant, cell and probe. The normal CDF
of the shifted response is still evaluated for every retained trial.
The grouped implementation reproduced the original trial-wise
likelihood and gradients across eight tested parameter sets per
model. Its mean log density also matched the SciPy calculation at
an absolute tolerance of 5 × 10⁻⁸ and a relative tolerance of 10⁻⁸.
Both implementations evaluated the same model, and the receipts
identify each source version by SHA-256.

Independent queues can run separate probes in parallel. Each fit
locks its receipt path during sampling and publishes its JSON in a
single rename. If a second queue reaches the same fit, it checks
the saved settings and release input hashes before reusing the
receipt. A test with two worker processes verified one fit execution
and preservation of the result when a conflicting setting was submitted.

Run `exponential_tail_report.py` in the pinned sampling environment
to check coverage of the declared attempt grid. Its `--write` option
exports the inventory after all initial and required extended fits have
reported. The inventory keeps pilot and failed attempts and computes a
five-probe mean score for a model when all five probes qualified.
