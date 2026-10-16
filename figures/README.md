# Reproducible result figures

The eight SVGs come directly from the archived browser run in
`../results/browser-analysis/browser-results.zip`. The two mean plots show
equal-participant means with pointwise 95% t intervals. Same-label AT-minus-Baseline curves are
descriptive and do not establish matched cue times. Lines connect means; no
sigmoid boundary inference is implied by those two mean plots.

`descriptive_sigmoids.svg` shows the four selected logistic approximations, raw
and extracted points, and conditional participant-bootstrap bands.
`sigmoid_extrapolation.svg` marks predictions outside the measured distance range
with dashed lines. Full plateaus are model assumptions; these plots do not
establish participant PPS boundaries.

`pps_shape.svg` shows the four explicitly shape-constrained curves on common
linear axes with centered raw/extracted data, conditional bootstrap bands and
the tuned line. `sigmoid_geometry.svg` normalizes fitted amplitudes to display
model geometry only; no observations or uncertainty are represented on that
scale. The visible S shapes satisfy imposed criteria; active constraints and
weak predictive support prevent an empirical PPS-boundary claim. Both the full
figures and their manuscript placement were visually inspected.

`../analysis/prepare_publication.py` promotes the SVGs and renders the same report
values into the PNGs used by the Overleaf draft. Earlier 40-person figures are
preserved with the historical writing archive.

`questionnaire_summary.svg` shows individual/mean MAIA-2 scores with participant-
bootstrap intervals and the complete paired spatial transition matrix.
`questionnaire_associations.svg` shows all 32 MAIA-to-outcome rank coefficients;
the 33rd spatial-change/behaviour coefficient is printed below. Corrected p values
and pointwise intervals are in the download. Neither plot converts recorded
spatial codes to an unverified psychological anchor direction.

`participant_example.svg` pairs the first public record's raw RT means/SE with
normalized fitted geometry. `participant_diagnostics.svg` shows predictive error,
parameter uncertainty, reliability and association sensitivity. All 42 records are
in `results/browser-analysis/participant_curve_atlas.pdf`; no record was selected
for having an attractive shape. Normalized 0/1 plateaus are imposed, and the atlas
flags unresolved P011/P033 linkage.
