# Observable Plot

Sources: [repository](https://github.com/observablehq/plot),
[marks](https://observablehq.github.io/plot/features/marks),
[plot and styling options](https://observablehq.github.io/plot/features/plots),
[examples](https://observablehq.com/@observablehq/plot-gallery).
Snapshot: package 0.6.17, commit
[`535723d`](https://github.com/observablehq/plot/blob/535723d5e433727720d9b673c31622821bb03210/src/index.js).
All exact exports, including classes and helpers, are in
[catalog.json](catalog.json), `toolkits.observable-plot`.

## Approach

Compose data-bound marks and scales with `Plot.plot`; add facets and transforms
as needed. The output is SVG, optionally inside an HTML figure with captions or
legends. CSS/style options control appearance, not the scientific definition of
an estimate. The project analysis owner supplies approved summaries and intervals.

## Decision tree

```text
Tabular data and a 2D comparison?
  Distribution -> dots/ticks; bin + rect for histogram; box for quartiles.
    Smooth distribution requested? -> approved/precomputed KDE + area/line.
  Repeated people -> line grouped by participant + dots; facet to reduce overlap.
  Continuous relationship -> dot; overlap -> density, hexbin or binned cells.
  Ordered change -> line + dot; approved interval -> area/rule behind them.
  Estimate/contrast -> dot + rule endpoints; reference rule at actual zero.
  Matrix -> cell/rect; many comparable groups -> fx/fy facets.
  Geography -> geo; field -> contour/raster/vector.
  Tree -> tree/cluster; arbitrary force graph -> inspect D3 instead.
Need specialized 3D or linked selection grammar? -> Plotly or Vega-Lite profile.
Need unusual geometry? -> custom mark only if simpler than the existing D3 owner.
```

## Complete mark-family inventory at the pin

Variants such as X/Y are orientations, not separate statistical methods.

| Family | Public drawing/interaction functions | Typical use |
| --- | --- | --- |
| Area | `area`, `areaX`, `areaY` | Filled ranges, approved uncertainty ribbons, stacked area |
| Arrow | `arrow` | Directed paired displacement |
| Auto | `auto`, `autoSpec` | Exploratory suggested encodings; review the specification |
| Axis/grid | `axisX`, `axisY`, `axisFx`, `axisFy`, `gridX`, `gridY`, `gridFx`, `gridFy` | Coordinate and facet guides |
| Bar | `barX`, `barY` | Category totals or precomputed summaries |
| Bollinger | `bollinger`, `bollingerX`, `bollingerY` | Rolling summary/envelope; not a default inferential CI |
| Box | `boxX`, `boxY` | Quartiles and outliers; identify observation unit |
| Cell | `cell`, `cellX`, `cellY` | Matrix/heatmap cells |
| Contour | `contour` | Scalar-field contours |
| Crosshair | `crosshair`, `crosshairX`, `crosshairY` | Interactive coordinate reading |
| Delaunay/Voronoi | `delaunayLink`, `delaunayMesh`, `hull`, `voronoi`, `voronoiMesh` | Spatial adjacency and regions |
| Density | `density` | Smoothed two-dimensional density |
| Difference | `differenceX`, `differenceY` | Highlight signed differences between series |
| Dot | `dot`, `dotX`, `dotY`, `circle`, `hexagon` | Scatter, strip, bubble and participant points |
| Frame | `frame` | Plot boundary |
| Geography | `geo`, `sphere`, `graticule` | Geographic geometries and guides |
| Hexgrid | `hexgrid` | Hexagonal grid guide |
| Image | `image` | Image marks; not a substitute for a live data plot |
| Line | `line`, `lineX`, `lineY` | Ordered profiles, ECDF or approved fitted curves |
| Linear regression | `linearRegressionX`, `linearRegressionY` | Built-in fit; requires an authorized matching model |
| Link | `link` | Supplied links/segments |
| Raster | `raster` | Scalar/color fields; raster content is not fully vector |
| Rect | `rect`, `rectX`, `rectY` | Bins, intervals, rectangles |
| Rule | `ruleX`, `ruleY` | References, intervals and whiskers |
| Text | `text`, `textX`, `textY` | Labels and annotations |
| Tick | `tickX`, `tickY` | Rug/strip distributions |
| Tip | `tip` | Tooltips |
| Tree | `tree`, `cluster` | Hierarchies |
| Vector | `vector`, `vectorX`, `vectorY`, `spike` | Direction and magnitude |
| Waffle | `waffleX`, `waffleY` | Unit-based composition/counts |

The raster export group additionally exposes `interpolateNone`,
`interpolatorBarycentric`, `interpolateNearest`, `interpolatorRandomWalk`.
Class exports and these helpers are retained in the machine inventory but are
not additional plot families.

Transform groups: basic filter/reverse/sort/shuffle/transform/initializer;
bin/binX/binY; centroid/geoCentroid; dodgeX/dodgeY;
find/group/groupX/groupY/groupZ; hexbin; normalize/normalizeX/normalizeY;
map/mapX/mapY; shiftX/shiftY; window/windowX/windowY;
select/selectFirst/selectLast/selectMaxX/selectMaxY/selectMinX/selectMinY;
stackX/stackX1/stackX2/stackY/stackY1/stackY2; treeNode/treeLink.
Pointer interactions: pointer/pointerX/pointerY.

Rainclouds, violins, forest plots, ECDFs, residual plots and paired-estimation
plots are compositions or prepared data, not dedicated Plot chart constructors.
Do not mistake `density` (2D) for a built-in one-dimensional violin.

## Integration checks

Use approved data rather than library-computed CIs for repeated participants.
Preserve line group IDs, order and missing gaps. Check margins explicitly: Plot
does not automatically make space for every long tick label. Inspect the actual
SVG separately from any HTML legend/caption when exporting a standalone figure.
Validate raster/image layers before claiming a fully vector export. Return to
the [shared selection and verification rules](README.md).
