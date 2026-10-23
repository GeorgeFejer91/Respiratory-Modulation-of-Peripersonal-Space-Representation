"""Minimal exploratory SOA check for Segment 1; see results/pps_soa/SPECIFICATION.md."""

import csv
import json
import platform
import zipfile
from hashlib import sha256
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy import linalg, stats

from inference import repeated_anova
from paper_analysis import CONDITIONS, PHASES, SOAS, cell_cube, clean, grouped_means
from preparation import FILES, audit_release, load_pair


def analyze(people, trials, excluded=("P011", "P033"), *, baseline_correct=True):
    retained, quality, counts = clean(people, trials)
    retained = [r for r in retained if r["participant_id"] not in excluded]
    ids, cube = cell_cube(retained)
    baseline = grouped_means([r for r in retained if r["trial_type"] == "Baseline"],
                             ("participant_id", "condition", "phase"))
    missing_baseline = [pid for pid in ids if any((pid, c, p) not in baseline
                        for c in CONDITIONS for p in PHASES)] if baseline_correct else []
    if baseline_correct:
        keep = [i for i, pid in enumerate(ids) if pid not in missing_baseline]
        ids, cube = [ids[i] for i in keep], cube[keep].copy()
        for i, pid in enumerate(ids):
            for ci, condition in enumerate(CONDITIONS):
                for pi, phase in enumerate(PHASES):
                    cube[i, ci, pi] -= baseline[pid, condition, phase]
    if len(ids) < 3:
        raise ValueError("At least three complete participants are required.")
    means = cube.mean(axis=(1, 2))
    test = next(r for r in repeated_anova(cube) if r["effect"] == "SOA")
    test["df1_GG"] = test["df1"] * test["epsilon_GG"]
    test["df2_GG"] = test["df2"] * test["epsilon_GG"]
    test["partial_eta_squared"] = test["F"] * test["df1"] / (test["F"] * test["df1"] + test["df2"])
    summary = []
    for soa, values in zip(SOAS, means.T):
        sd = float(values.std(ddof=1))
        half = float(stats.t.ppf(.975, len(ids)-1) * sd / np.sqrt(len(ids)))
        mean = float(values.mean())
        summary.append(dict(soa_ms=soa, measure="corrected_rt_ms" if baseline_correct else "reaction_time_ms",
                            mean_ms=mean, sd_ms=sd, median_ms=float(np.median(values)),
                            n=len(ids), ci_low_ms=mean-half, ci_high_ms=mean+half))
    difference = means[:, -1] - means[:, 0]
    half = float(stats.t.ppf(.975, len(ids)-1) * stats.sem(difference))
    contrast = dict(direction="RT(2700) minus RT(300)", mean_ms=float(difference.mean()),
                    ci_low_ms=float(difference.mean()-half), ci_high_ms=float(difference.mean()+half))
    scores = means @ linalg.helmert(5).T
    diagnostics = [dict(contrast=i+1, W=float(stats.shapiro(column).statistic),
                        p=float(stats.shapiro(column).pvalue)) for i, column in enumerate(scores.T)]
    incomplete = sorted({r["participant_id"] for r in retained} - set(ids))
    report = dict(execution="native Python; saved display in browser", classification="exploratory",
                  measure="corrected_rt_ms" if baseline_correct else "reaction_time_ms",
                  correction="AT minus retained participant × Condition × Phase baseline mean; baseline SOAs pooled" if baseline_correct else "none; raw RT reference",
                  missing_baseline_excluded=missing_baseline,
                  excluded_linkage=list(excluded), participant_ids=ids, incomplete_excluded=incomplete,
                  cleaning_counts_full_release=counts, quality=quality, anova=test,
                  summary=summary, endpoint_contrast=contrast, contrast_normality=diagnostics,
                  interval="Pointwise marginal mean 95% t CI across participants; not a paired-contrast CI",
                  retained_at=sum(r["participant_id"] in ids and r["trial_type"] == "Audio-Tactile" for r in retained))
    return report, cube, means


def apa(report):
    a = report["anova"]
    p = "p < .001" if a["p_GG"] < .001 else f"p = {a['p_GG']:.3f}".replace("0.", ".")
    return (f"F({a['df1_GG']:.2f}, {a['df2_GG']:.2f}) = {a['F']:.2f}, {p}, "
            f"η²ₚ = {a['partial_eta_squared']:.3f}, εGG = {a['epsilon_GG']:.3f}").replace("= 0.", "= .")


def build(root):
    output = root / "results/pps_soa"
    people, trials = load_pair(*[(root / "data/raw" / name).read_bytes() for name in FILES])
    audit_release(people, trials)
    report, cube, means = analyze(people, trials)
    raw_report, raw_cube, _ = analyze(people, trials, baseline_correct=False)
    if raw_report["participant_ids"] != report["participant_ids"]:
        raise ValueError("Primary and raw-reference cohorts differ; report matched cohorts before promotion.")
    report["raw_reference"] = {key: raw_report[key] for key in ("measure", "correction", "anova", "summary", "endpoint_contrast")}
    report["apa"] = apa(report)
    report["linkage_sensitivities"] = []
    for excluded in ((), ("P011",), ("P033",)):
        other, _, _ = analyze(people, trials, excluded)
        report["linkage_sensitivities"].append(dict(excluded=list(excluded), anova=other["anova"],
            summary=other["summary"], endpoint_contrast=other["endpoint_contrast"],
            warning="Full release includes dependent linked recordings" if not excluded else "Unresolved linked-record attribution"))
    report["runtime"] = dict(python=platform.python_version(), numpy=np.__version__,
        scipy=scipy.__version__, matplotlib=matplotlib.__version__)
    (output / "results.json").write_text(json.dumps(report, indent=2, allow_nan=False)+"\n", encoding="utf-8", newline="\n")
    with (output / "participant_cells.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(["participant_id", "condition", "phase", "soa_ms", "reaction_time_ms", "baseline_mean_ms", "corrected_rt_ms"])
        for i, (pid, cells) in enumerate(zip(report["participant_ids"], cube)):
            for ci, condition in enumerate(CONDITIONS):
                for pi, phase in enumerate(PHASES):
                    for si, soa in enumerate(SOAS):
                        raw = raw_cube[i, ci, pi, si]
                        corrected = cells[ci, pi, si]
                        writer.writerow([pid, condition, phase, int(soa), raw, raw-corrected, corrected])
    with (output / "summary.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(report["summary"][0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(report["summary"])
    with plt.rc_context({"font.family":"DejaVu Sans", "font.size":12, "svg.fonttype":"none",
                         "svg.hashsalt":"study5-pps-soa", "axes.spines.top":False, "axes.spines.right":False}):
        fig, ax = plt.subplots(figsize=(7.2, 4.6), layout="constrained")
        ax.plot(SOAS, means.T, color="#777777", alpha=.45, linewidth=.75, marker=".", markersize=3)
        group = np.array([r["mean_ms"] for r in report["summary"]])
        half = np.array([r["ci_high_ms"]-r["mean_ms"] for r in report["summary"]])
        ax.errorbar(SOAS, group, yerr=half, color="black", marker="o", linewidth=2,
                    capsize=4, label=f"Mean and 95% CI (N = {len(means)})", zorder=3)
        low, high = min(0., means.min(), (group-half).min()), max(0., means.max(), (group+half).max())
        span = max(high-low, 1.)
        ax.set(xlabel="Stimulus onset asynchrony (ms)", ylabel="AT − Baseline RT (ms)",
               xticks=SOAS, xlim=(180, 2820), ylim=(low-.05*span if low < 0 else 0, high+.08*span))
        ax.axhline(0, color="#555555", linestyle=":", linewidth=1)
        ax.legend(frameon=False, loc="upper right", fontsize=11)
        fig.savefig(output / "soa_rt.svg", metadata={"Date":None}, facecolor="white")
        # Canonical text bytes survive Git's Windows/Linux line-ending policy.
        svg = output / "soa_rt.svg"
        svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines())+"\n", encoding="utf-8", newline="\n")
        fig.savefig(output / "soa_rt.png", dpi=300, facecolor="white")
        plt.close(fig)
        fig, axes = plt.subplots(2, 2, figsize=(8, 7), layout="constrained")
        for i, ax in enumerate(axes.flat):
            stats.probplot((means @ linalg.helmert(5).T)[:, i], plot=ax)
            ax.axhline(0, color="#555555", linestyle=":", linewidth=.7)
            ax.set_title(f"Orthogonal SOA contrast {i+1}")
        fig.savefig(output / "diagnostics.png", dpi=160, facecolor="white")
        plt.close(fig)
    contrast = report["endpoint_contrast"]
    finding = ("The omnibus test supports different population mean RTs across SOAs."
               if report["anova"]["p_GG"] < .05 else
               "The omnibus test does not establish different population mean RTs across SOAs.")
    rows = "\n".join(f"| {s['soa_ms']:.0f} | {s['mean_ms']:.2f} | {s['sd_ms']:.2f} | {s['median_ms']:.2f} | {s['n']} | [{s['ci_low_ms']:.2f}, {s['ci_high_ms']:.2f}] |" for s in report["summary"])
    sensitivity = "\n".join(f"- Excluded {s['excluded'] or 'neither linked record'}: N = {s['anova']['n']}; " + apa(s) + "." for s in report["linkage_sensitivities"])
    (output / "RESULTS.md").write_text(f"""# Segment 1: does RT depend on SOA?

Exploratory basic phenomenon check using **baseline-corrected RT (AT − Baseline)**.
**{report['apa']}** (Greenhouse–Geisser correction).
N = {len(means)} complete participants; {report['retained_at']} retained AT trials;
incomplete exclusions: {report['incomplete_excluded'] or 'none'}. P011/P033 excluded.
{finding} This is an SOA check, not proof
of a specifically spatial PPS mechanism, sigmoid or physiological boundary.

**Figure 1**

*Baseline-corrected reaction times across stimulus onset asynchronies*

![Participant RT profiles and group means](soa_rt.svg)

*Note.* Grey lines show each person's five means, averaging the four Condition ×
Phase cells equally. Black points show the equal-person mean with pointwise
marginal 95% t CIs (39 df), not within-person contrast CIs or simultaneous bands.
Subtract each participant × Condition × Phase retained baseline mean (all
baseline SOAs pooled) before averaging. Negative values mean AT responses are
faster than baseline. No normalization or smoothing. Lines are visual guides.
The zero reference and all negative values are retained. Mean intervals describe
the corrected participant scores and include their observed baseline-estimation
variation; they are not conditional trial-level or separately refitted baseline
intervals. [Full settings and limitations](SPECIFICATION.md).

| SOA (ms) | M (ms) | SD (ms) | Median (ms) | n | 95% CI (ms) |
| --- | --- | --- | --- | --- | --- |
{rows}

The descriptive paired endpoint difference, RT(2700) − RT(300), is
{contrast['mean_ms']:.2f} ms, 95% CI [{contrast['ci_low_ms']:.2f}, {contrast['ci_high_ms']:.2f}].
This CI is for the paired difference; no additional endpoint p test was run.
Partial eta squared is a descriptive omnibus effect-size point estimate; no
eta-squared CI is claimed. The endpoint CI supplies magnitude uncertainty in ms.

## Diagnostics and sensitivities

Sphericity is addressed by always using GG correction. Participant pairing and
complete cells are checked, and the known linked pair is excluded. Contrast Q–Q
plots and all four descriptive Shapiro results are retained in `diagnostics.png`
and `results.json`; they do not select a test or change cleaning. Population
sampling independence and physiological interpretation cannot be certified by
normality screens. All sensitivity outcomes are reported, with unadjusted p values:

{sensitivity}

The Q–Q plots show tail departures, especially for contrast 4. The corrected
ANOVA p value remains an approximate inference; no diagnostic-triggered test
switch or additional cleaning was performed. The endpoint interval includes zero.

Native Python calculation; the browser displays saved, hashed outputs. The
complete `results.zip` includes cell values, settings, statistics and figures.
Independent statsmodels/pandas/covariance checks are in `workbook/test_pps_soa.py`.
Input, source and output hashes and actual runtime versions are in `manifest.json`.
This is a basic SOA check; temporal expectancy/foreperiod explanations remain.

## Raw-RT reference

Raw AT RT is retained explicitly in `raw_reference` in results.json and alongside
the matched baseline and corrected RT in participant_cells.csv. Subtracting one
constant from all SOAs within each participant × condition × phase does not alter
their SOA contrasts under equal-cell averaging. Thus the raw-reference omnibus
statistics and paired endpoint contrast agree with the corrected analysis (within
roundoff), while the means, SDs and marginal CIs differ. The graph and primary
summaries above now use corrected values, as clarified by the owner.

## Software guidance

Statistical and figure review used Scientific Agent Skills: Kassis, T., Agarwal,
V., He, Y., Patel, D., & Brueckner, A. M. (2026). *Scientific Agent Skills: A Library
of Procedural Knowledge for Research Agents*. https://doi.org/10.48550/arXiv.2609.00065
""", encoding="utf-8", newline="\n")
    artifacts = ["SPECIFICATION.md", "results.json", "participant_cells.csv", "summary.csv", "soa_rt.svg", "soa_rt.png", "diagnostics.png", "RESULTS.md"]
    source_paths = ["workbook/pps_soa.py", "workbook/test_pps_soa.py", "workbook/paper_analysis.py", "workbook/inference.py", "workbook/preparation.py", "workbook/requirements.txt", "workbook/requirements-validation.txt"]
    manifest = dict(classification="exploratory", execution=report["execution"], runtime=report["runtime"],
        input_sha256={name:sha256((root/"data/raw"/name).read_bytes()).hexdigest() for name in FILES},
        source_sha256={p:sha256((root/p).read_bytes()).hexdigest() for p in source_paths},
        artifact_sha256={p:sha256((output/p).read_bytes()).hexdigest() for p in artifacts})
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8", newline="\n")
    with zipfile.ZipFile(output / "results.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        for name in [*artifacts, "manifest.json"]:
            archive.write(output / name, name)
    print(report["apa"])
    return report


if __name__ == "__main__":
    build(Path(__file__).resolve().parents[1])
