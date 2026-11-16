# Boundaries of recorded tactile outcomes

The primary 40 participants provided 9,588 observed audio–tactile
trials and 4,793 tactile-only trials. Of these, 801 and 443 were
recorded as misses, respectively. Another 80 and 25 trials were
hits with an unavailable latency. The response analysis uses every
observed tactile trial. It covers the probability of a miss and
the probability of a miss or a hit slower than 400, 600 or 800 ms.
For the time-based outcomes, both allocations of unknown hit
latencies contribute to the uncertainty sets. [Specification](RESPONSE_SPECIFICATION.md)

## Observed boundaries and held distances

None of the 4,128 estimated profiles or 5,504 paired contrasts
localized a boundary under monotonicity. These counts include repeated
analyses of the same trials. For every primary phase-specific
participant profile and every primary group phase and condition
profile, the monotone half response remained compatible with the
entire measured range for each endpoint under the pooled-Baseline
definition. Constant adverse probability was also compatible.
The result held across both distance assignments and the timing-unverified
same-label Baseline sensitivity.

For the registered-axis miss outcome, the flat model gave the
lowest held-distance RMSE. Error was 8.43 percentage points for
individual profiles and 1.11 points for the equal-person group.
For the miss-or-slow outcome at 600 ms, the isotonic predictor
gave 2.28 points at group level under either allocation of unknown
latencies, compared with 3.42 and 3.57 for the flat predictor.
The flat predictor gave slightly lower individual errors on that
outcome. The improvement for the average group profile left the
half-response location unresolved.

## Recovery and interpretation

The simulated 20-percentage-point transition had an average
condition shift of 13.14 cm. The procedure localized 86.1% of group
profiles under that generator. For all 96 repetitions the joint
condition envelope contained the shift, with both localization and
coverage in 7.3%. Every simulated participant location set remained
unlocalized under that generator. The flat generator produced no
false localizations. Joint state coverage was 100% in these draws;
the intervals were broad by construction under the fixed design.

These results assess recorded tactile outcomes alongside the
existing analyses of RT conditional on a recorded hit. The timing
of a missed or unrecorded response is unknown. A source-specific
click-detection window, if recovered, would be needed to justify
any right-censored latency analysis. The [acquisition and
classification methods](../../manuscript/sections/methods.tex)
describe the different RT provenance across versions.

[Profiles](response_threshold_profiles.csv) ·
[Contrasts](response_threshold_contrasts.csv) ·
[Simulations and hashes](response_threshold_results.json) ·
[Code](../../analysis/boundary_methods/response_boundary.py)
