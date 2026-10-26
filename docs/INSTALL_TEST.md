# Experimental install and game test

There is no engine-verified release yet. The build creates a **development test package**, not a stable distribution.

1. Run `python3 tools/generate.py`, `python3 tools/validate.py`, then `python3 -m unittest discover -s tests -v`.
2. Run `python3 scripts/package.py --target 1.13 --experimental` (or `--target 1.14`). This only declares the target, not compatibility.
3. Extract `gs_garrison/` and `gs_garrison.mod` together into your own `Documents/Paradox Interactive/Victoria 3/mod/` folder. The descriptor path is relative to that mod folder.
4. Create a test playset, enable only this mod, launch with debug logging, use a copied save or new game.
5. Check `error.log` for unknown properties/scopes/modifiers/assets before advancing. In particular verify the building schema and population reads; do not dismiss errors because tests passed.
6. Build a 卫戍营区/Garrison Compound using the government construction lens. Confirm it employs workers and is paid by the treasury without recruiting a field unit.
7. Record population/workers/infrastructure, advance one month, inspect the state modifier, then compare month 3 and month 6 political results. Compare with an identical baseline save without the facility.
8. Test standby, short supplies, occupation, change of owner, police/decree combination and reload. Complete VALIDATION.md separately for each exact patch/build.

Non-experimental packaging deliberately exits until game verification has been recorded in compatibility.json. Do not set game_verified to true merely to bypass this gate.
