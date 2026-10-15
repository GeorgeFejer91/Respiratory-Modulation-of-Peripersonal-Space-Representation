"""Compare an actual browser report to a separately computed native report."""

import argparse
import json
from hashlib import sha256
from pathlib import Path


def compare(native_path, browser_directory):
    n=json.loads(native_path.read_text())
    b=json.loads((browser_directory/"analysis_results.json").read_text())
    if n["runtime"]["execution"]!="native validation" or b["runtime"]["execution"]!="browser Pyodide":
        raise AssertionError("Two separately executed runtimes are required.")
    if n["cohort"]!=b["cohort"]:
        raise AssertionError("Cohort mismatch.")
    out={"browser_zip_sha256":sha256((browser_directory/"browser-results.zip").read_bytes()).hexdigest(),
         "native_runtime":n["runtime"],"browser_runtime":b["runtime"],"models":[],"sigmoid_diagnostics":[]}
    for a,z in zip(n["mixed_models"]+n["missing_rt_stress"],b["mixed_models"]+b["missing_rt_stress"]):
        if a["name"]!=z["name"] or a["status"]!=z["status"]:
            raise AssertionError("Model/status mismatch.")
        ll=max(abs(a[k]-z[k]) for k in ("ll_full","ll_reduced"))
        beta=max(abs(u["estimate"]-v["estimate"]) for u,v in zip(a["coefficients"],z["coefficients"]))
        if ll>1e-5 or beta>1e-4:
            raise AssertionError("Mixed-model cross-runtime tolerance exceeded.")
        out["models"].append({"name":a["name"],"max_log_likelihood_error":ll,"max_coefficient_error":beta})
    for a,z in zip(n["sigmoid_summary"],b["sigmoid_summary"]):
        if (a["axis"],a["level"],a["r2_pass_cells"])!=(z["axis"],z["level"],z["r2_pass_cells"]):
            raise AssertionError("Participant sigmoid gate mismatch.")
        out["sigmoid_diagnostics"].append({"axis":a["axis"],"level":a["level"],
            "r2_pass_cells":a["r2_pass_cells"],"native_bound_hits":a["bound_hit_cells"],"browser_bound_hits":z["bound_hit_cells"]})
    numeric_errors=[]

    def walk(a,z):
        if isinstance(a,dict):
            if a.keys()!=z.keys():raise AssertionError("Descriptive field mismatch.")
            for k in a:walk(a[k],z[k])
        elif isinstance(a,list):
            if len(a)!=len(z):raise AssertionError("Descriptive list length mismatch.")
            for u,v in zip(a,z):walk(u,v)
        elif isinstance(a,(int,float)) and not isinstance(a,bool):
            numeric_errors.append(abs(a-z))
            if abs(a-z)>1e-8:raise AssertionError("Descriptive numeric mismatch.")
        elif a!=z:
            raise AssertionError("Descriptive label/status mismatch.")

    walk(n["descriptive_sigmoids"],b["descriptive_sigmoids"])
    out["descriptive_sigmoids"]={"candidate_count":b["descriptive_sigmoids"]["candidate_count"],
        "bootstrap_draws":b["descriptive_sigmoids"]["bootstrap_draws"],
        "numeric_values_compared":len(numeric_errors),"max_absolute_numeric_error":max(numeric_errors),
        "scope":"Every descriptive result value, including all candidates, intervals, comparisons, sensitivity and prediction bands"}
    out["status"]="passed; identical cohort and gate pass counts; model tolerances 1e-5/1e-4; every descriptive value within 1e-8; legacy nonlinear-bound diagnostics may differ"
    return out


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("native_report",type=Path)
    parser.add_argument("--browser-directory",type=Path,default=Path("results/browser-analysis"))
    parser.add_argument("--output",type=Path,default=Path(".for-ai-local/full-analysis/browser-native-parity.json"))
    args=parser.parse_args()
    evidence=compare(args.native_report,args.browser_directory)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(evidence,indent=2)+"\n")
    print(evidence["status"])
