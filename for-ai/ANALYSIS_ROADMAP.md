# Analysis and living-publication roadmap

## Active goal — GitHub Pages as the analysis workspace and living preprint

### Completed amendment — separate graph display and error controls

Owner request (2026-10-23): style Condition/Phase like the combinable chart
controls and distinguish graph display layers from error-bar/whisker settings.

- [x] Keep native grouping checkboxes with matching selected-button styling;
  separate Graph display from Error bars / whiskers, move the error metric beside
  its independent Whiskers toggle and give mean points a stable, precise label.
- [x] Verify all 64 display/whisker combinations, independently inspect whiskers
  by keyboard, preserve table/downloads, pooling, corrections and normalization.
  The 71-test pinned workbook suite, 270 independent JavaScript/pandas cases,
  error-metric, chart-layer, pivot and overview browser gates pass locally.
  Desktop/phone screenshots are visually checked; real Pretext, eight viewports,
  long localized labels, 200% text and spacing are covered in Chromium. Physical
  Safari and screen readers remain untested. RTK is unavailable; bounded native
  commands are used.
- [x] Commit/push, verify the exact Pages deployment and live controls.

Work started from clean main `1740166`. Source `ad7ccd7` and hover-contrast
correction `a2fde56` are integrated and pushed on main; the local task branch
`codex/graph-control-groups` is retained. Build/native checks use the existing
pinned `.venv` and UTF-8. [Actions run 40004663639](https://github.com/GeorgeFejer91/Respiratory-Modulation-of-Peripersonal-Space-Representation/actions/runs/40004663639)
passed the full fixed analyses, independent numerical validation and deployment
of `a2fde56`. Four served pivot assets match the tested production build exactly;
all 64 display/whisker combinations, error-metric and overview gates pass live,
including the selected-button hover regression. The live control screenshot is visually
checked. No scientific inputs, methods or saved results changed. This evidence-only
checkpoint changes no served artifact. No task blocker remains; next action is
the broader scientific and living-publication checklist, which stays open.

### Completed amendment — A4 publication preview default

Owner request (2026-10-23): start desktop publication content at A4 portrait width,
excluding navigation, while retaining reader sizing. Use one responsive 210 CSS mm
column for text, figures and the embedded explorer, with the shared border owner
for whole-column resizing/reset. Keep individual sizing and phone reflow.

- [x] Implement the default, accessible width border and text remeasurement on
  content resizing; update the existing browser gate for A4, widening/narrowing,
  reset and responsive containment.
- [x] Production build and 71 workbook tests pass. Local overview, border,
  exact-point and error-metric browser checks pass, including real Pretext,
  phone/landscape, enlarged text and spacing. RTK remains unavailable; use the
  documented bounded native-shell fallback.
- [x] Local chart-layer (all 32 combinations), phase-explorer (all 32), table-copy
  and visual desktop/phase/phone checks pass; self-review, whitespace and context
  safety gates pass. Complete tables and original chart/data values are preserved.
- [x] Commit/push, follow the exact Pages deployment and check live behavior.
  The broader goal stays open.

Work started from clean main at `f13b249`. Source `49a25e6` is pushed to main;
Actions run `39998393501` passed build, fixed analysis, independent validation and
Pages deployment. Live border/A4 and full overview checks pass. Landing HTML,
CSS, overview script, resize owner and text-fit owner match the tested production
build after newline normalization. Citation checks also pass locally. No data,
scientific outputs or analysis methods changed; no task blocker remains. Physical
Safari and screen readers remain untested. Next action: resume the broader
scientific/publication checklist; this formatting amendment is complete.

### Completed amendment — focused D3 controls for Segment 2

Owner request (2026-10-23): use one supplied plotting toolbox and give Segment 2
relevant flexibility comparable to Segment 0. Reuse this chart worktree and the
shared point inspector/resize/Pretext owners. D3 7.9.0 will own the Segment 2 SVG
scales, data joins and density geometry, bundled locally with license/provenance.

- [x] Keep raw six-group rainclouds as default; add trial-group and independent
  dot/density/box/mean/pointwise-CI controls, reset, current-view CSV/SVG exports.
- [x] Offer matched-baseline-corrected paired deltas for five AT SOAs. Derive
  phase values from the verified participant groups and reuse the existing paired
  t-interval method at build time; independently compare with Condition × Phase
  participant cells. No new p values, exclusions, fitting or normalization.
- [x] Verify all control combinations, exact points/exports, empty states,
  mobile/enlarged-text/Pretext, independent review, regression gates and the exact
  deployed source/live behavior. Keep the wider publication goal open.

Owner follow-up: phrase Segment 2 as a scientific general-RT question, embed a
mini literature review with APA author–year/full-reference popovers, and add an
end References segment. Preserve the statistical result and avoid causal or
synchrony-perception claims. Verify citation identity/access, positive and contrary
studies, keyboard/focus, DOI/fallback links and enlarged-text rendering. Consensus
reauthentication was requested; only the in-app browser is connected and the login
handoff is open. Continue independent work with checked primary sources.

Implementation choice: a small native control area above the existing figure;
all layers start on, trial types retain fixed labels/colors/order. Corrected view
omits the self-subtracted baseline and explains why. Original saved statistics,
cohort, cleaning and static downloads stay fixed. Integrated newer main cleanup
(no supplemental graph/trailing link list), error metrics and table-below layout.
Local evidence: production build, 71 workbook tests, 270 independent Python/JS
comparisons, all32 phase-layer combinations, raw/corrected/CSV/SVG/empty/reset,
citation/focus/reflow, overview/point/border/error-metric browser checks pass.
Desktop/phone/raw/corrected/citation renders inspected. Review found and verified
a fix for CI-only inspection and dynamic count labels; final review has no
material findings. Physical Safari and screen readers remain untested.
Source `85fc18e` is pushed to main and the retained chart branch. Actions run
`39975177111` passed the complete analysis, independent numerical validation and
Pages deployment. Live phase32/citation/overview/point/border checks pass. The
new chart, citation code, D3/license and landing HTML match the validated build
after newline normalization; the full numerical payload matches exactly as data.
The first live border checks exposed a harness startup race (count before chart
readiness); moving the existing ready wait before that count fixes the gate,
which then passes live. This follow-up changes only verification/state, no served
asset. Consensus still returns UNAUTHORIZED; the regular browser is not connected
to available UI tools. The connection-page/login handoff was opened in-app and
the exact connection link supplied for the owner’s regular browser. Primary
publisher/PMC sources and Crossref metadata support the review independently.
Next action: resume the broader scientific/publication checklist; Consensus
needs manual reconnection if requested for further searches. The wider goal is open.

### Completed cleanup — remove the supplemental Segment 2 block

Owner request (2026-10-23): remove the screenshot's corrected-overall comparison
and trailing explanatory paragraph/link list as clutter. Keep the main raincloud,
corrected phase answer and archived evidence unchanged. This supersedes the
supplemental-disclosure portion of the earlier raincloud amendment below.

- [x] Remove the block, unused renderer/styles and unused overall chart payload.
  Adapt existing browser gates to require its absence and verify archived CSV bytes.
- [x] Production build, all 70 workbook tests, overview/point/border browser
  gates, rendered desktop review, context/safety and whitespace checks pass.
- [x] Push cleanup source 8f4d523 to main and verify the remote SHA. Live
  overview/point gates pass; HTML, CSS, both chart scripts and numerical payload
  match the tested production build after newline normalization.
- [ ] Resolve the superseded deployment status with the newer combined source
  under the active D3 amendment above; do not claim this workflow succeeded.

Work is on main from 67e2bdc; no pre-existing changes were present. Four viewport
layouts, 200% text/spacing, real Pretext, keyboard/touch and all 240 raincloud
values pass. The Windows test server required an explicit JavaScript MIME type
for .mjs; the existing project Python environment supplies statsmodels. No source
data or native statistical results changed. The wider scientific/publication
goal stays open. Cleanup CI completed its build and full numerical validations;
its deploy step reported success, but concurrent main update 85fc18e superseded
the run and GitHub recorded cancellation/deployment error. The served cleanup
was independently verified; the combined-source publication remains the active
D3 amendment's next action. At handoff main includes that concurrent integration,
which preserves this removal; no unrelated work was edited.
RTK is unavailable; bounded native commands are the documented fallback.

### Completed formatting rule — Pretext accordion stretch

Owner request (2026-10-23): make Uncodixfy Pretext accordion-stretch logic the
general live-page formatting rule to prevent text overflow.

- [x] Record the bounded-panel contract in `PROJECT.md`, require its skill route
  in `SKILLS.md`, and add Pretext plus rendered overflow/resize acceptance checks
  to `VERIFICATION.md`. Preserve document flow for long text and complete tables.
- [x] Review the policy diff against the installed skill and existing document/
  chooser scroll contracts; context/safety and whitespace checks pass. Referenced
  project documents and installed stretch guidance exist.

This is a protocol-only change; no runtime layout or deployment claim follows.
The Pages path filter excludes these edits, so no site rebuild is required.
Observed baseline: clean `main` at `f4900c8`, synchronized with `origin/main`;
only these four control-plane files are task-owned. Commit/push follows the
standing workflow, with exact remote-SHA verification at handoff. RTK was
unavailable; bounded native shell commands were used. No blocker for this rule.
Next action: apply the rule and its rendered gate to subsequent live-page layout
changes; continue the existing scientific/publication checklist. Overall goal open.

### Completed amendment — independent error metric and numeric error cells

Owner request (2026-10-23): select SD, confidence intervals or another standard
error measure independently, and put the selected error in separate responsive
table cells. Reuse the existing pooled participant means and shared chart owner.

- [x] Add SD (default), SE, pointwise 95% Student-t CI and none. Use participant
  sample SD/n after within-person pooling; undefined n < 2 and zero spread remain
  distinct. Keep marginal uncertainty separate from paired-effect inference and
  baseline-estimation uncertainty; no fixed analysis/model changes.
- [x] Separate numeric mean/SD/SE cells and lower/upper CI cells, full-precision
  rectangular clipboard export, stable complete CSV with every error measure,
  labelled narrow-screen reflow and content-fit table border resizing.
- [x] Complete final local gates, authorized commit/integration/push and exact
  CI/Pages/live verification; record source/remote state here.

Plan/evidence: bounded change in existing pivot engine, app, HTML/CSS and chart;
the existing 270 JavaScript/pandas cases and 516 SciPy interval fixtures pass.
All 70 workbook tests and production build pass (Windows requires UTF-8 mode).
Local interval/copy/pivot/overview/border/point/layer gates pass. Independent review
found one stale hidden-layer caption, fixed with a regression assertion; final
review found no remaining actionable issues. Source `f4900c8` was fast-forwarded
to main and its remote SHA verified. Actions run `39972049299` passed the complete
fixed-analysis/numerical-validation build and Pages deployment for that source.
Live interval, clipboard, layer, border and overview gates pass. All five changed
pivot assets match the validated source bytes after LF normalization. The overview
and border gates were run from that exact commit because separate concurrent
overview work changed the checkout while this release deployed; those unrelated
changes were preserved. No external blocker remains for this amendment.
The t lookup covers the released maximum 42 participants, with unavailable CIs
for larger samples. Physical Safari and assistive technology remain untested.
Next action: resume the wider scientific/publication checklist, which stays open.

### Active amendment — table below the plot

Owner clarification (2026-10-23): put the pivot table under its visualization,
including desktop. Retain border resizing and page flow without nested scrolling.

- [x] Use one full-width column in both standalone and embedded pivots; remove
  desktop width-sharing logic and resize table/plot independently from the right.
- [ ] Verify desktop/phone order, resize/copy/point access, production build and
  exact live deployment under the existing publication workflow.

Plan/state: small change to the existing pivot CSS/resizer bindings and border
regression gate on codex/table-below-plot from 9360736. The initial regression
correctly failed the desktop table-below-plot requirement. Statistical data and
rendering owners remain unchanged. Next action: complete browser gates and publish.
Production build, all 70 workbook tests, and border/overview/pivot/layer/copy/
point-inspection browser gates pass. Independent review found no actionable
issues. Table order is checked inside the iframe in one layout read, avoiding
scroll-anchoring races. Next action: authorized push and exact live verification.
The wider scientific/publication goal remains open.

### Completed amendment — Segment 2 rainclouds and point inspection

Owner request (2026-10-23): promote the six raw Inhale−Exhale trial-group deltas
as the main Segment 2 visualization, stacked rainclouds, with exact-value click/
tap inspection across plots. This overrides the previous figure ordering, not
the preserved corrected overall inference or cleaning. Keep the wider goal open.

- [x] Render six stacked half-density/box/participant clouds, preserving all 240
  paired deltas, the original pointwise mean CIs, colors and explicit zero. Use
  the existing descriptive Gaussian-KDE rule (1.06 × sample SD × n^(−1/5)),
  trim to observed support, and retain static SVG/PNG/PDF plus full data.
- [x] Share a persistent point-detail box across the overview and live explorers;
  include exact serialized values, units and identity/context, keyboard navigation,
  touch, dismissal and a static/data fallback. Inspect existing plot owners first.
  Owner selected current page/explorer plots and future plots; older workbook/
  archived report figures are outside this retrofit.
- [x] Verify source/data identity, density math, all points, real browser point
  activation, reflow/Pretext, existing controls, suite, authorized Git publication,
  exact CI/Pages deployment and changed live behavior.

Owner clarified HTML-based rendering: draw every current chart from numerical
data with HTML/SVG elements; static image/PDF exports are downloads only.
Work isolated on codex/phase-raincloud-points from main a129ddd.
Pre-integration evidence: production build, all 70 workbook tests, 270 independent
Python/JavaScript cases, and overview/pivot/layer/point-inspection browser checks
pass locally. All 240 HTML raincloud point values match the CSV; all 1,013 current
overview marks (SOA, raincloud, corrected pairs, blocks) expose exact data. The
current exploratory heatmap also uses the shared HTML/SVG inspector. The original
native statistical summaries and input data are unchanged. Phone/desktop renders
were inspected; physical Safari and assistive technology remain untested.
Integration with title/border resizing is verified locally: all 70 tests, 270
Python/JavaScript comparisons, overview/point/pivot/layer/copy/border browser gates
pass. The border gate includes HTML raincloud growth, Home reset and content
minima; phone/desktop renders were inspected. Independent review confirms
unchanged results and no remaining material findings after the caption correction.
Source `5710b14` is pushed on main and the retained chart branch. Actions run
`39964405325` passed the full fixed analysis, independent numerical validation
and Pages deployment. Live overview, point-inspection, border-resize and chart-
layer gates pass at the renamed publication URL. All 240 deltas match the live
CSV; the entire numerical payload equals the validated build. New chart script
bytes match after LF normalization; inspector, CSV and raincloud SVG match exactly.
The current page has no embedded plot images. Static downloads remain separate.
No external blocker remains for this amendment. Next action: resume the broader
scientific/publication checklist; physical Safari and screen-reader testing remain
unrun. The wider goal is open.


### Scientific web-figure selection guide — 2026-10-23

- [x] Add [data-to-plot and toolkit decision trees](visualization/README.md),
  seven toolkit profiles and a commit-pinned [source inventory](visualization/catalog.json)
  for Observable Plot, D3, D3 Graph Gallery, Vega-Lite, Plotly.js, Penrose and SVG.js.
  Route future chart selection from the README and skill index; preserve approved
  statistics, native live charts, existing owners and the lightweight startup path.
- [x] Verify all seven inventories against non-truncated pinned source trees,
  their tree hashes and 62 fetched-source SHA-256 receipts. All 49 local links/
  anchors resolve; 26 reference URLs are accessible (one throttled HEAD request
  was confirmed with browser fetch). JSON, context/safety and whitespace gates
  pass. RTK is unavailable; bounded native shell output was used.
- [x] Commit/push guide checkpoint `06167f8` on `main`; verify its full SHA
  equals remote `refs/heads/main` and the working tree is clean.

Scope: agent reference documentation only; no plotting runtime, plugin, model,
served figure or publication-readiness status changes. Source publication is
verified; chart runtime/build/deployment checks were not run for this protocol-only
change. No external blocker remains for the guide. Next action: resume live-plot
migration and the existing scientific acceptance checklist. The wider publication
goal remains open.

### Completed amendment — direct resizing and page flow

Owner request (2026-10-23): remove table size sliders, drag table borders directly,
eliminate nested scrolling and use available screen space across plot layouts.
This supersedes historical internal-scroll/size-control instructions below.

- [x] Replace sliders with shared border handles for tables and plot surfaces,
  keyboard reset/arrows and pointer/touch capture. Tables grow with content;
  the desktop graph/table share width, and the overview uses screen width.
- [x] Verify resize/reflow, enlarged text, emulated touch, data/CSV/selection,
  independent review, combined production build and exact live publication.

Plan/state: reuse pivot/overview owners and pinned Pretext; actual borders alter
layout/SVG dimensions while statistical outputs stay fixed. Native chart migration
remains its own open item. Work is isolated on codex/resize-panels from 60fedb2;
69 workbook tests, 270 independent JavaScript/pandas cases, production build,
border/layer/copy/overview/pivot checks pass. Expanded border checks include
mouse/keyboard/emulated touch, layout-breakpoint transitions, one scroll surface,
200% text/spacing, and full-width desktop/phone rendering. A reproduced review
finding about stale stacked widths was fixed and regression-tested; final review
has no further findings. Narrow cells show three significant digits while copy,
CSV, full-value details and selected cell nodes retain full precision/identity.
Physical Safari and assistive-technology coverage remain untested.
Source ccdf710 was normally merged with the publication-title update and pushed
as 63ede43. Actions run 39962510271 passed the full fixed analyses, independent
numerical checks and Pages deployment. Live resize, overview/pivot, chart-layer
and table-copy gates pass at the renamed publication URL. Shared resizer,
overview/app JavaScript and CSS bytes match that exact Git revision. One initial
evidence-link request failed during deployment propagation; direct HTTP checks
and the complete repeated overview gate pass. This evidence-only update changes
no served artifact. Next action: resume native-plot migration and the broader
scientific/publication checklist, using the existing visualization-selection
guide for the owner's toolkit suggestions. The resize worktree/branch is retained
at the source checkpoint. Physical Safari and screen-reader checks remain unrun.
The wider scientific/publication goal remains open.

### Publication-name rename — 2026-10-23

- [x] Confirm the publication title from the existing README and owner approval
  to rename the project and GitHub repository. Update maintained links and the
  landing-page title; preserve historical artifacts and active checkout paths.
- [x] Rename GitHub and update the shared `origin`; save the publication title
  through Codex's project service and legacy workspace label. Keep the existing
  checkout/worktree roots so active chats and hourly synchronization remain valid.
- [x] Production build, 69 workbook tests, 270 Python/JavaScript parity cases,
  both changed notebook checks, context/secret-pattern gate and whitespace check
  pass. Overview browser gate passes; the title additionally passes at
  320/390/844/1440 px, 200% text and spacing overrides. Phone/desktop renders
  inspected. Windows local serving required the correct `.mjs` MIME type and
  UTF-8 build mode; no product workaround was added. RTK remains unavailable.
- [ ] Verify deployment and exact remote synchronization; record source/run
  evidence here. The running desktop may need a refresh to show its saved label.

Next action: complete rename verification, then resume the existing scientific
and publication acceptance checklist. The wider publication goal remains open.

### Live-page plot rule — 2026-10-23

- [x] Record the owner's native-web-chart requirement in `PROJECT.md` and its
  rendering/data checks in `VERIFICATION.md`; static exports remain available.
- [x] Migrate current overview/explorer plot images to charts rendered from the
  approved data, preserving estimates, uncertainty, pairing and accessible data
  access. Live verification is recorded in the completed raincloud amendment
  above. Older workbook/archived report figures retain the owner-selected scope.

The instruction-only checkpoint started from clean, synchronized `main` at
`13b35ef` and changed no served assets. Its current-page migration is now verified
through source `5710b14` and successful deployment `39964405325`, as recorded
above. Future plots retain this rule. Next action: resume the broader scientific
and publication gates. The wider publication goal remains open.

### Completed amendment — spreadsheet-style table copying

- [x] Reuse the shared read-only pivot table for rectangular drag, Shift-click,
  keyboard and touch ranges, select all and Excel-compatible TSV copying. Keep
  full precision, blank missing cells, internal scrolling and size controls.
- [x] Production build, all 69 workbook tests, 270 Python/JavaScript parity cases,
  pivot and overview browser gates pass. Dedicated Chromium checks pass for
  ranges, clipboard values, result reset and actual embedded clipboard fallback;
  phone/desktop renders inspected. RTK is unavailable; bounded native commands
  were used. Actual Excel paste, physical Safari and screen readers are untested.
- [x] Commit/push `a9a09dc` and verify deployment of combined source `a129ddd`
  through successful Actions run `39957489994`; the earlier run was superseded
  by the merged chart-layer change. Live clipboard and overview gates pass,
  including real clipboard reads and the embedded fallback. The served HTML,
  selection/app JavaScript and CSS match source hashes. The combined tree also
  passes all 69 workbook tests, 270 parity cases and chart/pivot/overview gates.
  `main` is synchronized through `2c4d6f3` before this evidence-only checkpoint;
  no additional site deployment is needed for this roadmap update.

Next action: resume the existing measurement/publication questions. The wider
scientific/publication acceptance checklist remains open.

### GitHub synchronization checkpoint — 2026-10-23

- [x] Fetch and inspect all five worktrees: clean, with `main` matching
  `origin/main` at `9fab5aa`. One historical local-only checkpoint, `7990a9e`,
  contains the earlier overview source; preserve it on its branch without merging.
- [x] Run the required context/secret-pattern gate and whitespace check; both pass.
  Existing roadmap-length and archived-image warnings remain. RTK is unavailable;
  bounded native commands provide the observed evidence.
- [x] Activate the hourly Codex follow-up `keep-study-5-pushed-to-github` under the
  owner's continuing commit/push authorization. It checks verified public-safe
  work and stays quiet when unchanged, preserving private and unfinished material.
- [x] Push synchronization policy `6888c6e` on `main` and all six other local branch
  tips. Verify every branch's exact SHA using `git ls-remote --heads origin`;
  all seven match, with a clean working tree after the push. This source-only
  update changes no served-site files and claims no new deployment.

Next action: the hourly follow-up checks for new completed work; resume the
existing scientific/publication checklist. The wider publication goal remains open.

### Completed amendment — baseline-corrected RT is the default

Owner clarification (2026-10-23): current SOA, phase and block analyses and future
RT analyses use AT minus the retained participant × Condition × Phase baseline
mean, pooling baseline SOAs, before their declared aggregation. Raw RT stays an
explicit reference; historical snapshots and Segment 0's benefit sign are retained.

- [x] Amend the three specifications and rebuild corrected primary means, figures,
  downloads and result manifests. Keep negative values and explicit zero references.
  SOA F/p and endpoint contrasts are unchanged; its corrected endpoint means are
  −8.60 and −24.38 ms. Phase corrected means are −17.57/−19.73 ms, with unchanged
  phase difference −2.16 ms, p=.664. Corrected block slope is −0.120 ms/block,
  95% CI [−1.321, 1.081], t(38)=−0.203, p=.840; raw p=.584 is labelled reference.
- [x] Independently verify matched pooled baselines, all four SOA cells, missing
  baseline handling, invariance, block aggregation and 117 statsmodels coefficients;
  all 69 workbook tests pass after integration. All three corrected figures were
  visually inspected; 800 exported SOA cells and 503 block means independently
  match trial-level subtraction of the pooled matched baseline.
- [x] Finish production-page checks, authorized commit/push, exact CI/deployment
  and live verification. Source `72d68a9` passed Actions run `39880298506`, including
  the full fixed/reference analyses, independent validation and Pages deployment.
  The live overview gate passes: corrected primary-measure labels in all three
  segments, actual ZIP/CSV downloads matching source, 11 sections, four viewport
  sizes, Pretext, keyboard/touch, 200% text/spacing and current Segment 0 grouping.
  The initial run for `47d10fb` was superseded by the combined phase-audit update;
  its labelled raw trial-group reference preserves the corrected primary display.
  Native calculation remains distinct from browser display. Physical Safari is
  untested. The managed worktree is clean and synchronized to deployed source;
  this evidence-only update does not require a redundant site build.

This clarification is complete. Next action: continue the remaining ordered
measurement/publication questions using corrected RT by default.

The initial raw-primary checkpoints below are historical; this amendment owns
the current primary-measure choice. The wider publication goal remains open.

### Completed analysis — overall RT drift across consecutive blocks

Owner request (2026-10-23): average RT across all chronological blocks spanning
both consecutive conditions. This exploratory native analysis is complete;
the wider scientific/publication goal remains open.

- [x] Freeze the 12-block question, original cleaning, participant-level linear
  slope test, quadratic/condition-adjusted checks and linkage sensitivities in
  `results/block_rt/SPECIFICATION.md` before numerical execution.
- [x] Export participant/block means, all-available primary40 descriptives,
  complete-block statistics, trajectories, diagnostics and input/source/output
  hashes. `results/block_rt/RESULTS.md` records all findings and limitations.
- [x] Independently check chronology/condition order, pandas trial aggregation,
  117 statsmodels coefficients, saved means/p values, synthetic effects and hashes
  with `for-ai/orchestration/block_rt.py --check`; release audit and all 66
  workbook tests pass. Both exported figures were visually inspected.

Complete-block inference retains 39 participants: P011/P033 remain excluded for
linkage, and P008 lacks usable AT RTs in block 7. P008's other blocks remain in
the all-available primary40 table. The initial raw-reference linear slope is −0.685 ms/block, 95% CI
[−3.199, 1.829], t(38)=−0.552, p=.584; adjusted for condition, −0.057 ms/block,
p=.968. Quadratic p=.820 with a strong tail departure. No systematic decline is
established; lack of significance does not establish absence of practice/fatigue.
The first-to-last paired change is −20.54 ms, 95% CI [−52.22, 11.15].

Owner follow-up: publish this graph in new Segment 3 after the phase question,
renumbering later segments (11 sections total). Use one spaghetti panel, with
actual participant segments blue/solid for Control and red/dashed for Viscereality;
replace the order-group display. Black points retain the overall equal-person
mean/pointwise 95% t CIs. The figure-only change leaves results.json byte-identical.
All 78 rendered SVG segments match each participant's actual condition and style.

- [x] Add the segment, native-result labels, missing-block note and complete/all-
  available CSV downloads; production build checks the full block-result manifest.
- [x] Preserve numerical estimates and pass all 67 workbook tests.
- [x] Pass final rendered browser checks: four viewport sizes, 200% text/spacing,
  real Pretext measurements, all 11 sections, block navigation, figure loading and
  an actual CSV download identical to the source. Physical Safari remains untested.
- [x] Verify the exact live deployment: source `dc7360e`, Actions run
  `39877716247`, successful build and Pages deployment. The full overview browser
  gate passes on the live URL, including Figure 3, block navigation/download and
  all four viewport/text matrices. Download references were pinned to that Git
  revision because concurrent Segment 2 work had regenerated local phase files.

Source/results were originally committed in `a68de1a`; the Segment 3 amendment
is committed, pushed and deployed from `dc7360e` on main. Native computation
remains distinct from the verified browser display. Concurrent uncommitted
Segment 2 phase-source/results work was preserved. Historical manuscript
unchanged. This amendment is complete. Next action: resume the remaining
question-led analyses and wider open scientific/publication acceptance gates.

### Completed amendment — Segment 1 basic PPS phenomenon check

Owner request (2026-10-23): Segment 1 first asks whether RT differs by SOA,
using the simplest appropriate paired analysis, a graph and APA-style statistics.
This replaces its baseline-correction question. Keep the wider publication goal open.

- [x] Freeze the exploratory one-factor SOA question, existing cleaning, primary40,
  equal Condition × Phase cell weights, GG correction and linkage sensitivities in
  `results/pps_soa/SPECIFICATION.md` before execution.
- [x] Compute the five-level RM ANOVA and a raw RT graph with participant profiles,
  pointwise 95% t CIs and APA results. Retain all sensitivities, effect magnitude,
  diagnostics, data/source hashes and downloads in `results/pps_soa/`.
- [x] Independently verify ANOVA with statsmodels, GG epsilon with projected sample
  covariance, means/CIs with pandas/SciPy, baseline translation and missing cells.
- [x] Install 55 absent project-routed skills with the Codex installer helpers;
  validate discovery metadata, retain source pins/licenses and existing skills.
  Receipt: `orchestration/project_skills_installation.json`. Exact `consensus-mcp`
  skill unresolved; the connected Consensus tool is available. GSD skills/workflow
  assets installed; compiled CLI/runtime/hooks not installed or executed.
- [x] Verify the production page, accessible graph/downloads and responsive layout.
  Production build, 64 workbook tests and the rendered overview gate pass: four
  viewports, enlarged text/spacing, Pretext, keyboard/touch, Segment 0/2 preservation
  and an actual Segment 1 ZIP download matching the verified archive. All 17 result
  manifest hashes match canonical staged Git bytes. Skill validation rechecks all
  55 entries and 380 installed-file hashes. Physical iPhone/Safari remains untested.
- [x] Commit/push and verify the exact Pages deployment and live Segment 1.
  Source `c4a26c7` on `main` passed Actions run `39874953819`: all 64 tests,
  data/preparation checks, full fixed/reference analyses, independent numerical
  validation, production build and Pages deployment. The complete overview browser
  gate passes against the live site, including the SOA graph, exact APA text and
  actual ZIP download matching the checked local archive. Native calculation and
  saved-result display remain distinct. The earlier CI roundoff-only test failure
  is resolved by 1e-12 relative/1e-14 absolute numerical tolerances; artifact hash
  and ZIP comparisons remain exact.

State: native primary N = 40, F(2.52, 98.11) = 3.28, p = .031, partial eta squared
= .078, GG epsilon = .629. Mean RT decreases from 681.47 to 665.69 ms across the
endpoint SOAs; paired endpoint difference −15.78 ms, 95% CI [−31.95, 0.39].
Tail deviations remain visible in contrast Q–Q plots; inferential assumptions and
temporal-expectancy alternatives remain. This establishes neither a spatially
specific PPS mechanism nor a physiological boundary. New source owner is
`workbook/pps_soa.py`; saved native results are displayed, not fitted in-browser.
The bounded Segment 1 request is complete. Source `c4a26c7` is deployed and the
canonical `main` checkout was fast-forwarded to it; the managed
`codex/pps-soa-check` worktree retains its verification evidence. Segment 0/2 work
and unrelated ongoing edits are preserved. This evidence update changes only the
control plane, so it does not require a redundant site deployment.
Next action: continue the remaining ordered publication/measurement questions;
the wider scientific, browser-migration and author-review acceptance stays open.

Owner decision (2026-10-21, D-0015): develop the current publication primarily as
a live HTML paper on GitHub Pages, with its analysis available there and versioned
source/results in GitHub. This supersedes the pause on current-paper HTML
authoring; it does not overwrite the preserved version-1.9 manuscript or resolve
the scientific identification questions below. Keep this checklist open until
the executable analysis, paper, reproducibility and publication gates pass.

Standing execution goal (owner instruction, 2026-10-22): use the Superpowers
completion flow for every authorized change, automatically committing validated
task-owned work, pushing through the permitted Git path and verifying live-page
publication. The exact protocol is in `WORKFLOW.md`; authorization persists across
sessions. Keep this publication goal open until its scientific acceptance gates pass.

- [x] Record automatic Superpowers Git completion, commit/push authorization and
  live-deployment verification in the canonical router, skill route and workflow.
- [x] Install and validate the HyperFormula, Handsontable and Univer integration
  skill assets, preserve their references/licenses and record pinned provenance
  in `orchestration/spreadsheet_skills.json`; route them in `SKILLS.md`.
- [x] Preview and run the installed For-AI additive baseline migration; preserve
  and include the nested RTK, focused Superpowers and GSD Core workflow guides.
- [x] Establish the publication-first contract, canonical owners and readiness
  gates in `PROJECT.md`, `WORKFLOW.md` and `VERIFICATION.md`.
  Skill structure, asset hashes, baseline-source matches, local links and the
  project context gate pass; these checks do not establish browser migration.
- [x] Inventory each existing analysis as browser-executable, native-only,
  saved-output-only or unrun; record its engine, specification, inputs, runtime,
  numerical reference, browser-download evidence and remaining migration work.
  See `results/BROWSER_COVERAGE.md`; this audits source and archived evidence,
  not a fresh execution of every method.
- [ ] Build the current HTML paper from verified results, with question/method/
  result/figure/reference links into executable analyses and downloadable evidence.
  Keep exploratory session state separate from the published result record.
- [ ] Port remaining analyses in finite declared batches; run actual browser
  executions and downloads, independent numerical parity, uncertainty/diagnostic
  checks and performance/failure-state checks before claiming browser coverage.
  A spreadsheet formula engine does not replace the scientific inference engine.
- [ ] Verify mobile/keyboard/accessibility, downloadable run settings and hashes,
  complete figures/data/source, and a stable versioned publication snapshot.
- [ ] Complete author/scientific review and verify the exact Pages deployment
  and live paper/analysis paths; only then label that release publication-ready.

State: the landing page is a compact ten-section overview. Segment 0 is only
its central descriptive pivot chart/table; later sections each contain one question
and links to analysis/evidence. Segment 2 also gives a compact RT phase answer.
Narrative and detailed limitations remain in linked
reports. The executable workbook remains at `workbook.html`; models/data are unchanged.
The desktop menu remains fixed; phones use the collapsible bottom menu, with
embedded dialogs reserving its visible height.

Current extension (2026-10-23): Segment 0 fixes SOA on X and uses one grouping
checkbox each for Condition and Phase. Both checked shows four curves; one
checked shows two curves pooled over the other factor; neither shows one pooled
curve. Every state preserves all source cells, pooling within participant before
across-person summaries. Default-off Normalize RT retains trial-based min–max
and z-score methods; grouping never changes the normalization references.
See the active grouping amendment below. Earlier level-filter controls are
superseded; the standalone pivot retains its broader controls.

Publication: source `c4a4564` pushed to `main` passed Actions run 39808535590,
including the full reference analyses, independent numerical validation and Pages
deployment. Actual live Chromium checks pass all grouping/correction/SD controls,
mean-SD-n exports and table/plot identity, fixed desktop navigation, the collapsible
phone menu, active-section tracking, embedded settings, keyboard, Pretext, four/six
viewports, 200% text and spacing, plus standalone pivot checks. The separate
navigation check also records a 57px phone bar and smooth anchor scrolling.
The bundled Node/Playwright runtime now completes both standard browser scripts.
Scientific review, remaining browser migration and publication readiness stay open.
Next action: develop the table/analysis behind each remaining single question
without restoring a text-heavy landing page. Physical iPhone/Safari is untested.
The pivot/frontend milestones below retain
their own execution/deployment evidence.

Plot scale rule (owner clarification, 2026-10-22): every quantitative plot uses
zero as its actual reference. Nonnegative values and uncertainty start at exactly
zero. When negative values occur, retain the full range and mark zero explicitly.
The shared pivot chart now uses that scale and labels the zero line when its range
extends below zero. Local production build and JavaScript syntax check pass. Commit
`d5bcf76` passed full Actions run 39811976223 and its live chart was checked: raw
means start at zero; corrected means below zero remain visible with a zero reference.
The explicit zero tick refinement is commit `ae6d7ba`; run 39813873259 subsequently
completed successfully, including Pages deployment. Its served JavaScript includes
the zero tick, and the field-list browser checks verify the rendered label on
corrected plots. Continue the active field-list amendment below.

## Segment 2 — overall inhale versus exhale RT

Owner request (2026-10-23): add Segment 2 answering whether RTs were generally
faster during inhale. The existing response-level paired contrasts already answer
this; no new fitting or cleaning is needed. Later sections are renumbered 3–9,
with their existing anchors preserved.

- [x] Add the question, compact answer, cohort/weighting labels and links to the
  saved native report and complete contrast/sensitivity CSV.
- [x] Independently reproduce primary40 raw and pooled-baseline phase estimates,
  paired t statistics, two-sided p values and 95% CIs from released participant
  cells, and verify the displayed rounding (`workbook/test_overview.py`).
- [x] Run the production build, 60 workbook tests, data audit and overview
  browser gate: section order/numbering, phase navigation, real Pretext, four
  viewports, 200% text, spacing, keyboard/touch and existing Segment 0 controls.
- [x] Commit/push and verify exact CI, Pages deployment and changed live behavior.

Result: raw Inhale−Exhale = +18.47 ms (95% CI 6.96 to 29.98; p=.0024),
so raw AT responses were slower during inhale. Matched AT−Baseline phase contrast
= −2.16 ms (95% CI −12.15 to 7.82; p=.664), inconclusive. Equal condition/SOA
weights within each of 40 participants; P011/P033 excluded; unadjusted tests.
These exploratory native results do not establish a PPS parameter effect or
browser execution of the analysis. The source data and saved results are unchanged.

Local evidence: production build `.for-ai-local/phase-site`, independent numerical
test and complete overview browser script pass; desktop screenshot visually
reviewed. Windows build uses Python UTF-8 mode. RTK is unavailable here; bounded
native commands and the reviewed local GSD/Superpowers fallback guides were used.
Physical iPhone/Safari and scientific publication acceptance remain open.
Publication: source `8268f9e` on main passed Actions run `39873722384`, including
the full workbook/fixed analysis, independent numerical validation and Pages
deployment. The complete overview browser gate also passes on the live site,
including Segment 2, its navigation/Pretext and preserved Segment 0 interactions.
The later independently developed Segment 1 integration `da66210` was fast-forwarded
locally and preserves Segment 2; its separate run `39874757294` is still in progress
and is not covered by this deployment claim. Branch: main, synchronized before
this evidence update. Segment 2 is complete. Next action: resume the remaining
living-publication checklist; keep the overall scientific/publication goal open.

### Segment 2 amendment — direction audit, six trial groups and research

Owner requests (2026-10-23): independently confirm inhale/exhale direction, plot
the five AT SOAs and pooled Baseline in matching colors, and compare published
findings, specifically external multisensory synchrony-detection tasks. Keep the
established cohort, cleaning and overall contrast family unchanged.

- [x] Reaggregate literal released phase strings directly from retained trials;
  independently compare with the existing pandas participant cells and confirm
  all three saved native contrasts, CIs and two-sided p values.
- [x] Add raw-reference Figure 2b with six phase-mean lines and matching individual paired
  deltas/pointwise 95% t CIs, redundant colors/markers/line styles, explicit zero
  references and all observations. Preserve SVG/PNG/PDF, 480 participant/group/
  phase means, 240 participant deltas, six summaries, settings/runtime and hashes
  under `results/phase_rt/`; `workbook/phase_rt.py` is the native owner.
- [x] Integrate the concurrent baseline-corrected-primary amendment while
  preserving its primary overall figure. Keep the six-group plot as a labelled
  raw reference (`phase_raw_groups`), with both sets of SVG/PNG/PDF exports.
- [x] Clarify scheduled/instructed labels versus unverified actual physiology,
  raw RT versus Segment 0's reversed-sign baseline benefit, and saved native status.
- [x] Verify the production build, 69 workbook tests and local
  overview browser gate (four viewports, 200% text/spacing, Pretext, keyboard/touch,
  Figure 2, six-row CSV download, responsive research page and existing segments).
- [x] Save the 12-source targeted research comparison and access/query ledger in
  `literature_review/RESPIRATION_RT.md` and `respiration_rt_sources.json`, including
  contrary RT findings, explicit synchrony tasks and RT/perception dissociations.
- [x] Commit/push the six-group extension, follow exact CI/Pages deployment and
  verify the final live figure, exports and research note.

Result: Exhale raw M = 662.19 ms; Inhale M = 680.66 ms. Raw Inhale−Exhale is
+18.47 ms; pooled baseline phase difference is +20.63 ms; AT−Baseline phase
difference is −2.16 ms, inconclusive. No label-order/index reversal was found in
the current release/analysis path. Upstream acquisition labels and actual breathing
remain unverifiable from these CSVs. Original inputs and native result family
are unchanged. The graphic includes the shared software-guidance credit by link.
The six exploratory Inhale−Exhale estimates are +16.41, +8.94, +29.90, +22.91,
+14.18 and +20.63 ms; the 300/800/2700-ms pointwise intervals include zero. No
six-test p family or SOA-interaction inference is added. Same-direction respiratory
RT reports coexist with opposite findings. No directly matching respiratory-phase
external synchrony-judgment study was identified in the targeted search; this does
not establish literature absence. RTs cannot confirm a subjective-synchrony effect.
Consensus was unauthorized; opened primary/institutional web sources were used.
Both figures were visually inspected, including the raw-reference phone and live
desktop rendering. The raw PNG is 1380×2520 at 300 dpi, opaque white, with SVG
glyph outlines to avoid browser font substitution. Source `6018871` and integration
`72d68a9` are pushed to main. The latter preserves concurrent corrected-primary
analyses and Segment 0 pooling. Actions run `39880298506` passed all 69 tests,
full reference analyses, independent numerical validation and Pages deployment.
The complete overview browser gate passes live: 11 sections, both phase figures,
actual six-row CSV download, responsive research page, four viewport/text matrices,
Pretext and preserved grouping/normalization controls. Eleven live figure/result/
research artifacts match checked local bytes. Context and release audits pass;
physical iPhone/Safari and actual respiratory physiology remain unverified.
The task is complete; this evidence-only update does not change the served site.
Next action: resume the wider open living-publication/scientific acceptance gates.

## Visualization — fast pivot table and linked chart

### Completed amendment — combinable figure layers

Owner request (2026-10-23): switch/combine dot-whisker summaries, actual
participant values, spaghetti trajectories and violin distributions in Segment 0.

- [x] Retain the already pooled participant values behind each mean/SD/n cell.
- [x] Add independent mean dots/whiskers, mean line, participant dots, spaghetti
  and violin toggles, preserving correction/normalization, grouping and pairing.
- [x] Verify independent numerical parity, rendered accessibility/reflow, source
  downloads and missing/constant/small-n cases; commit/push and verify deployment.

Plan: extend the existing pivot engine/chart/app and their regression checks;
reuse SVG, native controls and pinned Pretext. Participant values are per-person
means after pooling unchecked factors, never trial rows. Violin KDE is descriptive
and explicitly labelled. Existing fixed analyses remain unchanged.
State: 69 tests, 270 JavaScript/pandas cases (including every participant value),
independent SciPy KDE and production build pass. All 32 combinations, participant
CSV, missing/constant/small-n cases, correction/normalization/grouping,
keyboard/touch, six viewports, 200% text/spacing and real Pretext pass in Chromium.
Both standard overview/pivot browser gates pass; desktop/phone images were
visually inspected. Independent code review reports no actionable findings.
Physical Safari/assistive-technology coverage remains untested; RTK is unavailable.
Source 562e64f was normally integrated with the concurrent table-copy change and
pushed on main as a129ddd. Both changes passed the combined local browser gates.
[Actions run 39957489994](https://github.com/GeorgeFejer91/Study5_Publication/actions/runs/39957489994)
passed the full fixed analyses, independent numerical validation and deployment.
All 32 combinations and participant CSV, the overview and the table-copy gate
also pass on the live deployment. Served HTML/app/chart/engine/CSS bytes match
that exact Git revision. The context/secret-pattern gate passes with main
matching origin/main; only existing roadmap/archive warnings remain.
This evidence-only checkpoint changes no served artifact. The worktree and
feature branch are retained; the canonical checkout is synchronized after push.
Next action: resume the wider question-led scientific/publication checklist.
The overall scientific/publication acceptance goal remains open.

### Active amendment — Condition/Phase grouping checkboxes

Owner clarification (2026-10-23): use one checkbox per factor to pool data when
unchecked, replacing separate level-selection checkboxes. SOA stays fixed.
Normalization and baseline controls retain their existing definitions.

- [x] Replace four level filters with two factor grouping controls.
- [x] Verify four/two/two/one curves, participant pooling/SD/n, normalization,
  table/CSV identity, keyboard/touch and responsive rendering.
- [x] Commit/push and verify the exact live deployment.

State: implemented in 27e837e on codex/segment0-pooling, integrated into main,
and included in deployed source 72d68a9. The red check observed four controls
instead of the required two. Production build, 69 tests on the combined tree,
270 independent JavaScript/pandas cases and independent source review pass.
Both standard browser scripts pass locally and live: four/two/two/one curves,
default 800 source cells and n=40, participant-level SD, pooled normalized means,
CSV, keyboard/touch, actual Pretext, four/six viewports, 200% text and spacing.
The phone controls were visually inspected; physical iPhone/Safari is untested.
[Actions run 39880298506](https://github.com/GeorgeFejer91/Study5_Publication/actions/runs/39880298506)
passed the full reference analyses, independent validation and Pages deployment.
The served Segment 0 app, CSS and HTML bytes match that deployed Git revision.
The isolated worktree stays clean; unrelated analysis changes were integrated
through normal fast-forwards without editing another task's source.
Next action: continue the wider question-led publication checklist, preserving
these grouping and normalization contracts. The broader scientific goal stays open.

### Active amendment — fixed SOA, series selection and participant normalization

Owner request (2026-10-23): fix SOA, replace field dragging with individual
Condition/Phase checkboxes, and offer participant-specific normalization across
all conditions. Research distinguishes z-scores from 0–1 min–max scaling; the
owner permits multiple methods. Supersedes the earlier drop-driven layout.

- [x] Fix SOA from released data and add four native series checkboxes.
- [x] Add default-off normalization with min–max and z-score choices, based on
  every person's retained AT trial distribution pooled across all factors.
  Correction on normalizes baseline benefit; off normalizes raw RT. Visibility
  does not change references; constant/undefined scales remain missing.
- [x] Complete rendered checks, commit/push, and exact live deployment.

State: production build, 59 workbook tests, 270 independent JavaScript/pandas
cases and both rendered browser scripts pass, including all 16 series
selections with both corrections and normalization methods, missingness and
undefined scales. Research/access limits and formulas are in
workbook/RT_NORMALIZATION.md. The normalized payload loads on demand.
Keyboard/touch, Pretext, four/six viewports, 200% text and spacing pass; the phone
controls were visually inspected. Physical iPhone/Safari remains untested.
Source commits ebe6e3e/955fccb were pushed on main and included in deployment
8268f9e. Actions run 39873722384 passed the full reference analyses, numerical
checks and Pages deployment. Both standard browser scripts then passed against
the live overview and pivot; deployed app/engine/chart/HTML bytes match that Git
revision (compare Git blobs, since Windows working copies use CRLF).
The later combined main build da66210 failed a separate Segment 1 floating-point
equality test and did not replace this deployment. Its owner retains that work;
this task did not modify those changes. Broader scientific acceptance stays open.
Next action: continue the remaining question-led analyses; retain this Segment 0
normalization contract and verify newer deployments through their own gates.

### Active amendment — drop-driven field placement

Owner request (2026-10-23): drag field boxes into destination boxes to change the
layout; remove click-to-add and click-menu moves. Stage pointer/keyboard moves
until a valid drop, with visible destination/insertion feedback. Keep mouse,
touch/pen and keyboard pick-up/drop, removal, reordering and cancellation; preserve
the shared table/chart state and all baseline/SD/zero/data contracts.

- [x] Replace click placement/menu with pending drag/drop and destination feedback.
- [x] Verify actual mouse/touch/keyboard drops, cancellation and responsive rendering.
- [x] Commit, publish and verify exact deployment and live interaction.

State: production build, 59 workbook tests, 170 independent numerical cases and both
rendered browser scripts pass. Native dragging/reordering, outside drops, keyboard
pending/drop/Escape, trusted touch drop/cancel, inert clicks/taps and embedded edge
scrolling pass. No table/chart update occurs during a pending move. The phone UI
was visually inspected; four/six viewports, 200% text and spacing pass. These are
Chromium/emulated touch checks, not physical iPhone/Safari/pen qualification.
Source `0d4f059` is published on `main`;
[Actions run 39866203075](https://github.com/GeorgeFejer91/Study5_Publication/actions/runs/39866203075)
passed the reference analysis, independent numerical validation and Pages deployment.
Both browser scripts pass against the live overview/standalone pages, including
inert field clicks/taps, native mouse drops/reordering, keyboard drop/cancel,
trusted touch drop/cancel and embedded edge scrolling. Existing raw records/CSV,
baseline toggle, SD/n, zero reference, navigation, Pretext and responsive checks pass.
This interaction amendment is complete. Next action: develop the table and analysis
behind the remaining single questions from the active roadmap.
The overall scientific goal remains open.

### Active amendment — baseline benefit toggle

Owner request (2026-10-22): Segment 0 starts with baseline correction on and uses
a toggle to switch to uncorrected RT. Corrected display is Baseline − AT RT,
labelled `baseline_benefit_ms` in CSV; fixed AT − Baseline analyses stay unchanged.
Positive means indicate faster responses. Preserve genuine negatives, nulls,
participant grouping, sample SD/n and the existing zero-reference rule.

- [x] Add the default-on accessible switch and shared derived table/chart measure.
- [x] Independently verify sign, missingness, grouping, SD/n and original records.
- [x] Verify rendered local behavior, publish and exercise the exact live deployment.

State: 170 independent JavaScript/pandas cases, 59 workbook tests, production
build and the overview/standalone rendered browser checks pass. Keyboard Space/
Enter and pointer switching restore identical corrected means/SDs; chart/table/
CSV identify Baseline − RT. The compact payload remains unchanged at 63,941 bytes.
Both toggle states fit at 320/640/1280 CSS px with normal/200% text and a minimum
44px target in Chromium; the phone control was visually inspected.
Source `2d1a349` is published on `main`;
[Actions run 39832911744](https://github.com/GeorgeFejer91/Study5_Publication/actions/runs/39832911744)
passed the reference analysis, independent numerical validation and Pages deployment.
Both browser scripts pass against the live site: default-on correction, pointer/
Space/Enter switching, Baseline − RT labels and derived CSV, linked means/SD/n,
zero reference, raw records, field layouts, filters and responsive/enlarged-text
checks. The standalone pivot preserves its original correction. Physical iPhone/
Safari remains untested. This display amendment is complete. Next action: develop
the table and analysis behind the remaining single questions from the active roadmap.
The overall scientific/publication goal remains open.

### Active amendment — field-based Segment 0

Owner request: replace mode/checkbox controls with an Excel-style field list.
Readers add, remove, move and reorder SOA, distance, condition, phase and
participant fields in Rows/Columns; one layout drives the table and chart.
No grouping fields means an unaggregated trial table with original exclusion
flags and the selected cohort. Grouped means continue to use retained AT
participant-distance means and equal-person means/sample SD/n. Keep the
baseline correction selector, zero reference and complete scrollable/exportable
table. Desktop dragging needs equivalent touch/keyboard field actions.

- [x] Implement field list, area/reordering interactions and ungrouped records.
- [x] Verify independent summaries/raw exports and linked table/chart identity.
- [x] Verify responsive/keyboard/Pretext behavior and preserve standalone pivot.
- [x] Commit, publish, check exact deployment and record observed live behavior.

State: local production build, 59 workbook tests, 133 independent JavaScript/pandas
cases and both rendered browser scripts pass. The overview checks cover native
dragging, keyboard/touch moves and order, no-SOA groups, raw trial rows/CSV, button
filters, correction/SD, table/plot identity, zero ticks, four viewports, 200% text
and spacing. Standalone coverage spans six viewports and source races. Full release
contains 17,114 raw trial rows; Primary 40 contains 16,298. One local raw-view
render took 6,150 ms; this is not a physical-phone/network benchmark. Table resizing
no longer rebuilds its rows, and labels/values scroll within the complete grid.
No new spreadsheet runtime or statistical model. Source `3744bf7` is published on
`main`; [Actions run 39825629998](https://github.com/GeorgeFejer91/Study5_Publication/actions/runs/39825629998)
passed the full reference analysis, independent numerical validation and Pages
deployment. Both browser scripts also pass against the actual live overview and
standalone pivot: field dragging/moving/reordering, raw records/CSV, linked grouped
means/SD/n, correction, zero labels, filters, cohort changes, keyboard and the
responsive/enlarged-text matrix. The live Primary 40 raw view rendered all 16,298
rows in 6,681 ms in one Chromium run; this is not a physical-phone/network benchmark.
A separate local 320×568 raw-view check confirms all 26 columns and 16,298 rows,
internal horizontal/vertical scrolling and no outer-page overflow. Physical
iPhone/Safari remains untested. This visualization amendment is complete; the
broader scientific/publication goal stays open. Next action: develop the table and
analysis behind each remaining single question from the active roadmap.

Owner-approved priority: fast loading and smartphone compatibility. `/pivot/`
uses lightweight JavaScript and lazy JSON prepared by the established Python
owner. This step changes no statistical models or historical manuscripts.

### Verified table foundation

This checklist records the earlier table-only milestone. The linked-chart step
below supersedes its table-only default and compact-payload size. The full-table
viewport amendment below supersedes this milestone's pagination behavior.

- [x] Keep the default page limited to the table, Activate filters and Pivot
  settings. Disabling filters ignores retained selections. Export CSV includes
  every pivot row/column with full numeric precision, including off-page cells.
- [x] Load only the default 46,023-byte data payload initially, enforced below a
  64 KiB build budget. Full means, 17,114 trials, participant questionnaires and
  the catalogue of 264 tracked saved tables load on demand. Preserve source
  identity and the original cleaning/scoring/baseline correction.
- [x] Implement touch targets, row/column and field/value pagination, keyboard
  focus/Escape, and ordered stretch settings without internal scrolling. Locked
  Pretext 1.0.0 measures bounded labels after the first table and on dialog open.
  Its unavailable state retains browser wrapping and geometry pagination.
- [x] Preserve the marimo fallback at `/pivot/app/` and expanded controls,
  heatmap, source inspection and downloads at `/exploratory/`.
- [x] Pass 59 workbook tests, 60 JavaScript/Python parity cases, strict/WASM
  notebook checks, native fallback and audited production build. Check totals,
  missingness, boolean/numeric axes, validation errors and cohort/filter semantics.
  Actual browser CSV matches Python at 1e-10; the live paginated export is
  byte-identical to that full six-row/six-column reference.
- [x] Verify phone portrait/landscape, desktop, enlarged text, spacing overrides,
  full-value access, delayed overlapping source loads and anchored stretch groups.
- [x] Verify the complete CI, exact Pages deployment and live execution.

State: **PIVOT STEP VERIFIED.** Deployed source `b84da44` on `main` passed the
full reference analysis and independent numerical validation. Live filters change
800→400→800 records; row/column paging and CSV export work. The exploratory
notebook still executes separately. One local first-table observation was 209 ms,
versus 38.4 seconds for marimo; the live first table was 973 ms here. These are
single Chromium observations, not controlled physical-phone/network benchmarks.

Tested viewports span 320×568 portrait, 640×360 landscape and 1920×1080 desktop.
At 200% text, small settings use nine ordered control pages; very short enlarged
worksheets deliberately scroll the outer document. Text-spacing overrides are
browser-verified because Pretext does not model word spacing. Physical iPhone/
Safari remains untested. Details are in `docs/engineering/SESSION.md`.
### Linked chart

Verified extension: a linked descriptive chart on `/pivot/`, using the same
worker result and selection state as the table. No new inference is authorized.

- [x] Add structured pivot series metadata and an SOA default without loading
  full sources at startup; verify exact cell/point and aggregation consistency.
- [x] Add responsive chart controls, units, hover/keyboard values, missing-data
  gaps, multi-measure selection and empty/error states; preserve table exports.
- [x] Verify combined Condition/SOA filters, grouping/measure/summary changes,
  source races, mobile/enlarged layouts, notebook gates and production build.
- [x] Record the verified Git state and exact publication outcome.

State: local implementation, 60 numerical parity cases, chart fixtures, 59 workbook
tests, strict/WASM notebooks, native fallback and audited production build pass.
Browser checks cover six viewports, 200% text, spacing, source races and CSV identity.
The compact SOA payload is 51,603 bytes; no new runtime dependency was added.
Implementation `e111a63` is included in deployed source `c40d470` on `main`.
The complete CI/reference analysis, independent numerical validation and Pages
deployment pass. Six live pivot assets match the reviewed bytes; the complete
browser regression also passes on the live page, including combined filters,
CSV identity and the six-size/enlarged-text matrix. Prior deployed evidence above
belongs to the earlier table-only version. Physical iPhone/Safari remains untested.
Next action: use the linked pivot to choose the next descriptive comparison.
The broader living-publication and scientific inference goals remain open.

### Full-table viewport rule — owner request 2026-10-22

Standard for every Excel-like or data table shown on a live page: render the
complete result in one table with internal scrolling and user controls for table
height and width. Never divide table rows or columns across Next/Previous buttons.
The existing 100,000-cell result guard remains in force; complete table display
does not authorize unbounded data expansion. Settings preserve ordered stretch
groups, and chooser lists expose all choices through scrolling rather than pages.

- [x] Render every current pivot row and column at once; keep CSV bytes and linked
  chart cells identical to the full result.
- [x] Add keyboard-operable height/width controls and an internally scrollable
  table viewport; remove table, settings and chooser pagination buttons.
- [x] Verify local Chromium rendering at 1254×720: all six default rows and six
  columns appear together; both size controls update; all settings groups and the
  complete field chooser are reachable without Next/Previous buttons. Also verify
  the embedded grouped means table retains its SD/n details and grouping controls.
  Build, 59 workbook tests, 125 JavaScript/Python parity cases and the context gate pass.
- [x] Push reviewed source `b8e955a1d09671dbd64673a84039eaf560c70ada`; Pages
  workflow run [39810516916](https://github.com/GeorgeFejer91/Study5_Publication/actions/runs/39810516916)
  completed successfully, including build, analysis, independent numerical
  validation and deploy. Verified the public pivot and `?view=core` pages in
  Chromium: the complete tables, internal scroll regions, height/width sliders,
  and core mean/SD/n cells are present without Next/Previous controls. The
  repository's Playwright package is unavailable here; direct Chromium rendering
  was used, and physical iPhone/Safari remains untested.

State: implementation, local and deployed browser verification pass. The broader
living-publication and scientific inference goals remain open.
Next action: continue the broader publication work from its active checklist.

Visualization skill setup (2026-10-21): the five owner-requested figure,
exploration and uncertainty skills are installed and routed in `SKILLS.md`;
`orchestration/visualization_skills.json` records pinned sources and content
verification. All five Codex skill validations and hash receipts, ten Python
syntax checks, sixteen OpenAI local-reference checks and the project context
gate passed. Setup did not run plotting helpers, fit models or deploy the site.
The pivot frontend verification above is complete; the broader living-publication
and scientific inference goals remain open.

## Goal and status rules

Answer each level separately before selecting the paper narrative. Deliver
`results/RESULTS_REPORT.md` with evidence links and completion status for every
question. VERIFIED means a computation/check was observed; PARTIAL means some
evidence exists but the scientific identification claim remains open; BLOCKED
means the released data cannot supply a required source; NOT RUN means exactly
that. A completed analysis with an inconclusive result is not a failed task.

The initial roadmap and unpooled Bayesian specification were fixed after seeing
version-1.9 results, before calculating that extension. The later joint-model and
baseline-comparison goals followed inspection of its results and are now computed
with the limits recorded below.
These amendments are exploratory, not a new preregistration. The historical
LaTeX/Typst snapshot stays frozen; current HTML authoring follows D-0015. Use the
installed Ponytail skill:
reuse preparation, scoring and contrast definitions; add only the portable model,
its report/export and proportional checks. Preserve the legacy reference.

## Active goal — usable Bayesian evidence for experimental PPS parameter effects

Recorded 2026-10-20 after the previous results: identify a scientifically usable
Bayesian statistic supporting an Inhale − Exhale effect, a Viscereality − Control
effect, or their interaction on PPS midpoint (cm) or normalized sharpness (/cm),
if supported by the observations. Retain all four participant cells and propagated
AT − Baseline uncertainty. This is an exploratory extension, not a preregistration
or a promise of a nonzero effect. Computational completion can yield an
inconclusive or unidentifiable parameter comparison.

- [x] Q10.1 Record the target: six primary contrasts (three effects × two
  parameters), plus the established simple contrasts. Preserve the primary40
  cohort, fixed cleaning, all earlier results and unadjusted frequentist outputs.
- [ ] Q10.2 Freeze a finite extension specification before new effect estimates:
  nuisance adjustments, reduced boundary-only/shared-sharpness and
  sharpness-only/shared-boundary models, proper priors, diagnostic gates,
  simulation counts and numerical extension/stopping budgets. Select restrictions
  by scientific rationale and predictive adequacy, never by favorable contrasts.
- [ ] Q10.3 Audit trial index, block, intervention order and baseline calibration
  for identifiable nuisance effects. Verify source-dependent timing before
  changing baseline matching; retain unresolved timing/linkage as explicit limits.
  Review checkpoint: `paper_analysis.clean` already applies participant-wide
  mean ±2.5 sample-SD trimming across distances, conditions, phases and AT/Baseline.
  Per-distance trimming would be a new exploratory sensitivity. Prioritise plots
  of every trial with existing exclusions marked, cell counts/distributions and
  time/block trends; fatigue or additional exclusions are not established by
  visual fit quality. Rolling averages are diagnostic unless the full inferential
  pipeline accounts for induced covariance, shape distortion and held-out testing.
  Owner correction: interventions occurred consecutively in one sitting. Early
  blocks within each intervention do not control accumulated time. Prioritise
  the shared session-wide RT trend, jointly estimated with AT/Baseline and PPS
  uncertainty, using original global trial order across both interventions.
  `results/trial_cleaning/session_specification.json` fixes five adjusted fits and
  five additional matched predictive folds; early fits remain sensitivity only.
- [ ] Q10.4 Fit the frozen joint hierarchical candidates with baseline and
  individual-fit uncertainty. Keep Gaussian/robust references and every failed
  fit. Do not use ANOVAs on pooled posterior medians as independent evidence.
- [x] Q10.5 Export all six primary contrasts and simple contrasts for the declared
  trial-cleaning/session-time batch: posterior
  estimate, 95% credible interval and directional probability, with physical units
  and population/cohort target. Assess practically meaningful effects only with
  justified thresholds; add Bayes factors only with explicit proper hypothesis
  priors and stable calculations. Posterior probabilities are not p values.
- [ ] Q10.6 Check null/known-effect recovery across repeated simulations, prior
  sensitivity, posterior prediction and matched held-out targets. A narrow
  interval or imposed visible S does not establish parameter identification;
  retain failed diagnostic gates and their consequences for interpretation.
- [ ] Q10.7 Compile the complete evidence table and classify each parameter
  effect as supported under the stated model, model-dependent, inconclusive or
  not identifiable. Distinguish RT-location/curve effects from boundary/sharpness
  effects. Stop after the declared scope and report all outcomes.
- [ ] Q10.8 Define the owner's requested last-30-participant sensitivity using
  verified collection order, then refit the same session-time models and retain
  the full-cohort reference. **BLOCKED:** the released participant IDs are arbitrary
  and the CSVs omit collection dates (`workbook/DATA_RELEASE.md`); higher public
  IDs do not establish later recruitment. Obtain public IDs for the intended
  cohort before fitting. Keep the existing quality/linkage exclusions and report
  the actual retained count. Existing pooled posterior draws cannot substitute
  for a subgroup refit. This post-results sensitivity is exploratory.

Status: **DECLARED CLEANING/TIME BATCH VERIFIED; BROADER GOAL OPEN.**
`results/trial_cleaning/RESULTS.md` records the eight unadjusted fits/fifteen
matched predictive refits; `SESSION_RESULTS.md` in that directory records five
continuous-session-time fits/five further refits. Twelve independent numerical
checks and the complete export/hash audit pass; all 162 atlas pages were visually
inspected. Eight of thirteen full fits pass their fixed convergence gate, all
twenty predictive gates pass, and no primary (0/78) or simple (0/182) parameter
interval excludes zero. Failed models remain inconclusive. Local filtering removes
71 additional AT hits; RMSE for held-out mean RTs is 59.62 ms with the original filter, 60.07 ms
with local filtering, 61.58 ms with rolling means and 60.10 ms with joint linear
time control. A positive quadratic RT component is supported in that sensitivity,
but it is not a PPS effect or a causal fatigue diagnosis. Both visible95 models
have 0/600 AT mean-profile discrepancy tails: imposed S geometry has poor average-
profile adequacy despite converged sampling. Early blocks do not rule out fatigue.
Q10.2–.4 and .6–.7 remain PARTIAL: this bounded batch is complete, while reduced
boundary-only/sharpness-only models, repeated Bayesian recovery/coverage and the
broader scientific evidence classification remain open. Next action: establish
the requested last-30 cohort's public IDs and freeze its membership before any
refit. Reduced models and recovery budgets remain later open items; do not select
another cleaning/shape variant by significance. Source timing/linkage remains unresolved.
Questionnaire follow-ups, browser integration and manuscript updates were not run
for this native amendment; earlier inputs and numerical results are unchanged.
Publication: the audited native source/results have been pushed normally to
`main`, with the remote SHA verified. Automatic workbook checks are separate
from native-model verification and do not establish browser execution of these
new models.
The shared RTK/GSD/Superpowers skill baseline is unavailable
in this environment; use the existing roadmap and context checks as the bounded
fallback rather than installing dependencies or creating a second progress ledger.

## Completed computation — explicitly visible, shape-constrained Bayesian sigmoid

The owner explicitly authorizes an in-range midpoint/width restriction after
inspection of nearly linear broad fits. Fit the declared `visible95` prior (5/95%
component levels inside 10–100 cm) and `visible90` sensitivity, preserving positive
amplitude, raw observations, fixed cleaning and joint Baseline uncertainty.
The specified geometry is in `results/visible_sigmoid/specification.json`; this
is a post-results theory constraint, not evidence of observed S curvature.

- [x] Q9.1 Verify endpoint geometry, midpoint/derivative, exact marginalized
  likelihood, prior simulation and conditional export independently.
- [x] Q9.2 Run both full fits and retain every paired boundary/sharpness contrast,
  diagnostic status and prior-versus-posterior information check.
- [x] Q9.3 Run five primary held-distance refits and compare with the preserved
  broad-directional predictions on identical targets; no selection by significance.
- [x] Q9.4 Export a visibly sigmoid mean-parameter model figure, actual RT figures,
  all 40 participants' curves and boundary intervals. Inspect every page and verify
  hashes, labels, exact shape guarantees and original-data preservation.

Deliver `results/visible_sigmoid/RESULTS.md`; preserve earlier snapshots. Q1.7 is
not closed by prior-constrained intervals or visually guaranteed model curvature.
Both full fits converge with zero divergences; all 12 main boundary/sharpness
contrast intervals include zero. All 160 normalized curves satisfy the in-range
shape restriction, and every atlas page was visually inspected. Five independent
numerical checks and the full export/hash audit pass. Predictive validation is
**PARTIAL**: the 10 cm fold still fails convergence after its fixed extension;
the four converged folds have diagnostic RMSE 66.92 ms versus 45.86 ms for the
broad reference. The failed fold remains exported and whole-five-fold summaries
are provisional. The visible S is a computed model-imposed approximation, not
stronger evidence for physiological PPS boundaries. Width-cap/midpoint coupling
also limits interpretation of apparent individual precision.

## Completed reference — consistent asymptote direction across conditions

The owner rejects condition-specific reversals of the near/far RT asymptotes.
Refit with one theory-motivated orientation for all four curves: nonnegative
amplitude on increasing distance (lower RT near, higher RT far). This does not
fix the numerical heights of the plateaus or justify narrow widths. Keep the
earlier signed results as a reference; preserve raw reversed/flat observations.
The pre-fit extension is `results/directional_sigmoid/specification.json`.

- [x] Q8.1 Verify the marginalized positive-amplitude likelihood against an
  independent full-trial multivariate-normal calculation and conditional draws.
- [x] Q8.2 Fit all four cells jointly, check convergence and retain all midpoint,
  sharpness and response contrasts without selecting by significance.
- [x] Q8.3 Run all ten matched positive/unrestricted held-distance refits; report
  predictive tradeoffs, including uncertainty and failed diagnostic gates.
- [x] Q8.4 Export all 40 participants' consistently oriented curves and uncertainty,
  inspect every atlas page, and update the method recommendation with limitations.

Results: `results/directional_sigmoid/RESULTS.md`. Five numerical checks passed;
the full fit has no divergences and passes the stated convergence gate. All ten
predictive gates passed; held-distance RMSE is 46.90 ms with positive amplitudes
and 47.27 ms unrestricted, with an uncertain paired MSE difference. All six main
shape contrasts include zero. All 160 curves have the requested direction, but
156 midpoint medians are beyond the sampled range and no midpoint interval is
wholly inside it. The direction-constrained model is the requested exploratory
approximation, with the signed reference retained; Q1.7 remains open. Every atlas
page was visually inspected and full-draw summaries, contrasts and artifact hashes
were independently checked.

## Completed reference — publication-defensible individual sigmoid approximation

The owner authorizes pooling across participants and smoothing across SOA to
estimate four sigmoid curves per retained person, and requests a recommended
analysis and lead result. Use the converged native `joint_logistic_marginal` as an
explicitly exploratory approximation, with cell-noise sensitivity and the earlier
complete battery retained. This is a practical numerical choice, not demonstrated
best prediction or permission to select an effect-producing analysis.

- [x] Q7.1 Choose one common, converged estimator with baseline uncertainty and
  partial pooling across people; retain signed amplitudes and all four cells.
- [x] Q7.2 Package every retained person's parameters/intervals and measured-range
  responses alongside a clearly labelled full-sigmoid model illustration. Quantify
  how much of the transition is observed; do not equate a guaranteed S on a
  standardized axis with measured curvature.
- [x] Q7.3 Retain joint posterior Condition, Phase and interaction contrasts, plus
  simple contrasts and the noise sensitivity. Do not treat pooled medians as
  independent measurements for a new effect claim.
- [x] Q7.4 Recommend the most defensible lead finding with its model sensitivity,
  rather than the smallest nominal p value. State physiological identification
  and publication limits, verify the package and visually inspect every atlas page.

Output: `results/publication_sigmoid_choice/RECOMMENDATION.md`. No manuscript or
Pages integration is required. Q1.7 remains open even if every person has a finite
model curve. All 160 parameter records match the original full-draw summaries;
all 28 retained parameter contrasts include zero. All 40 atlas pages were visually
inspected, and the full-S row is a labelled standardized model illustration.

## Completed batch — baseline-corrected experimental effects across model families

Determine whether Inhale versus Exhale, Viscereality versus Control, or their
interaction changes the baseline-corrected PPS response. Test all three effects
for sigmoid boundary and normalized sharpness; also assess linear and logarithmic
distance models. The owner explicitly confirms subtraction of Baseline RT from
Audio–Tactile RT. Primary matching follows the existing participant × Condition ×
Phase baseline mean. Same-nominal-SOA correction is a separately labelled
sensitivity because equivalent cue timing cannot be verified from the release.
Carry uncertainty from both trial types into inference. Raw-RT models are a
reference, not the requested primary corrected analysis.

For each parameter θ, report Condition (Viscereality−Control, phase-averaged),
Phase (Inhale−Exhale, condition-averaged), and the interaction:

`Iθ = (θ_Viscereality,Inhale − θ_Viscereality,Exhale)
    − (θ_Control,Inhale − θ_Control,Exhale)`.

The overall Inhale−Exhale difference is a Phase main effect. Report it and the two
within-condition phase differences alongside the interaction; neither a significant
phase effect nor significance in only one condition establishes an interaction.

Start with a hierarchical nonlinear sigmoid model with participant-specific midpoint,
positive sharpness, baseline RT and signed response amplitude. Include Condition,
Phase and Condition × Phase in the shape parameters, with participant variation
in the repeated contrasts and explicit partial-pooling assumptions. Retain all four
cells and the fixed preparation/cohort rules. Fit individual parameters and group
effects jointly so their uncertainty remains connected.

The comparison also includes frequentist nonlinear estimation, mixed models for
linear/log-distance effects, paired contrast/resampling methods, and screened
literature sensitivities. Linear/logarithmic slopes are not sigmoid sharpness;
these families have no intrinsic plateau midpoint. Compare them on predictions
and explicitly shared observed-range response contrasts. The expanded specification
is in `workbook/ANALYSIS_PLAN.md`; the source-to-method rationale is in
`literature_review/ANALYSIS_RATIONALE.md`.

This is post-results exploratory work. **Goal and correction definition: RECORDED.
Baseline availability and focused literature audit: VERIFIED with access limits.
Expanded native registry, implementation, fits and tests: COMPUTED with diagnostic
and identification limits.** The owner has deferred Pages documentation and browser
integration for this batch. Its registry and results are in
`results/baseline_effects/`; executable source is in `analysis/baseline_effects/`.
Exhaust
the declared, scientifically distinct feasible approaches and record reasons for
omissions; do not promise an unlimited search or stop at the first significant
result. Existing results and diagnostic failures remain part of the evidence.

## Level 0 — Data and preprocessing

- [x] Q0.1 Audit released rows, missingness, source hashes and questionnaire scoring.
- [x] Q0.2 Record timing: baseline MAIA once; spatial ratings after each condition.
- [x] Q0.3 Define the four participant × Condition × Phase fitting cells uniformly.
- [x] Q0.4 Retain the fixed RT cleaning rule; never optimize it for shape or p values.
- [ ] Q0.5 Resolve P011/P033 recording linkage (BLOCKED by missing source mapping).
- [x] Q0.6 Primary new RT inference excludes both; retain three cohort sensitivities.
- [x] Q0.7 Audit baseline availability and define subtraction, matching and sign:
  4,192 retained Baseline RTs for the primary 40-record cohort, all 800 nominal-SOA
  cells populated, but only 1–6 observations per such cell; source cue timing is
  unverified. The primary correction pools baseline hits within person/condition/phase.
- [x] Q0.8 Implement and independently verify baseline correction and propagated
  uncertainty, including reused-baseline covariance, sparse cells, signed values,
  and translation invariance of a free-intercept curve. Preserve raw inputs/cleaning.

## Level 1 — Observed shape and reliability

- [x] Q1.1 Audit raw profiles and the original trial-level fit gate separately from
  model-only normalized geometry; keep flat and reversed responses.
- [x] Q1.2 Compare extraction/smoothing methods using held-out RT prediction,
  including constant, linear and broad/visible sigmoid alternatives.
- [x] Q1.3 Assess split-half reliability, condition-change reliability and known-signal
  recovery. Existing weak reliability is a result, not a reason to delete records.
- [x] Q1.4 Check whether Bayesian sigmoid prediction improves on simpler models.
- [x] Q1.5 Quantify whether posterior shape information exceeds the prior, whether
  both bends lie in the sampled range, and sensitivity to shape/nuisance priors.
- [x] Q1.6 Inspect every Bayesian raw/normalized participant plot and group plot.
- [ ] Q1.7 Establish reliable physiological boundaries for all people (PARTIAL;
  computable proxies do not satisfy this scientific identification requirement).

## Level 2 — Individual midpoint and sharpness

- [x] Q2.1 Define boundary `m` in cm and normalized sharpness `1/(4*w)` per cm;
  keep signed RT amplitude/derivative distinct from normalized sharpness.
- [x] Q2.2 Preserve the 168 existing four-cell proxies and their refit intervals.
- [x] Q2.3 Fit a genuine, explicitly specified Bayesian sigmoid posterior to each
  observed trial cell; report median, interval, amplitude, prior information and
  grid/boundary diagnostics. Do not smooth the likelihood or force nonzero amplitude.
- [x] Q2.4 Verify numerical integration against an independent calculation and a
  finer grid; check posterior predictive fit and prior-predictive plausibility.
- [x] Q2.5 Propagate draws for the uncertainty-aware analysis; retain the separately
  requested fixed-median conventional ANOVA as Q3.6.
- [x] Q2.6 State which estimates are data-informed and which remain prior-dependent;
  no claim that an assumption-free or universally best fit exists.

## Level 3 — Main experimental question

- [x] Q3.1 Preserve the prior 2×2 parameter ANOVA/ANCOVA with curve-refit uncertainty.
- [x] Q3.2 For both Bayesian parameters report Phase (Inhale−Exhale), Condition
  (Viscereality−Control), and Condition × Phase, using paired participant draws.
- [x] Q3.3 Distinguish the posterior cohort-average contrast from participant-population
  uncertainty; use paired Bayesian-bootstrap weights for the latter, clearly labelled.
- [x] Q3.4 Repeat across priors and the four linkage cohorts; no preferred result by p.
- [x] Q3.5 Decide whether observed effects are robust, inconclusive or model-dependent;
  computational estimates alone do not establish physiological changes.
- [x] Q3.6 Run the owner-requested conventional 2 × 2 RM ANOVAs on Bayesian
  posterior medians, with unadjusted p values and explicit omission of within-fit
  uncertainty; verify independently and retain all prior/cohort sensitivities.
- [x] Q3.7 Fix the joint model's likelihood, numerical proper priors, random-effects
  structure, sampler, diagnostics, cohort sensitivities and finite set of model
  checks in the native `analysis_registry.json` and per-model specifications before
  each batch, with post hoc diagnostic amendments labelled. Incorporate measured
  Baseline trials into the corrected estimand and propagate their uncertainty.
  Keep treatment priors centred on zero and justify scales from the design/measurement units; do not
  choose them from the desired interaction result. Browser feasibility is deferred.
- [x] Q3.8 Fit trial responses, all four participant curves and population effects
  in one hierarchical Bayesian analysis. Model positive sharpness on a log scale,
  retaining baseline/amplitude variation and flat/reversed responses. Export
  posterior draws; distinguish a log-sharpness coefficient (ratio of ratios)
  from the interaction in normalized sharpness on its original scale.
- [x] Q3.9 Check multiple-chain convergence, effective sample sizes, Monte Carlo
  error, prior/posterior prediction and known-signal/null recovery. Compare simpler
  response models and the fixed prior/likelihood sensitivities. Record computational
  or identification failures; numerical improvements must not be selected by
  whether they produce a positive interaction.
- [x] Q3.10 Report both parameters' paired interaction contrasts, overall Phase and
  Condition effects, and the phase difference within each condition. Give estimates,
  95% credible intervals and directional posterior probabilities; distinguish
  finite-cohort contrasts from population effects. Assess meaningful-size effects
  only after recording justified thresholds. Posterior probabilities are not p
  values. If Bayes factors are added, fix the null, alternative and proper priors
  explicitly and check the calculation's stability.
- [x] Q3.11 Independently verify the native joint implementation, inspect
  raw-data/curve/contrast plots, and retain its full
  results and sensitivities. Classify the interaction as supported under the stated
  model, model-dependent, inconclusive, or not estimable. Preserve all outcomes;
  no search-until-significant stopping rule or manuscript narrative is required.
- [x] Q3.12 Freeze a source-linked registry of baseline schemes, model families,
  estimands, inference methods and diagnostics before their new effect tests.
  Include constant, linear distance, log distance and sigmoid models; distinguish
  a literature replication, a generic sensitivity and an unsuitable/unidentifiable
  model. Add justified methods by dated amendments, preserving earlier results.
- [ ] Q3.13 Fit the frequentist nonlinear counterpart and linear/log-distance
  repeated-measures models. Test Condition, Phase and their interaction for shape
  parameters or distance coefficients, with participant dependence and uncertainty
  from both Baseline and AT. Include profile/parametric bootstrap, whole-person
  resampling and valid paired contrasts; report singular/nonidentified fits.
  **PARTIAL:** individual grid/continuous NLS, paired RM ANOVA, multivariate,
  permutation/rank/sign and refit checks are computed. A separate nonlinear
  mixed-effects fit and profile-likelihood confidence sets were not run;
  R/nlme is unavailable in the current environment. Refit stability intervals
  are not claimed to have calibrated confidence coverage.
- [x] Q3.14 Fit corresponding Bayesian linear/log-distance models and declared
  robust/prior sensitivities. Separate log distance from log RT; corrected RT can
  be negative. Report posterior contrasts and explicitly specified Bayes factors
  only where proper priors and stable computation support them.
- [x] Q3.15 Evaluate screened sigmoid/plateau/smoothing alternatives fairly,
  including the published fixed-observed-extrema logistic as a labelled sensitivity.
  Repeat tuning/baseline estimation within applicable validation/refit loops; inspect
  raw and corrected curves, recover known/null effects and retain all failures.
- [x] Q3.16 Compile every model/effect, unadjusted p or posterior summary, effect
  size/interval, cohort, correction and diagnostic status into one results inventory.
  Identify nominal findings, robust patterns, specification-sensitive findings and
  inconclusive effects separately. A general RT benefit or a significant simple
  effect alone is not a PPS boundary change or Condition × Phase interaction.

## Level 4 — Descriptive average curves and figures

- [x] Q4.1 Preserve observed equal-person cell means and earlier group fits.
- [x] Q4.2 Plot four Bayesian average response functions with raw data and uncertainty.
  An average of sigmoids need not itself be a sigmoid; do not force it into one.
- [x] Q4.3 Display midpoint and sharpness intervals with consistent units/axes and
  separate model geometry from the actual RT response; visually inspect figures.
- [x] Q4.4 Inspect all four corrected response curves and corresponding Baseline/AT
  summaries, model comparisons and experimental contrasts with uncertainty. Show
  extrapolation and imposed geometry; do not change axes to imply observed bends.

## Level 5 — Spatial frame, MAIA-2 and joint exploration

- [x] Q5.1 Preserve all eight MAIA subscales, paired spatial comparison, numerical
  delta, ordinal sensitivities and prior moderation/cell-association analyses.
- [x] Q5.2 Propagate Bayesian parameter uncertainty into four cell associations with
  baseline MAIA and same-condition spatial ratings and into parameter changes
  versus spatial delta and MAIA. Participants remain independent units.
- [x] Q5.3 Fit separate subscale models for spatial delta, MAIA and their product,
  with order adjustment, on the four orthogonal PPS summaries. The product in the
  Condition/Phase/interaction summary is the corresponding three-/four-factor
  exploratory moderation, not mediation. Keep all eight scales and both outcomes.
- [x] Q5.4 Label these modular posterior/participant-bootstrap descriptive regressions
  accurately; they are not a jointly estimated hierarchical latent-covariate model.
  Report raw uncertainty and full counts, never select scales or cleaning by results.
- [x] Q5.5 Explain whether any association survives parameter and prior uncertainty;
  do not call absent evidence proof of no biological relationship.

## Level 6 — Reproducibility and final evidence report

- [x] Q6.1 Keep the existing verified browser analysis and manuscript snapshot intact.
- [x] Q6.2 Unit/independent checks, real-browser execution, actual download and
  native/browser parity for the new results-only branch.
- [x] Q6.3 Archive data/code/artifact hashes and readable numerical tables/figures.
- [x] Q6.4 Complete `results/RESULTS_REPORT.md` with each level's findings, status,
  remaining limitations and links, without drafting manuscript prose.
- [x] Q6.5 Push the validated changes and verify the live results companion.
- [ ] Q6.6 Verify and publish the expanded corrected-model results in the browser,
  update the results-only report and link every conclusion to the full registry.
  **DEFERRED by the owner's results-only request.** Older checked browser items
  refer to their published analyses, not the new native extension.
- [x] Q6.7 Independently check and package the native corrected-model results,
  figures, model diagnostics and full inventory in
  `results/baseline_effects/RESULTS.md`, preserving the older published snapshots.

## Interpretation contract

The Bayesian extension is a quadrature approximation with a declared likelihood
and proper priors, not assumption-free inference. It deliberately provides an
unpooled posterior reference: partial pooling can stabilize estimates but can also
supply apparent similarity in weak data. A full joint hierarchical nonlinear model
is not implied by this reference and must be labelled NOT RUN unless executed
and diagnosed. Finite Bayesian medians and attractive curves do not by themselves
close Q1.7. No baseline MAIA mediator or questionnaire-driven data cleaning.

Completion means all feasible checklist computations and a candid evidence report.
It does not require a significant experimental difference, a positive correlation,
or treating every participant as having an empirically identified sigmoid.

## Current evidence checkpoint

The completed unpooled model/contrast/association computations and fixed-median
ANOVAs have run in native Python and Pyodide with independent checks and matching
numerical results. The individual and average figures have been visually inspected.
Computational completion does not close Q1.7: the individual parameters remain
poorly identified and unreliable, and experimental/questionnaire associations
are inconclusive after propagating uncertainty. Q0.5 still requires source mapping.
The requested conventional tests on fixed Bayesian posterior medians are also
computed and independently checked; none of their primary or sensitivity tests
establishes a condition, phase or interaction difference at unadjusted .05.
The native baseline-corrected extension has now run: five individual sigmoid
families, continuous/refit checks, linear/log-distance and categorical tests,
twelve joint Bayesian specifications, twenty held-distance refits, recovery and
prior/likelihood/nuisance-pooling sensitivities. Some nonlinear sampler diagnostics
still fail after the finite extension budget; these are inconclusive model results,
not null-effect evidence. The independently marginalized nuisance models converge
and retain very wide parameter intervals. Fourteen independent numerical checks
pass, and all 40 native atlas pages and average/baseline figures were inspected.
The published result archive/report/evidence and preserved legacy ZIP/PDF match
the checked local bytes. Public application input checks and editor execution
passed for that earlier snapshot. Source mapping (Q0.5), reliable physiological
identification (Q1.7), the unrun parts of Q3.13 and deferred browser integration
(Q6.6) remain open. The native report separates exploratory RT-level interactions
from unsupported PPS boundary/sharpness claims, and demonstrates why ANOVAs on
hierarchically pooled posterior medians can give false positives in a null
simulation. Earlier raw-RT browser results remain separate.
