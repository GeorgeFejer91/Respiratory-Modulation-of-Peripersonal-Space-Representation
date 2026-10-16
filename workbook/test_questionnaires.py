"""Instrument scoring, ordinal inference and missing-data regression checks."""

import itertools
import json
import unittest

import numpy as np
from scipy import stats

from preparation import PARTICIPANT_COLUMNS, validate_questionnaire_rows
from questionnaires import alpha, association, moderation, rank_correlation, run, score_people, spatial_summary


def person():
    return dict.fromkeys(PARTICIPANT_COLUMNS, "") | {"participant_id": "P000", "condition_order": "test"}


class QuestionnaireTests(unittest.TestCase):
    def test_direction_and_complete_subscale_scoring(self):
        p = person()
        p.update({f"maia2_item_{i:02d}": "0" for i in range(1, 38)})
        # Not-Worrying has three reversed and two direct items: (5+5+0+0+5)/5.
        scores, audit = score_people([p])
        self.assertEqual(scores[0]["maia2_not_worrying"], 3.)
        self.assertEqual(scores[0]["maia2_not_distracting"], 5.)
        self.assertEqual(scores[0]["maia2_attention_regulation"], 0.)
        p["maia2_item_01"] = ""
        p["maia2_noticing"] = "4"
        scores, audit = score_people([p])
        self.assertIsNone(scores[0]["maia2_noticing"])
        self.assertEqual(audit[0]["status"], "stored_only")

    def test_invalid_items_and_conflicting_ordinal_encoding_rejected(self):
        for value in ("2.5", "6", "nan", "unscored"):
            p = person() | {"maia2_item_01": value}
            with self.assertRaises(ValueError): validate_questionnaire_rows([p])
        for letter, code in (("A", "8"), ("", "1"), ("I", "9")):
            with self.assertRaises(ValueError):
                validate_questionnaire_rows([person() | {"spfrref_control": letter, "spfrref_control_ordinal": code}])

    def test_raw_alpha_known_two_item_case_and_undefined_constant(self):
        self.assertAlmostEqual(float(alpha(np.array([[0., 0.], [1., 1.], [2., 3.], [3., 2.]]))), 8/9)
        self.assertTrue(np.isnan(alpha(np.ones((5, 3)))))
        self.assertLess(float(alpha(np.array([[0., 3.], [1., 1.], [2., 2.], [3., 0.]]))), 0)

    def test_sign_test_counts_ties_and_is_invariant_to_spacing(self):
        data = [dict(condition_order="test", spfrref_control_ordinal=c, spfrref_viscereality_ordinal=v,
                     spfrref_change_direction=float(np.sign(v-c))) for c, v in [(1, 2), (1, 8), (3, 4), (8, 1), (2, 2), (3, 3)]]
        r = spatial_summary(data, np.random.default_rng(3), 100)
        self.assertEqual((r["higher"], r["lower"], r["ties"], r["n_pairs"]), (3, 1, 2, 6))
        self.assertEqual(r["p"], .625)
        self.assertAlmostEqual(r["paired_dominance"], 1/3)
        self.assertEqual(sum(x["n"] for x in r["transitions"]), 6)
        all_tied = [dict(r, spfrref_change_direction=0.) for r in data]
        self.assertIsNone(spatial_summary(all_tied, np.random.default_rng(3), 100)["p"])

    def test_tied_rho_and_monte_carlo_p_agree_with_exhaustive_reference(self):
        x, y = np.array([0., 0., 1., 2., 3.]), np.array([0., 1., 1., 2., 1.])
        reference = float(stats.spearmanr(x, y).statistic)
        self.assertAlmostEqual(float(rank_correlation(x, y)), reference)
        null = [abs(stats.spearmanr(x, z).statistic) for z in itertools.permutations(y)]
        exact = np.mean(np.array(null) >= abs(reference)-1e-12)
        r = association([{"x": a, "y": b} for a, b in zip(x, y)], "x", "y", np.random.default_rng(23), 19999, 2000)
        self.assertAlmostEqual(r["p"], exact, delta=.02)
        self.assertGreater(r["p"], 0.)
        self.assertLess(r["bootstrap_valid"], 2000)

    def test_missing_questionnaires_remain_missing_and_family_is_preserved(self):
        r = run([person()], {}, bootstrap_draws=20, permutations=20)
        self.assertEqual(r["maia_complete"], 0)
        self.assertEqual(len(r["associations"]), 33)
        self.assertTrue(all(x["p"] is None and "p_holm" not in x for x in r["associations"]))
        self.assertEqual(r["resampling"]["adjustment"], "none")
        self.assertEqual(r["spatial"]["n_pairs"], 0)
        self.assertEqual(len(r["delta_associations"]), 9)
        self.assertEqual(len(r["moderation"]), 16)
        self.assertTrue(all(x["status"] == "not_estimable" for x in r["moderation"]))
        json.dumps(r, allow_nan=False)

    def test_signed_delta_retains_magnitude_and_ignores_presentation_order(self):
        p = person() | {"condition_order": "Control-Viscereality", "spfrref_control": "A",
            "spfrref_control_ordinal": "1", "spfrref_viscereality": "E", "spfrref_viscereality_ordinal": "5"}
        for order in ("Control-Viscereality", "Viscereality-Control"):
            r = score_people([p | {"condition_order": order}])[0][0]
            self.assertEqual((r["spfrref_delta"], r["spfrref_change_direction"]), (4., 1.))
        r = score_people([p | {"spfrref_control": "H", "spfrref_control_ordinal": "8"}])[0][0]
        self.assertEqual((r["spfrref_delta"], r["spfrref_change_direction"]), (-3., -1.))
        r = score_people([p | {"spfrref_control": "", "spfrref_control_ordinal": ""}])[0][0]
        self.assertIsNone(r["spfrref_delta"])

    def test_moderation_known_slope_uncertainty_and_degenerate_predictors(self):
        x = np.arange(5, dtype=float)
        y = 1+.5*x+np.array([1., -2., 2., -2., 1.])
        rows = [dict(x=a, spfrref_delta=b, condition_order="Control-Viscereality") for a, b in zip(x, y)]
        r = moderation(rows, "x")
        self.assertEqual(r["status"], "computed")
        self.assertAlmostEqual(r["beta"], .5)
        self.assertAlmostEqual(r["se"], np.sqrt(7/15))
        self.assertAlmostEqual(r["F"], 15/28)
        self.assertEqual(r["df"], 3)
        self.assertEqual(r["hc3_status"], "computed")
        self.assertEqual(moderation(rows, "x", True)["status"], "not_estimable")
        self.assertEqual(moderation([r | {"x": 2.} for r in rows], "x")["status"], "not_estimable")
        self.assertEqual(moderation([r | {"spfrref_delta": 0.} for r in rows], "x")["status"], "not_estimable")

    def test_order_term_recovery_and_missing_order_exclusion(self):
        rows = []
        for order, label in enumerate(("Control-Viscereality", "Viscereality-Control")):
            for x, error in zip(range(5), (1., -2., 2., -2., 1.)):
                rows.append(dict(x=float(x), spfrref_delta=1+.5*x+2*order+error, condition_order=label))
        r = moderation(rows, "x", True)
        self.assertAlmostEqual(r["beta"], .5)
        self.assertAlmostEqual(r["order_beta"], 2.)
        self.assertEqual(r["df"], 7)
        rows.append(dict(x=2., spfrref_delta=0., condition_order="unknown"))
        self.assertEqual(moderation(rows, "x")["n"], 11)
        self.assertEqual(moderation(rows, "x", True)["n"], 10)


if __name__ == "__main__":
    unittest.main()
