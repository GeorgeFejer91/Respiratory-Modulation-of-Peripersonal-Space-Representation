"""Compare the shipped JavaScript pivot with the existing pandas implementation."""

import argparse
import json
import math
import subprocess
from pathlib import Path

import pandas as pd
from scipy.stats import gaussian_kde

from pivot_data import AGGREGATIONS, cohort_frame, exploration_views, pivot_frame, typed_frame
from pivot_static import browser_frame, normalization_parameters
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
    frames["benefit-edge"] = pd.DataFrame({"participant_id": ["A", "B", "C", "D"],
        "soa_ms": [100, 100, 200, 300], "reaction_time_ms": [400., 700., 500., 500.],
        "baseline_mean_ms": [500., 600., 500., 600.], "corrected_rt_ms": [-100., 100., 0., None]})
    snapshots = [dict(columns=["group", "rt", "flag", "empty"], rows=[
        dict(group="x", rt="2.25", flag="True", empty=""),
        dict(group="y", rt="", flag="False", empty="")])]
    frames["snapshot"] = typed_frame(snapshots[0]["rows"])
    cases = []
    def add(name, rows, columns, values, aggregation, **extra):
        cases.append(dict(frame=name, settings=dict(rows=rows, columns=columns, values=values,
                         aggregation=aggregation, totals=extra.pop("totals", True), cohort=extra.pop("cohort", "Full release"), filtersEnabled=False,
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
        for value in ["reaction_time_ms", "corrected_rt_ms", "baseline_benefit_ms"]:
            for cohort in ["Primary behavioural cohort", "Full release", "Exclude P011", "Exclude P033"]:
                for filtered in [False, True]:
                    cases.append(dict(frame="Participant-distance means", settings=dict(rows=["soa_ms"], columns=columns,
                        values=[value], aggregation="Mean", totals=False, cohort=cohort, participantSummary=True,
                        filtersEnabled=filtered, filters={"phase": ["Inhale"]})))
    cases.append(dict(frame="people-edge", settings=dict(rows=["soa_ms"], columns=[], values=["rt"],
        aggregation="Mean", totals=False, cohort="Full release", participantSummary=True, filtersEnabled=False)))
    for name in ["All trial records", "Participant-distance means"]:
        for filtered in [False, True]:
            cases.append(dict(frame=name, settings=dict(rows=[], columns=[], values=[], aggregation="Mean",
                totals=False, cohort="Primary behavioural cohort", rawRecords=True,
                filtersEnabled=filtered, filters={"phase": ["Inhale"]})))
    for rows, columns in [([], ["condition"]), ([], ["phase", "condition"]),
                          (["phase", "soa_ms"], ["condition"]), (["condition", "phase"], ["soa_ms"])]:
        cases.append(dict(frame="Participant-distance means", settings=dict(rows=rows, columns=columns,
            values=["reaction_time_ms"], aggregation="Mean", totals=False, cohort="Primary behavioural cohort",
            participantSummary=True, filtersEnabled=False)))
    for aggregation in ["Mean", "Minimum", "Maximum", "Standard deviation"]:
        add("benefit-edge", ["soa_ms"], [], ["baseline_benefit_ms"], aggregation)
    for value in ["reaction_time_ms", "baseline_benefit_ms", "reaction_time_norm", "baseline_benefit_norm", "reaction_time_z", "baseline_benefit_z"]:
        for columns in [[], ["condition"], ["phase"], ["condition", "phase"]]:
            for cohort in ["Full release", "Primary behavioural cohort", "Exclude P011", "Exclude P033"]:
                add("Participant-distance means", ["soa_ms"], columns, [value], "Mean",
                    participantSummary=True, totals=False, cohort=cohort)
    for value in ["reaction_time_norm", "baseline_benefit_norm", "reaction_time_z", "baseline_benefit_z"]:
        add("benefit-edge", ["soa_ms"], [], [value], "Mean", participantSummary=True, totals=False)
    add("benefit-edge", [], [], ["baseline_benefit_ms"], "Mean", rawRecords=True)
    payload = dict(frames={name: browser_frame(frame) for name, frame in frames.items()}, cases=cases, snapshots=snapshots)
    payload["frames"]["Participant-distance means"]["normalizers"] = normalization_parameters(frames["All trial records"])
    edge_trials = frames["benefit-edge"].assign(retained_global=True, trial_type="Audio-Tactile")
    payload["frames"]["benefit-edge"]["normalizers"] = normalization_parameters(edge_trials)
    runner = Path(__file__).with_name("check_pivot_javascript.mjs")
    process = subprocess.run([node, str(runner)], input=json.dumps(payload, allow_nan=False), text=True,
                             encoding="utf-8", capture_output=True)
    if process.returncode:
        raise RuntimeError(process.stderr)
    actual = json.loads(process.stdout)
    density = gaussian_kde([0., 1., 4., 9., 16.], bw_method=1.06 * 5 ** (-.2))
    for point in actual["violin"]["points"]:
        assert math.isclose(point["density"], float(density([point["value"]])[0]), rel_tol=1e-12)
    for index, (case, observed) in enumerate(zip(cases, actual["results"], strict=True)):
        settings = case["settings"]
        frame = cohort_frame(frames[case["frame"]], settings["cohort"])
        if not settings.get("rawRecords") and any(value.startswith("baseline_benefit") for value in settings["values"]):
            frame["baseline_benefit_ms"] = (frame.baseline_mean_ms - frame.reaction_time_ms).where(
                frame.corrected_rt_ms.notna())
        for value in [value for value in settings["values"] if value.endswith(("_norm", "_z"))]:
            field = value.rsplit("_", 1)[0] + "_ms"
            trials = frames["All trial records"]
            reference = trials[trials.retained_global & (trials.trial_type == "Audio-Tactile")].copy() if case["frame"] == "Participant-distance means" else frames[case["frame"]].copy()
            reference["baseline_benefit_ms"] = -reference.corrected_rt_ms
            grouped = reference.groupby("participant_id")[field]
            offset = grouped.mean() if value.endswith("_z") else grouped.min()
            scale = grouped.std(ddof=1) if value.endswith("_z") else grouped.max() - grouped.min()
            frame[value] = (frame[field] - frame.participant_id.map(offset)) / frame.participant_id.map(scale).replace(0, float("nan"))
        for field, values in settings.get("seriesFilters", {}).items():
            frame = frame[frame[field].isin(values)]
        if settings["filtersEnabled"]:
            for field, values in settings["filters"].items():
                if values:
                    frame = frame[frame[field].isin(values)]
        source_count = len(frame)
        if settings.get("rawRecords"):
            expected = browser_frame(frame)
            assert observed["rawRecords"] and observed["axisCount"] == 0
            assert observed["columns"] == expected["columns"]
            assert observed["rows"] == expected["rows"]
            assert observed["count"] == source_count
            continue
        if "baseline_benefit_ms" in settings["values"]:
            frame["baseline_benefit_ms"] = (frame.baseline_mean_ms - frame.reaction_time_ms).where(
                frame.corrected_rt_ms.notna())
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
            # Independent per-person records must survive the worker unchanged.
            for row_index, row in enumerate(observed["rows"][:observed["dataRowCount"]]):
                for part in observed["series"]:
                    selected = frame
                    for field, target in zip(settings["rows"] + settings["columns"],
                                             row[:len(settings["rows"])] + part["group"], strict=True):
                        selected = selected[selected[field].isna() if target == "(missing)" else selected[field] == target]
                    records = observed["stats"][row_index][part["column"] - observed["axisCount"]]["observations"]
                    expected_people = selected.sort_values("participant_id")
                    assert [record["participant"] for record in records] == expected_people.participant_id.tolist(), index
                    for record, target in zip(records, expected_people[part["measure"]], strict=True):
                        assert record["value"] is None if pd.isna(target) else math.isclose(record["value"], target, abs_tol=1e-10), index
            for name, aggregation in [("sd", "Standard deviation"), ("n", "Count nonmissing")]:
                expected_stats = browser_frame(pivot_frame(frame, settings["rows"], settings["columns"],
                    settings["values"], aggregation, False))
                for row_index, row in enumerate(expected_stats["rows"]):
                    for column, target in enumerate(row[observed["axisCount"]:]):
                        value = observed["stats"][row_index][column][name]
                        assert target is value if target is None else math.isclose(target, value, rel_tol=1e-10, abs_tol=1e-10), (index, name, target, value)
    assert actual["snapshot"] == browser_frame(frames["snapshot"])
    assert actual["csv"] == '\ufeff"a","b"\r\n"=literal","quote""comma,"\r\n'
    print(f"JavaScript / Python parity: {len(cases)} cases; linked chart cells, combined SOA/condition filters, missingness, totals, CSV and typing pass.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--node", default="node")
    validate(parser.parse_args().node)
