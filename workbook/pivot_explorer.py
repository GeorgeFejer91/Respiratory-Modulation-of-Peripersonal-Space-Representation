# /// script
# requires-python = ">=3.12"
# dependencies = ["marimo==0.25.1", "pandas==3.0.6", "numpy==2.4.3", "scipy==1.17.1", "matplotlib==3.10.8"]
# ///

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full", app_title="Study 5 · Pivot explorer")


@app.cell
def _():
    import marimo as mo
    import sys
    import json
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    from pathlib import Path
    from preparation import FILES, load_pair, local_release_pair, audit_release
    from pivot_data import exploration_views, cohort_frame, pivot_frame, typed_frame, result_catalog, AGGREGATIONS
    return AGGREGATIONS, FILES, Path, audit_release, cohort_frame, exploration_views, json, load_pair, local_release_pair, mo, np, pd, pivot_frame, plt, result_catalog, sys, typed_frame


@app.cell
def _(mo):
    mo.md("""
    # Pivot explorer

    Choose a table, filter records, then assign **Rows**, **Columns**, and **Values**.
    Changes recalculate in your browser. Click table headers to sort; download the
    current pivot or its filtered source below. Use the heatmap to compare cells.

    **Descriptive exploration.** The default behavioural cohort excludes the linked
    P011/P033 recordings. This page does not refit models or change earlier analyses.
    """)
    return


@app.cell
async def _(FILES, Path, audit_release, exploration_views, json, load_pair, local_release_pair, mo, result_catalog, sys):
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
def _(mo, views):
    collection = mo.ui.dropdown([*views, "Saved analysis tables"], value="Participant-distance means",
                                 label="Data collection", allow_select_none=False)
    cohort = mo.ui.dropdown(["Primary behavioural cohort", "Full release", "Exclude P011", "Exclude P033"],
                           value="Primary behavioural cohort", label="Participant cohort", allow_select_none=False)
    mo.hstack([collection, cohort], wrap=True, justify="start", gap=2)
    return cohort, collection


@app.cell
def _(catalog, collection, mo):
    saved_table = mo.ui.dropdown([row["source"] for row in catalog], value=catalog[0]["source"],
                                label="Saved result table", allow_select_none=False)
    if collection.value == "Saved analysis tables":
        mo.output.append(mo.vstack([saved_table, mo.md("Each saved table is a separate frozen result. Fields such as model, quantity, cohort, gate, and units must be kept separate when interpreting summaries. Use the source link to check its report.")]))
    return (saved_table,)


@app.cell
async def _(Path, catalog, collection, fetch_json, mo, pd, saved_table, sys, typed_frame, views):
    source_note = "Live preparation from the unchanged audited CSV pair."
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
        source_note = f"Frozen saved output: [{_entry['source']}](https://github.com/GeorgeFejer91/Study5_Publication/blob/main/{_entry['source']}). No refitting."
    else:
        source_frame = views[collection.value]
    mo.md(source_note)
    return source_frame, source_note


@app.cell
def _(cohort, cohort_frame, mo, source_frame):
    cohort_data = cohort_frame(source_frame, cohort.value)
    _fields = list(cohort_data.columns)
    _defaults = [field for field in ("condition", "phase", "trial_type", "outcome", "model", "quantity", "gate") if field in _fields]
    filter_fields = mo.ui.multiselect(_fields, value=_defaults[:4], label="Filter fields")
    mo.vstack([mo.md("## 1 · Filter records"), filter_fields,
               mo.md("Select values to keep. Clearing a filter keeps zero records. Missing values have their own entry. Cohort filtering applies only to tables containing participant_id; aggregate result tables retain their original cohorts.")])
    return cohort_data, filter_fields


@app.cell
def _(cohort_data, filter_fields, mo):
    filters = mo.ui.dictionary({field: mo.ui.multiselect(
        sorted(cohort_data[field].astype(object).fillna("(missing)").astype(str).unique().tolist()),
        value=sorted(cohort_data[field].astype(object).fillna("(missing)").astype(str).unique().tolist()), label=field)
        for field in filter_fields.value})
    filters
    return (filters,)


@app.cell
def _(cohort_data, filters):
    filtered = cohort_data.copy()
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
    mo.vstack([mo.md("## 2 · Arrange the pivot"),
               mo.hstack([row_fields, column_fields, value_fields], wrap=True, justify="start", gap=2),
               mo.hstack([aggregation, totals], wrap=True, justify="start", gap=2),
               mo.md("Totals use the filtered source records. Blanks are missing, not zero; SD uses n−1. Saved results start with totals off to keep quantities and model variants separate.")])
    return aggregation, column_fields, row_fields, totals, value_fields


@app.cell
def _(aggregation, column_fields, filtered, mo, pivot_frame, row_fields, totals, value_fields):
    pivot_error = None
    pivot = None
    try:
        pivot = pivot_frame(filtered, row_fields.value, column_fields.value, value_fields.value, aggregation.value, totals.value)
    except ValueError as _error:
        pivot_error = str(_error)
    mo.stop(pivot_error is not None, mo.callout(pivot_error or "", kind="warn"))
    _people = f"{filtered.participant_id.nunique()} participants" if "participant_id" in filtered else "Aggregate table · original cohort"
    mo.vstack([mo.md(f"## 3 · Pivot table\n**{len(filtered):,} source records** · **{_people}** · {len(pivot):,} pivot rows"),
               mo.ui.table(pivot, selection=None, pagination=True, page_size=20, show_download=True,
                           show_data_types=False, show_column_summaries=False, label="Current pivot",
                           format_mapping={field: "{:.6g}" for field in pivot.select_dtypes(include="number").columns})])
    return (pivot,)


@app.cell
def _(aggregation, collection, column_fields, cohort, filter_fields, filters, filtered, json, mo, pivot, row_fields, source_note, totals, value_fields):
    _settings = dict(collection=collection.value, source=source_note, cohort=cohort.value, filters=filters.value,
                     rows=row_fields.value, columns=column_fields.value, values=value_fields.value,
                     aggregation=aggregation.value, totals=totals.value, source_records=len(filtered))
    pivot_download = mo.download(pivot.to_csv(index=False).encode(), filename="study5-pivot.csv", mimetype="text/csv", label="Download pivot CSV")
    source_download = mo.download(lambda: filtered.to_csv(index=False).encode(), filename="study5-filtered-source.csv", mimetype="text/csv", label="Download filtered source CSV")
    settings_download = mo.download(json.dumps(_settings, indent=2).encode(), filename="study5-pivot-settings.json", label="Download settings")
    mo.hstack([pivot_download, source_download, settings_download], wrap=True, justify="start", gap=2)
    return pivot_download, settings_download, source_download


@app.cell
def _(mo, pivot):
    _numeric = pivot.select_dtypes(include="number").columns.tolist()
    _default = [field for field in _numeric if "Grand total" not in field][:4]
    chart_values = mo.ui.multiselect(_numeric, value=_default, label="Heatmap columns")
    mo.vstack([mo.md("## 4 · Heatmap\nChoose comparable numeric columns with the same units. At most the first 40 pivot rows and 12 selected columns are plotted; the table and download keep every cell. Colour shows magnitude, not statistical evidence."), chart_values])
    return (chart_values,)


@app.cell
def _(chart_values, mo, np, pivot, plt, row_fields):
    mo.stop(not chart_values.value or pivot.empty, mo.md("Select numeric heatmap columns and retain at least one record."))
    _sample = pivot.head(40)
    _selected = chart_values.value[:12]
    _matrix = _sample[_selected].to_numpy(dtype=float)
    _fig, _axis = plt.subplots(figsize=(max(7, len(_selected) * 1.8), max(3, len(_sample) * .3)))
    _image = _axis.imshow(np.ma.masked_invalid(_matrix), aspect="auto", cmap="cividis")
    _axis.set_xticks(range(len(_selected)), _selected, rotation=40, ha="right", fontsize=9)
    _labels = [" · ".join(str(row[field]) for field in row_fields.value) for row in _sample.to_dict("records")] if row_fields.value else _sample.iloc[:, 0].astype(str).tolist()
    _axis.set_yticks(range(len(_sample)), _labels, fontsize=9)
    _fig.colorbar(_image, ax=_axis, label="Value in selected column units")
    _fig.tight_layout()
    _rendered = mo.as_html(_fig)
    plt.close(_fig)
    _rendered
    return


@app.cell
def _(filtered, mo):
    mo.accordion({
        "Inspect filtered source records": mo.ui.table(filtered, selection=None, page_size=10,
                                                       show_column_summaries=False, label="Filtered source records"),
        "Measurement, weighting and interpretation": mo.md("""
        Corrected RT = Audio–Tactile RT − retained participant × condition × phase
        Baseline mean, in ms. The existing participant-wide ±2.5 SD cleaner is reused;
        baseline means pool SOAs. Distance uses the registered 10–100 cm mapping for
        AT trials only. Descriptive correction does not propagate baseline uncertainty.

        Participant-distance means weight each observed participant × condition ×
        phase × distance cell equally; trial summaries weight each trial equally.
        P011/P033 share a recording with swapped condition labels; full-release
        behavioural summaries do not establish 42 independent recordings.

        MAIA was measured once at baseline; spatial ratings once per condition.
        Pictogram anchors remain unverified. Questionnaire fields repeat across
        distance cells: use the participant table for participant-weighted summaries.
        Numerical spatial-code differences assume comparable category spacing.

        Saved model medians, intervals and diagnostic flags are frozen outputs.
        Keep quantities, units, model variants and original cohorts separate.
        Averaging posterior medians or interval endpoints creates no new posterior
        or inferential test. A visible S imposed by a model is not an observed PPS boundary.
        """)})
    return


if __name__ == "__main__":
    app.run()
