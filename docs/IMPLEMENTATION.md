# Technical implementation

## Active mode
Fixed local garrison facility with dedicated employment. This explicitly replaces the old actual-army prototype objective following the user's request to research permanence. It does not claim to locate field armies in individual states.

## Data flow
`on_monthly_pulse_country` appends a namespaced on_action → each owned state → remove previous tier → reset on owner/controller changes → locate active, supplied garrison building → count workforce of pops employed in that building → calculate coverage → apply one 45-day tier → advance continuous service months → conditional bounded political effects.

The country monthly hook is intentional: the versioned on_actions logs list state monthly scope as none, while shared documentation describes state scope. Use the unambiguous country hook and explicit state iteration.

Generation in tools/generate.py creates numeric script values, building and production method definitions, tier modifiers and localization from balance.json. Engine effects/triggers are hand-maintained and refer to generated values. Employment counting uses pop employment filters and workforce; exact behavior for partially employed pops must be checked in game.

Production methods carry fixed infrastructure costs; employment jobs and goods use documented level/workforce scaling. Empty/idle/shortage buildings never pass active service eligibility. When short of inputs all benefits stop conservatively; wages and physical footprint remain.

## Evidence and limits
- Key state/formation/pop interfaces matched 1.13.11 and 1.14.5-openbeta generated docs.
- Shared type docs have stale building examples (`production_methods` vs live mod source `production_method_groups`); use contemporary original mod code for building property shape, and flag exact schema validation pending.
- Negative add_radicals_in_state values, script numeric reads from trigger names, government wages, job seeking workforce, and localization assets need engine checks.
- Controller equality represents the exposed state controller, not a proven per-province occupation fraction. Partial occupation must be tested.
- No vanilla override, no replace_path, no DLC dependency designed. AI automatic construction intentionally disabled for prototype; AI/player identical effects when facilities exist, not equal adoption behavior.
- No actual game runtime in this environment. Package output is experimental only, not an assertion of playability.

## Cleanup
No service → remove all tiers and service-month counter on next monthly tick. Owner change → reset before applying new-state logic. Political effects are historical changes, not temporary modifiers. Disabling the entire mod removes its definitions, but restoring a prior save is the reliable rollback for political changes. The runtime modifier expiry is a fallback, not an instant uninstall guarantee.
