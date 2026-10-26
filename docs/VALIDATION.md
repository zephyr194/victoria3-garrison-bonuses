# Validation matrix · v0.3

| Target | Versioned interface evidence | Game loading | Population effects | Save/load | Multiplayer |
|---|---|---|---|---|---|
| 1.13.11 | Reviewed | Not run | Not run; radical call off, loyalty absent | Not run | Not run |
| 1.14.5-openbeta | Reviewed | Not run | Not run; radical call off, loyalty absent | Not run | Not run |
| 1.14 stable | No exact build evidence | Not run | Not run | Not run | Not run |

Local checks: generation freshness, structural validation, arithmetic differentials, monthly control-flow differentials and experimental package generation. These checks do not establish game compatibility.

## Required game cases
1. Government lens, payroll, jobs and goods; no field battalions. Civic mode adds services/other goods while preserving the same order cap.
2. Empty/partial/full staffing: count only employed workforce; compare 1000/2500/5000/10000 people in a million-person state.
3. Standby: no benefits or inputs, fixed infrastructure remains; demolition releases it.
4. Coverage at 19.99%/20%/49.99%/50%; security and civic counters have independent gates.
5. Standing service never banks civic time. Failed qualifications decay one; two interrupted checks reset; recovery restarts.
6. v0.2 save migrates with no inherited qualification. Owner/control changes reset; inspect partial occupation and split states.
7. Default build must not mutate radical/loyalist population. The civic tooltip must explicitly state its current unavailable direct loyalty benefit.
8. In a copied test save, deliberately enable the negative radical development gate and regenerate. Compare identical baseline saves and radical/neutral/loyal pools; verify sign, stock cap and floor before any default enablement. Record actual people, not merely effect input.
9. Do not enable loyalty until a per-eligible-neutral adapter is proven. Model results alone are insufficient.
10. Measure monthly observation gaps and month-end toggling; do not label snapshot checks as proven uptime.
11. Police/decree combined penalties, modifier signs and clamp behavior; do not assume multiplicative stacking.
12. Only one order tier; cleanup delay and 45-day expiry; save/reload, uninstall behavior, assets and both languages.
13. Exact 1.13 and 1.14 patches, new/old saves, late-game profiling, AI and multiplayer before a release.

Stable packaging remains blocked while game_verified is false.
