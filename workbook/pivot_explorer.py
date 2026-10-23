# /// script
# requires-python = ">=3.12"
# dependencies = ["marimo==0.25.1", "pandas==3.0.6", "numpy==2.4.3", "scipy==1.17.1", "matplotlib==3.10.8"]
# ///

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full", app_title="Study 5 · Pivot table")


@app.cell
def _():
    import marimo as mo
    import sys
    import json
    import pandas as pd
    from pathlib import Path
    from preparation import FILES, load_pair, local_release_pair, audit_release
    from pivot_data import exploration_views, cohort_frame, pivot_frame, typed_frame, result_catalog, AGGREGATIONS

    return (
        AGGREGATIONS,
        FILES,
        Path,
        audit_release,
        cohort_frame,
        exploration_views,
        json,
        load_pair,
        local_release_pair,
        mo,
        pd,
        pivot_frame,
        result_catalog,
        sys,
        typed_frame,
    )


@app.cell
def _(mo):
    mo.md("""
    # Pivot table
    """)
    return


@app.cell
async def _(
    FILES,
    Path,
    audit_release,
    exploration_views,
    json,
    load_pair,
    local_release_pair,
    mo,
    result_catalog,
    sys,
):
    if sys.platform == "emscripten":
        from pyodide.http import pyfetch as _pyfetch
        async def fetch_json(path):
            _response = await _pyfetch(str(mo.notebook_location() / "public" / "snapshots" / path))
            if not _response.ok:
                raise ValueError(f"Saved table download failed: {_response.status}")
            return await _response.json()
        _contents = []
        for _filename in FILES:
            _response = await _pyfetch(str(mo.notebook_location() / ".." / ".." / "public" / "data" / _filename))
            if not _response.ok:
                raise ValueError(f"Public data download failed: {_response.status}")
            _contents.append(await _response.bytes())
        _people, _trials = load_pair(*_contents)
        catalog = await fetch_json("catalog.json")
    else:
        _people, _trials = load_pair(*local_release_pair())
        _root = Path(__file__).resolve().parent.parent
        catalog = [dict(source=path) for path in result_catalog(_root)]
        async def fetch_json(path):
            return json.loads(Path(path).read_text())
    audit_release(_people, _trials)
    views = exploration_views(_people, _trials)
    return catalog, fetch_json, views


@app.cell
def _(catalog, mo, views):
    collection = mo.ui.dropdown([*views, "Saved analysis tables"], value="Participant-distance means",
                                label="Data collection", allow_select_none=False)
    cohort = mo.ui.dropdown(["Primary behavioural cohort", "Full release", "Exclude P011", "Exclude P033"],
                           value="Primary behavioural cohort", label="Participant cohort", allow_select_none=False)
    saved_table = mo.ui.dropdown([row["source"] for row in catalog], value=catalog[0]["source"],
                                label="Saved result table", allow_select_none=False)
    filters_enabled = mo.ui.checkbox(value=False, label="Activate filters")
    filters_enabled
    return cohort, collection, filters_enabled, saved_table


@app.cell
async def _(
    Path,
    catalog,
    collection,
    fetch_json,
    pd,
    saved_table,
    sys,
    typed_frame,
    views,
):
    source_note = "Audited public CSV pair · descriptive summaries."
    if collection.value == "Saved analysis tables":
        _entry = next(row for row in catalog if row["source"] == saved_table.value)
        if sys.platform == "emscripten":
            _snapshot = await fetch_json(_entry["file"])
            if _snapshot["sha256"] != _entry["sha256"] or _snapshot["source"] != _entry["source"]:
                raise ValueError("Saved table identity differs from its catalogue.")
            source_frame = typed_frame(_snapshot["rows"])
        else:
            source_frame = typed_frame(pd.read_csv(Path(__file__).resolve().parent.parent / _entry["source"],
                                                  dtype=str, keep_default_na=False).to_dict("records"))
        source_note = f"Frozen output: [{_entry['source']}](https://github.com/GeorgeFejer91/Respiratory-Modulation-of-Peripersonal-Space-Representation/blob/main/{_entry['source']}). Keep quantities, units, variants and original cohorts separate."
    else:
        source_frame = views[collection.value]
    return source_frame, source_note


@app.cell
def _(cohort, cohort_frame, mo, source_frame):
    cohort_data = cohort_frame(source_frame, cohort.value)
    _fields = list(cohort_data.columns)
    _defaults = [field for field in ("condition", "phase", "trial_type", "outcome", "model", "quantity", "gate") if field in _fields]
    filter_fields = mo.ui.multiselect(_fields, value=_defaults[:4], label="Filter fields")
    return cohort_data, filter_fields


@app.cell
def _(cohort_data, filter_fields, mo):
    _widgets = {field: mo.ui.multiselect(
        sorted(cohort_data[field].astype(object).fillna("(missing)").astype(str).unique().tolist()),
        value=sorted(cohort_data[field].astype(object).fillna("(missing)").astype(str).unique().tolist()), label=field)
        for field in filter_fields.value}
    filters = mo.ui.batch(mo.md("\n\n".join("{" + field + "}" for field in _widgets)), _widgets)
    return (filters,)


@app.cell
def _(cohort_data, filters, filters_enabled):
    filtered = cohort_data.copy()
    if filters_enabled.value:
        for _field, _selected in filters.value.items():
            filtered = filtered[filtered[_field].astype(object).fillna("(missing)").astype(str).isin(_selected)]
    return (filtered,)


@app.cell
def _(AGGREGATIONS, cohort_data, collection, mo):
    _fields = list(cohort_data.columns)
    _numeric = cohort_data.select_dtypes(include="number").columns.tolist()
    _row_defaults = ["distance_cm"] if "distance_cm" in _fields else [field for field in ("model", "cohort", "prior", "quantity", "parameter", "term", "participant_id", "cell") if field in _fields]
    row_fields = mo.ui.multiselect(_fields, value=_row_defaults, label="Rows")
    column_fields = mo.ui.multiselect(_fields, value=[field for field in ["condition", "phase"] if field in _fields], label="Columns")
    value_fields = mo.ui.multiselect(_fields, value=next(([field] for field in ["corrected_rt_ms", "reaction_time_ms", "posterior_median", "median", "age_years"] if field in _numeric), _numeric[:1]), label="Values")
    aggregation = mo.ui.dropdown([*AGGREGATIONS, "Row count"], value="Mean", label="Summarize by", allow_select_none=False)
    totals = mo.ui.checkbox(value=collection.value != "Saved analysis tables", label="Grand totals")
    return aggregation, column_fields, row_fields, totals, value_fields


@app.cell
def _(
    aggregation,
    cohort,
    collection,
    column_fields,
    mo,
    row_fields,
    saved_table,
    source_note,
    totals,
    value_fields,
):
    mo.accordion({"Pivot settings": mo.vstack([
        mo.hstack([collection, cohort], wrap=True, justify="start", gap=2),
        *([saved_table] if collection.value == "Saved analysis tables" else []),
        mo.hstack([row_fields, column_fields, value_fields], wrap=True, justify="start", gap=2),
        mo.hstack([aggregation, totals], wrap=True, justify="start", gap=2),
        mo.md(source_note),
        mo.md("Default: 40 participants, excluding linked P011/P033. Corrected RT (ms) = AT − retained participant × condition × phase Baseline mean. Participant-distance means give each cell equal weight; trials give each trial equal weight. Use the participant table for questionnaire means. These descriptive summaries do not propagate model uncertainty. [Methods](https://github.com/GeorgeFejer91/Respiratory-Modulation-of-Peripersonal-Space-Representation/blob/main/workbook/README.md)."),
    ])})
    return


@app.cell
def _(filter_fields, filters, filters_enabled, mo):
    if filters_enabled.value:
        mo.output.append(mo.vstack([filter_fields, filters]))
    return


@app.cell
def _(
    aggregation,
    column_fields,
    filtered,
    mo,
    pivot_frame,
    row_fields,
    totals,
    value_fields,
):
    pivot_error = None
    pivot = None
    try:
        pivot = pivot_frame(filtered, row_fields.value, column_fields.value, value_fields.value, aggregation.value, totals.value)
    except ValueError as _error:
        pivot_error = str(_error)
    mo.stop(pivot_error is not None, mo.callout(pivot_error or "", kind="warn"))
    _people = f" · {filtered.participant_id.nunique()} participants" if "participant_id" in filtered else " · original cohort"
    mo.vstack([
        mo.ui.table(pivot, selection=None, pagination=True, page_size=20, show_download=True,
                    show_data_types=False, show_column_summaries=False, label="Pivot table",
                    format_mapping={field: "{:.6g}" for field in pivot.select_dtypes(include="number").columns}),
        mo.md(f"{len(filtered):,} source records{_people}"),
    ])
    return


if __name__ == "__main__":
    app.run()
