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
    [Analysis contract](./ANALYSIS_PLAN.md) · [Data release record](./DATA_RELEASE.md) ·
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
        mo.md("## 7 · Reproduce the paper analysis\nThe complete run performs participant-wide mean ±2.5-SD RT trimming, ML mixed models, cohort/coding/scale sensitivities, cluster-robust models, participant contrasts, repeated-measures ANOVA, sigmoid gates, and missing-RT stress tests. Preview filters above do not affect this run."),
        mo.callout("A full run computes in this browser. Source recordings and private acquisition metadata cannot be reconstructed from the CSVs; those checks are explicitly marked unavailable. Models and tables are a reproducible draft for author review.",kind="info"),
        run_analysis,
    ])
    return (run_analysis,)


@app.cell
def _():
    from paper_analysis import analyze
    from publication_report import result_bundle, primary_summary, figure_svg, markdown_report
    return analyze, figure_svg, markdown_report, primary_summary, result_bundle


@app.cell
def _(analyze, mo, people, run_analysis, trials):
    mo.stop(not run_analysis.value, mo.md("Choose **Run complete paper analysis** to calculate the publication results."))
    with mo.status.spinner(title="Computing the complete behavioral analysis in Python…"):
        paper_results, paper_retained = analyze(people, trials)
    return paper_results, paper_retained


@app.cell
def _(mo, paper_results, primary_summary, synthetic):
    _summary = primary_summary(paper_results)
    mo.vstack([
        mo.md("## 8 · Primary results and robustness"),
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
def _(mo, paper_results):
    mo.vstack([
        mo.md("## 10 · Diagnostics, assumptions and gated follow-ups"),
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
            "Boundary/MAIA/SpFrRef inference gate":mo.json(paper_results["boundary_followups"]),
            "Questionnaire descriptives":mo.ui.table(paper_results["questionnaire_descriptives"],selection=None),
            "Missing-hit-RT stress scenarios":mo.json(paper_results["missing_rt_stress"]),
            "Source-dependent checks unavailable from CSVs":mo.md("\n".join("- "+s for s in paper_results["unavailable_checks"])),
        }),
    ])
    return


@app.cell
def _(markdown_report, mo, paper_results, paper_retained, result_bundle, source_bytes):
    analysis_zip, analysis_manifest = result_bundle(paper_results,paper_retained,source_bytes)
    mo.vstack([
        mo.md("## 11 · Export the complete analysis\nSave the full JSON report, model/coefficient tables, participant QC, retained RTs, curve/sigmoid/ANOVA tables, publication SVGs, and source/output hashes. All files are generated from this run."),
        mo.download(analysis_zip,filename="study5_publication_analysis.zip",mimetype="application/zip",label="Download complete analysis"),
        mo.accordion({"Read the analysis report":mo.md(markdown_report(paper_results)),"Inspect the reproducibility manifest":mo.json(analysis_manifest)}),
    ])
    return analysis_manifest, analysis_zip


if __name__ == "__main__":
    app.run()
