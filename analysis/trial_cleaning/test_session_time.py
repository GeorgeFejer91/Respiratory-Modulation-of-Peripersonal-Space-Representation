"""Global time alignment and joint, rather than plug-in, drift likelihood checks."""
import unittest
import numpy as np

import run
from session_time import time_arrays, moments, make_model


class SessionTimeChecks(unittest.TestCase):
    def test_global_clock_never_restarts_at_condition_change(self):
        people, _, eligible, _, ids, _ = run.source()
        rows, _, _ = run.prepare(eligible)
        rt = run.tensors(rows, ids)
        timed = time_arrays(rows, ids, people)
        for a, t in zip(rt, timed):
            self.assertTrue(np.array_equal(np.isfinite(a), np.isfinite(t)))
            self.assertTrue((np.nanmin(t) >= -.5) and (np.nanmax(t) <= .5))
        for i, pid in enumerate(ids):
            order = next(p['condition_order'] for p in people if p['participant_id'] == pid)
            first = order.split('-')[0]
            for c, cell in enumerate(run.CELL_NAMES):
                t = timed[0][i, c]
                self.assertTrue((t[np.isfinite(t)] < 0).all() if cell.startswith(first+' ')
                                else (t[np.isfinite(t)] > 0).all())

    def test_moments_reproduce_full_trial_residualization(self):
        rng = np.random.default_rng(879)
        rt, t = rng.normal(.6, .12, (2, 4, 5, 8)), rng.uniform(-.5, .5, (2, 4, 5, 8))
        rt[0, 2, 3, 0], t[0, 2, 3, 0] = np.nan, np.nan
        n, y, ss, means, cross, xx = moments(rt, t, 2)
        coefficients = np.array([[.09, -.14], [-.05, .08]])
        g = coefficients[:, None, None]
        actual = rt-coefficients[:, None, None, 0, None]*t-coefficients[:, None, None, 1, None]*t*t
        nr, yr, ssr = run.directional.sufficient(actual)
        np.testing.assert_array_equal(n, nr)
        np.testing.assert_allclose(y-(means*g).sum(-1), yr, atol=1e-15)
        np.testing.assert_allclose(ss-2*(cross*g).sum(-1)+(xx*g[..., :, None]*g[..., None, :]).sum((-1, -2)), ssr, atol=1e-15)

    def test_joint_likelihood_matches_direct_trial_residualization(self):
        rng = np.random.default_rng(789)
        at, baseline = rng.normal(600, 90, (1, 4, 5, 3)), rng.normal(610, 80, (1, 4, 5, 2))
        ta, tb = rng.uniform(-.5, .5, at.shape), rng.uniform(-.5, .5, baseline.shape)
        at[0, 2, 1], ta[0, 2, 1] = np.nan, np.nan
        for shape, rolling, coefficients in (("broad", False, [.08]), ("broad", True, [.08]),
                ("broad", False, [.08, -.16]), ("visible95", True, [.08])):
            model = make_model(['P000'], at, baseline, ta, tb, shape, rolling, len(coefficients))
            point = model.initial_point()
            point['beta_time'][:] = coefficients
            actual = model.compile_logp(vars=model.potentials)(point)
            aa, bb = at.copy(), baseline.copy()
            for j, coefficient in enumerate(coefficients):
                aa -= 1000*coefficient*ta**(j+1)
                bb -= 1000*coefficient*tb**(j+1)
            reference = run.make_model(['P000'], aa, bb, shape, rolling)
            expected = reference.compile_logp(vars=reference.potentials)(reference.initial_point())
            self.assertAlmostEqual(actual, expected, delta=2e-8)

    def test_missing_distance_time_statistics_are_zero_and_no_leakage(self):
        rng = np.random.default_rng(981)
        y, t = rng.normal(size=(1, 4, 5, 3)), rng.uniform(-.5, .5, (1, 4, 5, 3))
        y[:, :, 2], t[:, :, 2] = np.nan, np.nan
        outputs = moments(y, t, 2)
        for a in outputs:
            np.testing.assert_allclose(a[:, :, 2], 0)


if __name__ == '__main__':
    unittest.main()
