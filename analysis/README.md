# Publication analysis

The executable analysis owner is the [marimo browser workbook](../workbook/README.md),
with its fixed [analysis contract](../workbook/ANALYSIS_PLAN.md). All data-supported
statistics run in the browser; native checks validate the engine independently.
Historical source-dependent work remains in `../for-ai/orchestration/`.

`prepare_publication.py` accepts a complete browser result ZIP, verifies its
input/output/code hashes and browser runtime, then copies report/tables to
`../results/browser-analysis/`, SVGs to `../figures/`, and renders the report's
figure data to the Overleaf PNGs. It generates the abstract and Results from that
exact report; it does not recompute models. After compiling and visually checking
the manuscript, `--preprint-pdf` archives the draft and source hashes for Pages.
See the workbook guide for commands.

The post hoc four-sigmoid extension is documented in
`../workbook/SIGMOID_EXPLORATION.md`; `sigmoid_literature_sources.json` records the
accessed implementation/documentation sources and their hashes. Scientific
sources support the methods, not a claim that the study establishes physiological
sigmoid boundaries.
