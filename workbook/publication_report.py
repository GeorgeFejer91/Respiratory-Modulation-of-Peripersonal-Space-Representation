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
from participant_report import (markdown as participant_markdown, curve_bytes,
    diagnostic_figure_bytes, atlas_bytes, normalized_trials, diagnostics, contrast_diagnostics)


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
    def value_or_missing(value, digits=2):
        return "unidentified" if value is None else f"{value:.{digits}f}"
    lines=["# Study 5 · Reproducible publication companion analysis", "",
        report["status"],"",
        f"The released dataset contains {s['participants']} participant records and {c['trial_rows_input']:,} observed trials "
        f"of {c['planned_trials']:,} planned slots. The primary participant-wide mean ±2.5 sample-SD trim removed {c['removed_2_5_sd']:,} "
        f"recorded hits, retaining {s['retained_at']:,} Audio–Tactile and {s['retained_baseline']:,} Baseline RTs. "
        f"There were {c['missing_hit_rt']} hit-labelled trials without RT ({c['missing_at_hit_rt']} Audio–Tactile).", "",
        "**Recording-linkage review:** "+report["participant_sigmoids"].get("linkage_audit",{}).get("status","unavailable")+". Check the recording audit before interpreting behavioural inference and RT–questionnaire links; questionnaire-only results are separate.", "",
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
        "Boundary inference and its MAIA/SpFrRef associations remain gated when participant fits are not interpretable. Group and five-mean fits are descriptive.","",
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
        a=d["shape_audit"]
        lines += ["", "## Visible PPS-like shape: stronger exploratory audit", "", a["criteria"], "",
            f"Original pipelines satisfying the criterion in all four curves: {a['original_candidates_with_four_visible_transitions']}/{d['candidate_count']}. "
            f"Shape-constrained selection: `{a['visible_method']}`; tuning RMSE {a['visible_tuning_rmse_ms']:.3f} ms. "
            f"Fair tuned line: `{a['linear_method']}`; tuning RMSE {a['linear_tuning_rmse_ms']:.3f} ms.", "",
            "| Prediction family | Nested outer RMSE (ms) |", "| --- | ---: |"]
        lines.extend(f"| {r['family']} | {r['outer_rmse_ms']:.3f} |" for r in a["nested_prediction"]["scores"])
        lines += ["",a["nested_prediction"]["scope"],"",a["interpretation"],"",
            "The four imposed-shape midpoint/width estimates, constraint hits and conditional intervals are exported separately. "
            "Raw-mean curvature tests assess any nonlinearity, not sigmoid shape; see their exported statistics and assumptions. "
            "Evaluate empirical support separately from the imposed geometry."]
    q=report["questionnaires"];s=q["spatial"]
    lines += ["", "## MAIA-2 and spatial frame of reference: exploratory", "",
        f"{q['maia_complete']}/{q['participants']} participants have all 37 MAIA-2 items. "
        f"All eight dimensions were recomputed: {q['scoring']['matches']} stored scores matched; {q['scoring']['mismatches']} mismatched. "
        "Subscale means require all constituent items. Blank responses remain missing; no MAIA total was formed.", "",
        "| MAIA-2 dimension | n | Mean | SD | Alpha | Pointwise 95% alpha interval |",
        "| --- | ---: | ---: | ---: | ---: | --- |"]
    for r in q["scales"]:
        lines.append(f"| {r['label']} | {r['n']} | {value_or_missing(r['mean'])} | {value_or_missing(r['sd'])} | {value_or_missing(r['alpha'])} | [{value_or_missing(r['alpha_ci_low'])}, {value_or_missing(r['alpha_ci_high'])}] |")
    lines += ["", "Alpha is a sample internal-consistency diagnostic, not evidence of validity or a basis for deleting items.", "",
        f"Spatial-frame paired ratings: n={s['n_pairs']}; Viscereality higher={s['higher']}, lower={s['lower']}, tied={s['ties']}. "
        f"Two-sided exact sign-test p={s['p'] if s['p'] is not None else 'not estimable'}; ties are excluded only from the binomial denominator. "
        f"Higher fraction among non-ties={value_or_missing(s['higher_fraction_non_ties'])}, exact 95% CI "
        f"[{value_or_missing(s['higher_fraction_ci_low'])}, {value_or_missing(s['higher_fraction_ci_high'])}]. "
        "This is an exploratory ordinal condition comparison. The administered anchor key is unavailable; higher codes are not automatically labelled allocentric.", "",
        q["administration"], "",
        "### Main follow-up: numerical spatial change", "",
        "Delta = post-Viscereality code minus post-Control code, independent of presentation order. "
        f"Mean={value_or_missing(s['delta_descriptives']['mean'])}, SD={value_or_missing(s['delta_descriptives']['sd'])}, "
        f"median={value_or_missing(s['delta_descriptives']['median'])}. These differences assume comparable category steps.", "",
        "| Pre-experiment MAIA-2 dimension | n | Spearman rho with delta | Pointwise 95% interval | Unadjusted permutation p |",
        "| --- | ---: | ---: | --- | ---: |"]
    labels={r["field"]:r["label"] for r in q["scales"]}
    for r in q["delta_associations"][:8]:
        lines.append(f"| {labels[r['x']]} | {r['n']} | {value_or_missing(r['rho'])} | [{value_or_missing(r['ci_low'])}, {value_or_missing(r['ci_high'])}] | {value_or_missing(r['p'],5)} |")
    lines += ["", "### Condition × MAIA moderation", "", q["delta_analysis"]["model"], "",
        "| MAIA-2 dimension | Model | n | Slope | F(1,df) | df | Classical p | HC3 95% interval | HC3 p |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |"]
    for r in q["moderation"]:
        lines.append(f"| {labels[r['field']]} | {r['model']} | {r['n']} | {value_or_missing(r['beta'])} | {value_or_missing(r['F'])} | {r['df']} | {value_or_missing(r['p'],5)} | [{value_or_missing(r['hc3_ci_low'])}, {value_or_missing(r['hc3_ci_high'])}] | {value_or_missing(r['hc3_p'],5)} |")
    lines += ["", q["delta_analysis"]["scope"], "", q["delta_analysis"]["comparison_count"], "",
        "The eight direction-only associations are ordinal sensitivities; all 33 earlier associations remain in the supplementary download. "
        "The behavioural correlate is a raw-RT SOA-slope interaction, not a sigmoid boundary. " + q["resampling"]["scope"], "",
        *["- "+r for r in q["limitations"]], "", "## Coverage of released data", "",
        "| Domain | Status | Output |", "| --- | --- | --- |",
        *[f"| {r['domain']} | {r['status']} | {r['output']} |" for r in report["data_coverage"]]]
    lines += ["", "## Interpretation and unavailable provenance", "", *[f"- {r}" for r in report["interpretation"]+report["unavailable_checks"]],"",
        "## Reproducibility", "",f"Runtime: {json.dumps(report['runtime'],sort_keys=True)}", "",
        "The result ZIP contains model and diagnostic tables, participant QC, cell/curve summaries, sigmoid fits, the retained RT table, SVG figures, and the full JSON report. "
        "The manifest records exact input/output hashes. Primary models always use the fixed analysis contract and are independent of the preparation preview controls."]
    return "\n".join(lines)+"\n"+participant_markdown(report["participant_sigmoids"])+robustness_markdown(report)


def robustness_markdown(report):
    r=report["robustness"];g=r["group_shape"];p=report["participant_sigmoids"]
    if p["status"]!="computed":return "\n## Remaining-analysis checks\n\nIndividual proxies unavailable: "+p["reason"]+"\n"
    lines=["\n## Remaining-analysis robustness checks", "",
           "Post-results amendment: all specifications were fixed before this extension. Exclusions preserve the original CSVs and cannot resolve recording identity.","",
           "| Excluded records | Comparison | n records | LR p (unadjusted) |", "| --- | --- | ---: | ---: |"]
    for s in r["recording_linkage"]:
        for m in s["mixed_models"]:
            lines.append(f"| {', '.join(s['excluded_ids'])} | {m['name']} | {m.get('participants','NA')} | {m.get('p',float('nan')):.5f} |")
    lines.extend(["","### Cohort mean fitted-parameter contrasts","",
        "Pointwise 95% intervals resample people (linked records together) and trials and refit both models. They condition on the selected method and cleaning. These are model-dependent proxies, not validated PPS boundaries.","",
        "| Cohort | Plateau model | Contrast | Parameter | Mean | 95% refit interval |",
        "| --- | --- | --- | --- | ---: | --- |"])
    for label,rows in [("Full release",p["contrasts"])]+[("Exclude "+','.join(s['excluded_ids']),s['contrasts']) for s in p['linkage_sensitivities']]:
        for a in rows:
            lines.append(f"| {label} | {a['model']} | {a['contrast']} | {a['parameter']} | {a['estimate']:.4f} | [{a['ci_low']:.4f}, {a['ci_high']:.4f}] |")
    lines.extend(["","### Reliability of the changes used in correlations","",
        "| Model | Parameter change | Median split-half rho | Recovery rho: cell-specific / shared baseline truth |",
        "| --- | --- | ---: | --- |"])
    for a in contrast_diagnostics(p):
        if a["contrast"]=="condition_delta":
            lines.append(f"| {a['model']} | {a['parameter']} | {a['median_split_half_rho']:.3f} | {a['sigmoid_median_recovery_rho']:.3f} / {a['sigmoid_shared_plateaus_median_recovery_rho']:.3f} |")
    if g["status"]=="computed":
        lines.extend(["","### Group shape comparison without ambiguous recordings","",g["interpretation"],"",
                      "| Family | Outer prediction RMSE (ms) |","| --- | ---: |"])
        lines.extend(f"| {a['family']} | {a['outer_rmse_ms']:.3f} |" for a in g["prediction"]["scores"])
        lines.extend(["",f"All nine geometry specifications and {len(g['selection_resamples'])} repeated-selection draws are exported. The repeated selections chose {len(g['selection_frequencies'])} distinct methods. No preferred appearance was selected after inspection.","",
            "Remaining evidence limits: recording-to-person mapping, waveforms and breathing traces, acquisition timing, independent dense-distance validation, serial-dependence calibration and method-selection-adjusted interval coverage remain unavailable or unestablished."])
    return "\n".join(lines)+"\n"


def robustness_figure_bytes(report,format="svg"):
    with plt.rc_context({"font.family":"DejaVu Sans","font.size":9,"svg.hashsalt":"study5-remaining-v1"}):
        fig,axes=plt.subplots(2,2,figsize=(12,8.5));r=report["robustness"];p=report["participant_sigmoids"]
        models=[("Full release",report["mixed_models"][0])]+[("Exclude "+'/'.join(s["excluded_ids"]),s["mixed_models"][0]) for s in r["recording_linkage"]]
        ax=axes[0,0]
        for i,(label,m) in enumerate(models):
            c=m["coefficients"][-1];scale=1000/m["soa_sd_ms"]
            ax.plot([c["ci_low"]*scale,c["ci_high"]*scale],[i,i],color="#175b8d")
            ax.plot(c["estimate"]*scale,i,"o",color="#175b8d")
        ax.set_yticks(range(len(models)),[a[0] for a in models]);ax.invert_yaxis();ax.axvline(0,color="#777777",lw=.8,ls=":")
        ax.set_title("Primary RT interaction · linkage sensitivities");ax.set_xlabel("Condition × Phase × SOA (ms per 1 s SOA)\nModel-based 95% intervals")
        ax=axes[0,1];scores=r["group_shape"]["prediction"]["scores"]
        labels={"logistic":"Broad sigmoid","visible":"Visible sigmoid","linear":"Linear","logarithmic":"Log distance","constant":"Constant"}
        ax.barh([labels[a["family"]] for a in scores],[a["outer_rmse_ms"] for a in scores],color="#477f9e");ax.invert_yaxis()
        ax.set_title("Group prediction · exclude both records");ax.set_xlabel("Nested omitted-position RMSE (ms)")
        ax=axes[1,0];summary=contrast_diagnostics(p)
        metrics=("midpoint_cm","normalized_steepness_per_cm","midpoint_slope_ms_per_cm")
        for model,offset,color,label in (("individual_plateaus",-.16,"#175b8d","Separate plateaus"),("shared_plateaus",.16,"#b65121","Shared plateaus")):
            values=[next(a["median_split_half_rho"] for a in summary if a["model"]==model and a["contrast"]=="condition_delta" and a["parameter"]==m) for m in metrics]
            ax.bar(np.arange(3)+offset,values,.3,color=color,label=label)
        ax.set_xticks(range(3),["Midpoint Δ","Steepness Δ","RT slope Δ"]);ax.set_ylim(-.4,1);ax.axhline(0,color="#777777",lw=.8)
        ax.set_title("Condition-change rank reliability · full release");ax.set_ylabel("Median split-half Spearman rho");ax.legend(frameon=False,fontsize=8)
        ax=axes[1,1];labels=[];j=0
        both=next((s for s in p["linkage_sensitivities"] if len(s["excluded_ids"])>1),None)
        for cohort,rows in [("Full release",p["contrasts"])]+([("Exclude both",both["contrasts"])] if both else []):
            for a in rows:
                if a["contrast"]!="condition_delta" or a["parameter"]!="midpoint_cm":continue
                shared=a["model"]=="shared_plateaus";color="#b65121" if shared else "#175b8d"
                ax.plot([a["ci_low"],a["ci_high"]],[j,j],color=color);ax.plot(a["estimate"],j,"o",color=color)
                labels.append(cohort+"\n"+("Shared" if shared else "Separate"));j+=1
        ax.set_yticks(range(j),labels);ax.invert_yaxis();ax.axvline(0,color="#777777",lw=.8,ls=":")
        ax.set_title("Mean fitted-midpoint change");ax.set_xlabel("Viscereality − Control (cm)\n95% conditional refit intervals")
        for ax in axes.ravel():ax.spines[["top","right"]].set_visible(False)
        fig.suptitle("Remaining-analysis checks · post hoc specifications",fontsize=14,y=.98)
        fig.text(.5,.025,"Exclusions do not identify the correct recording mapping. Fitted parameter changes remain model-dependent proxies.",ha="center",fontsize=9)
        fig.subplots_adjust(left=.17,right=.97,top=.90,bottom=.13,wspace=.56,hspace=.55)
        stream=io.BytesIO();fig.savefig(stream,format=format,dpi=250,metadata={"Date":None} if format=="svg" else None);plt.close(fig)
        return stream.getvalue()


def figure_bytes(report,measure,format="svg"):
    if measure=="remaining_robustness":return robustness_figure_bytes(report,format)
    if measure=="participant_diagnostics":
        return diagnostic_figure_bytes(report["participant_sigmoids"],format)
    if measure=="participant_example":
        r=report["participant_sigmoids"]
        return curve_bytes(r,r["plot_data"]["participant_ids"][0],format)
    if measure=="spatial_change":
        return spatial_change_figure_bytes(report,format)
    if measure in ("questionnaire_summary", "questionnaire_associations"):
        return questionnaire_figure_bytes(report,format,associations=measure=="questionnaire_associations")
    if measure in ("pps_shape","sigmoid_geometry"):
        return shape_figure_bytes(report,format,normalized=measure=="sigmoid_geometry")
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
        fig,axes=plt.subplots(2,2,figsize=(10,7.6),dpi=200,sharex=True,sharey=True)
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


def shape_figure_bytes(report,format="svg",normalized=False):
    d=report["descriptive_sigmoids"];a=d["shape_audit"]
    x=np.array(d["display_distance_cm"]);observed=np.array(d["distances_cm"])
    with plt.rc_context({"font.size":10,"font.family":"DejaVu Sans","svg.hashsalt":"study5-pps-shape-v1",
                         "axes.spines.top":False,"axes.spines.right":False}):
        fig,axes=plt.subplots(2,2,figsize=(10,8),sharex=True,sharey=True)
        for j,(ax,r) in enumerate(zip(axes.flat,a["visible_parameters"])):
            color="#2563a6" if r["condition"]=="Control" else "#c94c50"
            if normalized:
                original=d["parameters"][j]
                if not original["flat_unidentified"]:
                    ax.plot(x,expit((x-original["midpoint_cm"])/original["width_cm"]),color=".5",ls="--",lw=1.5,label="Original best-score sigmoid")
                if not r["flat_unidentified"]:
                    ax.plot(x,expit((x-r["midpoint_cm"])/r["width_cm"]),color=color,lw=2.5,label="Shape-constrained sigmoid")
                else:
                    ax.text(.5,.5,"Flat fit: normalized shape unidentified",transform=ax.transAxes,ha="center",fontsize=8)
                ax.axhspan(.1,.9,color=".9",alpha=.5,zorder=-2,label="10–90% transition")
                ax.set(ylim=(-.05,1.05),yticks=[0,.1,.5,.9,1],ylabel="Fraction of fitted asymptotic change")
            else:
                center=np.mean(a["visible_points_ms"][j])
                ax.fill_between(x,a["visible_centered_bootstrap_low_ms"][j],a["visible_centered_bootstrap_high_ms"][j],color=color,alpha=.13,label="95% conditional bootstrap")
                raw=np.array(d["raw_points_ms"][j]);points=np.array(a["visible_points_ms"][j])
                ax.scatter(observed,raw-raw.mean(),facecolors="none",edgecolors=".4",s=35,label="Raw means, centered",zorder=4)
                ax.scatter(observed,points-center,color=".15",s=23,label="Extracted means, centered",zorder=4)
                ax.plot(x,np.array(a["linear_predictions_ms"][j])-np.mean(a["linear_points_ms"][j]),color=".5",ls="--",label="Tuned linear benchmark")
                ax.plot(x,np.array(a["visible_predictions_ms"][j])-center,color=color,lw=2.5,label="Shape-constrained sigmoid")
                ax.axhline(0,color=".8",lw=.6,zorder=-2)
                ax.set(ylabel="Centered reaction time (ms)")
            ax.axvline(r["midpoint_cm"],color=color,ls=":",lw=.8)
            flag="*" if r["width_at_bound"] or r["midpoint_at_sampling_limit"] else ""
            ax.set_title(f"{r['condition']} · {r['phase']}\nm = {r['midpoint_cm']:.1f} cm; width = {r['width_cm']:.1f} cm{flag}",fontsize=11)
            ax.set(xlim=(7,103),xticks=observed,xlabel="Nominal distance (cm)")
            ax.grid(axis="y",alpha=.15)
        handles,labels=axes.flat[0].get_legend_handles_labels()
        fig.legend(handles,labels,loc="lower center",ncol=3,fontsize=8,bbox_to_anchor=(.5,.027))
        fig.suptitle("PPS-shaped approximations · imposed-shape sensitivity",fontsize=15,y=.98)
        fig.text(.5,.94,"Model geometry only · amplitude normalized; no observations on this scale" if normalized else
                 f"{d['participants']} participants · five observed positions · same axes and uniform processing for every curve",ha="center",fontsize=9)
        fig.text(.5,.008,"* Width or midpoint reaches a constraint. Visible S shapes are imposed; assess empirical support separately.",ha="center",fontsize=8)
        fig.subplots_adjust(top=.84,bottom=.19,left=.10,right=.98,hspace=.48,wspace=.25)
        stream=io.BytesIO()
        fig.savefig(stream,format=format,dpi=300,metadata={"Date":None,"Creator":"Study 5 marimo publication companion"} if format=="svg" else None)
        plt.close(fig)
        return stream.getvalue()


def spatial_change_figure_bytes(report,format="svg"):
    q=report["questionnaires"]
    with plt.rc_context({"font.size":10,"font.family":"DejaVu Sans","svg.hashsalt":"study5-spatial-change-v1",
                         "axes.spines.top":False,"axes.spines.right":False}):
        fig,(ax,bx)=plt.subplots(1,2,figsize=(12,6.8),sharey=True)
        for i,r in enumerate(q["delta_associations"][:8]):
            if r["rho"] is not None:
                if r["ci_low"] is not None:ax.hlines(i,r["ci_low"],r["ci_high"],color="#195b8d",linewidth=2)
                ax.scatter(r["rho"],i,color="#195b8d",s=35,zorder=3)
        for model,offset,color,label in (("unadjusted",-.12,"#195b8d","MAIA only"),
                                         ("order_adjusted",.12,"#b65121","With presentation order")):
            for i,r in enumerate([r for r in q["moderation"] if r["model"]==model]):
                if r["beta"] is not None:
                    if r["hc3_ci_low"] is not None:bx.hlines(i+offset,r["hc3_ci_low"],r["hc3_ci_high"],color=color,linewidth=2)
                    bx.scatter(r["beta"],i+offset,color=color,s=28,zorder=3,label=label if i==0 else None)
        ax.set_yticks(range(8),[r["label"] for r in q["scales"]]);ax.invert_yaxis()
        ax.set_xlim(-1,1);ax.set_xlabel("Spearman rho with numerical delta")
        ax.set_title("Main correlations · bootstrap 95% intervals",pad=14)
        bx.set_xlabel("Condition × MAIA slope\nSpatial-code steps per MAIA point")
        bx.set_title("Moderation · HC3 95% intervals",pad=14)
        for panel in (ax,bx):panel.axvline(0,color="#808080",linestyle="--",linewidth=1);panel.grid(axis="x",alpha=.15)
        handles,labels=bx.get_legend_handles_labels()
        if handles:fig.legend(handles,labels,loc="center",bbox_to_anchor=(.70,.15),ncol=2,fontsize=9,frameon=False)
        fig.suptitle("Pre-experiment interoception and post-intervention spatial change",y=.97,fontsize=14)
        fig.text(.5,.085,"Delta = post-Viscereality code minus post-Control code. Positive values indicate higher Viscereality codes.",ha="center",fontsize=9)
        fig.text(.5,.035,"Exploratory, unadjusted inference; intervals are pointwise. Numerical category steps assume comparable spacing.",ha="center",fontsize=9)
        fig.subplots_adjust(left=.18,right=.98,top=.85,bottom=.28,wspace=.20)
        stream=io.BytesIO()
        fig.savefig(stream,format=format,dpi=300,metadata={"Date":None,"Creator":"Study 5 marimo publication companion"} if format=="svg" else None)
        plt.close(fig)
        return stream.getvalue()


def questionnaire_figure_bytes(report,format="svg",associations=False):
    q=report["questionnaires"]
    with plt.rc_context({"font.size":10,"font.family":"DejaVu Sans","svg.hashsalt":"study5-questionnaires-v1",
                         "axes.spines.top":False,"axes.spines.right":False}):
        if associations:
            fig,ax=plt.subplots(figsize=(10.5,6.1))
            matrix=np.array([r["rho"] if r["rho"] is not None else np.nan for r in q["associations"][:32]]).reshape(8,4)
            im=ax.imshow(matrix,cmap="RdBu_r",vmin=-1,vmax=1,aspect="auto")
            for i in range(8):
                for j in range(4):
                    ax.text(j,i,f"{matrix[i,j]:.2f}" if np.isfinite(matrix[i,j]) else "NA",ha="center",va="center",color="black" if abs(matrix[i,j])<.6 else "white")
            ax.set_yticks(range(8),[r["label"] for r in q["scales"]])
            ax.set_xticks(range(4),["Control\nrating", "Viscereality\nrating", "Rating change\ndirection", "RT slope\ninteraction"])
            fig.colorbar(im,ax=ax,label="Spearman rho",fraction=.04,pad=.04)
            fig.suptitle("Supplementary: earlier MAIA-2 associations with ratings and behaviour",y=.96,fontsize=14)
            final=q["associations"][-1]
            rho="NA" if final["rho"] is None else f"{final['rho']:.3f}"
            fig.text(.5,.08,f"Additional comparison: rating-change direction vs RT slope interaction, rho = {rho}.",ha="center",fontsize=9)
            fig.text(.5,.035,"All 33 exploratory comparisons are exported with pointwise intervals and unadjusted p values.",ha="center",fontsize=9)
            fig.subplots_adjust(left=.24,right=.93,top=.86,bottom=.21)
        else:
            fig,(ax,bx)=plt.subplots(1,2,figsize=(12,5.8),gridspec_kw={"width_ratios":[1.15,1.]})
            for i,r in enumerate(q["scales"]):
                values=[p[r["field"]] for p in q["scores"] if p[r["field"]] is not None]
                ax.scatter(values,i+np.linspace(-.13,.13,len(values)),color="#507494",alpha=.32,s=12)
                if r["mean"] is not None and r["mean_ci_low"] is not None:
                    ax.hlines(i,r["mean_ci_low"],r["mean_ci_high"],color="#173f62",linewidth=2)
                    ax.scatter([r["mean"]],[i],color="#173f62",s=35,zorder=3)
            ax.set_yticks(range(8),[r["label"] for r in q["scales"]]);ax.invert_yaxis()
            ax.set_xlim(-.1,5.1);ax.set_xticks(range(6));ax.set_xlabel("Recomputed subscale score (0–5)")
            ax.set_title("Eight MAIA-2 dimensions",pad=14)
            matrix=np.array([r["n"] for r in q["spatial"]["transitions"]]).reshape(8,8).T
            bx.imshow(matrix,origin="lower",cmap="Blues",vmin=0,vmax=max(1,matrix.max()))
            for i in range(8):
                for j in range(8):
                    bx.text(j,i,str(matrix[i,j]) if matrix[i,j] else "·",ha="center",va="center",color="white" if matrix[i,j]>.55*max(1,matrix.max()) else "#425466")
            bx.set_xticks(range(8),list("ABCDEFGH"));bx.set_yticks(range(8),list("ABCDEFGH"))
            bx.set_xlabel("Control category");bx.set_ylabel("Viscereality category")
            bx.set_title("Paired spatial-frame responses",pad=14)
            s=q["spatial"]
            fig.suptitle(f"Questionnaire coverage · {q['maia_complete']} complete MAIA-2 records · {s['n_pairs']} spatial pairs",y=.96,fontsize=14)
            fig.text(.5,.085,"Left: individual scores, means and pointwise 95% participant-bootstrap intervals. Right: participant counts.",ha="center",fontsize=9)
            fig.text(.5,.035,f"Viscereality higher / equal / lower: {s['higher']} / {s['ties']} / {s['lower']}. A–H retain recorded ordering; anchor direction is unverified.",ha="center",fontsize=9)
            fig.subplots_adjust(left=.18,right=.97,top=.82,bottom=.22,wspace=.50)
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
    q=report["questionnaires"]
    for measure in ("questionnaire_summary","questionnaire_associations","spatial_change"):
        files[measure+".svg"]=figure_svg(report,measure).encode()
    for key in ("scoring_audit","scores","scales","items","associations","delta_associations","moderation","interscale_descriptive"):
        files["questionnaire_"+key+".csv"]=as_table(q[key])
    files["spatial_comparison.csv"]=as_table([q["spatial"]])
    for key in ("order_counts","transitions","distributions","descriptives","delta_distribution"):
        files["spatial_"+key+".csv"]=as_table(q["spatial"][key])
    files["data_coverage.csv"]=as_table(report["data_coverage"])
    individual=report["participant_sigmoids"]
    if individual["status"]=="computed":
        for measure in ("participant_example","participant_diagnostics"):
            files[measure+".svg"]=figure_bytes(report,measure)
        files["participant_curve_atlas.pdf"]=atlas_bytes(individual)
        files["participant_normalized_rt.csv"]=as_table(normalized_trials(individual,retained))
        files["participant_diagnostics.csv"]=as_table(diagnostics(individual))
        for key in ("parameters","shared_parameters","participant_scores","shared_participant_scores",
                    "associations","shared_associations","candidates","reliability","recovery","contrasts","contrast_reliability"):
            files["participant_"+key+".csv"]=as_table(individual[key])
        files["participant_prediction.csv"]=as_table(individual["prediction"]["scores"])
        files["participant_linkage_audit.json"]=json.dumps(individual["linkage_audit"],indent=2).encode()
        files["participant_contrast_diagnostics.csv"]=as_table(contrast_diagnostics(individual))
        for key in ("associations","shared_associations","participant_scores","shared_participant_scores","contrasts"):
            files["participant_linkage_sensitivity_"+key+".csv"]=as_table([
                row|{"excluded_ids":",".join(s["excluded_ids"]),"selected_method":s["selected_method"]}
                for s in individual["linkage_sensitivities"] for row in s[key]])
    robustness=report["robustness"];group=robustness["group_shape"]
    files["robustness_results.json"]=json.dumps(robustness,indent=2,allow_nan=False).encode()
    files["robustness_linkage_models.csv"]=as_table([m|{"excluded_ids":','.join(s["excluded_ids"]),"category":category}
        for s in robustness["recording_linkage"] for category in ("mixed_models","cluster_models") for m in s[category]])
    files["robustness_linkage_coefficients.csv"]=as_table([c|{"excluded_ids":','.join(s["excluded_ids"]),"model":m["name"]}
        for s in robustness["recording_linkage"] for category in ("mixed_models","cluster_models") for m in s[category] for c in m.get("coefficients",[])])
    if group["status"]=="computed":
        files["remaining_robustness.svg"]=figure_bytes(report,"remaining_robustness")
        files["robustness_prediction.csv"]=as_table(group["prediction"]["scores"])
        for key in ("log_distance_candidates","geometry_sensitivities","selection_frequencies"):
            files["robustness_"+key+".csv"]=as_table(group[key])
        files["robustness_geometry_parameters.csv"]=as_table([p|{"criteria":s["criteria"],"width_floor_cm":s["width_floor_cm"]}
            for s in group["geometry_sensitivities"] for p in s.get("parameters",[])])
        files["robustness_selection_resamples.csv"]=as_table([p|{"replicate":s["replicate"],"method":s["method"]}
            for s in group["selection_resamples"] for p in s["parameters"]])
    d=report["descriptive_sigmoids"]
    if d["status"]=="computed":
        for measure in ("descriptive_sigmoids","sigmoid_extrapolation","pps_shape","sigmoid_geometry"):
            files[measure+".svg"]=figure_svg(report,measure).encode()
        for key in ("parameters","comparisons","candidates"):
            files["descriptive_sigmoid_"+key+".csv"]=as_table(d[key])
        a=d["shape_audit"]
        for key in ("original_geometry","visible_geometry","visible_parameters","visible_candidates","linear_candidates"):
            files["pps_shape_"+key+".csv"]=as_table(a[key])
        files["pps_shape_nested_prediction.csv"]=as_table(a["nested_prediction"]["scores"])
        files["pps_shape_raw_curvature.csv"]=as_table(a["raw_curvature"]["rows"])
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
    source_code={name:(Path(__file__).resolve().parent/name).read_bytes() for name in ("inference.py","paper_analysis.py","preparation.py","publication_report.py","descriptive_sigmoid.py","sigmoid_shape.py","questionnaires.py","participant_sigmoid.py","participant_report.py")}
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
