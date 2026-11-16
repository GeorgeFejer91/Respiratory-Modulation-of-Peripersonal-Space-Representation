# Sensitivity to the source-observed tactile timing offset

Source recordings documented Audio–Tactile tactile cues 500 ms
later in the absolute trial than nominally equal-delay Baseline
cues in 15 cleared sessions. The public release supplies SOA
labels and lacks the mapping needed to identify those sessions.
Apply +500 ms to the Audio–Tactile cue time as a working sensitivity
in primary40. This does not assert that the other 25 sessions used
that offset. [Source timing methods](../../manuscript/sections/methods.tex)

Audio–Tactile nominal SOA (s) shares absolute trial time with
tactile-only nominal delay (s+500) under this convention.
The exact pairs are 300→800 and 2200→2700 ms. They support a
finite paired endpoint difference and no free midpoint. Retain
both pairs and report the participant and paired group endpoint
contrasts in milliseconds. A two-point effect can be represented
by a line or arbitrarily many sigmoids with a free level and span.

As a second sensitivity, linearly interpolate tactile-only expected
RT between adjacent measured labels. Keep Audio–Tactile SOAs
300, 800, 1500, and 2200 ms. The 2700 ms probe maps to 3200 ms and
requires Baseline extrapolation, so omit it. Propagate the shared
variance introduced when interpolated probes reuse a tactile-only
mean. Project the signed logistic midpoint with both distance axes
and the same flat, linear and log-distance references as the primary
profiles. Require an entirely within-probe compatibility set and
exclude boundary-free competitors before calling a midpoint localized.
Compare four held-probe folds with a ±160 ms fitted-span cap and
run 96 whole-cohort matched-covariance means simulations for a flat
and a strong 160 ms transition. The interpolation is a model for
tactile-only expected RT. It cannot provide verified cue matching.
