"""Independent references for questionnaire statistics in the actual browser report."""

import argparse
import json
from pathlib import Path

import numpy as np
from scipy import stats
from statsmodels.stats.descriptivestats import sign_test
from statsmodels.stats.proportion import proportion_confint

from preparation import load_pair, local_release_pair


def validate(report_path):
    report=json.loads(report_path.read_text())
    q=report["questionnaires"]
    people,_=load_pair(*local_release_pair())
    # Independent covariance identity, using the instrument's published item map.
    blocks=[range(1,5),range(5,11),range(11,16),range(16,23),range(23,28),range(28,32),range(32,35),range(35,38)]
    errors=[]
    for row,block in zip(q["scales"],blocks):
        raw=np.array([[float(p[f"maia2_item_{i:02d}"]) for i in block]
                      for p in people if all(p[f"maia2_item_{i:02d}"]!="" for i in block)])
        signs=np.array([-1 if i in (5,6,7,8,9,10,11,12,15) else 1 for i in block])
        covariance=np.cov(raw*signs,rowvar=False,ddof=1)
        k=len(block)
        mean_variance=np.trace(covariance)/k
        mean_covariance=(covariance.sum()-np.trace(covariance))/(k*(k-1))
        expected=k*mean_covariance/(mean_variance+(k-1)*mean_covariance)
        errors.append(abs(expected-row["alpha"]))
    pairs=[(int(p["spfrref_viscereality_ordinal"]),int(p["spfrref_control_ordinal"]))
           for p in people if p["spfrref_viscereality_ordinal"] and p["spfrref_control_ordinal"]]
    differences=np.array([v-c for v,c in pairs])
    _,p=sign_test(differences)
    sign_error=abs(p-q["spatial"]["p"])
    lo,hi=proportion_confint(np.sum(differences>0),np.sum(differences!=0),method="beta")
    interval_error=max(abs(lo-q["spatial"]["higher_fraction_ci_low"]),abs(hi-q["spatial"]["higher_fraction_ci_high"]))
    correlation_errors=[]
    for row in q["associations"]:
        pairs=[(r[row["x"]],r[row["y"]]) for r in q["scores"] if r[row["x"]] is not None and r[row["y"]] is not None]
        if row["status"]=="computed":
            rho=stats.spearmanr(np.array(pairs)).statistic
            correlation_errors.append(abs(rho-row["rho"]))
    assert q["resampling"]["adjustment"]=="none" and len(q["associations"])==33
    assert all("p_holm" not in r for r in q["associations"])
    assert max(errors+[sign_error,interval_error]+correlation_errors)<1e-10
    assert q["scoring"]["mismatches"]==0 and q["scoring"]["matches"]==328
    return {"status":"passed","browser_execution":report["runtime"]["execution"],
            "max_alpha_covariance_identity_error":max(errors),"statsmodels_sign_test_error":sign_error,
            "statsmodels_exact_proportion_interval_error":interval_error,"max_scipy_spearman_error":max(correlation_errors),
            "association_adjustment":"none","associations_checked":len(correlation_errors),
            "scope":"Covariance alpha identity; independent statsmodels sign test and beta interval; SciPy rank correlations. Exhaustive tied-permutation reference and missing/range edge cases are unit-tested. All 33 associations are retained with unadjusted p values. These checks do not validate the administered anchor key or preregistration wording."}


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report",type=Path,default=Path("results/browser-analysis/analysis_results.json"))
    parser.add_argument("--output",type=Path,default=Path(".for-ai-local/full-analysis/questionnaire-validation.json"))
    args=parser.parse_args()
    evidence=validate(args.report)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(evidence,indent=2)+"\n")
    print(evidence["status"])
