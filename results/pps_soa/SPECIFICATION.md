# Segment 1: basic SOA–RT check

Owner request, 2026-10-23: first test whether RT differs by SOA, using the
simplest appropriate analysis, an observed-data graph and APA-style statistics.
This is an exploratory initial phenomenon check, not a new registration claim.
Specification written before running this extension.

- Outcome: retained, unnormalized, uncorrected Audio–Tactile RT in milliseconds.
- Reuse `paper_analysis.clean`: recorded hits/responses, Catch false-alarm
  exclusion >30%, participant pooled AT/Baseline mean ±2.5 sample SD. No new
  trial filter, smoothing, cutoff or imputation. Keep partial sessions.
- Primary cohort excludes both linked records P011/P033. Show the full release
  and each single exclusion as labelled linkage sensitivities, never as four
  independent confirmations.
- Calculate each participant × Condition × Phase × SOA cell mean, then average
  the four Condition × Phase cells equally at each SOA. Use only participants
  with all 20 cells; list any incomplete exclusions. People, not trials, are the
  independent units. Preserve all four cells in the source download.
- One primary omnibus null: the five population mean RTs at 300, 800, 1500,
  2200 and 2700 ms are equal. Use the existing repeated-measures ANOVA SOA main
  effect, equivalent to a one-factor five-level within-person ANOVA on those
  averages. Always use Greenhouse–Geisser corrected degrees of freedom and p.
  Report F, corrected df, p, epsilon and partial eta squared. No post hoc tests
  or experimental interaction tests in this segment. P values are unadjusted.
- Show every participant's five means, the equal-person mean and pointwise
  95% t confidence intervals (n−1 df). These are marginal mean intervals, not
  within-person difference intervals or simultaneous bands. Start Y at zero.
  X uses actual SOA spacing; connecting segments are visual guides, not fits.
- Report the prespecified descriptive endpoint contrast RT(2700) − RT(300),
  its paired 95% t CI, and all five M/SD/median/n summaries. No endpoint p test.
  Inspect paired profiles and four orthogonal SOA contrast Q–Q plots; report
  contrast Shapiro diagnostics descriptively without changing the test/filter.
- Verify F/uncorrected df/p independently with statsmodels AnovaRM, epsilon
  with the projected sample covariance, means with pandas, and unchanged F
  after subtracting each participant's matched Condition × Phase baseline.
  The constant baseline subtraction cannot change within-person SOA contrasts
  under this complete, equal-cell aggregation. Do not claim baseline interaction
  or spatial specificity from this invariance.
- This check establishes SOA dependence if supported. Temporal expectancy,
  foreperiod and other explanations remain possible. It cannot establish a
  specifically spatial PPS mechanism, a sigmoid or a physiological boundary.
- Native calculation with saved results displayed on the landing page; do not
  claim that the browser recomputes this test. Download inputs/settings/hashes,
  person-cell values, statistics and static figures. Historical results stay fixed.
