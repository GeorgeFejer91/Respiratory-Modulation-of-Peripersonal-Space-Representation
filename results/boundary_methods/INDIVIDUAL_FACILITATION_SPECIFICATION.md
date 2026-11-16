# Farthest facilitated probe for an individual participant

This exploratory extension was specified on 2026-11-16 before examining
individual endpoint sets. The recovered planning proposal motivates a
separate sampled endpoint alongside a first group RT decrease. The [existing group test](FACILITATION_EDGE_SPECIFICATION.md)
gives a detection rule based on across-participant tests.
The individual estimand here is the farthest **sampled** probe with
strictly positive expected facilitation in one participant phase cell or
one equal-phase condition. It permits arbitrary shapes and an explicit
state for no facilitated probe. Finding the endpoint at the outermost
probe leaves extent beyond the measured range unresolved.

Use the current primary40 retained raw RTs. At each probe define
facilitation as Baseline minus Audio–Tactile mean RT. Use participant
and cell-specific pooled Baseline, nominal same-label Baseline, and
the two exact cue matches from the +500 ms sensitivity. Keep the same
physical probe index across the registered and trajectory maps. For
each profile use the [primitive mean uncertainty](THRESHOLD_SPECIFICATION.md)
with two-sided 95% Bonferroni bands over the available AT means and
distinct Baseline means. Include both phases in that allocation for
an equal-phase profile, averaging the phase-specific mean bounds.
The within-bin working model assumes independent Normal trial RTs.
Preserve unavailable variance when a required bin has fewer than two
retained trials. Missing outcomes and cohort eligibility use the
existing rules.

Project the primitive band into every compatible sampled endpoint.
With separate reference means, probe `j` is possible if the upper
facilitation bound at `j` is positive and each farther probe can have
nonpositive facilitation. With pooled Baseline, a single Baseline value
must work at all probes. The largest such value allowed by the farther
AT upper bounds and the Baseline upper bound must exceed the AT lower
bound at `j` and reach the Baseline lower bound. Retain the no-facilitation
state when all probes can have nonpositive facilitation under the same
reference. A set with one probe and no undefined state localizes the
sampled endpoint. For paired effects use the existing seven contrast
weights and the equal-phase condition difference, with 98.75% marginal
profile coverage before projection. Retain the possibility that a
contrast is undefined and report the finite contrast limits conditional
on a sampled endpoint in each active profile. The intervals protect
within-profile probes and the four components of each contrast. The
exploratory comparisons across people and reference choices are reported
without cross-person selection or a confirmatory claim.

Repeat the projection with one probe omitted and keep the pooled
reference fixed across omissions. The rule estimates an endpoint on
the observed probes. It has no predictive model at the omitted probe.
Use the existing [held-probe mean RT comparisons](THRESHOLD_RESULTS.md)
as complementary evidence for interpolation on the five-probe designs.
Use seed 20261208 and 96 working-model simulated datasets each for
zero, constant +120 ms, and +40 and +120 ms through the second nearest
Control probe and the third nearest Viscereality probe. Preserve
participant-phase trial counts, estimated sampling variances and
the shared reference structure. Use Normal mean and chi-square variance
sampling from [the existing recovery approach](THRESHOLD_SPECIFICATION.md).
Apply exact cue matching to the same planted probe values. Record state
coverage, unique correct and incorrect localization, and widths and
undefined states for the paired effects. Verify the shared-Baseline
projection against an independent feasibility calculation.
