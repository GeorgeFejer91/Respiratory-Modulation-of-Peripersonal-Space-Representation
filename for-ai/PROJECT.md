# Project contract

## Purpose and primary goal

Publish the Study 5 paper's reproducible analysis as a live marimo companion on
GitHub Pages. Readers must be able to run preparation, every data-supported model,
diagnostics and figures entirely in the browser and download the analysis record.
Maintain a self-contained Overleaf draft reconciled to an actual 42-person browser
run. The project owner authorised public release of the deidentified data and
confirmed ethical approval; see `workbook/DATA_RELEASE.md`.

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
