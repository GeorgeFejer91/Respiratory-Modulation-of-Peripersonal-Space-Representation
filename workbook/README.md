# Live data preparation workbook

This marimo workbook provides a reactive view of Study 5 data preparation:
input checks, trial and condition choices, recorded RT-window flags, sequential
row counts, an RT histogram, candidate rows, and a downloadable CSV with a JSON
preparation manifest. The manifest records settings and source/output hashes.
Inputs are kept intact and missing values are not imputed. All preparation
choices remain exploratory; no statistical model or final analysis is promoted.

## Work in the browser

The GitHub Pages build publishes two views:

- `/Study5_Publication/`: interactive application with preparation controls.
- `/Study5_Publication/editor/`: editable Python workbook running in the browser.

The public default is generated synthetic data: eight invented participants and
480 invented trials. Use **Upload CSV pair** to select the documented participant
and trial CSVs. Both files are required, schema/order must match `data/raw/README.md`,
and partial uploads never fall back to synthetic inputs. The published workbook
uses Pyodide: CSV contents are processed in browser memory, with no data-processing
backend. Runtime and package files download from marimo/Pyodide hosts. A modern
browser and an internet connection are required for the first load.

Refresh clears the current inputs and choices. Use **Download prepared data +
manifest** to save your result. Edits made in the online Python editor can be
downloaded; they do not automatically commit to GitHub or update the published
workbook. Use the navigation link in the workbook to switch between its application
and editor views.

The published site is a public tool, not a publication of participant observations.
The build exports only workbook source and its local helper module. It never reads
or copies `data/raw/`, and it does not embed execution snapshots. Publishing the
real data or refreshing the manuscript's older 40-person results remains a
separate scientific/release task.

## Run and develop locally

From the repository root, with Python 3.12 or later:

```bash
python3 -m venv .for-ai-local/workbook-venv
.for-ai-local/workbook-venv/bin/python -m pip install -r workbook/requirements.txt uv
.for-ai-local/workbook-venv/bin/marimo edit workbook/data_preparation.py
```

Use `marimo run workbook/data_preparation.py` for the application view. Python
executes on your local machine in these modes. When using the prepared Codex cloud
environment, first `source /workspace/.study5-environment/env.sh`; this provides
writable configuration/cache locations. Do not expose the local editor as a public
server; the Pages deployment uses the browser runtime.

## Verify and build

```bash
python3 -m unittest discover -s workbook -p 'test_*.py' -v
python3 for-ai/orchestration/public_data.py check data/raw
.for-ai-local/workbook-venv/bin/marimo check workbook/data_preparation.py --strict
.for-ai-local/workbook-venv/bin/marimo check workbook/data_preparation.py --select MW --strict
.for-ai-local/workbook-venv/bin/python workbook/build_site.py
python3 -m http.server --directory .for-ai-local/site
```

The exporter needs `uv` to package the local `preparation.py` helper. The build
produces `.for-ai-local/site/index.html`, an editable `editor/` view, their assets,
and `.nojekyll`. Serve that directory over HTTP; opening `index.html` as a local
file does not load its relative assets reliably. Generated files, runtime caches,
and downloads should remain ignored.

`preparation.py` owns the shared schemas and publication key/source-code checks.
The existing `public_data.py` CLI imports those checks, preserving its commands.
The workbook additionally validates Boolean fields and numeric RTs before filtering.

## Publish with GitHub Pages

`.github/workflows/workbook-pages.yml` tests and rebuilds the site whenever workbook
changes reach `main`; it also supports **Actions → Publish browser workbook → Run
workflow**. It uploads only `.for-ai-local/site` and deploys through GitHub Pages.
The workflow uses the repository's GitHub Actions publishing source without
changing repository visibility.

Enable **Repository Settings → Pages → Build and deployment → Source: GitHub
Actions** before the first deployment, then run the workflow. A private
repository needs a GitHub plan that supports Pages for private repositories; the
published site can still be public. Preserve this repository's private visibility.
Confirm the deployment URL and a successful action before reporting the site live.

Only the generated tool artifact is public. Do not add participant CSVs, private
exports, or notebook execution caches to the artifact.
