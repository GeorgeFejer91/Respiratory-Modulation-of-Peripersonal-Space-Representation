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
TRIAL_GROUPS = [(f"AT {soa:.0f} ms", soa) for soa in SOAS] + [("Baseline", None)]
COLORS = ("#4477AA", "#CC6677", "#117733", "#882255", "#AA4499", "#000000")
MARKERS = ("o", "s", "^", "D", "v", "X")
LINES = ("-", "--", "-.", ":", (0, (5, 1)), (0, (1, 1)))


def trial_group_values(people, trials):
    retained, _, _ = clean(people, trials)
    retained = [r for r in retained if r["participant_id"] not in ("P011", "P033")]
    at = grouped_means([r for r in retained if r["trial_type"] == "Audio-Tactile"],
                       ("participant_id", "condition", "phase", "soa_ms"))
    baseline = grouped_means([r for r in retained if r["trial_type"] == "Baseline"],
                             ("participant_id", "condition", "phase"))
    rows = []
    for pid in sorted({r["participant_id"] for r in retained}):
        for phase in PHASES:
            for group, soa in TRIAL_GROUPS:
                # Named phase keys preserve direction; baseline pools its retained SOAs.
                try:
                    values = [baseline[pid, c, phase] if soa is None else at[pid, c, phase, soa]
                              for c in ("Control", "Viscereality")]
                except KeyError as error:
                    raise ValueError(f"Incomplete phase cells for {pid}: {error}") from error
                rows.append(dict(participant_id=pid, phase=phase, trial_group=group,
                                 reaction_time_ms=float(np.mean(values))))
    return rows


def phase_values(people, trials):
    values = trial_group_values(people, trials)
    lookup = {(r["participant_id"], r["phase"], r["trial_group"]): r["reaction_time_ms"] for r in values}
    rows = []
    for pid in sorted({r["participant_id"] for r in values}):
        for phase in PHASES:
            raw = float(np.mean([lookup[pid, phase, group] for group, soa in TRIAL_GROUPS if soa is not None]))
            base = lookup[pid, phase, "Baseline"]
            rows.append(dict(participant_id=pid, phase=phase, reaction_time_ms=raw,
                             baseline_mean_ms=base, corrected_rt_ms=raw-base))
    return rows


def group_summaries(rows):
    lookup = {(r["participant_id"], r["phase"], r["trial_group"]): r["reaction_time_ms"] for r in rows}
    ids = sorted({r["participant_id"] for r in rows})
    summary, deltas = [], []
    for group, _ in TRIAL_GROUPS:
        exhale = np.array([lookup[pid, "Exhale", group] for pid in ids])
        inhale = np.array([lookup[pid, "Inhale", group] for pid in ids])
        difference = inhale-exhale
        summary.append(dict(trial_group=group, exhale_mean_ms=float(exhale.mean()),
                            inhale_mean_ms=float(inhale.mean()), **describe(difference)))
        deltas.extend(dict(participant_id=pid, trial_group=group, delta_inhale_minus_exhale_ms=float(value))
                      for pid, value in zip(ids, difference))
    return summary, deltas


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
    return dict(phase_means={phase: describe([lookup[pid, phase]["reaction_time_ms"] for pid in ids]) for phase in PHASES},
                contrasts=contrasts, direction="Inhale minus Exhale; positive = slower during inhale")


def build(root):
    output = root / "results/phase_rt"
    people, trials = load_pair(*[(root/"data/raw"/name).read_bytes() for name in FILES])
    audit_release(people, trials)
    rows = phase_values(people, trials)
    report = summarize(rows)
    group_values = trial_group_values(people, trials)
    report["trial_groups"], deltas = group_summaries(group_values)
    report["group_intervals"] = "Six exploratory pointwise 95% t CIs; not simultaneous; no additional p tests"
    report["group_colors"] = dict(zip((g for g, _ in TRIAL_GROUPS), COLORS))
    report["execution"] = "Native Python calculation; browser displays saved results"
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
    summary_csv = [dict(trial_group=s["trial_group"], exhale_mean_ms=s["exhale_mean_ms"], inhale_mean_ms=s["inhale_mean_ms"],
                       delta_inhale_minus_exhale_ms=s["mean"], delta_sd_ms=s["sd"], ci_low_ms=s["ci_low"], ci_high_ms=s["ci_high"], n=s["n"])
                   for s in report["trial_groups"]]
    for name, records in (("participant_trial_groups.csv", group_values), ("trial_group_deltas.csv", deltas),
                          ("trial_group_summary.csv", summary_csv)):
        with (output/name).open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=list(records[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(records)
    (output/"results.json").write_text(json.dumps(report, indent=2, allow_nan=False)+"\n", encoding="utf-8", newline="\n")
    # Outline SVG glyphs so browsers need no locally installed plotting font.
    with plt.rc_context({"font.family": "DejaVu Sans", "font.size": 14, "svg.fonttype": "path", "pdf.fonttype": 42,
                         "svg.hashsalt": "study5-phase-rt", "axes.spines.top": False, "axes.spines.right": False}):
        fig, axes = plt.subplots(2, 1, figsize=(4.6, 8.4), layout="constrained")
        ax = axes[0]
        maximum = 0
        for s, color, marker, line in zip(report["trial_groups"], COLORS, MARKERS, LINES):
            means = [s["exhale_mean_ms"], s["inhale_mean_ms"]]
            ax.plot([0, 1], means, color=color, marker=marker, linestyle=line, linewidth=2, markersize=7)
            maximum = max(maximum, *means)
        ax.set(title="A. Raw RT by Trial Group", ylabel="Mean Reaction Time (ms)",
               xticks=[0, 1], xticklabels=PHASES, xlim=(-.2, 1.2), ylim=(0, maximum*1.10))
        ax = axes[1]
        all_values = []
        for i, (s, color, marker, line) in enumerate(zip(report["trial_groups"], COLORS, MARKERS, LINES)):
            values = np.array([r["delta_inhale_minus_exhale_ms"] for r in deltas if r["trial_group"] == s["trial_group"]])
            all_values.extend(values)
            ax.scatter(values, i+np.linspace(-.18, .05, len(values)), color=color, s=12)
            # Put the estimate below its observations so the CI stays visible.
            ax.plot([0, s["mean"]], [i+.25, i+.25], color=color, linestyle=line, linewidth=1.5)
            ax.errorbar(s["mean"], i+.25, xerr=s["ci_high"]-s["mean"], color=color, marker=marker,
                        markerfacecolor="white", markeredgewidth=1.5, capsize=4, linewidth=2, zorder=3)
        ax.axvline(0, color="black", linestyle="--", linewidth=1)
        labels = [f"{s['trial_group']}\n{s['mean']:+.2f} ms".replace("-", "−") for s in report["trial_groups"]]
        ax.set(title="B. Inhale − Exhale", xlabel="Paired RT Difference (ms)",
               yticks=range(6), yticklabels=labels, ylim=(5.6, -.6))
        # Retain every participant difference and the explicit zero reference.
        lower = min([0, *all_values, *[s["ci_low"] for s in report["trial_groups"]]])
        upper = max([0, *all_values, *[s["ci_high"] for s in report["trial_groups"]]])
        ax.set_xlim(lower-.08*(upper-lower), upper+.08*(upper-lower))
        for extension, options in (("svg", {"metadata": {"Date": None}}), ("png", {"dpi": 300}), ("pdf", {})):
            fig.savefig(output/f"phase_rt.{extension}", facecolor="white", **options)
        plt.close(fig)
    svg = output/"phase_rt.svg"
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines())+"\n", encoding="utf-8", newline="\n")
    table = "\n".join(f"| {MEASURES[m]} | {s['mean']:+.2f} | [{s['ci_low']:.2f}, {s['ci_high']:.2f}] | {s['t']:.3f} | {s['p']:.6f} |" for m, s in report["contrasts"].items())
    means = [report["phase_means"][phase]["mean"] for phase in PHASES]
    group_table = "\n".join(f"| {s['trial_group']} | {s['exhale_mean_ms']:.2f} | {s['inhale_mean_ms']:.2f} | {s['mean']:+.2f} | [{s['ci_low']:.2f}, {s['ci_high']:.2f}] | {s['n']} |" for s in report["trial_groups"])
    (output/"RESULTS.md").write_text(f"""# Segment 2: phase direction by main trial group

Raw AT RT: Exhale **{means[0]:.2f} ms**, Inhale **{means[1]:.2f} ms**.
The positive Inhale−Exhale contrast means slower raw RT during inhale.
It is reproduced directly from the released trial labels without a numeric
phase index, and independently checked against the pandas participant cells.

![Colored trial-group phase means and paired phase deltas](phase_rt.svg)

Panel A shows six raw group-mean phase pairs; colors, markers and line styles
identify the five AT SOAs and pooled Baseline. Panel B uses the same key, shows
every participant's paired delta, with means and pointwise 95% t CIs below the dots
(39 df). Right of zero means slower during inhale; left means faster. No
normalization or smoothing. All plotted observations are retained in the axes.

| Trial group | Exhale M (ms) | Inhale M (ms) | Delta (ms) | Pointwise 95% CI (ms) | n |
| --- | --- | --- | --- | --- | --- |
{group_table}

The six deltas are calculated within each participant before averaging people,
with equal condition weights. Baseline pools retained trials within condition/phase.
The intervals are exploratory and pointwise, not simultaneous; no new six-test
p-value family is added. [Exact group values](participant_trial_groups.csv),
[participant deltas](trial_group_deltas.csv), [summary CSV](trial_group_summary.csv).
Catch trials have no comparable correct-hit target RT and remain excluded.

## Preserved overall reference contrasts

| Measure | Inhale−Exhale (ms) | Paired 95% CI (ms) | t(39) | Unadjusted two-sided p |
| --- | --- | --- | --- | --- |
{table}

Baseline RT also increases during inhale. Subtraction therefore leaves a small,
inconclusive phase difference. Segment 0 instead shows Baseline−AT **benefit**
by default: its sign is reversed from corrected RT (AT−Baseline), and larger
benefit does not mean a shorter raw RT. These are distinct questions.

The overall reference rows are the existing exploratory primary40 contrasts.
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
    paths = ["workbook/phase_rt.py", "workbook/test_phase_groups.py", "workbook/paper_analysis.py", "workbook/preparation.py", "workbook/requirements.txt", "results/baseline_effects/response_tests.csv"]
    artifacts = ["SPECIFICATION.md", "RESULTS.md", "participant_phases.csv", "participant_trial_groups.csv", "trial_group_deltas.csv", "trial_group_summary.csv", "results.json", "phase_rt.svg", "phase_rt.png", "phase_rt.pdf"]
    manifest = dict(classification="exploratory paired trial-group deltas; preserved overall reference contrasts", runtime=report["runtime"],
        input_sha256={name: sha256((root/"data/raw"/name).read_bytes()).hexdigest() for name in FILES},
        source_sha256={name: sha256((root/name).read_bytes()).hexdigest() for name in paths},
        artifact_sha256={name: sha256((output/name).read_bytes()).hexdigest() for name in artifacts})
    (output/"manifest.json").write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8", newline="\n")
    print(json.dumps(report["trial_groups"], indent=2))


if __name__ == "__main__":
    build(Path(__file__).resolve().parents[1])
