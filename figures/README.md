# Reproducible result figures

The four SVGs come directly from the archived browser run in
`../results/browser-analysis/browser-results.zip`. They show equal-participant
means with pointwise 95% t intervals. Same-label AT-minus-Baseline curves are
descriptive and do not establish matched cue times. Lines connect means; no
sigmoid boundary inference is implied by those two mean plots.

`descriptive_sigmoids.svg` shows the four selected logistic approximations, raw
and extracted points, and conditional participant-bootstrap bands.
`sigmoid_extrapolation.svg` marks predictions outside the measured distance range
with dashed lines. Full plateaus are model assumptions; these plots do not
establish participant PPS boundaries.

`../analysis/prepare_publication.py` promotes the SVGs and renders the same report
values into the PNGs used by the Overleaf draft. Earlier 40-person figures are
preserved with the historical writing archive.
