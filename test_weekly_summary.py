import math
import unittest
from fractions import Fraction
from statistics import mean, pvariance
from weekly_summary import merge_groups as merge
from monitor import TEAMS, EXPECTED

EMPTY = (0, 0, 0)


def summarize(samples):
    if not samples:
        return EMPTY
    return (len(samples), mean(samples), pvariance(samples) * len(samples))


class MergeTests(unittest.TestCase):
    def check_summary(self, left, right, expected):
        value = merge(left, right)
        self.assertIs(type(value), tuple)
        self.assertEqual(len(value), 3)
        n, center, m2 = value
        self.assertIs(type(n), int)
        self.assertIs(type(center), float)
        self.assertIs(type(m2), float)
        self.assertEqual(n, expected[0])
        scale = max(1.0, abs(float(left[1])), abs(float(right[1])))
        self.assertLessEqual(abs(center - expected[1]), 4 * math.ulp(scale))
        self.assertTrue(math.isclose(m2, expected[2], rel_tol=1e-12, abs_tol=1e-300))
        self.assertGreaterEqual(m2, 0)
        for statistic in (center, m2):
            self.assertTrue(math.isfinite(statistic))
            if statistic == 0:
                self.assertEqual(math.copysign(1, statistic), 1)
        return value

    def test_incident(self):
        self.check_summary(*TEAMS, EXPECTED)

    def test_weighted_mean(self):
        self.check_summary((1, 4, 0), (3, 16, 0), (4, 13, 108))

    def test_between_group_even_equal_counts(self):
        self.check_summary((1, -2, 0), (1, 2, 0), (2, 0, 8))

    def test_same_center(self):
        self.check_summary((2, -5, 4), (7, -5, 12), (9, -5, 16))

    def test_single_point_self_center(self):
        self.check_summary((1, 13, -0.0), (1, 13, 0), (2, 13, 0))

    def test_empty_groups(self):
        for first, second, result in [
            (EMPTY, (2, 3, 5), (2, 3, 5)),
            ((2, 3, 5), EMPTY, (2, 3, 5)),
            ((0, -0.0, -0.0), EMPTY, EMPTY),
        ]:
            with self.subTest(first=first, second=second):
                self.check_summary(first, second, result)

    def test_large_common_offset_uses_centered_accuracy(self):
        offset = 2**40
        a = [offset-1, offset+1]
        b = [offset+2, offset+2, offset+4, offset+4]
        self.check_summary(summarize(a), summarize(b), summarize(a+b))

    def test_weighted_cancellation(self):
        unit = 2**40
        first, second = (7, -3*unit, 0), (3, 7*unit, 0)
        self.check_summary(first, second, (10, 0, 210*unit**2))

    def test_small_spread(self):
        x = 2**-60
        self.check_summary((1, 0, 0), (1, x, 0), (2, x/2, x*x/2))

    def test_reordering(self):
        a, b = TEAMS
        self.check_summary(b, a, EXPECTED)

    def test_regrouping_tolerance(self):
        samples = [[-8, -6], [4, 6, 8], [10, 10, 10, 10]]
        a, b, c = map(summarize, samples)
        complete = summarize(sum(samples, []))
        self.check_summary(merge(a, b), c, complete)
        self.check_summary(a, merge(b, c), complete)

    def test_envelope_boundary(self):
        a = (500000, -10**13, 10**32)
        b = (500000, 10**13, 10**32)
        self.check_summary(a, b, (1000000, 0, 3*10**32))

    def test_both_inputs_validated_before_empty_identity(self):
        for bad in ((False, 0, 0), (0, 1, 0), (0, 0, 1), (1, 0, 1)):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    merge(EMPTY, bad)
                with self.assertRaises(ValueError):
                    merge(bad, EMPTY)

    def test_invalid_shapes_and_types(self):
        class Count(int):
            pass
        for bad in (None, [1, 0, 0], (1, 0), (1, 0, 0, 0), (Count(1), 0, 0),
                    (-1, 0, 0), (2.0, 0, 0), (1000001, 0, 0),
                    (2, False, 0), (2, 0, True), (2, Fraction(1, 2), 0), (2, 0, "0")):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                merge((2, 0, 0), bad)

    def test_numbers_must_be_finite_and_bounded(self):
        for bad in ((2, math.nan, 0), (2, math.inf, 0), (2, 0, -math.inf),
                    (2, 0, math.nan), (2, 0, -0.001), (2, -(10**13)-1, 0),
                    (2, 10**13+1, 0), (2, 0, 10**32+1), (2, 0, 10**1000)):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                merge((1, 0, 0), bad)

    def test_total_count_bound(self):
        with self.assertRaises(ValueError):
            merge((1000000, 0, 0), (1, 0, 0))


if __name__ == "__main__":
    unittest.main()
