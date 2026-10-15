# Overleaf preprint

Upload this folder's contents as one Overleaf project and set `main.tex` as the main document. Compile with pdfLaTeX and BibTeX. All active sections, references, and referenced images are local to this folder.

The active draft reports the released 42-person analysis executed in the marimo
browser companion. Its abstract, Results, and two result figures derive from the
verified download in `../results/browser-analysis/`. Regenerate them with
`python analysis/prepare_publication.py path/to/browser-results.zip` from the
repository root. That command consumes browser results; it does not rerun models.

Author review remains necessary before submission, including collection/stopping
history, registration departures, ethics-statement details, and source-provenance
limits. The older 40-person text and figures are preserved in
`../for-ai/writing-archive/40-person-pre-browser/` and are outside the Overleaf build.
