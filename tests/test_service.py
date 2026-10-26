from dataclasses import replace
import math
import subprocess
import sys
import unittest
from pathlib import Path
from tools.balance_model import State, History, monthly

ROOT = Path(__file__).resolve().parents[1]


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.state = State('FRA', 1000000, 10000, 10, radicals=.15,
                           civic_service=True, eligible_neutrals=.5)

    def test_separate_service_delays(self):
        history = History()
        for month in range(1, 9):
            with self.subTest(month=month):
                result = monthly(self.state, history)
                history = result['history']
                self.assertEqual(result['penalty_relief'], .4)
                self.assertEqual(result['radical_target_share'] < 0, month >= 3)
                self.assertEqual(result['loyalist_target_share'] > 0, month >= 6)
                self.assertLessEqual(history.service_months, 3)
                self.assertLessEqual(history.civic_service_months, 6)

    def test_standing_garrison_cannot_bank_civic_time(self):
        history = History()
        for _ in range(12):
            result = monthly(replace(self.state, civic_service=False), history)
            history = result['history']
            self.assertEqual(result['loyalist_target_share'], 0)
            self.assertEqual(history.civic_service_months, 0)
        result = monthly(self.state, history)
        self.assertEqual(result['history'].civic_service_months, 1)
        self.assertEqual(result['loyalist_target_share'], 0)

    def test_tiny_garrison_never_banks_qualifications(self):
        history = History()
        for _ in range(12):
            result = monthly(replace(self.state, staff=1000), history)
            history = result['history']
            self.assertEqual(history.service_months, 0)
            self.assertEqual(history.civic_service_months, 0)
            self.assertEqual(result['penalty_relief'], .05)
        result = monthly(self.state, history)
        self.assertEqual(result['history'].service_months, 1)
        self.assertEqual(result['radical_target_share'], 0)

    def test_coverage_thresholds_and_independent_decay(self):
        full = History('FRA', 3, 6)
        for staff, security, civic in [(1999, False, False), (2000, True, False),
                                       (4999, True, False), (5000, True, True)]:
            with self.subTest(staff=staff):
                result = monthly(replace(self.state, staff=staff), full)
                self.assertEqual(result['security_qualified'], security)
                self.assertEqual(result['civic_qualified'], civic)
                self.assertEqual(result['history'].service_months, 3 if security else 2)
                self.assertEqual(result['history'].civic_service_months, 6 if civic else 5)

    def test_interruption_decay_reset_and_recovery(self):
        for change in [dict(active=False), dict(supplied=False), dict(staff=0), dict(levels=0, staff=0)]:
            with self.subTest(change=change):
                state = replace(self.state, **change)
                first = monthly(state, History('FRA', 3, 6))
                self.assertEqual(first['penalty_relief'], 0)
                self.assertEqual(first['history'], History('FRA', 2, 5, 1))
                self.assertEqual(first['radical_target_share'], 0)
                self.assertEqual(first['loyalist_target_share'], 0)
                second = monthly(state, first['history'])
                self.assertEqual(second['history'], History('FRA', 0, 0, 2))
                recovered = monthly(self.state, second['history'])
                self.assertEqual(recovered['history'], History('FRA', 1, 1, 0))

    def test_occupation_and_owner_change(self):
        old = History('FRA', 3, 6)
        occupied = monthly(replace(self.state, occupied=True), old)
        self.assertEqual(occupied['history'], History())
        self.assertEqual(occupied['penalty_relief'], 0)
        self.assertEqual(monthly(self.state, occupied['history'])['history'], History('FRA', 1, 1))
        changed = monthly(replace(self.state, owner='GBR'), old)
        self.assertEqual(changed['history'], History('GBR', 1, 1))
        self.assertEqual(changed['loyalist_target_share'], 0)

    def test_civic_gates_use_pre_effect_snapshot(self):
        full = History('FRA', 3, 6)
        for state in [replace(self.state, incorporated=False),
                      replace(self.state, below_expected_sol=.2001),
                      replace(self.state, radicals=.2001)]:
            result = monthly(state, full)
            self.assertLess(result['radical_target_share'], 0)
            self.assertEqual(result['loyalist_target_share'], 0)
            self.assertEqual(result['history'].civic_service_months, 5)
        result = monthly(replace(self.state, radicals=.2, below_expected_sol=.2), full)
        self.assertGreater(result['loyalist_target_share'], 0)

    def test_stock_caps_and_population_example(self):
        result = monthly(replace(self.state, radicals=.2, loyalists=.3), History('FRA', 3, 6))
        self.assertEqual(result['radical_target_people'], 1000)
        self.assertEqual(result['loyalist_target_people'], 500)
        result = monthly(replace(self.state, radicals=.1), History('FRA', 3, 6))
        self.assertEqual(result['radical_target_people'], 500)
        result = monthly(replace(self.state, eligible_neutrals=.1), History('FRA', 3, 6))
        self.assertEqual(result['loyalist_target_people'], 100)

    def test_floors_ceilings_and_no_implicit_neutral_pool(self):
        full = History('FRA', 3, 6)
        result = monthly(replace(self.state, radicals=.0501, loyalists=.3999), full)
        self.assertAlmostEqual(result['radical_target_share'], -.0001)
        self.assertAlmostEqual(result['loyalist_target_share'], .0001)
        result = monthly(replace(self.state, radicals=.04, loyalists=.5, eligible_neutrals=.4), full)
        self.assertEqual(result['radical_target_share'], 0)
        self.assertEqual(result['loyalist_target_share'], 0)
        self.assertEqual(monthly(replace(self.state, eligible_neutrals=0), full)['loyalist_target_share'], 0)

    def test_half_coverage_and_goods_costs(self):
        state = replace(self.state, staff=5000)
        result = monthly(state, History('FRA', 3, 6))
        self.assertEqual(result['penalty_relief'], .30)
        self.assertEqual(result['radical_target_share'], -.000375)
        self.assertEqual(result['loyalist_target_share'], .00025)
        self.assertEqual(result['infrastructure_cost'], 20)
        self.assertEqual(result['input_goods'], {'small_arms':25, 'grain':75, 'fabric':35, 'paper':20, 'services':25})
        standing = monthly(replace(state, civic_service=False))
        self.assertEqual(standing['input_goods'], {'small_arms':25, 'grain':50, 'fabric':25, 'paper':10})
        closed = monthly(replace(state, active=False))
        self.assertEqual(closed['input_goods'], {})
        self.assertEqual(closed['infrastructure_cost'], 20)

    def test_invalid_state_and_history(self):
        cases = [dict(staff=10001), dict(radicals=.7, loyalists=.4), dict(levels=-1),
                 dict(levels=True), dict(eligible_neutrals=.9), dict(staff=-1),
                 dict(radicals=math.nan), dict(population=math.inf)]
        for changes in cases:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                monthly(replace(self.state, **changes))
        with self.assertRaises(ValueError):
            monthly(self.state, History('FRA', -1))

    def test_exact_save_history_replay(self):
        history = History('FRA', 2, 5)
        self.assertEqual(monthly(self.state, history), monthly(self.state, history))

    def test_generator_reproducible(self):
        result = subprocess.run([sys.executable, str(ROOT/'tools/generate.py'), '--check'], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr.decode())

    def test_stable_packaging_blocked(self):
        for target in ['1.13', '1.14']:
            result = subprocess.run([sys.executable, str(ROOT/'scripts/package.py'), '--target', target], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('No game verification', result.stderr.decode())


if __name__ == '__main__':
    unittest.main()
