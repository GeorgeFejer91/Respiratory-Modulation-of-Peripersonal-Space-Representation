#import "style.typ": manuscript
#show: manuscript

#align(center)[
  #set par(justify: false, first-line-indent: 0pt)
  #set footnote(numbering: "*")
  #text(size: 17pt, weight: "bold")[Respiratory Modulation of Peripersonal Space Representation]

  #v(0.8em)
  *George Fejer*#super[1,2,3]#footnote[Correspondence: george.fejer\@aliusresearch.org], *Till Holzapfel*#super[4],
  *Michael Gaebler*#super[2], *Bigna Lenggenhager*#super[7,8]

  #v(0.4em)
  #text(size: 10pt)[
    #super[1] University of Konstanz, Konstanz, Germany\
    #super[2] Max Planck Institute for Human Cognitive and Brain Sciences, Germany\
    #super[3] ALIUS Research Network, Germany\
    #super[4] Sensory Citizens, Germany\
    #super[7] Association for Independent Research, Zurich, Switzerland\
    #super[8] University Hospital of Psychiatry, Zurich, Switzerland
  ]

  #v(0.6em)
  October 16, 2026
]

#v(1em)
#align(center)[*Abstract*]
#block(inset: (x: 0.25in))[
  #set text(size: 11pt)
  #set par(first-line-indent: 0pt)
  #include "sections/abstract.typ"
]

#block[
  #set par(first-line-indent: 0pt)
  *Keywords:* peripersonal space, respiration, virtual reality, interoception, embodied cognition
]

#block[
  #set par(first-line-indent: 0pt)
  *Analysis draft for author review.* Results from 42 participant
  records are reproduced by the browser companion. Two records share an identical
  behavioural recording with reversed intervention labels; source mapping must be
  resolved before behavioural inference can be finalized. Collection-history and
  ethics-statement details also require author review before submission.
]

#set par.line(numbering: n => text(fill: gray, size: 6pt, font: "New Computer Modern")[#n], number-clearance: 9pt)
#include "sections/introduction.typ"
#include "sections/methods.typ"
#include "sections/results.typ"
#include "sections/discussion.typ"

#set par.line(numbering: none)
#include "sections/acknowledgements.typ"

#bibliography("references.bib", style: "apa", title: [References])
