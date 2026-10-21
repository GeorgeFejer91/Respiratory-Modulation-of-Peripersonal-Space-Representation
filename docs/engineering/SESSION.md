# Pivot explorer scope

Add a separate marimo pivot explorer under `/pivot/`, its portable preparation
and aggregation module, an explicit catalogue of tracked public result CSVs,
focused checks, and Pages build/CI integration. Preserve the existing workbook,
all statistical engines, raw CSV bytes, saved results and manuscripts.
The requested final UI has a minimal table and Activate filters switch at
`/pivot/`, with configuration collapsed under Pivot settings. Expanded controls,
heatmap and downloads remain on the separate `/exploratory/` subpage.

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

Final minimal-view checks: native filter activation changes 800 to 400 records;
deactivation restores 800 while preserving the chosen filter values. The same
on/off sequence was observed in the real browser. The default view shows only
the table, its filter switch, collapsed settings and source count. The expanded
notebook is preserved separately and both native notebook executions pass.

Publication: source `231cb0f` on `main` passed GitHub's complete build, reference
analysis, independent validation and Pages deployment. Both live subpages were
opened and executed. The published pivot was checked through 800→400→800 filter
toggling, and Exploratory figures loaded its saved source through the shared
catalogue. Unrelated instruction/review changes remain untouched.
