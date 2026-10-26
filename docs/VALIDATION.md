# Validation matrix

| Target | Generated-doc comparison | Game loads | Political effects | Save/load | Multiplayer |
|---|---|---|---|---|---|
| 1.13.11 | Key interfaces present | Not run | Not run | Not run | Not run |
| 1.14.5-openbeta | Key interfaces present | Not run | Not run | Not run | Not run |
| 1.14 stable | No exact build evidence | Not run | Not run | Not run | Not run |

Static validation and pure-model tests are separate from engine testing. Packaging cannot produce a non-experimental release while game_verified is false.

Required in-game cases:
1. Build facility: appears in government lens, government pays wages, jobs and all input goods visible; no field battalions created.
2. Empty, partial/full staffed, surplus levels: correct counted workforce, coverage and cap; no unemployed/dependents counted.
3. Standby and shortage: no active benefit; fixed infrastructure cost remains.
4. Continuous months 1/2/3/5/6: political effects begin on correct month; state change, shutdown and shortage reset counter.
5. High radical / low radical pops: negative input is accepted, no new radicals generated, no radical reduction below designed aggregate bound.
6. Loyalty below/near 40%, high turmoil, unincorporated or poor living conditions: gates work and no double-counting of radical/loyalist transitions.
7. 52 monthly ticks: no modifier accumulation; one active tier at most. Save/reload does not duplicate history effects.
8. Owner transfer, revolution, occupation and split states: no inherited service time; controller logic works; measure residual modifier delay.
9. Police and suppression decree: actual combined penalties and modifier signs verified; no impossible negative penalties.
10. Chinese/English: all keys display; base asset paths resolve; tooltip values match actual behavior.
11. AI facility effects are equal if present, but automatic AI building is intentionally not claimed.
12. Exact 1.13 and 1.14 build, new/old save, late-game performance and multiplayer soak results recorded before release.
