"""Recovery, direction, normalization and leakage checks for individual proxies."""

import unittest
from unittest.mock import patch

import numpy as np
from scipy import optimize, special

from descriptive_sigmoid import predict
from participant_sigmoid import (PenalizedGrid, X, catalogue, estimate, method_catalogue,
    linkage_audit, metrics, resample_trials, shared_plateaus, summarize, trial_tensor)


class ParticipantSigmoidTests(unittest.TestCase):
    def test_known_shape_signed_direction_and_flat_profile(self):
        grid=PenalizedGrid(fine=True)
        truth=np.array([[600.,80.,.45,.10],[650.,-90.,.50,.12]])
        fit=grid.fit(X,predict(truth,X))
        np.testing.assert_allclose(fit[:,2],truth[:,2],atol=.01)
        np.testing.assert_allclose(fit[:,3],truth[:,3],rtol=.04)
        self.assertGreater(fit[0,1],0);self.assertLess(fit[1,1],0)
        self.assertEqual(grid.fit(X,np.full((1,5),600.))[0,1],0.)

    def test_affine_normalization_keeps_midpoint_and_does_not_reverse_response(self):
        for amplitude in (80.,-80.):
            p=np.array([[600.,amplitude,.45,.1]])
            raw=predict(p,X)[0];lower=min(p[0,0],p[0,0]+amplitude)
            normalized=(raw-lower)/abs(amplitude)
            expected=special.expit((X-.45)/.1)
            np.testing.assert_allclose(normalized,expected if amplitude>0 else 1-expected)
            self.assertAlmostEqual(metrics(p)[0,2],amplitude/(360*.1))
            self.assertEqual(10+90*p[0,2],50.5)

    def test_penalized_grid_matches_independent_scalar_objective(self):
        grid=PenalizedGrid();y=np.array([[600.,610.,655.,670.,680.]])
        center=np.array([[.45,.12]]);variance=np.array([100.]);strength=4.
        fit=grid.fit(X,y,variance,center,strength)
        reference=[]
        for m,w in grid.shapes:
            q=special.expit((X-m)/w);design=np.column_stack([np.ones(5),q])
            b,a=np.linalg.lstsq(design,y[0],rcond=None)[0]
            a=np.clip(a,-500,500);b=np.mean(y[0]-a*q)
            loss=np.sum((y[0]-b-a*q)**2)/100+4*(((m-.45)/.25)**2+(np.log(w/.12)/np.log(2))**2)
            reference.append((loss,[b,a,m,w]))
        expected=min(reference,key=lambda r:round(r[0],10))[1]
        np.testing.assert_allclose(fit[0],expected,atol=1e-10)

    def test_pool_excludes_all_copies_of_target_person(self):
        rng=np.random.default_rng(5);cube=rng.normal(600,20,(7,4,5));variance=np.full_like(cube,100.)
        identities=np.array([0,0,1,2,3,4,5]);method=method_catalogue()[1];grid=PenalizedGrid()
        _,before,_=estimate(cube,variance,method,grid,identities=identities)
        cube[:2,:,2]+=1000
        _,after,_=estimate(cube,variance,method,grid,identities=identities)
        np.testing.assert_array_equal(before[:2],after[:2])

    def test_external_pool_does_not_use_test_person_outcome(self):
        rng=np.random.default_rng(6);train=rng.normal(600,20,(7,4,5));test=train[:2].copy()
        method=method_catalogue()[1];grid=PenalizedGrid();v=np.full_like(test,100.)
        _,before,_=estimate(test,v,method,grid,training=train)
        test[:,:,2]+=1000
        _,after,_=estimate(test,v,method,grid,training=train)
        np.testing.assert_array_equal(before,after)

    def test_shared_plateaus_recover_joint_signal_and_preserve_common_endpoints(self):
        truth=np.array([[[600.,80.,.4,.1],[600.,80.,.5,.1],[600.,80.,.55,.12],[600.,80.,.45,.12]]])
        y=predict(truth.reshape(-1,4),X).reshape(1,4,5);grid=PenalizedGrid(fine=True)
        initial=grid.fit(X,y.reshape(-1,5)).reshape(1,4,4)
        result,converged=shared_plateaus(y,np.ones_like(y)*100,{'penalty':0.},grid,truth[:,:,2:],initial)
        self.assertTrue(converged.all())
        self.assertLess(np.max(abs(predict(result.reshape(-1,4),X)-y.reshape(-1,5))),.2)
        self.assertEqual(np.ptp(result[0,:,0]),0.);self.assertEqual(np.ptp(result[0,:,1]),0.)

    def test_trial_bootstrap_preserves_cell_counts_and_robust_summary(self):
        tensor=np.full((2,4,5,6),np.nan);tensor[0,:,:,:3]=[1.,2.,10.];tensor[1,:,:,:5]=[1.,2.,3.,4.,100.]
        sample=resample_trials(tensor,np.random.default_rng(8))
        np.testing.assert_array_equal(np.isfinite(sample).sum(-1),np.isfinite(tensor).sum(-1))
        self.assertEqual(summarize(tensor,'trim20')[0][1,0,0],3.)
        self.assertEqual(summarize(tensor,'median')[0][0,0,0],2.)
        self.assertEqual(len(catalogue()),126)
        self.assertEqual(sum(r['scope']=='main' for r in catalogue()),27)
        self.assertEqual(trial_tensor([])[0],[])

    def test_linkage_audit_detects_condition_swapped_recording_and_keeps_rows(self):
        rows=[]
        for pid,order in (("A",("Control","Viscereality")),("B",("Viscereality","Control"))):
            for k,c in enumerate(order):
                rows.append(dict(participant_id=pid,trial_index=k,condition=c,trial_type="Audio-Tactile",
                                 phase="Exhale",soa_ms=300,reaction_time_ms=600+k,outcome="hit"))
        audit=linkage_audit(rows)
        self.assertEqual(audit['groups'][0]['participant_ids'],['A','B'])
        self.assertEqual(audit['groups'][0]['condition_label_relationship'],['swapped'])
        self.assertEqual(len(rows),4)
        rows[-1]['reaction_time_ms']=602
        self.assertFalse(linkage_audit(rows)['groups'])


if __name__=='__main__':unittest.main()
