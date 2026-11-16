# Study 5 boundary methods from the PPS Kit catalogue

The 16 November 2026 screen covered 1,409 PDF pages across all 94 records
in the catalogue. This included 73 main sources and 21 separately retained
copies matched to the inventory checksums. The source versions include
journal issues, accepted manuscripts, preprints, chapters and one abstract.
Search-hit screening nominated candidates, then we checked the relevant
method sections and supplements for the decisions below. Coverage is
complete for this catalogue snapshot, with a focused search for related
methods outside it. The research ledger and source copies remain with the
private library.

A later revision retained the same 94 records and source hashes. The
structured comparison identified 68 changed analysis fields across 18
DOIs. The revisions contain 481 procedure records each. The comparison
prompted a direct test of the first detectable adjacent RT decrease,
which uses a different selection criterion from a fitted change point.

The comparison uses the [fixed Study 5 registry](../results/baseline_effects/analysis_registry.json),
the [browser analysis plan](../workbook/ANALYSIS_PLAN.md), and the native
directional, visible-shape and trial-cleaning branches. Record a method
variant only when it changes an estimator, outcome, identification assumption
or unit of generalization. Numerical optimization settings and arbitrary
combinations of the same models do not add independent evidence.

The [common monotone shift comparison](../results/boundary_methods/MONOTONE_SHIFT_RESULTS.md)
keeps the function shape unspecified while testing relative horizontal
displacement. All 2,048 estimable paired sets retained every shift,
including under a shared RT level. Allowing displacement worsened
group held-probe mean RT prediction in all four baseline and axis settings.

| Method and source | Relation to Study 5 | Decision |
| --- | --- | --- |
| Fixed-extrema logistic and mean-RT comparisons in [Canzoneri et al. (2012)](https://doi.org/10.1371/journal.pone.0044306), Methods, and [Noel et al. (2018)](https://doi.org/10.1152/jn.00652.2017), equation 1 | Study 5 already ran fixed-extrema logistic, free logistic, probit, Gompertz and log-logistic on both nominal axes; tested means, medians, smoothing, directional and constrained curves | Covered. The Noel fixed-extrema median variant falls within existing choices. Different approaches or stimulus velocities require measurements Study 5 did not collect |
| Ferroni et al. [2022](https://doi.org/10.1093/schbul/sbac067), Methods, and [2026](https://doi.org/10.1016/j.neuropsychologia.2026.109490), MATLAB supplements mmc3–4 | Real additional estimator. It scales per-distance RT means to their own range, enforces monotonicity, pads the ends, and integrates an implied transition distribution. [Miller and Ulrich (2001)](https://doi.org/10.3758/BF03194551) established the psychometric estimator for response frequencies. The PPS implementation adapts it to normalized RT | Run. A location is a descriptive centroid; matched-noise flat simulations test the effect of normalizing an empirical range |
| Fixed-extrema sigmoid on mean natural-log RT in [Ferri et al. (2015)](https://doi.org/10.1523/JNEUROSCI.1696-15.2015), pp. 16330 and 16333 | Same five SOAs as Study 5. Earlier log-distance models transform the predictor, and earlier log-RT regressions do not fit a boundary on mean log latencies. Ferri compared looming with flat sound and reported findings in a fit-selected sample | Run on the existing retained positive AT trials. Compare with a matched raw-scale sigmoid and predictors trained on four SOAs. A stationary-sound contrast cannot be reproduced |
| First adjacent RT drop in [Hobeika et al. (2018)](https://doi.org/10.1007/s00221-017-5158-2) and [Hobeika et al. (2019), §3](https://pmc.ncbi.nlm.nih.gov/articles/PMC6731720/) | The group rule identifies the first sampled gap with a detectable decrease while the sound approaches | [Run directly](../results/boundary_methods/ADJACENT_RULE_RESULTS.md). Both raw exhale profiles selected 50–73 cm registered. Same-label subtraction selected no gap and the paired RT change was uncertain |
| Farthest facilitated probe in [Teraoka et al. (2024)](https://muroran-it.repo.nii.ac.jp/record/2000223/files/Comparison%20of%20peripersonal%20space%20in%20front%20and%20rear%20spaces.pdf) and [Rahmani et al. (2025)](https://dael.euracoustics.org/confs/fa2025/data/articles/000866.pdf) | The signed-rank/Holm and paired t/JZS rules both select a probe using a tactile-only comparator | [Group selection](../results/boundary_methods/FACILITATION_EDGE_RESULTS.md) changed across Baseline references. [Individual uncertainty sets](../results/boundary_methods/INDIVIDUAL_FACILITATION_RESULTS.md) isolated only one endpoint in 718 estimable profiles, at 100 cm under nominal same-label subtraction. Every estimable paired individual contrast could be undefined and every conditional interval included zero |
| Delay-specific CDF and percentile contrasts in [Amiel et al. (2026)](https://doi.org/10.1016/j.cortex.2025.11.015), §3.2.2.2 and supplement | Separates portions of the RT distribution. The original subtracts a fixed-sound comparator. Study 5 previously ran means, robust summaries and Student-t location models, without a family of quartile-specific boundary candidates | Run .25, .50 and .75 profile sensitivities only. The source has more trials per cell and a within-delay auditory comparator |
| Corrected log-distance gradient in [Hobeika et al. (2020)](https://doi.org/10.1016/j.jneumeth.2019.108534), §§2.2 and 3.1 | Study 5 tested log-distance with and without tactile-only correction. The source uses a fixed far sound to address expectancy | Log-distance already run. The stationary-sound design cannot be recreated from the existing release. A distance gradient alone has no boundary parameter |
| Inverse efficiency and redundant-target race bounds in [Collignon et al. (2009)](https://doi.org/10.1016/j.neuropsychologia.2009.07.025), §§2.4–3, and [Murray et al. (2005)](https://doi.org/10.1093/cercor/bhh197) | Misses and hit probability offer a complement to RT. Study 5 has no auditory target RT distribution, and auditory-only catches ask participants to withhold responses | A race bound is unavailable. A joint hit/latency model can assess selection on recorded outcomes. Inverse efficiency would change the outcome and is not a direct boundary estimator |
| EEG or motor response contrasts, temporal order, presence reports, lesion effects, reaching thresholds and explicit peripersonal judgments across the catalogue | Distinct outcomes, measurement models or interventions. Study 5 released scheduled phase, tactile hits, RT, and questionnaire reports | No conversion to an observed participant RT boundary. These sources can motivate prior assumptions or a future design |

## Finite follow-up registry

| Family | Next adjudication |
| --- | --- |
| Reduced or shared nonlinear structure | The [GLS reductions](../results/boundary_methods/PROFILE_RESULTS.md) implement shared width, shared midpoint and both. The [hierarchical comparisons](../results/boundary_methods/HIERARCHY_RESULTS.md) add population and participant sharing under a marginal trial likelihood. All 45 held-probe fits and 32 recovery attempts are recorded. Condition-level peak differences remained unresolved and predicted responses could not distinguish factorial midpoint and width variation |
| Profile likelihood and weak identification | Ran [absolute calibrated midpoint profiles](../results/boundary_methods/PROFILE_RESULTS.md). They admit non-identification and boundary-free alternatives and retain disconnected sets, outside-range values and zero amplitude. The [paired mixed likelihood](../results/boundary_methods/MIXED_PROFILE_RESULTS.md) integrates discrete random midpoints and selects population shape by maximum marginal likelihood. Condition support reached both search limits. The zero-shift model scored highest on held data across both maps and lattices |
| Continuous change points | Ran [near and far plateau hinges and a free broken line](../results/boundary_methods/KNOT_RESULTS.md). One exploratory participant–condition–phase cell supported a near-plateau knot on both mappings under pooled Baseline. No knot or paired difference was robust to the timing-unverified same-label sensitivity. Group curves retained boundary-free references |
| Crossing of a fitted line with the lower confidence limit of tactile-only RT in [Serino et al. (2015)](https://doi.org/10.1038/srep18603), Fig. 7 | A baseline-calibrated operational trunk boundary. The crossing moves with uncertainty in tactile-only RT or selection of the fastest Baseline delay. The Noel et al. conference abstract cannot establish an equivalent fit | [Ran](../results/boundary_methods/BASELINE_CROSSING_RESULTS.md) four reference rules with uncertainty-aware ratio sets, refits and recovery. No observed crossing or paired contrast localized |
| Monotone partial identification | Ran [compatible location and censoring sets](../results/boundary_methods/THRESHOLD_RESULTS.md) for the observed-range half response and 0, 20 and 40 ms of facilitation. No observed crossing or paired contrast localized. Isotonic interpolation improved held-distance prediction under pooled Baseline and lost that advantage with same-label subtraction. A monotone spline, GAM or Gaussian process adds assumptions about smoothness between the probes |
| Distribution and selection | The [two-part observed-outcome comparison](../results/boundary_methods/RESPONSE_RESULTS.md) adds miss and miss-or-slow boundaries. No observed outcome or paired contrast localized. The [shared recorded-response likelihood](../results/boundary_methods/JOINT_RECORDED_RESULTS.md) gave the same single within-range participant phase interval as RT only. Group held prediction favored a latency-only sigmoid and all paired intervals included zero. The [lognormal center and dispersion sensitivity](../results/boundary_methods/DISTRIBUTION_RESULTS.md) found three exploratory dispersion cells with no supported paired boundary. A common censoring deadline remains unverified |
| Condition-level estimands and sensitivities | Compare the location of each group's equal-person average curve with the average of latent participant locations under valid partial pooling. Hold both phases and apply the existing pairing and recording-linkage sensitivities. Check stability under the alternative axis, timing-unverified same-label baseline, session-time covariates and retained-trial counts. Keep the nominated last-30 sensitivity pending verified recruitment order |
| Mechanistic separation | Time and distance are aliased along the trajectory. The documented +500 ms cue-offset sensitivity leaves two exact Baseline matches, which identify an endpoint difference. Its four-point interpolation leaves every tested midpoint compatible. Additional source-waveform links could verify how widely the offset applies. Independent space and time effects require design variation. [Timing sensitivity](../results/boundary_methods/CUE_TIME_RESULTS.md) |

[Noel et al. (2015), §§3.1–3.2](https://doi.org/10.1016/j.cognition.2015.07.012)
used corrected paired distance comparisons with a fastest end-probe
tactile-only reference. The Study 5 adaptation averages the earliest
and latest Baseline means across conditions separately, within each
participant and phase. It subtracts the faster mean from both conditions.
The three linkage cohorts each yielded zero of 30 group probe
comparisons at the one-sided 0.01 cutoff. The smallest unadjusted
probability was 0.126 across cohorts. All 18 group monotone
zero-crossing sets were unresolved. The probe tests use the five-probe
Bonferroni allocation within each profile. Absolute cue timing remains
uncertain for the nominal Baseline labels.

An operational d′ analysis used each participant phase cell's pooled
audio-only catch false-alarm rate. In the primary40 sample, 24 of 1,917
catches were false alarms, and 11 of those had a recorded time. All
catches lack a distance bin. The log-linear estimator used the
inverse-normal transforms of the hit and false-alarm proportions
with a half-count correction. The false-alarm term is a common
offset across a cell's probes. All 18 group profiles across the
three cohort choices admitted a flat curve and retained unresolved
monotone half-range crossings. The pooled catch rate measures
trial-level false alarms across the trajectory.
[Bassolino et al. (2010)](https://doi.org/10.1016/j.neuropsychologia.2009.11.009) ·
[Hautus (1995)](https://doi.org/10.3758/BF03203619)

A sensitivity motivated by the 16 ms expectancy correction in
Holmes et al. adds `16 × (SOA − 300) / 2400` ms to retained AT
latencies. The offset assumes a linear effect over the nominal SOAs
and cancels from raw paired RT differences. Both distance maps and
both Baseline rules yielded zero localized participant phase
midpoints. Every group profile retained all 121 tested midpoint
locations. Flat predictions had the lowest held group RMSE under
both Baseline rules. Physical distance and elapsed time remain
aliased. [Holmes et al. (2020)](https://doi.org/10.1007/s00221-020-05771-5)

The [initial numerical report](../results/boundary_methods/RESULTS.md) and
[profile report](../results/boundary_methods/PROFILE_RESULTS.md) record the
completed batches. The ongoing checklist is in the [analysis roadmap](../for-ai/ANALYSIS_ROADMAP.md).
