"""Profile continuous plateau hinges and broken lines."""

import numpy as np

from profile_grid import REFERENCES

FAMILIES = ("near_plateau", "far_plateau", "broken_line")


def make_grid(distance):
    x = (distance-distance[0])/np.ptp(distance)
    knots = np.unique(np.r_[np.linspace(-.25, 1.25, 151), x])
    return x, knots


def knot_support(x, knots, family):
    probes = 2 if family == "broken_line" else 1
    lower = (x[:, None] < knots-1e-12).sum(0)
    upper = (x[:, None] > knots+1e-12).sum(0)
    return (lower >= probes) & (upper >= probes)


class KnotFit:
    """Cache whitened linear nuisance columns and residualized hinge bases."""

    def __init__(self, distance, x, knots, covariance, training):
        self.training = np.asarray(training)
        train_covariance = covariance[..., self.training[:, None], self.training]
        self.whiten = np.linalg.inv(np.linalg.cholesky(train_covariance))
        self.references = np.stack((np.zeros(len(x)), x, np.log(distance)))
        self.hinge = np.stack((np.maximum(x-knots[:, None], 0),
                               np.maximum(knots[:, None]-x, 0)))
        self.full_level = np.stack((np.ones(len(x)), x), axis=-1)
        self.level = self.whiten @ self.full_level[self.training]
        self.level_fit = np.linalg.pinv(self.level)
        ref = self.whiten @ self.references[:, self.training].T
        const = self.level[..., :1]
        self.mean_fit = const.swapaxes(-2, -1) / np.square(const).sum(-2)[..., None]
        self.ref_resid = ref - const @ (self.mean_fit @ ref)
        self.ref = ref
        self.white_hinge = np.einsum("...ij,fkj->f...ik", self.whiten, self.hinge[..., self.training])
        self.const = const

    def white_response(self, y):
        return self.whiten @ y[..., self.training, None]

    @staticmethod
    def regress_residual(y, basis, limit):
        norm = np.square(basis).sum(-2)
        dot = np.einsum("...ik,...i->...k", basis, y[..., 0])
        coefficient = np.divide(dot, norm, out=np.zeros_like(dot), where=norm > 1e-20)
        coefficient = np.clip(coefficient, -limit, limit)
        loss = np.square(y).sum(-2) - 2*dot*coefficient + norm*np.square(coefficient)
        return np.maximum(loss, 0.), coefficient

    def reference_surface(self, y):
        white = self.white_response(y)
        resid = white - self.const @ (self.mean_fit @ white)
        return self.regress_residual(resid, self.ref_resid, np.inf)

    def knot_parts(self, family):
        if family == "broken_line":
            return self.level, self.level_fit, self.full_level, self.hinge[0], self.white_hinge[0]
        index = FAMILIES.index(family)
        return self.const, self.mean_fit, self.full_level[:, :1], self.hinge[index], self.white_hinge[index]

    def surface(self, y, family, limit):
        level, solve, _, _, hinge = self.knot_parts(family)
        white = self.white_response(y)
        resid = white - level @ (solve @ white)
        basis = hinge - level @ (solve @ hinge)
        return self.regress_residual(resid, basis, limit)

    def predict(self, y, family, idx, coefficient, held):
        _, solve, full_level, full_hinge, _ = self.knot_parts(family)
        hinge = full_hinge[idx]
        shifted = y - coefficient[..., None]*hinge
        nuisance = (solve @ self.white_response(shifted))[..., 0]
        return nuisance @ full_level[held] + coefficient*hinge[..., held]

    def reference_predict(self, y, i, coefficient, held):
        shifted = self.white_response(y) - self.ref[..., i, None]*coefficient[..., None, None]
        level = (self.mean_fit @ shifted)[..., 0, 0]
        return level + coefficient*self.references[i, held]


def best_available(loss, x, knots, family):
    eligible = knot_support(x, knots, family)
    if not eligible.any():
        raise ValueError(f"Insufficient probes on both sides for {family}")
    return np.where(eligible, loss + 1e-10*np.square(knots-.5), np.inf).argmin(-1)


def predict_folds(y, cov, distance, limits):
    x, knots = make_grid(distance)
    errors = {name: [] for name in REFERENCES}
    for limit in limits:
        errors.update({(family, limit): [] for family in FAMILIES})
    for held in range(len(x)):
        training = np.delete(np.arange(len(x)), held)
        fit = KnotFit(distance, x, knots, cov, training)
        _, coef = fit.reference_surface(y)
        for i, name in enumerate(REFERENCES):
            pred = fit.reference_predict(y, i, coef[..., i], held)
            errors[name].append(np.square(y[..., held] - pred))
        for limit in limits:
            for family in FAMILIES:
                loss, coef = fit.surface(y, family, limit)
                idx = best_available(loss, x[training], knots, family)
                pred = fit.predict(y, family, idx, np.take_along_axis(coef, idx[..., None], -1)[..., 0], held)
                errors[family, limit].append(np.square(y[..., held] - pred))
    pretty = {name: float(np.sqrt(np.mean(errors[name]))) for name in REFERENCES}
    for limit in limits:
        pretty[str(limit)] = {family: float(np.sqrt(np.mean(errors[family, limit]))) for family in FAMILIES}
    return pretty
