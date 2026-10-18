"""Independent numerical checks for the native baseline-results batch."""
import unittest

import numpy as np
import pandas as pd
from scipy import optimize, stats
from statsmodels.stats.anova import AnovaRM

from baseline_effects import (CurveGrid, DISTANCES, W, load_data, profiles,
    cohort_mask, shape_basis, DESIGN)
from inference import paired, repeated_anova


class BaselineChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ids, cls.at, cls.baseline, cls.audit = load_data()

    def test_matching_sign_counts_and_translation(self):
        self.assertEqual(self.audit["primary40_counts"], {"AT": 8478, "Baseline": 4192})
        y = profiles(self.at, self.baseline, "pooled_cp")
        raw = np.nanmean(self.at, axis=-1)
        for i, c in ((0, 0), (13, 2), (41, 3)):
            b = self.baseline[i, c][np.isfinite(self.baseline[i, c])].mean()
            np.testing.assert_allclose(y[i, c], raw[i, c]-b)
        np.testing.assert_allclose(np.diff(y, axis=-1), np.diff(raw, axis=-1), atol=1e-12)
        grid = CurveGrid(DISTANCES["registered"], "logistic")
        p, prediction, _ = grid.fit(raw.reshape(-1, 5))
        pc, corrected_prediction, _ = grid.fit(y.reshape(-1, 5))
        np.testing.assert_allclose(p[:, 1:], pc[:, 1:], atol=1e-8)
        np.testing.assert_allclose(prediction-np.nanmean(self.baseline.reshape(42, 4, -1), -1).reshape(-1, 1), corrected_prediction, atol=1e-8)

    def test_factorial_parameter_coding(self):
        np.testing.assert_allclose(W[:3]@DESIGN, np.column_stack([np.zeros(3), np.eye(3)]))

    def test_held_out_prediction_translation_invariance(self):
        raw = profiles(self.at, self.baseline, "raw").reshape(-1, 5)
        corrected = profiles(self.at, self.baseline, "pooled_cp").reshape(-1, 5)
        shift = (raw-corrected)[:, :1]
        for family in ("logistic", "probit", "gompertz", "loglogistic", "fixed_extrema_logistic"):
            grid = CurveGrid(DISTANCES["registered"], family)
            for held in range(5):
                train = np.arange(5) != held
                _, pred, _ = grid.fit(raw[:, train], columns=train)
                _, pred_corrected, _ = grid.fit(corrected[:, train], columns=train)
                np.testing.assert_allclose(pred-shift, pred_corrected, atol=1e-6)

    def test_all_sigmoids_share_midpoint_and_derivative_definition(self):
        m, w = np.array([55.]), np.array([15.])
        step = 1e-4
        for family in ("logistic", "probit", "gompertz", "loglogistic", "fixed_extrema_logistic"):
            q = shape_basis(np.array([55-step, 55, 55+step]), m, w, family)[0]
            self.assertAlmostEqual(q[1], .5, places=12)
            self.assertAlmostEqual((q[2]-q[0])/(2*step), 1/60, places=9)

    def test_profiled_coefficients_match_independent_lstsq(self):
        rng = np.random.default_rng(76)
        y = rng.normal(0, 40, (8, 5))
        weights = rng.integers(2, 12, y.shape)
        for family in ("logistic", "probit", "gompertz", "loglogistic"):
            grid = CurveGrid(DISTANCES["registered"], family)
            p, predictions, _ = grid.fit(y, weights)
            for a, wy, yy, pp in zip(p, weights, y, predictions):
                q = shape_basis(DISTANCES["registered"], a[2:3], a[3:4], family)[0]
                design = np.column_stack([np.ones(5), q])
                beta = np.linalg.lstsq(design*np.sqrt(wy[:, None]), yy*np.sqrt(wy), rcond=None)[0]
                if abs(a[1]) < 999.99:
                    np.testing.assert_allclose(a[:2], beta, rtol=1e-7, atol=1e-7)
                np.testing.assert_allclose(pp, design@a[:2], atol=1e-10)

    def test_fixed_extrema_chooses_best_orientation_and_grid_shape(self):
        rng = np.random.default_rng(80)
        y = rng.normal(0, 40, (4, 5))
        grid = CurveGrid(DISTANCES["registered"], "fixed_extrema_logistic")
        p, pred, _ = grid.fit(y)
        for yy, pp in zip(y, pred):
            increasing = yy.min()+np.ptp(yy)*grid.q
            decreasing = yy.max()-np.ptp(yy)*grid.q
            reference = min(np.sum((increasing-yy)**2, 1).min(), np.sum((decreasing-yy)**2, 1).min())
            self.assertAlmostEqual(float(np.sum((pp-yy)**2)), float(reference), places=7)

    def test_sufficient_likelihood_equals_every_trial(self):
        from joint_pps import sufficient
        a = self.at[:3]/1000
        count, mean, sse = sufficient(a)
        mu = np.full(count.shape, .65)
        sigma = np.array([.09, .12, .18])[:, None, None]
        compressed = np.sum(-count*np.log(sigma)-.5*(sse+count*(mean-mu)**2)/sigma**2)
        direct = np.nansum(-np.log(sigma[..., None])-.5*((a-mu[..., None])/sigma[..., None])**2)
        self.assertAlmostEqual(compressed, direct, places=9)

    def test_subtracted_baseline_covariance(self):
        rng = np.random.default_rng(8)
        at = rng.normal(0, 3, (150000, 5))
        base_mean = rng.normal(0, 2, 150000)
        covariance = np.cov((at-base_mean[:, None]).T)
        np.testing.assert_allclose(covariance, np.eye(5)*9+4, atol=.12)

    def test_continuous_refinement_never_worsens_grid_objective(self):
        from check_baseline_fits import continuous_fit
        y = profiles(self.at[:1], self.baseline[:1], "pooled_cp").reshape(-1, 5)
        for family in ("logistic", "probit", "gompertz", "loglogistic", "fixed_extrema_logistic"):
            grid = CurveGrid(DISTANCES["registered"], family)
            pars, pred, _ = grid.fit(y)
            for yy, p, predicted in zip(y, pars, pred):
                loss, result, success = continuous_fit(yy, family, p)
                self.assertLessEqual(loss*2, np.sum((predicted-yy)**2)+1e-7)

    def test_pymc_joint_likelihood_matches_independent_trial_sum(self):
        from joint_pps import make_model
        from scipy.special import expit
        ids, at, base = self.ids[:3], self.at[:3], self.baseline[:3]
        for correction in ("pooled_cp", "same_label"):
            model = make_model(ids, at, base, correction=correction)
            point = model.initial_point()
            point["beta_amplitude"] = np.array([.08, .01, -.01, .02])
            point["beta_delta"] = np.array([-.02, .01, .01, .005])
            point["beta_midpoint"] = np.array([.5, .1, -.1, .05])
            point["beta_log_width"] = np.array([np.log(1/6), .1, .1, .2])
            m = point["beta_midpoint"]@DESIGN.T
            width = np.exp(point["beta_log_width"]@DESIGN.T)
            amp = point["beta_amplitude"]@DESIGN.T
            delta = point["beta_delta"]@DESIGN.T
            base_mean = point["baseline_mean"]
            if correction == "pooled_cp":
                base_mean = base_mean[..., None]
            mu = base_mean+delta[:, None]+amp[:, None]*(expit(((DISTANCES["registered"]-10)/90-m[:, None])/width[:, None])-.5)
            sa = np.exp(point["sigma_at_log__"])[:, None, None, None]
            sb = np.exp(point["sigma_baseline_log__"])[:, None, None, None]
            expected = np.nansum(-np.log(sa)-.5*((at/1000-mu[..., None])/sa)**2)
            expected += np.nansum(-np.log(sb)-.5*((base/1000-base_mean[..., None])/sb)**2)
            fn = model.compile_logp(vars=model.potentials, mode="FAST_COMPILE")
            self.assertAlmostEqual(float(fn(point)), expected, places=8)

    def test_empty_held_out_distance_has_zero_sufficient_likelihood(self):
        from joint_pps import sufficient
        a = self.at[:3].copy()
        a[:, :, 2, :] = np.nan
        count, mean, sse = sufficient(a)
        np.testing.assert_equal(count[:, :, 2], 0)
        np.testing.assert_equal(mean[:, :, 2], 0)
        np.testing.assert_equal(sse[:, :, 2], 0)

    def test_marginal_likelihood_matches_full_multivariate_normal(self):
        self.check_marginal_likelihood(False)

    def test_cell_specific_noise_marginal_likelihood_matches_full_normal(self):
        self.check_marginal_likelihood(True)

    def check_marginal_likelihood(self, cell_noise):
        from joint_pps import make_marginal_model
        from scipy.special import expit
        ids, at, base = self.ids[:1], self.at[:1], self.baseline[:1]
        model = make_marginal_model(ids, at, base, cell_noise=cell_noise)
        point = model.initial_point()
        point["beta_midpoint"] = np.array([.5, .1, -.1, .05])
        point["beta_log_width"] = np.array([np.log(1/6), .1, .1, .2])
        m = point["beta_midpoint"]@DESIGN.T
        width = np.exp(point["beta_log_width"]@DESIGN.T)
        if cell_noise:
            point["sigma_at_log__"] += np.log([[.7, 1., 1.3, 1.6]])
            point["sigma_baseline_log__"] += np.log([[1.4, 1.2, 1., .8]])
        reference = 0.
        for c in range(4):
            index = (0, c) if cell_noise else 0
            sa, sb = np.exp(point["sigma_at_log__"])[index], np.exp(point["sigma_baseline_log__"])[index]
            y, design, variance = [], [], []
            for d in range(5):
                q = expit(((DISTANCES["registered"][d]-10)/90-m[c])/width[c])-.5
                for tensor, row, sd in ((base, [1., 0., 0.], sb), (at, [1., 1., q], sa)):
                    values = tensor[0, c, d][np.isfinite(tensor[0, c, d])]/1000
                    y.extend(values); design.extend([row]*len(values)); variance.extend([sd**2]*len(values))
            design = np.array(design)
            covariance = np.diag(variance)+design@np.diag([.4**2, .2**2, .15**2])@design.T
            reference += stats.multivariate_normal.logpdf(y, mean=np.full(len(y), .6), cov=covariance)+len(y)/2*np.log(2*np.pi)
        fn = model.compile_logp(vars=model.potentials, mode="FAST_COMPILE")
        used = {v.name for v in fn.f.maker.fgraph.inputs}
        self.assertAlmostEqual(float(fn({k: v for k, v in point.items() if k in used})), reference, places=8)

    def test_real_data_anova_matches_statsmodels(self):
        mask = cohort_mask(self.ids, "primary40")
        y = profiles(self.at[mask], self.baseline[mask], "pooled_cp")
        records = [dict(pid=i, condition=c, phase=p, distance=d, value=y[i, c*2+p, d])
            for i in range(len(y)) for c in range(2) for p in range(2) for d in range(5)]
        table = AnovaRM(pd.DataFrame(records), "value", "pid", within=["condition", "phase", "distance"]).fit().anova_table
        actual = repeated_anova(y.reshape(-1, 2, 2, 5))
        for row in actual:
            name = row["effect"].lower().replace(" × ", ":").replace("soa", "distance")
            self.assertAlmostEqual(row["F"], table.loc[name, "F Value"], places=9)
            self.assertAlmostEqual(row["p_uncorrected"], table.loc[name, "Pr > F"], places=9)
        contrast = y.mean(-1)@W[:3].T
        for j in range(3):
            result = paired(contrast[:, j])
            independent = stats.ttest_1samp(contrast[:, j], 0)
            self.assertAlmostEqual(result["t"], independent.statistic, places=12)
            self.assertAlmostEqual(result["p"], independent.pvalue, places=12)


if __name__ == "__main__":
    unittest.main()
