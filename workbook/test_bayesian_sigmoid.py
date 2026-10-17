"""Independent probability identities and paired-design checks for Bayesian results."""

import unittest

import numpy as np
from scipy import special, stats

from bayesian_sigmoid import (PARAMETERS, ShapeGrid, WEIGHTS, cohort_results,
                             conjugate, draw_parameters, point_estimate_anova, recording_weights,
                             weighted_rank_correlation, weighted_regression)
from descriptive_sigmoid import LABELS
from questionnaires import SCALES


class BayesianSigmoidTests(unittest.TestCase):
    def test_point_anova_pairs_labels_excludes_recordings_and_rejects_bad_cells(self):
        cells = []
        for i in range(6):
            for condition, phase in LABELS:
                c = .5 if condition == "Viscereality" else -.5
                p = .5 if phase == "Inhale" else -.5
                y = 52.+i+c*(2.+.3*i)+p*(-1.+.2*i)+c*p*(.5+.1*i)
                cells.append(dict(prior="primary", participant_id=f"T{i}", condition=condition,
                    phase=phase, midpoint_cm=y, normalized_steepness_per_cm=y*.001))
        rows = point_estimate_anova(cells[::-1], ["T1", "T0"])
        main = [r for r in rows if r["excluded_ids"] == "T0,T1" and r["parameter"] == "midpoint_cm"]
        self.assertEqual(len(rows), 24)
        expected = {"Condition": 2.+.3*np.arange(2, 6), "Phase": -1.+.2*np.arange(2, 6),
                    "Condition × Phase": .5+.1*np.arange(2, 6)}
        for r in main:
            contrast = expected[r["effect"]]
            reference = stats.ttest_1samp(contrast, 0.)
            self.assertEqual(r["n"], 4)
            self.assertAlmostEqual(r["estimate"], contrast.mean(), places=12)
            self.assertAlmostEqual(r["F"], reference.statistic**2, places=9)
            self.assertAlmostEqual(r["p"], reference.pvalue, places=12)
        for bad in (cells[:-1], cells+[cells[0]], [cells[0] | {"midpoint_cm": np.nan}]+cells[1:]):
            with self.assertRaises(ValueError):
                point_estimate_anova(bad)

    def test_conjugate_evidence_matches_multivariate_student_t(self):
        rng = np.random.default_rng(12)
        q = np.repeat(np.linspace(-.4, .4, 5), 3)
        y = .65+.12*q+rng.normal(0., .04, len(q))
        counts = np.full(5, 3.)
        sums = y.reshape(5, 3).sum(1)
        squares = (y*y).reshape(5, 3).sum(1)
        fit = conjugate(counts, sums, squares, np.linspace(-.4, .4, 5))
        design = np.column_stack([np.ones(len(y)), q])
        reference = stats.multivariate_t.logpdf(y, loc=design @ np.array([.6, 0.]),
            shape=.01*(np.eye(len(y))+4.*design@design.T), df=4)
        self.assertAlmostEqual(float(fit["log_ml"][0]), reference, places=9)

    def test_exact_held_block_prediction_identity(self):
        q = np.linspace(-.5, .5, 5)
        observations = np.array([[.52, .58], [.55, .61], [.6, .58], [.64, .63], [.7, .66]])
        n, sy, syy = np.full(5, 2.), observations.sum(1), (observations**2).sum(1)
        full = conjugate(n, sy, syy, q)
        train = [v.copy() for v in (n, sy, syy)]
        for v in train:
            v[-1] = 0.
        fit = conjugate(*train, q)
        covariance = np.array([[fit["v00"][0], fit["v01"][0]], [fit["v01"][0], fit["v11"][0]]])
        held_design = np.column_stack([np.ones(2), np.full(2, q[-1])])
        location = held_design @ np.array([fit["b"][0], fit["a"][0]])
        scale = fit["scale"][0]/fit["alpha"]*(np.eye(2)+held_design@covariance@held_design.T)
        reference = stats.multivariate_t.logpdf(observations[-1], loc=location,
                                               shape=scale, df=2.*fit["alpha"])
        self.assertAlmostEqual(float(full["log_ml"][0]-fit["log_ml"][0]), reference, places=9)

    def test_no_observations_return_proper_shape_prior(self):
        for name in ("primary", "expanded_support", "concentrated_width", "wide_nuisance"):
            grid = ShapeGrid(name)
            fit = grid.fit(np.zeros(5), np.zeros(5), np.zeros(5))
            np.testing.assert_allclose(fit["weights"], np.exp(grid.logprior), rtol=1e-12)
            self.assertAlmostEqual(fit["logz"], 0., places=12)

    def test_signed_amplitude_is_not_forced_into_a_positive_response(self):
        grid = ShapeGrid()
        q = special.expit((np.linspace(0., 1., 5)-.5)/.08)-.5
        n = np.full(5, 100.)
        y = .6-.1*q
        fit = grid.fit(n, n*y, n*(y*y+.005**2))
        samples, _ = draw_parameters(fit, np.random.default_rng(3), 500)
        self.assertLess(float(np.mean(samples[:, 1] > 0)), .01)
        self.assertLess(abs(float(np.median(samples[:, 2]))-.5), .05)

    def test_weighted_ranks_equal_expanded_spearman_with_ties(self):
        x = np.array([[1., 2., 2., 3., 4.], [1., 2., 3., 3., 3.]])
        y = np.array([[3., 1., 1., 2., 4.], [1., 2., 1., 4., 4.]])
        weights = np.array([[2, 0, 1, 3, 1], [1, 2, 1, 0, 3]])
        actual = weighted_rank_correlation(x, y, weights)
        reference = [stats.spearmanr(np.repeat(a, w), np.repeat(b, w)).statistic
                     for a, b, w in zip(x, y, weights)]
        np.testing.assert_allclose(actual, reference, atol=1e-14)

    def test_linked_records_share_resampling_weights(self):
        rng = np.random.default_rng(15)
        for bootstrap in (False, True):
            weights = recording_weights(rng, ["A", "B", "C", "D"], 30, bootstrap, [("A", "C")])
            np.testing.assert_array_equal(weights[:, 0], weights[:, 2])
            self.assertTrue(np.any(weights[:, 0] != weights[:, 1]))

    def test_weighted_regression_matches_weighted_lstsq(self):
        rng = np.random.default_rng(9)
        design = np.column_stack([np.ones(25), rng.normal(size=(25, 4))])
        weights = rng.exponential(size=(7, 25))
        outcomes = rng.normal(size=(7, 25, 3))
        actual = weighted_regression(design, weights, outcomes)
        for i in range(7):
            reference = np.linalg.lstsq(design*np.sqrt(weights[i, :, None]),
                                        outcomes[i]*np.sqrt(weights[i, :, None]), rcond=None)[0]
            np.testing.assert_allclose(actual[i], reference, atol=1e-12)
        self.assertIsNone(weighted_regression(np.ones((25, 2)), weights, outcomes))

    def test_joint_interaction_and_missing_data_keep_paired_effect_signs(self):
        rng = np.random.default_rng(31)
        n, nd = 20, 50
        a, s = rng.normal(size=(2, n))
        a -= a.mean(); s -= s.mean()
        order = np.arange(n) % 2
        ids = [f"T{i:03d}" for i in range(n)]
        records = []
        for i, pid in enumerate(ids):
            r = dict(participant_id=pid, condition_order="Viscereality-Control" if order[i] else "Control-Viscereality",
                     spfrref_delta=float(s[i]), spfrref_change_direction=float(np.sign(s[i])),
                     spfrref_control_ordinal=3., spfrref_viscereality_ordinal=float(3.+s[i]))
            r.update({"maia2_"+scale: float(a[i]+2.) for scale in SCALES})
            records.append(r)
        parameters = np.zeros((nd, n, 4, 4))
        parameters[..., 0] = .6
        parameters[..., 1] = .08
        parameters[..., 3] = .12
        condition = np.array([-.5, -.5, .5, .5])
        parameters[..., 2] = .5+condition[None, None, :]*(.02*a+.01*s+.03*a*s)[:, None]
        group, cells, associations, regressions = cohort_results(parameters, ids, records, "primary", rng)
        product = [r for r in regressions if r["effect"] == "Condition" and r["parameter"] == PARAMETERS[0]
                   and r["term"] == "MAIA × spatial_delta"]
        self.assertEqual(len(associations), 92)
        self.assertEqual(len(regressions), 192)
        self.assertEqual(len(cells), 16)
        for row in product:
            self.assertAlmostEqual(row["median"], 90.*.03, places=10)
        records[0]["maia2_noticing"] = None
        _, _, _, incomplete = cohort_results(parameters, ids, records, "primary", rng)
        self.assertEqual({r["n_complete"] for r in incomplete if r["scale"] == "noticing"}, {n-1})


if __name__ == "__main__":
    unittest.main()
