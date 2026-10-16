= Results
<results>
== Released cohort and response quality
<released-cohort-and-response-quality>
The analysis used all 42 participant records in the released tables (34 women, 8 men; mean age 23.0 years, SD 4.0, range 19--37). Twenty-one completed each condition order. There were 17,114 observed trials of 17,136 planned slots: 10,068 Audio--Tactile, 5,033 Baseline, and 2,013 Catch trials. Forty-one sessions were complete; one partial session lacked 22 trials but supplied all 20 Condition $times$ Phase $times$ SOA cells. There were 24 Catch false alarms, and no participant exceeded the 30% Catch exclusion rule. Low-hit-rate flags are reported without adding an exclusion criterion.

Among hit-labelled trials, 105 RTs were missing (80 Audio--Tactile and 25 Baseline). These trials remained in hit-rate denominators. The participant-wide mean $plus.minus$ 2.5-SD trim removed 382 of 13,694 recorded hit RTs, retaining 8,916 Audio--Tactile and 4,396 Baseline RTs. Adding a 200-ms minimum after trimming removed no further observations. Forty-one participants had the full questionnaire measures and one had PPS measures only.

A recording-integrity audit found that P011 and P033 share all 408 behavioural trial records, with Control/Viscereality labels swapped, despite different questionnaire responses. The CSVs were preserved; the correct recording-to-person mapping is unresolved. Full-release behavioural inference below is provisional and cannot assume 42 independent recordings. The new individual-parameter extension reports explicit exclusions of both records and of each separately. Questionnaire-only spatial/MAIA results do not depend on the RT mapping.

== Primary interaction and sensitivity analyses
<primary-interaction-and-sensitivity-analyses>
Adding the Condition $times$ Phase $times$ numeric-SOA term to the trial-level random-intercept ML model did not improve fit, $chi^2 \( 1 \) = 0.024$, $p = .878$. With symmetric Condition/Phase coding and standardized SOA, its estimate was 0.81~ms per SOA SD (SE 5.31; 95% model-based Wald CI $\[ - 9.60 , 11.23 \]$). This interval permits effects in either direction and does not establish equivalence.

The categorical-SOA comparison gave $chi^2 \( 4 \) = 2.27$, $p = .686$. Excluding the partial session left 41 participants (numeric $p = .807$; categorical $p = .773$). The Control-only Phase $times$ SOA test was also not detected (numeric $p = .430$; categorical $p = .468$). Allowing a participant random SOA slope yielded $p = .859$. The participant-cell repeated-measures three-way interaction was $F \( 4 , 164 \) = 0.99$, Greenhouse--Geisser $epsilon.alt = 0.839$, corrected $p = .406$.

The equal-participant five-SOA slope contrast was 0.03~ms per SOA SD, 95% CI $\[ - 7.88 , 7.95 \]$, $t \( 41 \) = 0.008$, $p = .993$. The Monte Carlo sign-flip test used 19,999 draws with a fixed seed ($p = .994$). Its exploratory paired JZS factor was $upright(B F)_10 = 0.167$ ($upright(B F)_01 = 6.00$). This normal-likelihood participant model is distinct from the registered mixed model; the slope distribution departed from normality (Shapiro--Wilk $p = .005$).

The exploratory participant-cluster-robust models gave the following three-way terms. Normal Wald intervals use the documented finite-cluster sandwich correction.

#block[
#figure(
  align(center)[#table(
    columns: 4,
    align: (left,right,right,right,),
    table.header([Model], [Estimate], [95% CI], [$p$],),
    table.hline(),
    [Raw RT], [-1.543], [$\[ - 9.57 , 6.49 \]$], [$.706$],
    [Log RT], [-0.003], [$\[ - 0.01 , 0.01 \]$], [$.614$],
    [Time-on-task-adjusted RT], [-1.584], [$\[ - 9.59 , 6.42 \]$], [$.698$],
    [Hit probability (log odds)], [0.001], [$\[ - 0.23 , 0.24 \]$], [$.994$],
  )]
  , kind: table, numbering: none
  )

]
The missing-hit-RT stress tests imputed only the 80 Audio--Tactile hits lacking RTs, then recomputed trimming. Median-only imputation gave $p = .960$; signed $- 200$ and $+ 200$~ms scenarios gave $p = .428$ and $p = .253$, respectively. These specified scenarios do not recover missed-trial RTs or identify the missingness mechanism. Full model coefficients, scaling, diagnostics, intermediate tables, and all stress scenarios are in the companion's downloadable report.

#figure(image("../figures/study5_current_rt_soa_curves.png", width: 100%),
  caption: [
    #strong[Audio--Tactile RT by SOA, Condition, and instructed respiratory phase in the 42-person cohort.] Each point averages participant means with equal person weight; all cells contain 42 participants. Intervals are pointwise 95% $t$ intervals across participant means. Longer SOAs correspond to nearer nominal auditory positions. Lines connect means and are not sigmoid fits; inference comes from the stated models.
  ]
)
<study5:fig:current_rt_soa>

== Sigmoid viability and descriptive PPS shape
<sigmoid-viability-and-descriptive-pps-shape>
None of 168 trial-level participant $times$ Condition $times$ Phase sigmoid fits reached $R^2 gt.eq .70$ (median $R^2 = 0.038$; maximum 0.419). The largest saturated five-SOA trial-level $R^2$ ceiling was 0.430. Thus no deterministic sigmoid of these SOAs could reach .70 in any cell, independent of the particular nonlinear optimizer or parameter bounds. Sigmoids improved unpenalized in-sample RMSE over a line in 164/168 cells; this does not establish stable boundaries.

Fitting four parameters to five SOA means instead yielded 79/168 qualifying cells and 3 participants passing all four cells, with none having four bound-free fits. Such fits have one residual degree of freedom and were not used to rescue the failed trial-level gate. Replacing approximate registered distances with trajectory-implied positions left the trial-level pass count at zero. Parameter-bound diagnostics and group fits are supplied descriptively. Participant midpoint/sharpness contrasts and their MAIA-2 or pictographic associations were not estimable under the planned fit gate.

== Four uniformly estimated descriptive sigmoid curves
<four-uniformly-estimated-descriptive-sigmoid-curves>
A separate post hoc analysis obtained nonflat sigmoid approximations for all four Condition $times$ Phase groups using a single extraction, smoothing, and fitting rule (Figure~#ref(<study5:fig:descriptive_sigmoids>, supplement: none)). All 42 participants contributed all five positions with equal person weight. The search compared 320 pipelines spanning mean, median, trimmed-mean and winsorized summaries; Gaussian local-constant/local-linear and tricube local-linear smoothing; curvature penalization; isotonic projection; and separate versus shared logistic widths. The original trial-level gate above was retained as a distinct analysis.

The lowest crossed participant/position prediction score selected 20% per-tail winsorization within participant cells, Gaussian local-constant smoothing with bandwidth 0.5 of the nominal distance span (45~cm), and separate logistic widths. This same pipeline was applied to all four curves. The tuning RMSE was 47.053~ms, compared with 47.317~ms for a line and 47.437~ms for a constant. The fixed prediction target was each held-out person's raw mean at the omitted position minus that person's raw mean across the other four positions. The small advantage over a line is a post-selection descriptive score, not independent evidence of sigmoid superiority.

For $f \( d \) = a + A "expit" \( \( d - m \) \/ s \)$, $m$ is the half-amplitude midpoint, $s$ is the logistic width, and the RT derivative at the midpoint is $A \/ \( 4 s \)$. Smaller widths indicate sharper normalized transitions; RT slopes additionally depend on amplitude. Width is not a Gaussian standard deviation. Estimates refer to the registration's approximate distance labels.

#block[
#figure(
  align(center)[#table(
    columns: 4,
    align: (left,right,right,right,),
    table.header([Condition / phase], [$m$ (cm)], [$s$ (cm)], [$f' \( m \)$ (ms/cm)],),
    table.hline(),
    [Control / Exhale], [71.50], [35.29], [0.0907],
    [Control / Inhale], [96.25], [42.56], [0.0846],
    [Viscereality / Exhale], [82.75], [35.29], [0.0900],
    [Viscereality / Inhale], [25.38], [30.38], [0.0686],
  )]
  , kind: table, numbering: none
  )

]
The 1,000 whole-participant bootstrap resamples preserved each person's four curves together and refitted smoothing and the sigmoid model. Conditional 95% percentile intervals for the four midpoints, in table order, were \[37.6, 88.0\]; \[18.5, 100.0\]; \[31.8, 100.0\]; \[10.0, 93.3\]~cm. Flat fits occurred in 0.9%, 8.7%, 3.2%, 8.7% of resamples; midpoint-bound hits, including flat draws, occurred in 2.0%, 21.0%, 6.3%, 14.1%. Midpoint and width intervals exclude flat draws, for which these parameters are unidentified, and condition on the selected pipeline. They do not include uncertainty from choosing among 320 methods and should not be treated as unconditional coverage guarantees.

Descriptively, the Inhale-minus-Exhale midpoint difference was 24.75~cm in Control and -57.38~cm in Viscereality. Their difference was -82.12~cm, conditional bootstrap interval \[-107.25, 25.62\]~cm, based on 828 resamples with all contributing curves nonflat. No confirmatory test was assigned to this post hoc group-parameter contrast. The report includes all paired midpoint, width and RT-slope comparisons.

The fitted 10--90% transition spans were 155.1, 187.0, 155.1, 133.5~cm, each exceeding the sampled 90-cm span. Consequently, the complete S shapes and their asymptotes depend on extrapolation. A fixed alternative using 20% trimmed means and a narrower Gaussian bandwidth of 0.3 yielded midpoints 61.7, 84.6, 68.1, 31.4~cm, with tuning RMSE 48.784~ms. Applying the selected rule to trajectory-implied coordinates yielded 74.7, 87.3, 82.0, 34.3~cm; expanding the midpoint/width/amplitude search bounds yielded 70.8, 94.8, 84.2, 25.8~cm. These method and coordinate sensitivities limit a literal boundary interpretation. All candidate scores and parameter estimates, including edge and flat solutions, remain available in the companion.

#figure(image("../figures/study5_descriptive_sigmoids.png", width: 100%),
  caption: [
    #strong[Four uniformly estimated descriptive sigmoids.] Open gray circles are raw participant-weighted means; black points are participant-weighted winsorized cell summaries; crosses show Gaussian-kernel-smoothed summaries. Solid curves are logistic approximations fitted to the five smoothed design points, with no interpolated observations added to the fit. Vertical dotted lines mark the fitted midpoints. Bands are pointwise participant-bootstrap percentiles conditional on the selected pipeline, including flat resamples. The full search, parameter uncertainty, and model extrapolations are available in the browser companion.
  ]
)
<study5:fig:descriptive_sigmoids>

== Measured-range PPS shape and predictive support
<measured-range-pps-shape-and-predictive-support>
The stronger exploratory goal required a visible transition within the observed range, rather than a sigmoid that is nearly linear over that range. None of the 320 original pipelines met all measured-range criteria in all four curves. An additional 320 pipelines imposed those criteria, while 160 linear pipelines received the same extraction and smoothing options. The lowest-scoring constrained method used 10% per-tail trimming, a Gaussian bandwidth of 13.5~cm, increasing isotonic projection and separate logistic widths. Its tuning RMSE was 47.086~ms, versus 47.178~ms for the tuned linear family. These are method-selection scores.

#figure(
  align(center)[#table(
    columns: 6,
    align: (left,left,right,right,right,right,),
    table.header([Condition], [Phase], [Midpoint (cm)], [Width (cm)], [Slope (ms/cm)], [Width floor],),
    table.hline(),
    [Control], [Exhale], [56.12], [4.50], [0.9194], [Yes],
    [Control], [Inhale], [72.62], [8.51], [0.4234], [No],
    [Viscereality], [Exhale], [69.25], [4.50], [0.7733], [Yes],
    [Viscereality], [Inhale], [30.62], [4.50], [0.6310], [Yes],
  )]
  , caption: [Imposed-shape descriptive estimates. A visible transition is enforced by the model constraints; it is not an empirical finding. Conditional intervals and constraint-hit frequencies are provided in the companion.]
  , kind: table
  )

Three of the four width estimates reached the 4.5-cm minimum, and the Control/Inhale midpoint reached the upper sampling constraint. Conditional 95% midpoint intervals, in table order, were \[44.50, 72.62\]; \[27.25, 72.62\]; \[38.11, 72.62\]; \[27.25, 72.62\]~cm. These intervals are truncated by the shape restrictions and exclude flat resamples; they do not establish stable physiological boundaries.

Six outer participant folds repeated the complete pipeline selection inside each training set, using five inner participant folds crossed with omitted positions. Outer RMSE was 47.772~ms for the original sigmoid family, 47.634~ms for the constrained family, 47.701~ms for tuned lines and 47.437~ms for a constant. The constrained curve's small advantage over tuned lines did not extend to the constant benchmark. These exploratory estimates address new participants at the known design positions; overlapping training sets and post hoc family development preclude a confirmatory model-superiority claim.

A separate unsmoothed participant-level test projected each five-position curve onto the three contrasts orthogonal to an intercept and distance. Hotelling tests of these nonlinear components gave Holm-adjusted $p$ values of 0.215, 1.000, 1.000, 1.000, in table order. This test concerns any nonlinearity, not specifically a sigmoid, and assumes multivariate-normal participant contrasts. Failure to detect curvature does not prove linearity. Together, the predictive results and active constraints leave the data-supported PPS-shape goal unresolved, despite obtaining four visibly S-shaped model approximations.

#figure(image("../figures/study5_pps_shape.png", width: 100%),
  caption: [
    #strong[Measured-range PPS-shaped sensitivity.] Common linear axes preserve between-curve scale comparisons. Raw means (open circles), trimmed summaries (black points), fitted curves and the tuned line are each centered on their corresponding five-position mean; subtracting a constant cannot create curvature. Bands resample participants jointly, refit the constrained model and recenter each draw. They condition on the selected extraction and shape restrictions. Asterisks mark active width or midpoint constraints. All five observed positions remain visible.
  ]
)
<study5:fig:pps_shape>

#figure(image("../figures/study5_sigmoid_geometry.png", width: 100%),
  caption: [
    #strong[Fitted shape separated from empirical support.] The vertical axis normalizes each fitted asymptotic RT change to 0--1. Colored lines show the imposed-shape family; dashed gray lines retain the original best-score family. This diagnostic displays model geometry only, without observations or empirical uncertainty on this scale. It shows why the original curves did not display both plateaus within the measured range, and how explicit constraints produce an S shape. It is not additional evidence for that shape in the measurements.
  ]
)
<study5:fig:sigmoid_geometry>

== Baseline, sound, and order diagnostics
<baseline-sound-and-order-diagnostics>
Across ten supplementary paired contrasts, Holm adjustment was applied as one family. Overall Audio--Tactile minus within-Condition/Phase mean Baseline RT was -18.81~ms, 95% CI $\[ - 27.00 , - 10.63 \]$, unadjusted $p < .001$, Holm $p < .001$. Baseline Inhale minus Exhale RT was 18.08~ms, 95% CI $\[ 3.28 , 32.88 \]$, unadjusted $p = .018$, Holm $p = .143$. The Baseline Condition $times$ Phase contrast was 17.43~ms, 95% CI $\[ 1.56 , 33.30 \]$, unadjusted $p = .032$, Holm $p = .225$. These checks neither establish phase invariance nor provide adjusted evidence of a Baseline phase difference.

The far-minus-near Audio--Tactile difference was 13.80~ms, 95% CI $\[ - 1.82 , 29.42 \]$; the analogous Baseline nominal-label difference was 11.69~ms, 95% CI $\[ - 6.90 , 30.28 \]$. Their difference was 2.11~ms, 95% CI $\[ - 18.44 , 22.66 \]$. Far Audio--Tactile minus Baseline was -10.50~ms using the Condition/Phase reference and -24.83~ms using the same nominal SOA label (Holm $p = .023$ for the latter). Equal labels do not establish cue-time matching; these differences cannot isolate auditory proximity or remove temporal expectancy.

Pink-minus-white Audio--Tactile RT was -2.86~ms, 95% CI $\[ - 9.30 , 3.58 \]$. Among the 20 participants with all four noise types available, the exploratory Friedman test gave $chi^2 \( 3 \) = 7.80$, $p = .050$. This availability-defined subset cannot be assigned to an acquisition version from the released tables. The two order subgroups each contained 21 participants; their slope contrasts were -4.19~ms, 95% CI $\[ - 14.64 , 6.27 \]$, and 4.25~ms, 95% CI $\[ - 8.27 , 16.78 \]$. These descriptive subgroup results do not establish order equivalence.

#figure(image("../figures/study5_delay_matched_facilitation.png", width: 100%),
  caption: [
    #strong[Exploratory Audio--Tactile minus Baseline RT paired by nominal SOA label.] Points average 42 participant differences within Condition $times$ Phase $times$ label. Negative values indicate faster Audio--Tactile responses. Baseline has no sound; matching labels does not establish equal trial-relative tactile-cue time. Intervals are pointwise 95% $t$ intervals across participants. Lines connect means and carry no boundary inference.
  ]
)
<study5:fig:delay_matched_facilitation>

== MAIA-2 and spatial frame of reference
<maia-2-and-spatial-frame-of-reference>
This post hoc extension analysed 41 complete MAIA-2 records and 41 complete spatial-frame pairs. All 328 stored MAIA-2 subscale scores matched independent recomputation from the 37 items, including reverse scoring; there were 0 mismatches. The participant with missing questionnaires remained in the behavioural cohort. Table~#ref(<study5:tab:maia>, supplement: none) reports all eight dimensions and internal-consistency uncertainty. These are self-reported interoceptive dimensions, not objective interoceptive accuracy. The lower alpha estimates for Noticing and Emotional Awareness warrant caution; no items were removed to improve reliability.

#block[
#figure(
  align(center)[#table(
    columns: 5,
    align: (left,right,right,right,right,),
    table.header([Dimension], [Mean], [SD], [Alpha], [95% alpha interval],),
    table.hline(),
    [Noticing], [3.24], [0.66], [0.565], [\[0.188, 0.740\]],
    [Not Distracting], [2.24], [0.85], [0.842], [\[0.725, 0.906\]],
    [Not Worrying], [2.29], [0.82], [0.704], [\[0.511, 0.808\]],
    [Attention Regulation], [2.96], [0.67], [0.784], [\[0.648, 0.858\]],
    [Emotional Awareness], [3.47], [0.70], [0.589], [\[0.314, 0.740\]],
    [Self Regulation], [2.85], [0.86], [0.814], [\[0.690, 0.885\]],
    [Body Listening], [2.80], [0.92], [0.777], [\[0.602, 0.867\]],
    [Trusting], [3.59], [0.98], [0.861], [\[0.777, 0.909\]],
  )]
  , caption: [MAIA-2 subscale scores (0--5), each with $n = 41$. Intervals are pointwise percentile intervals from 2,000 participant-bootstrap draws. Alpha is a sample internal-consistency diagnostic, not a test of dimensionality or validity.]
  , kind: table
  ) <study5:tab:maia>

]
Viscereality spatial-frame ratings were higher than Control for 22 participants, lower for 6, and tied for 13 (Fig.~#ref(<study5:fig:questionnaires>, supplement: none)). The two-sided exact sign test gave $p = 0.00372$. Among the 28 non-ties, the higher-rating proportion was 0.786, exact 95% CI $\[ 0.590 , 0.917 \]$. Paired dominance across all 41 pairs was 0.390, percentile 95% CI $\[ 0.171 , 0.610 \]$. Both condition medians were category D. Higher/equal/lower counts by condition order were Control-Viscereality: 13/6/2; Viscereality-Control: 9/7/4. These descriptive order counts do not rule out period or carryover effects. The administered pictogram key is absent from the release, so a higher A--H code is not assigned an allocentric or egocentric interpretation. This exploratory ordinal difference does not establish a PPS-boundary change or its mechanism.

MAIA-2 was administered once before the experiment and spatial-frame ratings after each intervention, as confirmed by the project owner. The main follow-up outcome was the signed numerical code difference $Delta = upright(V i s c e r e a l i t y) - upright(C o n t r o l)$, irrespective of presentation order. Mean $Delta$ was 0.756 category steps (SD 1.480), median 1, interquartile range 0--2, and range -3 to 5. These are post-intervention condition differences, not changes from a pre-intervention spatial baseline; their numerical magnitudes assume comparable category steps.

#block[
#figure(
  align(center)[#table(
    columns: 6,
    align: (left,right,left,right,right,right,),
    table.header([Dimension], [$rho_Delta$], [95% interval], [$p_Delta$], [$rho_(upright(d i r))$], [$p_(upright(d i r))$],),
    table.hline(),
    [Noticing], [0.273], [\[-0.017, 0.529\]], [0.0872], [0.286], [0.0697],
    [Not Distracting], [0.097], [\[-0.241, 0.389\]], [0.5466], [0.031], [0.8439],
    [Not Worrying], [0.092], [\[-0.232, 0.415\]], [0.5657], [0.024], [0.8781],
    [Attention Regulation], [0.114], [\[-0.186, 0.414\]], [0.4809], [0.005], [0.9765],
    [Emotional Awareness], [-0.062], [\[-0.378, 0.247\]], [0.6992], [-0.028], [0.8616],
    [Self Regulation], [0.208], [\[-0.138, 0.501\]], [0.1915], [0.070], [0.6600],
    [Body Listening], [0.167], [\[-0.160, 0.459\]], [0.2954], [0.101], [0.5312],
    [Trusting], [0.376], [\[0.081, 0.627\]], [0.0160], [0.335], [0.0345],
  )]
  , caption: [Pre-experiment MAIA-2 and signed spatial change, $n = 41$. Main analyses correlate numerical $Delta$ with each dimension; direction-only ($- 1 , 0 , + 1$) correlations are ordinal sensitivities. All $p$ values are unadjusted two-sided permutation values; intervals are pointwise paired-participant bootstrap intervals.]
  , kind: table
  ) <study5:tab:spatial_delta>

]
Trusting was positively associated with numerical $Delta$: $rho = 0.376$, pointwise 95% CI $\[ 0.081 , 0.627 \]$, unadjusted permutation $p = 0.0160$ (Table~#ref(<study5:tab:spatial_delta>, supplement: none); Fig.~#ref(<study5:fig:spatial_delta>, supplement: none)). The direction-only sensitivity was also positive ($rho = 0.335$, $p = 0.0345$). The other seven numerical-delta correlations had $p > .05$; this does not establish absence of associations. The ancillary correlation between numerical $Delta$ and the raw-RT Condition $times$ Phase SOA-slope interaction was $rho = - 0.020$, pointwise 95% CI $\[ - 0.328 , 0.294 \]$, $p = 0.9046$. The RT contrast is not a PPS boundary.

#block[
#figure(
  align(center)[#table(
    columns: 7,
    align: (left,right,right,right,right,right,right,),
    [], table.cell(align: center, colspan: 3)[MAIA only], table.cell(align: center, colspan: 3)[With presentation order],
    [Dimension], [$b$], [$p$], [$p_(upright(H C 3))$], [$b$], [$p$], [$p_(upright(H C 3))$],
    [Noticing], [0.641], [0.0705], [0.0185], [0.604], [0.0962], [0.0312],
    [Not Distracting], [0.387], [0.1606], [0.2850], [0.471], [0.0968], [0.2179],
    [Not Worrying], [0.137], [0.6371], [0.7261], [0.101], [0.7320], [0.8213],
    [Attention Regulation], [0.422], [0.2313], [0.2970], [0.409], [0.2477], [0.3489],
    [Emotional Awareness], [-0.065], [0.8489], [0.8457], [-0.079], [0.8181], [0.8059],
    [Self Regulation], [0.468], [0.0838], [0.1144], [0.469], [0.0843], [0.1241],
    [Body Listening], [0.237], [0.3573], [0.3317], [0.244], [0.3451], [0.2963],
    [Trusting], [0.613], [0.0085], [0.0293], [0.624], [0.0075], [0.0235],
  )]
  , caption: [Condition $times$ MAIA moderation, fitted through participant-level numerical $Delta$, $n = 41$ per model. Slopes are code steps per one MAIA point. Ordinary two-sided $t$ inference is equivalent to the repeated-measures interaction $F = t^2$; HC3 provides approximate heteroskedasticity-sensitive inference. Residual degrees of freedom are 39 and 38. All $p$ values are unadjusted; the companion exports all intervals, $F$ statistics and model diagnostics.]
  , kind: table
  ) <study5:tab:spatial_moderation>

]
The Trusting interaction slope was 0.613 code steps per MAIA point, $F \( 1 , 39 \) = 7.681$, $p = 0.0085$. Its HC3 interval was $\[ 0.065 , 1.160 \]$, $p = 0.0293$. Accounting for presentation order gave $b = 0.624$, $F \( 1 , 38 \) = 7.987$, $p = 0.0075$; HC3 95% CI $\[ 0.089 , 1.159 \]$, $p = 0.0235$. Noticing depended on the uncertainty estimator: ordinary $p = 0.0705$ and 0.0962, versus HC3 $p = 0.0185$ and 0.0312, without/with order respectively. This less consistent pattern is reported alongside its non-detection in the main rank analysis (Table~#ref(<study5:tab:spatial_moderation>, supplement: none)).

These are exploratory associations and trait-moderation estimates, not mediation or independent replications. The analysis direction was chosen after inspecting earlier results, all intervals are pointwise, and no multiple-testing correction was applied. The 33 earlier absolute-rating, direction and behavioural associations remain available as supplementary audit outputs, alongside the nine new delta correlations and 16 moderation fits. Small sample size, uncertain reliability, category-spacing assumptions and possible confounding/carryover limit inference. Boundary-related questionnaire associations remain unestimated under the original fit gate.

#figure(image("../figures/study5_spatial_change.png", width: 100%),
  caption: [
    #strong[Pre-experiment traits and post-intervention spatial change.] Left: all eight MAIA-2 correlations with numerical $Delta$ and pointwise bootstrap 95% intervals. Right: Condition $times$ MAIA slopes with and without presentation order and HC3 95% intervals. Higher $Delta$ means higher recorded Viscereality codes relative to Control; the administered pictogram direction is unverified.
  ]
)
<study5:fig:spatial_delta>

#figure(image("../figures/study5_questionnaires.png", width: 100%),
  caption: [
    #strong[Questionnaire coverage and paired spatial ratings.] Left: individual recomputed MAIA-2 subscale scores, means and pointwise 95% participant-bootstrap intervals. Right: counts for all Control/Viscereality category pairs; vertical position above the matching-category diagonal indicates a higher Viscereality code. All 41 paired records are represented. A--H preserve the recorded ordering without assuming equal psychological distances or a verified anchor direction.
  ]
)
<study5:fig:questionnaires>

== Individual sigmoid proxies and plateau normalization
<individual-sigmoid-proxies-and-plateau-normalization>
The additional exploratory extension obtained 168 four-cell sigmoid approximations from 42 participant records. Uniform selection among 84 candidates chose mean extraction, Gaussian local-constant smoothing with a 27-cm bandwidth, and a shape penalty of 4. Separate plateaus were primary; sharing both plateaus across each person's four curves was a sensitivity. Expected increasing direction occurred in 104/168 primary fits; decreasing responses were retained. The visible S shape was imposed by the measured-range constraints, so numerical parameter availability does not establish physiological boundaries.

Nested omitted-position prediction RMSE was 48.507~ms for the visible family, 51.694 for broad sigmoids, 48.269 for lines, 47.437 for a constant, and 47.237 for shared plateaus (Fig.~#ref(<study5:fig:individual_diagnostics>, supplement: none)). The shared-plateau improvement over a constant was only 0.200~ms. These descriptive scores do not test the significance of differences between overlapping folds.

Normalizing by each fitted lower plateau and absolute amplitude gives common asymptotes 0 and 1 while preserving midpoint and width. Raw observations were not clipped. The plateau-separation bootstrap interval excluded zero for only 29/168 separate-plateau fits and 40/168 shared-plateau fits; the latter represent ten people with four repeated flags. All 42 shared-model point fits converged under the specified alternating solver, without a guarantee of global optimality. The 42-page downloadable atlas shows all four raw-RT profiles with standard errors above their normalized model geometry, with recording-linkage flags.

Midpoint split-half rank reliability was low: medians 0.047 and 0.106 for separate and shared plateaus, respectively, across ten splits and four cells. Corresponding median conditional midpoint interval widths were 39.79 and 39.00~cm. With known 80-ms sigmoids and cell-specific baselines, median midpoint recovery correlations across 30 simulations were 0.036 and 0.183. Under shared-baseline simulated truth, shared-model midpoint recovery improved to 0.360. Width-derived steepness remained poorly recovered. These checks concern the stated simulations and within-session splits; they do not measure test--retest reliability or interval coverage.

Table~#ref(<study5:tab:individual_links>, supplement: none) gives all 27 main questionnaire associations for each model. Four primary or shared-model point-estimate tests had unadjusted $p < .05$, but all 54 refit-bootstrap intervals included zero. For example, the spatial-change/midpoint-change correlation moved from approximately zero under separate plateaus to $rho = .331$ under shared plateaus. This model dependence and weak parameter reliability preclude a stable boundary association claim. Different nominal findings appeared for MAIA Not Distracting, Emotional Awareness and Attention Regulation across specifications; no finding was selected as the primary outcome after inspection. Both complete sets of 126 associations and three linkage-exclusion specifications are retained, yielding 1,008 unadjusted tests. Excluding both ambiguous records, or each separately, repeated RT-only method selection; the selected smoothing/penalty choices differed. Those sensitivity analyses cannot determine the correct recording mapping. All RT--questionnaire inference remains provisional until that linkage is resolved.

#block[
#figure(
  align(center)[#table(
    columns: 4,
    align: (left,right,right,right,),
    table.cell(align: center, colspan: 4)[Separate plateaus],
    [Baseline trait / spatial change], [Midpoint], [Steepness], [RT slope],
    [Noticing], [-0.12 (0.454)], [-0.07 (0.682)], [-0.01 (0.938)],
    [Not Distracting], [0.31 (0.048)], [-0.15 (0.331)], [-0.20 (0.202)],
    [Not Worrying], [0.25 (0.118)], [0.15 (0.349)], [0.05 (0.731)],
    [Attention Regulation], [-0.03 (0.830)], [-0.03 (0.840)], [0.17 (0.292)],
    [Emotional Awareness], [-0.34 (0.032)], [-0.18 (0.254)], [0.07 (0.648)],
    [Self-Regulation], [-0.07 (0.650)], [-0.07 (0.647)], [0.08 (0.623)],
    [Body Listening], [0.00 (0.996)], [-0.28 (0.077)], [-0.14 (0.367)],
    [Trusting], [0.02 (0.880)], [-0.15 (0.351)], [-0.00 (0.989)],
    [Spatial code difference], [-0.00 (0.994)], [0.17 (0.290)], [0.14 (0.375)],
    table.cell(align: center, colspan: 4)[Shared plateaus],
    [Baseline trait / spatial change], [Midpoint], [Steepness], [RT slope],
    [Noticing], [0.09 (0.560)], [-0.05 (0.771)], [-0.07 (0.669)],
    [Not Distracting], [0.08 (0.636)], [-0.11 (0.480)], [-0.22 (0.164)],
    [Not Worrying], [0.06 (0.730)], [0.19 (0.220)], [0.21 (0.184)],
    [Attention Regulation], [0.16 (0.311)], [-0.06 (0.710)], [-0.39 (0.012)],
    [Emotional Awareness], [-0.06 (0.724)], [-0.14 (0.365)], [-0.21 (0.181)],
    [Self-Regulation], [0.07 (0.647)], [-0.08 (0.612)], [-0.13 (0.419)],
    [Body Listening], [0.02 (0.907)], [-0.23 (0.157)], [-0.18 (0.258)],
    [Trusting], [0.30 (0.059)], [-0.19 (0.237)], [-0.27 (0.084)],
    [Spatial code difference], [0.33 (0.034)], [0.16 (0.329)], [0.17 (0.299)],
  )]
  , caption: [Exploratory Spearman correlations of baseline MAIA-2 or spatial-code difference with Viscereality--Control parameter differences (equal phase weights; $n = 41$). Cells give $rho$ (unadjusted pairing-permutation $p$). Parameters come from four fitted curves per person. All refit-bootstrap intervals include zero; complete intervals, cell-specific correlations and recording-exclusion sensitivities are in the companion. Full-release RT linkage is unresolved.]
  , kind: table
  ) <study5:tab:individual_links>

]
#figure(image("../figures/study5_participant_diagnostics.png", width: 100%),
  caption: [
    Individual-parameter audit. Prediction differences are small; midpoint intervals are wide and split-half reliability is low. The lower-right panel compares the same 27 main association estimates under the two plateau assumptions. Neither normalized appearance nor numerical fit availability establishes a reliable PPS boundary.
  ]
)
<study5:fig:individual_diagnostics>

== Recording exclusions and remaining robustness checks
<recording-exclusions-and-remaining-robustness-checks>
An explicitly post-results amendment reran the primary behavioural models after excluding the two ambiguous records together and each separately. The numeric Condition $times$ Phase $times$ SOA result remained uncertain in every specification (Table~#ref(<study5:tab:linkage_models>, supplement: none)). All three categorical-interaction and Control-only numeric/categorical comparisons also had unadjusted $p > .05$. Raw/log cluster models, equal-person slope contrasts and raw-RT repeated-measures ANOVA are retained in the companion. These exclusions test sensitivity and do not identify the correct recording-to-person mapping.

#block[
#figure(
  align(center)[#table(
    columns: 5,
    align: (left,right,right,right,right,),
    table.header([Excluded], [Records], [Estimate], [95% interval], [$p$],),
    table.hline(),
    [P011, P033], [40], [0.86], [\[-9.73, 11.45\]], [0.873],
    [P011], [41], [1.09], [\[-9.41, 11.59\]], [0.839],
    [P033], [41], [0.58], [\[-9.92, 11.08\]], [0.913],
  )]
  , caption: [Primary numeric interaction after recording exclusions. Estimates are ms per cohort-specific SOA SD, with model-based Wald intervals; $p$ is the unadjusted full/reduced ML likelihood-ratio comparison. Cleaning and SOA scaling were recomputed for each cohort.]
  , kind: table
  ) <study5:tab:linkage_models>

]
For the four fitted curves per person, equal-phase Condition, equal-condition Phase and Condition $times$ Phase contrasts were calculated for midpoint, normalized steepness and signed RT derivative under both plateau models. All four linkage specifications received 500 person/group-plus-trial refits. Across 72 mean contrasts, 0 conditional refit intervals excluded zero; across 216 main questionnaire associations, 0 did so. For example, the separate-plateau mean midpoint change excluding both ambiguous records was -16.07~cm, with interval \[-28.17, 18.16\]~cm. The sizeable point shift reflects a fitted, partially pooled proxy; the wide interval and weak reliability prevent interpreting it as demonstrated PPS contraction.

The changes used in correlations were themselves unstable. Across ten splits, median rank correlations for midpoint change were -0.074 and 0.066 for separate and shared plateaus, respectively. Corresponding normalized-steepness values were 0.052 and -0.009; signed RT-slope values were 0.064 and 0.155. Known-signal simulations also assessed all three contrasts. Shared-model midpoint-change recovery was better when truth shared plateaus, but this simulation-specific improvement does not establish reliable observed individual differences (Fig.~#ref(<study5:fig:remaining_robustness>, supplement: none)).

The group-response audit excluded both ambiguous recordings ($n = 40$) and added 160 log-distance pipelines with the same extraction/smoothing choices as lines. Six-outer/five-inner participant/position prediction gave RMSEs 47.993~ms for broad sigmoids, 47.915 for visible sigmoids, 48.087 for lines, 48.121 for log distance and 48.020 for a constant. The visible family's improvement over a constant was 0.105~ms; this small descriptive difference is not a significance test or physiological validation. The log-distance comparison does not reproduce the expectancy-controlled design of #cite(<hobeika2019capturing>, form: "prose");. Unsmoothed nonlinear-component tests in the four curves all had unadjusted $p > .05$.

Nine fixed geometry specifications crossed three width floors with permissive, existing and strict visibility criteria. Their descriptive leave-position RMSE ranged from 47.47 to 94.59~ms; the large error under one permissive specification illustrates instability when an omitted position leaves the transition poorly constrained. Thirty whole-person resamples repeated all 320 visible-method selections with repeated copies kept in the same validation fold. They selected 27 distinct pipelines, and the most frequent appeared only 3 times. These finite sensitivity checks retain all outcomes; thirty draws describe selection instability and do not provide calibrated selection-adjusted tail intervals.

#figure(image("../figures/study5_remaining_robustness.png", width: 100%),
  caption: [
    Post-results robustness extension. Top left: primary RT interaction and model-based uncertainty across recording exclusions, rescaled to a common one-second SOA increment. Top right: five response families on the same 40-record prediction target. Bottom left: reliability of fitted Condition differences. Bottom right: midpoint-change point estimates and intervals that refit the models. Large fitted shifts can coexist with very uncertain, unreliable changes.
  ]
)
<study5:fig:remaining_robustness>

== Repeated-measures analysis of PPS midpoint and sharpness
<repeated-measures-analysis-of-pps-midpoint-and-sharpness>
The next exploratory question concerned all four fitted Condition $times$ Phase profiles and their relationship to baseline MAIA-2 and post-intervention spatial change. The main presentation excludes both ambiguous recordings (Exclude P011/P033; 40 behavioural records). Both plateau specifications remain reported; fitting methods were chosen from RT prediction without questionnaire outcomes. No multiple-testing correction was applied.

The 2$times$2 ANOVA on point estimates yielded 11 of 12 conventional terms with $p < .05$ across midpoint and normalized sharpness (Table~#ref(<study5:tab:parameter_anova>, supplement: none)). However, 0 of their 95% curve-refit intervals excluded zero. These two uncertainty calculations answer different conditional questions: the conventional ANOVA treats the estimated parameters as observed data, whereas hierarchical resampling re-estimates the curves and shared pooling. Small conventional $p$ values cannot overcome unstable fitted parameters.

#block[
#figure(
  align(center)[#table(
    columns: 6,
    align: (left,left,left,right,right,left,),
    table.header([Plateaus], [Outcome], [Effect], [$F$], [$p$], [95% refit interval],),
    table.hline(),
    [Separate], [Midpoint], [C], [5353], [2.301e-43], [\[-28.17, 18.16\]],
    [Separate], [Sharpness], [C], [70.85], [2.653e-10], [\[-0.01982, 0.02652\]],
    [Separate], [Midpoint], [P], [3440], [1.186e-39], [\[-27.68, 17\]],
    [Separate], [Sharpness], [P], [206.9], [3.514e-17], [\[-0.02187, 0.02773\]],
    [Separate], [Midpoint], [C $times$ P], [3420], [1.322e-39], [\[-57.06, 29.71\]],
    [Separate], [Sharpness], [C $times$ P], [0.1132], [0.7384], [\[-0.04683, 0.04107\]],
    [Shared], [Midpoint], [C], [528.1], [2.805e-24], [\[-29.12, 18.79\]],
    [Shared], [Sharpness], [C], [49.51], [1.911e-08], [\[-0.01957, 0.0259\]],
    [Shared], [Midpoint], [P], [505.6], [6.172e-24], [\[-27.14, 15.95\]],
    [Shared], [Sharpness], [P], [188.8], [1.571e-16], [\[-0.02147, 0.02725\]],
    [Shared], [Midpoint], [C $times$ P], [588.3], [3.911e-25], [\[-51.88, 28.38\]],
    [Shared], [Sharpness], [C $times$ P], [5.922], [0.01963], [\[-0.04608, 0.04043\]],
  )]
  , caption: [Exploratory parameter RM ANOVA. C denotes Viscereality minus Control, P denotes Inhale minus Exhale, and C $times$ P is the difference of phase effects. Each $F$ has (1,39) df. Intervals describe the corresponding mean contrast in cm or normalized sharpness (cm$""^(- 1)$), not the $F$ statistic.]
  , kind: table
  ) <study5:tab:parameter_anova>

]
With presentation order included, 2 of 36 Condition-moderation terms had conventional $p < .05$; 0 curve-refit intervals excluded zero. Table~#ref(<study5:tab:parameter_covariates>, supplement: none) reports all eight MAIA-2 dimensions and spatial-code change for both outcomes. Covariate slopes describe how Viscereality--Control parameter change varies per score point. The spatial model compares changes measured in the same participants; it cannot establish that spatial experience caused a PPS change. MAIA-2 is a baseline trait and is not an intervention mediator.

#block[
#figure(
  align(center)[#table(
    columns: 6,
    align: (left,left,right,right,left,left,),
    table.header([Outcome], [Covariate], [Shared $beta$], [Shared $p$], [Shared refit interval], [Separate refit interval],),
    table.hline(),
    [Midpoint], [Noticing], [0.9871], [0.4553], [\[-4.809, 8.077\]], [\[-5.616, 6.696\]],
    [Sharpness], [Noticing], [0.0003005], [0.5694], [\[-0.005266, 0.004824\]], [\[-0.005273, 0.004792\]],
    [Midpoint], [Not Distracting], [0.5153], [0.6182], [\[-5.035, 5.581\]], [\[-4.804, 4.921\]],
    [Sharpness], [Not Distracting], [0.000183], [0.6573], [\[-0.004333, 0.003912\]], [\[-0.004481, 0.003733\]],
    [Midpoint], [Not Worrying], [-0.5031], [0.594], [\[-5.1, 4.658\]], [\[-3.617, 4.317\]],
    [Sharpness], [Not Worrying], [0.0005136], [0.1676], [\[-0.003458, 0.00434\]], [\[-0.003553, 0.004325\]],
    [Midpoint], [Attention Regulation], [1.648], [0.1567], [\[-5.321, 7.479\]], [\[-5.998, 5.963\]],
    [Sharpness], [Attention Regulation], [-9.453e-05], [0.8408], [\[-0.004183, 0.005561\]], [\[-0.00424, 0.005532\]],
    [Midpoint], [Emotional Awareness], [1.5], [0.1738], [\[-5.789, 7.534\]], [\[-5.143, 4.996\]],
    [Sharpness], [Emotional Awareness], [-0.001219], [0.003739], [\[-0.005562, 0.004053\]], [\[-0.005692, 0.004245\]],
    [Midpoint], [Self Regulation], [-0.3935], [0.6941], [\[-5.395, 5.352\]], [\[-4.883, 4.225\]],
    [Sharpness], [Self Regulation], [-0.0003675], [0.3547], [\[-0.00447, 0.003697\]], [\[-0.004492, 0.003664\]],
    [Midpoint], [Body Listening], [-0.8171], [0.3499], [\[-5.361, 3.529\]], [\[-4.368, 3.732\]],
    [Sharpness], [Body Listening], [8.1e-05], [0.8173], [\[-0.004397, 0.002981\]], [\[-0.004298, 0.002911\]],
    [Midpoint], [Trusting], [1.258], [0.1279], [\[-3.552, 6.248\]], [\[-3.359, 3.962\]],
    [Sharpness], [Trusting], [-0.0005302], [0.1071], [\[-0.003926, 0.003041\]], [\[-0.003873, 0.003164\]],
    [Midpoint], [Spatial Change], [0.6596], [0.2095], [\[-2.264, 3.256\]], [\[-2.247, 2.528\]],
    [Sharpness], [Spatial Change], [9.266e-05], [0.6616], [\[-0.001929, 0.002606\]], [\[-0.001896, 0.002709\]],
  )]
  , caption: [Order-adjusted Condition $times$ covariate terms. Each MAIA-2 dimension and spatial delta enters a separate continuous-covariate model. Coefficients use cm or cm$""^(- 1)$ per score point. The companion also reports ordinary/HC3 uncertainty, both order specifications, between-person means, Phase and three-way moderation, ordinal-direction sensitivity and every recording exclusion.]
  , kind: table
  ) <study5:tab:parameter_covariates>

]
All 1,328 nominal ANOVA/ANCOVA terms across four linkage specifications and both plateau models were retained. Across that entire family, 2 refit intervals excluded zero: Shared plateaus, Midpoint, Phase by attention regulation, Exclude P011, without order adjustment: \[0.3911, 20.88\]; Shared plateaus, Midpoint, Phase by attention regulation, Exclude P011, with order adjustment: \[0.6976, 20.93\]. These isolated sensitivity results were absent from the both-excluded primary presentation and do not establish a mapping-robust association. Hierarchical intervals used 500 curve-refitting resamples per specification; these condition on the earlier RT-selected method and cleaning and do not estimate selection-adjusted coverage. The previously near-zero change-score reliability remains a central limitation for interpreting questionnaire associations. A better-fitting numerical sigmoid is insufficient to identify a physiological boundary or establish questionnaire influence.

#figure(image("../figures/study5_parameter_repeated_measures.png", width: 100%),
  caption: [
    Repeated-measures parameter analysis excluding both ambiguous records. Upper panels show the three within-person effects; lower panels show order-adjusted Condition moderation. Points and 95% hierarchical curve-refit intervals retain both plateau models. Sharpness is $1 \/ \( 4 s \)$ for logistic width $s$ in cm. These are fitted proxies with previously weak reliability.
  ]
)
<study5:fig:parameter_repeated_measures>

== Reproducibility and evidence limits
<reproducibility-and-evidence-limits>
All reported behavioral computations were executed in the marimo browser companion with Pyodide, Python 3.14.2, NumPy 2.4.3, SciPy 1.17.1, and Matplotlib 3.10.8. The archived browser download records input, code, and output SHA-256 hashes. Native reference checks independently verified random-intercept ML fits, cluster-robust linear and binomial coefficients/uncertainty, repeated-measures $F$ statistics, and JZS quadrature. Additional native references checked questionnaire alpha through its covariance identity, the exact ordinal sign test and interval, all 42 rank correlations, and all 16 moderation fits including ordinary and HC3 uncertainty. Independent long-format participant-intercept models verified the delta regression's Condition $times$ MAIA slope, standard error, $F$ statistic and $p$ value. Every questionnaire result was also compared across native and browser runtimes. For individual proxies, independent KernelReg smoothing and scalar least-squares grid objectives checked all 168 primary fits; weighted least squares checked shared plateaus conditionally, and SciPy independently checked correlations across both models and recording exclusions. Every individual result was compared across native and browser runtimes. A failed or unavailable check is distinguished from a computed null result.

The released CSVs do not contain waveforms, belt recordings, acquisition-version labels, collection dates, or the private provenance needed to identify two historically documented RT-onset variants. The browser analysis therefore does not rerun waveform timing, measured respiratory compliance, pilot-date classification, version-specific contrasts, or that source-definition exclusion. Historical source audits remain historical evidence, rather than new 42-person verification.
