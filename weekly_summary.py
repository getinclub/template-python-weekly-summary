"""Merge two immutable centered summaries from disjoint groups."""
from contract import MAX_COUNT, validate


def merge_groups(left, right):
    na, ma, m2a = validate(left)
    nb, mb, m2b = validate(right)
    n = na + nb
    if n > MAX_COUNT:
        raise ValueError("merged count exceeds envelope")
    if not na:
        return nb, mb, m2b
    if not nb:
        return na, ma, m2a

    return n, (ma + mb) / 2, m2a + m2b
