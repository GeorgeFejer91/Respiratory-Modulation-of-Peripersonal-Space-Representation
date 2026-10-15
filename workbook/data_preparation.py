# /// script
# requires-python = ">=3.12"
# dependencies = ["marimo==0.25.1"]
# ///

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full", app_title="Study 5 · Data preparation")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    from collections import Counter
    from html import escape
    from preparation import demo_pair, load_pair, prepare, make_bundle, WINDOWS
    return Counter, WINDOWS, demo_pair, escape, load_pair, make_bundle, prepare


@app.cell
def _(mo):
    _navigation = "[Return to the application](../)" if mo.app_meta().mode == "edit" else "[Open the editable workbook](./editor/)"
    mo.md(f"""
    # Study 5 · Data preparation

    A live research workbook. Follow each transformation, change preparation
    choices, and inspect exactly which observations reach the candidate dataset.

    **Exploratory preparation** · Python runs in your browser on the published
    page. Uploaded CSV contents are processed in browser memory and are not
    sent to a processing server. Refreshing the page clears this session.
    Download your prepared data and manifest before leaving.

    {_navigation} to work with the Python steps online.
    Changes in the browser can be downloaded; publishing a revised page requires
    committing the workbook source to GitHub.
    """)
    return


@app.cell
def _(mo):
    source = mo.ui.dropdown(
        ["Synthetic demonstration", "Upload CSV pair"],
        value="Synthetic demonstration", label="Data source", allow_select_none=False,
    )
    participants_upload = mo.ui.file(filetypes=[".csv"], label="Participant CSV", max_size=10000000)
    trials_upload = mo.ui.file(filetypes=[".csv"], label="Trial CSV", max_size=50000000)
    mo.vstack([
        mo.md("## 1 · Choose inputs\nUse the documented participant and trial CSV schemas."),
        source, mo.hstack([participants_upload, trials_upload], justify="start", gap=2),
        mo.md("The example is generated from synthetic rules. It contains no Study 5 participant observations."),
    ])
    return participants_upload, source, trials_upload


@app.cell
def _(demo_pair, mo, participants_upload, source, trials_upload):
    synthetic = source.value == "Synthetic demonstration"
    mo.stop(
        not synthetic and (not participants_upload.value or not trials_upload.value),
        mo.callout("Choose both CSV files to begin. Partial uploads are never mixed with example data.", kind="info"),
    )
    source_bytes = demo_pair() if synthetic else (
        participants_upload.value[0].contents, trials_upload.value[0].contents
    )
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
def _(Counter, mo, people, synthetic, trials):
    input_qc = [
        {"check": "Participants", "count": len(people)},
        {"check": "Trial rows", "count": len(trials)},
        {"check": "Missing recorded RT", "count": sum(r["reaction_time_ms"] == "" for r in trials)},
        *[{"check": f"Outcome: {key}", "count": value} for key, value in sorted(Counter(r["outcome"] for r in trials).items())],
    ]
    mo.vstack([
        mo.md("## 2 · Validate and inspect\nSchemas, contiguous person IDs, trial keys, joins, Boolean fields, finite RTs, and known source-code/path patterns passed."),
        mo.callout("SYNTHETIC DEMONSTRATION · 8 invented participants, 480 invented trials." if synthetic else "UPLOADED DATA · This view reflects your CSV pair. Checks do not establish consent or complete anonymity.", kind="warn" if synthetic else "info"),
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
        mo.md("The current manuscript reports an older 40-person analysis. This workbook prepares data views; it does not rerun models or validate manuscript results."),
    ])
    return bundle, manifest


if __name__ == "__main__":
    app.run()
