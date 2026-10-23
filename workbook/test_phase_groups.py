"""Independent checks of the owner-requested six paired trial-group deltas."""
import unittest

import numpy as np
import pandas as pd
from scipy import stats

from paper_analysis import clean
from phase_rt import COLORS, TRIAL_GROUPS, group_summaries, trial_group_values
from preparation import load_pair, local_release_pair


class PhaseGroupTests(unittest.TestCase):
    def test_named_trial_groups_against_independent_pandas_pairs(self):
        people, trials = load_pair(*local_release_pair())
        rows = trial_group_values(people, trials)
        summary, deltas = group_summaries(rows)
        self.assertEqual((len(rows), len(deltas), len(summary)), (480, 240, 6))
        retained, _, _ = clean(people, trials)
        frame = pd.DataFrame(retained)
        frame = frame[~frame.participant_id.isin(["P011", "P033"])].copy()
        frame["reaction_time_ms"] = pd.to_numeric(frame.reaction_time_ms)
        for (name, soa), s in zip(TRIAL_GROUPS, summary):
            selection = frame[frame.trial_type == ("Baseline" if soa is None else "Audio-Tactile")]
            if soa is not None:
                selection = selection[pd.to_numeric(selection.soa_ms) == soa]
            cells = selection.groupby(["participant_id", "condition", "phase"]).reaction_time_ms.mean()
            pairs = cells.groupby(["participant_id", "phase"]).mean().unstack()
            self.assertEqual(pairs.shape, (40, 2))
            self.assertEqual(s["trial_group"], name)
            difference = pairs.Inhale-pairs.Exhale
            interval = stats.ttest_rel(pairs.Inhale, pairs.Exhale).confidence_interval()
            np.testing.assert_allclose([s["exhale_mean_ms"], s["inhale_mean_ms"], s["mean"], s["sd"], s["ci_low"], s["ci_high"]],
                [pairs.Exhale.mean(), pairs.Inhale.mean(), difference.mean(), difference.std(ddof=1), interval.low, interval.high], atol=1e-10)
            actual = {r["participant_id"]: r["delta_inhale_minus_exhale_ms"] for r in deltas if r["trial_group"] == name}
            np.testing.assert_allclose([actual[pid] for pid in difference.index], difference, atol=1e-10)
        self.assertAlmostEqual(np.mean([s["mean"] for s in summary[:5]]), 18.46897679220313)
        self.assertAlmostEqual(summary[-1]["mean"], 20.63191179226738)

    def test_six_required_series_colors_have_graphical_contrast(self):
        self.assertEqual(len(set(COLORS)), 6)
        for color in COLORS:
            rgb = [int(color[i:i+2], 16)/255 for i in (1, 3, 5)]
            linear = [c/12.92 if c <= .04045 else ((c+.055)/1.055)**2.4 for c in rgb]
            luminance = sum(c*w for c, w in zip(linear, (.2126, .7152, .0722)))
            self.assertGreaterEqual(1.05/(luminance+.05), 3, color)


if __name__ == "__main__":
    unittest.main()
