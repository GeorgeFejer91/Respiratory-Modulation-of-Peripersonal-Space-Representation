import unittest

import pandas as pd

from pivot_data import cohort_frame, exploration_views, pivot_frame
from preparation import load_pair, local_release_pair


class PivotTests(unittest.TestCase):
    def test_totals_missing_counts_and_no_axes(self):
        frame = pd.DataFrame({"group": ["A", "A", "B", "B"],
                              "phase": ["I", "I", "I", "E"], "rt": [2., 4., 12., None]})
        result = pivot_frame(frame, ["group"], ["phase"], ["rt"], "Mean").set_index("group")
        self.assertEqual(result.loc["Grand total", "rt · Grand total"], 6.)
        self.assertTrue(pd.isna(result.loc["B", "rt · E"]))
        self.assertEqual(pivot_frame(frame, [], [], ["rt"], "Count nonmissing", False).rt.iloc[0], 3)
        self.assertEqual(pivot_frame(frame, [], [], [], "Row count", False)["Record count"].iloc[0], 4)
        self.assertTrue(pd.isna(pivot_frame(frame.iloc[3:], [], [], ["rt"], "Sum", False).rt.iloc[0]))
        self.assertTrue(pivot_frame(frame.iloc[:0], ["group"], [], ["rt"], "Mean").empty)
        with self.assertRaises(ValueError):
            pivot_frame(frame, ["group"], ["group"], ["rt"], "Mean")
        self.assertEqual(pivot_frame(frame, [], [], ["group"], "Unique values", False).group.iloc[0], 2)
        with self.assertRaises(ValueError):
            pivot_frame(frame, [], [], ["group"], "Mean")
        large = pd.DataFrame({"a": range(400), "b": range(400), "v": range(400)})
        with self.assertRaisesRegex(ValueError, "100,000"):
            pivot_frame(large, ["a"], ["b"], ["v"], "Mean")

    def test_release_grain_cohorts_and_baseline(self):
        people, trials = load_pair(*local_release_pair())
        views = exploration_views(people, trials)
        self.assertEqual(len(views["All trial records"]), 17114)
        self.assertEqual(len(views["Participants and questionnaires"]), 42)
        frame = views["All trial records"]
        primary = cohort_frame(views["Participant-distance means"], "Primary behavioural cohort")
        self.assertEqual(primary.participant_id.nunique(), 40)
        cell = frame[(frame.participant_id == "P000") & (frame.condition == "Control") & (frame.phase == "Exhale")]
        expected = cell[cell.retained_global & (cell.trial_type == "Baseline")].reaction_time_ms.mean()
        at = cell[cell.retained_global & (cell.trial_type == "Audio-Tactile")]
        self.assertAlmostEqual(at.corrected_rt_ms.iloc[0], at.reaction_time_ms.iloc[0] - expected)
        self.assertTrue(frame[frame.trial_type != "Audio-Tactile"].corrected_rt_ms.isna().all())
        self.assertEqual(frame[frame.retained_global & (frame.trial_type == "Audio-Tactile")].shape[0], 8916)


if __name__ == "__main__":
    unittest.main()
