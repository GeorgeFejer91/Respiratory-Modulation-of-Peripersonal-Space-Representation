# Penrose

Sources: [repository](https://github.com/penrose/penrose),
[gallery](https://penrose.cs.cmu.edu/examples),
[editor, languages and exports](https://penrose.cs.cmu.edu/docs/ref/using).
Snapshot:
[`164ad55`](https://github.com/penrose/penrose/tree/164ad55777e9975baa0e0860a5d18051f66beafa/packages/examples/src).
All 194 trio paths, 46 example folders and 53 featured IDs are in
[catalog.json](catalog.json), `toolkits.penrose`.

## Approach and decision tree

Domain defines types/relations; Substance describes the concrete objects and
relationships; Style assigns geometry and constraints/objectives. A trio ties
these sources together. Optimization finds a diagram layout. This is useful for
semantic scientific schematics, not automatically a valid statistical plot.

```text
Is the figure mainly data mapped to measured axes?
  Yes -> Plot/Vega-Lite/D3/Plotly; keep inference in the analysis owner.
  No -> are semantic relationships the important source of layout?
    No, exact apparatus coordinates matter -> inline SVG or SVG.js.
    Yes -> choose a nearby Penrose example/domain:
      Sets/logic -> set theory/Euler and constraint examples.
      Geometry/algebra -> geometry, linear algebra, matrices, groups.
      Networks/topology -> graph, hypergraph, spectral, persistent homology.
      Physics/chemistry/computation -> fields, molecules, circuits, arrays.
      No matching domain -> model the vocabulary and constraints explicitly.
Need live dragging? -> experimental Penrose interactions need separate validation.
Need an export? -> SVG/PDF; inspect equations, embedded images and layout quality.
```

## Complete top-level example-folder inventory

These are example families, not 46 built-in chart constructors or a guarantee
that every domain compiles with a different release. Some are tests or tutorials.

| Area | All exact folder IDs |
| --- | --- |
| Sets and abstract relationships | `set-theory-domain`, `set-potatoes`, `alloy-models`, `box-arrow-diagram` |
| Algebra and matrices | `exterior-algebra`, `fake-3d-linear-algebra`, `group-theory`, `lagrange-bases`, `linear-algebra-domain`, `matrix-library`, `matrix-ops` |
| Graphs/topology | `graph-domain`, `hypergraph`, `spectral-graphs`, `persistent-homology`, `mobius` |
| Geometry/meshes | `geometry-domain`, `curve-examples`, `envelopes`, `geometric-queries`, `impossible-ngon`, `minkowski-tests`, `shape-distance`, `shape-spec`, `triangle-mesh-2d`, `triangle-mesh-3d` |
| Dynamics/physics/probability | `Dynamics`, `stochastic-process`, `walk-on-spheres`, `ray-tracing`, `random-sampling` |
| Chemistry/circuits | `atoms-and-bonds`, `molecules`, `structural-formula`, `logic-circuit-domain` |
| Computation/data/text | `array-models`, `dataviz`, `timeline`, `tsne`, `word-cloud`, `fancy-text` |
| Other illustrations/learning | `animation`, `dinoshade`, `fractals`, `interactive`, `tutorials` |

For individual alternatives, search `trios` or `featured_gallery_ids` in the
catalogue and reconstruct an immutable link from `source_base + path`. The live
gallery is client-rendered; featured membership was extracted from
[`registry.json`](https://github.com/penrose/penrose/blob/164ad55777e9975baa0e0860a5d18051f66beafa/packages/examples/src/registry.json),
using `gallery: true` and a matching `.trio.json` file, not guessed from a blank
HTML response. Featured examples are a subset of all trio sources.

## Integration checks

Preserve source trio files and chosen layout variation with exported assets.
Check semantic relations, constraint satisfaction, arrow direction, label
overlap and any physical scale by inspection. Resampling changes layout, not
the underlying evidence. Mark schematic geometry as such. SVG for TeX has a
different equation workflow from ordinary SVG; inspect the intended consumer.
Do not replace live data-driven charts with exported diagram images. Follow
[shared selection and verification rules](README.md).
