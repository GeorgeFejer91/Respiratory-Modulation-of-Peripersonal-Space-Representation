# Verification and readiness gates

Evidence must match the claim. Missing dependencies, credentials, hardware, or
runtime access produce `BLOCKED` or `NOT RUN`, never `VERIFIED`.

## Result vocabulary

- `VERIFIED`: the named check directly observed the claimed surface and passed.
- `PARTIAL`: some required evidence passed and the missing scope is named.
- `BLOCKED`: a concrete external or authority blocker prevented the check.
- `NOT RUN`: the check was intentionally not applicable or not attempted, with
  the reason stated.

## Gate 0: bootstrap readiness

From the repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File for-ai/scripts/check-context.ps1 -ProjectRoot . -RequireRemote
git status --short
git rev-parse HEAD
git ls-remote origin refs/heads/main
```

Pass when the context checker succeeds, the intended tree is clean, and local
`HEAD` equals `origin/main`.

## Gate 1: task contract

Before implementation, name:

- the observable user outcome;
- affected product surface and owner;
- acceptance criteria;
- focused check that can fail for the requested behavior;
- broader checks required by affected boundaries;
- explicitly deferred work.

## Gate 2: focused change

From the repository root, check the deidentified participant and trial keys:

```powershell
py for-ai/orchestration/public_data.py check data/raw
```

The current candidate should have `P000`-`P041` and 17,114 unique trial rows.
The checker rejects unexpected columns, source codes and paths, duplicate IDs,
and trial rows without a participant. It does not establish consent or eliminate
all reidentification risk.

## Gate 3: integrated readiness

Compile `manuscript/main.tex` from inside `manuscript/` using pdfLaTeX and
BibTeX or `latexmk -pdf`; inspect the resulting PDF for missing figures,
citations, and layout defects. Only the `manuscript/` contents may be needed in
Overleaf. Before claiming current results, rerun the approved models on the
42-person CSVs and reconcile every sample size, statistic, and result figure.
Classify deviations from the preregistration explicitly.

Public release additionally requires a documented consent, ethics, and access
review; the private repository setting is not that review.

## Gate 4: publication

1. Review status and diff; preserve unrelated changes.
2. Confirm only intended paths are staged.
3. Confirm all required gates passed or are honestly reported.
4. Create one coherent commit under normal repository policy.
5. Push without force and without bypassing protection or secret scanning.
6. Verify the remote commit and required CI/deployment for that exact SHA.

Do not change visibility to public while the consent review or 42-person
manuscript refresh remains open.

## Handoff evidence

Report exact commands or observed surfaces, results, untested scope, commit SHA,
remote synchronization, CI/deployment state, and whether `for-ai/` changed.
