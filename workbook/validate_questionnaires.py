"""Independent references for questionnaire statistics in the actual browser report."""

import argparse
import json
from pathlib import Path

import numpy as np
import statsmodels.api as sm
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
    for row in q["associations"]+q["delta_associations"]:
        pairs=[(r[row["x"]],r[row["y"]]) for r in q["scores"] if r[row["x"]] is not None and r[row["y"]] is not None]
        if row["status"]=="computed":
            rho=stats.spearmanr(np.array(pairs)).statistic
            correlation_errors.append(abs(rho-row["rho"]))
    assert q["resampling"]["adjustment"]=="none" and len(q["associations"])==33
    assert all("p_holm" not in r for r in q["associations"])
    assert len(q["delta_associations"])==9 and len(q["moderation"])==16
    source={p["participant_id"]:p for p in people}
    for row in q["scores"]:
        p=source[row["participant_id"]]
        expected=float(p["spfrref_viscereality_ordinal"])-float(p["spfrref_control_ordinal"]) if p["spfrref_viscereality_ordinal"] and p["spfrref_control_ordinal"] else None
        assert row["spfrref_delta"]==expected
    model_errors=[];long_errors=[]
    order_codes={"Control-Viscereality":0.,"Viscereality-Control":1.}
    for row in q["moderation"]:
        adjusted=row["model"]=="order_adjusted"
        records=[p for p in q["scores"] if p[row["field"]] is not None and p["spfrref_delta"] is not None
                 and (not adjusted or p["condition_order"] in order_codes)]
        x=np.array([p[row["field"]] for p in records]);x=x-x.mean()
        y=np.array([p["spfrref_delta"] for p in records]);n=len(y)
        design=np.column_stack([np.ones(n),x])
        if adjusted:
            order=np.array([order_codes[p["condition_order"]] for p in records]);order=order-order.mean()
            design=np.column_stack([design,order])
        fit=sm.OLS(y,design).fit();robust=fit.get_robustcov_results(cov_type="HC3",use_t=True)
        assert row["status"]=="computed" and row["df"]==fit.df_resid
        for key,value in {"beta":fit.params[1],"se":fit.bse[1],"p":fit.pvalues[1],"F":fit.tvalues[1]**2,
                "ci_low":fit.conf_int()[1,0],"ci_high":fit.conf_int()[1,1],"r_squared":fit.rsquared,
                "hc3_se":robust.bse[1],"hc3_p":robust.pvalues[1],
                "hc3_ci_low":robust.conf_int()[1,0],"hc3_ci_high":robust.conf_int()[1,1],
                "max_leverage":fit.get_influence().hat_matrix_diag.max(),
                "max_cook_distance":fit.get_influence().cooks_distance[0].max()}.items():
            model_errors.append(abs(value-row[key]))
        if adjusted:model_errors.append(abs(fit.params[2]-row["order_beta"]))
        condition=np.tile([-.5,.5],n)
        long_x=np.column_stack([np.repeat(np.eye(n),2,axis=0),condition,condition*np.repeat(x,2)])
        if adjusted:long_x=np.column_stack([long_x,condition*np.repeat(order,2)])
        long_y=np.array([[p["spfrref_control_ordinal"],p["spfrref_viscereality_ordinal"]] for p in records]).ravel()
        repeated=sm.OLS(long_y,long_x).fit()
        assert repeated.df_resid==fit.df_resid
        for observed,expected in ((repeated.params[n+1],row["beta"]),(repeated.bse[n+1],row["se"]),
                                  (repeated.tvalues[n+1]**2,row["F"]),(repeated.pvalues[n+1],row["p"])):
            long_errors.append(abs(observed-expected))
    assert max(errors+[sign_error,interval_error]+correlation_errors+model_errors+long_errors)<1e-10
    assert q["scoring"]["mismatches"]==0 and q["scoring"]["matches"]==328
    return {"status":"passed","browser_execution":report["runtime"]["execution"],
            "max_alpha_covariance_identity_error":max(errors),"statsmodels_sign_test_error":sign_error,
            "statsmodels_exact_proportion_interval_error":interval_error,"max_scipy_spearman_error":max(correlation_errors),
            "association_adjustment":"none","associations_checked":len(correlation_errors),
            "moderation_models_checked":len(q["moderation"]),"max_statsmodels_ols_hc3_error":max(model_errors),
            "max_long_format_interaction_error":max(long_errors),
            "scope":"Covariance alpha identity; independent statsmodels sign test and beta interval; 42 SciPy rank correlations; 16 OLS/HC3 fits and long-format participant-intercept Condition × MAIA interaction equivalence. Exhaustive tied-permutation reference and missing/range edge cases are unit-tested. No multiple-testing correction. These checks do not validate the administered anchor key or preregistration wording."}


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report",type=Path,default=Path("results/browser-analysis/analysis_results.json"))
    parser.add_argument("--output",type=Path,default=Path(".for-ai-local/full-analysis/questionnaire-validation.json"))
    args=parser.parse_args()
    evidence=validate(args.report)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(evidence,indent=2)+"\n")
    print(evidence["status"])
