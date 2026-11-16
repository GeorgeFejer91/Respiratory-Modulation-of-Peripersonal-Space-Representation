"""Assemble matched held-probe and recovery results from qualified fit receipts."""

import hashlib
import json
from pathlib import Path

import numpy as np

from hierarchy_geometry import LOCAL
from screen import DISTANCES, OUT, ROOT, cohort_mask, load_data, write_csv

MODELS = ("constant","linear","log_distance","full","shared_width","reduced_condition",
          "reduced_condition_width","shared_contrasts","shared_location")
RECOVERY_MODELS = ("reduced_condition","reduced_condition_width")
GENERATORS = ("flat","weak_shared_width","shared_width","heterogeneous_width")


def assemble():
    ids, trials, _, audit = load_data()
    count = np.isfinite(trials[cohort_mask(ids,"primary40")]).sum(axis=(0,1,3))
    inventory, held, observed, recovery = [], [], [], []
    for path in sorted(LOCAL.glob("*.json")):
        item = json.loads(path.read_text(encoding="utf8"))
        if item["input"]["input_sha256"] != audit["input_sha256"] or item["cohort_size"] != 40:
            raise ValueError(f"Mismatched release or cohort in {path.name}")
        source = dict(receipt=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        calibration = item.get("calibration","pooled_marginal")
        tags = dict(model=item["model"],calibration=calibration,prior_scale=item["prior_scale"],
                    warmup=item["tune"],draws=item["draws"],chains=item["chains"],
                    diagnostic_pass=item["diagnostic_pass"],divergences=item["divergences"])
        inventory.append(dict(source,**tags,held_probe_index=item["held_distance"],
                              fit_definition_sha256=item["local_definition_sha256"],
                              target_diagnostics=item["target_diagnostics"]))
        if item["held_distance"] is not None and calibration == "pooled_marginal" and item["prior_scale"] == 1:
            i = item["held_distance"]
            scores = item["held_predictions"]
            if scores.get("target_trials",count[i]) != count[i]:
                raise ValueError(f"Held trial count differs in {path.name}")
            held.append(dict(tags,receipt=path.name,probe_index=i,distance_cm=DISTANCES["registered"][i],
                             **dict(scores,target_trials=count[i])))
        elif "recovery" in item:
            recovery.append(dict(tags,receipt=path.name,**item["recovery"]))
        elif item["held_distance"] is None and "population_condition_phase_interaction_cm" in item:
            observed.append(dict(tags,receipt=path.name,**{k:v for k,v in item.items()
                                 if k.endswith("_cm") or k.endswith("_ms") or "fraction_inside" in k}))

    comparison, missing = [], []
    for model in MODELS:
        choices = []
        for i in range(5):
            fits = [r for r in held if r["model"]==model and r["probe_index"]==i and r["diagnostic_pass"]]
            if fits:
                choices.append(max(fits,key=lambda r:r["draws"]))
            else:
                missing.append([model,i])
        if len(choices) == 5:
            scores = [r["log_score_per_trial"] for r in choices]
            rmse = {k:float(np.sqrt(np.mean([r[k]**2 for r in choices])))
                    for k in ("rmse_individual_ms","rmse_group_ms")}
            comparison.append(dict(model=model,held_trials=int(count.sum()),
                                   held_log_score=float(np.average(scores,weights=count)),**rmse,
                                   selected_receipts=json.dumps([r["receipt"] for r in choices])))

    synthesis = []
    for model in RECOVERY_MODELS:
        for case in GENERATORS:
            attempts = [r for r in recovery if r["model"]==model and r["scenario"]==case]
            qualified = [r for r in attempts if r["diagnostic_pass"]]
            if len({r["replicate"] for r in attempts})!=len(attempts):
                raise ValueError("Multiple attempts for the same recovery seed need an explicit selection rule.")
            row = dict(model=model,scenario=case,attempts=len(attempts),qualified=len(qualified))
            if case != "flat" and qualified:
                cols = ("individual_midpoint_interval_fraction","individual_midpoint_rmse_cm",
                        "individual_effect_rmse_cm","population_effects_covered")
                row.update({k:np.mean([r[k] for r in qualified],axis=0).tolist() for k in cols})
            synthesis.append(row)

    probes_path = OUT/"hierarchy_held_probes.csv"
    prediction_path = OUT/"hierarchy_prediction.csv"
    write_csv(probes_path,held)
    write_csv(prediction_path,comparison)
    sources = Path(__file__).parent
    files = [Path(__file__),sources/"reduced_hierarchy.py", sources/"hierarchy_geometry.py",
             ROOT/"analysis/baseline_effects/joint_pps.py", OUT/"HIERARCHY_SPECIFICATION.md",
             probes_path,prediction_path,OUT/"hierarchy_group_peaks.csv",
             OUT/"hierarchy_participant_midpoints.csv",OUT/"hierarchy_recovery_geometry.csv"]
    (OUT/"hierarchy_fit_inventory.json").write_text(json.dumps(dict(
        input=audit,inventory=inventory,observed=observed,missing_qualified_folds=missing,
        recovery_runs=recovery,recovery_summary=synthesis,
        sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
        ),indent=2,allow_nan=False)+"\n",encoding="utf8",newline="\n")
    print(f"{len(comparison)} complete predictive families. Missing qualified folds {missing}.")


if __name__ == "__main__":
    assemble()
