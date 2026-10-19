"""Geometry and independent full-trial likelihood checks for the visible-S prior."""
import unittest

import numpy as np
from scipy import linalg, special, stats
import pymc as pm
import xarray as xr

from fit import geometry, make_model, prior_draws, directional


class VisibleChecks(unittest.TestCase):
    def test_geometry_endpoint_plateaus_midpoint_and_derivative(self):
        rng = np.random.default_rng(120)
        position, fraction = rng.uniform(size=(2, 10000))
        for epsilon in (.05, .10):
            m, w = geometry(position, fraction, epsilon)
            self.assertTrue(((m > 10)&(m < 100)&(w > 2)).all())
            self.assertTrue((special.expit((10-m)/w) <= epsilon+1e-12).all())
            self.assertTrue((special.expit((100-m)/w) >= 1-epsilon-1e-12).all())
            np.testing.assert_allclose(special.expit((m-m)/w), .5)
            h = 1e-4
            np.testing.assert_allclose((special.expit(h/w)-special.expit(-h/w))/(2*h), 1/(4*w), rtol=1e-8)

    def test_mean_and_marginal_median_geometry_stays_feasible(self):
        rng = np.random.default_rng(77)
        m, w = geometry(special.expit(rng.normal(size=(6000, 40, 4))),
                        special.expit(rng.normal(size=(6000, 40, 4))), .05)
        for a, b in ((np.median(m, 0), np.median(w, 0)),
                     (np.median(m.mean(1), 0), np.median(w.mean(1), 0))):
            self.assertTrue((special.expit((10-a)/b) <= .05+1e-10).all())
            self.assertTrue((special.expit((100-a)/b) >= .95-1e-10).all())

    def test_full_trial_marginal_likelihood(self):
        rng = np.random.default_rng(89)
        at, baseline = rng.normal(600, 90, (1, 4, 5, 3)), rng.normal(610, 80, (1, 4, 5, 2))
        at[0, 2, 1, 0] = np.nan
        for epsilon in (.05, .10):
            model = make_model(["P000"], at, baseline, epsilon)
            point = model.initial_point()
            point["sigma_at_log__"][:] = np.log(.12)
            point["sigma_baseline_log__"][:] = np.log(.14)
            actual = model.compile_logp(vars=model.potentials)(point)
            m, w = geometry(.5, .5, epsilon)
            q = special.expit((directional.X-m)/w)-.5
            reference = 0.
            for c in range(4):
                a, b = at[0, c].ravel()/1000, baseline[0, c].ravel()/1000
                qa = np.repeat(q, 3)[np.isfinite(a)]
                a = a[np.isfinite(a)]
                y = np.r_[b, a]
                dq = np.r_[np.zeros(len(b)), qa]
                dd = np.r_[np.zeros(len(b)), np.ones(len(a))]
                cov = np.diag(np.r_[np.full(len(b), .14**2), np.full(len(a), .12**2)]) + \
                    .4**2*np.ones((len(y), len(y)))+.2**2*np.outer(dd, dd)+.15**2*np.outer(dq, dq)
                cross = .15**2*dq
                mu = cross@linalg.solve(cov, y-.6)
                variance = .15**2-cross@linalg.solve(cov, cross)
                reference += stats.multivariate_normal.logpdf(y, np.full(len(y), .6), cov) + \
                    .5*len(y)*np.log(2*np.pi)+np.log(2)+stats.norm.logcdf(mu/np.sqrt(variance))
            self.assertAlmostEqual(actual, reference, delta=2e-8)

    def test_empty_AT_likelihood_and_export(self):
        at, baseline = np.full((1, 4, 5, 2), np.nan), np.full((1, 4, 5, 2), 600.)
        model = make_model(["P000"], at, baseline)
        score = model.compile_logp(vars=[model["likelihood_at"]])(model.initial_point())
        self.assertAlmostEqual(score, 0., places=10)
        with model:
            prior = pm.sample_prior_predictive(draws=4, random_seed=79)
        mock = xr.DataTree.from_dict({"posterior": prior["prior"].to_dataset()})
        directional.complete_trace(mock, True, 91)
        p = mock["posterior"].dataset
        self.assertTrue((p.amplitude.values > 0).all())
        self.assertTrue((np.diff(p.corrected_curve.values, axis=-1) >= 0).all())

    def test_prior_simulator_agrees_with_pymc_distribution(self):
        at, baseline = np.full((1, 4, 5, 2), 590.), np.full((1, 4, 5, 2), 600.)
        model = make_model(["P000"], at, baseline)
        with model:
            p = pm.sample_prior_predictive(draws=5000, var_names=["midpoint_cm", "width_cm"], random_seed=83)["prior"].dataset
        simulated = prior_draws(.05, 1)
        for quantity in ("midpoint_cm", "width_cm"):
            observed = p[quantity].values.reshape(-1, 4)
            np.testing.assert_allclose(observed.mean(0), simulated[quantity].mean(0).ravel(), atol=.65)
            np.testing.assert_allclose(observed.std(0), simulated[quantity].std(0).ravel(), atol=.65)


if __name__ == "__main__":
    unittest.main()
