# Browser publication companion

The marimo application executes the released Study 5 analysis entirely in the
reader's browser using Pyodide. The published default loads the deidentified
42-person, 17,114-trial dataset. Select **Run complete paper analysis** to compute
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
analyses. The
[contract](ANALYSIS_PLAN.md) distinguishes primary questions, sensitivities,
supplementary analyses and registration ambiguities. It documents fixed nonlinear
bounds and the unavailable private metadata.

Native reference validation uses statsmodels independently of the browser engine.
The archived report and [results](../results/README.md) record both execution surfaces.
No participant boundary or related questionnaire inference is produced when the
trial-level sigmoid gate fails. Same-label Baseline subtraction is descriptive.

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

## Publish on GitHub Pages

The source repository stays private. Its GitHub plan must support Pages for private
repositories; the Pages artifact is intended to be public. Dataset publication is
explicitly authorised in [DATA_RELEASE.md](DATA_RELEASE.md).

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
