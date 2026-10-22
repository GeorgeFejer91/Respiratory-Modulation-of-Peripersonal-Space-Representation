# Participant-specific RT normalization in Segment 0

The owner requested a descriptive, participant-specific 0–1 display on
2026-10-23, subsequently allowing multiple normalization methods. **Normalize RT**
offers within-person min–max scaling and z-scoring with explicit method labels.

## Research and choice

A within-participant z-score subtracts that person's mean and divides by their
SD: `z = (RT − mean_i) / SD_i`. It expresses relative RT in SD units, with
values on either side of zero; it does not constrain values to 0–1. RT research
has used trial-level z-transforms before condition averaging. Simulations show
that z-score costs can reduce some speed-related confounding but do not remove
all general or strategic slowing effects. See
[Hedge, Powell & Sumner (2018), author-hosted published paper](https://orca.cardiff.ac.uk/id/eprint/114139/8/Hedge.%20Psychology%20and%20aging.pub%20pdf.pdf)
and the [standard-score definition](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html).

For the requested bounded display, use `u = (value − min_i) / (max_i − min_i)`.
This maps each participant's observed minimum/maximum to 0/1, preserving their
relative spacing. This formula and its sensitivity to extreme values are
documented in [MinMaxScaler](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.MinMaxScaler.html).
This is a display choice matching the owner's requested range, not evidence
that min–max scaling is the preferred inferential RT method. Z-scoring also
does not guarantee a Gaussian RT distribution; the b-CFS findings in
[Gayet & Stein (2017)](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2017.00437/full)
illustrate task-dependent results and should not be generalized as validation
of this study's display.

## Exact display contract

- Estimate each person's reference distribution from all their retained AT
  trials, pooling both conditions, both phases and all SOAs. Compute their
  mean, sample SD (n−1), minimum and maximum. Trial count determines the
  reference distribution; participants remain equally weighted in summaries.
- Use those same references to transform the existing 20 cell means per person.
  Both transforms are linear within a person, so transforming cell means equals
  transforming every trial first and then averaging within each cell. References
  use trial variation, not just variation between the 20 cell means.
- With baseline correction off, scale uncorrected cell RTs. With it on, first
  form Baseline − AT RT for every retained trial, using the established
  participant × Condition × Phase baseline mean, and scale those benefits.
- Estimate one reference distribution per participant before cohort/series
  selection. Never standardize separately per condition, phase or SOA, and
  never renormalize visible series.
- Omit missing trial values from estimation; retain missing cells. An empty or
  constant range, or zero/undefined SD, produces missing normalized scores.
  No new exclusions, trimming or imputation are introduced.
- Aggregate normalized cells with equal participant weight. Display sample SD
  across participants and nonmissing n; n<2 has undefined SD. SD whiskers can
  extend outside 0–1 and must not be clipped or called confidence intervals.
- Raw normalized scores increase with slower RT; normalized baseline benefits
  increase with greater benefit. For min–max, zero is the observed minimum,
  not zero milliseconds or absence of facilitation. A value of 0.5 is the
  midpoint of that person's observed range, not a probability or half-speed.
- Z-scores are measured in within-participant SD units and may be negative or
  exceed 1. They remove each participant's overall mean and SD; they do not
  force a Gaussian distribution. Their CSV names are `reaction_time_z` and
  `baseline_benefit_z`; 0–1 names end in `_norm` instead.
- Default to normalization off, min–max selected, baseline correction on.
  Load trial reference metadata only when normalization is requested. Preserve
  source data, historical analyses and the original AT − Baseline field.

Min–max scaling removes each person's overall level and range. It can magnify
small noisy ranges and depends on empirical extremes. It supports descriptive
relative-pattern comparisons, not claims of equal absolute speed, equal
measurement precision, identified PPS boundaries or corrected causal effects.
Inferential analyses retain their declared methods and millisecond references.

Sources opened on 2026-10-23 through web search/fetch. Consensus was attempted
but required reauthentication. The Cardiff PDF and official scaler documentation
were accessible; PubMed/PMC access was rate-limited/challenged, so full-text RT
claims above use the accessible Cardiff paper and publisher-hosted b-CFS paper.
