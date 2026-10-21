# Pivot explorer scope

Add a separate marimo pivot explorer under `/pivot/`, its portable preparation
and aggregation module, an explicit catalogue of tracked public result CSVs,
focused checks, and Pages build/CI integration. Preserve the existing workbook,
all statistical engines, raw CSV bytes, saved results and manuscripts.

Initial state: `main` at `b96a2e3`; local instruction changes in `AGENTS.md`,
`for-ai/README.md`, `for-ai/SKILLS.md`, untracked `for-ai/skills/`, and an
untracked Typst review JSON predate this task and stay outside its commit.

Verify aggregation against hand-calculated unequal-size groups, missing values,
counts, totals and no-axis cases; verify baseline sign/matching and cohort
selection; run workbook tests, strict/WASM notebook checks, audited production
build and actual browser interactions/downloads. Exercise responsive layout.
Publication is complete only after the exact commit deploys and the live page
loads and reacts. Existing inference and its open roadmap remain unchanged.

Local evidence: 59 workbook tests, strict and WASM notebook checks, native
notebook execution and isolated production export pass. A deliberately wrong
mean fails the totals regression. Browser CSV payload matches native values at
1e-10; median aggregation, phase filtering, saved session-table selection and
heatmap rendering were observed. The page and notebook reflow at 320 CSS px.
Browser download clicks could not be captured by the in-app browser (including
ordinary eager links); file-save capture remains unverified. The working
checkout's pre-existing CRLF bibliography mismatch was avoided by building the
committed LF sources in an ignored isolated checkout, without changing the file.
