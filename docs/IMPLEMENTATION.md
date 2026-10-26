# Technical implementation · v0.3

## Runtime path
`on_monthly_pulse_country` appends a namespaced child. It visits only owned states with a garrison or a service record requiring cleanup. Each update clears old order tiers, resets old schema/ownership history, checks control and service mode, then reads dedicated employment only when a supplied operating facility exists.

State records:
- `gs_service_schema`: schema 3. v0.2 progress is discarded on migration.
- `gs_service_owner`: owner scope; an ownership mismatch resets both qualifications.
- `gs_service_months`: security qualification, bounded 0..3.
- `gs_civic_months`: separate civic qualification, bounded 0..6.
- `gs_interruption_months`: unavailable-service checks, bounded 0..2.

Temporary staff, coverage, relief and radical snapshot variables are removed after each update. Never count field army manpower, barracks slots or dependents.

Both production methods share employment and infrastructure scaling. Civic mode adds grain/fabric/paper/services; standby has no employment or inputs but retains level-scaled capacity reservation. Whether government payroll and partially employed pop workforce behave as intended remains a game-test item.

## Attitude changes
The Python oracle returns **target population shares/people**, not purported engine inputs. Eligible neutral share is explicit and defaults to zero. Both calculations use the pre-effect snapshot.

The runtime deradicalization budget is capped by total population, existing radical stock and room to the design floor before coverage scaling. Its negative `add_radicals_in_state` call is guarded by `gs_radical_effects_enabled`, generated from `experimental_radical_effects_enabled=false`. This is deliberately off until negative-value semantics are measured.

There is **no runtime loyalist effect call**. Available state effects do not establish individual neutral-only selection subject to acceptance and expected-SoL conditions. Civic qualification is tracked, but no broad state effect substitutes for that missing adapter. This remains an unfinished runtime feature.

## Explicit fallbacks
- Supply: checked building shortage boolean, not fabricated local shortage intensity. Any shortage stops effects.
- Uptime: monthly observations only. Counters and decay reduce low-staff prebanking but do not prove continuous operation or prevent all between-tick toggling.
- Stacking: the vanilla `state_turmoil_effects_mult` is used; no verified independent multiplicative layer.
- Current-order cleanup is monthly with 45-day expiry fallback. Historical attitude changes, when experimentally enabled, do not instantly reverse on closure.

## Generation and verification
`balance.json` is the single numeric source. The generator emits three production methods, feature gates, parameters, tiers and BOM-prefixed Chinese/English localization. Package version is read from the same config.

`tools/validate.py` checks generated freshness, braces, namespaced definitions/references and localization. It is not a Paradox schema validator.

Tests compare arithmetic script values with independent balance fixtures. A small control-flow harness executes the actual scripted effects/triggers and compares qualification, cleanup and tier results over 300 changing snapshots, plus migration and experimental-gate cases. It supplies employment as an input and records political calls; it cannot validate engine scopes, true workforce, population mutation semantics, event scheduling or game loading.

No actual game was launched. Exact 1.13/1.14 patch compatibility, performance, payroll, occupation granularity, saves and multiplayer remain unverified. Non-experimental packages remain blocked.
