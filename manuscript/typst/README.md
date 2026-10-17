# Study 5 Typst snapshot

Open `main.typ` in UnderTree and recompile. The project uses Typst 0.15.1,
a local style, six editable section files, the 13 referenced figures,
and a cited-only bibliography. No packages or network access are required:

```sh
typst compile main.typ Study5.pdf
```

This is a format conversion of the active `../main.tex`, `../sections/`,
`../references.bib`, and referenced `../figures/` assets. The LaTeX source remains
the canonical publication draft and the analysis promotion pipeline continues to
update it. After a scientific source update, refresh this derived snapshot before
using its PDF. The Typst conversion does not rerun or revise any analysis. The snapshot includes
the condition-matched spatial–PPS amendment from analysis version 1.9, including
its two tables, figure, methods and uncertainty qualifications.

The 42-record author-review warning, unresolved recording linkage, exploratory
qualifications, full Discussion, tables, captions, citation keys and statistics
are retained. The title date records the conversion date, 2026-10-16.

Native counters preserve figure/table/section references. Two uncaptioned tables
remain unnumbered. Statistical-expression commas are preserved explicitly to
avoid Pandoc 3.6.4 converting them to spacing. Bibliography aliases are materialized
as their cited keys, with bibliographic fields otherwise unchanged. Distinct
source records for the same Barsalou paper remain distinct.

Typography, pagination, float placement, and APA citation/reference formatting
differ from the LaTeX build. Typst's built-in APA formatter can add a date comma
to year-only miscellaneous references; bibliography verification and author
submission review remain separate from this conversion.

The compiled PDF and machine-specific conversion/QA evidence are local outputs,
excluded from Git. Original sources are preserved. No author-review or submission
readiness is implied by a successful compile.
