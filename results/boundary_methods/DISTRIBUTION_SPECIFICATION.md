# Positive RT distribution and dispersion boundary

This exploratory extension compares two features of the retained positive
audio–tactile hit distribution. Under a lognormal working model, the log
location is log median RT and the log scale is the logarithm of the
within-probe standard deviation of log RT. A changing log scale alters the
spacing of the fitted quantiles, including the upper tail. A midpoint in
either feature is an operational response boundary. It has no unique
mapping to a cognitive process. [RT distribution modelling](https://doi.org/10.3389/fpsyg.2015.01171)
and [parameter interpretation](https://doi.org/10.3758/PBR.16.5.798).

Use the fixed retained trial tensors, primary40 and the two single-exclusion
cohorts for group sensitivity. Use registered and trajectory axes. Log RT
is in seconds. Estimate log location by the log sample mean and log scale
by the bias-corrected log sample SD. The correction subtracts half the
mean log chi-square pivot, and the log-scale variance is one quarter of
its trigamma variance. The equal-person group target averages the
individual feature profiles. Its group covariance uses complete paired
participant vectors. A constant pooled tactile-only reference on either
feature translates that feature and leaves its fitted shape unchanged.
The same-label baseline is addressed separately in the original timing
analysis.

Project 95% absolute midpoint sets on the existing signed 121-by-42
logistic grid, including reference fits for constant, linear and log distance.
Use the existing t envelope for individual location, a simulated centered
log chi-square envelope for individual log scale, and the whole-person
Hotelling region for mean group contrasts. Combine phase feature values
with equal weights. Use 98.75% for each phase cell in the four-cell
contrast projection. Keep the complete grid, boundary-free alternatives
and conditional extrema. Report a bounded transition only when the set
lies inside the probed interval and all three reference profiles are
incompatible. Report both components; Bonferroni across the four phase
cells does not adjust across the two distribution features or two axes.

Leave out all retained AT hits at one probe per fold, with the original
cleaning fixed. Use the same weighted feature-profile estimator for the
flat, linear and log-distance reference families, and compare a logistic
location only, a logistic dispersion only and two independent logistic
profiles. Use equal-participant log density on held RTs, including the
change-of-variables term. The primary span cap is log(2) on each
component. Repeat with log(1.5) and log(3). These are predictive
regularizers. As a support sensitivity, shift the lognormal's lower bound
from 0 to a fixed 150 ms and refit both features. The second support bound
is an exploratory modelling choice and represents no estimated delay.
Positive-tail distribution scores concern
retained hits and do not describe omissions.

Use seed 20261124 and 96 synthetic primary40 cohorts per generator.
Preserve retained trial counts and subject-by-cell nuisance variation.
Generate flat features, a 0.18 log-location span with constant log scale,
and a 0.35 log-scale span with constant location. Derive the simulated
sampling distributions from independent normal sufficient statistics.
Set the four midpoint targets close to 55, 45, 65 and 60 cm on the
registered grid and compare individual location coverage, localization,
and condition-contrast error with matched group results. Retain the false
localization rates for the flat feature. This calibrates the working model
conditional on the released trimming and trial counts.
