"""Independent likelihood and conditional-sampling checks for direction constraints."""
import unittest

import numpy as np
from scipy import linalg, special, stats
import pymc as pm
import xarray as xr

from model import make_model, nuisance_draws, complete_trace


class DirectionChecks(unittest.TestCase):
    def test_marginal_likelihood_against_full_trial_multivariate_normal(self):
        rng = np.random.default_rng(89)
        at, baseline = rng.normal(600, 90, (1, 4, 5, 3)), rng.normal(610, 80, (1, 4, 5, 2))
        at[0, 2, 1, 0] = np.nan
        q = special.expit((np.array([10, 27, 50, 73, 100])-55)/15)-.5
        for positive in (False, True):
            model = make_model(["P000"], at, baseline, positive)
            point = model.initial_point()
            point["sigma_at_log__"][:] = np.log(.12)
            point["sigma_baseline_log__"][:] = np.log(.14)
            actual = model.compile_logp(vars=model.potentials)(point)
            reference = 0.
            for c in range(4):
                a, b = at[0, c].reshape(-1)/1000, baseline[0, c].reshape(-1)/1000
                qa = np.repeat(q, 3)[np.isfinite(a)]
                a = a[np.isfinite(a)]
                y = np.r_[b, a]
                design_q = np.r_[np.zeros(len(b)), qa]
                design_delta = np.r_[np.zeros(len(b)), np.ones(len(a))]
                covariance = np.diag(np.r_[np.full(len(b), .14**2), np.full(len(a), .12**2)]) + \
                    .4**2*np.ones((len(y), len(y))) + .2**2*np.outer(design_delta, design_delta) + \
                    .15**2*np.outer(design_q, design_q)
                reference += stats.multivariate_normal.logpdf(y, np.full(len(y), .6), covariance)+.5*len(y)*np.log(2*np.pi)
                if positive:
                    cross = .15**2*design_q
                    mu = cross@linalg.solve(covariance, y-.6)
                    variance = .15**2-cross@linalg.solve(covariance, cross)
                    reference += np.log(2)+stats.norm.logcdf(mu/np.sqrt(variance))
            self.assertAlmostEqual(actual, reference, places=8)

    def test_conditional_truncation_means_and_covariance(self):
        n = 150000
        shape = (n,)
        values = {"amp_mean": -.04, "c11": .03**2, "offset_mean": .6,
                  "c00": .05**2, "c01": -.0005, "base_mean": .61,
                  "base_variance": .002, "offset_variance": .042}
        conditional = {"conditional_"+k: np.full(shape, v) for k, v in values.items()}
        amp, delta, baseline = nuisance_draws(conditional, True, np.random.default_rng(34))
        self.assertTrue((amp > 0).all())
        mean, variance = stats.truncnorm.stats(.04/.03, np.inf, loc=-.04, scale=.03, moments="mv")
        self.assertAlmostEqual(amp.mean(), mean, delta=.00015)
        self.assertAlmostEqual(amp.var(), variance, delta=.000003)
        offset = delta+baseline
        expected_mean = .6+values["c01"]/values["c11"]*(mean+.04)
        self.assertAlmostEqual(offset.mean(), expected_mean, delta=.0005)
        expected_covariance = values["c01"]/values["c11"]*variance
        self.assertAlmostEqual(np.cov(amp, offset)[0, 1], expected_covariance, delta=.000003)

    def test_empty_AT_block_contributes_zero_even_with_constraint(self):
        at = np.full((1, 4, 5, 2), np.nan)
        baseline = np.full((1, 4, 5, 2), 600.)
        model = make_model(["P000"], at, baseline, True)
        actual = model.compile_logp(vars=[model["likelihood_at"]])(model.initial_point())
        self.assertAlmostEqual(actual, 0., places=10)

    def test_monotonicity_midpoint_and_derivative(self):
        x = np.linspace(0, 150, 3001)
        for width, amplitude in ((4., .01), (15., .1), (120., .2)):
            y = -.05+amplitude*(special.expit((x-55)/width)-.5)
            self.assertTrue((np.diff(y) > 0).all())
            self.assertAlmostEqual(y[1100], -.05)
            derivative = (y[1101]-y[1099])/.1
            self.assertAlmostEqual(derivative, amplitude/(4*width), delta=1e-7)

    def test_postprocessing_adds_positive_monotonic_curves_to_trace(self):
        at, baseline = np.full((1, 4, 5, 2), 590.), np.full((1, 4, 5, 2), 610.)
        model = make_model(["P000"], at, baseline, True)
        with model:
            # These mock draws only exercise export; they are not a predictive/model check.
            prior = pm.sample_prior_predictive(draws=4, random_seed=79)
        trace = xr.DataTree.from_dict({"posterior": prior["prior"].to_dataset()})
        complete_trace(trace, True, 91)
        posterior = trace["posterior"].dataset
        self.assertTrue((posterior.amplitude.values > 0).all())
        self.assertTrue((np.diff(posterior.corrected_curve.values, axis=-1) >= 0).all())
        self.assertEqual(posterior.mean_RT_effect_ms.shape, (1, 4, 3))


if __name__ == "__main__":
    unittest.main()
