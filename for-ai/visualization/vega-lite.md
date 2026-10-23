# Vega-Lite

Sources: [repository](https://github.com/vega/vega-lite),
[example gallery](https://vega.github.io/vega-lite/examples/),
[paper figures and SVG export](https://vega.github.io/vega-lite/tutorials/figures.html),
[Vega renderer API](https://vega.github.io/vega/docs/api/view/).
Snapshot: package 6.5.0, commit
[`85fab8d`](https://github.com/vega/vega-lite/blob/85fab8d12c873b3b224ef9a33c807642953325ba/site/_data/examples.json).
All marks, 203 featured entries and 816 example specification paths are in
[catalog.json](catalog.json), `toolkits.vega-lite`.

## Approach and decision tree

Describe data fields, variable types, encodings, marks and transformations in a
JSON specification. Compose views through layering, facets, repetition and
concatenation; parameters/selections coordinate interaction. Vega-Lite compiles
to Vega. Prefer specification/configuration styling over editing generated DOM.

```text
Need a portable declarative specification?
  One quantitative distribution -> binned bar/rect, tick/point or density area.
  Groups -> point layers and approved intervals; boxplot if its definition fits.
  Paired or ordered data -> line with participant detail + points.
  Estimates -> precomputed point + rule, or errorbar with explicit bounds.
  Approved curve and band -> line + area, or errorband with explicit bounds.
  Matrix -> rect; geographic geometry -> geoshape.
  Many comparisons -> facet/repeat/concat with declared scale resolution.
  Linked filtering/brush -> parameters/selections and coordinated views.
Need a violin/raincloud? -> density transform + mirrored area + points, or a
  precomputed density; this is a composition, not a native violin mark.
Need Sankey/force layout or unsupported geometry? -> inspect Vega or D3.
Need scientific 3D/volume? -> Plotly profile.
```

## Complete mark inventory at the pin

Primitive marks: **arc, area, bar, image, line, point, rect, rule, text, tick,
trail, circle, square, geoshape**. Composite marks: **boxplot, errorbar,
errorband**. Composites expand to layered primitives; inspect defaults before
using computed summaries. Counts are not counts of possible charts.

## Complete featured-gallery category coverage

All individual IDs and category assignments are in the JSON inventory; these
groups summarize the whole featured gallery without repeating 203 variants.

| Category | Chart options demonstrated |
| --- | --- |
| Bars | Simple, grouped, stacked/normalized, horizontal, negative, ranged/Gantt, diverging/population pyramid, layered, labeled and responsive bars |
| Distributions | Histogram/pre-binned histogram, density, 2D bins, cumulative/ECDF and layered distribution displays |
| Scatter/strip | Scatter, strip/jitter, bubble, image/text points and explicit missing-value encodings |
| Lines | Single/multiple series, point overlays, slope, step, monotone, connected scatter, rank/bump, variable-width trail, dashed/gapped lines |
| Areas | Area, gradient/overlaid/stacked/normalized area, streamgraph and horizon |
| Tables/matrices | Heatmap, table bubble, calendar matrix, dense time-series matrix, mosaic and wind vectors |
| Circular | Pie, donut, radial, ordinal-angle and pyramid variants |
| Calculations | Differences, residuals, waterfall, top-k, parallel coordinates, QQ, regression/LOESS, rolling aggregates and ternary composition |
| Composite marks | CI/SD error bars, interval bands and boxplots with differing whisker definitions/precomputed summaries |
| Layers | Text annotations, thresholds, mean overlays, Likert distributions, range dots, bullet/candlestick and dual-axis examples |
| Multiple views | Facets/trellis, repeat, concatenation, scatterplot matrices and marginal distributions |
| Maps | Geographic shapes, points, projections and layered maps |
| Interaction | Filtering, selections, brushing, pan/zoom, highlights, tooltips and linked multi-view displays |

An example may implement an option through multiple marks/transforms rather than
a named constructor. The exact featured IDs remain the authoritative finite
enumeration. The 203 gallery entries reference 189 unique specifications; another
627 specifications are unfeatured. Some are implementation variants or tests.

## Integration checks

Supply precomputed approved summaries/interval bounds for inferential figures.
Do not allow default aggregation, error bars, LOESS or imputation examples to
alter the analysis. Keep participant identity in line `detail` and preserve gaps.
State whether facet scales are shared; independent scales can defeat comparison.
Use the embed/view renderer option for SVG when required (Vega defaults to
canvas); HTML legends/tooltips and externally referenced image marks need export
inspection. Validate linked selections against table/download values and provide
keyboard/touch alternatives. Return to [shared rules](README.md).
