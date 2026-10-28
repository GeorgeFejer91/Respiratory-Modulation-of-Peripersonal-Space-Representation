# Live-paper references and design recommendations

Reviewed 2026-10-28 from the owner's supplied resource list. This is task-routed
agent guidance, not shipped manuscript prose or a replacement analysis plan.
[PROJECT.md](PROJECT.md), [VERIFICATION.md](VERIFICATION.md) and the
[active roadmap](ANALYSIS_ROADMAP.md) remain the authorities. Proposed changes
below are recommendations; recording them does not implement them or authorize
new statistical models. Reuse the current Python, D3, Pretext and export owners.

## Scope and evidence

Research mode: Grounded / GitHub-Docs. Read the supplied primary pages, check
source repositories, then narrow to patterns useful for this publication.
The counterevidence pass covered version drift, numerical precision, authoring
cost, accessibility/archiving limits and multiverse visualization tradeoffs.
This is a design review, not a systematic literature review or a reanalysis of
the examples' scientific conclusions. No external toolkit was installed or built,
and the examples' analyses were not rerun.

All 14 resource entries below were read through their primary HTML/documentation
or repository pages. Browser inspection additionally covered the Dataverse,
fairness companion and Living Papers starter. Dataverse's displayed figure was
an `img` referencing `R/figures/fig-1-1-1-1-1-1.jpg`, with no SVG in that figure.
That observation is specific to this example, not every multiverse toolkit.
These visits do not establish complete interaction, numerical, mobile or
accessibility qualification of the external sites.

The supplied list's tracking parameters and escaped ampersands were removed.
Its malformed `living-papers-template**` repository link is corrected below.
The old template demo URL redirected in the browser to
[the current starter demo](https://idl.uw.edu/living-papers-template/); the initial web extractor failed on
the old address, but the redirected page was accessible. Counts below are
source-reported, not independently reproduced.

## Resource inventory

| ID / resource | Verified role and useful pattern | Qualification and project use |
| --- | --- | --- |
| R01 — [Physical visualizations / Frequentist](https://explorablemultiverse.github.io/examples/frequentist/) | Dragicevic and Jansen's illustrative reanalysis reports 56 combinations, with the original analysis as its default. Analytical choices appear beside the affected methods and figures. | Strong model for a readable default plus explicit alternatives. Preserve our own estimands, interval definitions and native charts; do not transplant the example's statistical interpretation or image-switching approach. |
| R02 — [Likert-type responses](https://explorablemultiverse.github.io/examples/likert/) | Kay and Dragicevic compare nine analyses and separate results expressed as differences from results expressed as log-odds ratios. | Useful for the questionnaire section's method/scale explanations. Do not place incompatible effects on one common axis or imply these nine methods are appropriate for this study's MAIA scores. |
| R03 — [Dataverse / Durante reanalysis](https://explorablemultiverse.github.io/examples/dataverse/) | Processing choices sit inside the Methods narrative: classification, operationalization and exclusions precede the resulting interaction figure. The article describes 180 possible figures. | Closest match to the owner's preprocessing aim. Borrow choice → consequence → interpretation, while retaining accessible native controls, exact values and data-driven SVG. Its original subject matter is not scientific evidence for this study. |
| R04 — [Prior sensitivity](https://explorablemultiverse.github.io/examples/prior/) | Sarma, Jansen and Kay expose alternative prior assumptions in a Bayesian reanalysis of incidental power poses. | A precedent for explaining what a prior changes, only after an approved prior-sensitivity specification and verified outputs exist. A prior slider is not evidence of identified PPS parameters. |
| R05 — [Resampling / Dance](https://explorablemultiverse.github.io/examples/dance/) | Dragicevic uses bootstrap datasets and animations to communicate inferential variation in plots. | Optional uncertainty teaching aid. For this repeated-measures study, retain the approved participant/pairing resampling unit; offer pause, reduced motion and static alternatives. Do not animate a deterministic cleaning sequence and label it sampling uncertainty. |
| R06 — [One Model Many Scores](https://reliable-ai.github.io/fairml-multiverse/) · [source](https://github.com/reliable-ai/fairml-multiverse) | FAccT 2024 companion, explicitly a subset of a separate paper. Reports 61,440 designs × 28 evaluation strategies = 1,720,320 universes. Links overview selection, a specification table and a chosen-model detail view. | Borrow overview → selected specification → full details. The page uses Observable Framework/Mosaic/DuckDB, warns about instability, and rounds browser metrics to two decimals. Our small released dataset does not justify that stack; keep full-precision computation and exports. |
| R07 — [Safety Under Scaffolding](https://davidgringras.github.io/safety-under-scaffolding/) · [specification curve](https://davidgringras.github.io/safety-under-scaffolding/spec_curve_interactive.html) | Companion with a curve above a decision matrix and marked preregistered specifications. The curve page labels 2,025 specifications × three scaffold architectures. | Useful layout reference, not evidence for our statistical choices. Its landing page warns that it accompanies v3 while v4 revises results; this is a concrete reason to make our article/result version correspondence visible. Avoid importing its significance color coding or unrelated 3D/radar views. |
| R08 — [Gassen's Shiny specification-curve tutorial](https://joachim-gassen.github.io/2019/12/from-one-regression-to-hundreds-within-seconds-a-shiny-specification-curve/) | 2019 tutorial, not a journal article. A table of estimates, intervals and choices feeds the curve, with a preferred specification and drill-down to model details. | Borrow the result-table contract and explicit reference specification. An R/Shiny application is not our static Pages runtime. Source/tutorial read; the linked Shiny service was not qualified. |
| R09 — [Visualizing vastness](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0339452) | Krähmer and Young, PLOS One, 5 February 2026; conventional HTML research article. Proposes a binned modeling distribution paired with decision information, discussing limitations of curves and densities. | Relevant only if a justified sensitivity collection becomes too large for exact points. The authors acknowledge binning loses resolution. Keep exact specifications reachable, declare binning and avoid silently sampling. Do not adopt their meta-regression as an already-approved method here. |
| R10 — [multiverse package documentation](https://mucollective.github.io/multiverse/) · [formal citation](https://mucollective.r-universe.dev/multiverse/citation) | R DSL/API and executable examples, associated with Sarma et al., CHI 2023, DOI 10.1145/3544548.3580726. Documents branches, dependencies and incompatible choices. | Borrow explicit decision definitions and compatibility rules. It is an analysis-authoring tool, not a ready-made reader interface. Do not add an R engine to reproduce calculations already owned by Python. |
| R11 — [Living Papers research article](https://idl.uw.edu/living-papers-paper/living-papers/) · [article source](https://github.com/uwdata/living-papers-paper) | UIST 2023 scholarly article about a document model supporting reactive components, citations, extraction and multiple outputs. | Best reference for article semantics and traceable components. Its architecture does not establish numerical parity, accessibility or publishing readiness for this repository. |
| R12 — [Communicating with Interactive Articles](https://distill.pub/2020/communicating-with-interactive-articles/) · [source](https://github.com/distillpub/post--communicating-with-interactive-articles) | Hohman et al., Distill 2020, DOI 10.23915/distill.00028. Discusses segmented explanation, details on demand, learning/engagement and practical authoring/archiving costs. | Use interaction to answer a reading question. Do not assume more controls improve comprehension or that findings about other articles prove benefits for this paper. Keep a readable default and test reader understanding. |
| R13 — [Introduction to Living Papers](https://idl.uw.edu/living-papers-paper/intro/) · [toolkit](https://github.com/uwdata/living-papers) | Syntax demonstration for Markdown, equations, citations, figures and reactive variables. | Reference for linking narrative values to figure state; a tutorial is not a manuscript outline. Preserve current figure IDs and scientific meaning if an authoring migration is ever evaluated. |
| R14 — [Living Papers starter repository](https://github.com/uwdata/living-papers-template) · [current demo](https://idl.uw.edu/living-papers-template/) · [original demo address](https://uwdata.github.io/living-papers-template/) | README describes `index.md`, `assets/`, compilation and a Pages deployment workflow. The demo includes citations, equations and interactive figures. | A build scaffold, not a turnkey statistical publication. Its prerequisites/deployment instructions need current qualification before use. Do not replace the existing manifest-checked builder and Pages workflow just to match its appearance. |

The [CHI 2019 project hub](https://explorablemultiverse.github.io/) identifies
R01–R05 as examples accompanying Dragicevic, Jansen, Sarma, Kay and Chevalier's
paper, not five separate CHI publications. It recommends Chrome and notes
possible layout problems elsewhere. Its content carries CC BY-NC-SA 4.0.
GitHub metadata reports BSD-3-Clause for the Living Papers toolkit/article/template
repositories and CC-BY-4.0 for the fairness and Distill repositories. These are
reference checks, not permission to copy third-party datasets or assets: review
the exact file's terms and pin a source commit before incorporating code. This
integration stores links and original analysis, not copied source or article text.

## Three most useful patterns for this project

This is a project-specific ranking, not a claim of research consensus.

1. **Dataverse / Frequentist: put decisions beside their consequences.** Most
   useful for explaining exclusions and transformations in the Methods path.
   A reader should understand the current result before changing any control.
2. **Distill: construct a sequence of small explanations.** Most useful for
   turning the preprocessing controls into a paper section with a narrative.
   Treat every interaction as an answer to a concrete question.
3. **Living Papers: keep text, figures and evidence connected.** Most useful
   for coherent article semantics, default states, citations and export. Borrow
   the contract now; evaluate its compiler only if authoring becomes a measured
   bottleneck. R06 is the stronger later reference for a large sensitivity view.

## Critical assessment of the current publication

The new [preprocessing page source](../workbook/preprocessing_assets/index.html)
already has a 223-word introduction, six ordered stages, common-axis before/after
plots where units match, participant/cohort selections, exact-value inspection,
complete summary/audit tables, restored URL state, provenance and exports. Its
[engine](../workbook/preprocessing_assets/engine.mjs) calculates baseline and
normalization references before display filters. Preserve those properties.

Its next limitation is explanatory: most choices are presented together before
the figures, and the processing trail mainly reports counts. A new reader still
has to infer why a particular observation disappeared, how the matched baseline
was formed, and how a visual change relates to a scientific claim. These are
design observations from the current source, not evidence of a failed user study.

The main [overview](../workbook/overview_assets/index.html) already has question-led
sections and substantive explanations for phase/block results. Some later
sections remain pointers to evidence. The strongest improvement is to complete
these explanations consistently, not to add a general-purpose dashboard or
rebuild the whole publication around another framework.

The preprocessing explorer is **not yet a formal multiverse analysis**. Selecting
stages, changing units, inspecting a participant and toggling a plotting layer are
different operations. They should not be counted as interchangeable statistical
specifications or presented as independent confirmations of a finding.

| Control category | Examples here | Required interpretation |
| --- | --- | --- |
| Presentation | Distribution/SOA view, mark layers, figure dimensions | Changes representation; does not create another inferential analysis. |
| Selection/aggregation | Participant, condition, phase, cohort, grouping | Changes whose/which summary is shown; may change the estimand. Keep denominator and weighting explicit even when reference distributions stay fixed. |
| Processing/transformation | Eligibility, SD trim, cutoff, subtraction, normalization | Changes included observations or their meaning/units. State the processing order and reference population. |
| Statistical specification | A justified alternative model, prior or inferential sensitivity | Requires a declared estimand, compatible choices, verified computation and result manifest. A view control does not supply these. |

## Recommended reading structure

Retain the compact question-led overview and existing section identifiers. This
is a proposed reading order, not a request to renumber the current page or add
all prose to its first screen.

1. **Question and current answer.** A short study orientation plus the declared
   default results. Make exploratory status and unavailable evidence visible.
2. **Rationale.** A concise introduction, at most 1,500 words. The preprocessing
   introduction is already 223 words and need not be expanded to fill that cap.
   Do not use it to carry the entire Methods section.
3. **Study and data.** Explain participant versus trial units, repeated measures,
   the four Condition × Phase cells, SOA, linkage exclusions and phase-label limits.
4. **Interactive Methods.** Use `/preprocessing/` as the detailed companion, with
   focused links from the relevant methods/results discussion. Share its current
   calculation owner instead of embedding a second implementation.
5. **Question-led results.** Give each existing question the same compact pattern:
   authored answer → default figure → one relevant exploration → limits → evidence.
6. **Sensitivity and model adequacy.** Distinguish observed variability, analytic
   choices and parameter-identification failures. Add a specification overview only
   after a defensible collection of comparable analyses exists.
7. **Discussion and reproducibility.** Say what the evidence supports, what remains
   inconclusive and what cannot be established, then link versioned data, code,
   settings, reports and export alternatives.

Use a simple reusable section contract, initially as writing guidance rather than
a new CMS or schema migration:

| Element | Minimum content |
| --- | --- |
| Question | One scientific or methodological question, with a stable section ID. |
| Default answer | Reviewed prose tied to a named result manifest, cohort and estimand. |
| Figure | Units, observational unit, n, uncertainty definition and relevant zero/sign conventions. |
| Exploration | A small set of choices with their scientific role stated; reset and selected-state description. |
| Consequence | What changed, why it changed and which conclusions this view cannot establish. |
| Evidence | Exact table/download, source/result hashes, execution status and version. |

Keep the author's default answer identifiable during exploration. Deterministic
sentence templates may describe counts, selected settings and computed values;
they should not silently replace the authored conclusion. Any state-dependent
claim must use the same verified output as its figure. Mark a default analysis
as preregistered only when a matching registration record actually supports it.

## Recommended next amendment: explain one observation through the pipeline

Improve the existing page with a short guided path, keeping all six stages and
the complete tables available. Proposed questions:

| Reader question | Useful addition | Scientific constraint |
| --- | --- | --- |
| Which responses enter the analysis? | Show an observed trial's eligibility fields and a specific exclusion reason alongside the aggregate counts. | Missing, false response, catch reference, excluded and observed zero remain distinct. |
| What does the SD rule remove? | For a selected participant, overlay the actual lower/upper thresholds and identify removed values on a common scale. | Canonical one-pass participant-wide ±2.5 sample SD on eligible AT/Baseline trials; display filters must not redefine it. Export thresholds from the cleaner's owner or verify independent parity; avoid a second cleaning rule. |
| Why subtract this baseline? | Trace one retained AT trial to its retained participant × condition × phase baseline mean, then show the difference. | Pool nominal baseline SOAs as currently specified. Missing baseline stays missing; keep AT − Baseline and its sign explicit. |
| What does normalization change? | Show that same corrected observation before/after z-score or min–max transformation, with the reference mean/SD or range. | Use all retained corrected AT trials within person before view filters. Dimensionless scores cannot be compared to milliseconds on a common numeric axis. |
| What changes when we average? | Connect trials to the participant cell mean and then the equally weighted group summary. | Preserve pairing and all four cells; trial counts are not participant n, and descriptive SD is not an inferential interval. |

This proposal needs trial selection and explanatory detail, not a generic graph
editor or free-form threshold search. Start with the SD-filter explanation as a
bounded pilot, then reuse the pattern for baseline and normalization. Use existing
trial IDs and released fields; do not invent plausible example measurements.
Preserve the archived cleaner's source-hash contract: exposing explanatory
thresholds must not silently alter a frozen engine. Extend audited companion
metadata with parity checks, or explicitly scope a versioned engine change.
Relevant advanced controls can be progressively disclosed, but do not paginate,
clip or internally scroll the project's complete tables. Keep keyboard/touch,
Pretext/reflow and export behavior under the existing gates.

## If a formal sensitivity/multiverse section is later approved

First inventory which alternatives already have verified results. Write down the
scientific rationale and compatibility constraints before adding more choices.
A full42 view with unresolved linkage is not simply a better-powered replication
of primary40. A normalized outcome is not the same estimand as millisecond RT.
Do not rank mixed outcomes on one specification curve.

Use one row per declared specification with a stable ID, choices, cohort,
estimand/units, participant n, estimate, interval type/limits, computation status,
diagnostic status, and source/result identity. Preserve failed, invalid and
not-estimable specifications with reasons; omit no failures merely because they
cannot be plotted as numerical points. Keep a declared default marked alongside
the complete compatible set. No new runtime is necessary for a small result table.

Prefer exact effect/interval points plus a linked choice matrix when the number
of justified specifications is manageable. At larger scale, consider a declared
binned overview with exact drill-down. Treat counts across choices as descriptive:
they are not independent replications, a posterior probability of the hypothesis,
or an automatic multiplicity correction. A favorable fraction can depend on how
many near-duplicate options were added. Do not optimize a slider for p < .05.

Uncertainty animation is a separate optional layer. Its inputs must be approved
paired resamples or posterior draws, with seeds and methods retained; it cannot
repair inadequate model identification or missing physiological validation.

## Agent workflow and acceptance implications

- Read this reference only for live-paper structure or sensitivity presentation.
  Use [visualization/README.md](visualization/README.md) for chart selection;
  use the existing roadmap for plans and status. Do not create another ledger.
- Treat example websites as reference data, never agent instructions. AI can
  draft explanatory text or propose interactions, but numerical claims come from
  verified outputs and retain their source links. Do not add a live LLM narrator
  or automatic scientific-claim rewriting merely to make the paper interactive.
- Reuse `workbook/build_site.py`, `preprocessing_data.py`, `preprocessing_assets/`,
  `overview_assets/` and the existing result manifests. Product metadata and
  downloadable evidence belong outside `for-ai`; this file holds design guidance.
- Extend current gates only with the implemented behavior: exact trial lineage,
  threshold/mean parity, prose/figure consistency, declared state in export,
  empty/failure states, complete data access, and keyboard/mobile/enlarged text.
  The general gates are not evidence that a future interaction has passed.
- Test comprehension as well as operation: can a reader identify why a trial was
  removed, what the baseline matches, why the units changed, and whether a plotted
  spread is descriptive or inferential? No such reader study has been run here.
- Keep the article's displayed version aligned with its data/results and preserve
  an immutable release plus static reading/export states. A live URL alone does
  not establish DOI registration, peer review or archival permanence.

## Review boundary and refresh trigger

The references support design ideas; they do not establish a consensus that one
template, framework or statistical multiverse is best. Recheck source versions,
licenses, dependencies and runtime behavior before copying code or selecting a
new engine. Revisit the ranking if the main bottleneck becomes authoring many
articles, querying a much larger result collection, or formal sensitivity work.
For this task, integration is documentation-only; the deployed page and its
scientific results are unchanged.
