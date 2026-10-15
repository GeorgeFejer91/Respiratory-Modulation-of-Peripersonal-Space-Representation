"""Independent native validation of the browser engine against statsmodels.

Run from the repository root with requirements-validation.txt installed.
No reference-library result is used by the browser pipeline.
"""

import argparse
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import integrate
from statsmodels.stats.anova import AnovaRM

from inference import cluster_regression,jzs,mixed_ml,repeated_anova
from paper_analysis import clean,cell_cube,design,numeric
from preparation import FILES,load_pair


def validate(root):
    people,trials=load_pair(*[(root/"data"/"raw"/name).read_bytes() for name in FILES])
    retained,_,counts=clean(people,trials)
    evidence={"cohort":counts,"mixed_models":[],"cluster_regression":{},"anova":[],"jzs":[]}
    for control,categorical in ((False,False),(True,False),(False,True)):
        rows=[r for r in retained if r["trial_type"]=="Audio-Tactile" and (not control or r["condition"]=="Control")]
        x,names,_,_=design(rows,control,categorical)
        y=np.array([numeric(r,"reaction_time_ms") for r in rows])
        g=np.array([r["participant_id"] for r in rows])
        for full in (True,False):
            matrix=x if full else x[:,:-(4 if categorical else 1)]
            ours=mixed_ml(matrix,y,g)
            candidates=[]
            for method in ("lbfgs","powell"):
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    fit=sm.MixedLM(y,matrix,groups=g).fit(reml=False,method=method,disp=False)
                if fit.converged and np.isfinite(fit.llf):candidates.append(fit)
            if not candidates:raise AssertionError("No finite independent mixed-model fit.")
            reference=max(candidates,key=lambda f:f.llf)
            error=abs(ours["ll"]-reference.llf)
            coef_error=float(np.max(np.abs(ours["beta"]-reference.fe_params)))
            if error>1e-5 or coef_error>1e-4:raise AssertionError(f"Mixed-model mismatch: {error}, {coef_error}")
            evidence["mixed_models"].append({"control":control,"categorical":categorical,"full":full,
                "ll_error":error,"max_beta_error":coef_error})
        if not control and not categorical:
            ours=cluster_regression(x,y,g,names)
            reference=sm.OLS(y,x).fit(cov_type="cluster",cov_kwds={"groups":g,"use_correction":True},use_t=False)
            b=np.array([r["estimate"] for r in ours["coefficients"]])
            se=np.array([r["se"] for r in ours["coefficients"]])
            np.testing.assert_allclose(b,reference.params,rtol=1e-8,atol=1e-7)
            np.testing.assert_allclose(se,reference.bse,rtol=1e-8,atol=1e-7)
            evidence["cluster_regression"]={"max_beta_error":float(np.max(abs(b-reference.params))),
                "max_se_error":float(np.max(abs(se-reference.bse)))}
    ids,cube=cell_cube(retained)
    frame=pd.DataFrame([{"participant":pid,"condition":c,"phase":p,"soa":s,"rt":cube[i,c,p,s]}
        for i,pid in enumerate(ids) for c in range(2) for p in range(2) for s in range(5)])
    reference=AnovaRM(frame,"rt","participant",within=["condition","phase","soa"]).fit().anova_table
    for ours in repeated_anova(cube):
        key=ours["effect"].lower().replace(" × ",":")
        f_error=abs(ours["F"]-float(reference.loc[key,"F Value"]))
        if f_error>1e-8:raise AssertionError(f"ANOVA mismatch: {key}, {f_error}")
        evidence["anova"].append({"effect":key,"F_error":f_error})
    for t,n in ((.1,40),(2.5,20),(0.,42)):
        def integrand(g):
            factor=1+n*.5*g
            return factor**(-.5)*((1+t*t/(n-1))/(1+t*t/((n-1)*factor)))**(n/2)*g**(-1.5)*np.exp(-1/(2*g))/np.sqrt(2*np.pi)
        value,_=integrate.quad(integrand,0,np.inf,epsabs=1e-9,limit=300)
        error=abs(jzs(t,n)-value)
        if error>1e-7:raise AssertionError("JZS integral mismatch.")
        evidence["jzs"].append({"t":t,"n":n,"error":error})
    rows=[r for r in trials if r["trial_type"]=="Audio-Tactile"]
    x,names,_,_=design(rows)
    y=np.array([float(r["outcome"]=="hit") for r in rows])
    g=np.array([r["participant_id"] for r in rows])
    ours=cluster_regression(x,y,g,names,binomial=True)
    reference=sm.GLM(y,x,family=sm.families.Binomial()).fit(cov_type="cluster",cov_kwds={"groups":g,"use_correction":True})
    b=np.array([r["estimate"] for r in ours["coefficients"]]);se=np.array([r["se"] for r in ours["coefficients"]])
    np.testing.assert_allclose(b,reference.params,rtol=1e-5,atol=1e-6)
    np.testing.assert_allclose(se,reference.bse,rtol=1e-5,atol=1e-6)
    evidence["binomial_cluster"]={"max_beta_error":float(np.max(abs(b-reference.params))),"max_se_error":float(np.max(abs(se-reference.bse)))}
    evidence["status"]="passed independent statsmodels and quadrature validation"
    return evidence


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=Path(".for-ai-local/full-analysis/independent-validation.json"))
    args=parser.parse_args()
    result=validate(Path(__file__).resolve().parents[1])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+"\n")
    print(result["status"])
