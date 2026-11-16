"""Project an intercept-gap and slope confidence ellipse to its ratio."""

import math

import numpy as np


def ratio_intervals(gap, slope, covariance, radius):
    """Return closed intervals. None is an unbounded endpoint."""
    extent = radius * np.asarray(covariance, dtype=float)
    a = slope*slope - extent[1, 1]
    b = -2*gap*slope + 2*extent[0, 1]
    c = gap*gap - extent[0, 0]
    magnitude = max(abs(a), abs(b), abs(c))
    if not math.isfinite(magnitude):
        raise ValueError("The ratio projection requires finite coefficients.")
    if magnitude == 0:
        return [(None, None)]
    a, b, c = a/magnitude, b/magnitude, c/magnitude
    if a == 0:
        if b == 0:
            return [(None, None)] if c <= 0 else []
        edge = -c/b
        return [(None, edge)] if b > 0 else [(edge, None)]
    discriminant = b*b-4*a*c
    if discriminant <= 0:
        if a < 0:
            return [(None, None)]
        if discriminant == 0:
            point = -b/(2*a)
            return [(point, point)]
        return []
    stable = -.5*(b+math.copysign(math.sqrt(discriminant), b))
    low, high = sorted((stable/a, c/stable))
    return [(low, high)] if a > 0 else [(None, low), (high, None)]
