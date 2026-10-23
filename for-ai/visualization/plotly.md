# Plotly.js

Sources: [repository](https://github.com/plotly/plotly.js),
[JavaScript examples](https://plotly.com/javascript/),
[figure reference](https://plotly.com/javascript/reference/),
[SVG/WebGL differences](https://plotly.com/javascript/webgl-vs-svg/),
[static export](https://plotly.com/javascript/static-image-export/).
Snapshot: package 4.1.2, commit
[`96c9eb3`](https://github.com/plotly/plotly.js/tree/96c9eb33d55f4b3ef7ec177adfcc2f542904bfb2/src/traces).
All 47 trace IDs, source paths and source-declared categories are in
[catalog.json](catalog.json), `toolkits.plotly`.

## Approach and decision tree

Build `data` as a list of traces, with `layout` and interaction configuration.
Modes, subplots, error bars, fill, shapes and annotations extend traces; they
are not additional trace types. Use the figure API to style scientific content;
CSS controls the surrounding HTML. Assess the bundle before adding this to the
lightweight pivot startup path.

```text
Need a ready-made specialized scientific trace?
  2D observations/paired profiles -> scatter markers/lines, split by person.
  Distributions -> histogram/box/violin; 2D density -> histogram2d[contour].
  Matrix or field -> heatmap/contour; vector arrows -> quiver at this pin.
  Estimate/forest -> scatter + explicit error_x/error_y arrays.
  Approved curve/band -> scatter lines + filled bounds; no implicit refit.
  Polar/ternary/Smith/carpet coordinates -> matching trace family below.
  Surface/3D/vector volume -> matching WebGL trace; provide a 2D alternative.
  Geographic -> projected geo or tiled map family; audit network/tile needs.
Need fully vector export?
  SVG trace -> inspect actual exported SVG and all overlays.
  WebGL/tiled/image trace -> raster/mixed export; select a suitable SVG alternative
    when the scientific question allows it. Renaming the file is not conversion.
Need arbitrary geometric layout? -> D3/SVG.js/Penrose as appropriate.
```

## Complete trace inventory at the pin

| Trace family | All exact IDs | Data and plot options |
| --- | --- | --- |
| Cartesian observations | `scatter`, `scattergl` | Markers, lines/steps, fills, errors, paired profiles; `scattergl` uses WebGL |
| Category/change | `bar`, `waterfall`, `funnel`, `funnelarea` | Counts, signed increments and stages; distinguish common denominators |
| Distributions | `box`, `violin`, `histogram` | Quartiles, densities and binned counts |
| Matrices/density | `heatmap`, `contour`, `histogram2d`, `histogram2dcontour` | Scalar matrices and two-dimensional distributions |
| Cartesian vector field | `quiver` | Positions x/y and components u/v; verify availability against the selected runtime version |
| Composition/hierarchy | `pie`, `sunburst`, `treemap`, `icicle` | Common wholes and nested categories |
| Relationships/multivariate | `sankey`, `parcoords`, `parcats`, `splom` | Flows, parallel numeric/category axes and scatterplot matrices |
| Polar | `scatterpolar`, `scatterpolargl`, `barpolar` | Cyclic/directional variables; GL variant has raster export limits |
| Ternary/Smith | `scatterternary`, `scattersmith` | Compositions summing to a whole; complex impedance coordinates |
| Curvilinear carpet | `carpet`, `scattercarpet`, `contourcarpet` | Parameterized coordinate grids and associated values |
| Projected geography | `scattergeo`, `choropleth` | Geographic points/lines and region encodings |
| Tiled maps | `scattermap`, `choroplethmap`, `densitymap` | MapLibre-backed map layers; inspect external style/tile dependencies |
| 3D positions/surfaces | `scatter3d`, `surface`, `mesh3d` | Point/line geometry, regular surface grids and arbitrary meshes |
| 3D scalar/vector fields | `isosurface`, `volume`, `cone`, `streamtube` | Scalar volumes and vector-field geometry |
| Finance | `ohlc`, `candlestick` | Open/high/low/close data; no general need in this study |
| Other displays | `image`, `indicator`, `table` | Raster/image data, scalar gauges and tabular displays; no analysis inference |

The table contains exactly 47 IDs. Older examples can mention removed or legacy
trace names; choose against the pinned inventory and the actual installed
version, not memory. Core `scatter` is included even though the full bundle
registers it through its core module. Partial bundles may not include every ID.

## Compositions and limits

Forest/coefficient, raincloud, ECDF, Kaplan-Meier, residual and paired-estimation
figures need prepared data and/or combinations of traces; their names do not
establish a dedicated constructor or statistical estimator. Error arrays accept
approved asymmetric bounds; do not substitute SD for CI. The source categories
in the catalogue help identify rendering, but are not an export guarantee.

WebGL-rendered content becomes embedded raster data in SVG/PDF exports. Image
and tiled-map content also require inspection before claiming pure vector output.
Check limits on WebGL contexts if many plots share a page. MathJax is optional
and separately loaded; add it only for a concrete label requirement. Keep full
data access and verify browser/export results under [shared rules](README.md).
