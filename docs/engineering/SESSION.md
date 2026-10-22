# Pivot frontend scope and evidence

The linked-chart extension uses structured series/row metadata from the same
worker result as the table, with SOA as the initial axis. No models, source CSVs,
saved numerical results or scientific cleaning changed. Settings update live;
chart style/measure remain presentation choices. Totals stay out of the chart;
nulls break lines and genuine zeros remain points. Shared hover/tap values handle
overlapping series; keyboard arrows navigate individual points. Generic saved
summaries cannot mix known measurement units on one chart axis. Density limits
request filtering and preserve the table/export instead of silently sampling.

Observed extension checks: 59 tests in the pinned Python 3.12 environment; all
60 Python/JavaScript parity cases plus point/cell identity, combined Condition/SOA,
unequal totals, missingness, text counts and mixed-unit fixtures. Strict/WASM checks
on all three notebooks and native pivot execution pass. The audited production
build passes with UTF-8 enabled on Windows. The compact default payload now has
SOA and is 51,603 bytes, below the existing 64 KiB budget. RTK was unavailable;
bounded native commands were used. No new product runtime dependency was needed.

`check_pivot_browser.cjs` exercises actual clicks, filters (800→160→800), full CSV
identity, summary/measure/grouping changes, empty/invalid/all-missing states,
keyboard point navigation, saved sources, an actually delayed uncached trial
request, partial-null line gaps, dense output and missing-Pretext fallback.
Its geometry matrix covers 320×568, 375×667, 640×360, 768×1024, 1280×800 and
1920×1080, including 200% text and spacing overrides; page edges, modal overflow,
SVG tick collisions and Escape/focus are checked. SVG text/word-spacing geometry
is browser-verified rather than a Pretext line-box parity claim. Physical iPhone/
Safari is untested. The chart and table use deliberate document flow on phones.
The Windows HTTP preview needs `.mjs` served as JavaScript. No private data enter
the preview or build.

Publication verified: implementation `e111a63` is included in deployed `c40d470`
on `main`, alongside the separately owned overview. The complete CI/reference
analysis, independent validation and Pages deployment pass. Live HTML, application,
chart, engine, layout and CSS bytes match the reviewed pivot source. The entire
browser regression passes against the live URL, including combined Condition/SOA
filters, exact CSV bytes, all source/measure/grouping changes and the six-size/
200%-text matrix. The earlier implementation-only run was superseded by the
combined build rather than a numerical failure. Concurrent overview edits in the
original checkout were preserved; the evidence update uses an isolated checkout.
The broader publication/scientific readiness goal remains open.

## Earlier table-only release

Replace only `/pivot/` with lightweight JavaScript and a worker, using build-time
JSON from the established Python preparation. Keep `/pivot/app/` as the marimo
fallback and preserve `/exploratory/`, the workbook/editor, scientific engines,
raw CSV bytes, saved results and manuscripts. Allowed changes: pivot assets,
static export, focused parity checks, build/CI integration and routed guidance.
The roadmap owns the active checklist; no new inference is part of this task.

Initial instruction/skill changes were excluded from the pivot implementation
commit and subsequently integrated by a separate repository update. Preserve
that work and the remaining untracked Typst review JSON. The local bibliography's existing CRLF hash mismatch is avoided by building
committed LF sources in an ignored isolated checkout; the user's file is unchanged.

Observed checks: 59 workbook tests; 60 JavaScript/Python parity cases, including
boolean/numeric column axes, weighted totals, missing data, counts, errors and
cohort/filter semantics. An intentionally wrong JavaScript mean fails the
hand-calculated regression. Strict/WASM checks and native pivot execution pass.
The audited production export passes, preserving both notebook pages and all
264 saved-table snapshots. Its assets match the current frontend source.

The production preview's first table rendered in 209 ms in one local Chromium
run, versus 38.4 seconds in one local marimo comparison; this is not a controlled
mobile/network benchmark. Default data is 46,023 bytes, below the 64 KiB build
budget. Full means, trials and saved tables load on selection. Actual browser
CSV download succeeded; all six rows/six columns match Python at 1e-10.

Browser checks cover 320×568, 375×667, 390×844, 640×360, 768×1024, 1280×800
and 1920×1080; default page/table regions have no overflow. At 200% text,
settings page through nine ordered controls without internal overflow even at
320×568. Short enlarged worksheets use deliberate outer document scrolling.
Text-spacing overrides are browser-verified; Pretext does not model word spacing.
Filters change 800→400→800, median and trial loading work, and saved-table search,
selection and aggregation were exercised. Physical iPhone/Safari remains untested.
Escape dismisses settings and returns focus to its trigger. A missing-Pretext
fixture retains readable text and settings pagination, with measurement explicitly
marked unavailable. Invalid axis assignments clear stale output and disable export.
Dialog resize observation measures newly opened filters/details; measurements use
fractional content bounds and block labels, avoiding false wraps from inline or
integer-rounded widths. Measured filter actions each fit on one line.
A deliberately delayed trial-load fixture verifies that rapid source changes keep
the latest participant selection when the older trial response arrives.

Publication: source `b84da44` on `main` passed the full CI, reference analysis,
independent numerical checks and exact Pages deployment. The live 375-pixel phone
view loads, filters 800→400→800, pages across both axes and exports the complete
native-verified CSV. Final deployed modal labels are measured and fit; the
exploratory notebook still runs. Group/control gaps grow with the window while
header/footer anchors remain inset without panel overflow. Local HTTP servers
were stopped. The broader living-publication and scientific goals remain open.
