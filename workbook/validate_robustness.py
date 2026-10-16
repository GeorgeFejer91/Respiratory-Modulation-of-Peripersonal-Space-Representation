"""Independent references for linkage models, contrasts and the log benchmark."""

import argparse
import json
import warnings
from pathlib import Path

import numpy as np
from scipy import stats
from scipy.special import expit
import statsmodels.api as sm

from preparation import FILES, load_pair
from paper_analysis import clean
from descriptive_sigmoid import extract_cells, smooth, DISTANCES


def validate(root,report):
    people,trials=load_pair(*[(root/"data/raw"/name).read_bytes() for name in FILES])
    evidence={"mixed_models":[],"contrasts_checked":0,"geometry_checks":0}
    for cohort in report["robustness"]["recording_linkage"]:
        drop=cohort["excluded_ids"]
        roster=[p for p in people if p["participant_id"] not in drop]
        retained,_,counts=clean(roster,[r for r in trials if r["participant_id"] not in drop])
        assert counts==cohort["cohort"]
        for model in cohort["mixed_models"]:
            control=model["name"].startswith("Control-only");categorical="categorical" in model["name"]
            rows=[r for r in retained if r["trial_type"]=="Audio-Tactile" and (not control or r["condition"]=="Control")]
            soa=np.array([float(r["soa_ms"]) for r in rows]);z=(soa-soa.mean())/soa.std(ddof=1)
            c=np.array([.5 if r["condition"]=="Viscereality" else -.5 for r in rows])
            p=np.array([.5 if r["phase"]=="Inhale" else -.5 for r in rows])
            basis=[(soa==s).astype(float) for s in (800,1500,2200,2700)] if categorical else [z]
            columns=[np.ones(len(rows)),p,*basis,*[p*b for b in basis]] if control else [
                np.ones(len(rows)),c,p,*basis,c*p,*[c*b for b in basis],*[p*b for b in basis],*[c*p*b for b in basis]]
            x=np.column_stack(columns);y=np.array([float(r["reaction_time_ms"]) for r in rows])
            groups=np.array([r["participant_id"] for r in rows]);ll=[];maximum_error=0.
            for full in (True,False):
                matrix=x if full else x[:,:-(4 if categorical else 1)];candidates=[]
                for method in ("lbfgs","powell"):
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        fit=sm.MixedLM(y,matrix,groups=groups).fit(reml=False,method=method,disp=False)
                    if fit.converged and np.isfinite(fit.llf):candidates.append(fit)
                assert candidates,"No converged independent reference"
                reference=max(candidates,key=lambda f:f.llf);ll.append(reference.llf)
                error=abs(reference.llf-model["ll_full" if full else "ll_reduced"])
                assert error<1e-5;maximum_error=max(maximum_error,error)
                if full:
                    np.testing.assert_allclose(reference.fe_params,[a["estimate"] for a in model["coefficients"]],atol=1e-4,rtol=0)
            np.testing.assert_allclose(stats.chi2.sf(max(0,2*(ll[0]-ll[1])),4 if categorical else 1),model["p"],atol=1e-6,rtol=0)
            evidence["mixed_models"].append(dict(excluded_ids=drop,name=model["name"],max_log_likelihood_error=maximum_error))
    p=report["participant_sigmoids"]
    cohorts=[p]+p["linkage_sensitivities"]
    cells=("control_exhale","control_inhale","viscereality_exhale","viscereality_inhale")
    for cohort in cohorts:
        for row in cohort["contrasts"]:
            records=cohort["shared_participant_scores" if row["model"]=="shared_plateaus" else "participant_scores"]
            v=np.array([[r[row["parameter"]+"_"+c] for c in cells] for r in records])
            if row["contrast"]=="condition_delta":delta=(v[:,2]+v[:,3]-v[:,0]-v[:,1])/2
            elif row["contrast"]=="phase_delta":delta=(v[:,1]+v[:,3]-v[:,0]-v[:,2])/2
            else:delta=v[:,3]-v[:,2]-v[:,1]+v[:,0]
            np.testing.assert_allclose(delta.mean(),row["estimate"],atol=1e-10)
            np.testing.assert_allclose(delta.std(ddof=1),row["between_record_sd"],atol=1e-10)
            assert row["ci_low"]<=row["ci_high"] and row["bootstrap_draws"]==500
            evidence["contrasts_checked"]+=1
        for key in ("associations","shared_associations"):
            assert all(a["hierarchical_bootstrap_valid"]>450 for a in cohort[key] if a["rho"] is not None)
    g=report["robustness"]["group_shape"]
    retained,_,_=clean(people,trials)
    ids,cubes,_=extract_cells([r for r in retained if r["participant_id"] not in g["excluded_ids"]])
    x=(DISTANCES-10)/90;errors=np.zeros((len(ids),4,5))
    for fold in g["prediction"]["outer_folds"]:
        test=np.array([ids.index(pid) for pid in fold["test_participant_ids"]]);train=np.setdiff1d(np.arange(len(ids)),test)
        method=fold["methods"]["logarithmic"]["selected_method"]
        aggregation,kind,strength,_=method.split("/")
        for j in range(5):
            keep=np.arange(5)!=j;y=cubes[aggregation][train].mean(0)[:,keep]
            ys=smooth(x[keep],y,kind,float(strength))
            design=np.column_stack([np.ones(4),np.log(DISTANCES[keep])])
            coefficients=np.linalg.lstsq(design,ys.T,rcond=None)[0]
            pred=np.array([1,np.log(DISTANCES[j])])@coefficients-y.mean(1)
            target=cubes["mean"][test,:,j]-cubes["mean"][test][:,:,keep].mean(2)
            errors[test,:,j]=(target-pred)**2
    score=next(a for a in g["prediction"]["scores"] if a["family"]=="logarithmic")
    np.testing.assert_allclose(errors.mean((1,2)),score["per_participant_mse"],atol=1e-8,rtol=0)
    evidence["log_distance_rmse_error"]=abs(float(np.sqrt(errors.mean()))-score["outer_rmse_ms"])
    for spec in g["geometry_sensitivities"]:
        if spec["status"]!="computed":continue
        rules=spec["criteria_values"]
        for row in spec["parameters"]:
            midpoint=row["midpoint_cm"];width=row["width_cm"];q=expit((DISTANCES-midpoint)/width)
            dense=np.linspace(10,100,181);curve=expit((dense-midpoint)/width)
            design=np.column_stack([np.ones(len(dense)),dense]);residual=curve-design@np.linalg.lstsq(design,curve,rcond=None)[0]
            assert q[0]<=rules["tail"]+1e-10 and q[-1]>=1-rules["tail"]-1e-10
            assert sum(DISTANCES<midpoint)>=rules["flank_positions"] and sum(DISTANCES>midpoint)>=rules["flank_positions"]
            assert np.any((q>=rules["central_fraction"])&(q<=1-rules["central_fraction"]))
            assert np.max(abs(residual))/np.ptp(curve)>=rules["departure_min"]-1e-10
            assert width>=spec["width_floor_cm"]-1e-10
            evidence["geometry_checks"]+=1
    evidence["status"]="passed; 12 independent full/reduced ML comparisons, 72 contrast identities, log-distance least-squares prediction and all feasible geometry constraints"
    evidence["limits"]="Numerical checks do not validate physiology, source identity, interval coverage or method-selection assumptions. Log prediction reuses the already-tested smoother."
    return evidence


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report",type=Path,default=Path("results/browser-analysis/analysis_results.json"))
    parser.add_argument("--output",type=Path,default=Path(".for-ai-local/remaining/independent-validation.json"))
    args=parser.parse_args();result=validate(Path(__file__).resolve().parents[1],json.loads(args.report.read_text()))
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+"\n")
    print(result["status"])
