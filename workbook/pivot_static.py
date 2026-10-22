"""Export the existing descriptive views for the lightweight browser pivot."""

import json

import pandas as pd

from pivot_data import exploration_views


def browser_frame(frame):
    columns = list(frame.columns)
    numeric = [field for field in columns if pd.api.types.is_numeric_dtype(frame[field])]
    types = {field: ("boolean" if pd.api.types.is_bool_dtype(frame[field]) else
                     "integer" if pd.api.types.is_integer_dtype(frame[field]) else
                     "number" if field in numeric else "text") for field in columns}
    records = frame.astype(object).where(frame.notna(), None).values.tolist()
    return dict(columns=columns, numeric=numeric, types=types, rows=records)


def build_views(people, trials, destination):
    destination.mkdir(parents=True, exist_ok=True)
    catalog = []
    for name, frame in exploration_views(people, trials).items():
        filename = {"Participant-distance means": "means.json", "All trial records": "trials.json",
                    "Participants and questionnaires": "participants.json"}[name]
        payload = browser_frame(frame)
        (destination / filename).write_text(json.dumps(payload, allow_nan=False, separators=(",", ":")), encoding="utf-8")
        if filename == "means.json":
            preview = browser_frame(frame[["participant_id", "condition", "phase", "soa_ms", "distance_cm", "corrected_rt_ms"]])
            preview_text = json.dumps(preview, allow_nan=False, separators=(",", ":"))
            if len(preview_text.encode("utf-8")) > 65536:
                raise ValueError("The default pivot data exceeds its 64 KiB startup budget.")
            (destination / "means-preview.json").write_text(preview_text, encoding="utf-8")
            core = browser_frame(frame[["participant_id", "condition", "phase", "soa_ms", "distance_cm", "reaction_time_ms"]])
            core_text = json.dumps(core, allow_nan=False, separators=(",", ":"))
            if len(core_text.encode("utf-8")) > 65536:
                raise ValueError("The core-data preview exceeds its 64 KiB startup budget.")
            (destination / "means-core-preview.json").write_text(core_text, encoding="utf-8")
        catalog.append(dict(name=name, file=filename, records=len(frame)))
    return catalog
