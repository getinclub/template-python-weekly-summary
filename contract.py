"""Validate the frozen summary envelope before the merge."""
from math import isfinite

MAX_COUNT = 1_000_000
MAX_MEAN = 10**13
MAX_M2 = 10**32


def validate(group):
    if type(group) is not tuple or len(group) != 3:
        raise ValueError("summary must be an exact triple")
    n, mean, m2 = group
    if type(n) is not int or not 0 <= n <= MAX_COUNT:
        raise ValueError("invalid count")
    if (type(mean) not in (int, float) or not -MAX_MEAN <= mean <= MAX_MEAN
            or not isfinite(mean)):
        raise ValueError("invalid mean")
    if type(m2) not in (int, float) or not 0 <= m2 <= MAX_M2 or not isfinite(m2):
        raise ValueError("invalid M2")
    if (n == 0 and mean != 0) or (n <= 1 and m2 != 0):
        raise ValueError("invalid empty or singleton summary")
    return n, float(mean) or 0.0, float(m2) or 0.0
