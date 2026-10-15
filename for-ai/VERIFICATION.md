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

Expected release: 42 people and 17,114 unique observed trials. Exact schema, field,
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
and figures. A native run or export alone cannot establish browser execution.

## Numerical and manuscript checks

With `workbook/requirements-validation.txt` installed, run
`python workbook/validate_statistics.py`. Its independent statsmodels ML,
linear/binomial sandwich, ANOVA and quadrature comparisons must pass. Compare an
actual Pyodide report to native engine outputs at the recorded tolerances, including
cohort, estimates, likelihoods and gate results. Record different optimizer-bound
diagnostics honestly; they cannot alter the saturated trial R² ceiling conclusion.

Only `analysis/prepare_publication.py` promotes a hash-verified browser download.
Reconcile all sample counts, models, captions and scientific interpretation with
that exact report. Compile from `manuscript/` using pdfLaTeX/BibTeX via `latexmk`;
inspect the resulting PDF visually, especially tables, figures, captions and
references. Archive the checked PDF with `--preprint-pdf` and rebuild the site.
Only manuscript contents are required for Overleaf.

Author review before submission remains distinct from computation: document
collection/stopping history, registration choices, ethics-statement details and
source-provenance limits. Never invent missing source-dependent checks or promote
an exploratory paired Bayes factor to the registered mixed-model comparison.

## Publication

Review/stage intended paths, commit, push without force or bypassing protections,
and verify exact remote SHA. Preserve private repository visibility. Check GitHub
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
