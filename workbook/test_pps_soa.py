"""Independent numerical checks for the basic Segment 1 SOA test."""
import unittest
import json
import zipfile
from hashlib import sha256
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.anova import AnovaRM

from inference import repeated_anova
from paper_analysis import clean, grouped_means
from pps_soa import analyze
from preparation import load_pair, local_release_pair


class SOATests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.people, cls.trials = load_pair(*local_release_pair())
        cls.report, cls.cube, cls.means = analyze(cls.people, cls.trials)

    def test_independent_one_factor_anova_and_epsilon(self):
        frame = pd.DataFrame(self.means, index=self.report['participant_ids'],
                             columns=[300, 800, 1500, 2200, 2700])
        long = frame.rename_axis('participant_id').reset_index().melt(
            id_vars='participant_id', var_name='soa_ms', value_name='rt')
        reference = AnovaRM(long, 'rt', 'participant_id', within=['soa_ms']).fit().anova_table.iloc[0]
        result = self.report['anova']
        np.testing.assert_allclose([result['F'], result['df1'], result['df2'], result['p_uncorrected']],
            [reference['F Value'], reference['Num DF'], reference['Den DF'], reference['Pr > F']], rtol=1e-10)
        center = np.eye(5) - np.ones((5, 5))/5
        covariance = center @ np.cov(self.means.T, ddof=1) @ center
        epsilon = np.trace(covariance)**2 / (4*np.trace(covariance @ covariance))
        self.assertAlmostEqual(result['epsilon_GG'], epsilon, places=12)
        self.assertAlmostEqual(result['p_GG'], stats.f.sf(result['F'], 4*epsilon, 156*epsilon), places=12)

    def test_equal_cells_not_pooled_trials_and_interval(self):
        retained, _, _ = clean(self.people, self.trials)
        frame = pd.DataFrame(retained)
        frame['reaction_time_ms'] = pd.to_numeric(frame.reaction_time_ms)
        base = frame[frame.trial_type == 'Baseline'].groupby(
            ['participant_id','condition','phase']).reaction_time_ms.mean().rename('baseline_mean_ms')
        frame = frame.join(base, on=['participant_id','condition','phase'])
        frame['corrected_rt_ms'] = frame.reaction_time_ms-frame.baseline_mean_ms
        frame = frame[(frame.trial_type == 'Audio-Tactile') & ~frame.participant_id.isin(['P011','P033'])]
        cells = frame.groupby(['participant_id', 'condition', 'phase', 'soa_ms']).corrected_rt_ms.mean()
        reference = cells.groupby(['participant_id','soa_ms']).mean().unstack()
        reference.columns = reference.columns.astype(float)
        reference = reference.reindex(columns=[300,800,1500,2200,2700])
        np.testing.assert_allclose(self.means, reference.to_numpy(), atol=1e-10)
        self.assertEqual(len(self.means), 40)
        self.assertEqual(self.report['incomplete_excluded'], [])
        for record, values in zip(self.report['summary'], reference.to_numpy().T):
            low, high = stats.t.interval(.95, 39, loc=values.mean(), scale=stats.sem(values))
            np.testing.assert_allclose([record['ci_low_ms'],record['ci_high_ms']], [low,high])
        self.assertEqual(set(self.report['excluded_linkage']), {'P011','P033'})
        self.assertEqual(self.report['measure'], 'corrected_rt_ms')

    def test_matched_baseline_translation_and_incomplete_cells(self):
        retained, _, _ = clean(self.people, self.trials)
        baseline = grouped_means([r for r in retained if r['trial_type']=='Baseline'],
                                 ('participant_id','condition','phase'))
        raw_report, raw_cube, _ = analyze(self.people, self.trials, baseline_correct=False)
        corrected = raw_cube.copy()
        for i, pid in enumerate(self.report['participant_ids']):
            for ci, condition in enumerate(('Control','Viscereality')):
                for pi, phase in enumerate(('Exhale','Inhale')):
                    corrected[i,ci,pi] -= baseline[pid,condition,phase]
        np.testing.assert_allclose(self.cube, corrected, atol=1e-12)
        test = next(r for r in repeated_anova(corrected) if r['effect']=='SOA')
        np.testing.assert_allclose([test['F'],test['epsilon_GG'],test['p_GG']],
            [self.report['anova'][k] for k in ('F','epsilon_GG','p_GG')], rtol=1e-10)
        np.testing.assert_allclose([raw_report['anova'][k] for k in ('F','epsilon_GG','p_GG')],
            [self.report['anova'][k] for k in ('F','epsilon_GG','p_GG')], rtol=1e-10)
        removed = [r for r in self.trials if not (r['participant_id']=='P001' and
            r['trial_type']=='Audio-Tactile' and r['condition']=='Control' and
            r['phase']=='Exhale' and float(r['soa_ms'])==300)]
        report, _, _ = analyze(self.people, removed)
        self.assertIn('P001', report['incomplete_excluded'])
        self.assertEqual(report['anova']['n'], 39)
        missing = [r for r in self.trials if not (r['participant_id']=='P001' and
            r['trial_type']=='Baseline' and r['condition']=='Control' and r['phase']=='Exhale')]
        report, _, _ = analyze(self.people, missing)
        self.assertIn('P001', report['missing_baseline_excluded'])
        self.assertNotIn('P001', report['participant_ids'])

    def test_saved_hashes_archive_and_portable_text_bytes(self):
        root = Path(__file__).resolve().parents[1]
        folder = root / 'results/pps_soa'
        manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
        for section, prefix in (('source_sha256', root), ('input_sha256', root/'data/raw'),
                                ('artifact_sha256', folder)):
            for name, digest in manifest[section].items():
                data = (prefix / name).read_bytes()
                self.assertEqual(sha256(data).hexdigest(), digest, name)
                if section == 'artifact_sha256' and name.endswith(('.json','.md','.csv','.svg')):
                    self.assertNotIn(b'\r\n', data, 'Generated text must survive Git LF conversion')
        with zipfile.ZipFile(folder / 'results.zip') as archive:
            self.assertEqual(set(archive.namelist()), {*manifest['artifact_sha256'], 'manifest.json'})
            for name in archive.namelist():
                self.assertEqual(archive.read(name), (folder / name).read_bytes())
        saved = json.loads((folder / 'results.json').read_text(encoding='utf-8'))
        self.assertEqual(saved['anova'].keys(), self.report['anova'].keys())
        for key, value in saved['anova'].items():
            if isinstance(value, (float, int)):
                np.testing.assert_allclose(value, self.report['anova'][key], rtol=1e-12, atol=1e-14)
            else:
                self.assertEqual(value, self.report['anova'][key])


if __name__ == '__main__':
    unittest.main()
