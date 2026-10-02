"""Build and check the publication CSVs from an already deidentified export.

The input location is supplied at run time. No source identifiers or crosswalk
are saved in this repository.
"""

import argparse
import csv
import re
from collections import Counter
from hashlib import sha256
from pathlib import Path


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


def read_csv(path, expected):
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != expected:
            raise ValueError(f"Unexpected columns in {path.name}: {reader.fieldnames}")
        rows = list(reader)
    if not rows or any(None in row for row in rows):
        raise ValueError(f"Missing or malformed rows in {path.name}")
    return rows


def write_csv(path, columns, rows):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def check(folder):
    people = read_csv(folder / FILES[0], PARTICIPANT_COLUMNS)
    trials = read_csv(folder / FILES[1], TRIAL_COLUMNS)
    ids = [row["participant_id"] for row in people]
    expected = [f"P{i:03d}" for i in range(len(people))]
    if ids != expected:
        raise ValueError("Participant IDs are not unique and contiguous from P000")
    per_person = Counter()
    seen_trials = set()
    for row in trials:
        participant = row["participant_id"]
        if participant not in ids:
            raise ValueError(f"Trial references an unknown participant: {participant}")
        per_person[participant] += 1
        trial_id = f"{participant}_T{per_person[participant]:04d}"
        if row["trial_id"] != trial_id or trial_id in seen_trials:
            raise ValueError(f"Invalid or duplicate trial ID: {row['trial_id']}")
        seen_trials.add(trial_id)
    if set(per_person) != set(ids):
        raise ValueError("At least one participant has no trials")
    for filename in FILES:
        content = (folder / filename).read_text(encoding="utf-8")
        if re.search(r"(?i)dataset0[1-9]|PUB\d+|[A-Z]:\\|[/\\]Users[/\\]", content):
            raise ValueError(f"Source identifier or path found in {filename}")
    print(f"PASS: {len(people)} contiguous participants, {len(trials)} unique trial rows")


def build(source, destination):
    people = read_csv(source / FILES[0], PARTICIPANT_COLUMNS)
    trials = read_csv(source / FILES[1], TRIAL_COLUMNS)
    old_ids = [row["participant_id"] for row in people]
    if len(old_ids) != len(set(old_ids)):
        raise ValueError("Input participant IDs are not unique")
    # Hash ordering separates publication numbers from the input file order.
    shuffled = sorted(old_ids, key=lambda old: sha256(old.encode("utf-8")).digest())
    mapping = {old: f"P{i:03d}" for i, old in enumerate(shuffled)}
    per_person = Counter()
    for row in people:
        row["participant_id"] = mapping[row["participant_id"]]
    people.sort(key=lambda row: row["participant_id"])
    for row in trials:
        old = row["participant_id"]
        if old not in mapping:
            raise ValueError(f"Trial references an unknown input participant: {old}")
        row["participant_id"] = mapping[old]
    trials.sort(key=lambda row: (row["participant_id"], int(row["trial_index"])))
    for row in trials:
        new = row["participant_id"]
        per_person[new] += 1
        row["trial_id"] = f"{new}_T{per_person[new]:04d}"
    destination.mkdir(parents=True, exist_ok=True)
    write_csv(destination / FILES[0], PARTICIPANT_COLUMNS, people)
    write_csv(destination / FILES[1], TRIAL_COLUMNS, trials)
    check(destination)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build", "check"))
    parser.add_argument("folder", type=Path, help="Source folder for build; output folder for check")
    parser.add_argument("output", type=Path, nargs="?", help="Output folder for build")
    args = parser.parse_args()
    if args.action == "build":
        if args.output is None:
            parser.error("build requires an output folder")
        build(args.folder, args.output)
    else:
        if args.output is not None:
            parser.error("check accepts one folder")
        check(args.folder)
