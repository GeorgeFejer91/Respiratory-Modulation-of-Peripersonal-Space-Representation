"""Scientific behavior checks for the descriptive extraction and sigmoid model."""

import unittest

import numpy as np
from scipy import optimize

from descriptive_sigmoid import (ProfileGrid, extract_cells, parameter_rows,
                                 predict, smooth, smoother_specs)


class DescriptiveSigmoidTests(unittest.TestCase):
    def test_known_sigmoids_recovered_from_five_uneven_positions(self):
        x=np.array([0.,17/90,40/90,63/90,1.])
        expected=np.array([[630.,50.,.3,.15],[650.,30.,.6,.2],[610.,40.,.5,.1],[660.,25.,.7,.3]])
        fit=ProfileGrid(fine=True).fit(x,predict(expected,x))
        np.testing.assert_allclose(fit[:,2],expected[:,2],atol=.01)
        np.testing.assert_allclose(fit[:,3],expected[:,3],rtol=.04)
        self.assertLess(np.max(np.abs(predict(fit,x)-predict(expected,x))),.12)

    def test_profile_grid_agrees_with_independent_nonlinear_optimization(self):
        x=np.array([0.,.2,.45,.7,1.])
        y=np.array([[650.,655.,667.,681.,687.]])
        fit=ProfileGrid(fine=True).fit(x,y)
        reference=optimize.least_squares(lambda p: predict(p[None,:],x)[0]-y[0],
            fit[0],bounds=([-2000,0,0,.05],[2000,500,1,1]),xtol=1e-12,ftol=1e-12,gtol=1e-12)
        self.assertLess(np.max(np.abs(predict(fit,x)[0]-predict(reference.x[None,:],x)[0])),.1)

    def test_decreasing_data_cannot_manufacture_expected_direction(self):
        fit=ProfileGrid().fit(np.linspace(0,1,5),np.array([[5.,4.,3.,2.,1.]]))
        self.assertEqual(fit[0,1],0.)
        self.assertTrue(parameter_rows(fit)[0]["flat_unidentified"])

    def test_smoothers_preserve_offsets_and_local_linear_affine_signal(self):
        x=np.array([0.,.2,.45,.7,1.])
        y=np.array([[1.,3.,2.,5.,4.]])
        for kind,strength in smoother_specs():
            np.testing.assert_allclose(smooth(x,y+500,kind,strength)-500,smooth(x,y,kind,strength),atol=1e-10)
        for kind in ("gaussian_linear","tricube_linear"):
            np.testing.assert_allclose(smooth(x,(3+7*x)[None,:],kind,.75),(3+7*x)[None,:],atol=1e-10)

    def test_person_weight_does_not_depend_on_cell_trial_count(self):
        rows=[]
        for pid,values in (("A",[10.,10.,10.,10.,100.]),("B",[30.]*20)):
            for c in ("Control","Viscereality"):
                for p in ("Exhale","Inhale"):
                    for s in (300,800,1500,2200,2700):
                        rows.extend(dict(participant_id=pid,condition=c,phase=p,soa_ms=s,
                                         reaction_time_ms=v,trial_type="Audio-Tactile") for v in values)
        ids,cubes,incomplete=extract_cells(rows)
        self.assertEqual(ids,["A","B"]);self.assertFalse(incomplete)
        np.testing.assert_allclose(cubes["winsor20"].mean(0),20.)
        np.testing.assert_allclose(cubes["mean"].mean(0),29.)

    def test_reported_width_and_derivative_have_correct_units(self):
        p=np.array([[600.,40.,.5,.2]])
        row=parameter_rows(p)[0]
        h=1e-5
        derivative=(predict(p,[.5+h])[0,0]-predict(p,[.5-h])[0,0])/(2*h*90)
        self.assertAlmostEqual(row["midpoint_slope_ms_per_cm"],derivative,places=8)
        self.assertAlmostEqual(row["transition_10_90_cm"],2*np.log(9)*18)
        self.assertEqual(row["midpoint_cm"],55.)


if __name__=="__main__":
    unittest.main()
