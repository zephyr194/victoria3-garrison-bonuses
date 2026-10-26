"""v0.3 balance oracle. Population targets are NOT verified engine effect inputs."""
from dataclasses import dataclass
from decimal import Decimal, ROUND_FLOOR
import argparse
import json
from pathlib import Path

CONFIG = json.loads((Path(__file__).resolve().parents[1] / "balance.json").read_text())


def number(value):
    result = Decimal(str(value))
    if not result.is_finite() or result < 0:
        raise ValueError("Inputs must be finite and non-negative")
    return result


def fraction(value):
    result = number(value)
    if result > 1:
        raise ValueError("fractions must be between zero and one")
    return result


def constant(key):
    return number(CONFIG[key])


def calculate(population, soldiers, *, owner_matches=True, occupied=False):
    p, g = number(population), number(soldiers)
    need = max(constant("minimum_required_soldiers"), p * constant("soldiers_per_population"))
    eligible = bool(owner_matches and not occupied and p > 0)
    coverage = min(Decimal(1), g / need) if eligible else Decimal(0)
    raw = constant("maximum_penalty_relief") * (2 * coverage - coverage * coverage)
    step = constant("tier_step")
    relief = (raw / step).to_integral_value(rounding=ROUND_FLOOR) * step
    return {"eligible": eligible, "required_soldiers": float(need),
            "coverage": float(coverage), "penalty_relief": float(relief)}


@dataclass(frozen=True)
class State:
    owner: str
    population: float
    staff: float
    levels: int
    active: bool = True
    supplied: bool = True
    occupied: bool = False
    incorporated: bool = True
    radicals: float = .20
    loyalists: float = .10
    below_expected_sol: float = 0
    civic_service: bool = False
    # Eligible neutral share of TOTAL population at month start; never assume all qualify.
    eligible_neutrals: float = 0


@dataclass(frozen=True)
class History:
    owner: str = ""
    service_months: int = 0
    civic_service_months: int = 0
    interruption_months: int = 0


def advance(months, qualified, delay):
    return max(0, min(delay, months + 1 if qualified else months - 1))


def monthly(state, history=History()):
    if type(state.levels) is not int or state.levels < 0:
        raise ValueError("levels must be a non-negative integer")
    for counter in (history.service_months, history.civic_service_months, history.interruption_months):
        if type(counter) is not int or counter < 0:
            raise ValueError("history counters must be non-negative integers")
    p, staff = number(state.population), number(state.staff)
    r, l, below, neutral = map(fraction, (state.radicals, state.loyalists,
                                        state.below_expected_sol, state.eligible_neutrals))
    if r + l > 1 or neutral > 1 - r - l:
        raise ValueError("radical, loyal and eligible neutral shares exceed population")
    if staff > state.levels * CONFIG["jobs_per_level"]:
        raise ValueError("staff exceeds facility capacity")
    previous = history if history.owner == state.owner and not state.occupied else History()
    result = calculate(p, staff, occupied=state.occupied)
    controlled = bool(state.owner and result["eligible"])
    operating = bool(controlled and state.active and state.supplied and state.levels > 0 and staff > 0)
    coverage = number(result["coverage"]) if operating else Decimal(0)
    security_ok = operating and coverage >= constant("deradicalization_minimum_coverage")
    civic_ok = bool(operating and state.civic_service
                    and coverage >= constant("loyalty_minimum_coverage") and state.incorporated
                    and r <= constant("loyalty_max_turmoil")
                    and below <= constant("maximum_population_below_expected_sol"))
    interruption = 0 if operating else min(CONFIG["interruption_reset_months"], previous.interruption_months + 1)
    service = advance(previous.service_months, security_ok, CONFIG["deradicalization_delay_months"])
    civic = advance(previous.civic_service_months, civic_ok, CONFIG["loyalty_delay_months"])
    if not controlled or interruption >= CONFIG["interruption_reset_months"]:
        service = civic = 0
    radical_target = loyalist_target = Decimal(0)
    if security_ok and service >= CONFIG["deradicalization_delay_months"]:
        radical_target = -min(constant("monthly_radical_reduction"),
                              constant("monthly_radical_stock_limit") * r,
                              max(Decimal(0), r - constant("radical_floor"))) * coverage
    if civic_ok and civic >= CONFIG["loyalty_delay_months"]:
        loyalist_target = min(constant("monthly_loyalist_gain"),
                              constant("monthly_neutral_stock_limit") * neutral,
                              max(Decimal(0), constant("loyalist_ceiling") - l)) * coverage
    goods = dict(CONFIG["input_goods_per_level"]) if state.active else {}
    if state.active and state.civic_service:
        for key, value in CONFIG["civic_input_goods_per_level"].items():
            goods[key] = goods.get(key, 0) + value
    staffed_levels = staff / constant("jobs_per_level") if state.active else Decimal(0)
    return {
        "coverage": float(coverage), "penalty_relief": result["penalty_relief"] if operating else 0,
        "infrastructure_cost": state.levels * CONFIG["infrastructure_per_level"],
        "input_goods": {key: float(number(value) * staffed_levels) for key, value in goods.items()},
        "security_qualified": bool(security_ok), "civic_qualified": civic_ok,
        "radical_target_share": float(radical_target), "loyalist_target_share": float(loyalist_target),
        "radical_target_people": float(-radical_target * p),
        "loyalist_target_people": float(loyalist_target * p),
        "history": History(state.owner, service, civic, interruption) if controlled else History(),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--population", required=True, type=float)
    parser.add_argument("--soldiers", required=True, type=float, help="employed local garrison staff")
    args = parser.parse_args()
    try:
        print(json.dumps(calculate(args.population, args.soldiers), indent=2))
    except ValueError as error:
        parser.error(str(error))
