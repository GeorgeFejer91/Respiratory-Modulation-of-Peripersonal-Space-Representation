"""Numerical behavior tests for the portable scientific engine."""

import copy
import unittest

import numpy as np
from scipy import stats

from inference import holm,jzs,mixed_ml,paired,repeated_anova,sign_flip
from paper_analysis import clean
from preparation import demo_pair,load_pair


class InferenceTests(unittest.TestCase):
    def test_profile_likelihood_matches_dense_gaussian_density(self):
        rng=np.random.default_rng(19)
        groups=np.repeat(np.arange(8),8)
        z=rng.normal(size=len(groups))
        x=np.column_stack([np.ones(len(z)),z])
        y=2+3*z+np.repeat(rng.normal(size=8),8)+rng.normal(size=len(z))
        fit=mixed_ml(x,y,groups)
        ratio=fit["relative_covariance"][0][0]
        covariance=fit["residual_variance"]*(np.eye(len(y))+ratio*(groups[:,None]==groups))
        dense=stats.multivariate_normal.logpdf(y,mean=x@fit["beta"],cov=covariance)
        self.assertAlmostEqual(fit["ll"],dense,places=8)
        self.assertTrue(fit["converged"])

    def test_paired_interval_is_participant_based(self):
        values=np.array([1.,3.,4.,7.,8.])
        result=paired(values,bayes=False)
        expected=stats.ttest_1samp(values,0)
        self.assertEqual(result["n"],5)
        self.assertAlmostEqual(result["t"],expected.statistic,places=12)
        self.assertAlmostEqual(result["p"],expected.pvalue,places=12)
        self.assertLess(result["ci_low"],result["estimate"])

    def test_sign_flip_uses_exact_distribution_for_small_samples(self):
        result=sign_flip([1.,2.,3.])
        self.assertEqual(result["method"],"exact sign-flip")
        self.assertEqual(result["draws"],8)
        self.assertAlmostEqual(result["p"],.25)

    def test_jzs_null_and_reference_value(self):
        self.assertAlmostEqual(jzs(.1,40),.17138307217032722,places=9)
        self.assertLess(jzs(0.,42),1)
        self.assertGreater(jzs(4.,42),1)

    def test_holm_is_monotonic_and_retains_unadjusted_values(self):
        values=[{"p":.01},{"p":.04},{"p":.03}]
        holm(values)
        self.assertEqual([r["p"] for r in values],[.01,.04,.03])
        np.testing.assert_allclose([r["p_holm"] for r in values],[.03,.06,.06])

    def test_rm_anova_has_correct_df_and_gg_limits(self):
        rng=np.random.default_rng(3)
        rows=repeated_anova(rng.normal(size=(12,2,2,5)))
        self.assertEqual(len(rows),7)
        for row in rows:
            self.assertEqual(row["df2"],row["df1"]*11)
            self.assertGreaterEqual(row["epsilon_GG"],1/row["df1"])
            self.assertLessEqual(row["epsilon_GG"],1)
        self.assertEqual(next(r for r in rows if r["effect"]=="Condition")["epsilon_GG"],1.)

    def test_catch_threshold_is_strict_and_cleaning_preserves_inputs(self):
        people,trials=load_pair(*demo_pair())
        before=copy.deepcopy((people,trials))
        _,quality,_=clean(people,trials)
        self.assertEqual((people,trials),before)
        catches=[r for r in trials if r["participant_id"]=="P000" and r["trial_type"]=="Catch"]
        for row in catches[:3]:row["outcome"]="false_alarm"
        _,quality,_=clean(people,trials)
        self.assertFalse(quality[0]["excluded_catch"])
        catches[3]["outcome"]="false_alarm"
        retained,quality,_=clean(people,trials)
        self.assertTrue(quality[0]["excluded_catch"])
        self.assertTrue(all(r["participant_id"]!="P000" for r in retained))


if __name__=="__main__":
    unittest.main()
