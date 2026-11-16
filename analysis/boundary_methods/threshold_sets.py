"""Exact compatibility over five monotone probe means in a rectangular band."""

from dataclasses import dataclass

import numpy as np

TOLERANCE_MS = 1e-9


@dataclass
class OrderedBand:
    minimum: np.ndarray
    maximum: np.ndarray

    @classmethod
    def from_limits(cls, lower, upper):
        """Tighten to pointwise extrema attained by feasible ordered sequences."""
        least = np.maximum.accumulate(lower, axis=-1)
        greatest = np.minimum.accumulate(upper[..., ::-1], axis=-1)[..., ::-1]
        return cls(least, greatest)

    @property
    def feasible(self):
        return (self.minimum <= self.maximum + TOLERANCE_MS).all(-1)

    @property
    def flat(self):
        return self.feasible & (self.minimum[..., -1] <= self.maximum[..., 0]+TOLERANCE_MS)

    def crosses(self, target):
        """Return feasible closed intervals and possible plateau or censoring."""
        lo, hi = self.minimum, self.maximum
        valid = self.feasible
        le = lo <= target+TOLERANCE_MS
        ge = hi >= target-TOLERANCE_MS
        return CrossingSet(
            intervals=(le[..., :-1] & ge[..., 1:]) & valid[..., None],
            plateau=(le[..., 1:] & ge[..., :-1]).any(-1) & valid,
            no_rise=np.zeros_like(valid),
            left=(hi[..., 0] > target+TOLERANCE_MS) & valid,
            right=(lo[..., -1] < target-TOLERANCE_MS) & valid,
        )

    def midpoint(self):
        lo, hi = self.minimum, self.maximum
        inside = self._half_feasible(lo[..., :-1], hi[..., 1:])
        # A positive-span midpoint differs from both response endpoints.
        plateau = self._half_feasible(lo[..., 2:-1], hi[..., 1:-2])
        absent = np.zeros_like(self.feasible)
        return CrossingSet(inside, plateau.any(-1), self.flat, absent, absent)

    def _half_feasible(self, target_lower, target_upper):
        """Check whether a positive-span endpoint pair puts its mean in the target band."""
        a = self.minimum[..., :1]
        b = self.maximum[..., -1:]
        # The initial pair maximizes the span. If its sum is out of range,
        # move the nearest endpoint just enough to reach the required sum.
        smallest_a = np.maximum(a, 2*target_lower-b)
        largest_b = np.minimum(b, 2*target_upper-a)
        return (
            self.feasible[..., None]
            & (target_lower <= target_upper+TOLERANCE_MS)
            & (smallest_a <= self.maximum[..., :1]+TOLERANCE_MS)
            & (largest_b >= self.minimum[..., -1:]-TOLERANCE_MS)
            & (largest_b-smallest_a > TOLERANCE_MS)
        )


@dataclass
class CrossingSet:
    intervals: np.ndarray
    plateau: np.ndarray
    no_rise: np.ndarray
    left: np.ndarray
    right: np.ndarray

    @property
    def localized(self):
        return (self.intervals.any(-1) & ~self.intervals.all(-1) & ~self.plateau
                & ~self.no_rise & ~self.left & ~self.right)

    def pieces(self, distance, index):
        included = self.intervals[index]
        edges = np.flatnonzero(np.diff(np.r_[False, included, False]))
        return [[float(distance[lo]), float(distance[hi])] for lo, hi in edges.reshape(-1, 2)]
