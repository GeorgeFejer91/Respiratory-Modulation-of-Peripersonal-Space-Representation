# Segment 2 phase-direction audit and figure

This owner-requested analysis preserves the existing overall response-level
contrasts and adds the six exploratory paired trial-group estimates below.
It changes neither cleaning nor the fitted models.

## Owner extension: all main RT trial groups

The subsequent request separates raw AT trials at SOAs 300, 800, 1500, 2200 and
2700 ms, plus one pooled Baseline group. For each person/group/phase, average
conditions equally; pool baseline trials within condition/phase as before.
Calculate each person's delta as Inhale minus Exhale before averaging people.
Export all six phase means/deltas, their sample SDs, n and pointwise 95% t CIs.
These are exploratory descriptive contrasts; add no new p-value family or cleaning.
The six intervals are pointwise, not simultaneous/multiplicity-adjusted intervals.
Catch trials do not provide a comparable correct-hit target RT and remain excluded.
Owner visualization amendment (2026-10-23): make these six raw phase-delta groups
the main Segment 2 visualization, using stacked horizontal rainclouds. Keep raw
units and labels explicit; retain the corrected overall result/figure separately.
Each cloud uses Gaussian KDE with bandwidth 1.06 × sample SD × n^(−1/5), trimmed
to observed min/max and equal peak height. Suppress density for n<3 or zero SD.
Show median/quartile boxes and 1.5-IQR whiskers, all 40 participant deltas, and the
unchanged pointwise mean 95% t CI in a separate band. Vertical deterministic
offsets affect only placement. The browser renders HTML/SVG charts directly from verified numerical data, with
exact values, identity and units in a shared click/tap/keyboard inspector. Static
exports remain separate download alternatives; do not embed chart images.
Smoothing is descriptive; add no inferential test. Keep physiological-label limits.

- Inputs: the unchanged audited public CSV pair. Reuse `paper_analysis.clean`:
  recorded AT/Baseline hits, existing catch rule and participant ±2.5 sample-SD
  trimming. Exclude both unresolved linked recordings P011/P033 (primary40).
- Read the literal `Exhale` and `Inhale` strings throughout. The public-data
  release copies these labels without recoding them. This checks analysis direction
  against the release, not the acquisition system or actual breathing compliance;
  belt recordings are unavailable here.
- Within each person/condition/phase, average AT trials within each SOA and then
  weight the five SOAs equally. Average conditions equally, then people equally.
  Baseline uses all retained trials pooled within person/condition/phase, followed
  by equal condition weights. Require complete cells rather than silently dropping
  incomplete people. Retain the original four-cell source in the released inputs.
- Corrected RT is AT minus that matched baseline. All phase differences are
  **Inhale minus Exhale**; positive means slower RT during inhale. Segment 0's
  Baseline-minus-AT benefit display has the opposite correction sign.
- The selected main visual is `phase_raw_groups`; the corrected overall
  `phase_rt` figure remains a supplemental reference. This changes display order,
  not the preserved corrected overall inference. Keep all signed values and zero.
- Reproduce the existing three primary40 mean/Phase rows in
  `results/baseline_effects/response_tests.csv` before exporting. Retain its full
  family/sensitivity link. Two-sided p values remain unadjusted; no new test is
  selected from the direction or significance. The corrected result is inconclusive.
- Export SVG, PNG, PDF, exact participant phase values, summary statistics, a
  short evidence report and hashes of inputs/source/outputs with runtime versions.
  This is a native figure shown in the browser; no browser fitting is claimed.
- Independently compare the literal-trial aggregation to the existing pandas
  participant-cell preparation, check signed subtraction and saved estimates/CIs,
  then inspect the actual figure and rendered page at desktop/phone sizes.
