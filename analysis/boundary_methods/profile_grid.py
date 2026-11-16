"""Bounded GLS profiles and joint projections for the five-location design."""

from dataclasses import dataclass

import numpy as np
from scipy.special import expit

MODELS = ("free", "shared_width", "shared_midpoint", "shared_both")
REFERENCES = ("flat", "linear", "log_distance")
AMPLITUDE_LIMIT = 1000.


@dataclass
class ShapeGrid:
    distance: np.ndarray
    normalized_midpoint: np.ndarray
    relative_width: np.ndarray

    @classmethod
    def logistic(cls, distance):
        return cls(np.asarray(distance), np.linspace(-1., 2., 121),
                   np.unique(np.r_[np.geomspace(.025, 2., 41), 1/6]))

    @property
    def midpoints(self):
        return self.distance[0] + self.normalized_midpoint * np.ptp(self.distance)

    @property
    def design_subset(self):
        return (self.normalized_midpoint >= -.5) & (self.normalized_midpoint <= 1.5)

    @property
    def shapes(self):
        x = (self.distance - self.distance[0]) / np.ptp(self.distance)
        z = (x - self.normalized_midpoint[:, None, None]) / self.relative_width[None, :, None]
        q = np.where(z[..., :1] > 0, -expit(-z), expit(z))
        return (q - q[..., :1]) / np.ptp(q, axis=-1, keepdims=True)

    @property
    def reference_shapes(self):
        x = self.distance
        return np.stack((np.zeros(len(x)), (x-x[0])/np.ptp(x),
                         (np.log(x)-np.log(x[0]))/np.ptp(np.log(x))))


def diag_cov(variance):
    return variance[..., None, :] * np.eye(variance.shape[-1])


class WeightedBasis:
    """Cache the contrast transformation and whitened response bases."""

    def __init__(self, covariance, shapes, training=None, span_limit=AMPLITUDE_LIMIT):
        self.covariance = covariance
        self.shapes = shapes
        self.span_limit = span_limit
        self.training = np.arange(shapes.shape[-1]) if training is None else np.asarray(training)
        count = len(self.training)
        operator = np.eye(count)[1:] - np.eye(count)[0]
        cov = covariance[..., self.training[:, None], self.training]
        transform = np.linalg.cholesky(operator @ cov @ operator.T)
        self.transform = np.linalg.solve(transform, np.broadcast_to(operator, transform.shape[:-2]+operator.shape))
        self.chosen_basis = shapes[..., self.training]
        self.white_q = np.einsum("...ij,kj->...ik", self.transform, self.chosen_basis)
        self.norm = np.square(self.white_q).sum(-2)

    def surface(self, values):
        """Loss over shape candidates, profiling out intercept and signed span."""
        y = np.einsum("...ij,...j->...i", self.transform, values[..., self.training])
        dot = np.einsum("...i,...ik->...k", y, self.white_q)
        amplitude = np.divide(dot, self.norm, out=np.zeros_like(dot), where=self.norm > 0)
        amplitude = np.clip(amplitude, -self.span_limit, self.span_limit)
        loss = np.square(y).sum(-1, keepdims=True) - 2*dot*amplitude + self.norm*np.square(amplitude)
        return np.maximum(loss, 0), amplitude

    def predict(self, values, index, amplitude, held):
        q = self.shapes[index]
        shifted = values[..., self.training] - amplitude[..., None] * q[..., self.training]
        c = self.covariance[..., self.training[:, None], self.training]
        weights = np.linalg.solve(c, np.ones((*c.shape[:-1], 1)))[..., 0]
        level = np.sum(weights*shifted, axis=-1) / weights.sum(-1)
        return level + amplitude*q[..., held]


def reduced_choices(loss, normalized_midpoint, width):
    """Return midpoint and width indices for shapes shared across cells."""
    midpoint_penalty = (normalized_midpoint-.5)**2
    width_penalty = np.log(width*6)**2
    ranked = loss + 1e-10*(midpoint_penalty[:, None] + width_penalty)
    min_m = ranked.argmin(-2)
    min_w = ranked.argmin(-1)
    free_m = ranked.min(-1).argmin(-1)
    free_w = np.take_along_axis(min_w, free_m[..., None], axis=-1)[..., 0]
    shared_w = ranked.min(-2).sum(-2).argmin(-1)
    shared_m = ranked.min(-1).sum(-2).argmin(-1)
    common = ranked.sum(-3).reshape(*loss.shape[:-3], -1).argmin(-1)
    common_m, common_w = np.divmod(common, len(width))

    def across_cells(index):
        return np.broadcast_to(index[..., None], free_m.shape)

    shared_m, shared_w = across_cells(shared_m), across_cells(shared_w)
    return {
        "free": (free_m, free_w),
        "shared_width": (np.take_along_axis(min_m, shared_w[..., None], -1)[..., 0], shared_w),
        "shared_midpoint": (shared_m, np.take_along_axis(min_w, shared_m[..., None], -1)[..., 0]),
        "shared_both": (across_cells(common_m), across_cells(common_w)),
    }


def joint_shapes(compatible, model):
    if model == "shared_width":
        return compatible & compatible.any(-2).all(-2)[..., None, None, :]
    if model == "shared_midpoint":
        return compatible & compatible.any(-1).all(-2)[..., None, :, None]
    if model == "shared_both":
        return compatible & compatible.all(-3, keepdims=True)
    return compatible


def intervals(supported, midpoints):
    """Contiguous runs of compatible grid points, without filling gaps."""
    edges = np.flatnonzero(np.diff(np.r_[False, supported, False]))
    return [[float(midpoints[lo]), float(midpoints[hi-1])] for lo, hi in edges.reshape(-1, 2)]


def contrast_range(supported, midpoints, weights, model):
    """Extrema of a midpoint contrast over an already intersected joint set."""
    active = weights != 0
    if not supported.any(axis=(-2, -1)).all():
        return None
    if model in ("shared_both", "shared_midpoint"):
        return [0., 0.]
    grid_values = midpoints[None, :, None]*weights[active, None, None]
    subset = supported[active]
    if model == "shared_width":
        widths = supported.any(-2).all(0)
        subset = subset[..., widths]
        lower = np.where(subset, grid_values, np.inf).min(-2).sum(0)
        upper = np.where(subset, grid_values, -np.inf).max(-2).sum(0)
        return [float(lower.min()), float(upper.max())]
    lower = np.where(subset, grid_values, np.inf).min((-2, -1)).sum()
    upper = np.where(subset, grid_values, -np.inf).max((-2, -1)).sum()
    return [float(lower), float(upper)]


def predict_folds(values, cov, grid, span_limit=AMPLITUDE_LIMIT):
    mid = grid.design_subset
    h = grid.shapes[mid]
    curve_basis = h.reshape(-1, len(grid.distance))
    width = grid.relative_width
    errors = {name: [] for name in (*MODELS, *REFERENCES)}
    for held in range(len(grid.distance)):
        training = np.delete(np.arange(len(grid.distance)), held)
        engine = WeightedBasis(cov, curve_basis, training, span_limit)
        loss, amplitudes = engine.surface(values)
        fitted = reduced_choices(loss.reshape(*values.shape[:-1], len(h), len(width)),
                                 grid.normalized_midpoint[mid], width)
        for name, (m, w) in fitted.items():
            idx = m*len(width) + w
            amplitude = np.take_along_axis(amplitudes, idx[..., None], -1)[..., 0]
            pred = engine.predict(values, idx, amplitude, held)
            errors[name].append(np.square(values[..., held] - pred))
        ref = WeightedBasis(cov, grid.reference_shapes, training, span_limit)
        _, amplitudes = ref.surface(values)
        for k, name in enumerate(REFERENCES):
            ids = np.full(values.shape[:-1], k)
            pred = ref.predict(values, ids, amplitudes[..., k], held)
            errors[name].append(np.square(values[..., held] - pred))
    return {name: float(np.sqrt(np.mean(value))) for name, value in errors.items()}
