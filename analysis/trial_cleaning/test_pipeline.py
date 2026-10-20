"""Independent checks for trimming, information loss, leakage and likelihood."""
import unittest
import numpy as np
from scipy import linalg, special, stats

from run import (source, trim, prepare, tensors, mean_precision, make_model,
                 SOA_DISTANCE, visible, directional, X, W)


class PipelineChecks(unittest.TestCase):
    def test_global_filter_exactly_preserves_reference_and_early_conditions(self):
        _, _, eligible, original, ids, _ = source()
        rows, _, _ = prepare(eligible, local=False)
        self.assertEqual({r["trial_id"] for r in original}, {r["trial_id"] for r in rows})
        early, _, _ = prepare(eligible, early=True)
        at, baseline = tensors(early, ids)
        self.assertTrue((np.isfinite(at).sum(-1) > 0).all())
        self.assertTrue((np.isfinite(baseline).sum((-1, -2)) > 0).all())
        self.assertEqual(len(ids), 40)
        self.assertTrue(all(int(r["block_number"]) <= 3 for r in early))
        self.assertTrue(all(pid not in {"P011", "P033"} for pid in ids))

    def test_one_pass_sample_sd_filter_small_groups_and_outlier(self):
        rows = [dict(trial_id=str(i), reaction_time_ms=str(v), group="large")
                for i, v in enumerate([500.]*19+[5000.])]
        rows += [dict(trial_id="small"+str(i), reaction_time_ms=str(v), group="small")
                 for i, v in enumerate([500., 500., 500., 5000.])]
        rows += [dict(trial_id="single", reaction_time_ms="600", group="single")]
        kept, detail = trim(rows, ["group"])
        self.assertNotIn("19", {r["trial_id"] for r in kept})
        self.assertTrue({"small3", "single"}.issubset({r["trial_id"] for r in kept}))
        for n in range(2, 9):
            z = np.array([0.]*(n-1)+[1.])
            z = (z-z.mean())/z.std(ddof=1)
            self.assertLess(np.max(np.abs(z)), 2.5)
        self.assertEqual(len(detail), len(rows))

    def test_rolling_precision_covariance_rank_and_information_loss(self):
        n = np.array([4, 8, 6, 5, 7.])
        h = (np.eye(5)[:-1]+np.eye(5)[1:])/2
        covariance = (h/n)@h.T
        precision, rank = mean_precision(n[None, None], True)
        self.assertEqual(rank.item(), 4)
        self.assertGreater(covariance[0, 1], 0)
        np.testing.assert_allclose(precision[0, 0], h.T@linalg.solve(covariance, h), atol=1e-13)
        np.testing.assert_allclose(precision[0, 0]@np.array([1, -1, 1, -1, 1.]), 0, atol=1e-13)
        self.assertGreaterEqual(np.linalg.eigvalsh(np.diag(n)-precision[0, 0]).min(), -1e-12)
        rng = np.random.default_rng(789)
        rolled = rng.normal(size=(100000, 5))/np.sqrt(n)@h.T
        np.testing.assert_allclose(np.cov(rolled.T), covariance, atol=.0016)
        p, ranks = mean_precision(np.array([[[4, 8, 0, 5, 7]]]), True)
        self.assertEqual(ranks.item(), 2)
        np.testing.assert_allclose(p[0, 0, 2], 0)

    def test_identity_likelihood_matches_both_preserved_models(self):
        rng = np.random.default_rng(782)
        at, baseline = rng.normal(600, 90, (1, 4, 5, 3)), rng.normal(610, 80, (1, 4, 5, 2))
        at[0, 2, 1] = np.nan
        for shape in ("broad", "visible95"):
            old = directional.make_model(["P000"], at, baseline) if shape == "broad" else visible.make_model(["P000"], at, baseline)
            new = make_model(["P000"], at, baseline, shape, False)
            expected = old.compile_logp(vars=old.potentials)(old.initial_point())
            actual = new.compile_logp(vars=new.potentials)(new.initial_point())
            self.assertAlmostEqual(actual, expected, delta=2e-8)

    def test_rolling_likelihood_against_independent_joint_normal(self):
        rng = np.random.default_rng(83)
        at, baseline = rng.normal(600, 90, (1, 4, 5, 3)), rng.normal(610, 80, (1, 4, 5, 2))
        at[0, 2, 1] = np.nan
        model = make_model(["P000"], at, baseline, "broad", True)
        point = model.initial_point()
        point["sigma_at_log__"][:] = np.log(.12)
        point["sigma_baseline_log__"][:] = np.log(.14)
        actual = model.compile_logp(vars=model.potentials)(point)
        q = special.expit((X-55)/15)-.5
        reference = 0.
        for c in range(4):
            a, b = at[0, c]/1000, baseline[0, c].reshape(-1)/1000
            n = np.isfinite(a).sum(-1)
            mean = np.divide(np.nansum(a, -1), n, out=np.zeros(5), where=n > 0)
            sse = np.nansum((a-mean[:, None])**2)
            df = np.maximum(n-1, 0).sum()
            h = (np.eye(5)[:-1]+np.eye(5)[1:])/2
            h = h[np.all((h == 0) | (n[None, :] > 0), axis=1)]
            noise = (h/np.maximum(n, 1))@h.T
            y = np.r_[b, h@mean]
            d = np.r_[np.zeros(len(b)), np.ones(len(h))]
            aq = np.r_[np.zeros(len(b)), h@q]
            covariance = linalg.block_diag(.14**2*np.eye(len(b)), .12**2*noise)
            covariance += .4**2*np.ones_like(covariance)+.2**2*np.outer(d, d)+.15**2*np.outer(aq, aq)
            reference += stats.multivariate_normal.logpdf(y, np.full(len(y), .6), covariance)
            reference += .5*len(y)*np.log(2*np.pi)+.5*np.linalg.slogdet(noise)[1]-.5*df*np.log(.12**2)-sse/(2*.12**2)
            cross = .15**2*aq
            am = cross@linalg.solve(covariance, y-.6)
            av = .15**2-cross@linalg.solve(covariance, cross)
            reference += np.log(2)+stats.norm.logcdf(am/np.sqrt(av))
        self.assertAlmostEqual(actual, reference, delta=2e-8)

    def test_held_out_rt_cannot_change_training_filters_or_smoother(self):
        _, _, eligible, _, ids, _ = source()
        distance = 50.
        changed = [{**r, "reaction_time_ms": str(float(r["reaction_time_ms"])*1000)}
                   if r["trial_type"] == "Audio-Tactile" and SOA_DISTANCE[float(r["soa_ms"])] == distance
                   else r for r in eligible]
        a, ga, la = prepare(eligible, held=distance)
        b, gb, lb = prepare(changed, held=distance)
        self.assertEqual({r["trial_id"] for r in a}, {r["trial_id"] for r in b})
        np.testing.assert_allclose(ga.mean_ms, gb.mean_ms)
        np.testing.assert_allclose(la.mean_ms, lb.mean_ms)
        at, _ = tensors(a, ids)
        self.assertFalse(np.isfinite(at[:, :, 2]).any())
        precision, _ = mean_precision(np.isfinite(at).sum(-1), True)
        np.testing.assert_allclose(precision[..., 2, :], 0)

    def test_factorial_contrast_and_convolved_model_geometry(self):
        cells = np.array([20., 25., 30., 42.])
        np.testing.assert_allclose(W[:3]@cells, [13.5, 8.5, 7.])
        h = (np.eye(5)[:-1]+np.eye(5)[1:])/2
        q = special.expit((X-61)/8)
        self.assertGreater(np.max(abs(h@q-special.expit((h@X-61)/8))), .01)

    def test_time_slope_matches_ols_and_singleton_variance_is_undefined(self):
        from diagnostics import time_slope, residual_sd
        import pandas as pd
        rng = np.random.default_rng(819)
        distance = np.tile(np.arange(5), 9)
        t = rng.uniform(size=45)
        y = 500+distance*10+43*t+rng.normal(0, 3, 45)
        design = np.column_stack([(distance == d).astype(float) for d in range(5)]+[t])
        expected = np.linalg.lstsq(design, y, rcond=None)[0][-1]
        self.assertAlmostEqual(time_slope(y, distance, t), expected, places=9)
        singletons = pd.DataFrame(dict(soa_ms=np.arange(5), rt=np.arange(5)+500.))
        self.assertTrue(np.isnan(residual_sd(singletons)))


if __name__ == "__main__":
    unittest.main()
