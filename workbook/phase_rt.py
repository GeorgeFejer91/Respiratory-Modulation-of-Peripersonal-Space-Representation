"""Audit literal phase labels and plot the existing Segment 2 RT contrasts."""
import csv
import json
import platform
from hashlib import sha256
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy import stats

from paper_analysis import clean, grouped_means, SOAS
from preparation import FILES, audit_release, load_pair

PHASES = ("Exhale", "Inhale")
MEASURES = {"reaction_time_ms": "Raw AT", "baseline_mean_ms": "Baseline", "corrected_rt_ms": "AT − Baseline"}


def phase_values(people, trials):
    retained, _, _ = clean(people, trials)
    retained = [r for r in retained if r["participant_id"] not in ("P011", "P033")]
    at = grouped_means([r for r in retained if r["trial_type"] == "Audio-Tactile"],
                       ("participant_id", "condition", "phase", "soa_ms"))
    baseline = grouped_means([r for r in retained if r["trial_type"] == "Baseline"],
                             ("participant_id", "condition", "phase"))
    rows = []
    for pid in sorted({r["participant_id"] for r in retained}):
        for phase in PHASES:
            # Literal labels avoid relying on the order of an encoded phase axis.
            try:
                raw = float(np.mean([at[pid, condition, phase, soa]
                    for condition in ("Control", "Viscereality") for soa in SOAS]))
                base = float(np.mean([baseline[pid, condition, phase] for condition in ("Control", "Viscereality")]))
            except KeyError as error:
                raise ValueError(f"Incomplete phase cells for {pid}: {error}") from error
            rows.append(dict(participant_id=pid, phase=phase, reaction_time_ms=raw,
                             baseline_mean_ms=base, corrected_rt_ms=raw-base))
    return rows


def describe(values):
    values = np.asarray(values)
    mean, sd = float(values.mean()), float(values.std(ddof=1))
    half = float(stats.t.ppf(.975, len(values)-1) * sd / np.sqrt(len(values)))
    return dict(n=len(values), mean=mean, sd=sd, ci_low=mean-half, ci_high=mean+half)


def summarize(rows):
    lookup = {(r["participant_id"], r["phase"]): r for r in rows}
    ids = sorted({r["participant_id"] for r in rows})
    contrasts = {}
    for measure in MEASURES:
        differences = [lookup[pid, "Inhale"][measure] - lookup[pid, "Exhale"][measure] for pid in ids]
        test = stats.ttest_1samp(differences, 0)
        contrasts[measure] = {**describe(differences), "t": float(test.statistic), "p": float(test.pvalue)}
    return dict(primary_measure="corrected_rt_ms",
                corrected_phase_means={phase: describe([lookup[pid, phase]["corrected_rt_ms"] for pid in ids]) for phase in PHASES},
                phase_means={phase: describe([lookup[pid, phase]["reaction_time_ms"] for pid in ids]) for phase in PHASES},
                contrasts=contrasts, direction="Inhale minus Exhale; positive = slower during inhale")


def build(root):
    output = root / "results/phase_rt"
    people, trials = load_pair(*[(root/"data/raw"/name).read_bytes() for name in FILES])
    audit_release(people, trials)
    rows = phase_values(people, trials)
    report = summarize(rows)
    with (root/"results/baseline_effects/response_tests.csv").open(encoding="utf-8") as source:
        saved = {r["correction"]: r for r in csv.DictReader(source) if r["cohort"] == "primary40"
                 and r["extraction"] == "mean" and r["metric"] == "mean_RT_ms" and r["effect"] == "Phase"}
    for measure, correction in zip(MEASURES, ("raw", "baseline_reference", "pooled_cp")):
        result = report["contrasts"][measure]
        for key, old in (("mean", "estimate"), ("ci_low", "ci_low"), ("ci_high", "ci_high"), ("p", "p"), ("t", "t")):
            if not np.isclose(result[key], float(saved[correction][old]), rtol=1e-10, atol=1e-10):
                raise RuntimeError(f"Saved phase contrast disagrees: {measure}/{key}")
        result["saved_shapiro_p"] = float(saved[correction]["shapiro_p"])
    report["runtime"] = dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__, matplotlib=matplotlib.__version__)
    output.mkdir(parents=True, exist_ok=True)
    with (output/"participant_phases.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    (output/"results.json").write_text(json.dumps(report, indent=2, allow_nan=False)+"\n", encoding="utf-8", newline="\n")
    lookup = {(r["participant_id"], r["phase"]): r for r in rows}
    ids = sorted({r["participant_id"] for r in rows})
    corrected = np.array([[lookup[pid, phase]["corrected_rt_ms"] for phase in PHASES] for pid in ids])
    # Outline SVG glyphs so browsers need no locally installed plotting font.
    with plt.rc_context({"font.family": "DejaVu Sans", "font.size": 14, "svg.fonttype": "path", "pdf.fonttype": 42,
                         "svg.hashsalt": "study5-phase-rt", "axes.spines.top": False, "axes.spines.right": False}):
        fig, axes = plt.subplots(2, 1, figsize=(4.6, 7.8), layout="constrained")
        ax = axes[0]
        ax.plot([0, 1], corrected.T, color="#666666", linewidth=.8, alpha=.8, marker=".", markersize=4)
        means = [report["corrected_phase_means"][phase]["mean"] for phase in PHASES]
        half = [report["corrected_phase_means"][phase]["ci_high"]-means[i] for i, phase in enumerate(PHASES)]
        ax.errorbar([0, 1], means, yerr=half, color="black", marker="s", capsize=5, linewidth=2, zorder=3)
        low, high = min(0., corrected.min(), min(np.array(means)-half)), max(0., corrected.max(), max(np.array(means)+half))
        span = max(high-low, 1.)
        ax.axhline(0, color="black", linestyle=":", linewidth=1)
        ax.set(title="A. Baseline-corrected RT", ylabel="AT − Baseline RT (ms)",
               xticks=[0, 1], xticklabels=[f"{phase}\nMean {means[i]:.2f} ms" for i, phase in enumerate(PHASES)],
               xlim=(-.4, 1.4), ylim=(low-.08*span if low < 0 else 0, high+.08*span))
        ax = axes[1]
        offsets = np.linspace(-.13, .13, len(ids))
        all_values = []
        for i, measure in enumerate(MEASURES):
            values = np.array([lookup[pid, "Inhale"][measure]-lookup[pid, "Exhale"][measure] for pid in ids])
            all_values.extend(values)
            s = report["contrasts"][measure]
            ax.scatter(i+offsets, values, color="#666666", alpha=.8, s=16)
            ax.errorbar(i, s["mean"], yerr=s["ci_high"]-s["mean"], color="black", marker="s", capsize=5, linewidth=2, zorder=3)
        ax.axhline(0, color="black", linestyle="--", linewidth=1)
        labels = [f"{name}\n{report['contrasts'][measure]['mean']:+.2f} ms".replace("-", "−")
                  for measure, name in zip(MEASURES, ("Raw AT", "Baseline", "AT −\nBaseline"))]
        ax.set(title="B. Inhale − Exhale", ylabel="Paired RT Difference (ms)",
               xticks=range(3), xticklabels=labels, xlim=(-.5, 2.5))
        # Retain every participant difference and the explicit zero reference.
        lower = min([0, *all_values, *[s["ci_low"] for s in report["contrasts"].values()]])
        upper = max([0, *all_values, *[s["ci_high"] for s in report["contrasts"].values()]])
        ax.set_ylim(lower-.08*(upper-lower), upper+.08*(upper-lower))
        for extension, options in (("svg", {"metadata": {"Date": None}}), ("png", {"dpi": 300}), ("pdf", {})):
            fig.savefig(output/f"phase_rt.{extension}", facecolor="white", **options)
        plt.close(fig)
    svg = output/"phase_rt.svg"
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines())+"\n", encoding="utf-8", newline="\n")
    table = "\n".join(f"| {MEASURES[m]} | {s['mean']:+.2f} | [{s['ci_low']:.2f}, {s['ci_high']:.2f}] | {s['t']:.3f} | {s['p']:.6f} |" for m, s in report["contrasts"].items())
    (output/"RESULTS.md").write_text(f"""# Segment 2: phase direction checked against literal trial labels

Primary baseline-corrected RT (AT − matched Baseline): Exhale **{means[0]:.2f} ms**,
Inhale **{means[1]:.2f} ms**. The corrected phase contrast remains inconclusive.
Raw AT RT is a labelled reference: Exhale {report['phase_means']['Exhale']['mean']:.2f} ms,
Inhale {report['phase_means']['Inhale']['mean']:.2f} ms. Its positive Inhale−Exhale
contrast means slower raw RT during inhale.
It is reproduced directly from the released trial labels without a numeric
phase index, and independently checked against the pandas participant cells.

![Baseline-corrected participant pairs and paired phase contrasts](phase_rt.svg)

Grey marks represent the 40 participants; black squares and whiskers are means
and 95% t CIs (39 df). Panel A uses corrected RT and marginal phase-mean CIs. Panel B uses paired
phase-difference CIs: above zero means slower during inhale, below zero faster.
All observations are retained in the axes. No normalization or smoothing.

| Measure | Inhale−Exhale (ms) | Paired 95% CI (ms) | t(39) | Unadjusted two-sided p |
| --- | --- | --- | --- | --- |
{table}

Baseline RT also increases during inhale. Subtraction therefore leaves a small,
inconclusive phase difference. Segment 0 instead shows Baseline−AT **benefit**
by default: its sign is reversed from corrected RT (AT−Baseline), and larger
benefit does not mean a shorter raw RT. These are distinct questions.

These are the existing exploratory primary40 contrasts, not new tests or fits.
P011/P033 are excluded. All conditions and SOAs receive equal weight within each
person's AT summary; matched baseline pools retained trials within condition/phase.
The original exclusions are unchanged. See [exact settings](SPECIFICATION.md),
[participant values](participant_phases.csv), [statistics/runtime](results.json),
and [the complete native family and sensitivities](https://github.com/GeorgeFejer91/Study5_Publication/blob/main/results/baseline_effects/response_tests.csv).
Paired-t assumptions and the saved difference-score Shapiro diagnostics remain
descriptive limitations; no diagnostic selects a different test or cleaning rule.

**Label limit:** this verifies the direction given the scheduled/instructed phase
labels in the released CSV. No respiratory belt recordings are available here to
verify actual physiology or reconstruct acquisition-side labelling. No new causal
or PPS-boundary claim is made. The browser displays the saved native figure.

Software guidance is acknowledged in the [shared software note](../pps_soa/RESULTS.md#software-guidance).
""", encoding="utf-8", newline="\n")
    paths = ["workbook/phase_rt.py", "workbook/paper_analysis.py", "workbook/preparation.py", "workbook/requirements.txt", "results/baseline_effects/response_tests.csv"]
    artifacts = ["SPECIFICATION.md", "RESULTS.md", "participant_phases.csv", "results.json", "phase_rt.svg", "phase_rt.png", "phase_rt.pdf"]
    manifest = dict(classification="exploratory; visualization of existing contrasts", runtime=report["runtime"],
        input_sha256={name: sha256((root/"data/raw"/name).read_bytes()).hexdigest() for name in FILES},
        source_sha256={name: sha256((root/name).read_bytes()).hexdigest() for name in paths},
        artifact_sha256={name: sha256((output/name).read_bytes()).hexdigest() for name in artifacts})
    (output/"manifest.json").write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8", newline="\n")
    print(json.dumps(report["phase_means"]))


if __name__ == "__main__":
    build(Path(__file__).resolve().parents[1])
