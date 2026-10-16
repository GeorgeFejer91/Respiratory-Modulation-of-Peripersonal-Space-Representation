"""Portable data checks and exploratory preparation, shared with the CSV CLI.

This module uses only the Python standard library so it also runs in Pyodide.
It never reads repository data or writes files on import.
"""

import csv
import io
import json
import math
import re
import zipfile
from collections import Counter
from hashlib import sha256


PARTICIPANT_COLUMNS = (
    ["participant_id", "data_availability", "age_years", "gender", "handedness",
     "condition_order", "planned_trials", "analysis_trials", "spfrref_viscereality",
     "spfrref_viscereality_ordinal", "spfrref_control", "spfrref_control_ordinal"]
    + [f"maia2_item_{i:02d}" for i in range(1, 38)]
    + [f"maia2_{name}" for name in (
        "noticing", "not_distracting", "not_worrying", "attention_regulation",
        "emotional_awareness", "self_regulation", "body_listening", "trusting")]
)
TRIAL_COLUMNS = [
    "participant_id", "trial_id", "trial_index", "part_number", "condition",
    "block_number", "trial_number", "phase", "noise_type", "trial_type",
    "soa_ms", "distance_bin", "response_given", "outcome", "reaction_time_ms",
    "rt_valid_100_2000", "rt_valid_200_2000",
]
FILES = ("study5_participants.csv", "study5_pps_trials.csv")
WINDOWS = {
    "No RT window": None,
    "Recorded 100–2000 ms flag": "rt_valid_100_2000",
    "Recorded 200–2000 ms flag": "rt_valid_200_2000",
}
PRIVATE_PATTERN = re.compile(r"(?i)dataset0[1-9]|PUB\d+|[A-Z]:\\|[/\\]Users[/\\]")


def decode_csv(content, expected):
    """Decode a schema-controlled UTF-8 CSV without inferring missing values."""
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValueError("CSV files must use UTF-8 encoding.") from error
    reader = csv.DictReader(io.StringIO(text, newline=""))
    if reader.fieldnames != expected:
        raise ValueError("Unexpected CSV columns or column order; use the documented export schema.")
    rows = list(reader)
    if not rows or any(None in row or any(v is None for v in row.values()) for row in rows):
        raise ValueError("Missing or malformed CSV rows.")
    return rows


def encode_csv(columns, rows):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def validate_public_rows(people, trials):
    """Enforce the existing publication CSV key, join, and source-code checks."""
    if not people or not trials:
        raise ValueError("Participant and trial tables must both contain rows.")
    ids = [row["participant_id"] for row in people]
    if ids != [f"P{i:03d}" for i in range(len(people))]:
        raise ValueError("Participant IDs are not unique and contiguous from P000.")
    per_person = Counter()
    seen_trials = set()
    for row in trials:
        participant = row["participant_id"]
        if participant not in ids:
            raise ValueError("A trial references an unknown participant.")
        per_person[participant] += 1
        trial_id = f"{participant}_T{per_person[participant]:04d}"
        if row["trial_id"] != trial_id or trial_id in seen_trials:
            raise ValueError("Invalid or duplicate trial ID.")
        seen_trials.add(trial_id)
    if set(per_person) != set(ids):
        raise ValueError("At least one participant has no trials.")
    for row in [*people, *trials]:
        if any(PRIVATE_PATTERN.search(value) for value in row.values()):
            raise ValueError("A source identifier or private acquisition path was found.")


def validate_questionnaire_rows(people):
    """Check numeric instrument ranges and agreement of the two ordinal encodings."""
    for row in people:
        for key, text in row.items():
            if key.startswith("maia2_") and text != "":
                try:
                    value = float(text)
                except (ValueError, TypeError) as error:
                    raise ValueError("MAIA responses/scores must be numeric or blank.") from error
                if not math.isfinite(value) or not 0 <= value <= 5 or ("item_" in key and not value.is_integer()):
                    raise ValueError("MAIA items must be integers 0–5; subscale scores must be within 0–5.")
        for condition in ("control", "viscereality"):
            letter = row.get("spfrref_"+condition, "")
            code = row.get("spfrref_"+condition+"_ordinal", "")
            if letter == "" and code == "":
                continue
            if letter not in tuple("ABCDEFGH") or code not in tuple(str(i) for i in range(1, 9)) or ord(letter)-64 != int(code):
                raise ValueError("Spatial-frame letters A–H must agree with ordinal codes 1–8; missing pairs must be blank.")


def load_pair(participant_bytes, trial_bytes):
    people = decode_csv(participant_bytes, PARTICIPANT_COLUMNS)
    trials = decode_csv(trial_bytes, TRIAL_COLUMNS)
    validate_public_rows(people, trials)
    validate_questionnaire_rows(people)
    for row in trials:
        for flag in ("response_given", "rt_valid_100_2000", "rt_valid_200_2000"):
            if row[flag] not in ("True", "False"):
                raise ValueError(f"Invalid Boolean value in {flag}.")
        if row["reaction_time_ms"]:
            try:
                value = float(row["reaction_time_ms"])
            except ValueError as error:
                raise ValueError("A recorded reaction time is not numeric.") from error
            if not math.isfinite(value):
                raise ValueError("Recorded reaction times must be finite or blank.")
    return people, trials


def prepare(people, trials, *, trial_types, conditions, phases, window):
    """Return a fresh RT candidate view and a sequential, non-overlapping audit."""
    if window not in WINDOWS:
        raise ValueError("Unknown RT window.")
    stages = []

    def record(label, rows):
        previous = stages[-1]["rows_retained"] if stages else len(trials)
        stages.append({"step": label, "rows_retained": len(rows),
                       "rows_removed_here": previous - len(rows),
                       "participants": len({r['participant_id'] for r in rows})})
        return rows

    selected = record("1 · Validated input", list(trials))
    selected = record("2 · Trial types", [r for r in selected if r["trial_type"] in trial_types])
    selected = record("3 · Conditions and phases", [
        r for r in selected if r["condition"] in conditions and r["phase"] in phases
    ])
    selected = record("4 · Hits with recorded RT", [
        r for r in selected if r["outcome"] == "hit"
        and r["response_given"] == "True" and r["reaction_time_ms"] != ""
    ])
    flag = WINDOWS[window]
    selected = record("5 · RT window", [r for r in selected if flag is None or r[flag] == "True"])
    participant_fields = ("data_availability", "age_years", "gender", "handedness", "condition_order")
    lookup = {person["participant_id"]: person for person in people}
    prepared = [dict(row, **{
        f"participant_{key}": lookup[row["participant_id"]][key] for key in participant_fields
    }) for row in selected]
    columns = TRIAL_COLUMNS + [f"participant_{key}" for key in participant_fields]
    return prepared, stages, columns


def make_bundle(prepared, columns, stages, *, sources, settings, synthetic):
    """Create an in-memory, reproducible CSV + JSON download; no files are saved."""
    manifest = {
        "format_version": 1, "status": "exploratory data preparation",
        "synthetic_demo": synthetic,
        "source_sha256": {name: sha256(data).hexdigest() for name, data in zip(FILES, sources)},
        "settings": settings, "steps": stages,
        "missing_values": "Blank values are retained; no imputation is performed.",
        "rt_windows": "Uses recorded flags; does not recompute or reinterpret their bounds.",
    }
    csv_bytes = encode_csv(columns, prepared)
    manifest["prepared_csv_sha256"] = sha256(csv_bytes).hexdigest()
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in (
            ("prepared_trials.csv", csv_bytes),
            ("preparation_manifest.json", json.dumps(manifest, indent=2).encode("utf-8")),
        ):
            entry = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, content)
    return buffer.getvalue(), manifest


def demo_pair():
    """Generate synthetic examples from rules, without accessing participant data."""
    people, trials = [], []
    for person in range(8):
        participant = f"P{person:03d}"
        people.append(dict.fromkeys(PARTICIPANT_COLUMNS, "") | {
            "participant_id": participant, "data_availability": "synthetic",
            "age_years": str(22 + person), "gender": "synthetic", "handedness": "synthetic",
            "condition_order": "demo only", "planned_trials": "60", "analysis_trials": "60",
        })
        for index in range(1, 61):
            trial_type = ("Audio-Tactile", "Audio-Tactile", "Baseline", "Audio-Tactile", "Audio-Tactile", "Catch")[(index - 1) % 6]
            catch = trial_type == "Catch"
            missing = catch or index % 17 == 0
            rt = (95, 175, 420, 560, 740, 2100)[(index + person) % 6]
            trials.append(dict.fromkeys(TRIAL_COLUMNS, "") | {
                "participant_id": participant, "trial_id": f"{participant}_T{index:04d}",
                "trial_index": str(index), "part_number": "1" if index <= 30 else "2",
                "condition": "Control" if index <= 30 else "Viscereality",
                "block_number": str(1 + (index - 1) // 10), "trial_number": str(index),
                "phase": "Inhale" if index % 2 else "Exhale", "noise_type": "pink",
                "trial_type": trial_type, "soa_ms": str((300, 800, 1500, 2200, 2700)[index % 5]),
                "distance_bin": "", "response_given": str(not missing),
                "outcome": "correct_rejection" if catch else "miss" if missing else "hit",
                "reaction_time_ms": "" if missing else str(rt),
                "rt_valid_100_2000": str(not missing and 100 <= rt <= 2000),
                "rt_valid_200_2000": str(not missing and 200 <= rt <= 2000),
            })
    return encode_csv(PARTICIPANT_COLUMNS, people), encode_csv(TRIAL_COLUMNS, trials)


def local_release_pair():
    """Explicit native-mode access to the canonical release; unused in browsers."""
    from pathlib import Path
    folder=Path(__file__).resolve().parents[1]/"data"/"raw"
    return tuple((folder/name).read_bytes() for name in FILES)


def audit_release(people,trials):
    """Reject free text hidden in the allowlisted deidentified release fields."""
    validate_public_rows(people,trials)
    categories={
        "data_availability":{"full_measures","pps_only"},"gender":{"female","male"},
        "handedness":{"left","right"},
        "condition_order":{"Control-Viscereality","Viscereality-Control"},
    }
    for person in people:
        for key,allowed in categories.items():
            if person[key] not in allowed:raise ValueError(f"Unexpected free text in release field {key}.")
        for key,value in person.items():
            if key=="participant_id" or key in categories or value=="":continue
            if key in ("spfrref_viscereality","spfrref_control"):
                if value not in set("ABCDEFGH"):raise ValueError("Unexpected rating label.")
            else:
                try: number=float(value)
                except ValueError as error:raise ValueError(f"Unexpected free text in numeric release field {key}.") from error
                if not math.isfinite(number):raise ValueError("Nonfinite participant value in release.")
                if key.startswith("maia2_") and not 0<=number<=5:raise ValueError("MAIA response/score outside 0–5.")
    trial_categories={"condition":{"Control","Viscereality"},"phase":{"Inhale","Exhale"},
        "noise_type":{"blue","brown","pink","white","nan","N/A",""},
        "trial_type":{"Audio-Tactile","Baseline","Catch"},
        "outcome":{"hit","miss","false_alarm","correct_rejection"},
        "distance_bin":{"","D1","D2","D3","D4","D5"},
        "response_given":{"True","False"},"rt_valid_100_2000":{"True","False"},"rt_valid_200_2000":{"True","False"}}
    for trial in trials:
        for key,allowed in trial_categories.items():
            if trial[key] not in allowed:raise ValueError(f"Unexpected free text in trial release field {key}.")
        for key,value in trial.items():
            if key in trial_categories or key in ("participant_id","trial_id") or value=="":continue
            try:number=float(value)
            except ValueError as error:raise ValueError(f"Unexpected free text in numeric trial field {key}.") from error
            if not math.isfinite(number):raise ValueError("Nonfinite numeric trial value.")
    return {"status":"passed schema and full field-value release audit","participants":len(people),"trial_rows":len(trials)}
