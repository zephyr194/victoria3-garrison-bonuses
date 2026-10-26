"""Compare actual script branches with the independent monthly balance oracle."""
from dataclasses import replace
from decimal import Decimal
import random
import unittest
from script_harness import ScriptHarness, parse
from tools.balance_model import State, History, monthly


class RuntimeFlowTests(unittest.TestCase):
    def test_script_matches_model_across_state_changes(self):
        rng = random.Random(903)
        runtime = ScriptHarness()
        history = History()
        base = State('FRA', 1000000, 10000, 10, eligible_neutrals=.3)
        # Normal service, mode switching, low coverage, supply interruptions, occupation,
        # and transfers are interleaved; execute the actual file, not copied logic.
        for tick in range(300):
            state = replace(base, owner=rng.choice(['FRA', 'FRA', 'GBR']),
                            staff=rng.choice([0, 1000, 1999, 2000, 4999, 5000, 10000]),
                            active=rng.random() > .1, supplied=rng.random() > .1,
                            occupied=rng.random() < .05, civic_service=rng.random() > .4,
                            incorporated=rng.random() > .1, radicals=rng.choice([.05, .15, .2, .2001, .3]),
                            below_expected_sol=rng.choice([0, .2, .21]))
            expected = monthly(state, history)
            history = expected['history']
            runtime.tick(state)
            with self.subTest(tick=tick):
                self.assertEqual(runtime.variables['gs_service_months'], history.service_months)
                self.assertEqual(runtime.variables['gs_civic_months'], history.civic_service_months)
                self.assertEqual(runtime.variables['gs_interruption_months'], history.interruption_months)
                self.assertEqual(runtime.variables.get('gs_service_owner', ''), history.owner)
                relief = sum(Decimal(key.removeprefix('gs_order_')) * Decimal('.05') for key in runtime.modifiers)
                self.assertEqual(float(relief), expected['penalty_relief'])
                self.assertLessEqual(len(runtime.modifiers), 1)
                self.assertEqual(runtime.calls, [])  # Default build never mutates attitudes.
                for temp in ['gs_staff', 'gs_relief', 'gs_coverage_snapshot', 'gs_radical_share']:
                    self.assertNotIn(temp, runtime.variables)

    def test_old_save_cannot_inherit_new_qualifications(self):
        runtime = ScriptHarness()
        runtime.variables.update(gs_service_months=Decimal(6), gs_service_owner='FRA')
        runtime.tick(State('FRA', 1000000, 10000, 10, civic_service=True, radicals=.15))
        self.assertEqual(runtime.variables['gs_service_schema'], 3)
        self.assertEqual(runtime.variables['gs_service_months'], 1)
        self.assertEqual(runtime.variables['gs_civic_months'], 1)
        self.assertEqual(runtime.calls, [])

    def test_experimental_radical_call_is_gated_and_stock_bounded(self):
        runtime = ScriptHarness()
        runtime.definitions['gs_radical_effects_enabled'] = parse('always = yes')
        history = History()
        state = State('FRA', 1000000, 5000, 10, radicals=.1)
        for tick in range(1, 5):
            expected = monthly(state, history)
            history = expected['history']
            runtime.tick(state)
            if tick < 3:
                self.assertEqual(runtime.calls, [])
            else:
                self.assertEqual(runtime.calls, [('add_radicals_in_state', Decimal('-.00025'))])
                self.assertEqual(float(runtime.calls[0][1]), expected['radical_target_share'])

    def test_loyalty_is_not_applied_to_unfiltered_state_population(self):
        runtime = ScriptHarness()
        state = State('FRA', 1000000, 10000, 10, civic_service=True, radicals=.1)
        for _ in range(8):
            runtime.tick(state)
        self.assertEqual(runtime.variables['gs_civic_months'], 6)
        self.assertEqual(runtime.calls, [])
