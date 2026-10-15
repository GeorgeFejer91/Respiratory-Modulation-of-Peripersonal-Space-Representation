# Browser analysis record

`browser-analysis/` contains the exact Pyodide download, full JSON report,
Markdown report, model/coefficient tables and diagnostics from the released
42-person data. The ZIP also includes retained RTs, figure SVGs and exact engine
source. Its manifest hashes inputs, code and outputs. These are reproducible
analysis-draft results for author review.

`independent-validation.json` records native statsmodels and quadrature comparisons;
these checks do not supply the browser's results. `browser-native-parity.json`
records cross-runtime likelihood/coefficient agreement and nonlinear-bound
diagnostic differences. `study5-preprint.pdf` is the
compiled working draft, with source/PDF/browser-ZIP hashes in `preprint_manifest.json`.

Regenerate only from an actual browser download using
`analysis/prepare_publication.py`; follow `workbook/README.md` for PDF preparation.
Do not manufacture estimates for unavailable provenance or gated boundary outcomes.
