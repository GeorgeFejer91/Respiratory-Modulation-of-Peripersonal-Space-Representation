"""Descriptive views and pivots; no statistical models are fitted here."""

import json
from hashlib import sha256
from pathlib import Path

import pandas as pd

from paper_analysis import AXES, clean
from questionnaires import score_people


SAVED_FOLDERS = (
    "baseline_effects", "bayesian", "browser-analysis", "directional_sigmoid",
    "publication_sigmoid_choice", "trial_cleaning", "visible_sigmoid",
)
AGGREGATIONS = {
    "Mean": "mean", "Median": "median", "Sum": "sum", "Count nonmissing": "count",
    "Standard deviation": "std", "Minimum": "min", "Maximum": "max",
    "Unique values": "nunique",
}


def typed_frame(rows):
    frame = pd.DataFrame(rows).replace("", None)
    for column in frame:
        present = frame[column].dropna()
        if len(present) and present.isin(["True", "False"]).all():
            frame[column] = frame[column].map({"True": True, "False": False})
        elif len(present):
            numeric = pd.to_numeric(frame[column], errors="coerce")
            if numeric.notna().sum() == len(present):
                frame[column] = numeric
    return frame


def exploration_views(people, trials):
    retained, _, _ = clean(people, trials)
    kept_ids = {row["trial_id"] for row in retained}
    participants = typed_frame(people)
    scored, _ = score_people(people)
    scores = pd.DataFrame(scored).set_index("participant_id")
    for field in scores:
        if field.startswith(("maia2_", "spfrref_")):
            participants[field] = participants.participant_id.map(scores[field])
    frame = typed_frame(trials)
    frame["retained_global"] = frame.trial_id.isin(kept_ids)
    frame["linked_recording"] = frame.participant_id.isin(["P011", "P033"])
    frame["distance_cm"] = frame.soa_ms.map(AXES["registered"]).where(frame.trial_type == "Audio-Tactile")
    frame = frame.merge(participants[["participant_id", "age_years", "gender", "handedness", "condition_order"]],
                        on="participant_id", validate="many_to_one")
    keys = ["participant_id", "condition", "phase"]
    baseline = frame[frame.retained_global & (frame.trial_type == "Baseline")].groupby(keys).reaction_time_ms.mean()
    frame = frame.join(baseline.rename("baseline_mean_ms"), on=keys)
    frame["corrected_rt_ms"] = (frame.reaction_time_ms - frame.baseline_mean_ms).where(
        frame.retained_global & (frame.trial_type == "Audio-Tactile"))
    means = frame[frame.retained_global & (frame.trial_type == "Audio-Tactile")].groupby(
        keys + ["soa_ms", "distance_cm"], as_index=False).agg(
            reaction_time_ms=("reaction_time_ms", "mean"), corrected_rt_ms=("corrected_rt_ms", "mean"),
            baseline_mean_ms=("baseline_mean_ms", "first"), n_trials=("trial_id", "size"))
    means = means.merge(participants, on="participant_id", validate="many_to_one")
    return {"Participant-distance means": means, "All trial records": frame,
            "Participants and questionnaires": participants}


def cohort_frame(frame, cohort):
    if "participant_id" not in frame or cohort == "Full release":
        return frame.copy()
    excluded = {"Primary behavioural cohort": ["P011", "P033"],
                "Exclude P011": ["P011"], "Exclude P033": ["P033"]}[cohort]
    return frame[~frame.participant_id.isin(excluded)].copy()


def pivot_frame(frame, rows, columns, values, aggregation, totals=True):
    if set(rows) & set(columns):
        raise ValueError("A field can be assigned to Rows or Columns, not both.")
    if not values and aggregation != "Row count":
        raise ValueError("Choose at least one numeric Values field, or use Row count.")
    if any(field in rows + columns for field in values):
        raise ValueError("Values fields must be different from Rows and Columns.")
    source = frame.copy()
    if aggregation == "Row count":
        source["Record count"] = 1
        values, function = ["Record count"], "sum"
    else:
        function = AGGREGATIONS[aggregation]
        if function not in ("count", "nunique") and any(not pd.api.types.is_numeric_dtype(source[field]) for field in values):
            raise ValueError("This summary requires numeric Values fields. For text, choose Count nonmissing or Unique values.")
        if function == "sum":
            function = lambda series: series.sum(min_count=1)
    for field in rows + columns:
        source[field] = source[field].astype(object).fillna("(missing)")
    if not rows:
        source["All records"] = "All records"
        rows = ["All records"]
    if source.empty:
        return pd.DataFrame(columns=rows)
    row_count = len(source[rows].drop_duplicates())
    column_count = len(source[columns].drop_duplicates()) if columns else 1
    if (row_count + 1) * (column_count + 1) * len(values) > 100000:
        raise ValueError("This pivot exceeds 100,000 cells. Filter records or remove a high-cardinality Rows/Columns field.")
    result = source.groupby(rows + columns, observed=True, sort=True)[values].agg(function)
    if columns:
        result = result.unstack(columns)
        if totals:
            row_totals = source.groupby(rows, observed=True)[values].agg(function)
            for value in values:
                result[(value, "Grand total", *([""] * (len(columns) - 1)))] = row_totals[value]
    if totals:
        if columns:
            column_totals = source.groupby(columns, observed=True)[values].agg(function)
            grand = {key: column_totals.loc[key[1] if len(columns) == 1 else key[1:], key[0]]
                     for key in result.columns if key[1] != "Grand total"}
            for value in values:
                grand[(value, "Grand total", *([""] * (len(columns) - 1)))] = source[value].agg(function)
        else:
            grand = {value: source[value].agg(function) for value in values}
        total_index = "Grand total" if len(rows) == 1 else ("Grand total", *([""] * (len(rows) - 1)))
        result.loc[total_index, :] = pd.Series(grand)
    if isinstance(result.columns, pd.MultiIndex):
        result.columns = [" · ".join(str(part) for part in parts if str(part)) for parts in result.columns]
    return result.reset_index()


def result_catalog(root):
    import subprocess
    tracked = subprocess.run(["git", "ls-files", "results"], cwd=root, check=True,
                             capture_output=True, text=True).stdout.splitlines()
    return [path for path in tracked if path.endswith(".csv") and Path(path).parts[1] in SAVED_FOLDERS]


def build_snapshots(root, destination):
    from preparation import PRIVATE_PATTERN
    import csv
    destination.mkdir(parents=True, exist_ok=True)
    catalog = []
    for relative in result_catalog(root):
        content = (root / relative).read_bytes()
        text = content.decode("utf-8-sig")
        if PRIVATE_PATTERN.search(text):
            raise ValueError("Private source pattern in pivot snapshot: " + relative)
        reader = csv.DictReader(text.splitlines())
        records = list(reader)
        filename = sha256(relative.encode()).hexdigest()[:16] + ".json"
        payload = dict(source=relative, sha256=sha256(content).hexdigest(), columns=reader.fieldnames, rows=records)
        (destination / filename).write_text(json.dumps(payload, allow_nan=False), encoding="utf-8")
        catalog.append(dict(source=relative, sha256=payload["sha256"], rows=len(records), file=filename))
    (destination / "catalog.json").write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    return catalog
