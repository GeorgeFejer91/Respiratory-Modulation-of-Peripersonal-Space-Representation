# Boundary method audit, first numerical batch

Exploratory specification fixed 2026-11-16 after earlier Study 5 results and
before calculating the estimates below. The [literature audit](../../literature_review/BOUNDARY_METHOD_AUDIT.md)
records which analysis families are already covered and what remains.

Use the fixed retained hit trials and primary40 cohort, excluding the two
unresolved linked recordings. Use five nominal registered distances and the
documented trajectory as separate coordinate sensitivities. Within each
participant, retain both conditions and both phases. Also compute each
condition's equal-phase profile. For condition and phase summaries at the
cohort level, estimate the location of the equal-person profile separately
from the mean of individual locations. Each summary must say which it uses.

1. [Ferroni et al. (2026)](https://doi.org/10.1016/j.neuropsychologia.2026.109490)
   supplementary MATLAB examples (mmc3 and mmc4) support a PPS-specific
   Spearman–Kärber calculation from per-location trimmed mean AT latencies.
   Trim 10% total per location, rounding 5% to the nearest whole observation
   per tail. Sort by increasing distance, orient toward slower far RTs, and
   give each distance equal weight, as in the equal-count authors' example.
   After min–max scaling, apply weighted least-squares monotonic regression
   with equal weights. Pad one adjacent interval at each end, integrate the
   step masses as uniform within each interval, and report their centroid,
   difference limen and tail mass. Use untransformed RTs, with pooled baseline
   subtraction as an invariance check. Same-label correction is a separately
   labelled timing-unverified sensitivity for follow-up. A zero-range or fully
   pooled profile has no location in this audit. The centroid describes the
   implied transition distribution and may differ from its median or the
   observed half-range crossing. The authors' example fixes a displayed
   response range, and a finite result alone does not identify a boundary.
2. [Ferri et al. (2015)](https://doi.org/10.1523/JNEUROSCI.1696-15.2015)
   fitted the fixed-extrema sigmoid to mean natural-log RT at the same five
   SOAs. Fit this response scale using the established Study 5 grid and tie
   policy on the SOA axis, alongside the identical model using arithmetic
   means. Keep the established cleaning and all fits. Label active width or
   midpoint bounds and outside-range estimates. Do not transfer the source's
   stationary-sound comparison, trimming rule or fit-selected sample. Use ms
   for the estimated SOA and only map in-range estimates to nominal cm.

Use five held-SOA folds and a training mean comparator on the same target for
each response scale. As Spearman–Kärber is a location summary, evaluate its
underlying RT projection separately, with linear interpolation between
monotone training values and constant extrapolation. The fixed gate remains
unchanged. All folds condition on the existing cleaning, which can use trials
from the held SOA. These are within-person predictions, not prospective
recruitment validation.

For Spearman–Kärber, use 999 within-bin participant bootstrap draws and 999
paired whole-participant draws for mean profiles. Report availability and
conditional 95% percentile ranges side by side. Compare odd/even within-bin
split estimates using Spearman correlation over observed pairs, as a
descriptive within-session stability check. Simulate 256 replicates per
scenario, using retained trial counts and within-bin RT SDs. Generate flat,
80-ms step and 160-ms step profiles, the latter two jumping between the
second and third registered positions. Report availability and recovery
relative to the gap midpoint. Within-bin resampling and simulations assume
independent trial errors conditional on the matched samples. Phase and
condition differences are paired; keep non-estimates and show complete-pair
counts. Report every result without using direction or significance to select
the analysis.

The first batch screens alternative summaries and predictive adequacy. Log
RT confidence sets, selection-aware change-point uncertainty, repeated
effect recovery, and the archive's conditional local-only source checks
are separate pending tasks. Pooling, interpolation, normalized RT
distributions and fit quality do not resolve the alias between foreperiod
and nominal spatial distance.
