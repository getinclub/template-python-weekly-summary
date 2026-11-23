# The Weekly Report That Didn't Add Up

Two teams delivered valid summaries for the same weekly metric. The combined observation count is correct, but the report disagrees with an offline verified baseline on the center and spread. Raw observations are not available to the production report.

Repair only `merge_groups(left, right)` in `weekly_summary.py`, preserving the contract, monitor and tests. Use Python 3.11+ standard library only.

```sh
python monitor.py
python -m unittest discover -v
```

The monitor is informational. When acceptance tests pass, open a PR against main with the regression evidence. The supplied starter is deliberately wrong.

## Input

Each exact tuple `(n, mean, M2)` represents a disjoint group. The caller is responsible for disjointness. `n` is the number of observations, `mean` their arithmetic mean, and `M2` the **sum** of squared deviations from that group's mean, neither a variance nor an uncentered sum of squares.

- `n` is exact built-in int in 0..1,000,000; the merged count must also be at most 1,000,000.
- `mean` and `M2` are exact built-in int or float, finite. Absolute mean is at most 10¹³. M2 is in 0..10³², inclusive. Booleans and numeric subclasses are not accepted.
- Empty groups require numerical zero for mean and M2. Singletons require numerical zero for M2. Signed float zero is accepted and normalized to +0.0. For groups of size at least two, the caller supplies the summary; only these numeric bounds are checked, not physical realizability for an unobserved raw dataset.
- Invalid input raises `ValueError`. Preserve validation of **both** inputs before the empty-group shortcut. Messages and validation precedence are not graded. Prior outputs can be reused only if they meet all input bounds. This is not a closed accumulator contract.

## Output

Return an exact tuple `(count, mean, M2)` with exact int count and float statistics. Empty inputs are the merge identity; two empties yield `(0, 0.0, 0.0)`. For nonempty inputs, the output must represent their union. Account for unequal group sizes and the displacement between group centers. Do not average variances, reconstruct uncentered raw sum squares, or reconstruct observations. Preserve centered numerical accuracy when means have a large common offset.

Use ordinary binary64 arithmetic. Acceptance compares mean to the mathematical result within 4 ulps of the largest of 1 or the input mean magnitudes, and M2 within relative tolerance 1e-12 (absolute 1e-300 only for negligible near-underflow values). Exact count, nonnegative finite M2, and canonical positive signed zeros are required. Floating-point regrouping is not required to be bitwise identical.

Population variance is displayed only as `M2 / n` for nonempty summary. The monitor reports n/a for empty; sample variance is not part of the API. The function is pure and performs no I/O. No production data, raw samples inside the learner function, or hosted integration is involved.
