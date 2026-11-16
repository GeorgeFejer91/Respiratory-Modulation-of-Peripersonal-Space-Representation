"""Simultaneous five-probe bounds from primitive AT and Baseline means."""

from dataclasses import dataclass

import numpy as np
from scipy.stats import t

from profile import moments
from screen import phase_profiles


@dataclass
class MeanProbeInputs:
    at: tuple
    baseline: tuple | None

    @property
    def center(self):
        at_mean = self.at[0]
        return at_mean if self.baseline is None else at_mean - self.baseline[0]

    @classmethod
    def from_trials(cls, at, baseline, correction):
        a = moments(at)
        if correction == "raw":
            return cls(a, None)
        if correction == "pooled_cp":
            baseline = baseline.reshape(*baseline.shape[:-2], 1, -1)
        return cls(a, moments(baseline))

    def room(self, alpha, phases=1):
        a_count = self.at[0].shape[-1]
        b_count = 0 if self.baseline is None else self.baseline[0].shape[-1]
        tail = alpha/(2*phases*(a_count+b_count))
        _, at_var, at_df = self.at
        radius = t.isf(tail, at_df)*np.sqrt(at_var)
        if self.baseline is not None:
            _, baseline_var, baseline_df = self.baseline
            radius += t.isf(tail, baseline_df)*np.sqrt(baseline_var)
        return radius

    def individual_bands(self, alpha):
        center = phase_profiles(self.center)
        phase = self.room(alpha)
        individual = self.room(alpha, phases=2)
        equal_phase = individual.reshape(*individual.shape[:-2], 2, 2, 5).mean(-2)
        radius = np.concatenate([phase, equal_phase], axis=-2)
        valid = np.isfinite(radius).all(-1)
        return center-radius, center+radius, valid


def group_bands(profile, alpha):
    """Construct bands over whole-person vectors, allowing any leading batches."""
    summaries = phase_profiles(profile)
    count = summaries.shape[-3]
    center = summaries.mean(-3)
    s2 = summaries.var(-3, ddof=1)/count
    radius = t.isf(alpha/(2*center.shape[-1]), count-1)*np.sqrt(s2)
    return center-radius, center+radius, np.isfinite(radius).all(-1)
