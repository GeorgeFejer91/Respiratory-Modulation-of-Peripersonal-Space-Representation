"""Exploratory chronological-block RT analysis; results/block_rt/SPECIFICATION.md."""
import argparse
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
import platform
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "workbook"))
from preparation import FILES, audit_release, load_pair
from paper_analysis import clean

OUT = ROOT / "results/block_rt"
SEED = 20261023
TERMS = ("linear_ms_per_block", "quadratic_ms_per_block_squared", "condition_adjusted_ms_per_block")


def block(row):
    return 6 * (int(row["part_number"]) - 1) + int(row["block_number"])


def coefficients(means, conditions):
    x = np.arange(1., 13.) - 6.5
    linear = np.linalg.lstsq(np.column_stack([np.ones(12), x]), means, rcond=None)[0][1]
    quadratic = np.linalg.lstsq(np.column_stack([np.ones(12), x, x*x]), means, rcond=None)[0][2]
    adjusted = np.linalg.lstsq(np.column_stack([np.ones(12), x, conditions]), means, rcond=None)[0][1]
    return linear, quadratic, adjusted


def describe(values):
    a = np.asarray(values, dtype=float)
    mean, sd = float(a.mean()), float(a.std(ddof=1))
    se = sd / np.sqrt(len(a))
    half = float(stats.t.ppf(.975, len(a)-1)*se)
    return dict(n=len(a), mean_ms=mean, sd_ms=sd, se_ms=float(se),
                ci_low_ms=mean-half, ci_high_ms=mean+half, median_ms=float(np.median(a)))


def inference(values):
    a = np.asarray(values, dtype=float)
    r = describe(a)
    test = stats.ttest_1samp(a, 0)
    r.update(t=float(test.statistic), df=len(a)-1, p=float(test.pvalue),
             dz=float(a.mean()/a.std(ddof=1)), shapiro_p=float(stats.shapiro(a).pvalue),
             loo_mean_min=float(min((a.sum()-a)/(len(a)-1))),
             loo_mean_max=float(max((a.sum()-a)/(len(a)-1))))
    rng = np.random.default_rng(SEED)
    boot = a[rng.integers(0, len(a), size=(9999, len(a)))].mean(axis=1)
    r["bootstrap_ci_low"], r["bootstrap_ci_high"] = map(float, np.quantile(boot, [.025, .975]))
    return r


def prepare(people, trials):
    retained, quality, counts = clean(people, trials)
    orders = {p["participant_id"]: p["condition_order"] for p in people}
    for row in trials:
        b = block(row)
        assert 1 <= b <= 12
        assert b == (int(row["trial_index"])-1)//34 + 1
        assert row["condition"] == orders[row["participant_id"]].split("-")[int(row["part_number"])-1]
    groups = defaultdict(list)
    for row in retained:
        if row["trial_type"] == "Audio-Tactile":
            groups[(row["participant_id"], block(row), row["condition"])].append(float(row["reaction_time_ms"]))
    records = [dict(participant_id=pid, session_block=b, condition=c, condition_order=orders[pid],
                    retained_trials=len(a), mean_rt_ms=float(np.mean(a))) for (pid, b, c), a in sorted(groups.items())]
    return pd.DataFrame(records), quality, counts, retained


def analyze(frame, excluded):
    part = frame[~frame.participant_id.isin(excluded)]
    wide = part.pivot(index="participant_id", columns="session_block", values="mean_rt_ms").reindex(columns=range(1, 13))
    incomplete = wide.index[wide.isna().any(axis=1)].tolist()
    wide = wide.dropna()
    if len(wide) < 3:
        raise ValueError("At least three complete participants are required")
    participant = []
    for pid, row in wide.iterrows():
        conditions = part[part.participant_id == pid].sort_values("session_block").condition.eq("Viscereality").to_numpy(dtype=float)
        participant.append(dict(participant_id=pid, **dict(zip(TERMS, coefficients(row.to_numpy(), conditions))),
                                endpoint_ms=float(row[12]-row[1])))
    slopes = pd.DataFrame(participant)
    summary = [dict(session_block=int(b), **describe(a)) for b, a in wide.items()]
    report = dict(excluded_linkage=list(excluded), participant_ids=wide.index.tolist(),
                  incomplete_excluded=incomplete, summary=summary,
                  tests={term: inference(slopes[term]) for term in TERMS},
                  endpoint=describe(slopes.endpoint_ms),
                  retained_at=int(part[part.participant_id.isin(wide.index)].retained_trials.sum()))
    return report, wide, slopes


def build():
    people, trials = load_pair(*[(ROOT / "data/raw" / name).read_bytes() for name in FILES])
    audit_release(people, trials)
    frame, quality, counts, _ = prepare(people, trials)
    report, wide, slopes = analyze(frame, ("P011", "P033"))
    report.update(classification="exploratory", execution="native Python; no browser execution",
                  cleaning_counts_full_release=counts, participant_quality=quality, bootstrap_seed=SEED)
    observed = frame[~frame.participant_id.isin(("P011", "P033"))]
    report["available_primary40_descriptive"] = [dict(session_block=int(b), **describe(a.mean_rt_ms))
        for b, a in observed.groupby("session_block")]
    report["linkage_sensitivities"] = [analyze(frame, excluded)[0] for excluded in (("P011",), ("P033",))]
    # Full-release output is descriptive because two records share one recording.
    full = frame.pivot(index="participant_id", columns="session_block", values="mean_rt_ms").dropna()
    report["full42_descriptive"] = [dict(session_block=int(b), **describe(a)) for b, a in full.items()]
    report["runtime"] = dict(python=platform.python_version(), numpy=np.__version__, pandas=pd.__version__,
                             scipy=scipy.__version__, matplotlib=matplotlib.__version__)
    frame.to_csv(OUT / "participant_blocks.csv", index=False, lineterminator="\n")
    slopes.to_csv(OUT / "participant_coefficients.csv", index=False, lineterminator="\n")
    pd.DataFrame(report["summary"]).to_csv(OUT / "summary.csv", index=False, lineterminator="\n")
    pd.DataFrame(report["available_primary40_descriptive"]).to_csv(OUT / "available_primary40_summary.csv", index=False, lineterminator="\n")
    (OUT / "results.json").write_text(json.dumps(report, indent=2, allow_nan=False)+"\n", encoding="utf-8", newline="\n")
    with plt.rc_context({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False,
                         "svg.fonttype": "none", "svg.hashsalt": "study5-block-rt"}):
        fig, ax = plt.subplots(figsize=(8.6, 5.2), layout="constrained")
        x = np.arange(1, 13)
        styles = {"Control": ("#005a9c", "-"), "Viscereality": ("#ba2525", "--")}
        # Color each actual intervention segment, independent of presentation order.
        for pid, values in wide.iterrows():
            person = frame[frame.participant_id == pid].set_index("session_block")
            for start in (1, 7):
                blocks = np.arange(start, start+6)
                condition = person.loc[start, "condition"]
                assert person.loc[blocks, "condition"].nunique() == 1
                color, linestyle = styles[condition]
                line, = ax.plot(blocks, values.loc[blocks], color=color, linestyle=linestyle, alpha=.45, lw=.9)
                line.set_gid(f"trajectory-{pid}-{start}-{condition}")
        for condition, (color, linestyle) in styles.items():
            ax.plot([], [], color=color, linestyle=linestyle, lw=1.5, label=condition)
        means = wide.mean().to_numpy()
        half = stats.t.ppf(.975, len(wide)-1)*wide.sem().to_numpy()
        ax.errorbar(x, means, yerr=half, color="black", marker="o", capsize=3, lw=2,
                         label=f"Equal-person mean, N={len(wide)}")
        ax.axvline(6.5, color="#555555", ls=":", lw=1)
        ax.set(xlabel="Chronological block (condition switch after block 6)", xticks=x, xlim=(.65, 12.35),
               ylabel="Audio–Tactile RT (ms)", ylim=(0, wide.to_numpy().max()*1.07),
               title="Participant reaction times across consecutive conditions")
        ax.legend(frameon=False, fontsize=10, loc="lower left")
        for extension in ("png", "svg"):
            fig.savefig(OUT / f"block_rt.{extension}", dpi=220, facecolor="white", metadata={"Date": None} if extension == "svg" else None)
        svg = OUT / "block_rt.svg"
        svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines())+"\n", encoding="utf-8", newline="\n")
        plt.close(fig)
        fig, axes = plt.subplots(1, 3, figsize=(11, 3.7), layout="constrained")
        for ax, term in zip(axes, TERMS):
            stats.probplot(slopes[term], plot=ax)
            ax.axhline(0, color="#555555", ls=":", lw=.7)
            ax.set_title(term.replace("_", " "), fontsize=9)
        fig.savefig(OUT / "diagnostics.png", dpi=160, facecolor="white")
        plt.close(fig)
    lines = ["# Does average RT decline across blocks?", "", "**The analysis does not establish a systematic RT decline across the session.**", "",
             "Exploratory native analysis; original cleaning and primary40. Both conditions occurred consecutively.", "",
             f"N = {len(wide)} participants, {report['retained_at']} retained AT trials. Incomplete-block exclusions: {report['incomplete_excluded'] or 'none'}.", "",
             "![Participant RT trajectories across 12 chronological blocks: blue solid Control segments, red dashed Viscereality segments, and black overall means](block_rt.png)", "",
             "Blue solid lines are participant block means during Control; red dashed lines show Viscereality. Each person's segments use their actual condition in that part of the session and stop at the switch between blocks 6/7. Black points are equal-person means; intervals are pointwise marginal 95% t CIs, not paired-change CIs. The vertical dotted line marks the switch. No smoothing, normalization or baseline subtraction. Zero-based y-axis. Underlying observations and retained-trial counts: participant_blocks.csv. Owner-requested figure-only amendment: replace the order-group panel with condition-colored participant trajectories; statistical results are unchanged.", "",
             f"| Test | Mean coefficient | 95% t CI | t({len(wide)-1}) | Two-sided p | dz | Bootstrap 95% CI |", "| --- | ---: | --- | ---: | ---: | ---: | --- |"]
    for term, r in report["tests"].items():
        lines.append(f"| {term} | {r['mean_ms']:.3f} | [{r['ci_low_ms']:.3f}, {r['ci_high_ms']:.3f}] | {r['t']:.3f} | {r['p']:.6f} | {r['dz']:.3f} | [{r['bootstrap_ci_low']:.3f}, {r['bootstrap_ci_high']:.3f}] |")
    e = report["endpoint"]
    lines += ["", f"Paired block 12 minus block 1: {e['mean_ms']:.2f} ms, 95% CI [{e['ci_low_ms']:.2f}, {e['ci_high_ms']:.2f}]. No separate endpoint p test.", "",
              "Negative linear coefficients indicate speeding; positive indicate slowing. Quadratic coefficients are in ms/block² and describe curvature, not a monotonic decrease. The condition-adjusted coefficient estimates within-condition change assuming a shared linear slope and a level shift at the switch. Unadjusted exploratory p values for the full three-test family follow the owner's policy; all CIs are pointwise.", "",
              "## Block means", "", "| Block | Mean ms | SD ms | n | 95% CI ms |", "| --- | ---: | ---: | ---: | --- |"]
    lines += [f"| {r['session_block']} | {r['mean_ms']:.2f} | {r['sd_ms']:.2f} | {r['n']} | [{r['ci_low_ms']:.2f}, {r['ci_high_ms']:.2f}] |" for r in report["summary"]]
    lines += ["", "The descriptive table above uses the same 39 complete participants at every block. To retain every available person, available_primary40_summary.csv separately includes all 40 primary participants wherever observed (n=39 at block 7, n=40 otherwise). This descriptive companion was added after observing the missing block; the inferential specification was unchanged.", "",
              "## Sensitivities and limits", ""]
    for s in report["linkage_sensitivities"]:
        r = s["tests"][TERMS[0]]
        lines.append(f"- Excluding {s['excluded_linkage']}: n={r['n']}, linear slope {r['mean_ms']:.3f} ms/block, 95% CI [{r['ci_low_ms']:.3f}, {r['ci_high_ms']:.3f}], p={r['p']:.6f}. All three tests are retained in results.json.")
    lines += ["", "P008 has no retained AT responses in chronological block 7 (18 misses and two hits with missing RT) and is excluded only from complete-block inference; their other block means remain in participant_blocks.csv and the available40 table. P016 has a partial recorded session but usable RTs in every block and is retained. Complete-case inference does not correct informative missing responses or misses. Full42 descriptive means are in results.json; it is not 42 independent recordings. Original participant/trial exclusions and missingness counts are preserved there. Pooling retained trials can reflect changing phase/SOA composition; condition order, practice, carryover and fatigue are not causally separated. Block number is not elapsed time. These results concern overall RT, not a drift-diffusion parameter or a PPS boundary.", "",
              "All three participant-coefficient Q–Q plots are in diagnostics.png. The linear and adjusted slopes show moderate tail deviations; quadratic coefficients include a strong lower-tail outlier (Shapiro p < .001), making that t approximation particularly uncertain. Bootstrap intervals also include zero. Shapiro p values, leave-one-out mean ranges and fixed-seed whole-person bootstrap CIs are retained in results.json. Normality screens do not establish independence or justify post hoc cleaning. No diagnostic-driven method switch. Specifications, code/data/output hashes and runtime versions accompany the results.", "",
              "Reproduce: `.venv/Scripts/python.exe for-ai/orchestration/block_rt.py`; independently verify: add `--check`. Native saved outputs are displayed in Segment 3; the historical manuscript is unchanged."]
    (OUT / "RESULTS.md").write_text("\n".join(lines)+"\n", encoding="utf-8", newline="\n")
    source = ["for-ai/orchestration/block_rt.py", "workbook/paper_analysis.py", "workbook/preparation.py", "workbook/requirements.txt", "workbook/requirements-validation.txt"]
    manifest = dict(classification="exploratory", runtime=report["runtime"], seed=SEED,
                    input_sha256={name: sha256((ROOT / "data/raw" / name).read_bytes()).hexdigest() for name in FILES},
                    source_sha256={name: sha256((ROOT / name).read_bytes()).hexdigest() for name in source},
                    artifact_sha256={p.name: sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.iterdir()) if p.name != "manifest.json"})
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8", newline="\n")
    print(json.dumps({"n": len(wide), "tests": report["tests"], "endpoint": e}, indent=2))


def check():
    import statsmodels.api as sm
    import xml.etree.ElementTree as ET
    people, trials = load_pair(*[(ROOT / "data/raw" / name).read_bytes() for name in FILES])
    frame, _, _, retained = prepare(people, trials)
    raw = pd.DataFrame(retained).query("trial_type == 'Audio-Tactile'").copy()
    raw["session_block"] = (raw.trial_index.astype(int)-1)//34 + 1
    independent = raw.assign(rt=raw.reaction_time_ms.astype(float)).groupby(["participant_id", "session_block"]).rt.agg(["mean", "count"])
    for row in frame.itertuples():
        r = independent.loc[(row.participant_id, row.session_block)]
        np.testing.assert_allclose(row.mean_rt_ms, r["mean"], atol=1e-10)
        assert row.retained_trials == r["count"]
    saved = json.loads((OUT / "results.json").read_text(encoding="utf-8"))
    _, wide, slopes = analyze(frame, ("P011", "P033"))
    x = np.arange(1., 13.) - 6.5
    for pid, y in wide.iterrows():
        c = frame[frame.participant_id == pid].sort_values("session_block").condition.eq("Viscereality").to_numpy(dtype=float)
        ref = [sm.OLS(y, sm.add_constant(x)).fit().params.iloc[1],
               sm.OLS(y, np.column_stack([np.ones(12), x, x*x])).fit().params.iloc[2],
               sm.OLS(y, np.column_stack([np.ones(12), x, c])).fit().params.iloc[1]]
        np.testing.assert_allclose(slopes.set_index("participant_id").loc[pid, list(TERMS)], ref, atol=1e-10)
    for term in TERMS:
        r = saved["tests"][term]
        np.testing.assert_allclose(r["mean_ms"], slopes[term].mean(), atol=1e-10)
        np.testing.assert_allclose(r["p"], stats.ttest_1samp(slopes[term], 0).pvalue, atol=1e-12)
    np.testing.assert_allclose(wide.mean(), pd.read_csv(OUT / "summary.csv").mean_ms, atol=1e-10)
    observed = independent.loc[~independent.index.get_level_values(0).isin(("P011", "P033"))]
    np.testing.assert_allclose(observed["mean"].groupby("session_block").mean(),
                               pd.read_csv(OUT / "available_primary40_summary.csv").mean_ms, atol=1e-10)
    c = (x > 0).astype(float)
    np.testing.assert_allclose(coefficients(700-3*x, c), [-3, 0, -3], atol=1e-10)
    assert abs(coefficients(700-3*x+40*c, c)[2]+3) < 1e-10
    manifest = json.loads((OUT / "manifest.json").read_text())
    for name, expected in manifest["artifact_sha256"].items():
        assert sha256((OUT / name).read_bytes()).hexdigest() == expected
    for name, expected in manifest["source_sha256"].items():
        assert sha256((ROOT / name).read_bytes()).hexdigest() == expected
    for name, expected in manifest["input_sha256"].items():
        assert sha256((ROOT / "data/raw" / name).read_bytes()).hexdigest() == expected
    svg = ET.parse(OUT / "block_rt.svg")
    segments = {node.attrib["id"]: node for node in svg.iter() if node.attrib.get("id", "").startswith("trajectory-")}
    assert len(segments) == 2*len(wide)
    for pid in wide.index:
        person = frame[frame.participant_id == pid].set_index("session_block")
        for start in (1, 7):
            condition = person.loc[start, "condition"]
            segment = segments[f"trajectory-{pid}-{start}-{condition}"]
            style = " ".join(node.attrib.get("style", "") for node in segment.iter())
            assert ("#005a9c" if condition == "Control" else "#ba2525") in style
            assert ("stroke-dasharray" in style) == (condition == "Viscereality")
    print(f"PASS: chronology/order, independent trial aggregation, {3*len(wide)} statsmodels coefficients, saved/available40 means/p values, synthetic trends, all hashes")
    print(f"PASS: {len(segments)} plotted participant segments match actual conditions, colors and line styles")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    check() if args.check else build()
