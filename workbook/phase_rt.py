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
    group_values = trial_group_values(people, trials)
    report["trial_groups"], deltas = group_summaries(group_values)
    report["group_intervals"] = "Six exploratory pointwise 95% t CIs; not simultaneous; no additional p tests"
    report["group_colors"] = dict(zip((g for g, _ in TRIAL_GROUPS), COLORS))
    report['raincloud'] = {'method':'Gaussian KDE', 'bandwidth':'1.06 × sample SD × n^(−1/5)',
        'support':'trimmed to each observed min/max; equal peak height',
        'box':'median, quartiles and 1.5 IQR whiskers; all observations shown separately',
        'jitter':'deterministic vertical offsets, no measured-value displacement'}
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
    draw_corrected_overall(output, rows, report)
    draw_raincloud(output, report, deltas)
    table = "\n".join(f"| {MEASURES[m]} | {s['mean']:+.2f} | [{s['ci_low']:.2f}, {s['ci_high']:.2f}] | {s['t']:.3f} | {s['p']:.6f} |" for m, s in report["contrasts"].items())
    means = [report["phase_means"][phase]["mean"] for phase in PHASES]
    group_table = "\n".join(f"| {s['trial_group']} | {s['exhale_mean_ms']:.2f} | {s['inhale_mean_ms']:.2f} | {s['mean']:+.2f} | [{s['ci_low']:.2f}, {s['ci_high']:.2f}] | {s['n']} |" for s in report["trial_groups"])
    (output/"RESULTS.md").write_text(f"""# Segment 2: phase direction by main trial group

Primary baseline-corrected RT (AT − matched Baseline): Exhale **{report['corrected_phase_means']['Exhale']['mean']:.2f} ms**,
Inhale **{report['corrected_phase_means']['Inhale']['mean']:.2f} ms**. The corrected phase contrast remains inconclusive.
Raw AT RT is a labelled reference: Exhale {report['phase_means']['Exhale']['mean']:.2f} ms,
Inhale {report['phase_means']['Inhale']['mean']:.2f} ms. Its positive Inhale−Exhale
contrast means slower raw RT during inhale.
It is reproduced directly from the released trial labels without a numeric
phase index, and independently checked against the pandas participant cells.

![Primary baseline-corrected phase means and overall contrasts](phase_rt.svg)

The primary figure shows corrected participant pairs, marginal mean 95% t CIs,
and paired overall contrasts. Its zero references retain all negative values.

## Main visualization: six raw trial-group rainclouds

![Colored raw trial-group phase means and paired phase deltas](phase_raw_groups.svg)

Six horizontal rainclouds show all 40 participant deltas per trial group. Half
violins use Gaussian KDE with bandwidth 1.06 × sample SD × n^(−1/5), trimmed to
the observed range and scaled to equal peak height. Smoothing is descriptive.
Boxes show median/quartiles and 1.5-IQR whiskers; every observed point is retained.
Hollow markers below the dots show the mean and the original pointwise 95% t CI
(39 df). Right of zero means slower during inhale; left means faster. Vertical
offsets separate marks without changing values. No RT normalization is applied.
The browser renders HTML/SVG charts directly from the saved data, with exact-value
click/tap boxes. SVG/PNG/PDF files are static download alternatives.
The owner selected this raw-delta display as the main visual; corrected inference
and its overall plot remain available separately.

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
    artifacts = ["SPECIFICATION.md", "RESULTS.md", "participant_phases.csv", "participant_trial_groups.csv", "trial_group_deltas.csv", "trial_group_summary.csv", "results.json", "phase_rt.svg", "phase_rt.png", "phase_rt.pdf", "phase_raw_groups.svg", "phase_raw_groups.png", "phase_raw_groups.pdf"]
    manifest = dict(classification="exploratory paired trial-group deltas; preserved overall reference contrasts", runtime=report["runtime"],
        input_sha256={name: sha256((root/"data/raw"/name).read_bytes()).hexdigest() for name in FILES},
        source_sha256={name: sha256((root/name).read_bytes()).hexdigest() for name in paths},
        artifact_sha256={name: sha256((output/name).read_bytes()).hexdigest() for name in artifacts})
    (output/"manifest.json").write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8", newline="\n")
    print(json.dumps(report["trial_groups"], indent=2))


def raincloud_density(values):
    values = np.asarray(values, dtype=float)
    if len(values) < 3 or not np.isfinite(values).all() or values.std(ddof=1) <= 0:
        return None
    bandwidth = float(1.06 * values.std(ddof=1) * len(values)**(-.2))
    grid = np.linspace(values.min(), values.max(), 49)
    density = stats.gaussian_kde(values, bw_method=1.06*len(values)**(-.2))(grid)
    return grid, density, bandwidth


def draw_raincloud(output, report, deltas):
    with plt.rc_context({'font.family':'DejaVu Sans','font.size':13,'svg.fonttype':'path','pdf.fonttype':42,
                         'svg.hashsalt':'study5-phase-raincloud','axes.spines.top':False,'axes.spines.right':False}):
        fig, ax = plt.subplots(figsize=(7.6,6.8),layout='constrained')
        for i,(summary,color,marker) in enumerate(zip(report['trial_groups'],COLORS,MARKERS)):
            records=[r for r in deltas if r['trial_group']==summary['trial_group']]
            values=np.array([r['delta_inhale_minus_exhale_ms'] for r in records])
            cloud=raincloud_density(values)
            if cloud is not None:
                grid,density,_=cloud
                ax.fill_between(grid,i-.08,i-.08-.4*density/density.max(),color=color,alpha=.22,edgecolor=color,lw=1)
            ax.boxplot([values],positions=[i+.02],orientation='horizontal',widths=.09,showfliers=False,whis=1.5,
                       manage_ticks=False,patch_artist=True,boxprops={'facecolor':'white','edgecolor':color},
                       medianprops={'color':color,'linewidth':2},whiskerprops={'color':color},capprops={'color':color})
            ax.scatter(values,i+np.linspace(.14,.32,len(values)),color=color,s=15)
            ax.errorbar(summary['mean'],i+.48,xerr=summary['ci_high']-summary['mean'],color=color,
                            marker=marker,markerfacecolor='white',markeredgewidth=1.5,capsize=4,linewidth=2)
        ax.axvline(0,color='black',ls='--',lw=1)
        labels=[f"{r['trial_group']}\n{r['mean']:+.2f} ms".replace('-','−') for r in report['trial_groups']]
        ax.set(title='Inhale − Exhale',xlabel='Paired RT Difference (ms)',yticks=range(6),yticklabels=labels,ylim=(5.78,-.65))
        all_values=[r['delta_inhale_minus_exhale_ms'] for r in deltas]
        low,high=min(0,*all_values),max(0,*all_values)
        ax.set_xlim(low-.07*(high-low),high+.07*(high-low))
        fig.savefig(output/'phase_raw_groups.svg',facecolor='white',metadata={'Date':None})
        fig.savefig(output/'phase_raw_groups.png',dpi=300,facecolor='white')
        fig.savefig(output/'phase_raw_groups.pdf',facecolor='white')
        plt.close(fig)
    svg=output/'phase_raw_groups.svg'
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8',newline='\n')


def draw_corrected_overall(output, rows, report):
    """Preserve the concurrently requested primary corrected-RT display."""
    lookup = {(r["participant_id"], r["phase"]): r for r in rows}
    ids = sorted({r["participant_id"] for r in rows})
    corrected = np.array([[lookup[pid, phase]["corrected_rt_ms"] for phase in PHASES] for pid in ids])
    with plt.rc_context({"font.family":"DejaVu Sans", "font.size":14, "svg.fonttype":"path", "pdf.fonttype":42,
                         "svg.hashsalt":"study5-phase-rt", "axes.spines.top":False, "axes.spines.right":False}):
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
        all_values = []
        for i, measure in enumerate(MEASURES):
            values = np.array([lookup[pid, "Inhale"][measure]-lookup[pid, "Exhale"][measure] for pid in ids])
            all_values.extend(values)
            s = report["contrasts"][measure]
            ax.scatter(i+np.linspace(-.13, .13, len(ids)), values, color="#666666", alpha=.8, s=16)
            ax.errorbar(i, s["mean"], yerr=s["ci_high"]-s["mean"], color="black", marker="s", capsize=5, linewidth=2, zorder=3)
        ax.axhline(0, color="black", linestyle="--", linewidth=1)
        labels = [f"{name}\n{report['contrasts'][measure]['mean']:+.2f} ms".replace("-", "−")
                  for measure, name in zip(MEASURES, ("Raw AT", "Baseline", "AT −\nBaseline"))]
        ax.set(title="B. Inhale − Exhale", ylabel="Paired RT Difference (ms)", xticks=range(3), xticklabels=labels, xlim=(-.5, 2.5))
        lower = min([0, *all_values, *[s["ci_low"] for s in report["contrasts"].values()]])
        upper = max([0, *all_values, *[s["ci_high"] for s in report["contrasts"].values()]])
        ax.set_ylim(lower-.08*(upper-lower), upper+.08*(upper-lower))
        for extension, options in (("svg", {"metadata":{"Date":None}}), ("png", {"dpi":300}), ("pdf", {})):
            fig.savefig(output/f"phase_rt.{extension}", facecolor="white", **options)
        plt.close(fig)
    svg = output/"phase_rt.svg"
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines())+"\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    build(Path(__file__).resolve().parents[1])
