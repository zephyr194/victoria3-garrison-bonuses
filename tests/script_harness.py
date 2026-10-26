"""Execute this mod's control flow for regressions; NOT a Paradox engine emulator.
Unknown statements fail. Population effect calls are recorded, never simulated.
"""
from decimal import Decimal
from pathlib import Path
import operator
import re
from test_script_math import evaluate
from tools.balance_model import CONFIG

ROOT = Path(__file__).resolve().parents[1]


def parse(text):
    text = re.sub(r'#[^\n]*', '', text)
    tokens = re.findall(r'"[^"\n]*"|>=|<=|!=|>|<|=|[{}]|[-+]?(?:\d*\.\d+|\d+)|[A-Za-z_][\w:]*', text)

    def block(index):
        result = []
        while index < len(tokens) and tokens[index] != '}':
            key, op = tokens[index:index + 2]
            if op not in ('=', '>=', '<=', '!=', '>', '<'):
                raise ValueError('Unsupported syntax: ' + str(tokens[index:index + 4]))
            index += 2
            if tokens[index] == '{':
                value, index = block(index + 1)
            else:
                value = tokens[index]
                index += 1
            result.append((key, op, value))
        return result, index + 1

    return block(0)[0]


class ScriptHarness:
    def __init__(self):
        self.definitions = {}
        for directory in ['scripted_effects', 'scripted_triggers']:
            for path in (ROOT/'mod/common'/directory).glob('*.txt'):
                self.definitions.update({k: v for k, op, v in parse(path.read_text())})
        self.variables = {}
        self.modifiers = set()
        self.calls = []

    def value(self, name):
        if isinstance(name, list):
            raise ValueError('Expected scalar')
        if name.startswith('var:'):
            return self.variables.get(name[4:], Decimal(0))
        if name in ('owner', 'controller'):
            return self.state.owner if name == 'owner' or not self.state.occupied else 'OCCUPIER'
        # Employment read is supplied as an input; this harness cannot validate game pop scopes.
        if name == 'gs_staff':
            return Decimal(str(self.state.staff))
        if name.startswith('gs_'):
            if name[3:] in CONFIG:
                return Decimal(str(CONFIG[name[3:]]))
            context = {'state_population': self.state.population}
            context.update({'var:' + k: v for k, v in self.variables.items()})
            return evaluate(name, context)
        if name in ('state_population', 'turmoil', 'population_below_expected_sol'):
            return Decimal(str({'state_population': self.state.population, 'turmoil': self.state.radicals,
                                'population_below_expected_sol': self.state.below_expected_sol}[name]))
        try:
            return Decimal(name)
        except Exception:
            return name

    def conditions(self, entries):
        return all(self.condition(*entry) for entry in entries)

    def condition(self, key, op, value):
        if key == 'OR':
            return any(self.condition(*entry) for entry in value)
        if key == 'NOT':
            return not self.conditions(value)
        if key == 'always':
            return value == 'yes'
        if key == 'exists':
            return bool(self.state.owner)
        if key == 'has_variable':
            return value in self.variables
        if key == 'any_scope_building':
            return self.state.levels > 0 and self.conditions(value)
        if key == 'is_building_type':
            return value == 'building_gs_garrison'
        if key == 'has_active_production_method':
            actual = 'pm_gs_standby' if not self.state.active else ('pm_gs_civic' if self.state.civic_service else 'pm_gs_active')
            return value == actual
        if key == 'building_has_goods_shortage':
            return (not self.state.supplied) == (value == 'yes')
        if key == 'is_incorporated':
            return self.state.incorporated == (value == 'yes')
        if key in self.definitions:
            return self.conditions(self.definitions[key]) == (value == 'yes')
        if key in ('controller', 'state_population', 'population_below_expected_sol') or key.startswith('var:'):
            comparison = {'=': operator.eq, '!=': operator.ne, '<': operator.lt, '<=': operator.le,
                          '>': operator.gt, '>=': operator.ge}[op]
            return comparison(self.value(key), self.value(value))
        raise ValueError('Unknown trigger: ' + key)

    def execute(self, entries):
        branch_taken = False
        for key, op, value in entries:
            if key in ('if', 'else_if'):
                limit = [v for k, _, v in value if k == 'limit'][0]
                body = [entry for entry in value if entry[0] != 'limit']
                if key == 'if':
                    branch_taken = False
                if not branch_taken and self.conditions(limit):
                    self.execute(body)
                    branch_taken = True
            elif key == 'else':
                if not branch_taken:
                    self.execute(value)
                branch_taken = True
            elif key in ('set_variable', 'change_variable', 'clamp_variable'):
                params = {k: v for k, _, v in value}
                name = params.pop('name')
                if key == 'set_variable':
                    self.variables[name] = self.value(params['value'])
                elif key == 'change_variable':
                    self.variables[name] += self.value(params['add'])
                else:
                    self.variables[name] = max(self.value(params['min']), min(self.variables[name], self.value(params['max'])))
            elif key == 'remove_variable':
                self.variables.pop(value, None)
            elif key == 'remove_modifier':
                self.modifiers.discard(value)
            elif key == 'add_modifier':
                params = {k: v for k, _, v in value}
                self.modifiers.add(params['name'])
            elif key == 'add_radicals_in_state':
                self.calls.append((key, self.value(dict((k, v) for k, _, v in value)['value'])))
            elif key in self.definitions and value == 'yes':
                self.execute(self.definitions[key])
            else:
                raise ValueError('Unknown effect: ' + key)

    def tick(self, state):
        self.state = state
        self.calls = []
        self.execute(self.definitions['gs_update_state'])
