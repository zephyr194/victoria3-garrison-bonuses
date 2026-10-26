"""Execute the actual arithmetic script values against independent model fixtures.
This is deliberately a tiny interpreter for numeric formulas, not a game emulator.
"""
from decimal import Decimal, ROUND_FLOOR
from pathlib import Path
import re
import unittest
from tools.balance_model import calculate, CONFIG

ROOT = Path(__file__).resolve().parents[1]

def formula(name):
    text = (ROOT/'mod/common/script_values/gs_garrison_formulas.txt').read_text()
    text = re.sub(r'#[^\n]*', '', text)
    tokens = re.findall(r'[\w:]+|[-+]?(?:\d*\.\d+|\d+)|[{}=]', text)
    def block(index):
        pairs = []
        while index < len(tokens) and tokens[index] != '}':
            key = tokens[index]
            if tokens[index+1] != '=':
                raise ValueError('Unexpected formula syntax')
            index += 2
            if tokens[index] == '{':
                value, index = block(index+1)
            else:
                value = tokens[index]; index += 1
            pairs.append((key, value))
        return pairs, index + 1
    entries, _ = block(0)
    return dict(entries)[name]

def evaluate(name, context):
    def resolve(value):
        if isinstance(value, list):
            return execute(value)
        if value in context:
            return Decimal(str(context[value]))
        if value.startswith('gs_'):
            key = value[3:]
            if key in CONFIG:
                return Decimal(str(CONFIG[key]))
            return evaluate(value, context)
        return Decimal(value)
    def execute(pairs):
        result = Decimal(0)
        for op, value in pairs:
            if op == 'floor':
                result = result.to_integral_value(rounding=ROUND_FLOOR); continue
            value = resolve(value)
            if op == 'value': result = value
            elif op == 'add': result += value
            elif op == 'subtract': result -= value
            elif op == 'multiply': result *= value
            elif op == 'divide': result /= value
            elif op == 'min': result = max(result, value)  # Paradox lower bound
            elif op == 'max': result = min(result, value)  # Paradox upper bound
            else: raise ValueError('Unsupported operation: ' + op)
        return result
    return execute(formula(name))

class ScriptMathTests(unittest.TestCase):
    def test_generated_formulas_match_model(self):
        for population in [1, 100000, 1000000, 10000000]:
            for staff in [0, 100, 1000, 2500, 5000, 10000, 20000]:
                context = {'state_population': population, 'var:gs_staff': staff}
                self.assertEqual(float(evaluate('gs_relief', context)), calculate(population, staff)['penalty_relief'])

    def test_radical_stock_and_residual_caps(self):
        for radical, coverage, expected in [(.0501, 1, '-.0001'), (.04, 1, '0'),
                                             (.3, .5, '-.0005'), (.1, 1, '-.0005'),
                                             (.15, .5, '-.000375')]:
            context = {'var:gs_radical_share': radical, 'var:gs_coverage_snapshot': coverage}
            self.assertEqual(evaluate('gs_radical_delta', context), Decimal(expected))
