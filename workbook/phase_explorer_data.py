"""Prepare phase-explorer views from the audited, equally weighted person cells."""
from phase_rt import describe


def build_phase_explorer(saved, phase_groups):
    lookup = {(r['participant_id'], r['phase'], r['trial_group']): float(r['reaction_time_ms'])
              for r in phase_groups}
    ids = sorted({r['participant_id'] for r in phase_groups})
    result = {}
    for outcome in ('raw', 'corrected'):
        summaries, rows = [], []
        for group in saved['trial_groups']:
            name = group['trial_group']
            if outcome == 'corrected' and name == 'Baseline':
                continue
            selected = []
            for pid in ids:
                raw = [lookup[pid, phase, name] for phase in ('Exhale', 'Inhale')]
                baseline = [lookup[pid, phase, 'Baseline'] for phase in ('Exhale', 'Inhale')]
                exhale, inhale = [value-base if outcome == 'corrected' else value for value, base in zip(raw, baseline)]
                selected.append(dict(participant_id=pid, trial_group=name,
                    exhale_ms=exhale, inhale_ms=inhale, delta_ms=inhale-exhale,
                    raw_exhale_ms=raw[0], raw_inhale_ms=raw[1],
                    baseline_exhale_ms=baseline[0], baseline_inhale_ms=baseline[1]))
            rows.extend(selected)
            summaries.append(group if outcome == 'raw' else dict(trial_group=name,
                **describe([r['delta_ms'] for r in selected])))
        result[outcome] = dict(groups=summaries, rows=rows)
    return result
