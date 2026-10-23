"""Catch baseline-sign, pairing and interval regressions in the live explorer."""
import csv
import importlib.util
import json
from pathlib import Path
import unittest

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]


class PhaseExplorerTests(unittest.TestCase):
    def test_corrected_deltas_match_independent_condition_phase_cells(self):
        self.assertIsNotNone(importlib.util.find_spec('phase_explorer_data'),
                             'The focused phase explorer data owner is missing')
        from phase_explorer_data import build_phase_explorer
        saved = json.loads((ROOT/'results/phase_rt/results.json').read_text())
        with (ROOT/'results/phase_rt/participant_trial_groups.csv').open(newline='') as source:
            groups = list(csv.DictReader(source))
        before = json.dumps([saved, groups], sort_keys=True)
        result = build_phase_explorer(saved, groups)
        self.assertEqual(json.dumps([saved, groups], sort_keys=True), before)
        self.assertEqual(result['raw']['groups'], saved['trial_groups'])
        self.assertEqual(len(result['raw']['rows']), 240)
        self.assertEqual(len(result['corrected']['rows']), 200)
        self.assertEqual(len(result['corrected']['groups']), 5)
        cells = pd.read_csv(ROOT/'results/pps_soa/participant_cells.csv')
        cells = cells[~cells.participant_id.isin(['P011', 'P033'])]
        for summary in result['corrected']['groups']:
            soa = int(summary['trial_group'].split()[1])
            pairs = cells[cells.soa_ms == soa].groupby(['participant_id', 'phase']).corrected_rt_ms.mean().unstack()
            differences = pairs.Inhale-pairs.Exhale
            interval = stats.ttest_rel(pairs.Inhale, pairs.Exhale).confidence_interval()
            np.testing.assert_allclose([summary['mean'], summary['ci_low'], summary['ci_high']],
                                       [differences.mean(), interval.low, interval.high], atol=1e-10)
            self.assertEqual(summary['n'], 40)
            rows = [r for r in result['corrected']['rows'] if r['trial_group'] == summary['trial_group']]
            self.assertEqual(len({r['participant_id'] for r in rows}), 40)
            for row in rows:
                self.assertAlmostEqual(row['delta_ms'], differences[row['participant_id']], places=10)
                self.assertAlmostEqual(row['exhale_ms'], pairs.loc[row['participant_id'], 'Exhale'], places=10)
                self.assertAlmostEqual(row['inhale_ms'], pairs.loc[row['participant_id'], 'Inhale'], places=10)
        self.assertAlmostEqual(np.mean([g['mean'] for g in result['corrected']['groups']]),
                               saved['contrasts']['corrected_rt_ms']['mean'], places=10)
        with (ROOT/'results/phase_rt/trial_group_deltas.csv').open(newline='') as source:
            original = {(r['participant_id'], r['trial_group']): float(r['delta_inhale_minus_exhale_ms']) for r in csv.DictReader(source)}
        for row in result['raw']['rows']:
            self.assertEqual(row['delta_ms'], original[row['participant_id'], row['trial_group']])
