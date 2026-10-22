# Verification and readiness gates

Evidence must match the claim. Use VERIFIED, PARTIAL, BLOCKED and NOT RUN precisely;
unavailable metadata and fit-gated outcomes are not computed null results.

## Bootstrap and task contract

Read the routed context, inspect status, and name the observable outcome and owner.
Preserve unrelated work. Run `pwsh -NoProfile -File for-ai/scripts/check-context.ps1
-ProjectRoot . -RequireRemote`; remote mismatch during intentional development
must be reconciled by a normal validated push, never by resetting user work.

## Workbook and data

### Living publication acceptance (D-0015)

For changes to the question-led landing page, serve a production build and run
`node workbook/check_overview_browser.cjs URL` with Playwright available. Check
section anchors, scroll tracking, evidence/tool links, keyboard skip access,
actual Pretext measurements, narrow/wide layouts, 200% text and spacing overrides.
Verify `/workbook.html` remains available with its existing relative assets.
For Segment 0, verify fixed SOA values (300, 800, 1500, 2200, 2700 ms), no
drag/drop controls, all 16 combinations of the four native Condition/Phase
checkboxes, and empty results when either group is unchecked. Check mouse,
keyboard and touch selection, raw/baseline-benefit RT with normalization off, min–max and z-scores,
Mean/Mean ± SD in both views, table/CSV mean-SD-n identity, and SD-aware chart
extents/tooltips. Normalization references use each participant's complete retained AT trials
across conditions/phases/SOAs before cell averaging/filtering; hiding series must
not renormalize scores. Independently compare trial-based mean/sample SD and
minimum/maximum. Verify normalization data loads on demand.
Verify dimensionless labels/CSV names and zero/undefined range as missing scores.
Run check_pivot_javascript.py for independent pandas means, sample SDs and n
across grouping/correction/cohort/filter combinations, including normalization.
Retain unequal within-person counts, n=1/undefined SD, missing values and
zero-valued means. The standalone pivot keeps broader field/source controls.
Apply the project-wide figure-scale rule to every changed quantitative plot: if
all values and uncertainty are nonnegative, the y-axis lower bound is exactly zero
with no padding below. If values or intervals extend below zero, retain their full
extent and render an explicit zero reference; never clip data to satisfy the bound.

GitHub Pages is the primary publication/analysis target. Before marking a version
publication-ready, verify all of the following, in addition to the applicable
method-specific checks below:

- A method-by-method coverage inventory distinguishes actual browser execution,
  native computation, saved-output inspection and unrun work. Opening a CSV in a
  pivot table does not establish that its producing model ran in the browser.
- The HTML paper's questions, methods, results, figures, references and limitations
  trace to one declared publication version and its approved result manifests.
  Preserve exploratory/preregistered labels, failed diagnostics and unavailable
  provenance. Keep the earlier paper/reference labelled as a historical version.
- Actual browser runs/downloads preserve inputs, code revision, runtime versions,
  settings/formulas, cohort/exclusions, seeds, uncertainty and result hashes.
  Compare migrated outputs independently against native/reference results.
- Any selected spreadsheet runtime is pinned and its supported formula set is
  tested for missing values, errors, coercion, references and recalculation.
  Edited/exploratory cells cannot silently replace released inputs or fixed paper
  results. Upstream templates and skill validation are not numerical evidence.
- Paper reading, analysis controls, tables/figures and export work on narrow and
  wide layouts, enlarged text, keyboard/touch and accessible non-colour cues.
  Show run progress, failed/unsupported calculations and native-only status.
- Record source/version identity and preserve a stable Git tag/release or archived
  snapshot with paper, data, code, settings and figure/result downloads. Verify
  source push, CI, exact deployment and live execution separately. Author and
  scientific review remain necessary; hosting does not imply peer review or DOI.

### Existing executable workbook checks

For Segment 1, run `python workbook/pps_soa.py` and the `test_pps_soa.py` tests.
Independently check statsmodels one-factor RM ANOVA, projected-covariance GG
epsilon/p, equal-cell pandas means, t intervals, matched-baseline invariance,
complete-case exclusions and primary40. Inspect the graph/contrast Q–Q plots;
verify native saved-result labels, exact APA text, static graph and downloaded
ZIP/CSV on the production page. `build_site.py` checks input/source/result hashes
and every ZIP member. Run the landing-page browser gate and preserve the broader
publication/migration limitations.

From the repository root in the pinned workbook environment:

```bash
python for-ai/orchestration/public_data.py check data/raw
python -m unittest discover -s workbook -p 'test_*.py' -v
marimo check workbook/data_preparation.py --strict
marimo check workbook/data_preparation.py --select MW --strict
python workbook/build_site.py
```

Expected release: 42 participant records and 17,114 unique trial IDs. P011 and
P033 share identical behavioural records with reversed condition labels; unique
IDs do not establish independent recordings. Exact schema, field,
key, source-pattern and release hash checks must pass. A refreshed dataset requires
a new field audit and verified separate private backup before changing the build
allowlist. Owner authorisation/ethical approval is recorded in DATA_RELEASE.md.

The artifact intentionally includes only the audited participant/trial CSV pair in
each application/editor view, executable source/runtime assets, release/analysis
records, the browser reference download and the hashed working preprint. No private
backup, crosswalk, recordings, historical source archive or execution cache belongs
in it. A build checks allowlisted CSVs and preprint/reference provenance.

Exercise the export over HTTP in a modern browser: published data load, full
analysis, preview-filter independence, complete download, editable view, valid
uploads, malformed input and partial-upload rejection. Inspect results, manifests
and figures. Check for browser RPC timeout notifications after a full run and
result-table/participant-selector interactions; PDF atlas generation must finish
before new result tables mount and request data. A native run or export alone cannot establish browser execution.
The complete ZIP uses a lazy download callback: verify the actual click and
downloaded hashes, including the 96-artifact release. Embedding that payload in
cell HTML can exceed marimo's output-size limit even after computation succeeds.

## Numerical and manuscript checks

For `/pivot/`, also run strict and WASM marimo checks on
`workbook/pivot_explorer.py`, the `test_pivot_data.py` checks included in the
workbook suite, and a native `app.run()` (800 default source records, six pivot
rows). Check unequal-size grand totals, missing values, text counts, baseline
sign/matching and cohort exclusions. Build only tracked public-result snapshots;
verify their CSV hashes/catalogue identity, private-pattern scan, lazy selection,
actual browser aggregation/filter changes and CSV export.

Run `python workbook/check_pivot_javascript.py` with Node 22 available to compare
the shipped JavaScript summaries with Python, including missing values, totals,
cohort/filter semantics and validation errors. The default page must start without
Pyodide and without preloading trials, questionnaires, the full means payload or
saved catalogues. Check the first-table DOM timing and actual lazy source changes.
Check 320×568 portrait, 640×360 landscape, intermediate and desktop sizes, 200%
text and text-spacing overrides. Verify settings' header/footer anchors, ordered
stretch groups, full control visibility and no Next/Previous paging. Verify the
complete result row/column count is present at once, internal table scrolling,
height/width controls, full-value access, touch targets, focus, Escape and CSV
export. Pretext predictions require actual
bounded-label measurements and rendered checks; unsupported word spacing remains
browser-verified. Record physical-browser/device coverage limits. Verify the default
minimal view hides filters/settings, activating filters reveals controls, and
deactivating them restores the chosen cohort regardless of retained selections.
For the linked chart, verify exact point/cell identity, exclusion of grand totals,
actual SOA spacing, separate measures/units, sample-SD/count semantics, missing
gaps versus true zeros, combined Condition/SOA filters and empty/error states.
The initial compact payload includes SOA and stays below 64 KiB. Table scrolling
and sizing must not truncate chart data. Check hover/tap comparisons of overlapping series,
keyboard point navigation, density limits, source races and mixed-unit warnings.
With Playwright/Chromium available to Node (or through `NODE_PATH`), run
`node workbook/check_pivot_browser.cjs <HTTP pivot URL>` against the audited build.
Its fixtures additionally check broken lines, explicit limits and missing-Pretext
fallback. Serve `.mjs` as JavaScript; the Windows Python MIME map may require an
explicit server override. The chart's SVG ticks use actual rendered bounds for
overlap checks; their Pretext height status is browser-only.
Run the same strict/WASM checks on `workbook/exploratory_figures.py` and verify
its heatmap/expanded controls remain available at `/exploratory/`; its saved
tables must load from the shared `/pivot/app/public/snapshots/` catalogue.
Check the page and wrapper navigation at narrow/normal/wide viewports, text
enlargement and keyboard operation. Marimo owns notebook controls; Pretext 1.0.0
measures the JavaScript pivot and wrapper/navigation, with readable wrapping as
its fallback. Keep `/pivot/app/` working as the marimo fallback.
Keep the existing workbook source and saved reference identities unchanged.

With `workbook/requirements-validation.txt` installed, run
`python workbook/validate_statistics.py`. Its independent statsmodels ML,
linear/binomial sandwich, ANOVA and quadrature comparisons must pass. Compare an
actual Pyodide report to native engine outputs at the recorded tolerances, including
cohort, estimates, likelihoods and gate results. Record different optimizer-bound
diagnostics honestly; they cannot alter the saturated trial R² ceiling conclusion.

For the descriptive extension also run `python workbook/validate_sigmoids.py`:
statsmodels KernelReg independently checks the selected Gaussian smoother and a
continuous nonlinear least-squares fit checks the profile grid's curve predictions.
Verify all 320 tuning scores, the four selected curves, and bootstrap outputs
against a real browser run. Preserve conditional-interval and selection limits.

For the PPS-shape extension, verify all 800 candidates, six nested outer folds,
explicit measured-range geometry, fair tuned-linear comparison and unsmoothed
curvature diagnostics. `validate_sigmoids.py` additionally checks Hotelling
statistics with statsmodels and an independent contrast basis. Visually inspect
both centered-data and normalized-model figures at publication size. A visible
curve imposed by constraints is not evidence of an observed PPS transition.

For literature/rationale updates, verify citation identity and actual access level,
retain contrary evidence and failed-search records, and distinguish completed
analyses from recommendations. Check rendered review links in both application
and editor views. A source's abstract, software implementation and full paper are
different evidence levels; unavailable Consensus access must remain explicit.

Only `analysis/prepare_publication.py` promotes a verified legacy browser download
into the manuscript. The results-only branch follows the separate gate below.
For questionnaires, also run `python workbook/validate_questionnaires.py` against
that browser report: independently check alpha through the covariance identity,
the ordinal sign test/exact interval and rank correlations; retain all 33
earlier associations with unadjusted p values. Check all nine numerical-delta
correlations and 16 moderation fits against SciPy/statsmodels; independently
verify the delta slope/SE/F/p against long-format participant-intercept Condition
× MAIA models. Verify HC3 covariance, order coding, centring and degenerate/missing
cases. Unit-test reverse scoring, incomplete subscales, invalid item/category
encodings, undefined statistics and a tied permutation against exhaustive
enumeration. Compare every questionnaire result across native/Pyodide runtimes.
Inspect both questionnaire figures and preserve the distinction between ordinal
rating direction, numerical category steps, unverified pictogram anchors and
unavailable PPS boundaries. Preserve owner-confirmed baseline-MAIA and
post-intervention spatial timing. Inspect the spatial-change correlation and
moderation figure, including all eight dimensions and both order specifications.

For individual proxies, run `python workbook/validate_participant_sigmoids.py`.
Verify 168 curves per plateau specification, 84 candidates, 500 parameter and
association resamples, six linked-record-safe outer folds and all 1,008 unadjusted
association tests including exclusion sensitivities. Check normalized trial RTs
against the unchanged source, retain zero-amplitude/uncertain-denominator flags,
and visually inspect every page of the raw/normalized atlas. Compare every
individual-result value across native/Pyodide. Keep the linkage issue visible and
do not equate constrained S shapes with reliable individual PPS boundaries.

For the remaining-analysis amendment, run `python workbook/validate_robustness.py`:
independent statsmodels full/reduced ML checks cover all 12 exclusion comparisons;
contrast identities, log-distance least-squares predictions and nine geometry
specifications have separate references. Compare all new results across runtimes
(ML uses the existing likelihood/coefficient tolerances). Verify 72 mean contrasts,
500 refits for every exclusion, 180 change-reliability records, 160 log-distance
candidates and 30 grouped-copy repeated selections. Inspect section 14 and the
new robustness figure. Keep selection stability distinct from calibrated intervals.

For parameter RM ANOVA/ANCOVA, the same robustness validator independently
checks 48 one-df ANOVA terms with statsmodels AnovaRM and 1,280 covariate terms
with OLS/HC3 references. Verify 332 terms per linkage cohort, 500 refits and valid
interval counts, all four within-person cells, eight separate baseline MAIA
dimensions, spatial delta/direction and both order specifications. Compare every
model field across native/Pyodide, inspect section 15 and the new parameter
figure, and retain conventional-versus-refit uncertainty distinctions.

For condition-matched spatial–PPS associations, the robustness validator also
checks 64 cell correlations with SciPy and 128 within/between model coefficients
with statsmodels OLS/HC3 and a long-format design. Verify the 64 reused delta
coefficients and intervals remain identical to their earlier models. Check all
500 refits/undefined counts, correct condition/phase matching, native/Pyodide
parity, section 16, both exported CSVs and the spatial–PPS figure. Participant
counts must not treat the two phases sharing one spatial rating as extra people.

For the results-only Bayesian branch, run all 57 unit tests and both strict marimo
checks. `validate_bayesian.py` independently checks 144 fixed-basis marginal
likelihoods against full-covariance multivariate Student-t densities and 80 WLS
coefficients against statsmodels. Verify 672 four-prior individual fits, 256 paired
contrast records, 256 cell-average records, 1,472 rank associations, 3,072 joint
coefficients, all distance-held-out predictions, ten split halves, 20 matched-noise
simulation replicates per scenario and the fine-grid comparison. Verify the actual
browser download and every numeric result against a separate native execution at
1e-8; inspect all 42 atlas pages, raw average curves, cell parameters and contrasts.
Exercise the independent button, participant selector, preview-filter independence,
download, editor/uploads and RPC stability. Keep linked recordings' draws/weights
paired. Check code/input/artifact hashes and published identity. The new results
manifest must declare `manuscript_updated=false` and retain the earlier version-1.9
reference. Preserve its nine engine files, manuscript sources and PDF byte-for-byte.
This phase requires the results report and roadmap, not manuscript compilation;
D-0012 supersedes the manuscript-refresh gate for these new results.
The requested fixed-posterior-median extension adds 96 conventional RM ANOVA terms;
check all F/p/df against statsmodels AnovaRM, verify pairing/missing/duplicate-cell
handling, and include the primary table and actual CSV download in browser parity.
Keep the omitted within-fit uncertainty explicit and all p values unadjusted.

For the baseline-corrected model comparison (D-0014), first fix the finite
numerical registry in `workbook/ANALYSIS_PLAN.md`. Verify the correction's sign and
participant/Condition/Phase matching, sparse/missing baseline handling, covariance
from reused baseline means, and free-intercept translation invariance. Check all
three experimental contrasts for every included sigmoid/linear/log-distance family;
linear/log-distance slopes must not be labelled sigmoid boundaries/sharpness.
Independent checks, null/known-effect recovery, model diagnostics, real browser
execution/download and complete results reporting are required before promotion.
The recorded goal and literature update do not satisfy these unrun numerical gates.

The owner's subsequent results-only request defers Pages documentation and
browser integration for the native batch in `analysis/baseline_effects/`. Its
executable registry is `results/baseline_effects/analysis_registry.json`, including
labelled numerical/post hoc amendments. Run its own unit/numerical checks, preserve
the unchanged public-data hashes, inspect every output figure, verify all result
counts and diagnostic flags, and hash the native results bundle. Shared baseline
covariance, full-trial versus sufficient-statistic likelihoods, analytically
marginalized likelihoods versus full multivariate normals, continuous refinement,
paired ANOVA and translation invariance have independent checks. Failed sampler
diagnostics and weak recovery remain findings rather than completed measurement
validation. Native-only execution must be explicit; the earlier browser gates
continue to apply to any future browser integration. Do not rebuild the site or
refresh manuscripts merely to deliver these native numerical results.

For the publication-method choice, run `analysis/publication_sigmoid_choice.py`.
It checks original input hashes, the complete convergence gate, full-draw response
reconstruction and midpoint/derivative geometry before packaging. Verify all 160
parameter records against the original posterior summaries, all 28 joint shape
contrasts against the original table, all 40 atlas pages and the ZIP/manifest bytes.
The standardized full-S panels must retain their model-illustration label and
shaded measured segment; these panels do not establish observed curvature or
justify independent-observation tests on shared pooled point estimates.

For the consistent-direction amendment, run the five tests in
`analysis/directional_sigmoid/test_model.py`, the specified full fit, all ten
positive/unrestricted held-distance refits and `report.py`. Verify the full-trial
marginal likelihood and truncated/Gaussian conditional reconstruction, convergence,
all 160 curves' monotonicity, paired parameter contrasts and matched prediction
targets. Inspect all 40 atlas pages and check the manifest/ZIP. A positive amplitude
interval follows from its prior support; never count it as evidence for the sign.
Preserve reversed raw observations and earlier signed results. Shared orientation
must not be described as shared numerical asymptote heights or observed plateaus.

For the explicit visible-S amendment, run the five checks in
`analysis/visible_sigmoid/test_visible.py`, both declared fits, five primary held-
distance refits and `make_report.py`. Verify endpoint bounds on every draw and
all 160 median-parameter curves; verify exact matching to the broad reference's
held-out trials. Inspect the normalized/actual-RT/boundary figures and all 40
atlas pages. Retain the prior-versus-posterior and width-cap diagnostics. The
shape, in-range midpoints and sharpness floor are prior guarantees, not evidence
of observed curvature or measurement precision. Label mean-parameter curves
separately from mean RT functions and preserve all existing input/output hashes.

For the trial-cleaning/rolling amendment, run all twelve checks in
`analysis/trial_cleaning/test_*.py`, `diagnostics.py`, the eight unadjusted and five
session-time full fits, and all twenty matched held-distance refits. Run both
report scripts, then `report.py package` and `validate_outputs.py`. Confirm the
original global filter is reproduced, early blocks retain both interventions,
no held AT outcome affects either training cutoff, and the rolling likelihood
matches an independently calculated joint normal with overlap covariance and
positive-amplitude restriction. Verify global time does not restart by condition
and the joint trend likelihood matches direct trial residualization. Inspect all
42 trial pages, 80 unadjusted and 40 session-time curve pages;
check every exported parameter/contrast, target identity, input/source/reference
hash and ZIP byte. Keep undefined small-sample SDs and incomplete fatigue-test
counts explicit. R² on five means/four rolling means is not trial-level R² or
physiological validation; all failed gates and the full effect family remain.

For legacy manuscript promotion, reconcile sample counts, models, captions and scientific interpretation with
that exact report. Compile from `manuscript/` using pdfLaTeX/BibTeX via `latexmk`;
inspect the resulting PDF visually, especially tables, figures, captions and
references. Archive the checked PDF with `--preprint-pdf` and rebuild the site.
Only manuscript contents are required for Overleaf.

For the derived Typst snapshot, compile `manuscript/typst/main.typ` with Typst
0.15.1. Check current canonical-source hashes, prose/caption content, all tables,
math punctuation and statistics, citation keys, labels and native references.
Render and inspect the complete PDF, especially wide tables and large figures.
Keep machine-specific conversion scripts, inventories and rendered QA in ignored
`.for-ai-local/typst-conversion/`; keep preview PDFs ignored. A format-only refresh
does not recompute or promote analysis results and does not replace the LaTeX gate.

Author review before submission remains distinct from computation: document
collection/stopping history, registration choices, ethics-statement details and
source-provenance limits. Never invent missing source-dependent checks or promote
an exploratory paired Bayes factor to the registered mixed-model comparison.

## Publication

Review/stage intended paths, commit, push without force or bypassing protections,
and verify exact remote SHA. Public repository visibility is owner-authorised
under D-0011; inspect tracked files and Git history before the visibility change,
then verify GitHub reports the repository as public. Check GitHub
Pages configuration and the exact deployment outcome, then visit both live views
and exercise browser analysis. Do not call the site live from a push alone.

A GitHub Actions budget block or denied Pages administration is an external
blocker. Prepare the tested artifact and publishing branch, then report the exact
repository-settings action required; do not ask again for already-given data-release
authorisation. Saving a cloud environment draft is separate from deploying Pages.

## Handoff

Report changes, checks and limits, control-plane updates, commit/remote state,
actual deployment status and the smallest remaining action. Keep raw logs and
transient run IDs outside the control plane.
