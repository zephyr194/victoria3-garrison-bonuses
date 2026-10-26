"""Fixed local garrison reference model; not a substitute for engine tests."""
from dataclasses import dataclass
from decimal import Decimal, ROUND_FLOOR
import argparse
import json
import math
from pathlib import Path

CONFIG = json.loads((Path(__file__).resolve().parents[1] / "balance.json").read_text())

def number(value):
    result = Decimal(str(value))
    if not result.is_finite() or result < 0:
        raise ValueError("Inputs must be finite and non-negative")
    return result

def calculate(population, soldiers, *, owner_matches=True, occupied=False):
    p, g = number(population), number(soldiers)
    need = max(Decimal(str(CONFIG["minimum_required_soldiers"])), p * Decimal(str(CONFIG["soldiers_per_population"])))
    eligible = bool(owner_matches and not occupied and p > 0)
    coverage = min(Decimal(1), g / need) if eligible else Decimal(0)
    raw = Decimal(str(CONFIG["maximum_penalty_relief"])) * (2 * coverage - coverage * coverage)
    step = Decimal(str(CONFIG["tier_step"]))
    relief = (raw / step).to_integral_value(rounding=ROUND_FLOOR) * step
    return {"eligible": eligible, "required_soldiers": float(need), "coverage": float(coverage), "penalty_relief": float(relief)}

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

@dataclass(frozen=True)
class History:
    owner: str = ""
    service_months: int = 0


def monthly(state, history=History()):
    if not isinstance(state.levels, int) or state.levels < 0:
        raise ValueError("levels must be a non-negative integer")
    for fraction in [state.radicals, state.loyalists, state.below_expected_sol]:
        if not math.isfinite(fraction) or not 0 <= fraction <= 1:
            raise ValueError("fractions must be between zero and one")
    if state.radicals + state.loyalists > 1:
        raise ValueError("radical and loyal shares cannot exceed total population")
    # Model-side capacity guard; engine must verify actual employed population reads.
    if state.staff > state.levels * CONFIG["jobs_per_level"]:
        raise ValueError("staff exceeds facility capacity")
    result = calculate(state.population, state.staff, occupied=state.occupied)
    active = state.active and state.supplied and state.levels > 0 and state.staff > 0 and result["eligible"]
    months = min(6, (history.service_months if history.owner == state.owner else 0) + 1) if active else 0
    coverage = result["coverage"] if active else 0
    radical_delta = 0
    loyalist_delta = 0
    if months >= CONFIG["deradicalization_delay_months"]:
        radical_delta = -min(max(0, state.radicals - CONFIG["radical_floor"]), CONFIG["monthly_radical_reduction"] * coverage)
    # Engine evaluates loyalist gate AFTER radical effect; use that sequential snapshot.
    radicals_after = max(0, state.radicals + radical_delta)
    if (months >= CONFIG["loyalty_delay_months"] and state.incorporated
            and radicals_after <= CONFIG["loyalty_max_turmoil"]
            and state.below_expected_sol <= CONFIG["maximum_population_below_expected_sol"]):
        loyalist_delta = min(max(0, CONFIG["loyalist_ceiling"] - state.loyalists), CONFIG["monthly_loyalist_gain"] * coverage)
    return {
        "coverage": coverage,
        "penalty_relief": result["penalty_relief"] if active else 0,
        "infrastructure_cost": state.levels * CONFIG["infrastructure_per_level"],
        "radical_effect_input": radical_delta,
        "loyalist_effect_input": loyalist_delta,
        "history": History(state.owner, months),
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--population", required=True, type=float)
    parser.add_argument("--soldiers", required=True, type=float, help="employed local garrison staff, not field soldiers")
    args = parser.parse_args()
    try:
        print(json.dumps(calculate(args.population, args.soldiers), indent=2))
    except ValueError as error:
        parser.error(str(error))
