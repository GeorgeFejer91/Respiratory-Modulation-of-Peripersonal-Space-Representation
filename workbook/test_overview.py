"""Check Segment 2 against released participant cells and saved native contrasts."""
import csv
from pathlib import Path
import unittest
import json
from hashlib import sha256

import numpy as np

from scipy import stats

from pivot_data import cohort_frame, exploration_views
from preparation import load_pair, local_release_pair


class PhaseOverviewTests(unittest.TestCase):
    def test_block_segment_provenance_and_claims(self):
        root = Path(__file__).resolve().parents[1]
        folder = root / "results/block_rt"
        manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
        for section, prefix in (("input_sha256", root / "data/raw"), ("source_sha256", root), ("artifact_sha256", folder)):
            for name, digest in manifest[section].items():
                self.assertEqual(sha256((prefix / name).read_bytes()).hexdigest(), digest, name)
        report = json.loads((folder / "results.json").read_text(encoding="utf-8"))
        self.assertEqual(report['measure'], 'corrected_rt_ms')
        self.assertIn('raw_reference', report)
        html = (root / "workbook/overview_assets/index.html").read_text(encoding="utf-8")
        section = html.split('<section id="blocks"', 1)[1].split('</section>', 1)[0]
        r = report["tests"]["linear_ms_per_block"]
        self.assertEqual(r["n"], 39)
        self.assertEqual(report["incomplete_excluded"], ["P008"])
        for value in (r["mean_ms"], r["ci_low_ms"], r["ci_high_ms"], r["t"]):
            self.assertIn(f"{value:.2f}".replace("-", "−"), section)
        self.assertIn(f"{r['p']:.3f}"[1:], section)
        self.assertIn('Native calculation; saved results shown here.', section)
        self.assertIn('results/block_rt/block_rt.svg', section)
        self.assertEqual([r["n"] for r in report["available_primary40_descriptive"]], [40]*6+[39]+[40]*5)

    def test_literal_trial_labels_and_plot_data(self):
        from phase_rt import phase_values, summarize
        people, trials = load_pair(*local_release_pair())
        values = phase_values(people, trials)
        reference = cohort_frame(exploration_views(people, trials)["Participant-distance means"],
                                 "Primary behavioural cohort")
        expected = reference.groupby(["participant_id", "phase"])[
            ["reaction_time_ms", "baseline_mean_ms", "corrected_rt_ms"]].mean()
        self.assertEqual(len(values), 80)
        for row in values:
            np.testing.assert_allclose([row[k] for k in expected.columns],
                                      expected.loc[(row["participant_id"], row["phase"])], atol=1e-10)
        reverse = phase_values(people, list(reversed(trials)))
        for first, second in zip(values, reverse):
            self.assertEqual((first["participant_id"], first["phase"]), (second["participant_id"], second["phase"]))
            np.testing.assert_allclose([first[k] for k in expected.columns], [second[k] for k in expected.columns], atol=1e-10)
        report = summarize(values)
        self.assertEqual(report['primary_measure'], 'corrected_rt_ms')
        for phase in ('Exhale','Inhale'):
            self.assertAlmostEqual(report['corrected_phase_means'][phase]['mean'],
                expected.xs(phase, level='phase').corrected_rt_ms.mean())
        self.assertAlmostEqual(report["phase_means"]["Exhale"]["mean"], 662.1920580095339)
        self.assertAlmostEqual(report["phase_means"]["Inhale"]["mean"], 680.661034801737)
        for row in values:
            self.assertAlmostEqual(row["corrected_rt_ms"], row["reaction_time_ms"]-row["baseline_mean_ms"])
        self.assertAlmostEqual(report["contrasts"]["reaction_time_ms"]["mean"], 18.46897679220313)
        self.assertAlmostEqual(report["contrasts"]["baseline_mean_ms"]["mean"], 20.63191179226738)
        self.assertAlmostEqual(report["contrasts"]["corrected_rt_ms"]["mean"], -2.1629350000642553)

    def test_phase_figure_provenance(self):
        root = Path(__file__).resolve().parents[1]
        folder = root / "results/phase_rt"
        manifest = json.loads((folder/"manifest.json").read_text(encoding="utf-8"))
        for section, prefix in (("input_sha256", root/"data/raw"), ("source_sha256", root), ("artifact_sha256", folder)):
            for name, digest in manifest[section].items():
                self.assertEqual(sha256((prefix/name).read_bytes()).hexdigest(), digest, name)
        self.assertIn("Baseline-corrected RT", (folder/"phase_rt.svg").read_text(encoding="utf-8"))
        svg = (folder/"phase_raw_groups.svg").read_text(encoding="utf-8")
        for label in ("Exhale", "Inhale", "Inhale − Exhale", "AT 300 ms", "AT 800 ms", "AT 1500 ms", "AT 2200 ms", "AT 2700 ms", "Baseline"):
            self.assertIn(label, svg)
        from phase_rt import COLORS
        for color in COLORS:
            self.assertIn(color.lower(), svg.lower())

    def test_paired_phase_claims(self):
        root = Path(__file__).resolve().parents[1]
        views = exploration_views(*load_pair(*local_release_pair()))
        cells = cohort_frame(views["Participant-distance means"], "Primary behavioural cohort")
        with (root / "results/baseline_effects/response_tests.csv").open(encoding="utf-8") as source:
            saved = {row["correction"]: row for row in csv.DictReader(source)
                     if row["cohort"] == "primary40" and row["extraction"] == "mean"
                     and row["metric"] == "mean_RT_ms" and row["effect"] == "Phase"}
        html = (root / "workbook/overview_assets/index.html").read_text(encoding="utf-8")
        for correction, measure in (("raw", "reaction_time_ms"), ("pooled_cp", "corrected_rt_ms")):
            # Equal SOA/condition weights within person; paired persons are the inferential units.
            phase = cells.groupby(["participant_id", "phase"])[measure].mean().unstack()
            difference = phase.Inhale - phase.Exhale
            self.assertEqual(len(difference), 40)
            self.assertFalse(difference.isna().any())
            estimate = difference.mean()
            result = stats.ttest_1samp(difference, 0)
            interval = result.confidence_interval()
            row = saved[correction]
            for value, key in ((estimate, "estimate"), (result.statistic, "t"),
                               (result.pvalue, "p"), (interval.low, "ci_low"), (interval.high, "ci_high")):
                self.assertAlmostEqual(value, float(row[key]), places=9)
            for value in (estimate, interval.low, interval.high):
                self.assertIn(f"{value:.2f}".replace("-", "−"), html)
            self.assertIn(f"{result.pvalue:.4f}"[1:] if correction == "raw" else f"{result.pvalue:.3f}"[1:], html)
        self.assertGreater(float(saved["raw"]["ci_low"]), 0)
        self.assertLess(float(saved["pooled_cp"]["ci_low"]), 0)
        self.assertGreater(float(saved["pooled_cp"]["ci_high"]), 0)


if __name__ == "__main__":
    unittest.main()
