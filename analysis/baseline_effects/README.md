# Native baseline-corrected results

This is the results-only native extension. Read
[`RESULTS.md`](../../results/baseline_effects/RESULTS.md) and the complete
[`analysis_registry.json`](../../results/baseline_effects/analysis_registry.json).
The existing browser engine and manuscript snapshot are separate, unchanged
analyses. These new results have not been executed in Pyodide or added to Pages.

Use Python 3.12 and the pinned `requirements.txt` in an isolated environment.
Commands below run from the repository root. Set `OPENBLAS_NUM_THREADS=1` and
`OMP_NUM_THREADS=1` for the inference runs; four sampler chains are used. Outputs
go to `results/baseline_effects/`; large local posterior traces go to ignored
`.for-ai-local/baseline_effects/` and need several GB of disk space.

```bash
python analysis/baseline_effects/baseline_effects.py registry
python analysis/baseline_effects/baseline_effects.py frequentist
python analysis/baseline_effects/baseline_effects.py bootstrap
python analysis/baseline_effects/check_baseline_fits.py refinement
python analysis/baseline_effects/check_baseline_fits.py recovery
python analysis/baseline_effects/check_baseline_fits.py nominal
python -m unittest discover -s analysis/baseline_effects -p 'test_*.py' -v
```

The seven initial joint models are `joint_logistic`, `joint_logistic_wide`,
`joint_logistic_student`, `joint_logistic_same_label`, `joint_constant`,
`joint_linear` and `joint_log_distance`. Their final sampling settings are in
each `*_specification.json`. The diagnostic extensions use:

```bash
python analysis/baseline_effects/joint_pps.py joint_logistic --draws 12000 --tune 6000 --target-accept .99
```

Substitute the other model names to reproduce their extensions. Numerical
failures remain results; a sampler return value does not establish convergence.
The additional, explicitly post hoc independent-nuisance sensitivity uses exact
Gaussian marginalization with the same paired shape hierarchy:

```bash
python analysis/baseline_effects/joint_pps.py joint_logistic_marginal --draws 3000 --tune 3000 --target-accept .99
python analysis/baseline_effects/joint_pps.py joint_logistic_heterogeneous --draws 3000 --tune 3000 --target-accept .99
python analysis/baseline_effects/joint_pps_checks.py cv
python analysis/baseline_effects/joint_pps_checks.py recovery
python analysis/baseline_effects/joint_pps_checks.py predictive
python analysis/baseline_effects/plot_baseline_results.py
python analysis/baseline_effects/report_baseline_results.py
```

Cross-validation resumes completed folds from its two output CSVs. For a fresh
rerun, move `joint_held_distance_predictions.csv` and
`joint_held_distance_diagnostics.csv` elsewhere first. The summary builder needs
all twelve model runs, the prediction checks and the figures. It records exact
source, data and output hashes and creates `native_results.zip`.

The three further post hoc response checks are `joint_constant_student`,
`joint_linear_student` and `joint_log_distance_student`, using the default
sampling settings unless their diagnostic files record an extension. They check
the RT-level interaction suggested by the Student-t sigmoid without relying on
uncertain shape parameters. All fixed population coefficients and finite-cohort
response contrasts are retained.

The main correction is AT minus the pooled Baseline mean within participant ×
Condition × Phase. Same-nominal-SOA subtraction is a timing-unverified
sensitivity. The primary 40-person cohort excludes both P011 and P033 because
their recordings are identical with condition labels reversed. Frequentist
cohort sensitivities do not resolve that source mapping.

All p values are unadjusted. Grid/continuous point estimates, two-level refit
stability intervals, full joint posterior contrasts and conventional ANOVAs on
pooled posterior medians answer different questions. In particular, the latter
omit shared fitting uncertainty and are not valid independent confirmation of a
hierarchical model effect. The deliberately null simulation demonstrates this.
