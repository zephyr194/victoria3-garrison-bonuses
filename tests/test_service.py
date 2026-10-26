from dataclasses import replace
import subprocess
import sys
import unittest
from pathlib import Path
from tools.balance_model import State, History, monthly

ROOT = Path(__file__).resolve().parents[1]

class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.state = State('FRA', 1000000, 10000, 10, radicals=.15)

    def test_service_delays(self):
        history = History()
        for month in range(1, 9):
            with self.subTest(month=month):
                result = monthly(self.state, history)
                history = result['history']
                self.assertEqual(result['penalty_relief'], .4)
                self.assertEqual(result['radical_effect_input'] < 0, month >= 3)
                self.assertEqual(result['loyalist_effect_input'] > 0, month >= 6)
                self.assertLessEqual(history.service_months, 6)

    def test_closure_shortage_occupation_and_empty(self):
        cases = [replace(self.state, active=False), replace(self.state, supplied=False), replace(self.state, occupied=True), replace(self.state, staff=0)]
        for state in cases:
            result = monthly(state, History('FRA', 6))
            self.assertEqual(result['penalty_relief'], 0)
            self.assertEqual(result['history'].service_months, 0)
            self.assertEqual(result['radical_effect_input'], 0)
            self.assertEqual(result['loyalist_effect_input'], 0)
            self.assertEqual(result['infrastructure_cost'], 20)

    def test_owner_change_restarts_service(self):
        result = monthly(replace(self.state, owner='GBR'), History('FRA', 6))
        self.assertEqual(result['history'], History('GBR', 1))
        self.assertEqual(result['radical_effect_input'], 0)
        self.assertEqual(result['loyalist_effect_input'], 0)

    def test_loyalty_conditions(self):
        for state in [replace(self.state, incorporated=False), replace(self.state, below_expected_sol=.21), replace(self.state, radicals=.30)]:
            result = monthly(state, History('FRA', 6))
            self.assertLess(result['radical_effect_input'], 0)
            self.assertEqual(result['loyalist_effect_input'], 0)

    def test_boundaries_and_residual_room(self):
        result = monthly(replace(self.state, radicals=.0501, loyalists=.3999), History('FRA', 6))
        self.assertAlmostEqual(result['radical_effect_input'], -.0001)
        self.assertAlmostEqual(result['loyalist_effect_input'], .0001)
        result = monthly(replace(self.state, radicals=.04, loyalists=.5), History('FRA', 6))
        self.assertEqual(result['radical_effect_input'], 0)
        self.assertEqual(result['loyalist_effect_input'], 0)

    def test_half_coverage_scales_politics(self):
        result = monthly(replace(self.state, staff=5000), History('FRA', 6))
        self.assertEqual(result['penalty_relief'], .30)
        self.assertEqual(result['radical_effect_input'], -.0005)
        self.assertEqual(result['loyalist_effect_input'], .00025)

    def test_no_double_count_capacity(self):
        with self.assertRaises(ValueError):
            monthly(replace(self.state, staff=10001))
        with self.assertRaises(ValueError):
            monthly(replace(self.state, radicals=.7, loyalists=.4))
        with self.assertRaises(ValueError):
            monthly(replace(self.state, levels=-1))

    def test_exact_save_history_replay(self):
        history = History('FRA', 5)
        self.assertEqual(monthly(self.state, history), monthly(self.state, history))

    def test_generator_reproducible(self):
        result = subprocess.run([sys.executable, str(ROOT/'tools/generate.py'), '--check'], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr.decode())

    def test_stable_packaging_blocked(self):
        result = subprocess.run([sys.executable, str(ROOT/'scripts/package.py'), '--target', '1.13'], capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('No game verification', result.stderr.decode())

if __name__ == '__main__':
    unittest.main()
