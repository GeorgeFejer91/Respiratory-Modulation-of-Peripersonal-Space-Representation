# Farthest detectable tactile facilitation

This exploratory analysis tests for the farthest sampled distance at
which sound speeds tactile responses relative to tactile-only Baseline.
It uses the established Study 5 cleaning and the same three recording
linkage cohorts. Each participant contributes a vector of differences
between their mean Baseline and audiotactile RTs. Positive values
indicate facilitation. The main cohort is primary40. Compute four
condition-by-phase profiles and two equal-phase condition profiles.

- **Pooled log RT.** Teraoka et al. pooled Baseline over tactile timings
  and applied one-sample signed-rank tests with Holm adjustment. Use
  mean natural-log RT in each trial set and repeat on nominal same-label
  and offset-matched Baseline. Apply two-sided signed-rank tests with
  the asymptotic reference distribution, using midranks for ties and
  dropping zero differences. A qualifying probe must have a positive
  signed-rank direction and adjusted p < .05.
  [Teraoka et al. (2024), Data analysis](https://muroran-it.repo.nii.ac.jp/record/2000223/files/Comparison%20of%20peripersonal%20space%20in%20front%20and%20rear%20spaces.pdf)
- **Nominal matched-label mean RT.** Rahmani et al. combine adjusted
  paired comparisons with Bayesian evidence at each sampled interval.
  The paper describes paired t and signed-rank tests in the same method
  account. This implementation specifies two-sided paired t tests and the
  existing two-sided JZS paired t Bayes factor with Cauchy scale √0.5.
  A qualifying probe must have a positive mean, Bonferroni-adjusted
  p < .05 and BF₁₀ ≥ 3. Report an observed stronger-evidence sensitivity
  at BF₁₀ > 10. Repeat on pooled and offset-matched raw RT.
  [Rahmani et al. (2025), §§2.5–3.1](https://dael.euracoustics.org/confs/fa2025/data/articles/000866.pdf)

The comparison family is the available probes of one group profile.
Report every observed effect and adjusted p value. Across five probes,
the farthest qualifying probe can have a nearer probe that fails.
Retain this pattern and whether the qualifying span touches the outer
sampled edge. With no qualifying probe, record no selection. A sampled
edge specifies a detectability rule. A continuous transition, the absence
of facilitation at farther distances, and a shift within a gap require
additional evidence. A condition difference in detectability alone is
insufficient to identify a condition difference in the location.

The two nominal same-label calculations assume comparability of labels.
The offset sensitivity applies +500 ms to the sample as a working
assumption and uses only the 27 and 100 cm registered probes with exact
AT-to-Baseline matches. Use both nominal distance maps when recording a
selected probe. The waveform subset lacks a public crosswalk.
[Timing evidence](CUE_TIME_RESULTS.md)

Use 999 paired whole-participant bootstrap replicates for each series.
Keep counts for all selected probes and no selection, plus concordance
of conditions within phase and after equal-phase averaging. Report
two-sided simultaneous t intervals across probes for the group mean
of participants' RT differences and each of the seven paired factorial
contrasts.
These are arithmetic mean differences in ms or mean-log differences.
For signed-rank results report the median and retain the distinct target
of the mean intervals. Reapply the rules with one probe omitted, including
both two-probe omissions in the offset sensitivity. The rule supplies
no prediction at an omitted probe. Use existing
[held-probe mean RT comparisons](THRESHOLD_RESULTS.md) for prediction.

Recovery uses 96 whole-participant resampled profiles per configuration
and generator, centered at the group profile. Use seed 20261201. Give
the two conditions facilitation through the second and third nearest
probes in five-probe designs. For exact cue matching, sample these
generators at 27 and 100 cm, leaving the same near-probe truth in both
conditions. Use zero, 40 and 120 ms facilitation in raw RT. On the
log scale use log(1 + amplitude/500 ms). Include a constant nonzero
facilitation generator at the larger magnitude across all probes.
Record per-profile null selection, exact recovery, wrong-probe and
no-selection counts, and joint equal-phase condition recovery. The
strong constant case checks whether detection at the outermost probe
can occur even without a transition. The design supplies no within-person
trial pairing for a signed-rank or paired t test across modalities.
Participant location checks use separate compatibility-set analyses.
