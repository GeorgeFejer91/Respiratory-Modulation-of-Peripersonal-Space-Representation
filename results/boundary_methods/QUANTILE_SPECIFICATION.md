# Distributional boundary screen

Fixed 2026-11-16 after the arithmetic-mean screen and before the quantile fits.
[Amiel et al. (2026)](https://doi.org/10.1016/j.cortex.2025.11.015), §3.2.2.2,
compare RT percentile profiles across looming and stationary sounds. Study 5
lacks that comparison, so use the distributional idea with a reduced set of
quartiles (.25, .50, .75) because each participant has few retained trials
per distance. Preserve the original RT cleaning, five SOAs, primary40 and
all four repeated cells. Treat equal-phase condition profiles as averages
of phase-specific quantiles. Equal-person group profiles likewise average
individual quantiles. Neither corresponds to quantiles of pooled trials.

Within bins, use linear empirical quantiles and estimate their variance
from 499 fixed within-bin resamples. Use the trial-mean discrete model
compatibility machinery on the quantile profiles with the estimated
quantile variances. Keep flat, linear and log-distance candidates.
Report all six group profiles and both distance mappings for each
quantile. Count missing and zero-variance profiles if they occur.
Use the same five held-distance predictions, targeting the corresponding
observed quartile and training on the other four. Compare RMSE within,
never across, quantiles. Quantile estimates depend on the sample sizes
and retention rule, and the approximate model compatibility decision
does not control multiplicity across the quantiles.

Run 256 simulations each for flat, an 80-ms linear trend, and positive
80-ms and 160-ms steps across the second/third positions. Match Study 5's trial counts and
use a common retained RT SD within each participant and cell so the
generating quantiles have the same prescribed spatial shape. Simulate
Gaussian quantile summaries using the first-order quantile sampling variance
under normal RTs. Counts
of correct gap declarations are diagnostic under that approximation.
This procedure does not test an auditory/tactile race model and does
not impute outcomes for nonresponses or missing RT.
