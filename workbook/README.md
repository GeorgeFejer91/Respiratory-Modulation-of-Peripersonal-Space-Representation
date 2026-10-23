# Browser analysis and living publication

GitHub Pages is the primary target for the current paper and its analysis.
The existing workbook/editor and explorers remain executable; the complete
HTML-paper integration and browser migration of newer native-only models are
tracked in the [publication roadmap](../for-ai/ANALYSIS_ROADMAP.md). Saved result
tables do not mean their producing models run here. Current-paper HTML authoring
uses verified outputs, while the version-1.9 manuscript/reference stays historical.

The development environment includes the HyperFormula, Handsontable and Univer
integration skills, routed in [for-ai/SKILLS.md](../for-ai/SKILLS.md). Those
instructions guide future formula/grid work; their runtime libraries have not
been added to this site. Keep the current preparation, statistical engines and
fast pivot as the authoritative implementations until a scoped replacement
passes numerical and real-browser checks.

Segment 0 fixes the X-axis to the released SOA values: **300, 800, 1500, 2200,
2700 ms**. **Group curves by** has one checkbox for **Condition** and one for
**Phase**, both initially checked. Both checked shows four Condition × Phase
curves. Condition only shows two condition curves pooled over phases; Phase only
shows two phase curves pooled over conditions. Neither checked shows one curve
pooled over both factors. Pool within each participant before across-person mean
and sample SD: every state retains all source cells and equal participant weight.
The table and CSV use the same grouping. There is no field dragging or editable
axis layout in this segment.

The **Baseline correction** toggle starts on: **Baseline − RT (ms)**, using the
existing retained participant × condition × phase baseline mean. Positive values
indicate faster-than-baseline responses; negative values remain visible. Switch
it off for uncorrected RT. The adjacent **Normalize RT** toggle starts off.
Choose **0–1 range (min–max)** or **Z-score (mean 0, SD 1)** in **Normalization
method**. Each participant's reference distribution uses all their retained AT
trials pooled across both conditions, both phases and all SOAs, before any
display selections. The same normalization then applies to cell means and the
across-participant summary. Baseline correction works with either method:
normalize raw RT with correction off, or Baseline − AT RT benefit with it on.

Z-scores use each participant's mean and sample SD (n−1); min–max uses their
minimum/maximum. Missing values remain missing and zero/undefined scale gives
missing scores. Changing grouping does not recalculate the scale. CSV names end
in _z or _norm respectively; millisecond measures keep _ms. Raw scores increase
with slower RT; corrected scores increase with greater baseline benefit.
These are descriptive display transformations, preserving data and fixed
analyses. See [normalization methods and researched sources](RT_NORMALIZATION.md).
Mean ± SD whiskers are not confidence intervals and may extend beyond 0–1.

**Display** selects means with or without sample SD in both views. Full-value
details and CSV retain SD/n. **Pivot settings** keeps cohort and calculation
controls; the standalone pivot below provides the broader field/filter/source
catalogue. Nonnegative plots start at zero; negative values remain visible with
a labeled zero reference.

In Segment 0's Mean view, **Show together** lets you combine **Mean ± SD**,
**Mean line**, **Participant dots**, **Spaghetti** and **Violin** independently.
Choose Mean only in Display to hide the sample-SD whiskers. Participant values
are actual per-person means after pooling unchecked factors, not trial rows;
they follow the same baseline and normalization controls. Spaghetti joins the
same person within each group, with gaps for missing SOAs. Violins are smoothed
participant distributions, with their bandwidth/trim shown below the chart;
width does not encode sample size, and n < 3 or constant groups have no violin.
**Download participant values (CSV)** exports these values at full precision.
Summary table/CSV values do not change when switching figure layers. For other
aggregations, the existing Chart style selector remains available.

The [pivot explorer](https://georgefejer91.github.io/Study5_Publication/pivot/)
is a lightweight JavaScript subpage with a pivot table and linked chart. The
initial chart uses SOA (ms) on x and Condition × Phase as series, showing mean
corrected RT (ms). Both views use the same worker result: field assignments,
summary, cohort and filter changes update them immediately. Switch on
**Activate filters** to choose fields and values to keep. Switching it off ignores
those selections and restores every record in the chosen cohort. Open
**Pivot settings** to choose participant-distance means, every trial,
participant/questionnaire records or a saved analysis table, then assign Rows,
Columns, Values and a summary function; **Done** closes settings. Numeric
summaries offer numeric Values fields; counts also allow text. **Export CSV**
downloads every pivot row and column. The table shows the complete result at
once, scrolls within its own viewport, and has height and width controls. No
Next/Previous buttons page table data, field choices or settings groups. Settings
stretch with the available space and keep all ordered groups visible.
CSV downloads retain full precision; displayed summaries use six significant digits.
The read-only table supports rectangular cell selection: drag, Shift-click, or
use arrows with Shift to extend a range, then Ctrl+C/⌘C or **Copy selection**.
On touch screens, tap the first cell, enable **Extend selection**, and tap the
last cell. **Select all cells** includes headers. Copied tab-separated rows paste
directly into Excel, retaining full precision and blank missing cells. **Mean ± SD**
copies as one text cell; select **Mean only** for numeric cells. A new result
clears the selection; the released data remain read-only.
Use **Chart style** for automatic, line, points or grouped bars. A multi-measure
pivot exposes **Chart measure**, keeping different measures off the same y-axis.
Other row fields split into additional series; column groups keep their pivot
identity. Table scrolling and sizing leave the chart unchanged. Hover/tap compares every
series at that x; keyboard focus and arrow keys read individual points. Numeric
x values keep their actual spacing in line/point views; categorical bar positions
refer back to full labels on points and table rows. Grand totals are omitted from
the chart, missing cells break lines, and actual zeros remain visible. Lines
connect descriptive summaries and supply no fitted model or inferential interval.
Mixed measurement units in generic saved summaries require a parameter/quantity/
units filter before plotting. Dense charts show an explicit filter request above
4,000 cells, 48 series or 100 x values; the full table and export remain available.
On narrow screens, chart and the internally scrollable table use ordinary document
scrolling.

The default is the 40-person behavioural cohort; select Full release for all 42
records. The page performs descriptive aggregation and never refits saved models.
Saved-table snapshots are built from tracked result CSVs, record their source
hashes, and load only the selected table. Initial data stays below a 64 KiB build
budget; full field sets, trial records and saved tables load on demand. A worker
performs the aggregation. Locked Pretext 1.0.0 measures labels after the first
table, with readable browser wrapping as fallback. Text enlargement is preserved;
very short enlarged layouts use ordinary document scrolling.
`pivot_static.py` exports the existing `pivot_data.py` preparation, sharing the
established cleaner and questionnaire scorer. JavaScript/Python parity is checked
with `python workbook/check_pivot_javascript.py` (Node 22 or later). With
Playwright/Chromium available to Node, `node workbook/check_pivot_browser.cjs
http://127.0.0.1:8765/pivot/` checks an HTTP-served build, including real selections,
CSV downloads, missing/empty/error states, source races and rendered text geometry.
The [marimo pivot notebook](https://georgefejer91.github.io/Study5_Publication/pivot/app/)
remains available; run it locally with `marimo run workbook/pivot_explorer.py`.

The [Exploratory figures](https://georgefejer91.github.io/Study5_Publication/exploratory/)
subpage keeps the expanded explorer, heatmap, source inspection and separate
CSV/settings downloads. Its source is `exploratory_figures.py`; both pages share
the same authoritative preparation and saved-result snapshot catalogue.

The original `corrected_rt_ms` is AT minus the retained participant × condition × phase Baseline
mean, in ms. Default means weight participant-distance cells equally; trial
summaries weight trials equally. MAIA is baseline-only and spatial ratings are
per condition, with unverified pictogram anchors. Questionnaire values repeated
over distance cells are not additional participants. Saved model summaries retain
their original uncertainty/diagnostic limits; their aggregation is descriptive.

The marimo application executes the released Study 5 analysis entirely in the
reader's browser using Pyodide. The published default loads the deidentified
42-record, 17,114-trial dataset. The active **Run Bayesian parameter analysis**
branch runs separately: individual posteriors, simpler-model prediction, prior
sensitivity, reliability/recovery, paired Condition × Phase contrasts and spatial
× MAIA exploration. Its download has its own manifest and 42-page raw/conditional
geometry atlas. See the [results-only report](../results/RESULTS_REPORT.md) and
[ordered checklist](../for-ai/ANALYSIS_ROADMAP.md). No historical-manuscript refresh is required;
the earlier version-1.9 paper/reference remain preserved.

Select **Run complete paper analysis** to compute
models, diagnostics, figures and the complete result download. The fixed
[analysis contract](ANALYSIS_PLAN.md) governs this run; exploratory preparation
filters above it do not change the paper's estimates.

## How Codex connects to marimo

The GitHub repository is the connection. Codex edits `data_preparation.py` and its
Python helpers here; marimo turns those cells into a reactive workbook. Changes
pushed to `main` trigger the Pages workflow. No marimo account, API token or
Python server is needed for this browser deployment.

The application is at `/Study5_Publication/`; `/Study5_Publication/editor/` exposes
the editable Python cells. Browser edits can be downloaded but do not automatically
commit to GitHub. Commit reviewed edits to the repository to update the shared site.
In the editor, use the run button to start the cells.

## Use the companion

1. Open the application and inspect the published-data audit.
2. Explore preparation controls or upload a complete CSV pair using the documented
   schemas. A partial upload stops; it never falls back to demonstration data.
3. Run the complete analysis and inspect model status, uncertainty, sigmoid gates
   and the unavailable-provenance record.
4. Download the complete analysis before refreshing. It includes JSON, Markdown,
   model/diagnostic CSVs, retained RTs, SVG figures, source code and SHA-256 hashes.

Synthetic demonstration data are a separate labelled option. Uploaded file
contents are processed in browser memory without a processing backend. Refresh
clears the session. Runtime/package downloads need internet access and a modern
browser. The published reference download and working preprint are labelled as a
prior browser run and an author-review draft; live results compute from the selected
inputs. An unsuccessful fit or unavailable source check is never silently replaced.

## Analysis and numerical verification

`paper_analysis.py` owns the pipeline; `inference.py` implements portable NumPy/SciPy
statistics; `preparation.py` owns shared schemas, preparation and release checks;
`publication_report.py` generates result bundles and Matplotlib figures;
`questionnaires.py` owns MAIA-2 scoring/reliability and ordinal spatial-frame
analyses. `bayesian_sigmoid.py` owns the unpooled conjugate/grid Bayesian reference
and modular uncertainty propagation; `bayesian_report.py` owns its separate
tables/figures/download. This is not a full joint hierarchical nonlinear model. The
[contract](ANALYSIS_PLAN.md) distinguishes primary questions, sensitivities,
supplementary analyses and registration ambiguities. It documents fixed nonlinear
bounds and the unavailable private metadata.

Native reference validation uses statsmodels independently of the browser engine.
`validate_bayesian.py` additionally checks the marginal likelihood with an
independent multivariate Student-t reference and bootstrap regressions with WLS.
Its `--report <native-json> --browser-zip <actual-download>` mode verifies every
new result across the two executions. Promote results-only browser artifacts into
`results/bayesian/`; the site build requires their exact code/input/artifact hashes
and browser-validation identity. Do not use `prepare_publication.py` for this branch
as part of the living HTML publication workflow.
The archived report and [results](../results/README.md) record both execution surfaces.
The original participant-boundary inference remains gated when trial-level fits fail.
A separately labelled individual-proxy extension exports four exploratory curves
per record, 0–1 fitted-plateau normalization, a shared-plateau sensitivity, all
questionnaire links and a 42-page atlas. These proxies have weak reliability and
do not meet the original boundary criterion. P011 and P033 share identical RT
recordings with reversed condition labels; source linkage is unresolved, so
full-release behavioural inference and RT–questionnaire links are provisional. Same-label Baseline subtraction is descriptive.

## Develop, verify and build

From the repository root, with Python 3.12 or later and `uv` installed:

```bash
python3 -m venv .for-ai-local/workbook-venv
.for-ai-local/workbook-venv/bin/python -m pip install -r workbook/requirements.txt uv
.for-ai-local/workbook-venv/bin/marimo edit workbook/data_preparation.py
```

Use `marimo run workbook/data_preparation.py` for a native application. In the
prepared Codex environment first source `/workspace/.study5-environment/env.sh`.
Native modes execute on that machine; the exported Pages site runs in the browser.
Do not expose an unauthenticated native editor publicly.

```bash
python -m unittest discover -s workbook -p 'test_*.py' -v
python for-ai/orchestration/public_data.py check data/raw
marimo check workbook/data_preparation.py --strict
marimo check workbook/data_preparation.py --select MW --strict
python workbook/build_site.py
```

For independent numerical checks:

```bash
python -m pip install -r workbook/requirements-validation.txt
python workbook/validate_statistics.py
python workbook/validate_sigmoids.py
python workbook/validate_questionnaires.py
python workbook/validate_participant_sigmoids.py
```

The build exports both application and editor with their local helper modules,
without execution snapshots. It includes exactly the two audited CSVs in each
view, release/analysis records, the reference browser download and the working
preprint. Changed release hashes or preprint sources stop the build. Keep private
backups, crosswalks, recordings and execution caches outside the public artifact.
Serve `.for-ai-local/site` over HTTP for browser verification, including real
analysis/downloads and malformed/partial-upload handling. Native execution and
HTML export alone do not verify browser computation.

After a new browser analysis, refresh the paper and tables without re-running models:

```bash
python analysis/prepare_publication.py path/to/browser-results.zip
cd manuscript
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=../.for-ai-local/build main.tex
cd ..
# Visually inspect the compiled PDF before archiving it.
python analysis/prepare_publication.py path/to/browser-results.zip --preprint-pdf .for-ai-local/build/main.pdf
python workbook/build_site.py
```

When the engine changes, first use `python workbook/build_site.py --development`
to create an unpublished browser verification build. It deliberately omits the
stale reference record and PDF. Run/download the new analysis in the browser,
promote it, rebuild/review/archive the PDF, then run the default release build.
The default build still requires all engine/reference/paper hashes to match.

The [PPS sigmoid-shape extension](SIGMOID_EXPLORATION.md) compares 320 original
sigmoid pipelines, 320 explicitly shape-constrained pipelines and 160 equally
processed lines. It reports four midpoint/width/slope estimates per sigmoid
family, conditional participant-bootstrap uncertainty, nested participant
prediction and unsmoothed curvature tests. Centered data plots and normalized
model-only plots expose the difference between visible geometry and empirical
support. The latter remains weak in the reference dataset; four imposed S shapes
do not establish physiological boundaries. Full rankings, inner selection scores,
comparisons, constraints and extrapolations are downloadable.

The remaining-analysis section adds primary RT models for all three recording
exclusions, 500 refits for every exclusion's associations and mean parameter
contrasts, and reliability/recovery of the within-person changes. Its 40-record
group audit compares five response families including log distance, nine fixed
geometry specifications and 30 repeated method selections. These finite checks
are complete and remain exploratory; waveform provenance, recording identity
and validated physiological boundaries remain unresolved. Verify them with
`python workbook/validate_robustness.py`.

## Condition-matched spatial ratings and PPS

Section 16 matches each condition's spatial rating to its Exhale/Inhale PPS
midpoint and normalized sharpness. It reports cell-specific rank correlations
and separates mean spatial level between people from condition change within
people, including phase dependence and presentation-order sensitivities. The
two phases share one rating per condition and do not count as extra participants.
Both plateau assumptions, all recording exclusions and 500 curve-refit intervals
remain available. The export adds `spatial_cell_associations.csv` and
`spatial_parameter_models.csv`: 192 estimates, including 64 reused delta-model
coefficients, so 128 nominal tests are added. All p values are unadjusted.

## Publish on GitHub Pages

The owner authorised making the source repository public on 2026-10-16,
superseding its earlier private visibility. Dataset publication is explicitly
authorised in [DATA_RELEASE.md](DATA_RELEASE.md). Private backups, identity
records and raw recordings remain outside the repository and deployment.

For automatic builds, choose **Settings → Pages → Build and deployment → Source:
GitHub Actions**. The **Publish browser workbook** workflow tests/builds/deploys on
relevant pushes to `main`, and can be run manually. GitHub Actions must have an
available budget; source write access does not imply permission to enable Pages.

An already-built `gh-pages` branch is an alternative publishing source. Select
**Deploy from a branch → gh-pages → / (root)** and save. GitHub still manages its
Pages deployment; confirm its outcome. Refresh that branch with reviewed output
from `python workbook/build_site.py`, using a normal commit and push without force.
Do not merge generated site files into `main`.

After successful deployment, verify both the application and editor at
`https://georgefejer91.github.io/Study5_Publication/`. A pushed commit or a prepared
publishing branch is not proof that the website is live.

The [questionnaire review](../literature_review/QUESTIONNAIRES.md) covers all
37 items/eight dimensions, paired spatial ratings, exact ordinal inference,
numerical change correlations and Condition × baseline-MAIA moderation. MAIA-2
was completed once before the experiment; spatial ratings followed each
intervention (owner-confirmed). The browser reports eight main trait–delta
correlations, an ancillary delta–RT correlation, direction-only sensitivities,
and 16 moderation fits with classical/HC3 uncertainty and presentation-order
sensitivities. All p values are unadjusted and intervals pointwise. The download
retains the 33 earlier associations, complete scoring audit, reliability
intervals, transition matrix and coverage table. The original registration wording
and pictogram anchor direction remain unverified; these are explicit limits.

The parameter repeated-measures section adds a complete 2×2 Condition × Phase
ANOVA for midpoint and normalized sharpness, plus separate continuous MAIA-2 and
spatial-change covariates. All 1,328 terms across both plateau models and four
linkage cohorts are exported in participant_repeated_measures.csv, with ordinary,
HC3 and hierarchical curve-refit uncertainty. The primary display excludes both
ambiguous records. These are exploratory models of fitted proxies; they cannot
remove the observed poor reliability or establish causal questionnaire influence.


## Clickable HTML charts

Current overview, pivot and exploratory charts are HTML/SVG elements drawn from
numerical data, with a shared exact-value box. Click/tap a point or use Tab,
arrows and Enter/Space; Esc or Close dismisses it. The box preserves participant
identity/context, units and full numeric precision. Previous/Next exposes covered
observations. This is also the rule for future current-page plots. Older workbook
and archived report figures are outside this retrofit; SVG/PNG/PDF remain static
download alternatives.

Segment 2's main visual is six raw Inhale−Exhale rainclouds. Densities use the fixed
descriptive Gaussian bandwidth, observed-range trim and equal peak height; boxes
show median/quartiles/1.5-IQR whiskers, all 240 participant dots are retained, and
mean/pointwise 95% t CIs remain separate. Corrected overall inference is preserved
and its graph is available in a disclosure. The browser renders charts from
verified `publication-data.json`; it does not refit inferential models.
The current exploratory heatmap reuses the pivot controls, worker and complete
scrollable table; the older notebook remains under `/exploratory/app/`.
