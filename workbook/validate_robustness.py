"""Independent references for linkage models, contrasts and the log benchmark."""

import argparse
import json
import warnings
from pathlib import Path

import numpy as np
from scipy import stats
from scipy.special import expit
import statsmodels.api as sm
from statsmodels.stats.anova import AnovaRM
import pandas as pd

from preparation import FILES, load_pair
from paper_analysis import clean
from descriptive_sigmoid import extract_cells, smooth, DISTANCES


def validate_repeated_parameters(report):
    p=report["participant_sigmoids"];evidence={"anova_terms":0,"ancova_terms":0,"max_F_absolute_error":0.}
    cells=("control_exhale","control_inhale","viscereality_exhale","viscereality_inhale")
    for cohort in [p]+p["linkage_sensitivities"]:
        for model,key in (("individual_plateaus","participant_scores"),("shared_plateaus","shared_participant_scores")):
            records=cohort[key];rows=[a for a in cohort["repeated_measures"] if a["model"]==model]
            assert len(rows)==166
            for metric in ("midpoint_cm","normalized_steepness_per_cm"):
                v=np.array([[r[metric+"_"+c] for c in cells] for r in records])
                outcomes={"Mean across cells":v.mean(1),"Condition":(v[:,2]+v[:,3]-v[:,0]-v[:,1])/2,
                          "Phase":(v[:,1]+v[:,3]-v[:,0]-v[:,2])/2,"Condition × Phase":v[:,3]-v[:,2]-v[:,1]+v[:,0]}
                frame=pd.DataFrame({"person":np.repeat(np.arange(len(records)),4),"Condition":np.tile([0,0,1,1],len(records)),
                                    "Phase":np.tile([0,1,0,1],len(records)),"value":v.ravel()})
                table=AnovaRM(frame,"value","person",within=["Condition","Phase"]).fit().anova_table
                for row in [a for a in rows if a["parameter"]==metric]:
                    field=row["predictor"];y=outcomes[row["effect"]]
                    if field=="none":
                        reference=table.loc[row["effect"].replace(" × ",":")]
                        np.testing.assert_allclose([row["F"],row["p"],row["df1"],row["df2"]],reference[["F Value","Pr > F","Num DF","Den DF"]],rtol=1e-8,atol=1e-7)
                        evidence["anova_terms"]+=1
                        x=np.empty((len(records),0));keep=np.ones(len(records),dtype=bool)
                    else:
                        columns=[np.array([r.get(field) for r in records],dtype=float)]
                        if row["order_adjusted"]:
                            columns.append(np.array([{"Control-Viscereality":0.,"Viscereality-Control":1.}.get(r["condition_order"],np.nan) for r in records]))
                        x=np.column_stack(columns);keep=np.isfinite(x).all(1)
                        evidence["ancova_terms"]+=1
                    design=np.column_stack([np.ones(keep.sum()),x[keep]-x[keep].mean(0)])
                    assert keep.sum()==row["n"] and row["df2"]==len(y[keep])-design.shape[1]
                    if row["status"]!="computed":continue
                    target=0 if field=="none" else 1
                    reference=sm.OLS(y[keep],design).fit();robust=reference.get_robustcov_results(cov_type="HC3",use_t=True)
                    f=float(reference.tvalues[target]**2)
                    np.testing.assert_allclose([row["estimate"],row["se"],row["F"],row["p"],row["ci_low"],row["ci_high"]],
                        [reference.params[target],reference.bse[target],f,reference.pvalues[target],*reference.conf_int()[target]],rtol=1e-8,atol=1e-7)
                    np.testing.assert_allclose([row["hc3_se"],row["hc3_F"],row["hc3_p"],row["hc3_ci_low"],row["hc3_ci_high"]],
                        [robust.bse[target],robust.tvalues[target]**2,robust.pvalues[target],*robust.conf_int()[target]],rtol=1e-8,atol=1e-7)
                    assert row["refit_bootstrap_valid"]>450 and row["refit_ci_low"]<=row["refit_ci_high"]
                    evidence["max_F_absolute_error"]=max(evidence["max_F_absolute_error"],abs(row["F"]-f))
    return evidence


def validate_spatial_parameters(report):
    """Independent ranks, contrast regressions and the equivalent long-format design."""
    p=report["participant_sigmoids"]
    evidence={"cell_correlations":0,"regression_terms":0,"reused_terms":0,"max_long_format_beta_error":0.,"undefined_refit_draws":0}
    cells=("control_exhale","control_inhale","viscereality_exhale","viscereality_inhale")
    for cohort in [p]+p["linkage_sensitivities"]:
        for model,key in (("individual_plateaus","participant_scores"),("shared_plateaus","shared_participant_scores")):
            records=cohort[key]
            for row in [a for a in cohort["spatial_cell_associations"] if a["model"]==model]:
                assert row["x"]=="spfrref_"+row["condition"].lower()+"_ordinal"
                assert row["summary"]==row["condition"].lower()+"_"+row["phase"].lower()
                pairs=np.array([(r[row["x"]],r[row["y"]]) for r in records],dtype=float)
                pairs=pairs[np.isfinite(pairs).all(1)]
                assert len(pairs)==row["n"]
                if row["rho"] is not None:
                    np.testing.assert_allclose(stats.spearmanr(*pairs.T).statistic,row["rho"],atol=1e-12)
                    assert 0<row["p"]<=1
                assert 0<=row["hierarchical_bootstrap_valid"]<=500
                evidence["undefined_refit_draws"]+=500-row["hierarchical_bootstrap_valid"]
                evidence["cell_correlations"]+=1
            ratings=np.array([[r.get("spfrref_control_ordinal"),r.get("spfrref_viscereality_ordinal")] for r in records],dtype=float)
            level=ratings.mean(1);delta=ratings[:,1]-ratings[:,0]
            order=np.array([{"Control-Viscereality":0.,"Viscereality-Control":1.}.get(r["condition_order"],np.nan) for r in records])
            for row in [a for a in cohort["spatial_parameter_models"] if a["model"]==model]:
                values=np.array([[r[row["parameter"]+"_"+cell] for cell in cells] for r in records])
                keep=np.isfinite(ratings).all(1)&np.isfinite(values).all(1)
                if row["order_adjusted"]:keep&=np.isfinite(order)
                v=values[keep];b=level[keep]-level[keep].mean();d=delta[keep]-delta[keep].mean()
                y={"Mean across cells":v.mean(1),"Phase":(v[:,1]+v[:,3]-v[:,0]-v[:,2])/2,
                   "Condition":(v[:,2]+v[:,3]-v[:,0]-v[:,1])/2,"Condition × Phase":v[:,3]-v[:,2]-v[:,1]+v[:,0]}[row["effect"]]
                between=row["predictor"]=="spfrref_mean"
                assert (row["effect"] in ("Mean across cells","Phase"))==between
                columns=[np.ones(len(y)),b if between else d]
                o=order[keep]-order[keep].mean()
                if row["order_adjusted"]:columns.append(o)
                design=np.column_stack(columns)
                assert row["n"]==len(y) and row["df2"]==len(y)-design.shape[1]
                assert 0<=row["refit_bootstrap_valid"]<=500
                if row["status"]=="computed":
                    reference=sm.OLS(y,design).fit();robust=reference.get_robustcov_results(cov_type="HC3",use_t=True)
                    np.testing.assert_allclose([row["estimate"],row["se"],row["F"],row["p"],row["ci_low"],row["ci_high"]],
                        [reference.params[1],reference.bse[1],reference.tvalues[1]**2,reference.pvalues[1],*reference.conf_int()[1]],rtol=1e-8,atol=1e-7)
                    np.testing.assert_allclose([row["hc3_se"],row["hc3_F"],row["hc3_p"],row["hc3_ci_low"],row["hc3_ci_high"]],
                        [robust.bse[1],robust.tvalues[1]**2,robust.pvalues[1],*robust.conf_int()[1]],rtol=1e-8,atol=1e-7)
                    # A balanced long-format within/between model has the same four spatial slopes.
                    c=np.tile([-.5,-.5,.5,.5],len(y));phase=np.tile([-.5,.5,-.5,.5],len(y))
                    bl=np.repeat(b,4);wl=c*np.repeat(d,4)
                    long_columns=[np.ones(len(c)),c,phase,c*phase,bl,bl*phase,wl,wl*phase]
                    if row["order_adjusted"]:
                        ol=np.repeat(o,4);long_columns.extend([ol,ol*c,ol*phase,ol*c*phase])
                    long=sm.OLS(v.ravel(),np.column_stack(long_columns)).fit()
                    target={"Mean across cells":4,"Phase":5,"Condition":6,"Condition × Phase":7}[row["effect"]]
                    error=abs(float(long.params[target])-row["estimate"])
                    np.testing.assert_allclose(long.params[target],row["estimate"],atol=1e-9,rtol=1e-8)
                    evidence["max_long_format_beta_error"]=max(error,evidence["max_long_format_beta_error"])
                if not between:
                    previous=next(a for a in cohort["repeated_measures"] if all(a[k]==row[k] for k in ("model","effect","parameter","predictor","order_adjusted")))
                    assert {k:v for k,v in row.items() if k!="spatial_component"}==previous
                    evidence["reused_terms"]+=1
                evidence["undefined_refit_draws"]+=500-row["refit_bootstrap_valid"]
                evidence["regression_terms"]+=1
    assert (evidence["cell_correlations"],evidence["regression_terms"],evidence["reused_terms"])==(64,128,64)
    return evidence


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
    evidence["parameter_repeated_measures"]=validate_repeated_parameters(report)
    evidence["spatial_parameters"]=validate_spatial_parameters(report)
    evidence["status"]="passed; independent linkage ML, contrast identities, log-distance prediction, geometry, 48 parameter ANOVA terms, 1,280 ANCOVA terms and condition-matched spatial ranks/within-between models"
    evidence["limits"]="Numerical checks do not validate physiology, source identity, interval coverage or method-selection assumptions. Log prediction reuses the already-tested smoother."
    return evidence


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report",type=Path,default=Path("results/browser-analysis/analysis_results.json"))
    parser.add_argument("--output",type=Path,default=Path(".for-ai-local/remaining/independent-validation.json"))
    args=parser.parse_args();result=validate(Path(__file__).resolve().parents[1],json.loads(args.report.read_text()))
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+"\n")
    print(result["status"])
