"""Portable publication companion report, SVG figures and reproducibility ZIP."""

import csv
import io
import json
import math
import zipfile
from hashlib import sha256
from html import escape
from pathlib import Path

import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.special import expit

from preparation import FILES,TRIAL_COLUMNS,encode_csv


def as_table(rows):
    fields=list(dict.fromkeys(key for row in rows for key,value in row.items() if not isinstance(value,(dict,list))))
    stream=io.StringIO(newline="")
    writer=csv.DictWriter(stream,fieldnames=fields,extrasaction="ignore")
    writer.writeheader();writer.writerows(rows)
    return stream.getvalue().encode()


def primary_summary(report):
    c=report["cohort"];m=report["mixed_models"][0]
    term=m["coefficients"][-1]
    gate=next(r for r in report["sigmoid_summary"] if r["axis"]=="registered" and r["level"]=="trials")
    return {"participants":c["participants_input"],"retained_at":c["retained_at"],
        "retained_baseline":c["retained_baseline"],"lr":m["lr"],"p":m["p"],
        "estimate":term["estimate"],"ci_low":term["ci_low"],"ci_high":term["ci_high"],
        "sigmoid_pass":gate["r2_pass_cells"],"sigmoid_cells":gate["cells"],
        "r2_ceiling":gate["max_trial_r2_ceiling"]}


def markdown_report(report):
    s=primary_summary(report);c=report["cohort"]
    def value_or_missing(value):
        return "unidentified" if value is None else f"{value:.2f}"
    lines=["# Study 5 · Reproducible publication companion analysis", "",
        report["status"],"",
        f"The released dataset contains {s['participants']} independent participants and {c['trial_rows_input']:,} observed trials "
        f"of {c['planned_trials']:,} planned slots. The primary participant-wide mean ±2.5 sample-SD trim removed {c['removed_2_5_sd']:,} "
        f"recorded hits, retaining {s['retained_at']:,} Audio–Tactile and {s['retained_baseline']:,} Baseline RTs. "
        f"There were {c['missing_hit_rt']} hit-labelled trials without RT ({c['missing_at_hit_rt']} Audio–Tactile).", "",
        "## Primary question", "",
        f"The Condition × Phase × numeric SOA random-intercept ML comparison gives χ²(1)={s['lr']:.6f}, p={s['p']:.6f}. "
        f"The interaction is {s['estimate']:.6f} ms per SOA SD, model-based 95% Wald CI [{s['ci_low']:.6f}, {s['ci_high']:.6f}]. "
        "A non-significant result does not establish equivalence or a zero effect.","",
        "## Mixed-model comparisons", "", "| Comparison | Participants | LR | df | p | Status |", "| --- | ---: | ---: | ---: | ---: | --- |"]
    for m in report["mixed_models"]+report["missing_rt_stress"]:
        lines.append(f"| {m['name']} | {m.get('participants','')} | {m.get('lr',float('nan')):.6g} | {m.get('df','')} | {m.get('p',float('nan')):.6g} | {m['status']} |")
    lines += ["", "## Sigmoid viability", "",
        f"{s['sigmoid_pass']}/{s['sigmoid_cells']} registered-axis trial cells satisfy R²≥.70. "
        f"The maximum saturated five-SOA trial-level R² ceiling is {s['r2_ceiling']:.6f}. "
        "Any deterministic curve depending only on these SOAs is bounded by this ceiling, independently of sigmoid parameter bounds. "
        "Boundary/MAIA/SpFrRef inference remains gated when participant fits are not interpretable. Group and five-mean fits are descriptive.","",
        "## Supplementary participant contrasts", "", "| Contrast | n | Estimate (ms) | 95% CI | p | Holm p |", "| --- | ---: | ---: | --- | ---: | ---: |"]
    for r in report["supplementary_contrasts"]:
        if r["status"]=="computed":lines.append(f"| {r['name']} | {r['n']} | {r['estimate']:.4f} | [{r['ci_low']:.4f}, {r['ci_high']:.4f}] | {r['p']:.6g} | {r.get('p_holm',float('nan')):.6g} |")
    d=report["descriptive_sigmoids"]
    if d["status"]=="computed":
        lines += ["", "## Four uniformly estimated descriptive sigmoids", "",
            f"Selected from {d['candidate_count']} pipelines: `{d['selected_method']}`. "
            f"Tuning shape RMSE {d['selected_tuning_rmse_ms']:.3f} ms; linear benchmark "
            f"{d['validation']['linear_shape_rmse_ms']:.3f} ms; constant benchmark {d['validation']['constant_shape_rmse_ms']:.3f} ms. "
            "These are post hoc selection scores, not an independent test of sigmoid superiority. "
            "The fits describe the extracted RT summary; winsorized summaries need not equal raw means.", "",
            "| Condition / phase | Midpoint (cm) | Width (cm) | RT slope at midpoint (ms/cm) | Conditional midpoint interval (cm) | Flat bootstrap draws |",
            "| --- | ---: | ---: | ---: | --- | ---: |"]
        for r in d["parameters"]:
            lines.append(f"| {r['condition']} / {r['phase']} | {r['midpoint_cm']:.2f} | {r['width_cm']:.2f} | {r['midpoint_slope_ms_per_cm']:.4f} | [{value_or_missing(r['midpoint_cm_conditional_bootstrap_low'])}, {value_or_missing(r['midpoint_cm_conditional_bootstrap_high'])}] | {r['bootstrap_flat_fraction']:.1%} |")
        lines += ["", d["parameter_definitions"]+".", "", d["bootstrap_scope"], "",
            "Only five positions were sampled. Full S-shaped extrapolations and asymptotes are model assumptions. "
            "The report includes all candidate scores and parameters, a fixed robust reference, trajectory-axis and expanded-bound sensitivity, and paired descriptive comparisons."]
    lines += ["", "## Interpretation and unavailable provenance", "", *[f"- {r}" for r in report["interpretation"]+report["unavailable_checks"]],"",
        "## Reproducibility", "",f"Runtime: {json.dumps(report['runtime'],sort_keys=True)}", "",
        "The result ZIP contains model and diagnostic tables, participant QC, cell/curve summaries, sigmoid fits, the retained RT table, SVG figures, and the full JSON report. "
        "The manifest records exact input/output hashes. Primary models always use the fixed analysis contract and are independent of the preparation preview controls."]
    return "\n".join(lines)+"\n"


def figure_bytes(report,measure,format="svg"):
    if measure in ("descriptive_sigmoids","sigmoid_extrapolation"):
        return sigmoid_figure_bytes(report,format,extrapolate=measure=="sigmoid_extrapolation")
    data=[r for r in report["group_curves"] if r["measure"]==measure]
    title="Audio–Tactile reaction time by SOA" if measure=="raw_at" else "AT minus Baseline at the same nominal SOA label"
    subtitle=f"Participant-weighted means and pointwise 95% t intervals · {report['cohort']['participants_input']} participants"
    with plt.rc_context({"font.size":10,"font.family":"DejaVu Sans","svg.hashsalt":"study5-companion-v1", "axes.spines.top":False,"axes.spines.right":False}):
        fig,ax=plt.subplots(figsize=(9.6,5.1),dpi=200)
        for condition,color in (("Control","#2563a6"),("Viscereality","#c94c50")):
            for phase,style in (("Exhale","-"),("Inhale","--")):
                rows=sorted([r for r in data if r["condition"]==condition and r["phase"]==phase],key=lambda r:r["soa_ms"])
                x=[r["soa_ms"] for r in rows];y=[r["mean_ms"] for r in rows]
                error=[[r["mean_ms"]-r["ci_low"] for r in rows],[r["ci_high"]-r["mean_ms"] for r in rows]]
                ax.errorbar(x,y,yerr=error,color=color,linestyle=style,marker="o",markersize=4,
                    capsize=3,linewidth=1.5,label=f"{condition} / {phase}")
        ax.set(xlabel="Nominal SOA (ms)",ylabel="Reaction time (ms)",xticks=[300,800,1500,2200,2700])
        ax.grid(axis="y",alpha=.2);ax.legend(frameon=False,ncol=2,fontsize=9)
        if measure!="raw_at":ax.axhline(0,color="0.5",linestyle=":",linewidth=1)
        fig.suptitle(title,fontsize=14,y=.98)
        fig.text(.5,.91,subtitle,ha="center",fontsize=9)
        if measure!="raw_at":fig.text(.5,.025,"Same nominal label does not establish matched cue time. Lines connect means; no sigmoid inference.",ha="center",fontsize=8)
        fig.subplots_adjust(top=.85,bottom=.15,left=.1,right=.97)
        stream=io.BytesIO()
        fig.savefig(stream,format=format,dpi=300,metadata={"Date":None,"Creator":"Study 5 marimo publication companion"} if format=="svg" else None)
        plt.close(fig)
        return stream.getvalue()


def figure_svg(report,measure):
    return figure_bytes(report,measure).decode("utf-8")


def sigmoid_figure_bytes(report,format="svg",extrapolate=False):
    d=report["descriptive_sigmoids"]
    if d["status"]!="computed":
        raise ValueError("Descriptive sigmoid figure requires a complete analysis.")
    colors=["#2563a6","#2563a6","#c94c50","#c94c50"]
    with plt.rc_context({"font.size":10,"font.family":"DejaVu Sans","svg.hashsalt":"study5-sigmoids-v1","axes.spines.top":False,"axes.spines.right":False}):
        fig,axes=plt.subplots(2,2,figsize=(10,7.6),dpi=200,sharex=True)
        for j,(ax,r,color) in enumerate(zip(axes.flat,d["parameters"],colors)):
            x=np.array(d["display_distance_cm"])
            if extrapolate:
                extended=np.linspace(0,220,400)
                y=r["lower_asymptote_ms"]+r["amplitude_ms"]*expit((extended-r["midpoint_cm"])/r["width_cm"])
                ax.plot(extended,y,color=color,linestyle="--",alpha=.7,label="Model extrapolation")
                ax.axvspan(10,100,color="#dfe6e9",alpha=.55,label="Sampled range")
            else:
                ax.fill_between(x,d["pointwise_bootstrap_low_ms"][j],d["pointwise_bootstrap_high_ms"][j],color=color,alpha=.12,label="95% pointwise bootstrap")
            ax.scatter(d["distances_cm"],d["raw_points_ms"][j],facecolors="none",edgecolors="#777777",s=30,label="Raw mean")
            ax.scatter(d["distances_cm"],d["extracted_points_ms"][j],color="#222222",s=22,label="Extracted summary",zorder=4)
            ax.scatter(d["distances_cm"],d["smoothed_points_ms"][j],color=color,marker="x",s=30,label="Kernel-smoothed summary",zorder=4)
            ax.plot(x,d["predictions_ms"][j],color=color,lw=2,label="Selected logistic")
            ax.axvline(r["midpoint_cm"],color=color,lw=.8,linestyle=":")
            ax.set_title(f"{r['condition']} · {r['phase']}\nm = {r['midpoint_cm']:.1f} cm; width = {r['width_cm']:.1f} cm",fontsize=11)
            ax.set(xlabel="Nominal distance (cm)",ylabel="Reaction time summary (ms)")
            ax.grid(axis="y",alpha=.15)
        handles,labels=axes.flat[0].get_legend_handles_labels()
        fig.legend(handles,labels,loc="lower center",ncol=3,fontsize=8,bbox_to_anchor=(.5,.025))
        fig.suptitle("Four descriptive sigmoid approximations"+(" · extrapolation" if extrapolate else ""),fontsize=15,y=.98)
        fig.text(.5,.935,f"One uniform extraction/smoothing rule · {d['participants']} participants · five observed positions per curve",ha="center",fontsize=9)
        fig.text(.5,.008,"Dashed extensions are model predictions outside the sampled range." if extrapolate else "Bands condition on the selected pipeline; group curves do not establish individual PPS boundaries.",ha="center",fontsize=8)
        fig.subplots_adjust(top=.84,bottom=.19,left=.09,right=.98,hspace=.5,wspace=.27)
        stream=io.BytesIO()
        fig.savefig(stream,format=format,dpi=300,metadata={"Date":None,"Creator":"Study 5 marimo publication companion"} if format=="svg" else None)
        plt.close(fig)
        return stream.getvalue()


def result_bundle(report,retained,sources):
    files={"analysis_report.md":markdown_report(report).encode(),
        "analysis_results.json":json.dumps(report,indent=2,allow_nan=False).encode(),
        "retained_rt_trials.csv":encode_csv(TRIAL_COLUMNS,retained),
        "raw_at_curves.svg":figure_svg(report,"raw_at").encode(),
        "same_label_facilitation.svg":figure_svg(report,"same_label_at_minus_baseline").encode()}
    d=report["descriptive_sigmoids"]
    if d["status"]=="computed":
        for measure in ("descriptive_sigmoids","sigmoid_extrapolation"):
            files[measure+".svg"]=figure_svg(report,measure).encode()
        for key in ("parameters","comparisons","candidates"):
            files["descriptive_sigmoid_"+key+".csv"]=as_table(d[key])
    for key in ("participant_quality","supplementary_contrasts","sigmoid_summary","sigmoid_fits",
                "repeated_measures_anova","group_curves","order_sensitivities","questionnaire_descriptives",
                "group_sigmoid_descriptions"):
        files[key+".csv"]=as_table(report[key])
    model_rows=[];coefficient_rows=[]
    for category in ("mixed_models","cluster_models","missing_rt_stress"):
        for model in report[category]:
            model_rows.append(dict(model,category=category))
            coefficient_rows.extend(dict(row,model=model["name"],category=category) for row in model.get("coefficients",[]))
    files["models.csv"]=as_table(model_rows);files["coefficients.csv"]=as_table(coefficient_rows)
    source_code={name:(Path(__file__).resolve().parent/name).read_bytes() for name in ("inference.py","paper_analysis.py","preparation.py","publication_report.py","descriptive_sigmoid.py")}
    files.update({"analysis_source/"+name:content for name,content in source_code.items()})
    manifest={"analysis_version":report["analysis_version"],"status":report["status"],
        "source_sha256":dict(zip(FILES,[sha256(b).hexdigest() for b in sources])),
        "artifact_sha256":{name:sha256(data).hexdigest() for name,data in files.items()},
        "runtime":report["runtime"],"contract":"workbook/ANALYSIS_PLAN.md",
        "code_sha256":{name:sha256(content).hexdigest() for name,content in source_code.items()},
        "preview_filters_affect_paper_analysis":False}
    files["manifest.json"]=json.dumps(manifest,indent=2).encode()
    buffer=io.BytesIO()
    with zipfile.ZipFile(buffer,"w",compression=zipfile.ZIP_DEFLATED) as archive:
        for name,content in files.items():
            info=zipfile.ZipInfo(name,(2026,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            archive.writestr(info,content)
    return buffer.getvalue(),manifest
