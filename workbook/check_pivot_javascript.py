"""Compare the shipped JavaScript pivot with the existing pandas implementation."""

import argparse
import json
import math
import subprocess
from pathlib import Path

import pandas as pd

from pivot_data import AGGREGATIONS, cohort_frame, exploration_views, pivot_frame, typed_frame
from pivot_static import browser_frame
from preparation import load_pair, local_release_pair


def validate(node):
    frames = exploration_views(*load_pair(*local_release_pair()))
    frames["edge"] = pd.DataFrame({"group": ["A", "A", "B", "B", None], "phase": ["I", "I", "I", "E", "E"],
                                  "rt": [2., 4., 12., None, 0.], "other": [1., 3., 6., None, 9.],
                                  "text": ["x", "x", "y", None, ""], "flag": [True, False, True, False, True]})
    frames["empty"] = frames["edge"].iloc[:0]
    frames["large"] = pd.DataFrame({"group": range(400), "phase": range(400), "rt": range(400)})
    frames["people-edge"] = pd.DataFrame({"participant_id": ["A", "A", "A", "B", "B", "C"],
        "soa_ms": [1, 1, 1, 1, 1, 2], "phase": ["I", "I", "E", "I", "E", "I"],
        "rt": [2., 4., 6., 10., 14., 0.]})
    snapshots = [dict(columns=["group", "rt", "flag", "empty"], rows=[
        dict(group="x", rt="2.25", flag="True", empty=""),
        dict(group="y", rt="", flag="False", empty="")])]
    frames["snapshot"] = typed_frame(snapshots[0]["rows"])
    cases = []
    def add(name, rows, columns, values, aggregation, **extra):
        cases.append(dict(frame=name, settings=dict(rows=rows, columns=columns, values=values,
                         aggregation=aggregation, totals=True, cohort="Full release", filtersEnabled=False,
                         filters={}, **extra)))
    for aggregation in [*AGGREGATIONS, "Row count"]:
        for axes in [(["group"], ["phase"]), ([], []), (["group", "phase"], [])]:
            add("edge", *axes, ["rt", "other"], aggregation)
        add("Participant-distance means", ["distance_cm"], ["condition", "phase"], ["corrected_rt_ms"], aggregation)
        add("All trial records", ["trial_type"], ["condition", "phase"], ["reaction_time_ms"], aggregation)
    for name in ["empty", "large", "snapshot"]:
        add(name, ["group"], [] if name == "snapshot" else ["phase"], ["rt"], "Mean")
    add("edge", ["group"], [], ["text"], "Unique values")
    add("edge", ["group"], [], ["text"], "Count nonmissing")
    add("edge", ["group"], [], ["text"], "Mean")
    add("edge", ["group"], ["group"], ["rt"], "Mean")
    add("edge", ["group"], [], ["group"], "Mean")
    add("edge", [], [], [], "Mean")
    add("edge", [], [], ["flag"], "Mean")
    add("edge", ["group"], ["flag"], ["rt"], "Mean")
    add("edge", ["group"], ["other"], ["rt"], "Mean")
    add("Participant-distance means", ["participant_id", "condition"], ["distance_cm", "phase"], ["corrected_rt_ms"], "Mean")
    for enabled in [True, False]:
        settings = dict(rows=["distance_cm"], columns=["condition", "phase"], values=["corrected_rt_ms"], aggregation="Mean",
                        totals=False, cohort="Primary behavioural cohort", filtersEnabled=enabled, filters={"phase": ["Exhale"]})
        cases.append(dict(frame="Participant-distance means", settings=settings))
    for columns in [[], ["phase"], ["condition"], ["condition", "phase"]]:
        for value in ["reaction_time_ms", "corrected_rt_ms"]:
            for cohort in ["Primary behavioural cohort", "Full release", "Exclude P011", "Exclude P033"]:
                for filtered in [False, True]:
                    cases.append(dict(frame="Participant-distance means", settings=dict(rows=["soa_ms"], columns=columns,
                        values=[value], aggregation="Mean", totals=False, cohort=cohort, participantSummary=True,
                        filtersEnabled=filtered, filters={"phase": ["Inhale"]})))
    cases.append(dict(frame="people-edge", settings=dict(rows=["soa_ms"], columns=[], values=["rt"],
        aggregation="Mean", totals=False, cohort="Full release", participantSummary=True, filtersEnabled=False)))
    payload = dict(frames={name: browser_frame(frame) for name, frame in frames.items()}, cases=cases, snapshots=snapshots)
    runner = Path(__file__).with_name("check_pivot_javascript.mjs")
    process = subprocess.run([node, str(runner)], input=json.dumps(payload, allow_nan=False), text=True,
                             encoding="utf-8", capture_output=True)
    if process.returncode:
        raise RuntimeError(process.stderr)
    actual = json.loads(process.stdout)
    for index, (case, observed) in enumerate(zip(cases, actual["results"], strict=True)):
        settings = case["settings"]
        frame = cohort_frame(frames[case["frame"]], settings["cohort"])
        if settings["filtersEnabled"]:
            for field, values in settings["filters"].items():
                if values:
                    frame = frame[frame[field].isin(values)]
        source_count = len(frame)
        if settings.get("participantSummary"):
            keys = list(dict.fromkeys(["participant_id", *settings["rows"], *settings["columns"]]))
            frame = frame.groupby(keys, dropna=False, as_index=False)[settings["values"]].mean()
        try:
            expected = pivot_frame(frame, settings["rows"], settings["columns"], settings["values"], settings["aggregation"], settings["totals"])
        except ValueError:
            assert "error" in observed, (index, case, observed)
            continue
        assert "error" not in observed, (index, case, observed)
        expected = browser_frame(expected)
        assert expected["columns"] == observed["columns"], (index, expected["columns"], observed["columns"])
        assert len(expected["rows"]) == len(observed["rows"]), index
        assert source_count == observed["count"], index
        for expected_row, observed_row in zip(expected["rows"], observed["rows"], strict=True):
            for target, value in zip(expected_row, observed_row, strict=True):
                if isinstance(target, (int, float)) and not isinstance(target, bool):
                    assert isinstance(value, (int, float)) and math.isclose(target, value, rel_tol=1e-10, abs_tol=1e-10), (index, target, value)
                else:
                    assert target == value, (index, target, value)
        if settings.get("participantSummary"):
            for name, aggregation in [("sd", "Standard deviation"), ("n", "Count nonmissing")]:
                expected_stats = browser_frame(pivot_frame(frame, settings["rows"], settings["columns"],
                    settings["values"], aggregation, False))
                for row_index, row in enumerate(expected_stats["rows"]):
                    for column, target in enumerate(row[len(settings["rows"]):]):
                        value = observed["stats"][row_index][column][name]
                        assert target is value if target is None else math.isclose(target, value, rel_tol=1e-10, abs_tol=1e-10), (index, name, target, value)
    assert actual["snapshot"] == browser_frame(frames["snapshot"])
    assert actual["csv"] == '\ufeff"a","b"\r\n"=literal","quote""comma,"\r\n'
    print(f"JavaScript / Python parity: {len(cases)} cases; linked chart cells, combined SOA/condition filters, missingness, totals, CSV and typing pass.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--node", default="node")
    validate(parser.parse_args().node)
