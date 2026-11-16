# First detectable adjacent RT decrease

Hobeika et al. inferred group PPS extent from the first reliable RT
decrease when traversing adjacent sampled delays from far to near.
Their design included a simultaneous-delay comparison and used
Newman–Keuls tests. Study 5 has five positive nominal SOAs. This
adaptation uses directional paired tests with a Bonferroni allocation
across the four adjacent comparisons within each group profile.
[Hobeika et al. (2019), Results](https://pmc.ncbi.nlm.nih.gov/articles/PMC6731720/)

Use equal-participant means for every phase and for both equal-phase
condition profiles. Use the existing trial cleaning. Evaluate primary40
and the two recording-linkage variants, with raw AT and same-label
subtraction. Pooled Baseline subtracts a constant within a phase profile
and gives the same adjacent differences as raw AT. Treat nominal
same-label timing as unverified.

For each adjacent gap, compute each participant's farther-minus-nearer
mean RT and test the equal-person mean for a positive difference.
Inspect gaps from far to near and select the first with one-sided
adjusted p < .05. Retain every group difference, p value and two-sided
simultaneous comparison interval. The four tests form a within-profile
family. Comparisons across phases, cohorts and baseline variants are
exploratory. Report the selected gap on both nominal maps. A gap
selected by this rule describes a statistically detectable change
between probes.

Resample 999 whole participant profiles to quantify the stability
of selecting a particular gap, retaining a no-selection state.
For paired interpretation, retain whether both condition profiles
select the same gap, different gaps, or give a missing selection.
The paired change in the adjacent RT difference receives a
two-sided simultaneous interval across four gaps for each factorial
and simple contrast. This is a contrast in RT changes in milliseconds.
Repeat the rule with one probe omitted at a time. A skipped probe
can create a wider comparison interval. The fixed reference for
held RT prediction is the existing calibrated discrete step family.
[Step prediction and recovery](RESULTS.md#discrete-change-point)

Use 96 primary40 simulated cohorts per generator and baseline rule
by resampling centered whole participant profiles. The null profile
has zero group adjacent contrast. The step generators add a 40 or
120 ms transition between the second and third near-to-far probes
in Control, and between the third and fourth probes in Viscereality.
The locations are fixed across phases in each simulated condition.
Record each profile's frequency of selecting the correct gap,
the wrong gap or no gap. Record the frequency of jointly recovering
both equal-phase condition gaps.
