# /// script
# requires-python = ">=3.12"
# dependencies = ["marimo==0.25.1", "numpy==2.4.3", "scipy==1.17.1", "matplotlib==3.10.8"]
# ///

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full", app_title="Study 5 · Publication companion")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    from collections import Counter
    from html import escape
    import sys
    from preparation import demo_pair, local_release_pair, load_pair, prepare, make_bundle, WINDOWS, FILES
    return Counter, FILES, WINDOWS, demo_pair, escape, load_pair, local_release_pair, make_bundle, prepare, sys


@app.cell
def _(mo):
    _editor_view = str(mo.notebook_location()).rstrip("/").endswith("/editor")
    _navigation = "[Return to the application](../)" if _editor_view else "[Open the editable workbook](./editor/)"
    mo.md(f"""
    # Study 5 · Publication companion

    **Respiratory Modulation of Peripersonal Space Representation**

    Reproduce the paper's behavioral analysis from the released deidentified
    data. Follow preparation, run every data-supported model and sensitivity,
    inspect fit diagnostics, and download the complete analysis record.

    **Live browser computation** · Python runs in your browser on the published
    page. Uploaded CSV contents are processed in browser memory and are not
    sent to a processing server. Refreshing the page clears this session.
    Download your analysis record before leaving. The paper-analysis pipeline
    uses the fixed cleaning/model contract; exploratory preview controls do not
    change its primary result.

    {_navigation} to work with the Python steps online.
    Changes in the browser can be downloaded; publishing a revised page requires
    committing the workbook source to GitHub.

    [Working preprint · author-review draft](./paper.pdf) ·
    [Individual curve atlas · exploratory](./individual-curves.pdf) ·
    [Analysis contract](./ANALYSIS_PLAN.md) · [Data release record](./DATA_RELEASE.md) ·
    [Descriptive sigmoid methods and sources](./SIGMOID_EXPLORATION.md) ·
    [Miniature literature review](./literature_review/index.html) ·
    [Literature evidence ledger](./sigmoid_literature_sources.json) ·
    [Reference browser run](./reference/browser-results.zip)
    """)
    return


@app.cell
def _(mo):
    source = mo.ui.dropdown(
        ["Published Study 5 data", "Upload CSV pair", "Synthetic demonstration"],
        value="Published Study 5 data", label="Data source", allow_select_none=False,
    )
    participants_upload = mo.ui.file(filetypes=[".csv"], label="Participant CSV", max_size=10000000)
    trials_upload = mo.ui.file(filetypes=[".csv"], label="Trial CSV", max_size=50000000)
    mo.vstack([
        mo.md("## 1 · Choose inputs\nUse the documented participant and trial CSV schemas."),
        source, mo.hstack([participants_upload, trials_upload], justify="start", gap=2),
        mo.md("The published dataset contains 42 participants and 17,114 trials. It uses arbitrary participant IDs and contains no name fields. Synthetic demonstration data are a separate, clearly labelled option."),
    ])
    return participants_upload, source, trials_upload


@app.cell
async def _(FILES, demo_pair, local_release_pair, mo, participants_upload, source, sys, trials_upload):
    synthetic = source.value == "Synthetic demonstration"
    mo.stop(
        source.value == "Upload CSV pair" and (not participants_upload.value or not trials_upload.value),
        mo.callout("Choose both CSV files to begin. Partial uploads are never mixed with example data.", kind="info"),
    )
    if synthetic:
        source_bytes = demo_pair()
    elif source.value == "Upload CSV pair":
        source_bytes = (participants_upload.value[0].contents, trials_upload.value[0].contents)
    elif sys.platform == "emscripten":
        from pyodide.http import pyfetch as _pyfetch
        _contents = []
        for _filename in FILES:
            _response = await _pyfetch(str(mo.notebook_location() / "public" / "data" / _filename))
            if not _response.ok:
                raise ValueError(f"Published data download failed: {_response.status}")
            _contents.append(await _response.bytes())
        source_bytes = tuple(_contents)
    else:
        source_bytes = local_release_pair()
    return source_bytes, synthetic


@app.cell
def _(load_pair, mo, source_bytes):
    validation_error = None
    people, trials = [], []
    try:
        people, trials = load_pair(*source_bytes)
    except ValueError as _error:
        validation_error = str(_error)
    mo.stop(validation_error is not None, mo.callout(f"Validation stopped: {validation_error}", kind="danger"))
    return people, trials


@app.cell
def _(Counter, mo, people, source, synthetic, trials):
    input_qc = [
        {"check": "Participants", "count": len(people)},
        {"check": "Trial rows", "count": len(trials)},
        {"check": "Missing recorded RT", "count": sum(r["reaction_time_ms"] == "" for r in trials)},
        *[{"check": f"Outcome: {key}", "count": value} for key, value in sorted(Counter(r["outcome"] for r in trials).items())],
    ]
    mo.vstack([
        mo.md("## 2 · Validate and inspect\nSchemas, contiguous person IDs, trial keys, joins, Boolean fields, finite RTs, and known source-code/path patterns passed."),
        mo.callout("SYNTHETIC DEMONSTRATION · 8 invented participants, 480 invented trials." if synthetic else "PUBLISHED STUDY DATA · Released deidentified observations." if source.value == "Published Study 5 data" else "UPLOADED DATA · This view reflects your CSV pair.", kind="warn" if synthetic else "info"),
        mo.ui.table(input_qc, selection=None, show_download=False, pagination=False),
        mo.md("Misses and Catch outcomes remain visible in the input audit. Blank RT and questionnaire values stay missing; no imputation or automatic participant exclusion occurs."),
    ])
    return (input_qc,)


@app.cell
def _(WINDOWS, mo, trials):
    trial_type = mo.ui.multiselect(sorted({r["trial_type"] for r in trials}), value=[_type for _type in ("Audio-Tactile", "Baseline") if any(_r["trial_type"] == _type for _r in trials)], label="Trial types")
    condition = mo.ui.multiselect(sorted({r["condition"] for r in trials}), value=sorted({r["condition"] for r in trials}), label="Conditions")
    phase = mo.ui.multiselect(sorted({r["phase"] for r in trials}), value=sorted({r["phase"] for r in trials}), label="Respiratory phases")
    rt_window = mo.ui.dropdown(list(WINDOWS), value="No RT window", label="RT window", allow_select_none=False)
    mo.vstack([
        mo.md("## 3 · Choose a candidate RT view\nControls recalculate all downstream outputs. These choices define an exploratory view, not an approved analysis cohort."),
        mo.hstack([trial_type, condition, phase, rt_window], widths="equal", wrap=True),
        mo.md("The RT view requires a hit, a recorded response, and a nonblank RT. RT windows use the supplied flags exactly as recorded. Empty selections deliberately retain zero rows."),
    ])
    return condition, phase, rt_window, trial_type


@app.cell
def _(condition, people, phase, prepare, rt_window, trial_type, trials):
    settings = {
        "trial_types": trial_type.value, "conditions": condition.value,
        "phases": phase.value, "window": rt_window.value,
    }
    prepared, stages, columns = prepare(people, trials, **settings)
    return columns, prepared, settings, stages


@app.cell
def _(mo, prepared, stages, trials):
    mo.vstack([
        mo.md("## 4 · Follow the preparation steps"),
        mo.hstack([
            mo.stat(f"{len(prepared):,}", label="Candidate trial rows", bordered=True),
            mo.stat(str(len({r['participant_id'] for r in prepared})), label="Participants represented", bordered=True),
            mo.stat(f"{len(trials) - len(prepared):,}", label="Rows outside this view", bordered=True),
        ], widths="equal"),
        mo.ui.table(stages, selection=None, pagination=False, show_download=False),
        mo.md("Removal counts are sequential: each row is counted only at its first removal step. Your original input tables remain intact."),
    ])
    return


@app.cell
def _(escape, mo, prepared):
    _bins = [0] * 20
    for _row in prepared:
        _rt = float(_row["reaction_time_ms"])
        _bins[max(0, min(19, int(_rt / 125)))] += 1
    _maximum = max(_bins, default=0) or 1
    _bars = "".join(
        f'<rect x="{45 + i * 29}" y="{190 - count / _maximum * 150:.2f}" width="25" height="{count / _maximum * 150:.2f}" fill="#247a74"><title>{i * 125}–{(i + 1) * 125} ms: {count} rows</title></rect>'
        for i, count in enumerate(_bins)
    )
    _label = escape("Candidate RT distribution. Edge bins include values outside 0–2500 ms.")
    mo.vstack([
        mo.md("### Recorded RT distribution\nHover over a bar to inspect its count. The first and last bins include values outside the displayed range."),
        mo.Html(f'<svg viewBox="0 0 660 235" role="img" aria-label="{_label}" style="width:100%;max-width:900px"><title>{_label}</title>{_bars}<path d="M45 190H625" stroke="currentColor"/><text x="45" y="215" fill="currentColor" font-size="13">0 ms</text><text x="300" y="215" fill="currentColor" font-size="13">1250 ms</text><text x="570" y="215" fill="currentColor" font-size="13">2500 ms</text></svg>'),
    ])
    return


@app.cell
def _(mo, prepared):
    mo.vstack([
        mo.md("## 5 · Inspect the candidate data\nParticipant attributes are joined by ID with a `participant_` prefix. Preview a sample below; the download includes every retained row."),
        mo.ui.table(prepared[:500], selection=None, page_size=10, pagination=True, show_download=False, label=f"First {min(500, len(prepared))} of {len(prepared)} retained rows"),
    ] if prepared else [mo.callout("No rows match these preparation choices. Change the controls above; the empty export still records your choices.", kind="warn")])
    return


@app.cell
def _(columns, make_bundle, mo, prepared, settings, source_bytes, stages, synthetic):
    bundle, manifest = make_bundle(prepared, columns, stages, sources=source_bytes, settings=settings, synthetic=synthetic)
    mo.vstack([
        mo.md("## 6 · Download the preparation record\nThe ZIP contains `prepared_trials.csv` and `preparation_manifest.json`: input and output hashes, settings, and row counts at every step. No original filenames or acquisition paths are recorded."),
        mo.download(bundle, filename="study5_preparation.zip", mimetype="application/zip", label="Download prepared data + manifest"),
        mo.accordion({"Inspect the preparation manifest": mo.json(manifest)}),
        mo.md("The preview is exploratory. Continue below to execute the fixed paper-analysis pipeline on the full validated input."),
    ])
    return bundle, manifest


@app.cell
def _(mo):
    run_analysis = mo.ui.run_button(label="Run complete paper analysis")
    mo.vstack([
        mo.md("## 7 · Reproduce the paper analysis\nThe complete run performs participant-wide mean ±2.5-SD RT trimming, ML mixed models, cohort/coding/scale sensitivities, cluster-robust models, participant contrasts, repeated-measures ANOVA, sigmoid gates, missing-RT stress tests, and an 800-pipeline shape comparison: 320 original sigmoids, 320 shape-constrained sigmoids and 160 equally processed lines. It includes nested participant prediction and 1,000 participant bootstrap resamples for each selected sigmoid family. Preview filters above do not affect this run."),
        mo.callout("A full run computes in this browser, including 84 individual-curve methods, separate/shared plateau normalization, 500-resample intervals, reliability/recovery checks and questionnaire links. Source recordings and private acquisition metadata cannot be reconstructed from the CSVs; those checks are explicitly marked unavailable. Models and tables are a reproducible draft for author review.",kind="info"),
        run_analysis,
    ])
    return (run_analysis,)


@app.cell
def _():
    from paper_analysis import analyze
    from publication_report import result_bundle, primary_summary, figure_svg, markdown_report
    from participant_report import curve_bytes, diagnostics, contrast_diagnostics
    return analyze, contrast_diagnostics, curve_bytes, diagnostics, figure_svg, markdown_report, primary_summary, result_bundle


@app.cell
def _(analyze, mo, people, result_bundle, run_analysis, source_bytes, trials):
    mo.stop(not run_analysis.value, mo.md("Choose **Run complete paper analysis** to calculate the publication results."))
    with mo.status.spinner(title="Computing the complete behavioral analysis in Python…") as _spinner:
        paper_results, paper_retained = analyze(people, trials, progress=lambda _text: _spinner.update(title=_text))
        _spinner.update(title="Building figures and the complete curve atlas…")
        # Finish the expensive PDF export before result tables issue browser RPCs.
        analysis_zip, analysis_manifest = result_bundle(paper_results,paper_retained,source_bytes)
    return analysis_manifest, analysis_zip, paper_results, paper_retained


@app.cell
def _(mo, paper_results, primary_summary, synthetic):
    _summary = primary_summary(paper_results)
    mo.vstack([
        mo.md("## 8 · Primary results and robustness"),
        mo.callout(paper_results["participant_sigmoids"].get("linkage_audit",{}).get("status","Individual profiles unavailable")+". Full-release behavioural inference requires the source-recording linkage to be verified; see the individual-profile audit below.",kind="warn"),
        mo.callout("These results use synthetic example data." if synthetic else "These results were computed from the selected deidentified dataset.",kind="warn" if synthetic else "success"),
        mo.hstack([
            mo.stat(str(_summary["participants"]),label="Participants",bordered=True),
            mo.stat(f'{_summary["retained_at"]:,}',label="Retained Audio–Tactile RTs",bordered=True),
            mo.stat(f'{_summary["p"]:.6f}',label="Primary interaction p",bordered=True),
            mo.stat(f'{_summary["sigmoid_pass"]}/{_summary["sigmoid_cells"]}',label="Trial sigmoid cells passing R²≥.70",bordered=True),
        ],widths="equal",wrap=True),
        mo.md(f'Primary interaction: **{_summary["estimate"]:.3f} ms per SOA SD**, 95% model-based Wald CI **[{_summary["ci_low"]:.3f}, {_summary["ci_high"]:.3f}]**. A non-significant difference does not establish equivalence. The saturated trial R² ceiling is **{_summary["r2_ceiling"]:.3f}**.'),
        mo.ui.table([{k:r.get(k) for k in ("name","status","participants","n","lr","df","p")} for r in paper_results["mixed_models"]],selection=None,pagination=False,label="Mixed-model comparisons"),
    ])
    return


@app.cell
def _(figure_svg, mo, paper_results):
    mo.vstack([
        mo.md("## 9 · Reproducible figures\nEvery point is a mean across participant means. Intervals are pointwise 95% t intervals across participants; plotted overlap is not the interaction test."),
        mo.Html(figure_svg(paper_results,"raw_at")),
        mo.Html(figure_svg(paper_results,"same_label_at_minus_baseline")),
    ])
    return


@app.cell
def _(figure_svg, mo, paper_results):
    _d = paper_results["descriptive_sigmoids"]
    mo.stop(_d["status"] != "computed", mo.callout(_d.get("reason", "Descriptive curves unavailable."), kind="warn"))
    _a = _d["shape_audit"]
    mo.vstack([
        mo.md(f"## 10 · Four descriptive sigmoid curves\nAll four curves use **{_d['selected_method']}**, selected uniformly from **{_d['candidate_count']} pipelines**. Each person has equal weight. These post hoc approximations describe the extracted RT summaries; the original participant fit gate remains separate."),
        mo.md("**Midpoint m** locates half of the fitted asymptotic RT change. **Width s** controls the transition: smaller s means a steeper curve. It is a logistic scale, not a Gaussian standard deviation. The RT slope at the midpoint is amplitude/(4s)."),
        mo.md("### New goal: a visible, data-supported PPS transition\nThe goal now requires both bends inside the measured range, adequate sampling around the midpoint, fair predictive comparisons, and visual inspection. A mathematical sigmoid alone does not meet it. The [literature review](./literature_review/index.html) explains the scientific rationale, contrary evidence and remaining checks. Prediction scores condition on already-cleaned participant profiles; they evaluate relative shape rather than absolute RT."),
        mo.Html(figure_svg(paper_results,"pps_shape")),
        mo.Html(figure_svg(paper_results,"sigmoid_geometry")),
        mo.callout(f"The shape-constrained method is {_a['visible_method']}. These S shapes are imposed by explicit criteria. {_a['original_candidates_with_four_visible_transitions']}/{_d['candidate_count']} original pipelines met those criteria in all four curves. Compare the outer prediction errors below before interpreting a physiological boundary.",kind="warn"),
        mo.ui.table([{k:v for k,v in r.items() if k in ("family","outer_rmse_ms")} for r in _a["nested_prediction"]["scores"]],selection=None,pagination=False,label="Nested participant prediction; lower error is better"),
        mo.ui.table(_a["visible_parameters"],selection=None,pagination=False,label="Imposed-shape estimates and conditional uncertainty"),
        mo.md("### Original unconstrained-shape search\nThe following broad sigmoids and their uncertainty retain the original best-score result for comparison."),
        mo.Html(figure_svg(paper_results,"descriptive_sigmoids")),
        mo.ui.table([{k:r[k] for k in ("condition","phase","midpoint_cm","width_cm","midpoint_slope_ms_per_cm","midpoint_cm_conditional_bootstrap_low","midpoint_cm_conditional_bootstrap_high","bootstrap_flat_fraction","bootstrap_midpoint_bound_fraction")} for r in _d["parameters"]],selection=None,pagination=False,label="Midpoint, width and steepness; conditional bootstrap intervals"),
        mo.callout(f"Prediction-error tuning score: {_d['selected_tuning_rmse_ms']:.3f} ms; straight-line benchmark: {_d['validation']['linear_shape_rmse_ms']:.3f} ms. The improvement is small. Five sampled positions cannot establish the full S shape or its asymptotes. Bootstrap intervals condition on this selected method and nonflat draws; flat and boundary-hit fractions are reported explicitly.",kind="warn"),
        mo.accordion({
            "Shape criteria and measured-range diagnostics":mo.json({k:_a[k] for k in ("criteria","original_geometry","visible_geometry","interpretation")}),
            "Nested prediction and all inner selection scores":mo.json(_a["nested_prediction"]),
            "Unsmoothed curvature test · any nonlinearity, not specifically sigmoid":mo.vstack([mo.md(_a["raw_curvature"]["method"]),mo.ui.table(_a["raw_curvature"]["rows"],selection=None)]),
            "320 shape-constrained and 160 tuned-linear candidates":mo.ui.table([{k:v for k,v in r.items() if k not in ("parameters","fold_rmse_ms")} for r in _a["visible_candidates"]+_a["linear_candidates"]],selection=None,page_size=10),
            "Full sigmoid extrapolation · model assumptions outside the data":mo.Html(figure_svg(paper_results,"sigmoid_extrapolation")),
            "All 320 extraction/smoothing candidates":mo.ui.table([{k:v for k,v in r.items() if k not in ("parameters","fold_rmse_ms")} for r in _d["candidates"]],selection=None,page_size=10),
            "Paired descriptive midpoint and steepness comparisons":mo.ui.table(_d["comparisons"],selection=None),
            "Robust reference, coordinate and bound sensitivity":mo.json(_d["sensitivity"]),
            "Parameter definitions, bounds and bootstrap scope":mo.json({k:_d[k] for k in ("formula","parameter_definitions","bounds","grid","selection","bootstrap_scope")}),
        }),
    ])
    return


@app.cell
def _(mo, paper_results):
    mo.vstack([
        mo.md("## 11 · Diagnostics, assumptions and gated follow-ups"),
        mo.accordion({
            "Cohort and cleaning":mo.json(paper_results["cohort"]),
            "Participant quality":mo.ui.table(paper_results["participant_quality"],selection=None,page_size=10),
            "Cluster-robust models":mo.json(paper_results["cluster_models"]),
            "Participant slope contrasts and exploratory JZS":mo.json(paper_results["participant_slope_interaction"]),
            "Repeated-measures ANOVA":mo.ui.table(paper_results["repeated_measures_anova"],selection=None),
            "Supplementary contrasts and Holm adjustment":mo.ui.table(paper_results["supplementary_contrasts"],selection=None),
            "Four-noise Friedman":mo.json(paper_results["four_noise_friedman"]),
            "Order-stratified sensitivity":mo.ui.table(paper_results["order_sensitivities"],selection=None),
            "Sigmoid viability and coordinate sensitivity":mo.ui.table(paper_results["sigmoid_summary"],selection=None),
            "Descriptive group sigmoid fits":mo.ui.table(paper_results["group_sigmoid_descriptions"],selection=None),
            "Boundary and boundary-related questionnaire gate":mo.json(paper_results["boundary_followups"]),
            "Missing-hit-RT stress scenarios":mo.json(paper_results["missing_rt_stress"]),
            "Source-dependent checks unavailable from CSVs":mo.md("\n".join("- "+s for s in paper_results["unavailable_checks"])),
        }),
    ])
    return


@app.cell
def _(figure_svg, mo, paper_results):
    _q=paper_results["questionnaires"]
    _s=_q["spatial"]
    mo.vstack([
        mo.md("## 12 · MAIA-2 and spatial frame of reference\nExploratory analyses of all eight interoceptive dimensions and paired spatial ratings. [Scientific rationale and data coverage](./literature_review/QUESTIONNAIRES.html)."),
        mo.md(f"**Scoring audit:** {_q['scoring']['matches']} stored subscale scores match recomputation; {_q['scoring']['mismatches']} mismatches. {_q['maia_complete']}/{_q['participants']} participants have complete MAIA-2 data. Missing questionnaires do not change the primary behavioural cohort."),
        mo.md(_q["administration"]),
        mo.Html(figure_svg(paper_results,"questionnaire_summary")),
        mo.md(f"**Paired spatial ratings:** Viscereality higher / equal / lower = {_s['higher']} / {_s['ties']} / {_s['lower']}. Exact two-sided sign-test p = {_s['p'] if _s['p'] is not None else 'not estimable'}. Higher means a higher recorded A–H code; the administered anchor key is unavailable."),
        mo.md("### Main follow-up: numerical spatial change\nDelta = post-Viscereality code minus post-Control code, independent of presentation order. MAIA-2 was measured before the experiment; these models test trait moderation."),
        mo.Html(figure_svg(paper_results,"spatial_change")),
        mo.ui.table(_q["delta_associations"][:8],selection=None),
        mo.callout("Numerical code differences assume comparable category steps. Direction-only correlations provide an ordinal sensitivity. All p values are unadjusted; intervals are pointwise. The raw-RT slope contrast is not a PPS boundary.",kind="info"),
        mo.accordion({
            "Condition × MAIA models: classical and HC3 uncertainty":mo.ui.table(_q["moderation"],selection=None,page_size=16),
            "Direction-only sensitivity":mo.ui.table([r for r in _q["associations"] if r["y"]=="spfrref_change_direction"],selection=None),
            "Delta and behavioural contrast":mo.ui.table(_q["delta_associations"][8:],selection=None),
            "Numerical delta distribution and summary":mo.json({"distribution":_s["delta_distribution"],"summary":_s["delta_descriptives"]}),
            "Eight dimensions and reliability uncertainty":mo.ui.table(_q["scales"],selection=None),
            "Supplementary: 33 earlier associations":mo.ui.table(_q["associations"],selection=None,page_size=12),
            "Supplementary association figure":mo.Html(figure_svg(paper_results,"questionnaire_associations")),
            "37 item distributions and item–rest diagnostics":mo.ui.table(_q["items"],selection=None,page_size=10),
            "Spatial comparison, order counts and transition table":mo.json(_s),
            "Scoring audit":mo.ui.table(_q["scoring_audit"],selection=None,page_size=10),
            "Descriptive inter-subscale correlations":mo.ui.table(_q["interscale_descriptive"],selection=None),
            "Resampling and interpretation limits":mo.json({"resampling":_q["resampling"],"delta_analysis":_q["delta_analysis"],"limitations":_q["limitations"]}),
            "Coverage of every released data domain":mo.ui.table(paper_results["data_coverage"],selection=None),
        }),
    ])
    return


@app.cell
def _(diagnostics, figure_svg, mo, paper_results):
    _r=paper_results["participant_sigmoids"]
    mo.stop(_r["status"]!="computed",mo.md(_r.get("reason","Individual profiles unavailable")))
    participant_view=mo.ui.dropdown(_r["plot_data"]["participant_ids"],value=_r["plot_data"]["participant_ids"][0],label="Participant curve atlas")
    mo.vstack([
        mo.md("## 13 · Individual curves and common RT plateaus\nFour condition × phase curves per person. [Scientific rationale](./literature_review/INDIVIDUAL_PARAMETERS.html)."),
        mo.callout(_r["linkage_audit"]["status"]+". "+_r["linkage_audit"]["interpretation"],kind="warn"),
        mo.md(f"**{_r['curve_count']} exploratory curves** using `{_r['selected_method']['method']}`. "+_r["interpretation"]),
        mo.md("**Common plateaus:** subtract each fitted lower plateau and divide by its fitted plateau separation. The lower plateau becomes 0 and the upper becomes 1. Midpoint is unchanged; normalized steepness is 1/(4 × width). Raw RT slope additionally depends on amplitude and direction. No observations are clipped. A second model shares the RT plateaus across each person's four curves."),
        mo.Html(figure_svg(paper_results,"participant_diagnostics")),
        mo.ui.table(diagnostics(_r),selection=None,label="Reliability, known-signal recovery and uncertainty"),
        mo.accordion({
            "Main questionnaire links · individual plateaus":mo.ui.table([r for r in _r["associations"] if r["scope"]=="main"],selection=None,page_size=27),
            "Main questionnaire links · shared plateaus":mo.ui.table([r for r in _r["shared_associations"] if r["scope"]=="main"],selection=None,page_size=27),
            "All parameters and conditional intervals":mo.ui.table(_r["parameters"]+_r["shared_parameters"],selection=None,page_size=8),
            "All 84 candidate methods and prediction scores":mo.vstack([mo.ui.table(_r["candidates"],selection=None),mo.json(_r["prediction"])]),
            "Recording audit and exclusion sensitivities":mo.json({"audit":_r["linkage_audit"],"exclusions":_r["linkage_sensitivities"]}),
            "All questionnaire links · two models":mo.ui.table([r|{"model":k} for k in ("associations","shared_associations") for r in _r[k]],selection=None),
            "Uncertainty and method scope":mo.md(_r["selection_scope"]+"\n\n"+_r["uncertainty"]),
        }),
        participant_view,
    ])
    return (participant_view,)


@app.cell
def _(curve_bytes, mo, paper_results, participant_view):
    mo.vstack([
        mo.md(f"### Participant {participant_view.value} · raw RT and normalized curves"),
        mo.Html(curve_bytes(paper_results["participant_sigmoids"],participant_view.value).decode()),
    ])
    return


@app.cell
def _(contrast_diagnostics, figure_svg, mo, paper_results):
    _r=paper_results["robustness"];_g=_r["group_shape"];_p=paper_results["participant_sigmoids"]
    mo.stop(_g["status"]!="computed" or _p["status"]!="computed",mo.md("Additional robustness checks unavailable for this cohort."))
    mo.vstack([
        mo.md("## 14 · Remaining-analysis robustness checks\nPrimary models excluding ambiguous recordings, uncertainty in fitted changes, log-distance comparison and shape-constraint sensitivity. All are post hoc; no new multiple-testing correction is applied."),
        mo.Html(figure_svg(paper_results,"remaining_robustness")),
        mo.ui.table(contrast_diagnostics(_p),selection=None,label="Reliability and recovery of within-person changes"),
        mo.accordion({
            "Primary RT linkage exclusions":mo.json(_r["recording_linkage"]),
            "Parameter contrasts and refit intervals":mo.ui.table(_p["contrasts"]+[
                a|{"excluded_ids":','.join(s["excluded_ids"])} for s in _p["linkage_sensitivities"] for a in s["contrasts"]],selection=None),
            "Five-family nested prediction":mo.ui.table(_g["prediction"]["scores"],selection=None),
            "All nine geometry specifications":mo.json(_g["geometry_sensitivities"]),
            "Repeated method-selection stability":mo.ui.table(_g["selection_frequencies"],selection=None),
            "Interpretation and limits":mo.md(_g["interpretation"]),
        }),
    ])
    return


@app.cell
def _(figure_svg, mo, paper_results):
    from participant_report import repeated_rows, repeated_primary, repeated_markdown
    _p=paper_results["participant_sigmoids"]
    mo.stop(_p["status"]!="computed",mo.md("Individual-parameter repeated-measures models unavailable."))
    _rows,_label=repeated_primary(_p)
    mo.vstack([
        mo.md("## 15 · PPS boundary and sharpness: repeated-measures models\nAll four Condition × Phase cells contribute. MAIA-2 dimensions remain continuous baseline covariates; spatial-rating change is a post-intervention correlate. Classical tests condition on fitted proxies; curve-refit intervals and poor reliability limit physiological interpretation."),
        mo.Html(figure_svg(paper_results,"parameter_repeated_measures")),
        mo.ui.table([a for a in _rows if a["predictor"]=="none"],selection=None,label="2 × 2 repeated-measures ANOVA · "+_label),
        mo.ui.table([a for a in _rows if a["effect"]=="Condition" and a["order_adjusted"] and a["predictor"]!="spfrref_change_direction"],selection=None,label="Condition × MAIA/spatial change · order-adjusted ANCOVA"),
        mo.accordion({"Every cohort, effect and covariate":mo.ui.table(repeated_rows(_p),selection=None),
                      "Model definitions and interpretation":mo.md(repeated_markdown(_p))}),
    ])
    return


@app.cell
def _(analysis_manifest, analysis_zip, markdown_report, mo, paper_results):
    mo.vstack([
        mo.md("## 16 · Export the complete analysis\nIncludes the 42-page individual curve atlas, normalized trial RTs, both individual parameter specifications, all questionnaire links and recording-exclusion sensitivities with refit intervals, parameter ANOVA/ANCOVA models, log-distance and shape robustness checks, plus the full earlier analysis, figures, source code and hashes. All files are generated from this run."),
        mo.download(analysis_zip,filename="study5_publication_analysis.zip",mimetype="application/zip",label="Download complete analysis"),
        mo.accordion({"Read the analysis report":mo.md(markdown_report(paper_results)),"Inspect the reproducibility manifest":mo.json(analysis_manifest)}),
    ])
    return


if __name__ == "__main__":
    app.run()
