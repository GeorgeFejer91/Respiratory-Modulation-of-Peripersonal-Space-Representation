# D3 Graph Gallery

Sources: [repository](https://github.com/holtzy/D3-graph-gallery),
[live gallery](https://d3-graph-gallery.com/),
[worked interactive SVG scatterplot](https://d3-graph-gallery.com/graph/scatter_grouped_highlight.html).
Snapshot:
[`8f12759`](https://github.com/holtzy/D3-graph-gallery/blob/8f12759d589c09248d841795293be9197308531b/index.html).
Every category/navigation page and all 165 example paths are in
[catalog.json](catalog.json), `toolkits.d3-gallery`.

## Approach and decision tree

This is a tutorial and example collection, using HTML containers, SVG, CSS and
JavaScript. It is not another plotting runtime or an approved statistics source.

```text
Need to learn or adapt an existing D3 recipe?
  Distribution -> violin/density/histogram/boxplot/ridgeline.
  Relationship -> scatter/bubble/connected scatter/heatmap/correlogram/density2d.
  Category/rank -> bar/lollipop; parallel for many measures.
  Ordered change -> line/area/stacked area/streamgraph.
  Hierarchy/composition -> treemap/dendrogram/packing/pie/donut.
  Spatial -> geographic map family matching the data.
  Relations/flows -> network/Sankey/chord/arc/bundling.
Then inspect the exact example:
  Does the D3 import match the project? -> adapt only the relevant code.
  External companion dependency? -> inspect/license/pin before adding.
  Statistical recipe differs from the project? -> retain approved preparation.
  No useful example? -> official D3/Plot/Vega-Lite documentation.
```

## All 37 chart-family landing pages

Page names below map directly to `https://d3-graph-gallery.com/<page>.html`.

| Family | All category pages |
| --- | --- |
| Distribution | `violin`, `density`, `histogram`, `boxplot`, `ridgeline` |
| Relationship | `scatter`, `heatmap`, `correlogram`, `bubble`, `connectedscatter`, `density2d` |
| Ranking/multivariate | `barplot`, `spider`, `wordcloud`, `parallel`, `lollipop`, `circular_barplot` |
| Hierarchy/composition | `treemap`, `donut`, `pie`, `dendrogram`, `circularpacking` |
| Ordered change | `line`, `area`, `stackedarea`, `streamgraph` |
| Geography | `backgroundmap`, `choropleth`, `hexbinmap`, `cartogram`, `connectionmap`, `bubblemap` |
| Connections/flows | `chord`, `network`, `sankey`, `arc`, `bundle` |

The other three local links are instructional pages: `intro_d3js`, `custom`,
`interactivity`. They are not chart types. The machine catalogue preserves
every `graph/*.html` filename so an agent can locate individual variants without
loading this entire repository. Reconstruct an immutable GitHub link using its
`source_base` and the example path.

## Scientific and compatibility limits

Some examples offer D3 v4 and v6 variants; read the actual script import rather
than assuming current D3 compatibility. Example smoothing, binning, jitter,
aggregation or bootstrap code is not automatically suitable for paired research
data. Radar charts can obscure scales; streamgraph offsets move the baseline;
word clouds are descriptive text displays. Assess suitability before copying a
recipe. Reuse the current application's sizing, accessibility and export owners,
then run [shared checks](README.md).
