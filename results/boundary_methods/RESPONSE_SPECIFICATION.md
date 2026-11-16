# Outcome-based boundary sensitivity

Study 5 records a tactile hit or miss on each observed Audio–Tactile
and Baseline trial. On the public release, all primary40 misses lack
an RT, while 80 Audio–Tactile and 25 Baseline hits lack an RT. Use a
two-part observed-outcome analysis, with the existing conditional RT
results for the latency component and these direct outcomes for the
response component. A miss may be an omission or a failure to detect
a click in the recording. A shared right-censoring time could not be
established from the public Methods or the companion source inventory.
Eight-second stimulus files and RT analysis cutoffs serve different
purposes. Do not supply a latent latency for a miss or missing RT.

Analyze miss probability and the probability of a miss or a hit
slower than 400, 600 or 800 ms. The latter is a joint recorded
response-speed estimand, with interval-valued counts for hits lacking
RT. Report the hit definition separately. Code a known slow hit or
miss as adverse and a known hit at or below the threshold as favorable.
The lower event count assigns all unknown hit latencies to favorable
and the upper count assigns all to adverse. The latency thresholds
sample near the center and flanks of the response-time distribution.
They are exploratory and do not define a clinical cutoff.

Use the observed denominator and the released participant, condition,
scheduled phase and nominal SOA. Maintain primary40 and both distance
mappings. Use raw AT proportions for the pooled-Baseline half response,
because subtracting a pooled cell constant leaves its location
unchanged. Repeat on AT minus Baseline at matched nominal labels as a
timing-unverified sensitivity. Also run the alternate linkage cohorts
for the group, using equal-person means.

For individual phase cells project simultaneous 95% Clopper–Pearson
rectangles from the lower and upper event counts. At group level use
whole-participant t marginal intervals and the same Bonferroni
allocation. Propagate the intervals through equal-phase averaging
and same-label AT minus Baseline. Group comparisons do not use
trial-level independence. Individual binomial intervals condition on
independent trials within each retained design bin. Use a 98.75%
marginal rectangle when projecting the paired four-cell contrasts.
Apply the monotone partial-identification routine to adverse
probability increasing with distance. Allow any continuous monotone
curve and report empty, full and unresolved sets. These are boundaries
of recorded outcomes under a monotonicity restriction.

Compare flat, linear, log-distance and isotonic predictions on the
five held probes for raw AT adverse probabilities. Repeat on the two
recorded endpoint codings for missing RT. For 96 whole-cohort
simulations per generator, match observed AT denominators. Use a
flat 8% adverse rate, an increasing line from 4% to 19%, and a
logistic 20 percentage point transition with four known location
centers and variation in person intercept. Retain the identity of
the paired condition estimand and report localization, coverage and
state recovery under the working independent-bin generators.
