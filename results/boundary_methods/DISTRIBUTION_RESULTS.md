# Lognormal center and dispersion boundaries

The analysis used retained positive audio–tactile hit RTs. The log center
describes the median RT on a logarithmic scale. The log dispersion
describes the spacing of the fitted quantiles. The sensitivity changed
the distribution's lower bound from 0 to 150 ms. Both analyses used the
same hits and reported density on the original RT scale in seconds.
The distribution components are statistical features of RT.
[Specification](DISTRIBUTION_SPECIFICATION.md) · [RT distribution modelling](https://doi.org/10.3389/fpsyg.2015.01171)

## Observed support

Across 2,064 profile records, no log-center or group profile yielded a
bounded transition. Ten records showed a bounded dispersion transition.
They represent three participant cells whose fits were repeated across
support choices and axes. The table gives the compatibility sets on the
registered axis.

| Participant cell | Lower bound 0 ms | Lower bound 150 ms | Signed dispersion change |
|---|---|---|---|
| P004 Viscereality Inhale | 30.25–48.25 cm | 30.25–46.00 cm | Increase |
| P025 Control Inhale | 30.25–43.75 cm | 28.00–46.00 cm | Decrease |
| P006 Control Inhale | Unresolved | 39.25–46.00 cm | Decrease |

The trajectory axis gave the same three localization patterns in
different coordinates. The entries are exploratory cell-level sets.
Multiplicity across participants, components or axes was not controlled.
Of 9,632 contrast records, 4,816 remained unresolved and 4,816 fixed
midpoint differences at zero through the model constraint. None yielded
an empirically bounded condition, phase or interaction contrast.

## Held-probe prediction

The distance-constant distribution scored highest at both support
bounds, both axes and all three span caps. For the unshifted
registered-axis primary cap, the equal-person held log densities were
0.817 for constant, 0.758 for a logistic dispersion only, 0.756 for
linear, 0.720 for log distance, 0.446 for a logistic center only and
0.290 for separate logistic center and dispersion. At the 150 ms lower
bound they were 0.832 for constant and 0.778 for a logistic dispersion
only. Prediction tests used four training probes and the held trials
at the fifth. The dispersion candidates gave local descriptions in
some cells without improving out-of-probe prediction across the cohort.

## Recovery and limitations

The 96 cohorts per generator used the actual trial counts. The
simulated condition difference was +11.25 cm for each structured
feature. For known log-center shifts, the procedure localized 0.43%
of participant cells and 23.70% of group cells. For known log-dispersion
shifts it localized 0.35% and 2.60%, respectively. Conditional point
condition RMSEs were 47.82 and 10.54 cm for log center and 55.48 and
35.00 cm for log dispersion, at participant and group levels.
The generating shape was compatible in at least 98.17% of cases for
both features. In flat simulations, spurious localization was at most
0.21% of participant cells and 0.52% of group cells. These are
working-model fixed-design simulations. Sparse within-probe hits and
the adequacy cutoffs limit how often an identifiable transition
appears even with planted shapes.

The location and dispersion inference assumes independent Normal log
RT within a retained probe. The group procedure assumes independent
participant vectors. Earlier hit selection and trimming define the
estimand. An ex-Gaussian fit would distinguish an exponential tail
parameter from a lognormal dispersion parameter. Such a fit needs
additional nuisance sharing to estimate a separate tail curve when
some bins have only two hits.

[Profiles](distribution_profiles.csv) ·
[Contrasts](distribution_contrasts.csv) ·
[Predictions](distribution_prediction.csv) ·
[Estimates and hashes](distribution_results.json) ·
[Code](../../analysis/boundary_methods/distribution.py)
