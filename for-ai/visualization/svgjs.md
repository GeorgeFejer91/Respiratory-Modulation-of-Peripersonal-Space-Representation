# SVG.js

Sources: [repository](https://github.com/svgdotjs/svg.js),
[element API](https://svgjs.dev/docs/3.2/shape-elements/),
[documentation](https://svgjs.dev/docs/3.2/),
[optional dragging plugin](https://svgjs.dev/docs/3.2/plugins/svg-draggable-js/).
Snapshot: package 3.2.8, commit
[`4b8809b`](https://github.com/svgdotjs/svg.js/blob/4b8809b1554c44a84f8992cdbda60480336cc040/src/main.js).
All 30 element exports/source paths are in
[catalog.json](catalog.json), `toolkits.svgjs`.

## Approach and decision tree

Create and manipulate SVG elements through a JavaScript API, including geometry,
groups, transforms, text, styles, events and animations. A method named `plot`
updates shape geometry; it is not a statistical chart constructor.

```text
Need a coordinate-defined apparatus, timeline illustration or custom schematic?
  Existing inline SVG is simple enough -> use the existing owner directly.
  Need repeated shape construction/animation -> consider SVG.js.
    Boxes/landmarks -> Rect/Circle/Ellipse.
    Segments/arrows -> Line/Polyline/Path + Marker.
    Closed regions -> Polygon/Path; label with Text/Tspan/TextPath.
    Repeated components -> G/Symbol/Use with transforms.
    Cropping/visual layers -> ClipPath/Mask; fill -> Gradient/Pattern.
Need data scales, axes, bins or statistical summaries?
  Use the existing chart owner, Plot/Vega-Lite/D3/Plotly; SVG.js supplies none.
Need constraint-optimized semantic layout? -> Penrose.
Need drag behavior? -> optional plugin, separately reviewed; not core capability.
```

## Complete element inventory at the pin

| Responsibility | All exported element classes |
| --- | --- |
| Geometry | `Circle`, `Ellipse`, `Line`, `Path`, `Polygon`, `Polyline`, `Rect` |
| Text | `Text`, `TextPath`, `Tspan` |
| Containers/reuse | `A`, `Container`, `Defs`, `ForeignObject`, `Fragment`, `G`, `Svg`, `Symbol`, `Use` |
| Appearance/layers | `ClipPath`, `Gradient`, `Image`, `Marker`, `Mask`, `Pattern`, `Stop`, `Style` |
| Base classes | `Dom`, `Element`, `Shape` |

These 30 classes are a finite element inventory, not 30 plot types. Arbitrary
custom diagrams can be assembled, but no histogram, violin, forest, axis,
regression, scale, confidence interval or network-layout engine is supplied by
this element list. Events/animation, transforms and numeric/color/path helper
types are other APIs rather than additional chart families.

## Integration checks

Keep coordinate systems and `viewBox` consistent and use physical units only
when calibrated. Preserve readable labels, meaningful title/description, grouping,
keyboard alternatives and reduced-motion behavior for animated content. Scope
CSS and element IDs to avoid collisions. `ForeignObject` embeds HTML and `Image`
can embed raster content; inspect standalone export/font compatibility rather
than assuming every SVG is portable or wholly vector. Custom data charts still
need approved preparation, scales and all [shared checks](README.md).
