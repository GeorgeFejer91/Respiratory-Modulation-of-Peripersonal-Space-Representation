"""Recovery, direction, normalization and leakage checks for individual proxies."""

import unittest
from unittest.mock import patch

import numpy as np
from scipy import optimize, special, stats

from descriptive_sigmoid import predict
from participant_sigmoid import (PenalizedGrid, X, catalogue, estimate, method_catalogue,
    linkage_audit, metrics, resample_trials, shared_plateaus, summarize, trial_tensor,
    parameter_contrasts, contrast_correlation, person_records, repeated_parameter_models, attach_refit_intervals,
    spatial_parameter_models, spatial_catalogue, correlations)


class ParticipantSigmoidTests(unittest.TestCase):
    def test_spatial_models_separate_opposite_within_and_between_effects(self):
        rng=np.random.default_rng(95);n=60;level=rng.normal(4,.4,n);delta=rng.normal(.6,.4,n)
        order=np.arange(n)%2;c=np.array([-.5,-.5,.5,.5]);p=np.array([-.5,.5,-.5,.5])
        midpoint=45+2*(level-level.mean())[:,None]+(3-4*(delta-delta.mean())+.7*order)[:,None]*c
        midpoint=midpoint+(1+1.5*(level-level.mean()))[:,None]*p+(2+.8*(delta-delta.mean()))[:,None]*c*p
        midpoint=midpoint+rng.normal(0,.005,(n,4));sharpness=np.full((n,4),.025)
        pars=np.stack([np.full((n,4),600.),np.full((n,4),80.),(midpoint-10)/90,1/(360*sharpness)],axis=-1)
        ids=[str(i) for i in range(n)]
        q={"scores":[dict(participant_id=pid,spfrref_control_ordinal=level[i]-delta[i]/2,
            spfrref_viscereality_ordinal=level[i]+delta[i]/2,spfrref_delta=delta[i],
            condition_order=("Control-Viscereality","Viscereality-Control")[order[i]]) for i,pid in enumerate(ids)]}
        rows=spatial_parameter_models(pars,ids,q,"individual_plateaus")
        self.assertEqual(len(rows),16)
        for effect,predictor,truth in (("Mean across cells","spfrref_mean",2.),("Phase","spfrref_mean",1.5),
                ("Condition","spfrref_delta",-4.),("Condition × Phase","spfrref_delta",.8)):
            row=next(r for r in rows if r['effect']==effect and r['predictor']==predictor and r['parameter']=='midpoint_cm' and r['order_adjusted'])
            self.assertAlmostEqual(row['estimate'],truth,delta=.015)
        self.assertNotIn('spfrref_mean',q['scores'][0])
        coefficients=spatial_parameter_models(pars,ids,q,"individual_plateaus",True)
        for row,value in zip(rows,coefficients):self.assertEqual(row['estimate'],value)
        previous=repeated_parameter_models(pars,ids,q,'individual_plateaus')
        for row in rows:
            if row['predictor']!='spfrref_delta':continue
            before=next(r for r in previous if all(r[k]==row[k] for k in ('effect','predictor','parameter','order_adjusted')))
            self.assertEqual({k:v for k,v in row.items() if k!='spatial_component'},before)
        shifted=pars.copy();shifted[:,:,2]+=rng.normal(0,2,(n,1))
        after=spatial_parameter_models(shifted,ids,q,'individual_plateaus')
        for before,new in zip(rows,after):
            if before['predictor']=='spfrref_delta' and before['parameter']=='midpoint_cm':
                for key in ('estimate','se','hc3_se'):self.assertAlmostEqual(before[key],new[key],places=9)
        q['scores'][0]['spfrref_control_ordinal']=None;q['scores'][0]['spfrref_delta']=None
        self.assertTrue(all(r['n']==n-1 for r in spatial_parameter_models(pars,ids,q,'individual_plateaus')))
        q['scores'][1]['condition_order']='unknown'
        incomplete=spatial_parameter_models(pars,ids,q,'individual_plateaus')
        self.assertTrue(all(r['n']==n-2 for r in incomplete if r['order_adjusted']))
        for record in q['scores']:
            record.update(spfrref_control_ordinal=4,spfrref_viscereality_ordinal=4,spfrref_delta=0)
        self.assertTrue(all(r['status']=='not_estimable' for r in spatial_parameter_models(pars,ids,q,'individual_plateaus')))

    def test_spatial_cell_correlations_match_the_correct_condition_and_phase(self):
        records=[]
        for i in range(9):
            record={'spfrref_control_ordinal':i,'spfrref_viscereality_ordinal':8-i}
            for cell in ('control_exhale','control_inhale','viscereality_exhale','viscereality_inhale'):
                value=(i if cell.startswith('control') else 8-i)*(1 if cell.endswith('exhale') else -1)
                for metric in ('midpoint_cm','normalized_steepness_per_cm'):record[metric+'_'+cell]=value
            records.append(record)
        values=correlations(records,spatial_catalogue())
        self.assertEqual(len(values),8)
        np.testing.assert_allclose(values,[1,1,-1,-1,1,1,-1,-1])

    def test_repeated_parameter_models_recover_interactions_and_respect_missingness(self):
        rng=np.random.default_rng(72);n=48;x=rng.normal(size=n);order=np.arange(n)%2
        c=np.array([-.5,-.5,.5,.5]);p=np.array([-.5,.5,-.5,.5])
        midpoint=45+rng.normal(0,4,(n,1))+(2+3*x+.7*order)[:,None]*c+(-1+2*x)[:,None]*p+(4-x)[:,None]*c*p+rng.normal(0,.4,(n,4))
        sharpness=.025+rng.normal(0,.002,(n,4))
        pars=np.stack([np.full((n,4),600.),np.full((n,4),80.),(midpoint-10)/90,1/(360*sharpness)],axis=-1)
        ids=[str(i) for i in range(n)]
        q={"scores":[dict(participant_id=pid,maia2_trusting=x[i],condition_order=("Control-Viscereality","Viscereality-Control")[order[i]]) for i,pid in enumerate(ids)]}
        rows=repeated_parameter_models(pars,ids,q,"individual_plateaus")
        self.assertEqual(len(rows),166)
        selected=lambda a:next(r for r in a if r['effect']=='Condition' and r['parameter']=='midpoint_cm' and r['predictor']=='maia2_trusting' and r['order_adjusted'])
        r=selected(rows);self.assertAlmostEqual(r['estimate'],3.,delta=.12)
        self.assertEqual((r['df1'],r['df2']),(1,n-3))
        self.assertAlmostEqual(r['F'],(r['estimate']/r['se'])**2)
        shifted=pars.copy();shifted[:,:,2]+=rng.normal(0,10,(n,1))
        after=selected(repeated_parameter_models(shifted,ids,q,"individual_plateaus"))
        for key in ('estimate','F','p','hc3_se'):self.assertAlmostEqual(r[key],after[key],places=8)
        coefficients=repeated_parameter_models(pars,ids,q,"individual_plateaus",True)
        for a,b in zip(rows,coefficients):self.assertEqual(a['estimate'],b)
        q['scores'][0]['maia2_trusting']=None
        self.assertEqual(selected(repeated_parameter_models(pars,ids,q,'individual_plateaus'))['n'],n-1)
        q['scores'][1]['condition_order']='unknown'
        incomplete=repeated_parameter_models(pars,ids,q,'individual_plateaus')
        self.assertEqual(selected(incomplete)['n'],n-2)
        unadjusted=next(a for a in incomplete if a['predictor']=='maia2_trusting' and not a['order_adjusted'])
        self.assertEqual(unadjusted['n'],n-1)
        constant=pars.copy();constant[:,:,2]=.5;constant[:,:,3]=.1
        self.assertTrue(all(a['status']=='not_estimable' for a in repeated_parameter_models(constant,ids,q,'individual_plateaus')))
        for record in q['scores']:record['maia2_trusting']=1.
        self.assertEqual(selected(repeated_parameter_models(pars,ids,q,'individual_plateaus'))['status'],'not_estimable')

    def test_refit_intervals_retain_undefined_draw_counts(self):
        rows=[{},{}];attach_refit_intervals(rows,[[1.,None],[2.,None],[3.,4.]])
        self.assertEqual(rows[0]['refit_bootstrap_valid'],3)
        self.assertAlmostEqual(rows[0]['refit_ci_low'],1.05)
        self.assertEqual(rows[1]['refit_bootstrap_valid'],1)

    def test_contrast_ranks_preserve_mathematical_ties_despite_machine_roundoff(self):
        truth=np.array([0.,0.,0.,1.,2.]);noise=np.array([0.,2e-15,-2e-15,0.,0.])
        y=np.arange(5.)
        self.assertAlmostEqual(contrast_correlation(truth+noise,y),stats.spearmanr(truth,y).statistic)
        self.assertIsNone(contrast_correlation(noise,np.arange(5.)))
        pars=np.array([[[600.,80.,.5,.10],[600.,80.,.5,.12],[600.,80.,.5,.12],[600.,80.,.5,.10]],
                       [[600.,90.,.5,.12],[600.,90.,.5,.10],[600.,90.,.5,.10],[600.,90.,.5,.12]]])
        records=person_records(pars,['A','B'],{'scores':[{'participant_id':i} for i in ('A','B')]})
        self.assertTrue(all(r['normalized_steepness_per_cm_condition_delta']==0. for r in records))

    def test_within_person_changes_cancel_offsets_and_recover_factor_effects(self):
        # A 2x2 experiment with a 6-unit Condition effect, 2-unit Phase effect and 4-unit interaction.
        cells=np.array([0.,0.,4.,8.])[None,:,None]*np.array([1.,2.,3.])[None,None,:]
        expected=np.array([[[6.,12.,18.],[2.,4.,6.],[4.,8.,12.]]])
        np.testing.assert_allclose(parameter_contrasts(cells),expected)
        offsets=np.arange(5.)[:,None,None,None]*100
        np.testing.assert_allclose(parameter_contrasts(cells[None]+offsets),np.repeat(expected[None],5,axis=0))

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
