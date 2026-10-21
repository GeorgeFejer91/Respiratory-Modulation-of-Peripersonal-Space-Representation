# Fast pivot frontend scope

Replace only `/pivot/` with lightweight JavaScript and a worker, using build-time
JSON from the established Python preparation. Keep `/pivot/app/` as the marimo
fallback and preserve `/exploratory/`, the workbook/editor, scientific engines,
raw CSV bytes, saved results and manuscripts. Allowed changes: pivot assets,
static export, focused parity checks, build/CI integration and routed guidance.
The roadmap owns the active checklist; no new inference is part of this task.

Initial unrelated local changes in AGENTS.md, for-ai/README.md, for-ai/SKILLS.md,
untracked for-ai/skills/ and the Typst review JSON remain excluded. The existing
committed visualization-skill routing is preserved. Do not reset or absorb this
work. The local bibliography's existing CRLF hash mismatch is avoided by building
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

Publication: implementation validation is complete; commit, full CI and exact
Pages deployment/live execution are the remaining gate. Keep the overall
scientific inference goal open.
