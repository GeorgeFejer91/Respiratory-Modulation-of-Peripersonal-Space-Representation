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

The extension includes 320 original and 320 constrained sigmoid pipelines plus
160 equally processed lines; six nested outer participant folds with all inner
selection scores; unsmoothed curvature tests; and 1,000 participant bootstrap
refits per selected sigmoid family. All four constrained curves visibly bend,
but active constraints and weak predictive support leave the data-supported PPS
goal unresolved. Centered observations and normalized model geometry are separate
figures. The original participant fit gate is retained.

`sigmoid-independent-validation.json` records independent kernel, continuous
sigmoid and Hotelling checks. Cross-runtime comparison covers every descriptive
and shape-audit number at tolerance 1e-8. Candidate records are matched by method
identity because mathematically tied linear projections can reorder by roundoff;
selected methods must match exactly and any ranking changes must be score ties.

Regenerate only from an actual browser download using
`analysis/prepare_publication.py`; follow `workbook/README.md` for PDF preparation.
Do not manufacture estimates for unavailable provenance or gated boundary outcomes.

Questionnaire outputs include all 37 item distributions, eight independently
recomputed MAIA-2 scores/reliability intervals, all 64 spatial transitions and the
exact paired sign comparison, 33 rank associations with permutation/Holm inference,
28 descriptive inter-scale correlations and a domain coverage table. The browser
uses 2,000 bootstrap draws and 19,999 permutations per association.
`questionnaire-independent-validation.json` records independent covariance-alpha,
exact ordinal, rank-correlation and multiplicity references. Cross-runtime parity
compares every questionnaire value and status at tolerance 1e-8.
