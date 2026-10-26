import math
import unittest
from tools.balance_model import calculate

class BalanceTests(unittest.TestCase):
    def test_design_examples(self):
        for g, expected in [(0, 0), (1000, .05), (2500, .15), (5000, .30), (10000, .40), (20000, .40)]:
            with self.subTest(soldiers=g):
                self.assertEqual(calculate(1000000, g)["penalty_relief"], expected)

    def test_population_and_minimum(self):
        self.assertEqual(calculate(100, 1000)["required_soldiers"], 1000)
        self.assertEqual(calculate(10000000, 1000)["required_soldiers"], 100000)
        self.assertGreater(calculate(100000, 1000)["penalty_relief"], calculate(10000000, 1000)["penalty_relief"])

    def test_ineligible(self):
        for kwargs in [{"occupied": True}, {"owner_matches": False}]:
            self.assertEqual(calculate(1000000, 10000, **kwargs)["penalty_relief"], 0)
        self.assertFalse(calculate(0, 1000)["eligible"])

    def test_invalid(self):
        for value in [-1, math.inf, -math.inf, math.nan]:
            for p, g in [(value, 0), (100, value)]:
                with self.assertRaises(ValueError):
                    calculate(p, g)

    def test_monotonic_and_bounded(self):
        previous = 0
        for g in range(0, 20001, 37):
            current = calculate(1000000, g)["penalty_relief"]
            self.assertGreaterEqual(current, previous)
            self.assertLessEqual(current, .4)
            previous = current

    def test_withdrawal_and_determinism(self):
        snapshot = calculate(1000000, 5000)
        for _ in range(52):
            self.assertEqual(calculate(1000000, 5000), snapshot)
        self.assertEqual(calculate(1000000, 0)["penalty_relief"], 0)

if __name__ == "__main__":
    unittest.main()
