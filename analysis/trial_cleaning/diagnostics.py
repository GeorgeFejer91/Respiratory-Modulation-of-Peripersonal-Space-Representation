"""Every-trial distribution plots and fixed time-on-task diagnostics."""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pandas as pd
from scipy import stats

from run import (OUT, ROOT, source, prepare, tensors, directional, X, W, EFFECTS,
                 CELL_NAMES, SOA_DISTANCE, write_csv, write_json, test_batch,
                 interaction, safe_call)


def time_slope(rt, distance, position):
    """Within-distance linear time trend; coefficient is ms per observed span."""
    rt, distance, position = map(np.asarray, (rt, distance, position))
    y, t = rt.astype(float).copy(), position.astype(float).copy()
    for d in np.unique(distance):
        index = distance == d
        y[index] -= y[index].mean()
        t[index] -= t[index].mean()
    return float(t@y/(t@t)) if t@t > 1e-12 else np.nan


def residual_sd(rows):
    if not len(rows):
        return np.nan
    groups = rows.groupby("soa_ms").rt
    residuals = rows.rt-groups.transform("mean")
    df = len(rows)-rows.soa_ms.nunique()
    return float(np.sqrt(np.sum(residuals**2)/df)) if df > 0 else np.nan


def main():
    people, trials, eligible, old, ids, old_counts = source()
    audit = pd.DataFrame(trials)
    audit["primary_inference"] = audit.participant_id.isin(ids)
    audit["eligible_hit"] = audit.trial_id.isin({r["trial_id"] for r in eligible})
    selections, counts, cell_records = {}, [], []
    for early in (False, True):
        period = "early" if early else "full"
        rows, glob, local = prepare(eligible, early)
        global_ids, local_ids = set(glob.loc[glob.keep, "trial_id"]), {r["trial_id"] for r in rows}
        audit[period+"_global_keep"] = audit.trial_id.isin(global_ids)
        audit[period+"_local_keep"] = audit.trial_id.isin(local_ids)
        for label, detail in (("global", glob), ("local", local)):
            detail = detail.set_index("trial_id")
            for field in ("mean_ms", "sd_ms", "n", "z"):
                audit[period+"_"+label+"_"+field] = audit.trial_id.map(detail[field])
        for label, selected in (("global", [r for r in eligible if r["trial_id"] in global_ids]), ("local", rows)):
            selections[period+"_"+label] = selected
            for cohort, roster in (("full42", {p["participant_id"] for p in people}), ("primary40", set(ids))):
                selected_primary = [r for r in selected if r["participant_id"] in roster]
                at, baseline = tensors(selected_primary, sorted(roster))
                counts.append(dict(period=period, filter=label, cohort=cohort,
                    AT=int(np.isfinite(at).sum()), Baseline=int(np.isfinite(baseline).sum()),
                    missing_AT_distance_cells=int(np.sum(np.isfinite(at).sum(-1) == 0)),
                    missing_Baseline_distance_cells=int(np.sum(np.isfinite(baseline).sum(-1) == 0))))
            at, baseline = tensors(selected, ids)
            for kind, tensor in (("AT", at), ("Baseline", baseline)):
                n, mean, sse = directional.sufficient(tensor)
                for i, pid in enumerate(ids):
                    for c, cell in enumerate(CELL_NAMES):
                        for d, distance in enumerate(X):
                            number = int(n[i, c, d])
                            cell_records.append(dict(period=period, filter=label, participant_id=pid,
                                cell=cell, trial_type=kind, distance_cm=distance, n=number,
                                mean_ms=mean[i, c, d] if number else None,
                                sd_ms=np.sqrt(sse[i, c, d]/(number-1)) if number > 1 else None))
    audit.to_csv(OUT / "trial_audit.csv", index=False)
    write_csv(OUT / "retained_counts.csv", counts)
    write_csv(OUT / "distance_distributions.csv", cell_records)
    write_json(OUT / "original_counts.json", old_counts)
    rt_diagnostics, rt_values, rt_meta = [], [], []
    for name, selected in selections.items():
        at, baseline = tensors(selected, ids)
        curve = np.nanmean(at, -1)-np.nanmean(baseline.reshape(len(ids), 4, -1), -1)[..., None]
        for quantity, values in (("mean_corrected_RT_ms", curve.mean(-1)),
                                  ("far_minus_near_ms", curve[..., -1]-curve[..., 0])):
            for term, contrast in zip(EFFECTS[:3], W[:3]):
                rt_values.append(values@contrast)
                rt_meta.append(dict(dataset=name, quantity=quantity, term=term))
        rt_values.append(curve.mean((1, 2)))
        rt_meta.append(dict(dataset=name, quantity="mean_corrected_RT_ms", term="AT-minus-Baseline"))
    write_csv(OUT / "response_tests.csv", test_batch(np.column_stack(rt_values), rt_meta))
    for period in ("full", "early"):
        selected = [r for r in selections[period+"_local"] if r["participant_id"] in ids]
        for control in (False, True):
            name = period+("_control" if control else "_factorial")
            result = safe_call(interaction, name, selected, control=control, label=name)
            rt_diagnostics.append(dict(dataset=period+"_local", **result))
    write_json(OUT / "registered_RT_models.json", rt_diagnostics)

    frame = pd.DataFrame(trials)
    frame = frame[frame.participant_id.isin(ids)].copy()
    for field in ("trial_index", "block_number", "soa_ms"):
        frame[field] = pd.to_numeric(frame[field], errors="coerce")
    frame["rt"] = pd.to_numeric(frame.reaction_time_ms, errors="coerce")
    span = frame.groupby(["participant_id", "condition"]).trial_index
    frame["position"] = (frame.trial_index-span.transform("min"))/(span.transform("max")-span.transform("min"))
    frame["kept"] = frame.trial_id.isin({r["trial_id"] for r in selections["full_local"]})
    frame["early"] = frame.block_number <= 3
    frame["cell"] = frame.condition+" "+frame.phase
    time_records, period_records = [], []
    for pid in ids:
        for cell in CELL_NAMES:
            cell_frame = frame[(frame.participant_id == pid) & (frame.cell == cell)]
            record = dict(participant_id=pid, cell=cell)
            for kind, short in (("Audio-Tactile", "AT"), ("Baseline", "Baseline")):
                kept = cell_frame[cell_frame.kept & (cell_frame.trial_type == kind)]
                record[short+"_RT_time_slope_ms"] = time_slope(kept.rt, kept.soa_ms, kept.position)
                half_values = []
                for early in (True, False):
                    all_rows = cell_frame[(cell_frame.trial_type == kind) & (cell_frame.early == early)]
                    values = all_rows[all_rows.kept]
                    means = values.groupby("soa_ms").rt.mean()
                    half_values.append(dict(mean=means, sd=residual_sd(values),
                        miss=float((all_rows.outcome == "miss").mean())))
                    period_records.append(dict(participant_id=pid, cell=cell, trial_type=short,
                        period="blocks1-3" if early else "blocks4-6", trials=len(all_rows),
                        retained_RT=len(values), distance_cells=len(means), residual_sd_ms=residual_sd(values),
                        miss_rate=float((all_rows.outcome == "miss").mean())))
                common = half_values[0]["mean"].index.intersection(half_values[1]["mean"].index)
                record[short+"_late_minus_early_RT_ms"] = float((half_values[1]["mean"][common]-half_values[0]["mean"][common]).mean())
                record[short+"_late_minus_early_SD_ms"] = half_values[1]["sd"]-half_values[0]["sd"]
                record[short+"_late_minus_early_miss_rate"] = half_values[1]["miss"]-half_values[0]["miss"]
            catches = cell_frame[cell_frame.trial_type == "Catch"]
            record["Catch_late_minus_early_false_alarm_rate"] = float(
                (catches[~catches.early].outcome == "false_alarm").mean()-(catches[catches.early].outcome == "false_alarm").mean())
            time_records.append(record)
    time_frame = pd.DataFrame(time_records)
    time_frame.to_csv(OUT / "participant_time_trends.csv", index=False)
    write_csv(OUT / "time_period_quality.csv", period_records)
    trend_tests = []
    for quantity in time_frame.columns[2:]:
        a = time_frame.pivot(index="participant_id", columns="cell", values=quantity).loc[ids, CELL_NAMES].values
        complete = np.isfinite(a).all(1)
        excluded = ",".join(np.asarray(ids)[~complete])
        a = a[complete]
        values, metadata = [], []
        for term, weights in zip(("Average", *EFFECTS[:3]), np.vstack([np.ones(4)/4, W[:3]])):
            values.append(a@weights)
            metadata.append(dict(quantity=quantity, term=term, complete_participants=len(a),
                                 incomplete_participants=excluded))
        if len(a) >= 3:
            trend_tests.extend(test_batch(np.column_stack(values), metadata))
        else:
            trend_tests.extend(dict(**m, status="not_estimable") for m in metadata)
    write_csv(OUT / "time_trend_tests.csv", trend_tests)
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "pdf.fonttype": 42})
    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    plot_specs = [("Audio-Tactile", "rt", "AT RT (ms)"), ("Baseline", "rt", "Baseline RT (ms)"),
                  ("Audio-Tactile", "miss", "AT miss rate"), ("Catch", "false", "Catch false-alarm rate")]
    colors = ["#215A8E", "#387C9B", "#B24C22", "#D37824"]
    for ax, (kind, field, title) in zip(axes.flat, plot_specs):
        for cell, color in zip(CELL_NAMES, colors):
            part = frame[(frame.cell == cell) & (frame.trial_type == kind)].copy()
            if field == "rt":
                part = part[part.kept]
                part["value"] = part.rt
            else:
                part["value"] = (part.outcome == ("miss" if field == "miss" else "false_alarm")).astype(float)
            individual = part.groupby(["participant_id", "block_number"]).value.mean().unstack("block_number")
            mean = individual.mean()
            if field == "rt":
                error = individual.sem()*stats.t.ppf(.975, individual.count()-1)
            else:
                rng = np.random.default_rng(20261520)
                a = individual.to_numpy()
                weights = rng.multinomial(len(a), np.full(len(a), 1/len(a)), 4999)
                boot = (weights@np.nan_to_num(a))/(weights@np.isfinite(a))
                low, high = np.quantile(boot, [.025, .975], axis=0)
                error = np.vstack([mean.to_numpy()-low, high-mean.to_numpy()])
            ax.errorbar(mean.index, mean, yerr=error, color=color, marker="o", ms=3, label=cell, lw=1)
        ax.set(title=title, xlabel="Block within intervention", xticks=range(1, 7))
        ax.axvline(3.5, ls=":", color="#777777")
    axes[0, 0].legend(fontsize=8)
    fig.suptitle("Observed time course: full-session cleaning; equal participant weight")
    fig.text(.5, .01, "RT intervals: participant t intervals; rate intervals: 4,999 whole-person bootstrap draws.\n"
        "Time trends can reflect practice, stimulus differences or fatigue; they do not establish a cause.", ha="center", fontsize=8)
    fig.tight_layout(rect=(0, .035, 1, .95))
    fig.savefig(OUT / "time_course.png", dpi=170)
    fig.savefig(OUT / "time_course.pdf")
    plt.close(fig)

    eligible_frame = audit[audit.eligible_hit].copy()
    eligible_frame["distance_cm"] = eligible_frame.soa_ms.astype(float).map(SOA_DISTANCE)
    eligible_frame["rt"] = eligible_frame.reaction_time_ms.astype(float)
    keys = ["participant_id", "condition", "phase", "soa_ms", "trial_type"]
    local_stats = eligible_frame[eligible_frame.full_global_keep][keys+["full_local_mean_ms", "full_local_sd_ms", "full_local_n"]].drop_duplicates(keys)
    eligible_frame = eligible_frame.drop(columns=["full_local_mean_ms", "full_local_sd_ms", "full_local_n"]).merge(local_stats, on=keys, how="left")
    eligible_frame["full_local_reference_z"] = (eligible_frame.rt-eligible_frame.full_local_mean_ms)/eligible_frame.full_local_sd_ms
    reference_z = eligible_frame.set_index("trial_id").full_local_reference_z
    audit["full_local_reference_z"] = audit.trial_id.map(reference_z)
    audit.to_csv(OUT / "trial_audit.csv", index=False)
    plot_rng = np.random.default_rng(20261020)
    plotted = []
    with PdfPages(OUT / "every_trial_distributions.pdf") as pdf:
        for person in people:
            pid = person["participant_id"]
            fig, axes = plt.subplots(4, 2, figsize=(16, 17))
            for c, cell in enumerate(CELL_NAMES):
                condition, phase = cell.split()
                for col, kind in enumerate(("Audio-Tactile", "Baseline")):
                    ax = axes[c, col]
                    group = eligible_frame[(eligible_frame.participant_id == pid) &
                        (eligible_frame.condition == condition) & (eligible_frame.phase == phase) & (eligible_frame.trial_type == kind)]
                    for distance in X:
                        points = group[group.distance_cm == distance].sort_values("trial_id")
                        if not len(points):
                            continue
                        if len(points) > 1 and points.rt.std() > 0:
                            violin = ax.violinplot(points.rt.values, positions=[distance], widths=11, showextrema=False)
                            violin["bodies"][0].set(facecolor="#B5C8D3", edgecolor="none", alpha=.35)
                        mean, sd = points.full_local_mean_ms.iloc[0], points.full_local_sd_ms.iloc[0]
                        if np.isfinite(sd):
                            ax.vlines(distance, mean-2.5*sd, mean+2.5*sd, color="#777777", lw=.7)
                            ax.plot([distance-3, distance+3], [mean]*2, color="#333333", lw=1.2)
                        ax.text(distance, .98, f"n={len(points)}→{int(points.full_local_keep.sum())}\nμ={mean:.0f}, s={sd:.0f}",
                                transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=6.5)
                        offsets = plot_rng.permutation(np.linspace(-4, 4, len(points)))
                        for offset, row in zip(offsets, points.itertuples(index=False)):
                            plotted.append(row.trial_id)
                            color = "#B3261E" if not row.full_global_keep else ("#CF7900" if not row.full_local_keep else "#215A8E")
                            ax.plot(distance+offset, row.rt, "o", color=color, ms=3.2)
                            z = (row.rt-mean)/sd if np.isfinite(sd) and sd > 0 else np.nan
                            fallback = not np.isfinite(z)
                            z = row.full_global_z if fallback else z
                            ax.annotate(("g" if fallback else "")+f"{z:+.1f}" if np.isfinite(z) else "NA",
                                (distance+offset, row.rt), xytext=(2, 2), textcoords="offset points", fontsize=5.4, color=color)
                    lo, hi = group.rt.min(), group.rt.max()
                    span = max(150, hi-lo)
                    ax.set(title=f"{cell} — {kind}", xlim=(1, 109), xticks=X, ylim=(lo-.08*span, hi+.27*span),
                           xlabel="Physical distance (cm)", ylabel="Individual recorded hit RT (ms)")
            status = "included in primary40 inference" if pid in ids else "excluded from primary40: unresolved recording linkage"
            fig.suptitle(f"{pid}: every eligible hit, with violins and standardized deviations\n{status}", fontsize=14)
            fig.text(.5, .018, "Blue: retained. Red: original global exclusion. Orange: additional local exclusion. Every point is one eligible recorded hit.\n"
                "Labels are local z scores using global-retained reference means/SDs; g denotes global z fallback. n shows eligible→retained.\n"
                "Grey ranges: local μ ±2.5 sample SD. Horizontal jitter is layout only. Misses/catches and missing RTs remain in the separate audit. No visual cutoff tuning.",
                ha="center", fontsize=8)
            fig.tight_layout(rect=(0, .065, 1, .945))
            pdf.savefig(fig)
            if pid == "P000":
                fig.savefig(OUT / "every_trial_example.png", dpi=130)
            plt.close(fig)
    assert len(plotted) == len(eligible) and set(plotted) == {r["trial_id"] for r in eligible}
    write_json(OUT / "trial_plot_checks.json", dict(pages=len(people), eligible_hits=len(eligible),
        plotted_hits=len(plotted), every_eligible_hit_plotted_exactly_once=True,
        horizontal_jitter="fixed-seed layout independent of RT value"))
    print("Prepared all 42 trial pages, fatigue/quality checks and four registered RT refits.", flush=True)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    main()
