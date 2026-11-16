"""Validate the ex-Gaussian attempt grid and combine matched held-probe scores."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from exponential_tail import LOCAL, MODELS, SHAPES
from screen import OUT, ROOT, cohort_mask, load_data


def inventory():
    ids, rt, _, input_audit = load_data()
    cohort = cohort_mask(ids, "primary40")
    participants = ids[cohort].tolist()
    counts = np.isfinite(rt[cohort]).sum(axis=(0, 1, 3))
    expected = {(model, "observed", held) for model in MODELS for held in (None, *range(5))}
    expected.update({("tail", "flat", None), ("tail", "shift", None)})
    attempts = {key: {} for key in expected}
    pilots = []
    for path in sorted(LOCAL.glob("*.json")):
        item = json.loads(path.read_text(encoding="utf8"))
        if item["input"]["input_sha256"] != input_audit["input_sha256"]:
            raise ValueError(f"Mismatched input release in {path.name}")
        key = (item["model"], item["scenario"], item["held_probe_index"])
        if key not in expected:
            raise ValueError(f"Unexpected model, scenario or probe in {path.name}")
        size = (item["chains"], item["warmup"], item["draws"])
        record = dict(receipt=path.name, sha256=hashlib.sha256(path.read_bytes()).hexdigest(), **item)
        if size == (2, 300, 150) and not item["diagnostic_pass"] and key == ("tail", "observed", None):
            pilots.append(record)
            continue
        if size not in {(4, 1500, 1500), (4, 3000, 6000)}:
            raise ValueError(f"Unexpected sampling budget in {path.name}")
        if item.get("participant_order") != participants:
            raise ValueError(f"Mismatched participant order in {path.name}")
        if key[2] is not None:
            prediction = item["held_predictions"]
            if (prediction["target_trials"] != counts[key[2]]
                    or not np.isfinite(prediction["log_score_per_trial"])):
                raise ValueError(f"Invalid held prediction in {path.name}")
        required = {"trial_mu", "trial_tau", "core_sd"}
        if key[0] in SHAPES:
            required.update(("midpoint_cm", "width_cm"))
        if set(item["diagnostics"]) != required:
            raise ValueError(f"Incomplete target diagnostics in {path.name}")
        verified = (item["divergences"] == 0
                    and all(values["max_rhat"] is not None and values["max_rhat"] <= 1.01
                            and min(values["min_bulk"], values["min_tail"]) >= 400
                            for values in item["diagnostics"].values()))
        if verified != item["diagnostic_pass"]:
            raise ValueError(f"Diagnostic gate mismatch in {path.name}")
        if size in attempts[key]:
            raise ValueError(f"Duplicate fit at the same sampling budget in {path.name}")
        attempts[key][size] = record

    ordered = sorted(expected, key=lambda key: (key[0], key[1], -1 if key[2] is None else key[2]))
    missing, incomplete, failed, selected = [], [], [], {}
    for key in ordered:
        grid = attempts[key]
        first = grid.get((4, 1500, 1500))
        extension = grid.get((4, 3000, 6000))
        if first is None:
            missing.append(key)
            continue
        if first["diagnostic_pass"]:
            selected[key] = first
        elif extension is None:
            incomplete.append(key)
        elif extension["diagnostic_pass"]:
            selected[key] = extension
        else:
            failed.append(key)

    held = []
    for model in MODELS:
        folds = [selected.get((model, "observed", index)) for index in range(5)]
        if all(folds):
            scores = [fold["held_predictions"]["log_score_per_trial"] for fold in folds]
            held.append(dict(model=model, target_trials=int(counts.sum()),
                             log_score_per_trial=float(np.average(scores, weights=counts)),
                             probe_scores=scores, receipts=[fold["receipt"] for fold in folds]))
    sources = [ROOT / "analysis/boundary_methods/exponential_tail.py", ROOT / "analysis/boundary_methods/screen.py",
               ROOT / "analysis/baseline_effects/requirements.txt", OUT / "EXPONENTIAL_TAIL_SPECIFICATION.md"]
    return dict(input=input_audit, held_trial_counts=counts.tolist(), pilots=pilots,
                attempts=[a for key in ordered for a in attempts[key].values()],
                pending_initial_fits=missing, pending_extensions=incomplete,
                failed_after_extension=failed, held=held,
                sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in [Path(__file__), *sources]})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = inventory()
    print(f"{len(result['attempts'])} full-budget attempts; "
          f"{len(result['pending_initial_fits'])} missing initial fits; "
          f"{len(result['pending_extensions'])} pending extensions; "
          f"{len(result['failed_after_extension'])} failed after extension; "
          f"{len(result['held'])} complete held comparisons.")
    if args.write:
        if result["pending_initial_fits"] or result["pending_extensions"]:
            raise SystemExit("Complete the declared attempts before freezing the report.")
        (OUT / "exponential_tail_inventory.json").write_text(
            json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf8", newline="\n")
