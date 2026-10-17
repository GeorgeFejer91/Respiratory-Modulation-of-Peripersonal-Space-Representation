"""Results-only Bayesian tables, figures and independently hashed browser download."""

import io
import json
import platform
import sys
import zipfile
from hashlib import sha256
from pathlib import Path

import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import scipy
from scipy.special import expit

from bayesian_sigmoid import PARAMETERS, PRIORS, SEED
from descriptive_sigmoid import DISTANCES, LABELS
from preparation import FILES
from publication_report import as_table


SOURCE_FILES = ("bayesian_sigmoid.py", "bayesian_report.py", "inference.py",
    "paper_analysis.py", "preparation.py", "publication_report.py", "descriptive_sigmoid.py",
    "sigmoid_shape.py", "questionnaires.py", "participant_sigmoid.py", "participant_report.py")
TABLES = ("cells", "model_evidence", "prediction", "group_contrasts", "group_cell_summaries", "associations",
          "joint_moderation", "quadrature_checks", "reliability", "recovery", "prior_predictive")


def primary_rows(report, key, prior="primary"):
    excluded = ",".join(report["primary_excluded_ids"])
    return [r for r in report[key] if r.get("prior", prior) == prior and
            (r.get("excluded_ids", excluded) == excluded) and not r.get("ambiguous_recording", False)]


def prediction_summary(report):
    rows = []
    rng = np.random.default_rng(SEED+2)
    for prior in PRIORS:
        observations = primary_rows(report, "prediction", prior)
        models = ("constant", "linear", "log_distance", "sigmoid")
        errors = {}
        for model in models:
            selected = [r for r in observations if r["model"] == model]
            ids = sorted({r["participant_id"] for r in selected})
            errors[model] = np.array([np.mean([r["squared_mean_error_ms2"] for r in selected
                                              if r["participant_id"] == pid]) for pid in ids])
            rows.append(dict(prior=prior, model=model, held_distance_rmse_ms=float(np.sqrt(errors[model].mean())),
                mean_block_log_predictive_density=float(np.mean([r["held_block_log_predictive_density"] for r in selected])),
                n_participants=len(ids)))
        resample = rng.integers(len(ids), size=(5000, len(ids)))
        for comparator in models[:-1]:
            difference = np.sqrt(errors["sigmoid"][resample].mean(1))-np.sqrt(errors[comparator][resample].mean(1))
            target = next(r for r in rows if r["prior"] == prior and r["model"] == comparator)
            target["sigmoid_minus_this_rmse_ms"] = float(np.sqrt(errors["sigmoid"].mean())-np.sqrt(errors[comparator].mean()))
            target["difference_low"], target["difference_high"] = np.quantile(difference, [.025, .975]).tolist()
    return rows


def fmt(value, digits=3):
    return "undefined" if value is None else f"{value:.{digits}g}"


def markdown(report):
    if report["status"] != "computed":
        return "# Bayesian results\n\nNot estimable: "+report.get("reason", "unknown reason")
    cells = primary_rows(report, "cells")
    contrasts = [r for r in primary_rows(report, "group_contrasts")
                 if r["scope"] == "posterior + Bayesian bootstrap" and r["effect"] != "Mean"]
    bounded = sum(r["midpoint_cm_low"] >= 10 and r["midpoint_cm_high"] <= 100 for r in cells)
    informative_amplitude = sum(r["amplitude_low"] > 0 or r["amplitude_high"] < 0 for r in cells)
    lines = ["# Study 5 — Bayesian parameter results", "",
        "Results-only exploratory extension. The version-1.9 manuscript and complete analysis are preserved.", "",
        "## 1. Can we compute individual sigmoids, and are they identified?", "",
        f"All {len(report['participant_ids'])*4} participant × condition × phase cells have proper sigmoid posteriors under "
        f"each of four declared priors ({len(report['cells'])} fits). The main behavioural cohort excludes "
        f"{', '.join(report['primary_excluded_ids']) or 'no records'} and contains {len(cells)//4} records. "
        "Recording copies share posterior draws and resampling weights; the source mapping is still unresolved.", "",
        f"**Computability is established; individual physiological boundary identification is not.** "
        f"Of the {len(cells)} primary cells, {bounded} have their entire 95% midpoint interval inside 10–100 cm. "
        f"Only {informative_amplitude} signed-amplitude intervals exclude zero. Median joint shape information "
        f"gain is {fmt(np.median([r['shape_information_nats'] for r in cells]))} nats. Median posterior probability "
        f"that both 10–90% bends lie within the measured range is "
        f"{fmt(np.median([r['probability_10_90_inside_measured_range'] for r in cells]))}. "
        "These are descriptive diagnostics, not a new physiological pass/fail gate.", "",
        "The primary prior midpoint is centred at 55 cm. An average posterior midpoint near 55 cm is therefore "
        "not evidence that the measured PPS boundary is 55 cm. Sharpness also depends strongly on the declared "
        "width support; averages of prior-dependent parameters must retain that qualification.", "",
        "## 2. Does a sigmoid predict better than simpler responses?", "",
        "Each distance was held out and all its trials excluded from fitting. RMSE uses the held-out raw cell "
        "mean, equal participant/cell/distance weighting, and no smoothing. Model probabilities use explicit "
        "equal prior probabilities and proper nuisance priors; they are not assumption-free shape evidence.", "",
        "| Prior | Model | Held-distance RMSE (ms) | Sigmoid minus comparator RMSE, 95% paired-person interval (ms) |",
        "| --- | --- | ---: | --- |"]
    for r in prediction_summary(report):
        difference = (f"{fmt(r['sigmoid_minus_this_rmse_ms'])} [{fmt(r['difference_low'])}, {fmt(r['difference_high'])}]"
                      if "difference_low" in r else "—")
        lines.append(f"| {r['prior']} | {r['model']} | {fmt(r['held_distance_rmse_ms'])} | {difference} |")
    lines += ["", "Negative differences favour the sigmoid. A small advantage over a constant does not "
              "identify its midpoint/width or establish observed S curvature.", "",
        "## 3. Do midpoint or sharpness differ by condition or phase?", "",
        "Condition = Viscereality−Control; Phase = Inhale−Exhale; interaction = the difference of those phase "
        "effects. Four cells stay paired within each participant. The following are primary-prior posterior "
        "plus Bayesian-bootstrap descriptive intervals; finite-cohort posterior intervals and every prior/cohort "
        "sensitivity are separately exported. This is not a fully hierarchical population-effects model.", "",
        "| Parameter | Effect | Median | 95% interval | Probability above zero |", "| --- | --- | ---: | --- | ---: |"]
    for r in contrasts:
        lines.append(f"| {r['parameter']} | {r['effect']} | {fmt(r['median'])} | [{fmt(r['low'])}, {fmt(r['high'])}] | {r['probability_positive']:.2f} |")
    lines += ["", "Midpoints use cm; normalized sharpness uses cm⁻¹. These intervals quantify model-conditional "
              "and modular participant uncertainty; they do not establish equivalence when zero is included.", "",
        "### Descriptive cell-average parameters", "",
        "These are means of conditional individual parameters, not fitted boundaries of the average response "
        "function. Their proximity to the prior centre and their sensitivity to width support prevent a "
        "physiological interpretation.", "",
        "| Cell | Parameter | Conditional mean, median [95% interval] |", "| --- | --- | --- |"]
    for r in primary_rows(report, "group_cell_summaries"):
        if r["scope"] == "posterior + Bayesian bootstrap":
            lines.append(f"| {r['condition']} · {r['phase']} | {r['parameter']} | {fmt(r['median'])} [{fmt(r['low'])}, {fmt(r['high'])}] |")
    lines += ["",
        "## 4. Prior sensitivity and reliability", "",
        "| Prior | Median midpoint interval width (cm) | Median sharpness | Median shape information (nats) | Cell amplitude intervals excluding zero |",
        "| --- | ---: | ---: | ---: | ---: |"]
    for prior in PRIORS:
        rows = primary_rows(report, "cells", prior)
        lines.append(f"| {prior} | {fmt(np.median([r['midpoint_cm_high']-r['midpoint_cm_low'] for r in rows]))} | "
            f"{fmt(np.median([r['normalized_steepness_per_cm'] for r in rows]))} | "
            f"{fmt(np.median([r['shape_information_nats'] for r in rows]))} | "
            f"{sum(r['amplitude_low'] > 0 or r['amplitude_high'] < 0 for r in rows)} |")
    lines += ["", "| Parameter | Split-half four-cell-mean rho | Split-half condition-change rho | Matched-sigmoid recovery rho |",
              "| --- | ---: | ---: | ---: |"]
    for parameter in PARAMETERS:
        def median_rho(summary):
            return np.median([r["rho"] for r in report["reliability"] if r["parameter"] == parameter and r["summary"] == summary])
        recovery = np.median([r["recovery_rho"] for r in report["recovery"] if r["parameter"] == parameter and r["scenario"] == "sigmoid"])
        lines.append(f"| {parameter} | {fmt(median_rho('Mean'))} | {fmt(median_rho('Condition'))} | {fmt(recovery)} |")
    lines += ["", "Ten split halves measure within-session stability, not test–retest reliability. Recovery uses "
              "20 replicates of 80-ms sigmoid signals with the actual design/counts and a matched Gaussian noise "
              "model; it does not validate arbitrary RT distributions or real physiological boundaries. Flat "
              "and linear simulations remain in the full export.", "",
              "| Prior | Prior-predictive negative RT fraction | Prior residual SD 95% range (ms) |",
              "| --- | ---: | --- |"]
    for r in report["prior_predictive"]:
        lines.append(f"| {r['prior']} | {r['negative_rt_fraction']:.1%} | "
                     f"[{fmt(r['prior_sigma_ms'][0])}, {fmt(r['prior_sigma_ms'][2])}] |")
    lines += ["", "The Gaussian working model admits negative RTs, especially under the deliberately wider prior. "
              "This is an explicit prior-predictive limitation, not a positive-support RT model. Bayesian fitting "
              "still assumes a likelihood, priors, noise structure and finite integration support.", "",
        "## 5. Spatial ratings, MAIA-2 and joint exploration", "",
        "The same-condition rating is paired with each condition's two respiratory-phase estimates. MAIA-2 "
        "is measured once before the experiment; spatial change compares two post-intervention ratings. "
        "Eight continuous subscales stay separate. Numerical spatial changes assume comparable category "
        "spacing; rank/direction sensitivities retain that limitation.", "",
        "| Prior | Rank-association intervals excluding zero / 92 | Joint-model coefficient intervals excluding zero / 192 |",
        "| --- | ---: | ---: |"]
    for prior in PRIORS:
        counts = []
        for key in ("associations", "joint_moderation"):
            rows = primary_rows(report, key, prior)
            counts.append(sum(r["low"] is not None and (r["low"] > 0 or r["high"] < 0) for r in rows))
        lines.append(f"| {prior} | {counts[0]} / 92 | {counts[1]} / 192 |")
    lines += ["", f"Across four priors and four recording cohorts the download retains {len(report['associations'])} "
        f"rank-association records and {len(report['joint_moderation'])} joint-model coefficient records. "
        "They are repeated exploratory sensitivities, not independent replications. Rank intervals combine "
        "latent-parameter draws with paired recording-group bootstrap counts. Joint coefficients combine "
        "latent draws with Bayesian-bootstrap WLS, controlling for order. Neither is a full latent-covariate posterior.", "",
        "Each joint model includes centred MAIA, spatial delta, their product and presentation order. The "
        "product on the Condition contrast addresses Condition × MAIA × spatial change; the product on the "
        "Condition × Phase contrast additionally varies with respiratory phase. All three scientific "
        "coefficients and all four orthogonal summaries are retained. No causal mediation is identified.", "",
        "## 6. What is complete and what remains unresolved?", "",
        "The computational Bayesian reference, individual tables, prediction, prior sensitivity, paired "
        "experimental contrasts, descriptive curves and full exploratory links are implemented. The "
        "results do not establish reliable participant-level physiological midpoint/sharpness identification "
        "or a robust experimental/questionnaire effect. A full joint hierarchical nonlinear model, "
        "serial-dependence/positive-support likelihood sensitivity and independent test–retest data have not "
        "been supplied by this extension. No claim of a universally best model is made.", "",
        "Raw RT panels and conditional unit-amplitude geometry are separate. Normalized S geometry is "
        "implied by choosing a sigmoid family. Its appearance does not establish observed curvature. "
        "Average functions integrate over people and posterior draws and need not themselves be sigmoids.", "",
        "The download records sources and artifact hashes. The broader level-by-level synthesis is "
        "`results/RESULTS_REPORT.md`; `for-ai/ANALYSIS_ROADMAP.md` owns the active checklist. Manuscript "
        "drafting remains paused. Earlier frequentist p values are unadjusted; the new probabilities are "
        "not p values or multiplicity-adjusted guarantees.", "",
        "Methodological context: [Hedge et al., reliability and individual differences]"
        "(https://doi.org/10.3758/s13428-017-0935-1); "
        "[Stan guide to posterior predictive checks]"
        "(https://mc-stan.org/docs/stan-users-guide/posterior-predictive-checks.html). "
        "The conjugate likelihood, quadrature and modular summaries are explicitly specified and "
        "independently verified in this repository, not attributed to either source.", ""]
    return "\n".join(lines)


def figure_bytes(report, kind="curves", format="svg"):
    with matplotlib.rc_context({"svg.hashsalt": "study5-bayes1", "font.size": 10}):
        if kind == "curves":
            fig, axes = plt.subplots(1, 4, figsize=(14, 4.3), sharex=True, sharey=True)
            for ax, r in zip(axes, report["average_curves"]):
                lo, median, hi = np.array(r["posterior_average_ms"])
                ax.fill_between(r["distance_cm"], lo, hi, color="#16729b", alpha=.2)
                ax.plot(r["distance_cm"], median, color="#16729b", lw=2)
                ax.errorbar(DISTANCES, r["observed_mean_ms"], yerr=1.96*np.array(r["observed_se_ms"]),
                            fmt="o", color="#b55d22", ms=4, capsize=3)
                ax.set(title=r["condition"]+"\n"+r["phase"], xlabel="Nominal distance (cm)", xlim=(10, 100))
                ax.grid(alpha=.18)
            axes[0].set_ylabel("Reaction time (ms)")
            fig.suptitle("Four average response functions · observed data and Bayesian uncertainty", y=.99)
            fig.text(.5, .025, "Orange: observed equal-person means ± 1.96 SE. Blue: posterior + paired Bayesian-bootstrap average, 95% interval.\n"
                     "Primary prior, both ambiguous records excluded. These average functions are not constrained to be sigmoid-shaped.",
                     ha="center", fontsize=9)
            fig.tight_layout(rect=(0, .13, 1, .91))
        elif kind == "cell_parameters":
            fig, axes = plt.subplots(1, 2, figsize=(11, 4.3))
            for ax, parameter in zip(axes, PARAMETERS):
                rows = [r for r in primary_rows(report, "group_cell_summaries") if
                        r["scope"] == "posterior + Bayesian bootstrap" and r["parameter"] == parameter]
                for j, r in enumerate(rows):
                    ax.errorbar(r["median"], j, xerr=[[r["median"]-r["low"]], [r["high"]-r["median"]]],
                        fmt="o", color="#16729b", capsize=3)
                ax.set_yticks(range(4), [c+" · "+p for c, p in LABELS])
                ax.set_xlabel("Mean conditional midpoint (cm)" if parameter == PARAMETERS[0] else "Mean conditional sharpness (cm⁻¹)")
                ax.grid(axis="x", alpha=.2)
            axes[0].axvline(55., color=".5", ls="--")
            fig.suptitle("Descriptive cell-average parameters · conditional on the sigmoid model")
            fig.text(.5, .02, "Dashed line: midpoint prior centre (55 cm). Primary prior; posterior + Bayesian-bootstrap intervals.\n"
                     "Prior-dependent individual fits do not establish physiological boundaries.",
                     ha="center", fontsize=8)
            fig.tight_layout(rect=(0, .13, 1, .94))
        elif kind == "parameters":
            fig, axes = plt.subplots(1, 2, figsize=(12, 4.7))
            for ax, parameter in zip(axes, PARAMETERS):
                for p, (prior, color) in enumerate(zip(PRIORS, ("#16729b", "#c16c26", "#447f40", "#8b559a"))):
                    rows = [r for r in primary_rows(report, "group_contrasts", prior)
                            if r["scope"] == "posterior + Bayesian bootstrap" and r["parameter"] == parameter and r["effect"] != "Mean"]
                    for j, r in enumerate(rows):
                        ax.errorbar(r["median"], j+(p-1.5)*.16,
                                    xerr=[[r["median"]-r["low"]], [r["high"]-r["median"]]],
                                    fmt="o", capsize=2, label=prior if j == 0 else None, ms=4, color=color)
                ax.axvline(0, color=".4", ls="--", lw=1)
                ax.set_yticks(range(3), ["Condition", "Phase", "Condition × Phase"])
                ax.set_xlabel("Midpoint difference (cm)" if parameter == PARAMETERS[0] else "Normalized sharpness difference (cm⁻¹)")
                ax.grid(axis="x", alpha=.2)
            axes[1].legend(loc="upper left", bbox_to_anchor=(0., -.2), ncols=2, fontsize=8)
            fig.suptitle("Experimental contrasts · parameter and participant uncertainty")
            fig.tight_layout(rect=(0, .08, 1, .95))
        else:
            raise ValueError("Unknown Bayesian figure.")
        buffer = io.BytesIO()
        fig.savefig(buffer, format=format, metadata={"Date": None} if format == "svg" else None, dpi=160)
        plt.close(fig)
        return buffer.getvalue()


def participant_figure(report, participant_id):
    rows = [r for r in report["individual_curves"] if r["participant_id"] == participant_id]
    summaries = [r for r in report["cells"] if r["prior"] == "primary" and r["participant_id"] == participant_id]
    fig, axes = plt.subplots(2, 4, figsize=(14, 7.2), sharex=True, sharey="row")
    for j, (r, summary) in enumerate(zip(rows, summaries)):
        x = r["distance_cm"]
        for i, field in enumerate(("response_ms", "conditional_geometry")):
            lo, median, hi = np.array(r[field])
            ax = axes[i, j]
            ax.fill_between(x, lo, hi, color="#16729b", alpha=.19)
            ax.plot(x, median, color="#16729b", lw=2)
            ax.grid(alpha=.18)
            if i == 0:
                ax.errorbar(DISTANCES, r["observed_mean_ms"], yerr=1.96*np.array(r["observed_se_ms"]),
                            fmt="o", ms=3, color="#b55d22", capsize=2)
                ax.set_title(r["condition"]+" · "+r["phase"], fontsize=10)
            else:
                representative = expit((np.array(x)-summary["midpoint_cm"])/summary["width_cm"])
                ax.plot(x, representative, color=".4", ls="--", lw=1)
                ax.set(ylim=(-.02, 1.02), xlabel="Nominal distance (cm)")
                ax.text(.03, .94, f"m {summary['midpoint_cm']:.1f} [{summary['midpoint_cm_low']:.1f}, {summary['midpoint_cm_high']:.1f}] cm\n"
                        f"sharpness {summary['normalized_steepness_per_cm']:.4f} cm⁻¹", transform=ax.transAxes,
                        va="top", fontsize=8, bbox=dict(facecolor="white", alpha=.8, edgecolor="none"))
    axes[0, 0].set_ylabel("Raw RT response (ms)")
    axes[1, 0].set_ylabel("Conditional increasing\nunit-amplitude geometry")
    flag = " · AMBIGUOUS RECORDING LINKAGE" if rows[0]["ambiguous_recording"] else ""
    fig.suptitle(participant_id+" · Bayesian raw response and assumed sigmoid geometry"+flag, fontsize=13)
    fig.text(.5, .025, "Top: raw means ± 1.96 SE; posterior response median and 95% band retain signed amplitude. "
             "Bottom: increasing unit-amplitude sigmoid geometry, not normalized observations.\n"
             "Dashed: representative marginal-median shape. The imposed S and finite midpoint do not demonstrate an observed PPS boundary. "
             "Shared axes; measured distances only.", ha="center", fontsize=8.5)
    fig.tight_layout(rect=(0, .08, 1, .95))
    return fig


def atlas_bytes(report):
    buffer = io.BytesIO()
    with PdfPages(buffer, metadata={"Title": "Study 5 Bayesian participant curves", "CreationDate": None,
                                   "ModDate": None}) as pdf:
        for pid in report["participant_ids"]:
            fig = participant_figure(report, pid)
            pdf.savefig(fig)
            plt.close(fig)
    return buffer.getvalue()


def result_bundle(report, sources):
    # The entry notebook is embedded in the export, not installed as a Python module.
    code = {name: (Path(__file__).resolve().parent/name).read_bytes() for name in SOURCE_FILES}
    files = {"bayesian_results.json": json.dumps(report, indent=2, allow_nan=False).encode(),
             "bayesian_results.md": markdown(report).encode(),
             "bayesian_prediction_summary.csv": as_table(prediction_summary(report)),
             "bayesian_average_curves.svg": figure_bytes(report),
             "bayesian_cell_parameters.svg": figure_bytes(report, "cell_parameters"),
             "bayesian_parameter_contrasts.svg": figure_bytes(report, "parameters"),
             "bayesian_participant_atlas.pdf": atlas_bytes(report)}
    files.update({"bayesian_"+key+".csv": as_table(report[key]) for key in TABLES})
    files.update({"analysis_source/"+name: data for name, data in code.items()})
    runtime = dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
                   matplotlib=matplotlib.__version__, platform=platform.system(),
                   execution="browser Pyodide" if sys.platform == "emscripten" else "native validation")
    manifest = dict(analysis_version=report["analysis_version"], runtime=runtime,
        source_sha256={name: sha256(data).hexdigest() for name, data in zip(FILES, sources)},
        code_sha256={name: sha256(data).hexdigest() for name, data in code.items()},
        artifact_sha256={name: sha256(data).hexdigest() for name, data in files.items()},
        manuscript_updated=False, contract="workbook/ANALYSIS_PLAN.md", legacy_analysis_version="1.9")
    files["manifest.json"] = json.dumps(manifest, indent=2).encode()
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in files.items():
            info = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    return buffer.getvalue(), manifest
