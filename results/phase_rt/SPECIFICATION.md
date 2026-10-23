# Segment 2 phase-direction audit and figure

This owner-requested visualization rechecks the existing exploratory response-level
contrasts; it adds no model, cleaning choice or inferential comparison.

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
- Panel A: raw AT participant pairs and phase means with marginal 95% t CIs.
  Start the nonnegative raw RT axis at zero. Panel B: all participant phase
  differences for raw AT, baseline, and AT-minus-baseline, with paired mean 95%
  t CIs, a visible zero reference, and all negative/positive observations retained.
  Horizontal offsets only separate points; they are deterministic, not data values.
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
