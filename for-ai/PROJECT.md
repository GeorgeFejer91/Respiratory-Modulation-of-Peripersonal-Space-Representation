# Project contract

## Purpose

Publication manuscript, deidentified dataset, and reproducible analysis materials for the Study 5 peripersonal-space experiment.

## Primary goal

Prepare a standalone, Overleaf-compatible Study 5 preprint and a deidentified,
unified behavioral dataset, then promote only reviewed analyses to the
publication-facing folders.

## Non-goals

- No participant names, original source IDs, acquisition paths, private
  crosswalks, collection dates, or raw recordings in this repository.
- No public release before consent, ethics, and access terms are confirmed.
- No exploratory result presented as a preregistered or final analysis.

Add project-specific non-goals only after they prevent a plausible wrong turn.

## Product/control-plane boundary

- Product source and deliverables: `manuscript/`, `data/raw/`, `analysis/`,
  `figures/`, and `results/`.
- Agent orchestration and durable project memory: `for-ai/`.
- Local generated diagnostics and scratch evidence: `.for-ai-local/` (ignored).

## Architecture and ownership

`manuscript/main.tex` is the self-contained Overleaf entry point; its active
sections, bibliography, and figures are adjacent. `data/raw/` holds two
deidentified CSVs with one contiguous person ID system. `for-ai/orchestration/`
owns data-export checking and exploratory analyses. Once an analysis is agreed,
its reproducible pipeline moves to `analysis/`, with accepted figures and
machine-readable statistics in `figures/` and `results/`. Prior prose stays in
`for-ai/writing-archive/`.

## Current verified state

- Private GitHub repository initialized on 2026-10-02.
- Data candidate contains 42 independent people (`P000`-`P041`) and 17,114
  selected primary behavioral trial rows; both CSVs passed the ID/privacy check.
- The active preprint text still reports the older 40-person analysis. Its
  statistical claims and result figures are pending a 42-person rerun.
- The [AsPredicted registration](https://aspredicted.org/az9f89.pdf) is the
  public preregistration source. It does not by itself clear analysis departures.

Git and runnable checks are the authority for branch, revision, and behavior.
Do not turn this section into a second status ledger.
