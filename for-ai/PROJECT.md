# Project contract

## Purpose and primary goal

Publish the Study 5 paper's reproducible analysis as a live marimo companion on
GitHub Pages. Readers must be able to run preparation, every data-supported model,
diagnostics and figures entirely in the browser and download the analysis record.
Maintain a self-contained Overleaf draft reconciled to an actual 42-person browser
run. The project owner authorised public release of the deidentified data and
confirmed ethical approval; see `workbook/DATA_RELEASE.md`.

The active goal is to extend the analysis to four sigmoid transitions
characteristic of peripersonal-space experiments (Control/Viscereality ×
Exhale/Inhale): visible lower and upper bends within the sampled range, an
interpretable midpoint, and measurable steepness. Use a uniform, scientifically
justified extraction/smoothing/fitting procedure; evaluate predictive performance
against equally processed lines and inspect the figures visually. Report when
the measurements do not support the desired shape. An imposed S shape or a
sigmoid that appears only after extrapolation does not complete this goal.

The earlier 320-pipeline analysis produced four computable descriptive curves,
but all four 10–90% transitions exceed the measured range. That computational
milestone does not satisfy the new shape requirement. Maintain the full method
audit and uncertainty, run the extension in the browser, and reconcile the Results
to the actual browser download. The original participant fit gate and the evidence
needed for a physiological PPS boundary remain separate.

The current evidence goal is to make the rationale for this exploratory extension
scientifically defensible. Maintain a miniature review in `literature_review/`
with supporting and contrary PPS evidence, method-to-claim links, search/access
records, and explicit unresolved checks. Use Consensus when configured and the
installed multi-source search workflow; disclose unavailable providers. Completion
means a traceable rationale and calibrated claims, not a guaranteed sigmoid or a
retrospective claim of preregistration. Link the review from the browser companion
and reconcile its conclusions with the manuscript.

## Non-goals

- No names, source IDs/paths, private crosswalks, collection dates or recordings
  in the public artifact; keep verified backups outside it.
- Do not change the source repository's private visibility.
- No exploratory result presented as preregistered or author-approved final work.
- Do not fabricate physiological compliance, provenance or gated boundary results.

## Ownership

- `workbook/`: marimo application/editor, shared schema and preparation checks,
  fixed analysis contract, portable inference, reports, figures and Pages build.
- `data/raw/`: audited release CSV pair, arbitrary contiguous participant IDs.
- `analysis/prepare_publication.py`: consumes verified browser results to refresh
  manuscript statistics, tables, figure assets and the compiled draft manifest;
  it does not recompute models.
- `manuscript/`: self-contained Overleaf source and figures. `results/` and
  `figures/`: browser-produced publication-draft artifacts and native validation.
- `literature_review/`: focused scientific synthesis, evidence table, analysis
  rationale and reproducible search record; no participant data or copied papers.
- `for-ai/`: agent instructions, historical writing and source analyses.
  `.for-ai-local/`: ignored builds and local diagnostics.

## Verified scientific boundaries

The released cohort contains 42 independent people (`P000`–`P041`) and 17,114
observed trials. The active manuscript now derives from that browser analysis;
the 40-person text/figures are archived. Author review remains necessary before
submission, including collection/stopping history, ethics-statement details and
registration interpretations. The public CSVs cannot reproduce waveform timing,
measured belt compliance, dates, version labels or private source-onset exclusions.

The [registration](https://aspredicted.org/az9f89.pdf) remains the registration
source. `workbook/ANALYSIS_PLAN.md` states the executable operationalisation,
explicit ambiguities and computational bounds. Fit-gated follow-ups remain not
estimable when the gate fails. Native numerical agreement is distinct from
browser verification; source pushes are distinct from successful deployment.
