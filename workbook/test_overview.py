"""Check Segment 2 against released participant cells and saved native contrasts."""
import csv
from pathlib import Path
import unittest

from scipy import stats

from pivot_data import cohort_frame, exploration_views
from preparation import load_pair, local_release_pair


class PhaseOverviewTests(unittest.TestCase):
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
