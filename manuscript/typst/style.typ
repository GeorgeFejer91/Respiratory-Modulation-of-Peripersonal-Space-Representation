// Local manuscript formatting; no package downloads or external dependencies.
#let manuscript(body) = {
  set document(
    title: "Respiratory Modulation of Peripersonal Space Representation",
    author: ("George Fejer", "Till Holzapfel", "Michael Gaebler", "Bigna Lenggenhager"),
  )
  set page(paper: "us-letter", margin: 1in, numbering: "1")
  set text(font: "New Computer Modern", size: 12pt, lang: "en", hyphenate: false)
  set par(justify: true, leading: 0.75em, spacing: 0.35em, first-line-indent: 1.2em)
  set heading(numbering: "1.1", supplement: [Section])
  show heading.where(level: 1): set text(size: 14pt)
  show heading.where(level: 2): set text(size: 12pt)
  show heading: set par.line(numbering: none)
  set figure(gap: 6pt)
  show figure.where(kind: image): set figure(supplement: [Fig.])
  show figure.where(kind: table): set text(size: 9pt)
  show figure.where(kind: table): set par(leading: 1.5pt, first-line-indent: 0pt)
  set table(stroke: none, inset: (x: 4pt, y: 3pt))
  show figure: set par.line(numbering: none)
  show figure.caption: set text(size: 8pt)
  show figure.caption: set par(justify: false, leading: 1.5pt, first-line-indent: 0pt)
  show figure.caption: it => align(left)[
    #strong[#it.supplement #context it.counter.display(it.numbering)] #it.body
  ]
  body
}
