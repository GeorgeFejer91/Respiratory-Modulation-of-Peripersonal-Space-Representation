"""Figures and exports for exploratory individual curves and plateau normalization."""

import io

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

from descriptive_sigmoid import DISTANCES, LABELS, predict
from participant_sigmoid import METRICS, CONTRASTS, X


def repeated_rows(r):
    return [row|{"excluded_ids":','.join(cohort.get("excluded_ids",[])),
                 "cohort":"Exclude "+','.join(cohort["excluded_ids"]) if cohort.get("excluded_ids") else "Full release (provisional)"}
            for cohort in [r]+r["linkage_sensitivities"] for row in cohort["repeated_measures"]]


def repeated_primary(r):
    cohort=max(r["linkage_sensitivities"],key=lambda s:len(s["excluded_ids"])) if r["linkage_sensitivities"] else r
    return cohort["repeated_measures"],"Exclude "+'/'.join(cohort["excluded_ids"]) if cohort.get("excluded_ids") else "Full release"


def repeated_markdown(r):
    if r["status"]!="computed":return ""
    rows,label=repeated_primary(r)
    lines=["\n## PPS parameters: repeated-measures ANOVA and ANCOVA","",r["repeated_measures_scope"],"",
        f"Main presentation: {label}. Sharpness = 1/(4 × width in cm); larger values mean a narrower transition. MAIA dimensions are fitted separately and kept continuous. Spatial delta is Viscereality − Control.","",
        "| Model | Parameter | Effect / covariate | n | Estimate | F (1, df) | Unadjusted p | HC3 p | 95% curve-refit interval |",
        "| --- | --- | --- | ---: | ---: | --- | ---: | ---: | --- |"]
    def f(value):return "NA" if value is None else f"{value:.5g}"
    for a in rows:
        if a["predictor"]!="none" and (a["effect"]!="Condition" or not a["order_adjusted"] or a["predictor"]=="spfrref_change_direction"):continue
        term=a["effect"] if a["predictor"]=="none" else a["effect"]+" × "+a["predictor"]
        lines.append(f"| {a['model']} | {a['parameter']} | {term} | {a['n']} | {f(a['estimate'])} | {f(a['F'])} (1, {a['df2']}) | {f(a['p'])} | {f(a['hc3_p'])} | [{f(a['refit_ci_low'])}, {f(a['refit_ci_high'])}] |")
    lines.extend(["","Conventional F/p and HC3 treat fitted parameters as outcomes. They do not propagate curve fitting or shared-pool uncertainty. Interpret them beside the refit intervals and the previously weak parameter-change reliability. All 1,328 terms, both order specifications, phase/three-way moderators, between-person effects and spatial-direction sensitivities are exported. No multiplicity correction was applied."])
    return "\n".join(lines)+"\n"


def repeated_figure_bytes(r,format="svg"):
    rows,label=repeated_primary(r)
    with plt.rc_context({"font.family":"DejaVu Sans","font.size":9,"svg.hashsalt":"study5-rm-v1"}):
        fig,axes=plt.subplots(2,2,figsize=(13,10.5))
        predictors=list(dict.fromkeys(a["predictor"] for a in rows if a["predictor"] not in ("none","spfrref_change_direction")))
        for column,metric in enumerate(METRICS[:2]):
            for panel in (0,1):
                ax=axes[panel,column];labels=["Condition","Phase","Condition × Phase"] if panel==0 else predictors
                for model,offset,color,name in (("individual_plateaus",-.13,"#175b8d","Separate plateaus"),("shared_plateaus",.13,"#b65121","Shared plateaus")):
                    for i,term in enumerate(labels):
                        a=next(a for a in rows if a["model"]==model and a["parameter"]==metric and
                               ((panel==0 and a["predictor"]=="none" and a["effect"]==term) or
                                (panel==1 and a["predictor"]==term and a["effect"]=="Condition" and a["order_adjusted"])))
                        y=i+offset
                        if a["refit_ci_low"] is not None:ax.plot([a["refit_ci_low"],a["refit_ci_high"]],[y,y],color=color,lw=1.7)
                        if a["estimate"] is not None:ax.plot(a["estimate"],y,"o",color=color,ms=4,label=name if i==0 else None)
                ax.set_yticks(range(len(labels)),[s.replace("maia2_","").replace("spfrref_delta","Spatial change").replace("_"," ").title() for s in labels]);ax.invert_yaxis()
                ax.axvline(0,color="#888888",lw=.8,ls=":");ax.spines[["top","right"]].set_visible(False)
                units="cm" if column==0 else "1/cm"
                ax.set_xlabel(("Fitted contrast ("+units+")") if panel==0 else "Condition-change slope ("+units+" per score point)")
                ax.set_title(("Midpoint" if column==0 else "Normalized sharpness")+(" · 2×2 effects" if panel==0 else " · order-adjusted moderators"))
        axes[0,0].legend(frameon=False,fontsize=8,loc="best")
        fig.suptitle("PPS proxy ANOVA / ANCOVA · "+label,fontsize=14,y=.98)
        fig.text(.5,.035,"Points: fitted contrasts/slopes. Lines: 95% hierarchical curve-refit intervals; method and cleaning fixed.",ha="center",fontsize=9)
        fig.text(.5,.014,"Exploratory associations of unstable proxies; baseline MAIA and post-intervention spatial change do not establish causal influence.",ha="center",fontsize=9)
        fig.subplots_adjust(left=.17,right=.97,top=.91,bottom=.10,wspace=.60,hspace=.45)
        stream=io.BytesIO();fig.savefig(stream,format=format,dpi=250,metadata={"Date":None} if format=="svg" else None);plt.close(fig)
        return stream.getvalue()


def diagnostics(r):
    out=[]
    for model,key in (("individual_plateaus","parameters"),("shared_plateaus","shared_parameters")):
        rows=r[key]
        for metric in METRICS:
            reliability=[a["rho"] for a in r["reliability"] if a["model"]==model and a["parameter"]==metric and a["rho"] is not None]
            for scenario in ("sigmoid","sigmoid_shared_plateaus"):
                recovery=[a[metric+"_recovery_rho"] for a in r["recovery"] if a["model"]==model and a["scenario"]==scenario and a[metric+"_recovery_rho"] is not None]
                out.append(dict(model=model,parameter=metric,scenario=scenario,
                    median_split_half_rho=float(np.median(reliability)) if reliability else None,
                    median_recovery_rho=float(np.median(recovery)) if recovery else None,
                    median_interval_width=float(np.median([a[metric+"_ci_high"]-a[metric+"_ci_low"] for a in rows]))))
    return out


def contrast_diagnostics(r):
    out=[]
    for model in ("individual_plateaus","shared_plateaus"):
        for contrast in CONTRASTS:
            for metric in METRICS:
                values=[a["rho"] for a in r["contrast_reliability"] if a["model"]==model and a["contrast"]==contrast and a["parameter"]==metric and a["rho"] is not None]
                row=dict(model=model,contrast=contrast,parameter=metric,
                    median_split_half_rho=float(np.median(values)) if values else None)
                for scenario in ("sigmoid","sigmoid_shared_plateaus"):
                    key=metric+"_"+contrast+"_recovery_rho"
                    recovered=[a[key] for a in r["recovery"] if a["model"]==model and a["scenario"]==scenario and a.get(key) is not None]
                    row[scenario+"_median_recovery_rho"]=float(np.median(recovered)) if recovered else None
                out.append(row)
    return out


def curve_figure(r,pid):
    data=r["plot_data"];i=data["participant_ids"].index(pid)
    raw=np.asarray(data["raw_means"])[i];se=np.asarray(data["raw_se"])[i]
    pars=np.asarray(data["parameters"])[i];shared=np.asarray(data["shared_parameters"])[i]
    dense=np.linspace(0,1,201);curves=predict(pars,dense);joint=predict(shared,dense)
    rows=[a for a in r["parameters"] if a["participant_id"]==pid]
    flagged=any(pid in group["participant_ids"] for group in r["linkage_audit"]["groups"])
    fig,axes=plt.subplots(2,4,figsize=(14,7.2),sharex=True,sharey="row")
    ylo=min(np.min(raw-se),curves.min(),joint.min());yhi=max(np.max(raw+se),curves.max(),joint.max())
    pad=max(10.,.08*(yhi-ylo))
    for j,((condition,phase),row) in enumerate(zip(LABELS,rows)):
        color="#175b8d" if condition=="Control" else "#b54343";ax,bx=axes[:,j]
        ax.errorbar(DISTANCES,raw[j],yerr=se[j],fmt="o",ms=4,mfc="white",color=color,elinewidth=.9,capsize=2,label="Raw mean ± SE")
        ax.plot(10+90*dense,curves[j],color=color,lw=2,label="Individual plateaus")
        ax.plot(10+90*dense,joint[j],color="#555555",ls="--",lw=1.5,label="Shared plateaus")
        ax.set_title(f"{condition} · {phase}\nm = {row['midpoint_cm']:.1f} cm; s = {row['width_cm']:.1f} cm",fontsize=10)
        ax.set_ylim(ylo-pad,yhi+pad);ax.axvline(row["midpoint_cm"],color=color,alpha=.25,lw=1)
        if abs(pars[j,1])>=1e-6:
            low=min(pars[j,0],pars[j,0]+pars[j,1]);bx.plot(10+90*dense,(curves[j]-low)/abs(pars[j,1]),color=color,lw=2)
        else:bx.text(.5,.5,"Flat: normalization undefined",ha="center",transform=bx.transAxes,fontsize=8)
        if abs(shared[j,1])>=1e-6:
            low=min(shared[j,0],shared[j,0]+shared[j,1]);bx.plot(10+90*dense,(joint[j]-low)/abs(shared[j,1]),color="#555555",ls="--",lw=1.5)
        bx.set_ylim(-.05,1.05);bx.set_yticks([0,.5,1]);bx.axhline(.5,color="#aaaaaa",lw=.7,ls=":")
        bx.set_title("Amplitude interval " + ("excludes zero" if row["normalization_stable"] else "includes zero · unstable scale"),fontsize=8)
        bx.set_xlabel("Nominal distance (cm)");bx.set_xticks([10,50,100])
        for panel in (ax,bx):panel.grid(alpha=.15);panel.spines[["top","right"]].set_visible(False)
    axes[0,0].set_ylabel("Raw reaction time (ms)");axes[1,0].set_ylabel("Normalized fitted geometry\nLower = 0; upper = 1")
    fig.suptitle(f"{pid} · four individual sigmoid approximations"+(" · RECORDING LINKAGE UNRESOLVED" if flagged else ""),fontsize=14,y=.98)
    handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc="upper center",bbox_to_anchor=(.5,.925),ncol=3,frameon=False,fontsize=9)
    fig.text(.5,.075,"Top: observations and fitted RT. Bottom: model geometry only; common 0/1 plateaus are imposed by normalization.",ha="center",fontsize=9)
    fig.text(.5,.035,"S-shaped geometry is constrained. Reversed curves remain reversed. These are provisional proxies, not validated individual PPS boundaries.",ha="center",fontsize=9)
    fig.subplots_adjust(left=.07,right=.985,top=.83,bottom=.16,hspace=.45,wspace=.20)
    return fig


def curve_bytes(r,pid,format="svg"):
    with plt.rc_context({"font.family":"DejaVu Sans","font.size":9,"svg.hashsalt":"study5-individual-v1"}):
        fig=curve_figure(r,pid);stream=io.BytesIO()
        fig.savefig(stream,format=format,dpi=220,metadata={"Date":None} if format=="svg" else None)
        plt.close(fig);return stream.getvalue()


def atlas_bytes(r):
    stream=io.BytesIO()
    with plt.rc_context({"font.family":"DejaVu Sans","font.size":9}):
        with PdfPages(stream,metadata={"Title":"Study 5 individual sigmoid proxies and normalized geometry","CreationDate":None,"ModDate":None}) as pdf:
            for pid in r["plot_data"]["participant_ids"]:
                fig=curve_figure(r,pid);pdf.savefig(fig);plt.close(fig)
    return stream.getvalue()


def diagnostic_figure_bytes(r,format="svg"):
    with plt.rc_context({"font.family":"DejaVu Sans","font.size":10,"svg.hashsalt":"study5-individual-diagnostics-v1"}):
        fig,axes=plt.subplots(2,2,figsize=(12,8))
        scores=r["prediction"]["scores"];ax=axes[0,0]
        labels={"visible":"Visible sigmoid","broad":"Broad sigmoid","linear":"Line","constant":"Constant","shared_plateaus":"Shared plateaus"}
        ax.barh([labels[a["family"]] for a in scores],[a["outer_rmse_ms"] for a in scores],color="#477f9e")
        ax.invert_yaxis();ax.set_xlabel("Omitted-position prediction RMSE (ms)");ax.set_title("Prediction · lower is better")
        ax=axes[0,1]
        for key,color,label in (("parameters","#175b8d","Individual"),("shared_parameters","#b65121","Shared plateaus")):
            widths=[a["midpoint_cm_ci_high"]-a["midpoint_cm_ci_low"] for a in r[key]]
            ax.hist(widths,bins=np.linspace(0,50,11),alpha=.55,color=color,label=label)
        ax.set_xlabel("Midpoint bootstrap interval width (cm)");ax.set_ylabel("Curves");ax.set_title("Conditional midpoint uncertainty");ax.legend(frameon=False,fontsize=9)
        ax=axes[1,0];summary=diagnostics(r)
        for model,color,offset,label in (("individual_plateaus","#175b8d",-.16,"Individual"),("shared_plateaus","#b65121",.16,"Shared plateaus")):
            values=[next(a["median_split_half_rho"] for a in summary if a["model"]==model and a["parameter"]==m) for m in METRICS]
            ax.bar(np.arange(3)+offset,values,.3,color=color,label=label)
        ax.set_xticks(range(3),["Midpoint","Steepness","RT derivative"]);ax.set_ylim(-.2,1);ax.axhline(0,color="#555555",lw=.8)
        ax.set_ylabel("Median split-half Spearman rho");ax.set_title("Individual-difference reliability");ax.legend(frameon=False,fontsize=9)
        ax=axes[1,1]
        main=[a for a in r["associations"] if a["scope"]=="main"]
        shared={(a["x"],a["y"]):a for a in r["shared_associations"]}
        xx=[a["rho"] for a in main];yy=[shared[(a["x"],a["y"])]["rho"] for a in main]
        ax.scatter(xx,yy,s=25,color="#175b8d");ax.plot([-1,1],[-1,1],ls="--",color="#888888",lw=1)
        ax.set(xlim=(-1,1),ylim=(-1,1),xlabel="Correlation · individual plateaus",ylabel="Correlation · shared plateaus",title="27 main links · model sensitivity")
        for ax in axes.ravel():ax.spines[["top","right"]].set_visible(False)
        fig.suptitle("Participant sigmoid diagnostics · provisional recording linkage",fontsize=14,y=.98)
        fig.text(.5,.025,"Shape constraints, smoothing and shared plateaus can produce curves without reliable individual boundaries. All correlation tests are exploratory.",ha="center",fontsize=9)
        fig.subplots_adjust(left=.15,right=.97,top=.90,bottom=.12,wspace=.43,hspace=.42)
        stream=io.BytesIO();fig.savefig(stream,format=format,dpi=250,metadata={"Date":None} if format=="svg" else None);plt.close(fig)
        return stream.getvalue()


def normalized_trials(r,retained):
    by={(a["participant_id"],a["condition"],a["phase"]):a for a in r["parameters"]}
    shared={(a["participant_id"],a["condition"],a["phase"]):a for a in r["shared_parameters"]}
    out=[]
    for row in retained:
        key=(row["participant_id"],row["condition"],row["phase"])
        if row["trial_type"]!="Audio-Tactile" or key not in by:continue
        a,b=by[key],shared[key];rt=float(row["reaction_time_ms"])
        out.append({k:row[k] for k in ("participant_id","trial_id","condition","phase","soa_ms","reaction_time_ms")}|{
            "normalized_rt":(rt-a["lower_plateau_ms"])/abs(a["signed_amplitude_ms"]) if not a["flat"] else None,
            "normalization_stable":a["normalization_stable"],
            "shared_plateau_normalized_rt":(rt-b["lower_plateau_ms"])/abs(b["signed_amplitude_ms"]) if not b["flat"] else None,
            "shared_normalization_stable":b["normalization_stable"]})
    return out


def markdown(r):
    if r["status"]!="computed":return "\n## Individual sigmoid proxies\n\n"+r["reason"]+"\n"
    lines=["\n## Individual sigmoid proxies and normalized RT", "",r["interpretation"],"",
           "**Recording-linkage audit:** "+r["linkage_audit"]["status"]+". "+r["linkage_audit"]["interpretation"],"",
           f"{r['curve_count']} curves; selected method `{r['selected_method']['method']}`. "+r["normalization"],"",
           r["selection_scope"],"",r["uncertainty"],"",
           "| Family | Outer prediction RMSE (ms) |","| --- | ---: |"]
    lines.extend(f"| {a['family']} | {a['outer_rmse_ms']:.3f} |" for a in r["prediction"]["scores"])
    for name,key in (("Individual plateaus","associations"),("Shared-plateau sensitivity","shared_associations")):
        lines.extend(["",f"### {name}: all 27 main contrast associations", "", "Intervals include refitting uncertainty; permutation p values condition on point estimates. All are unadjusted and provisional.","",
                      "| Questionnaire | Parameter difference | n | rho | 95% interval | p |","| --- | --- | ---: | ---: | --- | ---: |"])
        fmt=lambda v:"NA" if v is None else f"{v:.4f}"
        for a in r[key]:
            if a["scope"]=="main":lines.append(f"| {a['x']} | {a['metric']} | {a['n']} | {fmt(a['rho'])} | [{fmt(a['ci_low'])}, {fmt(a['ci_high'])}] | {fmt(a['p'])} |")
    lines.extend(["","All 126 tests per model, all three linkage-exclusion specifications (1,008 tests total), parameter tables, reliability/recovery, normalized trial RTs and a 42-page curve atlas are in the download. Exclusion sensitivities do not determine the correct recording mapping."])
    return "\n".join(lines)+"\n"
