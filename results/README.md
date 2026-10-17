# Results and reproducibility

## Active results-only analysis

Start with [RESULTS_REPORT.md](RESULTS_REPORT.md) for the level-by-level findings
and [the question checklist](../for-ai/ANALYSIS_ROADMAP.md) for completion status.
`bayesian/` contains the separate real-browser Bayesian approximation, four prior
specifications, individual parameters, experimental contrasts, spatial/MAIA joint
exploration, figures and atlas. `bayesian-independent-validation.json` records
independent probability/regression checks and actual native/browser parity.
The original `browser-analysis/` reference and manuscript PDF stay at version 1.9;
manuscript drafting is paused. Bayesian fitting is not assumption-free, and its
finite medians do not establish physiological boundary identification.


## Earlier browser analysis record

`browser-analysis/` contains the exact Pyodide download, full JSON report,
Markdown report, model/coefficient tables and diagnostics from the released
42-participant-record data. The ZIP also includes retained RTs, figure SVGs and exact engine
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
exact paired sign comparison, numerical spatial deltas, 42 rank associations
with unadjusted permutation inference, 16 Condition × MAIA moderation fits,
28 descriptive inter-scale correlations and a domain coverage table. Eight
baseline-MAIA versus post-intervention-delta correlations are the main follow-up;
direction-only and earlier absolute-rating associations remain supplementary.
The moderation fits report ordinary and HC3 uncertainty with/without presentation
order. The browser uses 2,000 bootstrap draws and 19,999 permutations per
association. MAIA is measured once before the experiment, not as a mediator.
`questionnaire-independent-validation.json` records independent covariance-alpha,
exact ordinal and rank-correlation references, all 16 OLS/HC3 comparisons and
long-format repeated-measures interaction equivalence. Cross-runtime parity
compares every questionnaire value and status at tolerance 1e-8. All questionnaire
p values are unadjusted and intervals are pointwise.

The individual extension adds 168 four-cell proxies, 84 candidate methods and
separate/shared-plateau specifications. `participant_normalized_rt.csv` preserves
all 8,916 retained AT RTs and adds unclipped fitted-plateau normalization and
instability flags. `participant_curve_atlas.pdf` shows all 42 records, with raw RTs
above common 0–1 fitted geometry. Midpoint split-half reliability is low (.047
separate; .106 shared), and every main refit-bootstrap association interval includes
zero. Complete parameter tables, 1,008 unadjusted tests across both models and
three linkage exclusions, recovery checks and their inputs are retained.

**Source linkage requires review:** P011 and P033 share all 408 behavioural trial
records with condition labels swapped, despite different questionnaire responses.
Source CSVs are unchanged. Full-release behavioural inference and RT–questionnaire
links are provisional; numerical agreement is not evidence of independent
recordings. `participant-sigmoid-independent-validation.json` checks scalar grid
objectives, independent smoothing, conditional shared-plateau OLS, all 1,008
Spearman coefficients, normalized RTs and linked-record folds. Cross-runtime parity
covers every new result at tolerance 1e-8.
