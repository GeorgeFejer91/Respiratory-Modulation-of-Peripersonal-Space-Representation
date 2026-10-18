# Verification and readiness gates

Evidence must match the claim. Use VERIFIED, PARTIAL, BLOCKED and NOT RUN precisely;
unavailable metadata and fit-gated outcomes are not computed null results.

## Bootstrap and task contract

Read the routed context, inspect status, and name the observable outcome and owner.
Preserve unrelated work. Run `pwsh -NoProfile -File for-ai/scripts/check-context.ps1
-ProjectRoot . -RequireRemote`; remote mismatch during intentional development
must be reconciled by a normal validated push, never by resetting user work.

## Workbook and data

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
