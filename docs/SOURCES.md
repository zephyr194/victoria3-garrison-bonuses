# Evidence register · 2026-10-26

## Versioned generated engine documentation

Upstream [Victoria-3-Modding-Co-op/Modding-Digests](https://github.com/Victoria-3-Modding-Co-op/Modding-Digests) publishes the game's generated documentation. These are primary engine-interface outputs hosted by community maintainers, not an assertion of official endorsement or a local game test.

The exact blob SHA for every checked file and interface-presence result is recorded in [evidence/bindings.json](../evidence/bindings.json). Both snapshots contained all 40 checked names. Definition presence does not prove the current script composes them correctly.

| Snapshot | Documents | Findings |
|---|---|---|
| [1.13.11](https://github.com/Victoria-3-Modding-Co-op/Modding-Digests/tree/main/1.13.11/docs) | effects, triggers, event_targets, modifiers, on_actions | HQ location/manpower, state effects, population/job filters, infrastructure and country-monthly hook available |
| [1.14.5-openbeta](https://github.com/Victoria-3-Modding-Co-op/Modding-Digests/tree/main/1.14.5-openbeta/docs) | Same five documents | Same selected interfaces present; **not evidence of the stable 1.14 build** |

`current_hq` returns HQ, not state. `manpower` returns current combat-unit strength. `every_military_formation` works from country/front/HQ. No direct formation-to-state location link was proven in this research. This is an incomplete-capability finding, not proof that no workaround exists.

`on_monthly_pulse_country` has country scope in both generated logs. State monthly scope is listed as none in those logs and differs from shared type guidance; implementation deliberately uses the country hook.

The state effects document describes movement towards radicalism/loyalism but does not establish the exact semantics of negative values or ordering across radical/neutral/loyal categories. Negative radical effect is implemented experimentally and requires explicit game testing before release.

## Shared engine type guidance

- [Production methods](https://github.com/Victoria-3-Modding-Co-op/Modding-Digests/blob/main/documentation/types/production_methods.md): workforce_scaled versus level_scaled, state/building modifiers.
- [Script values](https://github.com/Victoria-3-Modding-Co-op/Modding-Digests/blob/main/documentation/types/script_values.md): formula order; `min` is a lower bound and `max` an upper bound.
- [On actions](https://github.com/Victoria-3-Modding-Co-op/Modding-Digests/blob/main/documentation/types/on_actions.md): append namespaced child actions instead of replacing vanilla effect blocks.
- [Buildings](https://github.com/Victoria-3-Modding-Co-op/Modding-Digests/blob/main/documentation/types/buildings.md): broad capabilities; some sample property names differ from contemporary mod code and are not treated as exact current schema proof.

## First-party author source examples (shape only)

- [Morgenroete's original gallery definition](https://github.com/Morgenrote-Team/Morgenroete-Beta/blob/Main/common/buildings/mr_arts_klimt_buildings.txt), retrieved blob SHA `ca1dcfca6513673e9851ac8d107dbca442d6370d`: `bg_government`, `production_method_groups`, `required_construction`, government/private construction filters. The project scripts are original, not a copied building definition. This source is not a 1.13/1.14 engine certification.
- [Better Politics original population script](https://github.com/Better-Politics-Mod/Better-Politics-Mod-Vic-3/blob/f02230c35eeb5bce4244ce5ee04c231007774679/better-politics-mod/common/script_values/bpm_population_values.txt): numeric state_population within script formulas.
- Base-game barracks icon path is referenced by contemporary mod asset inventories. The game file itself was not inspected locally; icon resolution is a test item, not a verified asset claim.

## Product mechanism references

- [Paradox Dev Diary #42](https://www.paradoxinteractive.com/games/victoria-3/news/dev-diary-42-cultural-secessions): historical explanation separating radicals, turmoil and negative effects. Not current API evidence.
- [Garrison Gameplay author's Workshop page](https://steamcommunity.com/sharedfiles/filedetails/?id=3770872919): author describes HQ-based regional garrison effects on a monthly update. This informs comparison only; no implementation code or precise allocation formula was obtained, and its wider diplomacy mechanics are outside scope.

## Still unverified

Actual engine loading, building schema and government payroll, employment-filter workforce accuracy, negative political-effect semantics, partial occupation/controller behavior, descriptor loading, icon paths, stacking with police/decrees, AI adoption, save/load, multiplayer and performance. All rates and costs are project design proposals, not sourced vanilla numbers.
